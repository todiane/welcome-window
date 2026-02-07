import os
from datetime import timedelta


class Config:
    """Application configuration"""

    # Basic Flask config
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite:///welcome_window.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session config
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # SocketIO config
    SOCKETIO_PING_TIMEOUT = 60
    SOCKETIO_PING_INTERVAL = 25

    # Admin credentials (change these!)
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME") or "admin"
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD") or "changeme123"

    # Feature flags
    REQUIRE_NAMES = False
    LOG_VISITS = True
    MAX_MESSAGE_LENGTH = 500

    # Site info
    SITE_NAME = "Diane's Welcome Window"
    SITE_TAGLINE = "Drop by for a chat when the light is on"
