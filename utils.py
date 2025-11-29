"""
Database connection and utility functions
"""
import sqlite3
from contextlib import contextmanager
import hashlib
from functools import wraps
from flask import session, redirect, url_for, flash


def get_db_connection(config):
    """Create and return a database connection"""
    db_path = getattr(config, "DB_PATH", "hospital.db")
    connection = sqlite3.connect(
        db_path,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        check_same_thread=False
    )
    connection.row_factory = sqlite3.Row
    # Enforce FK constraints for SQLite
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def get_db_cursor(config):
    """Context manager for database operations"""
    connection = get_db_connection(config)
    cursor = connection.cursor()
    try:
        yield cursor
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()


def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password, hashed_password):
    """Verify password against hash"""
    return hash_password(plain_password) == hashed_password


# ============================================
# DECORATORS FOR ROUTE PROTECTION
# ============================================

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Decorator to require specific role(s)"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login to access this page.', 'error')
                return redirect(url_for('auth.login'))

            if session.get('role') not in roles:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('main.index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def patient_required(f):
    """Decorator for patient-only routes"""
    return role_required('patient')(f)


def doctor_required(f):
    """Decorator for doctor-only routes"""
    return role_required('doctor')(f)


def admin_required(f):
    """Decorator for admin-only routes"""
    return role_required('admin')(f)
