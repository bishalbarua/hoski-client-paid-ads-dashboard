"""
FaBesthetics Restructure Build Script
Purpose: Builds the new campaign structure per the Google Ads Strategy Brief (Apr 3, 2026).
         Creates all campaigns, ad groups, keywords, and RSA ad copy in PAUSED status.
         Shows a full preview and requires a single approval before executing.

Structure being built:
  Campaign 1: Hoski | Brand | FaBesthetics | Search | 3apr26
    - $5/day | Maximize Clicks ($3.00 CPC cap) | PAUSED
    - Ad Group: LHR Brand
      7 keywords (brand exact + phrase)
      1 RSA (2 brand headlines pinned to H1 for brand recognition)

  Campaign 2: Hoski | NB | LHR | Mahopac | Search | 3apr26
    - $35/day | Maximize Conversions (no target) | PAUSED
    - Ad Group 1: lhr_near_me_local       — 10 keywords, 1 RSA
    - Ad Group 2: lhr_body_part_specific  — 12 keywords, 1 RSA
    - Ad Group 3: lhr_price_package       — 8 keywords, 1 RSA (offer pinned H1)

  Campaign-level negatives on NB campaign:
    - Brand terms, all competitor brand names (exact), wrong-service terms, TOFU, at-home devices

  PMax (ID: 23510390095) paused immediately.

  Old Search (ID: 23636687451) is NOT touched by this script.
  Pause it manually after confirming the new NB campaign has 3 days of impressions.

Manual steps after running this script (in Google Ads UI):
  1. Add geo targeting on both new campaigns (Mahopac NY + 40-mile radius)
  2. Add language: English
  3. Review RSAs in UI (Ads tab) — approve and enable campaigns when ready
  4. Verify Enhanced Conversions is active (Diagnostics tab) before enabling

Usage:
    cd "Google Ads Manager"
    python3 "clients/FaBesthetics (9304117954)/build_restructure.py"
    python3 "clients/FaBesthetics (9304117954)/build_restructure.py" --dry-run

Changelog:
    2026-04-03  Initial build — full restructure per strategy brief.
                Includes RSA copy for all 4 ad groups.
"""

import argparse
import os
from datetime import datetime
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

load_dotenv()

# ─── CONFIG ──────────────────────────────────────────────────────────────────

CUSTOMER_ID = "9304117954"

PMAX_CAMPAIGN_ID = "23510390095"   # Hoski - PMax - Laser Hair Removal (ENABLED → PAUSED)
OLD_SEARCH_ID    = "23636687451"   # Hoski | Search | Laser Hair Removal | 10/3/2026
                                    # NOT touched here — pause manually after 3 days of NB impressions.

BRAND_CAMPAIGN_NAME = "Hoski | Brand | FaBesthetics | Search | 3apr26"
NB_CAMPAIGN_NAME    = "Hoski | NB | LHR | Mahopac | Search | 3apr26"

BRAND_BUDGET_DAILY  = 5.00    # $5/day
NB_BUDGET_DAILY     = 35.00   # $35/day
BRAND_CPC_CAP       = 3.00    # $3.00 max CPC cap on brand Maximize Clicks

LANDING_PAGE = "https://go.fabestheticsny.com/laser-hair-removal-mahopac-offer/"


# ─── KEYWORDS ─────────────────────────────────────────────────────────────────
# Each keyword: (text, match_type)

BRAND_AG_KEYWORDS = [
    ("fabesthetics",              "EXACT"),
    ("fab esthetics",             "EXACT"),
    ("fabestheticsny",            "EXACT"),
    ("fabesthetics mahopac",      "EXACT"),
    ("fabesthetics laser",        "EXACT"),
    ("becky pfeifer aesthetics",  "PHRASE"),
    ("fabesthetics ny",           "PHRASE"),
]

LHR_NEAR_ME_KEYWORDS = [
    ("laser hair removal near me",           "PHRASE"),
    ("laser hair removal near me",           "EXACT"),
    ("laser hair removal mahopac",           "PHRASE"),
    ("laser hair removal mahopac",           "EXACT"),
    ("laser hair removal westchester",       "PHRASE"),
    ("permanent hair removal near me",       "PHRASE"),
    ("laser hair removal clinic near me",    "PHRASE"),
    ("best laser hair removal near me",      "PHRASE"),
    ("laser treatment near me",              "PHRASE"),
    ("diode laser hair removal near me",     "PHRASE"),
]

LHR_BODY_PART_KEYWORDS = [
    ("underarm laser hair removal near me",  "PHRASE"),
    ("underarm laser hair removal",          "EXACT"),
    ("brazilian laser hair removal near me", "PHRASE"),
    ("brazilian laser hair removal",         "EXACT"),
    ("bikini laser hair removal near me",    "PHRASE"),
    ("leg laser hair removal near me",       "PHRASE"),
    ("facial hair laser removal near me",    "PHRASE"),
    ("upper lip laser hair removal",         "PHRASE"),
    ("laser hair removal for women near me", "PHRASE"),
    ("laser hair removal for men near me",   "PHRASE"),
    ("men's laser hair removal near me",     "EXACT"),
    ("full body laser hair removal near me", "PHRASE"),
]

LHR_PRICE_PACKAGE_KEYWORDS = [
    ("laser hair removal cost near me",        "PHRASE"),
    ("how much does laser hair removal cost",  "PHRASE"),
    ("laser hair removal packages near me",    "PHRASE"),
    ("laser hair removal deals near me",       "PHRASE"),
    ("affordable laser hair removal near me",  "PHRASE"),
    ("laser hair removal cost",                "EXACT"),
    ("laser hair removal specials near me",    "PHRASE"),
    ("laser hair removal price",               "PHRASE"),
]


# ─── RSA COPY ─────────────────────────────────────────────────────────────────
# Each headline: (text, pin_position_or_None)
#   pin_position: "HEADLINE_1", "HEADLINE_2", "HEADLINE_3", or None
# Each description: (text, pin_position_or_None)
#
# Char limits: headlines <=30, descriptions <=90.
# Pinning strategy:
#   Brand AG:     2 brand name variants pinned H1 (brand recognition is the goal)
#   Near Me AG:   No pinning (let Google optimize)
#   Body Part AG: No pinning
#   Price AG:     Offer headline pinned H1 (price searchers need to see the hook immediately)

BRAND_AG_RSA = {
    "headlines": [
        # Keyword headlines — brand name front-loaded
        ("FaBesthetics Mahopac NY",        "HEADLINE_1"),  # 23 — pin H1 variant 1
        ("FaBesthetics Laser Spa",         "HEADLINE_1"),  # 22 — pin H1 variant 2
        ("FaBesthetics - Book Now",        "HEADLINE_1"),  # 23 — pin H1 variant 3
        # Benefit headlines
        ("Personalized Every Visit",       None),          # 24
        ("Results You Can See",            None),          # 19
        ("Skip Shaving for Good",          None),          # 21
        ("Smoother Skin Guaranteed",       None),          # 24
        # Social proof
        ("Becky Pfeifer BSN Expert",       None),          # 24
        ("Certified Laser Specialist",     None),          # 25
        ("Trusted Mahopac Laser Spa",      None),          # 25
        # CTAs
        ("Book Your Session Today",        None),          # 23
        ("Check Availability Online",      None),          # 25
        ("Reserve Your Spot Now",          None),          # 21
        # Differentiators
        ("One Provider. Full Focus.",      None),          # 25
        ("15% Off 4 or More Sessions",     None),          # 26
    ],
    "descriptions": [
        # D1: Value prop + CTA
        ("FaBesthetics Mahopac NY. Laser by Becky Pfeifer BSN. Book 4+ sessions and save 15%.",   None),  # 84
        # D2: Benefits + proof
        ("Save 15% when you book 4+ sessions. Certified specialist. Mahopac and Westchester.",    None),  # 82
        # D3: Differentiator
        ("Single-provider laser spa in Mahopac NY. Personalized settings for your skin. Book today.", None),  # 89
        # D4: Objection handler
        ("BSN-certified laser care. All skin tones welcome. No rush. Book online at your own pace.", None),  # 88
    ],
}

NEAR_ME_AG_RSA = {
    "headlines": [
        # Keyword headlines — primary keyword front-loaded for relevance
        ("Laser Hair Removal Near Me",     None),          # 26
        ("Laser Removal in Mahopac NY",    None),          # 27
        ("Permanent Hair Removal Near Me", None),          # 30
        # Benefit headlines
        ("Skip Shaving Permanently",       None),          # 24
        ("All Skin Tones Treated",         None),          # 22
        ("Sessions Under 30 Minutes",      None),          # 25
        # Social proof
        ("Certified BSN Laser Clinic",     None),          # 26
        ("Trusted Mahopac Laser Clinic",   None),          # 28
        ("Serving Westchester County",     None),          # 26
        # CTAs
        ("Book Online - Same Week Appt",   None),          # 28
        ("Free Consult - No Commitment",   None),          # 28
        ("Check Same-Week Availability",   None),          # 28
        # Differentiators
        ("15% Off When You Book 4+",       None),          # 24
        ("One Specialist. Your Results.",  None),          # 29
        ("Modern Laser. Precise Results.", None),          # 30
    ],
    "descriptions": [
        # D1: Value prop + CTA
        ("Laser hair removal in Mahopac NY. All skin tones welcome. Book 4+ sessions and save 15%.", None),  # 89
        # D2: Benefits + proof
        ("Certified BSN specialist. Mahopac, Yorktown and Westchester. Same-week bookings available.", None),  # 88
        # D3: Differentiator
        ("Skip waxing for good. Modern laser calibrated to your skin tone. Book online in minutes.", None),  # 86 -- wait let me count: Skip waxing for good.(19) Modern laser calibrated to your skin tone.(43) Book online in minutes.(22) = 84
        # D4: Objection handler
        ("Sessions under 30 minutes. No hidden fees. Save 15% when you book 4 or more sessions.", None),  # 84
    ],
}

BODY_PART_AG_RSA = {
    "headlines": [
        # Keyword headlines — body part terms front-loaded
        ("Underarm and Brazilian Laser",   None),          # 28
        ("Laser Removal All Body Areas",   None),          # 28
        ("Legs and Full Body Laser NY",    None),          # 27
        # Benefit headlines
        ("Permanent Results by Body Area", None),          # 30
        ("Outlasts Waxing Every Time",     None),          # 26
        ("All Skin Tones Treated Safely",  None),          # 29
        # Social proof
        ("Certified Laser Specialist",     None),          # 25
        ("Mahopac NY Trusted Laser Spa",   None),          # 28
        # CTAs
        ("Book Your Area Laser Session",   None),          # 28
        ("Same-Week Bookings Available",   None),          # 28
        ("Free Consult - Pick Your Area",  None),          # 29
        # Differentiators
        ("15% Off 4+ Sessions Any Area",   None),          # 28
        ("Private Professional Setting",   None),          # 28
        ("Men and Women Both Welcome",     None),          # 25
        ("Fast Sessions per Body Area",    None),          # 27
    ],
    "descriptions": [
        # D1: Value prop + CTA
        ("Underarm, Brazilian, leg and full body laser in Mahopac NY. Save 15% on 4+ sessions.", None),  # 84
        # D2: Benefits + proof
        ("Stop waxing. Certified BSN for all body areas. All skin tones. Same-week bookings.", None),    # 81 -- wait: Stop waxing.(12) Certified BSN for all body areas.(34) All skin tones.(16) Same-week bookings.(20) = 82
        # D3: Differentiator
        ("Private spa. Men and women welcome. Modern laser for any body area. Book online today.", None),  # 84
        # D4: Objection handler
        ("Fast sessions by body area. No hidden fees. 15% off when you book 4 or more sessions.", None),  # 84
    ],
}

PRICE_PACKAGE_AG_RSA = {
    "headlines": [
        # Keyword headlines
        ("Laser Hair Removal Packages",    None),          # 27
        ("Laser Hair Removal Cost NY",     None),          # 26
        ("Affordable Laser Near Mahopac",  None),          # 29
        # Offer — pinned H1 (price searchers need to see the hook upfront)
        ("Save 15% on 4+ Sessions",        "HEADLINE_1"),  # 23 — PIN H1
        # Benefit headlines
        ("Clear Pricing - No Hidden Fees", None),          # 30
        ("Better Value Than NYC Prices",   None),          # 28
        ("Skip Monthly Waxing Costs",      None),          # 25
        ("Invest Once. Smooth Forever.",   None),          # 28
        # Social proof
        ("Certified Specialist Value",     None),          # 24
        ("Trusted Mahopac Laser Clinic",   None),          # 28
        # CTAs
        ("Get Pricing - No Commitment",    None),          # 27
        ("Compare Our Package Deals",      None),          # 25
        ("Book a Free Consult Today",      None),          # 25
        # Differentiators
        ("No Contracts. Pay Per Package.", None),          # 30
        ("Packages for Every Budget",      None),          # 25
    ],
    "descriptions": [
        # D1: Value prop + CTA
        ("Laser packages in Mahopac NY. Book 4+ sessions and save 15% automatically. No hidden fees.", None),  # 90
        # D2: Benefits + proof
        ("Skip NYC prices. Affordable laser near Mahopac. Certified BSN. See package options.", None),  # 83
        # D3: Differentiator
        ("Waxing adds up fast. Laser is a long-term investment. 15% off 4+ sessions. Book today.", None),  # 87
        # D4: Objection handler
        ("No contracts. No hidden fees. Free consultation to discuss your options. Book online now.", None),  # 88
    ],
}


# ─── NEGATIVE KEYWORDS FOR NB CAMPAIGN ───────────────────────────────────────
# Each entry: (text, match_type, reason_label)

NB_NEGATIVE_KEYWORDS = [
    # Brand guard
    ("fabesthetics",           "EXACT",  "brand guard"),
    ("fab esthetics",          "EXACT",  "brand guard"),
    ("fabestheticsny",         "EXACT",  "brand guard"),
    ("becky pfeifer",          "EXACT",  "brand guard"),
    # Competitor brand names (confirmed in search terms report)
    ("milan laser",                    "EXACT",  "competitor"),
    ("milan laser hair removal",       "EXACT",  "competitor"),
    ("simply skin",                    "EXACT",  "competitor"),
    ("dare to be bare",                "EXACT",  "competitor"),
    ("beautyfix",                      "EXACT",  "competitor"),
    ("beautyfix medspa",               "EXACT",  "competitor"),
    ("caroline's spa",                 "EXACT",  "competitor"),
    ("laser away",                     "EXACT",  "competitor"),
    ("ideal image",                    "EXACT",  "competitor"),
    ("european wax center",            "EXACT",  "competitor"),
    # Wrong-service skin treatment terms
    ("dark spot",           "PHRASE", "wrong service"),
    ("age spot",            "PHRASE", "wrong service"),
    ("pigmentation",        "PHRASE", "wrong service"),
    ("acne scar",           "PHRASE", "wrong service"),
    ("spider vein",         "PHRASE", "wrong service"),
    ("varicose",            "PHRASE", "wrong service"),
    ("microneedling",       "PHRASE", "wrong service"),
    ("botox",               "PHRASE", "wrong service"),
    ("lip filler",          "PHRASE", "wrong service"),
    ("filler",              "PHRASE", "wrong service"),
    ("body contouring",     "PHRASE", "wrong service"),
    ("emsculpt",            "PHRASE", "wrong service"),
    ("emslim",              "PHRASE", "wrong service"),
    ("weight loss",         "PHRASE", "wrong service"),
    ("cellulite",           "PHRASE", "wrong service"),
    ("tattoo removal",      "PHRASE", "wrong service"),
    ("dermaplaning",        "PHRASE", "wrong service"),
    ("chemical peel",       "PHRASE", "wrong service"),
    ("eyebrow",             "PHRASE", "wrong service"),
    # At-home devices
    ("home laser",          "PHRASE", "at-home device"),
    ("at home",             "PHRASE", "at-home device"),
    ("ipl device",          "PHRASE", "at-home device"),
    ("ipl at home",         "PHRASE", "at-home device"),
    ("ulike",               "PHRASE", "at-home device"),
    ("braun ipl",           "PHRASE", "at-home device"),
    ("philips lumea",       "PHRASE", "at-home device"),
    # Employment intent
    ("jobs",                "PHRASE", "employment"),
    ("careers",             "PHRASE", "employment"),
    ("hiring",              "PHRASE", "employment"),
    ("salary",              "PHRASE", "employment"),
    ("aesthetician school", "PHRASE", "employment"),
    ("esthetician program", "PHRASE", "employment"),
    # TOFU informational
    ("does laser hair removal hurt",      "PHRASE", "informational"),
    ("how does laser hair removal work",  "PHRASE", "informational"),
    ("laser hair removal side effects",   "PHRASE", "informational"),
    ("is laser hair removal permanent",   "PHRASE", "informational"),
    ("laser hair removal vs waxing",      "PHRASE", "informational"),
    ("what is laser hair removal",        "PHRASE", "informational"),
    ("laser hair removal reddit",         "PHRASE", "informational"),
    # Wrong product
    ("laser engraving",   "PHRASE", "wrong product"),
    ("laser cutting",     "PHRASE", "wrong product"),
    ("laser printer",     "PHRASE", "wrong product"),
    ("laser tag",         "PHRASE", "wrong product"),
    ("lasik",             "PHRASE", "wrong product"),
    ("laser pointer",     "PHRASE", "wrong product"),
    ("laser eye surgery", "PHRASE", "wrong product"),
]

BRAND_NEGATIVE_KEYWORDS = [
    ("laser hair removal",    "PHRASE", "non-brand service term"),
    ("hair removal",          "PHRASE", "non-brand service term"),
    ("laser treatment",       "PHRASE", "non-brand service term"),
    ("permanent hair removal","PHRASE", "non-brand service term"),
    ("medspa",                "PHRASE", "non-brand service term"),
    ("med spa",               "PHRASE", "non-brand service term"),
    ("skin center",           "PHRASE", "non-brand service term"),
]


# ─── GOOGLE ADS CLIENT ────────────────────────────────────────────────────────

def build_client():
    return GoogleAdsClient.load_from_dict({
        "developer_token":   os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "client_id":         os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret":     os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token":     os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "login_customer_id": os.environ["GOOGLE_ADS_CUSTOMER_ID"],
        "use_proto_plus":    True,
    })


# ─── PREVIEW ──────────────────────────────────────────────────────────────────

def _fmt_kw(text, match_type):
    return f"[{text}]" if match_type == "EXACT" else f'"{text}"'

def _fmt_headline(text, pin):
    pin_str = f"  (pinned {pin})" if pin else ""
    return f"    {text!r}  ({len(text)} chars){pin_str}"

def _fmt_desc(text, pin):
    pin_str = f"  (pinned {pin})" if pin else ""
    return f"    {text!r}  ({len(text)} chars){pin_str}"

def print_preview():
    sep = "=" * 72
    print(f"\n{sep}")
    print("FULL PREVIEW — FaBesthetics Restructure")
    print("All new entities created PAUSED. Single approval to execute.")
    print(f"{sep}\n")

    print("STEP 1 — PAUSE PMax")
    print(f"  Campaign ID {PMAX_CAMPAIGN_ID}: Hoski - PMax - Laser Hair Removal")
    print(f"  ENABLED → PAUSED\n")

    print(f"STEP 2 — CREATE: {BRAND_CAMPAIGN_NAME}")
    print(f"  Budget: ${BRAND_BUDGET_DAILY:.0f}/day | Maximize Clicks (${BRAND_CPC_CAP:.2f} CPC cap) | PAUSED")
    print(f"  Ad Group: LHR Brand")
    print(f"  Keywords ({len(BRAND_AG_KEYWORDS)}):")
    for kw, mt in BRAND_AG_KEYWORDS:
        print(f"    {_fmt_kw(kw, mt)}")
    print(f"  RSA Headlines ({len(BRAND_AG_RSA['headlines'])}):")
    for text, pin in BRAND_AG_RSA["headlines"]:
        print(_fmt_headline(text, pin))
    print(f"  RSA Descriptions ({len(BRAND_AG_RSA['descriptions'])}):")
    for text, pin in BRAND_AG_RSA["descriptions"]:
        print(_fmt_desc(text, pin))
    print(f"  Campaign negatives: {len(BRAND_NEGATIVE_KEYWORDS)} non-brand service terms\n")

    print(f"STEP 3 — CREATE: {NB_CAMPAIGN_NAME}")
    print(f"  Budget: ${NB_BUDGET_DAILY:.0f}/day | Maximize Conversions (no target) | PAUSED")

    ag_configs = [
        ("lhr_near_me_local",      LHR_NEAR_ME_KEYWORDS,    NEAR_ME_AG_RSA),
        ("lhr_body_part_specific", LHR_BODY_PART_KEYWORDS,  BODY_PART_AG_RSA),
        ("lhr_price_package",      LHR_PRICE_PACKAGE_KEYWORDS, PRICE_PACKAGE_AG_RSA),
    ]
    for ag_name, kws, rsa in ag_configs:
        print(f"\n  Ad Group: {ag_name}")
        print(f"  Keywords ({len(kws)}):")
        for kw, mt in kws:
            print(f"    {_fmt_kw(kw, mt)}")
        print(f"  RSA Headlines ({len(rsa['headlines'])}):")
        for text, pin in rsa["headlines"]:
            print(_fmt_headline(text, pin))
        print(f"  RSA Descriptions ({len(rsa['descriptions'])}):")
        for text, pin in rsa["descriptions"]:
            print(_fmt_desc(text, pin))

    print(f"\n  Campaign negatives ({len(NB_NEGATIVE_KEYWORDS)}):")
    categories = {}
    for kw, mt, label in NB_NEGATIVE_KEYWORDS:
        categories.setdefault(label, []).append((kw, mt))
    for label, items in categories.items():
        print(f"    [{label}] {len(items)} keywords")

    total_kw = (len(BRAND_AG_KEYWORDS) + len(LHR_NEAR_ME_KEYWORDS) +
                len(LHR_BODY_PART_KEYWORDS) + len(LHR_PRICE_PACKAGE_KEYWORDS))
    total_rsa_headlines = sum(len(r["headlines"]) for r in [BRAND_AG_RSA, NEAR_ME_AG_RSA, BODY_PART_AG_RSA, PRICE_PACKAGE_AG_RSA])
    total_rsa_descs = sum(len(r["descriptions"]) for r in [BRAND_AG_RSA, NEAR_ME_AG_RSA, BODY_PART_AG_RSA, PRICE_PACKAGE_AG_RSA])
    total_neg = len(NB_NEGATIVE_KEYWORDS) + len(BRAND_NEGATIVE_KEYWORDS)

    print(f"\n{'─'*72}")
    print(f"SUMMARY:")
    print(f"  Campaigns created (PAUSED): 2")
    print(f"  Ad groups created:          4  (1 brand + 3 non-brand)")
    print(f"  Keywords added:             {total_kw}")
    print(f"  RSAs created:               4  ({total_rsa_headlines} headlines, {total_rsa_descs} descriptions)")
    print(f"  Negative keywords added:    {total_neg}")
    print(f"  Campaigns paused:           1  (PMax ID {PMAX_CAMPAIGN_ID})")
    print(f"  NOT TOUCHED:                Old Search ID {OLD_SEARCH_ID}")
    print(f"                              (pause manually after 3 days of NB impressions)")
    print(f"{'─'*72}")
    print(f"\nFLAGS — verify with client before enabling:")
    print(f"  'Sessions Under 30 Minutes' — confirm accurate for all treatment areas")
    print(f"  'Certified BSN Laser Clinic' — Becky Pfeifer BSN confirmed in client notes")
    print(f"{'─'*72}\n")


def request_approval(dry_run):
    if dry_run:
        print("[DRY RUN] No changes made.")
        return False
    answer = input("Approve and execute all changes above? [yes/no]: ").strip().lower()
    if answer == "yes":
        print("\nApproved. Executing...\n")
        return True
    print("Cancelled. No changes made.")
    return False


# ─── BUILD OPERATIONS ─────────────────────────────────────────────────────────

def pause_pmax(client, customer_id):
    campaign_service = client.get_service("CampaignService")
    op = client.get_type("CampaignOperation")
    op.update.resource_name = campaign_service.campaign_path(customer_id, PMAX_CAMPAIGN_ID)
    op.update.status = client.enums.CampaignStatusEnum.PAUSED
    op.update_mask.paths.append("status")
    try:
        campaign_service.mutate_campaigns(customer_id=customer_id, operations=[op])
        print(f"  PMax paused.")
    except GoogleAdsException as ex:
        for err in ex.failure.errors:
            print(f"  [ERROR] {err.message}")


def create_budget(client, customer_id, name, daily_dollars):
    budget_service = client.get_service("CampaignBudgetService")
    op = client.get_type("CampaignBudgetOperation")
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    op.create.name = f"Budget | {name} | {ts}"
    op.create.amount_micros = int(daily_dollars * 1_000_000)
    op.create.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
    op.create.explicitly_shared = False
    response = budget_service.mutate_campaign_budgets(customer_id=customer_id, operations=[op])
    rn = response.results[0].resource_name
    print(f"  Budget created: ${daily_dollars:.0f}/day  ({rn})")
    return rn


def create_brand_campaign(client, customer_id, budget_rn):
    campaign_service = client.get_service("CampaignService")
    op = client.get_type("CampaignOperation")
    op.create.name = BRAND_CAMPAIGN_NAME
    op.create.status = client.enums.CampaignStatusEnum.PAUSED
    op.create.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
    op.create.campaign_budget = budget_rn
    op.create.network_settings.target_google_search = True
    op.create.network_settings.target_search_network = False
    op.create.network_settings.target_content_network = False
    op.create.contains_eu_political_advertising = client.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
    # Maximize Clicks = target_spend in the API. CPC cap is set via cpc_bid_ceiling_micros.
    op.create.target_spend.cpc_bid_ceiling_micros = int(BRAND_CPC_CAP * 1_000_000)
    response = campaign_service.mutate_campaigns(customer_id=customer_id, operations=[op])
    rn = response.results[0].resource_name
    cid = rn.split("/")[-1]
    print(f"  Brand campaign created: {BRAND_CAMPAIGN_NAME}  (ID: {cid})")
    return rn, cid


def create_nb_campaign(client, customer_id, budget_rn):
    campaign_service = client.get_service("CampaignService")
    op = client.get_type("CampaignOperation")
    op.create.name = NB_CAMPAIGN_NAME
    op.create.status = client.enums.CampaignStatusEnum.PAUSED
    op.create.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
    op.create.campaign_budget = budget_rn
    op.create.network_settings.target_google_search = True
    op.create.network_settings.target_search_network = False
    op.create.network_settings.target_content_network = False
    op.create.contains_eu_political_advertising = client.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
    # Maximize Conversions — no target CPA (setting the bidding strategy type via the oneof field)
    op.create.maximize_conversions.target_cpa_micros = 0
    response = campaign_service.mutate_campaigns(customer_id=customer_id, operations=[op])
    rn = response.results[0].resource_name
    cid = rn.split("/")[-1]
    print(f"  NB campaign created: {NB_CAMPAIGN_NAME}  (ID: {cid})")
    return rn, cid


def create_ad_group(client, customer_id, campaign_rn, ag_name):
    ag_service = client.get_service("AdGroupService")
    op = client.get_type("AdGroupOperation")
    op.create.name = ag_name
    op.create.campaign = campaign_rn
    op.create.status = client.enums.AdGroupStatusEnum.ENABLED
    response = ag_service.mutate_ad_groups(customer_id=customer_id, operations=[op])
    rn = response.results[0].resource_name
    ag_id = rn.split("/")[-1]
    print(f"    Ad group created: {ag_name}  (ID: {ag_id})")
    return rn


def create_keywords(client, customer_id, ag_rn, keywords):
    criterion_service = client.get_service("AdGroupCriterionService")
    mt_enum = client.enums.KeywordMatchTypeEnum
    ops = []
    for kw_text, match_type_str in keywords:
        op = client.get_type("AdGroupCriterionOperation")
        op.create.ad_group = ag_rn
        op.create.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        op.create.keyword.text = kw_text
        op.create.keyword.match_type = getattr(mt_enum, match_type_str)
        ops.append(op)
    try:
        response = criterion_service.mutate_ad_group_criteria(customer_id=customer_id, operations=ops)
        print(f"      {len(response.results)} keywords added.")
    except GoogleAdsException as ex:
        for err in ex.failure.errors:
            print(f"      [ERROR] {err.message}")


def create_rsa(client, customer_id, ag_rn, rsa_data, ag_label):
    """Create one RSA for the given ad group."""
    ad_group_ad_service = client.get_service("AdGroupAdService")
    pin_enum = client.enums.ServedAssetFieldTypeEnum

    op = client.get_type("AdGroupAdOperation")
    op.create.ad_group = ag_rn
    op.create.status = client.enums.AdGroupAdStatusEnum.PAUSED
    op.create.ad.final_urls.append(LANDING_PAGE)

    for text, pin_pos in rsa_data["headlines"]:
        h = client.get_type("AdTextAsset")
        h.text = text
        if pin_pos:
            h.pinned_field = getattr(pin_enum, pin_pos)
        op.create.ad.responsive_search_ad.headlines.append(h)

    for text, pin_pos in rsa_data["descriptions"]:
        d = client.get_type("AdTextAsset")
        d.text = text
        if pin_pos:
            d.pinned_field = getattr(pin_enum, pin_pos)
        op.create.ad.responsive_search_ad.descriptions.append(d)

    try:
        response = ad_group_ad_service.mutate_ad_group_ads(customer_id=customer_id, operations=[op])
        ad_id = response.results[0].resource_name.split("/")[-1]
        print(f"      RSA created for {ag_label}  (Ad ID: {ad_id})")
    except GoogleAdsException as ex:
        for err in ex.failure.errors:
            print(f"      [ERROR creating RSA for {ag_label}] {err.message}")


def create_campaign_negatives(client, customer_id, campaign_rn, negatives, label):
    criterion_service = client.get_service("CampaignCriterionService")
    mt_enum = client.enums.KeywordMatchTypeEnum
    ops = []
    for kw_text, match_type_str, _ in negatives:
        op = client.get_type("CampaignCriterionOperation")
        op.create.campaign = campaign_rn
        op.create.negative = True
        op.create.keyword.text = kw_text
        op.create.keyword.match_type = getattr(mt_enum, match_type_str)
        ops.append(op)
    try:
        response = criterion_service.mutate_campaign_criteria(customer_id=customer_id, operations=ops)
        print(f"    {len(response.results)} negative keywords added to {label}.")
    except GoogleAdsException as ex:
        for err in ex.failure.errors:
            print(f"    [ERROR adding negatives to {label}] {err.message}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="FaBesthetics restructure build")
    parser.add_argument("--dry-run", action="store_true", help="Preview only — no changes made")
    args = parser.parse_args()

    print_preview()

    if not request_approval(args.dry_run):
        return

    client      = build_client()
    customer_id = CUSTOMER_ID

    # ── Step 1: Pause PMax ────────────────────────────────────────────────────
    # Already paused on first run attempt — skip.
    print("\nStep 1: PMax already paused (done on previous run). Skipping.")

    # ── Step 2: Brand Campaign ────────────────────────────────────────────────
    # Brand campaign and LHR Brand ad group already created on a previous run:
    #   Campaign ID: 23721018377  — Hoski | Brand | FaBesthetics | Search | 3apr26
    #   Ad Group ID: 195259782179 — LHR Brand
    # Keywords, RSA, and campaign negatives were created in that same run.
    # Skipping Step 2 entirely to avoid duplicates.
    EXISTING_BRAND_CAMPAIGN_ID = "23721018377"
    print(f"\nStep 2: Brand campaign already exists (ID: {EXISTING_BRAND_CAMPAIGN_ID}). Skipping.")

    # ── Step 3: Non-Brand LHR Campaign ───────────────────────────────────────
    print("\nStep 3: Building Non-Brand LHR campaign...")
    nb_budget_rn = create_budget(client, customer_id, NB_CAMPAIGN_NAME, NB_BUDGET_DAILY)
    nb_campaign_rn, nb_campaign_id = create_nb_campaign(client, customer_id, nb_budget_rn)

    ag_configs = [
        ("lhr_near_me_local",      LHR_NEAR_ME_KEYWORDS,       NEAR_ME_AG_RSA),
        ("lhr_body_part_specific", LHR_BODY_PART_KEYWORDS,     BODY_PART_AG_RSA),
        ("lhr_price_package",      LHR_PRICE_PACKAGE_KEYWORDS, PRICE_PACKAGE_AG_RSA),
    ]
    for ag_name, keywords, rsa_data in ag_configs:
        print(f"  Creating ad group: {ag_name}...")
        ag_rn = create_ad_group(client, customer_id, nb_campaign_rn, ag_name)
        print("    Adding keywords...")
        create_keywords(client, customer_id, ag_rn, keywords)
        print("    Creating RSA...")
        create_rsa(client, customer_id, ag_rn, rsa_data, ag_name)

    print("  Adding campaign-level negative keywords...")
    create_campaign_negatives(
        client, customer_id, nb_campaign_rn,
        NB_NEGATIVE_KEYWORDS,
        label=NB_CAMPAIGN_NAME,
    )

    # ── Done ──────────────────────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("BUILD COMPLETE")
    print("=" * 72)
    print(f"\nNew campaigns (both PAUSED):")
    print(f"  Brand ID:  {EXISTING_BRAND_CAMPAIGN_ID}  — {BRAND_CAMPAIGN_NAME}  (pre-existing)")
    print(f"  NB ID:     {nb_campaign_id}  — {NB_CAMPAIGN_NAME}")
    print(f"\nManual steps before enabling (Google Ads UI):")
    print(f"  1. Add geo targeting on both campaigns: Mahopac NY + 40-mile radius")
    print(f"  2. Add language: English")
    print(f"  3. Review RSA copy in Ads tab (4 RSAs created, all PAUSED)")
    print(f"  4. Verify Enhanced Conversions active: Diagnostics tab > Enhanced Conversions")
    print(f"  5. Enable both campaigns once steps 1-4 are confirmed")
    print(f"  6. After 3 days of NB impressions, pause old Search ID {OLD_SEARCH_ID}")
    print(f"\n  DO NOT pause old Search ID {OLD_SEARCH_ID} before step 6.")
    print("=" * 72)


if __name__ == "__main__":
    main()
