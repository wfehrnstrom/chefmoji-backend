from os import environ
from flask import Flask, render_template
from flask_socketio import SocketIO
from dotenv import load_dotenv
from pathlib import Path
import os
import argparse
import game_update_pb2

from game import Game

load_dotenv(dotenv_path=Path('../.env'))
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
# REMOVE/RESTRICT CORS_ALLOWED_ORIGINS. THIS IS DEVELOPMENT ONLY.
socketio = SocketIO(app, cors_allowed_origins='*')

game_sessions = dict()

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
def handle_player_keypress(keydata):
    pass

@socketio.on('join-req')
def handle_join(join_req):
    print('Join Request Received\n')
    # TODO: join request validation scheme
    print(join_req)
    join_req = {'id': '1aLc90'}
    if 'id' in join_req:
        if join_req['id'] in game_sessions:
            pass
        else:
            game_sessions[join_req['id']] = Game(join_req['id'])
        socketio.emit('tick', {'map': game_sessions[join_req['id']].map.to_str()})

@socketio.on('connect')
def handle_connect():
    print('Connected to client!')
    socketio.emit('accepting-connections')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == "__main__":
    socketio.run(app)