# Email Configuration Setup for Talents Royale

This guide will help you configure Outlook email for sending confirmation emails.

## Step 1: Create a .env file

Create a `.env` file in your project root (same directory as `manage.py`) if it doesn't exist.

## Step 2: Add Outlook Email Credentials

Add the following to your `.env` file:

```env
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@outlook.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@outlook.com
```

**CRITICAL: You MUST use an App Password!**
- Microsoft has disabled basic authentication for Outlook
- You **CANNOT** use your regular password
- You **MUST** create and use an App Password (see Step 3)

## Step 3: Generate App Password (REQUIRED)

**You MUST create an App Password - regular passwords will NOT work!**

### Method 1: Via Microsoft Account Security (Recommended)

1. Go to https://account.microsoft.com/security
2. Sign in with your Microsoft account
3. Go to **"Security"** → **"Advanced security options"**
4. Under **"App passwords"**, click **"Create a new app password"**
   - If you don't see "App passwords", you may need to enable 2FA first
5. Name it "Talents Royale" or similar
6. Copy the generated 16-character password (no spaces)
7. Use this password in your `.env` file for `EMAIL_HOST_PASSWORD`

### Method 2: Via Security Info Page

1. Go to https://mysignins.microsoft.com/security-info
2. Sign in with your Microsoft account
3. Click **"Add method"** → Select **"App password"**
4. Name it "Talents Royale"
5. Copy the generated password
6. Use this password in your `.env` file

### If App Passwords Option is Not Available:

If you don't see the App Password option, you may need to:
1. Enable 2-Step Verification first:
   - Go to https://account.microsoft.com/security
   - Enable "Two-step verification"
2. Then the App Password option will appear

### Alternative: Enable SMTP AUTH (For Organization Accounts)

If you're using a Microsoft 365/Office 365 account:
1. Go to https://admin.microsoft.com/
2. Navigate to **Users** → **Active users**
3. Select your account
4. Click **Mail** tab → **Manage email apps**
5. Ensure **"Authenticated SMTP"** is checked
6. Save changes

## Step 4: Test Email Configuration

After setting up, restart your Django server and try signing up a new account. You should receive a confirmation email.

## Troubleshooting

### Error: "Authentication unsuccessful, basic authentication is disabled"

**This means you're using your regular password instead of an App Password!**

**Solution:**
1. You MUST create an App Password (see Step 3 above)
2. Use the App Password (16 characters, no spaces) in your `.env` file
3. Make sure you're using `smtp.office365.com` not `smtp-mail.outlook.com`

### Other Common Issues:

**Emails not sending?**
1. ✅ Check that your `.env` file is in the project root
2. ✅ Verify you're using an **App Password**, not your regular password
3. ✅ Make sure `EMAIL_HOST=smtp.office365.com` (not smtp-mail.outlook.com)
4. ✅ Ensure your email address in `.env` matches exactly (case-sensitive)
5. ✅ Check the Django console for error messages
6. ✅ Restart your Django server after changing `.env` file

**"App passwords" option not showing?**
- Enable 2-Step Verification first, then App Passwords will appear

**Still not working?**
- Try using Gmail instead (see below) - it's often easier to set up

### Using Gmail instead?
If you prefer to use Gmail, change in `.env`:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

For Gmail, you'll need to:
1. Enable 2-Step Verification
2. Generate an App Password from your Google Account settings
3. Use that App Password in the `.env` file

## Email Features

The system now supports:
- ✅ Email confirmation for new user registration
- ✅ Email confirmation for email address changes
- ✅ Resend confirmation email functionality
- ✅ Beautiful HTML email templates
- ✅ 24-hour expiration for confirmation links
- ✅ Confirmation codes for manual entry

