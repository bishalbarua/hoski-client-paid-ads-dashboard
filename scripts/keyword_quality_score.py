"""
Keyword Quality Score Audit
Purpose: Pull Quality Score and component ratings for all active keywords across
         all (or one) client accounts. Flags low-QS keywords by root cause so you
         know exactly what to fix — ad copy, relevance, or landing page.

         Quality Score directly impacts CPC and ad rank. A QS of 4 vs 7 can mean
         paying 2–3x more per click for the same position.

Setup:
    Requires environment variables:
        GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET,
        GOOGLE_ADS_REFRESH_TOKEN, GOOGLE_ADS_CUSTOMER_ID

Usage:
    python3 scripts/keyword_quality_score.py                            # all clients
    python3 scripts/keyword_quality_score.py --customer-id 5544702166   # single client
    python3 scripts/keyword_quality_score.py --min-spend 5              # only flag kws with ≥$5 spend
    python3 scripts/keyword_quality_score.py --show-all                 # include healthy kws in output

Quality Score Thresholds:
    🚨 CRITICAL  QS ≤ 4  — paying significantly above-market CPCs
    ⚠️  WARNING   QS 5–6  — below average; room to improve
    ✅  HEALTHY   QS 7–10 — on par or above average

Component Ratings (each flagged separately):
    search_predicted_ctr    → BELOW_AVERAGE = ad copy not matching search intent
    creative_quality_score  → BELOW_AVERAGE = headline/keyword relevance weak
    post_click_quality_score → BELOW_AVERAGE = landing page experience poor

    Fix guide:
        Low Expected CTR     → Rewrite headlines; include keyword in H1/H2
        Low Ad Relevance     → Tighten ad group themes; add keyword to ad copy
        Low Landing Page Exp → Improve page speed, message match, and UX

Changelog:
    2026-03-19  Initial version — QS snapshot, component breakdown, spend impact,
                root-cause grouping, per-campaign output.
"""

import argparse
import os
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

# ─── THRESHOLDS ───────────────────────────────────────────────────────────────

QS_CRITICAL = 4   # QS ≤ this → critical
QS_WARNING  = 6   # QS ≤ this → warning
DEFAULT_MIN_SPEND = 0.0  # minimum 30-day spend to include in flagged output

COMPONENT_LABELS = {
    "ABOVE_AVERAGE": "✅ Above avg",
    "AVERAGE":       "➡️  Average",
    "BELOW_AVERAGE": "🔴 Below avg",
    "UNKNOWN":       "—  No data",
    "UNSPECIFIED":   "—  No data",
}

FIX_GUIDE = {
    "ctr":       "Rewrite headlines — include the keyword and a strong CTA. Mirror search intent in H1.",
    "relevance": "Tighten ad group theme — move keyword to its own ad group, add it to headline 1/2.",
    "landing":   "Fix landing page — improve load speed, match headline to keyword, clear CTA above fold.",
}

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


# ─── PULL ────────────────────────────────────────────────────────────────────

def pull_quality_scores(ga_service, customer_id):
    """
    Pull current Quality Score snapshot — no date segmentation.
    QS is a point-in-time value, not a time-series metric.
    """
    rows = run_query(ga_service, customer_id, """
        SELECT
            campaign.name,
            campaign.status,
            ad_group.name,
            ad_group.status,
            ad_group_criterion.criterion_id,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.status,
            ad_group_criterion.quality_info.quality_score,
            ad_group_criterion.quality_info.search_predicted_ctr,
            ad_group_criterion.quality_info.creative_quality_score,
            ad_group_criterion.quality_info.post_click_quality_score
        FROM keyword_view
        WHERE campaign.status = ENABLED
          AND ad_group.status = ENABLED
          AND ad_group_criterion.status = ENABLED
        ORDER BY campaign.name, ad_group.name
    """)

    keywords = {}
    for row in rows:
        kw  = row.ad_group_criterion
        qi  = kw.quality_info
        cid = str(kw.criterion_id)

        keywords[cid] = {
            "cid":        cid,
            "campaign":   row.campaign.name,
            "ad_group":   row.ad_group.name,
            "text":       kw.keyword.text,
            "match_type": kw.keyword.match_type.name,
            "qs":         qi.quality_score,            # 0 = no data
            "ctr_rating": qi.search_predicted_ctr.name,
            "rel_rating": qi.creative_quality_score.name,
            "lp_rating":  qi.post_click_quality_score.name,
            # filled by metrics query
            "cost":        0.0,
            "impressions": 0,
            "clicks":      0,
            "conversions": 0.0,
        }
    return keywords


def pull_keyword_metrics(ga_service, customer_id):
    """Pull 30-day performance metrics per keyword."""
    rows = run_query(ga_service, customer_id, """
        SELECT
            ad_group_criterion.criterion_id,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions
        FROM keyword_view
        WHERE segments.date DURING LAST_30_DAYS
          AND campaign.status = ENABLED
          AND ad_group.status = ENABLED
          AND ad_group_criterion.status = ENABLED
    """)

    metrics = defaultdict(lambda: {"cost": 0.0, "impressions": 0, "clicks": 0, "conversions": 0.0})
    for row in rows:
        cid = str(row.ad_group_criterion.criterion_id)
        m   = row.metrics
        metrics[cid]["cost"]        += m.cost_micros / 1_000_000
        metrics[cid]["impressions"] += m.impressions
        metrics[cid]["clicks"]      += m.clicks
        metrics[cid]["conversions"] += m.conversions

    return metrics


def audit_account(ga_service, customer_id):
    keywords = pull_quality_scores(ga_service, customer_id)
    metrics  = pull_keyword_metrics(ga_service, customer_id)

    # Merge metrics into keyword records
    for cid, kw in keywords.items():
        m = metrics.get(cid, {})
        kw["cost"]        = m.get("cost", 0.0)
        kw["impressions"] = m.get("impressions", 0)
        kw["clicks"]      = m.get("clicks", 0)
        kw["conversions"] = m.get("conversions", 0.0)

    return keywords


# ─── ANALYSE ─────────────────────────────────────────────────────────────────

def classify(kw):
    qs = kw["qs"]
    if qs == 0:
        return "no_data"
    elif qs <= QS_CRITICAL:
        return "critical"
    elif qs <= QS_WARNING:
        return "warning"
    else:
        return "healthy"


def get_root_causes(kw):
    causes = []
    if kw["ctr_rating"] == "BELOW_AVERAGE":
        causes.append("ctr")
    if kw["rel_rating"] == "BELOW_AVERAGE":
        causes.append("relevance")
    if kw["lp_rating"] == "BELOW_AVERAGE":
        causes.append("landing")
    return causes


# ─── PRINT ───────────────────────────────────────────────────────────────────

def qs_bar(qs):
    if qs == 0:
        return "[          ] N/A"
    filled = qs  # 1–10 scale → use as number of filled blocks
    return f"[{'█' * filled}{'░' * (10 - filled)}] {qs}/10"


def print_keyword(kw, show_fix=True):
    qs     = kw["qs"]
    causes = get_root_causes(kw)
    ctr    = kw["clicks"] / kw["impressions"] if kw["impressions"] > 0 else 0
    cpc    = kw["cost"]   / kw["clicks"]      if kw["clicks"]      > 0 else 0

    if qs == 0:
        qs_icon = "⬜"
    elif qs <= QS_CRITICAL:
        qs_icon = "🚨"
    elif qs <= QS_WARNING:
        qs_icon = "⚠️ "
    else:
        qs_icon = "✅"

    print(f"      {qs_icon} \"{kw['text']}\" [{kw['match_type']}]  {qs_bar(qs)}")
    print(f"           AdGroup: {kw['ad_group']}")
    print(f"           Expected CTR: {COMPONENT_LABELS.get(kw['ctr_rating'], kw['ctr_rating'])}"
          f"  |  Ad Relevance: {COMPONENT_LABELS.get(kw['rel_rating'], kw['rel_rating'])}"
          f"  |  Landing Page: {COMPONENT_LABELS.get(kw['lp_rating'], kw['lp_rating'])}")
    if kw["cost"] > 0 or kw["impressions"] > 0:
        print(f"           Spend: ${kw['cost']:.2f}  |  Clicks: {kw['clicks']}  |  CTR: {ctr:.1%}  |  CPC: ${cpc:.2f}  |  Conv: {kw['conversions']:.0f}")
    if show_fix and causes:
        for cause in causes:
            print(f"           💡 Fix ({cause}): {FIX_GUIDE[cause]}")


def print_account(client_name, customer_id, keywords, min_spend, show_all):
    if not keywords:
        print(f"\n⬜  {client_name} ({customer_id}) — No active keywords")
        return 0, 0

    # Classify all keywords
    critical = [kw for kw in keywords.values() if classify(kw) == "critical" and kw["cost"] >= min_spend]
    warning  = [kw for kw in keywords.values() if classify(kw) == "warning"  and kw["cost"] >= min_spend]
    no_data  = [kw for kw in keywords.values() if classify(kw) == "no_data"]
    healthy  = [kw for kw in keywords.values() if classify(kw) == "healthy"]

    # Sort flagged keywords by spend (highest waste first)
    critical.sort(key=lambda k: k["cost"], reverse=True)
    warning.sort(key=lambda k: k["cost"], reverse=True)

    total_spend_at_risk = sum(kw["cost"] for kw in critical) + sum(kw["cost"] for kw in warning)
    avg_qs = (
        sum(kw["qs"] for kw in keywords.values() if kw["qs"] > 0)
        / max(1, sum(1 for kw in keywords.values() if kw["qs"] > 0))
    )

    if critical:
        account_icon = "🚨"
    elif warning:
        account_icon = "⚠️ "
    else:
        account_icon = "✅"

    total_kws = len(keywords)
    print(f"\n{account_icon}  {client_name} ({customer_id})")
    print(f"    {total_kws} enabled keywords  |  Avg QS: {avg_qs:.1f}/10  |  "
          f"🚨 {len(critical)} critical  |  ⚠️  {len(warning)} warning  |  "
          f"⬜ {len(no_data)} no data  |  Spend at risk: ${total_spend_at_risk:.2f}")

    # ── Root cause summary ───────────────────────────────────────────────────
    all_flagged = critical + warning
    ctr_issues  = sum(1 for kw in all_flagged if "ctr"      in get_root_causes(kw))
    rel_issues  = sum(1 for kw in all_flagged if "relevance" in get_root_causes(kw))
    lp_issues   = sum(1 for kw in all_flagged if "landing"   in get_root_causes(kw))
    if all_flagged:
        print(f"    Root causes: Expected CTR issues: {ctr_issues}  |  Ad Relevance issues: {rel_issues}  |  Landing Page issues: {lp_issues}")

    # ── Critical keywords ────────────────────────────────────────────────────
    if critical:
        print(f"\n    🚨 CRITICAL — QS ≤ {QS_CRITICAL} ({len(critical)} keywords)")
        # Group by campaign
        by_campaign = defaultdict(list)
        for kw in critical:
            by_campaign[kw["campaign"]].append(kw)
        for camp, kws in by_campaign.items():
            print(f"\n      Campaign: {camp}")
            for kw in kws:
                print_keyword(kw)

    # ── Warning keywords ─────────────────────────────────────────────────────
    if warning:
        print(f"\n    ⚠️  WARNING — QS {QS_CRITICAL + 1}–{QS_WARNING} ({len(warning)} keywords)")
        by_campaign = defaultdict(list)
        for kw in warning:
            by_campaign[kw["campaign"]].append(kw)
        for camp, kws in by_campaign.items():
            print(f"\n      Campaign: {camp}")
            for kw in kws:
                print_keyword(kw, show_fix=False)  # skip fix tips on warnings to reduce noise

    # ── No QS data ───────────────────────────────────────────────────────────
    if no_data:
        print(f"\n    ⬜ NO QS DATA — {len(no_data)} keyword(s) (new or too few impressions to score)")

    # ── Healthy (optional) ───────────────────────────────────────────────────
    if show_all and healthy:
        print(f"\n    ✅ HEALTHY — QS 7–10 ({len(healthy)} keywords)")
        healthy_sorted = sorted(healthy, key=lambda k: k["cost"], reverse=True)
        for kw in healthy_sorted[:10]:
            qs = kw["qs"]
            cpc = kw["cost"] / kw["clicks"] if kw["clicks"] > 0 else 0
            print(f"      ✅ \"{kw['text']}\" [{kw['match_type']}]  QS: {qs}/10  |  Spend: ${kw['cost']:.2f}  |  Campaign: {kw['campaign']}")

    if not critical and not warning:
        print("    ✅ All keywords with spend are scoring 7+ — no QS issues detected")

    return len(critical), len(warning)


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Keyword Quality Score audit — flags low-QS keywords by root cause")
    parser.add_argument("--customer-id", help="Single account ID (omit to run all clients)")
    parser.add_argument("--client-name", help="Display name when using --customer-id")
    parser.add_argument("--min-spend",   type=float, default=DEFAULT_MIN_SPEND,
                        help=f"Only flag keywords with ≥ this 30-day spend (default: ${DEFAULT_MIN_SPEND:.0f} = all)")
    parser.add_argument("--show-all",    action="store_true",
                        help="Also display healthy keywords (QS 7+) in output")
    args = parser.parse_args()

    client     = build_client()
    ga_service = client.get_service("GoogleAdsService")

    if args.customer_id:
        targets = {(args.client_name or args.customer_id): args.customer_id.replace("-", "")}
    else:
        targets = ALL_CLIENTS

    print("\n" + "="*60)
    print("KEYWORD QUALITY SCORE AUDIT")
    print(f"Thresholds: 🚨 QS ≤ {QS_CRITICAL}  |  ⚠️  QS ≤ {QS_WARNING}  |  ✅ QS 7+")
    if args.min_spend > 0:
        print(f"Filter: only keywords with ≥ ${args.min_spend:.0f} spend in last 30 days")
    print("="*60)

    total_critical = 0
    total_warnings = 0
    errored        = []

    for name, cid in targets.items():
        try:
            keywords = audit_account(ga_service, cid)
            c, w = print_account(name, cid, keywords, args.min_spend, args.show_all)
            total_critical += c
            total_warnings += w
        except Exception as e:
            errored.append(name)
            print(f"\n❌  {name} ({cid}) — Error: {e}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  Accounts checked:    {len(targets) - len(errored)}/{len(targets)}")
    print(f"  🚨 Critical (QS ≤ {QS_CRITICAL}): {total_critical} keywords")
    print(f"  ⚠️  Warning  (QS ≤ {QS_WARNING}): {total_warnings} keywords")
    if errored:
        print(f"  ❌ Errored:          {', '.join(errored)}")
    if total_critical == 0 and total_warnings == 0:
        print(f"\n  ✅ No low-QS keywords found{' with spend above threshold' if args.min_spend > 0 else ''}.")
    print("="*60)


if __name__ == "__main__":
    main()
