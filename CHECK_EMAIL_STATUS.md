# 🔍 How to Check if Emails Are Working

## After Patient Registration

When a patient registers, you should see detailed logs in Render. Here's what to check:

### Step 1: Check Render Logs

1. Go to **Render Dashboard** → Your **MediFlow** service
2. Click **"Logs"** in the left sidebar
3. Look for messages that start with `📧`

### Step 2: What You Should See

**✅ If Email Service is Working:**
```
============================================================
📧 EMAIL SERVICE CHECK - Patient Registration
============================================================
📧 Email service status: ENABLED ✅
📧 MAIL_USERNAME: parthkothawade2003@gmail.com
📧 MAIL_PASSWORD: SET ✅
📧 MAIL_SERVER: smtp.gmail.com
📧 MAIL_PORT: 587
📧 Attempting to send welcome email to: patient@example.com
📧 Patient name: John Doe
📧 ✅ Welcome email queued successfully for: patient@example.com
📧 Check Render logs for email send status (look for '✅ Email sent' or '❌ Email failed')
============================================================

📧 [Email Service] Queuing email to patient@example.com: 🎉 Successfully Registered on MediFlow - Welcome John Doe!
📧 [Email Service] Email thread started for patient@example.com
📧 [Email Thread] Starting email send to patient@example.com
📧 [Email Thread] Server: smtp.gmail.com:587
📧 [Email Thread] Username: parthkothawade2003@gmail.com
📧 [Email Thread] Connecting to SMTP server...
📧 [Email Thread] Starting TLS...
📧 [Email Thread] Logging in...
📧 [Email Thread] Sending message...
✅ Email sent successfully to patient@example.com: 🎉 Successfully Registered on MediFlow - Welcome John Doe!
```

**❌ If Email Service is Disabled:**
```
============================================================
📧 EMAIL SERVICE CHECK - Patient Registration
============================================================
📧 Email service status: DISABLED ❌ (no credentials)
📧 MAIL_USERNAME: NOT SET
📧 MAIL_PASSWORD: NOT SET ❌
⚠️ ❌ Email service disabled - Cannot send welcome email
============================================================
```

**❌ If There's an Authentication Error:**
```
📧 [Email Thread] Logging in...
❌ SMTP Authentication Error: (535, '5.7.8 Username and Password not accepted')
   Check your MAIL_USERNAME and MAIL_PASSWORD
```

### Step 3: Common Issues

#### Issue 1: "Email service status: DISABLED"

**Solution:**
- Check Render Environment Variables
- Make sure `MAIL_USERNAME` and `MAIL_PASSWORD` are set
- Click "Save, rebuild, and deploy" after adding them

#### Issue 2: "SMTP Authentication Error"

**Solution:**
- Regenerate Gmail App Password
- Update `MAIL_PASSWORD` in Render (remove spaces)
- Redeploy the service

#### Issue 3: "Email sent successfully" but no email received

**Solution:**
- Check spam/junk folder
- Wait 5-10 minutes (delays can occur)
- Verify the email address is correct
- Check Gmail filters

### Step 4: Test Email Configuration

You can test your email setup by running the test script:

1. Go to Render Dashboard → Your Service → **"Shell"**
2. Run: `python3 test_email_render.py`

This will test your email configuration and show any errors.

## Email Flow at Each Step

### ✅ Patient Registration
- Welcome email sent immediately
- Subject: "🎉 Successfully Registered on MediFlow - Welcome [Name]!"
- Message: "You have successfully registered on MediFlow!"

### ✅ Doctor Registration  
- Welcome email sent immediately
- Subject: "🎉 Successfully Registered on MediFlow - Welcome [Name]!"
- Message: "Your account is under review for verification"

### ✅ Appointment Booking
- Confirmation email to patient
- Notification email to doctor
- Both sent immediately after booking

### ✅ Appointment Cancellation
- Cancellation email to patient
- Notification to doctor
- Both sent immediately after cancellation

### ✅ Appointment Reminder
- Reminder email 24 hours before appointment
- Sent via `send_reminders.py` (cron job)

## Next Steps

1. **Check Render logs** after registering a new patient
2. **Look for the email status messages** shown above
3. **If you see errors**, follow the solutions provided
4. **If emails are sent successfully**, check your inbox (and spam folder)

The email system is now configured to send emails at every step. If you don't see emails, check the Render logs to see what's happening!



