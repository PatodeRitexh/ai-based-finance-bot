import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base application configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-key-bfsi-2026")
    DEBUG = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true")

    # Instance directory for SQLite database
    INSTANCE_DIR = BASE_DIR / "instance"
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)

    # SQLite Database URI
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{INSTANCE_DIR / 'finance.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False  # Set to True when HTTPS is enabled in production
    PERMANENT_SESSION_LIFETIME = 86400 * 7  # 7 days

    # Gemini AI configuration
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash").strip()

    # Application settings
    DEFAULT_CURRENCY = "INR"
    DEFAULT_CURRENCY_SYMBOL = "₹"
