#!/usr/bin/env python3
"""
Create PMax Mother's Day 2026 campaign for Global Diamond Montreal (GDM)
Account: 7087867966 | MCC: 4781259815

What this script creates (campaign stays PAUSED):
  - Campaign budget + PMax campaign (Canada, EN+FR, $45/day)
  - 3 asset groups: Diamond Earrings / Diamond Pendants / Diamond Bracelets
  - All headlines (15/group) and descriptions (5/group)
  - Business name asset linked to all 3 groups
  - Sitelinks, callouts, structured snippet at campaign level
  - Listing group filters: custom_label_0=mothers-day-2026 INCLUDED, all else EXCLUDED
  - Search theme signals: 15 per asset group (45 total)
  - Geo targeting: Canada | Languages: English + French

Usage:
    python3 scripts/create_pmax_mothers_day_2026.py [--dry-run]
    --dry-run   Validate text limits and preview. No API calls made.

Manual steps AFTER this script:
    1. Upload images: 1 landscape (1200x628) + 1 square (1200x1200) per asset group
    2. Add YouTube video link per asset group (avoid Google auto-generate)
    3. Upload Customer Match audience list (export from Shopify)
    4. Add brand exclusions: Campaign Settings > Brand exclusions
       (global diamond montreal, doctor diamond, gdm jewelry, etc.)
    5. Add Mother's Day promotion extension via UI
    6. Confirm all 10 products approved in Merchant Center with custom_label_0=mothers-day-2026
    7. Verify collection page URLs exist in Shopify before enabling
"""

import os
import sys
import argparse

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.protobuf import json_format


# ─── ACCOUNT / CAMPAIGN CONFIG ────────────────────────────────────────────────

CUSTOMER_ID = "7087867966"
CAMPAIGN_NAME = "Hoski | PMax | Mother's Day 2026 | Feed Only"
DAILY_BUDGET_DOLLARS = 45.00
START_DATE = "20260416"
END_DATE = "20260511"
FEED_LABEL = "CA"
CUSTOM_LABEL_VALUE = "mothers-day-2026"
BUSINESS_NAME = "Global Diamond Montreal"

CANADA_GEO_TARGET = "geoTargetConstants/2124"
LANGUAGE_CONSTANTS = ["languageConstants/1000", "languageConstants/1002"]  # EN, FR


# ─── ASSET GROUP DATA ─────────────────────────────────────────────────────────

ASSET_GROUPS = [
    {
        "name": "Hoski | MD26 | Diamond Earrings",
        "final_url": "https://globaldiamondmontreal.com/collections/diamond-earrings",
        "headlines": [
            "Diamond Earrings for Mom",
            "Lab-Grown Diamond Studs",
            "Mother's Day Diamond Gift",
            "14K Gold Diamond Studs",
            "Diamond Stud Earrings Canada",
            "Free Shipping. 30-Day Returns.",
            "Manufacturer Price - No Markup",
            "Global Diamond Montreal",
            "Since 1982 - 40+ Years",
            "From $390 - Real Diamonds",
            "Diamond Earrings Gift for Her",
            "White Gold Diamond Studs",
            "VS Clarity, F Color, Certified",
            "Gift-Wrapped Free",
            "Mother's Day - Shop Now",
        ],
        "descriptions": [
            "Studs from $390 in 14k gold. Manufacturer pricing. Free shipping. Gift for Mom.",
            "Lab-grown or natural studs from $390. Gift-wrapped. Ships in 14 days. 30-day returns.",
            "Manufacturer since 1982. No retail markup. VS clarity, F color diamond studs.",
            "Diamond studs in white or yellow gold. 0.10ct to 0.26ct. Free gift packaging.",
            "Real diamonds at manufacturer pricing. Better quality, same budget. Ships to CA.",
        ],
        "search_themes": [
            "mothers day diamond earrings",
            "diamond stud earrings gift",
            "lab grown diamond studs canada",
            "mothers day earring gift ideas",
            "diamond earrings for mom",
            "14k gold stud earrings canada",
            "diamond stud earrings mothers day",
            "gift diamond earrings women",
            "earrings for mom mothers day",
            "white gold diamond stud earrings",
            "diamond earring gift canada",
            "mothers day jewellery earrings",
            "mothers day gift fine jewelry",
            "best jewelry gift for mom",
            "real diamond earrings canada",
        ],
    },
    {
        "name": "Hoski | MD26 | Diamond Pendants",
        "final_url": "https://globaldiamondmontreal.com/collections/pendants",
        "headlines": [
            "Diamond Necklace for Mom",
            "Heart Pendant Mothers Day Gift",
            "14K Gold Diamond Pendant",
            "Diamond Heart Necklace Canada",
            "Gold Necklace Gift for Her",
            "Chain Included - Ready to Gift",
            "Manufacturer Price - No Markup",
            "Diamond Pendant from $1,100",
            "Natural Diamond Pendants",
            "Free Shipping Across Canada",
            "Global Diamond Montreal",
            "Greek Key Diamond Pendant",
            "Since 1982 - Fine Jewelry",
            "Gift-Wrapped Free. Ships Fast.",
            "Mother's Day - Shop Pendants",
        ],
        "descriptions": [
            "Diamond heart pendants from $1,100. Chain included. Gift-wrapped free. Ships to Canada.",
            "Natural and lab-grown pendants in 10k/14k gold. Manufacturer pricing, no markup.",
            "Manufacturer since 1982. Heart, cross, and halo diamond pendants. Free Canadian shipping.",
            "Diamond pendant with chain included - ready to gift. From $1,100. Ships in 14 days.",
            "Heart, greek key, and halo pendants. White/yellow/rose gold. Direct from manufacturer.",
        ],
        "search_themes": [
            "mothers day diamond necklace",
            "heart pendant mothers day gift",
            "diamond heart necklace canada",
            "gold necklace gift for mom",
            "mothers day necklace pendant",
            "diamond pendant necklace gift",
            "necklace for mom mothers day",
            "heart necklace diamond gift",
            "mothers day jewellery necklace",
            "gold diamond necklace canada",
            "diamond pendant gift ideas",
            "personalized jewelry for mom",
            "fine jewelry necklace canada",
            "mothers day gift ideas jewelry",
            "necklace gift for her canada",
        ],
    },
    {
        "name": "Hoski | MD26 | Diamond Bracelets",
        "final_url": "https://globaldiamondmontreal.com/collections/diamond-bracelets",
        "headlines": [
            "Diamond Bracelet for Mom",
            "Tennis Bracelet - Mothers Day",
            "Diamond Tennis Bracelet Canada",
            "Gemstone Bracelet Gift for Her",
            "14K Gold Tennis Bracelet",
            "Manufacturer Price - No Markup",
            "Diamond Bracelets from $2,080",
            "Ruby + Diamond Gold Bracelet",
            "Sapphire + Diamond Bracelet",
            "Free Shipping. 30-Day Returns.",
            "Global Diamond Montreal",
            "Diamond Bracelet Since 1982",
            "Tennis Bracelet 1.90 CTW",
            "Gift-Wrapped. Ships to Canada.",
            "Mother's Day - Shop Bracelets",
        ],
        "descriptions": [
            "Diamond tennis and gemstone bracelets from $2,080. 14k gold. Free Canadian shipping.",
            "Diamond tennis in white gold. Gemstone bracelets in yellow gold. Manufacturer pricing.",
            "Manufacturer since 1982. 1.90ctw tennis bracelet. 9.7ct ruby bracelet. Ships to Canada.",
            "Diamond or gemstone bracelet from $2,080 in 14k gold. Free gift-wrapping included.",
            "Manufacturer-direct diamond and gemstone bracelets. No retail markup. White/yellow gold.",
        ],
        "search_themes": [
            "mothers day diamond bracelet",
            "tennis bracelet mothers day gift",
            "diamond tennis bracelet canada",
            "gemstone bracelet gift for mom",
            "mothers day bracelet gift",
            "ruby diamond bracelet gift",
            "gold bracelet mothers day",
            "mothers day bracelets montreal",
            "diamond bracelet for women canada",
            "fine jewelry bracelet gift",
            "tennis bracelet canada",
            "sapphire diamond bracelet gift",
            "mothers day luxury jewelry gift",
            "gemstone bracelet women",
            "bracelet gift for mom canada",
        ],
    },
]

SITELINKS = [
    {
        "link_text": "Diamond Earrings",
        "description1": "Lab-grown & natural diamond studs",
        "description2": "14k gold from $390",
        "final_url": "https://globaldiamondmontreal.com/collections/diamond-earrings",
    },
    {
        "link_text": "Diamond Necklaces",
        "description1": "Heart & halo diamond pendants",
        "description2": "Chain included. From $1,100.",
        "final_url": "https://globaldiamondmontreal.com/collections/pendants",
    },
    {
        "link_text": "Diamond Bracelets",
        "description1": "Tennis & gemstone bracelets",
        "description2": "14k gold from $2,080",
        "final_url": "https://globaldiamondmontreal.com/collections/diamond-bracelets",
    },
    {
        "link_text": "Free Diamond Studs Offer",
        "description1": "Free 0.26ct studs with $2,500+",
        "description2": "Free 0.50ct studs with $3,500+",
        "final_url": "https://globaldiamondmontreal.com/",
    },
    {
        "link_text": "Mothers Day Gifts",
        "description1": "Earrings, pendants, bracelets",
        "description2": "Gift-wrapped. Ships across Canada.",
        "final_url": "https://globaldiamondmontreal.com/collections",
    },
    {
        "link_text": "Book an Appointment",
        "description1": "Visit our Montreal showroom",
        "description2": "See the full collection in person",
        "final_url": "https://globaldiamondmontreal.com/pages/appointment-1",
    },
]

CALLOUTS = [
    "Free Canadian Shipping",
    "30-Day Returns Guaranteed",
    "Manufacturer Pricing",
    "Since 1982 - 40+ Years",
    "Lab-Grown Diamonds",
    "Free Gift Packaging",
    "Sourced from 12 Countries",
    "Ships in 14 Business Days",
]

STRUCTURED_SNIPPET = {
    "header": "Types",
    "values": [
        "Diamond Earrings",
        "Heart Pendants",
        "Tennis Bracelets",
        "Ruby Bracelets",
        "Lab-Grown Diamonds",
        "Gold Necklaces",
    ],
}


# ─── VALIDATION ───────────────────────────────────────────────────────────────

def validate_text_limits():
    errors = []
    for ag in ASSET_GROUPS:
        g = ag["name"]
        for i, h in enumerate(ag["headlines"], 1):
            if len(h) > 30:
                errors.append(f"[{g}] Headline {i} ({len(h)} chars > 30): '{h}'")
        for i, d in enumerate(ag["descriptions"], 1):
            if len(d) > 90:
                errors.append(f"[{g}] Description {i} ({len(d)} chars > 90): '{d}'")
    for sl in SITELINKS:
        if len(sl["link_text"]) > 25:
            errors.append(f"Sitelink link_text ({len(sl['link_text'])} > 25): '{sl['link_text']}'")
        if len(sl["description1"]) > 35:
            errors.append(f"Sitelink desc1 ({len(sl['description1'])} > 35): '{sl['description1']}'")
        if len(sl["description2"]) > 35:
            errors.append(f"Sitelink desc2 ({len(sl['description2'])} > 35): '{sl['description2']}'")
    for c in CALLOUTS:
        if len(c) > 25:
            errors.append(f"Callout ({len(c)} > 25): '{c}'")
    for v in STRUCTURED_SNIPPET["values"]:
        if len(v) > 25:
            errors.append(f"Snippet value ({len(v)} > 25): '{v}'")
    if errors:
        raise ValueError("Character limit violations:\n" + "\n".join(f"  - {e}" for e in errors))
    print("  All text lengths valid.")


# ─── CLIENT ───────────────────────────────────────────────────────────────────

def build_client():
    return GoogleAdsClient.load_from_dict({
        "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "login_customer_id": os.environ["GOOGLE_ADS_CUSTOMER_ID"],
        "use_proto_plus": True,
    })


# ─── MERCHANT CENTER LOOKUP ───────────────────────────────────────────────────

def get_merchant_center_id(client, customer_id):
    ga_service = client.get_service("GoogleAdsService")
    query = """
        SELECT campaign.shopping_setting.merchant_id
        FROM campaign
        WHERE campaign.advertising_channel_type IN ('PERFORMANCE_MAX', 'SHOPPING')
        AND campaign.status != 'REMOVED'
        LIMIT 10
    """
    try:
        rows = list(ga_service.search(customer_id=customer_id, query=query))
        seen = {}
        for row in rows:
            mc = row.campaign.shopping_setting.merchant_id
            if mc:
                seen[mc] = seen.get(mc, 0) + 1
        if seen:
            mc_id = max(seen, key=seen.get)
            print(f"  Found Merchant Center ID: {mc_id}")
            return int(mc_id)
        print("  WARNING: No linked Merchant Center found — shopping feed will not be filtered.")
        return None
    except GoogleAdsException as ex:
        print(f"  WARNING: Could not fetch Merchant Center: {ex}")
        return None


# ─── TEMP RESOURCE NAME HELPERS ───────────────────────────────────────────────
# Globally unique temp ID allocation (all negatives share one namespace per batch):
#   -1          : campaign_budget
#   -2          : campaign
#   -6,-7,-8    : asset_groups (1-based idx + 5)
#
# AssetGroupListingGroupFilter uses compound resource names: {ag_temp_id}~{filter_seq}
# The asset group part MUST be negative (temp); the filter sequence MUST be positive.
# Format: customers/{cid}/assetGroupListingGroupFilters/{ag_temp_id}~{filter_seq}
#   AG1: -6~1 / -6~2 / -6~3  (root/incl/excl)
#   AG2: -7~1 / -7~2 / -7~3
#   AG3: -8~1 / -8~2 / -8~3
#
# Note: campaign criteria do NOT use temp resource names (nothing references them)

def budget_rn(cid):
    return f"customers/{cid}/campaignBudgets/-1"

def campaign_rn(cid):
    return f"customers/{cid}/campaigns/-2"

def asset_group_rn(cid, idx):        # 1-based → -6,-7,-8
    return f"customers/{cid}/assetGroups/-{idx + 5}"

def listing_filter_rn(cid, ag_idx, local_idx):
    """Compound resource name for AssetGroupListingGroupFilter.
    ag_idx: 1-based (1=earrings, 2=pendants, 3=bracelets)
    local_idx: 1=root (SUBDIVISION), 2=incl (UNIT_INCLUDED), 3=excl (UNIT_EXCLUDED)
    Asset group part is negative temp ID; filter sequence is positive.
    """
    ag_temp_id = -(ag_idx + 5)   # -6, -7, -8
    return f"customers/{cid}/assetGroupListingGroupFilters/{ag_temp_id}~{local_idx}"


# ─── OPERATION BUILDERS ───────────────────────────────────────────────────────
# All builders use direct proto-plus field access (no CopyFrom) on MutateOperation
# nested objects. This is the correct pattern for use_proto_plus=True with the
# Google Ads Python client v19+.

def op_budget(client, cid):
    m = client.get_type("MutateOperation")
    b = m.campaign_budget_operation.create
    b.resource_name = budget_rn(cid)
    b.name = "Hoski | PMax | Mother's Day 2026 | Budget"
    b.amount_micros = int(DAILY_BUDGET_DOLLARS * 1_000_000)
    b.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
    b.explicitly_shared = False
    return m


def op_campaign(client, cid, merchant_center_id):
    m = client.get_type("MutateOperation")
    c = m.campaign_operation.create
    c.resource_name = campaign_rn(cid)
    c.name = CAMPAIGN_NAME
    c.status = client.enums.CampaignStatusEnum.PAUSED
    c.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.PERFORMANCE_MAX
    c.campaign_budget = budget_rn(cid)
    c.start_date_time = "2026-04-16 00:00:00"
    c.end_date_time = "2026-05-11 23:59:59"
    # proto3 optional bool: False (default 0) loses presence tracking with direct assignment.
    # ParseDict forces the presence bit even when the value is the proto3 default (False).
    json_format.ParseDict({"containsEuPoliticalAdvertising": False}, c._pb, ignore_unknown_fields=True)
    # Maximize Conversion Value, no tROAS for first 7 days of learning
    c.maximize_conversion_value.target_roas = 0
    if merchant_center_id:
        c.shopping_setting.merchant_id = merchant_center_id
        c.shopping_setting.feed_label = FEED_LABEL
    return m


def op_geo_criterion(client, cid):
    m = client.get_type("MutateOperation")
    cr = m.campaign_criterion_operation.create
    cr.campaign = campaign_rn(cid)
    cr.location.geo_target_constant = CANADA_GEO_TARGET
    return m


def op_language_criterion(client, cid, lang_constant):
    m = client.get_type("MutateOperation")
    cr = m.campaign_criterion_operation.create
    cr.campaign = campaign_rn(cid)
    cr.language.language_constant = lang_constant
    return m


def op_asset_group(client, cid, ag_idx, ag_data):
    m = client.get_type("MutateOperation")
    ag = m.asset_group_operation.create
    ag.resource_name = asset_group_rn(cid, ag_idx)
    ag.campaign = campaign_rn(cid)
    ag.name = ag_data["name"]
    ag.final_urls.append(ag_data["final_url"])
    ag.status = client.enums.AssetGroupStatusEnum.PAUSED
    return m


def ops_listing_group_filter(client, cid, ag_idx):
    """
    3 operations per asset group:
      root (SUBDIVISION)
        -> included (UNIT_INCLUDED, custom_label_0 = "mothers-day-2026")
        -> excluded (UNIT_EXCLUDED, catch-all)
    ag_idx: 1-based
    """
    root_rn = listing_filter_rn(cid, ag_idx, 1)
    incl_rn = listing_filter_rn(cid, ag_idx, 2)
    excl_rn = listing_filter_rn(cid, ag_idx, 3)
    ag_res = asset_group_rn(cid, ag_idx)

    m_root = client.get_type("MutateOperation")
    r = m_root.asset_group_listing_group_filter_operation.create
    r.resource_name = root_rn
    r.asset_group = ag_res
    r.type_ = client.enums.ListingGroupFilterTypeEnum.SUBDIVISION
    r.listing_source = client.enums.ListingGroupFilterListingSourceEnum.SHOPPING

    m_incl = client.get_type("MutateOperation")
    i = m_incl.asset_group_listing_group_filter_operation.create
    i.resource_name = incl_rn
    i.asset_group = ag_res
    i.type_ = client.enums.ListingGroupFilterTypeEnum.UNIT_INCLUDED
    i.listing_source = client.enums.ListingGroupFilterListingSourceEnum.SHOPPING
    i.parent_listing_group_filter = root_rn
    i.case_value.product_custom_attribute.index = (
        client.enums.ListingGroupFilterCustomAttributeIndexEnum.INDEX0
    )
    i.case_value.product_custom_attribute.value = CUSTOM_LABEL_VALUE

    m_excl = client.get_type("MutateOperation")
    e = m_excl.asset_group_listing_group_filter_operation.create
    e.resource_name = excl_rn
    e.asset_group = ag_res
    e.type_ = client.enums.ListingGroupFilterTypeEnum.UNIT_EXCLUDED
    e.listing_source = client.enums.ListingGroupFilterListingSourceEnum.SHOPPING
    e.parent_listing_group_filter = root_rn

    return [m_root, m_incl, m_excl]


def op_search_theme(client, cid, ag_idx, theme_text):
    m = client.get_type("MutateOperation")
    s = m.asset_group_signal_operation.create
    s.asset_group = asset_group_rn(cid, ag_idx)
    s.search_theme.text = theme_text
    return m


# ─── ASSEMBLE ALL OPERATIONS ──────────────────────────────────────────────────

def build_all_operations(client, cid, merchant_center_id):
    """Returns (ops_list, summary_lines). Shell only — no asset operations.
    Assets (text, images, video, sitelinks, callouts) must be added manually in the UI.
    """
    ops = []
    summary = []

    # Budget + Campaign
    ops.append(op_budget(client, cid))
    summary.append(f"CampaignBudget: ${DAILY_BUDGET_DOLLARS:.0f}/day (STANDARD delivery)")

    ops.append(op_campaign(client, cid, merchant_center_id))
    mc = f"MC:{merchant_center_id}" if merchant_center_id else "NO MC LINKED — add manually"
    summary.append(f"Campaign: '{CAMPAIGN_NAME}' | PAUSED | {START_DATE} to {END_DATE} | {mc}")

    # Geo + Language criteria
    ops.append(op_geo_criterion(client, cid))
    summary.append("Geo: Canada (geoTargetConstants/2124)")
    for lang in LANGUAGE_CONSTANTS:
        ops.append(op_language_criterion(client, cid, lang))
    summary.append("Languages: English (1000), French (1002)")

    # Asset groups (PAUSED, no assets — add in UI)
    for ag_idx, ag_data in enumerate(ASSET_GROUPS, 1):
        ops.append(op_asset_group(client, cid, ag_idx, ag_data))
        summary.append(f"AssetGroup {ag_idx}: '{ag_data['name']}' -> {ag_data['final_url']}")

    # Listing group filters (3 nodes per asset group = 9 total)
    for ag_idx in range(1, len(ASSET_GROUPS) + 1):
        ops.extend(ops_listing_group_filter(client, cid, ag_idx))
    summary.append(
        f"Listing group filters: custom_label_0={CUSTOM_LABEL_VALUE} INCLUDED, "
        f"all else EXCLUDED (3 nodes x 3 groups)"
    )

    # Search theme signals (15 per group = 45 total)
    for ag_idx, ag_data in enumerate(ASSET_GROUPS, 1):
        for theme in ag_data["search_themes"]:
            ops.append(op_search_theme(client, cid, ag_idx, theme))
        summary.append(
            f"AssetGroup {ag_idx} search themes: {len(ag_data['search_themes'])} signals"
        )

    return ops, summary


# ─── PREVIEW + APPROVAL ───────────────────────────────────────────────────────

def print_preview(summary_lines, total_ops):
    print()
    print("=" * 65)
    print("  PREVIEW: GDM PMax Mother's Day 2026")
    print(f"  Account: {CUSTOMER_ID}  |  Total operations: {total_ops}")
    print("=" * 65)
    for line in summary_lines:
        print(f"  + {line}")
    print()
    print("  Manual steps required after creation:")
    print("    - Upload images per asset group (landscape + square)")
    print("    - Add YouTube video link per asset group")
    print("    - Upload Customer Match audience")
    print("    - Add brand exclusions via Google Ads UI")
    print("    - Add Mother's Day promotion extension via UI")
    print("=" * 65)


def request_approval(dry_run):
    if dry_run:
        print("\n[DRY RUN] No changes made.")
        return False
    answer = input("\nCreate this campaign in Google Ads? [yes/no]: ").strip().lower()
    if answer == "yes":
        print("Approved. Executing...\n")
        return True
    print("Cancelled.")
    return False


# ─── EXECUTE ──────────────────────────────────────────────────────────────────

def execute_batch(client, customer_id, ops):
    ga_service = client.get_service("GoogleAdsService")
    try:
        response = ga_service.mutate(
            customer_id=customer_id,
            mutate_operations=ops,
        )
        created = len(response.mutate_operation_responses)
        print(f"  Batch complete. {created} resources created.")
        for r in response.mutate_operation_responses:
            if r.campaign_result.resource_name:
                print(f"  Campaign: {r.campaign_result.resource_name}")
                break
        return True
    except GoogleAdsException as ex:
        print(f"\nGoogle Ads API error:")
        for err in ex.failure.errors:
            print(f"  [{err.error_code}] {err.message}")
            if err.location:
                for fv in err.location.field_path_elements:
                    print(f"    at field: {fv.field_name} (index {fv.index})")
        return False


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Create PMax Mother's Day 2026 campaign for GDM (7087867966)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Validate and preview without any API calls"
    )
    args = parser.parse_args()

    print("\nGDM PMax Mother's Day 2026 — Campaign Builder")
    print("-" * 46)

    # Step 1: validate text
    print("\n[1/4] Validating text asset character limits...")
    try:
        validate_text_limits()
    except ValueError as e:
        print(f"\nValidation failed:\n{e}")
        sys.exit(1)

    # Step 2: build client
    print("\n[2/4] Building Google Ads client...")
    try:
        client = build_client()
        print("  Client ready.")
    except KeyError as e:
        print(f"  Missing env var: {e}")
        sys.exit(1)

    # Step 3: merchant center (skip for dry run)
    if args.dry_run:
        merchant_center_id = None
        print("\n[3/4] Skipping Merchant Center lookup (dry run).")
    else:
        print("\n[3/4] Looking up linked Merchant Center...")
        merchant_center_id = get_merchant_center_id(client, CUSTOMER_ID)

    # Step 4: build operations
    print("\n[4/4] Building batch operations...")
    ops, summary = build_all_operations(client, CUSTOMER_ID, merchant_center_id)
    print(f"  {len(ops)} operations assembled.")

    print_preview(summary, len(ops))

    if not request_approval(args.dry_run):
        return

    print("Submitting batch to Google Ads API...")
    success = execute_batch(client, CUSTOMER_ID, ops)
    if success:
        print("\nDone. Campaign created PAUSED.")
        print("Complete the manual steps above, then enable when ready.")
    else:
        print("\nCreation failed — see errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
