# backend/app/config.py

import os
from dotenv import load_dotenv
from sqlalchemy.pool import NullPool

# -----------------------------
# Base directory & .env loading
# -----------------------------
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

if os.path.exists(ENV_PATH):
    # allow .env to override system environment variables
    load_dotenv(ENV_PATH, override=True)


# -----------------------------
# Config class
# -----------------------------
class Config:
    # Database URL handling
    raw_db_url = os.getenv("DATABASE_URL", "")

    # Fix old postgres:// scheme
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace(
            "postgres://", "postgresql://", 1
        )

    # Optional debug print (safe)
    if raw_db_url:
        print(
            "Using DB URL:",
            "postgresql://***:***@" + raw_db_url.split("@", 1)[1]
        )
    else:
        print("WARNING: DATABASE_URL is missing")

    SQLALCHEMY_DATABASE_URI = raw_db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ✅ Correct SQLAlchemy engine options for Supabase / remote Postgres
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": NullPool,     # Supabase manages pooling
        "connect_args": {
            "sslmode": "require",
        },
        "pool_pre_ping": True,     # auto-reconnect if connection dies
        "pool_recycle": 300,       # recycle connections every 5 minutes
    }

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-this")


# -----------------------------
# Environment-specific config
# -----------------------------
if os.environ.get("FLASK_ENV") == "production":
    # Nothing special yet, keep it valid
    pass
