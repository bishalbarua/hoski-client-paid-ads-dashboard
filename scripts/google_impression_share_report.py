"""
Impression Share Report
Purpose: Pull Search impression share health for all (or one) client accounts.
         Shows how much of the available auction you're capturing, and what's
         causing the losses — budget constraints or low ad rank.

         Note: Competitor-level auction insights (overlap rate, outranking share)
         require Standard API Access. This script uses the IS metrics available
         under Basic Access. Upgrade to Standard Access to unlock competitor data.

Setup:
    Requires environment variables:
        GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET,
        GOOGLE_ADS_REFRESH_TOKEN, GOOGLE_ADS_CUSTOMER_ID

Usage:
    python3 scripts/impression_share_report.py                           # all clients
    python3 scripts/impression_share_report.py --customer-id 5544702166  # single client
    python3 scripts/impression_share_report.py --days 7                  # 7-day window

Metrics Explained:
    IS (Impression Share)         — % of eligible impressions you actually showed for
    Top IS                        — % of times your ad showed at the top of the page
    Abs Top IS                    — % of times your ad was in position #1
    IS Lost (Budget)              — % of auctions lost because budget ran out
    IS Lost (Rank)                — % of auctions lost due to low Quality Score or bid
    Top IS Lost (Budget/Rank)     — same breakdown but for top-of-page positions

Flags:
    🚨 CRITICAL
        - IS Lost (Budget) > 30%  → campaign needs more budget
        - IS Lost (Rank) > 40%    → quality score or bids too low
        - IS < 20%                → capturing less than 1 in 5 eligible impressions

    ⚠️  WARNING
        - IS Lost (Budget) 15–30%
        - IS Lost (Rank) 20–40%
        - IS 20–40%               → room to grow

    ✅  HEALTHY
        - IS > 60% with balanced losses

Changelog:
    2026-03-19  Initial version — IS, Top IS, Abs Top IS, budget/rank loss breakdown.
"""

import argparse
import os
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

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

# Thresholds
IS_CRITICAL         = 0.20   # IS below 20% → critical
IS_WARNING          = 0.40   # IS below 40% → warning
BUDGET_LOSS_CRIT    = 0.30   # >30% IS lost to budget → critical
BUDGET_LOSS_WARN    = 0.15   # >15% IS lost to budget → warning
RANK_LOSS_CRIT      = 0.40   # >40% IS lost to rank → critical
RANK_LOSS_WARN      = 0.20   # >20% IS lost to rank → warning

# ─── SETUP ───────────────────────────────────────────────────────────────────

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
        for error in ex.failure.errors:
            print(f"    [API Error] {error.message}")
        return []


# ─── AUDIT ───────────────────────────────────────────────────────────────────

def audit_account(ga_service, customer_id, days):
    date_range = f"LAST_{days}_DAYS" if days in (7, 14, 30) else "LAST_30_DAYS"

    rows = run_query(ga_service, customer_id, f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.serving_status,
            campaign.advertising_channel_type,
            campaign_budget.amount_micros,
            metrics.cost_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.search_impression_share,
            metrics.search_top_impression_share,
            metrics.search_absolute_top_impression_share,
            metrics.search_budget_lost_impression_share,
            metrics.search_rank_lost_impression_share,
            metrics.search_budget_lost_top_impression_share,
            metrics.search_rank_lost_top_impression_share,
            metrics.search_budget_lost_absolute_top_impression_share,
            metrics.search_rank_lost_absolute_top_impression_share
        FROM campaign
        WHERE segments.date DURING {date_range}
          AND campaign.status = ENABLED
          AND campaign.advertising_channel_type = SEARCH
        ORDER BY metrics.cost_micros DESC
    """)

    # Aggregate by campaign (rows come back per-day segmented)
    campaigns = {}
    for row in rows:
        c = row.campaign
        m = row.metrics
        cid = str(c.id)

        if cid not in campaigns:
            campaigns[cid] = {
                "name": c.name,
                "budget": row.campaign_budget.amount_micros / 1_000_000,
                "cost": 0.0,
                "impressions": 0,
                "clicks": 0,
                # IS metrics — take last non-zero value (they're account-level, not additive)
                "is": 0.0,
                "top_is": 0.0,
                "abs_top_is": 0.0,
                "lost_budget": 0.0,
                "lost_rank": 0.0,
                "lost_top_budget": 0.0,
                "lost_top_rank": 0.0,
                "lost_abs_budget": 0.0,
                "lost_abs_rank": 0.0,
            }

        campaigns[cid]["cost"]       += m.cost_micros / 1_000_000
        campaigns[cid]["impressions"] += m.impressions
        campaigns[cid]["clicks"]      += m.clicks

        # IS metrics are ratios — average them weighted by impressions
        if m.impressions > 0:
            w = m.impressions
            prev_w = campaigns[cid]["impressions"] - w  # weight before this row
            total_w = campaigns[cid]["impressions"]

            def wavg(prev_val, new_val):
                return (prev_val * prev_w + new_val * w) / total_w if total_w > 0 else new_val

            campaigns[cid]["is"]             = wavg(campaigns[cid]["is"],             m.search_impression_share)
            campaigns[cid]["top_is"]         = wavg(campaigns[cid]["top_is"],         m.search_top_impression_share)
            campaigns[cid]["abs_top_is"]     = wavg(campaigns[cid]["abs_top_is"],     m.search_absolute_top_impression_share)
            campaigns[cid]["lost_budget"]    = wavg(campaigns[cid]["lost_budget"],    m.search_budget_lost_impression_share)
            campaigns[cid]["lost_rank"]      = wavg(campaigns[cid]["lost_rank"],      m.search_rank_lost_impression_share)
            campaigns[cid]["lost_top_budget"]= wavg(campaigns[cid]["lost_top_budget"],m.search_budget_lost_top_impression_share)
            campaigns[cid]["lost_top_rank"]  = wavg(campaigns[cid]["lost_top_rank"],  m.search_rank_lost_top_impression_share)
            campaigns[cid]["lost_abs_budget"]= wavg(campaigns[cid]["lost_abs_budget"],m.search_budget_lost_absolute_top_impression_share)
            campaigns[cid]["lost_abs_rank"]  = wavg(campaigns[cid]["lost_abs_rank"],  m.search_rank_lost_absolute_top_impression_share)

    return campaigns


def evaluate_campaign(c):
    issues = []
    is_val      = c["is"]
    lost_budget = c["lost_budget"]
    lost_rank   = c["lost_rank"]

    # Skip campaigns with no meaningful data
    if c["impressions"] == 0 and c["cost"] == 0:
        return [], "⬜"

    # IS Lost to Budget
    if lost_budget > BUDGET_LOSS_CRIT:
        issues.append(("CRITICAL", "🚨", f"BUDGET LIMITING — losing {lost_budget:.0%} of impressions to budget. Increase daily budget (currently ${c['budget']:.2f}/day)."))
    elif lost_budget > BUDGET_LOSS_WARN:
        issues.append(("WARNING", "⚠️ ", f"BUDGET CONSTRAINT — losing {lost_budget:.0%} of impressions to budget (${c['budget']:.2f}/day)."))

    # IS Lost to Rank
    if lost_rank > RANK_LOSS_CRIT:
        issues.append(("CRITICAL", "🚨", f"RANK LIMITING — losing {lost_rank:.0%} of impressions to low ad rank. Improve Quality Score or increase bids."))
    elif lost_rank > RANK_LOSS_WARN:
        issues.append(("WARNING", "⚠️ ", f"RANK DRAG — losing {lost_rank:.0%} of impressions to ad rank. Review keyword Quality Scores."))

    # Overall IS
    if is_val < IS_CRITICAL and c["cost"] > 10:
        issues.append(("CRITICAL", "🚨", f"VERY LOW IS {is_val:.0%} — capturing less than 1 in 5 eligible impressions."))
    elif is_val < IS_WARNING and c["cost"] > 10:
        issues.append(("WARNING", "⚠️ ", f"LOW IS {is_val:.0%} — significant room to grow impression share."))

    # Determine campaign status icon
    if any(lvl == "CRITICAL" for lvl, _, _ in issues):
        icon = "🚨"
    elif any(lvl == "WARNING" for lvl, _, _ in issues):
        icon = "⚠️ "
    elif c["impressions"] > 0:
        icon = "✅"
    else:
        icon = "⬜"

    return issues, icon


# ─── PRINT ───────────────────────────────────────────────────────────────────

def print_account(client_name, customer_id, campaigns, days):
    if not campaigns:
        print(f"\n⬜  {client_name} ({customer_id}) — No active Search campaigns")
        return

    all_issues = []
    for c in campaigns.values():
        issues, _ = evaluate_campaign(c)
        all_issues.extend(issues)

    has_critical = any(lvl == "CRITICAL" for lvl, _, _ in all_issues)
    has_warning  = any(lvl == "WARNING"  for lvl, _, _ in all_issues)
    account_icon = "🚨" if has_critical else ("⚠️ " if has_warning else "✅")

    total_cost = sum(c["cost"] for c in campaigns.values())
    print(f"\n{account_icon}  {client_name} ({customer_id}) — {len(campaigns)} Search campaign(s) | {days}-day window | Total spend: ${total_cost:.2f}")

    for c in campaigns.values():
        issues, camp_icon = evaluate_campaign(c)

        is_bar = _is_bar(c["is"])
        print(f"\n    {camp_icon} {c['name']}")
        print(f"         IS: {c['is']:.0%} {is_bar}  |  Top IS: {c['top_is']:.0%}  |  Abs Top IS: {c['abs_top_is']:.0%}")
        print(f"         IS Lost → Budget: {c['lost_budget']:.0%}  |  Rank: {c['lost_rank']:.0%}")
        print(f"         Top IS Lost → Budget: {c['lost_top_budget']:.0%}  |  Rank: {c['lost_top_rank']:.0%}")
        print(f"         Spend: ${c['cost']:.2f}  |  Impressions: {c['impressions']:,}  |  Clicks: {c['clicks']:,}")

        if not issues:
            print(f"         ✅ Healthy IS — no major losses detected")
        else:
            for _, icon, msg in issues:
                print(f"         {icon}  {msg}")


def _is_bar(is_val):
    """Simple ASCII bar for impression share."""
    filled = round(is_val * 20)
    return f"[{'█' * filled}{'░' * (20 - filled)}]"


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Impression share report — Search campaigns")
    parser.add_argument("--customer-id", help="Single account ID (omit to run all clients)")
    parser.add_argument("--client-name", help="Display name when using --customer-id")
    parser.add_argument("--days", type=int, default=30, choices=[7, 14, 30], help="Lookback window in days (default: 30)")
    args = parser.parse_args()

    client = build_client()
    ga_service = client.get_service("GoogleAdsService")

    if args.customer_id:
        targets = {(args.client_name or args.customer_id): args.customer_id.replace("-", "")}
    else:
        targets = ALL_CLIENTS

    print("\n" + "="*60)
    print("IMPRESSION SHARE REPORT — Search Campaigns")
    print(f"Lookback: {args.days} days")
    print("Note: Competitor-level data requires Standard API Access.")
    print("="*60)

    total_critical = 0
    total_warnings = 0
    errored = []

    for name, cid in targets.items():
        try:
            campaigns = audit_account(ga_service, cid, args.days)
            print_account(name, cid, campaigns, args.days)
            for c in campaigns.values():
                issues, _ = evaluate_campaign(c)
                total_critical += sum(1 for lvl, _, _ in issues if lvl == "CRITICAL")
                total_warnings += sum(1 for lvl, _, _ in issues if lvl == "WARNING")
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
        print("\n  ✅ All Search campaigns have healthy impression share.")
    print("="*60)


if __name__ == "__main__":
    main()
