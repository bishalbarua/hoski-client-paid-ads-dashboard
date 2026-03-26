"""
Keyword Theme Expander
Purpose: Takes a client's current keyword list and uses the Claude API to:
           1. Identify keyword themes in the client's category that are NOT
              currently being targeted
           2. Cross-reference with search term data to see if any of those
              untargeted themes are already driving traffic (via broad match)
           3. Produce an expansion brief with themes, example keywords, search
              intent classification, and priority score

         Use this when launching new ad groups, planning account expansion,
         or when a client wants to grow volume.

Setup:
    Requires environment variables in .env:
        GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID,
        GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN,
        GOOGLE_ADS_CUSTOMER_ID
        ANTHROPIC_API_KEY

Usage:
    python3 scripts/keyword_theme_expander.py --customer-id 5544702166
    python3 scripts/keyword_theme_expander.py --customer-id 5216656756 --business "dental clinic"

Changelog:
    2026-03-23  Initial version — current keyword extraction, Claude theme
                analysis, search term cross-reference, expansion brief.
"""

import argparse
import json
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

CLIENT_BUSINESS_TYPES = {
    "5865660247": "personal injury and car accident law firm in Texas",
    "3857223862": "dental clinic in Montreal offering general and cosmetic dentistry",
    "7709532223": "estate jewelry buyer and seller",
    "9304117954": "medical spa offering botox, fillers, and aesthetic treatments",
    "5544702166": "premium performance socks brand",
    "3720173680": "craft brewery in Ontario",
    "7228467515": "custom furniture store in Ontario",
    "8134824884": "family medical clinic",
    "7628667762": "spine and nerve surgery centre",
    "8159668041": "home care services for seniors in Texas",
    "5216656756": "dental clinic in Ontario offering implants, veneers, and general dentistry",
    "5907367258": "dental clinic in Ontario",
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


# ─── PULL CURRENT KEYWORDS ────────────────────────────────────────────────────

def pull_current_keywords(ga_service, customer_id):
    """Pull all active keywords with their ad group context."""
    rows = run_query(ga_service, customer_id, """
        SELECT
            campaign.name,
            ad_group.name,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type
        FROM keyword_view
        WHERE ad_group_criterion.status = ENABLED
          AND ad_group.status = ENABLED
          AND campaign.status = ENABLED
        ORDER BY campaign.name, ad_group.name
    """)

    keywords = []
    seen     = set()
    for row in rows:
        text = row.ad_group_criterion.keyword.text.lower()
        if text not in seen:
            seen.add(text)
            keywords.append({
                "text":      text,
                "match":     row.ad_group_criterion.keyword.match_type.name,
                "campaign":  row.campaign.name,
                "ad_group":  row.ad_group.name,
            })

    return keywords


def pull_search_terms(ga_service, customer_id, start_date, end_date):
    """Pull converting search terms for cross-reference."""
    rows = run_query(ga_service, customer_id, f"""
        SELECT
            search_term_view.search_term,
            metrics.clicks,
            metrics.conversions,
            metrics.cost_micros
        FROM search_term_view
        WHERE segments.date >= '{start_date}'
          AND segments.date <= '{end_date}'
          AND campaign.status = ENABLED
        ORDER BY metrics.conversions DESC
    """)

    terms = {}
    for row in rows:
        term = row.search_term_view.search_term.lower()
        if term not in terms:
            terms[term] = {"clicks": 0, "conv": 0.0, "cost": 0.0}
        terms[term]["clicks"] += row.metrics.clicks
        terms[term]["conv"]   += row.metrics.conversions
        terms[term]["cost"]   += row.metrics.cost_micros / 1_000_000

    return terms


# ─── CLAUDE THEME EXPANSION ──────────────────────────────────────────────────

def expand_themes_claude(current_keywords, business_type, client_name):
    """Use Claude to identify untargeted keyword themes."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None, "ANTHROPIC_API_KEY not set"

    try:
        import anthropic
        client_ai = anthropic.Anthropic(api_key=api_key)

        kw_sample = [k["text"] for k in current_keywords[:80]]  # sample to avoid token overflow
        kw_list   = "\n".join(f"- {k}" for k in kw_sample)

        prompt = f"""You are a Google Ads specialist analysing keyword coverage for a client.

Business: {client_name}
Business type: {business_type}

Current keyword list ({len(current_keywords)} total, showing sample):
{kw_list}

Your task:
1. Identify 5-8 keyword THEMES that are relevant to this business but NOT represented in the current keyword list
2. For each theme, provide:
   - Theme name (2-4 words)
   - Why it's relevant to this business
   - 3-5 example keywords
   - Intent classification: TRANSACTIONAL, INFORMATIONAL, NAVIGATIONAL, or COMMERCIAL
   - Priority: HIGH (ready to buy), MEDIUM (consideration stage), or LOW (top of funnel)

Return your response as a JSON array with this structure:
[
  {{
    "theme": "theme name",
    "rationale": "why relevant",
    "keywords": ["kw1", "kw2", "kw3"],
    "intent": "TRANSACTIONAL",
    "priority": "HIGH"
  }}
]

Return ONLY the JSON array, no other text."""

        message = client_ai.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()
        # Extract JSON from response
        start = response_text.find("[")
        end   = response_text.rfind("]") + 1
        if start != -1 and end > start:
            themes = json.loads(response_text[start:end])
            return themes, None

        return None, "Could not parse JSON from Claude response"

    except Exception as e:
        return None, str(e)


# ─── CROSS-REFERENCE ──────────────────────────────────────────────────────────

def cross_reference_search_terms(themes, search_terms):
    """Check if any theme keywords already appear in search term data."""
    for theme in themes:
        theme["in_search_terms"] = []
        for kw in theme.get("keywords", []):
            for term, data in search_terms.items():
                if kw.lower() in term or term in kw.lower():
                    theme["in_search_terms"].append({
                        "term":   term,
                        "clicks": data["clicks"],
                        "conv":   data["conv"],
                    })

    return themes


# ─── PRINT REPORT ─────────────────────────────────────────────────────────────

def print_report(customer_id, client_name, current_keywords, themes, search_terms):
    run_date = date.today().strftime("%Y-%m-%d")
    print(f"\nKEYWORD THEME EXPANDER — {client_name} ({customer_id})")
    print(f"Current active keywords: {len(current_keywords)}  |  Run date: {run_date}")
    print("=" * 70)

    if not themes:
        print("  Could not generate theme expansion. Check ANTHROPIC_API_KEY.")
        return

    # Sort: HIGH priority first, then TRANSACTIONAL intent
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    themes.sort(key=lambda x: order.get(x.get("priority", "LOW"), 2))

    for t in themes:
        priority = t.get("priority", "?")
        intent   = t.get("intent", "?")
        print(f"\n  [{priority}] {t['theme'].upper()}")
        print(f"  Intent: {intent}")
        print(f"  Why: {t['rationale']}")
        print(f"  Starter keywords:")
        for kw in t.get("keywords", []):
            print(f"    - {kw}")

        in_terms = t.get("in_search_terms", [])
        if in_terms:
            print(f"  Already appearing in search terms (from broad match):")
            for s in in_terms[:5]:
                print(f"    - \"{s['term']}\" ({s['clicks']} clicks, {s['conv']:.0f} conv)")
            if len(in_terms) > 5:
                print(f"    ... and {len(in_terms)-5} more")

    print(f"\n{'='*70}")
    high = sum(1 for t in themes if t.get("priority") == "HIGH")
    print(f"  High priority expansion themes: {high}/{len(themes)}")
    print(f"  Use /keyword-research to build out full ad groups for each theme.")
    print("=" * 70)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Keyword theme expander — find untargeted themes using Claude"
    )
    parser.add_argument("--customer-id", required=True, help="Account ID")
    parser.add_argument("--client-name", help="Display name (optional)")
    parser.add_argument("--business",    help="Business description (optional, overrides preset)")
    parser.add_argument("--days",        type=int, default=30,
                        help="Search term lookback in days (default: 30)")
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

    business_type = args.business or CLIENT_BUSINESS_TYPES.get(cid, "local business")

    ga_client  = build_client()
    ga_service = ga_client.get_service("GoogleAdsService")

    print(f"\nAnalysing keyword coverage for {client_name} ...")
    print(f"Business type: {business_type}")

    current_keywords = pull_current_keywords(ga_service, cid)
    search_terms     = pull_search_terms(ga_service, cid, start_date, end_date)
    print(f"  {len(current_keywords)} active keywords, {len(search_terms)} search terms")

    print(f"  Generating theme expansion via Claude ...")
    themes, error = expand_themes_claude(current_keywords, business_type, client_name)

    if error:
        print(f"  Error: {error}")
        return

    themes = cross_reference_search_terms(themes or [], search_terms)
    print_report(cid, client_name, current_keywords, themes, search_terms)


if __name__ == "__main__":
    main()
