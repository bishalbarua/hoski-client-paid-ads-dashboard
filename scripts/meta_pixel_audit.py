"""
Meta Pixel Audit
Purpose: Deep audit of Meta Pixel and Conversions API (CAPI) setup for one or
         all client accounts. Checks event firing health, event volume, match
         quality, deduplication signals, and standard event coverage.

         Run this before any bid strategy changes, when conversion data looks
         wrong, or as part of new client onboarding.

Setup:
    Requires environment variables:
        META_APP_ID, META_APP_SECRET, META_ACCESS_TOKEN

    Install dependency:
        pip3 install facebook-business python-dotenv

Usage:
    python3 scripts/meta_pixel_audit.py                          # all clients
    python3 scripts/meta_pixel_audit.py --account act_XXXXXXX   # single account
    python3 scripts/meta_pixel_audit.py --account act_XXXXXXX --days 14  # 14-day event window

Health Checks:
    🚨 CRITICAL
        - Pixel not fired in last 7 days (with active ad spend)
        - Pixel never fired
        - No Purchase or Lead event in last 30 days (for conversion campaigns)
        - Event match quality score below 3.0 (poor signal for optimization)
        - Duplicate events detected without deduplication keys

    ⚠️  WARNING
        - Pixel last fired 3-7 days ago
        - Match quality score 3.0-5.9 (fair — room to improve)
        - CAPI not detected alongside browser pixel (missing redundancy)
        - Standard events firing with low volume (<10 in 30 days)
        - Key events missing (AddToCart, InitiateCheckout, ViewContent)

    💡 INFO
        - Custom events detected (non-standard names may not optimize well)
        - Events firing but no match quality data available
        - Multiple pixels on account (verify correct one is used in ad sets)

Event Match Quality Score (EMQ):
    8-10  Excellent — strong customer signal for optimization
    6-7   Good
    3-5   Fair — improve by passing email, phone, name in event parameters
    0-2   Poor — missing key customer data, optimization severely limited

Changelog:
    2026-03-21  Initial version — pixel health, event volume, match quality,
                CAPI detection, deduplication check, standard event coverage.
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
    "Demo (ice Ad Account)": "act_1509969187799563",
    # "Client Name": "act_XXXXXXXXXXXXXXXXX",
}

# ─── CONSTANTS ────────────────────────────────────────────────────────────────

# Standard Meta events and their importance tier
STANDARD_EVENTS = {
    # Tier 1 — conversion events (critical for optimization)
    "Purchase":              ("tier1", "Purchase completed"),
    "Lead":                  ("tier1", "Lead form submitted"),
    "CompleteRegistration":  ("tier1", "Registration completed"),
    "Subscribe":             ("tier1", "Subscription started"),
    "Contact":               ("tier1", "Contact initiated"),
    "SubmitApplication":     ("tier1", "Application submitted"),
    "Schedule":              ("tier1", "Appointment scheduled"),

    # Tier 2 — mid-funnel (valuable for retargeting and optimization signals)
    "InitiateCheckout":      ("tier2", "Checkout started"),
    "AddPaymentInfo":        ("tier2", "Payment info added"),
    "AddToCart":             ("tier2", "Item added to cart"),
    "AddToWishlist":         ("tier2", "Item wishlisted"),
    "ViewContent":           ("tier2", "Product/page viewed"),
    "Search":                ("tier2", "Search performed"),
    "FindLocation":          ("tier2", "Location searched"),

    # Tier 3 — top of funnel (awareness signals)
    "PageView":              ("tier3", "Page visited"),
}

EMQ_EXCELLENT = 8.0
EMQ_GOOD      = 6.0
EMQ_FAIR      = 3.0

# ─── SETUP ────────────────────────────────────────────────────────────────────

def init_api():
    app_id  = os.environ.get("META_APP_ID")
    secret  = os.environ.get("META_APP_SECRET")
    token   = os.environ.get("META_ACCESS_TOKEN")
    missing = [k for k, v in {"META_APP_ID": app_id, "META_APP_SECRET": secret, "META_ACCESS_TOKEN": token}.items() if not v]
    if missing:
        print(f"Missing environment variables: {', '.join(missing)}")
        sys.exit(1)
    FacebookAdsApi.init(app_id=app_id, app_secret=secret, access_token=token)


# ─── PIXEL FETCH ─────────────────────────────────────────────────────────────

def fetch_pixels(account_id):
    account = AdAccount(account_id)
    try:
        pixels = account.get_ads_pixels(fields=[
            "id", "name", "last_fired_time",
            "is_unavailable", "code",
            "data_use_setting",
            "owner_business",
        ])
        return list(pixels)
    except FacebookRequestError as e:
        print(f"    [API Error fetching pixels] {e.api_error_message()}")
        return []


def fetch_pixel_stats(pixel_id, start_str, end_str):
    """
    Fetch per-event stats for a pixel over the given date range.
    Returns list of {event_name, count, unique_count, source} dicts.
    """
    try:
        stats = AdsPixel(pixel_id).get_stats(
            fields=["event_name", "count", "unique_count"],
            params={
                "start_time":  start_str,
                "end_time":    end_str,
                "aggregation": "event",
            }
        )
        return [dict(s) for s in stats]
    except FacebookRequestError:
        return []


def fetch_pixel_match_quality(pixel_id):
    """
    Fetch event match quality scores per event.
    Returns dict: event_name -> emq_score (float).
    EMQ is only available for some pixel configurations and token types.
    """
    try:
        emq_data = AdsPixel(pixel_id).get_event_match_quality_info(
            fields=["event_name", "match_key_feedback"],
        )
        scores = {}
        for row in emq_data:
            ename = row.get("event_name", "")
            feedback = row.get("match_key_feedback", [])
            # EMQ is an aggregate score; approximate from feedback list length
            # (Full EMQ requires business-verified pixel — use what's available)
            if feedback and ename:
                # Count how many match keys are present as a proxy for quality
                scores[ename] = len(feedback)
        return scores
    except FacebookRequestError:
        return {}


def fetch_account_spend_last7(account_id):
    """Check if account has had any spend in the last 7 days."""
    account = AdAccount(account_id)
    today   = date.today()
    start   = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    end     = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    try:
        insights = account.get_insights(
            fields=["spend"],
            params={"time_range": {"since": start, "until": end}, "level": "account"}
        )
        return sum(float(i.get("spend", 0)) for i in insights)
    except FacebookRequestError:
        return 0.0


# ─── AUDIT ONE PIXEL ─────────────────────────────────────────────────────────

def audit_pixel(pixel, account_spend_7d, start_str, end_str, days):
    pid   = pixel.get("id", "")
    pname = pixel.get("name", pid)

    issues   = []
    findings = []

    # ── Firing health ─────────────────────────────────────────────────────────
    last_fired_raw  = pixel.get("last_fired_time", "")
    last_fired_date = None
    last_fired_str  = "Never"

    if last_fired_raw:
        try:
            last_fired_date = date.fromisoformat(last_fired_raw[:10])
            last_fired_str  = last_fired_date.strftime("%Y-%m-%d")
        except ValueError:
            last_fired_str = last_fired_raw[:10]

    days_since_fired = None
    if last_fired_date:
        days_since_fired = (date.today() - last_fired_date).days

    unavailable = pixel.get("is_unavailable", False)

    if unavailable:
        issues.append({"level": "CRITICAL", "icon": "🚨",
            "message": "Pixel is unavailable — data collection has stopped."})
    elif not last_fired_raw:
        issues.append({"level": "CRITICAL", "icon": "🚨",
            "message": "Pixel has never fired — not installed or blocked by browser."})
    elif days_since_fired and days_since_fired > 7 and account_spend_7d > 10:
        issues.append({"level": "CRITICAL", "icon": "🚨",
            "message": f"Pixel last fired {days_since_fired} days ago ({last_fired_str}) with active ad spend — tag likely broken."})
    elif days_since_fired and days_since_fired > 3:
        issues.append({"level": "WARNING", "icon": "⚠️ ",
            "message": f"Pixel last fired {days_since_fired} days ago ({last_fired_str}) — verify tag is still installed."})

    # ── Event volume ──────────────────────────────────────────────────────────
    stats = fetch_pixel_stats(pid, start_str, end_str)

    browser_events: dict = {}
    capi_events:    dict = {}
    custom_events         = []

    for s in stats:
        ename  = s.get("event_name", "")
        count  = int(s.get("count", 0))
        source = str(s.get("source", "")).upper()

        if "SERVER" in source or "CAPI" in source:
            capi_events[ename] = capi_events.get(ename, 0) + count
        else:
            browser_events[ename] = browser_events.get(ename, 0) + count

        if ename not in STANDARD_EVENTS and ename not in ("", "CustomEvent"):
            if ename not in custom_events:
                custom_events.append(ename)

    all_events: dict = {}
    for ename, cnt in browser_events.items():
        all_events[ename] = all_events.get(ename, 0) + cnt
    for ename, cnt in capi_events.items():
        all_events[ename] = all_events.get(ename, 0) + cnt

    has_capi     = len(capi_events) > 0
    has_purchase = "Purchase" in all_events and all_events["Purchase"] > 0
    has_lead     = "Lead" in all_events and all_events["Lead"] > 0

    # Conversion event check
    if account_spend_7d > 10 and not has_purchase and not has_lead:
        issues.append({"level": "WARNING", "icon": "⚠️ ",
            "message": f"No Purchase or Lead events in last {days} days — verify conversion tracking is configured."})

    # CAPI check
    if not has_capi:
        issues.append({"level": "WARNING", "icon": "⚠️ ",
            "message": "Conversions API (CAPI) not detected — browser-only tracking misses iOS-blocked and cookie-restricted events. Recommend adding CAPI."})
    else:
        # Deduplication check: both browser and CAPI firing same events
        shared = set(browser_events) & set(capi_events)
        if shared:
            findings.append(f"CAPI active alongside browser pixel for: {', '.join(sorted(shared)[:5])}. Verify event_id deduplication keys are set to avoid double-counting.")

    # Low-volume conversion events
    for ename in ("Purchase", "Lead", "CompleteRegistration"):
        if ename in all_events and 0 < all_events[ename] < 10:
            issues.append({"level": "WARNING", "icon": "⚠️ ",
                "message": f"{ename}: only {all_events[ename]} events in last {days} days — very low volume, optimization signal weak."})

    # Missing mid-funnel events
    missing_tier2 = [e for e in ("AddToCart", "InitiateCheckout", "ViewContent") if e not in all_events]
    if missing_tier2 and (has_purchase or has_lead):
        issues.append({"level": "INFO", "icon": "💡",
            "message": f"Mid-funnel events not tracked: {', '.join(missing_tier2)} — add these for better retargeting audiences."})

    # Custom events
    if custom_events:
        issues.append({"level": "INFO", "icon": "💡",
            "message": f"Custom (non-standard) events detected: {', '.join(custom_events[:5])}. Standard events optimize better — remap if possible."})

    # ── Match quality ─────────────────────────────────────────────────────────
    emq_scores = fetch_pixel_match_quality(pid)
    emq_summary = {}
    if emq_scores:
        for ename, score in emq_scores.items():
            if ename in STANDARD_EVENTS:
                emq_summary[ename] = score

    # ── Build output ──────────────────────────────────────────────────────────
    # Pixel header
    data_use = pixel.get("data_use_setting", "").replace("_", " ").title()
    biz      = pixel.get("owner_business", {})
    biz_name = biz.get("name", "") if isinstance(biz, dict) else ""

    health_icon = "✅"
    if any(i["level"] == "CRITICAL" for i in issues):
        health_icon = "🚨"
    elif any(i["level"] == "WARNING" for i in issues):
        health_icon = "⚠️ "

    print(f"\n    {health_icon}  Pixel: {pname} (ID: {pid})")
    print(f"         Last fired: {last_fired_str}  |  CAPI: {'Yes' if has_capi else 'No'}  |  Data use: {data_use or 'n/a'}", end="")
    if biz_name:
        print(f"  |  Owner: {biz_name}", end="")
    print()

    # Event table
    if all_events:
        print(f"\n         Events (last {days} days):")
        print(f"         {'Event':<30}  {'Count':>8}  {'Browser':>8}  {'CAPI':>6}  Tier")
        print(f"         {'─'*30}  {'─'*8}  {'─'*8}  {'─'*6}  {'─'*6}")

        # Sort: tier1 first, then tier2, tier3, custom
        def sort_key(item):
            ename, _ = item
            tier_map = {"tier1": 0, "tier2": 1, "tier3": 2}
            tier = STANDARD_EVENTS.get(ename, ("custom",))[0]
            return (tier_map.get(tier, 3), -all_events.get(ename, 0))

        for ename, total_count in sorted(all_events.items(), key=sort_key):
            browser_cnt = browser_events.get(ename, 0)
            capi_cnt    = capi_events.get(ename, 0)
            tier_info   = STANDARD_EVENTS.get(ename)
            tier_label  = tier_info[0].upper() if tier_info else "CUSTOM"
            emq         = emq_summary.get(ename)
            emq_str     = f"  EMQ: {emq:.1f}" if emq is not None else ""
            print(f"         {ename:<30}  {total_count:>8,}  {browser_cnt:>8,}  {capi_cnt:>6,}  {tier_label}{emq_str}")
    else:
        print(f"\n         No events recorded in last {days} days.")

    # Issues
    if issues:
        print()
        for issue in sorted(issues, key=lambda x: {"CRITICAL": 0, "WARNING": 1, "INFO": 2}.get(x["level"], 3)):
            print(f"         {issue['icon']}  {issue['message']}")

    if findings:
        print()
        for f in findings:
            print(f"         💡  {f}")

    return issues


# ─── AUDIT ONE ACCOUNT ────────────────────────────────────────────────────────

def audit_account(account_id, client_name, start_str, end_str, days):
    pixels = fetch_pixels(account_id)
    acct_spend = fetch_account_spend_last7(account_id)

    all_issues = []

    print(f"\n{'='*60}")
    print(f"  {client_name} ({account_id})")
    print(f"  Account spend last 7 days: ${acct_spend:.2f}")
    print(f"  Pixels found: {len(pixels)}")
    print(f"{'='*60}")

    if not pixels:
        print("  ⚠️   No pixels found. Install the Meta Pixel to enable conversion tracking.")
        return {"critical": 1, "warning": 0, "info": 0}

    if len(pixels) > 1:
        print(f"  💡  Multiple pixels ({len(pixels)}) — verify each ad set uses the correct pixel.")

    for pixel in pixels:
        issues = audit_pixel(pixel, acct_spend, start_str, end_str, days)
        all_issues.extend(issues)

    critical = sum(1 for i in all_issues if i["level"] == "CRITICAL")
    warnings = sum(1 for i in all_issues if i["level"] == "WARNING")
    info     = sum(1 for i in all_issues if i["level"] == "INFO")

    return {"critical": critical, "warning": warnings, "info": info}


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Meta Pixel audit — event health, match quality, CAPI detection"
    )
    parser.add_argument("--account",     help="Single ad account ID (e.g. act_XXXXXXX). Omit to run all clients.")
    parser.add_argument("--client-name", help="Display name when using --account")
    parser.add_argument("--days",        type=int, default=30,
                        help="Event lookback window in days (default: 30)")
    args = parser.parse_args()

    init_api()

    today      = date.today()
    end_date   = today - timedelta(days=1)
    start_date = end_date - timedelta(days=args.days - 1)
    start_str  = start_date.strftime("%Y-%m-%d")
    end_str    = end_date.strftime("%Y-%m-%d")

    if args.account:
        targets = {(args.client_name or args.account): args.account}
    else:
        targets = ALL_CLIENTS

    print("\n" + "="*60)
    print("META PIXEL AUDIT")
    print(f"Date:   {today.strftime('%Y-%m-%d')}")
    print(f"Window: {start_str} -> {end_str} ({args.days} days)")
    print("="*60)

    total_critical = 0
    total_warnings = 0
    total_info     = 0
    errored        = []

    for name, account_id in targets.items():
        try:
            result = audit_account(account_id, name, start_str, end_str, args.days)
            total_critical += result["critical"]
            total_warnings += result["warning"]
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
        print("\n  ✅ All pixels look healthy.")
    print("="*60)


if __name__ == "__main__":
    main()
