# 🔍 Email Troubleshooting Guide

## Issue: Email Not Received After Registration

### Step 1: Check Render Logs

1. Go to your Render Dashboard
2. Click on your **MediFlow** service
3. Click on **"Logs"** in the left sidebar
4. Look for messages related to email when you registered

**What to look for:**

✅ **Success messages:**
```
📧 Email service status: ENABLED ✅
📧 Attempting to send welcome email to: patient@example.com
📧 [Email Service] Queuing email to patient@example.com: Welcome to HealthCare+...
📧 [Email Thread] Starting email send to patient@example.com
✅ Email sent successfully to patient@example.com: Welcome to HealthCare+
```

❌ **Error messages:**
```
❌ SMTP Authentication Error: ...
❌ SMTP Error: ...
❌ Email failed to patient@example.com: ...
```

⚠️ **Service disabled:**
```
📧 Email service status: DISABLED (no credentials)
⚠️ Email service disabled - MAIL_USERNAME or MAIL_PASSWORD not set
```

### Step 2: Common Issues & Solutions

#### Issue 1: "SMTP Authentication Error"

**Symptoms:**
- Logs show: `❌ SMTP Authentication Error`
- Error code: `535` or `534`

**Solutions:**
1. **Verify App Password:**
   - Go to Google Account → Security → App passwords
   - Make sure you're using the correct 16-character app password
   - App passwords don't have spaces (remove them if present)

2. **Regenerate App Password:**
   - Delete the old app password
   - Generate a new one
   - Update `MAIL_PASSWORD` in Render

3. **Check 2-Step Verification:**
   - Make sure 2-Step Verification is enabled
   - App passwords only work with 2FA enabled

#### Issue 2: "Connection Timeout" or "Connection Refused"

**Symptoms:**
- Logs show: `❌ SMTP Error` or connection timeout
- No connection to SMTP server

**Solutions:**
1. **Check Firewall:**
   - Render should allow outbound SMTP (port 587)
   - This is usually automatic, but check if blocked

2. **Try Different Port:**
   - Current: Port 587 (TLS)
   - Alternative: Port 465 (SSL) - requires code change

3. **Check Gmail Status:**
   - Visit: https://status.google.com
   - Verify Gmail SMTP is operational

#### Issue 3: "Email Service Disabled"

**Symptoms:**
- Logs show: `Email service status: DISABLED`

**Solutions:**
1. **Check Environment Variables in Render:**
   - Go to Environment tab
   - Verify `MAIL_USERNAME` and `MAIL_PASSWORD` are set
   - Make sure there are no extra spaces

2. **Redeploy After Adding Variables:**
   - After adding/updating environment variables
   - Click "Save, rebuild, and deploy"
   - Wait for deployment to complete

#### Issue 4: Email Sent But Not Received

**Symptoms:**
- Logs show: `✅ Email sent successfully`
- But no email in inbox

**Solutions:**
1. **Check Spam Folder:**
   - Gmail might mark it as spam initially
   - Look in "Spam" or "Junk" folder

2. **Check Email Address:**
   - Verify the email address used for registration
   - Make sure it's correct

3. **Gmail Filters:**
   - Check if Gmail filters are blocking it
   - Look in "All Mail" folder

4. **Wait a Few Minutes:**
   - Sometimes emails are delayed
   - Check again after 5-10 minutes

### Step 3: Test Email Configuration

Run this test script on Render to diagnose issues:

1. **Via Render Shell:**
   - Go to Render Dashboard → Your Service
   - Click "Shell" in left sidebar
   - Run: `python3 test_email_render.py`

2. **Or add to your code temporarily:**
   - Create a test route that calls the test script
   - Visit the route to see results

### Step 4: Verify Configuration

Check these in Render Environment Variables:

- ✅ `MAIL_USERNAME` = Your Gmail address
- ✅ `MAIL_PASSWORD` = 16-character app password (no spaces)
- ✅ `FLASK_ENV` = `production`
- ✅ `MAIL_DEFAULT_SENDER` = Your Gmail address

### Step 5: Quick Test

1. **Register a new test patient** with your own email
2. **Check Render logs immediately** after registration
3. **Look for email-related messages**
4. **Check your inbox** (and spam folder)

## Still Not Working?

### Debug Steps:

1. **Check if email service is enabled:**
   - Look for: `📧 Email service status: ENABLED ✅`
   - If not, environment variables aren't being read

2. **Check SMTP connection:**
   - Look for: `📧 [Email Thread] Connecting to SMTP server...`
   - If this fails, it's a network/firewall issue

3. **Check authentication:**
   - Look for: `📧 [Email Thread] Logging in...`
   - If this fails, it's an app password issue

4. **Check email sending:**
   - Look for: `📧 [Email Thread] Sending message...`
   - If this fails, it's a Gmail server issue

### Alternative: Use SendGrid (More Reliable)

If Gmail continues to have issues, consider using SendGrid:

1. Sign up for free SendGrid account (100 emails/day free)
2. Get API key
3. Update Render environment variables:
   - `MAIL_SERVER` = `smtp.sendgrid.net`
   - `MAIL_PORT` = `587`
   - `MAIL_USERNAME` = `apikey`
   - `MAIL_PASSWORD` = `your-sendgrid-api-key`

## Need More Help?

Check the logs and share:
1. What error messages you see
2. Whether email service shows as "ENABLED"
3. Any SMTP error codes

