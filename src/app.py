from os import environ
from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room
from dotenv import load_dotenv
from pathlib import Path
import os
import argparse

from game import Game

load_dotenv(dotenv_path=Path('../.env'))
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
# REMOVE/RESTRICT CORS_ALLOWED_ORIGINS. THIS IS DEVELOPMENT ONLY.
socketio = SocketIO(app, cors_allowed_origins='*')

game_sessions = dict()

# FOR NOW ONLY
# TODO: REMOVE
PLAYER_1_ID = '1aLc90'

@app.route("/")
def hello_world():
    socketio.emit('accepting-connections')
    return "Hello, World!"

@app.route("/session")
def handle_session_req():
    # if user has verified email
    # if user is not already in another session
    pass

@socketio.on('keypress')
def handle_player_keypress(key, game_id):
    # TODO: Handle specific player: for now, just automatically move first player
    if game_id in game_sessions:
        game = game_sessions[game_id]
        if game.valid_player_update(PLAYER_1_ID, key):
            # change game state
            game.update(PLAYER_1_ID, key)
            # send tick to all connected clients
            g_update(socketio, game_id, pb=True)
        else:
            raise ValueError


@socketio.on('join-req')
def handle_join(join_req):
    print('Join Request Received\n')
    # TODO: join request validation scheme
    print(join_req)
    join_req = {'id': PLAYER_1_ID}
    if 'id' in join_req:
        if join_req['id'] in game_sessions:
            pass
        else:
            game_sessions[join_req['id']] = Game(join_req['id'])
        join_room(join_req['id'])
        g_update(socketio, join_req['id'])
        g_update(socketio, join_req['id'], True)

def g_update(sio, g_id, pb=False):
    if g_id in game_sessions:
        if pb:
            sio.emit('tick', game_sessions[g_id].serialize_into_pb())
        else:
            sio.emit('tick', {'map': game_sessions[g_id].map.to_str()})

@socketio.on('connect')
def handle_connect():
    print('Connected to client!')
    socketio.emit('accepting-connections')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == "__main__":
    socketio.run(app)