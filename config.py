import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(16))
    DB_PATH = os.getenv("DB_PATH", "users_web.db")
    SPIKE_APP_ID = os.getenv("SPIKE_APP_ID")
    SPIKE_HMAC_KEY = os.getenv("SPIKE_HMAC_KEY")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # SESSION_COOKIE_SECURE = True  # enable in production