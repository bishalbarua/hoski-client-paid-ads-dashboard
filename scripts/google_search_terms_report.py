"""
Search Terms Report
Purpose: Pull and analyse search terms across all (or one) client accounts.
         Surfaces four actionable signals in one pass:
           1. Negative keyword candidates  — wasted spend, zero conversions
           2. Exact match candidates       — converting terms not yet targeted as exact
           3. New keyword opportunities    — untracked terms with strong engagement
           4. Match type promotion signals — high-click broad/phrase terms worth tightening

Setup:
    Requires environment variables:
        GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET,
        GOOGLE_ADS_REFRESH_TOKEN, GOOGLE_ADS_CUSTOMER_ID

Usage:
    python3 scripts/search_terms_report.py                            # all clients, 30 days
    python3 scripts/search_terms_report.py --customer-id 5544702166  # single client
    python3 scripts/search_terms_report.py --days 7                  # 7-day window
    python3 scripts/search_terms_report.py --min-cost 5              # only flag terms ≥$5 spend

Flags:
    🚫 NEGATIVE CANDIDATE
        - Spend ≥ $min_cost AND 0 conversions AND not already excluded
        - Sorted by spend descending (highest waste first)

    ⭐ EXACT MATCH CANDIDATE
        - ≥1 conversion AND not already targeted as a standalone exact keyword

    🔍 NEW KEYWORD OPPORTUNITY
        - CTR ≥ 3% AND ≥10 clicks AND status = NONE (not yet tracked at all)

    📌 MATCH TYPE PROMOTION
        - ≥5 clicks from a BROAD or PHRASE match triggered term
          that is already an ADDED keyword — signal to add an exact variant

Changelog:
    2026-03-19  Initial version — negatives, exact candidates, new opportunities,
                match type promotions, per-campaign grouping.
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

DEFAULT_MIN_COST     = 10.0  # minimum spend to flag as a negative candidate ($)
EXACT_MIN_CONV       = 1     # minimum conversions to flag as exact match candidate
OPPORTUNITY_MIN_CTR  = 0.03  # 3% CTR threshold for new keyword opportunities
OPPORTUNITY_MIN_CLICKS = 10  # minimum clicks for new keyword opportunity
PROMOTION_MIN_CLICKS = 5     # minimum clicks to suggest match type tightening

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

def pull_search_terms(ga_service, customer_id, days):
    date_range = f"LAST_{days}_DAYS" if days in (7, 14, 30) else "LAST_30_DAYS"

    rows = run_query(ga_service, customer_id, f"""
        SELECT
            campaign.name,
            campaign.status,
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
        WHERE segments.date DURING {date_range}
          AND campaign.status = ENABLED
        ORDER BY metrics.cost_micros DESC
        LIMIT 5000
    """)

    # Aggregate by (campaign, search_term) — rows can be split across ad groups
    terms = {}
    for row in rows:
        st   = row.search_term_view
        m    = row.metrics
        key  = (row.campaign.name, st.search_term)

        if key not in terms:
            terms[key] = {
                "campaign":    row.campaign.name,
                "ad_group":    row.ad_group.name,
                "term":        st.search_term,
                "status":      st.status.name,   # ADDED, EXCLUDED, NONE
                "impressions": 0,
                "clicks":      0,
                "cost":        0.0,
                "conversions": 0.0,
            }

        terms[key]["impressions"] += m.impressions
        terms[key]["clicks"]      += m.clicks
        terms[key]["cost"]        += m.cost_micros / 1_000_000
        terms[key]["conversions"] += m.conversions

    return list(terms.values())


# ─── ANALYSE ─────────────────────────────────────────────────────────────────

def analyse(terms, min_cost):
    negatives   = []   # waste: spend with no conversions
    exact_cands = []   # converting terms not yet exact-matched
    opportunities = [] # untracked terms with strong engagement
    promotions  = []   # added (broad/phrase) terms worth tightening

    for t in terms:
        cost   = t["cost"]
        clicks = t["clicks"]
        conv   = t["conversions"]
        impr   = t["impressions"]
        status = t["status"]
        ctr    = clicks / impr if impr > 0 else 0
        cpc    = cost / clicks if clicks > 0 else 0
        cpa    = cost / conv   if conv   > 0 else 0

        t["ctr"] = ctr
        t["cpc"] = cpc
        t["cpa"] = cpa

        # 🚫 Negative candidate — spend above threshold, zero conversions, not excluded yet
        if cost >= min_cost and conv == 0 and status != "EXCLUDED":
            negatives.append(t)

        # ⭐ Exact match candidate — converting, not already ADDED as a keyword
        if conv >= EXACT_MIN_CONV and status == "NONE":
            exact_cands.append(t)

        # 🔍 New keyword opportunity — untracked, high engagement
        if (status == "NONE"
                and ctr >= OPPORTUNITY_MIN_CTR
                and clicks >= OPPORTUNITY_MIN_CLICKS
                and conv == 0):  # already captured by exact_cands if converting
            opportunities.append(t)

        # 📌 Match type promotion — already a keyword but high click volume suggests exact variant
        if status == "ADDED" and clicks >= PROMOTION_MIN_CLICKS:
            promotions.append(t)

    negatives.sort(key=lambda t: t["cost"], reverse=True)
    exact_cands.sort(key=lambda t: t["conversions"], reverse=True)
    opportunities.sort(key=lambda t: t["clicks"], reverse=True)
    promotions.sort(key=lambda t: t["clicks"], reverse=True)

    return negatives, exact_cands, opportunities, promotions


# ─── PRINT ───────────────────────────────────────────────────────────────────

def print_section(title, icon, items, formatter, limit=20):
    print(f"\n  {icon}  {title} ({len(items)} found)")
    if not items:
        print("      None")
        return
    for t in items[:limit]:
        formatter(t)
    if len(items) > limit:
        print(f"      ... and {len(items) - limit} more")


def fmt_negative(t):
    print(f"      🚫  \"{t['term']}\"")
    print(f"           Campaign: {t['campaign']}  |  AdGroup: {t['ad_group']}")
    print(f"           Spend: ${t['cost']:.2f}  |  Clicks: {t['clicks']}  |  CTR: {t['ctr']:.1%}  |  Conv: 0")

def fmt_exact(t):
    print(f"      ⭐  \"{t['term']}\"")
    print(f"           Campaign: {t['campaign']}  |  AdGroup: {t['ad_group']}")
    print(f"           Conv: {t['conversions']:.0f}  |  CPA: ${t['cpa']:.2f}  |  Cost: ${t['cost']:.2f}  |  Clicks: {t['clicks']}")

def fmt_opportunity(t):
    print(f"      🔍  \"{t['term']}\"")
    print(f"           Campaign: {t['campaign']}  |  AdGroup: {t['ad_group']}")
    print(f"           Clicks: {t['clicks']}  |  CTR: {t['ctr']:.1%}  |  CPC: ${t['cpc']:.2f}  |  Impr: {t['impressions']:,}")

def fmt_promotion(t):
    print(f"      📌  \"{t['term']}\"")
    print(f"           Campaign: {t['campaign']}  |  AdGroup: {t['ad_group']}")
    print(f"           Clicks: {t['clicks']}  |  Conv: {t['conversions']:.0f}  |  CTR: {t['ctr']:.1%}  |  Cost: ${t['cost']:.2f}")


def print_account(client_name, customer_id, terms, days, min_cost):
    if not terms:
        print(f"\n⬜  {client_name} ({customer_id}) — No search term data in last {days} days")
        return

    negatives, exact_cands, opportunities, promotions = analyse(terms, min_cost)

    total_spend = sum(t["cost"] for t in terms)
    wasted_spend = sum(t["cost"] for t in negatives)
    total_conv  = sum(t["conversions"] for t in terms)

    has_neg  = len(negatives) > 0
    has_exact = len(exact_cands) > 0
    icon = "🚫" if has_neg else ("⭐" if has_exact else "✅")

    print(f"\n{icon}  {client_name} ({customer_id})")
    print(f"    {days}-day window  |  {len(terms)} unique terms  |  Total spend: ${total_spend:.2f}  |  Total conv: {total_conv:.0f}")
    if wasted_spend > 0:
        print(f"    ⚠️  Potentially wasted spend: ${wasted_spend:.2f} across {len(negatives)} negative candidate(s)")

    print_section("NEGATIVE CANDIDATES (add these as negatives)", "🚫", negatives, fmt_negative)
    print_section("EXACT MATCH CANDIDATES (add as [exact])", "⭐", exact_cands, fmt_exact)
    print_section("NEW KEYWORD OPPORTUNITIES (consider adding)", "🔍", opportunities, fmt_opportunity)
    print_section("MATCH TYPE PROMOTION SIGNALS (consider exact variant)", "📌", promotions, fmt_promotion)

    return {
        "negatives": len(negatives),
        "exact_cands": len(exact_cands),
        "opportunities": len(opportunities),
        "wasted_spend": wasted_spend,
    }


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Search terms report — negatives, opportunities, match type signals")
    parser.add_argument("--customer-id", help="Single account ID (omit to run all clients)")
    parser.add_argument("--client-name", help="Display name when using --customer-id")
    parser.add_argument("--days",     type=int,   default=30, choices=[7, 14, 30], help="Lookback window (default: 30)")
    parser.add_argument("--min-cost", type=float, default=DEFAULT_MIN_COST,        help=f"Min spend to flag as negative candidate (default: ${DEFAULT_MIN_COST:.0f})")
    args = parser.parse_args()

    client     = build_client()
    ga_service = client.get_service("GoogleAdsService")

    if args.customer_id:
        targets = {(args.client_name or args.customer_id): args.customer_id.replace("-", "")}
    else:
        targets = ALL_CLIENTS

    print("\n" + "="*60)
    print("SEARCH TERMS REPORT")
    print(f"Lookback: {args.days} days  |  Min cost for negative flag: ${args.min_cost:.0f}")
    print("="*60)

    total_negatives    = 0
    total_exact_cands  = 0
    total_opps         = 0
    total_wasted       = 0.0
    errored            = []

    for name, cid in targets.items():
        try:
            terms  = pull_search_terms(ga_service, cid, args.days)
            result = print_account(name, cid, terms, args.days, args.min_cost)
            if result:
                total_negatives   += result["negatives"]
                total_exact_cands += result["exact_cands"]
                total_opps        += result["opportunities"]
                total_wasted      += result["wasted_spend"]
        except Exception as e:
            errored.append(name)
            print(f"\n❌  {name} ({cid}) — Error: {e}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  Accounts checked:       {len(targets) - len(errored)}/{len(targets)}")
    print(f"  🚫 Negative candidates: {total_negatives}  (${total_wasted:.2f} potentially wasted)")
    print(f"  ⭐ Exact match cands:   {total_exact_cands}")
    print(f"  🔍 New opportunities:   {total_opps}")
    if errored:
        print(f"  ❌ Errored:            {', '.join(errored)}")
    if total_negatives == 0 and total_exact_cands == 0 and total_opps == 0:
        print("\n  ✅ No major search term issues found.")
    print("="*60)


if __name__ == "__main__":
    main()
