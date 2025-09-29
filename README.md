# NatWest Open Banking - Account Details Fetcher

A Python script to fetch user account details using NatWest's Open Banking API (Sandbox environment).

## Features

- Automated OAuth2 flow with sandbox auto-approval
- Fetches account information, balances, and recent transactions
- Clean terminal output with formatted account details
- Secure credential management

## Prerequisites

- Python 3.7+
- NatWest Developer Portal account
- Registered application with sandbox access

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd balance_check
```

2. Create a virtual environment:
```bash
python -m venv .venv
```

3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`

4. Install dependencies:
```bash
pip install requests
```

## Configuration

1. Copy the example configuration file:
```bash
cp config.example.py config.py
```

2. Edit `config.py` and add your NatWest API credentials:
   - `CLIENT_ID`: Your application's client ID
   - `CLIENT_SECRET`: Your application's client secret
   - `REDIRECT_URI`: Your registered redirect URI
   - `TEST_USERNAME`: Sandbox test customer number (default: 123456789012)

**IMPORTANT**: Never commit `config.py` to version control. It's already listed in `.gitignore`.

## Getting Your Credentials

1. Go to [NatWest Developer Sandbox](https://developer.sandbox.natwest.com/)
2. Register or log in to your account
3. Create a new application or select an existing one
4. Navigate to your app's details page
5. Copy your Client ID and Client Secret
6. Make sure your Redirect URI is registered in the app settings
7. Enable these sandbox features for your app:
   - "Allow programmatic authorisation"
   - "Allow reduced security"

## Usage

Run the script:
```bash
python natwest_account_fetcher.py
```

The script will:
1. Get a client credentials token
2. Create an account access consent
3. Auto-authorize the consent (sandbox mode)
4. Exchange authorization code for access token
5. Fetch and display account details, balances, and transactions

## Output

The script displays:
- Account ID, type, and currency
- Account number details
- Current balances (Available, Current, etc.)
- Recent transactions (last 5 by default)

## Project Structure

```
balance_check/
│
├── natwest_account_fetcher.py    # Main script
├── config.py                      # Your credentials (not in git)
├── config.example.py              # Template for config.py
├── .gitignore                     # Git ignore rules
├── README.md                      # This file
└── requirements.txt               # Python dependencies
```

## Security Notes

- This script is for **sandbox testing only**
- Never commit credentials to version control
- `config.py` is in `.gitignore` to prevent accidental commits
- For production use, implement proper secret management

## Troubleshooting

### "Configuration file not found"
Copy `config.example.py` to `config.py` and add your credentials.

### "403 Forbidden - no API access for this client"
Enable the Account & Transaction API in your app settings on the developer portal.

### "AUTO authorization_mode can only be used if..."
Enable "Allow programmatic authorisation" in your app's API configuration.

### "Impossible to verify signature of the jwt"
Enable "Allow reduced security" in your app's API configuration.

## API Documentation

- [NatWest Developer Portal](https://developer.sandbox.natwest.com/)
- [Getting Started Guide](https://developer.sandbox.natwest.com/api-catalog/4767019/getting-started)
- [Open Banking Specification](https://standards.openbanking.org.uk/)

## License

MIT License - feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please ensure you don't commit any credentials or sensitive information.

## Disclaimer

This is a sandbox testing tool. Do not use production credentials or real customer data with this script.