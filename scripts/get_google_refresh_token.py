"""
Google OAuth2 Refresh Token Generator
Run this once to get a refresh token covering Google Ads + Merchant Center,
then update GOOGLE_ADS_REFRESH_TOKEN in your .env file.

Reads CLIENT_ID and CLIENT_SECRET from .env automatically.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

SCOPES = [
    "https://www.googleapis.com/auth/adwords",
    "https://www.googleapis.com/auth/content",  # Google Merchant Center Content API
]


def main():
    client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("ERROR: GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET must be set in .env")
        return

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    credentials = flow.run_local_server(port=8085, prompt="consent")

    print(f"\n=== Your New Refresh Token ===")
    print(f"{credentials.refresh_token}")
    print(f"\nUpdate GOOGLE_ADS_REFRESH_TOKEN in your .env file with this value.")


if __name__ == "__main__":
    main()
