"""
Daily Pacing Monitor
Purpose: Morning health check across all (or one) Google Ads client accounts.
         Flags: budget overpacing, underpacing, limited-by-budget campaigns,
                disapproved ads, conversion tracking issues, and learning period status.

Setup:
    Requires environment variables:
        GOOGLE_ADS_DEVELOPER_TOKEN
        GOOGLE_ADS_CLIENT_ID
        GOOGLE_ADS_CLIENT_SECRET
        GOOGLE_ADS_REFRESH_TOKEN
        GOOGLE_ADS_CUSTOMER_ID  (your MCC ID)

Usage:
    python3 scripts/daily_pacing_monitor.py                          # all clients
    python3 scripts/daily_pacing_monitor.py --customer-id 5544702166 # single client
    python3 scripts/daily_pacing_monitor.py --customer-id 5544702166 --client-name Hoski

Pacing Logic:
    Expected spend = daily_budget * (hours_elapsed / 24)
    Pacing ratio   = actual_spend / expected_spend
    OVERPACING  🔴 if ratio > 1.25  (will overspend by >25%)
    ON TRACK    ✅ if 0.75 <= ratio <= 1.25
    UNDERPACING ⚠️  if ratio < 0.75  (spending too slowly)
    NO SPEND    🚨 if spend = $0 and budget > $0 and day is >20% elapsed

Changelog:
    2026-03-19  Initial version — pacing, disapprovals, limited budgets,
                zero-spend detection, learning period, conversion tracking health.
"""

import argparse
import os
import sys
from datetime import datetime, timezone, timedelta

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# ─── CLIENT REGISTRY (from CLAUDE.md) ────────────────────────────────────────

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

# ─── PACING THRESHOLDS ────────────────────────────────────────────────────────

OVERPACE_THRESHOLD  = 1.25   # >125% of expected spend → overpacing
UNDERPACE_THRESHOLD = 0.75   # <75% of expected spend → underpacing
MIN_DAY_ELAPSED     = 0.20   # only flag zero-spend after 20% of day has passed

# ─── BUILD CLIENT ─────────────────────────────────────────────────────────────

def build_client():
    return GoogleAdsClient.load_from_dict({
        "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "login_customer_id": os.environ["GOOGLE_ADS_CUSTOMER_ID"],
        "use_proto_plus": True
    })


def run_query(ga_service, customer_id, query):
    try:
        return list(ga_service.search(customer_id=customer_id, query=query))
    except GoogleAdsException as ex:
        # Surface the actual error message from the API
        for error in ex.failure.errors:
            print(f"    [API Error] {error.message}")
        return []


# ─── PACING ──────────────────────────────────────────────────────────────────

def check_pacing(ga_service, customer_id, today_str, day_fraction):
    """Returns list of pacing issues for enabled campaigns."""
    rows = run_query(ga_service, customer_id, f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.serving_status,
            campaign.bidding_strategy_type,
            campaign_budget.amount_micros,
            campaign_budget.has_recommended_budget,
            metrics.cost_micros
        FROM campaign
        WHERE segments.date = '{today_str}'
          AND campaign.status = ENABLED
        ORDER BY campaign_budget.amount_micros DESC
    """)

    issues = []
    all_campaigns = []

    for row in rows:
        c = row.campaign
        b = row.campaign_budget
        daily_budget = b.amount_micros / 1_000_000
        actual_spend = row.metrics.cost_micros / 1_000_000
        serving_status = c.serving_status.name

        if daily_budget == 0:
            continue

        # Skip campaigns that are enabled but not actually serving
        # (e.g. all ads paused, no keywords, ended flight — serving_status = NONE)
        if serving_status not in ("SERVING", "LIMITED_BY_BUDGET", "BUDGET_CONSTRAINED"):
            continue

        expected_spend = daily_budget * day_fraction
        pacing_ratio = (actual_spend / expected_spend) if expected_spend > 0 else 0

        camp_info = {
            "id": str(c.id),
            "name": c.name,
            "budget": daily_budget,
            "spend": actual_spend,
            "expected": expected_spend,
            "ratio": pacing_ratio,
            "serving_status": serving_status,
            "limited": b.has_recommended_budget,
            "bidding": c.bidding_strategy_type.name,
        }
        all_campaigns.append(camp_info)

        # Zero spend flag (only after 20% of day elapsed)
        if actual_spend == 0 and day_fraction >= MIN_DAY_ELAPSED:
            issues.append({
                "level": "CRITICAL",
                "icon": "🚨",
                "campaign": c.name,
                "message": f"ZERO SPEND — ${daily_budget:.2f} budget, nothing spent yet ({day_fraction*100:.0f}% of day elapsed)"
            })
        elif pacing_ratio > OVERPACE_THRESHOLD:
            issues.append({
                "level": "WARNING",
                "icon": "🔴",
                "campaign": c.name,
                "message": f"OVERPACING {pacing_ratio*100:.0f}% — spent ${actual_spend:.2f} of ${daily_budget:.2f} budget (expected ${expected_spend:.2f})"
            })
        elif pacing_ratio < UNDERPACE_THRESHOLD and day_fraction >= MIN_DAY_ELAPSED:
            issues.append({
                "level": "WARNING",
                "icon": "⚠️ ",
                "campaign": c.name,
                "message": f"UNDERPACING {pacing_ratio*100:.0f}% — spent ${actual_spend:.2f} of ${daily_budget:.2f} budget (expected ${expected_spend:.2f})"
            })

        # Limited by budget
        if b.has_recommended_budget:
            issues.append({
                "level": "INFO",
                "icon": "💸",
                "campaign": c.name,
                "message": f"LIMITED BY BUDGET — daily budget ${daily_budget:.2f} is capping impressions"
            })

    return issues, all_campaigns


# ─── DISAPPROVED ADS ─────────────────────────────────────────────────────────

def check_disapprovals(ga_service, customer_id):
    rows = run_query(ga_service, customer_id, """
        SELECT
            campaign.name,
            campaign.status,
            ad_group.name,
            ad_group.status,
            ad_group_ad.ad.id,
            ad_group_ad.policy_summary.approval_status,
            ad_group_ad.policy_summary.review_status,
            ad_group_ad.policy_summary.policy_topic_entries
        FROM ad_group_ad
        WHERE ad_group_ad.status = ENABLED
          AND ad_group_ad.policy_summary.approval_status != APPROVED
    """)

    issues = []
    for row in rows:
        ad = row.ad_group_ad
        approval = ad.policy_summary.approval_status.name
        review = ad.policy_summary.review_status.name
        topics = [t.topic for t in ad.policy_summary.policy_topic_entries] if ad.policy_summary.policy_topic_entries else []
        topic_str = ", ".join(topics) if topics else "no detail"

        campaign_active = row.campaign.status.name == "ENABLED"
        ad_group_active = row.ad_group.status.name == "ENABLED"
        fully_active = campaign_active and ad_group_active

        if approval == "DISAPPROVED":
            level = "CRITICAL" if fully_active else "WARNING"
            icon = "🚨" if fully_active else "⚠️ "
            suffix = "" if fully_active else " (campaign/ad group paused)"
        else:
            # APPROVED_LIMITED — only worth surfacing on fully active ads
            if not fully_active:
                continue
            level = "INFO"
            icon = "⏳"
            suffix = ""

        issues.append({
            "level": level,
            "icon": icon,
            "campaign": row.campaign.name,
            "message": f"AD {approval} ({review}) in [{row.ad_group.name}] — {topic_str}{suffix}"
        })

    return issues


# ─── CONVERSION TRACKING HEALTH ──────────────────────────────────────────────

def check_conversion_tracking(ga_service, customer_id, today_str):
    """Flag accounts with zero conversions in last 7 days where spend > $0."""
    rows = run_query(ga_service, customer_id, """
        SELECT
            metrics.conversions,
            metrics.all_conversions,
            metrics.cost_micros
        FROM customer
        WHERE segments.date DURING LAST_7_DAYS
    """)

    total_spend = sum(r.metrics.cost_micros / 1_000_000 for r in rows)
    total_conv = sum(r.metrics.conversions for r in rows)

    issues = []
    if total_spend > 50 and total_conv == 0:
        issues.append({
            "level": "CRITICAL",
            "icon": "🚨",
            "campaign": "ACCOUNT",
            "message": f"ZERO CONVERSIONS in last 7 days — ${total_spend:.2f} spent. Check conversion tracking."
        })
    return issues


# ─── LEARNING PERIOD ─────────────────────────────────────────────────────────

def check_learning_period(ga_service, customer_id):
    """Flag Smart Bidding campaigns with fewer than 30 conversions in last 30 days."""
    rows = run_query(ga_service, customer_id, """
        SELECT
            campaign.name,
            campaign.bidding_strategy_type,
            metrics.conversions
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
          AND campaign.status = ENABLED
        ORDER BY campaign.name
    """)

    smart_bidding = {
        "TARGET_CPA", "TARGET_ROAS", "MAXIMIZE_CONVERSIONS",
        "MAXIMIZE_CONVERSION_VALUE", "TARGET_IMPRESSION_SHARE"
    }

    campaign_conv = {}
    for row in rows:
        name = row.campaign.name
        bidding = row.campaign.bidding_strategy_type.name
        if name not in campaign_conv:
            campaign_conv[name] = {"bidding": bidding, "conversions": 0}
        campaign_conv[name]["conversions"] += row.metrics.conversions

    issues = []
    for name, data in campaign_conv.items():
        if data["bidding"] in smart_bidding and data["conversions"] < 30:
            issues.append({
                "level": "WARNING",
                "icon": "📚",
                "campaign": name,
                "message": f"LOW CONVERSION VOLUME for {data['bidding']} — only {data['conversions']:.0f} conv in last 30 days (need 30+ for stable Smart Bidding)"
            })

    return issues


# ─── AUDIT ONE ACCOUNT ────────────────────────────────────────────────────────

def audit_account(client, customer_id, client_name, today_str, day_fraction):
    ga_service = client.get_service("GoogleAdsService")

    pacing_issues, all_campaigns = check_pacing(ga_service, customer_id, today_str, day_fraction)
    disapproval_issues           = check_disapprovals(ga_service, customer_id)
    tracking_issues              = check_conversion_tracking(ga_service, customer_id, today_str)
    learning_issues              = check_learning_period(ga_service, customer_id)

    all_issues = pacing_issues + disapproval_issues + tracking_issues + learning_issues

    critical = [i for i in all_issues if i["level"] == "CRITICAL"]
    warnings = [i for i in all_issues if i["level"] == "WARNING"]
    info     = [i for i in all_issues if i["level"] == "INFO"]

    total_budget = sum(c["budget"] for c in all_campaigns)
    total_spend  = sum(c["spend"]  for c in all_campaigns)

    if critical:
        status_icon = "🚨"
    elif warnings:
        status_icon = "⚠️ "
    elif info:
        status_icon = "💡"
    else:
        status_icon = "✅"

    print(f"\n{status_icon}  {client_name} ({customer_id})")
    print(f"    Budget: ${total_budget:.2f}/day  |  Spent today: ${total_spend:.2f}  |  Active campaigns: {len(all_campaigns)}")

    if not all_issues:
        print("    All clear — no issues detected.")
    else:
        for issue in critical + warnings + info:
            print(f"    {issue['icon']}  [{issue['campaign']}] {issue['message']}")

    return {"critical": len(critical), "warnings": len(warnings), "info": len(info)}


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Daily pacing monitor — morning health check")
    parser.add_argument("--customer-id", help="Single account ID (omit to run all clients)")
    parser.add_argument("--client-name", help="Display name when using --customer-id")
    args = parser.parse_args()

    # Time calculations (Google Ads data is in account timezone; we use local time as proxy)
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    day_fraction = (now.hour * 3600 + now.minute * 60 + now.second) / 86400

    client = build_client()

    print("\n" + "="*60)
    print(f"DAILY PACING MONITOR")
    print(f"Run time: {now.strftime('%Y-%m-%d %H:%M')}  ({day_fraction*100:.1f}% of day elapsed)")
    print("="*60)

    if args.customer_id:
        # Single account mode
        label = args.client_name or args.customer_id
        targets = {label: args.customer_id.replace("-", "")}
    else:
        # All clients mode
        targets = ALL_CLIENTS

    total_critical = 0
    total_warnings = 0
    errored = []

    for name, cid in targets.items():
        try:
            result = audit_account(client, cid, name, today_str, day_fraction)
            total_critical += result["critical"]
            total_warnings += result["warnings"]
        except Exception as e:
            errored.append(name)
            print(f"\n❌  {name} ({cid}) — Error: {e}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  Accounts checked: {len(targets) - len(errored)}/{len(targets)}")
    print(f"  🚨 Critical issues: {total_critical}")
    print(f"  ⚠️  Warnings:        {total_warnings}")
    if errored:
        print(f"  ❌ Errored:         {', '.join(errored)}")
    if total_critical == 0 and total_warnings == 0:
        print("\n  ✅ All accounts look healthy.")
    print("="*60)


if __name__ == "__main__":
    main()
