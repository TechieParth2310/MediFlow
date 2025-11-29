"""
Patient Blueprint
Handles all patient-related routes and functionality
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils import patient_required, get_db_cursor
from models import Patient, Doctor, Appointment, TimeSlot, Notification, User
from datetime import datetime, date, time, timedelta
from email_service import get_email_service

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')


@patient_bp.route('/dashboard')
@patient_required
def dashboard():
    """Patient dashboard"""
    try:
        with get_db_cursor(patient_bp.config) as cursor:
            patient_id = session.get('profile_id')

            # Get upcoming appointments
            upcoming_appointments = Appointment.get_by_patient(
                cursor, patient_id, status='scheduled', limit=5
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

            # Get recent appointments
            recent_appointments = Appointment.get_by_patient(
                cursor, patient_id, limit=5
            )
            # Convert date/time strings back to objects
            recent_appointments = [dict(row) for row in recent_appointments]
            for appt in recent_appointments:
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
                    SUM(CASE WHEN status = 'scheduled' THEN 1 ELSE 0 END) as scheduled
                FROM appointments 
                WHERE patient_id = ?
            """, (patient_id,))
            stats = cursor.fetchone()

            # Get unread notifications count
            unread_count = Notification.get_unread_count(
                cursor, session['user_id'])

            return render_template(
                'patient/dashboard.html',
                upcoming_appointments=upcoming_appointments,
                recent_appointments=recent_appointments,
                stats=stats,
                unread_count=unread_count,
                title='Patient Dashboard'
            )

    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('main.index'))


@patient_bp.route('/doctors')
@patient_required
def find_doctors():
    """Search and browse doctors"""
    try:
        with get_db_cursor(patient_bp.config) as cursor:
            search_term = request.args.get('search', '').strip()
            specialization = request.args.get('specialization', '').strip()

            if search_term or specialization:
                doctors = Doctor.search(
                    cursor,
                    search_term=search_term if search_term else None,
                    specialization=specialization if specialization else None
                )
            else:
                doctors = Doctor.get_all_verified(cursor)

            # Get unique specializations for filter
            cursor.execute("""
                SELECT DISTINCT specialization 
                FROM doctors 
                WHERE is_verified = 1 
                ORDER BY specialization
            """)
            specializations = [row['specialization']
                               for row in cursor.fetchall()]

            return render_template(
                'patient/doctors.html',
                doctors=doctors,
                specializations=specializations,
                search_term=search_term,
                selected_specialization=specialization,
                title='Find Doctors'
            )

    except Exception as e:
        flash(f'Error loading doctors: {str(e)}', 'error')
        return redirect(url_for('patient.dashboard'))


@patient_bp.route('/doctor/<int:doctor_id>')
@patient_required
def doctor_profile(doctor_id):
    """View doctor profile and book appointment"""
    try:
        with get_db_cursor(patient_bp.config) as cursor:
            doctor = Doctor.get_by_id(cursor, doctor_id)

            if not doctor or not doctor['is_verified']:
                flash('Doctor not found', 'error')
                return redirect(url_for('patient.find_doctors'))

            # Get doctor's time slots
            time_slots_rows = TimeSlot.get_by_doctor(cursor, doctor_id)
            # Convert Row objects to dictionaries and parse time strings
            time_slots = []
            for row in time_slots_rows:
                slot_dict = dict(row)
                # Convert time strings back to time objects
                if isinstance(slot_dict['start_time'], str):
                    slot_dict['start_time'] = datetime.strptime(
                        slot_dict['start_time'], '%H:%M:%S').time()
                if isinstance(slot_dict['end_time'], str):
                    slot_dict['end_time'] = datetime.strptime(
                        slot_dict['end_time'], '%H:%M:%S').time()
                time_slots.append(slot_dict)

            # Get available dates (next 30 days)
            available_dates = []
            today = date.today()
            for i in range(30):
                check_date = today + timedelta(days=i)
                day_name = check_date.strftime('%A')

                # Check if doctor has slots on this day
                day_slots = [
                    slot for slot in time_slots if slot['day_of_week'] == day_name]
                if day_slots:
                    # Convert time objects to strings for JSON serialization
                    serializable_slots = []
                    for slot in day_slots:
                        slot_copy = slot.copy()
                        if isinstance(slot_copy['start_time'], time):
                            slot_copy['start_time'] = slot_copy['start_time'].strftime(
                                '%H:%M:%S')
                        if isinstance(slot_copy['end_time'], time):
                            slot_copy['end_time'] = slot_copy['end_time'].strftime(
                                '%H:%M:%S')
                        serializable_slots.append(slot_copy)

                    available_dates.append({
                        'date': check_date,
                        'day': day_name,
                        'slots': serializable_slots
                    })

            return render_template(
                'patient/doctor_profile.html',
                doctor=doctor,
                available_dates=available_dates[:14],  # Show next 2 weeks
                title=f'Dr. {doctor["full_name"]}'
            )

    except Exception as e:
        flash(f'Error loading doctor profile: {str(e)}', 'error')
        return redirect(url_for('patient.find_doctors'))


@patient_bp.route('/book-appointment', methods=['POST'])
@patient_required
def book_appointment():
    """Book an appointment"""
    try:
        doctor_id = request.form.get('doctor_id')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        reason = request.form.get('reason', '').strip()
        symptoms = request.form.get('symptoms', '').strip()

        if not all([doctor_id, appointment_date, appointment_time]):
            flash('Please fill in all required fields', 'error')
            return redirect(request.referrer or url_for('patient.find_doctors'))

        with get_db_cursor(patient_bp.config) as cursor:
            patient_id = session.get('profile_id')

            # Validate doctor exists and is verified
            doctor = Doctor.get_by_id(cursor, int(doctor_id))
            if not doctor or not doctor['is_verified']:
                flash('Invalid doctor selection', 'error')
                return redirect(url_for('patient.find_doctors'))

            # Check if slot is still available
            if Appointment.check_conflict(cursor, doctor_id, appointment_date, appointment_time):
                flash('This time slot is no longer available', 'error')
                return redirect(url_for('patient.doctor_profile', doctor_id=doctor_id))

            # Validate date is in future
            appt_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            if appt_date < date.today():
                flash('Cannot book appointments in the past', 'error')
                return redirect(url_for('patient.doctor_profile', doctor_id=doctor_id))

            # Create appointment
            appointment_id = Appointment.create(
                cursor, patient_id, doctor_id, appointment_date, appointment_time,
                reason_for_visit=reason,
                symptoms=symptoms
            )

            # Create notification for doctor
            Notification.create(
                cursor, doctor['user_id'],
                'New Appointment Booking',
                f'New appointment booked for {appointment_date} at {appointment_time}',
                'appointment'
            )

            # Send email notifications
            try:
                email_service = get_email_service(patient_bp.config)

                # Get patient details for email
                patient = Patient.get_by_id(cursor, patient_id)
                patient_user = User.get_by_id(cursor, session['user_id'])
                doctor_user = User.get_by_id(cursor, doctor['user_id'])

                # Convert date/time strings to datetime objects
                appt_date = datetime.strptime(
                    appointment_date, '%Y-%m-%d').date()
                appt_time_obj = datetime.strptime(
                    appointment_time, '%H:%M').time()

                # Send confirmation to patient
                email_service.send_appointment_confirmation(
                    patient_user['email'],
                    patient['full_name'],
                    doctor['full_name'],
                    appt_date,
                    appt_time_obj,
                    doctor['specialization']
                )

                # Send notification to doctor
                email_service.send_appointment_notification_to_doctor(
                    doctor_user['email'],
                    doctor['full_name'],
                    patient['full_name'],
                    appt_date,
                    appt_time_obj,
                    reason
                )
            except Exception as e:
                print(f"Email notification error: {e}")

            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('patient.appointment_detail', appointment_id=appointment_id))

    except Exception as e:
        flash(f'Error booking appointment: {str(e)}', 'error')
        return redirect(request.referrer or url_for('patient.find_doctors'))


@patient_bp.route('/appointments')
@patient_required
def appointments():
    """View all appointments"""
    try:
        with get_db_cursor(patient_bp.config) as cursor:
            patient_id = session.get('profile_id')
            status_filter = request.args.get('status')

            appointments = Appointment.get_by_patient(
                cursor, patient_id, status=status_filter
            )
            # Convert date/time strings back to objects
            appointments = [dict(row) for row in appointments]
            for appt in appointments:
                if isinstance(appt['appointment_date'], str):
                    appt['appointment_date'] = datetime.strptime(
                        appt['appointment_date'], '%Y-%m-%d').date()
                if isinstance(appt['appointment_time'], str):
                    appt['appointment_time'] = datetime.strptime(
                        appt['appointment_time'], '%H:%M:%S').time()

            return render_template(
                'patient/appointments.html',
                appointments=appointments,
                status_filter=status_filter,
                title='My Appointments'
            )

    except Exception as e:
        flash(f'Error loading appointments: {str(e)}', 'error')
        return redirect(url_for('patient.dashboard'))


@patient_bp.route('/appointment/<int:appointment_id>')
@patient_required
def appointment_detail(appointment_id):
    """View appointment details"""
    try:
        with get_db_cursor(patient_bp.config) as cursor:
            appointment = Appointment.get_by_id(cursor, appointment_id)

            if not appointment or appointment['patient_id'] != session.get('profile_id'):
                flash('Appointment not found', 'error')
                return redirect(url_for('patient.appointments'))

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
                'patient/appointment_detail.html',
                appointment=appointment,
                title='Appointment Details'
            )

    except Exception as e:
        flash(f'Error loading appointment: {str(e)}', 'error')
        return redirect(url_for('patient.appointments'))


@patient_bp.route('/appointment/<int:appointment_id>/cancel', methods=['POST'])
@patient_required
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    try:
        reason = request.form.get('reason', 'Cancelled by patient')

        with get_db_cursor(patient_bp.config) as cursor:
            # Verify appointment belongs to this patient
            appointment = Appointment.get_by_id(cursor, appointment_id)
            if not appointment or appointment['patient_id'] != session.get('profile_id'):
                flash('Appointment not found', 'error')
                return redirect(url_for('patient.appointments'))

            # Convert date/time strings back to objects
            if isinstance(appointment['appointment_date'], str):
                appointment['appointment_date'] = datetime.strptime(
                    appointment['appointment_date'], '%Y-%m-%d').date()
            if isinstance(appointment['appointment_time'], str):
                appointment['appointment_time'] = datetime.strptime(
                    appointment['appointment_time'], '%H:%M:%S').time()

            # Check if appointment can be cancelled
            if appointment['status'] in ['completed', 'cancelled']:
                flash('This appointment cannot be cancelled', 'error')
                return redirect(url_for('patient.appointment_detail', appointment_id=appointment_id))

            # Check cancellation time limit (24 hours before)
            appt_datetime = datetime.combine(
                appointment['appointment_date'], appointment['appointment_time'])
            hours_until = (appt_datetime - datetime.now()
                           ).total_seconds() / 3600

            if hours_until < 24:
                flash(
                    'Appointments can only be cancelled at least 24 hours in advance', 'error')
                return redirect(url_for('patient.appointment_detail', appointment_id=appointment_id))

            # Cancel appointment
            Appointment.update_status(
                cursor, appointment_id, 'cancelled',
                cancelled_by='patient',
                cancellation_reason=reason
            )

            # Create notification for doctor
            doctor = Doctor.get_by_id(cursor, appointment['doctor_id'])
            if doctor:
                Notification.create(
                    cursor, doctor['user_id'],
                    'Appointment Cancelled',
                    f'Appointment on {appointment["appointment_date"]} at {appointment["appointment_time"]} has been cancelled',
                    'cancellation'
                )

            # Send email notifications
            try:
                email_service = get_email_service(patient_bp.config)

                # Get user details
                patient = Patient.get_by_id(cursor, appointment['patient_id'])
                patient_user = User.get_by_id(cursor, session['user_id'])
                doctor_user = User.get_by_id(cursor, doctor['user_id'])

                # Send cancellation email to patient
                email_service.send_cancellation_notification(
                    patient_user['email'],
                    patient['full_name'],
                    doctor['full_name'],
                    appointment['appointment_date'],
                    appointment['appointment_time'],
                    'patient',
                    reason
                )

                # Notify doctor
                email_service.send_doctor_cancellation_notification(
                    doctor_user['email'],
                    doctor['full_name'],
                    patient['full_name'],
                    appointment['appointment_date'],
                    appointment['appointment_time']
                )
            except Exception as e:
                print(f"Email notification error: {e}")

            flash('Appointment cancelled successfully', 'success')
            return redirect(url_for('patient.appointments'))

    except Exception as e:
        flash(f'Error cancelling appointment: {str(e)}', 'error')
        return redirect(url_for('patient.appointment_detail', appointment_id=appointment_id))


@patient_bp.route('/profile')
@patient_required
def profile():
    """View/Edit patient profile"""
    try:
        with get_db_cursor(patient_bp.config) as cursor:
            patient_id = session.get('profile_id')
            patient = Patient.get_by_id(cursor, patient_id)

            # Get user email
            user = User.get_by_id(cursor, session['user_id'])
            user_email = user['email'] if user else ''

            return render_template(
                'patient/profile.html',
                patient=patient,
                user_email=user_email,
                title='My Profile'
            )

    except Exception as e:
        flash(f'Error loading profile: {str(e)}', 'error')
        return redirect(url_for('patient.dashboard'))


@patient_bp.route('/profile/update', methods=['POST'])
@patient_required
def update_profile():
    """Update patient profile"""
    try:
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        blood_group = request.form.get('blood_group', '').strip()
        emergency_contact = request.form.get('emergency_contact', '').strip()
        medical_history = request.form.get('medical_history', '').strip()
        allergies = request.form.get('allergies', '').strip()

        with get_db_cursor(patient_bp.config) as cursor:
            patient_id = session.get('profile_id')

            Patient.update(
                cursor, patient_id,
                phone=phone if phone else None,
                address=address if address else None,
                blood_group=blood_group if blood_group else None,
                emergency_contact=emergency_contact if emergency_contact else None,
                medical_history=medical_history if medical_history else None,
                allergies=allergies if allergies else None
            )

            flash('Profile updated successfully', 'success')
            return redirect(url_for('patient.profile'))

    except Exception as e:
        flash(f'Error updating profile: {str(e)}', 'error')
        return redirect(url_for('patient.profile'))
