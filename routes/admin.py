"""
Admin Blueprint
Handles all admin-related routes and functionality
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils import admin_required, get_db_cursor
from models import Doctor, Patient, Appointment, User
from datetime import datetime, date

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with overview"""
    try:
        with get_db_cursor(admin_bp.config) as cursor:
            # Get overall statistics
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM users WHERE role = 'doctor') as total_doctors,
                    (SELECT COUNT(*) FROM users WHERE role = 'patient') as total_patients,
                    (SELECT COUNT(*) FROM appointments) as total_appointments,
                    (SELECT COUNT(*) FROM doctors WHERE is_verified = 1) as verified_doctors,
                    (SELECT COUNT(*) FROM doctors WHERE is_verified = 0) as pending_doctors
            """)
            stats = cursor.fetchone()

            # Recent appointments
            cursor.execute("""
                SELECT 
                    a.id, a.appointment_date, a.appointment_time, a.status,
                    p.full_name as patient_name,
                    d.full_name as doctor_name,
                    d.specialization
                FROM appointments a
                JOIN patients p ON a.patient_id = p.id
                JOIN doctors d ON a.doctor_id = d.id
                ORDER BY a.created_at DESC
                LIMIT 10
            """)
            recent_appointments = cursor.fetchall()
            # Convert datetime strings back to objects
            recent_appointments = [dict(row) for row in recent_appointments]
            for appt in recent_appointments:
                if isinstance(appt['appointment_date'], str):
                    appt['appointment_date'] = datetime.strptime(
                        appt['appointment_date'], '%Y-%m-%d')
                if isinstance(appt['appointment_time'], str):
                    appt['appointment_time'] = datetime.strptime(
                        appt['appointment_time'], '%H:%M:%S').time()

            # Pending doctor verifications
            cursor.execute("""
                    SELECT 
                        d.id, d.full_name, d.specialization, d.registration_number,
                        d.qualification, d.experience_years, u.email, u.created_at,
                        u.id as user_id
                    FROM doctors d
                    JOIN users u ON d.user_id = u.id
                    WHERE d.is_verified = 0
                    ORDER BY u.created_at DESC
                """)
            pending_doctors = cursor.fetchall()
            # Convert datetime strings back to objects
            pending_doctors = [dict(row) for row in pending_doctors]
            for doctor in pending_doctors:
                if isinstance(doctor['created_at'], str):
                    doctor['created_at'] = datetime.strptime(
                        doctor['created_at'], '%Y-%m-%d %H:%M:%S')

            return render_template(
                'admin/dashboard.html',
                stats=stats,
                recent_appointments=recent_appointments,
                pending_doctors=pending_doctors,
                title='Admin Dashboard'
            )

    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('main.index'))


@admin_bp.route('/doctors')
@admin_required
def manage_doctors():
    """View and manage all doctors"""
    try:
        with get_db_cursor(admin_bp.config) as cursor:
            status_filter = request.args.get('status')

            if status_filter == 'verified':
                doctors = Doctor.get_all_verified(cursor)
                # Convert datetime strings back to objects
                doctors = [dict(row) for row in doctors]
                for doctor in doctors:
                    if isinstance(doctor['created_at'], str):
                        doctor['created_at'] = datetime.strptime(
                            doctor['created_at'], '%Y-%m-%d %H:%M:%S')
            elif status_filter == 'pending':
                cursor.execute("""
                    SELECT d.*, u.email, u.created_at, u.id as user_id
                    FROM doctors d
                    JOIN users u ON d.user_id = u.id
                    WHERE d.is_verified = 0
                    ORDER BY u.created_at DESC
                """)
                doctors = cursor.fetchall()
                # Convert datetime strings back to objects
                doctors = [dict(row) for row in doctors]
                for doctor in doctors:
                    if isinstance(doctor['created_at'], str):
                        doctor['created_at'] = datetime.strptime(
                            doctor['created_at'], '%Y-%m-%d %H:%M:%S')
            else:
                cursor.execute("""
                    SELECT d.*, u.email, u.created_at, u.id as user_id
                    FROM doctors d
                    JOIN users u ON d.user_id = u.id
                    ORDER BY u.created_at DESC
                """)
                doctors = cursor.fetchall()
                # Convert datetime strings back to objects
                doctors = [dict(row) for row in doctors]
                for doctor in doctors:
                    if isinstance(doctor['created_at'], str):
                        doctor['created_at'] = datetime.strptime(
                            doctor['created_at'], '%Y-%m-%d %H:%M:%S')

            return render_template(
                'admin/doctors.html',
                doctors=doctors,
                status_filter=status_filter,
                title='Manage Doctors'
            )

    except Exception as e:
        flash(f'Error loading doctors: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/doctors/<int:doctor_id>/verify', methods=['POST'])
@admin_required
def verify_doctor(doctor_id):
    """Verify a doctor"""
    try:
        with get_db_cursor(admin_bp.config) as cursor:
            cursor.execute("""
                UPDATE doctors 
                SET is_verified = 1 
                WHERE id = ?
            """, (doctor_id,))

            flash('Doctor verified successfully', 'success')
            return redirect(url_for('admin.manage_doctors'))

    except Exception as e:
        flash(f'Error verifying doctor: {str(e)}', 'error')
        return redirect(url_for('admin.manage_doctors'))


@admin_bp.route('/doctors/<int:doctor_id>/unverify', methods=['POST'])
@admin_required
def unverify_doctor(doctor_id):
    """Unverify a doctor"""
    try:
        with get_db_cursor(admin_bp.config) as cursor:
            cursor.execute("""
                UPDATE doctors 
                SET is_verified = 0 
                WHERE id = ?
            """, (doctor_id,))

            flash('Doctor unverified', 'success')
            return redirect(url_for('admin.manage_doctors'))

    except Exception as e:
        flash(f'Error unverifying doctor: {str(e)}', 'error')
        return redirect(url_for('admin.manage_doctors'))


@admin_bp.route('/patients')
@admin_required
def manage_patients():
    """View and manage all patients"""
    try:
        with get_db_cursor(admin_bp.config) as cursor:
            cursor.execute("""
                SELECT p.*, u.email, u.created_at, u.id as user_id
                FROM patients p
                JOIN users u ON p.user_id = u.id
                ORDER BY u.created_at DESC
            """)
            patients = cursor.fetchall()
            # Convert datetime strings back to objects
            patients = [dict(row) for row in patients]
            for patient in patients:
                if isinstance(patient['created_at'], str):
                    patient['created_at'] = datetime.strptime(
                        patient['created_at'], '%Y-%m-%d %H:%M:%S')

            return render_template(
                'admin/patients.html',
                patients=patients,
                title='Manage Patients'
            )

    except Exception as e:
        flash(f'Error loading patients: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/appointments')
@admin_required
def manage_appointments():
    """View and manage all appointments"""
    try:
        with get_db_cursor(admin_bp.config) as cursor:
            status_filter = request.args.get('status')

            query = """
                SELECT 
                    a.*,
                    p.full_name as patient_name,
                    d.full_name as doctor_name,
                    d.specialization,
                    pu.email as patient_email,
                    du.email as doctor_email
                FROM appointments a
                JOIN patients p ON a.patient_id = p.id
                JOIN doctors d ON a.doctor_id = d.id
                JOIN users pu ON p.user_id = pu.id
                JOIN users du ON d.user_id = du.id
            """

            if status_filter:
                query += " WHERE a.status = ?"
                cursor.execute(
                    query + " ORDER BY a.appointment_date DESC, a.appointment_time DESC", (status_filter,))
            else:
                cursor.execute(
                    query + " ORDER BY a.appointment_date DESC, a.appointment_time DESC")

            appointments = cursor.fetchall()
            # Convert datetime strings back to objects
            appointments = [dict(row) for row in appointments]
            for appt in appointments:
                if isinstance(appt['appointment_date'], str):
                    appt['appointment_date'] = datetime.strptime(
                        appt['appointment_date'], '%Y-%m-%d')
                if isinstance(appt['appointment_time'], str):
                    appt['appointment_time'] = datetime.strptime(
                        appt['appointment_time'], '%H:%M:%S').time()
                if isinstance(appt['created_at'], str):
                    appt['created_at'] = datetime.strptime(
                        appt['created_at'], '%Y-%m-%d %H:%M:%S')

            return render_template(
                'admin/appointments.html',
                appointments=appointments,
                status_filter=status_filter,
                title='Manage Appointments'
            )

    except Exception as e:
        flash(f'Error loading appointments: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user (soft delete or hard delete)"""
    try:
        with get_db_cursor(admin_bp.config) as cursor:
            # Don't allow deleting yourself
            if user_id == session.get('user_id'):
                flash('Cannot delete your own account', 'error')
                return redirect(request.referrer or url_for('admin.dashboard'))

            # Get user role to redirect properly
            user = User.get_by_id(cursor, user_id)
            if not user:
                flash('User not found', 'error')
                return redirect(url_for('admin.dashboard'))

            # Delete user (this will cascade to patients/doctors if FK constraints are set properly)
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

            flash(f'{user["role"].title()} deleted successfully', 'success')

            if user['role'] == 'doctor':
                return redirect(url_for('admin.manage_doctors'))
            elif user['role'] == 'patient':
                return redirect(url_for('admin.manage_patients'))
            else:
                return redirect(url_for('admin.dashboard'))

    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'error')
        return redirect(request.referrer or url_for('admin.dashboard'))
