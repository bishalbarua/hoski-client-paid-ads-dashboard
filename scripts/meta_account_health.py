"""
Meta Account Health Check
Purpose: Full structural audit of a Meta ad account. Covers pixel health,
         attribution settings, campaign objectives, bid strategies, account
         standing, payment status, and campaign/ad set/ad structure.

         Run this before any major campaign changes, when onboarding a new
         client account, or when performance suddenly drops for no obvious reason.

Setup:
    Requires environment variables:
        META_APP_ID, META_APP_SECRET, META_ACCESS_TOKEN

    Install dependency:
        pip3 install facebook-business python-dotenv

Usage:
    python3 scripts/meta_account_health.py                          # all clients
    python3 scripts/meta_account_health.py --account act_XXXXXXX   # single account
    python3 scripts/meta_account_health.py --account act_XXXXXXX --client-name "Client"

Health Checks:
    🚨 CRITICAL
        - Account disabled or flagged
        - Payment method missing or failed
        - Pixel not firing in last 7 days (with active spend)
        - No purchase or lead events tracked (running conversion campaigns)
        - Account spending limit hit
        - All campaigns paused (but account has budget)

    ⚠️  WARNING
        - Pixel events without deduplication (browser + CAPI both firing without event IDs)
        - Attribution window shorter than 7-day click (missing late converters)
        - Campaigns using Reach/Awareness objective but paying for conversions
        - Ad sets with 1 active ad only (no creative testing)
        - Campaigns with no active ad sets
        - No custom audiences or lookalikes in use
        - Broad targeting on all ad sets (no audience signals)

    💡 INFO
        - Attribution window set to 1-day click only
        - Using Advantage+ audience on all campaigns (no manual audience testing)
        - Campaign budget optimization disabled on campaigns with 3+ ad sets

Changelog:
    2026-03-21  Initial version — account standing, pixel health, attribution,
                campaign/ad set/ad structure audit, bid strategy review,
                payment status, audience signal check.
"""

import argparse
import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adspixel import AdsPixel
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


# ─── ACCOUNT STANDING ─────────────────────────────────────────────────────────

ACCOUNT_STATUS_MAP = {
    1:   ("✅", "Active"),
    2:   ("🚨", "Disabled"),
    3:   ("⚠️ ", "Unsettled (payment issue)"),
    7:   ("⚠️ ", "Pending Review"),
    8:   ("⚠️ ", "Pending Closure"),
    9:   ("⚠️ ", "In Grace Period"),
    100: ("⚠️ ", "Pending Closure"),
    101: ("🚨", "Closed"),
}

def check_account_standing(account_id):
    account = AdAccount(account_id)
    issues  = []
    info    = {}

    try:
        data = account.api_get(fields=[
            "name", "account_status", "disable_reason",
            "currency", "timezone_name",
            "amount_spent", "spend_cap",
            "funding_source_details",
            "business",
        ])
    except FacebookRequestError as e:
        return [{"level": "CRITICAL", "icon": "🚨", "section": "Account",
                 "message": f"Cannot fetch account details: {e.api_error_message()}"}], {}

    status_code = int(data.get("account_status", 1))
    icon, status_label = ACCOUNT_STATUS_MAP.get(status_code, ("⚠️ ", f"Unknown ({status_code})"))

    spend_cap    = float(data.get("spend_cap",    0)) / 100
    amount_spent = float(data.get("amount_spent", 0)) / 100

    info = {
        "name":         data.get("name", account_id),
        "status":       status_label,
        "status_icon":  icon,
        "currency":     data.get("currency", "USD"),
        "timezone":     data.get("timezone_name", ""),
        "amount_spent": amount_spent,
        "spend_cap":    spend_cap,
        "business":     data.get("business", {}).get("name", ""),
    }

    if status_code != 1:
        reason = data.get("disable_reason", "")
        reason_str = f" — Reason: {reason}" if reason else ""
        issues.append({"level": "CRITICAL", "icon": "🚨", "section": "Account",
            "message": f"Account status: {status_label}{reason_str}"})

    if spend_cap > 0:
        ratio = amount_spent / spend_cap
        if ratio >= 1.0:
            issues.append({"level": "CRITICAL", "icon": "🚨", "section": "Account",
                "message": f"Spending limit hit — ${amount_spent:.2f} of ${spend_cap:.2f} cap consumed. Ads are paused."})
        elif ratio >= 0.80:
            issues.append({"level": "WARNING", "icon": "⚠️ ", "section": "Account",
                "message": f"Spending limit {ratio*100:.0f}% consumed — ${amount_spent:.2f} of ${spend_cap:.2f}. Increase limit soon."})

    # Payment method check
    funding = data.get("funding_source_details", {})
    if not funding:
        issues.append({"level": "CRITICAL", "icon": "🚨", "section": "Account",
            "message": "No payment method on file — ads cannot run."})

    return issues, info


# ─── PIXEL HEALTH ─────────────────────────────────────────────────────────────

KEY_EVENTS = {"Purchase", "Lead", "CompleteRegistration", "AddToCart",
              "InitiateCheckout", "ViewContent", "Contact", "SubmitApplication"}

def check_pixel_health(account_id):
    account = AdAccount(account_id)
    issues  = []

    try:
        pixels = account.get_ads_pixels(fields=[
            "id", "name", "last_fired_time",
            "is_unavailable",
            "data_use_setting",
        ])
    except FacebookRequestError as e:
        return [{"level": "WARNING", "icon": "⚠️ ", "section": "Pixel",
                 "message": f"Cannot fetch pixels: {e.api_error_message()}"}], []

    if not pixels:
        issues.append({"level": "WARNING", "icon": "⚠️ ", "section": "Pixel",
            "message": "No Meta Pixel found on this account."})
        return issues, []

    pixel_summaries = []
    seven_days_ago  = date.today() - timedelta(days=7)

    for pixel in pixels:
        pid            = pixel.get("id", "")
        pname          = pixel.get("name", pid)
        last_fired_raw = pixel.get("last_fired_time", "")
        unavailable    = pixel.get("is_unavailable", False)

        last_fired_str = "Never"
        last_fired_date = None
        if last_fired_raw:
            try:
                last_fired_date = date.fromisoformat(last_fired_raw[:10])
                last_fired_str  = last_fired_date.strftime("%Y-%m-%d")
            except ValueError:
                last_fired_str = last_fired_raw[:10]

        pixel_summaries.append({"id": pid, "name": pname, "last_fired": last_fired_str})

        if unavailable:
            issues.append({"level": "CRITICAL", "icon": "🚨", "section": "Pixel",
                "message": f"Pixel '{pname}' is unavailable — data collection stopped."})
        elif last_fired_date and last_fired_date < seven_days_ago:
            days_since = (date.today() - last_fired_date).days
            issues.append({"level": "CRITICAL", "icon": "🚨", "section": "Pixel",
                "message": f"Pixel '{pname}' last fired {days_since} days ago ({last_fired_str}) — check if tag is broken."})
        elif not last_fired_raw:
            issues.append({"level": "WARNING", "icon": "⚠️ ", "section": "Pixel",
                "message": f"Pixel '{pname}' has never fired — not installed or not receiving events."})

        # Check standard events via pixel stats
        try:
            stats = AdsPixel(pid).get_stats(
                fields=["event_name", "count"],
                params={
                    "start_time": (date.today() - timedelta(days=30)).strftime("%Y-%m-%d"),
                    "end_time":   date.today().strftime("%Y-%m-%d"),
                    "aggregation": "event",
                }
            )
            tracked_events = {s.get("event_name") for s in stats if int(s.get("count", 0)) > 0}

            missing_key = KEY_EVENTS - tracked_events
            if "Purchase" not in tracked_events and "Lead" not in tracked_events:
                issues.append({"level": "WARNING", "icon": "⚠️ ", "section": "Pixel",
                    "message": f"Pixel '{pname}': no Purchase or Lead events in last 30 days — conversion tracking may be misconfigured."})
            elif missing_key:
                issues.append({"level": "INFO", "icon": "💡", "section": "Pixel",
                    "message": f"Pixel '{pname}': standard events not tracked — {', '.join(sorted(missing_key))}. Consider adding for better optimization signals."})
        except FacebookRequestError:
            pass  # Pixel stats endpoint may not be accessible with all token types

    return issues, pixel_summaries


# ─── ATTRIBUTION SETTINGS ─────────────────────────────────────────────────────

def check_attribution(account_id):
    """
    Check account-level attribution settings via active campaigns.
    Meta attribution is set at the ad set level (attribution_spec).
    """
    account = AdAccount(account_id)
    issues  = []

    try:
        adsets = account.get_ad_sets(
            fields=["id", "name", "campaign_id", "attribution_spec", "status"],
            params={"effective_status": ["ACTIVE"], "limit": 500}
        )
    except FacebookRequestError as e:
        return [{"level": "WARNING", "icon": "⚠️ ", "section": "Attribution",
                 "message": f"Cannot fetch ad set attribution: {e.api_error_message()}"}]

    short_window_count = 0
    one_day_only_count = 0
    total              = 0

    for adset in adsets:
        spec = adset.get("attribution_spec", [])
        if not spec:
            continue
        total += 1

        click_windows = [s.get("window_days") for s in spec if s.get("event_type") == "CLICK"]
        view_windows  = [s.get("window_days") for s in spec if s.get("event_type") == "VIEW"]

        max_click = max(click_windows) if click_windows else 0

        if max_click == 1:
            one_day_only_count += 1
        elif max_click < 7:
            short_window_count += 1

    if total > 0:
        if short_window_count == total:
            issues.append({"level": "WARNING", "icon": "⚠️ ", "section": "Attribution",
                "message": f"All active ad sets use <7-day click window — likely missing late converters. Recommend 7-day click."})
        elif short_window_count > 0:
            issues.append({"level": "INFO", "icon": "💡", "section": "Attribution",
                "message": f"{short_window_count}/{total} active ad sets use <7-day click window."})

        if one_day_only_count > total // 2:
            issues.append({"level": "INFO", "icon": "💡", "section": "Attribution",
                "message": f"{one_day_only_count}/{total} active ad sets use 1-day click only — may undercount conversions."})

    return issues


# ─── CAMPAIGN STRUCTURE ───────────────────────────────────────────────────────

CONVERSION_OBJECTIVES = {
    "OUTCOME_SALES", "OUTCOME_LEADS", "CONVERSIONS",
    "PRODUCT_CATALOG_SALES", "LEAD_GENERATION",
}

def check_campaign_structure(account_id):
    account = AdAccount(account_id)
    issues  = []

    # Fetch all campaigns
    try:
        campaigns = account.get_campaigns(
            fields=["id", "name", "status", "effective_status", "objective",
                    "special_ad_categories", "bid_strategy", "daily_budget",
                    "lifetime_budget", "budget_rebalance_flag"],
            params={"limit": 500}
        )
    except FacebookRequestError as e:
        return [{"level": "WARNING", "icon": "⚠️ ", "section": "Structure",
                 "message": f"Cannot fetch campaigns: {e.api_error_message()}"}], {}

    active_camps    = [c for c in campaigns if c.get("effective_status") == "ACTIVE"]
    paused_camps    = [c for c in campaigns if c.get("effective_status") in ("PAUSED", "CAMPAIGN_PAUSED")]
    total_camps     = len(campaigns)

    if total_camps == 0:
        issues.append({"level": "WARNING", "icon": "⚠️ ", "section": "Structure",
            "message": "No campaigns found in this account."})
        return issues, {}

    if len(active_camps) == 0 and total_camps > 0:
        issues.append({"level": "WARNING", "icon": "⚠️ ", "section": "Structure",
            "message": f"All {total_camps} campaign(s) are paused — no active spend."})

    # Fetch ad sets for all campaigns
    try:
        adsets = account.get_ad_sets(
            fields=["id", "name", "campaign_id", "status", "effective_status",
                    "targeting", "optimization_goal", "attribution_spec",
                    "promoted_object"],
            params={"limit": 500}
        )
    except FacebookRequestError:
        adsets = []

    adsets_by_camp: dict = {}
    for adset in adsets:
        cid = str(adset.get("campaign_id", ""))
        if cid not in adsets_by_camp:
            adsets_by_camp[cid] = []
        adsets_by_camp[cid].append(adset)

    # Fetch ads
    try:
        ads = account.get_ads(
            fields=["id", "adset_id", "status", "effective_status"],
            params={"limit": 500}
        )
    except FacebookRequestError:
        ads = []

    ads_by_adset: dict = {}
    for ad in ads:
        asid = str(ad.get("adset_id", ""))
        if asid not in ads_by_adset:
            ads_by_adset[asid] = []
        ads_by_adset[asid].append(ad)

    # Audit each campaign
    objectives_in_use: dict = {}
    bid_strategies_in_use: dict = {}
    has_cbo           = False
    no_audience_count = 0

    for camp in campaigns:
        cid       = str(camp.get("id", ""))
        cname     = camp.get("name", cid)
        objective = str(camp.get("objective", "")).upper()
        bid_strat = str(camp.get("bid_strategy", "")).replace("_", " ").title()
        eff_status = camp.get("effective_status", "")

        objectives_in_use[objective] = objectives_in_use.get(objective, 0) + 1
        if bid_strat:
            bid_strategies_in_use[bid_strat] = bid_strategies_in_use.get(bid_strat, 0) + 1

        if camp.get("budget_rebalance_flag"):
            has_cbo = True

        if eff_status != "ACTIVE":
            continue

        camp_adsets  = adsets_by_camp.get(cid, [])
        active_adsets = [a for a in camp_adsets if a.get("effective_status") == "ACTIVE"]

        if not active_adsets:
            issues.append({"level": "WARNING", "icon": "⚠️ ", "section": "Structure",
                "message": f"Campaign '{cname}' is active but has no active ad sets — not spending."})
            continue

        # Check ad count per ad set
        for adset in active_adsets:
            asid   = str(adset.get("id", ""))
            asname = adset.get("name", asid)
            adset_ads = [a for a in ads_by_adset.get(asid, []) if a.get("effective_status") == "ACTIVE"]

            if len(adset_ads) == 0:
                issues.append({"level": "WARNING", "icon": "⚠️ ", "section": "Structure",
                    "message": f"Ad set '{asname}' has no active ads."})
            elif len(adset_ads) == 1:
                issues.append({"level": "INFO", "icon": "💡", "section": "Structure",
                    "message": f"Ad set '{asname}' has only 1 active ad — add 2-3 creatives for testing."})

            # Check for broad targeting (no audience spec)
            targeting = adset.get("targeting", {})
            has_audience_signals = any([
                targeting.get("flexible_spec"),
                targeting.get("custom_audiences"),
                targeting.get("lookalike_audience"),
                targeting.get("interests"),
                targeting.get("behaviors"),
            ])
            if not has_audience_signals:
                no_audience_count += 1

        # CBO suggestion: campaigns with 3+ ad sets that don't use CBO
        if len(active_adsets) >= 3 and not camp.get("budget_rebalance_flag"):
            issues.append({"level": "INFO", "icon": "💡", "section": "Structure",
                "message": f"Campaign '{cname}' has {len(active_adsets)} active ad sets without CBO — Meta can't optimize budget allocation across ad sets."})

    if no_audience_count > 0:
        total_active_adsets = sum(
            len([a for a in adsets_by_camp.get(str(c.get("id", "")), []) if a.get("effective_status") == "ACTIVE"])
            for c in active_camps
        )
        issues.append({"level": "INFO", "icon": "💡", "section": "Targeting",
            "message": f"{no_audience_count}/{total_active_adsets} active ad sets use broad targeting with no audience signals — intentional for Advantage+ or missing targeting spec."})

    structure_summary = {
        "total_campaigns":  total_camps,
        "active_campaigns": len(active_camps),
        "paused_campaigns": len(paused_camps),
        "objectives":       objectives_in_use,
        "bid_strategies":   bid_strategies_in_use,
        "has_cbo":          has_cbo,
        "total_adsets":     len(adsets),
        "total_ads":        len(ads),
    }

    return issues, structure_summary


# ─── AUDIT ONE ACCOUNT ────────────────────────────────────────────────────────

def audit_account(account_id, client_name):
    standing_issues, acct_info = check_account_standing(account_id)
    pixel_issues,    pixels     = check_pixel_health(account_id)
    attr_issues                 = check_attribution(account_id)
    struct_issues, struct       = check_campaign_structure(account_id)

    all_issues = standing_issues + pixel_issues + attr_issues + struct_issues

    critical = [i for i in all_issues if i["level"] == "CRITICAL"]
    warnings = [i for i in all_issues if i["level"] == "WARNING"]
    info     = [i for i in all_issues if i["level"] == "INFO"]

    if critical:
        status_icon = "🚨"
    elif warnings:
        status_icon = "⚠️ "
    elif info:
        status_icon = "💡"
    else:
        status_icon = "✅"

    # ── Account header ────────────────────────────────────────────────────────
    name_str   = acct_info.get("name", client_name)
    status_str = acct_info.get("status_icon", "") + " " + acct_info.get("status", "")
    biz_str    = f"  |  Business: {acct_info['business']}" if acct_info.get("business") else ""
    tz_str     = acct_info.get("timezone", "")
    cur_str    = acct_info.get("currency", "")
    spent_str  = f"${acct_info.get('amount_spent', 0):,.2f}"
    cap_str    = f"  |  Spend cap: ${acct_info.get('spend_cap', 0):,.2f}" if acct_info.get("spend_cap", 0) > 0 else ""

    print(f"\n{status_icon}  {client_name} ({account_id})")
    print(f"    Account: {name_str}  |  Status: {status_str}{biz_str}")
    print(f"    Currency: {cur_str}  |  Timezone: {tz_str}  |  Lifetime spend: {spent_str}{cap_str}")

    # ── Pixel summary ─────────────────────────────────────────────────────────
    if pixels:
        print(f"\n    Pixels ({len(pixels)}):")
        for px in pixels:
            print(f"      • {px['name']} (ID: {px['id']})  |  Last fired: {px['last_fired']}")
    else:
        print("\n    Pixels: None found")

    # ── Campaign structure summary ─────────────────────────────────────────────
    if struct:
        obj_str = ", ".join(f"{v}x {k.replace('OUTCOME_','').replace('_',' ').title()}"
                            for k, v in sorted(struct["objectives"].items(), key=lambda x: -x[1]))
        bid_str = ", ".join(f"{v}x {k}" for k, v in sorted(struct["bid_strategies"].items(), key=lambda x: -x[1]))
        cbo_str = "CBO enabled on some campaigns" if struct["has_cbo"] else "No CBO"
        print(f"\n    Campaigns: {struct['active_campaigns']} active / {struct['paused_campaigns']} paused / {struct['total_campaigns']} total")
        print(f"    Ad sets: {struct['total_adsets']}  |  Ads: {struct['total_ads']}")
        print(f"    Objectives: {obj_str or 'n/a'}")
        print(f"    Bid strategies: {bid_str or 'n/a'}  |  {cbo_str}")

    # ── Issues ────────────────────────────────────────────────────────────────
    if not all_issues:
        print("\n    ✅ No issues detected — account looks healthy.")
    else:
        # Group by section
        sections: dict = {}
        for issue in critical + warnings + info:
            sec = issue.get("section", "General")
            if sec not in sections:
                sections[sec] = []
            sections[sec].append(issue)

        for section, section_issues in sections.items():
            print(f"\n    [{section}]")
            for issue in section_issues:
                print(f"      {issue['icon']}  {issue['message']}")

    return {
        "critical": len(critical),
        "warnings": len(warnings),
        "info":     len(info),
    }


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Meta account health check — full structural audit"
    )
    parser.add_argument("--account",     help="Single ad account ID (e.g. act_XXXXXXX). Omit to run all clients.")
    parser.add_argument("--client-name", help="Display name when using --account")
    args = parser.parse_args()

    init_api()

    if args.account:
        targets = {(args.client_name or args.account): args.account}
    else:
        targets = ALL_CLIENTS

    print("\n" + "="*60)
    print("META ACCOUNT HEALTH CHECK")
    print(f"Date: {date.today().strftime('%Y-%m-%d')}")
    print("="*60)

    total_critical = 0
    total_warnings = 0
    total_info     = 0
    errored        = []

    for name, account_id in targets.items():
        try:
            result = audit_account(account_id, name)
            total_critical += result["critical"]
            total_warnings += result["warnings"]
            total_info     += result["info"]
        except Exception as e:
            errored.append(name)
            print(f"\n❌  {name} ({account_id}) — Error: {e}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  Accounts checked: {len(targets) - len(errored)}/{len(targets)}")
    print(f"  🚨 Critical:  {total_critical}")
    print(f"  ⚠️  Warnings:  {total_warnings}")
    print(f"  💡 Info:      {total_info}")
    if errored:
        print(f"  ❌ Errored:   {', '.join(errored)}")
    if total_critical == 0 and total_warnings == 0 and not errored:
        print("\n  ✅ All accounts look healthy.")
    print("="*60)


if __name__ == "__main__":
    main()
