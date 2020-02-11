from flask import Flask, render_template, session, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room
from dotenv import load_dotenv
from pathlib import Path
from utils import rand_id, player_in_game, static_files_path
import os
import argparse

from game import Game

load_dotenv(dotenv_path=Path('../.env'))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
# REMOVE/RESTRICT CORS_ALLOWED_ORIGINS. THIS IS DEVELOPMENT ONLY.
socketio = SocketIO(app, cors_allowed_origins='*')

game_sessions = dict()

DEBUG = True

# KEY CONSTANTS
UID = 'uid'

@app.route('/')
def index():
    return 'Hello!'

@app.route('/hello')
def hello():
    return 'Hello!'

@app.route("/session")
def handle_session_req():
    # TODO: ensure user has logged in
    # if user has verified email
    # if user is not already in another session
    # socketio.emit('accepting-connections')
    return "Hello World!"

def make_new_session(owner_id):
    new_game_id = rand_id(allow_spec_chars=False)
    game_sessions[new_game_id] = Game(new_game_id, [owner_id])
    return new_game_id

@app.route("/lobby")
def handle_lobby():
    if UID in session:
        game_id = make_new_session(UID)
        join_room(game_id, UID)
        socketio.emit('session-init', game_id)
    return "Lobby!"

@socketio.on('play')
def start_game(owner_id, game_id):
    # MAY CAUSE ERROR. FLASK SESSION STATE MAY NOT PERSIST INTO THIS FUNCTION
    if owner_id in session and player_in_game(owner_id, game_sessions, game_id):
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

@socketio.on('join-game-with-id')
def join_game_with_id(game_id, player_id):
    print('Join Request Received\n')
    # TODO: join validation scheme: check whitelists or blacklists, if any.
    if player_id in session and game_id in game_sessions:
        print("Player: " + player_id + " joined the room: " + game_id + "!")
        join_room(game_id)
        if game_sessions[game_id].in_play():
            g_update(socketio, game_id)
            g_update(socketio, game_id, pb=True)

def g_update(sio, g_id, pb=False):
    if g_id in game_sessions:
        if pb:
            sio.emit('tick', game_sessions[g_id].serialize_into_pb())
        else:
            if DEBUG:
                for row in game_sessions[g_id].map.to_str():
                    print(row)
            sio.emit('tick', {'map': game_sessions[g_id].map.to_str()})

@socketio.on('connect')
def handle_connect():
    if not UID in session:
        generated_uid = rand_id()
        print("ISSUE ID")
        socketio.emit('issue-id', generated_uid)
        session[UID] = generated_uid

# @socketio.on('disconnect')
# def handle_disconnect():
#     print('Client disconnected')

if __name__ == "__main__":
    print("----------RUNNING AS MAIN---------")
    socketio.run(app)