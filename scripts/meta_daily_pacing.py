"""
Meta Daily Pacing Monitor
Purpose: Morning health check across all (or one) Meta ad accounts.
         Flags: budget overpacing, underpacing, zero spend, rejected ads,
                campaigns in learning phase, and account spending limits.

         Run this every morning before client check-ins.

Setup:
    Requires environment variables:
        META_APP_ID, META_APP_SECRET, META_ACCESS_TOKEN

    Install dependency:
        pip3 install facebook-business python-dotenv

Usage:
    python3 scripts/meta_daily_pacing.py                          # all clients
    python3 scripts/meta_daily_pacing.py --account act_XXXXXXX   # single account
    python3 scripts/meta_daily_pacing.py --account act_XXXXXXX --client-name "Client Name"

Pacing Logic:
    Daily budget campaigns:
        Expected spend  = daily_budget * (hours_elapsed / 24)
        Pacing ratio    = today_spend / expected_spend
        OVERPACING  🔴  ratio > 1.25  (will overspend by >25%)
        ON TRACK    ✅  0.75 <= ratio <= 1.25
        UNDERPACING ⚠️   ratio < 0.75  (spending too slowly)
        NO SPEND    🚨  spend = $0 and >20% of day has elapsed

    Lifetime budget campaigns:
        Expected spend  = lifetime_budget * (days_elapsed / total_flight_days)
        Same thresholds applied to the cumulative pacing ratio.
        Campaigns with no end date are skipped for lifetime pacing.

    Account spending limit:
        Warns when >80% of the account-level monthly spending limit is consumed.

Changelog:
    2026-03-21  Initial version — daily/lifetime pacing, zero-spend detection,
                rejected ad check, learning phase flag, account spending limit.
"""

import argparse
import os
import sys
from datetime import datetime, date, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.exceptions import FacebookRequestError

# ─── CLIENT REGISTRY ─────────────────────────────────────────────────────────

ALL_CLIENTS = {
    "Demo (ice Ad Account)": "act_1509969187799563",
    "FaBesthetics":          "act_373162790093046",
    # "Client Name": "act_XXXXXXXXXXXXXXXXX",
}

# ─── PACING THRESHOLDS ────────────────────────────────────────────────────────

OVERPACE_THRESHOLD  = 1.25   # >125% of expected spend
UNDERPACE_THRESHOLD = 0.75   # <75% of expected spend
MIN_DAY_ELAPSED     = 0.20   # only flag zero-spend after 20% of day elapsed
SPEND_LIMIT_WARN    = 0.80   # warn when 80%+ of account spending limit consumed

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


# ─── PACING ───────────────────────────────────────────────────────────────────

def check_pacing(account_id, today_str, day_fraction):
    """
    Check campaign-level pacing for today.
    Handles daily budget and lifetime budget campaigns separately.
    Returns (issues, campaign_summaries).
    """
    account = AdAccount(account_id)

    # Fetch active campaigns with budget info
    try:
        campaigns = account.get_campaigns(
            fields=[
                "id", "name", "status", "effective_status",
                "daily_budget", "lifetime_budget",
                "start_time", "stop_time",
                "bid_strategy",
            ],
            params={"effective_status": ["ACTIVE"], "limit": 500}
        )
    except FacebookRequestError as e:
        print(f"    [API Error fetching campaigns] {e.api_error_message()}")
        return [], []

    # Fetch today's spend per campaign via insights
    try:
        insights_raw = account.get_insights(
            fields=["campaign_id", "spend"],
            params={
                "level":      "campaign",
                "time_range": {"since": today_str, "until": today_str},
                "limit":      500,
            }
        )
        today_spend_map = {row["campaign_id"]: float(row.get("spend", 0)) for row in insights_raw}
    except FacebookRequestError:
        today_spend_map = {}

    issues        = []
    camp_summaries = []

    today = date.fromisoformat(today_str)

    for camp in campaigns:
        cid          = camp.get("id", "")
        name         = camp.get("name", cid)
        daily_budget = float(camp.get("daily_budget", 0)) / 100  if camp.get("daily_budget")    else None
        life_budget  = float(camp.get("lifetime_budget", 0)) / 100 if camp.get("lifetime_budget") else None
        today_spend  = today_spend_map.get(cid, 0.0)

        # Determine bid strategy label
        bid_strategy = str(camp.get("bid_strategy", "")).replace("_", " ").title() or "n/a"

        # ── Daily budget campaigns ──────────────────────────────────────────
        if daily_budget and daily_budget > 0:
            expected_spend = daily_budget * day_fraction
            pacing_ratio   = (today_spend / expected_spend) if expected_spend > 0 else 0

            camp_summaries.append({
                "name":          name,
                "budget_type":   "daily",
                "budget":        daily_budget,
                "spend":         today_spend,
                "expected":      expected_spend,
                "ratio":         pacing_ratio,
                "bid_strategy":  bid_strategy,
            })

            if today_spend == 0 and day_fraction >= MIN_DAY_ELAPSED:
                issues.append({"level": "CRITICAL", "icon": "🚨", "campaign": name,
                    "message": f"ZERO SPEND — ${daily_budget:.2f}/day budget, nothing spent ({day_fraction*100:.0f}% of day elapsed)"})
            elif pacing_ratio > OVERPACE_THRESHOLD:
                issues.append({"level": "WARNING", "icon": "🔴", "campaign": name,
                    "message": f"OVERPACING {pacing_ratio*100:.0f}% — spent ${today_spend:.2f} of ${daily_budget:.2f} budget (expected ${expected_spend:.2f})"})
            elif pacing_ratio < UNDERPACE_THRESHOLD and day_fraction >= MIN_DAY_ELAPSED:
                issues.append({"level": "WARNING", "icon": "⚠️ ", "campaign": name,
                    "message": f"UNDERPACING {pacing_ratio*100:.0f}% — spent ${today_spend:.2f} of ${daily_budget:.2f} budget (expected ${expected_spend:.2f})"})

        # ── Lifetime budget campaigns ───────────────────────────────────────
        elif life_budget and life_budget > 0:
            start_str = camp.get("start_time", "")
            stop_str  = camp.get("stop_time", "")

            if not stop_str:
                # No end date — can't calculate pacing ratio, just report spend
                camp_summaries.append({
                    "name":         name,
                    "budget_type":  "lifetime (no end date)",
                    "budget":       life_budget,
                    "spend":        today_spend,
                    "expected":     None,
                    "ratio":        None,
                    "bid_strategy": bid_strategy,
                })
                continue

            try:
                start_date     = date.fromisoformat(start_str[:10])
                end_date       = date.fromisoformat(stop_str[:10])
                total_days     = max((end_date - start_date).days, 1)
                days_elapsed   = max((today - start_date).days, 0)
                days_remaining = max((end_date - today).days, 1)
                pacing_ratio   = None
                expected_spend = None

                if days_elapsed > 0:
                    expected_spend = life_budget * (days_elapsed / total_days)
                    # Fetch total spend for the campaign since start
                    try:
                        lifetime_insights = account.get_insights(
                            fields=["campaign_id", "spend"],
                            params={
                                "level":      "campaign",
                                "time_range": {"since": start_str[:10], "until": today_str},
                                "filtering":  [{"field": "campaign.id", "operator": "EQUAL", "value": cid}],
                                "limit":      1,
                            }
                        )
                        total_spend = float(lifetime_insights[0].get("spend", 0)) if lifetime_insights else 0.0
                    except (FacebookRequestError, IndexError):
                        total_spend = today_spend

                    pacing_ratio = (total_spend / expected_spend) if expected_spend > 0 else 0

                    camp_summaries.append({
                        "name":         name,
                        "budget_type":  f"lifetime ({days_remaining}d remaining)",
                        "budget":       life_budget,
                        "spend":        total_spend,
                        "expected":     expected_spend,
                        "ratio":        pacing_ratio,
                        "bid_strategy": bid_strategy,
                    })

                    if total_spend == 0 and days_elapsed >= 1:
                        issues.append({"level": "CRITICAL", "icon": "🚨", "campaign": name,
                            "message": f"ZERO SPEND — ${life_budget:.2f} lifetime budget, {days_elapsed}d elapsed, nothing spent"})
                    elif pacing_ratio and pacing_ratio > OVERPACE_THRESHOLD:
                        budget_remaining = life_budget - total_spend
                        daily_implied    = budget_remaining / days_remaining
                        issues.append({"level": "WARNING", "icon": "🔴", "campaign": name,
                            "message": f"LIFETIME OVERPACING {pacing_ratio*100:.0f}% — ${total_spend:.2f} of ${life_budget:.2f} spent, ${daily_implied:.2f}/day implied to finish on time"})
                    elif pacing_ratio and pacing_ratio < UNDERPACE_THRESHOLD:
                        budget_remaining = life_budget - total_spend
                        daily_implied    = budget_remaining / days_remaining
                        issues.append({"level": "WARNING", "icon": "⚠️ ", "campaign": name,
                            "message": f"LIFETIME UNDERPACING {pacing_ratio*100:.0f}% — ${total_spend:.2f} of ${life_budget:.2f} spent, needs ${daily_implied:.2f}/day to finish on time"})

            except (ValueError, TypeError):
                continue

    return issues, camp_summaries


# ─── REJECTED ADS ─────────────────────────────────────────────────────────────

def check_rejected_ads(account_id):
    """
    Flag ads with WITH_ISSUES or DISAPPROVED effective status.
    Returns list of issues.
    """
    account = AdAccount(account_id)
    try:
        ads = account.get_ads(
            fields=["id", "name", "status", "effective_status", "adset_id",
                    "campaign_id", "review_feedback_summary"],
            params={
                "effective_status": ["WITH_ISSUES", "DISAPPROVED"],
                "limit": 200,
            }
        )
    except FacebookRequestError as e:
        print(f"    [API Error fetching ads] {e.api_error_message()}")
        return []

    # Also need campaign names — fetch separately
    try:
        campaigns = account.get_campaigns(fields=["id", "name"], params={"limit": 500})
        camp_name_map = {c["id"]: c["name"] for c in campaigns}
    except FacebookRequestError:
        camp_name_map = {}

    issues = []
    for ad in ads:
        eff_status  = str(ad.get("effective_status", "")).upper()
        ad_name     = ad.get("name", ad.get("id", "Unknown Ad"))
        camp_id     = str(ad.get("campaign_id", ""))
        camp_name   = camp_name_map.get(camp_id, camp_id)
        feedback    = ad.get("review_feedback_summary", "")
        feedback_str = f" — {feedback}" if feedback else ""

        if eff_status == "DISAPPROVED":
            issues.append({"level": "CRITICAL", "icon": "🚨", "campaign": camp_name,
                "message": f"AD DISAPPROVED: '{ad_name}'{feedback_str}"})
        elif eff_status == "WITH_ISSUES":
            issues.append({"level": "WARNING", "icon": "⚠️ ", "campaign": camp_name,
                "message": f"AD WITH ISSUES: '{ad_name}'{feedback_str}"})

    return issues


# ─── LEARNING PHASE ───────────────────────────────────────────────────────────

def check_learning_phase(account_id):
    """
    Flag campaigns in learning phase (fewer than ~50 optimization events
    in the past 7 days — Meta's threshold for exiting learning).
    Uses delivery_info from campaign insights as a proxy.
    """
    account = AdAccount(account_id)
    try:
        insights = account.get_insights(
            fields=["campaign_id", "campaign_name", "spend", "actions"],
            params={
                "level":      "campaign",
                "time_range": {"since": (date.today() - timedelta(days=7)).strftime("%Y-%m-%d"),
                               "until": (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")},
                "limit":      500,
            }
        )
    except FacebookRequestError:
        return []

    issues = []
    for row in insights:
        spend   = float(row.get("spend", 0))
        if spend < 1:
            continue  # Skip campaigns with negligible spend

        actions = {a["action_type"]: float(a["value"]) for a in (row.get("actions") or [])}
        # Approximate optimization events: purchases + leads + post engagements
        # Use pixel-specific action types only to avoid double-counting
        # (Meta returns "purchase" and "offsite_conversion.fb_pixel_purchase" for the same event)
        opt_events = (actions.get("offsite_conversion.fb_pixel_purchase", 0) +
                      actions.get("offsite_conversion.fb_pixel_lead", 0) +
                      actions.get("leadgen_grouped", 0) +
                      actions.get("post_engagement", 0))

        if opt_events < 50 and spend > 10:
            camp_name = row.get("campaign_name", row.get("campaign_id", ""))
            issues.append({"level": "INFO", "icon": "📚", "campaign": camp_name,
                "message": f"LEARNING PHASE — {opt_events:.0f} optimization events in last 7 days (50+ needed to exit learning). Avoid budget/bid changes."})

    return issues


# ─── ACCOUNT SPENDING LIMIT ───────────────────────────────────────────────────

def check_account_spending_limit(account_id):
    """
    Warn if the account-level spending limit is close to being hit.
    """
    account = AdAccount(account_id)
    try:
        info = account.api_get(fields=[
            "spend_cap",
            "amount_spent",
            "currency",
        ])
    except FacebookRequestError:
        return []

    spend_cap    = float(info.get("spend_cap", 0)) / 100
    amount_spent = float(info.get("amount_spent", 0)) / 100

    if spend_cap <= 0:
        return []  # No spending limit set

    ratio = amount_spent / spend_cap
    issues = []
    if ratio >= 1.0:
        issues.append({"level": "CRITICAL", "icon": "🚨", "campaign": "ACCOUNT",
            "message": f"SPENDING LIMIT HIT — ${amount_spent:.2f} spent of ${spend_cap:.2f} cap. Ads may be paused."})
    elif ratio >= SPEND_LIMIT_WARN:
        issues.append({"level": "WARNING", "icon": "⚠️ ", "campaign": "ACCOUNT",
            "message": f"SPENDING LIMIT {ratio*100:.0f}% consumed — ${amount_spent:.2f} of ${spend_cap:.2f} cap. Increase limit soon."})

    return issues


# ─── AUDIT ONE ACCOUNT ────────────────────────────────────────────────────────

def audit_account(account_id, client_name, today_str, day_fraction):
    pacing_issues, camp_summaries = check_pacing(account_id, today_str, day_fraction)
    rejected_issues               = check_rejected_ads(account_id)
    learning_issues               = check_learning_phase(account_id)
    limit_issues                  = check_account_spending_limit(account_id)

    all_issues = pacing_issues + rejected_issues + learning_issues + limit_issues

    critical = [i for i in all_issues if i["level"] == "CRITICAL"]
    warnings = [i for i in all_issues if i["level"] == "WARNING"]
    info     = [i for i in all_issues if i["level"] == "INFO"]

    total_budget = sum(c["budget"] for c in camp_summaries)
    total_spend  = sum(c["spend"]  for c in camp_summaries)

    if critical:
        status_icon = "🚨"
    elif warnings:
        status_icon = "⚠️ "
    elif info:
        status_icon = "💡"
    else:
        status_icon = "✅"

    print(f"\n{status_icon}  {client_name} ({account_id})")
    print(f"    Total budget: ${total_budget:.2f}/day equiv  |  Spent today: ${total_spend:.2f}  |  Active campaigns: {len(camp_summaries)}")

    # Per-campaign pacing table
    for c in sorted(camp_summaries, key=lambda x: x["budget"], reverse=True):
        budget_label = f"${c['budget']:.2f} ({c['budget_type']})"
        spend_label  = f"${c['spend']:.2f}"
        if c["ratio"] is not None:
            pct = c["ratio"] * 100
            if c["ratio"] > OVERPACE_THRESHOLD:
                pace_label = f"🔴 {pct:.0f}%"
            elif c["ratio"] < UNDERPACE_THRESHOLD:
                pace_label = f"⚠️  {pct:.0f}%"
            else:
                pace_label = f"✅ {pct:.0f}%"
        else:
            pace_label = "n/a"
        print(f"    [{pace_label}]  {c['name']}  |  Budget: {budget_label}  |  Spend: {spend_label}  |  Bid: {c['bid_strategy']}")

    if not all_issues:
        print("    All clear — no issues detected.")
    else:
        print()
        for issue in critical + warnings + info:
            print(f"    {issue['icon']}  [{issue['campaign']}] {issue['message']}")

    return {"critical": len(critical), "warnings": len(warnings), "info": len(info)}


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Meta daily pacing monitor — morning health check")
    parser.add_argument("--account",     help="Single ad account ID (e.g. act_XXXXXXX). Omit to run all clients.")
    parser.add_argument("--client-name", help="Display name when using --account")
    args = parser.parse_args()

    init_api()

    now           = datetime.now()
    today_str     = now.strftime("%Y-%m-%d")
    day_fraction  = (now.hour * 3600 + now.minute * 60 + now.second) / 86400

    if args.account:
        targets = {(args.client_name or args.account): args.account}
    else:
        targets = ALL_CLIENTS

    print("\n" + "="*60)
    print("META DAILY PACING MONITOR")
    print(f"Run time: {now.strftime('%Y-%m-%d %H:%M')}  ({day_fraction*100:.1f}% of day elapsed)")
    print("="*60)

    total_critical = 0
    total_warnings = 0
    errored        = []

    for name, account_id in targets.items():
        try:
            result = audit_account(account_id, name, today_str, day_fraction)
            total_critical += result["critical"]
            total_warnings += result["warnings"]
        except Exception as e:
            errored.append(name)
            print(f"\n❌  {name} ({account_id}) — Error: {e}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  Accounts checked: {len(targets) - len(errored)}/{len(targets)}")
    print(f"  🚨 Critical issues: {total_critical}")
    print(f"  ⚠️  Warnings:        {total_warnings}")
    if errored:
        print(f"  ❌ Errored:         {', '.join(errored)}")
    if total_critical == 0 and total_warnings == 0 and not errored:
        print("\n  ✅ All accounts look healthy.")
    print("="*60)


if __name__ == "__main__":
    main()
