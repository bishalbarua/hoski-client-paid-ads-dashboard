"""
Meta Ad Creative Report
Purpose: Ad-level creative performance breakdown across all (or one) Meta ad
         accounts. Shows creative type, copy preview, CTA, and performance
         metrics with period-over-period change flags.

         Useful for:
           - Identifying which creatives are driving results vs burning spend
           - Detecting creative fatigue before it kills performance
           - Informing creative refresh decisions with real data
           - Feeding /ad-copy-testing-analyzer and /creative-director skills

Setup:
    Requires environment variables:
        META_APP_ID, META_APP_SECRET, META_ACCESS_TOKEN

    Install dependency:
        pip3 install facebook-business python-dotenv

Usage:
    python3 scripts/meta_ad_creative_report.py                                     # all clients, weekly
    python3 scripts/meta_ad_creative_report.py --mode monthly                      # MoM comparison
    python3 scripts/meta_ad_creative_report.py --days 30                           # rolling 30 days
    python3 scripts/meta_ad_creative_report.py --start 2026-01-01 --end 2026-03-20 # exact range
    python3 scripts/meta_ad_creative_report.py --account act_XXXXXXX              # single account
    python3 scripts/meta_ad_creative_report.py --account act_XXXXXXX --top 10     # top 10 ads by spend
    python3 scripts/meta_ad_creative_report.py --flags-only                        # flagged ads only

Change Flags:
    CRITICAL  Results down >40%  |  CPA up >50%  |  CTR < 0.5% (dead creative)
    WARNING   Results down >20%  |  CPA up >25%  |  CTR down >30%  |  Spend up >25%
    WIN       Results up >20%  |  CPA down >20%
    STABLE    All metrics within thresholds

Changelog:
    2026-03-21  Initial version — ad-level creative performance, copy preview,
                creative type classification, period-over-period delta flags,
                dead creative detection (CTR below floor).
"""

import argparse
import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.exceptions import FacebookRequestError

# ─── CLIENT REGISTRY ─────────────────────────────────────────────────────────

ALL_CLIENTS = {
    "Demo (ice Ad Account)": "act_1509969187799563",
    # "Client Name": "act_XXXXXXXXXXXXXXXXX",
}

# ─── THRESHOLDS ───────────────────────────────────────────────────────────────

CRIT_CONV_DROP   = -0.40
WARN_CONV_DROP   = -0.20
WIN_CONV_GAIN    =  0.20
WARN_CPA_RISE    =  0.25
CRIT_CPA_RISE    =  0.50
WIN_CPA_DROP     = -0.20
WARN_CTR_DROP    = -0.30    # steeper threshold at ad level (creative-specific signal)
WARN_SPEND_RISE  =  0.25
CTR_DEAD_FLOOR   =  0.5     # CTR% below this = dead creative (image/video ads)

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


# ─── CREATIVE DETAILS ─────────────────────────────────────────────────────────

CREATIVE_FIELDS = [
    "id",
    "name",
    "title",
    "body",
    "call_to_action_type",
    "object_type",
    "image_url",
    "video_id",
    "object_story_spec",
    "asset_feed_spec",
]

def classify_creative_type(creative: dict) -> str:
    """Infer creative format from the creative object fields."""
    obj_type = str(creative.get("object_type", "")).upper()

    # Check asset_feed_spec — indicates dynamic/advantage+ creative
    if creative.get("asset_feed_spec"):
        return "Dynamic / Advantage+"

    # Check object_story_spec for carousel
    story_spec = creative.get("object_story_spec", {})
    if story_spec:
        if "link_data" in story_spec:
            link_data = story_spec["link_data"]
            if link_data.get("child_attachments"):
                return "Carousel"
            if link_data.get("picture") or link_data.get("image_hash"):
                return "Image"
        if "video_data" in story_spec:
            return "Video"
        if "photo_data" in story_spec:
            return "Image"
        if "template_data" in story_spec:
            return "Collection"

    # Fallback on object_type
    if "VIDEO" in obj_type:
        return "Video"
    if "PHOTO" in obj_type or "IMAGE" in obj_type:
        return "Image"
    if "SHARE" in obj_type:
        return "Link / Image"

    if creative.get("video_id"):
        return "Video"
    if creative.get("image_url"):
        return "Image"

    return "Unknown"


def extract_copy(creative: dict) -> tuple[str, str]:
    """Extract (headline, body) from a creative object. Returns truncated strings."""
    headline = ""
    body     = ""

    # Direct fields
    if creative.get("title"):
        headline = str(creative["title"])
    if creative.get("body"):
        body = str(creative["body"])

    # From object_story_spec
    story_spec = creative.get("object_story_spec", {})
    if story_spec:
        link_data  = story_spec.get("link_data", {})
        video_data = story_spec.get("video_data", {})
        data       = link_data or video_data

        if not headline and data.get("name"):
            headline = str(data["name"])
        if not body and data.get("message"):
            body = str(data["message"])
        if not body and data.get("description"):
            body = str(data["description"])

    # Truncate for display
    headline = (headline[:60] + "...") if len(headline) > 60 else headline
    body     = (body[:120] + "...") if len(body) > 120 else body

    return headline or "(no headline)", body or "(no body copy)"


def fetch_creative_details(creative_id: str) -> dict:
    """Fetch a single creative's details. Returns empty dict on failure."""
    try:
        creative = AdCreative(creative_id).api_get(fields=CREATIVE_FIELDS)
        return dict(creative)
    except FacebookRequestError:
        return {}


# ─── PULL ─────────────────────────────────────────────────────────────────────

INSIGHTS_FIELDS = [
    "ad_id",
    "ad_name",
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

def pull_ad_metrics(account_id, start, end, top=None):
    """
    Pull ad-level insights and creative details for a date range.
    Returns dict: ad_id -> metrics dict (sorted by spend desc, limited to top N if set).
    """
    account = AdAccount(account_id)

    # Fetch ad creative IDs
    try:
        ads_raw = account.get_ads(
            fields=["id", "name", "status", "creative", "adset_id"],
            params={"limit": 500}
        )
        ad_creative_map = {a["id"]: a.get("creative", {}).get("id") for a in ads_raw}
        ad_status_map   = {a["id"]: a.get("status", "UNKNOWN")       for a in ads_raw}
    except FacebookRequestError as e:
        print(f"    [API Error fetching ads] {e.api_error_message()}")
        ad_creative_map = {}
        ad_status_map   = {}

    # Fetch insights
    try:
        insights = account.get_insights(
            fields=INSIGHTS_FIELDS,
            params={
                "level":      "ad",
                "time_range": {"since": start, "until": end},
                "limit":      500,
            }
        )
    except FacebookRequestError as e:
        print(f"    [API Error fetching insights] {e.api_error_message()}")
        return {}

    ads = {}
    for row in insights:
        aid = row.get("ad_id", "")
        if not aid:
            continue

        actions     = {a["action_type"]: float(a["value"]) for a in (row.get("actions") or [])}
        action_vals = {a["action_type"]: float(a["value"]) for a in (row.get("action_values") or [])}

        purchases    = actions.get("offsite_conversion.fb_pixel_purchase", 0) + actions.get("purchase", 0)
        purchase_val = action_vals.get("offsite_conversion.fb_pixel_purchase", 0) + action_vals.get("purchase", 0)
        leads        = (actions.get("lead", 0) +
                        actions.get("offsite_conversion.fb_pixel_lead", 0) +
                        actions.get("leadgen_grouped", 0))
        total_results = purchases + leads if (purchases + leads) > 0 else actions.get("omni_custom", 0)

        spend  = float(row.get("spend", 0))
        impr   = int(row.get("impressions", 0))
        ctr    = float(row.get("ctr", 0))

        ads[aid] = {
            "id":             aid,
            "name":           row.get("ad_name", aid),
            "adset_name":     row.get("adset_name", ""),
            "campaign_name":  row.get("campaign_name", ""),
            "objective":      row.get("objective", ""),
            "status":         ad_status_map.get(aid, "UNKNOWN"),
            "spend":          spend,
            "impressions":    impr,
            "clicks":         int(row.get("clicks", 0)),
            "reach":          int(row.get("reach", 0)),
            "frequency":      float(row.get("frequency", 0)),
            "cpm":            float(row.get("cpm", 0)),
            "cpc":            float(row.get("cpc", 0)),
            "ctr":            ctr,
            "purchases":      purchases,
            "purchase_value": purchase_val,
            "leads":          leads,
            "total_results":  total_results,
            "cpa":            spend / total_results if total_results > 0 else None,
            "roas":           purchase_val / spend  if spend > 0 and purchase_val > 0 else None,
            "cpl":            spend / leads         if leads > 0 else None,
            "cpp":            spend / purchases     if purchases > 0 else None,
            # Creative details — fetched below
            "creative_type":  "Unknown",
            "headline":       "",
            "body":           "",
            "cta":            "",
        }

    # Sort by spend, apply top N limit
    sorted_ids = sorted(ads, key=lambda x: ads[x]["spend"], reverse=True)
    if top:
        sorted_ids = sorted_ids[:top]

    # Fetch creative details for the ads we're keeping
    for aid in sorted_ids:
        creative_id = ad_creative_map.get(aid)
        if creative_id:
            creative = fetch_creative_details(creative_id)
            if creative:
                ads[aid]["creative_type"] = classify_creative_type(creative)
                ads[aid]["headline"], ads[aid]["body"] = extract_copy(creative)
                ads[aid]["cta"] = str(creative.get("call_to_action_type", "")).replace("_", " ").title()

    # Return only the top N ads, preserving the sorted order as a dict
    return {aid: ads[aid] for aid in sorted_ids}


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


def classify_ad(curr, prior):
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

    # Dead creative — CTR too low to be viable (only flag if enough impressions)
    if curr["impressions"] >= 1000 and curr["ctr"] < CTR_DEAD_FLOOR:
        creative_type = curr.get("creative_type", "")
        if "Video" not in creative_type:  # video CTR benchmarks differ
            flags.append(("CRITICAL", f"Dead creative: CTR {curr['ctr']:.2f}% below {CTR_DEAD_FLOOR}% floor — pause and replace"))
            status = "critical"

    # Critical
    if status != "critical":
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

    # Wins
    if status == "stable":
        if conv_pct is not None and conv_pct >= WIN_CONV_GAIN:
            flags.append(("WIN", f"Results up {conv_pct*100:.0f}% ({prior['total_results']:.0f} -> {curr['total_results']:.0f})"))
            status = "win"
        if cpa_pct is not None and cpa_pct <= WIN_CPA_DROP:
            flags.append(("WIN", f"CPA down {abs(cpa_pct)*100:.0f}% (${prior['cpa']:.2f} -> ${curr['cpa']:.2f})"))
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

def print_ad_row(curr, prior):
    status, flags = classify_ad(curr, prior)
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
            _, cpa_d      = delta(curr["cpa"], prior["cpa"])
            cpa_delta     = fmt_delta(cpa_d, invert=True)
            prior_cpa_str = f"prior: ${prior['cpa']:.2f}, "
        else:
            cpa_delta     = "n/a"
            prior_cpa_str = ""
    else:
        spend_delta = conv_delta = ctr_delta = cpa_delta = "new"
        prior_spend_str = prior_conv_str = prior_ctr_str = prior_cpa_str = ""

    cpa_str  = f"${curr['cpa']:.2f}"  if curr["cpa"]  else "—"
    roas_str = f"{curr['roas']:.2f}x" if curr["roas"] else "—"
    cpl_str  = f"${curr['cpl']:.2f}"  if curr["cpl"]  else "—"
    cpp_str  = f"${curr['cpp']:.2f}"  if curr["cpp"]  else "—"
    cpm_str  = f"${curr['cpm']:.2f}"
    ctr_str  = f"{curr['ctr']:.2f}%"
    freq_str = f"{curr['frequency']:.1f}"

    status_label = "⏸ PAUSED" if curr.get("status") == "PAUSED" else "▶ ACTIVE"
    creative_type = curr.get("creative_type", "Unknown")
    cta           = curr.get("cta", "")
    headline      = curr.get("headline", "")
    body          = curr.get("body", "")

    print(f"\n         {icon}  {curr['name']}  [{status_label}]")
    print(f"              Ad Set: {curr['adset_name']}")
    print(f"              Format: {creative_type}  |  CTA: {cta or 'n/a'}")
    if headline:
        print(f"              Headline: {headline}")
    if body:
        print(f"              Body: {body}")
    print(f"              Spend: ${curr['spend']:.2f} ({prior_spend_str}{spend_delta})  |  Results: {curr['total_results']:.0f} ({prior_conv_str}{conv_delta})  |  CPA: {cpa_str} ({prior_cpa_str}{cpa_delta})")
    print(f"              🛒 Purchases: {curr['purchases']:.0f}  |  CPP: {cpp_str}  |  ROAS: {roas_str}    📋 Leads: {curr['leads']:.0f}  |  CPL: {cpl_str}")
    print(f"              Impr: {curr['impressions']:,}  |  Reach: {curr['reach']:,}  |  Freq: {freq_str}  |  CTR: {ctr_str} ({prior_ctr_str}{ctr_delta})  |  CPM: {cpm_str}")

    for level, msg in flags:
        flag_icon = "🚨" if level == "CRITICAL" else ("⚠️ " if level == "WARNING" else "✅")
        print(f"              {flag_icon}  {msg}")


def print_account(client_name, account_id, curr_ads, prior_ads, flags_only):
    if not curr_ads:
        print(f"\n⬜  {client_name} ({account_id}) — No ad data in this period")
        return {"critical": 0, "warning": 0, "win": 0, "stable": 0, "new": 0}

    # Group by campaign
    campaigns: dict = {}
    for aid, ad in curr_ads.items():
        camp = ad["campaign_name"] or "Unknown Campaign"
        if camp not in campaigns:
            campaigns[camp] = []
        campaigns[camp].append(aid)

    counts: dict = {"critical": 0, "warning": 0, "win": 0, "stable": 0, "new": 0}

    # Account rollup
    curr_spend   = sum(a["spend"]         for a in curr_ads.values())
    curr_results = sum(a["total_results"] for a in curr_ads.values())
    prior_spend  = sum(a["spend"]         for a in prior_ads.values()) if prior_ads else 0
    prior_results = sum(a["total_results"] for a in prior_ads.values()) if prior_ads else 0

    _, spend_pct = delta(curr_spend,   prior_spend)
    _, conv_pct  = delta(curr_results, prior_results)

    # Creative format summary
    format_counts: dict = {}
    for ad in curr_ads.values():
        fmt = ad.get("creative_type", "Unknown")
        format_counts[fmt] = format_counts.get(fmt, 0) + 1
    fmt_summary = ", ".join(f"{v}x {k}" for k, v in sorted(format_counts.items(), key=lambda x: -x[1]))

    prior_str      = f"prior: ${prior_spend:.2f}, "   if prior_spend > 0 else ""
    prior_conv_str = f"prior: {prior_results:.0f}, "  if prior_spend > 0 else ""

    print(f"\n➡️   {client_name} ({account_id})")
    print(f"    {len(curr_ads)} ad(s) across {len(campaigns)} campaign(s)  |  "
          f"Spend: ${curr_spend:.2f} ({prior_str}{fmt_delta(spend_pct, invert=True)})  |  "
          f"Results: {curr_results:.0f} ({prior_conv_str}{fmt_delta(conv_pct)})")
    print(f"    Formats: {fmt_summary}")

    for camp_name, ad_ids in sorted(campaigns.items()):
        camp_spend = sum(curr_ads[aid]["spend"] for aid in ad_ids)
        print(f"\n    Campaign: {camp_name}  (${camp_spend:.2f} spend, {len(ad_ids)} ad(s))")

        classified = {}
        for aid in ad_ids:
            curr  = curr_ads[aid]
            prior = prior_ads.get(aid)
            status, flags = classify_ad(curr, prior)
            classified[aid] = (status, flags, curr, prior)
            s = str(status)
            if s in counts:
                counts[s] += 1

        if flags_only:
            flagged = {aid: v for aid, v in classified.items() if v[0] in ("critical", "warning", "win")}
            if not flagged:
                print("         ➡️   All ads stable")
                continue
            for aid, (status, flags, curr, prior) in sorted(
                flagged.items(), key=lambda x: (x[1][0] != "critical", x[1][0] != "warning")
            ):
                print_ad_row(curr, prior)
        else:
            for aid, (status, flags, curr, prior) in sorted(
                classified.items(), key=lambda x: x[1][2]["spend"], reverse=True
            ):
                print_ad_row(curr, prior)

    return counts


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Meta ad creative report — creative format, copy preview, and performance breakdown"
    )
    parser.add_argument("--account",     help="Single ad account ID (e.g. act_XXXXXXX). Omit to run all clients.")
    parser.add_argument("--client-name", help="Display name when using --account")
    parser.add_argument("--mode",        choices=["weekly", "monthly"], default="weekly",
                        help="weekly (rolling 7d) or monthly (30d). Default: weekly")
    parser.add_argument("--days",        type=int,
                        help="Rolling N-day window vs prior N days. Overrides --mode.")
    parser.add_argument("--start",       help="Custom range start YYYY-MM-DD. Use with --end.")
    parser.add_argument("--end",         help="Custom range end YYYY-MM-DD. Use with --start.")
    parser.add_argument("--top",         type=int,
                        help="Limit to top N ads by spend per account (e.g. --top 10)")
    parser.add_argument("--flags-only",  action="store_true",
                        help="Only show ads with significant changes or warnings")
    args = parser.parse_args()

    init_api()
    dates = get_date_ranges(mode=args.mode, days=args.days, start=args.start, end=args.end)

    if args.account:
        targets = {(args.client_name or args.account): args.account}
    else:
        targets = ALL_CLIENTS

    mode_label = f"{args.days}D" if args.days else ("CUSTOM" if args.start else args.mode.upper())
    print("\n" + "="*60)
    print(f"META AD CREATIVE REPORT — {mode_label}")
    print(f"{dates['label']}")
    print(f"Current:  {dates['curr_start']} -> {dates['curr_end']}")
    if dates["prior_start"]:
        print(f"Prior:    {dates['prior_start']} -> {dates['prior_end']}")
    else:
        print("Prior:    n/a (exact range, no comparison period)")
    if args.top:
        print(f"Limit:    Top {args.top} ads by spend")
    if args.flags_only:
        print("Mode:     Flagged ads only")
    print("="*60)

    total_counts: dict = {"critical": 0, "warning": 0, "win": 0, "stable": 0, "new": 0}
    errored = []

    curr_start:  str = str(dates["curr_start"])
    curr_end:    str = str(dates["curr_end"])
    prior_start: str | None = dates["prior_start"]
    prior_end:   str | None = dates["prior_end"]

    for name, account_id in targets.items():
        try:
            curr_ads  = pull_ad_metrics(account_id, curr_start, curr_end, args.top)
            prior_ads = (pull_ad_metrics(account_id, str(prior_start), str(prior_end), args.top)
                         if prior_start and prior_end else {})
            counts = print_account(name, account_id, curr_ads, prior_ads, args.flags_only)
            for k in total_counts:
                total_counts[k] += counts.get(k, 0)
        except Exception as e:
            errored.append(name)
            print(f"\n❌  {name} ({account_id}) — Error: {e}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  Accounts checked: {len(targets) - len(errored)}/{len(targets)}")
    print(f"  🚨 Critical:  {total_counts['critical']} ad(s)")
    print(f"  ⚠️  Warnings:  {total_counts['warning']} ad(s)")
    print(f"  ✅ Wins:      {total_counts['win']} ad(s)")
    print(f"  ➡️   Stable:   {total_counts['stable']} ad(s)")
    if total_counts.get("new", 0):
        print(f"  🆕 New:       {total_counts['new']} ad(s)")
    if errored:
        print(f"  ❌ Errored:   {', '.join(errored)}")
    print("="*60)


if __name__ == "__main__":
    main()
