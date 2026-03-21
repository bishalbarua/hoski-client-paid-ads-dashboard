"""
Ad Copy Performance Report
Purpose: Analyse RSA (Responsive Search Ad) asset performance across all client accounts.
         Surfaces asset-level BEST/LOW/LEARNING labels, ad strength ratings,
         pinning issues, and specific copy to swap out.

Signals surfaced per ad:
  1. Ad Strength       — POOR / AVERAGE / GOOD / EXCELLENT (Google's overall rating)
  2. LOW assets        — specific headlines/descriptions being under-served (swap these)
  3. BEST assets       — top-performing copy (protect, don't delete)
  4. Pinning warnings  — over-pinned ads reduce Google's rotation flexibility
  5. Ad metrics        — impressions, CTR, conversions, spend, CPA per ad

Setup:
    Requires environment variables:
        GOOGLE_ADS_DEVELOPER_TOKEN, GOOGLE_ADS_CLIENT_ID, GOOGLE_ADS_CLIENT_SECRET,
        GOOGLE_ADS_REFRESH_TOKEN, GOOGLE_ADS_CUSTOMER_ID

Usage:
    python3 scripts/ad_copy_performance.py                            # all clients, 30d
    python3 scripts/ad_copy_performance.py --customer-id 5544702166  # single client
    python3 scripts/ad_copy_performance.py --days 7                  # 7-day window
    python3 scripts/ad_copy_performance.py --min-impr 500            # only ads ≥500 impressions
    python3 scripts/ad_copy_performance.py --show-all                # include GOOD-rated assets

Note on asset labels:
    Performance labels (BEST/GOOD/LOW/LEARNING) are a rolling aggregate assigned by Google
    and cannot be filtered by date. Ad-level metrics (impressions, cost, etc.) use the
    specified --days lookback window.

Changelog:
    2026-03-19  Initial version — ad strength, asset labels, pinning audit, per-ad metrics.
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

DEFAULT_MIN_IMPR     = 100   # skip ads below this impression count (too little data for labels)
MAX_PINNED_HEADLINES = 2     # flag as over-pinned if more than this many headlines are pinned

# ─── ICON MAPS ───────────────────────────────────────────────────────────────

AD_STRENGTH_ICON = {
    "EXCELLENT":   "🟢",
    "GOOD":        "🟡",
    "AVERAGE":     "🟠",
    "POOR":        "🔴",
    "PENDING":     "⏳",
    "NO_ADS":      "❌",
    "UNSPECIFIED": "—",
    "UNKNOWN":     "—",
}

PERF_LABEL_ICON = {
    "BEST":        "🟢 BEST",
    "GOOD":        "🔵 GOOD",
    "LOW":         "🔴 LOW",
    "LEARNING":    "⏳ LEARNING",
    "UNSPECIFIED": "—",
    "UNKNOWN":     "—",
}

# ─── SETUP ───────────────────────────────────────────────────────────────────

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
            print(f"    [API Error] {error.message}")
        return []


# ─── PULL AD METRICS ─────────────────────────────────────────────────────────

def pull_ad_metrics(ga_service, customer_id, days):
    """Pull impressions, clicks, cost, conversions per RSA for the date window."""
    date_range = f"LAST_{days}_DAYS" if days in (7, 14, 30) else "LAST_30_DAYS"

    rows = run_query(ga_service, customer_id, f"""
        SELECT
            campaign.name,
            campaign.status,
            ad_group.name,
            ad_group_ad.ad.id,
            ad_group_ad.ad_strength,
            ad_group_ad.status,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.ctr
        FROM ad_group_ad
        WHERE ad_group_ad.ad.type = RESPONSIVE_SEARCH_AD
          AND ad_group_ad.status = ENABLED
          AND campaign.status = ENABLED
          AND segments.date DURING {date_range}
        ORDER BY metrics.impressions DESC
    """)

    ads = {}
    for row in rows:
        ad_id = str(row.ad_group_ad.ad.id)
        if ad_id not in ads:
            ads[ad_id] = {
                "ad_id":       ad_id,
                "campaign":    row.campaign.name,
                "ad_group":    row.ad_group.name,
                "ad_strength": row.ad_group_ad.ad_strength.name,
                "impressions": 0,
                "clicks":      0,
                "cost":        0.0,
                "conversions": 0.0,
            }
        ads[ad_id]["impressions"] += row.metrics.impressions
        ads[ad_id]["clicks"]      += row.metrics.clicks
        ads[ad_id]["cost"]        += row.metrics.cost_micros / 1_000_000
        ads[ad_id]["conversions"] += row.metrics.conversions

    # Recompute CTR from aggregated totals
    for ad in ads.values():
        ad["ctr"] = ad["clicks"] / ad["impressions"] if ad["impressions"] > 0 else 0.0

    return ads


# ─── PULL ASSET PERFORMANCE LABELS ───────────────────────────────────────────

def pull_asset_labels(ga_service, customer_id):
    """Pull per-asset performance labels (BEST/GOOD/LOW/LEARNING) and pinning status.

    Asset labels are a rolling aggregate — they cannot be date-segmented.
    A label only appears after Google has served the asset enough times to assign one.
    """
    rows = run_query(ga_service, customer_id, """
        SELECT
            ad_group_ad.ad.id,
            ad_group_ad_asset_view.field_type,
            ad_group_ad_asset_view.performance_label,
            ad_group_ad_asset_view.pinned_field,
            asset.text_asset.text
        FROM ad_group_ad_asset_view
        WHERE ad_group_ad.status = ENABLED
          AND campaign.status = ENABLED
          AND ad_group_ad_asset_view.enabled = TRUE
    """)

    # assets[ad_id] = list of {field_type, label, pinned, text}
    assets = defaultdict(list)
    for row in rows:
        ad_id  = str(row.ad_group_ad.ad.id)
        view   = row.ad_group_ad_asset_view
        text   = row.asset.text_asset.text if row.asset.text_asset.text else "(no text)"
        pinned = view.pinned_field.name if view.pinned_field else None

        assets[ad_id].append({
            "field_type": view.field_type.name,       # HEADLINE or DESCRIPTION
            "label":      view.performance_label.name, # BEST, GOOD, LOW, LEARNING
            "pinned":     pinned,
            "text":       text,
        })

    return assets


# ─── ANALYSE ─────────────────────────────────────────────────────────────────

def analyse_ad(ad, asset_list, min_impr, show_all):
    """Returns an analysis dict, or None if the ad is below the impression threshold."""
    if ad["impressions"] < min_impr:
        return None

    headlines    = [a for a in asset_list if a["field_type"] == "HEADLINE"]
    descriptions = [a for a in asset_list if a["field_type"] == "DESCRIPTION"]
    pinned_count = sum(1 for h in headlines if h["pinned"] and h["pinned"] != "UNSPECIFIED")

    low_assets  = [a for a in asset_list if a["label"] == "LOW"]
    best_assets = [a for a in asset_list if a["label"] == "BEST"]
    good_assets = [a for a in asset_list if a["label"] == "GOOD"]
    learning    = [a for a in asset_list if a["label"] == "LEARNING"]

    warnings = []
    if ad["ad_strength"] in ("POOR", "AVERAGE"):
        warnings.append(f"Ad Strength is {ad['ad_strength']} — add more unique, keyword-rich headlines")
    if pinned_count > MAX_PINNED_HEADLINES:
        warnings.append(f"{pinned_count} headlines pinned to fixed positions — reduces rotation variety")
    if len(headlines) < 10:
        warnings.append(f"Only {len(headlines)} headline(s) — Google recommends 10–15 for full coverage")
    if len(descriptions) < 3:
        warnings.append(f"Only {len(descriptions)} description(s) — Google recommends 4")
    if low_assets:
        warnings.append(f"{len(low_assets)} LOW-rated asset(s) — replace these with stronger copy")

    return {
        "ad":          ad,
        "headlines":   headlines,
        "descriptions": descriptions,
        "low_assets":  low_assets,
        "best_assets": best_assets,
        "good_assets": good_assets,
        "learning":    learning,
        "pinned_count": pinned_count,
        "warnings":    warnings,
        "show_all":    show_all,
    }


# ─── PRINT ───────────────────────────────────────────────────────────────────

def print_asset_group(label_filter, asset_list, field_type):
    """Print assets matching label_filter for a given field type."""
    items = [a for a in asset_list if a["label"] == label_filter and a["field_type"] == field_type]
    if not items:
        return
    type_label = "Headlines" if field_type == "HEADLINE" else "Descriptions"
    print(f"                 {type_label}:")
    for a in items:
        pin_tag = f"  [pinned: {a['pinned']}]" if a["pinned"] and a["pinned"] != "UNSPECIFIED" else ""
        print(f"                   \"{a['text']}\"{pin_tag}")


def print_ad(result):
    ad   = result["ad"]
    impr = ad["impressions"]
    ctr  = f"{ad['ctr']*100:.2f}%"
    conv = ad["conversions"]
    cost = ad["cost"]
    cpc  = f"${cost / ad['clicks']:.2f}" if ad["clicks"] > 0 else "—"
    cpa  = f"${cost / conv:.2f}"         if conv > 0         else "—"

    strength_icon = AD_STRENGTH_ICON.get(ad["ad_strength"], "—")
    low           = result["low_assets"]
    best          = result["best_assets"]
    good          = result["good_assets"]
    learn         = result["learning"]

    # Row-level icon: worst condition wins
    if low or ad["ad_strength"] in ("POOR", "AVERAGE"):
        row_icon = "⚠️ "
    elif best:
        row_icon = "✅"
    else:
        row_icon = "➡️ "

    h_count = len(result["headlines"])
    d_count = len(result["descriptions"])

    print(f"\n      {row_icon}  [{ad['campaign']}] › [{ad['ad_group']}]")
    print(f"           Strength: {strength_icon} {ad['ad_strength']}  |  "
          f"Impr: {impr:,}  |  CTR: {ctr}  |  Conv: {conv:.0f}  |  CPA: {cpa}  |  "
          f"Spend: ${cost:.2f}  |  CPC: {cpc}")
    print(f"           {h_count} headlines  |  {d_count} descriptions  |  "
          f"{result['pinned_count']} pinned  |  "
          f"🟢 BEST: {len(best)}  |  🔴 LOW: {len(low)}  |  ⏳ LEARNING: {len(learn)}")

    if low:
        print(f"\n           🔴 LOW — replace these:")
        print_asset_group("LOW", result["headlines"],    "HEADLINE")
        print_asset_group("LOW", result["descriptions"], "DESCRIPTION")

    if best:
        print(f"\n           🟢 BEST — protect these:")
        print_asset_group("BEST", result["headlines"],    "HEADLINE")
        print_asset_group("BEST", result["descriptions"], "DESCRIPTION")

    if result["show_all"] and good:
        print(f"\n           🔵 GOOD:")
        print_asset_group("GOOD", result["headlines"],    "HEADLINE")
        print_asset_group("GOOD", result["descriptions"], "DESCRIPTION")

    if learn:
        print(f"\n           ⏳ LEARNING — needs more data:")
        print_asset_group("LEARNING", result["headlines"],    "HEADLINE")
        print_asset_group("LEARNING", result["descriptions"], "DESCRIPTION")

    if result["warnings"]:
        print()
        for warn in result["warnings"]:
            print(f"           ⚠️   {warn}")


def print_account(client_name, customer_id, ads, assets, min_impr, show_all):
    if not ads:
        print(f"\n⬜  {client_name} ({customer_id}) — No RSA data in this period")
        return {"total": 0, "low_ads": 0, "poor_strength": 0, "total_low": 0, "total_best": 0}

    results = []
    for ad_id, ad in ads.items():
        asset_list = assets.get(ad_id, [])
        result = analyse_ad(ad, asset_list, min_impr, show_all)
        if result:
            results.append(result)

    if not results:
        skipped = len(ads)
        print(f"\n⬜  {client_name} ({customer_id}) — {skipped} RSA(s) below {min_impr} impression threshold")
        return {"total": 0, "low_ads": 0, "poor_strength": 0, "total_low": 0, "total_best": 0}

    # Sort: ads with LOW assets first, then by spend
    results.sort(key=lambda r: (-len(r["low_assets"]), -r["ad"]["cost"]))

    total_low    = sum(len(r["low_assets"])  for r in results)
    total_best   = sum(len(r["best_assets"]) for r in results)
    poor_count   = sum(1 for r in results if r["ad"]["ad_strength"] in ("POOR", "AVERAGE"))
    low_ad_count = sum(1 for r in results if r["low_assets"])

    if low_ad_count > 0 or poor_count > 0:
        acct_icon = "⚠️ "
    elif total_best > 0:
        acct_icon = "✅"
    else:
        acct_icon = "➡️ "

    total_impr = sum(r["ad"]["impressions"] for r in results)
    total_conv = sum(r["ad"]["conversions"] for r in results)
    total_cost = sum(r["ad"]["cost"]        for r in results)

    print(f"\n{acct_icon}  {client_name} ({customer_id})")
    print(f"    {len(results)} RSA(s)  |  "
          f"Impr: {total_impr:,}  |  "
          f"Spend: ${total_cost:.2f}  |  "
          f"Conv: {total_conv:.0f}  |  "
          f"🔴 LOW assets: {total_low}  |  "
          f"🟠 Weak strength: {poor_count}  |  "
          f"🟢 BEST assets: {total_best}")

    for result in results:
        print_ad(result)

    return {
        "total":         len(results),
        "low_ads":       low_ad_count,
        "poor_strength": poor_count,
        "total_low":     total_low,
        "total_best":    total_best,
    }


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="RSA ad copy performance — asset labels, ad strength, pinning audit"
    )
    parser.add_argument("--customer-id", help="Single account ID (omit to run all clients)")
    parser.add_argument("--client-name", help="Display name when using --customer-id")
    parser.add_argument("--days",        type=int,   default=30, choices=[7, 14, 30],
                        help="Lookback window for ad metrics (default: 30)")
    parser.add_argument("--min-impr",    type=int,   default=DEFAULT_MIN_IMPR,
                        help=f"Min impressions to include an ad (default: {DEFAULT_MIN_IMPR})")
    parser.add_argument("--show-all",    action="store_true",
                        help="Also show GOOD-rated assets (default: BEST and LOW only)")
    args = parser.parse_args()

    client     = build_client()
    ga_service = client.get_service("GoogleAdsService")

    if args.customer_id:
        targets = {(args.client_name or args.customer_id): args.customer_id.replace("-", "")}
    else:
        targets = ALL_CLIENTS

    print("\n" + "="*60)
    print("AD COPY PERFORMANCE REPORT")
    print(f"Ad metrics: last {args.days} days  |  Min impressions: {args.min_impr}")
    print("Asset labels: rolling aggregate (not date-filtered)")
    print("🟢 BEST = protect  |  🔴 LOW = swap out  |  ⏳ LEARNING = wait")
    print("="*60)

    totals: dict[str, int] = {
        "total": 0, "low_ads": 0, "poor_strength": 0, "total_low": 0, "total_best": 0
    }
    errored: list[str] = []

    for name, cid in targets.items():
        try:
            ads    = pull_ad_metrics(ga_service, cid, args.days)
            assets = pull_asset_labels(ga_service, cid)
            result = print_account(name, cid, ads, assets, args.min_impr, args.show_all)
            for k in totals:
                totals[k] += result[k]
        except Exception as e:
            errored.append(name)
            print(f"\n❌  {name} ({cid}) — Error: {e}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"  Accounts checked:          {len(targets) - len(errored)}/{len(targets)}")
    print(f"  RSAs analyzed:             {totals['total']}")
    print(f"  🔴 Ads with LOW assets:    {totals['low_ads']}  ({totals['total_low']} LOW assets to replace)")
    print(f"  🟠 Weak ad strength:       {totals['poor_strength']} ads rated POOR/AVERAGE")
    print(f"  🟢 BEST assets found:      {totals['total_best']}")
    if errored:
        print(f"  ❌ Errored:               {', '.join(errored)}")
    if totals["total_low"] == 0 and totals["poor_strength"] == 0:
        print("\n  ✅ No major ad copy issues found.")
    print("="*60)


if __name__ == "__main__":
    main()
