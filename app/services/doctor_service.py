# doctor_service.py placeholder
# app/services/doctor_service.py

"""
Doctor service layer.

Handles the core logic for:
- Creating or fetching consultations
- Listing consultations for a student or doctor
- Reading and writing messages
- Closing consultations

Routes (doctor_routes.py) can call these functions to keep things clean.
"""

from datetime import datetime
from typing import List, Optional

from app.database.db import db
from app.models.consultation import Consultation, Message


# --------- Consultation operations --------- #

def get_or_create_consultation(student_id: int, doctor_id: int) -> Consultation:
    """
    Return an existing OPEN consultation between this student and doctor,
    or create a new one if it doesn't exist.
    """
    existing = Consultation.query.filter_by(
        student_id=student_id,
        doctor_id=doctor_id,
        status="open",
    ).first()

    if existing:
        return existing

    new_cons = Consultation(
        student_id=student_id,
        doctor_id=doctor_id,
        status="open",
        created_at=datetime.utcnow(),
        closed_at=None,
    )
    db.session.add(new_cons)
    db.session.commit()
    return new_cons


def list_consultations_for_student(student_id: int, status: Optional[str] = None) -> List[Consultation]:
    """
    Get consultations for a student.
    If status is 'open' or 'closed', filter by that status.
    """
    query = Consultation.query.filter_by(student_id=student_id)
    if status in ("open", "closed"):
        query = query.filter_by(status=status)

    return query.order_by(Consultation.created_at.desc()).all()


def list_consultations_for_doctor(doctor_id: int, status: Optional[str] = None) -> List[Consultation]:
    """
    Get consultations for a doctor.
    If status is 'open' or 'closed', filter by that status.
    """
    query = Consultation.query.filter_by(doctor_id=doctor_id)
    if status in ("open", "closed"):
        query = query.filter_by(status=status)

    return query.order_by(Consultation.created_at.desc()).all()


def close_consultation(consultation_id: int, doctor_id: int) -> bool:
    """
    Close a consultation if it belongs to the given doctor.
    Returns True if closed, False if not allowed or not found.
    """
    consultation = Consultation.query.get(consultation_id)
    if not consultation:
        return False

    if consultation.doctor_id != doctor_id:
        # Not the owner's consultation
        return False

    if consultation.status == "closed":
        return True  # already closed

    consultation.status = "closed"
    consultation.closed_at = datetime.utcnow()
    db.session.commit()
    return True


# --------- Message operations --------- #

def get_messages_for_consultation(consultation_id: int) -> List[Message]:
    """
    Return messages for a given consultation, sorted by time.
    """
    return (
        Message.query.filter_by(consultation_id=consultation_id)
        .order_by(Message.created_at.asc())
        .all()
    )


def add_message_to_consultation(
    consultation_id: int,
    sender_type: str,
    sender_id: int,
    content: str,
) -> Optional[Message]:
    """
    Add a new message to a consultation.
    - sender_type should be 'student', 'doctor', or 'ai'
    - Returns the created Message or None if consultation doesn't exist or closed.
    """
    consultation = Consultation.query.get(consultation_id)
    if not consultation:
        return None

    if consultation.status != "open":
        # Don't allow messages in closed consultations
        return None

    message = Message(
        consultation_id=consultation.id,
        sender_type=sender_type,
        sender_id=sender_id,
        content=content,
        created_at=datetime.utcnow(),
    )

    db.session.add(message)
    db.session.commit()
    return message
