"""
Authentication Blueprint
Handles login, registration, and logout for all user types
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils import get_db_cursor, hash_password, verify_password
from models import User, Doctor, Patient
from email_service import get_email_service
import re

auth_bp = Blueprint('auth', __name__)


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Validate password strength
    At least 8 characters, 1 uppercase, 1 lowercase, 1 number
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"


@auth_bp.route('/login')
def login():
    """Show unified login page"""
    if 'user_id' in session:
        # Redirect based on role
        role = session.get('role')
        if role == 'doctor':
            return redirect(url_for('doctor.dashboard'))
        elif role == 'patient':
            return redirect(url_for('patient.dashboard'))
        elif role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('main.index'))

    return render_template('auth/login.html', title='Login')


@auth_bp.route('/login', methods=['POST'])
def login_post():
    """Handle login submission"""
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', 'patient')  # patient, doctor, admin

    # Validation
    if not email or not password:
        flash('Please fill in all fields', 'error')
        return redirect(url_for('auth.login'))

    if not validate_email(email):
        flash('Invalid email format', 'error')
        return redirect(url_for('auth.login'))

    try:
        with get_db_cursor(auth_bp.config) as cursor:
            # Get user by email
            user = User.get_by_email(cursor, email)

            if not user:
                flash('Invalid email or password', 'error')
                return redirect(url_for('auth.login'))

            # Verify password
            if not verify_password(password, user['password']):
                flash('Invalid email or password', 'error')
                return redirect(url_for('auth.login'))

            # Check if user is active
            if not user['is_active']:
                flash(
                    'Your account has been deactivated. Please contact support.', 'error')
                return redirect(url_for('auth.login'))

            # Check role match
            if user['role'] != role:
                flash(f'Please login using the {user["role"]} portal', 'error')
                return redirect(url_for('auth.login'))

            # Set session
            session.permanent = True
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['role'] = user['role']

            # Get profile info
            if user['role'] == 'doctor':
                doctor = Doctor.get_by_user_id(cursor, user['id'])
                if doctor:
                    session['profile_id'] = doctor['id']
                    session['full_name'] = doctor['full_name']
                flash(f'Welcome back, Dr. {doctor["full_name"]}!', 'success')
                return redirect(url_for('doctor.dashboard'))

            elif user['role'] == 'patient':
                patient = Patient.get_by_user_id(cursor, user['id'])
                if patient:
                    session['profile_id'] = patient['id']
                    session['full_name'] = patient['full_name']
                flash(f'Welcome back, {patient["full_name"]}!', 'success')
                return redirect(url_for('patient.dashboard'))

            else:  # admin
                session['full_name'] = 'Admin'
                flash('Welcome, Admin!', 'success')
                return redirect(url_for('admin.dashboard'))

    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/register/patient')
def register_patient():
    """Show patient registration page"""
    return render_template('auth/register_patient.html', title='Patient Registration')


@auth_bp.route('/register/patient', methods=['POST'])
def register_patient_post():
    """Handle patient registration"""
    # Get form data
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    full_name = request.form.get('full_name', '').strip()
    phone = request.form.get('phone', '').strip()
    date_of_birth = request.form.get('date_of_birth')
    gender = request.form.get('gender')
    blood_group = request.form.get('blood_group')
    address = request.form.get('address', '').strip()

    # Validation
    if not all([email, password, confirm_password, full_name, phone]):
        flash('Please fill in all required fields', 'error')
        return redirect(url_for('auth.register_patient'))

    if not validate_email(email):
        flash('Invalid email format', 'error')
        return redirect(url_for('auth.register_patient'))

    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return redirect(url_for('auth.register_patient'))

    is_valid, message = validate_password(password)
    if not is_valid:
        flash(message, 'error')
        return redirect(url_for('auth.register_patient'))

    try:
        with get_db_cursor(auth_bp.config) as cursor:
            # Check if email already exists
            existing_user = User.get_by_email(cursor, email)
            if existing_user:
                flash('Email already registered. Please login.', 'error')
                return redirect(url_for('auth.register_patient'))

            # Create user
            password_hash = hash_password(password)
            user_id = User.create(cursor, email, password_hash, 'patient')

            # Create patient profile
            Patient.create(
                cursor, user_id, full_name,
                phone=phone,
                date_of_birth=date_of_birth if date_of_birth else None,
                gender=gender,
                blood_group=blood_group,
                address=address
            )

            # Send welcome email
            try:
                email_service = get_email_service(auth_bp.config)
                print(f"\n{'='*60}")
                print(f"📧 EMAIL SERVICE CHECK - Patient Registration")
                print(f"{'='*60}")
                print(f"📧 Email service status: {'ENABLED ✅' if email_service.enabled else 'DISABLED ❌ (no credentials)'}")
                print(f"📧 MAIL_USERNAME: {auth_bp.config.MAIL_USERNAME or 'NOT SET'}")
                print(f"📧 MAIL_PASSWORD: {'SET ✅' if auth_bp.config.MAIL_PASSWORD else 'NOT SET ❌'}")
                print(f"📧 MAIL_SERVER: {auth_bp.config.MAIL_SERVER}")
                print(f"📧 MAIL_PORT: {auth_bp.config.MAIL_PORT}")
                
                if email_service.enabled:
                    print(f"📧 Attempting to send welcome email to: {email}")
                    print(f"📧 Patient name: {full_name}")
                    email_service.send_welcome_email(email, full_name, 'patient')
                    print(f"📧 ✅ Welcome email queued successfully for: {email}")
                    print(f"📧 Check Render logs for email send status (look for '✅ Email sent' or '❌ Email failed')")
                else:
                    print(f"⚠️ ❌ Email service disabled - Cannot send welcome email")
                    print(f"⚠️ Check Render environment variables: MAIL_USERNAME and MAIL_PASSWORD")
                print(f"{'='*60}\n")
            except Exception as e:
                print(f"\n❌ CRITICAL: Welcome email error: {e}")
                import traceback
                traceback.print_exc()
                print(f"{'='*60}\n")

            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))

    except Exception as e:
        flash(f'Registration failed: {str(e)}', 'error')
        return redirect(url_for('auth.register_patient'))


@auth_bp.route('/register/doctor')
def register_doctor():
    """Show doctor registration page"""
    return render_template('auth/register_doctor.html', title='Doctor Registration')


@auth_bp.route('/register/doctor', methods=['POST'])
def register_doctor_post():
    """Handle doctor registration"""
    # Get form data
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')
    full_name = request.form.get('full_name', '').strip()
    specialization = request.form.get('specialization', '').strip()
    registration_number = request.form.get('registration_number', '').strip()
    qualification = request.form.get('qualification', '').strip()
    phone = request.form.get('phone', '').strip()
    experience_years = request.form.get('experience_years')
    consultation_fee = request.form.get('consultation_fee')
    address = request.form.get('address', '').strip()
    bio = request.form.get('bio', '').strip()

    # Validation
    if not all([email, password, confirm_password, full_name, specialization, registration_number, phone]):
        flash('Please fill in all required fields', 'error')
        return redirect(url_for('auth.register_doctor'))

    if not validate_email(email):
        flash('Invalid email format', 'error')
        return redirect(url_for('auth.register_doctor'))

    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return redirect(url_for('auth.register_doctor'))

    is_valid, message = validate_password(password)
    if not is_valid:
        flash(message, 'error')
        return redirect(url_for('auth.register_doctor'))

    try:
        with get_db_cursor(auth_bp.config) as cursor:
            # Check if email already exists
            existing_user = User.get_by_email(cursor, email)
            if existing_user:
                flash('Email already registered. Please login.', 'error')
                return redirect(url_for('auth.register_doctor'))

            # Check if registration number already exists
            cursor.execute(
                "SELECT id FROM doctors WHERE registration_number = ?", (registration_number,))
            if cursor.fetchone():
                flash('Registration number already exists', 'error')
                return redirect(url_for('auth.register_doctor'))

            # Create user
            password_hash = hash_password(password)
            user_id = User.create(cursor, email, password_hash, 'doctor')

            # Create doctor profile
            Doctor.create(
                cursor, user_id, full_name, specialization, registration_number,
                qualification=qualification,
                phone=phone,
                address=address,
                experience_years=int(
                    experience_years) if experience_years else None,
                consultation_fee=float(
                    consultation_fee) if consultation_fee else None,
                bio=bio
            )

            # Send welcome email
            try:
                email_service = get_email_service(auth_bp.config)
                print(f"\n{'='*60}")
                print(f"📧 EMAIL SERVICE CHECK - Doctor Registration")
                print(f"{'='*60}")
                print(f"📧 Email service status: {'ENABLED ✅' if email_service.enabled else 'DISABLED ❌ (no credentials)'}")
                
                if email_service.enabled:
                    print(f"📧 Attempting to send welcome email to: {email}")
                    email_service.send_welcome_email(email, full_name, 'doctor')
                    print(f"📧 ✅ Welcome email queued successfully for: {email}")
                else:
                    print(f"⚠️ ❌ Email service disabled - Cannot send welcome email")
                print(f"{'='*60}\n")
            except Exception as e:
                print(f"❌ Welcome email error: {e}")
                import traceback
                traceback.print_exc()

            flash('Registration successful! Your account will be verified by admin. You can login once verified.', 'success')
            return redirect(url_for('auth.login'))

    except Exception as e:
        flash(f'Registration failed: {str(e)}', 'error')
        return redirect(url_for('auth.register_doctor'))


@auth_bp.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('main.index'))
