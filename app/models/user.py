from datetime import datetime
from app.database.db import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    level = db.Column(db.String(10), nullable=False)  # UG / PG

    branch = db.Column(db.String(100), nullable=True)       # UG
    year = db.Column(db.Integer, nullable=True)             # UG
    department = db.Column(db.String(100), nullable=True)   # PG

    hostel = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    consultations = db.relationship(
        "Consultation",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    push_subscriptions = db.relationship(
        "PushSubscription",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.name} ({self.level})>"
