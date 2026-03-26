"""
Keyword Opportunity Finder
Purpose: Mines search term reports to find queries that are driving traffic
         but are NOT in the keyword list as exact or phrase matches. Groups
         opportunities by:
           - Converting terms not yet keyworded (add as exact match immediately)
           - High-CTR terms not converting (quality traffic, wrong intent match)
           - Terms appearing in multiple campaigns (consolidation opportunities)

         Run this monthly or when starting a new expansion cycle.

Setup:
    Requires environment variables in .env:
        GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID,
        GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN,
        GOOGLE_ADS_CUSTOMER_ID

Usage:
    python3 scripts/keyword_opportunity_finder.py --customer-id 5544702166
    python3 scripts/keyword_opportunity_finder.py --customer-id 5544702166 --days 60

Output:
    Three prioritised lists: converting opportunities, high-CTR opportunities,
    and multi-campaign terms worth consolidating.

Changelog:
    2026-03-23  Initial version — converting terms, high-CTR terms, campaign
                consolidation signals.
"""

import argparse
import os
from collections import defaultdict
from datetime import date, timedelta

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

# ─── CLIENT ──────────────────────────────────────────────────────────────────

def build_client():
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
        for error in ex.failure.errors:
            print(f"  [API Error] {error.message}")
        return []


# ─── PULL DATA ────────────────────────────────────────────────────────────────

def pull_search_terms(ga_service, customer_id, start_date, end_date):
    """Pull all search terms with performance."""
    rows = run_query(ga_service, customer_id, f"""
        SELECT
            search_term_view.search_term,
            search_term_view.status,
            campaign.name,
            ad_group.name,
            metrics.clicks,
            metrics.impressions,
            metrics.conversions,
            metrics.cost_micros
        FROM search_term_view
        WHERE segments.date >= '{start_date}'
          AND segments.date <= '{end_date}'
          AND campaign.status = ENABLED
        ORDER BY metrics.conversions DESC
    """)

    terms = defaultdict(lambda: {
        "campaigns": set(), "clicks": 0, "imps": 0, "conv": 0.0, "cost": 0.0,
        "status": "", "ad_groups": set()
    })

    for row in rows:
        term = row.search_term_view.search_term.lower().strip()
        t    = terms[term]
        t["campaigns"].add(row.campaign.name)
        t["ad_groups"].add(row.ad_group.name)
        t["clicks"] += row.metrics.clicks
        t["imps"]   += row.metrics.impressions
        t["conv"]   += row.metrics.conversions
        t["cost"]   += row.metrics.cost_micros / 1_000_000
        t["status"]  = row.search_term_view.status.name  # ADDED (already a keyword) or NONE

    return terms


def pull_existing_keywords(ga_service, customer_id):
    """Pull all existing active keywords (exact and phrase) for dedup check."""
    rows = run_query(ga_service, customer_id, """
        SELECT
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type
        FROM keyword_view
        WHERE ad_group_criterion.status = ENABLED
          AND ad_group.status = ENABLED
          AND campaign.status = ENABLED
    """)

    keywords = set()
    for row in rows:
        text = row.ad_group_criterion.keyword.text.lower().strip()
        keywords.add(text)

    return keywords


def pull_account_avg_ctr(ga_service, customer_id, start_date, end_date):
    """Account-level CTR for the period (benchmark for high-CTR filter)."""
    rows = run_query(ga_service, customer_id, f"""
        SELECT metrics.clicks, metrics.impressions
        FROM customer
        WHERE segments.date >= '{start_date}' AND segments.date <= '{end_date}'
    """)
    clicks = sum(r.metrics.clicks for r in rows)
    imps   = sum(r.metrics.impressions for r in rows)
    return clicks / imps if imps > 0 else 0.05


# ─── ANALYSIS ─────────────────────────────────────────────────────────────────

def find_opportunities(terms, existing_keywords, avg_ctr, min_clicks=3):
    """
    Split search terms into three opportunity buckets.
    Excludes terms that are already exact/phrase match keywords.
    """
    converting   = []  # has conversions, not yet a keyword
    high_ctr     = []  # CTR > 2x account avg, 0 conv, not yet a keyword
    multi_camp   = []  # appearing across multiple campaigns (consolidation)

    for term, data in terms.items():
        # Skip if already an exact match keyword
        if term in existing_keywords:
            continue

        # Skip very low traffic terms
        if data["clicks"] < min_clicks:
            continue

        ctr = data["clicks"] / data["imps"] if data["imps"] > 0 else 0
        cpa = data["cost"] / data["conv"] if data["conv"] > 0 else 0

        item = {
            "term":       term,
            "clicks":     data["clicks"],
            "conv":       data["conv"],
            "cost":       data["cost"],
            "ctr":        ctr,
            "cpa":        cpa,
            "campaigns":  sorted(data["campaigns"]),
            "n_camps":    len(data["campaigns"]),
        }

        if data["conv"] >= 1:
            converting.append(item)
        elif ctr >= avg_ctr * 2 and data["imps"] >= 20:
            high_ctr.append(item)

        if len(data["campaigns"]) >= 2 and data["conv"] >= 1:
            multi_camp.append(item)

    return (
        sorted(converting, key=lambda x: -x["conv"]),
        sorted(high_ctr,   key=lambda x: -x["ctr"]),
        sorted(multi_camp, key=lambda x: -x["n_camps"]),
    )


# ─── PRINT ────────────────────────────────────────────────────────────────────

def print_report(customer_id, client_name, converting, high_ctr, multi_camp,
                 start_date, end_date, total_terms, avg_ctr):
    print(f"\nKEYWORD OPPORTUNITY FINDER — {client_name} ({customer_id})")
    print(f"Period: {start_date} to {end_date}  |  {total_terms} unique search terms")
    print(f"Account avg CTR: {avg_ctr*100:.2f}%")
    print("=" * 70)

    # BUCKET 1: Converting terms
    print(f"\n[1] CONVERTING TERMS NOT YET KEYWORDED ({len(converting)} found)")
    print("    These are converting from broad/phrase match — add as exact match")
    print("    to get more control, better QS, and lower CPA.")
    print()
    if converting:
        print(f"  {'Term':<40} {'Conv':>5} {'Clicks':>6} {'Cost':>8} {'CPA':>7}")
        print(f"  {'-'*40} {'-'*5} {'-'*6} {'-'*8} {'-'*7}")
        for t in converting[:25]:
            print(f"  {t['term']:<40} {t['conv']:>5.0f} {t['clicks']:>6} ${t['cost']:>7.2f} ${t['cpa']:>6.2f}")
    else:
        print("  No converting terms found outside existing keyword list.")

    # BUCKET 2: High-CTR, zero-conversion
    print(f"\n[2] HIGH-CTR TERMS (NO CONVERSIONS) ({len(high_ctr)} found)")
    print("    CTR is >2x account average — people are clicking but not converting.")
    print("    Check: landing page match, offer clarity, or wrong intent stage.")
    print()
    if high_ctr:
        print(f"  {'Term':<40} {'CTR':>6} {'Clicks':>6} {'Imps':>7} {'Cost':>8}")
        print(f"  {'-'*40} {'-'*6} {'-'*6} {'-'*7} {'-'*8}")
        for t in high_ctr[:20]:
            print(f"  {t['term']:<40} {t['ctr']*100:>5.1f}% {t['clicks']:>6} {t['cost']:>8.2f}")
    else:
        print("  No high-CTR zero-conversion terms found.")

    # BUCKET 3: Multi-campaign terms
    print(f"\n[3] CONVERTING TERMS IN MULTIPLE CAMPAIGNS ({len(multi_camp)} found)")
    print("    These terms are converting across multiple campaigns — possible")
    print("    budget splitting, quality score dilution, and attribution confusion.")
    print()
    if multi_camp:
        print(f"  {'Term':<40} {'Conv':>5} {'Camps':>5} {'Campaigns'}")
        print(f"  {'-'*40} {'-'*5} {'-'*5} {'-'*30}")
        for t in multi_camp[:15]:
            camps = ", ".join(t["campaigns"][:2])
            if len(t["campaigns"]) > 2:
                camps += f" +{len(t['campaigns'])-2} more"
            print(f"  {t['term']:<40} {t['conv']:>5.0f} {t['n_camps']:>5} {camps}")
    else:
        print("  No multi-campaign terms found.")

    print("\n" + "=" * 70)
    total_opp = len(converting) + len(high_ctr)
    print(f"  Total opportunities: {total_opp}")
    print(f"  Converting terms to add as exact match: {len(converting)}")
    print(f"  High-CTR terms to investigate: {len(high_ctr)}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Keyword opportunity finder — mine search terms for expansion"
    )
    parser.add_argument("--customer-id", required=True, help="Account ID")
    parser.add_argument("--client-name", help="Display name (optional)")
    parser.add_argument("--days",        type=int, default=30,
                        help="Lookback window in days (default: 30)")
    parser.add_argument("--min-clicks",  type=int, default=3,
                        help="Min clicks to consider a term (default: 3)")
    args = parser.parse_args()

    today      = date.today()
    start_date = (today - timedelta(days=args.days)).strftime("%Y-%m-%d")
    end_date   = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    cid        = args.customer_id.replace("-", "")

    client_name = args.client_name
    if not client_name:
        for name, id_ in ALL_CLIENTS.items():
            if id_ == cid:
                client_name = name
                break
        if not client_name:
            client_name = cid

    ga_client  = build_client()
    ga_service = ga_client.get_service("GoogleAdsService")

    print(f"\nAnalysing {client_name} ...")
    terms    = pull_search_terms(ga_service, cid, start_date, end_date)
    keywords = pull_existing_keywords(ga_service, cid)
    avg_ctr  = pull_account_avg_ctr(ga_service, cid, start_date, end_date)

    print(f"  {len(terms)} unique search terms, {len(keywords)} existing keywords")

    converting, high_ctr, multi_camp = find_opportunities(
        terms, keywords, avg_ctr, min_clicks=args.min_clicks
    )

    print_report(
        cid, client_name, converting, high_ctr, multi_camp,
        start_date, end_date, len(terms), avg_ctr
    )


if __name__ == "__main__":
    main()
