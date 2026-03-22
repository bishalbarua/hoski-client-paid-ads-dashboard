"""
Meta Campaign Performance Snapshot
Purpose: Period-over-period campaign performance table across all (or one) Meta
         ad accounts. Compares current vs prior period for all active campaigns
         and flags significant changes — drops, spikes, and wins.

         Conversion metrics pulled:
           - Purchases (and purchase value for ROAS)
           - Leads (lead gen forms, website leads)
           - All other results as reported by the campaign objective
         Reach, video views, post engagement, and other awareness metrics are
         shown separately and not counted as business conversions.

         Designed as the data layer for /facebook-ads-performance-analyzer and
         /monthly-report skills, and as a baseline feed for anomaly detection.

Setup:
    Requires environment variables:
        META_APP_ID, META_APP_SECRET, META_ACCESS_TOKEN

    Install dependency:
        pip3 install facebook-business python-dotenv

Usage:
    python3 scripts/meta_campaign_snapshot.py                                      # all clients, last 7 days vs prior 7 days
    python3 scripts/meta_campaign_snapshot.py --mode monthly                       # last 30 days vs prior 30 days
    python3 scripts/meta_campaign_snapshot.py --days 90                            # last 90 days vs prior 90 days
    python3 scripts/meta_campaign_snapshot.py --start 2026-01-01 --end 2026-03-20  # exact range, no prior comparison
    python3 scripts/meta_campaign_snapshot.py --account act_XXXXXXX               # single account
    python3 scripts/meta_campaign_snapshot.py --flags-only                         # flagged campaigns only

Modes:
    weekly   (default)  Current 7 days vs prior 7 days
    monthly             Current 30 days vs prior 30 days
    --days N            Current N days vs prior N days (e.g. 14, 60, 90)
    --start/--end       Exact date range — no prior period, raw data only

Change Flags:
    CRITICAL  Conversions down >40%  |  CPA up >50%
    WARNING   Conversions down >20%  |  CPA up >25%  |  CTR down >20%  |  Spend up >25%
    WIN       Conversions up >20%  |  CPA down >20%  |  Spend down >20% with stable conv
    STABLE    All metrics within +/-20%

Changelog:
    2026-03-21  Initial version — WoW/MoM, delta flags, per-campaign table,
                purchase/lead conversion breakdown, frequency signal.
"""

import argparse
import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.exceptions import FacebookRequestError

# ─── CLIENT REGISTRY ─────────────────────────────────────────────────────────

ALL_CLIENTS = {
    "Demo (ice Ad Account)": "act_1509969187799563",
    # Add client Meta ad account IDs here as they are onboarded:
    # "Client Name": "act_XXXXXXXXXXXXXXXXX",
}

# ─── CANONICAL META ACTION TYPES ─────────────────────────────────────────────
#
# Meta's API returns the SAME event under multiple action_type names.
# Always use the pixel-specific names below. NEVER also add the generic
# short-form names (e.g. "purchase", "lead", "add_to_cart") — they overlap
# with the pixel names and will DOUBLE-COUNT.
#
# Metric              Use this key                            NOT this
# ─────────────────── ─────────────────────────────────────── ───────────────
# Online purchases    offsite_conversion.fb_pixel_purchase    purchase
# Purchase value      offsite_conversion.fb_pixel_purchase    purchase (value)
# Website leads       offsite_conversion.fb_pixel_lead        lead
# Lead-gen form leads leadgen_grouped                         (no overlap)
# Add to cart         offsite_conversion.fb_pixel_add_to_cart add_to_cart
# Checkout started    offsite_conversion.fb_pixel_initiate_checkout initiate_checkout
# Offline purchases   offline_conversion.purchase             (no overlap)
#
# Source: Meta Ads API docs — "Actions, Action Values, and Conversions"
# https://developers.facebook.com/docs/marketing-api/reference/ads-action-stats/

# ─── CHANGE THRESHOLDS ────────────────────────────────────────────────────────

CRIT_CONV_DROP  = -0.40
WARN_CONV_DROP  = -0.20
WIN_CONV_GAIN   =  0.20
WARN_CPA_RISE   =  0.25
CRIT_CPA_RISE   =  0.50
WIN_CPA_DROP    = -0.20
WARN_CTR_DROP   = -0.20
WARN_SPEND_RISE =  0.25
WIN_SPEND_DROP  = -0.20

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
    """
    Returns a date range dict with curr_start, curr_end, prior_start, prior_end, label.
    Priority: --start/--end > --days > --mode
    When --start/--end is used, prior_start/prior_end are None (no comparison period).
    """
    today = date.today()

    if start and end:
        # Exact range — no prior period
        curr_start = date.fromisoformat(start)
        curr_end   = date.fromisoformat(end)
        label      = f"Custom range: {start} to {end}"
        return {
            "curr_start":  curr_start.strftime("%Y-%m-%d"),
            "curr_end":    curr_end.strftime("%Y-%m-%d"),
            "prior_start": None,
            "prior_end":   None,
            "label":       label,
        }

    if days:
        curr_end   = today - timedelta(days=1)
        curr_start = curr_end - timedelta(days=days - 1)
        label      = f"Rolling {days} days vs prior {days} days"
    elif mode == "monthly":
        curr_end   = today - timedelta(days=1)
        curr_start = curr_end - timedelta(days=29)
        label      = "Month-over-Month (30 days)"
    else:  # weekly default
        curr_end   = today - timedelta(days=1)
        curr_start = curr_end - timedelta(days=6)
        label      = "Week-over-Week (rolling 7 days)"

    prior_end   = curr_start - timedelta(days=1)
    prior_start = prior_end - timedelta(days=(curr_end - curr_start).days)

    return {
        "curr_start":  curr_start.strftime("%Y-%m-%d"),
        "curr_end":    curr_end.strftime("%Y-%m-%d"),
        "prior_start": prior_start.strftime("%Y-%m-%d"),
        "prior_end":   prior_end.strftime("%Y-%m-%d"),
        "label":       label,
    }


# ─── PULL ─────────────────────────────────────────────────────────────────────

INSIGHTS_FIELDS = [
    "campaign_id",
    "campaign_name",
    "objective",
    "spend",
    "impressions",
    "clicks",
    "reach",
    "frequency",
    "cpm",
    "cpc",
    "ctr",
    "actions",          # conversions by action type
    "action_values",    # conversion values (purchases)
]

def pull_campaign_metrics(account_id, start, end):
    """
    Pull campaign-level insights for a date range.
    Returns dict: campaign_id -> metrics dict.
    """
    account = AdAccount(account_id)
    try:
        insights = account.get_insights(
            fields=INSIGHTS_FIELDS,
            params={
                "level":        "campaign",
                "time_range":   {"since": start, "until": end},
                "limit":        500,
            }
        )
    except FacebookRequestError as e:
        print(f"    [API Error] {e.api_error_message()}")
        return {}

    # Also fetch campaign status (active/paused) separately
    try:
        campaigns_raw = account.get_campaigns(
            fields=["id", "name", "status", "daily_budget", "lifetime_budget"],
            params={"limit": 500}
        )
        status_map = {c["id"]: c for c in campaigns_raw}
    except FacebookRequestError:
        status_map = {}

    campaigns = {}
    for row in insights:
        cid = row.get("campaign_id", "")
        if not cid:
            continue

        # Parse action types into buckets
        actions      = {a["action_type"]: float(a["value"]) for a in (row.get("actions") or [])}
        action_vals  = {a["action_type"]: float(a["value"]) for a in (row.get("action_values") or [])}

        purchases     = actions.get("offsite_conversion.fb_pixel_purchase", 0)
        purchase_val  = action_vals.get("offsite_conversion.fb_pixel_purchase", 0)
        leads         = (actions.get("offsite_conversion.fb_pixel_lead", 0) +
                         actions.get("leadgen_grouped", 0))
        total_results = purchases + leads if (purchases + leads) > 0 else actions.get("omni_custom", 0)

        spend = float(row.get("spend", 0))
        impr  = int(row.get("impressions", 0))
        clicks = int(row.get("clicks", 0))

        camp_info = status_map.get(cid, {})
        daily_budget    = float(camp_info.get("daily_budget", 0)) / 100 if camp_info.get("daily_budget") else None
        lifetime_budget = float(camp_info.get("lifetime_budget", 0)) / 100 if camp_info.get("lifetime_budget") else None

        campaigns[cid] = {
            "id":               cid,
            "name":             row.get("campaign_name", cid),
            "status":           camp_info.get("status", "UNKNOWN"),
            "objective":        row.get("objective", ""),
            "spend":            spend,
            "impressions":      impr,
            "clicks":           clicks,
            "reach":            int(row.get("reach", 0)),
            "frequency":        float(row.get("frequency", 0)),
            "cpm":              float(row.get("cpm", 0)),
            "cpc":              float(row.get("cpc", 0)),
            "ctr":              float(row.get("ctr", 0)),
            "purchases":        purchases,
            "purchase_value":   purchase_val,
            "leads":            leads,
            "total_results":    total_results,
            "daily_budget":     daily_budget,
            "lifetime_budget":  lifetime_budget,
            "cpa":              spend / total_results if total_results > 0 else None,
            "roas":             purchase_val / spend  if spend > 0 and purchase_val > 0 else None,
            "cpp":              spend / purchases     if purchases > 0 else None,
            "cpl":              spend / leads         if leads > 0 else None,
        }

    return campaigns


# ─── DELTA & FLAGS ────────────────────────────────────────────────────────────

def delta(curr, prior):
    if not prior:
        return None, None
    return curr - prior, (curr - prior) / abs(prior)


def fmt_delta(pct, invert=False, threshold=0.05):
    if pct is None:
        return "n/a"
    arrow = "▲" if pct > 0 else "▼"
    sign  = "+" if pct > 0 else ""
    val   = f"{sign}{pct*100:.1f}%"
    if abs(pct) < threshold:
        tag = ""
    elif (invert and pct > 0) or (not invert and pct < 0):
        tag = "⚠"
    else:
        tag = "✅"
    return f"{arrow}{val}{' ' + tag if tag else ''}".strip()


def classify_campaign(curr, prior):
    if not prior or prior.get("spend", 0) == 0:
        return "new", []

    flags  = []
    status = "stable"

    _, conv_pct  = delta(curr["total_results"], prior["total_results"])
    _, spend_pct = delta(curr["spend"],         prior["spend"])
    _, ctr_pct   = delta(curr["ctr"],           prior["ctr"])

    cpa_pct = None
    if curr["cpa"] and prior.get("cpa"):
        _, cpa_pct = delta(curr["cpa"], prior["cpa"])

    # Critical
    if conv_pct is not None and conv_pct <= CRIT_CONV_DROP:
        flags.append(("CRITICAL", f"Results down {abs(conv_pct)*100:.0f}% ({prior['total_results']:.0f} -> {curr['total_results']:.0f})"))
        status = "critical"
    if cpa_pct is not None and cpa_pct >= CRIT_CPA_RISE:
        flags.append(("CRITICAL", f"CPA up {cpa_pct*100:.0f}% (${prior['cpa']:.2f} -> ${curr['cpa']:.2f})"))
        status = "critical"

    # Warnings
    if status != "critical":
        if conv_pct is not None and CRIT_CONV_DROP < conv_pct <= WARN_CONV_DROP:
            flags.append(("WARNING", f"Results down {abs(conv_pct)*100:.0f}% ({prior['total_results']:.0f} -> {curr['total_results']:.0f})"))
            status = "warning"
        if cpa_pct is not None and WARN_CPA_RISE <= cpa_pct < CRIT_CPA_RISE:
            flags.append(("WARNING", f"CPA up {cpa_pct*100:.0f}% (${prior['cpa']:.2f} -> ${curr['cpa']:.2f})"))
            status = "warning"
        if ctr_pct is not None and ctr_pct <= WARN_CTR_DROP:
            flags.append(("WARNING", f"CTR down {abs(ctr_pct)*100:.0f}% ({prior['ctr']:.2f}% -> {curr['ctr']:.2f}%)"))
            status = "warning"
        if spend_pct is not None and spend_pct >= WARN_SPEND_RISE:
            flags.append(("WARNING", f"Spend up {spend_pct*100:.0f}% (${prior['spend']:.2f} -> ${curr['spend']:.2f})"))
            status = "warning"
        # Creative fatigue signal
        if curr.get("frequency", 0) >= 4.0:
            flags.append(("WARNING", f"High frequency: {curr['frequency']:.1f} — creative fatigue risk"))
            if status == "stable":
                status = "warning"

    # Wins
    if status == "stable":
        if conv_pct is not None and conv_pct >= WIN_CONV_GAIN:
            flags.append(("WIN", f"Results up {conv_pct*100:.0f}% ({prior['total_results']:.0f} -> {curr['total_results']:.0f})"))
            status = "win"
        if cpa_pct is not None and cpa_pct <= WIN_CPA_DROP:
            flags.append(("WIN", f"CPA down {abs(cpa_pct)*100:.0f}% (${prior['cpa']:.2f} -> ${curr['cpa']:.2f})"))
            status = "win"
        if spend_pct is not None and spend_pct <= WIN_SPEND_DROP and (conv_pct is None or conv_pct >= -0.05):
            flags.append(("WIN", f"Spend down {abs(spend_pct)*100:.0f}% (${prior['spend']:.2f} -> ${curr['spend']:.2f}) with stable results"))
            status = "win"

    return status, flags


# ─── PRINT ────────────────────────────────────────────────────────────────────

STATUS_ICON = {
    "critical": "🚨",
    "warning":  "⚠️ ",
    "win":      "✅",
    "stable":   "➡️ ",
    "new":      "🆕",
}

def print_campaign_row(curr, prior):
    status, flags = classify_campaign(curr, prior)
    icon = STATUS_ICON.get(status, "➡️ ")

    has_prior = prior and prior.get("spend", 0) > 0

    if has_prior:
        _, spend_d = delta(curr["spend"],         prior["spend"])
        _, conv_d  = delta(curr["total_results"], prior["total_results"])
        _, ctr_d   = delta(curr["ctr"],           prior["ctr"])
        spend_delta = fmt_delta(spend_d, invert=True)
        conv_delta  = fmt_delta(conv_d)
        ctr_delta   = fmt_delta(ctr_d)
        prior_spend_str = f"prior: ${prior['spend']:.2f}, "
        prior_conv_str  = f"prior: {prior['total_results']:.0f}, "
        prior_ctr_str   = f"prior: {prior['ctr']:.2f}%, "
        if curr["cpa"] and prior.get("cpa"):
            _, cpa_d    = delta(curr["cpa"], prior["cpa"])
            cpa_delta   = fmt_delta(cpa_d, invert=True)
            prior_cpa_str = f"prior: ${prior['cpa']:.2f}, "
        else:
            cpa_delta     = "n/a"
            prior_cpa_str = ""
    else:
        spend_delta = conv_delta = ctr_delta = cpa_delta = "new"
        prior_spend_str = prior_conv_str = prior_ctr_str = prior_cpa_str = ""

    spend    = curr["spend"]
    results  = curr["total_results"]
    purchases = curr["purchases"]
    leads    = curr["leads"]
    cpa_str  = f"${curr['cpa']:.2f}"  if curr["cpa"]  else "—"
    roas_str = f"{curr['roas']:.2f}x" if curr["roas"] else "—"
    cpl_str  = f"${curr['cpl']:.2f}"  if curr["cpl"]  else "—"
    cpp_str  = f"${curr['cpp']:.2f}"  if curr["cpp"]  else "—"
    rev_str  = f"${curr['purchase_value']:.2f}" if curr["purchase_value"] > 0 else "—"
    freq_str = f"{curr['frequency']:.1f}"
    cpm_str  = f"${curr['cpm']:.2f}"
    ctr_str  = f"{curr['ctr']:.2f}%"

    budget_str = ""
    if curr.get("daily_budget"):
        budget_str = f"  |  Budget: ${curr['daily_budget']:.2f}/day"
    elif curr.get("lifetime_budget"):
        budget_str = f"  |  Lifetime budget: ${curr['lifetime_budget']:.2f}"

    status_label = "⏸ PAUSED" if curr.get("status") == "PAUSED" else "▶ ACTIVE"
    obj_label    = curr.get("objective", "").replace("_", " ").title()

    print(f"\n      {icon}  {curr['name']}  [{status_label}]  ({obj_label})")
    print(f"           Spend: ${spend:.2f} ({prior_spend_str}{spend_delta})  |  Results: {results:.0f} ({prior_conv_str}{conv_delta})  |  CPA: {cpa_str} ({prior_cpa_str}{cpa_delta})")
    print(f"           🛒 Purchases: {purchases:.0f}  |  CPP: {cpp_str}  |  Revenue: {rev_str}  |  ROAS: {roas_str}    📋 Leads: {leads:.0f}  |  CPL: {cpl_str}")
    print(f"           Impr: {curr['impressions']:,}  |  Reach: {curr['reach']:,}  |  Freq: {freq_str}  |  CTR: {ctr_str} ({prior_ctr_str}{ctr_delta})  |  CPM: {cpm_str}{budget_str}")

    for level, msg in flags:
        flag_icon = "🚨" if level == "CRITICAL" else ("⚠️ " if level == "WARNING" else "✅")
        print(f"           {flag_icon}  {msg}")


def print_account(client_name, account_id, curr_camps, prior_camps, flags_only):
    empty = {"critical": 0, "warning": 0, "win": 0, "stable": 0, "new": 0}
    if not curr_camps:
        print(f"\n⬜  {client_name} ({account_id}) — No campaign data in this period")
        return empty

    classified = {}
    for cid, curr in curr_camps.items():
        prior  = prior_camps.get(cid)
        status, flags = classify_campaign(curr, prior)
        classified[cid] = (status, flags, curr, prior)

    counts: dict = {"critical": 0, "warning": 0, "win": 0, "stable": 0, "new": 0}
    for _, (status, _, _, _) in classified.items():
        s = str(status)
        if s in counts:
            counts[s] += 1

    # Account rollup
    curr_spend    = sum(c["spend"]          for c in curr_camps.values())
    curr_results  = sum(c["total_results"]  for c in curr_camps.values())
    curr_purch    = sum(c["purchases"]      for c in curr_camps.values())
    curr_leads    = sum(c["leads"]          for c in curr_camps.values())
    curr_rev      = sum(c["purchase_value"] for c in curr_camps.values())
    curr_reach    = sum(c["reach"]          for c in curr_camps.values())

    prior_spend   = sum(c["spend"]          for c in prior_camps.values()) if prior_camps else 0
    prior_results = sum(c["total_results"]  for c in prior_camps.values()) if prior_camps else 0
    prior_purch   = sum(c["purchases"]      for c in prior_camps.values()) if prior_camps else 0
    prior_leads   = sum(c["leads"]          for c in prior_camps.values()) if prior_camps else 0
    prior_rev     = sum(c["purchase_value"] for c in prior_camps.values()) if prior_camps else 0

    _, spend_pct  = delta(curr_spend,   prior_spend)
    _, conv_pct   = delta(curr_results, prior_results)

    acct_cpa  = curr_spend / curr_results if curr_results > 0 else None
    acct_roas = curr_rev   / curr_spend   if curr_spend > 0 and curr_rev > 0 else None

    if counts["critical"] > 0:
        account_icon = "🚨"
    elif counts["warning"] > 0:
        account_icon = "⚠️ "
    elif counts["win"] > 0:
        account_icon = "✅"
    else:
        account_icon = "➡️ "

    active_count = sum(1 for c in curr_camps.values() if c.get("status") == "ACTIVE")
    paused_count = len(curr_camps) - active_count
    camp_label   = (f"{len(curr_camps)} campaign(s) ({active_count} active, {paused_count} paused)"
                    if paused_count > 0 else f"{len(curr_camps)} campaign(s)")

    prior_spend_str = f"prior: ${prior_spend:.2f}, " if prior_spend > 0 else ""
    prior_conv_str  = f"prior: {prior_results:.0f}, " if prior_spend > 0 else ""

    print(f"\n{account_icon}  {client_name} ({account_id})")
    print(f"    {camp_label}  |  "
          f"Spend: ${curr_spend:.2f} ({prior_spend_str}{fmt_delta(spend_pct, invert=True)})  |  "
          f"Results: {curr_results:.0f} ({prior_conv_str}{fmt_delta(conv_pct)})  |  "
          f"CPA: {f'${acct_cpa:.2f}' if acct_cpa else '—'}  |  "
          f"ROAS: {f'{acct_roas:.2f}x' if acct_roas else '—'}")
    print(f"    🛒 Purchases: {curr_purch:.0f} (prior: {prior_purch:.0f})  |  "
          f"Revenue: {'$' + f'{curr_rev:.2f}' if curr_rev > 0 else '—'} (prior: {'$' + f'{prior_rev:.2f}' if prior_rev > 0 else '—'})  |  "
          f"📋 Leads: {curr_leads:.0f} (prior: {prior_leads:.0f})  |  "
          f"Reach: {curr_reach:,}")

    if flags_only:
        flagged = {cid: v for cid, v in classified.items() if v[0] in ("critical", "warning", "win")}
        if not flagged:
            print("    ➡️   All campaigns stable — no significant changes detected")
            return counts
        for cid, (status, flags, curr, prior) in sorted(
            flagged.items(), key=lambda x: (x[1][0] != "critical", x[1][0] != "warning")
        ):
            print_campaign_row(curr, prior)
    else:
        for cid, (status, flags, curr, prior) in sorted(
            classified.items(), key=lambda x: x[1][2]["spend"], reverse=True
        ):
            print_campaign_row(curr, prior)

    return counts


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Meta campaign performance snapshot — period-over-period with conversion breakdown"
    )
    parser.add_argument("--account",     help="Single ad account ID (e.g. act_XXXXXXX). Omit to run all clients.")
    parser.add_argument("--client-name", help="Display name when using --account")
    parser.add_argument("--mode",        choices=["weekly", "monthly"], default="weekly",
                        help="weekly (rolling 7d) or monthly (30d). Default: weekly")
    parser.add_argument("--days",        type=int,
                        help="Rolling N-day window vs prior N days (e.g. 14, 60, 90). Overrides --mode.")
    parser.add_argument("--start",       help="Custom range start date YYYY-MM-DD. Use with --end. No prior comparison.")
    parser.add_argument("--end",         help="Custom range end date YYYY-MM-DD. Use with --start.")
    parser.add_argument("--flags-only",  action="store_true",
                        help="Only show campaigns with significant changes")
    args = parser.parse_args()

    init_api()
    dates = get_date_ranges(mode=args.mode, days=args.days, start=args.start, end=args.end)

    if args.account:
        targets = {(args.client_name or args.account): args.account}
    else:
        targets = ALL_CLIENTS

    mode_label = f"{args.days}D" if args.days else ("CUSTOM" if args.start else args.mode.upper())
    print("\n" + "="*60)
    print(f"META CAMPAIGN PERFORMANCE SNAPSHOT — {mode_label}")
    print(f"{dates['label']}")
    print(f"Current:  {dates['curr_start']} -> {dates['curr_end']}")
    if dates["prior_start"]:
        print(f"Prior:    {dates['prior_start']} -> {dates['prior_end']}")
    else:
        print("Prior:    n/a (exact range mode, no comparison period)")
    if args.flags_only:
        print("Mode: Flagged campaigns only")
    print("="*60)

    total_counts = {"critical": 0, "warning": 0, "win": 0, "stable": 0, "new": 0}
    errored = []

    curr_start:  str = str(dates["curr_start"])
    curr_end:    str = str(dates["curr_end"])
    prior_start: str | None = dates["prior_start"]
    prior_end:   str | None = dates["prior_end"]

    for name, account_id in targets.items():
        try:
            curr_camps  = pull_campaign_metrics(account_id, curr_start, curr_end)
            prior_camps = (pull_campaign_metrics(account_id, str(prior_start), str(prior_end))
                           if prior_start and prior_end else {})
            counts = print_account(name, account_id, curr_camps, prior_camps, args.flags_only)
            for k in total_counts:
                total_counts[k] += counts.get(k, 0)
        except Exception as e:
            errored.append(name)
            print(f"\n❌  {name} ({account_id}) — Error: {e}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  Accounts checked: {len(targets) - len(errored)}/{len(targets)}")
    print(f"  🚨 Critical:  {total_counts['critical']} campaign(s)")
    print(f"  ⚠️  Warnings:  {total_counts['warning']} campaign(s)")
    print(f"  ✅ Wins:      {total_counts['win']} campaign(s)")
    print(f"  ➡️   Stable:   {total_counts['stable']} campaign(s)")
    if total_counts.get("new", 0):
        print(f"  🆕 New:       {total_counts['new']} campaign(s)")
    if errored:
        print(f"  ❌ Errored:   {', '.join(errored)}")
    print("="*60)


if __name__ == "__main__":
    main()
