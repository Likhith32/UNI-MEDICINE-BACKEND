# places_routes.py placeholder
# app/routes/places_routes.py

from flask import Blueprint, request, jsonify

from app.database.db import db
from app.models.place import Place
from app.utils.security import decode_access_token

places_bp = Blueprint("places", __name__, url_prefix="/api/places")


# ---------- Helpers ---------- #

ALLOWED_HOSTELS = {
    "Boys Hostel 1",
    "Boys Hostel 2",
    "Girls Hostel 1",
    "Girls Hostel 2",
}

ALLOWED_TYPES = {"hospital", "medical_shop"}


def _get_current_identity_optional():
    """
    Optional auth:
    - If token present and valid → return (role, id)
    - If no/invalid token → return (None, None)
    For nearby places, you may allow unauthenticated access OR
    restrict it; change behavior as you like.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, None

    token = auth_header.split(" ", 1)[1].strip()

    try:
        payload = decode_access_token(token)
    except Exception:
        return None, None

    return payload.get("role"), payload.get("sub")


# ---------- Routes ---------- #

@places_bp.route("", methods=["GET"])
def get_places():
    """
    Get nearby places (medical shops & hospitals).

    Query params:
      - hostel (optional but recommended): Boys Hostel 1, Boys Hostel 2, Girls Hostel 1, Girls Hostel 2
      - type   (optional): hospital | medical_shop

    Examples:
      GET /api/places?hostel=Boys%20Hostel%201
      GET /api/places?hostel=Boys%20Hostel%201&type=hospital
      GET /api/places  (returns all places)
    """
    # Optional: read user role/id (not strictly needed for this endpoint)
    role, user_id = _get_current_identity_optional()

    hostel = request.args.get("hostel")
    place_type = request.args.get("type")

    query = Place.query

    # Filter by hostel if provided and valid
    if hostel:
        if hostel not in ALLOWED_HOSTELS:
            return jsonify({"error": "Invalid hostel value."}), 400
        query = query.filter_by(hostel_tag=hostel)

    # Filter by type if provided and valid
    if place_type:
        place_type = place_type.lower()
        if place_type not in ALLOWED_TYPES:
            return jsonify({"error": "Invalid type. Use 'hospital' or 'medical_shop'."}), 400
        query = query.filter_by(type=place_type)

    places = query.order_by(Place.name.asc()).all()

    result = []
    for p in places:
        result.append(
            {
                "id": p.id,
                "name": p.name,
                "type": p.type,  # "hospital" or "medical_shop"
                "address": p.address,
                "hostel_tag": p.hostel_tag,
                "phone": p.phone,
                "open_hours": p.open_hours,
                "latitude": p.latitude,
                "longitude": p.longitude,
            }
        )

    return jsonify(result), 200


@places_bp.route("/<int:place_id>", methods=["GET"])
def get_place_by_id(place_id):
    """
    Get detailed info about a single place by its ID.
    Example:
      GET /api/places/3
    """
    place = Place.query.get(place_id)
    if not place:
        return jsonify({"error": "Place not found."}), 404

    return jsonify(
        {
            "id": place.id,
            "name": place.name,
            "type": place.type,
            "address": place.address,
            "hostel_tag": place.hostel_tag,
            "phone": place.phone,
            "open_hours": place.open_hours,
            "latitude": place.latitude,
            "longitude": place.longitude,
        }
    ), 200


# ---------- (Optional) Admin/Seed Endpoints ---------- #
# For a college project, you might pre-insert places via a script or DB GUI.
# If you want to add from API, you can protect these with an admin token.

@places_bp.route("", methods=["POST"])
def add_place():
    """
    (Optional) Add a new place – for admin/seed purposes.
    You can remove this route if you don't need API-based creation.

    Expected JSON:
    {
      "name": "Campus Health Clinic",
      "type": "hospital",
      "address": "Near Admin Block",
      "hostel_tag": "Boys Hostel 1",
      "phone": "9876543210",
      "open_hours": "9 AM - 6 PM",
      "latitude": 17.12345,
      "longitude": 78.54321
    }
    """
    # TODO: optionally restrict this to admin using role from JWT
    data = request.get_json() or {}

    name = (data.get("name") or "").strip()
    place_type = (data.get("type") or "").strip().lower()
    address = (data.get("address") or "").strip()
    hostel_tag = (data.get("hostel_tag") or "").strip()
    phone = (data.get("phone") or "").strip()
    open_hours = (data.get("open_hours") or "").strip()
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    errors = []
    if not name:
        errors.append("Name is required.")
    if place_type not in ALLOWED_TYPES:
        errors.append("Type must be 'hospital' or 'medical_shop'.")
    if hostel_tag not in ALLOWED_HOSTELS:
        errors.append("hostel_tag must be one of the known hostels.")
    if not address:
        errors.append("Address is required.")

    if errors:
        return jsonify({"errors": errors}), 400

    place = Place(
        name=name,
        type=place_type,
        address=address,
        hostel_tag=hostel_tag,
        phone=phone or None,
        open_hours=open_hours or None,
        latitude=latitude,
        longitude=longitude,
    )

    db.session.add(place)
    db.session.commit()

    return jsonify(
        {
            "id": place.id,
            "name": place.name,
            "type": place.type,
            "address": place.address,
            "hostel_tag": place.hostel_tag,
            "phone": place.phone,
            "open_hours": place.open_hours,
            "latitude": place.latitude,
            "longitude": place.longitude,
        }
    ), 201
