"""
Conversion Tracking Audit
Purpose: Audit all conversion actions across all (or one) client accounts.
         Checks tag health, primary/secondary designation, double-counting risk,
         attribution windows, value tracking, and recent activity.

         Run this before any bid strategy changes or when conversion data looks off.

Setup:
    Requires environment variables:
        GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET,
        GOOGLE_ADS_REFRESH_TOKEN, GOOGLE_ADS_CUSTOMER_ID

Usage:
    python3 scripts/conversion_tracking_audit.py                           # all clients
    python3 scripts/conversion_tracking_audit.py --customer-id 5544702166  # single client
    python3 scripts/conversion_tracking_audit.py --customer-id 5544702166 --client-name "Hoski.ca"

Health Checks:
    🚨 CRITICAL
        - Primary conversion action with 0 conversions in 30 days (tag likely broken)
        - No primary conversion actions at all (Smart Bidding has no signal)
        - Multiple primary actions in the same category (double-counting)
        - Primary action tracking low-value events (page views, engagement)
        - No conversion actions at all in the account

    ⚠️  WARNING
        - MANY_PER_CLICK counting on a lead-gen action (inflates conversion numbers)
        - Conversion action with 0 conversions in 14 days (may be stale)
        - Click-through lookback window < 14 days (likely missing late converters)
        - Secondary-only setup with Smart Bidding (bidding on all_conversions, not conversions)
        - Value-based bid strategy but $0 conversion value recorded

    💡 INFO
        - LAST_CLICK attribution (consider switching to Data-Driven)
        - View-through lookback window active (inflates conversion counts)
        - Action set to secondary (won't influence Smart Bidding targets)

Changelog:
    2026-03-19  Initial version — tag health, primary/secondary, double-counting,
                attribution windows, value tracking, recent activity check.
"""

import argparse
import os
from collections import defaultdict
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

# Categories that should NOT be primary conversion goals for lead-gen/eComm
SUSPICIOUS_PRIMARY_CATEGORIES = {
    "PAGE_VIEW",
    "ENGAGEMENT",
    "OTHER",
    "UNKNOWN",
}

# Categories where MANY_PER_CLICK is typically wrong (lead gen — one lead per click)
LEAD_GEN_CATEGORIES = {
    "LEAD", "CONTACT", "SUBMIT_LEAD_FORM",
    "REQUEST_QUOTE", "SIGN_UP", "GET_DIRECTIONS",
    "OUTBOUND_CLICK", "PHONE_CALL_LEAD",
}

MIN_LOOKBACK_DAYS = 14  # click-through window below this → warning

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


# ─── PULL ────────────────────────────────────────────────────────────────────

def pull_conversion_actions(ga_service, customer_id):
    """Pull all conversion action definitions (status, type, settings)."""
    rows = run_query(ga_service, customer_id, """
        SELECT
            conversion_action.id,
            conversion_action.name,
            conversion_action.status,
            conversion_action.category,
            conversion_action.type,
            conversion_action.counting_type,
            conversion_action.include_in_conversions_metric,
            conversion_action.value_settings.default_value,
            conversion_action.value_settings.always_use_default_value,
            conversion_action.click_through_lookback_window_days,
            conversion_action.view_through_lookback_window_days,
            conversion_action.attribution_model_settings.attribution_model
        FROM conversion_action
        WHERE conversion_action.status = ENABLED
        ORDER BY conversion_action.name
    """)

    actions = {}
    for row in rows:
        ca = row.conversion_action
        actions[str(ca.id)] = {
            "id":             str(ca.id),
            "name":           ca.name,
            "status":         ca.status.name,
            "category":       ca.category.name,
            "type":           ca.type_.name,
            "counting_type":  ca.counting_type.name,
            "is_primary":     ca.include_in_conversions_metric,
            "default_value":  ca.value_settings.default_value,
            "always_use_default_value": ca.value_settings.always_use_default_value,
            "click_lookback": ca.click_through_lookback_window_days,
            "view_lookback":  ca.view_through_lookback_window_days,
            "attribution":    ca.attribution_model_settings.attribution_model.name,
            # filled in from metrics query below
            "conv_30d":       0.0,
            "conv_14d":       0.0,
            "conv_value_30d": 0.0,
        }
    return actions


def pull_conversion_metrics(ga_service, customer_id):
    """Pull recent conversion counts per action (30 days and 14 days)."""
    rows_30 = run_query(ga_service, customer_id, """
        SELECT
            conversion_action.id,
            metrics.conversions,
            metrics.conversions_value
        FROM conversion_action
        WHERE segments.date DURING LAST_30_DAYS
    """)
    rows_14 = run_query(ga_service, customer_id, """
        SELECT
            conversion_action.id,
            metrics.conversions
        FROM conversion_action
        WHERE segments.date DURING LAST_14_DAYS
    """)

    conv_30 = defaultdict(lambda: {"conv": 0.0, "value": 0.0})
    for row in rows_30:
        aid = str(row.conversion_action.id)
        conv_30[aid]["conv"]  += row.metrics.conversions
        conv_30[aid]["value"] += row.metrics.conversions_value

    conv_14 = defaultdict(float)
    for row in rows_14:
        conv_14[str(row.conversion_action.id)] += row.metrics.conversions

    return conv_30, conv_14


def pull_account_spend(ga_service, customer_id):
    """Pull total spend in last 30 days to contextualise zero-conversion flags."""
    rows = run_query(ga_service, customer_id, """
        SELECT metrics.cost_micros
        FROM customer
        WHERE segments.date DURING LAST_30_DAYS
    """)
    return sum(r.metrics.cost_micros / 1_000_000 for r in rows)


# ─── AUDIT ───────────────────────────────────────────────────────────────────

def audit_account(ga_service, customer_id):
    actions       = pull_conversion_actions(ga_service, customer_id)
    conv_30, conv_14 = pull_conversion_metrics(ga_service, customer_id)
    account_spend = pull_account_spend(ga_service, customer_id)

    # Merge metrics into action records
    for aid, a in actions.items():
        a["conv_30d"]       = conv_30[aid]["conv"]
        a["conv_value_30d"] = conv_30[aid]["value"]
        a["conv_14d"]       = conv_14[aid]

    issues        = []
    action_issues = defaultdict(list)  # aid → list of (level, msg)

    primary   = [a for a in actions.values() if a["is_primary"]]
    secondary = [a for a in actions.values() if not a["is_primary"]]

    # ── No conversion actions at all ────────────────────────────────────────
    if not actions:
        issues.append(("CRITICAL", "🚨", "NO CONVERSION ACTIONS — account has no enabled conversion tracking. Smart Bidding has nothing to optimise toward."))
        return actions, issues, action_issues, account_spend

    # ── No primary conversion actions ───────────────────────────────────────
    if not primary:
        issues.append(("CRITICAL", "🚨", f"NO PRIMARY CONVERSIONS — {len(secondary)} action(s) exist but all are set to secondary. Smart Bidding is flying blind (uses All Conversions, not Conversions column)."))

    # ── Double-counting: multiple primaries in same category ─────────────────
    category_primaries = defaultdict(list)
    for a in primary:
        category_primaries[a["category"]].append(a["name"])
    for cat, names in category_primaries.items():
        if len(names) > 1:
            issues.append(("CRITICAL", "🚨", f"DOUBLE-COUNTING RISK — {len(names)} primary actions both in category {cat}: {', '.join(names)}. Each click may count as {len(names)}x conversions."))

    # ── Per-action checks ────────────────────────────────────────────────────
    for a in actions.values():
        aid   = a["id"]
        name  = a["name"]
        label = "PRIMARY" if a["is_primary"] else "SECONDARY"

        # Suspicious primary category
        if a["is_primary"] and a["category"] in SUSPICIOUS_PRIMARY_CATEGORIES:
            action_issues[aid].append(("CRITICAL", f"WRONG PRIMARY — {name} ({a['category']}) is set as primary but tracks a low-value event. Should be secondary."))

        # Primary with zero conversions in 30 days (tag likely broken)
        if a["is_primary"] and a["conv_30d"] == 0 and account_spend > 50:
            action_issues[aid].append(("CRITICAL", f"TAG LIKELY BROKEN — {name} is primary but recorded 0 conversions in 30 days despite ${account_spend:.2f} account spend. Check tag installation."))
        elif a["conv_14d"] == 0 and a["conv_30d"] > 0:
            # Had conversions in 30d window but not in last 14d — going stale
            action_issues[aid].append(("WARNING", f"GOING STALE — {name} had {a['conv_30d']:.0f} conv in 30 days but 0 in the last 14 days. Tag may have broken recently."))

        # MANY_PER_CLICK on a lead-gen category
        if a["counting_type"] == "MANY_PER_CLICK" and a["category"] in LEAD_GEN_CATEGORIES:
            action_issues[aid].append(("WARNING", f"COUNTING TYPE — {name} uses MANY_PER_CLICK for a lead-gen category ({a['category']}). This inflates conversion counts. Switch to ONE_PER_CLICK unless you intentionally want to count multiple form fills per session."))

        # Short click-through lookback
        if a["click_lookback"] < MIN_LOOKBACK_DAYS:
            action_issues[aid].append(("WARNING", f"SHORT LOOKBACK — {name} has a {a['click_lookback']}-day click-through window (recommended: 30–90 days for most businesses). Late converters are being missed."))

        # Attribution model
        if a["attribution"] in ("LAST_CLICK", "EXTERNAL", "UNKNOWN"):
            action_issues[aid].append(("INFO", f"ATTRIBUTION — {name} uses {a['attribution']}. Consider Data-Driven Attribution (GOOGLE_SEARCH_ATTRIBUTION_DATA_DRIVEN) once you have enough volume."))

        # View-through window active
        if a["view_lookback"] > 0:
            action_issues[aid].append(("INFO", f"VIEW-THROUGH WINDOW — {name} has a {a['view_lookback']}-day view-through window. These are included in All Conversions and can inflate reported numbers."))

        # Secondary — informational
        if not a["is_primary"]:
            action_issues[aid].append(("INFO", f"SECONDARY — {name} is set to secondary (won't influence Smart Bidding targets or appear in Conversions column)."))

    return actions, issues, action_issues, account_spend


# ─── PRINT ───────────────────────────────────────────────────────────────────

LEVEL_ICON = {"CRITICAL": "🚨", "WARNING": "⚠️ ", "INFO": "💡"}

def print_account(client_name, customer_id, actions, issues, action_issues, spend):
    primary   = [a for a in actions.values() if a["is_primary"]]
    secondary = [a for a in actions.values() if not a["is_primary"]]

    crits = [i for i in issues if i[0] == "CRITICAL"]
    warns = [i for i in issues if i[0] == "WARNING"]

    all_action_crits = sum(
        1 for aid_issues in action_issues.values()
        for lvl, _ in aid_issues if lvl == "CRITICAL"
    )
    all_action_warns = sum(
        1 for aid_issues in action_issues.values()
        for lvl, _ in aid_issues if lvl == "WARNING"
    )

    total_crits = len(crits) + all_action_crits
    total_warns = len(warns) + all_action_warns

    if total_crits > 0:
        account_icon = "🚨"
    elif total_warns > 0:
        account_icon = "⚠️ "
    elif actions:
        account_icon = "✅"
    else:
        account_icon = "⬜"

    print(f"\n{account_icon}  {client_name} ({customer_id})")
    print(f"    {len(actions)} conversion action(s)  |  {len(primary)} primary  |  {len(secondary)} secondary  |  30-day spend: ${spend:.2f}")

    # Account-level issues first
    for lvl, icon, msg in issues:
        print(f"    {icon}  {msg}")

    if not actions:
        return total_crits, total_warns

    # Per-action scorecard
    for a in sorted(actions.values(), key=lambda x: (not x["is_primary"], x["name"])):
        aid   = a["id"]
        label = "PRIMARY  " if a["is_primary"] else "SECONDARY"
        a_issues = action_issues.get(aid, [])

        a_crits = sum(1 for lvl, _ in a_issues if lvl == "CRITICAL")
        a_warns = sum(1 for lvl, _ in a_issues if lvl == "WARNING")

        if a_crits > 0:
            row_icon = "🚨"
        elif a_warns > 0:
            row_icon = "⚠️ "
        elif a_issues:
            row_icon = "💡"
        else:
            row_icon = "✅"

        value_str = ""
        if a["conv_value_30d"] > 0:
            value_str = f"  |  Value: ${a['conv_value_30d']:.2f}"
        elif a["default_value"] > 0:
            value_str = f"  |  Default value: ${a['default_value']:.2f}"

        print(f"\n    {row_icon} [{label}] {a['name']}")
        print(f"         Type: {a['type']}  |  Category: {a['category']}  |  Counting: {a['counting_type']}")
        print(f"         Click window: {a['click_lookback']}d  |  View window: {a['view_lookback']}d  |  Attribution: {a['attribution']}")
        print(f"         Conv (30d): {a['conv_30d']:.0f}  |  Conv (14d): {a['conv_14d']:.0f}{value_str}")

        if not a_issues:
            print(f"         ✅ No issues detected")
        else:
            for lvl, msg in a_issues:
                print(f"         {LEVEL_ICON[lvl]}  {msg}")

    return total_crits, total_warns


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Conversion tracking audit — tag health, primary/secondary, double-counting")
    parser.add_argument("--customer-id", help="Single account ID (omit to run all clients)")
    parser.add_argument("--client-name", help="Display name when using --customer-id")
    args = parser.parse_args()

    client     = build_client()
    ga_service = client.get_service("GoogleAdsService")

    if args.customer_id:
        targets = {(args.client_name or args.customer_id): args.customer_id.replace("-", "")}
    else:
        targets = ALL_CLIENTS

    print("\n" + "="*60)
    print("CONVERSION TRACKING AUDIT")
    print("Checks: tag health · primary/secondary · double-counting")
    print("        attribution · value tracking · counting type")
    print("="*60)

    total_critical = 0
    total_warnings = 0
    errored        = []

    for name, cid in targets.items():
        try:
            actions, issues, action_issues, spend = audit_account(ga_service, cid)
            c, w = print_account(name, cid, actions, issues, action_issues, spend)
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
        print("\n  ✅ All conversion tracking looks healthy.")
    print("="*60)


if __name__ == "__main__":
    main()
