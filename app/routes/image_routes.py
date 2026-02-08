# app/routes/image_routes.py

import os
import uuid
from flask import Blueprint, request, jsonify, current_app

from app.models.user import User
from app.utils.security import decode_access_token
from app.services.image_service import analyze_image

image_bp = Blueprint("image", __name__, url_prefix="/api/image")


# -------------------- Helpers -------------------- #

def _get_authenticated_student():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, (jsonify({"error": "Authorization header missing or invalid."}), 401)

    token = auth_header.split(" ", 1)[1].strip()

    try:
        payload = decode_access_token(token)
    except Exception:
        return None, (jsonify({"error": "Invalid or expired token."}), 401)

    if payload.get("role") != "student":
        return None, (jsonify({"error": "Only students can access this endpoint."}), 403)

    user_id = payload.get("sub")
    user = User.query.get(user_id)
    if not user:
        return None, (jsonify({"error": "User not found."}), 404)

    return user, None


def _allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in {"jpg", "jpeg", "png", "bmp"}


# -------------------- Routes -------------------- #

@image_bp.route("/diagnose", methods=["POST"])
def diagnose_image():
    """
    SAFE image-based skin observation endpoint.

    - Requires student JWT
    - Accepts image under key 'image' or 'file'
    - Uses AI to describe visible features and provide general guidance
    - DOES NOT diagnose disease

    Response example:
    {
      "predicted_condition": "acne",
      "confidence": 0.82,
      "explanation": "...",
      "note": "This is NOT a medical diagnosis..."
    }
    """

    student, error_response = _get_authenticated_student()
    if error_response:
        return error_response

    # Accept "image" or "file"
    file = request.files.get("image") or request.files.get("file")
    if not file or file.filename == "":
        return (
            jsonify(
                {
                    "error": (
                        "Image file is required "
                        "(use field name 'image' or 'file')."
                    )
                }
            ),
            400,
        )

    if not _allowed_file(file.filename):
        return (
            jsonify(
                {
                    "error": (
                        "Unsupported file type. "
                        "Allowed: jpg, jpeg, png, bmp."
                    )
                }
            ),
            400,
        )

    # Prepare upload folder
    upload_folder = os.path.join(current_app.instance_path, "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    # Generate unique filename
    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    file_path = os.path.join(upload_folder, unique_name)

    # Save file ONCE
    file.save(file_path)

    # Analyze image
    try:
        result = analyze_image(file_path=file_path, user_id=student.id)
    except Exception as e:
        print("Image analysis error:", e)

        # Cleanup on failure
        try:
            os.remove(file_path)
        except OSError:
            pass

        return (
            jsonify(
                {
                    "error": (
                        "Image analysis failed. "
                        "Please try again later or consult a doctor."
                    )
                }
            ),
            500,
        )

    # Cleanup file after analysis
    try:
        os.remove(file_path)
    except OSError:
        pass

    # Safety fallback (extra protection)
    if "note" not in result:
        result["note"] = (
            "This is an AI-generated visual observation only. "
            "It is NOT a medical diagnosis. "
            "Please consult a qualified doctor."
        )

    return jsonify(result), 200
