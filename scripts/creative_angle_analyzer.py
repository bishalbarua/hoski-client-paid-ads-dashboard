"""
Creative Angle Analyzer
Purpose: Pulls all RSA (Responsive Search Ad) assets from a client account via
         the Google Ads API. Classifies each headline and description by "copy
         angle" type, then measures which angle types have above/below average
         CTR and conversion rate. Surfaces underutilised angles and uses the
         Claude API to generate 5 new headline ideas for the weakest angle.

         Copy angle types:
           PRICE_OFFER    — "$99", "Free", "Save 20%", "From $X/month"
           SOCIAL_PROOF   — "Trusted by", "#1 rated", "1,000+ customers"
           URGENCY        — "Limited time", "Today only", "Act now"
           FEATURE        — What the product/service does or has
           OUTCOME        — What the customer achieves ("Get results in 30 days")
           CTA            — "Call now", "Book today", "Get a free quote"
           BRAND          — Brand name or branded differentiator

Setup:
    Requires environment variables in .env:
        GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID,
        GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN,
        GOOGLE_ADS_CUSTOMER_ID
        ANTHROPIC_API_KEY  (for Claude API headline generation)

Usage:
    python3 scripts/creative_angle_analyzer.py --customer-id 5544702166
    python3 scripts/creative_angle_analyzer.py --customer-id 5544702166 --no-generate

Changelog:
    2026-03-23  Initial version — angle classification, CTR/CVR by angle,
                underutilised angle detection, Claude-powered headline generation.
"""

import argparse
import os
import re
from collections import defaultdict

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

# ─── ANGLE CLASSIFICATION ────────────────────────────────────────────────────

ANGLE_PATTERNS = {
    "PRICE_OFFER": [
        r"\$[\d,]+", r"\bfree\b", r"\bsave\b", r"\bdiscount\b", r"\b\d+%\s*off\b",
        r"\bpromo\b", r"\bdeal\b", r"\baffordable\b", r"\blow\s*price\b",
        r"\bno\s*charge\b", r"\bcomplimentary\b",
    ],
    "SOCIAL_PROOF": [
        r"\btrusted\b", r"\b\d+[\+k]?\s*(customers?|clients?|patients?|reviews?)\b",
        r"\brated\b", r"\baward\b", r"\bcertified\b", r"\baccredited\b",
        r"\b#\s*1\b", r"\bbest\s*in\b", r"\bover\s*\d+\b",
    ],
    "URGENCY": [
        r"\blimited\s*time\b", r"\btoday\s*only\b", r"\bexpires?\b", r"\bhurry\b",
        r"\bact\s*now\b", r"\blast\s*chance\b", r"\bdon'?t\s*wait\b",
        r"\bthis\s*week\b", r"\bthis\s*month\b",
    ],
    "CTA": [
        r"\bcall\s*(now|today|us)\b", r"\bbook\b", r"\bschedule\b",
        r"\bget\s*(a|your|free)\b", r"\bcontact\b", r"\bstarts?\b",
        r"\bshop\b", r"\bvisit\b", r"\blearn\s*more\b", r"\bsign\s*up\b",
        r"\bapply\b", r"\brequest\b",
    ],
    "OUTCOME": [
        r"\bget\s+results?\b", r"\bfeel\b", r"\blook\b", r"\bachiev\b",
        r"\btransform\b", r"\bimprove\b", r"\bincrease\b", r"\bgrow\b",
        r"\bsuccess\b", r"\blose\b", r"\bgain\b", r"\brelief\b", r"\bheal\b",
        r"\bbetter\b",
    ],
}


def classify_angle(text):
    """Return the primary angle type for a piece of ad copy."""
    text_lower = text.lower()
    scores = defaultdict(int)

    for angle, patterns in ANGLE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                scores[angle] += 1

    if not scores:
        return "FEATURE"  # default: treat unclassified as feature copy

    return max(scores, key=scores.get)


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


# ─── PULL RSA ASSETS ─────────────────────────────────────────────────────────

def pull_rsa_assets(ga_service, customer_id):
    """Pull RSA asset performance via the ad_group_ad_asset_view."""
    rows = run_query(ga_service, customer_id, """
        SELECT
            campaign.name,
            ad_group.name,
            ad_group_ad_asset_view.asset_field_type,
            ad_group_ad_asset_view.performance_label,
            ad_group_ad_asset_view.enabled,
            asset.text_asset.text,
            metrics.clicks,
            metrics.impressions,
            metrics.conversions
        FROM ad_group_ad_asset_view
        WHERE ad_group_ad_asset_view.enabled = TRUE
          AND ad_group.status = ENABLED
          AND campaign.status = ENABLED
          AND segments.date DURING LAST_30_DAYS
          AND ad_group_ad_asset_view.asset_field_type IN (HEADLINE, DESCRIPTION)
    """)

    assets = []
    for row in rows:
        text   = row.asset.text_asset.text if row.asset.text_asset.text else ""
        if not text:
            continue
        assets.append({
            "campaign":    row.campaign.name,
            "ad_group":    row.ad_group.name,
            "type":        row.ad_group_ad_asset_view.asset_field_type.name,
            "performance": row.ad_group_ad_asset_view.performance_label.name,
            "text":        text,
            "clicks":      row.metrics.clicks,
            "imps":        row.metrics.impressions,
            "conv":        row.metrics.conversions,
        })

    return assets


# ─── ANGLE ANALYSIS ──────────────────────────────────────────────────────────

def analyse_by_angle(assets):
    """Aggregate performance by angle type."""
    by_angle = defaultdict(lambda: {
        "clicks": 0, "imps": 0, "conv": 0.0, "count": 0,
        "best": [], "worst": [], "examples": []
    })

    for a in assets:
        angle = classify_angle(a["text"])
        d     = by_angle[angle]
        d["clicks"] += a["clicks"]
        d["imps"]   += a["imps"]
        d["conv"]   += a["conv"]
        d["count"]  += 1
        d["examples"].append(a["text"])

        if a["performance"] == "BEST":
            d["best"].append(a["text"])
        elif a["performance"] == "LOW":
            d["worst"].append(a["text"])

    for angle, d in by_angle.items():
        d["ctr"] = d["clicks"] / d["imps"] if d["imps"] > 0 else 0.0
        d["cvr"] = d["conv"]   / d["clicks"] if d["clicks"] > 0 else 0.0

    return by_angle


def find_underutilised(by_angle, all_angles):
    """Find angle types with no representation or below-average performance."""
    all_types = set(all_angles)
    used_types = set(by_angle.keys())
    missing = all_types - used_types

    if by_angle:
        avg_ctr = sum(d["ctr"] for d in by_angle.values()) / len(by_angle)
        avg_cvr = sum(d["cvr"] for d in by_angle.values()) / len(by_angle)
        weak = [angle for angle, d in by_angle.items()
                if d["ctr"] < avg_ctr * 0.7 and d["count"] < 3]
    else:
        avg_ctr = avg_cvr = 0
        weak = []

    return missing, weak, avg_ctr, avg_cvr


# ─── CLAUDE GENERATION ───────────────────────────────────────────────────────

def generate_headlines_claude(angle, examples, client_name, business_type="business"):
    """Use Claude API to generate 5 headlines for a specific angle type."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return ["(Set ANTHROPIC_API_KEY to enable headline generation)"]

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        angle_descriptions = {
            "PRICE_OFFER":  "price or offer-focused (value, discounts, free offers, pricing)",
            "SOCIAL_PROOF": "social proof (reviews, ratings, trust signals, customer counts)",
            "URGENCY":      "urgency (limited time, act now, deadline-driven)",
            "FEATURE":      "feature-focused (what the product/service does or includes)",
            "OUTCOME":      "outcome-focused (what the customer achieves or feels)",
            "CTA":          "call-to-action (direct action language)",
        }

        existing = "\n".join(f"- {e}" for e in examples[:5]) if examples else "None yet"
        desc     = angle_descriptions.get(angle, angle.lower())

        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": (
                    f"Generate 5 Google Ads RSA headlines for a {client_name} account. "
                    f"These should be {desc} headlines.\n\n"
                    f"Existing headlines of this type:\n{existing}\n\n"
                    f"Requirements:\n"
                    f"- Maximum 30 characters each\n"
                    f"- No punctuation at the end\n"
                    f"- Unique angles, don't repeat existing headlines\n"
                    f"- No em dashes\n"
                    f"- Return ONLY the 5 headlines, one per line"
                )
            }]
        )
        return [line.strip(" -•") for line in message.content[0].text.strip().split("\n") if line.strip()][:5]

    except Exception as e:
        return [f"(Generation error: {e})"]


# ─── PRINT REPORT ─────────────────────────────────────────────────────────────

def print_report(customer_id, client_name, assets, by_angle, generate):
    ALL_ANGLE_TYPES = list(ANGLE_PATTERNS.keys()) + ["FEATURE"]
    run_date = __import__("datetime").date.today().strftime("%Y-%m-%d")

    missing, weak, avg_ctr, avg_cvr = find_underutilised(by_angle, ALL_ANGLE_TYPES)

    print(f"\nCREATIVE ANGLE ANALYZER — {client_name} ({customer_id})")
    print(f"Total RSA assets analysed: {len(assets)}  |  Run date: {run_date}")
    print("=" * 70)

    print(f"\nANGLE PERFORMANCE BREAKDOWN")
    print(f"  {'Angle':<16} {'Count':>6} {'CTR':>7} {'CVR':>7} {'Best':>5} {'Low':>5}  vs Avg CTR")
    print(f"  {'-'*16} {'-'*6} {'-'*7} {'-'*7} {'-'*5} {'-'*5}  {'-'*12}")

    for angle in ALL_ANGLE_TYPES:
        if angle not in by_angle:
            print(f"  {angle:<16} {'0':>6} {'n/a':>7} {'n/a':>7} {'0':>5} {'0':>5}  MISSING")
            continue
        d   = by_angle[angle]
        rel = ((d["ctr"] / avg_ctr) - 1) * 100 if avg_ctr > 0 else 0
        print(f"  {angle:<16} {d['count']:>6} {d['ctr']*100:>6.2f}% {d['cvr']*100:>6.2f}% "
              f"{len(d['best']):>5} {len(d['worst']):>5}  "
              f"{'▲' if rel >= 0 else '▼'}{abs(rel):.0f}%")

    # Priority angles for new creative
    target_angles = list(missing) + weak
    if not target_angles:
        print(f"\n  All angle types are represented. Account has good angle diversity.")

    else:
        print(f"\nUNDERUTILISED ANGLES — Create headlines for these:")
        for angle in target_angles[:3]:
            print(f"\n  [{angle}]")
            if angle in by_angle:
                print(f"  Current examples: {by_angle[angle]['examples'][:2]}")
                print(f"  CTR: {by_angle[angle]['ctr']*100:.2f}% vs avg {avg_ctr*100:.2f}%")
            else:
                print(f"  Status: Not used at all in this account")

            if generate:
                examples = by_angle.get(angle, {}).get("examples", [])
                print(f"\n  Generated headline ideas ({angle}):")
                headlines = generate_headlines_claude(angle, examples, client_name)
                for h in headlines:
                    print(f"    - {h}")

    print("\n" + "=" * 70)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Creative angle analyzer — RSA angle performance + headline generation"
    )
    parser.add_argument("--customer-id",  required=True, help="Account ID")
    parser.add_argument("--client-name",  help="Display name (optional)")
    parser.add_argument("--no-generate",  action="store_true",
                        help="Skip Claude headline generation")
    args = parser.parse_args()

    cid = args.customer_id.replace("-", "")
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

    print(f"\nAnalysing RSA creative angles for {client_name} ...")
    assets   = pull_rsa_assets(ga_service, cid)
    print(f"  {len(assets)} RSA asset records retrieved")

    if not assets:
        print("  No RSA asset data found. Ensure account has active RSAs with impressions.")
        return

    by_angle = analyse_by_angle(assets)
    print_report(cid, client_name, assets, by_angle, generate=not args.no_generate)


if __name__ == "__main__":
    main()
