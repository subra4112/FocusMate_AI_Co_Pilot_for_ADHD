from google_auth_oauthlib.flow import InstalledAppFlow
import json

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
creds = flow.run_local_server(port=0)

token_data = creds.to_json()
with open("token.json", "w") as f:
    f.write(token_data)

json.loads(token_data)  # raises if not valid
print("token.json saved and validated.")