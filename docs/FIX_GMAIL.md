# Fix: Still Getting Outlook Error with Gmail

## The Problem
Your `.env` file has Gmail settings, but you're still getting Outlook errors. This means **your Django server needs to be restarted** to pick up the new settings.

## Solution: Restart Django Server

1. **Stop your Django server:**
   - In the terminal where it's running, press `Ctrl+C` (or `Ctrl+Break` on Windows)
   - Wait for it to fully stop

2. **Start it again:**
   ```bash
   python manage.py runserver
   ```

3. **Try again:**
   - Sign up a new account or resend confirmation email
   - It should now use Gmail!

## Verify Your .env File

Your `.env` file should look like this:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=usmank.personal@gmail.com
EMAIL_HOST_PASSWORD=qodptwyjhrhvkgdr
DEFAULT_FROM_EMAIL=usmank.personal@gmail.com
```

✅ Your file looks correct!

## Important Notes

- **Always restart the server** after changing `.env` file
- Make sure you're using a **Gmail App Password**, not your regular password
- The App Password should be 16 characters with no spaces

## If Still Not Working

1. Double-check your Gmail App Password is correct
2. Make sure 2-Step Verification is enabled on your Google account
3. Verify the App Password was generated for "Mail" app
4. Check Django console for any error messages

