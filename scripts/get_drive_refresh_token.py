"""
Google Drive OAuth2 Refresh Token Generator
Run this once to authorize Drive access, then store the refresh token in .env.

Usage:
    python3 scripts/get_drive_refresh_token.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive"]

CLIENT_CONFIG = {
    "installed": {
        "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"],
    }
}


def main():
    flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
    credentials = flow.run_local_server(port=8080)
    print("\n=== Google Drive Refresh Token ===")
    print(credentials.refresh_token)
    print("\nAdd this to your .env file:")
    print(f'GOOGLE_DRIVE_REFRESH_TOKEN="{credentials.refresh_token}"')


if __name__ == "__main__":
    main()
