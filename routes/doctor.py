"""
Doctor Blueprint
Handles all doctor-related routes and functionality
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils import doctor_required, get_db_cursor
from models import Doctor, Appointment, TimeSlot, Patient, Notification, User
from datetime import datetime, date, time, timedelta
from email_service import get_email_service

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')


@doctor_bp.route('/dashboard')
@doctor_required
def dashboard():
    """Doctor dashboard"""
    try:
        with get_db_cursor(doctor_bp.config) as cursor:
            doctor_id = session.get('profile_id')

            # Get today's appointments
            today = date.today()
            today_appointments = Appointment.get_by_doctor(
                cursor, doctor_id, date_filter=today
            )
            # Convert date/time strings back to objects
            today_appointments = [dict(row) for row in today_appointments]
            for appt in today_appointments:
                if isinstance(appt['appointment_date'], str):
                    appt['appointment_date'] = datetime.strptime(
                        appt['appointment_date'], '%Y-%m-%d').date()
                if isinstance(appt['appointment_time'], str):
                    appt['appointment_time'] = datetime.strptime(
                        appt['appointment_time'], '%H:%M:%S').time()

            # Get upcoming appointments
            upcoming_appointments = Appointment.get_by_doctor(
                cursor, doctor_id, status='scheduled', limit=5
            )
            # Convert date/time strings back to objects
            upcoming_appointments = [dict(row)
                                     for row in upcoming_appointments]
            for appt in upcoming_appointments:
                if isinstance(appt['appointment_date'], str):
                    appt['appointment_date'] = datetime.strptime(
                        appt['appointment_date'], '%Y-%m-%d').date()
                if isinstance(appt['appointment_time'], str):
                    appt['appointment_time'] = datetime.strptime(
                        appt['appointment_time'], '%H:%M:%S').time()

            # Get statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_appointments,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                    SUM(CASE WHEN status = 'scheduled' THEN 1 ELSE 0 END) as scheduled,
                    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled
                FROM appointments 
                WHERE doctor_id = ?
            """, (doctor_id,))
            stats = cursor.fetchone()

            # Get unread notifications count
            unread_count = Notification.get_unread_count(
                cursor, session['user_id'])

            return render_template(
                'doctor/dashboard.html',
                today_appointments=today_appointments,
                upcoming_appointments=upcoming_appointments,
                stats=stats,
                unread_count=unread_count,
                title='Doctor Dashboard'
            )

    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('main.index'))


@doctor_bp.route('/appointments')
@doctor_required
def appointments():
    """View all appointments"""
    try:
        with get_db_cursor(doctor_bp.config) as cursor:
            doctor_id = session.get('profile_id')
            status_filter = request.args.get('status')
            date_filter = request.args.get('date')

            appointments = Appointment.get_by_doctor(
                cursor, doctor_id,
                status=status_filter,
                date_filter=date_filter
            )
            # Convert date/time strings back to objects
            for appt in appointments:
                if isinstance(appt['appointment_date'], str):
                    appt['appointment_date'] = datetime.strptime(
                        appt['appointment_date'], '%Y-%m-%d').date()
                if isinstance(appt['appointment_time'], str):
                    appt['appointment_time'] = datetime.strptime(
                        appt['appointment_time'], '%H:%M:%S').time()

            return render_template(
                'doctor/appointments.html',
                appointments=appointments,
                status_filter=status_filter,
                date_filter=date_filter,
                title='My Appointments'
            )

    except Exception as e:
        flash(f'Error loading appointments: {str(e)}', 'error')
        return redirect(url_for('doctor.dashboard'))


@doctor_bp.route('/appointment/<int:appointment_id>')
@doctor_required
def appointment_detail(appointment_id):
    """View appointment details"""
    try:
        with get_db_cursor(doctor_bp.config) as cursor:
            appointment = Appointment.get_by_id(cursor, appointment_id)

            if not appointment or appointment['doctor_id'] != session.get('profile_id'):
                flash('Appointment not found', 'error')
                return redirect(url_for('doctor.appointments'))

            # Convert date/time strings back to objects for template rendering
            if isinstance(appointment['appointment_date'], str):
                appointment['appointment_date'] = datetime.strptime(
                    appointment['appointment_date'], '%Y-%m-%d').date()
            if isinstance(appointment['appointment_time'], str):
                appointment['appointment_time'] = datetime.strptime(
                    appointment['appointment_time'], '%H:%M:%S').time()
            if appointment['date_of_birth'] and isinstance(appointment['date_of_birth'], str):
                appointment['date_of_birth'] = datetime.strptime(
                    appointment['date_of_birth'], '%Y-%m-%d').date()

            return render_template(
                'doctor/appointment_detail.html',
                appointment=appointment,
                title='Appointment Details'
            )

    except Exception as e:
        flash(f'Error loading appointment: {str(e)}', 'error')
        return redirect(url_for('doctor.appointments'))


@doctor_bp.route('/appointment/<int:appointment_id>/update', methods=['POST'])
@doctor_required
def update_appointment(appointment_id):
    """Update appointment (diagnosis, prescription, notes)"""
    try:
        diagnosis = request.form.get('diagnosis', '').strip()
        prescription = request.form.get('prescription', '').strip()
        notes = request.form.get('notes', '').strip()
        status = request.form.get('status')

        with get_db_cursor(doctor_bp.config) as cursor:
            # Verify appointment belongs to this doctor
            appointment = Appointment.get_by_id(cursor, appointment_id)
            if not appointment or appointment['doctor_id'] != session.get('profile_id'):
                flash('Appointment not found', 'error')
                return redirect(url_for('doctor.appointments'))

            # Convert date/time strings back to objects
            if isinstance(appointment['appointment_date'], str):
                appointment['appointment_date'] = datetime.strptime(
                    appointment['appointment_date'], '%Y-%m-%d').date()
            if isinstance(appointment['appointment_time'], str):
                appointment['appointment_time'] = datetime.strptime(
                    appointment['appointment_time'], '%H:%M:%S').time()

            # Update medical info
            if diagnosis or prescription or notes:
                Appointment.update_medical_info(
                    cursor, appointment_id, diagnosis, prescription, notes
                )

            # Update status if provided
            if status and status in ['confirmed', 'completed', 'cancelled']:
                Appointment.update_status(cursor, appointment_id, status)

                # Create notification for patient
                patient = Patient.get_by_id(cursor, appointment['patient_id'])
                if patient:
                    Notification.create(
                        cursor, patient['user_id'],
                        'Appointment Updated',
                        f'Your appointment on {appointment["appointment_date"]} has been updated to {status}',
                        'appointment'
                    )

                    # Send email if status changed to completed or cancelled
                    if status in ['completed', 'cancelled']:
                        try:
                            email_service = get_email_service(doctor_bp.config)
                            patient_user = User.get_by_id(
                                cursor, patient['user_id'])
                            doctor = Doctor.get_by_id(
                                cursor, appointment['doctor_id'])

                            if status == 'cancelled':
                                email_service.send_cancellation_notification(
                                    patient_user['email'],
                                    patient['full_name'],
                                    doctor['full_name'],
                                    appointment['appointment_date'],
                                    appointment['appointment_time'],
                                    'doctor',
                                    'Cancelled by doctor'
                                )
                        except Exception as e:
                            print(f"Email notification error: {e}")

            flash('Appointment updated successfully', 'success')
            return redirect(url_for('doctor.appointment_detail', appointment_id=appointment_id))

    except Exception as e:
        flash(f'Error updating appointment: {str(e)}', 'error')
        return redirect(url_for('doctor.appointment_detail', appointment_id=appointment_id))


@doctor_bp.route('/schedule')
@doctor_required
def schedule():
    """Manage time slots"""
    try:
        with get_db_cursor(doctor_bp.config) as cursor:
            doctor_id = session.get('profile_id')
            time_slots_rows = TimeSlot.get_by_doctor(cursor, doctor_id)
            # Convert Row objects to dictionaries and parse time strings
            time_slots = []
            for row in time_slots_rows:
                slot_dict = dict(row)
                # Convert time strings back to time objects for template rendering
                if isinstance(slot_dict['start_time'], str):
                    slot_dict['start_time'] = datetime.strptime(
                        slot_dict['start_time'], '%H:%M:%S').time()
                if isinstance(slot_dict['end_time'], str):
                    slot_dict['end_time'] = datetime.strptime(
                        slot_dict['end_time'], '%H:%M:%S').time()
                time_slots.append(slot_dict)

            # Group by day
            slots_by_day = {}
            days = ['Monday', 'Tuesday', 'Wednesday',
                    'Thursday', 'Friday', 'Saturday', 'Sunday']
            for day in days:
                slots_by_day[day] = [
                    slot for slot in time_slots if slot['day_of_week'] == day]

            return render_template(
                'doctor/schedule.html',
                slots_by_day=slots_by_day,
                days=days,
                title='My Schedule'
            )

    except Exception as e:
        flash(f'Error loading schedule: {str(e)}', 'error')
        return redirect(url_for('doctor.dashboard'))


@doctor_bp.route('/schedule/add', methods=['POST'])
@doctor_required
def add_time_slot():
    """Add a new time slot"""
    try:
        day_of_week = request.form.get('day_of_week')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        slot_duration = request.form.get('slot_duration', 30)

        if not all([day_of_week, start_time, end_time]):
            flash('Please fill in all fields', 'error')
            return redirect(url_for('doctor.schedule'))

        with get_db_cursor(doctor_bp.config) as cursor:
            doctor_id = session.get('profile_id')

            # Check for conflicts
            existing_slots = TimeSlot.get_by_doctor_and_day(
                cursor, doctor_id, day_of_week)
            start_obj = datetime.strptime(start_time, '%H:%M').time()
            end_obj = datetime.strptime(end_time, '%H:%M').time()

            for slot in existing_slots:
                # Parse the slot times from the database (stored as strings)
                slot_start = datetime.strptime(slot['start_time'], '%H:%M:%S').time(
                ) if isinstance(slot['start_time'], str) else slot['start_time']
                slot_end = datetime.strptime(slot['end_time'], '%H:%M:%S').time(
                ) if isinstance(slot['end_time'], str) else slot['end_time']

                if not (end_obj <= slot_start or start_obj >= slot_end):
                    flash('Time slot conflicts with existing schedule', 'error')
                    return redirect(url_for('doctor.schedule'))

            TimeSlot.create(cursor, doctor_id, day_of_week,
                            start_time, end_time, slot_duration)
            flash('Time slot added successfully', 'success')
            return redirect(url_for('doctor.schedule'))

    except Exception as e:
        flash(f'Error adding time slot: {str(e)}', 'error')
        return redirect(url_for('doctor.schedule'))


@doctor_bp.route('/schedule/delete/<int:slot_id>', methods=['POST'])
@doctor_required
def delete_time_slot(slot_id):
    """Delete a time slot"""
    try:
        with get_db_cursor(doctor_bp.config) as cursor:
            TimeSlot.delete(cursor, slot_id)
            flash('Time slot deleted successfully', 'success')
            return redirect(url_for('doctor.schedule'))

    except Exception as e:
        flash(f'Error deleting time slot: {str(e)}', 'error')
        return redirect(url_for('doctor.schedule'))


@doctor_bp.route('/profile')
@doctor_required
def profile():
    """View/Edit doctor profile"""
    try:
        with get_db_cursor(doctor_bp.config) as cursor:
            doctor_id = session.get('profile_id')
            doctor = Doctor.get_by_id(cursor, doctor_id)

            # Get user email
            user = User.get_by_id(cursor, session['user_id'])
            user_email = user['email'] if user else ''

            return render_template(
                'doctor/profile.html',
                doctor=doctor,
                user_email=user_email,
                title='My Profile'
            )

    except Exception as e:
        flash(f'Error loading profile: {str(e)}', 'error')
        return redirect(url_for('doctor.dashboard'))


@doctor_bp.route('/profile/update', methods=['POST'])
@doctor_required
def update_profile():
    """Update doctor profile"""
    try:
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        bio = request.form.get('bio', '').strip()
        consultation_fee = request.form.get('consultation_fee')

        with get_db_cursor(doctor_bp.config) as cursor:
            doctor_id = session.get('profile_id')

            Doctor.update(
                cursor, doctor_id,
                phone=phone if phone else None,
                address=address if address else None,
                bio=bio if bio else None,
                consultation_fee=float(
                    consultation_fee) if consultation_fee else None
            )

            flash('Profile updated successfully', 'success')
            return redirect(url_for('doctor.profile'))

    except Exception as e:
        flash(f'Error updating profile: {str(e)}', 'error')
        return redirect(url_for('doctor.profile'))
