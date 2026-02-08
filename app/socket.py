from flask_socketio import SocketIO, emit, join_room
from app.database.db import db
from app.models import Message
from app.services.notification_service import send_push_to_user

socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode="eventlet"
)

def init_socket(app):
    socketio.init_app(app)

@socketio.on("join")
def handle_join(data):
    join_room(str(data["user_id"]))

@socketio.on("send_message")
def handle_message(data):
    message = Message(
        consultation_id=data["consultation_id"],
        sender_id=data["sender_id"],
        sender_role=data["sender_role"],
        content=data["message"]
    )

    db.session.add(message)
    db.session.commit()

    # Realtime
    emit("new_message", {
        "consultation_id": data["consultation_id"],
        "sender_id": data["sender_id"],
        "message": data["message"]
    }, room=str(data["receiver_id"]))

    # Push notification
    send_push_to_user(
        data["receiver_id"],
        "New Message",
        "You received a new consultation message"
    )
