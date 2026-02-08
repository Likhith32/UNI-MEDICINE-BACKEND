from datetime import datetime
from app.database.db import db


class Consultation(db.Model):
    __tablename__ = "consultations"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    doctor_id = db.Column(
        db.Integer,
        db.ForeignKey("doctors.id"),
        nullable=False
    )

    status = db.Column(db.String(20), default="open", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)

    student = db.relationship(
        "User",
        back_populates="consultations"
    )

    doctor = db.relationship(
        "Doctor",
        back_populates="consultations"
    )

    messages = db.relationship(
        "Message",
        back_populates="consultation",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Consultation {self.id} status={self.status}>"
