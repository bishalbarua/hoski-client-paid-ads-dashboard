"""
Meta Audience Report
Purpose: Audit all custom audiences and lookalikes in a Meta ad account.
         Shows audience size, type, freshness, usage in active ad sets,
         and overlap warnings where the same audience is used across
         multiple ad sets competing in the same auction.

         Run this when:
           - Onboarding a new client to map their audience assets
           - Planning a retargeting or lookalike campaign
           - Diagnosing audience overlap causing ad set competition
           - Checking if website custom audiences are still refreshing

Setup:
    Requires environment variables:
        META_APP_ID, META_APP_SECRET, META_ACCESS_TOKEN

    Install dependency:
        pip3 install facebook-business python-dotenv

Usage:
    python3 scripts/meta_audience_report.py                          # all clients
    python3 scripts/meta_audience_report.py --account act_XXXXXXX   # single account
    python3 scripts/meta_audience_report.py --account act_XXXXXXX --show-unused  # include unused audiences

Health Checks:
    🚨 CRITICAL
        - Custom audience with 0 or <100 people (too small to serve)
        - Website custom audience not updated in 30+ days (pixel may be broken)
        - Customer list audience with 0 matched users

    ⚠️  WARNING
        - Audience used in 3+ ad sets simultaneously (overlap/auction conflict risk)
        - Lookalike source audience below 1,000 people (quality degraded)
        - Engagement audience not updated in 14+ days
        - Saved audience (interest targeting) not used in any active ad set

    💡 INFO
        - Lookalike audience without a corresponding retargeting audience
        - Customer list audience (good signal for lookalike seeding)
        - Large audiences (1M+) — may need narrowing for efficiency

Changelog:
    2026-03-21  Initial version — custom audiences, lookalikes, usage mapping,
                overlap detection, freshness check, size health.
"""

import argparse
import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.customaudience import CustomAudience
from facebook_business.exceptions import FacebookRequestError

# ─── CLIENT REGISTRY ─────────────────────────────────────────────────────────

ALL_CLIENTS = {
    "Bloomer Health":                       "act_215505746566668",
    "Estate Jewelry Priced Right":          "act_422065096974825",
    "FaBesthetics":                         "act_373162790093046",
    "GDM":                                  "act_1229672268157520",
    "New Norseman":                         "act_1066181008711486",
    "Park Road Custom Furniture and Decor": "act_1302601091367185",
    "Serenity Familycare":                  "act_853944849499524",
    "Som K. Plastic Surgery":               "act_1401504290137519",
    "Synergy Spine & Nerve Center":         "act_2121931534696543",
    "Texas FHC":                            "act_331716185722452",
    "Voit Dental 1":                        "act_1092673602882817",
}

# ─── THRESHOLDS ───────────────────────────────────────────────────────────────

MIN_AUDIENCE_SIZE    = 100       # below this = too small to serve
MIN_LAL_SOURCE_SIZE  = 1_000     # lookalike source below this = degraded quality
OVERLAP_WARN         = 3         # used in this many active ad sets = overlap risk
WEBSITE_STALE_DAYS   = 30        # website CA not updated in this many days
ENGAGEMENT_STALE_DAYS = 14       # engagement CA not updated in this many days
LARGE_AUDIENCE       = 1_000_000 # flag for informational note

# ─── AUDIENCE TYPE LABELS ─────────────────────────────────────────────────────

SUBTYPE_LABELS = {
    "CUSTOM":           "Custom (misc)",
    "WEBSITE":          "Website Visitors",
    "APP":              "App Activity",
    "OFFLINE_CONVERSION": "Offline Events",
    "LIST":             "Customer List",
    "ENGAGEMENT":       "Engagement",
    "PARTNER":          "Partner Data",
    "LOOKALIKE":        "Lookalike",
    "CLAIM":            "Claimed",
    "REGULATED_INTERESTS_BASED": "Interest-Based",
    "STUDY_RULE_AUDIENCE": "Study Audience",
    "FOX":              "Fox",
    "MANAGED":          "Managed",
}

# ─── SETUP ────────────────────────────────────────────────────────────────────

def init_api():
    app_id  = os.environ.get("HOSKI_META_APP_ID") or os.environ.get("META_APP_ID")
    secret  = os.environ.get("HOSKI_META_APP_SECRET") or os.environ.get("META_APP_SECRET")
    token   = os.environ.get("HOSKI_META_ACCESS_TOKEN") or os.environ.get("META_ACCESS_TOKEN")
    missing = [k for k, v in {"META_APP_ID": app_id, "META_APP_SECRET": secret, "META_ACCESS_TOKEN": token}.items() if not v]
    if missing:
        print(f"Missing environment variables: {', '.join(missing)}")
        sys.exit(1)
    FacebookAdsApi.init(app_id=app_id, app_secret=secret, access_token=token)


# ─── PULL ─────────────────────────────────────────────────────────────────────

def fetch_audiences(account_id):
    account = AdAccount(account_id)
    try:
        audiences = account.get_custom_audiences(
            fields=[
                "id", "name", "subtype", "approximate_count_lower_bound",
                "approximate_count_upper_bound", "time_updated",
                "time_content_updated", "delivery_status",
                "lookalike_spec", "retention_days",
                "rule", "description",
                "operation_status",
            ],
            params={"limit": 500}
        )
        return list(audiences)
    except FacebookRequestError as e:
        print(f"    [API Error fetching audiences] {e.api_error_message()}")
        return []


def fetch_adset_audiences(account_id):
    """
    Map audience IDs to the active ad sets using them.
    Returns: {audience_id: [adset_name, ...]}
    """
    account = AdAccount(account_id)
    try:
        adsets = account.get_ad_sets(
            fields=["id", "name", "campaign_name", "targeting", "effective_status"],
            params={"effective_status": ["ACTIVE"], "limit": 500}
        )
    except FacebookRequestError:
        return {}

    usage_map: dict = {}

    for adset in adsets:
        targeting = adset.get("targeting", {})
        asname    = adset.get("name", "")
        campname  = adset.get("campaign_name", "")
        label     = f"{campname} > {asname}"

        # Custom audiences
        for ca in targeting.get("custom_audiences", []):
            aid = str(ca.get("id", ""))
            if aid:
                if aid not in usage_map:
                    usage_map[aid] = []
                usage_map[aid].append(label)

        # Excluded custom audiences
        for ca in targeting.get("excluded_custom_audiences", []):
            aid = str(ca.get("id", ""))
            if aid:
                if aid not in usage_map:
                    usage_map[aid] = []
                usage_map[aid].append(f"{label} [excluded]")

    return usage_map


# ─── AUDIT ────────────────────────────────────────────────────────────────────

def audit_audiences(audiences, usage_map, show_unused):
    """
    Classify and audit each audience. Returns (groups, issues, stats).
    groups: dict of subtype -> list of audience dicts
    """
    today = date.today()

    groups: dict = {}
    all_issues   = []
    stats: dict  = {
        "total":      len(audiences),
        "website":    0,
        "list":       0,
        "engagement": 0,
        "lookalike":  0,
        "other":      0,
        "in_use":     0,
        "too_small":  0,
    }

    for aud in audiences:
        aid      = str(aud.get("id", ""))
        aname    = aud.get("name", aid)
        subtype  = str(aud.get("subtype", "CUSTOM")).upper()
        label    = SUBTYPE_LABELS.get(subtype, subtype)
        size_lo  = int(aud.get("approximate_count_lower_bound", 0) or 0)
        size_hi  = int(aud.get("approximate_count_upper_bound", 0) or 0)
        size_mid = (size_lo + size_hi) // 2 if size_hi > 0 else size_lo

        # Parse last updated date
        time_updated_raw = aud.get("time_content_updated") or aud.get("time_updated") or ""
        last_updated     = None
        last_updated_str = "Unknown"
        if time_updated_raw:
            try:
                last_updated     = date.fromisoformat(str(time_updated_raw)[:10])
                last_updated_str = last_updated.strftime("%Y-%m-%d")
            except ValueError:
                last_updated_str = str(time_updated_raw)[:10]

        days_since_update = (today - last_updated).days if last_updated else None

        used_in  = usage_map.get(aid, [])
        in_use   = len(used_in) > 0

        # Lookalike spec
        lal_spec   = aud.get("lookalike_spec", {})
        lal_ratio  = lal_spec.get("ratio", None) if lal_spec else None
        lal_source = lal_spec.get("origin", [{}])[0].get("id", "") if lal_spec and lal_spec.get("origin") else ""

        # Retention days (website audiences)
        retention = aud.get("retention_days")

        # Delivery/operation status
        delivery_status   = aud.get("delivery_status", {})
        operation_status  = aud.get("operation_status", {})
        delivery_code     = delivery_status.get("code", 200) if isinstance(delivery_status, dict) else 200

        # Stats
        if subtype == "WEBSITE":
            stats["website"] += 1
        elif subtype == "LIST":
            stats["list"] += 1
        elif subtype == "ENGAGEMENT":
            stats["engagement"] += 1
        elif subtype == "LOOKALIKE":
            stats["lookalike"] += 1
        else:
            stats["other"] += 1

        if in_use:
            stats["in_use"] += 1

        if size_mid < MIN_AUDIENCE_SIZE:
            stats["too_small"] += 1

        # Issues
        aud_issues = []

        if size_mid < MIN_AUDIENCE_SIZE and size_mid > 0:
            aud_issues.append(("CRITICAL", f"Audience too small ({size_mid:,} people) — below Meta's minimum to serve ads"))
        elif size_mid == 0 and subtype != "LOOKALIKE":
            aud_issues.append(("CRITICAL", "Audience has 0 people — check pixel events or list upload"))

        if subtype == "WEBSITE" and days_since_update is not None and days_since_update > WEBSITE_STALE_DAYS:
            aud_issues.append(("CRITICAL", f"Website audience not updated in {days_since_update} days — pixel may be broken"))

        if subtype == "ENGAGEMENT" and days_since_update is not None and days_since_update > ENGAGEMENT_STALE_DAYS:
            aud_issues.append(("WARNING", f"Engagement audience not updated in {days_since_update} days"))

        if len(used_in) >= OVERLAP_WARN:
            aud_issues.append(("WARNING", f"Used in {len(used_in)} active ad sets — auction overlap risk. Consider consolidating."))

        if subtype == "LOOKALIKE" and lal_ratio:
            pct = float(lal_ratio) * 100
            if pct > 5:
                aud_issues.append(("WARNING", f"Lookalike size {pct:.0f}% — larger lookalikes are less precise. Consider 1-3% for prospecting."))

        if size_mid >= LARGE_AUDIENCE and in_use:
            aud_issues.append(("INFO", f"Large audience ({size_mid/1_000_000:.1f}M people) — consider narrowing with interest or demographic layers for efficiency"))

        if delivery_code not in (200, 0) and in_use:
            aud_issues.append(("WARNING", f"Delivery status code {delivery_code} — audience may not be deliverable"))

        all_issues.extend([(aid, aname, lvl, msg) for lvl, msg in aud_issues])

        # Build audience dict
        aud_dict = {
            "id":           aid,
            "name":         aname,
            "subtype":      subtype,
            "label":        label,
            "size_lo":      size_lo,
            "size_hi":      size_hi,
            "size_mid":     size_mid,
            "last_updated": last_updated_str,
            "days_stale":   days_since_update,
            "retention":    retention,
            "in_use":       in_use,
            "used_in":      used_in,
            "lal_ratio":    lal_ratio,
            "lal_source":   lal_source,
            "issues":       aud_issues,
        }

        if subtype not in groups:
            groups[subtype] = []
        groups[subtype].append(aud_dict)

    # Sort each group by size desc
    for subtype in groups:
        groups[subtype].sort(key=lambda x: x["size_mid"], reverse=True)

    return groups, all_issues, stats


# ─── PRINT ────────────────────────────────────────────────────────────────────

def fmt_size(lo, hi, mid):
    if mid == 0:
        return "< 100"
    if hi > 0 and hi != lo:
        if hi >= 1_000_000:
            return f"{lo/1_000_000:.1f}M-{hi/1_000_000:.1f}M"
        elif hi >= 1_000:
            return f"{lo/1_000:.0f}K-{hi/1_000:.0f}K"
        return f"{lo:,}-{hi:,}"
    if mid >= 1_000_000:
        return f"~{mid/1_000_000:.1f}M"
    if mid >= 1_000:
        return f"~{mid/1_000:.0f}K"
    return f"~{mid:,}"


SUBTYPE_ORDER = ["WEBSITE", "LIST", "ENGAGEMENT", "LOOKALIKE", "APP",
                 "OFFLINE_CONVERSION", "CUSTOM", "PARTNER"]

def print_account(client_name, account_id, groups, all_issues, stats, show_unused):
    critical_count = sum(1 for _, _, lvl, _ in all_issues if lvl == "CRITICAL")
    warning_count  = sum(1 for _, _, lvl, _ in all_issues if lvl == "WARNING")

    if critical_count:
        status_icon = "🚨"
    elif warning_count:
        status_icon = "⚠️ "
    else:
        status_icon = "✅"

    print(f"\n{status_icon}  {client_name} ({account_id})")
    print(f"    Total audiences: {stats['total']}  |  In use: {stats['in_use']}  |  Too small: {stats['too_small']}")
    print(f"    Website: {stats['website']}  |  Customer Lists: {stats['list']}  |  Engagement: {stats['engagement']}  |  Lookalikes: {stats['lookalike']}  |  Other: {stats['other']}")

    if not groups:
        print("    No custom audiences found.")
        return

    # Print by type in preferred order
    all_subtypes = list(groups.keys())
    ordered = [s for s in SUBTYPE_ORDER if s in all_subtypes] + \
              [s for s in all_subtypes if s not in SUBTYPE_ORDER]

    for subtype in ordered:
        audiences = groups[subtype]
        label     = SUBTYPE_LABELS.get(subtype, subtype)

        if not show_unused:
            display = [a for a in audiences if a["in_use"] or a["issues"]]
        else:
            display = audiences

        if not display:
            continue

        print(f"\n    [{label.upper()}]  ({len(audiences)} total)")
        print(f"    {'Name':<35}  {'Size':>12}  {'Updated':>12}  {'In Use':>6}  {'Retention':>9}")
        print(f"    {'─'*35}  {'─'*12}  {'─'*12}  {'─'*6}  {'─'*9}")

        for aud in display:
            size_str     = fmt_size(aud["size_lo"], aud["size_hi"], aud["size_mid"])
            updated_str  = aud["last_updated"]
            in_use_str   = f"Yes ({len(aud['used_in'])})" if aud["in_use"] else "No"
            retention    = f"{aud['retention']}d" if aud.get("retention") else "—"
            name_str     = aud["name"][:35]

            # Flag icon
            if any(lvl == "CRITICAL" for lvl, _ in aud["issues"]):
                row_icon = "🚨"
            elif any(lvl == "WARNING" for lvl, _ in aud["issues"]):
                row_icon = "⚠️ "
            elif aud["issues"]:
                row_icon = "💡"
            else:
                row_icon = "  "

            lal_str = f"  [{float(aud['lal_ratio'])*100:.0f}% LAL]" if aud.get("lal_ratio") else ""

            print(f"    {row_icon} {name_str:<35}  {size_str:>12}  {updated_str:>12}  {in_use_str:>6}  {retention:>9}{lal_str}")

            # Show which ad sets use this audience
            if aud["in_use"] and aud["used_in"]:
                for adset_label in aud["used_in"][:3]:
                    print(f"         Used in: {adset_label}")
                if len(aud["used_in"]) > 3:
                    print(f"         ... and {len(aud['used_in']) - 3} more ad sets")

            # Issues
            for lvl, msg in aud["issues"]:
                icon = "🚨" if lvl == "CRITICAL" else ("⚠️ " if lvl == "WARNING" else "💡")
                print(f"         {icon}  {msg}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Meta audience report — custom audiences, lookalikes, usage, and overlap"
    )
    parser.add_argument("--account",     help="Single ad account ID (e.g. act_XXXXXXX). Omit to run all clients.")
    parser.add_argument("--client-name", help="Display name when using --account")
    parser.add_argument("--show-unused", action="store_true",
                        help="Show all audiences including those not in any active ad set")
    args = parser.parse_args()

    init_api()

    if args.account:
        targets = {(args.client_name or args.account): args.account}
    else:
        targets = ALL_CLIENTS

    print("\n" + "="*60)
    print("META AUDIENCE REPORT")
    print(f"Date: {date.today().strftime('%Y-%m-%d')}")
    print("Default: shows audiences in use or with issues. Use --show-unused for all.")
    print("="*60)

    total_critical = 0
    total_warnings = 0
    errored        = []

    for name, account_id in targets.items():
        try:
            audiences  = fetch_audiences(account_id)
            usage_map  = fetch_adset_audiences(account_id)
            groups, all_issues, stats = audit_audiences(audiences, usage_map, args.show_unused)
            print_account(name, account_id, groups, all_issues, stats, args.show_unused)
            total_critical += sum(1 for _, _, lvl, _ in all_issues if lvl == "CRITICAL")
            total_warnings += sum(1 for _, _, lvl, _ in all_issues if lvl == "WARNING")
        except Exception as e:
            errored.append(name)
            print(f"\n❌  {name} ({account_id}) — Error: {e}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  Accounts checked: {len(targets) - len(errored)}/{len(targets)}")
    print(f"  🚨 Critical:  {total_critical}")
    print(f"  ⚠️  Warnings:  {total_warnings}")
    if errored:
        print(f"  ❌ Errored:   {', '.join(errored)}")
    if total_critical == 0 and total_warnings == 0 and not errored:
        print("\n  ✅ All audiences look healthy.")
    print("="*60)


if __name__ == "__main__":
    main()
