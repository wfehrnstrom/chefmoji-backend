from flask import Flask, flash, url_for, redirect, send_from_directory, request, render_template, make_response
from flask_socketio import SocketIO, join_room, leave_room
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from utils import rand_id, player_in_game, redirect_ext_url, load_env_safe
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
from game import Game
import json

load_dotenv(find_dotenv())

DEBUG=(os.getenv('FLASK_ENV').lower()=='development')

# KEY CONSTANTS
UIDS = 'uids'

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

game_sessions = dict()

@app.route("/register", methods = ['POST'])
def register():
    # TODO: Get protobuf data from form
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
    # TODO: Get protobuf data from form
    # formdata.ParseFromString(request.form.get('protobuf'))
    # playerid = formdata.message.playerid
    # password = formdata.message.password
    # totp = formdata.message.password
    client_input = request.json
    playerid = client_input['playerid']
    password = client_input['password']
    totp = client_input['totp']

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
        toreturn["success"] = False
        toreturn["status"] = "OTHERFAILURES"
        return json.dumps(toreturn), 400

    if toreturn["success"]:
        response = make_response(redirect(url_for('redir')))
        response.status_code = 302
        response.headers["Set-Cookie"] = "HttpOnly;SameSite=Strict"
        response.set_cookie('session-key', rand_id())
        response.set_cookie('player-id', playerid)
        return response
    else:
        return json.dumps(toreturn), 400

# TODO: IDs will be issued through the TOTP mechanism Ertheo has setup, and not through this dummy route.
# @app.route('/issue-id')
# def issue_id():
#     if not UID in session:
#         generated_uid = rand_id()
#         session[UID] = generated_uid
#         socketio.emit('issue-id', generated_uid)
#         return 'ID Issued.'
#     else:
#         socketio.emit('issue-id', session[UID])
#         return 'ID already issued.'

# TODO: This will not work in a high request environment. Not threadsafe.
def make_new_session(owner_id):
    new_game_id = rand_id(allow_spec_chars=False)
    game_sessions[new_game_id] = Game(new_game_id, [owner_id])
    return new_game_id

@app.route("/create-game", method="POST")
def create_game():
    # TODO: Add client auth checking
    if UIDS in session:
        session_keys = session[UIDS]
        if session_keys[player_id] == client_supplied_session_key:
            game_id = make_new_session(session[UIDS])
            # Final message without additional room specifier.
            socketio.emit('session-init', game_id)
            return 'Game Creation Succeeded!'
    return 'Game Creation Failed!'

######################################## SOCKETIO ##################################################

@socketio.on('connect')
def handle_connect():
    print('-----SOCKETIO CONNECTION ESTABLISHED-----')

def broadcast_game(sio, g_id, pb=False):
    if g_id in game_sessions:
        if pb:
            sio.emit('tick', game_sessions[g_id].serialize_into_pb(), room=g_id)
        else:
            if DEBUG:
                for row in game_sessions[g_id].map.to_str():
                    print(row)
            sio.emit('tick', {'map': game_sessions[g_id].map.to_str()}, room=g_id)

@socketio.on('join-game-with-id')
def join_game_with_id(game_id, player_id, session_key):
    # TODO: join validation scheme: check whitelists or blacklists, if any.
    print("Player: " + player_id + " attempting to join the room: " + game_id)
    if session[] == player_id and game_id in game_sessions:
        print("Player: " + player_id + " joined the room: " + game_id + "!")
        join_room(game_id)
        if game_sessions[game_id].in_play():
            # broadcast_game(socketio, game_id)
            broadcast_game(socketio, game_id, pb=True)

@socketio.on('play')
def start_game(owner_id, game_id):
    # MAY CAUSE ERROR. FLASK SESSION STATE MAY NOT PERSIST INTO THIS FUNCTION
    if player_in_game(owner_id, game_sessions, game_id):
        # Set game state to playing
        game_sessions[game_id].play()
        # Broadcast game start to all connected players
        socketio.emit('tick', broadcast_game(socketio, game_id, pb=True), room=game_id)

@socketio.on('keypress')
def handle_player_keypress(msg, player_id, game_id):
    # TODO: Automatically make player moved the current session player.
    if player_in_game(player_id, game_sessions, game_id):
        game = game_sessions[game_id]
        decoded = PlayerAction()
        decoded.ParseFromString(bytes(list(msg.values())))
        if game.valid_player_update(player_id, decoded.key_press):
            # change game state
            game.update(player_id, decoded.key_press)
            # send tick to all connected clients
            broadcast_game(socketio, game_id, pb=True)
        else:
            print("Invalid update!")

@socketio.on('test')
def test():
    print('test comms received!')

if __name__ == "__main__":
    print("----------RUNNING AS MAIN---------")
    socketio.run(app)
