"""
Google Ads OAuth2 Refresh Token Generator
Run this once to get your refresh token, then store it as an environment variable.
"""

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/adwords"]

# Replace with YOUR values from Google Cloud Console
CLIENT_CONFIG = {
    "installed": {
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

def main():
    flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
    credentials = flow.run_local_server(port=8080)
    print(f"\n=== Your Refresh Token ===")
    print(f"{credentials.refresh_token}")
    print(f"\nAdd this to your shell profile (~/.zshrc or ~/.bashrc):")
    print(f'export GOOGLE_ADS_REFRESH_TOKEN="{credentials.refresh_token}"')

if __name__ == "__main__":
    main()
