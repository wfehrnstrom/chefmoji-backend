from flask import Flask, session
from flask_socketio import SocketIO, join_room, leave_room
from dotenv import load_dotenv
from pathlib import Path
from utils import rand_id, player_in_game, redirect_ext_url
import os
import argparse

from game import Game

load_dotenv(dotenv_path=Path('../.env'))

DEBUG=(os.getenv('FLASK_ENV').lower()=='development')

# KEY CONSTANTS
UID = 'uid'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')

# REMOVE/RESTRICT CORS_ALLOWED_ORIGINS. THIS IS DEVELOPMENT ONLY.
socketio = SocketIO(app, cors_allowed_origins='*')

game_sessions = dict()

@app.route('/test')
def hello():
    return 'Hello!'

# TODO: IDs will be issued through the TOTP mechanism Ertheo has setup, and not through this dummy route.
@app.route('/issue-id')
def issue_id():
    if not UID in session:
        generated_uid = rand_id()
        session[UID] = generated_uid
        socketio.emit('issue-id', generated_uid)
        return 'ID Issued.'
    else:
        socketio.emit('issue-id', session[UID])
        return 'ID already issued.'

# TODO: This will not work in a high request environment. Not threadsafe.
def make_new_session(owner_id):
    new_game_id = rand_id(allow_spec_chars=False)
    game_sessions[new_game_id] = Game(new_game_id, [owner_id])
    return new_game_id

@app.route("/create-game")
def create_game():
    if UID in session:
        game_id = make_new_session(session[UID])
        socketio.emit('session-init', game_id)
        # return redirect_ext_url('/lobby.html')
        return 'Game Creation Succeeded!'
    return 'Game Creation Failed!'


######################################## SOCKETIO ##################################################

@socketio.on('connect')
def handle_connect():
    print('-----SOCKETIO CONNECTION ESTABLISHED-----')

def g_update(sio, g_id, pb=False):
    if g_id in game_sessions:
        if pb:
            sio.emit('tick', game_sessions[g_id].serialize_into_pb())
        else:
            if DEBUG:
                for row in game_sessions[g_id].map.to_str():
                    print(row)
            sio.emit('tick', {'map': game_sessions[g_id].map.to_str()})

@socketio.on('join-game-with-id')
def join_game_with_id(game_id, player_id):
    # TODO: join validation scheme: check whitelists or blacklists, if any.
    print("Player: " + player_id + " attempting to join the room: " + game_id)
    if session[UID] == player_id and game_id in game_sessions:
        print("Player: " + player_id + " joined the room: " + game_id + "!")
        join_room(game_id)
        if game_sessions[game_id].in_play():
            g_update(socketio, game_id)
            g_update(socketio, game_id, pb=True)

@socketio.on('play')
def start_game(owner_id, game_id):
    # MAY CAUSE ERROR. FLASK SESSION STATE MAY NOT PERSIST INTO THIS FUNCTION
    print('checking for player')
    if player_in_game(owner_id, game_sessions, game_id):
        print("PLAY START.")
        # Set game state to playing
        game_sessions[game_id].play()
        # Broadcast game start to all connected players
        socketio.emit('tick', g_update(socketio, game_id), room=game_id)

@socketio.on('keypress')
def handle_player_keypress(key, player_id, game_id):
    # TODO: Automatically make player moved the current session player.
    if player_in_game(player_id, game_sessions, game_id):
        game = game_sessions[game_id]
        if game.valid_player_update(player_id, key):
            # change game state
            game.update(player_id, key)
            # send tick to all connected clients
            g_update(socketio, game_id)
            g_update(socketio, game_id, pb=True)
        else:
            print("Invalid update!")
            # raise ValueError

@socketio.on('test')
def test():
    print('test comms received!')

if __name__ == "__main__":
    print("----------RUNNING AS MAIN---------")
    socketio.run(app)