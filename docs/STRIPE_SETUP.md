# Stripe Payment Setup Guide

This guide will help you set up Stripe payments for token purchases in Talents Royale.

## Step 1: Create a Stripe Account

1. Go to https://stripe.com
2. Sign up for a free account
3. Complete the account setup process

## Step 2: Get Your API Keys

1. Log in to your Stripe Dashboard
2. Go to **Developers** → **API keys**
3. You'll see two keys:
   - **Publishable key** (starts with `pk_test_` for test mode or `pk_live_` for live mode)
   - **Secret key** (starts with `sk_test_` for test mode or `sk_live_` for live mode)

## Step 3: Add Keys to .env File

Add the following to your `.env` file in the project root:

```env
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

**Important:**
- Use `pk_test_` and `sk_test_` keys for development/testing
- Use `pk_live_` and `sk_live_` keys for production
- Never commit your `.env` file to version control!

## Step 4: Install Stripe Python Library

If you haven't already, install the Stripe Python library:

```bash
pip install stripe
```

Add it to your `requirements.txt` if you have one:

```
stripe>=7.0.0
```

## Step 5: Set Up Webhooks (Important!)

Webhooks ensure payments are processed even if the user closes the browser.

### For Development (Local Testing):

1. Install Stripe CLI: https://stripe.com/docs/stripe-cli
2. Login: `stripe login`
3. Forward webhooks: `stripe listen --forward-to localhost:8000/webhooks/stripe/`
4. Copy the webhook signing secret (starts with `whsec_`) and add it to your `.env` file

### For Production:

1. Go to Stripe Dashboard → **Developers** → **Webhooks**
2. Click **Add endpoint**
3. Enter your production URL: `https://yourdomain.com/webhooks/stripe/`
4. Select events to listen for:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
5. Copy the webhook signing secret and add it to your `.env` file

## Step 6: Configure Token Packages

Token packages are defined in `talentsroyale/settings.py`:

```python
TOKEN_PACKAGES = [
    {'tokens': 50, 'price': 4.99, 'name': 'Starter Pack', 'popular': False},
    {'tokens': 100, 'price': 8.99, 'name': 'Popular Pack', 'popular': True},
    {'tokens': 250, 'price': 19.99, 'name': 'Champion Pack', 'popular': False},
    {'tokens': 500, 'price': 34.99, 'name': 'Elite Pack', 'popular': False},
    {'tokens': 1000, 'price': 59.99, 'name': 'Royal Pack', 'popular': False},
]
```

You can modify these packages to match your pricing strategy.

## Step 7: Test the Payment Flow

1. **Restart your Django server** after updating `.env`
2. Go to `/purchase-tokens/` (must be logged in)
3. Click "Purchase Now" on any package
4. Use Stripe test card: `4242 4242 4242 4242`
   - Any future expiry date
   - Any 3-digit CVC
   - Any ZIP code
5. Complete the payment
6. Check that tokens were added to your account

## Step 8: Run Migrations

After setting up, create and run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Testing Cards

Stripe provides test cards for different scenarios:

- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **Requires Authentication**: `4000 0025 0000 3155`

See more: https://stripe.com/docs/testing

## Security Notes

1. **Never expose your secret key** - it should only be in `.env` file
2. **Use test keys for development** - switch to live keys only in production
3. **Webhook verification** - always verify webhook signatures
4. **HTTPS required** - Stripe requires HTTPS in production

## Troubleshooting

### "Stripe is not configured" error
- Check that `STRIPE_SECRET_KEY` is in your `.env` file
- Restart your Django server after adding keys

### Payment succeeds but tokens not added
- Check webhook is configured correctly
- Check Django logs for errors
- Verify webhook secret is correct

### Webhook errors
- Make sure webhook URL is accessible
- Check webhook signing secret matches
- Verify events are selected in Stripe dashboard

## Going Live

When ready for production:

1. Switch to live API keys in Stripe Dashboard
2. Update `.env` with live keys (`pk_live_` and `sk_live_`)
3. Set up production webhook endpoint
4. Test with real card (use small amount first!)
5. Monitor Stripe Dashboard for transactions

## Support

- Stripe Documentation: https://stripe.com/docs
- Stripe Support: https://support.stripe.com

