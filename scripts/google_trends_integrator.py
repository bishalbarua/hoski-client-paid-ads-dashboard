"""
Google Trends Integrator
Purpose: Takes a client's core keyword themes and fetches relative search
         interest from Google Trends. Outputs a monthly seasonality index
         per topic for the trailing 24 months. Supplements account history
         seasonality with market-level demand signals.

         Useful for:
           - Clients with less than 12 months of account history
           - Industry-level trend confirmation
           - Spotting emerging topic opportunities before they show in account data

Setup:
    Requires: pip install pytrends (add to requirements.txt)
    No API key required — uses Google Trends unofficial API.

    NOTE: pytrends may be rate-limited or blocked intermittently.
    If you get 429 errors, wait 60 seconds and try again.

Usage:
    python3 scripts/google_trends_integrator.py --customer-id 5544702166
    python3 scripts/google_trends_integrator.py --keywords "dental implants" "dental veneers" --geo CA-ON
    python3 scripts/google_trends_integrator.py --keywords "furniture store" --geo CA

    Geo codes: US (United States), CA (Canada), CA-ON (Ontario), CA-BC (British Columbia)

Changelog:
    2026-03-23  Initial version — monthly relative interest, seasonality index,
                trend direction, and peak month identification.
"""

import argparse
import os
import time
from collections import defaultdict
from datetime import date, timedelta

from dotenv import load_dotenv

load_dotenv()

# ─── CLIENT REGISTRY (for auto-keyword lookup hints) ─────────────────────────

CLIENT_KEYWORDS = {
    "5865660247": {"name": "Anand Desai Law Firm",    "keywords": ["personal injury lawyer", "car accident lawyer"], "geo": "US-TX"},
    "3857223862": {"name": "Dentiste",                "keywords": ["dentist near me", "dental cleaning"],            "geo": "CA-QC"},
    "7709532223": {"name": "Estate Jewelry Priced Right", "keywords": ["estate jewelry", "vintage jewelry"],         "geo": "US"},
    "9304117954": {"name": "FaBesthetics",            "keywords": ["botox near me", "lip filler"],                   "geo": "US-IL"},
    "5544702166": {"name": "Hoski.ca",                "keywords": ["premium socks", "performance socks"],            "geo": "CA"},
    "3720173680": {"name": "New Norseman",            "keywords": ["brewery near me", "craft beer"],                 "geo": "CA-ON"},
    "7228467515": {"name": "Park Road Custom Furniture", "keywords": ["custom furniture", "handmade furniture"],     "geo": "CA-ON"},
    "8134824884": {"name": "Serenity Familycare",     "keywords": ["family doctor near me", "family clinic"],        "geo": "CA"},
    "7628667762": {"name": "Synergy Spine",           "keywords": ["spine surgeon near me", "back pain specialist"], "geo": "US"},
    "8159668041": {"name": "Texas FHC",               "keywords": ["home care services", "in home care"],            "geo": "US-TX"},
    "5216656756": {"name": "Voit Dental",             "keywords": ["dentist near me", "dental implants"],            "geo": "CA-ON"},
}

MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# ─── TRENDS PULL ─────────────────────────────────────────────────────────────

def pull_trends(keywords, geo="US", months=24):
    """
    Pull relative monthly search interest from Google Trends.
    Returns dict: keyword -> list of (year, month, interest) tuples.
    """
    try:
        from pytrends.request import TrendReq
    except ImportError:
        print("ERROR: pytrends not installed. Run: pip install pytrends")
        return {}

    today      = date.today()
    start_date = (today.replace(day=1) - timedelta(days=months * 31)).strftime("%Y-%m")
    timeframe  = f"{start_date}-01 {today.strftime('%Y-%m-%d')}"

    # pytrends only supports 5 keywords at a time
    all_results = {}

    chunks = [keywords[i:i+5] for i in range(0, len(keywords), 5)]
    for chunk in chunks:
        try:
            pytrends = TrendReq(hl="en-US", tz=0)
            pytrends.build_payload(chunk, cat=0, timeframe=timeframe, geo=geo, gprop="")
            df = pytrends.interest_over_time()

            if df.empty:
                print(f"  No data returned for: {chunk}")
                continue

            for kw in chunk:
                if kw in df.columns:
                    monthly = defaultdict(list)
                    for idx, row in df.iterrows():
                        year  = idx.year
                        month = idx.month
                        monthly[(year, month)].append(row[kw])
                    all_results[kw] = {
                        (y, m): sum(vals) / len(vals)
                        for (y, m), vals in monthly.items()
                    }

            # Rate limit protection
            time.sleep(1)

        except Exception as e:
            print(f"  Trends error for {chunk}: {e}")
            time.sleep(5)

    return all_results


def build_seasonal_index(monthly_values):
    """
    Compute monthly seasonal index from trend data.
    Groups by calendar month, averages across years.
    """
    by_month = defaultdict(list)
    for (year, month), val in monthly_values.items():
        if val > 0:
            by_month[month].append(val)

    month_avgs = {m: sum(vals) / len(vals) if vals else 0.0
                  for m in range(1, 13)
                  for vals in [by_month.get(m, [])]}

    all_avgs   = [v for v in month_avgs.values() if v > 0]
    annual_avg = sum(all_avgs) / len(all_avgs) if all_avgs else 1.0

    if annual_avg == 0:
        return {m: 1.0 for m in range(1, 13)}

    return {m: month_avgs[m] / annual_avg for m in range(1, 13)}


def trend_direction(monthly_values):
    """Simple linear trend: compare first half avg vs second half avg."""
    sorted_vals = [v for _, v in sorted(monthly_values.items())]
    if len(sorted_vals) < 4:
        return "insufficient data"
    mid   = len(sorted_vals) // 2
    first = sum(sorted_vals[:mid]) / mid
    last  = sum(sorted_vals[mid:]) / (len(sorted_vals) - mid)
    if last > first * 1.10:
        return "GROWING"
    elif last < first * 0.90:
        return "DECLINING"
    return "STABLE"


def bar(index, width=15):
    filled = round(index * width)
    return "█" * min(filled, 25)


# ─── PRINT REPORT ─────────────────────────────────────────────────────────────

def print_report(keywords, results, geo, months):
    run_date = date.today().strftime("%Y-%m-%d")
    print(f"\nGOOGLE TRENDS INTEGRATOR")
    print(f"Geo: {geo}  |  Lookback: {months} months  |  Run date: {run_date}")
    print("=" * 70)

    if not results:
        print("  No trend data retrieved. Check keywords and geo code.")
        return

    for kw in keywords:
        if kw not in results:
            print(f"\n  [{kw}]: No data")
            continue

        monthly = results[kw]
        index   = build_seasonal_index(monthly)
        trend   = trend_direction(monthly)
        peak    = max(index, key=index.get)
        trough  = min(index, key=lambda k: index[k] if index[k] > 0 else 99)

        print(f"\n  KEYWORD: \"{kw}\"  |  Trend: {trend}")
        print(f"  {'Month':<6} {'Index':>7} {'Chart':<18} Interpretation")
        print(f"  {'-'*6} {'-'*7} {'-'*18} {'-'*20}")

        for m in range(1, 13):
            idx  = index[m]
            note = ""
            if m == peak:
                note = "PEAK"
            elif m == trough:
                note = "LOW"
            elif idx >= 1.15:
                note = "Above avg"
            elif idx <= 0.85:
                note = "Below avg"
            print(f"  {MONTH_NAMES[m-1]:<6} {idx:>6.2f}x {bar(idx):<18} {note}")

        print(f"  Peak: {MONTH_NAMES[peak-1]} ({index[peak]:.2f}x)  |  Low: {MONTH_NAMES[trough-1]} ({index[trough]:.2f}x)")

    print(f"\n{'='*70}")
    print("  Use these multipliers to adjust client budgets before peak months.")
    print("  Compare against account history (seasonality_forecaster.py) for validation.")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Google Trends integrator — seasonal interest and trend direction"
    )
    parser.add_argument("--customer-id", help="Account ID (auto-loads keyword presets)")
    parser.add_argument("--keywords",    nargs="+", help="Keywords to analyse (up to 5)")
    parser.add_argument("--geo",         default="US",
                        help="Geo code: US, CA, CA-ON, CA-BC, US-TX, etc. (default: US)")
    parser.add_argument("--months",      type=int, default=24,
                        help="Months of history (default: 24)")
    args = parser.parse_args()

    keywords = args.keywords
    geo      = args.geo

    # Auto-load presets from customer ID if no keywords specified
    if not keywords and args.customer_id:
        cid = args.customer_id.replace("-", "")
        if cid in CLIENT_KEYWORDS:
            preset   = CLIENT_KEYWORDS[cid]
            keywords = preset["keywords"]
            geo      = args.geo if args.geo != "US" else preset.get("geo", "US")
            print(f"Using preset keywords for {preset['name']}: {keywords}")

    if not keywords:
        print("ERROR: Provide --keywords or a --customer-id with registered presets.")
        return

    keywords = keywords[:5]  # pytrends limit per call

    print(f"\nFetching Google Trends for: {keywords}")
    print(f"Geo: {geo}  |  Months: {args.months}")

    results = pull_trends(keywords, geo=geo, months=args.months)
    print_report(keywords, results, geo, args.months)


if __name__ == "__main__":
    main()
