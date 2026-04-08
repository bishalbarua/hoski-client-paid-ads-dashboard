"""
Meta Ad Set Report
Purpose: Ad set level performance breakdown across all (or one) Meta ad accounts.
         Shows audience targeting summary, delivery health, cost per result,
         and period-over-period change flags per ad set.

         Useful for:
           - Identifying which audiences are driving results vs wasting spend
           - Spotting audience saturation (high frequency, declining CTR)
           - Diagnosing budget allocation issues across ad sets
           - Feeding /facebook-ads-performance-analyzer with granular data

Setup:
    Requires environment variables:
        META_APP_ID, META_APP_SECRET, META_ACCESS_TOKEN

    Install dependency:
        pip3 install facebook-business python-dotenv

Usage:
    python3 scripts/meta_adset_report.py                                          # all clients, weekly
    python3 scripts/meta_adset_report.py --mode monthly                           # MoM comparison
    python3 scripts/meta_adset_report.py --days 90                                # rolling 90 days
    python3 scripts/meta_adset_report.py --start 2026-01-01 --end 2026-03-20      # exact range
    python3 scripts/meta_adset_report.py --account act_XXXXXXX                   # single account
    python3 scripts/meta_adset_report.py --account act_XXXXXXX --campaign CAMP   # filter by campaign name
    python3 scripts/meta_adset_report.py --flags-only                             # flagged ad sets only

Change Flags:
    CRITICAL  Results down >40%  |  CPA up >50%
    WARNING   Results down >20%  |  CPA up >25%  |  CTR down >20%  |  Spend up >25%
              Frequency >= 4.0 (creative fatigue)  |  Frequency >= 6.0 (critical saturation)
    WIN       Results up >20%  |  CPA down >20%  |  Spend down >20% with stable results
    STABLE    All metrics within +/-20%

Changelog:
    2026-03-21  Initial version — ad set performance, audience targeting summary,
                frequency/saturation signals, period-over-period delta flags.
"""

import argparse
import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adset import AdSet
from facebook_business.exceptions import FacebookRequestError

# ─── CLIENT REGISTRY ─────────────────────────────────────────────────────────

ALL_CLIENTS = {
    "Demo (ice Ad Account)": "act_1509969187799563",
    "FaBesthetics":          "act_373162790093046",
    # Add client Meta ad account IDs here as they are onboarded:
    # "Client Name": "act_XXXXXXXXXXXXXXXXX",
}

# ─── CHANGE THRESHOLDS ────────────────────────────────────────────────────────

CRIT_CONV_DROP   = -0.40
WARN_CONV_DROP   = -0.20
WIN_CONV_GAIN    =  0.20
WARN_CPA_RISE    =  0.25
CRIT_CPA_RISE    =  0.50
WIN_CPA_DROP     = -0.20
WARN_CTR_DROP    = -0.20
WARN_SPEND_RISE  =  0.25
WIN_SPEND_DROP   = -0.20
FREQ_WARN        =  4.0   # creative fatigue threshold
FREQ_CRIT        =  6.0   # audience saturation threshold

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


# ─── DATE RANGES ─────────────────────────────────────────────────────────────

def get_date_ranges(mode=None, days=None, start=None, end=None):
    today = date.today()

    if start and end:
        curr_start = date.fromisoformat(start)
        curr_end   = date.fromisoformat(end)
        return {
            "curr_start":  curr_start.strftime("%Y-%m-%d"),
            "curr_end":    curr_end.strftime("%Y-%m-%d"),
            "prior_start": None,
            "prior_end":   None,
            "label":       f"Custom range: {start} to {end}",
        }

    if days:
        curr_end   = today - timedelta(days=1)
        curr_start = curr_end - timedelta(days=days - 1)
        label      = f"Rolling {days} days vs prior {days} days"
    elif mode == "monthly":
        curr_end   = today - timedelta(days=1)
        curr_start = curr_end - timedelta(days=29)
        label      = "Month-over-Month (30 days)"
    else:
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


# ─── TARGETING SUMMARY ────────────────────────────────────────────────────────

def summarize_targeting(targeting: dict) -> str:
    """Produce a compact one-line targeting summary from an ad set's targeting spec."""
    parts = []

    # Age
    age_min = targeting.get("age_min")
    age_max = targeting.get("age_max")
    if age_min or age_max:
        age_str = f"{age_min or '18'}-{age_max or '65+'}"
        parts.append(f"Age {age_str}")

    # Gender
    genders = targeting.get("genders", [])
    if genders == [1]:
        parts.append("Male")
    elif genders == [2]:
        parts.append("Female")

    # Locations
    geo = targeting.get("geo_locations", {})
    countries  = [c.get("name", c.get("country_code", "")) for c in geo.get("countries", [])]
    cities     = [c.get("name", "") for c in geo.get("cities", [])]
    regions    = [r.get("name", "") for r in geo.get("regions", [])]
    all_locs   = countries + regions + cities
    if all_locs:
        loc_str = ", ".join(all_locs[:3])
        if len(all_locs) > 3:
            loc_str += f" +{len(all_locs) - 3} more"
        parts.append(loc_str)

    # Interests
    interests = targeting.get("flexible_spec", [])
    if interests:
        all_interests = []
        for group in interests:
            for key in ("interests", "behaviors", "life_events", "industries"):
                all_interests.extend(i.get("name", "") for i in group.get(key, []))
        if all_interests:
            int_str = ", ".join(all_interests[:3])
            if len(all_interests) > 3:
                int_str += f" +{len(all_interests) - 3} more"
            parts.append(f"Interests: {int_str}")

    # Custom audiences
    custom = targeting.get("custom_audiences", [])
    if custom:
        names = [a.get("name", "Custom Audience") for a in custom[:2]]
        suffix = f" +{len(custom) - 2} more" if len(custom) > 2 else ""
        parts.append(f"CA: {', '.join(names)}{suffix}")

    # Lookalikes
    lookalikes = targeting.get("lookalike_audience", [])
    if lookalikes:
        parts.append(f"LAL: {len(lookalikes)} audience(s)")

    return "  |  ".join(parts) if parts else "Broad (no targeting spec)"


# ─── PULL ─────────────────────────────────────────────────────────────────────

INSIGHTS_FIELDS = [
    "adset_id",
    "adset_name",
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
    "actions",
    "action_values",
]

def pull_adset_metrics(account_id, start, end, campaign_filter=None):
    """
    Pull ad set level insights for a date range.
    Returns dict: adset_id -> metrics dict.
    """
    account = AdAccount(account_id)

    # Fetch targeting specs separately (not available in insights)
    try:
        adsets_raw = account.get_ad_sets(
            fields=[
                "id", "name", "status", "campaign_id", "campaign",
                "daily_budget", "lifetime_budget",
                "optimization_goal", "billing_event",
                "targeting",
            ],
            params={"limit": 500}
        )
        adset_meta = {a["id"]: a for a in adsets_raw}
    except FacebookRequestError as e:
        print(f"    [API Error fetching ad sets] {e.api_error_message()}")
        adset_meta = {}

    # Fetch insights
    try:
        insights = account.get_insights(
            fields=INSIGHTS_FIELDS,
            params={
                "level":      "adset",
                "time_range": {"since": start, "until": end},
                "limit":      500,
            }
        )
    except FacebookRequestError as e:
        print(f"    [API Error fetching insights] {e.api_error_message()}")
        return {}

    adsets = {}
    for row in insights:
        aid = row.get("adset_id", "")
        if not aid:
            continue

        camp_name = row.get("campaign_name", "")
        if campaign_filter and campaign_filter.lower() not in camp_name.lower():
            continue

        actions     = {a["action_type"]: float(a["value"]) for a in (row.get("actions") or [])}
        action_vals = {a["action_type"]: float(a["value"]) for a in (row.get("action_values") or [])}

        purchases    = actions.get("offsite_conversion.fb_pixel_purchase", 0)
        purchase_val = action_vals.get("offsite_conversion.fb_pixel_purchase", 0)
        leads        = (actions.get("offsite_conversion.fb_pixel_lead", 0) +
                        actions.get("leadgen_grouped", 0))
        total_results = purchases + leads if (purchases + leads) > 0 else actions.get("omni_custom", 0)

        spend  = float(row.get("spend", 0))
        impr   = int(row.get("impressions", 0))
        clicks = int(row.get("clicks", 0))
        freq   = float(row.get("frequency", 0))

        meta = adset_meta.get(aid, {})
        daily_budget    = float(meta.get("daily_budget", 0)) / 100 if meta.get("daily_budget") else None
        lifetime_budget = float(meta.get("lifetime_budget", 0)) / 100 if meta.get("lifetime_budget") else None
        targeting_spec  = meta.get("targeting", {}) if meta else {}
        targeting_str   = summarize_targeting(targeting_spec) if targeting_spec else "n/a"
        opt_goal        = meta.get("optimization_goal", "")

        adsets[aid] = {
            "id":               aid,
            "name":             row.get("adset_name", aid),
            "campaign_name":    camp_name,
            "objective":        row.get("objective", ""),
            "status":           meta.get("status", "UNKNOWN"),
            "opt_goal":         opt_goal.replace("_", " ").title() if opt_goal else "",
            "targeting":        targeting_str,
            "spend":            spend,
            "impressions":      impr,
            "clicks":           clicks,
            "reach":            int(row.get("reach", 0)),
            "frequency":        freq,
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
            "cpl":              spend / leads         if leads > 0 else None,
            "cpp":              spend / purchases     if purchases > 0 else None,
        }

    return adsets


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


def classify_adset(curr, prior):
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

    # Frequency signals (independent of prior period)
    freq = curr.get("frequency", 0)
    if freq >= FREQ_CRIT:
        flags.append(("CRITICAL", f"Frequency {freq:.1f} — severe audience saturation, refresh creative immediately"))
        status = "critical"
    elif freq >= FREQ_WARN:
        flags.append(("WARNING", f"Frequency {freq:.1f} — creative fatigue risk, plan rotation"))
        if status == "stable":
            status = "warning"

    # Critical
    if status != "critical":
        if conv_pct is not None and conv_pct <= CRIT_CONV_DROP:
            flags.append(("CRITICAL", f"Results down {abs(conv_pct)*100:.0f}% ({prior['total_results']:.0f} -> {curr['total_results']:.0f})"))
            status = "critical"
        if cpa_pct is not None and cpa_pct >= CRIT_CPA_RISE:
            flags.append(("CRITICAL", f"CPA up {cpa_pct*100:.0f}% (${prior['cpa']:.2f} -> ${curr['cpa']:.2f})"))
            status = "critical"

    # Warnings
    if status not in ("critical",):
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

def print_adset_row(curr, prior):
    status, flags = classify_adset(curr, prior)
    icon = STATUS_ICON.get(status, "➡️ ")

    has_prior = prior and prior.get("spend", 0) > 0

    if has_prior:
        _, spend_d = delta(curr["spend"],         prior["spend"])
        _, conv_d  = delta(curr["total_results"], prior["total_results"])
        _, ctr_d   = delta(curr["ctr"],           prior["ctr"])
        _, freq_d  = delta(curr["frequency"],     prior["frequency"])
        spend_delta = fmt_delta(spend_d, invert=True)
        conv_delta  = fmt_delta(conv_d)
        ctr_delta   = fmt_delta(ctr_d)
        freq_delta  = fmt_delta(freq_d, invert=True)
        prior_spend_str = f"prior: ${prior['spend']:.2f}, "
        prior_conv_str  = f"prior: {prior['total_results']:.0f}, "
        prior_ctr_str   = f"prior: {prior['ctr']:.2f}%, "
        if curr["cpa"] and prior.get("cpa"):
            _, cpa_d      = delta(curr["cpa"], prior["cpa"])
            cpa_delta     = fmt_delta(cpa_d, invert=True)
            prior_cpa_str = f"prior: ${prior['cpa']:.2f}, "
        else:
            cpa_delta     = "n/a"
            prior_cpa_str = ""
    else:
        spend_delta = conv_delta = ctr_delta = cpa_delta = freq_delta = "new"
        prior_spend_str = prior_conv_str = prior_ctr_str = prior_cpa_str = ""

    spend    = curr["spend"]
    results  = curr["total_results"]
    purchases = curr["purchases"]
    leads    = curr["leads"]
    cpa_str  = f"${curr['cpa']:.2f}"  if curr["cpa"]  else "—"
    roas_str = f"{curr['roas']:.2f}x" if curr["roas"] else "—"
    cpl_str  = f"${curr['cpl']:.2f}"  if curr["cpl"]  else "—"
    cpp_str  = f"${curr['cpp']:.2f}"  if curr["cpp"]  else "—"
    freq_str = f"{curr['frequency']:.1f}"
    cpm_str  = f"${curr['cpm']:.2f}"
    ctr_str  = f"{curr['ctr']:.2f}%"

    budget_str = ""
    if curr.get("daily_budget"):
        budget_str = f"  |  Budget: ${curr['daily_budget']:.2f}/day"
    elif curr.get("lifetime_budget"):
        budget_str = f"  |  Lifetime: ${curr['lifetime_budget']:.2f}"

    status_label = "⏸ PAUSED" if curr.get("status") == "PAUSED" else "▶ ACTIVE"

    print(f"\n         {icon}  {curr['name']}  [{status_label}]")
    print(f"              Goal: {curr['opt_goal'] or 'n/a'}{budget_str}")
    print(f"              Targeting: {curr['targeting']}")
    print(f"              Spend: ${spend:.2f} ({prior_spend_str}{spend_delta})  |  Results: {results:.0f} ({prior_conv_str}{conv_delta})  |  CPA: {cpa_str} ({prior_cpa_str}{cpa_delta})")
    print(f"              🛒 Purchases: {purchases:.0f}  |  CPP: {cpp_str}  |  ROAS: {roas_str}    📋 Leads: {leads:.0f}  |  CPL: {cpl_str}")
    print(f"              Impr: {curr['impressions']:,}  |  Reach: {curr['reach']:,}  |  Freq: {freq_str} ({freq_delta})  |  CTR: {ctr_str} ({prior_ctr_str}{ctr_delta})  |  CPM: {cpm_str}")

    for level, msg in flags:
        flag_icon = "🚨" if level == "CRITICAL" else ("⚠️ " if level == "WARNING" else "✅")
        print(f"              {flag_icon}  {msg}")


def print_account(client_name, account_id, curr_adsets, prior_adsets, flags_only):
    if not curr_adsets:
        print(f"\n⬜  {client_name} ({account_id}) — No ad set data in this period")
        return {"critical": 0, "warning": 0, "win": 0, "stable": 0, "new": 0}

    # Group by campaign
    campaigns: dict = {}
    for aid, adset in curr_adsets.items():
        camp = adset["campaign_name"] or "Unknown Campaign"
        if camp not in campaigns:
            campaigns[camp] = []
        campaigns[camp].append(aid)

    counts: dict = {"critical": 0, "warning": 0, "win": 0, "stable": 0, "new": 0}

    # Account rollup
    curr_spend   = sum(a["spend"]          for a in curr_adsets.values())
    curr_results = sum(a["total_results"]  for a in curr_adsets.values())
    curr_reach   = sum(a["reach"]          for a in curr_adsets.values())
    prior_spend  = sum(a["spend"]          for a in prior_adsets.values()) if prior_adsets else 0
    prior_results = sum(a["total_results"] for a in prior_adsets.values()) if prior_adsets else 0

    _, spend_pct = delta(curr_spend,   prior_spend)
    _, conv_pct  = delta(curr_results, prior_results)

    # Highest frequency ad set
    max_freq_adset = max(curr_adsets.values(), key=lambda a: a["frequency"])
    freq_warn_str  = f"  |  Max freq: {max_freq_adset['frequency']:.1f} ({max_freq_adset['name'][:30]})"

    prior_str = f"prior: ${prior_spend:.2f}, " if prior_spend > 0 else ""
    prior_conv_str = f"prior: {prior_results:.0f}, " if prior_spend > 0 else ""

    print(f"\n➡️   {client_name} ({account_id})")
    print(f"    {len(curr_adsets)} ad set(s) across {len(campaigns)} campaign(s)  |  "
          f"Spend: ${curr_spend:.2f} ({prior_str}{fmt_delta(spend_pct, invert=True)})  |  "
          f"Results: {curr_results:.0f} ({prior_conv_str}{fmt_delta(conv_pct)})  |  "
          f"Reach: {curr_reach:,}{freq_warn_str}")

    for camp_name, adset_ids in sorted(campaigns.items()):
        camp_adsets = {aid: curr_adsets[aid] for aid in adset_ids}
        camp_spend  = sum(a["spend"] for a in camp_adsets.values())
        print(f"\n    Campaign: {camp_name}  (${camp_spend:.2f} spend, {len(adset_ids)} ad set(s))")

        classified = {}
        for aid in adset_ids:
            curr  = curr_adsets[aid]
            prior = prior_adsets.get(aid)
            status, flags = classify_adset(curr, prior)
            classified[aid] = (status, flags, curr, prior)
            s = str(status)
            if s in counts:
                counts[s] += 1

        if flags_only:
            flagged = {aid: v for aid, v in classified.items() if v[0] in ("critical", "warning", "win")}
            if not flagged:
                print("         ➡️   All ad sets stable")
                continue
            for aid, (status, flags, curr, prior) in sorted(
                flagged.items(), key=lambda x: (x[1][0] != "critical", x[1][0] != "warning")
            ):
                print_adset_row(curr, prior)
        else:
            for aid, (status, flags, curr, prior) in sorted(
                classified.items(), key=lambda x: x[1][2]["spend"], reverse=True
            ):
                print_adset_row(curr, prior)

    return counts


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Meta ad set report — audience targeting, delivery, and conversion breakdown"
    )
    parser.add_argument("--account",     help="Single ad account ID (e.g. act_XXXXXXX). Omit to run all clients.")
    parser.add_argument("--client-name", help="Display name when using --account")
    parser.add_argument("--campaign",    help="Filter to ad sets under campaigns matching this name (partial match)")
    parser.add_argument("--mode",        choices=["weekly", "monthly"], default="weekly",
                        help="weekly (rolling 7d) or monthly (30d). Default: weekly")
    parser.add_argument("--days",        type=int,
                        help="Rolling N-day window vs prior N days (e.g. 14, 60, 90). Overrides --mode.")
    parser.add_argument("--start",       help="Custom range start YYYY-MM-DD. Use with --end. No prior comparison.")
    parser.add_argument("--end",         help="Custom range end YYYY-MM-DD. Use with --start.")
    parser.add_argument("--flags-only",  action="store_true",
                        help="Only show ad sets with significant changes or warnings")
    args = parser.parse_args()

    init_api()
    dates = get_date_ranges(mode=args.mode, days=args.days, start=args.start, end=args.end)

    if args.account:
        targets = {(args.client_name or args.account): args.account}
    else:
        targets = ALL_CLIENTS

    mode_label = f"{args.days}D" if args.days else ("CUSTOM" if args.start else args.mode.upper())
    print("\n" + "="*60)
    print(f"META AD SET REPORT — {mode_label}")
    print(f"{dates['label']}")
    print(f"Current:  {dates['curr_start']} -> {dates['curr_end']}")
    if dates["prior_start"]:
        print(f"Prior:    {dates['prior_start']} -> {dates['prior_end']}")
    else:
        print("Prior:    n/a (exact range, no comparison period)")
    if args.campaign:
        print(f"Filter:   campaigns matching '{args.campaign}'")
    if args.flags_only:
        print("Mode:     Flagged ad sets only")
    print("="*60)

    total_counts: dict = {"critical": 0, "warning": 0, "win": 0, "stable": 0, "new": 0}
    errored = []

    curr_start:  str = str(dates["curr_start"])
    curr_end:    str = str(dates["curr_end"])
    prior_start: str | None = dates["prior_start"]
    prior_end:   str | None = dates["prior_end"]

    for name, account_id in targets.items():
        try:
            curr_adsets  = pull_adset_metrics(account_id, curr_start, curr_end, args.campaign)
            prior_adsets = (pull_adset_metrics(account_id, str(prior_start), str(prior_end), args.campaign)
                            if prior_start and prior_end else {})
            counts = print_account(name, account_id, curr_adsets, prior_adsets, args.flags_only)
            for k in total_counts:
                total_counts[k] += counts.get(k, 0)
        except Exception as e:
            errored.append(name)
            print(f"\n❌  {name} ({account_id}) — Error: {e}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  Accounts checked: {len(targets) - len(errored)}/{len(targets)}")
    print(f"  🚨 Critical:  {total_counts['critical']} ad set(s)")
    print(f"  ⚠️  Warnings:  {total_counts['warning']} ad set(s)")
    print(f"  ✅ Wins:      {total_counts['win']} ad set(s)")
    print(f"  ➡️   Stable:   {total_counts['stable']} ad set(s)")
    if total_counts.get("new", 0):
        print(f"  🆕 New:       {total_counts['new']} ad set(s)")
    if errored:
        print(f"  ❌ Errored:   {', '.join(errored)}")
    print("="*60)


if __name__ == "__main__":
    main()
