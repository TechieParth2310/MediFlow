#!/usr/bin/env python3
"""
Test Email Configuration for Render Deployment
Run this to diagnose email issues
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import config

def test_email_config():
    """Test email configuration"""
    print("\n" + "="*60)
    print("EMAIL CONFIGURATION TEST")
    print("="*60)
    
    # Get config
    cfg = config['production']() if os.getenv('FLASK_ENV') == 'production' else config['default']()
    
    print(f"\n📧 Configuration Check:")
    print(f"   MAIL_SERVER: {cfg.MAIL_SERVER}")
    print(f"   MAIL_PORT: {cfg.MAIL_PORT}")
    print(f"   MAIL_USE_TLS: {cfg.MAIL_USE_TLS}")
    print(f"   MAIL_USERNAME: {cfg.MAIL_USERNAME or '[NOT SET]'}")
    print(f"   MAIL_PASSWORD: {'*' * 16 if cfg.MAIL_PASSWORD else '[NOT SET]'}")
    print(f"   MAIL_DEFAULT_SENDER: {cfg.MAIL_DEFAULT_SENDER}")
    
    if not cfg.MAIL_USERNAME or not cfg.MAIL_PASSWORD:
        print("\n❌ ERROR: MAIL_USERNAME or MAIL_PASSWORD not set!")
        print("   Check your Render environment variables")
        return False
    
    print(f"\n🔍 Testing SMTP Connection...")
    
    try:
        # Create test email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Test Email from MediFlow'
        msg['From'] = cfg.MAIL_DEFAULT_SENDER
        msg['To'] = cfg.MAIL_USERNAME  # Send to self for testing
        
        text_content = "This is a test email from MediFlow."
        html_content = "<html><body><p>This is a test email from MediFlow.</p></body></html>"
        
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        print(f"   Connecting to {cfg.MAIL_SERVER}:{cfg.MAIL_PORT}...")
        with smtplib.SMTP(cfg.MAIL_SERVER, cfg.MAIL_PORT, timeout=10) as server:
            print(f"   Starting TLS...")
            if cfg.MAIL_USE_TLS:
                server.starttls()
            
            print(f"   Logging in as {cfg.MAIL_USERNAME}...")
            server.login(cfg.MAIL_USERNAME, cfg.MAIL_PASSWORD)
            print(f"   ✅ Login successful!")
            
            print(f"   Sending test email...")
            server.send_message(msg)
            print(f"   ✅ Email sent successfully!")
        
        print(f"\n✅ SUCCESS! Test email sent to {cfg.MAIL_USERNAME}")
        print(f"   Check your inbox (and spam folder)")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ AUTHENTICATION ERROR: {str(e)}")
        print(f"\n   Possible causes:")
        print(f"   1. App password is incorrect")
        print(f"   2. 2-Step Verification not enabled on Gmail")
        print(f"   3. App password was revoked")
        print(f"\n   Solution:")
        print(f"   - Go to Google Account → Security → App passwords")
        print(f"   - Generate a new app password")
        print(f"   - Update MAIL_PASSWORD in Render")
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f"\n❌ CONNECTION ERROR: {str(e)}")
        print(f"\n   Possible causes:")
        print(f"   1. Firewall blocking SMTP port {cfg.MAIL_PORT}")
        print(f"   2. Network connectivity issues")
        print(f"   3. SMTP server is down")
        return False
        
    except smtplib.SMTPException as e:
        print(f"\n❌ SMTP ERROR: {str(e)}")
        return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_email_config()
