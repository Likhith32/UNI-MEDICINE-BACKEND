from flask import Blueprint, request, jsonify
import logging
import os

from app.utils.security import decode_access_token
from app.services.ai_service import chat_with_ai, get_disease_info
from app.services.image_service import analyze_image
from app.services.otc_service import find_best_matches

logger = logging.getLogger(__name__)

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")

# -------------------------------------------------------------------
# AUTH (JWT only, no DB calls)
# -------------------------------------------------------------------

def _get_authenticated_student():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, (jsonify({"error": "Authorization header missing or invalid."}), 401)

    token = auth_header.split(" ", 1)[1].strip()

    try:
        payload = decode_access_token(token)
    except Exception as e:
        logger.warning("JWT decode failed: %s", e)
        return None, (jsonify({"error": "Invalid or expired token."}), 401)

    if payload.get("role") != "student":
        return None, (jsonify({"error": "Only students can access this endpoint."}), 403)

    return payload, None


def _build_student_context_from_jwt(payload):
    return {
        "id": payload.get("sub"),
        "role": payload.get("role"),
        "name": payload.get("name", "Student"),
        "level": payload.get("level", "UG"),
        "branch": payload.get("branch", ""),
        "year": payload.get("year"),
        "department": payload.get("department"),
        "hostel": payload.get("hostel"),
    }

# -------------------------------------------------------------------
# OTC LOGIC
# -------------------------------------------------------------------

def _build_otc_block(symptom_text, age=None, top_k=3):
    symptom_text = (symptom_text or "").strip()

    if not symptom_text:
        return {
            "symptoms": "",
            "matches": [],
            "disclaimer": (
                "This is not a diagnosis. Always consult a qualified doctor "
                "before taking any medicine."
            ),
        }

    try:
        matches = find_best_matches(symptom_text, top_k=top_k)
    except Exception:
        logger.exception("OTC engine failure")
        return {
            "symptoms": symptom_text,
            "matches": [],
            "disclaimer": (
                "OTC suggestion service is temporarily unavailable. "
                "Please consult a doctor."
            ),
        }

    result_matches = []

    for cond in matches or []:
        disease_name = cond.get("name", "")
        try:
            expl = get_disease_info(disease_name) or {}
        except Exception:
            expl = {}

        result_matches.append({
            "slug": cond.get("slug"),
            "name": disease_name,
            "score_note": cond.get("score_note") or cond.get("score"),
            "recommended_otc_medicines": cond.get("recommended_otc_medicines", []),
            "precautions": cond.get("precautions", []),
            "when_to_see_doctor": cond.get("when_to_see_doctor", []),
            "llm_explanation": expl.get("explanation"),
        })

    return {
        "symptoms": symptom_text,
        "matches": result_matches,
        "disclaimer": (
            "This is NOT a diagnosis. OTC suggestions are generic and "
            "may not suit everyone. Always consult a qualified doctor."
        ),
    }

# -------------------------------------------------------------------
# MAIN CHAT ENDPOINT
# -------------------------------------------------------------------

@ai_bp.route("/chat", methods=["POST"])
def ai_chat():
    student_payload, error = _get_authenticated_student()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    age = data.get("age")

    if not message:
        return jsonify({"error": "Message is required."}), 400

    student_context = _build_student_context_from_jwt(student_payload)

    try:
        reply = chat_with_ai(
            user_context=student_context,
            message=message,
        )
    except Exception:
        logger.exception("AI chat failed")
        return jsonify({
            "error": "AI service is currently unavailable. Please try later."
        }), 500

    otc_block = _build_otc_block(
        symptom_text=message,
        age=age,
        top_k=3,
    )

    return jsonify({
        "reply": reply,
        "otc": otc_block,
    }), 200

# -------------------------------------------------------------------
# OTC-ONLY ENDPOINT
# -------------------------------------------------------------------

@ai_bp.route("/symptom-otc", methods=["POST"])
def symptom_otc():
    student_payload, error = _get_authenticated_student()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    symptoms = (data.get("symptoms") or "").strip()
    age = data.get("age")

    if not symptoms:
        return jsonify({"error": "symptoms field is required."}), 400

    otc_block = _build_otc_block(
        symptom_text=symptoms,
        age=age,
        top_k=3,
    )

    return jsonify(otc_block), 200

# -------------------------------------------------------------------
# IMAGE ANALYSIS ENDPOINT
# -------------------------------------------------------------------

@ai_bp.route("/image", methods=["POST"])
def ai_image():
    student_payload, error = _get_authenticated_student()
    if error:
        return error

    if "image" not in request.files:
        return jsonify({"error": "Image file is required."}), 400

    image_file = request.files["image"]

    if image_file.filename == "":
        return jsonify({"error": "Invalid image file."}), 400

    temp_path = f"/tmp/{image_file.filename}"
    image_file.save(temp_path)

    try:
        result = analyze_image(
            file_path=temp_path,
            user_id=student_payload.get("sub"),
        )
    except Exception:
        logger.exception("Image analysis failed")
        return jsonify({
            "error": "Image analysis service is currently unavailable."
        }), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return jsonify(result), 200

