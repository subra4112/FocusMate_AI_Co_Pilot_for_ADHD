"""
Exchange authorization code for refresh token.
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import json
import os

# Allow insecure transport for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Allow scope changes (you granted more permissions than requested)
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

SCOPES = ['https://www.googleapis.com/auth/calendar']

def exchange_code():
    """Exchange the authorization code for tokens."""
    
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', 
        SCOPES,
        redirect_uri='http://localhost:8080'
    )
    
    # The full redirect URL from the browser
    redirect_response = "http://localhost:8080/?code=4/0Ab32j90RPgSpcZvVqx-eZElAebj4JxgygQZFJ6v32ZOnr1s-_2a-w7ET1e8kvmLSXhzFTA&scope=https://www.googleapis.com/auth/calendar"
    
    try:
        # Exchange code for token
        flow.fetch_token(authorization_response=redirect_response)
        creds = flow.credentials
        
        # Display the tokens
        print("\n" + "="*70)
        print("SUCCESS! Here are your credentials:")
        print("="*70)
        print(f"\nGOOGLE_CLIENT_ID={creds.client_id}")
        print(f"GOOGLE_CLIENT_SECRET={creds.client_secret}")
        print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
        print("\n" + "="*70)
        print("\nAdd these to your .env file!")
        print("="*70)
        
        # Save to token.json
        with open('token.json', 'w') as f:
            token_data = {
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'refresh_token': creds.refresh_token,
                'token_uri': 'https://oauth2.googleapis.com/token',
                'scopes': SCOPES
            }
            json.dump(token_data, f, indent=2)
        
        print("\ntoken.json has been created!")
        print("Now you can run test_voice.py and it will sync to Google Calendar!")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    exchange_code()

