"""
Meta Frequency Monitor
Purpose: Track ad frequency across campaigns and ad sets to identify creative
         fatigue before it kills CTR and drives up CPM. Shows frequency by
         campaign, ad set, and individual ad, with urgency tiers and action
         recommendations.

         Frequency is the average number of times a unique person has seen
         your ad in the reporting window. High frequency = audience saturation.

         Run weekly as part of the creative refresh workflow.

Setup:
    Requires environment variables:
        META_APP_ID, META_APP_SECRET, META_ACCESS_TOKEN

    Install dependency:
        pip3 install facebook-business python-dotenv

Usage:
    python3 scripts/meta_frequency_monitor.py                          # all clients, last 7 days
    python3 scripts/meta_frequency_monitor.py --days 14                # last 14 days
    python3 scripts/meta_frequency_monitor.py --days 30                # last 30 days
    python3 scripts/meta_frequency_monitor.py --account act_XXXXXXX   # single account
    python3 scripts/meta_frequency_monitor.py --warn-only              # only show flagged ad sets

Frequency Thresholds (7-day window):
    ✅ HEALTHY    < 2.5    Good reach-to-frequency balance
    💡 MONITOR    2.5-3.9  Watch for CTR decline
    ⚠️  WARNING    4.0-5.9  Creative fatigue likely — plan rotation
    🚨 CRITICAL   >= 6.0   Audience saturated — refresh immediately

    Note: Thresholds scale with window length. A 30-day frequency of 8.0
    is less alarming than a 7-day frequency of 8.0. The script adjusts
    labels accordingly when using --days.

Changelog:
    2026-03-21  Initial version — campaign, ad set, and ad level frequency
                with urgency tiers, CTR correlation, and action recommendations.
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


# ─── FREQUENCY TIERS ─────────────────────────────────────────────────────────

def get_freq_tier(freq, window_days):
    """
    Return (icon, label, action) for a given frequency value.
    Thresholds scale with window length to avoid false alarms on longer windows.
    """
    # Scale thresholds: 7-day baseline, scale linearly with window
    scale = window_days / 7

    warn_floor = 4.0 * scale
    crit_floor = 6.0 * scale
    mon_floor  = 2.5 * scale

    if freq >= crit_floor:
        return ("🚨", "CRITICAL", "Refresh creative immediately — audience is saturated")
    elif freq >= warn_floor:
        return ("⚠️ ", "WARNING", "Plan creative rotation within 1-2 weeks")
    elif freq >= mon_floor:
        return ("💡", "MONITOR", "Watch CTR trend — rotation coming soon")
    else:
        return ("✅", "HEALTHY", "Frequency is within healthy range")


# ─── PULL ─────────────────────────────────────────────────────────────────────

CAMP_FIELDS = [
    "campaign_id", "campaign_name", "objective",
    "impressions", "reach", "frequency",
    "clicks", "ctr", "spend",
    "actions",
]

ADSET_FIELDS = [
    "adset_id", "adset_name", "campaign_name",
    "impressions", "reach", "frequency",
    "clicks", "ctr", "spend",
]

AD_FIELDS = [
    "ad_id", "ad_name", "adset_name", "campaign_name",
    "impressions", "reach", "frequency",
    "clicks", "ctr", "spend",
]


def pull_frequency_data(account_id, start, end):
    """
    Pull frequency at campaign, ad set, and ad level.
    Returns (campaigns, adsets, ads) — each a list of dicts sorted by frequency desc.
    """
    account = AdAccount(account_id)

    def fetch(fields, level):
        try:
            return list(account.get_insights(
                fields=fields,
                params={
                    "level":      level,
                    "time_range": {"since": start, "until": end},
                    "limit":      500,
                }
            ))
        except FacebookRequestError as e:
            print(f"    [API Error at {level} level] {e.api_error_message()}")
            return []

    def parse_row(row, id_key, name_key):
        actions = {a["action_type"]: float(a["value"]) for a in (row.get("actions") or [])}
        results = (actions.get("offsite_conversion.fb_pixel_purchase", 0) +
                   actions.get("purchase", 0) +
                   actions.get("lead", 0) +
                   actions.get("offsite_conversion.fb_pixel_lead", 0))
        spend   = float(row.get("spend", 0))
        freq    = float(row.get("frequency", 0))
        ctr     = float(row.get("ctr", 0))
        impr    = int(row.get("impressions", 0))
        reach   = int(row.get("reach", 0))

        return {
            "id":            row.get(id_key, ""),
            "name":          row.get(name_key, ""),
            "campaign_name": row.get("campaign_name", ""),
            "adset_name":    row.get("adset_name", ""),
            "objective":     row.get("objective", ""),
            "frequency":     freq,
            "impressions":   impr,
            "reach":         reach,
            "ctr":           ctr,
            "spend":         spend,
            "results":       results,
            "cpa":           spend / results if results > 0 else None,
        }

    raw_camps  = fetch(CAMP_FIELDS,  "campaign")
    raw_adsets = fetch(ADSET_FIELDS, "adset")
    raw_ads    = fetch(AD_FIELDS,    "ad")

    campaigns = sorted(
        [parse_row(r, "campaign_id", "campaign_name") for r in raw_camps  if float(r.get("frequency", 0)) > 0],
        key=lambda x: x["frequency"], reverse=True
    )
    adsets = sorted(
        [parse_row(r, "adset_id", "adset_name")       for r in raw_adsets if float(r.get("frequency", 0)) > 0],
        key=lambda x: x["frequency"], reverse=True
    )
    ads = sorted(
        [parse_row(r, "ad_id", "ad_name")             for r in raw_ads    if float(r.get("frequency", 0)) > 0],
        key=lambda x: x["frequency"], reverse=True
    )

    return campaigns, adsets, ads


# ─── PRINT ────────────────────────────────────────────────────────────────────

def freq_bar(freq, window_days):
    """Visual frequency bar: each block = 0.5 frequency."""
    blocks  = int(freq / 0.5)
    scale   = window_days / 7
    warn_bl = int(4.0 * scale / 0.5)
    crit_bl = int(6.0 * scale / 0.5)
    bar     = ""
    for i in range(min(blocks, 30)):
        if i >= crit_bl:
            bar += "█"
        elif i >= warn_bl:
            bar += "▓"
        else:
            bar += "░"
    return bar


def print_account(client_name, account_id, campaigns, adsets, ads, window_days, warn_only):
    if not campaigns and not adsets:
        print(f"\n⬜  {client_name} ({account_id}) — No frequency data in this period")
        return {"critical": 0, "warning": 0, "monitor": 0, "healthy": 0}

    counts: dict = {"critical": 0, "warning": 0, "monitor": 0, "healthy": 0}

    # Account-level frequency summary
    if campaigns:
        avg_freq   = sum(c["frequency"] for c in campaigns) / len(campaigns)
        max_camp   = campaigns[0]
        icon, label, _ = get_freq_tier(avg_freq, window_days)
        print(f"\n{icon}  {client_name} ({account_id})")
        print(f"    Avg campaign frequency: {avg_freq:.1f}  |  Highest: {max_camp['frequency']:.1f} ({max_camp['name'][:40]})")
    else:
        print(f"\n➡️   {client_name} ({account_id})")

    # Campaign level
    print(f"\n    CAMPAIGN FREQUENCY")
    print(f"    {'Freq':>6}  {'Reach':>8}  {'CTR':>6}  {'Spend':>8}  Status    Campaign")
    print(f"    {'─'*6}  {'─'*8}  {'─'*6}  {'─'*8}  {'─'*8}  {'─'*30}")

    for camp in campaigns:
        icon, label, action = get_freq_tier(camp["frequency"], window_days)
        s = label.lower()
        if s in counts:
            counts[s] += 1

        if warn_only and label in ("HEALTHY", "MONITOR"):
            continue

        ctr_str   = f"{camp['ctr']:.2f}%"
        spend_str = f"${camp['spend']:.2f}"
        reach_str = f"{camp['reach']:,}"
        bar       = freq_bar(camp["frequency"], window_days)
        print(f"    {camp['frequency']:>6.1f}  {reach_str:>8}  {ctr_str:>6}  {spend_str:>8}  {icon} {label:<8}  {camp['name'][:40]}")
        print(f"           {bar}")

    # Ad set level — only show flagged ones to keep output manageable
    flagged_adsets = [a for a in adsets if get_freq_tier(a["frequency"], window_days)[1] in ("WARNING", "CRITICAL")]

    if flagged_adsets:
        print(f"\n    FLAGGED AD SETS ({len(flagged_adsets)} of {len(adsets)} need attention)")
        print(f"    {'Freq':>6}  {'Reach':>8}  {'CTR':>6}  {'Spend':>8}  Status    Ad Set")
        print(f"    {'─'*6}  {'─'*8}  {'─'*6}  {'─'*8}  {'─'*8}  {'─'*30}")
        for adset in flagged_adsets:
            icon, label, action = get_freq_tier(adset["frequency"], window_days)
            ctr_str   = f"{adset['ctr']:.2f}%"
            spend_str = f"${adset['spend']:.2f}"
            reach_str = f"{adset['reach']:,}"
            bar       = freq_bar(adset["frequency"], window_days)
            print(f"    {adset['frequency']:>6.1f}  {reach_str:>8}  {ctr_str:>6}  {spend_str:>8}  {icon} {label:<8}  {adset['name'][:40]}")
            print(f"           Campaign: {adset['campaign_name'][:50]}")
            print(f"           Action: {action}")
            print(f"           {bar}")
    elif not warn_only:
        print(f"\n    AD SETS: {len(adsets)} total — none flagged for frequency")

    # Ad level — only show critically saturated ads
    crit_ads = [a for a in ads if get_freq_tier(a["frequency"], window_days)[1] == "CRITICAL"]
    if crit_ads:
        print(f"\n    CRITICALLY SATURATED ADS ({len(crit_ads)})")
        for ad in crit_ads:
            icon, label, action = get_freq_tier(ad["frequency"], window_days)
            print(f"    🚨  {ad['name'][:50]}")
            print(f"         Freq: {ad['frequency']:.1f}  |  Reach: {ad['reach']:,}  |  CTR: {ad['ctr']:.2f}%  |  Spend: ${ad['spend']:.2f}")
            print(f"         Ad Set: {ad['adset_name'][:50]}")
            print(f"         {freq_bar(ad['frequency'], window_days)}")

    return counts


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Meta frequency monitor — creative fatigue detection by campaign and ad set"
    )
    parser.add_argument("--account",     help="Single ad account ID (e.g. act_XXXXXXX). Omit to run all clients.")
    parser.add_argument("--client-name", help="Display name when using --account")
    parser.add_argument("--days",        type=int, default=7,
                        help="Lookback window in days (default: 7). Common values: 7, 14, 30.")
    parser.add_argument("--warn-only",   action="store_true",
                        help="Only show campaigns and ad sets with WARNING or CRITICAL frequency")
    args = parser.parse_args()

    init_api()

    today     = date.today()
    end_date  = today - timedelta(days=1)
    start_date = end_date - timedelta(days=args.days - 1)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str   = end_date.strftime("%Y-%m-%d")

    # Scale thresholds for display
    scale      = args.days / 7
    warn_thresh = 4.0 * scale
    crit_thresh = 6.0 * scale

    if args.account:
        targets = {(args.client_name or args.account): args.account}
    else:
        targets = ALL_CLIENTS

    print("\n" + "="*60)
    print(f"META FREQUENCY MONITOR — {args.days}-DAY WINDOW")
    print(f"Period: {start_str} -> {end_str}")
    print(f"Thresholds: Monitor >{2.5*scale:.1f}  |  Warning >{warn_thresh:.1f}  |  Critical >{crit_thresh:.1f}")
    if args.warn_only:
        print("Mode: Flagged only")
    print("="*60)

    total_counts: dict = {"critical": 0, "warning": 0, "monitor": 0, "healthy": 0}
    errored = []

    for name, account_id in targets.items():
        try:
            campaigns, adsets, ads = pull_frequency_data(account_id, start_str, end_str)
            counts = print_account(name, account_id, campaigns, adsets, ads, args.days, args.warn_only)
            for k in total_counts:
                total_counts[k] += counts.get(k, 0)
        except Exception as e:
            errored.append(name)
            print(f"\n❌  {name} ({account_id}) — Error: {e}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  Accounts checked: {len(targets) - len(errored)}/{len(targets)}")
    print(f"  🚨 Critical (refresh now):     {total_counts['critical']} campaign(s)")
    print(f"  ⚠️  Warning (plan rotation):    {total_counts['warning']} campaign(s)")
    print(f"  💡 Monitor (watch CTR trend):   {total_counts['monitor']} campaign(s)")
    print(f"  ✅ Healthy:                     {total_counts['healthy']} campaign(s)")
    if errored:
        print(f"  ❌ Errored:                    {', '.join(errored)}")
    print("="*60)


if __name__ == "__main__":
    main()
