"""
Test Meta Ads API connection.
Verifies credentials and lists all ad accounts accessible to the token.

Usage:
    python3 scripts/test_meta_connection.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.user import User

APP_ID = os.environ.get("META_APP_ID")
APP_SECRET = os.environ.get("META_APP_SECRET")
ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN")

missing = [k for k, v in {
    "META_APP_ID": APP_ID,
    "META_APP_SECRET": APP_SECRET,
    "META_ACCESS_TOKEN": ACCESS_TOKEN,
}.items() if not v]

if missing:
    print(f"Missing environment variables: {', '.join(missing)}")
    print("Check your .env file.")
    exit(1)

print("Initializing Meta Ads API...")
FacebookAdsApi.init(app_id=APP_ID, app_secret=APP_SECRET, access_token=ACCESS_TOKEN)

print("Fetching user info...")
me = User(fbid="me")
user_info = me.api_get(fields=["name", "email"])
print(f"  Authenticated as: {user_info.get('name')} ({user_info.get('email', 'no email')})")

print("\nFetching accessible ad accounts...")
ad_accounts = me.get_ad_accounts(fields=[
    "name",
    "account_id",
    "account_status",
    "currency",
    "timezone_name",
    "amount_spent",
])

if not ad_accounts:
    print("  No ad accounts found. Check your token permissions (needs ads_read).")
else:
    STATUS_MAP = {1: "Active", 2: "Disabled", 3: "Unsettled", 7: "Pending Review",
                  8: "Pending Closure", 9: "In Grace Period", 100: "Pending Closure",
                  101: "Closed", 201: "Any Active", 202: "Any Closed"}
    print(f"  Found {len(ad_accounts)} account(s):\n")
    for acct in ad_accounts:
        status = STATUS_MAP.get(acct.get("account_status"), "Unknown")
        spent = int(acct.get("amount_spent", 0)) / 100
        print(f"  Name:       {acct.get('name')}")
        print(f"  Account ID: act_{acct.get('account_id')}")
        print(f"  Status:     {status}")
        print(f"  Currency:   {acct.get('currency')}")
        print(f"  Timezone:   {acct.get('timezone_name')}")
        print(f"  Lifetime spend: {acct.get('currency')} {spent:,.2f}")
        print()

print("Connection test complete.")
