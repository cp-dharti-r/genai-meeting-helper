# Mailtrap Setup Guide

Mailtrap is perfect for testing emails in development - it catches all emails so they never reach real recipients.

## Quick Setup

### 1. Create a Mailtrap Account (Free)

1. Go to https://mailtrap.io
2. Sign up for a free account (no credit card required)
3. Create a new inbox (or use the default one)

### 2. Get Your Credentials

In your Mailtrap inbox, click on **"SMTP Settings"** and select **"PHP"** or **"Node.js - Nodemailer"** to see your credentials:

- **SMTP Host**: `sandbox.smtp.mailtrap.io`
- **SMTP Port**: `2525` (or `465` for SSL, `587` for TLS)
- **SMTP User**: Your Mailtrap username (shown in settings)
- **SMTP Password**: Your Mailtrap password (shown in settings)

### 3. Configure Your .env File

Create or edit `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Then edit `.env` and add your Mailtrap credentials:

```env
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=2525
SMTP_USER=your-mailtrap-username-here
SMTP_PASSWORD=your-mailtrap-password-here
SMTP_FROM=meetings@example.com
```

**Important**: Replace `your-mailtrap-username-here` and `your-mailtrap-password-here` with your actual Mailtrap credentials.

### 4. Restart the Server

After updating `.env`, restart your FastAPI server:

```bash
# Stop the server (Ctrl+C)
# Then restart:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test It

1. Create a meeting via the web UI
2. Start the meeting
3. Check your Mailtrap inbox - you should see the email there!

## What You'll See in Mailtrap

- All emails sent by the application
- Email content (HTML and plain text)
- Attachments (like calendar invites)
- Email headers and metadata
- Preview of how the email looks

## Mailtrap Features

✅ **Safe Testing**: Emails never reach real recipients  
✅ **Email Preview**: See how emails render  
✅ **HTML/Text View**: Switch between HTML and plain text  
✅ **Attachment Viewing**: Download and view attachments  
✅ **Spam Testing**: Check spam score  
✅ **Multiple Inboxes**: Separate inboxes for different environments  

## Troubleshooting

### "Connection refused" or "Timeout" errors

- Make sure you're using the correct SMTP_HOST: `sandbox.smtp.mailtrap.io`
- Check that SMTP_PORT is `2525`
- Verify your username and password are correct
- Check your internet connection

### "Authentication failed"

- Double-check your SMTP_USER and SMTP_PASSWORD
- Make sure there are no extra spaces in the .env file
- Try regenerating your Mailtrap password

### Emails not appearing

- Check server logs for errors
- Verify the .env file is in the project root
- Make sure the server was restarted after changing .env
- Check Mailtrap inbox - sometimes emails take a few seconds

## Alternative: Keep Logging (No SMTP)

If you don't want to set up Mailtrap right now, you can leave SMTP fields empty:

```env
SMTP_HOST=
SMTP_USER=
SMTP_PASSWORD=
```

Emails will be logged to the console instead of being sent. Check your server logs to see the email content.

## Production Setup

For production, use a real SMTP provider:
- **Gmail**: Use App Password (not regular password)
- **SendGrid**: Professional email service
- **AWS SES**: Scalable email service
- **Mailgun**: Developer-friendly email API

Just update your `.env` file with production SMTP credentials.

