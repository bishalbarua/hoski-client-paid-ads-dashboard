"""
Channel Attribution Analyzer
Purpose: For clients running both Google Ads and Meta Ads, compares conversion
         data from both APIs side-by-side across the same date ranges. Flags:
           - Days where both channels spiked together (correlated lift)
           - Days where one channel succeeded alone (incremental signal)
           - Total reported conversions vs likely real business outcomes
           - Potential double-counting between platforms

         Relevant clients:
           Dentiste, FaBesthetics, Park Road, Hoski.ca, Estate Jewelry

Setup:
    Requires environment variables in .env:
        GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID,
        GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN,
        GOOGLE_ADS_CUSTOMER_ID

        META_ACCESS_TOKEN, META_APP_ID, META_APP_SECRET

Usage:
    python3 scripts/channel_attribution_analyzer.py \\
        --google-id 5544702166 --meta-id act_215505746566668
    python3 scripts/channel_attribution_analyzer.py \\
        --google-id 5544702166 --meta-id act_215505746566668 --days 60

Changelog:
    2026-03-23  Initial version — daily channel comparison, correlation,
                double-count risk flagging.
"""

import argparse
import os
from collections import defaultdict
from datetime import date, timedelta

import requests
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

load_dotenv()

# ─── CLIENT REGISTRY ─────────────────────────────────────────────────────────

DUAL_CHANNEL_CLIENTS = {
    # Google ID: Meta account ID
    "5544702166":  "act_215505746566668",   # Hoski.ca + Bloomer Health (example pair)
    "9304117954":  "act_215505746566668",   # FaBesthetics
}

# ─── GOOGLE ADS CLIENT ───────────────────────────────────────────────────────

def build_google_client():
    return GoogleAdsClient.load_from_dict({
        "developer_token":   os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "client_id":         os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret":     os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token":     os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "login_customer_id": os.environ["GOOGLE_ADS_CUSTOMER_ID"],
        "use_proto_plus":    True,
    })


def run_google_query(ga_service, customer_id, query):
    try:
        return list(ga_service.search(customer_id=customer_id, query=query))
    except GoogleAdsException as ex:
        for error in ex.failure.errors:
            print(f"  [Google API Error] {error.message}")
        return []


# ─── PULL GOOGLE DATA ─────────────────────────────────────────────────────────

def pull_google_daily(ga_service, google_id, start_date, end_date):
    """Pull daily conversions and spend from Google Ads."""
    rows = run_google_query(ga_service, google_id, f"""
        SELECT
            segments.date,
            metrics.conversions,
            metrics.cost_micros,
            metrics.clicks
        FROM customer
        WHERE segments.date >= '{start_date}'
          AND segments.date <= '{end_date}'
    """)

    daily = {}
    for row in rows:
        d = row.segments.date
        if d not in daily:
            daily[d] = {"conv": 0.0, "cost": 0.0, "clicks": 0}
        daily[d]["conv"]   += row.metrics.conversions
        daily[d]["cost"]   += row.metrics.cost_micros / 1_000_000
        daily[d]["clicks"] += row.metrics.clicks

    return daily


# ─── PULL META DATA ───────────────────────────────────────────────────────────

def pull_meta_daily(meta_account_id, start_date, end_date):
    """Pull daily conversions and spend from Meta Ads API."""
    access_token = os.environ.get("META_ACCESS_TOKEN", "")
    if not access_token:
        print("  WARNING: META_ACCESS_TOKEN not set. Skipping Meta data.")
        return {}

    # Clean up account ID format
    act_id = meta_account_id if meta_account_id.startswith("act_") else f"act_{meta_account_id}"

    url    = f"https://graph.facebook.com/v18.0/{act_id}/insights"
    params = {
        "access_token": access_token,
        "fields":       "date_start,spend,actions,action_values",
        "time_range":   f'{{"since":"{start_date}","until":"{end_date}"}}',
        "time_increment": 1,   # daily
        "level":        "account",
    }

    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  Meta API error: {e}")
        return {}

    daily = {}
    for row in data.get("data", []):
        d    = row["date_start"]
        conv = 0.0

        # Sum all "purchase" or "lead" conversion actions
        for action in row.get("actions", []):
            if action["action_type"] in ("purchase", "lead", "submit_application",
                                         "complete_registration", "contact"):
                conv += float(action.get("value", 0))

        daily[d] = {
            "conv":  conv,
            "spend": float(row.get("spend", 0)),
        }

    return daily


# ─── ANALYSIS ─────────────────────────────────────────────────────────────────

def analyse_overlap(google_daily, meta_daily, days):
    """Compare daily performance across channels."""
    all_dates = sorted(set(list(google_daily.keys()) + list(meta_daily.keys())))

    overlap_days   = 0   # both channels had conversions
    google_only    = 0   # only Google had conversions
    meta_only      = 0   # only Meta had conversions
    neither        = 0   # neither had conversions

    total_google_conv = sum(d["conv"]  for d in google_daily.values())
    total_meta_conv   = sum(d["conv"]  for d in meta_daily.values())
    total_google_cost = sum(d["cost"]  for d in google_daily.values())
    total_meta_cost   = sum(d["spend"] for d in meta_daily.values())

    for d in all_dates:
        g_conv = google_daily.get(d, {}).get("conv", 0)
        m_conv = meta_daily.get(d, {}).get("conv", 0)

        if g_conv > 0 and m_conv > 0:
            overlap_days += 1
        elif g_conv > 0:
            google_only  += 1
        elif m_conv > 0:
            meta_only    += 1
        else:
            neither      += 1

    return {
        "dates":              all_dates,
        "overlap_days":       overlap_days,
        "google_only_days":   google_only,
        "meta_only_days":     meta_only,
        "neither_days":       neither,
        "total_google_conv":  total_google_conv,
        "total_meta_conv":    total_meta_conv,
        "total_google_cost":  total_google_cost,
        "total_meta_cost":    total_meta_cost,
        "reported_total":     total_google_conv + total_meta_conv,
        "overlap_pct":        overlap_days / len(all_dates) if all_dates else 0,
    }


# ─── PRINT REPORT ─────────────────────────────────────────────────────────────

def print_report(google_id, meta_id, google_daily, meta_daily, analysis, days):
    run_date = date.today().strftime("%Y-%m-%d")
    print(f"\nCHANNEL ATTRIBUTION ANALYZER")
    print(f"Google: {google_id}  |  Meta: {meta_id}  |  Window: {days} days")
    print(f"Run date: {run_date}")
    print("=" * 70)

    a = analysis
    print(f"\nCHANNEL SUMMARY")
    print(f"  {'':30} {'Google Ads':>12} {'Meta Ads':>12} {'Combined':>12}")
    print(f"  {'-'*30} {'-'*12} {'-'*12} {'-'*12}")
    print(f"  {'Reported Conversions':<30} {a['total_google_conv']:>12.0f} {a['total_meta_conv']:>12.0f} {a['reported_total']:>12.0f}")
    print(f"  {'Spend':<30} ${a['total_google_cost']:>10.2f} ${a['total_meta_cost']:>10.2f} ${a['total_google_cost']+a['total_meta_cost']:>10.2f}")

    if a["total_google_conv"] > 0:
        g_cpa = a["total_google_cost"] / a["total_google_conv"]
        print(f"  {'CPA':<30} ${g_cpa:>11.2f}", end="")
    if a["total_meta_conv"] > 0:
        m_cpa = a["total_meta_cost"] / a["total_meta_conv"]
        print(f" ${m_cpa:>11.2f}")
    else:
        print()

    print(f"\nDAILY OVERLAP ANALYSIS ({len(a['dates'])} days)")
    print(f"  Both channels converting:    {a['overlap_days']:>4} days ({a['overlap_pct']*100:.0f}%)")
    print(f"  Google only:                 {a['google_only_days']:>4} days")
    print(f"  Meta only:                   {a['meta_only_days']:>4} days")
    print(f"  Neither converting:          {a['neither_days']:>4} days")

    # Risk assessment
    print(f"\nATTRIBUTION RISK FLAGS")
    if a["overlap_pct"] > 0.50:
        print(f"  WARNING: Both channels report conversions on {a['overlap_pct']*100:.0f}% of days.")
        print(f"  High overlap suggests possible double-counting. The same customer may")
        print(f"  be counted as a conversion by both Google (view-through or click) and Meta.")
        print(f"  Actual conversions may be closer to MAX(Google, Meta) on overlap days.")
    elif a["overlap_pct"] > 0.25:
        print(f"  NOTE: Moderate overlap ({a['overlap_pct']*100:.0f}% of days). Monitor for double-counting.")
        print(f"  Consider running a holdout test on one channel to measure incrementality.")
    else:
        print(f"  LOW RISK: Channels tend to convert independently. Attribution overlap is low.")

    if a["total_google_conv"] > 0 and a["total_meta_conv"] > 0:
        ratio = a["total_google_conv"] / a["total_meta_conv"]
        if ratio > 3:
            print(f"\n  INFO: Google Ads drives {ratio:.1f}x more reported conversions than Meta.")
            print(f"  Meta may still be contributing assists — check Meta Attribution window settings.")
        elif ratio < 0.33:
            print(f"\n  INFO: Meta drives {1/ratio:.1f}x more reported conversions than Google.")

    # Daily table (last 14 days for readability)
    print(f"\nDAILY DETAIL (last 14 days)")
    print(f"  {'Date':<12} {'Google Conv':>12} {'Google Spend':>13} {'Meta Conv':>10} {'Meta Spend':>11}")
    print(f"  {'-'*12} {'-'*12} {'-'*13} {'-'*10} {'-'*11}")
    for d in a["dates"][-14:]:
        g = google_daily.get(d, {})
        m = meta_daily.get(d, {})
        print(f"  {d:<12} {g.get('conv', 0):>12.0f} ${g.get('cost', 0):>11.2f} "
              f"{m.get('conv', 0):>10.0f} ${m.get('spend', 0):>10.2f}")

    print("\n" + "=" * 70)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Channel attribution analyzer — Google Ads + Meta Ads side by side"
    )
    parser.add_argument("--google-id", required=True, help="Google Ads account ID")
    parser.add_argument("--meta-id",   required=True, help="Meta Ads account ID (act_XXXX)")
    parser.add_argument("--days",      type=int, default=30,
                        help="Lookback window in days (default: 30)")
    args = parser.parse_args()

    today      = date.today()
    start_date = (today - timedelta(days=args.days)).strftime("%Y-%m-%d")
    end_date   = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    google_id  = args.google_id.replace("-", "")

    ga_client  = build_google_client()
    ga_service = ga_client.get_service("GoogleAdsService")

    print(f"\nPulling data for {args.days} days ...")
    print(f"  Fetching Google Ads data ...")
    google_daily = pull_google_daily(ga_service, google_id, start_date, end_date)

    print(f"  Fetching Meta Ads data ...")
    meta_daily   = pull_meta_daily(args.meta_id, start_date, end_date)

    print(f"  Google: {len(google_daily)} days  |  Meta: {len(meta_daily)} days")

    if not google_daily and not meta_daily:
        print("  No data retrieved from either channel. Check credentials and account IDs.")
        return

    analysis = analyse_overlap(google_daily, meta_daily, args.days)
    print_report(google_id, args.meta_id, google_daily, meta_daily, analysis, args.days)


if __name__ == "__main__":
    main()
