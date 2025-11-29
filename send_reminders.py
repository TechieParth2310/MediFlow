#!/usr/bin/env python3
"""
Appointment Reminder Script
Run this daily (e.g., via cron) to send appointment reminders

Cron Example (run at 9 AM daily):
0 9 * * * cd /path/to/project && python3 send_reminders.py
"""
from datetime import datetime, timedelta
from config import config
from utils import get_db_connection
from email_service import get_email_service


def send_appointment_reminders():
    """Send reminders for appointments happening tomorrow"""

    cfg = config['default']()
    email_service = get_email_service(cfg)

    # Get appointments for tomorrow
    tomorrow = datetime.now().date() + timedelta(days=1)

    try:
        conn = get_db_connection(cfg)
        cursor = conn.cursor()

        # Query appointments for tomorrow with patient and doctor details
        query = """
            SELECT 
                a.id,
                a.appointment_date,
                a.appointment_time,
                p.full_name as patient_name,
                p.user_id as patient_user_id,
                d.full_name as doctor_name,
                pu.email as patient_email
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN users pu ON p.user_id = pu.id
            WHERE a.appointment_date = ? 
            AND a.status = 'scheduled'
        """

        cursor.execute(query, (tomorrow,))
        appointments = cursor.fetchall() or []

        print(f"\n{'='*60}")
        print(
            f"APPOINTMENT REMINDER SERVICE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        print(f"Checking appointments for: {tomorrow.strftime('%B %d, %Y')}")
        print(f"Found {len(appointments)} appointment(s) to remind\n")

        sent_count = 0
        for appt in appointments:
            try:
                email_service.send_appointment_reminder(
                    appt['patient_email'],
                    appt['patient_name'],
                    appt['doctor_name'],
                    appt['appointment_date'],
                    appt['appointment_time']
                )
                sent_count += 1
                print(
                    f"✅ Reminder sent to {appt['patient_name']} ({appt['patient_email']})")

            except Exception as e:
                print(
                    f"❌ Failed to send reminder to {appt['patient_name']}: {e}")

        cursor.close()
        conn.close()

        print(f"\n{'='*60}")
        print(
            f"Summary: {sent_count}/{len(appointments)} reminders sent successfully")
        print(f"{'='*60}\n")

        return sent_count

    except Exception as e:
        print(f"Error in reminder service: {e}")
        return 0


if __name__ == '__main__':
    send_appointment_reminders()
