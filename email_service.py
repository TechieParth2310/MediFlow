"""
Email Notification Service
Industry-level email notifications for appointments
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import threading


class EmailService:
    """Email service for sending notifications"""

    def __init__(self, config):
        self.config = config
        self.enabled = bool(config.MAIL_USERNAME and config.MAIL_PASSWORD)

    def _send_email_async(self, to_email, subject, html_content, text_content):
        """Send email in background thread"""
        try:
            print(f"📧 [Email Thread] Starting email send to {to_email}")
            print(f"📧 [Email Thread] Server: {self.config.MAIL_SERVER}:{self.config.MAIL_PORT}")
            print(f"📧 [Email Thread] Username: {self.config.MAIL_USERNAME}")
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config.MAIL_DEFAULT_SENDER
            msg['To'] = to_email

            # Attach both text and HTML versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)

            # Send email
            print(f"📧 [Email Thread] Connecting to SMTP server...")
            with smtplib.SMTP(self.config.MAIL_SERVER, self.config.MAIL_PORT, timeout=30) as server:
                print(f"📧 [Email Thread] Starting TLS...")
                if self.config.MAIL_USE_TLS:
                    server.starttls()
                print(f"📧 [Email Thread] Logging in...")
                server.login(self.config.MAIL_USERNAME,
                             self.config.MAIL_PASSWORD)
                print(f"📧 [Email Thread] Sending message...")
                server.send_message(msg)

            print(f"✅ Email sent successfully to {to_email}: {subject}")
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ SMTP Authentication Error: {str(e)}")
            print(f"   Check your MAIL_USERNAME and MAIL_PASSWORD")
        except smtplib.SMTPException as e:
            print(f"❌ SMTP Error: {str(e)}")
        except Exception as e:
            print(f"❌ Email failed to {to_email}: {str(e)}")
            import traceback
            traceback.print_exc()

    def send_email(self, to_email, subject, html_content, text_content):
        """Send email (async if enabled, else log only)"""
        if self.enabled:
            # Send in background thread to not block request
            print(f"📧 [Email Service] Queuing email to {to_email}: {subject}")
            thread = threading.Thread(
                target=self._send_email_async,
                args=(to_email, subject, html_content, text_content)
            )
            thread.daemon = True
            thread.start()
            print(f"📧 [Email Service] Email thread started for {to_email}")
        else:
            print(
                f"📧 [Email Service Disabled] Would send to {to_email}: {subject}")
            print(f"   MAIL_USERNAME: {self.config.MAIL_USERNAME or 'NOT SET'}")
            print(f"   MAIL_PASSWORD: {'SET' if self.config.MAIL_PASSWORD else 'NOT SET'}")

    # =============================================
    # APPOINTMENT NOTIFICATIONS
    # =============================================

    def send_appointment_confirmation(self, patient_email, patient_name, doctor_name,
                                      appointment_date, appointment_time, specialization):
        """Send appointment booking confirmation to patient"""
        subject = "Appointment Confirmed - HealthCare+"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4f7cff; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
                .details {{ background: white; padding: 20px; margin: 20px 0; border-left: 4px solid #4f7cff; }}
                .detail-row {{ margin: 10px 0; }}
                .label {{ font-weight: bold; color: #4f7cff; }}
                .footer {{ background: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 8px 8px; }}
                .btn {{ display: inline-block; padding: 12px 30px; background: #4f7cff; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏥 Appointment Confirmed!</h1>
                </div>
                <div class="content">
                    <p>Dear {patient_name},</p>
                    <p>Your appointment has been successfully booked. Here are the details:</p>
                    
                    <div class="details">
                        <div class="detail-row">
                            <span class="label">Doctor:</span> Dr. {doctor_name}
                        </div>
                        <div class="detail-row">
                            <span class="label">Specialization:</span> {specialization}
                        </div>
                        <div class="detail-row">
                            <span class="label">Date:</span> {appointment_date.strftime('%B %d, %Y')}
                        </div>
                        <div class="detail-row">
                            <span class="label">Time:</span> {appointment_time.strftime('%I:%M %p')}
                        </div>
                    </div>
                    
                    <p><strong>Important Notes:</strong></p>
                    <ul>
                        <li>Please arrive 10 minutes before your scheduled time</li>
                        <li>Bring any previous medical records if applicable</li>
                        <li>You can cancel up to 24 hours before the appointment</li>
                    </ul>
                    
                    <p>If you need to reschedule or cancel, please login to your account.</p>
                </div>
                <div class="footer">
                    <p>HealthCare+ | Professional Healthcare Management</p>
                    <p>This is an automated message, please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        APPOINTMENT CONFIRMED - HealthCare+
        
        Dear {patient_name},
        
        Your appointment has been successfully booked.
        
        APPOINTMENT DETAILS:
        - Doctor: Dr. {doctor_name}
        - Specialization: {specialization}
        - Date: {appointment_date.strftime('%B %d, %Y')}
        - Time: {appointment_time.strftime('%I:%M %p')}
        
        Important Notes:
        - Please arrive 10 minutes before your scheduled time
        - Bring any previous medical records if applicable
        - You can cancel up to 24 hours before the appointment
        
        Thank you,
        HealthCare+ Team
        """

        self.send_email(patient_email, subject, html_content, text_content)

    def send_appointment_notification_to_doctor(self, doctor_email, doctor_name, patient_name,
                                                appointment_date, appointment_time, reason):
        """Notify doctor of new appointment booking"""
        subject = f"New Appointment Booked - {appointment_date.strftime('%B %d')}"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4f7cff; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
                .details {{ background: white; padding: 20px; margin: 20px 0; border-left: 4px solid #2ecc71; }}
                .detail-row {{ margin: 10px 0; }}
                .label {{ font-weight: bold; color: #4f7cff; }}
                .footer {{ background: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 8px 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📅 New Appointment Booked</h1>
                </div>
                <div class="content">
                    <p>Dear Dr. {doctor_name},</p>
                    <p>A new appointment has been booked with you:</p>
                    
                    <div class="details">
                        <div class="detail-row">
                            <span class="label">Patient:</span> {patient_name}
                        </div>
                        <div class="detail-row">
                            <span class="label">Date:</span> {appointment_date.strftime('%B %d, %Y')}
                        </div>
                        <div class="detail-row">
                            <span class="label">Time:</span> {appointment_time.strftime('%I:%M %p')}
                        </div>
                        <div class="detail-row">
                            <span class="label">Reason:</span> {reason or 'General checkup'}
                        </div>
                    </div>
                    
                    <p>Login to your dashboard to view more details and patient information.</p>
                </div>
                <div class="footer">
                    <p>HealthCare+ | Professional Healthcare Management</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        NEW APPOINTMENT BOOKED - HealthCare+
        
        Dear Dr. {doctor_name},
        
        A new appointment has been booked with you:
        
        DETAILS:
        - Patient: {patient_name}
        - Date: {appointment_date.strftime('%B %d, %Y')}
        - Time: {appointment_time.strftime('%I:%M %p')}
        - Reason: {reason or 'General checkup'}
        
        Login to your dashboard to view more details.
        
        HealthCare+ Team
        """

        self.send_email(doctor_email, subject, html_content, text_content)

    def send_appointment_reminder(self, patient_email, patient_name, doctor_name,
                                  appointment_date, appointment_time):
        """Send reminder 24 hours before appointment"""
        subject = "Appointment Reminder - Tomorrow"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #ffc107; color: #333; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
                .reminder-box {{ background: #fff3cd; padding: 20px; margin: 20px 0; border-left: 4px solid #ffc107; }}
                .detail-row {{ margin: 10px 0; }}
                .label {{ font-weight: bold; color: #333; }}
                .footer {{ background: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 8px 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⏰ Appointment Reminder</h1>
                </div>
                <div class="content">
                    <p>Dear {patient_name},</p>
                    <p>This is a friendly reminder about your upcoming appointment:</p>
                    
                    <div class="reminder-box">
                        <div class="detail-row">
                            <span class="label">Doctor:</span> Dr. {doctor_name}
                        </div>
                        <div class="detail-row">
                            <span class="label">Date:</span> <strong>{appointment_date.strftime('%B %d, %Y')}</strong>
                        </div>
                        <div class="detail-row">
                            <span class="label">Time:</span> <strong>{appointment_time.strftime('%I:%M %p')}</strong>
                        </div>
                    </div>
                    
                    <p><strong>Preparation:</strong></p>
                    <ul>
                        <li>Arrive 10 minutes early</li>
                        <li>Bring identification and insurance card</li>
                        <li>Bring list of current medications</li>
                        <li>Note any questions or concerns</li>
                    </ul>
                    
                    <p>See you tomorrow!</p>
                </div>
                <div class="footer">
                    <p>HealthCare+ | Professional Healthcare Management</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        APPOINTMENT REMINDER - HealthCare+
        
        Dear {patient_name},
        
        This is a reminder about your appointment TOMORROW:
        
        - Doctor: Dr. {doctor_name}
        - Date: {appointment_date.strftime('%B %d, %Y')}
        - Time: {appointment_time.strftime('%I:%M %p')}
        
        Please arrive 10 minutes early and bring necessary documents.
        
        See you tomorrow!
        HealthCare+ Team
        """

        self.send_email(patient_email, subject, html_content, text_content)

    def send_cancellation_notification(self, patient_email, patient_name, doctor_name,
                                       appointment_date, appointment_time, cancelled_by, reason):
        """Notify patient about appointment cancellation"""
        subject = "Appointment Cancelled"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #ff6b6b; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
                .cancel-box {{ background: #ffe0e0; padding: 20px; margin: 20px 0; border-left: 4px solid #ff6b6b; }}
                .detail-row {{ margin: 10px 0; }}
                .label {{ font-weight: bold; color: #333; }}
                .footer {{ background: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 8px 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>❌ Appointment Cancelled</h1>
                </div>
                <div class="content">
                    <p>Dear {patient_name},</p>
                    <p>Your appointment has been cancelled.</p>
                    
                    <div class="cancel-box">
                        <div class="detail-row">
                            <span class="label">Doctor:</span> Dr. {doctor_name}
                        </div>
                        <div class="detail-row">
                            <span class="label">Date:</span> {appointment_date.strftime('%B %d, %Y')}
                        </div>
                        <div class="detail-row">
                            <span class="label">Time:</span> {appointment_time.strftime('%I:%M %p')}
                        </div>
                        <div class="detail-row">
                            <span class="label">Cancelled by:</span> {cancelled_by.title()}
                        </div>
                        {f'<div class="detail-row"><span class="label">Reason:</span> {reason}</div>' if reason else ''}
                    </div>
                    
                    <p>You can book a new appointment anytime through your dashboard.</p>
                </div>
                <div class="footer">
                    <p>HealthCare+ | Professional Healthcare Management</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        APPOINTMENT CANCELLED - HealthCare+
        
        Dear {patient_name},
        
        Your appointment has been cancelled:
        
        - Doctor: Dr. {doctor_name}
        - Date: {appointment_date.strftime('%B %d, %Y')}
        - Time: {appointment_time.strftime('%I:%M %p')}
        - Cancelled by: {cancelled_by.title()}
        {f'- Reason: {reason}' if reason else ''}
        
        You can book a new appointment anytime.
        
        HealthCare+ Team
        """

        self.send_email(patient_email, subject, html_content, text_content)

    def send_doctor_cancellation_notification(self, doctor_email, doctor_name, patient_name,
                                              appointment_date, appointment_time):
        """Notify doctor about patient cancellation"""
        subject = f"Appointment Cancelled by Patient - {appointment_date.strftime('%B %d')}"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #ff6b6b; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
                .footer {{ background: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 8px 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Appointment Cancelled</h1>
                </div>
                <div class="content">
                    <p>Dear Dr. {doctor_name},</p>
                    <p>The following appointment has been cancelled by the patient:</p>
                    <p><strong>Patient:</strong> {patient_name}<br>
                    <strong>Date:</strong> {appointment_date.strftime('%B %d, %Y')}<br>
                    <strong>Time:</strong> {appointment_time.strftime('%I:%M %p')}</p>
                    <p>This time slot is now available for new bookings.</p>
                </div>
                <div class="footer">
                    <p>HealthCare+ | Professional Healthcare Management</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        APPOINTMENT CANCELLED - HealthCare+
        
        Dear Dr. {doctor_name},
        
        Appointment cancelled by patient:
        - Patient: {patient_name}
        - Date: {appointment_date.strftime('%B %d, %Y')}
        - Time: {appointment_time.strftime('%I:%M %p')}
        
        This slot is now available.
        
        HealthCare+ Team
        """

        self.send_email(doctor_email, subject, html_content, text_content)

    # =============================================
    # ACCOUNT NOTIFICATIONS
    # =============================================

    def send_welcome_email(self, email, name, role):
        """Send welcome email after registration"""
        subject = f"Welcome to HealthCare+ - Your {role.title()} Account is Ready!"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4f7cff; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
                .welcome-box {{ background: white; padding: 20px; margin: 20px 0; border-left: 4px solid #4f7cff; }}
                .footer {{ background: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 8px 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welcome to HealthCare+!</h1>
                </div>
                <div class="content">
                    <p>Dear {name},</p>
                    <p>Thank you for registering with HealthCare+! Your {role} account has been created successfully.</p>
                    
                    <div class="welcome-box">
                        {'<p><strong>Next Steps for Patients:</strong></p><ul><li>Browse our verified doctors</li><li>Book your first appointment</li><li>Manage your health records</li></ul>' if role == 'patient' else '<p><strong>Next Steps for Doctors:</strong></p><ul><li>Your account is under review for verification</li><li>Once verified, you can set your schedule</li><li>Start accepting patient appointments</li></ul>'}
                    </div>
                    
                    <p>If you have any questions, feel free to reach out to our support team.</p>
                    
                    <p>Best regards,<br>The HealthCare+ Team</p>
                </div>
                <div class="footer">
                    <p>HealthCare+ | Professional Healthcare Management</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        WELCOME TO HealthCare+
        
        Dear {name},
        
        Thank you for registering! Your {role} account is ready.
        
        {'Browse doctors and book your first appointment!' if role == 'patient' else 'Your account will be verified by admin before you can accept appointments.'}
        
        Welcome aboard!
        HealthCare+ Team
        """

        self.send_email(email, subject, html_content, text_content)

    def send_doctor_verification_email(self, doctor_email, doctor_name):
        """Notify doctor when account is verified"""
        subject = "Your Doctor Account Has Been Verified!"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #2ecc71; color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
                .footer {{ background: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 8px 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Account Verified!</h1>
                </div>
                <div class="content">
                    <p>Dear Dr. {doctor_name},</p>
                    <p>Great news! Your doctor account has been verified and approved.</p>
                    <p>You can now:</p>
                    <ul>
                        <li>Set your availability schedule</li>
                        <li>Accept patient appointments</li>
                        <li>Manage patient consultations</li>
                        <li>Update medical records</li>
                    </ul>
                    <p>Login to your dashboard to get started!</p>
                </div>
                <div class="footer">
                    <p>HealthCare+ | Professional Healthcare Management</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        ACCOUNT VERIFIED - HealthCare+
        
        Dear Dr. {doctor_name},
        
        Your doctor account has been verified!
        
        You can now set your schedule and accept appointments.
        
        Login to get started!
        HealthCare+ Team
        """

        self.send_email(doctor_email, subject, html_content, text_content)


# Global email service instance
_email_service = None


def get_email_service(config):
    """Get email service singleton"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService(config)
    return _email_service
