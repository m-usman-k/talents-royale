# Talents Royale

A competitive talent showcase platform where users can participate in arenas, vote for contestants, and compete for glory.

## Features

- 🎯 **Arena System**: Multiple tier-based arenas (Recruit, Veteran, Champion, Elite)
- 🎬 **Contestant Submissions**: Upload videos or images to showcase your talent
- 🗳️ **Voting System**: Vote for your favorite contestants (free first vote, tokens for additional votes)
- 🪙 **Token Economy**: Purchase tokens to join arenas and vote
- 💳 **Payment Integration**: Secure Stripe payment system for token purchases
- ✉️ **Email Confirmation**: Email verification for account security
- 📊 **User Profiles**: Track your stats, achievements, and competition history
- 🏆 **Leaderboards**: See top performers in each arena

## Getting Started

### Prerequisites

- Python 3.8+
- Django 5.2+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd talents-royale
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install django python-decouple stripe
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   
   # Email Configuration (Gmail)
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-gmail-app-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   
   # Stripe Payment Configuration
   STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
   STRIPE_SECRET_KEY=sk_test_your_key_here
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main site: http://127.0.0.1:8000
   - Admin panel: http://127.0.0.1:8000/admin

## Documentation

For detailed setup instructions, see the documentation in the `docs/` folder:

- **[Email Setup Guide](docs/EMAIL_SETUP.md)** - Configure email for account verification
- **[Gmail Setup Guide](docs/GMAIL_SETUP.md)** - Quick Gmail configuration
- **[Stripe Payment Setup](docs/STRIPE_SETUP.md)** - Payment system configuration
- **[Troubleshooting](docs/TROUBLESHOOTING_GMAIL.md)** - Common email issues and solutions

## Project Structure

```
talents-royale/
├── accounts/          # Main app with models, views, forms
├── docs/              # Documentation files
├── media/             # User-uploaded files
├── static/            # CSS, JavaScript, images
├── templates/         # HTML templates
├── talentsroyale/    # Django project settings
└── manage.py         # Django management script
```

## Key Models

- **CustomUser**: User accounts with token balance
- **Arena**: Competition arenas with different tiers
- **Contestant**: User submissions to arenas
- **Vote**: Voting records
- **Payment**: Payment transactions
- **TokenTransaction**: Token purchase and usage history

## Token Packages

Default token packages (configurable in `settings.py`):

- Starter Pack: 50 tokens - $4.99
- Popular Pack: 100 tokens - $8.99
- Champion Pack: 250 tokens - $19.99
- Elite Pack: 500 tokens - $34.99
- Royal Pack: 1000 tokens - $59.99

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Security Notes

- Never commit `.env` file to version control
- Use test Stripe keys for development
- Enable HTTPS in production
- Keep Django secret key secure

## License

Copyright © 2025 Talents Royale™

## Support

For issues and questions, please refer to the documentation in the `docs/` folder or contact support.
