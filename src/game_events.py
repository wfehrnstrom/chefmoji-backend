from flask_socketio import SocketIO

@socketio.on('message')
def message(data):
    print('received: ' + data)

