"""
Data models for the application
Provides clean interface for database operations
"""
from datetime import datetime, date, time, timedelta


class User:
    """User model"""

    @staticmethod
    def create(cursor, email, password_hash, role):
        """Create a new user"""
        query = """
            INSERT INTO users (email, password, role) 
            VALUES (?, ?, ?)
        """
        cursor.execute(query, (email, password_hash, role))
        return cursor.lastrowid

    @staticmethod
    def get_by_email(cursor, email):
        """Get user by email"""
        query = "SELECT * FROM users WHERE email = ?"
        cursor.execute(query, (email,))
        return cursor.fetchone()

    @staticmethod
    def get_by_id(cursor, user_id):
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        return cursor.fetchone()

    @staticmethod
    def update_password(cursor, user_id, new_password_hash):
        """Update user password"""
        query = "UPDATE users SET password = ? WHERE id = ?"
        cursor.execute(query, (new_password_hash, user_id))


class Doctor:
    """Doctor model"""

    @staticmethod
    def create(cursor, user_id, full_name, specialization, registration_number, **kwargs):
        """Create a new doctor profile"""
        query = """
            INSERT INTO doctors 
            (user_id, full_name, specialization, registration_number, qualification, 
             phone, address, experience_years, consultation_fee, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            user_id, full_name, specialization, registration_number,
            kwargs.get('qualification'), kwargs.get(
                'phone'), kwargs.get('address'),
            kwargs.get('experience_years'), kwargs.get(
                'consultation_fee'), kwargs.get('bio')
        ))
        return cursor.lastrowid

    @staticmethod
    def get_by_user_id(cursor, user_id):
        """Get doctor by user ID"""
        query = "SELECT * FROM doctors WHERE user_id = ?"
        cursor.execute(query, (user_id,))
        return cursor.fetchone()

    @staticmethod
    def get_by_id(cursor, doctor_id):
        """Get doctor by ID"""
        query = "SELECT * FROM doctors WHERE id = ?"
        cursor.execute(query, (doctor_id,))
        return cursor.fetchone()

    @staticmethod
    def get_all_verified(cursor, limit=None, offset=0):
        """Get all verified doctors"""
        query = """
            SELECT d.*, u.email 
            FROM doctors d
            JOIN users u ON d.user_id = u.id
            WHERE d.is_verified = 1 AND u.is_active = 1
            ORDER BY d.full_name
        """
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        cursor.execute(query)
        return cursor.fetchall()

    @staticmethod
    def search(cursor, search_term=None, specialization=None):
        """Search doctors"""
        query = """
            SELECT d.*, u.email 
            FROM doctors d
            JOIN users u ON d.user_id = u.id
            WHERE d.is_verified = 1 AND u.is_active = 1
        """
        params = []

        if search_term:
            query += " AND (d.full_name LIKE ? OR d.specialization LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])

        if specialization:
            query += " AND d.specialization = ?"
            params.append(specialization)

        query += " ORDER BY d.full_name"
        cursor.execute(query, params)
        return cursor.fetchall()

    @staticmethod
    def update(cursor, doctor_id, **kwargs):
        """Update doctor profile"""
        fields = []
        values = []

        for key, value in kwargs.items():
            if value is not None:
                fields.append(f"{key} = ?")
                values.append(value)

        if fields:
            values.append(doctor_id)
            query = f"UPDATE doctors SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, values)


class Patient:
    """Patient model"""

    @staticmethod
    def create(cursor, user_id, full_name, **kwargs):
        """Create a new patient profile"""
        dob = kwargs.get('date_of_birth')
        if isinstance(dob, str) and dob:
            dob = datetime.strptime(dob, '%Y-%m-%d').date()
        query = """
            INSERT INTO patients 
            (user_id, full_name, date_of_birth, gender, phone, address, 
             blood_group, emergency_contact, medical_history, allergies)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            user_id, full_name, dob, kwargs.get('gender'),
            kwargs.get('phone'), kwargs.get(
                'address'), kwargs.get('blood_group'),
            kwargs.get('emergency_contact'), kwargs.get('medical_history'),
            kwargs.get('allergies')
        ))
        return cursor.lastrowid

    @staticmethod
    def get_by_user_id(cursor, user_id):
        """Get patient by user ID"""
        query = "SELECT * FROM patients WHERE user_id = ?"
        cursor.execute(query, (user_id,))
        return cursor.fetchone()

    @staticmethod
    def get_by_id(cursor, patient_id):
        """Get patient by ID"""
        query = "SELECT * FROM patients WHERE id = ?"
        cursor.execute(query, (patient_id,))
        return cursor.fetchone()

    @staticmethod
    def update(cursor, patient_id, **kwargs):
        """Update patient profile"""
        fields = []
        values = []

        for key, value in kwargs.items():
            if value is not None:
                fields.append(f"{key} = ?")
                values.append(value)

        if fields:
            values.append(patient_id)
            query = f"UPDATE patients SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, values)


class TimeSlot:
    """Time slot model for doctor availability"""

    @staticmethod
    def create(cursor, doctor_id, day_of_week, start_time, end_time, slot_duration=30):
        """Create a time slot"""
        start = datetime.strptime(
            start_time, '%H:%M').time() if isinstance(start_time, str) else start_time
        end = datetime.strptime(
            end_time, '%H:%M').time() if isinstance(end_time, str) else end_time
        query = """
            INSERT INTO time_slots (doctor_id, day_of_week, start_time, end_time, slot_duration)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(query, (doctor_id, day_of_week,
                       start, end, slot_duration))
        return cursor.lastrowid

    @staticmethod
    def get_by_doctor(cursor, doctor_id):
        """Get all time slots for a doctor"""
        query = """
            SELECT * FROM time_slots 
            WHERE doctor_id = ? AND is_active = 1
            ORDER BY CASE day_of_week 
                        WHEN 'Monday' THEN 1
                        WHEN 'Tuesday' THEN 2
                        WHEN 'Wednesday' THEN 3
                        WHEN 'Thursday' THEN 4
                        WHEN 'Friday' THEN 5
                        WHEN 'Saturday' THEN 6
                        ELSE 7
                     END,
                     start_time
        """
        cursor.execute(query, (doctor_id,))
        return cursor.fetchall()

    @staticmethod
    def get_by_doctor_and_day(cursor, doctor_id, day_of_week):
        """Get time slots for a doctor on a specific day"""
        query = """
            SELECT * FROM time_slots 
            WHERE doctor_id = ? AND day_of_week = ? AND is_active = 1
            ORDER BY start_time
        """
        cursor.execute(query, (doctor_id, day_of_week))
        return cursor.fetchall()

    @staticmethod
    def delete(cursor, slot_id):
        """Delete a time slot"""
        query = "DELETE FROM time_slots WHERE id = ?"
        cursor.execute(query, (slot_id,))

    @staticmethod
    def toggle_active(cursor, slot_id):
        """Toggle slot active status"""
        query = "UPDATE time_slots SET is_active = NOT is_active WHERE id = ?"
        cursor.execute(query, (slot_id,))


class Appointment:
    """Appointment model"""

    @staticmethod
    def create(cursor, patient_id, doctor_id, appointment_date, appointment_time, **kwargs):
        """Create a new appointment"""
        appt_date = datetime.strptime(
            appointment_date, '%Y-%m-%d').date() if isinstance(appointment_date, str) else appointment_date
        appt_time = datetime.strptime(
            appointment_time, '%H:%M').time() if isinstance(appointment_time, str) else appointment_time
        query = """
            INSERT INTO appointments 
            (patient_id, doctor_id, appointment_date, appointment_time, duration, 
             reason_for_visit, symptoms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            patient_id, doctor_id, appt_date, appt_time,
            kwargs.get('duration', 30), kwargs.get('reason_for_visit'),
            kwargs.get('symptoms')
        ))
        return cursor.lastrowid

    @staticmethod
    def get_by_id(cursor, appointment_id):
        """Get appointment by ID with full details"""
        query = """
            SELECT a.*, 
                   p.full_name as patient_name, p.phone as patient_phone, p.date_of_birth,
                   d.full_name as doctor_name, d.specialization, d.consultation_fee,
                   u.email as patient_email
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN users u ON p.user_id = u.id
            WHERE a.id = ?
        """
        cursor.execute(query, (appointment_id,))
        return cursor.fetchone()

    @staticmethod
    def get_by_patient(cursor, patient_id, status=None, limit=None):
        """Get appointments for a patient"""
        query = """
            SELECT a.*, 
                   d.full_name as doctor_name, d.specialization, d.phone as doctor_phone
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.id
            WHERE a.patient_id = ?
        """
        params = [patient_id]

        if status:
            query += " AND a.status = ?"
            params.append(status)

        query += " ORDER BY a.appointment_date DESC, a.appointment_time DESC"

        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query, params)
        return cursor.fetchall()

    @staticmethod
    def get_by_doctor(cursor, doctor_id, status=None, date_filter=None, limit=None):
        """Get appointments for a doctor"""
        query = """
            SELECT a.*, 
                   p.full_name as patient_name, p.phone as patient_phone, 
                   p.date_of_birth, p.blood_group
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.doctor_id = ?
        """
        params = [doctor_id]

        if status:
            query += " AND a.status = ?"
            params.append(status)

        if date_filter:
            query += " AND a.appointment_date = ?"
            params.append(date_filter)

        query += " ORDER BY a.appointment_date, a.appointment_time"

        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query, params)
        return cursor.fetchall()

    @staticmethod
    def check_conflict(cursor, doctor_id, appointment_date, appointment_time):
        """Check if time slot is already booked"""
        appt_date = datetime.strptime(
            appointment_date, '%Y-%m-%d').date() if isinstance(appointment_date, str) else appointment_date
        appt_time = datetime.strptime(
            appointment_time, '%H:%M').time() if isinstance(appointment_time, str) else appointment_time
        query = """
            SELECT id FROM appointments 
            WHERE doctor_id = ? 
            AND appointment_date = ? 
            AND appointment_time = ?
            AND status NOT IN ('cancelled', 'no_show')
        """
        cursor.execute(query, (doctor_id, appt_date, appt_time))
        return cursor.fetchone() is not None

    @staticmethod
    def update_status(cursor, appointment_id, status, **kwargs):
        """Update appointment status"""
        query = "UPDATE appointments SET status = ?"
        params = [status]

        if kwargs.get('cancelled_by'):
            query += ", cancelled_by = ?"
            params.append(kwargs['cancelled_by'])

        if kwargs.get('cancellation_reason'):
            query += ", cancellation_reason = ?"
            params.append(kwargs['cancellation_reason'])

        query += " WHERE id = ?"
        params.append(appointment_id)

        cursor.execute(query, params)

    @staticmethod
    def update_medical_info(cursor, appointment_id, diagnosis=None, prescription=None, notes=None):
        """Update appointment medical information (doctor only)"""
        fields = []
        values = []

        if diagnosis:
            fields.append("diagnosis = ?")
            values.append(diagnosis)
        if prescription:
            fields.append("prescription = ?")
            values.append(prescription)
        if notes:
            fields.append("notes = ?")
            values.append(notes)

        if fields:
            values.append(appointment_id)
            query = f"UPDATE appointments SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, values)


class Notification:
    """Notification model"""

    @staticmethod
    def create(cursor, user_id, title, message, notification_type='system'):
        """Create a notification"""
        query = """
            INSERT INTO notifications (user_id, title, message, type)
            VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (user_id, title, message, notification_type))
        return cursor.lastrowid

    @staticmethod
    def get_by_user(cursor, user_id, unread_only=False, limit=20):
        """Get notifications for a user"""
        query = "SELECT * FROM notifications WHERE user_id = ?"
        params = [user_id]

        if unread_only:
            query += " AND is_read = 0"

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        return cursor.fetchall()

    @staticmethod
    def mark_as_read(cursor, notification_id):
        """Mark notification as read"""
        query = "UPDATE notifications SET is_read = 1 WHERE id = ?"
        cursor.execute(query, (notification_id,))

    @staticmethod
    def get_unread_count(cursor, user_id):
        """Get count of unread notifications"""
        query = "SELECT COUNT(*) as count FROM notifications WHERE user_id = ? AND is_read = 0"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        return result['count'] if result else 0
