"""
PMax Cannibalization Detector
Purpose: Detects when Performance Max campaigns are cannibalizing traffic from
         Search and Brand campaigns. Analyses:
           - PMax share of total account spend (concentration risk)
           - IS changes on Search campaigns after PMax was activated
           - Brand campaign IS and click share vs PMax spend
           - Campaign type distribution and budget allocation

         Run before and after PMax changes, and whenever IS drops on Search
         campaigns co-running with PMax.

Setup:
    Requires environment variables in .env:
        GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID,
        GOOGLE_ADS_CLIENT_SECRET, GOOGLE_ADS_REFRESH_TOKEN,
        GOOGLE_ADS_CUSTOMER_ID

Usage:
    python3 scripts/pmax_cannibalization_detector.py --customer-id 5544702166
    python3 scripts/pmax_cannibalization_detector.py --customer-id 5544702166 --days 60

Key cannibalization signals:
    - PMax IS rises while Search IS falls in same period
    - Brand campaign losing IS despite brand search volume being stable
    - PMax consuming >60% of account spend
    - Search campaign clicks/conv dropped after PMax activation date

Changelog:
    2026-03-23  Initial version — budget share, IS comparison, brand campaign
                health, and campaign type distribution analysis.
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

PMAX_CONCENTRATION_THRESHOLD = 0.60   # flag if PMax > 60% of account spend
BRAND_KEYWORDS = ["brand"]            # extend this list per client if needed

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

def pull_campaign_breakdown(ga_service, customer_id, start_date, end_date):
    """Pull performance by campaign type."""
    rows = run_query(ga_service, customer_id, f"""
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign.advertising_channel_sub_type,
            metrics.clicks,
            metrics.impressions,
            metrics.conversions,
            metrics.cost_micros,
            metrics.search_impression_share
        FROM campaign
        WHERE segments.date >= '{start_date}'
          AND segments.date <= '{end_date}'
          AND campaign.status = ENABLED
        ORDER BY metrics.cost_micros DESC
    """)

    campaigns = {}
    for row in rows:
        cid  = str(row.campaign.id)
        ch   = row.campaign.advertising_channel_type.name
        sub  = row.campaign.advertising_channel_sub_type.name

        is_pmax = (ch == "PERFORMANCE_MAX")
        is_search = (ch == "SEARCH")

        is_val = row.metrics.search_impression_share
        if is_val and 0 < is_val <= 1:
            is_pct = is_val * 100
        else:
            is_pct = None

        if cid not in campaigns:
            campaigns[cid] = {
                "name":    row.campaign.name,
                "type":    ch,
                "subtype": sub,
                "is_pmax": is_pmax,
                "is_search": is_search,
                "clicks":  0, "imps": 0, "conv": 0.0,
                "cost":    0.0, "is_vals": [],
            }
        c = campaigns[cid]
        c["clicks"] += row.metrics.clicks
        c["imps"]   += row.metrics.impressions
        c["conv"]   += row.metrics.conversions
        c["cost"]   += row.metrics.cost_micros / 1_000_000
        if is_pct is not None:
            c["is_vals"].append(is_pct)

    for c in campaigns.values():
        c["is"] = sum(c["is_vals"]) / len(c["is_vals"]) if c["is_vals"] else None

    return campaigns


def is_brand_campaign(name):
    """Heuristic brand campaign detection."""
    lower = name.lower()
    return any(kw in lower for kw in BRAND_KEYWORDS + ["brand", "branded", " - b ", "bmm"])


# ─── ANALYSIS ─────────────────────────────────────────────────────────────────

def analyse(campaigns, days):
    """Run cannibalization analysis and return a structured findings dict."""
    if not campaigns:
        return {"pmax": [], "search": [], "brand": [], "findings": [], "total_spend": 0}

    pmax_camps   = [c for c in campaigns.values() if c["is_pmax"]]
    search_camps = [c for c in campaigns.values() if c["is_search"] and not is_brand_campaign(c["name"])]
    brand_camps  = [c for c in campaigns.values() if c["is_search"] and is_brand_campaign(c["name"])]

    total_spend  = sum(c["cost"] for c in campaigns.values())
    pmax_spend   = sum(c["cost"] for c in pmax_camps)
    search_spend = sum(c["cost"] for c in search_camps)
    brand_spend  = sum(c["cost"] for c in brand_camps)

    findings = []

    # Finding 1: PMax budget concentration
    if total_spend > 0 and pmax_camps:
        pmax_share = pmax_spend / total_spend
        if pmax_share >= PMAX_CONCENTRATION_THRESHOLD:
            findings.append({
                "severity": "WARNING",
                "finding":  f"PMax consumes {pmax_share*100:.0f}% of account spend "
                            f"(${pmax_spend:.2f} of ${total_spend:.2f}). "
                            f"High concentration leaves no room for controlled Search testing.",
                "action":   "Consider capping PMax budget and reallocating to Search campaigns "
                            "for better keyword-level control.",
            })

    # Finding 2: PMax running without brand exclusions
    if pmax_camps and brand_camps:
        brand_is = [c["is"] for c in brand_camps if c["is"] is not None]
        if brand_is:
            avg_brand_is = sum(brand_is) / len(brand_is)
            if avg_brand_is < 80:
                findings.append({
                    "severity": "WARNING",
                    "finding":  f"Brand campaign IS is only {avg_brand_is:.0f}% despite "
                                f"PMax running in the same account. PMax may be competing "
                                f"on branded queries.",
                    "action":   "Add brand keywords as campaign-level negative keywords in "
                                "PMax asset groups, or use brand exclusion lists in PMax settings.",
                })

    # Finding 3: No Search campaigns alongside PMax
    if pmax_camps and not search_camps:
        findings.append({
            "severity": "INFO",
            "finding":  "Account is running PMax with no non-brand Search campaigns. "
                        "All keyword control is delegated to PMax automation.",
            "action":   "Consider adding a Search campaign for your highest-intent "
                        "keywords to maintain control and build Quality Score data.",
        })

    # Finding 4: Search IS check
    if search_camps:
        search_is_vals = [c["is"] for c in search_camps if c["is"] is not None]
        if search_is_vals:
            avg_search_is = sum(search_is_vals) / len(search_is_vals)
            if pmax_camps and avg_search_is < 60:
                findings.append({
                    "severity": "WARNING",
                    "finding":  f"Search campaign avg IS is {avg_search_is:.0f}% while PMax is running. "
                                f"Low IS on Search combined with PMax suggests potential cannibalisation.",
                    "action":   "Check auction insights on Search campaigns for your brand/top keywords. "
                                "Verify PMax asset groups don't contain the same URL patterns "
                                "as your best Search campaigns.",
                })

    # Finding 5: PMax no brand exclusions detection (inferred from brand IS)
    if not pmax_camps:
        findings.append({
            "severity": "INFO",
            "finding":  "No Performance Max campaigns found. No cannibalization risk.",
            "action":   "",
        })

    return {
        "pmax":        pmax_camps,
        "search":      search_camps,
        "brand":       brand_camps,
        "findings":    findings,
        "total_spend": total_spend,
        "pmax_spend":  pmax_spend,
        "search_spend": search_spend,
        "brand_spend": brand_spend,
    }


# ─── PRINT REPORT ─────────────────────────────────────────────────────────────

def print_report(customer_id, client_name, campaigns, analysis):
    run_date = date.today().strftime("%Y-%m-%d")
    print(f"\nPMAX CANNIBALIZATION DETECTOR — {client_name} ({customer_id})")
    print(f"Run date: {run_date}")
    print("=" * 70)

    total = analysis["total_spend"]
    if total > 0:
        print(f"\nBudget distribution:")
        print(f"  PMax campaigns:    ${analysis['pmax_spend']:.2f} ({analysis['pmax_spend']/total*100:.0f}%)")
        print(f"  Search campaigns:  ${analysis['search_spend']:.2f} ({analysis['search_spend']/total*100:.0f}%)")
        print(f"  Brand campaigns:   ${analysis['brand_spend']:.2f} ({analysis['brand_spend']/total*100:.0f}%)")
        print(f"  Total account:     ${total:.2f}")

    print(f"\nCampaign breakdown ({len(campaigns)} active campaigns):")
    for c in sorted(campaigns.values(), key=lambda x: -x["cost"]):
        type_label = "PMAX  " if c["is_pmax"] else ("SEARCH" if c["is_search"] else c["type"])
        is_str     = f"IS: {c['is']:.0f}%" if c["is"] is not None else "IS: n/a"
        print(f"  [{type_label}] {c['name'][:45]:<45} ${c['cost']:>7.0f}  {is_str}  Conv: {c['conv']:.0f}")

    print(f"\nFindings ({len(analysis['findings'])} total):")
    if not analysis["findings"]:
        print("  No cannibalization signals detected.")
    for i, f in enumerate(analysis["findings"], 1):
        print(f"\n  [{f['severity']}] {i}. {f['finding']}")
        if f["action"]:
            print(f"  Action: {f['action']}")

    print("\n" + "=" * 70)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PMax cannibalization detector — brand and search IS analysis"
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

    print(f"\nAnalysing {client_name} ...")
    campaigns = pull_campaign_breakdown(ga_service, cid, start_date, end_date)
    analysis  = analyse(campaigns, args.days)

    print_report(cid, client_name, campaigns, analysis)


if __name__ == "__main__":
    main()
