"""
Manual OAuth flow to get refresh token.
This version doesn't auto-open browser - you copy/paste URLs manually.
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_refresh_token_manual():
    """Get a fresh refresh token via manual OAuth flow."""
    
    if not os.path.exists('credentials.json'):
        print("ERROR: credentials.json not found!")
        return
    
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', 
        SCOPES,
        redirect_uri='http://localhost:8080'
    )
    
    # Generate the authorization URL
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    print("\n" + "="*70)
    print("STEP 1: Copy this URL and paste it in your browser:")
    print("="*70)
    print(auth_url)
    print("\n")
    
    print("="*70)
    print("STEP 2: Sign in and grant permissions")
    print("="*70)
    print("After granting permissions, you'll be redirected to a URL like:")
    print("http://localhost:8080/?code=XXXXX&scope=...")
    print("\n")
    
    print("="*70)
    print("STEP 3: Paste the ENTIRE redirect URL here:")
    print("="*70)
    redirect_response = input("Paste the full URL: ").strip()
    
    # Fetch the token
    try:
        flow.fetch_token(authorization_response=redirect_response)
        creds = flow.credentials
        
        # Display the tokens
        print("\n" + "="*70)
        print("SUCCESS! Add these to your .env file:")
        print("="*70)
        print(f"\nGOOGLE_CLIENT_ID={creds.client_id}")
        print(f"GOOGLE_CLIENT_SECRET={creds.client_secret}")
        print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
        print("\n" + "="*70)
        
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
        
        print("\ntoken.json has been created!")
        print("Now update your .env and run test_voice.py")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        print("\nMake sure you pasted the COMPLETE URL including http://")

if __name__ == '__main__':
    get_refresh_token_manual()

