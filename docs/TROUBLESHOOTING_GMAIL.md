# Troubleshooting Gmail Authentication Error (535)

## The Error
```
Error: (535, b'5.7.8 Username and Password not accepted. For more information, go to
5.7.8 https://support.google.com/mail/?p=BadCredentials ...')
```

This error means Gmail is rejecting your email credentials.

## Quick Fix Steps

### Step 1: Verify 2-Step Verification is Enabled
1. Go to: https://myaccount.google.com/security
2. Check that **"2-Step Verification"** is **ON**
3. If it's OFF, enable it first (required for App Passwords)

### Step 2: Generate a New App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Sign in if prompted
3. Under **"Select app"**, choose **"Mail"**
4. Under **"Select device"**, choose **"Other (Custom name)"**
5. Type: **"Talents Royale"** (or any name)
6. Click **"Generate"**
7. **Copy the 16-character password immediately** (you won't see it again!)
   - It looks like: `abcd efgh ijkl mnop`
   - Remove spaces when using: `abcdefghijklmnop`

### Step 3: Update Your .env File
Make sure your `.env` file in the project root has:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Important:**
- Replace `your-email@gmail.com` with your actual Gmail address
- Replace `abcdefghijklmnop` with the App Password from Step 2 (no spaces!)
- Make sure there are no quotes around the values
- Make sure there are no extra spaces

### Step 4: Restart Django Server
**CRITICAL:** You must restart your Django server after changing `.env`:

1. Stop the server: Press `Ctrl+C` in the terminal
2. Start it again: `python manage.py runserver`
3. Try creating an account again

## Common Issues

### "Still getting the same error after restarting?"
- ✅ Double-check the App Password is correct (16 characters, no spaces)
- ✅ Verify 2-Step Verification is enabled
- ✅ Make sure you're using the App Password, NOT your regular Gmail password
- ✅ Check that your Gmail address in `.env` matches exactly (case-sensitive)
- ✅ Try generating a NEW App Password (old ones can expire)

### "I can't find the App Passwords option"
- You must enable 2-Step Verification first
- Go to: https://myaccount.google.com/security
- Enable "2-Step Verification"
- Then App Passwords will appear

### "The App Password doesn't work"
- Make sure you copied it correctly (16 characters)
- Remove all spaces
- Generate a new one if needed
- Make sure you selected "Mail" as the app type

### "Where is my .env file?"
- It should be in the project root (same folder as `manage.py`)
- If it doesn't exist, create it
- Make sure it's named exactly `.env` (with the dot at the start)

## Verification Checklist

Before trying again, verify:
- [ ] 2-Step Verification is enabled on Google account
- [ ] App Password was generated for "Mail" app
- [ ] App Password is 16 characters (no spaces)
- [ ] `.env` file is in project root
- [ ] `.env` file has correct email and password
- [ ] No quotes or extra spaces in `.env` values
- [ ] Django server was restarted after updating `.env`

## Still Not Working?

1. **Check Django console** for detailed error messages
2. **Try generating a completely new App Password**
3. **Verify your Gmail account is not locked or restricted**
4. **Check if you're using a Google Workspace account** (may have different requirements)
5. **See GMAIL_SETUP.md** in this docs folder for more detailed instructions

## Alternative: Use Console Email Backend (Development Only)

For development/testing, you can temporarily use console email backend:

In `talentsroyale/settings.py`, temporarily change:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

This will print emails to the console instead of sending them. **Don't use this in production!**

