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

game_session = None

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/session")
def handle_session_req():
    # if user has verified email
    # if user is not already in another session
    pass

@app.route("/game")
def game():
    return 'hi'
    global game_session
    if game_session is not None:
        game_session.debug()
    return game_session.debug()

@socketio.on('keypress')
def handle_player_keypress(keydata):
    pass

@socketio.on('game')
def handle_update():
    global game_session
    if game_session is not None:
        game_session.debug()

@socketio.on('connect')
def handle_connect():
    print('Connected to client!')
    global game_session
    game_session = Game('xxxxxx')

if __name__ == "__main__":
    socketio.run(app)