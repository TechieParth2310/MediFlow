"""
Application Configuration
Industry-level configuration management
"""
import os
from datetime import timedelta


class Config:
    """Base configuration class"""

    # Application Settings
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'dev-secret-key-change-in-production-2024'

    # Database Configuration
    DB_PATH = os.environ.get('DB_PATH') or os.path.join(
        os.path.dirname(__file__), 'hospital.db'
    )

    # Session Configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Set True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

    # File Upload Settings
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

    # Email Configuration (Render-friendly)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True

    # IMPORTANT FIX — remove placeholder blocking
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    # Default sender (should match Gmail account for deliverability)
    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER") or MAIL_USERNAME

    # Pagination
    APPOINTMENTS_PER_PAGE = 10
    DOCTORS_PER_PAGE = 12

    # Appointment Settings
    DEFAULT_SLOT_DURATION = 30  # minutes
    BOOKING_ADVANCE_DAYS = 30
    CANCELLATION_HOURS = 24


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # HTTPS only


class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    DB_PATH = os.path.join(os.path.dirname(__file__), 'hospital_test.db')


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
