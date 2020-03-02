from flask import Flask, flash, url_for, redirect, send_from_directory, request, render_template, make_response, session
from flask_socketio import SocketIO, join_room, leave_room, rooms
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from utils import rand_id, player_in_game, authd, eprint, player_owns_game
import os
import argparse
from signup_checker import signup_checker
from mailconfirm.tokenconfirm import generate_confirmation_token, confirm_token
from flask_mail import Mail
from flask_mail import Message
import sha3
import pyotp
import os
from protocol_buffers import emailconfirm_pb2, loginconfirm_pb2
from protocol_buffers.player_action_pb2 import PlayerAction
from db.db import DBman
from game import Game, OrderItem, GameState
from enum import Enum
import json
from threading import Timer

load_dotenv(find_dotenv())

DEBUG=(os.getenv('FLASK_ENV').lower()=='development')
HOSTNAME='https://chefmoji.wtf'
ADDR=HOSTNAME
PORT='80'
if DEBUG:
    HOSTNAME='http://localhost'
    PORT='8080'
    ADDR=HOSTNAME+':'+PORT

# KEY CONSTANTS
KEY='key'
ENCODING = 'utf-8'
STATUS = 'status'
SUCCESS = 'success'
TOTP_KEY = 'totpkey'
CLIENT_PLAYER_ID = 'playerid'
CLIENT_PASSWORD='password'
CLIENT_EMAIL='email'

# TODO
# Don't let player log in again if they are already logged in somewhere else
# If a client disconnects, remove them from the games they were in immediately
# Delete inactive games immediately
# Check if game join code is valid before redirecting player to lobby

app = Flask(__name__, instance_relative_config=True, template_folder='/var/www/data')

app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['MAIL_SERVER']=os.getenv('MAIL_SERVER')
app.config['MAIL_PORT']=os.getenv('MAIL_PORT')
app.config['MAIL_USE_SSL']=os.getenv('MAIL_USE_SSL')
app.config['MAIL_DEFAULT_SENDER']=os.getenv('MAIL_DEFAULT_SENDER')
app.config['MAIL_USERNAME']=os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD']=os.getenv('MAIL_PASSWORD')

db = DBman()
mail = Mail(app)

socketio = SocketIO(app, cors_allowed_origins=ADDR, logger=DEBUG, engineio_logger=DEBUG)

# TODO: Gate access to these structures using locks
game_sessions = dict()
player_ids = dict()
player_timers = dict()
socket_to_player = dict()

def send_email(subject, body, recipients):
    mail.send(Message(\
        subject = subject,\
        body = body,\
        sender = os.getenv('MAIL_USERNAME'),\
        recipients = recipients\
    ))

@app.route("/forget", methods = ['POST'])
def forget():

    toreturn = {
        "success": False
    }

    client_input = request.json
    if not client_input:
        return json.dumps(toreturn), 400

    if 'forgotwhat' in client_input:
        forgotwhat = client_input['forgotwhat']
    if 'email' in client_input:
        email = client_input['email']
    if 'mfakey' in client_input:
        totp = client_input['mfakey']

    try:
        if(forgotwhat == 'playerid'):
            playerid = db.get_player_id(email)
            if playerid:
                send_email('Chefmoji: Forgot player_id', f'This is your player id: {playerid}', [email])
                toreturn["success"] = True
        if(forgotwhat == 'password'):
            if db.email_exists_in_db(email) and db.check_totp(email, totp):
                password = db.set_temp_pwd(email)
                send_email('Chefmoji: Forgot password', f'This is your new password: {password}', [email])
                toreturn["success"] = True
    except Exception as err:
        json.dumps(toreturn)

    return json.dumps(toreturn)

@app.route("/register", methods = ['POST'])
def register():
    toreturn = {
        "success": False,
        "email": "OTHERFAILURES",
        "playerid": "OTHERFAILURES"
    }

    client_input = request.json
    # TODO: implement stricter error checking
    if (not client_input or CLIENT_PLAYER_ID not in client_input or CLIENT_PASSWORD not in client_input or CLIENT_EMAIL not in client_input):
        return json.dumps(toreturn), 400

    playerid = client_input[CLIENT_PLAYER_ID]
    password = client_input[CLIENT_PASSWORD]
    email = client_input[CLIENT_EMAIL]

    # Hash the password again using sha3
    password = sha3.sha3_256(password.encode(ENCODING)).hexdigest()

    # Validate the email and playerid
    checker = signup_checker(email, playerid)
    toreturn = checker.message
    if checker.message[SUCCESS]:
        try:
            # Write the email and playerid and hashed password to the database
            db.set_signupinfo(playerid, email, password)
        except Exception as err:
            print("%s" % err)
            checker.message[SUCCESS] = False
            checker.message[CLIENT_EMAIL] = "OTHERFAILURES"
            checker.message[CLIENT_PLAYER_ID] = "OTHERFAILURES"
            toreturn = checker.message
            return json.dumps(toreturn), 400
        try:
            token = generate_confirmation_token(email, os.getenv('SECRET_KEY'), os.getenv('SECRET_SALT'))
            recipients = [email]
            msg = Message('Hello, I am The chefmoji👨‍🍳👩‍🍳', sender = os.getenv('MAIL_USERNAME'),\
                    recipients = recipients)
            msg.body = url_for('email_confirm', token = token, _external=True)
            mail.send(msg)
        except Exception as err:
            print("%s" % err)
            return json.dumps(toreturn), 400
    return json.dumps(toreturn)

@app.route("/emailconfirm/<token>")
def email_confirm(token):
    # return a protobuf message
    toreturn = {
        "success": False,
        "status": "OTHERFAILURES", # DOESNOTEXIST, PREVCONFIRMED, JUSTCONFIRMED
        "totpkey": ""
    }
    try:
        email = confirm_token(token, os.getenv('SECRET_KEY'), os.getenv('SECRET_SALT'))
    except:
        toreturn[SUCCESS] = False
        toreturn["status"] = "DOESNOTEXIST"
        return render_template('emailconfirm.html', status=toreturn["status"], success=toreturn[SUCCESS], totpkey=toreturn["totpkey"])

    try:
        if db.email_exists_in_db(email): # if email exists in the database
            if db.is_account_verified2(email):
                toreturn[SUCCESS] = True
                toreturn["status"] = "PREVCONFIRMED"
            else:
                # set verified flag in db and write mfa key to datbase
                db.verify_account(email)
                totpkey = db.set_totp_key(email)
                toreturn[SUCCESS] = True
                toreturn["status"] = "JUSTCONFIRMED"
                toreturn["totpkey"] = totpkey
        else: #if email DOES NOT EXIST in the database
            toreturn[SUCCESS] = False
            toreturn["status"] = "DOESNOTEXIST"
    except Exception:
        toreturn[SUCCESS] = False
        toreturn["status"] = "OTHERFAILURES"
        return render_template('emailconfirm.html', status=toreturn["status"], success=toreturn[SUCCESS], totpkey=toreturn["totpkey"])

    return render_template('emailconfirm.html', status=toreturn["status"], success=toreturn[SUCCESS], totpkey=toreturn["totpkey"])
    # NOTE: working with flash on the front end - get_flashed_messages() https://pythonprogramming.net/flash-flask-tutorial/

@app.route("/login", methods = ['POST'])
def login():

    toreturn = {
        "success": False,
        "status": "OTHERFAILURES" # BADINPUT, INCOOLDOWN, NOTVERIFIED, GOOD, OTHERFAILURES
    }
    
    client_input = request.json
    if not client_input:
        return json.dumps(toreturn), 400

    if CLIENT_PLAYER_ID in client_input:
        playerid = client_input[CLIENT_PLAYER_ID]
    else:
        playerid = ''
    if CLIENT_PASSWORD in client_input:
        password = client_input[CLIENT_PASSWORD]
    else:
        password = ''
    if 'totp' in client_input:
        totp = client_input['totp']
    else:
        totp = ''

    # hash password
    password = sha3.sha3_256(password.encode(ENCODING)).hexdigest()

    # call DBman to check
    try:
        toreturn = db.check_login_info(playerid, password, totp, toreturn)
    except:
        eprint(json.dumps(toreturn))
        toreturn[SUCCESS] = False
        toreturn["status"] = "OTHERFAILURES"
        return json.dumps(toreturn), 400

    if toreturn[SUCCESS]:
        response = make_response(redirect(ADDR+'/lobby.html'), 302)
        response.headers["Set-Cookie"] = "HttpOnly;SameSite=Strict"
        session_key = rand_id(allow_spec_chars=False)
        player_ids[session_key] = playerid
        session[KEY]=session_key
        response.set_cookie('session-key', session_key)
        response.set_cookie('player-id', playerid)
        return response
    else:
        eprint(toreturn)
        return json.dumps(toreturn), 400

def make_new_session(owner_player_id):
    new_game_id = rand_id(allow_spec_chars=False)
    game_sessions[new_game_id] = (owner_player_id, Game(socketio, new_game_id, [owner_player_id]))
    return new_game_id

SUCCESS_CODE = 1
BAD_AUTH_CODE = 2
PLAYER_IN_GAME_CODE = 3
OTHER_ERROR_CODE = 4

@app.route("/check-auth", methods=["POST"])
def check_auth():
    resp = {
        "authorized": False,
        "error_code": OTHER_ERROR_CODE
    }
    if KEY in session:
        supplied_session_key = str(request.json['sessionkey'])
        player_id = str(request.json[CLIENT_PLAYER_ID])
        if (authd(player_id, supplied_session_key, player_ids, session[KEY])):
            resp["authorized"] = True
            resp["error_code"] = SUCCESS_CODE
            return resp, 200
    resp["error_code"] = BAD_AUTH_CODE
    return resp, 400

@app.route("/create-game", methods=["POST"])
def create_game():
    print("---------ATTEMPTING TO CREATE GAME------")
    resp = {
        "success": False,
        "reason": "",
        "error_code": OTHER_ERROR_CODE,
        "game_id": ""
    }
    if KEY in session:
        supplied_session_key = request.json['sessionkey']
        player_id = request.json[CLIENT_PLAYER_ID]
        if (authd(player_id, supplied_session_key, player_ids, session[KEY])):
            if player_owns_game(player_id, game_sessions):
                resp["reason"] = "Player already in a game"
                resp["error_code"] = PLAYER_IN_GAME_CODE
                return resp, 400
            game_id = make_new_session(player_id)
            resp["game_id"] = game_id
            resp["error_code"] = SUCCESS_CODE
            resp[SUCCESS] = True
            return resp, 200
    resp["error_code"] = BAD_AUTH_CODE
    resp["reason"] = "Provided authentication was invalid"
    return resp, 400

######################################## SOCKETIO ##################################################

@socketio.on('connect')
def handle_connect():
    print('-----SOCKETIO CONNECTION ESTABLISHED-----')

@socketio.on('player-id')
def store_player_id(player_id):
    socket_to_player[request.sid] = player_id
    print('Socket ID', request.sid, 'contains', player_id)

@socketio.on('disconnect')
def handle_disconnect():
    print('-----SOCKETIO CONNECTION DISCONNECTED-----')
    player_id = socket_to_player[request.sid]
    print('Client disconnected', player_id)
    for game_id in game_sessions.keys():
        if player_in_game(player_id, game_sessions, game_id):
            game_sessions[game_id][1].remove_player(player_id)
            break
    if game_sessions[game_id][1].state == GameState.FINISHED:
        del game_sessions[game_id]
    broadcast_game(socketio, game_id, pb=True)

def broadcast_game(sio, g_id, pb=False):
    if g_id in game_sessions:
        if pb:
            sio.emit('tick', game_sessions[g_id][1].serialize_into_pb(), room=g_id)
        else:
            sio.emit('tick', {'map': game_sessions[g_id][1].map.to_str()}, room=g_id)

def get_game_players(game_id, player_id, session_key):
    players = []
    if(session_key in player_ids and player_ids[session_key] == player_id and game_id in game_sessions):
        for p in player_ids.values():
            if player_in_game(p, game_sessions, game_id):
                players.append(p)

        if game_sessions[game_id][1].in_play():
            socketio.emit('get-game-players', (True, game_sessions[game_id][0] == player_id, \
                game_sessions[game_id][0], players), room=game_id); # game is in play
        else:
            socketio.emit('get-game-players', (False, game_sessions[game_id][0] == player_id, \
                game_sessions[game_id][0], players), room=game_id); # game is not in play

#TODO: add socket emit "join-failed" if game is already in play
@socketio.on('join-game-with-id')
def join_game_with_id(game_id, player_id, session_key):
    # TODO: join validation scheme: check whitelists or blacklists, if any.
    game_id, player_id, session_key = str(game_id), str(player_id), str(session_key)
    if session_key in player_ids and player_ids[session_key] == player_id and game_id in game_sessions:
        print("Player: " + player_id + " joined the room: " + game_id + " !")
        # if the player is already in the game, this is a no-op.
        if not game_sessions[game_id][1].has_player(player_id):
            successful_add = game_sessions[game_id][1].add_player(player_id)
            if not successful_add:
                socketio.emit("game-at-capacity")
                return
        join_room(game_id)
        socketio.emit("join-confirm", game_id)
        if game_sessions[game_id][1].in_play():
            broadcast_game(socketio, game_id, pb=True)
        else:
            get_game_players(game_id, player_id, session_key)

PLAYER_TIMEOUT = 60.0
if DEBUG:
    PLAYER_TIMEOUT = 15.0

@socketio.on('play')
def start_game(owner_session_key=None, game_id=None):
    if owner_session_key and owner_session_key in player_ids and game_id and player_in_game(player_ids[owner_session_key], game_sessions, game_id):
        # Set game state to playing
        socketio.emit('game-started', True, room=game_id)
        for player in game_sessions[game_id][1].players.values():
            player_timers[player.id] = Timer(PLAYER_TIMEOUT, remove_inactive_player, [player.id, game_id])
            player_timers[player.id].start()

        game_sessions[game_id][1].play()
        # Broadcast game start to all connected players
        broadcast_game(socketio, game_id, pb=True)

def remove_inactive_player(player_id, game_id):
    socketio.emit('timedout', {'player': player_id}, room=game_id)
    del player_timers[player_id]
    game_sessions[game_id][1].remove_player(player_id)
    if game_sessions[game_id][1].state == GameState.FINISHED:
        del game_sessions[game_id]
    broadcast_game(socketio, game_id, pb=True)

@socketio.on('keypress')
def handle_player_keypress(msg=None, session_key=None, game_id=None):
    if session_key and session_key in player_ids:
        player_id = player_ids[session_key]
    else:
        eprint('Error: session key invalid or not sent')
        return
    if game_id and msg and player_in_game(player_id, game_sessions, game_id):
        game = game_sessions[game_id][1]
        try:
            decoded = PlayerAction()
            decoded.ParseFromString(bytes(list(msg.values())))
            if game.valid_player_update(player_id, decoded.key_press):
                player_timers[player_id].cancel()
                player_timers[player_id] = Timer(PLAYER_TIMEOUT, remove_inactive_player, [player_id, game_id])
                player_timers[player_id].start()
                # change game state
                game.update(player_id, decoded.key_press)
                # send tick to all connected clients
                broadcast_game(socketio, game_id, pb=True)
        except Exception as err:
            eprint(err)

if __name__ == "__main__":
    print("----------RUNNING AS MAIN---------")
    socketio.run(app)
