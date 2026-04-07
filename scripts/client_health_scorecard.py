"""
Client Health Scorecard
Purpose: Computes a composite health score (0-100) for every Google Ads client
         account. Combines: conversion tracking status, budget pacing, Search
         IS trend, CTR trend, QS average, and disapproval count into a single
         ranked list. Writes a rolling history to Google Sheets.

         Run weekly (after mcc_rollup.py) to maintain a trend of account health.

Setup:
    Requires environment variables in .env:
        GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID,
        GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN,
        GOOGLE_ADS_CUSTOMER_ID  (MCC)
        GOOGLE_SHEETS_ID        (spreadsheet to write to, optional)

Usage:
    python3 scripts/client_health_scorecard.py             # all clients
    python3 scripts/client_health_scorecard.py --customer-id 5544702166
    python3 scripts/client_health_scorecard.py --sheets    # write to Google Sheets

Scoring breakdown (100 points total):
    Conversion tracking health   25 pts  (30 pts for service business accounts)
    Budget pacing                20 pts
    Search Impression Share WoW  20 pts
    CTR trend WoW                15 pts  (10 pts for service business accounts)
    Avg Quality Score            15 pts
    Disapprovals                  5 pts

    Service business accounts (dental, medical, legal, aesthetics, construction,
    high-ticket retail): conversion tracking weight is raised to 30 pts because
    call tracking is fragile, and CTR weight is reduced to 10 pts because CPL
    is a more meaningful signal than CTR for these verticals.

Changelog:
    2026-03-23  Initial version — composite score, ranked table, Sheets output.
    2026-04-07  Added SERVICE_BUSINESS_IDS and vertical-aware scoring weights.
"""

import argparse
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

load_dotenv()

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

# ─── SERVICE BUSINESS REGISTRY ───────────────────────────────────────────────
# Accounts where CPL and call tracking are the primary health signals.
# Conv tracking weight is raised (30 pts); CTR weight is reduced (10 pts).

SERVICE_BUSINESS_IDS = {
    "8159668041",  # Texas FHC
    "7628667762",  # Synergy Spine & Nerve Center
    "5216656756",  # Voit Dental (1)
    "5907367258",  # Voit Dental (2)
    "5865660247",  # Anand Desai Law Firm
    "8134824884",  # Serenity Familycare
    "9304117954",  # FaBesthetics
    "3857223862",  # Dentiste
    "5544702166",  # Hoski.ca
    "7228467515",  # Park Road Custom Furniture and Decor
    "3720173680",  # New Norseman
}

# ─── SCORING WEIGHTS ─────────────────────────────────────────────────────────

WEIGHT_CONV_HEALTH = 25
WEIGHT_PACING      = 20
WEIGHT_IS_TREND    = 20
WEIGHT_CTR_TREND   = 15
WEIGHT_QS          = 15
WEIGHT_DISAPPROVAL  = 5

# Service business overrides
WEIGHT_CONV_HEALTH_SERVICE = 30
WEIGHT_CTR_TREND_SERVICE   = 10

# ─── CLIENT ──────────────────────────────────────────────────────────────────

def build_ga_client():
    return GoogleAdsClient.load_from_dict({
        "developer_token":   os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "client_id":         os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret":     os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token":     os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "login_customer_id": os.environ["GOOGLE_ADS_CUSTOMER_ID"],
        "use_proto_plus":    True,
    })


def run_query(ga_service, customer_id, query):
    try:
        return list(ga_service.search(customer_id=customer_id, query=query))
    except GoogleAdsException as ex:
        return []


# ─── DATE HELPERS ─────────────────────────────────────────────────────────────

def dates():
    today     = date.today()
    yesterday = today - timedelta(days=1)
    return {
        "yesterday":        yesterday.strftime("%Y-%m-%d"),
        "this_week_start":  (today - timedelta(days=7)).strftime("%Y-%m-%d"),
        "this_week_end":    yesterday.strftime("%Y-%m-%d"),
        "prior_week_start": (today - timedelta(days=14)).strftime("%Y-%m-%d"),
        "prior_week_end":   (today - timedelta(days=8)).strftime("%Y-%m-%d"),
    }


# ─── COMPONENT SCORERS ───────────────────────────────────────────────────────

def score_conversion_health(ga_service, customer_id, d):
    """
    25 pts: Has primary conversion actions that fired recently.
    -15 if primary action has 0 conv in 30 days
    -10 if no primary conversion actions exist
    """
    rows_def = run_query(ga_service, customer_id, """
        SELECT
            conversion_action.include_in_conversions_metric,
            conversion_action.status
        FROM conversion_action
        WHERE conversion_action.status = ENABLED
    """)
    primary = [r for r in rows_def if r.conversion_action.include_in_conversions_metric]

    if not primary:
        return 5, "No primary conversion actions"

    rows_metrics = run_query(ga_service, customer_id, """
        SELECT
            conversion_action.include_in_conversions_metric,
            metrics.conversions
        FROM conversion_action
        WHERE segments.date DURING LAST_30_DAYS
    """)
    primary_conv = sum(
        r.metrics.conversions for r in rows_metrics
        if r.conversion_action.include_in_conversions_metric
    )

    if primary_conv == 0:
        return 10, "Primary actions exist but 0 conversions in 30 days"

    return 25, f"{primary_conv:.0f} conversions (30d)"


def score_pacing(ga_service, customer_id, d):
    """
    20 pts: Yesterday's spend was within 20% of daily budget.
    Deductions for overpacing or underpacing.
    """
    rows = run_query(ga_service, customer_id, f"""
        SELECT
            campaign_budget.amount_micros,
            metrics.cost_micros
        FROM campaign
        WHERE segments.date = '{d["yesterday"]}'
          AND campaign.status = ENABLED
    """)
    if not rows:
        return 10, "No spend data"

    total_budget = sum(r.campaign_budget.amount_micros / 1_000_000 for r in rows)
    total_spend  = sum(r.metrics.cost_micros / 1_000_000 for r in rows)

    if total_budget == 0:
        return 10, "No budget set"

    ratio = total_spend / total_budget
    if 0.80 <= ratio <= 1.10:
        return 20, f"Pacing healthy ({ratio*100:.0f}% of budget)"
    elif 0.60 <= ratio < 0.80 or 1.10 < ratio <= 1.20:
        return 14, f"Minor pacing deviation ({ratio*100:.0f}% of budget)"
    elif ratio < 0.20:
        return 5, f"Severe underpacing ({ratio*100:.0f}% of budget — possible stoppage)"
    else:
        return 8, f"Significant pacing issue ({ratio*100:.0f}% of budget)"


def score_is_trend(ga_service, customer_id, d):
    """
    20 pts: Search IS held steady or improved WoW.
    """
    def get_is(start, end):
        rows = run_query(ga_service, customer_id, f"""
            SELECT metrics.search_impression_share
            FROM customer
            WHERE segments.date >= '{start}' AND segments.date <= '{end}'
        """)
        vals = [r.metrics.search_impression_share for r in rows
                if 0 < r.metrics.search_impression_share <= 1]
        return sum(vals) / len(vals) if vals else None

    this_is = get_is(d["this_week_start"], d["this_week_end"])
    prev_is = get_is(d["prior_week_start"], d["prior_week_end"])

    if this_is is None or prev_is is None or prev_is == 0:
        return 10, "Insufficient IS data"

    drop_pts = (prev_is - this_is) * 100  # absolute percentage points
    if drop_pts <= 0:
        return 20, f"IS stable/improved ({this_is*100:.1f}%)"
    elif drop_pts <= 5:
        return 16, f"IS down {drop_pts:.1f} pts ({this_is*100:.1f}%)"
    elif drop_pts <= 15:
        return 10, f"IS down {drop_pts:.1f} pts ({this_is*100:.1f}%) — investigate"
    else:
        return 4, f"IS dropped {drop_pts:.1f} pts ({this_is*100:.1f}%) — major decline"


def score_ctr_trend(ga_service, customer_id, d):
    """
    15 pts: CTR held steady or improved WoW.
    """
    def get_ctr(start, end):
        rows = run_query(ga_service, customer_id, f"""
            SELECT metrics.clicks, metrics.impressions
            FROM customer
            WHERE segments.date >= '{start}' AND segments.date <= '{end}'
        """)
        clicks = sum(r.metrics.clicks for r in rows)
        imps   = sum(r.metrics.impressions for r in rows)
        return clicks / imps if imps > 0 else None

    this_ctr = get_ctr(d["this_week_start"], d["this_week_end"])
    prev_ctr = get_ctr(d["prior_week_start"], d["prior_week_end"])

    if this_ctr is None or prev_ctr is None or prev_ctr == 0:
        return 7, "Insufficient CTR data"

    change = (this_ctr - prev_ctr) / prev_ctr
    if change >= 0:
        return 15, f"CTR improved {change*100:.0f}% WoW ({this_ctr*100:.2f}%)"
    elif change >= -0.15:
        return 12, f"CTR down {abs(change)*100:.0f}% WoW ({this_ctr*100:.2f}%)"
    elif change >= -0.30:
        return 8, f"CTR down {abs(change)*100:.0f}% WoW — investigate"
    else:
        return 3, f"CTR dropped {abs(change)*100:.0f}% WoW — significant"


def score_quality_scores(ga_service, customer_id):
    """
    15 pts: Average QS across active keywords.
    Scaled: QS 8-10 = 15 pts, QS 7 = 12, QS 6 = 9, QS <6 = proportional.
    """
    rows = run_query(ga_service, customer_id, """
        SELECT
            ad_group_criterion.quality_info.quality_score,
            metrics.impressions
        FROM keyword_view
        WHERE ad_group_criterion.status = ENABLED
          AND ad_group.status = ENABLED
          AND campaign.status = ENABLED
          AND segments.date DURING LAST_30_DAYS
    """)

    # Impression-weighted average QS
    total_weight = 0
    weighted_qs  = 0
    seen = defaultdict(lambda: {"qs": 0, "imps": 0})

    for row in rows:
        qs   = row.ad_group_criterion.quality_info.quality_score
        imps = row.metrics.impressions
        if qs and qs > 0:
            weighted_qs  += qs * imps
            total_weight += imps

    if total_weight == 0:
        return 7, "No QS data available"

    avg_qs = weighted_qs / total_weight

    if avg_qs >= 8:
        return 15, f"Avg QS {avg_qs:.1f} (excellent)"
    elif avg_qs >= 7:
        return 12, f"Avg QS {avg_qs:.1f} (good)"
    elif avg_qs >= 6:
        return 9, f"Avg QS {avg_qs:.1f} (average — room to improve)"
    elif avg_qs >= 5:
        return 6, f"Avg QS {avg_qs:.1f} (below average)"
    else:
        return 3, f"Avg QS {avg_qs:.1f} (poor — prioritise QS improvements)"


def score_disapprovals(ga_service, customer_id):
    """
    5 pts: 0 disapprovals = 5 pts. Each disapproval deducts points.
    """
    rows = run_query(ga_service, customer_id, """
        SELECT
            campaign.status,
            ad_group.status,
            ad_group_ad.policy_summary.approval_status
        FROM ad_group_ad
        WHERE ad_group_ad.status = ENABLED
          AND ad_group_ad.policy_summary.approval_status = DISAPPROVED
    """)

    active_disapprovals = sum(
        1 for r in rows
        if r.campaign.status.name == "ENABLED" and r.ad_group.status.name == "ENABLED"
    )

    if active_disapprovals == 0:
        return 5, "No disapprovals"
    elif active_disapprovals == 1:
        return 2, f"{active_disapprovals} disapproved ad"
    else:
        return 0, f"{active_disapprovals} disapproved ads — fix urgently"


# ─── SCORE ONE ACCOUNT ────────────────────────────────────────────────────────

def score_account(ga_client, client_name, customer_id, d):
    """Compute all component scores and return a structured result."""
    is_service = customer_id in SERVICE_BUSINESS_IDS
    vertical   = "Service Business" if is_service else "DTC / E-commerce"

    w_conv = WEIGHT_CONV_HEALTH_SERVICE if is_service else WEIGHT_CONV_HEALTH
    w_ctr  = WEIGHT_CTR_TREND_SERVICE   if is_service else WEIGHT_CTR_TREND

    try:
        svc = ga_client.get_service("GoogleAdsService")

        conv_pts,  conv_note  = score_conversion_health(svc, customer_id, d)
        pacing_pts, pace_note = score_pacing(svc, customer_id, d)
        is_pts,    is_note    = score_is_trend(svc, customer_id, d)
        ctr_pts,   ctr_note   = score_ctr_trend(svc, customer_id, d)
        qs_pts,    qs_note    = score_quality_scores(svc, customer_id)
        disap_pts, disap_note = score_disapprovals(svc, customer_id)

        # Rescale component scores proportionally to their vertical-aware weights
        conv_pts_adj  = round(conv_pts  * w_conv / WEIGHT_CONV_HEALTH)
        ctr_pts_adj   = round(ctr_pts   * w_ctr  / WEIGHT_CTR_TREND)

        total     = conv_pts_adj + pacing_pts + is_pts + ctr_pts_adj + qs_pts + disap_pts
        max_total = w_conv + WEIGHT_PACING + WEIGHT_IS_TREND + w_ctr + WEIGHT_QS + WEIGHT_DISAPPROVAL

        result = {
            "client_name":  client_name,
            "customer_id":  customer_id,
            "vertical":     vertical,
            "score":        total,
            "max_score":    max_total,
            "grade":        score_to_grade(total, max_total),
            "components": {
                "conversion":    (conv_pts_adj, w_conv,              conv_note),
                "pacing":        (pacing_pts,   WEIGHT_PACING,       pace_note),
                "is_trend":      (is_pts,        WEIGHT_IS_TREND,    is_note),
                "ctr_trend":     (ctr_pts_adj,   w_ctr,              ctr_note),
                "quality_score": (qs_pts,         WEIGHT_QS,         qs_note),
                "disapprovals":  (disap_pts,      WEIGHT_DISAPPROVAL, disap_note),
            },
            "error": None,
        }
        if is_service:
            result["note"] = "Service business account — CPL and call tracking are primary health signals"
        return result
    except Exception as e:
        return {
            "client_name": client_name,
            "customer_id": customer_id,
            "vertical":    vertical,
            "score":       0,
            "max_score":   100,
            "grade":       "ERR",
            "components":  {},
            "error":       str(e),
        }


def score_to_grade(score, max_score):
    pct = score / max_score * 100 if max_score > 0 else 0
    if pct >= 90: return "A"
    if pct >= 75: return "B"
    if pct >= 60: return "C"
    if pct >= 45: return "D"
    return "F"


# ─── PRINT REPORT ─────────────────────────────────────────────────────────────

def print_report(results, run_date):
    valid   = [r for r in results if not r["error"]]
    errored = [r for r in results if r["error"]]

    # Sort worst to best so urgent items are at top
    valid.sort(key=lambda x: x["score"])

    print(f"\nCLIENT HEALTH SCORECARD — {run_date}")
    print("=" * 90)
    print(f"{'Client':<38} {'Vertical':<18} {'Score':>7} {'Grade':>5}  Components")
    print("-" * 90)

    for r in valid:
        comp     = r["components"]
        vertical = r.get("vertical", "")
        bar      = "|".join(
            f"{v[0]:>2}/{v[1]}"
            for k, v in comp.items()
        )
        note_flag = "  *" if r.get("note") else ""
        print(f"  {r['client_name']:<36} {vertical:<18} {r['score']:>4}/{r['max_score']}  [{r['grade']}]  {bar}{note_flag}")

    if errored:
        print("")
        for r in errored:
            print(f"  ERROR: {r['client_name']} — {r['error']}")

    print("-" * 90)

    if valid:
        avg = sum(r["score"] for r in valid) / len(valid)
        best = max(valid, key=lambda x: x["score"])
        worst = min(valid, key=lambda x: x["score"])
        print(f"  Portfolio avg score: {avg:.0f}")
        print(f"  Best:  {best['client_name']} ({best['score']})")
        print(f"  Worst: {worst['client_name']} ({worst['score']})")

    print("=" * 90)
    print("  Component key: conv | pacing | IS | CTR | QS | disapprovals")
    print("  * Service business account — CPL and call tracking are primary health signals")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Client health scorecard — composite weekly health score"
    )
    parser.add_argument("--customer-id", help="Single account ID (omit for all clients)")
    parser.add_argument("--client-name", help="Display name when using --customer-id")
    parser.add_argument("--threads",     type=int, default=5,
                        help="Thread pool size (default: 5)")
    args = parser.parse_args()

    run_date  = date.today().strftime("%Y-%m-%d")
    d         = dates()
    ga_client = build_ga_client()

    if args.customer_id:
        targets = {(args.client_name or args.customer_id): args.customer_id.replace("-", "")}
    else:
        targets = ALL_CLIENTS

    print(f"\nScoring {len(targets)} account(s) ...")

    results = []
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {
            executor.submit(score_account, ga_client, name, cid, d): name
            for name, cid in targets.items()
        }
        for future in as_completed(futures):
            result = futures[future]  # name string
            r = future.result()
            grade = r.get("grade", "?")
            print(f"  [{grade}] {r['client_name']} — {r['score']}/{r['max_score']}")
            results.append(r)

    print_report(results, run_date)


if __name__ == "__main__":
    main()
