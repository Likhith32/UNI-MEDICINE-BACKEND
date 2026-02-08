# app/routes/auth_routes.py

from flask import Blueprint, request, jsonify
from datetime import datetime
from app.database.db import db# ✅ use the SAME db instance from app/__init__.py
from app.models.user import User
from app.models.doctor import Doctor
from app.utils.security import create_access_token, verify_password, decode_access_token

auth_bp = Blueprint("auth", __name__)  # ✅ no url_prefix here — added in create_app()


# --------- Constants --------- #

ALLOWED_HOSTELS = {
    "Boys Hostel 1",
    "Boys Hostel 2",
    "Girls Hostel 1",
    "Girls Hostel 2",
}

ALLOWED_LEVELS = {"UG", "PG"}


# --------- Validation Helper --------- #
def validate_student_payload(data):
    """Validate student login input."""
    errors = []

    name = data.get("name", "").strip()
    level = data.get("level", "").strip().upper()
    hostel = data.get("hostel", "").strip()

    if not name:
        errors.append("Name is required.")
    if level not in ALLOWED_LEVELS:
        errors.append("Level must be 'UG' or 'PG'.")
    if hostel not in ALLOWED_HOSTELS:
        errors.append("Hostel is invalid.")

    # UG-specific checks
    if level == "UG":
        branch = data.get("branch", "").strip()
        year = data.get("year")
        if not branch:
            errors.append("Branch is required for UG students.")
        if year is None:
            errors.append("Year is required for UG students.")
        else:
            try:
                year_int = int(year)
                if year_int < 1 or year_int > 4:
                    errors.append("Year must be between 1 and 4.")
            except ValueError:
                errors.append("Year must be a number.")

    return errors


# --------- Routes --------- #

@auth_bp.route("/student-login", methods=["POST"])
def student_login():
    """Quick student login — creates the user if not found."""
    data = request.get_json() or {}

    errors = validate_student_payload(data)
    if errors:
        return jsonify({"errors": errors}), 400

    name = data["name"].strip()
    level = data["level"].strip().upper()
    hostel = data["hostel"].strip()
    branch = data.get("branch")
    year = data.get("year")
    department = data.get("department")

    if level == "UG" and year is not None:
        year = int(year)

    # Find or create the user
    query = User.query.filter_by(name=name, level=level, hostel=hostel)
    if level == "UG":
        query = query.filter_by(branch=branch, year=year)
    else:
        query = query.filter_by(department=department)

    user = query.first()

    if not user:
        user = User(
            name=name,
            level=level,
            branch=branch if level == "UG" else None,
            year=year if level == "UG" else None,
            department=department if level == "PG" else None,
            hostel=hostel,
            created_at=datetime.utcnow(),
        )
        db.session.add(user)
        db.session.commit()

    # Create JWT token
    token = create_access_token({"sub": user.id, "role": "student"})

    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "level": user.level,
            "branch": user.branch,
            "year": user.year,
            "department": getattr(user, "department", None),
            "hostel": user.hostel,
        },
    }), 200


@auth_bp.route("/doctor-login", methods=["POST"])
def doctor_login():
    """Login for doctors using email/password."""
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    doctor = Doctor.query.filter_by(email=email).first()
    if not doctor or not verify_password(password, doctor.password_hash):
        return jsonify({"error": "Invalid credentials."}), 401

    token = create_access_token({"sub": doctor.id, "role": "doctor"})

    return jsonify({
        "token": token,
        "doctor": {
            "id": doctor.id,
            "name": doctor.name,
            "email": doctor.email,
            "specialization": doctor.specialization,
        },
    }), 200


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    """Return the current authenticated user (student or doctor)."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return jsonify({"error": "Authorization header missing or invalid."}), 401

    token = auth_header.split(" ", 1)[1].strip()

    try:
        payload = decode_access_token(token)
    except Exception:
        return jsonify({"error": "Invalid or expired token."}), 401

    role = payload.get("role")
    user_id = payload.get("sub")

    if role == "student":
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found."}), 404
        return jsonify({
            "role": "student",
            "user": {
                "id": user.id,
                "name": user.name,
                "level": user.level,
                "branch": user.branch,
                "year": user.year,
                "department": getattr(user, "department", None),
                "hostel": user.hostel,
            },
        }), 200

    elif role == "doctor":
        doctor = Doctor.query.get(user_id)
        if not doctor:
            return jsonify({"error": "Doctor not found."}), 404
        return jsonify({
            "role": "doctor",
            "doctor": {
                "id": doctor.id,
                "name": doctor.name,
                "email": doctor.email,
                "specialization": doctor.specialization,
            },
        }), 200

    return jsonify({"error": "Unknown role in token."}), 400
