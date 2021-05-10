"""The Flask App."""

# pylint: disable=broad-except

import redis, os, json

from flask import (
    Flask,
    Response,
    abort,
    jsonify,
    request,
    render_template
)
from flask_socketio import SocketIO, emit

import eventlet
eventlet.monkey_patch()

TOPIC = 'event'
PORT = os.getenv('PORT', 80)
URL = os.getenv('URL', 'http://localhost')
PATH = os.getenv('PATH', None)

app = Flask(__name__)
socketio = SocketIO(
    app,
    message_queue='redis://',
    path=PATH
)

values = {
    'name': 'Widget',
    'url': URL
}

@app.errorhandler(404)
def resource_not_found(exception):
    """Returns exceptions as part of a json."""
    return jsonify(error=str(exception)), 404

@app.route("/widget")
def home():
    return render_template('index.html', **values)

@app.route("/publish", methods=["POST", "GET"])
def publish():
    """Posts a message to the pubsub topic"""
    if request.method == "POST":
        data = request.json
    if 'audioURL' in data.keys():
        socketio.emit('audio', {'audioURL': data['audioURL']}, broadcast=True)
    socketio.emit('message', {'data': data}, broadcast=True)
    return Response(status=204)

@socketio.on('connect')
def test_connect():
    emit('after connect',  {'data':'Connected'})

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=PORT)
