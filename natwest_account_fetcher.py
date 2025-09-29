#!/usr/bin/env python3
"""
NatWest Open Banking API - Account Details Fetcher
This script fetches user account details using NatWest's Open Banking API
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
import sys
import os

# Import configuration
try:
    from config import (
        CLIENT_ID, 
        CLIENT_SECRET, 
        REDIRECT_URI, 
        TEST_USERNAME,
        BASE_URL,
        AUTH_BASE_URL,
        API_VERSION
    )
except ImportError:
    print("\n" + "="*60)
    print("ERROR: Configuration file not found!")
    print("="*60)
    print("\nPlease create a 'config.py' file with your credentials.")
    print("You can copy 'config.example.py' and fill in your details.\n")
    sys.exit(1)


class NatWestAPIClient:
    """Client for NatWest Open Banking API"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, 
                 base_url: str, auth_base_url: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.base_url = base_url
        self.auth_base_url = auth_base_url
        self.access_token = None
        self.consent_id = None
        
    def get_client_credentials_token(self) -> bool:
        """Get access token using client credentials flow"""
        print("\n" + "="*60)
        print("STEP 1: Getting Client Credentials Token")
        print("="*60)
        
        url = f"{self.base_url}/token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'accounts'
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            
            print(f"✓ Token obtained successfully")
            print(f"  Token Type: {token_data.get('token_type')}")
            print(f"  Expires In: {token_data.get('expires_in')} seconds")
            print(f"  Scope: {token_data.get('scope')}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error getting token: {e}")
            if hasattr(e.response, 'text'):
                print(f"  Response: {e.response.text}")
            return False
    
    def create_account_consent(self) -> Optional[str]:
        """Create account access consent"""
        print("\n" + "="*60)
        print("STEP 2: Creating Account Access Consent")
        print("="*60)
        
        url = f"{self.base_url}/open-banking/v4.0/aisp/account-access-consents"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        data = {
            "Data": {
                "Permissions": [
                    "ReadAccountsDetail",
                    "ReadBalances",
                    "ReadTransactionsCredits",
                    "ReadTransactionsDebits",
                    "ReadTransactionsDetail",
                    "ReadProducts",
                    "ReadBeneficiariesDetail",
                    "ReadDirectDebits",
                    "ReadOffers",
                    "ReadScheduledPaymentsDetail",
                    "ReadStandingOrdersDetail",
                    "ReadStatementsDetail"
                ]
            },
            "Risk": {}
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            consent_data = response.json()
            self.consent_id = consent_data.get('Data', {}).get('ConsentId')
            
            print(f"✓ Consent created successfully")
            print(f"  Consent ID: {self.consent_id}")
            print(f"  Status: {consent_data.get('Data', {}).get('Status')}")
            print(f"  Created: {consent_data.get('Data', {}).get('CreationDateTime')}")
            
            return self.consent_id
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error creating consent: {e}")
            if hasattr(e.response, 'text'):
                print(f"  Response: {e.response.text}")
            return None
    
    def authorize_consent(self, username: str = "123456789012") -> Optional[str]:
        """
        Authorize consent (Auto-approval for sandbox)
        Returns authorization code
        """
        print("\n" + "="*60)
        print("STEP 3: Authorizing Consent (Sandbox Auto-Approval)")
        print("="*60)
        
        # Build authorization URL with auto-approval parameters
        auth_params = {
            'client_id': self.client_id,
            'response_type': 'code id_token',
            'scope': 'openid accounts',
            'redirect_uri': self.redirect_uri,
            'state': 'ABC',
            'request': self.consent_id,
            'authorization_mode': 'AUTO_POSTMAN',
            'authorization_username': f"{username}@55b21c17-7172-4105-8eff-750fe83efef9.example.org",
            'authorization_result': 'APPROVED',
            'authorization_accounts': '*'
        }
        
        url = f"{self.auth_base_url}/authorize"
        
        try:
            # Make first request with allow_redirects=False to capture the redirect
            print("  Making initial authorization request...")
            response = requests.get(url, params=auth_params, allow_redirects=False)
            
            # Check if we got a redirect
            if response.status_code in [302, 303, 307, 308]:
                location = response.headers.get('Location', '')
                print(f"  Got redirect to: {location[:80]}...")
                
                # Check if there's a code in the first redirect
                if 'code=' in location:
                    auth_code = location.split('code=')[1].split('&')[0]
                    print(f"✓ Authorization successful")
                    print(f"  Authorization Code: {auth_code[:20]}...")
                    return auth_code
                
                # If no code yet, follow the redirect (it's another authorization endpoint)
                print("  Following redirect to complete authorization...")
                
                # Make GET request to the authorization endpoint
                response2 = requests.get(location)
                
                # Check if response is JSON (AUTO_POSTMAN mode returns JSON)
                if response2.status_code == 200:
                    try:
                        # Try to parse as JSON
                        json_response = response2.json()
                        
                        if 'redirectUri' in json_response:
                            redirect_uri = json_response['redirectUri']
                            print(f"  Got redirect URI from JSON response")
                            
                            # Extract authorization code from redirect URI
                            if 'code=' in redirect_uri:
                                auth_code = redirect_uri.split('code=')[1].split('&')[0]
                                print(f"✓ Authorization successful")
                                print(f"  Authorization Code: {auth_code[:20]}...")
                                return auth_code
                            else:
                                print(f"✗ No authorization code in redirect URI")
                                print(f"  Redirect URI: {redirect_uri}")
                                return None
                        else:
                            print(f"✗ No redirectUri in JSON response")
                            print(f"  Response: {json_response}")
                            return None
                    except json.JSONDecodeError:
                        print(f"✗ Response is not JSON")
                        print(f"  Response preview: {response2.text[:300]}...")
                        return None
                
                # Handle redirect responses (AUTO mode)
                elif response2.status_code in [302, 303, 307, 308]:
                    location2 = response2.headers.get('Location', '')
                    print(f"  Got redirect to: {location2[:80]}...")
                    
                    if 'code=' in location2:
                        auth_code = location2.split('code=')[1].split('&')[0]
                        print(f"✓ Authorization successful")
                        print(f"  Authorization Code: {auth_code[:20]}...")
                        return auth_code
                    else:
                        print(f"✗ No authorization code in redirect")
                        return None
                else:
                    print(f"✗ Unexpected response status: {response2.status_code}")
                    print(f"  Response preview: {response2.text[:300]}...")
                    return None
            else:
                print(f"✗ Unexpected response status: {response.status_code}")
                print(f"  Response text: {response.text[:200]}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Error during authorization: {e}")
            return None
    
    def exchange_authorization_code(self, auth_code: str) -> bool:
        """Exchange authorization code for access token"""
        print("\n" + "="*60)
        print("STEP 4: Exchanging Authorization Code for Access Token")
        print("="*60)
        
        url = f"{self.base_url}/token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code',
            'code': auth_code
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get('access_token')
            
            print(f"✓ Access token obtained")
            print(f"  Token Type: {token_data.get('token_type')}")
            print(f"  Expires In: {token_data.get('expires_in')} seconds")
            print(f"  Scope: {token_data.get('scope')}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error exchanging code: {e}")
            if hasattr(e.response, 'text'):
                print(f"  Response: {e.response.text}")
            return False
    
    def get_accounts(self) -> Optional[List[Dict]]:
        """Fetch all accounts"""
        print("\n" + "="*60)
        print("STEP 5: Fetching Account Details")
        print("="*60)
        
        url = f"{self.base_url}/open-banking/v4.0/aisp/accounts"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            accounts_data = response.json()
            accounts = accounts_data.get('Data', {}).get('Account', [])
            
            print(f"✓ Retrieved {len(accounts)} account(s)")
            
            return accounts
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching accounts: {e}")
            if hasattr(e.response, 'text'):
                print(f"  Response: {e.response.text}")
            return None
    
    def get_account_balances(self, account_id: str) -> Optional[List[Dict]]:
        """Fetch account balances"""
        url = f"{self.base_url}/open-banking/v4.0/aisp/accounts/{account_id}/balances"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            balance_data = response.json()
            balances = balance_data.get('Data', {}).get('Balance', [])
            
            return balances
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching balances: {e}")
            return None
    
    def get_account_transactions(self, account_id: str, limit: int = 10) -> Optional[List[Dict]]:
        """Fetch account transactions"""
        url = f"{self.base_url}/open-banking/v4.0/aisp/accounts/{account_id}/transactions"
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            transaction_data = response.json()
            transactions = transaction_data.get('Data', {}).get('Transaction', [])
            
            # Return only the requested number of transactions
            return transactions[:limit]
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching transactions: {e}")
            return None
    
    def display_account_details(self, accounts: List[Dict]):
        """Display formatted account details"""
        print("\n" + "="*60)
        print("ACCOUNT DETAILS")
        print("="*60)
        
        for idx, account in enumerate(accounts, 1):
            print(f"\n{'─'*60}")
            print(f"ACCOUNT #{idx}")
            print(f"{'─'*60}")
            
            # Basic account info
            print(f"\n📋 Account Information:")
            print(f"  Account ID: {account.get('AccountId')}")
            print(f"  Account Type: {account.get('AccountType')}")
            print(f"  Account Sub Type: {account.get('AccountSubType')}")
            print(f"  Currency: {account.get('Currency')}")
            print(f"  Nickname: {account.get('Nickname', 'N/A')}")
            print(f"  Status: {account.get('Status', 'N/A')}")
            
            # Account details
            if 'Account' in account:
                acc_details = account['Account'][0] if isinstance(account['Account'], list) else account['Account']
                print(f"\n  Account Number:")
                print(f"    Scheme: {acc_details.get('SchemeName')}")
                print(f"    Identification: {acc_details.get('Identification')}")
                print(f"    Name: {acc_details.get('Name', 'N/A')}")
            
            # Fetch and display balances
            account_id = account.get('AccountId')
            balances = self.get_account_balances(account_id)
            
            if balances:
                print(f"\n💰 Balances:")
                for balance in balances:
                    bal_type = balance.get('Type')
                    amount = balance.get('Amount', {})
                    indicator = balance.get('CreditDebitIndicator')
                    
                    print(f"  {bal_type}:")
                    print(f"    Amount: {amount.get('Currency')} {amount.get('Amount')}")
                    print(f"    Type: {indicator}")
                    print(f"    Date: {balance.get('DateTime', 'N/A')}")
            
            # Fetch and display recent transactions
            transactions = self.get_account_transactions(account_id, limit=5)
            
            if transactions:
                print(f"\n📊 Recent Transactions (Last 5):")
                for txn_idx, txn in enumerate(transactions, 1):
                    amount = txn.get('Amount', {})
                    indicator = txn.get('CreditDebitIndicator')
                    sign = '+' if indicator == 'Credit' else '-'
                    
                    print(f"\n  Transaction {txn_idx}:")
                    print(f"    Date: {txn.get('BookingDateTime', 'N/A')}")
                    print(f"    Amount: {sign}{amount.get('Currency')} {amount.get('Amount')}")
                    print(f"    Type: {indicator}")
                    print(f"    Description: {txn.get('TransactionInformation', 'N/A')}")
                    print(f"    Reference: {txn.get('TransactionReference', 'N/A')}")
            
            print()


def main():
    """Main function to run the account details fetcher"""
    
    print("\n" + "="*60)
    print("NatWest Open Banking - Account Details Fetcher")
    print("="*60)
    print("Environment: Sandbox")
    print(f"API Version: {API_VERSION}")
    print(f"Test User: {TEST_USERNAME}")
    print("="*60)
    
    # Initialize client
    client = NatWestAPIClient(
        CLIENT_ID, 
        CLIENT_SECRET, 
        REDIRECT_URI,
        BASE_URL,
        AUTH_BASE_URL
    )
    
    # Step 1: Get initial access token
    if not client.get_client_credentials_token():
        print("\n✗ Failed to get initial token. Exiting.")
        sys.exit(1)
    
    # Step 2: Create consent
    consent_id = client.create_account_consent()
    if not consent_id:
        print("\n✗ Failed to create consent. Exiting.")
        sys.exit(1)
    
    # Step 3: Authorize consent
    auth_code = client.authorize_consent(TEST_USERNAME)
    if not auth_code:
        print("\n✗ Failed to authorize consent. Exiting.")
        sys.exit(1)
    
    # Step 4: Exchange authorization code for access token
    if not client.exchange_authorization_code(auth_code):
        print("\n✗ Failed to exchange authorization code. Exiting.")
        sys.exit(1)
    
    # Step 5: Get account details
    accounts = client.get_accounts()
    if not accounts:
        print("\n✗ Failed to fetch accounts. Exiting.")
        sys.exit(1)
    
    # Display formatted account details
    client.display_account_details(accounts)
    
    print("\n" + "="*60)
    print("✓ Account details fetched successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()