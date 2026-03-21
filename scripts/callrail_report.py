"""
CallRail Report
Pulls call data across all client accounts and cross-analyzes with ad source (Google, Meta, etc.)
Usage: python scripts/callrail_report.py [--days 30] [--client "Texas FHC"]
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from collections import defaultdict
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("CALLRAIL_API_KEY")
BASE_URL = "https://api.callrail.com/v3"

HEADERS = {
    "Authorization": f"Token token={API_KEY}",
    "Content-Type": "application/json",
}

SOURCE_MAP = {
    "google ads": "google",
    "google cpc": "google",
    "adwords": "google",
    "google organic": "organic",
    "facebook ads": "meta",
    "instagram ads": "meta",
    "facebook organic": "meta",
    "organic": "organic",
    "direct": "direct",
    "referral": "referral",
}


def get_all_accounts():
    resp = requests.get(f"{BASE_URL}/a.json", headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    return data.get("accounts", [])


def get_calls(account_id, start_date, end_date, page=1):
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "per_page": 250,
        "page": page,
        "fields": "id,start_time,duration,answered,source,source_name,utm_source,utm_medium,utm_campaign,first_call,lead_status,direction,gclid,fbclid",
    }
    resp = requests.get(f"{BASE_URL}/a/{account_id}/calls.json", headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json()


def fetch_all_calls(account_id, start_date, end_date):
    all_calls = []
    page = 1
    while True:
        data = get_calls(account_id, start_date, end_date, page)
        calls = data.get("calls", [])
        all_calls.extend(calls)
        if page >= data.get("total_pages", 1):
            break
        page += 1
    return all_calls


def classify_source(call):
    # gclid/fbclid are the most reliable signal for paid ad attribution.
    # They persist even when the session source shows as "Direct" on return visits.
    if call.get("gclid"):
        return "google"
    if call.get("fbclid"):
        return "meta"
    raw = (call.get("source") or call.get("utm_source") or call.get("utm_medium") or "unknown").lower()
    return SOURCE_MAP.get(raw, "other")


def analyze_calls(calls):
    stats = defaultdict(lambda: {
        "total": 0,
        "answered": 0,
        "missed": 0,
        "first_calls": 0,
        "total_duration_sec": 0,
        "campaigns": defaultdict(int),
    })

    for call in calls:
        source = classify_source(call)
        s = stats[source]
        s["total"] += 1
        if call.get("answered"):
            s["answered"] += 1
        else:
            s["missed"] += 1
        if call.get("first_call"):
            s["first_calls"] += 1
        s["total_duration_sec"] += call.get("duration", 0) or 0
        campaign = call.get("utm_campaign") or "unknown"
        s["campaigns"][campaign] += 1

    return stats


def print_account_report(account_name, calls, start_date, end_date):
    print(f"\n{'='*60}")
    print(f"  {account_name}")
    print(f"  {start_date} to {end_date}")
    print(f"{'='*60}")

    if not calls:
        print("  No calls found for this period.")
        return

    stats = analyze_calls(calls)
    total_calls = len(calls)
    print(f"  Total calls: {total_calls}\n")

    source_order = ["google", "meta", "organic", "direct", "referral", "other"]
    for source in source_order:
        s = stats.get(source)
        if not s or s["total"] == 0:
            continue
        pct = round(s["total"] / total_calls * 100)
        answered_rate = round(s["answered"] / s["total"] * 100) if s["total"] else 0
        avg_dur = round(s["total_duration_sec"] / s["total"]) if s["total"] else 0
        avg_min = f"{avg_dur // 60}m {avg_dur % 60}s"

        print(f"  [{source.upper()}]")
        print(f"    Calls:         {s['total']} ({pct}% of total)")
        print(f"    Answered:      {s['answered']} ({answered_rate}% answer rate)")
        print(f"    New leads:     {s['first_calls']}")
        print(f"    Avg duration:  {avg_min}")

        top_campaigns = sorted(s["campaigns"].items(), key=lambda x: x[1], reverse=True)[:3]
        if top_campaigns and not (len(top_campaigns) == 1 and top_campaigns[0][0] == "unknown"):
            print(f"    Top campaigns: {', '.join(f'{c} ({n})' for c, n in top_campaigns)}")
        print()


def main():
    parser = argparse.ArgumentParser(description="CallRail cross-channel call report")
    parser.add_argument("--days", type=int, default=30, help="Number of days to look back (default: 30)")
    parser.add_argument("--client", type=str, default=None, help="Filter to a specific client account name")
    args = parser.parse_args()

    if not API_KEY:
        print("ERROR: CALLRAIL_API_KEY not set in .env")
        sys.exit(1)

    end_date = datetime.today().strftime("%Y-%m-%d")
    start_date = (datetime.today() - timedelta(days=args.days)).strftime("%Y-%m-%d")

    print(f"\nCallRail Report: {start_date} to {end_date} ({args.days} days)")

    accounts = get_all_accounts()

    if args.client:
        accounts = [a for a in accounts if args.client.lower() in a["name"].lower()]
        if not accounts:
            print(f"No account found matching '{args.client}'")
            sys.exit(1)

    for account in accounts:
        name = account["name"]
        acc_id = account["id"]
        try:
            calls = fetch_all_calls(acc_id, start_date, end_date)
            print_account_report(name, calls, start_date, end_date)
        except requests.HTTPError as e:
            print(f"\n[{name}] API error: {e}")


if __name__ == "__main__":
    main()
