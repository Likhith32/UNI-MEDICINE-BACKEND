from datetime import datetime
from app.database.db import db


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)

    consultation_id = db.Column(
        db.Integer,
        db.ForeignKey("consultations.id"),
        nullable=False
    )

    sender_role = db.Column(db.String(20), nullable=False)  # student | doctor | ai
    sender_id = db.Column(db.Integer, nullable=False)

    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    consultation = db.relationship(
        "Consultation",
        back_populates="messages"
    )

    def __repr__(self):
        return f"<Message {self.id} {self.sender_role}>"
