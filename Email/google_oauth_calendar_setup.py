"""Run this once to generate token.json with Gmail + Calendar scopes."""

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar.events",
]


def main() -> None:
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    with open("token.json", "w", encoding="utf-8") as token_file:
        token_file.write(creds.to_json())
    print("token.json saved with Gmail + Calendar scopes.")


if __name__ == "__main__":
    main()

