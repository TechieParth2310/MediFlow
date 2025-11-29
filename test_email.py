#!/usr/bin/env python3
"""
Email Service Test Script
Quickly test email functionality
"""
from datetime import datetime, date, time
from config import config
from email_service import get_email_service


def test_email_service():
    """Test email service configuration"""

    cfg = config['default']()
    email_service = get_email_service(cfg)

    print("\n" + "="*60)
    print("EMAIL SERVICE TEST")
    print("="*60)

    # Check configuration
    print(f"\n📧 Email Service Status:")
    print(f"   Server: {cfg.MAIL_SERVER}")
    print(f"   Port: {cfg.MAIL_PORT}")
    print(f"   Username: {cfg.MAIL_USERNAME or '[NOT SET]'}")
    print(f"   Password: {'*' * 8 if cfg.MAIL_PASSWORD else '[NOT SET]'}")
    print(
        f"   Enabled: {'YES ✅' if email_service.enabled else 'NO (Log Mode) 📝'}")

    if not email_service.enabled:
        print("\n⚠️  Email service running in LOG-ONLY mode")
        print("   Emails will be printed to console, not actually sent")
        print("   This is normal for development/testing!\n")
        print("   To enable emails:")
        print("   1. Set MAIL_USERNAME environment variable")
        print("   2. Set MAIL_PASSWORD environment variable")
        print("   3. Restart the application\n")
    else:
        print("\n✅ Email service is ACTIVE and ready to send emails!\n")

    # Send test email
    print("-" * 60)
    print("Sending test email...\n")

    test_date = date(2025, 12, 25)
    test_time = time(10, 30)

    email_service.send_appointment_confirmation(
        'patient@example.com',
        'John Doe',
        'Dr. Smith',
        test_date,
        test_time,
        'Cardiologist'
    )

    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)

    if email_service.enabled:
        print("\nCheck the recipient's email inbox for the test message.")
    else:
        print("\nCheck the console output above to see the email content.")

    print()


if __name__ == '__main__':
    test_email_service()
