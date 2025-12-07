from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

connected_users = {}


@app.route("/")
def login():
    return render_template("login.html")


@app.route("/chat", methods=["POST"])
def chat():
    username = request.form["username"]
    room = request.form["room"]
    return render_template("chat.html", username=username, room=room)


@socketio.on("chat message")
def handle_chat(json):
    emit("chat message", json, broadcast=True, to=json["room"])


@socketio.on("writing")
def handle_writing(json):
    emit("writing", json, broadcast=True, to=json["room"])


@socketio.on("connect")
def on_connect(auth):
    if not auth:
        return

    username = auth.get("username")
    room = auth.get("room")

    if not username or not room:
        return

    connected_users[request.sid] = (username, room)
    join_room(room)
    emit("connected users", connected_users, broadcast=True, to=room)


@socketio.on("disconnect")
def on_disconnect():
    user = connected_users.get(request.sid)
    if user:
        room = user[1]
        leave_room(room)
        del connected_users[request.sid]
        emit("connected users", connected_users, broadcast=True, to=room)


if __name__ == "__main__":
    socketio.run(app)
