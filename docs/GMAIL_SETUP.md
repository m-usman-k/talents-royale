# Gmail Email Setup - Quick Guide

## Step 1: Enable 2-Step Verification

1. Go to: https://myaccount.google.com/security
2. Sign in with your Google account
3. Under **"Signing in to Google"**, find **"2-Step Verification"**
4. Click **"Get started"** and follow the prompts to enable it
   - You'll need to verify with your phone number
   - This is required to generate App Passwords

## Step 2: Generate App Password

1. Go to: https://myaccount.google.com/apppasswords
   - Or: https://myaccount.google.com/security → Scroll to "2-Step Verification" → Click "App passwords"
2. Sign in if prompted
3. Under **"Select app"**, choose **"Mail"**
4. Under **"Select device"**, choose **"Other (Custom name)"**
5. Type: **"Talents Royale"** (or any name you want)
6. Click **"Generate"**
7. **Copy the 16-character password** (it looks like: `abcd efgh ijkl mnop`)
   - ⚠️ **Copy it NOW** - you won't be able to see it again!
   - Remove spaces when using it (use: `abcdefghijklmnop`)

## Step 3: Update .env File

Create or update your `.env` file in the project root with:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Replace:**
- `your-email@gmail.com` with your actual Gmail address
- `abcdefghijklmnop` with the App Password you just generated (remove spaces)

## Step 4: Restart Django Server

After updating `.env`, restart your server:

```bash
# Stop server (Ctrl+C), then:
python manage.py runserver
```

## Step 5: Test It!

Try signing up a new account - you should receive a confirmation email!

## Troubleshooting

### "Invalid credentials" error?
- ✅ Make sure you're using the **App Password**, not your regular Gmail password
- ✅ Remove all spaces from the App Password
- ✅ Make sure 2-Step Verification is enabled
- ✅ Check that your Gmail address is correct (case-sensitive)

### "Less secure app access" error?
- This shouldn't happen with App Passwords, but if it does:
  1. Go to: https://myaccount.google.com/lesssecureapps
  2. Make sure it's enabled (though App Passwords should work without this)

### Still not working?
- Double-check your `.env` file is in the project root (same folder as `manage.py`)
- Make sure there are no extra spaces or quotes in your `.env` file
- Restart the Django server after making changes
- Check the Django console for error messages

## That's It!

Gmail is usually much easier to set up than Outlook. Once you have the App Password, it should work immediately!

