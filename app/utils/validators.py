# validators.py placeholder
# app/utils/validators.py

"""
Centralized validation utilities for the telemedicine app.

Used by:
- auth_routes.py (student & doctor login)
- places_routes.py (optional validation)
- future forms (e.g., symptom submissions)

All validators should return:
    (bool, message)
or raise a ValueError when used in service-level code.
"""

from typing import Dict, List, Tuple, Optional

# Allowed constants (to keep consistent with other files)
ALLOWED_HOSTELS = {
    "Boys Hostel 1",
    "Boys Hostel 2",
    "Girls Hostel 1",
    "Girls Hostel 2",
}

ALLOWED_LEVELS = {"UG", "PG"}

ALLOWED_PLACE_TYPES = {"hospital", "medical_shop"}


# ---------------------- Core Student Validation ---------------------- #

def validate_student_login_payload(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate a student quick login payload.

    Returns:
        (True, []) if valid,
        (False, [error messages]) if invalid.
    """

    errors = []

    name = (data.get("name") or "").strip()
    level = (data.get("level") or "").strip().upper()
    hostel = (data.get("hostel") or "").strip()
    branch = (data.get("branch") or "").strip()
    year = data.get("year")
    department = (data.get("department") or "").strip()

    # Name
    if not name:
        errors.append("Name is required.")

    # Level (UG / PG)
    if level not in ALLOWED_LEVELS:
        errors.append("Level must be 'UG' or 'PG'.")

    # Hostel
    if hostel not in ALLOWED_HOSTELS:
        errors.append("Hostel is invalid or missing.")

    # UG validation
    if level == "UG":
        if not branch:
            errors.append("Branch is required for UG students.")
        try:
            year_int = int(year)
            if year_int < 1 or year_int > 4:
                errors.append("Year must be between 1 and 4 for UG students.")
        except (ValueError, TypeError):
            errors.append("Year must be a number for UG students.")

    # PG validation
    if level == "PG":
        if not department:
            errors.append("Department is required for PG students.")

    return (len(errors) == 0, errors)


# ---------------------- Doctor Login Validation ---------------------- #

def validate_doctor_login_payload(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate a doctor login payload.

    Required:
        - email
        - password
    """
    errors = []
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email:
        errors.append("Email is required.")
    elif "@" not in email:
        errors.append("Invalid email format.")

    if not password:
        errors.append("Password is required.")

    return (len(errors) == 0, errors)


# ---------------------- Places Validation ---------------------- #

def validate_place_payload(data: Dict) -> Tuple[bool, List[str]]:
    """
    Validate the JSON body for creating a new place (hospital or medical shop).

    Expected:
    {
      "name": "Apollo Pharmacy",
      "type": "medical_shop",
      "address": "Main Road",
      "hostel_tag": "Boys Hostel 1",
      ...
    }
    """
    errors = []

    name = (data.get("name") or "").strip()
    place_type = (data.get("type") or "").strip().lower()
    address = (data.get("address") or "").strip()
    hostel_tag = (data.get("hostel_tag") or "").strip()

    if not name:
        errors.append("Place name is required.")
    if place_type not in ALLOWED_PLACE_TYPES:
        errors.append("Type must be either 'hospital' or 'medical_shop'.")
    if not address:
        errors.append("Address is required.")
    if hostel_tag not in ALLOWED_HOSTELS:
        errors.append("hostel_tag must be one of the known hostels.")

    return (len(errors) == 0, errors)


# ---------------------- Generic Helpers ---------------------- #

def validate_nonempty_fields(data: Dict, required_fields: List[str]) -> Tuple[bool, List[str]]:
    """
    Simple helper to check if required fields are non-empty in a dict.
    """
    errors = []
    for field in required_fields:
        if not (data.get(field) or "").strip():
            errors.append(f"{field} is required.")
    return (len(errors) == 0, errors)


def is_valid_hostel(hostel: str) -> bool:
    """
    Return True if hostel name is allowed.
    """
    return hostel in ALLOWED_HOSTELS


def is_valid_level(level: str) -> bool:
    """
    Return True if level is UG or PG.
    """
    return level.upper() in ALLOWED_LEVELS
