"""
Google Sheets Writer
Purpose: Write Google Ads and Meta campaign data to a Google Sheet using
         a service account. Acts as a shared utility called by other scripts.

Setup:
    1. Place sheets-credentials.json in the project root (already gitignored).
    2. Share your Google Sheet with the service account email in that JSON file.
    3. Add GOOGLE_SHEETS_ID to your .env file (the sheet ID from the URL).

Usage (standalone):
    python3 scripts/sheets_writer.py --source google --mode weekly
    python3 scripts/sheets_writer.py --source meta   --mode monthly
    python3 scripts/sheets_writer.py --source google --customer-id 3720173680

    Or import and call directly from another script:
        from scripts.sheets_writer import write_google_snapshot, write_meta_snapshot

Environment:
    GOOGLE_SHEETS_ID          Target spreadsheet ID (from the sheet URL)
    GOOGLE_SHEETS_CREDS_PATH  Path to service account JSON (default: sheets-credentials.json)
"""

import argparse
import os
import sys
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

from scripts.client_registry import get_google_ads_targets, resolve_google_sheet_target

load_dotenv()

# ─── CONFIG ──────────────────────────────────────────────────────────────────

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_CREDS_PATH = PROJECT_ROOT / "sheets-credentials.json"


# ─── AUTH ─────────────────────────────────────────────────────────────────────

def get_sheets_client():
    creds_path = os.environ.get("GOOGLE_SHEETS_CREDS_PATH", str(DEFAULT_CREDS_PATH))
    if not Path(creds_path).exists():
        print(f"[Sheets] Credentials not found at: {creds_path}")
        sys.exit(1)
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return gspread.authorize(creds)


def get_sheet_id(client_name: str = None):
    fallback_sheet_id = os.environ.get("GOOGLE_SHEETS_ID")
    if client_name:
        try:
            sheet_id, _ = resolve_google_sheet_target(client_name, fallback_sheet_id=fallback_sheet_id)
        except KeyError:
            sheet_id = fallback_sheet_id
    else:
        sheet_id = fallback_sheet_id
    if not sheet_id:
        print("[Sheets] GOOGLE_SHEETS_ID not set in .env")
        sys.exit(1)
    return sheet_id


# ─── CORE WRITE ───────────────────────────────────────────────────────────────

def write_to_sheet(sheet_id: str, tab_name: str, headers: list, rows: list[list]):
    """
    Write headers + rows to a named tab. Creates the tab if it doesn't exist.
    Clears existing content before writing.
    """
    gc = get_sheets_client()
    spreadsheet = gc.open_by_key(sheet_id)

    # Get or create the tab
    try:
        ws = spreadsheet.worksheet(tab_name)
        ws.clear()
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=tab_name, rows=1000, cols=30)

    all_rows = [headers] + rows
    ws.update(all_rows, value_input_option="USER_ENTERED")
    print(f"[Sheets] Written {len(rows)} rows to tab '{tab_name}'")


# ─── GOOGLE ADS FORMATTERS ────────────────────────────────────────────────────

GOOGLE_HEADERS = [
    "Client", "Account ID", "Campaign", "Status", "Channel", "Bidding",
    "Daily Budget", "Spend", "Impressions", "Clicks", "CTR %", "CPC",
    "Total Conversions", "Phone Calls", "Leads", "Purchases",
    "Revenue", "CPA", "CPL", "Cost/Call", "CPP", "ROAS",
    "Excluded Conv", "Period Start", "Period End", "Pulled At",
]


def google_campaigns_to_rows(
    client_name: str,
    customer_id: str,
    campaigns: dict,
    period_start: str,
    period_end: str,
) -> list[list]:
    pulled_at = date.today().isoformat()
    rows = []
    for camp in sorted(campaigns.values(), key=lambda c: c["cost"], reverse=True):
        rows.append([
            client_name,
            customer_id,
            camp["name"],
            camp.get("status", ""),
            camp.get("channel", ""),
            camp.get("bidding", ""),
            round(camp.get("daily_budget", 0), 2),
            round(camp["cost"], 2),
            camp["impressions"],
            camp["clicks"],
            round(camp["ctr"] * 100, 4) if camp.get("ctr") else 0,
            round(camp["cpc"], 2) if camp.get("cpc") else 0,
            round(camp["total_real_conv"], 1),
            round(camp["phone_conv"], 1),
            round(camp["lead_conv"], 1),
            round(camp["purchase_conv"], 1),
            round(camp["purchase_value"], 2),
            round(camp["cpa"], 2) if camp.get("cpa") else "",
            round(camp["cost_per_lead"], 2) if camp.get("cost_per_lead") else "",
            round(camp["cost_per_call"], 2) if camp.get("cost_per_call") else "",
            round(camp["cost_per_purchase"], 2) if camp.get("cost_per_purchase") else "",
            round(camp["roas"], 2) if camp.get("roas") else "",
            round(camp.get("excluded_conv", 0), 1),
            period_start,
            period_end,
            pulled_at,
        ])
    return rows


def write_google_snapshot(
    client_name: str,
    customer_id: str,
    campaigns: dict,
    period_start: str,
    period_end: str,
    tab_name: str = None,
):
    """Write a Google Ads campaign snapshot to Sheets."""
    sheet_id = get_sheet_id(client_name)
    try:
        _, default_tab = resolve_google_sheet_target(client_name, fallback_sheet_id=sheet_id, fallback_tab=tab_name)
    except KeyError:
        default_tab = tab_name or f"Google - {client_name}"
    tab = tab_name or default_tab
    rows = google_campaigns_to_rows(client_name, customer_id, campaigns, period_start, period_end)
    write_to_sheet(sheet_id, tab, GOOGLE_HEADERS, rows)


# ─── META FORMATTERS ──────────────────────────────────────────────────────────

META_HEADERS = [
    "Client", "Account ID", "Campaign", "Status", "Objective",
    "Spend", "Impressions", "Clicks", "Reach", "Frequency",
    "CTR %", "CPC", "CPM",
    "Total Results", "Purchases", "Revenue", "Leads",
    "CPA", "CPP", "CPL", "ROAS",
    "Daily Budget", "Lifetime Budget",
    "Period Start", "Period End", "Pulled At",
]


def meta_campaigns_to_rows(
    client_name: str,
    account_id: str,
    campaigns: dict,
    period_start: str,
    period_end: str,
) -> list[list]:
    pulled_at = date.today().isoformat()
    rows = []
    for camp in sorted(campaigns.values(), key=lambda c: c["spend"], reverse=True):
        rows.append([
            client_name,
            account_id,
            camp["name"],
            camp.get("status", ""),
            camp.get("objective", ""),
            round(camp["spend"], 2),
            camp["impressions"],
            camp["clicks"],
            camp.get("reach", 0),
            round(camp.get("frequency", 0), 2),
            round(camp["ctr"], 4) if camp.get("ctr") else 0,
            round(camp["cpc"], 2) if camp.get("cpc") else 0,
            round(camp.get("cpm", 0), 2),
            round(camp["total_results"], 1),
            round(camp["purchases"], 1),
            round(camp["purchase_value"], 2),
            round(camp["leads"], 1),
            round(camp["cpa"], 2) if camp.get("cpa") else "",
            round(camp["cpp"], 2) if camp.get("cpp") else "",
            round(camp["cpl"], 2) if camp.get("cpl") else "",
            round(camp["roas"], 2) if camp.get("roas") else "",
            round(camp["daily_budget"], 2) if camp.get("daily_budget") else "",
            round(camp["lifetime_budget"], 2) if camp.get("lifetime_budget") else "",
            period_start,
            period_end,
            pulled_at,
        ])
    return rows


def write_meta_snapshot(
    client_name: str,
    account_id: str,
    campaigns: dict,
    period_start: str,
    period_end: str,
    tab_name: str = None,
):
    """Write a Meta campaign snapshot to Sheets."""
    sheet_id = get_sheet_id()
    tab = tab_name or f"Meta - {client_name}"
    rows = meta_campaigns_to_rows(client_name, account_id, campaigns, period_start, period_end)
    write_to_sheet(sheet_id, tab, META_HEADERS, rows)


# ─── STANDALONE RUNNER ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Push campaign snapshot data to Google Sheets")
    parser.add_argument("--source", choices=["google", "meta"], required=True,
                        help="Data source: google or meta")
    parser.add_argument("--mode", choices=["weekly", "monthly"], default="weekly",
                        help="Date range mode. Default: weekly")
    parser.add_argument("--customer-id", help="Google Ads: single account ID")
    parser.add_argument("--account",     help="Meta: single ad account ID (e.g. act_XXXXXXX)")
    parser.add_argument("--tab",         help="Override the tab name in the sheet")
    args = parser.parse_args()

    today = date.today()
    if args.mode == "weekly":
        end   = today - timedelta(days=1)
        start = end - timedelta(days=6)
    else:
        end   = today - timedelta(days=1)
        start = end - timedelta(days=29)

    period_start = start.isoformat()
    period_end   = end.isoformat()

    if args.source == "google":
        # Import here to avoid requiring Google Ads creds when running Meta-only
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.google_campaign_performance_snapshot import (
            build_client, pull_campaign_metrics
        )
        ga_client  = build_client()
        ga_service = ga_client.get_service("GoogleAdsService")

        if args.customer_id:
            targets = {args.customer_id: args.customer_id.replace("-", "")}
        else:
            targets = get_google_ads_targets()

        for name, cid in targets.items():
            print(f"Pulling Google Ads: {name} ({cid}) ...")
            campaigns = pull_campaign_metrics(ga_service, cid, period_start, period_end)
            if campaigns:
                write_google_snapshot(name, cid, campaigns, period_start, period_end, tab_name=args.tab)
            else:
                print(f"  No data for {name}")

    elif args.source == "meta":
        sys.path.insert(0, str(PROJECT_ROOT))
        from scripts.meta_campaign_snapshot import (
            init_api, ALL_CLIENTS as META_CLIENTS, pull_campaign_metrics as meta_pull
        )
        init_api()

        if args.account:
            targets = {args.account: args.account}
        else:
            targets = {name: acct for name, acct in META_CLIENTS.items()}

        for name, account_id in targets.items():
            print(f"Pulling Meta: {name} ({account_id}) ...")
            campaigns = meta_pull(account_id, period_start, period_end)
            if campaigns:
                write_meta_snapshot(name, account_id, campaigns, period_start, period_end, tab_name=args.tab)
            else:
                print(f"  No data for {name}")


if __name__ == "__main__":
    main()
