"""
Meta Conversion Report
Purpose: Detailed conversion breakdown by action type, attribution window,
         and campaign. Shows purchases, leads, and other results with value
         tracking, CPA, ROAS, and attribution window comparison.

         Key use cases:
           - Understanding true conversion volume across attribution windows
           - Identifying which campaigns drive the most valuable conversions
           - Spotting attribution window discrepancies (1-day vs 7-day)
           - Feeding /monthly-report with conversion data for client reporting

Setup:
    Requires environment variables:
        META_APP_ID, META_APP_SECRET, META_ACCESS_TOKEN

    Install dependency:
        pip3 install facebook-business python-dotenv

Usage:
    python3 scripts/meta_conversion_report.py                                     # all clients, last 30 days
    python3 scripts/meta_conversion_report.py --mode weekly                       # last 7 days
    python3 scripts/meta_conversion_report.py --days 90                           # last 90 days
    python3 scripts/meta_conversion_report.py --start 2026-01-01 --end 2026-03-20 # exact range
    python3 scripts/meta_conversion_report.py --account act_XXXXXXX              # single account
    python3 scripts/meta_conversion_report.py --by-campaign                       # break down by campaign

Attribution Windows Compared:
    1dc   1-day click
    7dc   7-day click  (Meta default, recommended)
    1dv   1-day view
    28dc  28-day click (legacy, shown when available)

    A large gap between 1dc and 7dc means you have many late converters
    who click and return days later — common for high-consideration purchases.
    A large 1dv count means view-through attribution is inflating your numbers.

Flags:
    🚨 CRITICAL   Zero conversions with >$100 spend  |  CPA > 5x target
    ⚠️  WARNING    View-through > 30% of total reported conversions
                  7dc vs 1dc delta > 50% (large late-converter gap)
    💡 INFO        No value tracking on purchase events

Changelog:
    2026-03-21  Initial version — conversion breakdown by type, attribution
                window comparison, value/ROAS tracking, campaign rollup.
"""

import argparse
import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.exceptions import FacebookRequestError

# ─── CLIENT REGISTRY ─────────────────────────────────────────────────────────

ALL_CLIENTS = {
    "Demo (ice Ad Account)": "act_1509969187799563",
    # "Client Name": "act_XXXXXXXXXXXXXXXXX",
}

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


# ─── DATE RANGES ─────────────────────────────────────────────────────────────

def get_date_ranges(mode=None, days=None, start=None, end=None):
    today = date.today()

    if start and end:
        return {
            "curr_start":  start,
            "curr_end":    end,
            "prior_start": None,
            "prior_end":   None,
            "label":       f"Custom range: {start} to {end}",
        }

    if days:
        curr_end   = today - timedelta(days=1)
        curr_start = curr_end - timedelta(days=days - 1)
        label      = f"Rolling {days} days vs prior {days} days"
    elif mode == "weekly":
        curr_end   = today - timedelta(days=1)
        curr_start = curr_end - timedelta(days=6)
        label      = "Week-over-Week (rolling 7 days)"
    else:  # monthly default
        curr_end   = today - timedelta(days=1)
        curr_start = curr_end - timedelta(days=29)
        label      = "Month-over-Month (30 days)"

    prior_end   = curr_start - timedelta(days=1)
    prior_start = prior_end - timedelta(days=(curr_end - curr_start).days)

    return {
        "curr_start":  curr_start.strftime("%Y-%m-%d"),
        "curr_end":    curr_end.strftime("%Y-%m-%d"),
        "prior_start": prior_start.strftime("%Y-%m-%d"),
        "prior_end":   prior_end.strftime("%Y-%m-%d"),
        "label":       label,
    }


# ─── ACTION TYPE GROUPING ─────────────────────────────────────────────────────

# Maps raw Meta action_types to clean labels and categories
ACTION_GROUPS = {
    # Purchases
    "offsite_conversion.fb_pixel_purchase": ("Purchase",  "purchase"),
    "purchase":                             ("Purchase",  "purchase"),
    "omni_purchase":                        ("Purchase",  "purchase"),

    # Leads
    "offsite_conversion.fb_pixel_lead":     ("Lead",      "lead"),
    "lead":                                 ("Lead",      "lead"),
    "leadgen_grouped":                      ("Lead (Form)","lead"),
    "onsite_conversion.lead_grouped":       ("Lead (Form)","lead"),

    # Registrations
    "offsite_conversion.fb_pixel_complete_registration": ("Registration", "registration"),
    "omni_complete_registration":           ("Registration", "registration"),

    # Contacts / Appointments
    "offsite_conversion.fb_pixel_contact":  ("Contact",   "contact"),
    "offsite_conversion.fb_pixel_schedule": ("Appointment","contact"),

    # Mid-funnel (not primary but useful for reporting)
    "offsite_conversion.fb_pixel_initiate_checkout": ("Initiate Checkout", "checkout"),
    "offsite_conversion.fb_pixel_add_to_cart":       ("Add to Cart",       "cart"),
    "offsite_conversion.fb_pixel_view_content":      ("View Content",      "awareness"),
}

CONVERSION_CATEGORIES = {"purchase", "lead", "registration", "contact"}


# ─── PULL ─────────────────────────────────────────────────────────────────────

INSIGHTS_FIELDS = [
    "campaign_id",
    "campaign_name",
    "spend",
    "actions",
    "action_values",
    "cost_per_action_type",
]

# Attribution windows to request
ATTRIBUTION_WINDOWS = [
    "1d_click",
    "7d_click",
    "1d_view",
    "28d_click",
]


def pull_conversions(account_id, start, end, level="account"):
    """
    Pull conversion data with attribution window breakdown.
    Returns (account_level_dict, campaign_list).
    """
    account = AdAccount(account_id)

    params = {
        "time_range":          {"since": start, "until": end},
        "action_attribution_windows": ATTRIBUTION_WINDOWS,
        "limit": 500,
    }

    # Account-level pull
    try:
        acct_insights = account.get_insights(
            fields=INSIGHTS_FIELDS + ["impressions", "clicks", "reach"],
            params={**params, "level": "account"}
        )
        acct_rows = list(acct_insights)
    except FacebookRequestError as e:
        print(f"    [API Error account level] {e.api_error_message()}")
        acct_rows = []

    # Campaign-level pull
    try:
        camp_insights = account.get_insights(
            fields=INSIGHTS_FIELDS,
            params={**params, "level": "campaign"}
        )
        camp_rows = list(camp_insights)
    except FacebookRequestError as e:
        print(f"    [API Error campaign level] {e.api_error_message()}")
        camp_rows = []

    def parse_actions_with_windows(actions_raw, values_raw, cpa_raw):
        """
        Parse actions list into grouped dict with window breakdown.
        Returns: {label: {window: count, "value": val, "cpa": cpa}}
        """
        result: dict = {}

        for item in (actions_raw or []):
            action_type = item.get("action_type", "")
            if action_type not in ACTION_GROUPS:
                continue
            label, category = ACTION_GROUPS[action_type]

            if label not in result:
                result[label] = {
                    "category": category,
                    "1d_click": 0.0,
                    "7d_click": 0.0,
                    "1d_view":  0.0,
                    "28d_click": 0.0,
                    "value":    0.0,
                    "cpa":      None,
                }

            # Default (7d_click is Meta's default reporting window)
            default_val = float(item.get("value", 0))

            # Window-specific values
            result[label]["1d_click"]  = float(item.get("1d_click",  default_val))
            result[label]["7d_click"]  = float(item.get("7d_click",  default_val))
            result[label]["1d_view"]   = float(item.get("1d_view",   0))
            result[label]["28d_click"] = float(item.get("28d_click", 0))

        # Values
        for item in (values_raw or []):
            action_type = item.get("action_type", "")
            if action_type not in ACTION_GROUPS:
                continue
            label, _ = ACTION_GROUPS[action_type]
            if label in result:
                result[label]["value"] = float(item.get("7d_click", item.get("value", 0)))

        # CPA per action type
        for item in (cpa_raw or []):
            action_type = item.get("action_type", "")
            if action_type not in ACTION_GROUPS:
                continue
            label, _ = ACTION_GROUPS[action_type]
            if label in result:
                result[label]["cpa"] = float(item.get("7d_click", item.get("value", 0)))

        return result

    # Parse account-level
    acct_data: dict = {
        "spend":       0.0,
        "impressions": 0,
        "clicks":      0,
        "reach":       0,
        "actions":     {},
    }
    for row in acct_rows:
        acct_data["spend"]       += float(row.get("spend", 0))
        acct_data["impressions"] += int(row.get("impressions", 0))
        acct_data["clicks"]      += int(row.get("clicks", 0))
        acct_data["reach"]       += int(row.get("reach", 0))
        parsed = parse_actions_with_windows(
            row.get("actions", []),
            row.get("action_values", []),
            row.get("cost_per_action_type", []),
        )
        for label, vals in parsed.items():
            if label not in acct_data["actions"]:
                acct_data["actions"][label] = dict(vals)
            else:
                for window in ("1d_click", "7d_click", "1d_view", "28d_click"):
                    acct_data["actions"][label][window] = (
                        acct_data["actions"][label].get(window, 0) + vals.get(window, 0)
                    )
                acct_data["actions"][label]["value"] += vals.get("value", 0)

    # Parse campaign-level
    campaigns = []
    for row in camp_rows:
        spend  = float(row.get("spend", 0))
        parsed = parse_actions_with_windows(
            row.get("actions", []),
            row.get("action_values", []),
            row.get("cost_per_action_type", []),
        )
        if parsed or spend > 0:
            campaigns.append({
                "id":      row.get("campaign_id", ""),
                "name":    row.get("campaign_name", ""),
                "spend":   spend,
                "actions": parsed,
            })

    campaigns.sort(key=lambda x: x["spend"], reverse=True)
    return acct_data, campaigns


# ─── PRINT ────────────────────────────────────────────────────────────────────

def fmt_delta(curr, prior):
    if not prior or prior == 0:
        return ""
    pct   = (curr - prior) / abs(prior)
    arrow = "▲" if pct > 0 else "▼"
    sign  = "+" if pct > 0 else ""
    return f"  ({arrow}{sign}{pct*100:.0f}% vs prior)"


def print_conversion_table(actions, spend, prior_actions=None):
    """Print the conversion breakdown table with attribution windows."""
    if not actions:
        print("    No conversions tracked in this period.")
        return

    # Separate primary conversions from funnel metrics
    primary = {k: v for k, v in actions.items() if v["category"] in CONVERSION_CATEGORIES}
    funnel  = {k: v for k, v in actions.items() if v["category"] not in CONVERSION_CATEGORIES}

    def print_section(items, header):
        if not items:
            return
        print(f"\n    {header}")
        print(f"    {'Action':<22}  {'7d Click':>9}  {'1d Click':>9}  {'1d View':>8}  {'Value':>10}  {'CPA':>8}  {'ROAS':>6}")
        print(f"    {'─'*22}  {'─'*9}  {'─'*9}  {'─'*8}  {'─'*10}  {'─'*8}  {'─'*6}")

        for label, vals in sorted(items.items(), key=lambda x: -x[1].get("7d_click", 0)):
            cnt_7dc  = vals.get("7d_click", 0)
            cnt_1dc  = vals.get("1d_click", 0)
            cnt_1dv  = vals.get("1d_view",  0)
            value    = vals.get("value", 0)
            cpa      = vals.get("cpa")
            roas     = (value / spend) if spend > 0 and value > 0 else None

            cnt_7dc_str = f"{cnt_7dc:.0f}"
            cnt_1dc_str = f"{cnt_1dc:.0f}"
            cnt_1dv_str = f"{cnt_1dv:.0f}" if cnt_1dv > 0 else "—"
            val_str     = f"${value:,.2f}"   if value > 0  else "—"
            cpa_str     = f"${cpa:.2f}"      if cpa        else "—"
            roas_str    = f"{roas:.2f}x"     if roas       else "—"

            prior_cnt = (prior_actions or {}).get(label, {}).get("7d_click", 0)
            delta_str = fmt_delta(cnt_7dc, prior_cnt)

            # Attribution gap warnings
            flags = []
            if cnt_7dc > 0 and cnt_1dc > 0:
                late_ratio = (cnt_7dc - cnt_1dc) / cnt_7dc
                if late_ratio > 0.50:
                    flags.append(f"⚠️  {late_ratio*100:.0f}% are late converters (7dc vs 1dc gap)")
            if cnt_1dv > 0 and cnt_7dc > 0:
                view_ratio = cnt_1dv / (cnt_7dc + cnt_1dv)
                if view_ratio > 0.30:
                    flags.append(f"⚠️  View-through is {view_ratio*100:.0f}% of reported conversions — may inflate results")

            print(f"    {label:<22}  {cnt_7dc_str:>9}  {cnt_1dc_str:>9}  {cnt_1dv_str:>8}  {val_str:>10}  {cpa_str:>8}  {roas_str:>6}{delta_str}")
            for flag in flags:
                print(f"    {' '*22}  {flag}")

    print_section(primary, "PRIMARY CONVERSIONS (used for bid optimization)")
    print_section(funnel,  "FUNNEL METRICS (informational)")


def print_campaign_breakdown(campaigns, prior_campaigns=None):
    if not campaigns:
        return

    prior_map = {c["name"]: c for c in (prior_campaigns or [])}

    print(f"\n    CAMPAIGN BREAKDOWN")
    print(f"    {'Campaign':<35}  {'Spend':>8}  {'Purchases':>9}  {'Leads':>6}  {'Revenue':>10}  {'ROAS':>6}  {'CPA':>8}")
    print(f"    {'─'*35}  {'─'*8}  {'─'*9}  {'─'*6}  {'─'*10}  {'─'*6}  {'─'*8}")

    for camp in campaigns:
        spend    = camp["spend"]
        actions  = camp["actions"]
        name     = camp["name"][:35]

        purchases = sum(v.get("7d_click", 0) for k, v in actions.items() if v["category"] == "purchase")
        leads     = sum(v.get("7d_click", 0) for k, v in actions.items() if v["category"] == "lead")
        revenue   = sum(v.get("value", 0)    for k, v in actions.items() if v["category"] == "purchase")

        all_results = purchases + leads
        roas = revenue / spend if spend > 0 and revenue > 0 else None
        cpa  = spend / all_results if all_results > 0 else None

        prior = prior_map.get(camp["name"], {})
        prior_spend = prior.get("spend", 0)
        spend_delta = fmt_delta(spend, prior_spend) if prior_spend else ""

        spend_str = f"${spend:.2f}"
        purch_str = f"{purchases:.0f}"
        lead_str  = f"{leads:.0f}"
        rev_str   = f"${revenue:,.2f}" if revenue > 0 else "—"
        roas_str  = f"{roas:.2f}x"     if roas        else "—"
        cpa_str   = f"${cpa:.2f}"      if cpa         else "—"

        print(f"    {name:<35}  {spend_str:>8}  {purch_str:>9}  {lead_str:>6}  {rev_str:>10}  {roas_str:>6}  {cpa_str:>8}{spend_delta}")


def print_account(client_name, account_id, curr, prior, by_campaign, prior_campaigns):
    spend       = curr["spend"]
    actions     = curr["actions"]
    prior_acts  = (prior or {}).get("actions", {})

    prior_spend = (prior or {}).get("spend", 0)
    spend_delta = fmt_delta(spend, prior_spend)

    # Account header
    total_purchases = sum(v.get("7d_click", 0) for v in actions.values() if v["category"] == "purchase")
    total_leads     = sum(v.get("7d_click", 0) for v in actions.values() if v["category"] == "lead")
    total_revenue   = sum(v.get("value", 0)    for v in actions.values() if v["category"] == "purchase")
    total_results   = total_purchases + total_leads
    acct_roas = total_revenue / spend if spend > 0 and total_revenue > 0 else None
    acct_cpa  = spend / total_results if total_results > 0 else None

    issues = []
    if spend > 100 and total_results == 0:
        issues.append("🚨  ZERO conversions with >${:.0f} spend — check pixel and campaign setup.".format(spend))

    roas_str = f"{acct_roas:.2f}x" if acct_roas else "—"
    cpa_str  = f"${acct_cpa:.2f}"  if acct_cpa  else "—"

    status_icon = "🚨" if any("🚨" in i for i in issues) else ("⚠️ " if any("⚠️" in i for i in issues) else "➡️ ")

    print(f"\n{status_icon}  {client_name} ({account_id})")
    print(f"    Spend: ${spend:.2f}{spend_delta}  |  🛒 Purchases: {total_purchases:.0f}  |  📋 Leads: {total_leads:.0f}  |  Revenue: {'$' + f'{total_revenue:,.2f}' if total_revenue > 0 else '—'}  |  ROAS: {roas_str}  |  CPA: {cpa_str}")
    print(f"    Impressions: {curr['impressions']:,}  |  Clicks: {curr['clicks']:,}  |  Reach: {curr['reach']:,}")

    for issue in issues:
        print(f"    {issue}")

    print_conversion_table(actions, spend, prior_acts)

    if by_campaign:
        print_campaign_breakdown(curr.get("campaigns", []), prior_campaigns)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Meta conversion report — breakdown by action type, attribution window, and campaign"
    )
    parser.add_argument("--account",      help="Single ad account ID (e.g. act_XXXXXXX). Omit to run all clients.")
    parser.add_argument("--client-name",  help="Display name when using --account")
    parser.add_argument("--mode",         choices=["weekly", "monthly"], default="monthly",
                        help="weekly (7d) or monthly (30d). Default: monthly")
    parser.add_argument("--days",         type=int,
                        help="Rolling N-day window. Overrides --mode.")
    parser.add_argument("--start",        help="Custom range start YYYY-MM-DD.")
    parser.add_argument("--end",          help="Custom range end YYYY-MM-DD.")
    parser.add_argument("--by-campaign",  action="store_true",
                        help="Include per-campaign conversion breakdown")
    args = parser.parse_args()

    init_api()
    dates = get_date_ranges(mode=args.mode, days=args.days, start=args.start, end=args.end)

    if args.account:
        targets = {(args.client_name or args.account): args.account}
    else:
        targets = ALL_CLIENTS

    mode_label = f"{args.days}D" if args.days else ("CUSTOM" if args.start else args.mode.upper())
    print("\n" + "="*60)
    print(f"META CONVERSION REPORT — {mode_label}")
    print(f"{dates['label']}")
    print(f"Current:  {dates['curr_start']} -> {dates['curr_end']}")
    if dates["prior_start"]:
        print(f"Prior:    {dates['prior_start']} -> {dates['prior_end']}")
    else:
        print("Prior:    n/a (exact range, no comparison period)")
    print("Attribution windows: 7d click (primary)  |  1d click  |  1d view")
    print("="*60)

    errored = []

    curr_start:  str      = str(dates["curr_start"])
    curr_end:    str      = str(dates["curr_end"])
    prior_start: str | None = dates["prior_start"]
    prior_end:   str | None = dates["prior_end"]

    for name, account_id in targets.items():
        try:
            curr_data, curr_camps = pull_conversions(account_id, curr_start, curr_end)
            curr_data["campaigns"] = curr_camps

            prior_data     = None
            prior_camps    = []
            if prior_start and prior_end:
                prior_data, prior_camps = pull_conversions(account_id, str(prior_start), str(prior_end))

            print_account(name, account_id, curr_data, prior_data, args.by_campaign, prior_camps)
        except Exception as e:
            errored.append(name)
            print(f"\n❌  {name} ({account_id}) — Error: {e}")

    print("\n" + "="*60)
    print("Done.")
    if errored:
        print(f"Errored: {', '.join(errored)}")
    print("="*60)


if __name__ == "__main__":
    main()
