"""
Quick script to get a new Google Calendar refresh token.
Run this once to authenticate and get credentials.
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_refresh_token():
    """Get a fresh refresh token via OAuth flow."""
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("ERROR: credentials.json not found!")
        print("\nYou need to:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Enable Google Calendar API")
        print("3. Create OAuth 2.0 Client ID (Desktop app)")
        print("4. Download as credentials.json")
        return
    
    # Run the OAuth flow
    print("Starting OAuth flow...")
    print("A browser window will open. Sign in and grant permissions.")
    
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    # Use fixed port 8080 for web application OAuth
    creds = flow.run_local_server(port=8080)
    
    # Display the tokens
    print("\n" + "="*60)
    print("SUCCESS! Add these to your .env file:")
    print("="*60)
    print(f"\nGOOGLE_CLIENT_ID={creds.client_id}")
    print(f"GOOGLE_CLIENT_SECRET={creds.client_secret}")
    print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
    print("\n" + "="*60)
    
    # Save to token.json
    import json
    with open('token.json', 'w') as f:
        token_data = {
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'refresh_token': creds.refresh_token,
            'token_uri': 'https://oauth2.googleapis.com/token',
            'scopes': SCOPES
        }
        json.dump(token_data, f, indent=2)
    
    print("\ntoken.json has been updated!")
    print("Now you can run test_voice.py")

if __name__ == '__main__':
    get_refresh_token()

