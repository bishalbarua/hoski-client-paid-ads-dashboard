"""
N-Gram Analyzer
Purpose: Breaks all search terms in an account into 1, 2, and 3-word n-grams.
         Aggregates clicks, conversions, and cost per phrase. Surfaces:
           - High-cost, zero-conversion n-grams (negative keyword candidates)
           - High-converting n-grams (expand into dedicated keywords/ad groups)
           - Intent signals across the account search term corpus

         Invaluable for structural negative keyword development — rather than
         adding individual terms, you add phrase patterns that block thousands
         of irrelevant queries at once.

Setup:
    Requires environment variables in .env:
        GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID,
        GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN,
        GOOGLE_ADS_CUSTOMER_ID

Usage:
    python3 scripts/n_gram_analyzer.py --customer-id 5544702166
    python3 scripts/n_gram_analyzer.py --customer-id 5544702166 --days 60
    python3 scripts/n_gram_analyzer.py --customer-id 5544702166 --min-clicks 5

Output:
    Prints negative n-gram candidates (cost, no conv) and positive n-gram
    patterns (high converting). Saves full output to
    clients/[name]/analysis/ngrams-YYYY-MM-DD.md if --save is set.

Changelog:
    2026-03-23  Initial version — tri-gram analysis with wasted spend sorting
                and keyword expansion candidates.
"""

import argparse
import os
import re
from collections import defaultdict
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

# Common stopwords to exclude from n-gram analysis (rarely meaningful alone)
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "be", "been",
    "this", "that", "it", "i", "you", "my", "me", "we",
}

# ─── GOOGLE ADS CLIENT ───────────────────────────────────────────────────────

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


# ─── PULL SEARCH TERMS ────────────────────────────────────────────────────────

def pull_search_terms(ga_service, customer_id, start_date, end_date):
    rows = run_query(ga_service, customer_id, f"""
        SELECT
            search_term_view.search_term,
            metrics.clicks,
            metrics.conversions,
            metrics.cost_micros,
            metrics.impressions
        FROM search_term_view
        WHERE segments.date >= '{start_date}'
          AND segments.date <= '{end_date}'
          AND campaign.status = ENABLED
    """)

    terms = []
    seen  = set()
    for row in rows:
        term = row.search_term_view.search_term.lower().strip()
        if term in seen:
            continue
        seen.add(term)
        terms.append({
            "term":    term,
            "clicks":  row.metrics.clicks,
            "conv":    row.metrics.conversions,
            "cost":    row.metrics.cost_micros / 1_000_000,
            "imps":    row.metrics.impressions,
        })

    return terms


# ─── N-GRAM EXTRACTION ────────────────────────────────────────────────────────

def tokenize(text):
    """Simple whitespace tokenizer, removes punctuation."""
    return re.sub(r"[^\w\s]", "", text).split()


def extract_ngrams(term_data, n, exclude_stopwords_unigrams=True):
    """
    Aggregate n-gram performance across all search terms.
    For unigrams (n=1), optionally skip pure stopwords.
    """
    ngram_stats = defaultdict(lambda: {
        "clicks": 0, "conv": 0.0, "cost": 0.0, "imps": 0, "term_count": 0
    })

    for t in term_data:
        tokens = tokenize(t["term"])
        if len(tokens) < n:
            continue

        # Generate all n-grams from this term
        for i in range(len(tokens) - n + 1):
            gram = " ".join(tokens[i : i + n])

            # For unigrams, skip pure stopwords
            if n == 1 and exclude_stopwords_unigrams and gram in STOPWORDS:
                continue

            ngram_stats[gram]["clicks"]     += t["clicks"]
            ngram_stats[gram]["conv"]       += t["conv"]
            ngram_stats[gram]["cost"]       += t["cost"]
            ngram_stats[gram]["imps"]       += t["imps"]
            ngram_stats[gram]["term_count"] += 1

    return ngram_stats


# ─── ANALYSIS ─────────────────────────────────────────────────────────────────

def find_negative_candidates(ngram_stats, min_clicks=3, min_cost=5.0):
    """High clicks + high cost + 0 conversions = negative candidates."""
    candidates = []
    for gram, s in ngram_stats.items():
        if s["clicks"] >= min_clicks and s["cost"] >= min_cost and s["conv"] == 0:
            candidates.append({
                "gram":   gram,
                "clicks": s["clicks"],
                "cost":   s["cost"],
                "conv":   s["conv"],
                "terms":  s["term_count"],
            })
    return sorted(candidates, key=lambda x: -x["cost"])


def find_positive_patterns(ngram_stats, min_conv=1.0):
    """High-converting n-grams that may warrant dedicated targeting."""
    patterns = []
    for gram, s in ngram_stats.items():
        if s["conv"] >= min_conv:
            cpa = s["cost"] / s["conv"] if s["conv"] > 0 else 0
            patterns.append({
                "gram":   gram,
                "clicks": s["clicks"],
                "cost":   s["cost"],
                "conv":   s["conv"],
                "cpa":    cpa,
                "terms":  s["term_count"],
            })
    return sorted(patterns, key=lambda x: -x["conv"])


# ─── PRINT REPORT ─────────────────────────────────────────────────────────────

def print_report(customer_id, client_name, term_data, start_date, end_date, min_clicks):
    run_date = date.today().strftime("%Y-%m-%d")
    print(f"\nN-GRAM ANALYSIS — {client_name} ({customer_id})")
    print(f"Period: {start_date} to {end_date}  |  {len(term_data)} search terms")
    print("=" * 70)

    total_cost = sum(t["cost"] for t in term_data)
    total_conv = sum(t["conv"] for t in term_data)
    print(f"  Total spend: ${total_cost:.2f}  |  Total conv: {total_conv:.0f}")
    print()

    for n in [1, 2, 3]:
        label = {1: "UNIGRAMS (single words)", 2: "BIGRAMS (2-word phrases)", 3: "TRIGRAMS (3-word phrases)"}[n]
        print(f"─── {label} ──────────────────────────────────────────")

        stats    = extract_ngrams(term_data, n)
        neg_cand = find_negative_candidates(stats, min_clicks=min_clicks)
        pos_patt = find_positive_patterns(stats, min_conv=1.0)

        if neg_cand:
            total_wasted = sum(c["cost"] for c in neg_cand)
            print(f"\n  NEGATIVE CANDIDATES ({len(neg_cand)} phrases, ${total_wasted:.2f} wasted spend)")
            print(f"  {'Phrase':<35} {'Clicks':>6} {'Cost':>8} {'Conv':>5} {'Terms':>6}")
            print(f"  {'-'*35} {'-'*6} {'-'*8} {'-'*5} {'-'*6}")
            for c in neg_cand[:20]:
                print(f"  {c['gram']:<35} {c['clicks']:>6} ${c['cost']:>7.2f} {c['conv']:>5.0f} {c['terms']:>6}")

        if pos_patt:
            print(f"\n  HIGH-CONVERTING PATTERNS ({len(pos_patt)} phrases)")
            print(f"  {'Phrase':<35} {'Conv':>5} {'Cost':>8} {'CPA':>7} {'Terms':>6}")
            print(f"  {'-'*35} {'-'*5} {'-'*8} {'-'*7} {'-'*6}")
            for p in pos_patt[:15]:
                print(f"  {p['gram']:<35} {p['conv']:>5.0f} ${p['cost']:>7.2f} ${p['cpa']:>6.2f} {p['terms']:>6}")

        if not neg_cand and not pos_patt:
            print(f"  No significant n-grams found (try lowering --min-clicks)")

        print()

    print("=" * 70)
    print("  Negative candidates: add as phrase match negatives at campaign level")
    print("  Converting patterns: consider dedicated ad groups or exact-match keywords")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="N-gram analysis — structural keyword and negative keyword intelligence"
    )
    parser.add_argument("--customer-id", required=True,
                        help="Account ID to analyse")
    parser.add_argument("--client-name", help="Display name (optional)")
    parser.add_argument("--days",        type=int, default=30,
                        help="Lookback window in days (default: 30)")
    parser.add_argument("--min-clicks",  type=int, default=3,
                        help="Min clicks to surface a negative candidate (default: 3)")
    args = parser.parse_args()

    today      = date.today()
    start_date = (today - timedelta(days=args.days)).strftime("%Y-%m-%d")
    end_date   = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    cid        = args.customer_id.replace("-", "")

    # Look up client name from registry
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

    print(f"\nPulling search terms for {client_name} ...")
    term_data = pull_search_terms(ga_service, cid, start_date, end_date)
    print(f"  {len(term_data)} unique search terms found")

    if not term_data:
        print("  No search term data found. Check account activity and date range.")
        return

    print_report(cid, client_name, term_data, start_date, end_date, args.min_clicks)


if __name__ == "__main__":
    main()
