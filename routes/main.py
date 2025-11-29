"""
Main Blueprint
Handles home page and general routes
"""
from flask import Blueprint, render_template, session
from utils import get_db_cursor
from models import Doctor

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page"""
    try:
        with get_db_cursor(main_bp.config) as cursor:
            # Get featured doctors (limit 6)
            featured_doctors = Doctor.get_all_verified(cursor, limit=6)

            # Get specializations count
            cursor.execute("""
                SELECT specialization, COUNT(*) as count
                FROM doctors
                WHERE is_verified = 1
                GROUP BY specialization
                ORDER BY count DESC
                LIMIT 6
            """)
            specializations = cursor.fetchall()

            return render_template(
                'home.html',
                featured_doctors=featured_doctors,
                specializations=specializations,
                title='Welcome to Doctor Appointment System'
            )

    except Exception as e:
        # If database connection fails, show basic home page
        return render_template(
            'home.html',
            featured_doctors=[],
            specializations=[],
            title='Welcome to Doctor Appointment System'
        )


@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html', title='About Us')


@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html', title='Contact Us')
