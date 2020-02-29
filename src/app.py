from flask import Flask, flash, url_for, redirect, send_from_directory, request, render_template, make_response, session
from flask_socketio import SocketIO, join_room, leave_room
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from utils import rand_id, player_in_game, redirect_ext_url, authd, eprint, player_owns_game
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

# KEY CONSTANTS
KEY='key'

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

# REMOVE/RESTRICT CORS_ALLOWED_ORIGINS. THIS IS DEVELOPMENT ONLY.
socketio = SocketIO(app, cors_allowed_origins='*')

# TODO: Gate access to these structures using locks
game_sessions = dict()
player_ids = dict()
player_timers = dict()

@app.route("/register", methods = ['POST'])
def register():
    client_input = request.json
    playerid = client_input['playerid']
    password = client_input['password']
    email = client_input['email']

    # Hash the password again using sha3
    password = sha3.sha3_256(password.encode('utf-8')).hexdigest()

    # Validate the email and playerid
    checker = signup_checker(email, playerid)

    if checker.message["success"]:
        try:
            # Write the email and playerid and hashed password to the database
            db.set_signupinfo(playerid, email, password)
        except Exception as err:
            print("%s" % err)
            checker.message["success"] = False
            checker.message["email"] = "OTHERFAILURES"
            checker.message["playerid"] = "OTHERFAILURES"
            return json.dumps(checker.message)
        try:
            # TODO: Look at above to do, make sure write success before sending mail
            token = generate_confirmation_token(email, os.getenv('SECRET_KEY'), os.getenv('SECRET_SALT'))
            recipients = [email]
            msg = Message('Hello, I am The chefmoji👨‍🍳👩‍🍳', sender = os.getenv('MAIL_USERNAME'),\
                    recipients = recipients)
            msg.body = url_for('email_confirm', token = token, _external=True)
            mail.send(msg)
        except Exception as err:
            print("%s" % err)
            return json.dumps(checker.message)
    return json.dumps(checker.message)

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
        toreturn["success"] = False
        toreturn["status"] = "DOESNOTEXIST"
        return render_template('emailconfirm.html', status=toreturn["status"], success=toreturn["success"], totpkey=toreturn["totpkey"])

    try:
        if db.email_exists_in_db(email): # if email exists in the database
            if db.is_account_verified2(email):
                toreturn["success"] = True
                toreturn["status"] = "PREVCONFIRMED"
            else:
                # set verified flag in db and write mfa key to datbase
                db.verify_account(email)
                totpkey = db.set_totp_key(email)

                toreturn["success"] = True
                toreturn["status"] = "JUSTCONFIRMED"
                toreturn["totpkey"] = totpkey
        else: #if email DOES NOT EXIST in the database
            toreturn["success"] = False
            toreturn["status"] = "DOESNOTEXIST"
    except Exception as err:
        print('Error:', err)
        toreturn["success"] = False
        toreturn["status"] = "OTHERFAILURES"
        return render_template('emailconfirm.html', status=toreturn["status"], success=toreturn["success"], totpkey=toreturn["totpkey"])

    return render_template('emailconfirm.html', status=toreturn["status"], success=toreturn["success"], totpkey=toreturn["totpkey"])
    # NOTE: working with flash on the front end - get_flashed_messages() https://pythonprogramming.net/flash-flask-tutorial/

@app.route("/login", methods = ['POST'])
def login():
    client_input = request.json
    if 'playerid' in client_input:
        playerid = client_input['playerid']
    else:
        playerid = ''
    if 'password' in client_input:
        password = client_input['password']
    else:
        password = ''
    if 'totp' in client_input:
        totp = client_input['totp']
    else:
        totp = ''

    # hash password
    password = sha3.sha3_256(password.encode('utf-8')).hexdigest()

    # return a protobuf message
    toreturn = {
        "success": False,
        "status": "OTHERFAILURES" # BADINPUT, INCOOLDOWN, NOTVERIFIED, GOOD, OTHERFAILURES
    }

    # call DBman to check
    try:
        toreturn = db.check_login_info(playerid, password, totp, toreturn)
    except:
        print(json.dumps(toreturn))
        toreturn["success"] = False
        toreturn["status"] = "OTHERFAILURES"
        return json.dumps(toreturn), 400

    if toreturn["success"]:
        response = make_response(redirect('http://localhost:8080/lobby.html'), 302)
        response.headers["Set-Cookie"] = "HttpOnly;SameSite=Strict"
        session_key = rand_id(allow_spec_chars=False)
        # TODO: Insert Lock
        player_ids[session_key] = playerid
        session[KEY]=session_key
        response.set_cookie('session-key', session_key)
        response.set_cookie('player-id', playerid)
        return response
    else:
        print(toreturn)
        return json.dumps(toreturn), 400

# TODO: This will not work in a high request environment. Not threadsafe.
def make_new_session(owner_player_id):
    new_game_id = rand_id(allow_spec_chars=False)
    game_sessions[new_game_id] = (owner_player_id, Game(socketio, new_game_id, [owner_player_id]))
    return new_game_id

# TODO: CREATE ENUM WHEN I COME BACK THAT MARKS ERROR_CODE/REASON FOR NOT BEING ABLE TO JOIN GAME.
class GameCreationError(Enum):
    SUCCESS = 1
    BAD_AUTH = 2
    PLAYER_IN_GAME = 3
    OTHER_ERROR = 4

SUCCESS = 1
BAD_AUTH = 2
PLAYER_IN_GAME = 3
OTHER_ERROR = 4

@app.route("/check-auth", methods=["POST"])
def check_auth():
    resp = {
        "authorized": False,
        "error_code": OTHER_ERROR
    }
    if KEY in session:
        supplied_session_key = str(request.json['sessionkey'])
        player_id = str(request.json['playerid'])
        if (authd(player_id, supplied_session_key, player_ids, session[KEY])):
            resp["authorized"] = True
            resp["error_code"] = SUCCESS
            return resp, 200
    resp["error_code"] = BAD_AUTH
    return resp, 400

@app.route("/create-game", methods=["POST"])
def create_game():
    resp = {
        "success": False,
        "reason": "",
        "error_code": OTHER_ERROR,
        "game_id": ""
    }
    if KEY in session:
        supplied_session_key = str(request.json['sessionkey'])
        player_id = str(request.json['playerid'])
        if (authd(player_id, supplied_session_key, player_ids, session[KEY])):
            if player_owns_game(player_id, game_sessions):
                resp["reason"] = "Player already in-game"
                resp["error_code"] = PLAYER_IN_GAME
                return resp, 400
            game_id = make_new_session(player_id)
            resp["game_id"] = game_id
            resp["error_code"] = SUCCESS
            resp["success"] = True
            return resp, 200
    resp["error_code"] = BAD_AUTH
    resp["reason"] = "Provided authentication was invalid"
    return resp, 400

######################################## SOCKETIO ##################################################

@socketio.on('connect')
def handle_connect():
    print('-----SOCKETIO CONNECTION ESTABLISHED-----')

def broadcast_game(sio, g_id, pb=False):
    if g_id in game_sessions:
        if pb:
            sio.emit('tick', game_sessions[g_id][1].serialize_into_pb(), room=g_id)
        else:
            if DEBUG:
                for row in game_sessions[g_id][1].map.to_str():
                    print(row)
            sio.emit('tick', {'map': game_sessions[g_id][1].map.to_str()}, room=g_id)

def get_game_players(game_id, player_id, session_key):
    players = [];
    if(player_ids[session_key] == player_id and game_id in game_sessions):
        for p in player_ids.values():
            if player_in_game(p, game_sessions, game_id):
                players.append(p)

        print(str(player_id) + " owns game: " + str(game_sessions[game_id][0] == player_id) + " , game_sessions[game_id][0] = ", str(game_sessions[game_id][0]));

        if game_sessions[game_id][1].in_play():
            socketio.emit('get-game-players', (True, game_sessions[game_id][0] == player_id, \
                game_sessions[game_id][0], players), room=game_id) # game is in play
        else:
            socketio.emit('get-game-players', (False, game_sessions[game_id][0] == player_id, \
                game_sessions[game_id][0], players), room=game_id) # game is not in play

#TODO: add socket emit "join-failed" if game is already in play
@socketio.on('join-game-with-id')
def join_game_with_id(game_id, player_id, session_key):
    # TODO: join validation scheme: check whitelists or blacklists, if any.
    # TODO: check whether player is already in the game they are attempting to join

    game_id, player_id, session_key = str(game_id), str(player_id), str(session_key)
    if player_ids[session_key] == player_id and game_id in game_sessions:
        print("Player: " + player_id + " joined the room: " + game_id + " !")
        game_sessions[game_id][1].add_player(player_id)
        join_room(game_id)

        socketio.emit("join-confirm")
        if game_sessions[game_id][1].in_play():
            broadcast_game(socketio, game_id, pb=True)
        else:
            get_game_players(game_id, player_id, session_key)

@socketio.on('play')
def start_game(owner_session_key=None, game_id=None):
    # MAY CAUSE ERROR. FLASK SESSION STATE MAY NOT PERSIST INTO THIS FUNCTION
    if owner_session_key and owner_session_key in player_ids and game_id and player_in_game(player_ids[owner_session_key], game_sessions, game_id):
        # Set game state to playing
        # Broadcast game start to all connected players
        socketio.emit('game-started', True, room=game_id)
        # for p in player_ids:
        # TODO: for each player in this game, create a new Timer and add to player_timers dictionary
        for player in game_sessions[game_id][1].players.values():
            player_timers[player.id] = Timer(60.0, remove_inactive_player, [player.id, game_id])
            player_timers[player.id].start()

        game_sessions[game_id][1].play()
        socketio.emit('tick', broadcast_game(socketio, game_id, pb=True), room=game_id)

def remove_inactive_player(player_id, game_id):
    print('TIMES UP for:', player_id)
    socketio.emit('timedout', {'player': player_id}, room=game_id)
    del player_timers[player_id]
    game_sessions[game_id][1].remove_player(player_id)
    if game_sessions[game_id][1].state == GameState.FINISHED:
        del game_sessions[game_id]
    broadcast_game(socketio, game_id, pb=True)

@socketio.on('keypress')
def handle_player_keypress(msg=None, session_key=None, game_id=None):

    # TODO: Automatically make player moved the current session player.
    if session_key and session_key in player_ids:
        player_id = player_ids[session_key]
    else:
        eprint('session key invalid or not sent')
        return
    if game_id and msg and player_in_game(player_id, game_sessions, game_id):
        game = game_sessions[game_id][1]
        decoded = PlayerAction()
        decoded.ParseFromString(bytes(list(msg.values())))
        if game.valid_player_update(player_id, decoded.key_press):
            player_timers[player_id].cancel()
            player_timers[player_id] = Timer(60.0, remove_inactive_player, [player_id, game_id])
            player_timers[player_id].start()
            # change game state
            game.update(player_id, decoded.key_press)
            # send tick to all connected clients
            broadcast_game(socketio, game_id, pb=True)
        else:
            print("Invalid update!")

if __name__ == "__main__":
    print("----------RUNNING AS MAIN---------")
    socketio.run(app)
