"""
Smart Bidding Health Checker
Purpose: Audit all Smart Bidding campaigns across client accounts.
         Checks conversion volume, CPA/ROAS target alignment, budget constraints,
         conversion value tracking, and zero-conversion spend.

Setup:
    Requires environment variables:
        GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET,
        GOOGLE_ADS_REFRESH_TOKEN, GOOGLE_ADS_CUSTOMER_ID

Usage:
    python3 scripts/smart_bidding_health.py                           # all clients
    python3 scripts/smart_bidding_health.py --customer-id 5544702166  # single client
    python3 scripts/smart_bidding_health.py --customer-id 5544702166 --client-name Hoski
    python3 scripts/smart_bidding_health.py --days 14                 # shorter window

Health Checks:
    🚨 CRITICAL
        - Spent >$50 with 0 conversions → likely tracking broken or target too aggressive
        - tROAS/MaxConvValue campaign with $0 conversion value → value tracking broken
        - Actual CPA >150% of target → severely underperforming
        - Actual ROAS <50% of target → severely underperforming

    ⚠️ WARNING
        - <15 conversions in window → insufficient data for Smart Bidding
        - 15–29 conversions → borderline (Google needs 30+/month)
        - Actual CPA 110–150% of target → drifting above target
        - Actual ROAS 50–70% of target → drifting below target
        - Budget limiting a Smart Bidding campaign → prevents optimization

    💡 INFO
        - No target set (unconstrained Maximize Conversions/Value) → note only

Changelog:
    2026-03-19  Initial version
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

SMART_BIDDING_STRATEGIES = {
    "TARGET_CPA", "TARGET_ROAS",
    "MAXIMIZE_CONVERSIONS", "MAXIMIZE_CONVERSION_VALUE",
}

# Thresholds
CONV_CRITICAL  = 15   # below this → critical
CONV_WARNING   = 30   # below this → warning
CPA_WARN_RATIO = 1.10  # actual CPA 10% above target → warning
CPA_CRIT_RATIO = 1.50  # actual CPA 50% above target → critical
ROAS_WARN_RATIO = 0.70 # actual ROAS 30% below target → warning
ROAS_CRIT_RATIO = 0.50 # actual ROAS 50% below target → critical
MIN_SPEND_FOR_ZERO_CONV = 50  # $50 spend with 0 conv → flag

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

def audit_account(ga_service, customer_id, client_name, days):
    date_range = f"LAST_{days}_DAYS" if days in (7, 14, 30) else "LAST_30_DAYS"

    rows = run_query(ga_service, customer_id, f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.serving_status,
            campaign.bidding_strategy_type,
            campaign.target_cpa.target_cpa_micros,
            campaign.target_roas.target_roas,
            campaign.maximize_conversions.target_cpa_micros,
            campaign.maximize_conversion_value.target_roas,
            campaign_budget.amount_micros,
            campaign_budget.has_recommended_budget,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.cost_per_conversion,
            metrics.search_impression_share
        FROM campaign
        WHERE segments.date DURING {date_range}
          AND campaign.status = ENABLED
        ORDER BY metrics.cost_micros DESC
    """)

    # Aggregate by campaign (rows come back per-day segmented)
    campaigns = {}
    for row in rows:
        c = row.campaign
        b = row.campaign_budget
        m = row.metrics
        cid = str(c.id)

        bidding = c.bidding_strategy_type.name
        if bidding not in SMART_BIDDING_STRATEGIES:
            continue

        if cid not in campaigns:
            # Extract configured targets
            target_cpa_micros = 0
            target_roas = 0.0

            if bidding == "TARGET_CPA":
                target_cpa_micros = c.target_cpa.target_cpa_micros
            elif bidding == "TARGET_ROAS":
                target_roas = c.target_roas.target_roas
            elif bidding == "MAXIMIZE_CONVERSIONS":
                target_cpa_micros = c.maximize_conversions.target_cpa_micros
            elif bidding == "MAXIMIZE_CONVERSION_VALUE":
                target_roas = c.maximize_conversion_value.target_roas

            campaigns[cid] = {
                "name": c.name,
                "bidding": bidding,
                "serving_status": c.serving_status.name,
                "daily_budget": b.amount_micros / 1_000_000,
                "budget_limited": b.has_recommended_budget,
                "target_cpa": target_cpa_micros / 1_000_000 if target_cpa_micros else 0,
                "target_roas": target_roas,
                "cost": 0.0,
                "conversions": 0.0,
                "conv_value": 0.0,
            }

        campaigns[cid]["cost"]        += m.cost_micros / 1_000_000
        campaigns[cid]["conversions"] += m.conversions
        campaigns[cid]["conv_value"]  += m.conversions_value

    if not campaigns:
        return [], 0, 0

    results = []
    total_critical = 0
    total_warnings = 0

    for cid, c in campaigns.items():
        issues = []
        cost       = c["cost"]
        conv       = c["conversions"]
        conv_value = c["conv_value"]
        bidding    = c["bidding"]
        target_cpa  = c["target_cpa"]
        target_roas = c["target_roas"]
        actual_cpa  = (cost / conv) if conv > 0 else None
        actual_roas = (conv_value / cost) if cost > 0 else None

        # ── Zero conversions with meaningful spend ──────────────────────────
        if cost >= MIN_SPEND_FOR_ZERO_CONV and conv == 0:
            issues.append(("CRITICAL", "🚨", f"ZERO CONVERSIONS — ${cost:.2f} spent in {days} days. Check conversion tracking or target is too restrictive."))

        # ── Conversion value tracking for value-based strategies ────────────
        elif bidding in ("TARGET_ROAS", "MAXIMIZE_CONVERSION_VALUE"):
            if conv > 0 and conv_value == 0:
                issues.append(("CRITICAL", "🚨", f"NO CONVERSION VALUE recorded — {conv:.0f} conversions tracked but $0 value. Value tracking is broken for {bidding}."))

        # ── Conversion volume ───────────────────────────────────────────────
        if conv < CONV_CRITICAL and cost >= MIN_SPEND_FOR_ZERO_CONV:
            # Already flagged as zero conv above if applicable
            if conv > 0:
                issues.append(("CRITICAL", "🚨", f"CRITICALLY LOW VOLUME — only {conv:.0f} conv in {days} days (need 15+ for stable Smart Bidding)"))
        elif conv < CONV_WARNING:
            issues.append(("WARNING", "⚠️ ", f"LOW VOLUME — {conv:.0f} conv in {days} days (need 30+/month for optimal Smart Bidding)"))

        # ── CPA alignment ───────────────────────────────────────────────────
        if actual_cpa and target_cpa > 0:
            ratio = actual_cpa / target_cpa
            if ratio > CPA_CRIT_RATIO:
                issues.append(("CRITICAL", "🚨", f"CPA WAY ABOVE TARGET — actual ${actual_cpa:.2f} vs target ${target_cpa:.2f} ({ratio*100:.0f}% of target)"))
            elif ratio > CPA_WARN_RATIO:
                issues.append(("WARNING", "⚠️ ", f"CPA DRIFTING ABOVE TARGET — actual ${actual_cpa:.2f} vs target ${target_cpa:.2f} ({ratio*100:.0f}% of target)"))

        # ── ROAS alignment ──────────────────────────────────────────────────
        if actual_roas and target_roas > 0:
            ratio = actual_roas / target_roas
            if ratio < ROAS_CRIT_RATIO:
                issues.append(("CRITICAL", "🚨", f"ROAS WAY BELOW TARGET — actual {actual_roas:.2f}x vs target {target_roas:.2f}x ({ratio*100:.0f}% of target)"))
            elif ratio < ROAS_WARN_RATIO:
                issues.append(("WARNING", "⚠️ ", f"ROAS DRIFTING BELOW TARGET — actual {actual_roas:.2f}x vs target {target_roas:.2f}x ({ratio*100:.0f}% of target)"))

        # ── Budget limiting Smart Bidding ───────────────────────────────────
        if c["budget_limited"]:
            issues.append(("WARNING", "⚠️ ", f"BUDGET CAPPING SMART BIDDING — ${c['daily_budget']:.2f}/day budget is limiting optimization. Google recommends increasing it."))

        # ── No target set (informational) ───────────────────────────────────
        if bidding in ("MAXIMIZE_CONVERSIONS", "MAXIMIZE_CONVERSION_VALUE") and target_cpa == 0 and target_roas == 0:
            issues.append(("INFO", "💡", f"NO TARGET SET — running unconstrained {bidding}. Consider adding a target CPA/ROAS once you have 30+ conversions."))

        c_count = sum(1 for lvl, _, _ in issues if lvl == "CRITICAL")
        w_count = sum(1 for lvl, _, _ in issues if lvl == "WARNING")
        total_critical += c_count
        total_warnings += w_count

        # Status icon for this campaign
        if c_count > 0:
            status = "🚨"
        elif w_count > 0:
            status = "⚠️ "
        elif issues:
            status = "💡"
        else:
            status = "✅"

        target_str = ""
        if target_cpa > 0:
            target_str = f" | Target CPA: ${target_cpa:.2f}"
        elif target_roas > 0:
            target_str = f" | Target ROAS: {target_roas:.2f}x"

        actual_str = ""
        if actual_cpa:
            actual_str = f" | Actual CPA: ${actual_cpa:.2f}"
        if actual_roas:
            actual_str += f" | Actual ROAS: {actual_roas:.2f}x"

        results.append({
            "status": status,
            "name": c["name"],
            "bidding": bidding,
            "cost": cost,
            "conv": conv,
            "conv_value": conv_value,
            "target_str": target_str,
            "actual_str": actual_str,
            "budget": c["daily_budget"],
            "issues": issues,
        })

    return results, total_critical, total_warnings


# ─── PRINT ───────────────────────────────────────────────────────────────────

def print_account(client_name, customer_id, results, days):
    smart_campaigns = len(results)
    has_critical = any(r["status"] == "🚨" for r in results)
    has_warning  = any(r["status"] == "⚠️ " for r in results)

    account_icon = "🚨" if has_critical else ("⚠️ " if has_warning else "✅")

    if smart_campaigns == 0:
        print(f"\n⬜  {client_name} ({customer_id}) — No Smart Bidding campaigns")
        return

    print(f"\n{account_icon}  {client_name} ({customer_id}) — {smart_campaigns} Smart Bidding campaign(s) | {days}-day window")

    for r in results:
        print(f"\n    {r['status']} [{r['bidding']}] {r['name']}")
        print(f"         Cost: ${r['cost']:.2f} | Conv: {r['conv']:.0f} | Value: ${r['conv_value']:.2f}{r['target_str']}{r['actual_str']}")
        if not r["issues"]:
            print(f"         ✅ Healthy — no issues detected")
        for level, icon, msg in r["issues"]:
            print(f"         {icon}  {msg}")


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Smart Bidding health checker")
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
    print("SMART BIDDING HEALTH CHECK")
    print(f"Lookback: {args.days} days")
    print("="*60)

    total_critical = 0
    total_warnings = 0
    errored = []

    for name, cid in targets.items():
        try:
            results, c, w = audit_account(ga_service, cid, name, args.days)
            print_account(name, cid, results, args.days)
            total_critical += c
            total_warnings += w
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
        print("\n  ✅ All Smart Bidding campaigns look healthy.")
    print("="*60)


if __name__ == "__main__":
    main()
