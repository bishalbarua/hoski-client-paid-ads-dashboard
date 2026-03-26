"""
Audience Signal Builder
Purpose: Analyses demographic and audience performance data from Google Ads API.
         Surfaces which age brackets, genders, and household income tiers
         over/underindex on conversions. Produces:
           - Bid adjustment recommendations for standard campaigns
           - Audience signal recommendations for Performance Max campaigns
           - Audience exclusion candidates (if demographics massively underperform)

         Run before setting up a new PMax campaign or optimising bid adjustments
         on existing Search/Display campaigns.

Setup:
    Requires environment variables in .env:
        GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID,
        GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN,
        GOOGLE_ADS_CUSTOMER_ID

Usage:
    python3 scripts/audience_signal_builder.py --customer-id 5544702166
    python3 scripts/audience_signal_builder.py --customer-id 5216656756 --days 90

Changelog:
    2026-03-23  Initial version — demographic indexing, bid adjustment
                recommendations, PMax audience signal brief.
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

BID_ADJ_STRONG_POSITIVE = 1.20   # index >1.20 = suggest +20% bid adjustment
BID_ADJ_STRONG_NEGATIVE = 0.70   # index <0.70 = suggest -20% or exclusion

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


# ─── PULL DEMOGRAPHIC DATA ────────────────────────────────────────────────────

def pull_age_data(ga_service, customer_id, start_date, end_date):
    rows = run_query(ga_service, customer_id, f"""
        SELECT
            ad_group_criterion.age_range.type,
            metrics.clicks,
            metrics.impressions,
            metrics.conversions,
            metrics.cost_micros
        FROM age_range_view
        WHERE segments.date >= '{start_date}'
          AND segments.date <= '{end_date}'
          AND campaign.status = ENABLED
          AND ad_group.status = ENABLED
    """)

    by_age = defaultdict(lambda: {"clicks": 0, "imps": 0, "conv": 0.0, "cost": 0.0})
    for row in rows:
        age = row.ad_group_criterion.age_range.type_.name
        by_age[age]["clicks"] += row.metrics.clicks
        by_age[age]["imps"]   += row.metrics.impressions
        by_age[age]["conv"]   += row.metrics.conversions
        by_age[age]["cost"]   += row.metrics.cost_micros / 1_000_000

    return dict(by_age)


def pull_gender_data(ga_service, customer_id, start_date, end_date):
    rows = run_query(ga_service, customer_id, f"""
        SELECT
            ad_group_criterion.gender.type,
            metrics.clicks,
            metrics.impressions,
            metrics.conversions,
            metrics.cost_micros
        FROM gender_view
        WHERE segments.date >= '{start_date}'
          AND segments.date <= '{end_date}'
          AND campaign.status = ENABLED
          AND ad_group.status = ENABLED
    """)

    by_gender = defaultdict(lambda: {"clicks": 0, "imps": 0, "conv": 0.0, "cost": 0.0})
    for row in rows:
        gender = row.ad_group_criterion.gender.type_.name
        by_gender[gender]["clicks"] += row.metrics.clicks
        by_gender[gender]["imps"]   += row.metrics.impressions
        by_gender[gender]["conv"]   += row.metrics.conversions
        by_gender[gender]["cost"]   += row.metrics.cost_micros / 1_000_000

    return dict(by_gender)


def pull_income_data(ga_service, customer_id, start_date, end_date):
    rows = run_query(ga_service, customer_id, f"""
        SELECT
            ad_group_criterion.income_range.type,
            metrics.clicks,
            metrics.impressions,
            metrics.conversions,
            metrics.cost_micros
        FROM income_range_view
        WHERE segments.date >= '{start_date}'
          AND segments.date <= '{end_date}'
          AND campaign.status = ENABLED
          AND ad_group.status = ENABLED
    """)

    by_income = defaultdict(lambda: {"clicks": 0, "imps": 0, "conv": 0.0, "cost": 0.0})
    for row in rows:
        income = row.ad_group_criterion.income_range.type_.name
        by_income[income]["clicks"] += row.metrics.clicks
        by_income[income]["imps"]   += row.metrics.impressions
        by_income[income]["conv"]   += row.metrics.conversions
        by_income[income]["cost"]   += row.metrics.cost_micros / 1_000_000

    return dict(by_income)


# ─── INDEX CALCULATION ────────────────────────────────────────────────────────

def compute_index(segment_data):
    """
    Compute conversion index for each segment.
    index = (segment_cvr / account_avg_cvr)
    index > 1.0 = this segment converts better than average
    """
    total_clicks = sum(d["clicks"] for d in segment_data.values())
    total_conv   = sum(d["conv"]   for d in segment_data.values())
    avg_cvr      = total_conv / total_clicks if total_clicks > 0 else 0

    indexed = {}
    for seg, d in segment_data.items():
        cvr   = d["conv"] / d["clicks"] if d["clicks"] > 0 else 0
        index = cvr / avg_cvr if avg_cvr > 0 else 1.0
        cpa   = d["cost"] / d["conv"] if d["conv"] > 0 else 0
        indexed[seg] = {
            **d,
            "cvr":   cvr,
            "index": index,
            "cpa":   cpa,
        }

    return indexed, avg_cvr


def bid_adjustment_rec(index):
    """Suggest a bid adjustment based on the segment index."""
    if index >= 1.40:
        return "+30%"
    elif index >= 1.20:
        return "+15%"
    elif index >= 1.05:
        return "+5%"
    elif index <= 0.50:
        return "Exclude or -50%"
    elif index <= 0.70:
        return "-25%"
    elif index <= 0.90:
        return "-10%"
    return "No change"


# ─── PRINT REPORT ─────────────────────────────────────────────────────────────

def print_segment_table(label, indexed):
    CLEAN = {
        "AGE_RANGE_18_24": "18-24", "AGE_RANGE_25_34": "25-34",
        "AGE_RANGE_35_44": "35-44", "AGE_RANGE_45_54": "45-54",
        "AGE_RANGE_55_64": "55-64", "AGE_RANGE_65_UP":  "65+",
        "AGE_RANGE_UNDETERMINED": "Unknown",
        "MALE": "Male", "FEMALE": "Female", "UNDETERMINED": "Unknown",
        "INCOME_RANGE_0_50": "Top 50%", "INCOME_RANGE_50_60": "41-50%",
        "INCOME_RANGE_60_70": "31-40%", "INCOME_RANGE_70_80": "21-30%",
        "INCOME_RANGE_80_90": "11-20%", "INCOME_RANGE_90_100": "Lower 10%",
        "UNDETERMINED": "Unknown",
    }

    print(f"\n  {label}")
    print(f"  {'Segment':<18} {'Clicks':>7} {'Conv':>6} {'CVR':>7} {'Index':>7} {'CPA':>8}  Bid Adj")
    print(f"  {'-'*18} {'-'*7} {'-'*6} {'-'*7} {'-'*7} {'-'*8}  {'-'*12}")

    # Sort by index descending
    for seg, d in sorted(indexed.items(), key=lambda x: -x[1]["index"]):
        clean_name = CLEAN.get(seg, seg[:18])
        adj        = bid_adjustment_rec(d["index"])
        flag       = "*" if d["index"] >= BID_ADJ_STRONG_POSITIVE or d["index"] <= BID_ADJ_STRONG_NEGATIVE else " "
        print(f"  {flag}{clean_name:<17} {d['clicks']:>7} {d['conv']:>6.0f} {d['cvr']*100:>6.1f}% "
              f"{d['index']:>6.2f}x ${d['cpa']:>7.0f}  {adj}")


def print_report(customer_id, client_name, age_idx, gender_idx, income_idx):
    run_date = date.today().strftime("%Y-%m-%d")
    print(f"\nAUDIENCE SIGNAL BUILDER — {client_name} ({customer_id})")
    print(f"Run date: {run_date}")
    print("=" * 75)

    if age_idx:    print_segment_table("AGE BREAKDOWN", age_idx[0])
    if gender_idx: print_segment_table("GENDER BREAKDOWN", gender_idx[0])
    if income_idx: print_segment_table("HOUSEHOLD INCOME BREAKDOWN", income_idx[0])

    # PMax signal brief
    print(f"\n  PMAX AUDIENCE SIGNAL BRIEF")
    print(f"  Use these as audience signals in your Performance Max asset groups:")

    strong_positives = []
    if age_idx:
        for seg, d in age_idx[0].items():
            if d["index"] >= BID_ADJ_STRONG_POSITIVE and d["conv"] >= 3:
                strong_positives.append(f"Age group: {seg}")
    if gender_idx:
        for seg, d in gender_idx[0].items():
            if d["index"] >= BID_ADJ_STRONG_POSITIVE and d["conv"] >= 3:
                strong_positives.append(f"Gender: {seg}")

    if strong_positives:
        for s in strong_positives:
            print(f"  + {s}")
    else:
        print(f"  No strongly over-indexing demographics found.")
        print(f"  Use website visitors + customer list as primary PMax signals instead.")

    print(f"\n  * = segment with strong over/underperformance (bid adjustment recommended)")
    print("=" * 75)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Audience signal builder — demographic indexing and bid adjustment recommendations"
    )
    parser.add_argument("--customer-id", required=True, help="Account ID")
    parser.add_argument("--client-name", help="Display name (optional)")
    parser.add_argument("--days",        type=int, default=90,
                        help="Lookback window in days (default: 90)")
    args = parser.parse_args()

    today      = date.today()
    start_date = (today - timedelta(days=args.days)).strftime("%Y-%m-%d")
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

    print(f"\nAnalysing demographic data for {client_name} ({args.days} days) ...")
    age_data    = pull_age_data(ga_service, cid, start_date, end_date)
    gender_data = pull_gender_data(ga_service, cid, start_date, end_date)
    income_data = pull_income_data(ga_service, cid, start_date, end_date)

    age_idx    = compute_index(age_data)    if age_data    else None
    gender_idx = compute_index(gender_data) if gender_data else None
    income_idx = compute_index(income_data) if income_data else None

    print_report(cid, client_name, age_idx, gender_idx, income_idx)


if __name__ == "__main__":
    main()
