"""
Meta Full Audit
Purpose: Run a consolidated audit across all Meta monitoring modules for one ad account.
         Covers: Campaign performance snapshot, ad set breakdown, creative health,
                 daily pacing, account health, frequency, pixel, conversions,
                 and audience inventory.

         Saves a structured markdown report to clients/[client]/reports/.
         Run monthly or before any major strategic review.

Setup:
    Requires environment variables:
        META_APP_ID, META_APP_SECRET, META_ACCESS_TOKEN

    Install dependency:
        pip3 install facebook-business python-dotenv

Usage:
    python3 scripts/meta_full_audit.py --account act_XXXXXXX
    python3 scripts/meta_full_audit.py --account act_XXXXXXX --client-name "Acme Co"
    python3 scripts/meta_full_audit.py --account act_XXXXXXX --days 30
    python3 scripts/meta_full_audit.py --account act_XXXXXXX --days 30 --save

    --account       Ad account ID (e.g. act_1509969187799563)
    --client-name   Display name for the report header and file name
    --days          Lookback window in days (default: 30)
    --save          Save markdown report to clients/[client]/reports/

Changelog:
    2026-03-21  Initial version — consolidated audit across all 9 Meta modules
                with markdown save and executive summary.
"""

import argparse
import os
import sys
from datetime import date, datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adspixel import AdsPixel
from facebook_business.adobjects.customaudience import CustomAudience
from facebook_business.exceptions import FacebookRequestError

# ─── SETUP ────────────────────────────────────────────────────────────────────

def init_api():
    app_id  = os.environ.get("HOSKI_META_APP_ID") or os.environ.get("META_APP_ID")
    secret  = os.environ.get("HOSKI_META_APP_SECRET") or os.environ.get("META_APP_SECRET")
    token   = os.environ.get("HOSKI_META_ACCESS_TOKEN") or os.environ.get("META_ACCESS_TOKEN")
    missing = [k for k, v in {
        "META_APP_ID": app_id,
        "META_APP_SECRET": secret,
        "META_ACCESS_TOKEN": token,
    }.items() if not v]
    if missing:
        print(f"Missing environment variables: {', '.join(missing)}")
        sys.exit(1)
    FacebookAdsApi.init(app_id=app_id, app_secret=secret, access_token=token)


def get_date_range(days: int):
    end   = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    prior_end   = start - timedelta(days=1)
    prior_start = prior_end - timedelta(days=days - 1)
    return (
        start.strftime("%Y-%m-%d"),
        end.strftime("%Y-%m-%d"),
        prior_start.strftime("%Y-%m-%d"),
        prior_end.strftime("%Y-%m-%d"),
    )


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def delta_flag(curr: float, prior: float, higher_is_better: bool = True) -> str:
    if prior == 0:
        return "➡️ "
    pct = (curr - prior) / prior * 100
    if higher_is_better:
        if pct >= 10:  return f"✅ +{pct:.0f}%"
        if pct <= -10: return f"🚨 {pct:.0f}%"
        return f"➡️  {pct:+.0f}%"
    else:
        if pct <= -10: return f"✅ {pct:.0f}%"
        if pct >= 10:  return f"🚨 +{pct:.0f}%"
        return f"➡️  {pct:+.0f}%"


def fmt_currency(val: float) -> str:
    return f"${val:,.2f}"


def fmt_pct(val: float) -> str:
    return f"{val:.2f}%"


def safe_div(num: float, den: float, default: float = 0.0) -> float:
    return num / den if den > 0 else default


def fetch_insights(account: AdAccount, fields: list, level: str, since: str, until: str,
                   extra_params: dict | None = None) -> list:
    params: dict = {
        "level":      level,
        "time_range": {"since": since, "until": until},
        "limit":      500,
    }
    if extra_params:
        params.update(extra_params)
    try:
        return list(account.get_insights(fields=fields, params=params))
    except FacebookRequestError as e:
        print(f"    [API error at {level} level] {e.api_error_message()}")
        return []


# ─── MODULE 1: CAMPAIGN SNAPSHOT ──────────────────────────────────────────────

CAMP_FIELDS = [
    "campaign_id", "campaign_name", "objective",
    "impressions", "reach", "clicks", "ctr", "cpc",
    "spend", "frequency", "actions",
]


def run_campaign_snapshot(account: AdAccount, curr_start: str, curr_end: str,
                          prior_start: str, prior_end: str) -> tuple[list, list, dict]:
    curr_rows  = fetch_insights(account, CAMP_FIELDS, "campaign", curr_start, curr_end)
    prior_rows = fetch_insights(account, CAMP_FIELDS, "campaign", prior_start, prior_end)

    def parse(rows):
        out = {}
        for r in rows:
            actions = {a["action_type"]: float(a["value"]) for a in (r.get("actions") or [])}
            results = (
                actions.get("offsite_conversion.fb_pixel_purchase", 0) +
                actions.get("offsite_conversion.fb_pixel_lead", 0) +
                actions.get("leadgen_grouped", 0)
            )
            spend = float(r.get("spend", 0))
            out[r["campaign_id"]] = {
                "name":        r.get("campaign_name", ""),
                "objective":   r.get("objective", ""),
                "impressions": int(r.get("impressions", 0)),
                "reach":       int(r.get("reach", 0)),
                "clicks":      int(r.get("clicks", 0)),
                "ctr":         float(r.get("ctr", 0)),
                "cpc":         float(r.get("cpc", 0)),
                "spend":       spend,
                "frequency":   float(r.get("frequency", 0)),
                "results":     results,
                "cpa":         safe_div(spend, results),
            }
        return out

    curr  = parse(curr_rows)
    prior = parse(prior_rows)

    # Roll up totals
    totals: dict = {"spend": 0, "impressions": 0, "clicks": 0, "results": 0}
    for c in curr.values():
        totals["spend"]       += c["spend"]
        totals["impressions"] += c["impressions"]
        totals["clicks"]      += c["clicks"]
        totals["results"]     += c["results"]

    prior_totals: dict = {"spend": 0, "impressions": 0, "clicks": 0, "results": 0}
    for p in prior.values():
        prior_totals["spend"]       += p["spend"]
        prior_totals["impressions"] += p["impressions"]
        prior_totals["clicks"]      += p["clicks"]
        prior_totals["results"]     += p["results"]

    return list(curr.values()), list(prior.values()), {
        "curr": totals, "prior": prior_totals
    }


# ─── MODULE 2: CREATIVE HEALTH ────────────────────────────────────────────────

AD_FIELDS_CREATIVE = [
    "ad_id", "ad_name", "adset_name", "campaign_name",
    "impressions", "clicks", "ctr", "spend", "actions",
]


def run_creative_health(account: AdAccount, curr_start: str, curr_end: str) -> list:
    rows = fetch_insights(account, AD_FIELDS_CREATIVE, "ad", curr_start, curr_end)
    ads = []
    for r in rows:
        impr  = int(r.get("impressions", 0))
        ctr   = float(r.get("ctr", 0))
        spend = float(r.get("spend", 0))
        actions = {a["action_type"]: float(a["value"]) for a in (r.get("actions") or [])}
        results = (
            actions.get("offsite_conversion.fb_pixel_purchase", 0) +
            actions.get("offsite_conversion.fb_pixel_lead", 0) +
            actions.get("leadgen_grouped", 0)
        )
        dead = impr >= 1000 and ctr < 0.005
        ads.append({
            "id":       r.get("ad_id", ""),
            "name":     r.get("ad_name", ""),
            "campaign": r.get("campaign_name", ""),
            "adset":    r.get("adset_name", ""),
            "impr":     impr,
            "ctr":      ctr,
            "spend":    spend,
            "results":  results,
            "dead":     dead,
        })
    return sorted(ads, key=lambda x: x["spend"], reverse=True)


# ─── MODULE 3: FREQUENCY ──────────────────────────────────────────────────────

FREQ_FIELDS = [
    "campaign_id", "campaign_name",
    "impressions", "reach", "frequency", "clicks", "ctr", "spend",
]


def run_frequency(account: AdAccount, curr_start: str, curr_end: str, window_days: int) -> list:
    rows = fetch_insights(account, FREQ_FIELDS, "campaign", curr_start, curr_end)
    result = []
    for r in rows:
        freq = float(r.get("frequency", 0))
        if freq == 0:
            continue
        scale = window_days / 7
        if freq >= 6.0 * scale:
            tier = ("🚨", "CRITICAL")
        elif freq >= 4.0 * scale:
            tier = ("⚠️ ", "WARNING")
        elif freq >= 2.5 * scale:
            tier = ("💡", "MONITOR")
        else:
            tier = ("✅", "HEALTHY")
        result.append({
            "name":      r.get("campaign_name", ""),
            "frequency": freq,
            "reach":     int(r.get("reach", 0)),
            "ctr":       float(r.get("ctr", 0)),
            "spend":     float(r.get("spend", 0)),
            "icon":      tier[0],
            "tier":      tier[1],
        })
    return sorted(result, key=lambda x: x["frequency"], reverse=True)


# ─── MODULE 4: PIXEL HEALTH ───────────────────────────────────────────────────

def run_pixel_health(account: AdAccount) -> list:
    try:
        pixels = list(account.get_ads_pixels(fields=["id", "name", "last_fired_time"]))
    except FacebookRequestError:
        return []

    summary = []
    for px in pixels:
        last_fired = px.get("last_fired_time", "")
        if last_fired:
            try:
                fired_dt = datetime.fromisoformat(last_fired.replace("Z", "+00:00")).date()
                days_ago = (date.today() - fired_dt).days
                if days_ago == 0:
                    status = ("✅", "Fired today")
                elif days_ago <= 3:
                    status = ("✅", f"Fired {days_ago}d ago")
                elif days_ago <= 14:
                    status = ("⚠️ ", f"Fired {days_ago}d ago — check activity")
                else:
                    status = ("🚨", f"Last fired {days_ago}d ago — may be broken")
            except (ValueError, TypeError):
                status = ("➡️ ", "Unknown last fire time")
        else:
            status = ("🚨", "Never fired or no data")

        summary.append({
            "id":     px.get("id", ""),
            "name":   px.get("name", "Unknown Pixel"),
            "last":   last_fired[:10] if last_fired else "Never",
            "icon":   status[0],
            "detail": status[1],
        })
    return summary


# ─── MODULE 5: CONVERSION SUMMARY ─────────────────────────────────────────────

ACTION_LABELS: dict = {
    "offsite_conversion.fb_pixel_purchase": "Purchase (pixel)",
    "purchase":                             "Purchase",
    "offsite_conversion.fb_pixel_lead":     "Lead (pixel)",
    "lead":                                 "Lead",
    "offsite_conversion.fb_pixel_add_to_cart": "Add to Cart",
    "offsite_conversion.fb_pixel_initiate_checkout": "Initiate Checkout",
    "offsite_conversion.fb_pixel_view_content": "View Content",
    "complete_registration":                "Registration",
    "contact":                              "Contact",
    "schedule":                             "Schedule",
    "submit_application":                   "Application",
    "link_click":                           "Link Click",
    "post_engagement":                      "Post Engagement",
    "page_engagement":                      "Page Engagement",
}


def run_conversion_summary(account: AdAccount, curr_start: str, curr_end: str) -> dict:
    fields = ["actions", "spend", "impressions"]
    rows   = fetch_insights(account, fields, "account", curr_start, curr_end)
    totals: dict = {}
    spend  = 0.0
    impr   = 0

    for r in rows:
        spend += float(r.get("spend", 0))
        impr  += int(r.get("impressions", 0))
        for a in (r.get("actions") or []):
            key   = a["action_type"]
            label = ACTION_LABELS.get(key, key)
            totals[label] = totals.get(label, 0.0) + float(a["value"])

    return {"actions": totals, "spend": spend, "impressions": impr}


# ─── MODULE 6: AUDIENCE INVENTORY ─────────────────────────────────────────────

AUDIENCE_SUBTYPES = {
    "WEBSITE":       "Website (retargeting)",
    "LIST":          "Customer list",
    "LOOKALIKE":     "Lookalike",
    "ENGAGEMENT":    "Engagement",
    "APP":           "App activity",
    "OFFLINE":       "Offline events",
    "CUSTOM_COMBINATION": "Custom combination",
}


def run_audience_inventory(account: AdAccount) -> list:
    try:
        audiences = list(account.get_custom_audiences(fields=[
            "id", "name", "subtype", "approximate_count_lower_bound",
            "approximate_count_upper_bound", "time_updated",
        ]))
    except FacebookRequestError:
        return []

    result = []
    for a in audiences:
        subtype  = a.get("subtype", "UNKNOWN")
        label    = AUDIENCE_SUBTYPES.get(subtype, subtype.title())
        lo       = int(a.get("approximate_count_lower_bound", 0) or 0)
        hi       = int(a.get("approximate_count_upper_bound", 0) or 0)
        updated  = a.get("time_updated", "")
        if lo == 0:
            size_str = "Too small / < 1K"
            size_ok  = False
        elif lo >= 1_000_000:
            size_str = f"{lo/1_000_000:.1f}M-{hi/1_000_000:.1f}M"
            size_ok  = True
        elif lo >= 1_000:
            size_str = f"{lo/1_000:.0f}K-{hi/1_000:.0f}K"
            size_ok  = True
        else:
            size_str = f"{lo:,}-{hi:,}"
            size_ok  = lo >= 300

        result.append({
            "id":       a.get("id", ""),
            "name":     a.get("name", ""),
            "subtype":  label,
            "size":     size_str,
            "size_ok":  size_ok,
            "updated":  updated[:10] if updated else "Unknown",
        })

    return sorted(result, key=lambda x: x["subtype"])


# ─── ACCOUNT INFO ─────────────────────────────────────────────────────────────

def get_account_info(account_id: str) -> dict:
    try:
        acct = AdAccount(account_id)
        info = acct.api_get(fields=[
            "name", "account_status", "currency", "timezone_name",
            "spend_cap", "amount_spent",
        ])
        status_map = {1: "Active", 2: "Disabled", 3: "Unsettled", 7: "Pending Review",
                      8: "Pending Closure", 9: "In Grace Period", 100: "Temporarily Unavailable",
                      101: "Pending Closure", 201: "Closed"}
        code = info.get("account_status", 0)
        return {
            "name":      info.get("name", account_id),
            "status":    status_map.get(code, f"Unknown ({code})"),
            "currency":  info.get("currency", ""),
            "timezone":  info.get("timezone_name", ""),
            "spend_cap": float(info.get("spend_cap", 0) or 0) / 100,
            "spent":     float(info.get("amount_spent", 0) or 0) / 100,
        }
    except FacebookRequestError:
        return {"name": account_id, "status": "Unknown", "currency": "", "timezone": "",
                "spend_cap": 0.0, "spent": 0.0}


# ─── PRINT ────────────────────────────────────────────────────────────────────

def print_section(title: str, index: int):
    print(f"\n{'='*60}")
    print(f"{index}. {title}")
    print("="*60)


# ─── MARKDOWN ─────────────────────────────────────────────────────────────────

def build_markdown(
    account_id: str, client_name: str, days: int,
    curr_start: str, curr_end: str,
    prior_start: str, prior_end: str,
    account_info: dict,
    campaigns: list, prior_campaigns: list, totals: dict,
    creatives: list,
    frequency: list,
    pixels: list,
    conversions: dict,
    audiences: list,
) -> str:
    today      = date.today().strftime("%Y-%m-%d")
    prior_ctr  = totals["prior"]
    curr_ctr   = totals["curr"]

    lines = [
        f"# Meta Ads Full Audit: {client_name}",
        f"",
        f"**Account:** {account_id}  ",
        f"**Date:** {today}  ",
        f"**Period:** {curr_start} to {curr_end} ({days} days)  ",
        f"**Prior period:** {prior_start} to {prior_end}  ",
        f"",
        "---",
        "",
        "## Account Overview",
        "",
        f"| Field | Value |",
        f"|---|---|",
        f"| Status | {account_info['status']} |",
        f"| Currency | {account_info['currency']} |",
        f"| Timezone | {account_info['timezone']} |",
    ]
    if account_info["spend_cap"] > 0:
        pct = safe_div(account_info["spent"], account_info["spend_cap"]) * 100
        lines.append(f"| Lifetime spend cap | {fmt_currency(account_info['spent'])} / {fmt_currency(account_info['spend_cap'])} ({pct:.0f}%) |")

    lines += [
        "",
        "---",
        "",
        "## 1. Performance Summary",
        "",
        f"| Metric | Current ({days}d) | Prior ({days}d) | Change |",
        f"|---|---|---|---|",
        f"| Spend | {fmt_currency(curr_ctr['spend'])} | {fmt_currency(prior_ctr['spend'])} | {delta_flag(curr_ctr['spend'], prior_ctr['spend'], False)} |",
        f"| Impressions | {curr_ctr['impressions']:,} | {prior_ctr['impressions']:,} | {delta_flag(curr_ctr['impressions'], prior_ctr['impressions'])} |",
        f"| Clicks | {curr_ctr['clicks']:,} | {prior_ctr['clicks']:,} | {delta_flag(curr_ctr['clicks'], prior_ctr['clicks'])} |",
        f"| Results | {curr_ctr['results']:.0f} | {prior_ctr['results']:.0f} | {delta_flag(curr_ctr['results'], prior_ctr['results'])} |",
    ]

    if prior_ctr["spend"] > 0 and prior_ctr["results"] > 0:
        curr_cpa  = safe_div(curr_ctr["spend"], curr_ctr["results"])
        prior_cpa = safe_div(prior_ctr["spend"], prior_ctr["results"])
        lines.append(f"| CPA | {fmt_currency(curr_cpa)} | {fmt_currency(prior_cpa)} | {delta_flag(curr_cpa, prior_cpa, False)} |")

    lines += ["", "---", "", "## 2. Campaign Breakdown", ""]
    if campaigns:
        lines.append("| Campaign | Spend | Impressions | Clicks | CTR | Freq | Results | CPA |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for c in sorted(campaigns, key=lambda x: x["spend"], reverse=True):
            lines.append(
                f"| {c['name'][:40]} | {fmt_currency(c['spend'])} | {c['impressions']:,} | "
                f"{c['clicks']:,} | {fmt_pct(c['ctr'])} | {c['frequency']:.1f} | "
                f"{c['results']:.0f} | {fmt_currency(c['cpa']) if c['results'] > 0 else 'N/A'} |"
            )
    else:
        lines.append("_No campaign data in this period._")

    lines += ["", "---", "", "## 3. Creative Health", ""]
    dead_ads = [a for a in creatives if a["dead"]]
    if dead_ads:
        lines.append(f"**{len(dead_ads)} dead creative(s) detected** (1,000+ impr, CTR < 0.5%)\n")
        lines.append("| Ad | Campaign | Impressions | CTR | Spend |")
        lines.append("|---|---|---|---|---|")
        for a in dead_ads[:10]:
            lines.append(f"| {a['name'][:40]} | {a['campaign'][:30]} | {a['impr']:,} | {fmt_pct(a['ctr'])} | {fmt_currency(a['spend'])} |")
    else:
        lines.append("No dead creatives detected.")

    if creatives:
        lines += ["", "**Top 5 ads by spend:**", ""]
        lines.append("| Ad | Spend | CTR | Results |")
        lines.append("|---|---|---|---|")
        for a in creatives[:5]:
            lines.append(f"| {a['name'][:40]} | {fmt_currency(a['spend'])} | {fmt_pct(a['ctr'])} | {a['results']:.0f} |")

    lines += ["", "---", "", "## 4. Frequency", ""]
    if frequency:
        lines.append("| Campaign | Frequency | Reach | CTR | Spend | Status |")
        lines.append("|---|---|---|---|---|---|")
        for f in frequency:
            lines.append(
                f"| {f['name'][:40]} | {f['frequency']:.1f} | {f['reach']:,} | "
                f"{fmt_pct(f['ctr'])} | {fmt_currency(f['spend'])} | {f['icon']} {f['tier']} |"
            )
        flagged = [f for f in frequency if f["tier"] in ("WARNING", "CRITICAL")]
        if flagged:
            lines.append(f"\n**Action required:** {len(flagged)} campaign(s) need creative rotation.")
    else:
        lines.append("_No frequency data._")

    lines += ["", "---", "", "## 5. Pixel Health", ""]
    if pixels:
        lines.append("| Pixel | Last Fired | Status |")
        lines.append("|---|---|---|")
        for px in pixels:
            lines.append(f"| {px['name']} (ID: {px['id']}) | {px['last']} | {px['icon']} {px['detail']} |")
    else:
        lines.append("_No pixels found or access denied._")

    lines += ["", "---", "", "## 6. Conversions", ""]
    if conversions["actions"]:
        lines.append("| Conversion Type | Count |")
        lines.append("|---|---|")
        for label, count in sorted(conversions["actions"].items(), key=lambda x: -x[1]):
            lines.append(f"| {label} | {count:.0f} |")
    else:
        lines.append("_No conversion data in this period._")

    lines += ["", "---", "", "## 7. Audience Inventory", ""]
    if audiences:
        lines.append("| Audience | Type | Size | Last Updated |")
        lines.append("|---|---|---|---|")
        for a in audiences:
            size_icon = "✅" if a["size_ok"] else "⚠️ "
            lines.append(f"| {a['name'][:45]} | {a['subtype']} | {size_icon} {a['size']} | {a['updated']} |")
    else:
        lines.append("_No custom audiences found._")

    # Executive summary flags
    issues = []
    if pixels and any(px["icon"] == "🚨" for px in pixels):
        issues.append("Pixel not firing correctly")
    dead_count = len([a for a in creatives if a["dead"]])
    if dead_count:
        issues.append(f"{dead_count} dead creative(s) pulling spend")
    freq_flagged = [f for f in frequency if f["tier"] in ("WARNING", "CRITICAL")]
    if freq_flagged:
        issues.append(f"{len(freq_flagged)} campaign(s) at high frequency — creative fatigue risk")
    if curr_ctr["results"] == 0 and curr_ctr["spend"] > 0:
        issues.append("No conversions recorded — check pixel and conversion events")

    lines += ["", "---", "", "## Executive Summary", ""]
    if issues:
        lines.append("**Issues requiring attention:**\n")
        for issue in issues:
            lines.append(f"- {issue}")
    else:
        lines.append("No critical issues detected. Continue monitoring frequency and creative performance.")

    lines += [
        "",
        "---",
        f"_Generated by meta_full_audit.py on {today}_",
        "",
    ]

    return "\n".join(lines)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Meta full account audit — consolidated report across all monitoring modules"
    )
    parser.add_argument("--account",     required=True, help="Ad account ID (e.g. act_1509969187799563)")
    parser.add_argument("--client-name", default="",    help="Display name for headers and file name")
    parser.add_argument("--days",        type=int, default=30, help="Lookback window in days (default: 30)")
    parser.add_argument("--save",        action="store_true",  help="Save report to clients/[client]/reports/")
    args = parser.parse_args()

    account_id  = args.account if args.account.startswith("act_") else f"act_{args.account}"
    client_name = args.client_name or account_id
    days        = args.days

    init_api()

    curr_start, curr_end, prior_start, prior_end = get_date_range(days)
    account = AdAccount(account_id)

    print("\n" + "="*60)
    print(f"META FULL AUDIT: {client_name} ({account_id})")
    print(f"Period: {curr_start} to {curr_end} ({days} days)")
    print(f"Prior:  {prior_start} to {prior_end}")
    print("="*60)

    # ── Account info
    print_section("ACCOUNT INFO", 0)
    account_info = get_account_info(account_id)
    print(f"  Name:     {account_info['name']}")
    print(f"  Status:   {account_info['status']}")
    print(f"  Currency: {account_info['currency']}  |  Timezone: {account_info['timezone']}")
    if account_info["spend_cap"] > 0:
        pct = safe_div(account_info["spent"], account_info["spend_cap"]) * 100
        print(f"  Spend cap: {fmt_currency(account_info['spent'])} / {fmt_currency(account_info['spend_cap'])} ({pct:.0f}%)")

    # ── Campaigns
    print_section("CAMPAIGN SNAPSHOT", 1)
    campaigns, prior_campaigns, totals = run_campaign_snapshot(
        account, curr_start, curr_end, prior_start, prior_end
    )
    curr_t  = totals["curr"]
    prior_t = totals["prior"]
    print(f"\n  {'Metric':<18} {'Current':>12}  {'Prior':>12}  Change")
    print(f"  {'─'*18} {'─'*12}  {'─'*12}  {'─'*12}")
    print(f"  {'Spend':<18} {fmt_currency(curr_t['spend']):>12}  {fmt_currency(prior_t['spend']):>12}  {delta_flag(curr_t['spend'], prior_t['spend'], False)}")
    print(f"  {'Impressions':<18} {curr_t['impressions']:>12,}  {prior_t['impressions']:>12,}  {delta_flag(curr_t['impressions'], prior_t['impressions'])}")
    print(f"  {'Clicks':<18} {curr_t['clicks']:>12,}  {prior_t['clicks']:>12,}  {delta_flag(curr_t['clicks'], prior_t['clicks'])}")
    print(f"  {'Results':<18} {curr_t['results']:>12.0f}  {prior_t['results']:>12.0f}  {delta_flag(curr_t['results'], prior_t['results'])}")

    print(f"\n  {'Campaign':<40} {'Spend':>10}  {'CTR':>6}  {'Freq':>5}  {'Results':>8}")
    print(f"  {'─'*40} {'─'*10}  {'─'*6}  {'─'*5}  {'─'*8}")
    for c in sorted(campaigns, key=lambda x: x["spend"], reverse=True):
        print(f"  {c['name'][:40]:<40} {fmt_currency(c['spend']):>10}  {fmt_pct(c['ctr']):>6}  {c['frequency']:>5.1f}  {c['results']:>8.0f}")

    # ── Creative health
    print_section("CREATIVE HEALTH", 2)
    creatives = run_creative_health(account, curr_start, curr_end)
    dead_ads  = [a for a in creatives if a["dead"]]
    print(f"\n  Total ads with data: {len(creatives)}  |  Dead creatives: {len(dead_ads)}")
    if dead_ads:
        print(f"\n  DEAD CREATIVES (1K+ impr, CTR < 0.5%):")
        for a in dead_ads[:10]:
            print(f"    🚨 {a['name'][:45]}  CTR: {fmt_pct(a['ctr'])}  Spend: {fmt_currency(a['spend'])}")
    print(f"\n  Top 5 ads by spend:")
    for a in creatives[:5]:
        icon = "⚠️ " if a["dead"] else "  "
        print(f"    {icon}{a['name'][:45]}  {fmt_currency(a['spend'])}  CTR: {fmt_pct(a['ctr'])}  Results: {a['results']:.0f}")

    # ── Frequency
    print_section("FREQUENCY", 3)
    frequency = run_frequency(account, curr_start, curr_end, days)
    if frequency:
        for f in frequency:
            print(f"  {f['icon']} {f['name'][:42]}  Freq: {f['frequency']:.1f}  Reach: {f['reach']:,}  CTR: {fmt_pct(f['ctr'])}  [{f['tier']}]")
    else:
        print("  No frequency data.")

    # ── Pixel health
    print_section("PIXEL HEALTH", 4)
    pixels = run_pixel_health(account)
    if pixels:
        for px in pixels:
            print(f"  {px['icon']} {px['name']} (ID: {px['id']})")
            print(f"       Last fired: {px['last']}  |  {px['detail']}")
    else:
        print("  No pixels found or access denied.")

    # ── Conversion summary
    print_section("CONVERSION SUMMARY", 5)
    conversions = run_conversion_summary(account, curr_start, curr_end)
    print(f"\n  Spend: {fmt_currency(conversions['spend'])}  |  Impressions: {conversions['impressions']:,}")
    if conversions["actions"]:
        print(f"\n  {'Conversion Type':<40} {'Count':>8}")
        print(f"  {'─'*40} {'─'*8}")
        for label, count in sorted(conversions["actions"].items(), key=lambda x: -x[1]):
            print(f"  {label:<40} {count:>8.0f}")
    else:
        print("  No conversion events in this period.")

    # ── Audience inventory
    print_section("AUDIENCE INVENTORY", 6)
    audiences = run_audience_inventory(account)
    if audiences:
        print(f"\n  Total custom audiences: {len(audiences)}")
        small = [a for a in audiences if not a["size_ok"]]
        if small:
            print(f"  Audiences too small to target: {len(small)}")
        print(f"\n  {'Audience':<45} {'Type':<22} {'Size'}")
        print(f"  {'─'*45} {'─'*22} {'─'*15}")
        for a in audiences[:20]:
            icon = "✅" if a["size_ok"] else "⚠️ "
            print(f"  {a['name'][:45]:<45} {a['subtype']:<22} {icon} {a['size']}")
    else:
        print("  No custom audiences found or access denied.")

    # ── Issues summary
    print(f"\n{'='*60}")
    print("EXECUTIVE SUMMARY")
    print("="*60)
    issues = []
    if pixels and any(px["icon"] == "🚨" for px in pixels):
        issues.append("🚨 Pixel not firing correctly — conversion data unreliable")
    if dead_ads:
        issues.append(f"⚠️  {len(dead_ads)} dead creative(s) pulling spend — pause or refresh")
    freq_flagged = [f for f in frequency if f["tier"] in ("WARNING", "CRITICAL")]
    if freq_flagged:
        issues.append(f"⚠️  {len(freq_flagged)} campaign(s) at high frequency — creative fatigue risk")
    if curr_t["results"] == 0 and curr_t["spend"] > 0:
        issues.append("🚨 No conversions recorded — check pixel and event setup")
    if curr_t["spend"] > 0 and prior_t["spend"] > 0:
        spend_delta = safe_div(curr_t["spend"] - prior_t["spend"], prior_t["spend"]) * 100
        if spend_delta >= 30:
            issues.append(f"💡 Spend up {spend_delta:.0f}% vs prior period — monitor efficiency")

    if issues:
        for issue in issues:
            print(f"  {issue}")
    else:
        print("  No critical issues. Continue monitoring frequency and creative performance.")
    print("="*60)

    # ── Save
    if args.save:
        md = build_markdown(
            account_id, client_name, days,
            curr_start, curr_end, prior_start, prior_end,
            account_info,
            campaigns, prior_campaigns, totals,
            creatives,
            frequency,
            pixels,
            conversions,
            audiences,
        )

        safe_name   = client_name.replace(" ", "_").replace("/", "-")
        report_dir  = os.path.join("clients", f"{client_name} ({account_id})", "reports")
        os.makedirs(report_dir, exist_ok=True)
        filename    = f"meta_full_audit_{safe_name}_{curr_end}.md"
        output_path = os.path.join(report_dir, filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    main()
