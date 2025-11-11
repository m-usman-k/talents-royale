# Quick Fix for Outlook Email Authentication Error

## The Problem
You're getting: `Authentication unsuccessful, basic authentication is disabled`

This means Microsoft has disabled basic authentication and you **MUST** use an App Password.

## Quick Solution (3 Steps)

### Step 1: Create App Password
1. Go to: https://account.microsoft.com/security
2. Sign in
3. Click **"Advanced security options"**
4. Under **"App passwords"**, click **"Create a new app password"**
5. Name it "Talents Royale"
6. **Copy the 16-character password** (it looks like: `abcd-efgh-ijkl-mnop`)

### Step 2: Update .env File
Make sure your `.env` file has:

```env
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@outlook.com
EMAIL_HOST_PASSWORD=abcd-efgh-ijkl-mnop
DEFAULT_FROM_EMAIL=your-email@outlook.com
```

**Important:**
- Use `smtp.office365.com` (not smtp-mail.outlook.com)
- Use the App Password you just created (not your regular password)
- Remove any spaces from the App Password

### Step 3: Restart Server
Restart your Django server after updating `.env`

```bash
# Stop the server (Ctrl+C) then:
python manage.py runserver
```

## Still Not Working?

### Option 1: Use Gmail Instead
Gmail is often easier. In your `.env`:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

To get Gmail App Password:
1. Enable 2-Step Verification
2. Go to: https://myaccount.google.com/apppasswords
3. Generate App Password for "Mail"
4. Use that password

### Option 2: Test Without Email (Development)
For development, you can skip email confirmation temporarily by commenting out the email check in `accounts/views.py` signin_view function.

