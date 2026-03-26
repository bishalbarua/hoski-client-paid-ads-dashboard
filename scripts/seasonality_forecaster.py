"""
Seasonality Forecaster
Purpose: Builds a seasonal index for a client using their own 12-24 months of
         Google Ads historical data. Shows which months are high/low season,
         how spend and conversions trend across the year, and what the projected
         monthly performance looks like if budget stays constant.

         Use this for:
           - Budget planning conversations with clients
           - Recommending when to increase/decrease spend
           - Setting realistic expectations for "slow months"

Setup:
    Requires environment variables in .env:
        GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID,
        GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN,
        GOOGLE_ADS_CUSTOMER_ID

Usage:
    python3 scripts/seasonality_forecaster.py --customer-id 5544702166
    python3 scripts/seasonality_forecaster.py --customer-id 5544702166 --months 24

Output:
    Monthly seasonality index table, peak/trough identification,
    and budget recommendation multipliers.

Changelog:
    2026-03-23  Initial version — monthly index from account history,
                seasonal curve, budget planning multipliers.
"""

import argparse
import os
from collections import defaultdict
from datetime import date, timedelta

from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

load_dotenv()

# ─── CLIENT REGISTRY ─────────────────────────────────────────────────────────

ALL_CLIENTS = {
    "Anand Desai Law Firm":                 "5865660247",
    "Dentiste":                             "3857223862",
    "Estate Jewelry Priced Right":          "7709532223",
    "FaBesthetics":                         "9304117954",
    "GDM Google Ads":                       "7087867966",
    "Hoski.ca":                             "5544702166",
    "New Norseman":                         "3720173680",
    "Park Road Custom Furniture and Decor": "7228467515",
    "Serenity Familycare":                  "8134824884",
    "Synergy Spine & Nerve Center":         "7628667762",
    "Texas FHC":                            "8159668041",
    "Voit Dental (1)":                      "5216656756",
    "Voit Dental (2)":                      "5907367258",
}

MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# ─── CLIENT ──────────────────────────────────────────────────────────────────

def build_client():
    return GoogleAdsClient.load_from_dict({
        "developer_token":   os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "client_id":         os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret":     os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token":     os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "login_customer_id": os.environ["GOOGLE_ADS_CUSTOMER_ID"],
        "use_proto_plus":    True,
    })


def run_query(ga_service, customer_id, query):
    try:
        return list(ga_service.search(customer_id=customer_id, query=query))
    except GoogleAdsException as ex:
        for error in ex.failure.errors:
            print(f"  [API Error] {error.message}")
        return []


# ─── PULL DATA ────────────────────────────────────────────────────────────────

def pull_monthly_data(ga_service, customer_id, start_date, end_date):
    """Pull account-level data aggregated by month."""
    rows = run_query(ga_service, customer_id, f"""
        SELECT
            segments.month,
            metrics.cost_micros,
            metrics.clicks,
            metrics.impressions,
            metrics.conversions,
            metrics.conversions_value
        FROM customer
        WHERE segments.date >= '{start_date}'
          AND segments.date <= '{end_date}'
    """)

    monthly = defaultdict(lambda: {
        "cost": 0.0, "clicks": 0, "imps": 0, "conv": 0.0, "value": 0.0
    })

    for row in rows:
        month = row.segments.month   # format: YYYY-MM-01
        m     = monthly[month]
        m["cost"]   += row.metrics.cost_micros / 1_000_000
        m["clicks"] += row.metrics.clicks
        m["imps"]   += row.metrics.impressions
        m["conv"]   += row.metrics.conversions
        m["value"]  += row.metrics.conversions_value

    return monthly


# ─── SEASONALITY CALC ─────────────────────────────────────────────────────────

def build_seasonal_index(monthly_data, metric="conv"):
    """
    Compute a monthly seasonality index.
    index = month_avg / annual_avg
    index > 1.0 = above average month
    index < 1.0 = below average month
    """
    # Group by calendar month (1-12) across all years
    by_month = defaultdict(list)
    for month_str, data in monthly_data.items():
        month_num = int(month_str[5:7])  # extract MM from YYYY-MM-01
        value     = data[metric]
        if value > 0:
            by_month[month_num].append(value)

    # Average per calendar month
    month_avgs = {}
    for m in range(1, 13):
        vals = by_month.get(m, [])
        month_avgs[m] = sum(vals) / len(vals) if vals else 0.0

    # Annual average (of all months with data)
    all_avgs  = [v for v in month_avgs.values() if v > 0]
    annual_avg = sum(all_avgs) / len(all_avgs) if all_avgs else 1.0

    if annual_avg == 0:
        return {m: 1.0 for m in range(1, 13)}

    return {m: month_avgs[m] / annual_avg for m in range(1, 13)}


# ─── PRINT REPORT ─────────────────────────────────────────────────────────────

def bar(index):
    """ASCII bar chart for the index."""
    filled = round(index * 10)
    return "█" * min(filled, 20) + ("" if filled <= 20 else "+")


def print_report(customer_id, client_name, monthly_data, months):
    run_date = date.today().strftime("%Y-%m-%d")
    print(f"\nSEASONALITY FORECASTER — {client_name} ({customer_id})")
    print(f"Months of data analysed: {len(monthly_data)}  |  Run date: {run_date}")
    print("=" * 75)

    if len(monthly_data) < 6:
        print("  WARNING: Less than 6 months of data. Seasonal patterns may not be reliable.")

    conv_index  = build_seasonal_index(monthly_data, "conv")
    cost_index  = build_seasonal_index(monthly_data, "cost")
    click_index = build_seasonal_index(monthly_data, "clicks")

    # Actual monthly totals for context
    by_month = defaultdict(lambda: {"cost": 0.0, "conv": 0.0, "years": 0})
    for month_str, data in monthly_data.items():
        month_num = int(month_str[5:7])
        by_month[month_num]["cost"] += data["cost"]
        by_month[month_num]["conv"] += data["conv"]
        by_month[month_num]["years"] += 1

    print(f"\n  CONVERSION SEASONALITY INDEX (1.0 = average month)")
    print(f"  {'Month':<6} {'Index':>7} {'Trend':<22} {'Avg Conv':>9} {'Avg Spend':>10}  Note")
    print(f"  {'-'*6} {'-'*7} {'-'*22} {'-'*9} {'-'*10}  {'-'*15}")

    peak_month  = max(conv_index, key=conv_index.get)
    trough_month = min(conv_index, key=lambda k: conv_index[k] if conv_index[k] > 0 else 99)

    for m in range(1, 13):
        idx       = conv_index[m]
        cost_idx  = cost_index[m]
        years     = by_month[m]["years"]
        avg_conv  = by_month[m]["conv"] / years if years > 0 else 0
        avg_cost  = by_month[m]["cost"] / years if years > 0 else 0

        note = ""
        if m == peak_month:
            note = "PEAK SEASON"
        elif m == trough_month:
            note = "LOW SEASON"
        elif idx >= 1.20:
            note = "High"
        elif idx <= 0.80:
            note = "Low"

        idx_str = f"{idx:.2f}x"
        print(f"  {MONTH_NAMES[m-1]:<6} {idx_str:>7} {bar(idx):<22} {avg_conv:>9.1f} ${avg_cost:>9,.0f}  {note}")

    # Budget multipliers
    print(f"\n  BUDGET MULTIPLIERS (relative to your current monthly budget)")
    print(f"  Apply these when planning monthly budgets:")
    print()
    for m in range(1, 13):
        idx = conv_index[m]
        if idx >= 1.20:
            mult = f"+{(idx-1)*100:.0f}% (increase budget)"
        elif idx <= 0.80:
            mult = f"-{(1-idx)*100:.0f}% (consider reducing)"
        else:
            mult = "no change"
        print(f"  {MONTH_NAMES[m-1]}: {idx:.2f}x  ({mult})")

    print(f"\n  Peak month:   {MONTH_NAMES[peak_month-1]} (index: {conv_index[peak_month]:.2f}x)")
    print(f"  Trough month: {MONTH_NAMES[trough_month-1]} (index: {conv_index[trough_month]:.2f}x)")

    print("\n" + "=" * 75)
    print("  Note: Index based on this account's own history (not industry benchmarks).")
    print("  Use in budget planning conversations: 'March is typically 1.3x your average month.'")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Seasonality forecaster — monthly performance index from account history"
    )
    parser.add_argument("--customer-id", required=True, help="Account ID")
    parser.add_argument("--client-name", help="Display name (optional)")
    parser.add_argument("--months",      type=int, default=24,
                        help="Months of history to pull (default: 24)")
    args = parser.parse_args()

    today      = date.today()
    start_date = (today.replace(day=1) - timedelta(days=args.months * 31)).strftime("%Y-%m-01")
    end_date   = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    cid        = args.customer_id.replace("-", "")

    client_name = args.client_name
    if not client_name:
        for name, id_ in ALL_CLIENTS.items():
            if id_ == cid:
                client_name = name
                break
        if not client_name:
            client_name = cid

    ga_client  = build_client()
    ga_service = ga_client.get_service("GoogleAdsService")

    print(f"\nPulling {args.months} months of history for {client_name} ...")
    monthly_data = pull_monthly_data(ga_service, cid, start_date, end_date)
    print(f"  {len(monthly_data)} months of data retrieved")

    if not monthly_data:
        print("  No data found. Check account activity and date range.")
        return

    print_report(cid, client_name, monthly_data, args.months)


if __name__ == "__main__":
    main()
