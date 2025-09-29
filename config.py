# NatWest API Configuration Example
# Copy this file to 'config.py' and fill in your actual credentials
# DO NOT commit config.py to version control

# NatWest Sandbox Credentials
# Get these from: https://developer.sandbox.natwest.com/
CLIENT_ID = "C_YourClientIdHere"
CLIENT_SECRET = "YourClientSecretHere"
REDIRECT_URI = "http://balance-check.com"  # Must match your app's redirect URI

# Sandbox Test User
# Default sandbox test customer number
TEST_USERNAME = "123456789012"

# API Configuration
# Sandbox endpoints (do not change unless using production)
BASE_URL = "https://ob.sandbox.natwest.com"
AUTH_BASE_URL = "https://api.sandbox.natwest.com"
API_VERSION = "v4.0"
