# app/routes/doctors_list_routes.py

from flask import Blueprint, jsonify
from app.models.doctor import Doctor  # or from app.models.user import Doctor if that's where it lives

doctors_bp = Blueprint("doctors", __name__)

@doctors_bp.route("/doctors", methods=["GET"])
def list_doctors():
    """
    Return a list of all registered doctors.
    Used by the frontend /doctor-connect page (GET /api/doctors).
    """
    doctors = Doctor.query.order_by(Doctor.name.asc()).all()

    result = []
    for d in doctors:
        result.append(
            {
                "id": d.id,
                "name": d.name,
                "email": d.email,
                "specialization": getattr(d, "specialization", None),
            }
        )

    return jsonify(result), 200
