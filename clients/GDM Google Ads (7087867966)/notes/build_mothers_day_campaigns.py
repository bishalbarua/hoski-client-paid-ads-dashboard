"""
GDM — Mother's Day 2026 Campaign Builder
Creates both search campaigns in Google Ads account 7087867966.

Everything created PAUSED. To launch: enable campaigns in dashboard or via ads_writer.py.

What this builds:
  Campaign 1: GDM | Search | Mother's Day EN (2026) — $50/day, Apr 10 - May 11
    AG1: Mother's Day Bracelet Core         (6 keywords, 1 RSA)
    AG2: Mother's Day Jewelry Gift          (7 keywords, 1 RSA)
    AG3: Personalized + Custom [PRIORITY 1] (10 keywords, 1 RSA)
    AG4: Tennis + Diamond Bracelet          (7 keywords, 1 RSA)

  Campaign 2: GDM | Search | Mother's Day FR (2026) — $35/day, Apr 10 - May 11
    AG5: Fête des mères [PRIORITY 1]        (10 keywords, 1 RSA)
    AG6: Bracelet Diamant + Or FR           (8 keywords, 1 RSA)

  Per campaign: brand + category negative keywords, geo (Canada), language targeting
  Per ad group: cross-negative keywords
  Both campaigns: 6 sitelinks + 10 callouts

Run:
  cd [project root]
  python3 "clients/GDM Google Ads (7087867966)/notes/build_mothers_day_campaigns.py"
  python3 "clients/GDM Google Ads (7087867966)/notes/build_mothers_day_campaigns.py" --dry-run

Output log: clients/GDM Google Ads (7087867966)/notes/mothers_day_build_log.json
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

CUSTOMER_ID = "7087867966"
LP_URL = "https://globaldiamondmontreal.com/collections/mothers-day-bracelet-collection"
LOG_PATH = Path(__file__).parent / "mothers_day_build_log.json"

# Canada geo target constant ID
GEO_CANADA = 2124
# Language constants: 1000 = English, 1002 = French
LANG_EN = 1000
LANG_FR = 1002


# ─── CAMPAIGN DATA ────────────────────────────────────────────────────────────

SITELINKS = [
    {
        "link_text": "Mother's Day Collection",
        "description1": "10% off diamonds for Mom",
        "description2": "Free studs with $2,500+",
        "final_url": LP_URL,
    },
    {
        "link_text": "Shop Tennis Bracelets",
        "description1": "Lab-grown and natural diamonds",
        "description2": "Free shipping across Canada",
        "final_url": "https://globaldiamondmontreal.com/collections/tennis-bracelets",
    },
    {
        "link_text": "Book a Free Consultation",
        "description1": "In-store or virtual, free",
        "description2": "Available 7 days a week",
        "final_url": "https://globaldiamondmontreal.com/pages/book-appointment",
    },
    {
        "link_text": "Custom Bracelet Design",
        "description1": "Tell us her style and budget",
        "description2": "Built by a manufacturer",
        "final_url": "https://globaldiamondmontreal.com/pages/custom-design",
    },
    {
        "link_text": "Pay Monthly with Affirm",
        "description1": "Flexible payment options",
        "description2": "No upfront payment required",
        "final_url": "https://globaldiamondmontreal.com",
    },
    {
        "link_text": "Visit Us in Montreal",
        "description1": "Global Diamond Montreal",
        "description2": "40+ years of craftsmanship",
        "final_url": "https://globaldiamondmontreal.com/pages/contact",
    },
]

CALLOUTS = [
    "Free Shipping to Canada",
    "10% Off Diamonds",
    "Free Studs with $2,500+",
    "Lab-Grown Diamonds",
    "Made in Montreal",
    "40+ Years of Experience",
    "Pay Monthly with Affirm",
    "Free Consultation",
    "Custom Design Available",
    "Natural Diamonds",
]

BRAND_NEGATIVES = [
    ("pandora", "BROAD"),
    ("cartier", "BROAD"),
    ("hermes", "BROAD"),
    ("hermès", "BROAD"),
    ("louis vuitton", "BROAD"),
    ("tiffany", "BROAD"),
    ("tiffany and co", "BROAD"),
    ("gucci", "BROAD"),
    ("coach", "BROAD"),
    ("kate spade", "BROAD"),
    ("swarovski", "BROAD"),
    ("harry winston", "BROAD"),
    ("birks", "BROAD"),
    ("walmart", "BROAD"),
    ("amazon", "BROAD"),
    ("etsy", "BROAD"),
    ("ebay", "BROAD"),
    ("costco", "BROAD"),
    ("jobs", "BROAD"),
    ("career", "BROAD"),
    ("hiring", "BROAD"),
    ("how to make", "BROAD"),
    ("diy", "BROAD"),
    ("tutorial", "BROAD"),
    ("wholesale", "BROAD"),
    ("bulk", "BROAD"),
]

EN_CAMPAIGN_NEGATIVES = [
    ("charm bracelet", "PHRASE"),
    ("anklet", "PHRASE"),
    ("ankle bracelet", "PHRASE"),
    ("men's bracelet", "PHRASE"),
    ("bracelet men", "PHRASE"),
    ("bangle", "PHRASE"),
    ("beaded bracelet", "PHRASE"),
    ("rubber bracelet", "PHRASE"),
    ("silicone bracelet", "PHRASE"),
    ("friendship bracelet", "PHRASE"),
    ("string bracelet", "PHRASE"),
    ("repair", "PHRASE"),
    ("fix", "PHRASE"),
    ("broken", "PHRASE"),
    ("engraving only", "PHRASE"),
    ("used", "PHRASE"),
    ("second hand", "PHRASE"),
    ("pre-owned", "PHRASE"),
]

FR_CAMPAIGN_NEGATIVES = [
    ("bracelet homme", "PHRASE"),
    ("bracelet enfant", "PHRASE"),
    ("bracelet bébé", "PHRASE"),
    ("bracelet chevillère", "PHRASE"),
    ("occasion", "PHRASE"),
    ("d'occasion", "PHRASE"),
    ("réparer", "PHRASE"),
    ("grossiste", "PHRASE"),
]

CAMPAIGNS_DATA = [
    {
        "name": "GDM | Search | Mother's Day EN (2026)",
        "budget_name": "GDM | MD EN 2026 Budget",
        "budget_daily_usd": 50,
        "start_date": "2026-04-10 00:00:00",
        "end_date": "2026-05-11 23:59:59",
        "language_id": LANG_EN,
        "campaign_negatives": BRAND_NEGATIVES + EN_CAMPAIGN_NEGATIVES,
        "ad_groups": [
            {
                "name": "AG1: Mother's Day Bracelet Core",
                "final_url": LP_URL,
                "keywords": [
                    ("mothers day bracelet", "EXACT"),
                    ("mothers day bracelet", "PHRASE"),
                    ("happy mothers day bracelet", "EXACT"),
                    ("bracelet for mothers day", "PHRASE"),
                    ("mothers day bracelet gift", "PHRASE"),
                    ("mothers day bracelets canada", "PHRASE"),
                ],
                "negatives": [
                    ("personalized", "EXACT"),
                    ("custom", "EXACT"),
                    ("birthstone", "EXACT"),
                ],
                "headlines": [
                    # (text, pin_field_or_None)
                    ("Mother's Day Bracelets", "HEADLINE_1"),
                    ("10% Off Diamond Collection", None),
                    ("Free Studs With $2,500+ Orders", None),
                    ("20% Off Diamond Orders $3K+", None),
                    ("Montreal's Jeweler Since 1982", None),
                    ("Lab-Grown + Natural Diamonds", None),
                    ("Free Shipping Across Canada", None),
                    ("Book a Free Consultation", None),
                    ("The Perfect Gift for Mom", None),
                    ("Pay Monthly With Affirm", None),
                    ("40+ Years of Craftsmanship", None),
                    ("Designer Bracelets for Mom", None),
                    ("Shop the Bracelet Collection", None),
                    ("Free 1ct Studs on $5,000+", None),
                    ("In-Store and Online Pickup", None),
                ],
                "descriptions": [
                    ("10% off our diamond collection this Mother's Day. Free studs with $2,500+ orders.", "DESCRIPTION_1"),
                    ("GDM: Montreal's diamond manufacturer since 1982. Free studs with orders $2,500+.", None),
                    ("Pay monthly with Affirm. Free consultation available. Ships within 14 business days.", None),
                    ("Not just a retailer, we're a manufacturer. Custom bracelets made to her vision.", None),
                ],
            },
            {
                "name": "AG2: Mother's Day Jewelry Gift",
                "final_url": LP_URL,
                "keywords": [
                    ("mothers day jewelry gift", "PHRASE"),
                    ("mothers day presents jewellery", "PHRASE"),
                    ("mothers day jewellery", "PHRASE"),
                    ("jewelry for mom", "PHRASE"),
                    ("mom day jewelry", "PHRASE"),
                    ("jewellery for mother", "PHRASE"),
                    ("mothers day earrings", "PHRASE"),
                ],
                "negatives": [
                    ("bracelet", "EXACT"),
                ],
                "headlines": [
                    ("The Perfect Gift for Mom", "HEADLINE_1"),
                    ("Mother's Day Jewelry Sale", None),
                    ("10% Off Diamond Collection", None),
                    ("Free Studs With $2,500+ Orders", None),
                    ("Fine Jewelry for Mother's Day", None),
                    ("Montreal's Jeweler Since 1982", None),
                    ("Lab-Grown + Natural Diamonds", None),
                    ("Rings, Pendants and Bracelets", None),
                    ("Free Shipping Across Canada", None),
                    ("The Gift She'll Wear Forever", None),
                    ("Custom Jewelry for Her", None),
                    ("Book a Free Consultation", None),
                    ("Pay Monthly With Affirm", None),
                    ("Shop Our Mother's Day Gifts", None),
                    ("Gift Ideas She'll Treasure", None),
                ],
                "descriptions": [
                    ("Shop fine jewelry this Mother's Day. 10% off diamonds, free studs with $2,500+ orders.", "DESCRIPTION_1"),
                    ("Bracelets, rings, and pendants. GDM is Montreal's jewelry manufacturer since 1982.", None),
                    ("Free Canada shipping. Pay monthly with Affirm. Book a free consultation today.", None),
                    ("GDM designs and manufactures jewelry in Montreal. Every piece can be custom-made for her.", None),
                ],
            },
            {
                "name": "AG3: Personalized + Custom",
                "final_url": LP_URL,
                "keywords": [
                    ("personalized jewelry for mom", "PHRASE"),
                    ("custom jewelry for mom", "PHRASE"),
                    ("mothers personalized jewelry", "PHRASE"),
                    ("birthstone bracelet for mom", "PHRASE"),
                    ("mothers birthstone bracelet", "PHRASE"),
                    ("mom bracelet with birthstone", "PHRASE"),
                    ("family birthstone bracelets", "PHRASE"),
                    ("personalized bracelet for mom", "PHRASE"),
                    ("custom bracelet for mom", "PHRASE"),
                    ("personalized mothers day jewelry", "PHRASE"),
                ],
                "negatives": [],
                "headlines": [
                    ("Custom Designed for Her", "HEADLINE_1"),
                    ("Personalized Bracelets Mom", None),
                    ("Birthstone Bracelets for Mom", None),
                    ("Custom Jewelry for Mom", None),
                    ("10% Off Diamond Collection", None),
                    ("Free Studs With $2,500+ Orders", None),
                    ("Mother's Day Bracelets", None),
                    ("Montreal's Jeweler Since 1982", None),
                    ("Built Around Her Style", None),
                    ("Choose Her Stone and Metal", None),
                    ("Free Shipping Across Canada", None),
                    ("Book a Free Consultation", None),
                    ("Lab-Grown + Natural Diamonds", None),
                    ("Pay Monthly With Affirm", None),
                    ("Every Detail, Your Choice", None),
                ],
                "descriptions": [
                    ("Design a custom bracelet for Mom. Choose her stone, metal, and style at GDM.", "DESCRIPTION_1"),
                    ("GDM is a manufacturer, not just a store. Personalized pieces made exactly to your brief.", None),
                    ("10% off our diamond collection. Free studs with $2,500+ orders. Free Canada shipping.", None),
                    ("Choose her birthstone and metal. Free consultation included. Ships in 14 business days.", None),
                ],
            },
            {
                "name": "AG4: Tennis + Diamond Bracelet",
                "final_url": LP_URL,
                "keywords": [
                    ("tennis bracelet canada", "EXACT"),
                    ("tennis bracelet canada", "PHRASE"),
                    ("diamond tennis bracelet canada", "EXACT"),
                    ("diamond tennis bracelet canada", "PHRASE"),
                    ("designer bracelets for women", "PHRASE"),
                    ("diamond bracelet gift", "PHRASE"),
                    ("white gold bracelet for women", "PHRASE"),
                ],
                "negatives": [
                    ("mothers day", "EXACT"),
                    ("gift", "EXACT"),
                    ("birthday", "EXACT"),
                ],
                "headlines": [
                    ("Diamond Tennis Bracelets", "HEADLINE_1"),
                    ("Tennis Bracelets Canada", None),
                    ("10% Off Diamond Collection", None),
                    ("Free Studs With $2,500+ Orders", None),
                    ("20% Off Diamond Orders $3K+", None),
                    ("Lab-Grown + Natural Diamonds", None),
                    ("Montreal's Jeweler Since 1982", None),
                    ("Free Shipping Across Canada", None),
                    ("Designer Diamond Bracelets", None),
                    ("White Gold and Yellow Gold", None),
                    ("Gift Her a Diamond Bracelet", None),
                    ("Pay Monthly With Affirm", None),
                    ("Book a Free Consultation", None),
                    ("Free 1ct Studs on $5,000+", None),
                    ("40+ Years of Craftsmanship", None),
                ],
                "descriptions": [
                    ("Shop lab-grown and natural diamond tennis bracelets. 10% off this Mother's Day at GDM.", "DESCRIPTION_1"),
                    ("Free studs with diamond orders: 0.26ct at $2,500+, 0.50ct at $3,500+, 1ct at $5,000+.", None),
                    ("Montreal's jewelry manufacturer since 1982. Pay monthly with Affirm. Free Canada shipping.", None),
                    ("Not just a retailer, a manufacturer. Custom stone and setting options available at GDM.", None),
                ],
            },
        ],
    },
    {
        "name": "GDM | Search | Mother's Day FR (2026)",
        "budget_name": "GDM | MD FR 2026 Budget",
        "budget_daily_usd": 35,
        "start_date": "2026-04-10 00:00:00",
        "end_date": "2026-05-11 23:59:59",
        "language_id": LANG_FR,
        "campaign_negatives": BRAND_NEGATIVES + FR_CAMPAIGN_NEGATIVES,
        "ad_groups": [
            {
                "name": "AG5: Fête des mères",
                "final_url": LP_URL,
                "keywords": [
                    ("bracelet fete des meres", "PHRASE"),
                    ("bracelet fête des mères", "PHRASE"),
                    ("cadeau maman bijoux", "PHRASE"),
                    ("bijoux fete des meres", "PHRASE"),
                    ("bijoux fête des mères", "PHRASE"),
                    ("cadeau pour maman montreal", "PHRASE"),
                    ("bijoux fete des meres montreal", "PHRASE"),
                    ("bracelet pour maman", "PHRASE"),
                    ("bracelet maman personnalise", "PHRASE"),
                    ("cadeau maman montreal", "PHRASE"),
                ],
                "negatives": [],
                "headlines": [
                    ("Bracelet Fête des Mères", "HEADLINE_1"),
                    ("Cadeau Maman Bijoux GDM", None),
                    ("10% de Rabais sur Diamants", None),
                    ("Livraison Gratuite au Canada", None),
                    ("Bijoutier Montréalais 1982", None),
                    ("Bracelets Diamant pour Maman", None),
                    ("Studs Gratuits dès $2 500+", None),
                    ("Bracelet Personnalisé Maman", None),
                    ("Consultation Gratuite", None),
                    ("Diamants Naturels et Cultivés", None),
                    ("Payer Mensuel avec Affirm", None),
                    ("Or Blanc, Jaune et Rosé", None),
                    ("Bijoux sur Mesure Montréal", None),
                    ("40 Ans de Savoir-Faire", None),
                    ("La Fête des Mères en Bijoux", None),
                ],
                "descriptions": [
                    ("10% de rabais sur nos diamants ce fête des mères. Studs gratuits avec achats de $2 500+.", "DESCRIPTION_1"),
                    ("GDM, fabricant montréalais de bijoux depuis 1982. Bracelets sur mesure possibles.", None),
                    ("Payer mensuel avec Affirm. Consultation gratuite. Expédition en 14 jours ouvrables.", None),
                    ("Diamants naturels et cultivés. Chaque pièce conçue par nos artisans montréalais.", None),
                ],
            },
            {
                "name": "AG6: Bracelet Diamant + Or FR",
                "final_url": LP_URL,
                "keywords": [
                    ("bracelet diamant", "PHRASE"),
                    ("bracelet diamant femme", "PHRASE"),
                    ("tennis bracelet diamant", "PHRASE"),
                    ("bracelet diamant tennis", "PHRASE"),
                    ("bracelet or femme", "PHRASE"),
                    ("bracelet en or femme", "PHRASE"),
                    ("bracelet or blanc femme", "PHRASE"),
                    ("bracelet achat montreal", "PHRASE"),
                ],
                "negatives": [],
                "headlines": [
                    ("Bracelets Diamant pour Femme", "HEADLINE_1"),
                    ("Bracelets en Or pour Femme", None),
                    ("Bijoutier Montréalais 1982", None),
                    ("Bracelets Tennis Diamant", None),
                    ("Or Blanc, Jaune et Rosé", None),
                    ("Fabricant de Bijoux Montréal", None),
                    ("Livraison Gratuite au Canada", None),
                    ("Diamants Naturels et Cultivés", None),
                    ("Bijoux sur Mesure Montréal", None),
                    ("Consultation Gratuite", None),
                    ("40 Ans de Savoir-Faire", None),
                    ("Payer Mensuel avec Affirm", None),
                    ("Or 14K, 18K et Platine", None),
                    ("Collection Bijoux 2026", None),
                    ("Bracelets Femme Montréal", None),
                ],
                "descriptions": [
                    ("GDM, fabricant montréalais de bijoux en or et diamants depuis 1982. Livraison gratuite.", "DESCRIPTION_1"),
                    ("Choisissez votre métal et votre pierre. Chaque bracelet créé sur mesure à Montréal.", None),
                    ("Or blanc, jaune et rosé. Diamants naturels et cultivés. Consultation gratuite en boutique.", None),
                    ("Payer mensuel avec Affirm. Expédition 14 jours ouvrables. 35 000 heures d'artisanat.", None),
                ],
            },
        ],
    },
]


# ─── GOOGLE ADS CLIENT ────────────────────────────────────────────────────────

def build_client():
    return GoogleAdsClient.load_from_dict({
        "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
        "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "login_customer_id": os.environ["GOOGLE_ADS_CUSTOMER_ID"],
        "use_proto_plus": True,
    })


# ─── PREVIEW ─────────────────────────────────────────────────────────────────

def print_build_preview():
    print("\n" + "=" * 65)
    print("PREVIEW: GDM Mother's Day 2026 Campaign Build")
    print("=" * 65)
    total_kw = 0
    total_ag = 0
    for c in CAMPAIGNS_DATA:
        ag_count = len(c["ad_groups"])
        kw_count = sum(len(ag["keywords"]) for ag in c["ad_groups"])
        neg_count = len(c["campaign_negatives"])
        total_kw += kw_count
        total_ag += ag_count
        print(f"\n  Campaign: {c['name']}")
        print(f"    Budget:      ${c['budget_daily_usd']}/day (PAUSED)")
        print(f"    Dates:       {c['start_date'][:10]} to {c['end_date'][:10]}")
        print(f"    Ad groups:   {ag_count}")
        print(f"    Keywords:    {kw_count}")
        print(f"    Negatives:   {neg_count} (campaign level)")
        for ag in c["ad_groups"]:
            print(f"      - {ag['name']}: {len(ag['keywords'])} kw, 1 RSA, {len(ag['negatives'])} ag-neg")
    print(f"\n  Sitelinks:   {len(SITELINKS)} (both campaigns)")
    print(f"  Callouts:    {len(CALLOUTS)} (both campaigns)")
    print(f"\n  Total ad groups: {total_ag}")
    print(f"  Total keywords:  {total_kw}")
    print(f"  Total RSAs:      {total_ag}")
    print("=" * 65)


def request_approval(dry_run):
    if dry_run:
        print("\n[DRY RUN] No changes made.\n")
        return False
    answer = input("\nApprove and create all of the above? [yes/no]: ").strip().lower()
    if answer == "yes":
        print("Approved. Building...\n")
        return True
    print("Cancelled. No changes made.")
    return False


# ─── API OPERATIONS ───────────────────────────────────────────────────────────

def create_budget(client, cid, name, daily_usd):
    service = client.get_service("CampaignBudgetService")
    op = client.get_type("CampaignBudgetOperation")
    budget = op.create
    budget.name = name
    budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
    budget.amount_micros = int(daily_usd * 1_000_000)
    budget.explicitly_shared = False  # required for Maximize Conversions
    result = service.mutate_campaign_budgets(customer_id=cid, operations=[op])
    rn = result.results[0].resource_name
    print(f"  [budget] {name} — ${daily_usd}/day — {rn}")
    return rn


def create_campaign(client, cid, name, budget_rn, start, end, language_id):
    service = client.get_service("CampaignService")
    op = client.get_type("CampaignOperation")
    campaign = op.create
    campaign.name = name
    campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
    campaign.status = client.enums.CampaignStatusEnum.PAUSED
    campaign.start_date_time = start
    campaign.end_date_time = end
    campaign.campaign_budget = budget_rn
    # Maximize Conversions with no target CPA
    campaign.maximize_conversions.target_cpa_micros = 0
    # Search only — no display expansion, no search partners
    campaign.network_settings.target_google_search = True
    campaign.network_settings.target_search_network = False
    campaign.network_settings.target_content_network = False
    campaign.network_settings.target_partner_search_network = False
    # Required in v23. 3 = DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
    campaign.contains_eu_political_advertising = (
        client.enums.EuPoliticalAdvertisingStatusEnum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
    )

    result = service.mutate_campaigns(customer_id=cid, operations=[op])
    campaign_rn = result.results[0].resource_name
    campaign_id = campaign_rn.split("/")[-1]
    print(f"  [campaign] {name} — ID: {campaign_id} — PAUSED")

    # Geo: Canada
    _add_geo_target(client, cid, campaign_rn, GEO_CANADA)
    # Language
    _add_language_target(client, cid, campaign_rn, language_id)

    return campaign_rn, campaign_id


def _add_geo_target(client, cid, campaign_rn, geo_id):
    service = client.get_service("CampaignCriterionService")
    op = client.get_type("CampaignCriterionOperation")
    criterion = op.create
    criterion.campaign = campaign_rn
    geo_service = client.get_service("GeoTargetConstantService")
    criterion.location.geo_target_constant = geo_service.geo_target_constant_path(geo_id)
    service.mutate_campaign_criteria(customer_id=cid, operations=[op])
    print(f"    [geo] Canada (ID {geo_id}) added")


def _add_language_target(client, cid, campaign_rn, lang_id):
    service = client.get_service("CampaignCriterionService")
    op = client.get_type("CampaignCriterionOperation")
    criterion = op.create
    criterion.campaign = campaign_rn
    criterion.language.language_constant = f"languageConstants/{lang_id}"
    service.mutate_campaign_criteria(customer_id=cid, operations=[op])
    lang_name = "English" if lang_id == LANG_EN else "French"
    print(f"    [language] {lang_name} (ID {lang_id}) added")


def add_campaign_negatives(client, cid, campaign_rn, negatives):
    service = client.get_service("CampaignCriterionService")
    ops = []
    match_map = {
        "BROAD": client.enums.KeywordMatchTypeEnum.BROAD,
        "PHRASE": client.enums.KeywordMatchTypeEnum.PHRASE,
        "EXACT": client.enums.KeywordMatchTypeEnum.EXACT,
    }
    for kw_text, match_type_str in negatives:
        op = client.get_type("CampaignCriterionOperation")
        criterion = op.create
        criterion.campaign = campaign_rn
        criterion.negative = True
        criterion.keyword.text = kw_text
        criterion.keyword.match_type = match_map[match_type_str]
        ops.append(op)
    # Batch in chunks of 50 to stay within API limits
    for i in range(0, len(ops), 50):
        service.mutate_campaign_criteria(customer_id=cid, operations=ops[i:i + 50])
    print(f"    [negatives] {len(negatives)} campaign-level negatives added")


def create_ad_group(client, cid, campaign_rn, name):
    service = client.get_service("AdGroupService")
    op = client.get_type("AdGroupOperation")
    ag = op.create
    ag.name = name
    ag.campaign = campaign_rn
    ag.status = client.enums.AdGroupStatusEnum.PAUSED
    ag.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
    result = service.mutate_ad_groups(customer_id=cid, operations=[op])
    ag_rn = result.results[0].resource_name
    ag_id = ag_rn.split("/")[-1]
    print(f"    [ad group] {name} — ID: {ag_id} — PAUSED")
    return ag_rn, ag_id


def add_keywords(client, cid, ag_rn, keywords):
    service = client.get_service("AdGroupCriterionService")
    match_map = {
        "EXACT": client.enums.KeywordMatchTypeEnum.EXACT,
        "PHRASE": client.enums.KeywordMatchTypeEnum.PHRASE,
        "BROAD": client.enums.KeywordMatchTypeEnum.BROAD,
    }
    ops = []
    for kw_text, match_type_str in keywords:
        op = client.get_type("AdGroupCriterionOperation")
        criterion = op.create
        criterion.ad_group = ag_rn
        criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED
        criterion.keyword.text = kw_text
        criterion.keyword.match_type = match_map[match_type_str]
        ops.append(op)
    service.mutate_ad_group_criteria(customer_id=cid, operations=ops)
    print(f"      [keywords] {len(keywords)} added")


def add_ag_negatives(client, cid, ag_rn, negatives):
    if not negatives:
        return
    service = client.get_service("AdGroupCriterionService")
    match_map = {
        "EXACT": client.enums.KeywordMatchTypeEnum.EXACT,
        "PHRASE": client.enums.KeywordMatchTypeEnum.PHRASE,
        "BROAD": client.enums.KeywordMatchTypeEnum.BROAD,
    }
    ops = []
    for kw_text, match_type_str in negatives:
        op = client.get_type("AdGroupCriterionOperation")
        criterion = op.create
        criterion.ad_group = ag_rn
        criterion.negative = True
        criterion.keyword.text = kw_text
        criterion.keyword.match_type = match_map[match_type_str]
        ops.append(op)
    service.mutate_ad_group_criteria(customer_id=cid, operations=ops)
    print(f"      [ag negatives] {len(negatives)} added")


def create_rsa(client, cid, ag_rn, final_url, headlines, descriptions):
    service = client.get_service("AdGroupAdService")
    op = client.get_type("AdGroupAdOperation")
    ag_ad = op.create
    ag_ad.ad_group = ag_rn
    ag_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED

    ad = ag_ad.ad
    ad.final_urls.append(final_url)

    pin_map = {
        "HEADLINE_1": client.enums.ServedAssetFieldTypeEnum.HEADLINE_1,
        "HEADLINE_2": client.enums.ServedAssetFieldTypeEnum.HEADLINE_2,
        "HEADLINE_3": client.enums.ServedAssetFieldTypeEnum.HEADLINE_3,
        "DESCRIPTION_1": client.enums.ServedAssetFieldTypeEnum.DESCRIPTION_1,
        "DESCRIPTION_2": client.enums.ServedAssetFieldTypeEnum.DESCRIPTION_2,
    }

    rsa = ad.responsive_search_ad
    for text, pin in headlines:
        asset = client.get_type("AdTextAsset")
        asset.text = text
        if pin:
            asset.pinned_field = pin_map[pin]
        rsa.headlines.append(asset)

    for text, pin in descriptions:
        asset = client.get_type("AdTextAsset")
        asset.text = text
        if pin:
            asset.pinned_field = pin_map[pin]
        rsa.descriptions.append(asset)

    result = service.mutate_ad_group_ads(customer_id=cid, operations=[op])
    rsa_rn = result.results[0].resource_name
    print(f"      [RSA] created — {len(headlines)} headlines, {len(descriptions)} descriptions — PAUSED")
    return rsa_rn


def create_sitelink_asset(client, cid, link_text, desc1, desc2, final_url):
    service = client.get_service("AssetService")
    op = client.get_type("AssetOperation")
    asset = op.create
    asset.name = f"Sitelink: {link_text}"
    asset.sitelink_asset.link_text = link_text
    asset.sitelink_asset.description1 = desc1
    asset.sitelink_asset.description2 = desc2
    asset.final_urls.append(final_url)
    result = service.mutate_assets(customer_id=cid, operations=[op])
    return result.results[0].resource_name


def create_callout_asset(client, cid, callout_text):
    service = client.get_service("AssetService")
    op = client.get_type("AssetOperation")
    asset = op.create
    asset.name = f"Callout: {callout_text}"
    asset.callout_asset.callout_text = callout_text
    result = service.mutate_assets(customer_id=cid, operations=[op])
    return result.results[0].resource_name


def link_asset_to_campaign(client, cid, asset_rn, campaign_rn, field_type_enum):
    service = client.get_service("CampaignAssetService")
    op = client.get_type("CampaignAssetOperation")
    ca = op.create
    ca.asset = asset_rn
    ca.field_type = field_type_enum
    ca.campaign = campaign_rn
    service.mutate_campaign_assets(customer_id=cid, operations=[op])


def create_and_link_assets(client, cid, campaign_rn):
    sitelink_type = client.enums.AssetFieldTypeEnum.SITELINK
    callout_type = client.enums.AssetFieldTypeEnum.CALLOUT

    print(f"    [sitelinks] Creating {len(SITELINKS)} sitelinks...")
    for sl in SITELINKS:
        asset_rn = create_sitelink_asset(
            client, cid,
            sl["link_text"], sl["description1"], sl["description2"], sl["final_url"]
        )
        link_asset_to_campaign(client, cid, asset_rn, campaign_rn, sitelink_type)
    print(f"      {len(SITELINKS)} sitelinks linked")

    print(f"    [callouts] Creating {len(CALLOUTS)} callouts...")
    for ct in CALLOUTS:
        asset_rn = create_callout_asset(client, cid, ct)
        link_asset_to_campaign(client, cid, asset_rn, campaign_rn, callout_type)
    print(f"      {len(CALLOUTS)} callouts linked")


# ─── MAIN BUILD ───────────────────────────────────────────────────────────────

def build(client, dry_run):
    log = {
        "created_at": datetime.now().isoformat(),
        "customer_id": CUSTOMER_ID,
        "dry_run": dry_run,
        "campaigns": [],
    }

    for camp_data in CAMPAIGNS_DATA:
        print(f"\n{'='*65}")
        print(f"Building: {camp_data['name']}")
        print(f"{'='*65}")

        camp_log = {
            "name": camp_data["name"],
            "ad_groups": [],
        }

        # Budget
        budget_rn = create_budget(
            client, CUSTOMER_ID,
            camp_data["budget_name"],
            camp_data["budget_daily_usd"]
        )
        camp_log["budget_resource_name"] = budget_rn

        # Campaign
        campaign_rn, campaign_id = create_campaign(
            client, CUSTOMER_ID,
            camp_data["name"],
            budget_rn,
            camp_data["start_date"],
            camp_data["end_date"],
            camp_data["language_id"],
        )
        camp_log["resource_name"] = campaign_rn
        camp_log["campaign_id"] = campaign_id

        # Campaign-level negatives
        print(f"\n  Adding campaign negatives...")
        add_campaign_negatives(client, CUSTOMER_ID, campaign_rn, camp_data["campaign_negatives"])

        # Ad groups
        print(f"\n  Building ad groups...")
        for ag_data in camp_data["ad_groups"]:
            ag_rn, ag_id = create_ad_group(client, CUSTOMER_ID, campaign_rn, ag_data["name"])
            add_keywords(client, CUSTOMER_ID, ag_rn, ag_data["keywords"])
            add_ag_negatives(client, CUSTOMER_ID, ag_rn, ag_data["negatives"])
            rsa_rn = create_rsa(
                client, CUSTOMER_ID, ag_rn,
                ag_data["final_url"],
                ag_data["headlines"],
                ag_data["descriptions"],
            )
            camp_log["ad_groups"].append({
                "name": ag_data["name"],
                "resource_name": ag_rn,
                "ad_group_id": ag_id,
                "keywords_added": len(ag_data["keywords"]),
                "rsa_resource_name": rsa_rn,
            })

        # Assets
        print(f"\n  Adding ad assets...")
        create_and_link_assets(client, CUSTOMER_ID, campaign_rn)

        log["campaigns"].append(camp_log)
        print(f"\n  Campaign '{camp_data['name']}' complete.")

    # Write log
    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)
    print(f"\n{'='*65}")
    print(f"Build complete. Log saved to: {LOG_PATH}")
    print(f"\nCreated campaigns (PAUSED):")
    for c in log["campaigns"]:
        print(f"  ID {c['campaign_id']} — {c['name']}")
        for ag in c["ad_groups"]:
            print(f"    AG {ag['ad_group_id']} — {ag['name']} ({ag['keywords_added']} kw)")
    print(f"\nDashboard: https://ads.google.com/aw/campaigns?ocid={CUSTOMER_ID}")


def main():
    parser = argparse.ArgumentParser(
        description="GDM Mother's Day 2026 — Google Ads campaign builder"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview build plan without creating anything in Google Ads"
    )
    parser.add_argument(
        "--skip-confirm", action="store_true",
        help="Skip the approval prompt (use with caution)"
    )
    args = parser.parse_args()

    print_build_preview()

    if args.dry_run:
        print("\n[DRY RUN] No changes will be made to Google Ads.")
        return

    if not args.skip_confirm:
        answer = input("\nApprove and build all campaigns/ad groups/keywords/RSAs? [yes/no]: ").strip().lower()
        if answer != "yes":
            print("Cancelled. No changes made.")
            return
        print("Approved. Building...\n")

    client = build_client()
    try:
        build(client, dry_run=False)
    except GoogleAdsException as ex:
        print(f"\n[ERROR] Google Ads API error:")
        for error in ex.failure.errors:
            print(f"  {error.message}")
        sys.exit(1)
    except Exception as ex:
        print(f"\n[ERROR] Unexpected error: {ex}")
        raise


if __name__ == "__main__":
    main()
