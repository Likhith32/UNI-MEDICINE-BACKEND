# app/utils/security.py

import os
from datetime import datetime, timedelta
from typing import Dict, Any

import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 60 * 24  # 1 day


def _get_secret_key() -> str:
    """
    Always use the SAME SECRET_KEY that Flask uses.
    Prefer app.config['SECRET_KEY'], fallback to env, then to default.
    """
    try:
        secret = current_app.config.get("SECRET_KEY")
        if secret:
            return secret
    except RuntimeError:
        # No app context yet
        pass

    return os.getenv("SECRET_KEY", "dev-secret-change-this")


# ---------- Password hashing ---------- #

def hash_password(password: str) -> str:
    """Hash a plain text password using Werkzeug."""
    return generate_password_hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Verify a plain text password against a stored hash."""
    if not password_hash:
        return False
    return check_password_hash(password_hash, plain_password)


# ---------- JWT helpers ---------- #
def create_access_token(payload: Dict[str, Any],
                        expires_minutes: int = ACCESS_TOKEN_EXPIRES_MINUTES) -> str:
    """
    Create a JWT access token.

    payload must contain:
      - "sub": user/doctor id
      - "role": "student" or "doctor"
    """
    to_encode = payload.copy()

    # 🔴 Ensure "sub" is a string (PyJWT requirement)
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])

    now = datetime.utcnow()
    expire = now + timedelta(minutes=expires_minutes)

    to_encode.update(
        {
            "iat": now,
            "exp": expire,
        }
    )

    secret = _get_secret_key()
    token = jwt.encode(to_encode, secret, algorithm=ALGORITHM)

    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def decode_access_token(token: str) -> Dict[str, Any] | None:
    """
    Decode and verify a JWT access token.

    Returns payload dict on success, or None if invalid/expired.
    """
    secret = _get_secret_key()
    try:
        decoded = jwt.decode(token, secret, algorithms=[ALGORITHM])
        print("JWT decoded OK:", decoded)  # Debug line
        return decoded
    except jwt.ExpiredSignatureError as e:
        print("JWT expired:", e)
        return None
    except jwt.InvalidTokenError as e:
        print("JWT invalid:", e)
        return None
