"""
Campaign Performance Snapshot
Purpose: Clean period-over-period performance table across all (or one) client
         accounts. Compares current vs prior period for all active campaigns and
         flags significant changes — drops, spikes, and wins.

         Conversions are filtered to real business outcomes only:
           - Purchases (online + offline/store sales)
           - Phone call leads
           - Lead form submissions and contact requests
         Store visits, Get Directions, page views, and micro-conversions are
         EXCLUDED from all conversion counts, CPA, and ROAS calculations.

         Designed as the data layer for /weekly-check and /monthly-report skills,
         and as a baseline feed for anomaly detection.

Setup:
    Requires environment variables:
        GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET,
        GOOGLE_ADS_REFRESH_TOKEN, GOOGLE_ADS_CUSTOMER_ID

Usage:
    python3 scripts/campaign_performance_snapshot.py                            # all clients, weekly
    python3 scripts/campaign_performance_snapshot.py --mode monthly             # MoM comparison
    python3 scripts/campaign_performance_snapshot.py --customer-id 5544702166   # single client
    python3 scripts/campaign_performance_snapshot.py --flags-only               # only flagged campaigns

Modes:
    weekly   (default)  Current 7 days vs prior 7 days
    monthly             Current 30 days vs prior 30 days

Conversion Buckets:
    🛒 Purchases   PURCHASE, STORE_SALE
                   → Cost per Purchase, Revenue, ROAS
    📞 Phone Calls PHONE_CALL_LEAD
                   → Cost per Call
    📋 Leads       SUBMIT_LEAD_FORM, LEAD, CONTACT, REQUEST_QUOTE,
                   BOOK_APPOINTMENT, QUALIFIED_LEAD, CONVERTED_LEAD,
                   IMPORT_LEAD, SIGNUP, REQUEST_APPOINTMENT
                   → Cost per Lead
    ❌ Excluded    GET_DIRECTIONS, STORE_VISIT, PAGE_VIEW, ENGAGEMENT,
                   ADD_TO_CART, BEGIN_CHECKOUT, DOWNLOAD, OUTBOUND_CLICK

Change Flags (based on total real conversions):
    🚨 CRITICAL  Conversions ▼>40%  |  CPA ▲>50%
    ⚠️  WARNING   Conversions ▼>20%  |  CPA ▲>25%  |  CTR ▼>20%  |  Cost ▲>25%
    ✅ WIN        Conversions ▲>20%  |  CPA ▼>20%  |  Cost ▼>20% with stable conv
    ➡️  STABLE    All metrics within ±20%

Changelog:
    2026-03-19  Initial version — WoW/MoM, delta flags, per-campaign table.
    2026-03-19  Conversion filtering: only purchases, phone calls, and leads
                count as conversions. Added CPCall, CPL, CPPurchase, Revenue,
                ROAS. Excluded store visits, directions, micro-conversions.
"""

import argparse
import os
from datetime import date, timedelta
from collections import defaultdict
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# ─── CLIENT REGISTRY ─────────────────────────────────────────────────────────

ALL_CLIENTS = {
    "Anand Desai Law Firm":                 "5865660247",
    "Dentiste":                             "3857223862",
    "Estate Jewelry Priced Right":          "7709532223",
    "FaBesthetics":                         "9304117954",
    "GDM Google Ads":                       "7087867966",
    "Hoski.ca":                             "5544702166",
    "New Norseman":                         "3720173680",
    "Park Road Custom Furniture and Decor": "7228467515",
    "Serenity Familycare":                  "8134824884",
    "Synergy Spine & Nerve Center":         "7628667762",
    "Texas FHC":                            "8159668041",
    "Voit Dental (1)":                      "5216656756",
    "Voit Dental (2)":                      "5907367258",
}

# ─── CONVERSION CATEGORY BUCKETS ─────────────────────────────────────────────

PURCHASE_CATEGORIES = {
    "PURCHASE",
    "STORE_SALE",           # offline/in-store sales (distinct from STORE_VISIT)
}

PHONE_CATEGORIES = {
    "PHONE_CALL_LEAD",
}

LEAD_CATEGORIES = {
    "LEAD",
    "SUBMIT_LEAD_FORM",
    "CONTACT",
    "REQUEST_QUOTE",
    "BOOK_APPOINTMENT",
    "QUALIFIED_LEAD",
    "CONVERTED_LEAD",
    "IMPORT_LEAD",
    "SIGNUP",
    "REQUEST_APPOINTMENT",
}

# These are explicitly excluded — not counted as business conversions
EXCLUDED_CATEGORIES = {
    "GET_DIRECTIONS",
    "STORE_VISIT",
    "PAGE_VIEW",
    "ENGAGEMENT",
    "ADD_TO_CART",
    "BEGIN_CHECKOUT",
    "DOWNLOAD",
    "OUTBOUND_CLICK",
    "OFFER_IMPRESSION",
    "LOGIN",
}

# ─── CHANGE THRESHOLDS ────────────────────────────────────────────────────────

CRIT_CONV_DROP   = -0.40
WARN_CONV_DROP   = -0.20
WIN_CONV_GAIN    =  0.20
WARN_CPA_RISE    =  0.25
CRIT_CPA_RISE    =  0.50
WIN_CPA_DROP     = -0.20
WARN_CTR_DROP    = -0.20
WARN_COST_RISE   =  0.25
WIN_COST_DROP    = -0.20

# ─── SETUP ───────────────────────────────────────────────────────────────────

def build_client():
    return GoogleAdsClient.load_from_dict({
        "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "login_customer_id": os.environ["GOOGLE_ADS_CUSTOMER_ID"],
        "use_proto_plus": True
    })

def run_query(ga_service, customer_id, query):
    try:
        return list(ga_service.search(customer_id=customer_id, query=query))
    except GoogleAdsException as ex:
        for error in ex.failure.errors:
            print(f"    [API Error] {error.message}")
        return []


# ─── DATE RANGES ─────────────────────────────────────────────────────────────

def get_date_ranges(mode):
    today = date.today()

    if mode == "weekly":
        curr_end    = today - timedelta(days=1)
        curr_start  = curr_end - timedelta(days=6)
        label       = "Week-over-Week (rolling 7 days)"

    elif mode == "calendar-week":
        # Last completed Sun–Sat week
        # Python weekday(): Mon=0 … Sun=6. Saturday=5.
        days_since_sat = (today.weekday() - 5) % 7  # days elapsed since last Saturday
        if days_since_sat == 0:
            days_since_sat = 7  # today IS Saturday → use the previous one
        curr_end   = today - timedelta(days=days_since_sat)        # last Saturday
        curr_start = curr_end - timedelta(days=6)                  # prior Sunday
        label      = f"Calendar Week  {curr_start.strftime('%a %b %d')} – {curr_end.strftime('%a %b %d, %Y')}"

    else:  # monthly
        curr_end    = today - timedelta(days=1)
        curr_start  = curr_end - timedelta(days=29)
        label       = "Month-over-Month (30 days)"

    prior_end   = curr_start - timedelta(days=1)
    prior_start = prior_end - timedelta(days=(curr_end - curr_start).days)

    return {
        "curr_start":  curr_start.strftime("%Y-%m-%d"),
        "curr_end":    curr_end.strftime("%Y-%m-%d"),
        "prior_start": prior_start.strftime("%Y-%m-%d"),
        "prior_end":   prior_end.strftime("%Y-%m-%d"),
        "label":       label,
    }


# ─── PULL ────────────────────────────────────────────────────────────────────

def pull_base_metrics(ga_service, customer_id, start, end):
    """Pull impressions, clicks, cost per campaign for the date range.
    Includes ALL campaigns regardless of current status — a paused campaign
    may still have spend from earlier in the reporting window."""
    rows = run_query(ga_service, customer_id, f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign.bidding_strategy_type,
            campaign_budget.amount_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros
        FROM campaign
        WHERE segments.date BETWEEN '{start}' AND '{end}'
          AND metrics.impressions > 0
        ORDER BY metrics.cost_micros DESC
    """)

    campaigns = {}
    for row in rows:
        c   = row.campaign
        m   = row.metrics
        cid = str(c.id)
        if cid not in campaigns:
            campaigns[cid] = {
                "id":           cid,
                "name":         c.name,
                "status":       c.status.name,       # ENABLED or PAUSED
                "channel":      c.advertising_channel_type.name,
                "bidding":      c.bidding_strategy_type.name,
                "daily_budget": row.campaign_budget.amount_micros / 1_000_000,
                "impressions":  0,
                "clicks":       0,
                "cost":         0.0,
                # conversion buckets — filled by pull_conversion_breakdown()
                "purchase_conv":  0.0,
                "purchase_value": 0.0,
                "phone_conv":     0.0,
                "lead_conv":      0.0,
                "excluded_conv":  0.0,
            }
        campaigns[cid]["impressions"] += m.impressions
        campaigns[cid]["clicks"]      += m.clicks
        campaigns[cid]["cost"]        += m.cost_micros / 1_000_000

    return campaigns


def pull_conversion_breakdown(ga_service, customer_id, start, end):
    """
    Pull conversion counts segmented by action category.
    Returns dict: campaign_id → {category: (conv, value)}
    """
    rows = run_query(ga_service, customer_id, f"""
        SELECT
            campaign.id,
            segments.conversion_action_category,
            metrics.conversions,
            metrics.conversions_value
        FROM campaign
        WHERE segments.date BETWEEN '{start}' AND '{end}'
    """)

    breakdown = defaultdict(lambda: defaultdict(lambda: {"conv": 0.0, "value": 0.0}))
    for row in rows:
        cid      = str(row.campaign.id)
        category = row.segments.conversion_action_category.name
        breakdown[cid][category]["conv"]  += row.metrics.conversions
        breakdown[cid][category]["value"] += row.metrics.conversions_value

    return breakdown


def merge_conversions(campaigns, breakdown):
    """Apply categorized conversion counts into each campaign record."""
    for cid, camp in campaigns.items():
        cat_data = breakdown.get(cid, {})
        for category, vals in cat_data.items():
            if category in PURCHASE_CATEGORIES:
                camp["purchase_conv"]  += vals["conv"]
                camp["purchase_value"] += vals["value"]
            elif category in PHONE_CATEGORIES:
                camp["phone_conv"] += vals["conv"]
            elif category in LEAD_CATEGORIES:
                camp["lead_conv"] += vals["conv"]
            elif category in EXCLUDED_CATEGORIES:
                camp["excluded_conv"] += vals["conv"]
            # UNKNOWN / UNSPECIFIED / DEFAULT → not counted


def compute_derived(camp):
    """Compute derived metrics on a campaign dict (in-place)."""
    cost = camp["cost"]
    total_real = camp["purchase_conv"] + camp["phone_conv"] + camp["lead_conv"]

    camp["total_real_conv"] = total_real
    camp["ctr"]  = camp["clicks"] / camp["impressions"] if camp["impressions"] > 0 else 0.0
    camp["cpc"]  = cost / camp["clicks"]                if camp["clicks"]      > 0 else 0.0
    camp["cpa"]  = cost / total_real                    if total_real          > 0 else None
    camp["roas"] = camp["purchase_value"] / cost        if cost > 0 and camp["purchase_value"] > 0 else None

    camp["cost_per_call"]     = cost / camp["phone_conv"]    if camp["phone_conv"]    > 0 else None
    camp["cost_per_lead"]     = cost / camp["lead_conv"]     if camp["lead_conv"]     > 0 else None
    camp["cost_per_purchase"] = cost / camp["purchase_conv"] if camp["purchase_conv"] > 0 else None


def pull_campaign_metrics(ga_service, customer_id, start, end):
    campaigns = pull_base_metrics(ga_service, customer_id, start, end)
    breakdown  = pull_conversion_breakdown(ga_service, customer_id, start, end)
    merge_conversions(campaigns, breakdown)
    for camp in campaigns.values():
        compute_derived(camp)
    return campaigns


# ─── DELTA ───────────────────────────────────────────────────────────────────

def delta(curr, prior):
    if prior == 0:
        return None, None
    return curr - prior, (curr - prior) / abs(prior)


def fmt_delta(pct, invert=False, threshold=0.05):
    """Format a % delta with arrow. invert=True means higher = bad (e.g. CPA, cost)."""
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
    if not prior or prior.get("cost", 0) == 0:
        return "new", []

    flags  = []
    status = "stable"

    _, conv_pct = delta(curr["total_real_conv"], prior["total_real_conv"])
    _, cost_pct = delta(curr["cost"],            prior["cost"])
    _, ctr_pct  = delta(curr["ctr"],             prior["ctr"])

    cpa_pct = None
    if curr["cpa"] and prior.get("cpa"):
        _, cpa_pct = delta(curr["cpa"], prior["cpa"])

    # Critical
    if conv_pct is not None and conv_pct <= CRIT_CONV_DROP:
        flags.append(("CRITICAL", f"Conversions ▼{abs(conv_pct)*100:.0f}% ({prior['total_real_conv']:.0f} → {curr['total_real_conv']:.0f})"))
        status = "critical"
    if cpa_pct is not None and cpa_pct >= CRIT_CPA_RISE:
        flags.append(("CRITICAL", f"CPA ▲{cpa_pct*100:.0f}% (${prior['cpa']:.2f} → ${curr['cpa']:.2f})"))
        status = "critical"

    # Warnings
    if status != "critical":
        if conv_pct is not None and CRIT_CONV_DROP < conv_pct <= WARN_CONV_DROP:
            flags.append(("WARNING", f"Conversions ▼{abs(conv_pct)*100:.0f}% ({prior['total_real_conv']:.0f} → {curr['total_real_conv']:.0f})"))
            status = "warning"
        if cpa_pct is not None and WARN_CPA_RISE <= cpa_pct < CRIT_CPA_RISE:
            flags.append(("WARNING", f"CPA ▲{cpa_pct*100:.0f}% (${prior['cpa']:.2f} → ${curr['cpa']:.2f})"))
            status = "warning"
        if ctr_pct is not None and ctr_pct <= WARN_CTR_DROP:
            flags.append(("WARNING", f"CTR ▼{abs(ctr_pct)*100:.0f}% ({prior['ctr']*100:.2f}% → {curr['ctr']*100:.2f}%)"))
            status = "warning"
        if cost_pct is not None and cost_pct >= WARN_COST_RISE:
            flags.append(("WARNING", f"Cost ▲{cost_pct*100:.0f}% (${prior['cost']:.2f} → ${curr['cost']:.2f})"))
            status = "warning"

    # Wins
    if status == "stable":
        if conv_pct is not None and conv_pct >= WIN_CONV_GAIN:
            flags.append(("WIN", f"Conversions ▲{conv_pct*100:.0f}% ({prior['total_real_conv']:.0f} → {curr['total_real_conv']:.0f})"))
            status = "win"
        if cpa_pct is not None and cpa_pct <= WIN_CPA_DROP:
            flags.append(("WIN", f"CPA ▼{abs(cpa_pct)*100:.0f}% (${prior['cpa']:.2f} → ${curr['cpa']:.2f})"))
            status = "win"
        if cost_pct is not None and cost_pct <= WIN_COST_DROP and (conv_pct is None or conv_pct >= -0.05):
            flags.append(("WIN", f"Cost ▼{abs(cost_pct)*100:.0f}% (${prior['cost']:.2f} → ${curr['cost']:.2f}) with stable conversions"))
            status = "win"

    return status, flags


# ─── PRINT ───────────────────────────────────────────────────────────────────

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

    # ── Traffic metrics ──────────────────────────────────────────────────────
    cost  = curr["cost"]
    impr  = curr["impressions"]

    # ── Deltas ───────────────────────────────────────────────────────────────
    has_prior = prior and prior.get("cost", 0) > 0
    if has_prior:
        _, cost_d = delta(curr["cost"],           prior.get("cost", 0))
        _, conv_d = delta(curr["total_real_conv"], prior.get("total_real_conv", 0))
        _, ctr_d  = delta(curr["ctr"],            prior.get("ctr", 0))
        cost_delta = fmt_delta(cost_d, invert=True)
        conv_delta = fmt_delta(conv_d)
        ctr_delta  = fmt_delta(ctr_d)
        prior_cost_str = f"prior: ${prior['cost']:.2f}, "
        prior_conv_str = f"prior: {prior['total_real_conv']:.0f}, "
        prior_ctr_str  = f"prior: {prior['ctr']*100:.2f}%, "
        if curr["cpa"] and prior.get("cpa"):
            _, cpa_d   = delta(curr["cpa"], prior["cpa"])
            cpa_delta  = fmt_delta(cpa_d, invert=True)
            prior_cpa_str = f"prior: ${prior['cpa']:.2f}, "
        else:
            cpa_delta = "n/a"
            prior_cpa_str = ""
    else:
        cost_delta = conv_delta = ctr_delta = cpa_delta = "new"
        prior_cost_str = prior_conv_str = prior_ctr_str = prior_cpa_str = ""

    # ── Conversion breakdown ─────────────────────────────────────────────────
    purchase_conv  = curr["purchase_conv"]
    purchase_value = curr["purchase_value"]
    phone_conv     = curr["phone_conv"]
    lead_conv      = curr["lead_conv"]
    total_conv     = curr["total_real_conv"]
    excl_conv      = curr["excluded_conv"]

    cpa_str  = f"${curr['cpa']:.2f}"              if curr["cpa"]              else "—"
    roas_str = f"{curr['roas']:.2f}x"             if curr["roas"]             else "—"
    cpp_str  = f"${curr['cost_per_purchase']:.2f}" if curr["cost_per_purchase"] else "—"
    cpc_call = f"${curr['cost_per_call']:.2f}"     if curr["cost_per_call"]     else "—"
    cpl_str  = f"${curr['cost_per_lead']:.2f}"     if curr["cost_per_lead"]     else "—"
    rev_str  = f"${purchase_value:.2f}"            if purchase_value > 0        else "—"
    ctr_str  = f"{curr['ctr']*100:.2f}%"
    cpc_str  = f"${curr['cpc']:.2f}"

    status_label = "⏸ PAUSED" if curr.get("status") == "PAUSED" else "▶ ENABLED"
    print(f"\n      {icon}  {curr['name']}  [{status_label}]")
    print(f"           Spend: ${cost:.2f} ({prior_cost_str}{cost_delta})  |  Conv: {total_conv:.0f} ({prior_conv_str}{conv_delta})  |  CPA: {cpa_str} ({prior_cpa_str}{cpa_delta})")
    print(f"           📞 Calls: {phone_conv:.0f}  |  Cost/Call: {cpc_call}    📋 Leads: {lead_conv:.0f}  |  CPL: {cpl_str}    🛒 Purchases: {purchase_conv:.0f}  |  CPP: {cpp_str}  |  Revenue: {rev_str}  |  ROAS: {roas_str}")
    print(f"           Impr: {impr:,}  |  CTR: {ctr_str} ({prior_ctr_str}{ctr_delta})  |  CPC: {cpc_str}  |  Budget: ${curr['daily_budget']:.2f}/day  |  Bidding: {curr['bidding']}")
    if excl_conv > 0:
        print(f"           ⛔ Excluded (directions/visits/micro): {excl_conv:.0f} — not counted")

    for level, msg in flags:
        flag_icon = "🚨" if level == "CRITICAL" else ("⚠️ " if level == "WARNING" else "✅")
        print(f"           {flag_icon}  {msg}")


def print_account(client_name, customer_id, curr_camps, prior_camps, flags_only) -> dict[str, int]:
    empty: dict[str, int] = {"critical": 0, "warning": 0, "win": 0, "stable": 0, "new": 0}
    if not curr_camps:
        print(f"\n⬜  {client_name} ({customer_id}) — No active campaigns")
        return empty

    classified = {}
    for cid, curr in curr_camps.items():
        prior  = prior_camps.get(cid)
        status, flags = classify_campaign(curr, prior)
        classified[cid] = (status, flags, curr, prior)

    counts: dict[str, int] = {"critical": 0, "warning": 0, "win": 0, "stable": 0, "new": 0}
    for _, (status, _, _, _) in classified.items():
        s = str(status)
        if s in counts:
            counts[s] += 1

    # Account rollup
    curr_cost  = sum(c["cost"]            for c in curr_camps.values())
    curr_conv  = sum(c["total_real_conv"] for c in curr_camps.values())
    curr_rev   = sum(c["purchase_value"]  for c in curr_camps.values())
    curr_calls = sum(c["phone_conv"]      for c in curr_camps.values())
    curr_leads = sum(c["lead_conv"]       for c in curr_camps.values())
    curr_purch = sum(c["purchase_conv"]   for c in curr_camps.values())

    prior_cost  = sum(c["cost"]            for c in prior_camps.values()) if prior_camps else 0
    prior_conv  = sum(c["total_real_conv"] for c in prior_camps.values()) if prior_camps else 0
    prior_calls = sum(c["phone_conv"]      for c in prior_camps.values()) if prior_camps else 0
    prior_leads = sum(c["lead_conv"]       for c in prior_camps.values()) if prior_camps else 0
    prior_purch = sum(c["purchase_conv"]   for c in prior_camps.values()) if prior_camps else 0
    prior_rev   = sum(c["purchase_value"]  for c in prior_camps.values()) if prior_camps else 0

    _, cost_pct = delta(curr_cost, prior_cost)
    _, conv_pct = delta(curr_conv, prior_conv)

    acct_cpa  = curr_cost / curr_conv if curr_conv > 0 else None
    acct_roas = curr_rev  / curr_cost if curr_cost > 0 and curr_rev > 0 else None

    if counts["critical"] > 0:
        account_icon = "🚨"
    elif counts["warning"] > 0:
        account_icon = "⚠️ "
    elif counts["win"] > 0:
        account_icon = "✅"
    else:
        account_icon = "➡️ "

    active_count = sum(1 for c in curr_camps.values() if c.get("status") == "ENABLED")
    paused_count = len(curr_camps) - active_count
    camp_label   = f"{len(curr_camps)} campaign(s) ({active_count} active, {paused_count} paused)" if paused_count > 0 else f"{len(curr_camps)} campaign(s)"

    prior_cost_str = f"prior: ${prior_cost:.2f}, " if prior_cost > 0 else ""
    prior_conv_str = f"prior: {prior_conv:.0f}, "  if prior_cost > 0 else ""

    print(f"\n{account_icon}  {client_name} ({customer_id})")
    print(f"    {camp_label}  |  "
          f"Spend: ${curr_cost:.2f} ({prior_cost_str}{fmt_delta(cost_pct, invert=True)})  |  "
          f"Conv: {curr_conv:.0f} ({prior_conv_str}{fmt_delta(conv_pct)})  |  "
          f"CPA: {f'${acct_cpa:.2f}' if acct_cpa else '—'}  |  "
          f"ROAS: {f'{acct_roas:.2f}x' if acct_roas else '—'}")
    print(f"    📞 Calls: {curr_calls:.0f} (prior: {prior_calls:.0f})  |  "
          f"📋 Leads: {curr_leads:.0f} (prior: {prior_leads:.0f})  |  "
          f"🛒 Purchases: {curr_purch:.0f} (prior: {prior_purch:.0f})  |  "
          f"Revenue: {'$' + f'{curr_rev:.2f}' if curr_rev > 0 else '—'} (prior: {'$' + f'{prior_rev:.2f}' if prior_rev > 0 else '—'})")

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
            classified.items(), key=lambda x: x[1][2]["cost"], reverse=True
        ):
            print_campaign_row(curr, prior)

    return counts


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Campaign performance snapshot — period-over-period with filtered conversion types"
    )
    parser.add_argument("--customer-id",  help="Single account ID (omit to run all clients)")
    parser.add_argument("--client-name",  help="Display name when using --customer-id")
    parser.add_argument("--mode",         choices=["weekly", "calendar-week", "monthly"], default="weekly",
                        help="weekly (rolling 7d), calendar-week (last Sun–Sat vs prior Sun–Sat), monthly (30d). Default: weekly")
    parser.add_argument("--flags-only",   action="store_true",
                        help="Only show campaigns with significant changes")
    args = parser.parse_args()

    client     = build_client()
    ga_service = client.get_service("GoogleAdsService")
    dates      = get_date_ranges(args.mode)

    if args.customer_id:
        targets = {(args.client_name or args.customer_id): args.customer_id.replace("-", "")}
    else:
        targets = ALL_CLIENTS

    print("\n" + "="*60)
    print(f"CAMPAIGN PERFORMANCE SNAPSHOT — {args.mode.upper()}")
    print(f"{dates['label']}")
    print(f"Current:  {dates['curr_start']} → {dates['curr_end']}")
    print(f"Prior:    {dates['prior_start']} → {dates['prior_end']}")
    print("Conversions: purchases · phone calls · lead forms only")
    if args.flags_only:
        print("Mode: Flagged campaigns only")
    print("="*60)

    total_counts: dict[str, int] = {"critical": 0, "warning": 0, "win": 0, "stable": 0, "new": 0}
    errored: list[str] = []

    for name, cid in targets.items():
        try:
            curr_camps  = pull_campaign_metrics(ga_service, cid, dates["curr_start"],  dates["curr_end"])
            prior_camps = pull_campaign_metrics(ga_service, cid, dates["prior_start"], dates["prior_end"])
            counts = print_account(name, cid, curr_camps, prior_camps, args.flags_only)
            for k in ("critical", "warning", "win", "stable", "new"):
                total_counts[k] += counts.get(k, 0)
        except Exception as e:
            errored.append(name)
            print(f"\n❌  {name} ({cid}) — Error: {e}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  Accounts checked: {len(targets) - len(errored)}/{len(targets)}")
    print(f"  🚨 Critical drops:  {total_counts['critical']} campaign(s)")
    print(f"  ⚠️  Warnings:        {total_counts['warning']} campaign(s)")
    print(f"  ✅ Wins:             {total_counts['win']} campaign(s)")
    print(f"  ➡️   Stable:          {total_counts['stable']} campaign(s)")
    if total_counts.get("new", 0):
        print(f"  🆕 New (no prior):  {total_counts['new']} campaign(s)")
    if errored:
        print(f"  ❌ Errored:         {', '.join(errored)}")
    print("="*60)


if __name__ == "__main__":
    main()
