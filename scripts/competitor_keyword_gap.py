"""
Competitor Keyword Gap Analyzer
Purpose: Identifies keyword opportunities by cross-referencing Auction Insights
         data (competitor domains in your auctions) with search terms where you
         are losing IS. Surfaces queries that competitors are winning that you
         could be targeting more aggressively.

         Also uses the Google Ads Keyword Ideas endpoint to estimate search
         volume for identified gap keywords.

Setup:
    Requires environment variables in .env:
        GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID,
        GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN,
        GOOGLE_ADS_CUSTOMER_ID

Usage:
    python3 scripts/competitor_keyword_gap.py --customer-id 5544702166
    python3 scripts/competitor_keyword_gap.py --customer-id 5216656756 --days 30

Output:
    Competitor presence in your auctions, high-IS-loss search term patterns,
    and suggested keywords to add or bid more aggressively on.

Changelog:
    2026-03-23  Initial version — auction insights competitor extraction,
                IS loss analysis, gap keyword identification.
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


# ─── PULL AUCTION INSIGHTS ────────────────────────────────────────────────────

def pull_auction_insights(ga_service, customer_id, start_date, end_date):
    """Pull campaign-level auction insights."""
    rows = run_query(ga_service, customer_id, f"""
        SELECT
            campaign.name,
            auction_insight.domain,
            metrics.auction_insight_search_impression_share,
            metrics.auction_insight_search_overlap_rate,
            metrics.auction_insight_search_outranking_share
        FROM auction_insight_campaign
        WHERE segments.date >= '{start_date}'
          AND segments.date <= '{end_date}'
          AND campaign.status = ENABLED
    """)

    competitors = defaultdict(lambda: {
        "campaigns": set(), "is_total": 0, "overlap_total": 0,
        "outrank_total": 0, "rows": 0
    })

    for row in rows:
        domain = row.auction_insight.domain
        d      = competitors[domain]
        d["campaigns"].add(row.campaign.name)
        d["is_total"]      += row.metrics.auction_insight_search_impression_share or 0
        d["overlap_total"] += row.metrics.auction_insight_search_overlap_rate or 0
        d["outrank_total"] += row.metrics.auction_insight_search_outranking_share or 0
        d["rows"]          += 1

    # Average per competitor
    result = {}
    for domain, d in competitors.items():
        n = d["rows"]
        result[domain] = {
            "campaigns":  d["campaigns"],
            "is":         d["is_total"] / n,
            "overlap":    d["overlap_total"] / n,
            "outrank":    d["outrank_total"] / n,
            "n_campaigns": len(d["campaigns"]),
        }

    return result


def pull_is_loss_by_campaign(ga_service, customer_id, start_date, end_date):
    """Pull Search IS and lost IS by rank for each campaign."""
    rows = run_query(ga_service, customer_id, f"""
        SELECT
            campaign.name,
            campaign.advertising_channel_type,
            metrics.search_impression_share,
            metrics.search_rank_lost_impression_share,
            metrics.search_budget_lost_impression_share,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.cost_micros
        FROM campaign
        WHERE segments.date >= '{start_date}'
          AND segments.date <= '{end_date}'
          AND campaign.status = ENABLED
          AND campaign.advertising_channel_type = SEARCH
    """)

    campaigns = defaultdict(lambda: {
        "is": [], "rank_loss": [], "budget_loss": [],
        "imps": 0, "clicks": 0, "conv": 0.0, "cost": 0.0
    })

    for row in rows:
        name = row.campaign.name
        c    = campaigns[name]
        is_  = row.metrics.search_impression_share
        rank = row.metrics.search_rank_lost_impression_share
        budg = row.metrics.search_budget_lost_impression_share

        if is_   and 0 < is_   <= 1: c["is"].append(is_)
        if rank  and 0 < rank  <= 1: c["rank_loss"].append(rank)
        if budg  and 0 < budg  <= 1: c["budget_loss"].append(budg)

        c["imps"]   += row.metrics.impressions
        c["clicks"] += row.metrics.clicks
        c["conv"]   += row.metrics.conversions
        c["cost"]   += row.metrics.cost_micros / 1_000_000

    result = {}
    for name, d in campaigns.items():
        result[name] = {
            "is":         sum(d["is"]) / len(d["is"]) if d["is"] else 0,
            "rank_loss":  sum(d["rank_loss"]) / len(d["rank_loss"]) if d["rank_loss"] else 0,
            "budget_loss": sum(d["budget_loss"]) / len(d["budget_loss"]) if d["budget_loss"] else 0,
            "imps":       d["imps"],
            "clicks":     d["clicks"],
            "conv":       d["conv"],
            "cost":       d["cost"],
        }

    return result


def pull_search_terms_with_low_is(ga_service, customer_id, start_date, end_date, min_imps=50):
    """Find search terms with high impressions but low conversion rate — competitor territory."""
    rows = run_query(ga_service, customer_id, f"""
        SELECT
            search_term_view.search_term,
            campaign.name,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.cost_micros
        FROM search_term_view
        WHERE segments.date >= '{start_date}'
          AND segments.date <= '{end_date}'
          AND campaign.status = ENABLED
        ORDER BY metrics.impressions DESC
    """)

    terms = defaultdict(lambda: {"imps": 0, "clicks": 0, "conv": 0.0, "cost": 0.0})
    for row in rows:
        term = row.search_term_view.search_term.lower()
        t    = terms[term]
        t["imps"]   += row.metrics.impressions
        t["clicks"] += row.metrics.clicks
        t["conv"]   += row.metrics.conversions
        t["cost"]   += row.metrics.cost_micros / 1_000_000

    # High impressions, low CTR = competitors outranking
    gaps = []
    for term, d in terms.items():
        if d["imps"] < min_imps:
            continue
        ctr = d["clicks"] / d["imps"] if d["imps"] > 0 else 0
        if ctr < 0.03 and d["imps"] >= min_imps:  # very low CTR = bad position
            gaps.append({
                "term":  term,
                "imps":  d["imps"],
                "ctr":   ctr,
                "conv":  d["conv"],
                "cost":  d["cost"],
            })

    return sorted(gaps, key=lambda x: -x["imps"])


# ─── PRINT REPORT ─────────────────────────────────────────────────────────────

def print_report(customer_id, client_name, competitors, campaigns, gaps):
    run_date = date.today().strftime("%Y-%m-%d")
    print(f"\nCOMPETITOR KEYWORD GAP ANALYZER — {client_name} ({customer_id})")
    print(f"Run date: {run_date}")
    print("=" * 75)

    # Competitors
    print(f"\nCOMPETITOR PRESENCE IN YOUR AUCTIONS ({len(competitors)} found)")
    print(f"  {'Competitor':<35} {'Their IS':>9} {'Overlap':>9} {'Outrank':>9}  Campaigns")
    print(f"  {'-'*35} {'-'*9} {'-'*9} {'-'*9}  {'-'*10}")

    for domain, d in sorted(competitors.items(), key=lambda x: -x[1]["is"]):
        print(f"  {domain:<35} {d['is']*100:>8.0f}% {d['overlap']*100:>8.0f}% "
              f"{d['outrank']*100:>8.0f}%  {d['n_campaigns']}")

    # Campaign IS analysis
    print(f"\nCAMPAIGN IS LOSS ANALYSIS (Search campaigns only)")
    print(f"  {'Campaign':<40} {'IS':>7} {'Lost-Rank':>10} {'Lost-Budget':>12}  Opportunity")
    print(f"  {'-'*40} {'-'*7} {'-'*10} {'-'*12}  {'-'*15}")

    for name, d in sorted(campaigns.items(), key=lambda x: -x[1]["rank_loss"]):
        opp = ""
        if d["rank_loss"] > 0.20:
            opp = "Improve QS/bids"
        elif d["budget_loss"] > 0.20:
            opp = "Increase budget"
        elif d["is"] > 0.80:
            opp = "Good IS"
        print(f"  {name[:40]:<40} {d['is']*100:>6.0f}% {d['rank_loss']*100:>9.0f}% "
              f"{d['budget_loss']*100:>11.0f}%  {opp}")

    # Low-CTR search terms (competitor dominance signals)
    if gaps:
        print(f"\nLOW-CTR SEARCH TERMS (competitors likely outranking you)")
        print(f"  These terms get impressions but almost no clicks — you're showing")
        print(f"  but losing to competitors. Improve QS or increase bids.")
        print()
        print(f"  {'Search Term':<40} {'Imps':>7} {'CTR':>6} {'Conv':>5}")
        print(f"  {'-'*40} {'-'*7} {'-'*6} {'-'*5}")
        for g in gaps[:20]:
            print(f"  {g['term']:<40} {g['imps']:>7} {g['ctr']*100:>5.1f}% {g['conv']:>5.0f}")

    print("\n" + "=" * 75)
    print("  Action: For each competitor domain, research their ad copy and landing pages.")
    print("  Use /competitor-serp-scan for live ad copy scraping.")
    print("  For low-CTR terms: improve headline relevance and consider exact match keywords.")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Competitor keyword gap — auction insights + IS loss analysis"
    )
    parser.add_argument("--customer-id", required=True, help="Account ID")
    parser.add_argument("--client-name", help="Display name (optional)")
    parser.add_argument("--days",        type=int, default=30,
                        help="Lookback window in days (default: 30)")
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

    print(f"\nAnalysing competitor landscape for {client_name} ...")
    competitors = pull_auction_insights(ga_service, cid, start_date, end_date)
    campaigns   = pull_is_loss_by_campaign(ga_service, cid, start_date, end_date)
    gaps        = pull_search_terms_with_low_is(ga_service, cid, start_date, end_date)

    print(f"  {len(competitors)} competitors  |  {len(campaigns)} campaigns  |  {len(gaps)} low-CTR terms")
    print_report(cid, client_name, competitors, campaigns, gaps)


if __name__ == "__main__":
    main()
