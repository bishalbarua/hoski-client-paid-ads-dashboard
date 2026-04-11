"""
GDM — Mother's Day 2026 Google Ads Campaign Sheet Builder
Writes full campaign structure to Google Sheet: 1ihwhJxKTn6u1HzUzTx-EwNuKxEWw677hTAJQ5BxBusI

Tabs created:
  1. Overview            — Campaign settings, budgets, schedule
  2. Keywords - EN       — All EN keywords with ad group, match type, bids
  3. Keywords - FR       — All FR keywords
  4. Negative Keywords   — Account, campaign, and ad group cross-negatives
  5. RSA - AG1           — Mother's Day Bracelet Core (EN)
  6. RSA - AG2           — Mother's Day Jewelry Gift (EN)
  7. RSA - AG3           — Personalized + Custom (EN) [PRIORITY 1]
  8. RSA - AG4           — Tennis + Diamond Bracelet (EN)
  9. RSA - AG5           — Fete des meres (FR) [PRIORITY 1]
  10. RSA - AG6          — Bracelet Diamant + Or (FR) [NO PROMO]
  11. Ad Assets          — Sitelinks, callouts, structured snippets

Run:
  python3 clients/GDM\ Google\ Ads\ \(7087867966\)/notes/build_mothers_day_sheet.py

Requires:
  - sheets-credentials.json in project root (service account JSON)
  - The sheet shared with the service account email in that JSON
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.sheets_writer import write_to_sheet

SHEET_ID = "1ihwhJxKTn6u1HzUzTx-EwNuKxEWw677hTAJQ5BxBusI"


# ─── TAB 1: OVERVIEW ──────────────────────────────────────────────────────────

def build_overview():
    headers = ["Field", "Campaign 1 (EN)", "Campaign 2 (FR)"]
    rows = [
        ["Campaign Name",           "GDM | Search | Mother's Day EN (2026)",      "GDM | Search | Mother's Day FR (2026)"],
        ["Campaign Type",           "Search",                                       "Search"],
        ["Goal",                    "Sales / Purchases + Appointment Bookings",     "Sales / Purchases + Appointment Bookings"],
        ["Networks",                "Search only (no Display, no Search Partners)", "Search only (no Display, no Search Partners)"],
        ["Bid Strategy",            "Max Conversions",                              "Max Conversions"],
        ["Start Date",              "2026-04-10",                                   "2026-04-10"],
        ["End Date",                "2026-05-11",                                   "2026-05-11"],
        ["Daily Budget — Wks 1-2",  "$50 CAD (Apr 10-24)",                          "$35 CAD (Apr 10-24)"],
        ["Daily Budget — Wks 3-4",  "$75 CAD (Apr 25 - May 11)",                   "$50 CAD (Apr 25 - May 11)"],
        ["Est. Total Spend",        "~$1,500 CAD",                                  "~$850 CAD"],
        ["Languages",               "English",                                      "French"],
        ["Location",                "Canada",                                       "Canada (prioritize QC)"],
        ["Ad Rotation",             "Optimize (prefer best performing)",            "Optimize (prefer best performing)"],
        ["Landing Page",            "globaldiamondmontreal.com/collections/mothers-day-bracelet-collection",
                                    "globaldiamondmontreal.com/collections/mothers-day-bracelet-collection"],
        ["Conversion Actions",      "Purchase, Book Appointment (In-Store + Virtual), Add to Cart, Offline Upload (Zapier)",
                                    "Purchase, Book Appointment (In-Store + Virtual), Add to Cart, Offline Upload (Zapier)"],
        [""],
        ["BUDGET RAMP SCHEDULE", "", ""],
        ["Weeks 1-2 (Apr 10-24)",   "$85/day total",   ""],
        ["Weeks 3-4 (Apr 25-May 11)","$125/day total", ""],
        ["Est. Total All Campaigns", "~$2,350 CAD",    ""],
        [""],
        ["OFFER CONSTRAINTS", "", ""],
        ["10% off",                 "Diamond collection only — no min. Gold EXCLUDED.", ""],
        ["20% off",                 "Diamond purchases $3,000+. Gold EXCLUDED.",        ""],
        ["Free 0.26ct studs",       "Diamond purchases $2,500+ (updated from $2k)",     ""],
        ["Free 0.50ct studs",       "Diamond purchases $3,500+ (updated from $3k)",     ""],
        ["Free 1.00ct studs",       "Diamond purchases $5,000+",                        ""],
        ["Earring copy HOLD",       "Hold earring references in AG2 until Doc confirms price increases are live.", ""],
        ["AG6 (FR gold keywords)",  "NO promo copy — gold excluded. Brand/craftsmanship angle only.", ""],
        [""],
        ["BUILD ORDER", "", ""],
        ["Launch by Apr 12",        "AG3 (Personalized/Custom), AG1 (Bracelet Core), AG5 (FR Fete des meres)", ""],
        ["Launch by Apr 17",        "AG2 (Jewelry Gift), AG4 (Tennis/Diamond), AG6 (FR Or + Diamant)",         ""],
        ["Final Sprint Apr 25",     "Increase EN to $75/day, FR to $50/day. Kill any AG with CPA > $250.",      ""],
    ]
    write_to_sheet(SHEET_ID, "Overview", headers, rows)


# ─── TAB 2: KEYWORDS — EN ─────────────────────────────────────────────────────

def build_keywords_en():
    headers = [
        "Ad Group", "Ad Group #", "Keyword", "Match Type",
        "Avg Monthly (CA)", "Competition", "Low Bid CAD", "High Bid CAD", "Notes"
    ]
    rows = [
        # AG1: Mother's Day Bracelet Core
        ["Mother's Day Bracelet Core", "AG1", "mothers day bracelet",         "Exact",  "170", "HIGH",   "$0.87", "$3.47", "Core term — pin H1"],
        ["Mother's Day Bracelet Core", "AG1", "mothers day bracelet",         "Phrase", "170", "HIGH",   "$0.87", "$3.47", ""],
        ["Mother's Day Bracelet Core", "AG1", "happy mothers day bracelet",   "Exact",  "170", "HIGH",   "$0.87", "$3.47", ""],
        ["Mother's Day Bracelet Core", "AG1", "bracelet for mothers day",     "Phrase", "",    "",       "",      "",      ""],
        ["Mother's Day Bracelet Core", "AG1", "mothers day bracelet gift",    "Phrase", "",    "",       "",      "",      ""],
        ["Mother's Day Bracelet Core", "AG1", "mothers day bracelets canada", "Phrase", "",    "",       "",      "",      "Local modifier"],
        # AG2: Mother's Day Jewelry Gift
        ["Mother's Day Jewelry Gift",  "AG2", "mothers day jewelry gift",     "Phrase", "140", "LOW",    "$0.89", "$4.04", "LOW comp — priority"],
        ["Mother's Day Jewelry Gift",  "AG2", "mothers day presents jewellery","Phrase","140", "LOW",    "$0.89", "$4.04", "LOW comp — priority"],
        ["Mother's Day Jewelry Gift",  "AG2", "mothers day jewellery",        "Phrase", "480", "HIGH",   "$0.63", "$3.08", ""],
        ["Mother's Day Jewelry Gift",  "AG2", "jewelry for mom",              "Phrase", "320", "HIGH",   "$0.68", "$2.51", ""],
        ["Mother's Day Jewelry Gift",  "AG2", "mom day jewelry",              "Phrase", "480", "HIGH",   "$0.63", "$3.08", ""],
        ["Mother's Day Jewelry Gift",  "AG2", "jewellery for mother",         "Phrase", "320", "HIGH",   "$0.68", "$2.51", ""],
        ["Mother's Day Jewelry Gift",  "AG2", "mothers day earrings",         "Phrase", "70",  "HIGH",   "$0.68", "$2.20", "HOLD copy referencing earrings until Doc confirms"],
        # AG3: Personalized + Custom PRIORITY 1
        ["Personalized + Custom",      "AG3", "personalized jewelry for mom", "Phrase", "480", "LOW",    "$0.79", "$3.30", "PRIORITY — LOW comp"],
        ["Personalized + Custom",      "AG3", "custom jewelry for mom",       "Phrase", "480", "LOW",    "$0.79", "$3.30", "PRIORITY — LOW comp"],
        ["Personalized + Custom",      "AG3", "mothers personalized jewelry", "Phrase", "480", "LOW",    "$0.79", "$3.30", "PRIORITY — LOW comp"],
        ["Personalized + Custom",      "AG3", "birthstone bracelet for mom",  "Phrase", "170", "MEDIUM", "$0.68", "$2.75", ""],
        ["Personalized + Custom",      "AG3", "mothers birthstone bracelet",  "Phrase", "170", "MEDIUM", "$0.68", "$2.75", ""],
        ["Personalized + Custom",      "AG3", "mom bracelet with birthstone", "Phrase", "170", "MEDIUM", "$0.68", "$2.75", ""],
        ["Personalized + Custom",      "AG3", "family birthstone bracelets",  "Phrase", "210", "MEDIUM", "$0.78", "$2.65", ""],
        ["Personalized + Custom",      "AG3", "personalized bracelet for mom","Phrase", "20",  "MEDIUM", "",      "",      ""],
        ["Personalized + Custom",      "AG3", "custom bracelet for mom",      "Phrase", "20",  "MEDIUM", "",      "",      ""],
        ["Personalized + Custom",      "AG3", "personalized mothers day jewelry","Phrase","30", "LOW",    "$0.80", "$2.63", "LOW comp"],
        # AG4: Tennis + Diamond Bracelet
        ["Tennis + Diamond Bracelet",  "AG4", "tennis bracelet canada",           "Exact",  "590", "HIGH", "$0.52", "$2.62", "High volume — Exact"],
        ["Tennis + Diamond Bracelet",  "AG4", "tennis bracelet canada",           "Phrase", "590", "HIGH", "$0.52", "$2.62", ""],
        ["Tennis + Diamond Bracelet",  "AG4", "diamond tennis bracelet canada",   "Exact",  "260", "HIGH", "$0.60", "$3.22", "High value intent"],
        ["Tennis + Diamond Bracelet",  "AG4", "diamond tennis bracelet canada",   "Phrase", "260", "HIGH", "$0.60", "$3.22", ""],
        ["Tennis + Diamond Bracelet",  "AG4", "designer bracelets for women",     "Phrase", "210", "HIGH", "$0.77", "$2.73", ""],
        ["Tennis + Diamond Bracelet",  "AG4", "diamond bracelet gift",            "Phrase", "",    "",     "",      "",      ""],
        ["Tennis + Diamond Bracelet",  "AG4", "white gold bracelet for women",    "Phrase", "390", "HIGH", "$0.35", "$1.57", ""],
    ]
    write_to_sheet(SHEET_ID, "Keywords - EN", headers, rows)


# ─── TAB 3: KEYWORDS — FR ─────────────────────────────────────────────────────

def build_keywords_fr():
    headers = [
        "Ad Group", "Ad Group #", "Keyword", "Match Type",
        "Avg Monthly (CA)", "Competition", "Low Bid CAD", "High Bid CAD", "Notes"
    ]
    rows = [
        # AG5: Fête des mères FR PRIORITY 1
        ["Fete des meres",           "AG5", "bracelet fete des meres",            "Phrase", "",    "", "", "", "Include accented variant: fête des mères"],
        ["Fete des meres",           "AG5", "bracelet fête des mères",            "Phrase", "",    "", "", "", "Accented variant — low Keyword Planner vol but real traffic"],
        ["Fete des meres",           "AG5", "cadeau maman bijoux",                "Phrase", "",    "", "", "", ""],
        ["Fete des meres",           "AG5", "bijoux fete des meres",              "Phrase", "",    "", "", "", ""],
        ["Fete des meres",           "AG5", "bijoux fête des mères",              "Phrase", "",    "", "", "", "Accented"],
        ["Fete des meres",           "AG5", "cadeau pour maman montreal",         "Phrase", "",    "", "", "", "Local intent"],
        ["Fete des meres",           "AG5", "bijoux fete des meres montreal",     "Phrase", "",    "", "", "", "Local + occasion"],
        ["Fete des meres",           "AG5", "bracelet pour maman",                "Phrase", "",    "", "", "", ""],
        ["Fete des meres",           "AG5", "bracelet maman personnalise",        "Phrase", "",    "", "", "", "Personalization angle"],
        ["Fete des meres",           "AG5", "cadeau maman montreal",              "Phrase", "",    "", "", "", "Local intent"],
        # AG6: Bracelet Diamant + Or FR
        ["Bracelet Diamant + Or FR", "AG6", "bracelet diamant",                   "Phrase", "170", "HIGH", "$0.30", "$1.75", "NO promo copy — gold excluded"],
        ["Bracelet Diamant + Or FR", "AG6", "bracelet diamant femme",             "Phrase", "70",  "HIGH", "$0.30", "$1.22", "NO promo copy"],
        ["Bracelet Diamant + Or FR", "AG6", "tennis bracelet diamant",            "Phrase", "140", "HIGH", "$0.32", "$1.31", "NO promo copy"],
        ["Bracelet Diamant + Or FR", "AG6", "bracelet diamant tennis",            "Phrase", "140", "HIGH", "$0.32", "$1.31", "NO promo copy"],
        ["Bracelet Diamant + Or FR", "AG6", "bracelet or femme",                  "Phrase", "590", "HIGH", "$0.21", "$1.24", "NO promo copy — gold excluded"],
        ["Bracelet Diamant + Or FR", "AG6", "bracelet en or femme",               "Phrase", "880", "HIGH", "$0.12", "$0.97", "Highest FR vol — NO promo copy"],
        ["Bracelet Diamant + Or FR", "AG6", "bracelet or blanc femme",            "Phrase", "170", "HIGH", "$0.19", "$0.94", "NO promo copy"],
        ["Bracelet Diamant + Or FR", "AG6", "bracelet achat montreal",            "Phrase", "",    "",     "",      "",      "Local intent — brand angle"],
    ]
    write_to_sheet(SHEET_ID, "Keywords - FR", headers, rows)


# ─── TAB 4: NEGATIVE KEYWORDS ─────────────────────────────────────────────────

def build_negatives():
    headers = ["Level", "Campaign / Ad Group", "Negative Keyword", "Match Type", "Reason"]
    rows = [
        # Account level
        ["Account", "All Campaigns", "pandora",          "Broad", "Competitor brand"],
        ["Account", "All Campaigns", "cartier",          "Broad", "Competitor brand"],
        ["Account", "All Campaigns", "hermes",           "Broad", "Competitor brand"],
        ["Account", "All Campaigns", "hermès",           "Broad", "Competitor brand (accented)"],
        ["Account", "All Campaigns", "louis vuitton",    "Broad", "Competitor brand"],
        ["Account", "All Campaigns", "tiffany",          "Broad", "Competitor brand"],
        ["Account", "All Campaigns", "tiffany and co",   "Broad", "Competitor brand"],
        ["Account", "All Campaigns", "gucci",            "Broad", "Competitor brand"],
        ["Account", "All Campaigns", "coach",            "Broad", "Competitor brand"],
        ["Account", "All Campaigns", "kate spade",       "Broad", "Competitor brand"],
        ["Account", "All Campaigns", "swarovski",        "Broad", "Competitor brand"],
        ["Account", "All Campaigns", "harry winston",    "Broad", "Competitor brand"],
        ["Account", "All Campaigns", "birks",            "Broad", "Competitor brand"],
        ["Account", "All Campaigns", "walmart",          "Broad", "Mass retailer — not GDM audience"],
        ["Account", "All Campaigns", "amazon",           "Broad", "Mass retailer"],
        ["Account", "All Campaigns", "etsy",             "Broad", "Handmade marketplace — different intent"],
        ["Account", "All Campaigns", "ebay",             "Broad", "Resale — different intent"],
        ["Account", "All Campaigns", "costco",           "Broad", "Mass retailer"],
        ["Account", "All Campaigns", "jobs",             "Broad", "Employment"],
        ["Account", "All Campaigns", "career",           "Broad", "Employment"],
        ["Account", "All Campaigns", "hiring",           "Broad", "Employment"],
        ["Account", "All Campaigns", "salary",           "Broad", "Employment"],
        ["Account", "All Campaigns", "resume",           "Broad", "Employment"],
        ["Account", "All Campaigns", "how to make",      "Broad", "DIY intent"],
        ["Account", "All Campaigns", "diy",              "Broad", "DIY intent"],
        ["Account", "All Campaigns", "do it yourself",   "Broad", "DIY intent"],
        ["Account", "All Campaigns", "tutorial",         "Broad", "DIY intent"],
        ["Account", "All Campaigns", "free template",    "Broad", "Non-commercial"],
        ["Account", "All Campaigns", "wholesale",        "Broad", "B2B — different funnel"],
        ["Account", "All Campaigns", "bulk",             "Broad", "B2B — different funnel"],
        # EN Campaign level
        ["Campaign", "EN Campaign",  "charm bracelet",          "Phrase", "Product not in GDM catalog"],
        ["Campaign", "EN Campaign",  "anklet",                  "Phrase", "Product not in GDM catalog"],
        ["Campaign", "EN Campaign",  "ankle bracelet",          "Phrase", "Product not in GDM catalog"],
        ["Campaign", "EN Campaign",  "men's bracelet",          "Phrase", "Men's — outside Mother's Day scope"],
        ["Campaign", "EN Campaign",  "bracelet men",            "Phrase", "Men's"],
        ["Campaign", "EN Campaign",  "bangle",                  "Phrase", "Product type mismatch unless GDM has bangles — confirm"],
        ["Campaign", "EN Campaign",  "beaded bracelet",         "Phrase", "Not fine jewelry"],
        ["Campaign", "EN Campaign",  "rubber bracelet",         "Phrase", "Not fine jewelry"],
        ["Campaign", "EN Campaign",  "silicone bracelet",       "Phrase", "Not fine jewelry"],
        ["Campaign", "EN Campaign",  "friendship bracelet",     "Phrase", "Not fine jewelry"],
        ["Campaign", "EN Campaign",  "string bracelet",         "Phrase", "Not fine jewelry"],
        ["Campaign", "EN Campaign",  "repair",                  "Phrase", "Service — not a sale"],
        ["Campaign", "EN Campaign",  "fix",                     "Phrase", "Service — not a sale"],
        ["Campaign", "EN Campaign",  "broken",                  "Phrase", "Service — not a sale"],
        ["Campaign", "EN Campaign",  "engraving only",          "Phrase", "Service only — not a purchase"],
        ["Campaign", "EN Campaign",  "used",                    "Phrase", "Pre-owned — wrong intent"],
        ["Campaign", "EN Campaign",  "second hand",             "Phrase", "Pre-owned"],
        ["Campaign", "EN Campaign",  "pre-owned",               "Phrase", "Pre-owned"],
        # FR Campaign level
        ["Campaign", "FR Campaign",  "bracelet homme",          "Phrase", "Men's"],
        ["Campaign", "FR Campaign",  "bracelet enfant",         "Phrase", "Children's — not GDM target"],
        ["Campaign", "FR Campaign",  "bracelet bébé",           "Phrase", "Children's"],
        ["Campaign", "FR Campaign",  "bracelet chevillère",     "Phrase", "Ankle bracelet — not in catalog"],
        ["Campaign", "FR Campaign",  "occasion",                "Phrase", "Pre-owned"],
        ["Campaign", "FR Campaign",  "d'occasion",              "Phrase", "Pre-owned"],
        ["Campaign", "FR Campaign",  "réparer",                 "Phrase", "Repair service"],
        ["Campaign", "FR Campaign",  "grossiste",               "Phrase", "Wholesale"],
        # Ad Group cross-negatives
        ["Ad Group", "AG2 (Jewelry Gift) → routes to AG1",   "bracelet",     "Exact", "Bracelet-specific queries go to AG1"],
        ["Ad Group", "AG1 (Bracelet Core) → routes to AG3",  "personalized", "Exact", "Custom queries go to AG3"],
        ["Ad Group", "AG1 (Bracelet Core) → routes to AG3",  "custom",       "Exact", "Custom queries go to AG3"],
        ["Ad Group", "AG1 (Bracelet Core) → routes to AG3",  "birthstone",   "Exact", "Birthstone queries go to AG3"],
        ["Ad Group", "AG4 (Tennis/Diamond) → routes to AG1", "mothers day",  "Exact", "Occasion queries go to AG1/2"],
        ["Ad Group", "AG4 (Tennis/Diamond) → routes to AG1", "gift",         "Exact", "Gift queries go to AG1/2"],
        ["Ad Group", "AG4 (Tennis/Diamond) → routes to AG1", "birthday",     "Exact", "Birthday queries go to AG1/2"],
    ]
    write_to_sheet(SHEET_ID, "Negative Keywords", headers, rows)


# ─── RSA BUILDER HELPER ───────────────────────────────────────────────────────

def build_rsa_tab(tab_name, ag_name, campaign, lp_url, angle_note, offer_note,
                  headlines, descriptions, pinning_notes, char_warnings=None):
    """
    Write a full RSA tab.
    headlines = list of (text, char_count, pin_position or '')
    descriptions = list of (text, char_count, pin_position or '')
    """
    headers = ["Type", "#", "Text", "Char Count", "Pin Position", "Notes"]
    rows = []

    # Meta rows
    rows.append(["SETUP",        "",  "Ad Group",         ag_name,     "", ""])
    rows.append(["SETUP",        "",  "Campaign",         campaign,    "", ""])
    rows.append(["SETUP",        "",  "Landing Page",     lp_url,      "", ""])
    rows.append(["SETUP",        "",  "Creative Angle",   angle_note,  "", ""])
    rows.append(["SETUP",        "",  "Offer Note",       offer_note,  "", ""])
    rows.append(["", "", "", "", "", ""])

    for i, (text, char_count, pin, note) in enumerate(headlines, 1):
        warning = ""
        if char_warnings and i in char_warnings:
            warning = char_warnings[i]
        rows.append(["HEADLINE", str(i), text, str(char_count), pin, note or warning])

    rows.append(["", "", "", "", "", ""])

    for i, (text, char_count, pin, note) in enumerate(descriptions, 1):
        rows.append(["DESCRIPTION", str(i), text, str(char_count), pin, note or ""])

    rows.append(["", "", "", "", "", ""])
    rows.append(["PINNING NOTES", "", pinning_notes, "", "", ""])

    write_to_sheet(SHEET_ID, tab_name, headers, rows)


# ─── TAB 5: RSA — AG1 MOTHER'S DAY BRACELET CORE ─────────────────────────────

def build_rsa_ag1():
    headlines = [
        # (text, char_count, pin_position, note)
        ("Mother's Day Bracelets",         22, "H1 — Pin to position 1", "Core theme — always visible"),
        ("10% Off Diamond Collection",     26, "H1 — Pin to position 1 (alternate)", "Lead offer"),
        ("Free Studs With $2,500+ Orders", 30, "",  "Offer — updated threshold"),
        ("20% Off Diamond Orders $3K+",    27, "",  "High-ticket offer"),
        ("Montreal's Jeweler Since 1982",  29, "",  "Trust signal"),
        ("Lab-Grown + Natural Diamonds",   28, "",  "Product range"),
        ("Free Shipping Across Canada",    27, "",  "Logistics"),
        ("Book a Free Consultation",       24, "",  "CTA"),
        ("The Perfect Gift for Mom",       23, "",  "Occasion angle"),
        ("Pay Monthly With Affirm",        23, "",  "Financing"),
        ("40+ Years of Craftsmanship",     25, "",  "Trust"),
        ("Designer Bracelets for Mom",     26, "",  "Product + occasion"),
        ("Shop the Bracelet Collection",   28, "",  "CTA"),
        ("Free 1ct Studs on $5,000+",      25, "",  "Top-tier offer"),
        ("In-Store and Online Pickup",     26, "",  "Convenience"),
    ]
    descriptions = [
        ("10% off our diamond collection this Mother's Day. Free studs with $2,500+ orders.", 82,
         "D1 — Pin to position 1", "Lead offer description — always show first"),
        ("GDM: Montreal's diamond manufacturer since 1982. Free studs with orders $2,500+.", 80,
         "", "Trust + offer"),
        ("Pay monthly with Affirm. Free consultation available. Ships within 14 business days.", 84,
         "", "Logistics + financing"),
        ("Not just a retailer, we're a manufacturer. Custom bracelets made to her vision.", 78,
         "", "Manufacturer differentiator"),
    ]
    pinning = (
        "H1: Rotate between 'Mother's Day Bracelets' and '10% Off Diamond Collection'. "
        "D1: Always pin 'Lead offer description' to position 1."
    )
    build_rsa_tab(
        tab_name="RSA - AG1 Bracelet Core",
        ag_name="AG1: Mother's Day Bracelet Core",
        campaign="GDM | Search | Mother's Day EN (2026)",
        lp_url="globaldiamondmontreal.com/collections/mothers-day-bracelet-collection",
        angle_note="The gift she'll wear every day — designer bracelets from GDM",
        offer_note="10% off diamonds, 20% off $3K+, free studs $2,500+. Gold EXCLUDED from all promos.",
        headlines=headlines,
        descriptions=descriptions,
        pinning_notes=pinning,
    )


# ─── TAB 6: RSA — AG2 MOTHER'S DAY JEWELRY GIFT ──────────────────────────────

def build_rsa_ag2():
    headlines = [
        ("The Perfect Gift for Mom",       23, "H1 — Pin to position 1", "Occasion angle"),
        ("Mother's Day Jewelry Sale",       25, "",  "Campaign + offer"),
        ("10% Off Diamond Collection",      26, "",  "Lead offer"),
        ("Free Studs With $2,500+ Orders",  30, "",  "Offer"),
        ("Fine Jewelry for Mother's Day",   29, "",  "Premium angle"),
        ("Montreal's Jeweler Since 1982",   29, "",  "Trust signal"),
        ("Lab-Grown + Natural Diamonds",    28, "",  "Product range"),
        ("Rings, Pendants and Bracelets",   29, "",  "Product breadth"),
        ("Free Shipping Across Canada",     27, "",  "Logistics"),
        ("The Gift She'll Wear Forever",    28, "",  "Emotional angle"),
        ("Custom Jewelry for Her",          22, "",  "Personalization angle"),
        ("Book a Free Consultation",        24, "",  "CTA"),
        ("Pay Monthly With Affirm",         23, "",  "Financing"),
        ("Shop Our Mother's Day Gifts",     27, "",  "CTA"),
        ("Gift Ideas She'll Treasure",      26, "",  "Gift intent"),
    ]
    descriptions = [
        ("Shop fine jewelry this Mother's Day. 10% off diamonds, free studs with $2,500+ orders.", 86,
         "D1 — Pin to position 1", "Lead offer"),
        ("Bracelets, rings, and pendants. GDM is Montreal's jewelry manufacturer since 1982.", 82,
         "", "Product range + trust"),
        ("Free Canada shipping. Pay monthly with Affirm. Book a free consultation today.", 78,
         "", "Logistics + CTA"),
        ("GDM designs and manufactures jewelry in Montreal. Every piece can be custom-made for her.", 89,
         "", "Manufacturer differentiator"),
    ]
    pinning = (
        "H1: Pin 'The Perfect Gift for Mom' to position 1 — broadest appeal for gift-seekers. "
        "D1: Pin lead offer description to position 1. "
        "NOTE: Earring references — hold until Doc confirms price increases on earring SKUs are live."
    )
    build_rsa_tab(
        tab_name="RSA - AG2 Jewelry Gift",
        ag_name="AG2: Mother's Day Jewelry Gift (Broader)",
        campaign="GDM | Search | Mother's Day EN (2026)",
        lp_url="globaldiamondmontreal.com/collections/mothers-day-bracelet-collection",
        angle_note="The Mother's Day gift that outlasts flowers — fine jewelry from GDM",
        offer_note="10% off diamonds, free studs $2,500+. Gold EXCLUDED. Earring copy ON HOLD — confirm with Doc before referencing earrings.",
        headlines=headlines,
        descriptions=descriptions,
        pinning_notes=pinning,
    )


# ─── TAB 7: RSA — AG3 PERSONALIZED + CUSTOM (PRIORITY 1) ────────────────────

def build_rsa_ag3():
    headlines = [
        ("Custom Designed for Her",         22, "H1 — Pin to position 1", "PRIORITY — lead with differentiator"),
        ("Personalized Bracelets Mom",       25, "",  "Matches search intent"),
        ("Birthstone Bracelets for Mom",     28, "",  "Specific intent cluster"),
        ("Custom Jewelry for Mom",           22, "",  "Matches search intent"),
        ("10% Off Diamond Collection",       26, "",  "Offer"),
        ("Free Studs With $2,500+ Orders",   30, "",  "Offer"),
        ("Mother's Day Bracelets",           22, "",  "Occasion"),
        ("Montreal's Jeweler Since 1982",    29, "",  "Trust"),
        ("Built Around Her Style",           22, "",  "Personalization angle"),
        ("Choose Her Stone and Metal",       25, "",  "Customization specifics"),
        ("Free Shipping Across Canada",      27, "",  "Logistics"),
        ("Book a Free Consultation",         24, "",  "CTA — custom design starts with consult"),
        ("Lab-Grown + Natural Diamonds",     28, "",  "Product range"),
        ("Pay Monthly With Affirm",          23, "",  "Financing"),
        ("Every Detail, Your Choice",        25, "",  "Personalization angle"),
    ]
    descriptions = [
        ("Design a custom bracelet for Mom. Choose her stone, metal, and style at GDM.", 76,
         "D1 — Pin to position 1", "Matches personalization intent — always show"),
        ("GDM is a manufacturer, not just a store. Personalized pieces made exactly to your brief.", 88,
         "", "Manufacturer differentiator — key for custom intent"),
        ("10% off our diamond collection. Free studs with $2,500+ orders. Free Canada shipping.", 84,
         "", "Offer + logistics"),
        ("Choose her birthstone and metal. Free consultation included. Ships in 14 business days.", 86,
         "", "Custom process + logistics"),
    ]
    pinning = (
        "H1: Pin 'Custom Designed for Her' to position 1 — this is the primary intent match for this ad group. "
        "D1: Pin 'Design a custom bracelet for Mom...' to position 1 — reinforces the customization promise. "
        "STRATEGIC NOTE: This is PRIORITY 1 ad group. LOW competition + high-intent = highest expected ROI. "
        "GDM's manufacturer status is the unique angle no mass retailer can match. Lead with it."
    )
    build_rsa_tab(
        tab_name="RSA - AG3 Personalized",
        ag_name="AG3: Personalized + Custom Bracelet for Mom [PRIORITY 1]",
        campaign="GDM | Search | Mother's Day EN (2026)",
        lp_url="globaldiamondmontreal.com/collections/mothers-day-bracelet-collection",
        angle_note="Custom-designed bracelets, made by GDM — Montreal's jewelry manufacturer since 1982",
        offer_note="10% off diamonds, free studs $2,500+. Gold EXCLUDED. Manufacturer angle is primary differentiator for this group.",
        headlines=headlines,
        descriptions=descriptions,
        pinning_notes=pinning,
    )


# ─── TAB 8: RSA — AG4 TENNIS + DIAMOND BRACELET ──────────────────────────────

def build_rsa_ag4():
    headlines = [
        ("Diamond Tennis Bracelets",        24, "H1 — Pin to position 1", "Core product term"),
        ("Tennis Bracelets Canada",          22, "",  "Geo qualifier — high volume"),
        ("10% Off Diamond Collection",       26, "",  "Lead offer"),
        ("Free Studs With $2,500+ Orders",   30, "",  "Offer"),
        ("20% Off Diamond Orders $3K+",      27, "",  "High-ticket offer"),
        ("Lab-Grown + Natural Diamonds",     28, "",  "Product range"),
        ("Montreal's Jeweler Since 1982",    29, "",  "Trust"),
        ("Free Shipping Across Canada",      27, "",  "Logistics"),
        ("Designer Diamond Bracelets",       25, "",  "Premium angle"),
        ("White Gold and Yellow Gold",       25, "",  "Material specifics"),
        ("Gift Her a Diamond Bracelet",      27, "",  "Gift angle"),
        ("Pay Monthly With Affirm",          23, "",  "Financing"),
        ("Book a Free Consultation",         24, "",  "CTA"),
        ("Free 1ct Studs on $5,000+",        25, "",  "Top-tier offer"),
        ("40+ Years of Craftsmanship",       25, "",  "Trust"),
    ]
    descriptions = [
        ("Shop lab-grown and natural diamond tennis bracelets. 10% off this Mother's Day at GDM.", 86,
         "D1 — Pin to position 1", "Product + occasion + offer"),
        ("Free studs with diamond orders: 0.26ct at $2,500+, 0.50ct at $3,500+, 1ct at $5,000+.", 85,
         "", "Full offer ladder — bottom-funnel buyers want details"),
        ("Montreal's jewelry manufacturer since 1982. Pay monthly with Affirm. Free Canada shipping.", 88,
         "", "Trust + logistics + financing"),
        ("Not just a retailer, a manufacturer. Custom stone and setting options available at GDM.", 86,
         "", "Manufacturer differentiator"),
    ]
    pinning = (
        "H1: Pin 'Diamond Tennis Bracelets' to position 1 — core product match. "
        "D1: Pin offer description to position 1 — bottom-funnel buyers respond to specific offer details."
    )
    build_rsa_tab(
        tab_name="RSA - AG4 Tennis Diamond",
        ag_name="AG4: Tennis + Diamond Bracelet (Product-Specific)",
        campaign="GDM | Search | Mother's Day EN (2026)",
        lp_url="globaldiamondmontreal.com/collections/mothers-day-bracelet-collection",
        angle_note="Lab-grown or natural diamond tennis bracelets — 10% off + free studs with $2,500+ purchase",
        offer_note="10% off diamonds, 20% off $3K+, free studs $2,500+. Gold EXCLUDED.",
        headlines=headlines,
        descriptions=descriptions,
        pinning_notes=pinning,
    )


# ─── TAB 9: RSA — AG5 FÊTE DES MÈRES (FR) — PRIORITY 1 ──────────────────────

def build_rsa_ag5():
    headlines = [
        ("Bracelet Fête des Mères",          23, "H1 — Pin to position 1", "Core FR occasion term"),
        ("Cadeau Maman Bijoux GDM",          23, "",  "Gift + brand"),
        ("10% de Rabais sur Diamants",        26, "",  "Lead offer — FR"),
        ("Livraison Gratuite au Canada",      28, "",  "Logistics"),
        ("Bijoutier Montréalais 1982",        26, "",  "Trust + local"),
        ("Bracelets Diamant pour Maman",      28, "",  "Product + recipient"),
        ("Studs Gratuits dès $2 500+",        26, "",  "Offer — FR format for thousands"),
        ("Bracelet Personnalisé Maman",       27, "",  "Personalization angle"),
        ("Consultation Gratuite",             21, "",  "CTA"),
        ("Diamants Naturels et Cultivés",     29, "",  "Product range"),
        ("Payer Mensuel avec Affirm",         25, "",  "Financing"),
        ("Or Blanc, Jaune et Rosé",           23, "",  "Material specifics"),
        ("Bijoux sur Mesure Montréal",        26, "",  "Custom + local"),
        ("40 Ans de Savoir-Faire",            22, "",  "Trust"),
        ("La Fête des Mères en Bijoux",       27, "",  "Occasion angle"),
    ]
    descriptions = [
        ("10% de rabais sur nos diamants ce fête des mères. Studs gratuits avec achats de $2 500+.", 87,
         "D1 — Pin to position 1", "Lead offer — FR"),
        ("GDM, fabricant montréalais de bijoux depuis 1982. Bracelets sur mesure possibles.", 80,
         "", "Trust + manufacturer angle"),
        ("Payer mensuel avec Affirm. Consultation gratuite. Expédition en 14 jours ouvrables.", 83,
         "", "Logistics + financing"),
        ("Diamants naturels et cultivés. Chaque pièce conçue par nos artisans montréalais.", 80,
         "", "Product range + craftsmanship"),
    ]
    pinning = (
        "H1: Pin 'Bracelet Fête des Mères' to position 1 — core FR occasion match. "
        "D1: Pin lead offer FR description to position 1. "
        "NOTE: Include both accented (fête des mères) and non-accented (fete des meres) keyword variants "
        "in the ad group — Keyword Planner undercounts FR volume because searches split across accent variants. "
        "PRIORITY 1 — launch this before FR competitors activate Mother's Day campaigns."
    )
    build_rsa_tab(
        tab_name="RSA - AG5 FR Fete Meres",
        ag_name="AG5: Fête des mères — Bijoux et Bracelets [PRIORITY 1]",
        campaign="GDM | Search | Mother's Day FR (2026)",
        lp_url="globaldiamondmontreal.com/collections/mothers-day-bracelet-collection",
        angle_note="Un bracelet exceptionnel pour la fête des mères — Livraison gratuite au Canada",
        offer_note="10% de rabais sur diamants, studs gratuits dès $2 500+. Or EXCLU des promotions.",
        headlines=headlines,
        descriptions=descriptions,
        pinning_notes=pinning,
    )


# ─── TAB 10: RSA — AG6 BRACELET DIAMANT + OR FR (NO PROMO) ──────────────────

def build_rsa_ag6():
    headlines = [
        ("Bracelets Diamant pour Femme",    28, "H1 — Pin to position 1", "Core FR product term — NO promo"),
        ("Bracelets en Or pour Femme",      26, "",  "Gold bracelets — NO promo"),
        ("Bijoutier Montréalais 1982",      26, "",  "Trust + local"),
        ("Bracelets Tennis Diamant",        24, "",  "Product specific"),
        ("Or Blanc, Jaune et Rosé",         23, "",  "Material specifics"),
        ("Fabricant de Bijoux Montréal",    28, "",  "Manufacturer positioning"),
        ("Livraison Gratuite au Canada",    28, "",  "Logistics"),
        ("Diamants Naturels et Cultivés",   29, "",  "Product range"),
        ("Bijoux sur Mesure Montréal",      26, "",  "Custom + local"),
        ("Consultation Gratuite",           21, "",  "CTA"),
        ("40 Ans de Savoir-Faire",          22, "",  "Trust"),
        ("Payer Mensuel avec Affirm",       25, "",  "Financing"),
        ("Or 14K, 18K et Platine",          22, "",  "Material specifics"),
        ("Collection Bijoux 2026",          22, "",  "Recency signal"),
        ("Bracelets Femme Montréal",        24, "",  "Local + product"),
    ]
    descriptions = [
        ("GDM, fabricant montréalais de bijoux en or et diamants depuis 1982. Livraison gratuite.", 86,
         "D1 — Pin to position 1", "Trust + local — NO promo reference"),
        ("Choisissez votre métal et votre pierre. Chaque bracelet créé sur mesure à Montréal.", 82,
         "", "Customization angle — NO promo reference"),
        ("Or blanc, jaune et rosé. Diamants naturels et cultivés. Consultation gratuite en boutique.", 89,
         "", "Product range — NO promo reference"),
        ("Payer mensuel avec Affirm. Expédition 14 jours ouvrables. 35 000 heures d'artisanat.", 84,
         "", "Logistics + craftsmanship — NO promo reference"),
    ]
    pinning = (
        "H1: Pin 'Bracelets Diamant pour Femme' to position 1. "
        "D1: Pin trust/local description to position 1. "
        "CRITICAL NOTE: This ad group targets gold bracelet keywords. Gold is EXCLUDED from the Mother's Day "
        "promotion. DO NOT reference: 10% off, 20% off, free studs, or any discount. "
        "Use brand, craftsmanship, and manufacturer positioning ONLY."
    )
    build_rsa_tab(
        tab_name="RSA - AG6 FR Or + Diamant",
        ag_name="AG6: Bracelet Diamant + Or Femme (FR) [NO PROMO COPY]",
        campaign="GDM | Search | Mother's Day FR (2026)",
        lp_url="globaldiamondmontreal.com/collections/mothers-day-bracelet-collection",
        angle_note="Bracelets en or et diamants — fabricant montréalais depuis 1982",
        offer_note="GOLD IS EXCLUDED FROM ALL PROMOS. Zero discount references allowed in this ad group. Brand and craftsmanship angle only.",
        headlines=headlines,
        descriptions=descriptions,
        pinning_notes=pinning,
    )


# ─── TAB 11: AD ASSETS ────────────────────────────────────────────────────────

def build_ad_assets():
    headers = ["Asset Type", "Campaign / Level", "Field", "Value", "Notes"]
    rows = [
        # ── Sitelinks ──
        ["SITELINK", "Both Campaigns", "Link Text",      "Mother's Day Collection",  "30 chars max — link text"],
        ["SITELINK", "Both Campaigns", "Description 1",  "10% off diamonds for Mom", "35 chars max"],
        ["SITELINK", "Both Campaigns", "Description 2",  "Free studs with $2,500+",  ""],
        ["SITELINK", "Both Campaigns", "Final URL",      "globaldiamondmontreal.com/collections/mothers-day-bracelet-collection", ""],
        ["", "", "", "", ""],
        ["SITELINK", "Both Campaigns", "Link Text",      "Shop Tennis Bracelets",        ""],
        ["SITELINK", "Both Campaigns", "Description 1",  "Lab-grown and natural diamonds",""],
        ["SITELINK", "Both Campaigns", "Description 2",  "Free shipping across Canada",   ""],
        ["SITELINK", "Both Campaigns", "Final URL",      "globaldiamondmontreal.com/collections/tennis-bracelets", "Confirm URL is live"],
        ["", "", "", "", ""],
        ["SITELINK", "Both Campaigns", "Link Text",      "Book a Free Consultation",   ""],
        ["SITELINK", "Both Campaigns", "Description 1",  "In-store or virtual — free",  ""],
        ["SITELINK", "Both Campaigns", "Description 2",  "Available 7 days a week",     ""],
        ["SITELINK", "Both Campaigns", "Final URL",      "globaldiamondmontreal.com/pages/book-appointment", "Confirm URL"],
        ["", "", "", "", ""],
        ["SITELINK", "Both Campaigns", "Link Text",      "Custom Bracelet Design",     ""],
        ["SITELINK", "Both Campaigns", "Description 1",  "Tell us her style and budget",""],
        ["SITELINK", "Both Campaigns", "Description 2",  "Built by a manufacturer",    ""],
        ["SITELINK", "Both Campaigns", "Final URL",      "globaldiamondmontreal.com/pages/custom-design", "Confirm URL"],
        ["", "", "", "", ""],
        ["SITELINK", "Both Campaigns", "Link Text",      "Pay Monthly with Affirm",    ""],
        ["SITELINK", "Both Campaigns", "Description 1",  "Flexible payment options",   ""],
        ["SITELINK", "Both Campaigns", "Description 2",  "No upfront payment required",""],
        ["SITELINK", "Both Campaigns", "Final URL",      "globaldiamondmontreal.com",  "Update to Affirm page URL when integration is confirmed live"],
        ["", "", "", "", ""],
        ["SITELINK", "Both Campaigns", "Link Text",      "Visit Us in Montreal",       ""],
        ["SITELINK", "Both Campaigns", "Description 1",  "Global Diamond Montreal",    ""],
        ["SITELINK", "Both Campaigns", "Description 2",  "40+ years of craftsmanship", ""],
        ["SITELINK", "Both Campaigns", "Final URL",      "globaldiamondmontreal.com/pages/contact", ""],
        ["", "", "", "", ""],
        # ── Callouts ── (max 25 chars each)
        ["CALLOUT", "Both Campaigns", "Callout 1", "Free Shipping to Canada",  "23 chars"],
        ["CALLOUT", "Both Campaigns", "Callout 2", "10% Off Diamonds",         "16 chars"],
        ["CALLOUT", "Both Campaigns", "Callout 3", "Free Studs with $2,500+",  "23 chars — diamond campaigns only"],
        ["CALLOUT", "Both Campaigns", "Callout 4", "Lab-Grown Diamonds",       "18 chars"],
        ["CALLOUT", "Both Campaigns", "Callout 5", "Made in Montreal",         "16 chars"],
        ["CALLOUT", "Both Campaigns", "Callout 6", "40+ Years of Experience",  "23 chars"],
        ["CALLOUT", "Both Campaigns", "Callout 7", "Pay Monthly with Affirm",  "23 chars"],
        ["CALLOUT", "Both Campaigns", "Callout 8", "Free Consultation",        "17 chars"],
        ["CALLOUT", "Both Campaigns", "Callout 9", "Custom Design Available",  "23 chars"],
        ["CALLOUT", "Both Campaigns", "Callout 10","Natural Diamonds",         "16 chars"],
        ["", "", "", "", ""],
        ["CALLOUT NOTE", "", "AG6 (FR gold) callouts", "Remove 'Free Studs with $2,500+' callout from AG6. Gold is excluded from promo.", ""],
        ["", "", "", "", ""],
        # ── Structured Snippets ──
        ["STRUCTURED SNIPPET", "Both Campaigns", "Header Type", "Types",          "Google header type"],
        ["STRUCTURED SNIPPET", "Both Campaigns", "Value 1",     "Tennis Bracelets",         ""],
        ["STRUCTURED SNIPPET", "Both Campaigns", "Value 2",     "Gold Bracelets",           ""],
        ["STRUCTURED SNIPPET", "Both Campaigns", "Value 3",     "Diamond Bangles",          "Confirm GDM has bangles"],
        ["STRUCTURED SNIPPET", "Both Campaigns", "Value 4",     "Custom Bracelets",         ""],
        ["STRUCTURED SNIPPET", "Both Campaigns", "Value 5",     "Birthstone Bracelets",     ""],
        ["STRUCTURED SNIPPET", "Both Campaigns", "Value 6",     "Lab-Grown Diamonds",       ""],
        ["", "", "", "", ""],
        # ── Call Extension ──
        ["CALL EXTENSION", "Both Campaigns", "Phone Number",  "CONFIRM WITH CLIENT",   "Not in client notes — request from Doc"],
        ["CALL EXTENSION", "Both Campaigns", "Call Reporting","Enabled",               "Required for CallRail attribution"],
        ["CALL EXTENSION", "Both Campaigns", "Hours",         "Business hours only",   "Avoid calls outside staffed hours"],
        ["", "", "", "", ""],
        # ── Image Assets ──
        ["IMAGE ASSET", "Both Campaigns", "Image 1 — Primary",  "Tennis bracelet on white background",      "Product shot — request from Ana K.A. (designer)"],
        ["IMAGE ASSET", "Both Campaigns", "Image 2 — Lifestyle", "Woman wearing diamond bracelet",           "Lifestyle — request from Victor / Ana"],
        ["IMAGE ASSET", "Both Campaigns", "Image 3 — Occasion",  "Mother's Day gift box with bracelet",      "Occasion context — may use Doc's product shots with boxes"],
        ["IMAGE ASSET", "Both Campaigns", "Image 4 — Brand",     "GDM store front or Montreal workshop",    "Brand trust — available from Doc's assets drive"],
        ["IMAGE ASSET", "Both Campaigns", "Image Note",          "Assets Drive: drive.google.com/drive/folders/0APdLIJr-YPr2Uk9PVA", "Request images from Ana / Victor"],
    ]
    write_to_sheet(SHEET_ID, "Ad Assets", headers, rows)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print("Building GDM Mother's Day 2026 Google Ads Campaign Sheet...")
    print(f"Sheet ID: {SHEET_ID}")
    print()

    print("Writing tab: Overview...")
    build_overview()

    print("Writing tab: Keywords - EN...")
    build_keywords_en()

    print("Writing tab: Keywords - FR...")
    build_keywords_fr()

    print("Writing tab: Negative Keywords...")
    build_negatives()

    print("Writing tab: RSA - AG1 (Bracelet Core)...")
    build_rsa_ag1()

    print("Writing tab: RSA - AG2 (Jewelry Gift)...")
    build_rsa_ag2()

    print("Writing tab: RSA - AG3 (Personalized) [PRIORITY 1]...")
    build_rsa_ag3()

    print("Writing tab: RSA - AG4 (Tennis Diamond)...")
    build_rsa_ag4()

    print("Writing tab: RSA - AG5 (FR Fete des meres) [PRIORITY 1]...")
    build_rsa_ag5()

    print("Writing tab: RSA - AG6 (FR Or + Diamant) [NO PROMO]...")
    build_rsa_ag6()

    print("Writing tab: Ad Assets...")
    build_ad_assets()

    print()
    print("Done. All 11 tabs written.")
    print(f"Sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}")


if __name__ == "__main__":
    main()
