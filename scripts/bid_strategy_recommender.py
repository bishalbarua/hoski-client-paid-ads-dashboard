"""
Bid Strategy Recommender
Purpose: Evaluates every campaign's readiness to graduate to a smarter
         bidding strategy. Uses Google's recommended conversion thresholds
         and account-specific CPA stability to determine the right next step.

         Bid strategy progression:
           Manual CPC -> Enhanced CPC -> Maximize Conversions
           -> Target CPA -> Target ROAS (if value tracking is set up)

         Run before proposing bid strategy changes to any client.

Setup:
    Requires environment variables in .env:
        GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID,
        GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN,
        GOOGLE_ADS_CUSTOMER_ID

Usage:
    python3 scripts/bid_strategy_recommender.py --customer-id 5544702166
    python3 scripts/bid_strategy_recommender.py --customer-id 5544702166 --days 30

Thresholds (Google's recommended minimums):
    Maximize Conversions:   10+ conversions / month
    Target CPA:             30+ conversions / month, stable CPA
    Target ROAS:            50+ conversions / month, conversion value tracked

Changelog:
    2026-03-23  Initial version — campaign-level readiness assessment with
                CPA stability check and value tracking detection.
"""

import argparse
import os
import statistics
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

# ─── THRESHOLDS ───────────────────────────────────────────────────────────────

MIN_CONV_MAXIMIZE       = 10    # /month for Maximize Conversions
MIN_CONV_TCPA           = 30    # /month for Target CPA
MIN_CONV_TROAS          = 50    # /month for Target ROAS
CPA_STABILITY_CV_THRESH = 0.30  # Coefficient of variation <30% = stable CPA

SMART_BIDDING = {
    "TARGET_CPA", "TARGET_ROAS",
    "MAXIMIZE_CONVERSIONS", "MAXIMIZE_CONVERSION_VALUE",
}

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

def pull_campaign_data(ga_service, customer_id, start_date, end_date):
    """Pull campaign performance with daily granularity for CPA stability."""
    rows = run_query(ga_service, customer_id, f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.bidding_strategy_type,
            campaign.advertising_channel_type,
            segments.date,
            metrics.conversions,
            metrics.conversions_value,
            metrics.cost_micros,
            metrics.clicks
        FROM campaign
        WHERE segments.date >= '{start_date}'
          AND segments.date <= '{end_date}'
          AND campaign.status = ENABLED
        ORDER BY campaign.id, segments.date
    """)

    campaigns = defaultdict(lambda: {
        "name": "", "bidding": "", "channel": "",
        "daily_conv": [], "daily_cost": [], "daily_value": [],
        "total_conv": 0.0, "total_cost": 0.0, "total_value": 0.0,
        "total_clicks": 0,
    })

    for row in rows:
        cid = str(row.campaign.id)
        c   = campaigns[cid]
        c["name"]    = row.campaign.name
        c["bidding"] = row.campaign.bidding_strategy_type.name
        c["channel"] = row.campaign.advertising_channel_type.name

        conv  = row.metrics.conversions
        cost  = row.metrics.cost_micros / 1_000_000
        value = row.metrics.conversions_value

        c["daily_conv"].append(conv)
        c["daily_cost"].append(cost)
        c["daily_value"].append(value)

        c["total_conv"]   += conv
        c["total_cost"]   += cost
        c["total_value"]  += value
        c["total_clicks"] += row.metrics.clicks

    return campaigns


def pull_conversion_value_tracking(ga_service, customer_id):
    """Check if account has value-tracked primary conversion actions."""
    rows = run_query(ga_service, customer_id, """
        SELECT
            conversion_action.include_in_conversions_metric,
            conversion_action.value_settings.default_value,
            conversion_action.value_settings.always_use_default_value
        FROM conversion_action
        WHERE conversion_action.status = ENABLED
    """)

    for row in rows:
        ca = row.conversion_action
        if not ca.include_in_conversions_metric:
            continue
        if ca.value_settings.default_value > 0 or not ca.value_settings.always_use_default_value:
            return True  # value tracking is active

    return False


# ─── RECOMMEND ────────────────────────────────────────────────────────────────

def cpa_stability(daily_conv, daily_cost, min_days=7):
    """
    Returns coefficient of variation of daily CPA (lower = more stable).
    Filters to days with >0 conversions.
    """
    cpa_days = []
    for conv, cost in zip(daily_conv, daily_cost):
        if conv > 0:
            cpa_days.append(cost / conv)

    if len(cpa_days) < min_days:
        return None, len(cpa_days)

    mean = statistics.mean(cpa_days)
    if mean == 0:
        return None, len(cpa_days)

    std = statistics.stdev(cpa_days) if len(cpa_days) > 1 else 0
    cv  = std / mean
    return cv, len(cpa_days)


def recommend(campaign_data, days, has_value_tracking):
    """
    Generate a recommendation for a single campaign.
    Returns (recommendation, rationale, priority) tuple.
    """
    name      = campaign_data["name"]
    bidding   = campaign_data["bidding"]
    total_conv = campaign_data["total_conv"]
    total_cost = campaign_data["total_cost"]
    total_value = campaign_data["total_value"]

    # Normalize to monthly rate
    monthly_conv = total_conv * (30 / days)
    cpa_now      = total_cost / total_conv if total_conv > 0 else None

    cv, conv_days = cpa_stability(campaign_data["daily_conv"], campaign_data["daily_cost"])
    cpa_stable    = cv is not None and cv < CPA_STABILITY_CV_THRESH

    # Already on Smart Bidding
    if bidding in SMART_BIDDING:
        if bidding == "TARGET_ROAS" and monthly_conv < MIN_CONV_TROAS:
            return (
                "Stay on Target ROAS but may exit learning mode instability",
                f"Monthly conv rate is {monthly_conv:.0f} (need {MIN_CONV_TROAS}+ for stable tROAS). "
                f"Consider switching to tCPA until volume improves.",
                "MEDIUM",
            )
        return (
            f"Keep current strategy: {bidding}",
            f"Already on Smart Bidding with {monthly_conv:.0f} monthly conv.",
            "LOW",
        )

    # Manual CPC / Enhanced CPC path
    if monthly_conv < MIN_CONV_MAXIMIZE:
        return (
            "Stay on Manual CPC — not enough conversion volume",
            f"Monthly conv: {monthly_conv:.0f} (need {MIN_CONV_MAXIMIZE}+ for Maximize Conversions). "
            f"Focus on improving conversion rate and tracking before changing bidding.",
            "LOW",
        )
    elif monthly_conv < MIN_CONV_TCPA:
        return (
            "UPGRADE: Switch to Maximize Conversions",
            f"Monthly conv: {monthly_conv:.0f} — enough for Maximize Conversions. "
            f"Not yet ready for tCPA (need {MIN_CONV_TCPA}+ monthly). "
            f"Run Maximize Conversions for 30 days before setting a tCPA.",
            "HIGH",
        )
    elif monthly_conv >= MIN_CONV_TROAS and has_value_tracking and total_value > 0:
        if cpa_stable:
            return (
                "UPGRADE: Switch to Target ROAS",
                f"Monthly conv: {monthly_conv:.0f} with conversion value tracked. "
                f"CPA is stable (CV: {cv:.2f}). Current CPA: ${cpa_now:.0f}. "
                f"Set initial ROAS target at current ROAS minus 10-15% as a buffer.",
                "HIGH",
            )
        else:
            return (
                "UPGRADE: Switch to Target CPA (ROAS when stable)",
                f"Monthly conv: {monthly_conv:.0f} with value tracking. "
                f"CPA variance is high (CV: {cv:.2f} — need <{CPA_STABILITY_CV_THRESH}). "
                f"Start with tCPA to stabilise, then graduate to tROAS in 60+ days.",
                "HIGH",
            )
    elif monthly_conv >= MIN_CONV_TCPA:
        if cpa_stable:
            return (
                "UPGRADE: Switch to Target CPA",
                f"Monthly conv: {monthly_conv:.0f}. CPA stable (CV: {cv:.2f}). "
                f"Current CPA: ${cpa_now:.0f}. "
                f"Set initial tCPA target at current CPA + 20% buffer for safety.",
                "HIGH",
            )
        else:
            return (
                "Consider Switch to Target CPA (stabilise first)",
                f"Monthly conv: {monthly_conv:.0f} — volume is there. "
                f"CPA variance is high (CV: {cv:.2f if cv else 'n/a'}). "
                f"Check for conversion tracking issues before switching bid strategy.",
                "MEDIUM",
            )
    else:
        return (
            "Switch to Maximize Conversions",
            f"Monthly conv: {monthly_conv:.0f} — ready for Maximize Conversions. "
            f"tCPA available once you reach {MIN_CONV_TCPA}+ monthly conversions.",
            "HIGH",
        )


# ─── PRINT REPORT ─────────────────────────────────────────────────────────────

def print_report(customer_id, client_name, campaigns, days, has_value_tracking):
    run_date = date.today().strftime("%Y-%m-%d")
    print(f"\nBID STRATEGY RECOMMENDER — {client_name} ({customer_id})")
    print(f"Period: last {days} days  |  Value tracking: {'YES' if has_value_tracking else 'NO'}")
    print("=" * 75)

    recs = []
    for cid, data in campaigns.items():
        rec, rationale, priority = recommend(data, days, has_value_tracking)
        recs.append({
            "name":      data["name"],
            "bidding":   data["bidding"],
            "rec":       rec,
            "rationale": rationale,
            "priority":  priority,
            "conv":      data["total_conv"],
            "cost":      data["total_cost"],
        })

    # Sort: HIGH priority first
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    recs.sort(key=lambda x: order.get(x["priority"], 9))

    for r in recs:
        print(f"\n  [{r['priority']}] {r['name']}")
        print(f"  Current: {r['bidding']}  |  Conv (period): {r['conv']:.0f}  |  Spend: ${r['cost']:.0f}")
        print(f"  Recommendation: {r['rec']}")
        print(f"  Rationale: {r['rationale']}")

    high = [r for r in recs if r["priority"] == "HIGH"]
    print(f"\n{'='*75}")
    print(f"  Campaigns to upgrade: {len(high)}")
    print(f"  Note: All bid strategy changes require user approval before implementation.")
    print("=" * 75)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Bid strategy recommender — campaign readiness assessment"
    )
    parser.add_argument("--customer-id", required=True, help="Account ID")
    parser.add_argument("--client-name", help="Display name (optional)")
    parser.add_argument("--days",        type=int, default=30,
                        help="Analysis window in days (default: 30)")
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

    print(f"\nAnalysing bid strategy readiness for {client_name} ...")
    campaigns          = pull_campaign_data(ga_service, cid, start_date, end_date)
    has_value_tracking = pull_conversion_value_tracking(ga_service, cid)

    print(f"  {len(campaigns)} active campaigns found")
    print_report(cid, client_name, campaigns, args.days, has_value_tracking)


if __name__ == "__main__":
    main()
