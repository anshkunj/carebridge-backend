import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Basic Security
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")

    # App Config
    DEBUG = os.getenv("FLASK_ENV") == "development"

    # Request Limits
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB limit

    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")

    # Rate Limiting
    RATE_LIMIT = os.getenv("RATE_LIMIT", "10 per minute")

    # Medical Disclaimer
    MEDICAL_DISCLAIMER = (
        "This AI tool is for informational purposes only and "
        "does not replace professional medical advice."
    )