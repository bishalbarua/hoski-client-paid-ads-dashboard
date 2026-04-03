"""
New Norseman — Live Google Ads Audit
Account: 3720173680 (MCC: 4781259815)

Pulls:
  1. Campaign performance — last 7 days vs prior 7 days (WoW)
  2. Conversion breakdown by action name + category (calls, leads, purchases, excluded)
  3. Impression share lost to budget and rank (per campaign)
  4. Keyword performance — top spenders, zero-conv waste, quality scores
  5. Search terms — top by spend (last 7 days), zero-conv waste flagged
  6. Conversion action list — all actions, status, category (for tracking audit)

Usage:
    cd "Google Ads Manager"
    python3 "clients/New Norseman (3720173680)/norseman_live_audit.py"
    python3 "clients/New Norseman (3720173680)/norseman_live_audit.py" --days 14

Changelog:
    2026-04-04  Initial version — live audit for lead volume decline investigation.
"""

import argparse
import os
from collections import defaultdict
from datetime import date, timedelta

from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

load_dotenv()

# ─── CONFIG ──────────────────────────────────────────────────────────────────

CUSTOMER_ID = "3720173680"
CLIENT_NAME = "New Norseman"

# Conversion categories — mirrors google_campaign_performance_snapshot.py
PURCHASE_CATS = {"PURCHASE", "STORE_SALE"}
PHONE_CATS    = {"PHONE_CALL_LEAD"}
LEAD_CATS     = {
    "LEAD", "SUBMIT_LEAD_FORM", "CONTACT", "REQUEST_QUOTE",
    "BOOK_APPOINTMENT", "QUALIFIED_LEAD", "CONVERTED_LEAD",
    "IMPORT_LEAD", "SIGNUP", "REQUEST_APPOINTMENT",
}
EXCLUDED_CATS = {
    "GET_DIRECTIONS", "STORE_VISIT", "PAGE_VIEW", "ENGAGEMENT",
    "ADD_TO_CART", "BEGIN_CHECKOUT", "DOWNLOAD", "OUTBOUND_CLICK",
    "OFFER_IMPRESSION", "LOGIN",
}

# Waste threshold: flag keywords with spend >= this and 0 conversions
WASTE_SPEND_THRESHOLD = 50.0   # $50+

# ─── ARGS ────────────────────────────────────────────────────────────────────

parser = argparse.ArgumentParser(description="New Norseman live Google Ads audit")
parser.add_argument("--days", type=int, default=7,
                    help="Current period length in days (default: 7 for WoW)")
args = parser.parse_args()

DAYS = args.days
today         = date.today()
curr_end      = today - timedelta(days=1)
curr_start    = curr_end - timedelta(days=DAYS - 1)
prior_end     = curr_start - timedelta(days=1)
prior_start   = prior_end - timedelta(days=DAYS - 1)

CURR_RANGE  = f"BETWEEN '{curr_start}' AND '{curr_end}'"
PRIOR_RANGE = f"BETWEEN '{prior_start}' AND '{prior_end}'"

# Extended lookback for search terms and keywords (more data = better signal)
EXTENDED_START = today - timedelta(days=30)
EXTENDED_RANGE = f"BETWEEN '{EXTENDED_START}' AND '{curr_end}'"

# ─── CLIENT ──────────────────────────────────────────────────────────────────

client = GoogleAdsClient.load_from_dict({
    "developer_token":   os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
    "client_id":         os.environ["GOOGLE_ADS_CLIENT_ID"],
    "client_secret":     os.environ["GOOGLE_ADS_CLIENT_SECRET"],
    "refresh_token":     os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
    "login_customer_id": os.environ["GOOGLE_ADS_CUSTOMER_ID"],
    "use_proto_plus":    True,
})
ga_service = client.get_service("GoogleAdsService")


def run_query(query, label=""):
    try:
        return list(ga_service.search(customer_id=CUSTOMER_ID, query=query))
    except GoogleAdsException as ex:
        for err in ex.failure.errors:
            print(f"  [API Error{' — ' + label if label else ''}] {err.message}")
        return []


def pct_delta(curr, prior):
    if prior == 0:
        return None
    return (curr - prior) / abs(prior)


def fmt_pct(val, invert=False):
    """Format a percentage delta with direction and warning flag."""
    if val is None:
        return "new"
    arrow = "▲" if val > 0 else "▼"
    sign  = "+" if val > 0 else ""
    num   = f"{sign}{val*100:.1f}%"
    bad   = (invert and val > 0.10) or (not invert and val < -0.10)
    good  = (invert and val < -0.10) or (not invert and val > 0.10)
    tag   = " ⚠" if bad else (" ✅" if good else "")
    return f"{arrow}{num}{tag}"


def sep(char="─", width=70):
    print(char * width)


# ─── HEADER ──────────────────────────────────────────────────────────────────

print()
sep("=")
print(f"LIVE GOOGLE ADS AUDIT — {CLIENT_NAME} ({CUSTOMER_ID})")
print(f"Current:  {curr_start} → {curr_end}  ({DAYS} days)")
print(f"Prior:    {prior_start} → {prior_end}  ({DAYS} days)")
print(f"Extended: {EXTENDED_START} → {curr_end}  (30 days, for keywords + search terms)")
sep("=")


# ─── 1. CAMPAIGN PERFORMANCE — WoW ──────────────────────────────────────────

def pull_campaign_base(date_range):
    rows = run_query(f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign.bidding_strategy_type,
            campaign_budget.amount_micros,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.search_impression_share,
            metrics.search_budget_lost_impression_share,
            metrics.search_rank_lost_impression_share,
            metrics.search_top_impression_share
        FROM campaign
        WHERE segments.date {date_range}
          AND metrics.impressions > 0
        ORDER BY metrics.cost_micros DESC
    """, "campaign base")

    camps = {}
    for row in rows:
        c   = row.campaign
        m   = row.metrics
        b   = row.campaign_budget
        cid = str(c.id)
        if cid not in camps:
            camps[cid] = {
                "id":           cid,
                "name":         c.name,
                "status":       c.status.name,
                "channel":      c.advertising_channel_type.name,
                "bidding":      c.bidding_strategy_type.name,
                "daily_budget": b.amount_micros / 1_000_000,
                "impressions":  0,
                "clicks":       0,
                "cost":         0.0,
                "is_pmax":      c.advertising_channel_type.name == "PERFORMANCE_MAX",
                # impression share (last row wins — acceptable for daily aggregation)
                "impr_share":         m.search_impression_share,
                "budget_lost_is":     m.search_budget_lost_impression_share,
                "rank_lost_is":       m.search_rank_lost_impression_share,
                "top_is":             m.search_top_impression_share,
                # conversion buckets
                "purchase_conv":  0.0,
                "phone_conv":     0.0,
                "lead_conv":      0.0,
                "excluded_conv":  0.0,
                "purchase_value": 0.0,
            }
        camps[cid]["impressions"] += m.impressions
        camps[cid]["clicks"]      += m.clicks
        camps[cid]["cost"]        += m.cost_micros / 1_000_000
        # Update IS metrics with latest row
        camps[cid]["impr_share"]      = m.search_impression_share
        camps[cid]["budget_lost_is"]  = m.search_budget_lost_impression_share
        camps[cid]["rank_lost_is"]    = m.search_rank_lost_impression_share
        camps[cid]["top_is"]          = m.search_top_impression_share
    return camps


def pull_conv_breakdown(date_range):
    rows = run_query(f"""
        SELECT
            campaign.id,
            segments.conversion_action_name,
            segments.conversion_action_category,
            metrics.conversions,
            metrics.conversions_value
        FROM campaign
        WHERE segments.date {date_range}
    """, "conv breakdown")

    breakdown = defaultdict(lambda: defaultdict(lambda: {"conv": 0.0, "value": 0.0, "name": ""}))
    for row in rows:
        cid  = str(row.campaign.id)
        cat  = row.segments.conversion_action_category.name
        name = row.segments.conversion_action_name
        breakdown[cid][cat]["conv"]  += row.metrics.conversions
        breakdown[cid][cat]["value"] += row.metrics.conversions_value
        breakdown[cid][cat]["name"]   = name
    return breakdown


def merge_convs(camps, breakdown):
    for cid, camp in camps.items():
        for cat, vals in breakdown.get(cid, {}).items():
            if cat in PURCHASE_CATS:
                camp["purchase_conv"]  += vals["conv"]
                camp["purchase_value"] += vals["value"]
            elif cat in PHONE_CATS:
                camp["phone_conv"] += vals["conv"]
            elif cat in LEAD_CATS:
                camp["lead_conv"] += vals["conv"]
            elif cat in EXCLUDED_CATS:
                camp["excluded_conv"] += vals["conv"]


def compute_derived(camp):
    cost = camp["cost"]
    clicks = camp["clicks"]
    impr   = camp["impressions"]
    total  = camp["purchase_conv"] + camp["phone_conv"] + camp["lead_conv"]
    camp["total_real_conv"] = total
    camp["ctr"] = clicks / impr  if impr  > 0 else 0.0
    camp["cpc"] = cost / clicks  if clicks > 0 else 0.0
    camp["cpa"] = cost / total   if total  > 0 else None
    camp["cvr"] = total / clicks if clicks > 0 else 0.0


def pull_full(date_range):
    camps = pull_campaign_base(date_range)
    bd    = pull_conv_breakdown(date_range)
    merge_convs(camps, bd)
    for c in camps.values():
        compute_derived(c)
    return camps


curr_camps  = pull_full(CURR_RANGE)
prior_camps = pull_full(PRIOR_RANGE)

print()
sep("=")
print("1. CAMPAIGN PERFORMANCE — WEEK-OVER-WEEK")
sep("=")

for cid, c in sorted(curr_camps.items(), key=lambda x: x[1]["cost"], reverse=True):
    p = prior_camps.get(cid, {})
    p_cost  = p.get("cost", 0)
    p_conv  = p.get("total_real_conv", 0)
    p_ctr   = p.get("ctr", 0)
    p_cpa   = p.get("cpa")

    cost_d  = fmt_pct(pct_delta(c["cost"], p_cost), invert=True)
    conv_d  = fmt_pct(pct_delta(c["total_real_conv"], p_conv))
    ctr_d   = fmt_pct(pct_delta(c["ctr"], p_ctr))
    cpa_d   = fmt_pct(pct_delta(c["cpa"], p_cpa) if c["cpa"] and p_cpa else None, invert=True)

    cpa_str = f"${c['cpa']:.2f}"  if c["cpa"] else "—"
    cpl_str = f"${c['cost'] / c['lead_conv']:.2f}" if c["lead_conv"] > 0 else "—"

    # Impression share strings (PMax doesn't report search IS)
    if c["is_pmax"]:
        is_str = "IS: N/A (PMax)"
    else:
        is_val       = c["impr_share"]
        bud_lost     = c["budget_lost_is"]
        rank_lost    = c["rank_lost_is"]
        is_str = (
            f"IS: {is_val*100:.1f}%  "
            f"Lost-Budget: {bud_lost*100:.1f}%  "
            f"Lost-Rank: {rank_lost*100:.1f}%"
        )

    print(f"\n  {'⏸' if c['status'] == 'PAUSED' else '▶'} {c['name']}  [{c['status']}]")
    print(f"     Channel: {c['channel']} | Bidding: {c['bidding']} | Budget: ${c['daily_budget']:.0f}/day")
    print(f"     Spend:  ${c['cost']:.2f} (prior: ${p_cost:.2f}, {cost_d})")
    print(f"     Conv:   {c['total_real_conv']:.0f} real (prior: {p_conv:.0f}, {conv_d})")
    print(f"       📞 Calls: {c['phone_conv']:.0f}  |  📋 Leads: {c['lead_conv']:.0f}  |  🛒 Purchases: {c['purchase_conv']:.0f}")
    print(f"       ⛔ Excluded (not counted): {c['excluded_conv']:.0f}")
    print(f"     CPA: {cpa_str} ({cpa_d})  |  CPL: {cpl_str}")
    print(f"     CTR: {c['ctr']*100:.2f}% (prior: {p_ctr*100:.2f}%, {ctr_d})  |  CPC: ${c['cpc']:.2f}")
    print(f"     Impr: {c['impressions']:,}  |  Clicks: {c['clicks']:,}")
    print(f"     {is_str}")

# Account rollup
print()
sep()
curr_total_spend = sum(c["cost"] for c in curr_camps.values())
curr_total_conv  = sum(c["total_real_conv"] for c in curr_camps.values())
curr_total_leads = sum(c["lead_conv"] for c in curr_camps.values())
curr_total_calls = sum(c["phone_conv"] for c in curr_camps.values())
prior_total_spend = sum(p.get("cost", 0) for p in prior_camps.values())
prior_total_conv  = sum(p.get("total_real_conv", 0) for p in prior_camps.values())
acct_cpa = curr_total_spend / curr_total_conv if curr_total_conv > 0 else None

print(f"  ACCOUNT TOTAL — Current {DAYS}d")
print(f"  Spend: ${curr_total_spend:.2f} (prior: ${prior_total_spend:.2f}, {fmt_pct(pct_delta(curr_total_spend, prior_total_spend), invert=True)})")
print(f"  Real Conv: {curr_total_conv:.0f} (prior: {prior_total_conv:.0f}, {fmt_pct(pct_delta(curr_total_conv, prior_total_conv))})")
print(f"  Blended CPL: {f'${acct_cpa:.2f}' if acct_cpa else '—'}   |  Calls: {curr_total_calls:.0f}  |  Leads: {curr_total_leads:.0f}")
sep()


# ─── 2. CONVERSION ACTION AUDIT ──────────────────────────────────────────────

print()
sep("=")
print("2. CONVERSION ACTION AUDIT (all actions + what's counting)")
sep("=")

ca_rows = run_query(f"""
    SELECT
        conversion_action.id,
        conversion_action.name,
        conversion_action.category,
        conversion_action.type,
        conversion_action.status,
        conversion_action.counting_type,
        conversion_action.include_in_conversions_metric,
        conversion_action.primary_for_goal
    FROM conversion_action
    ORDER BY conversion_action.category, conversion_action.name
""", "conversion actions")

for row in ca_rows:
    ca = row.conversion_action
    primary = getattr(ca, "primary_for_goal", None)
    in_metric = ca.include_in_conversions_metric
    status = ca.status.name
    cat = ca.category.name
    bucket = (
        "PURCHASE"  if cat in PURCHASE_CATS else
        "PHONE"     if cat in PHONE_CATS    else
        "LEAD"      if cat in LEAD_CATS     else
        "EXCLUDED"  if cat in EXCLUDED_CATS else
        "UNKNOWN"
    )
    warn = ""
    if bucket == "EXCLUDED" and in_metric:
        warn = "  ⚠ EXCLUDED CATEGORY BUT COUNTING IN CONV METRIC"
    if bucket == "UNKNOWN":
        warn = "  ⚠ UNRECOGNIZED CATEGORY — AUDIT MANUALLY"

    print(f"\n  [{status}] {ca.name}")
    print(f"    Category: {cat} → Bucket: {bucket}")
    print(f"    Type: {ca.type_.name}  |  Counting: {ca.counting_type.name}")
    print(f"    Include in 'Conversions' metric: {in_metric}  |  Primary for goal: {primary}{warn}")


# ─── 3. IMPRESSION SHARE SUMMARY ─────────────────────────────────────────────

print()
sep("=")
print("3. IMPRESSION SHARE — BUDGET VS RANK LOST (last 7 days)")
sep("=")

for cid, c in sorted(curr_camps.items(), key=lambda x: x[1]["cost"], reverse=True):
    if c["is_pmax"]:
        print(f"\n  {c['name']}  → PMax (no Search IS data)")
        continue
    bud_lost  = c["budget_lost_is"]
    rank_lost = c["rank_lost_is"]
    is_val    = c["impr_share"]
    top_is    = c["top_is"]
    flag = ""
    if bud_lost > 0.15:
        flag = f"  🚨 Budget throttling: losing {bud_lost*100:.1f}% IS to budget"
    elif rank_lost > 0.20:
        flag = f"  ⚠ Rank problem: losing {rank_lost*100:.1f}% IS to low Ad Rank"
    print(f"\n  {c['name']}  [Budget: ${c['daily_budget']:.0f}/day]")
    print(f"    Impression Share: {is_val*100:.1f}%  |  Top IS: {top_is*100:.1f}%")
    print(f"    Lost to Budget: {bud_lost*100:.1f}%  |  Lost to Rank: {rank_lost*100:.1f}%{flag}")


# ─── 4. KEYWORD PERFORMANCE — LAST 30 DAYS ───────────────────────────────────

print()
sep("=")
print("4. KEYWORD PERFORMANCE (last 30 days — all keywords by spend)")
sep("=")

kw_rows = run_query(f"""
    SELECT
        campaign.name,
        ad_group.name,
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        ad_group_criterion.status,
        ad_group_criterion.quality_info.quality_score,
        ad_group_criterion.quality_info.post_click_quality_score,
        ad_group_criterion.quality_info.search_predicted_ctr,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.ctr,
        metrics.average_cpc
    FROM keyword_view
    WHERE segments.date {EXTENDED_RANGE}
    ORDER BY metrics.cost_micros DESC
""", "keywords")

kw_data = {}
for row in kw_rows:
    kw  = row.ad_group_criterion
    m   = row.metrics
    key = f"{kw.keyword.text}|{kw.keyword.match_type.name}|{row.campaign.name}"
    if key not in kw_data:
        kw_data[key] = {
            "text":           kw.keyword.text,
            "match_type":     kw.keyword.match_type.name,
            "status":         kw.status.name,
            "campaign":       row.campaign.name,
            "ad_group":       row.ad_group.name,
            "quality_score":  kw.quality_info.quality_score,
            "landing_qs":     kw.quality_info.post_click_quality_score.name if kw.quality_info.post_click_quality_score else "N/A",
            "predicted_ctr":  kw.quality_info.search_predicted_ctr.name if kw.quality_info.search_predicted_ctr else "N/A",
            "impressions":    0,
            "clicks":         0,
            "cost":           0.0,
            "conversions":    0.0,
        }
    kw_data[key]["impressions"] += m.impressions
    kw_data[key]["clicks"]      += m.clicks
    kw_data[key]["cost"]        += m.cost_micros / 1_000_000
    kw_data[key]["conversions"] += m.conversions

print(f"\n  Total keywords with activity: {len(kw_data)}")
print("\n  All keywords (sorted by spend):")
for key, kw in sorted(kw_data.items(), key=lambda x: x[1]["cost"], reverse=True):
    ctr = kw["clicks"] / kw["impressions"] * 100 if kw["impressions"] > 0 else 0
    cpc = kw["cost"] / kw["clicks"] if kw["clicks"] > 0 else 0
    cpa = kw["cost"] / kw["conversions"] if kw["conversions"] > 0 else None
    waste_flag = " 🗑 WASTE — $0 conv" if kw["cost"] >= WASTE_SPEND_THRESHOLD and kw["conversions"] == 0 else ""
    qs_flag = " ⚠ LOW QS" if kw["quality_score"] and kw["quality_score"] < 5 else ""
    mt = {"EXACT": f"[{kw['text']}]", "PHRASE": f'"{kw["text"]}"', "BROAD": kw["text"]}.get(kw["match_type"], kw["text"])
    print(f"\n    [{kw['status']}] {mt}{waste_flag}{qs_flag}")
    print(f"      Campaign: {kw['campaign']} | AG: {kw['ad_group']}")
    print(f"      QS: {kw['quality_score']} | Landing: {kw['landing_qs']} | pCTR: {kw['predicted_ctr']}")
    print(f"      Impr: {kw['impressions']:,} | Clicks: {kw['clicks']} | CTR: {ctr:.2f}% | Cost: ${kw['cost']:.2f} | CPC: ${cpc:.2f}")
    print(f"      Conv: {kw['conversions']:.1f} | CPA: {f'${cpa:.2f}' if cpa else '—'}")


# Waste summary
print()
sep()
print("  KEYWORD WASTE SUMMARY — spend >= $50, zero conversions (last 30 days):")
waste_kws = [(k, d) for k, d in kw_data.items() if d["cost"] >= WASTE_SPEND_THRESHOLD and d["conversions"] == 0]
if waste_kws:
    for _, kw in sorted(waste_kws, key=lambda x: x[1]["cost"], reverse=True):
        mt = {"EXACT": f"[{kw['text']}]", "PHRASE": f'"{kw["text"]}"', "BROAD": kw["text"]}.get(kw["match_type"], kw["text"])
        print(f"    ${kw['cost']:.2f}  |  {mt}  |  {kw['campaign']}")
else:
    print("    None found above $50 threshold.")
sep()


# ─── 5. SEARCH TERMS REPORT — LAST 30 DAYS ───────────────────────────────────

print()
sep("=")
print("5. SEARCH TERMS REPORT (last 30 days — top 50 by spend)")
sep("=")

st_rows = run_query(f"""
    SELECT
        campaign.name,
        ad_group.name,
        search_term_view.search_term,
        search_term_view.status,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.ctr,
        metrics.average_cpc
    FROM search_term_view
    WHERE segments.date {EXTENDED_RANGE}
    ORDER BY metrics.cost_micros DESC
    LIMIT 200
""", "search terms")

print(f"\n  Total search terms with activity: {len(st_rows)}")
print("\n  Top 50 search terms by spend:")
for i, row in enumerate(st_rows[:50]):
    st   = row.search_term_view
    m    = row.metrics
    cost = m.cost_micros / 1_000_000
    cpa  = cost / m.conversions if m.conversions > 0 else None
    waste_flag = " 🗑 WASTE" if cost >= WASTE_SPEND_THRESHOLD and m.conversions == 0 else ""
    print(f"\n    {i+1:2}. [{st.status.name}] \"{st.search_term}\"{waste_flag}")
    print(f"         Campaign: {row.campaign.name} | AG: {row.ad_group.name}")
    print(f"         Cost: ${cost:.2f} | Clicks: {m.clicks} | CTR: {m.ctr*100:.2f}% | CPC: ${m.average_cpc/1_000_000:.2f}")
    print(f"         Conv: {m.conversions:.1f} | CPA: {f'${cpa:.2f}' if cpa else '—'}")

print("\n  Top converting search terms (last 30 days):")
conv_terms = sorted(st_rows, key=lambda r: r.metrics.conversions, reverse=True)
for i, row in enumerate(conv_terms[:15]):
    if row.metrics.conversions == 0:
        break
    m    = row.metrics
    cost = m.cost_micros / 1_000_000
    cpa  = cost / m.conversions
    print(f"    {i+1:2}. \"{row.search_term_view.search_term}\" → Conv: {m.conversions:.1f} | CPA: ${cpa:.2f} | Cost: ${cost:.2f}")


# ─── 6. NEGATIVE KEYWORD LIST ────────────────────────────────────────────────

print()
sep("=")
print("6. NEGATIVE KEYWORDS (campaign-level)")
sep("=")

neg_rows = run_query("""
    SELECT
        campaign.name,
        campaign_criterion.keyword.text,
        campaign_criterion.keyword.match_type
    FROM campaign_criterion
    WHERE campaign_criterion.negative = TRUE
      AND campaign_criterion.type = KEYWORD
    ORDER BY campaign.name
""", "negatives")

neg_by_campaign = defaultdict(list)
for row in neg_rows:
    kw = row.campaign_criterion.keyword
    neg_by_campaign[row.campaign.name].append(f"{kw.text} [{kw.match_type.name}]")

if neg_by_campaign:
    for camp_name, kws in sorted(neg_by_campaign.items()):
        print(f"\n  {camp_name}  ({len(kws)} negatives)")
        for kw in kws:
            print(f"    -{kw}")
else:
    print("\n  ⚠ NO campaign-level negative keywords found.")


# ─── DONE ────────────────────────────────────────────────────────────────────

print()
sep("=")
print("DATA PULL COMPLETE")
print(f"Account: {CLIENT_NAME} ({CUSTOMER_ID})")
print(f"Run at: {date.today()}")
sep("=")
print()
