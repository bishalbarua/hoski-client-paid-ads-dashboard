"""
GDM — Engagement Rings: PMax + Local Search Campaign Sheet Builder
Lever 3 of the three-lever strategy (gdm-three-lever-strategy-2026-04.md)
Scheduled launch: Apr 25, 2026 (Weeks 3-4)

Tabs created:
  1.  Overview              — Settings for both campaigns, budget schedule, conversion goals
  2.  PMax - Campaign       — PMax settings, listing group tree, feed filter, budget ramp
  3.  PMax - Asset Groups   — 3 asset groups x 15 headlines + 5 descriptions
  4.  PMax - Search Themes  — 25 search themes x 3 asset groups
  5.  PMax - Audience Sigs  — 5 signal types with specs
  6.  PMax - Extensions     — Sitelinks, callouts, structured snippets, promotion, call
  7.  Search - Campaign     — Campaign settings, bid strategy, geo, match type rationale
  8.  Search - AG1          — Custom Ring MTL: keywords, RSA, cross-negatives
  9.  Search - AG2          — Rings Montreal: keywords, RSA, cross-negatives
  10. Search - AG3          — Ring Styles: keywords, RSA, cross-negatives
  11. Search - AG4          — Lab-Grown: keywords, RSA, cross-negatives
  12. Search - AG5          — Manufacturer Direct: keywords, RSA, cross-negatives
  13. Search - AG6          — Canada Virtual: keywords, RSA, cross-negatives
  14. Extensions - Search   — Sitelinks, callouts, snippets, call, location
  15. Negative Keywords     — Account-level, campaign-level, ad group cross-negatives
  16. Pre-Launch QA         — Checklist: feed, Merchant Center, assets, settings, conflict check

Run:
  python3 scripts/build_engagement_rings_sheet.py

Requires:
  - sheets-credentials.json in project root (service account JSON)
  - A new Google Sheet created and shared with the service account email
  - SHEET_ID constant below set to that sheet's ID
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.sheets_writer import write_to_sheet

# ── Set this to your new Google Sheet ID before running ──────────────────────
SHEET_ID = "1IzMtHdefPms45uL-vRRTrC9T3BpaN_7BGmPHSTpKdfY"
# ─────────────────────────────────────────────────────────────────────────────


# ─── TAB 1: OVERVIEW ──────────────────────────────────────────────────────────

def build_overview():
    headers = ["Field", "PMax Campaign", "Search Campaign"]
    rows = [
        ["Campaign Name",
         "Hoski | PMax | Engagement Rings | Feed + Search",
         "Hoski | Search | Engagement Rings | Local + Virtual"],
        ["Campaign Type",         "Performance Max",                    "Search"],
        ["Goal",                  "Sales + Appointment Bookings",       "Appointment Bookings (ring consultation)"],
        ["Networks",              "Google — all inventory",             "Search only (no Display, no Search Partners)"],
        ["Bid Strategy (launch)", "Maximize Conversion Value",          "Maximize Conversions"],
        ["Bid Strategy (day 14+)","tROAS 3.5x (if 5+ conversions)",     "Target CPA $585 (after 30+ conversions)"],
        ["Daily Budget (launch)", "$23/day",                            "$43/day"],
        ["Daily Budget (day 14+)","$30/day (if ROAS >= 2.5x)",         "$43/day (hold until CPA target active)"],
        ["Monthly Allocation",    "$700/month",                         "$1,300/month"],
        ["Start Date",            "2026-04-25",                         "2026-04-25"],
        ["Locations",             "Canada — all provinces",             "Montreal 50km radius + Canada-wide (virtual)"],
        ["Languages",             "English + French",                   "English"],
        ["Ad Rotation",           "Optimized by Google",                "Optimize — prefer best performing"],
        ["Final URL Expansion",   "OFF — ring consultation page only",  "Not applicable"],
        ["Landing Page",          "go.globaldiamondmontreal.com/appointment (primary)",
                                  "go.globaldiamondmontreal.com/appointment"],
        ["UTM",                   "",                                   "utm_campaign=engagement-rings on all final URLs"],
        [""],
        ["CONVERSION GOALS", "", ""],
        ["Primary",
         "Appointment booked (ring consultation) + Offline Purchase via Zapier",
         "Appointment booked (ring consultation)"],
        ["Secondary",
         "Online purchase, Add to cart, Calls from ads",
         "Calls from ads, Online purchase"],
        ["DO NOT USE",
         "Local directions — caused 68 fake conversions in PMax Local (lesson learned)",
         ""],
        [""],
        ["BUDGET SCHEDULE", "", ""],
        ["Launch (Apr 25)",       "$23/day PMax",                       "$43/day Search"],
        ["Day 14 check",          "Upgrade to $30/day if ROAS >= 2.5x", "Hold — review CPA"],
        ["Day 30 check",          "Set tROAS 3.5x if 5+ conversions",   "Set tCPA $585 if 30+ conversions"],
        ["Total monthly (launch)","~$700 CAD",                          "~$1,300 CAD"],
        [""],
        ["LEVER CONTEXT", "", ""],
        ["Strategy doc",          "gdm-three-lever-strategy-2026-04.md", ""],
        ["Why separate from general jewelry",
         "CPL ceiling $585 vs $365 general; avg ring value $4,000-6,000 vs $2,135 blended",
         "60-90 day retargeting window vs 30 days general"],
        ["Pre-launch gate",
         "Tag engagement ring products with custom_label_1 = engagement-rings in Shopify BEFORE launching PMax",
         "No feed dependency for Search — launch immediately"],
        ["Brand exclusions",
         "global diamond montreal, globaldiamondmontreal.com, global diamond, doctor diamond, gdm jewelry, gdm montreal",
         "Not applicable (handled by brand campaign staying active)"],
    ]
    write_to_sheet(SHEET_ID, "Overview", headers, rows)


# ─── TAB 2: PMAX - CAMPAIGN ───────────────────────────────────────────────────

def build_pmax_campaign():
    headers = ["Section", "Field", "Value", "Notes"]
    rows = [
        ["CAMPAIGN SETTINGS", "Campaign name",     "Hoski | PMax | Engagement Rings | Feed + Search", ""],
        ["CAMPAIGN SETTINGS", "Type",              "Performance Max",                                  ""],
        ["CAMPAIGN SETTINGS", "Goal",              "Sales + Appointment Bookings",                     ""],
        ["CAMPAIGN SETTINGS", "Bid strategy",      "Maximize Conversion Value",                        "No tROAS for first 14 days — ring purchase frequency too low to constrain early"],
        ["CAMPAIGN SETTINGS", "tROAS after day 14","3.5x",                                             "Only if 5+ conversions; otherwise hold Max Conv Value"],
        ["CAMPAIGN SETTINGS", "Daily budget",      "$23/day launch",                                   "Increase to $30/day after 14 days if ROAS >= 2.5x"],
        ["CAMPAIGN SETTINGS", "Start date",        "2026-04-25",                                       "Weeks 3-4 per three-lever sequencing plan"],
        ["CAMPAIGN SETTINGS", "Locations",         "Canada — all provinces",                           "Includes virtual consultation reach"],
        ["CAMPAIGN SETTINGS", "Languages",         "English + French",                                 ""],
        ["CAMPAIGN SETTINGS", "Final URL expansion","OFF",                                              "Ring consultation page only — no auto-expansion"],
        [""],
        ["BRAND EXCLUSIONS", "Term 1", "global diamond montreal",    ""],
        ["BRAND EXCLUSIONS", "Term 2", "globaldiamondmontreal.com",  ""],
        ["BRAND EXCLUSIONS", "Term 3", "global diamond",             ""],
        ["BRAND EXCLUSIONS", "Term 4", "doctor diamond",             "GDM brand nickname"],
        ["BRAND EXCLUSIONS", "Term 5", "gdm jewelry",                ""],
        ["BRAND EXCLUSIONS", "Term 6", "gdm montreal",               ""],
        [""],
        ["FEED FILTER",  "Custom Label used",   "custom_label_1",            "custom_label_0 is in use by Mother's Day campaign"],
        ["FEED FILTER",  "Filter value",        "engagement-rings",          "Must be tagged in Shopify before PMax launches"],
        ["FEED FILTER",  "Action on tagged",    "INCLUDE",                   ""],
        ["FEED FILTER",  "Action on untagged",  "EXCLUDE (Everything else)", "Critical — prevents Mother's Day products entering this campaign"],
        [""],
        ["LISTING GROUP", "Level 1",     "All Products",                                              ""],
        ["LISTING GROUP", "Level 2 — IN","Custom Label 1 = engagement-rings [INCLUDE]",               ""],
        ["LISTING GROUP", "Level 3a",    "  Product Type = Engagement Rings — Solitaire",             "Sub-segment"],
        ["LISTING GROUP", "Level 3b",    "  Product Type = Engagement Rings — Halo",                  "Sub-segment"],
        ["LISTING GROUP", "Level 3c",    "  Product Type = Engagement Rings — Custom",                "Sub-segment"],
        ["LISTING GROUP", "Level 3d",    "  Product Type = Engagement Rings — Lab-Grown",             "Sub-segment"],
        ["LISTING GROUP", "Level 2 — EX","Everything else [EXCLUDE]",                                 "Hard exclude — do not let other jewelry types enter"],
        [""],
        ["CONVERSION GOALS", "Primary 1",   "Appointment booked (ring consultation)",     "Tag from GHL via Zapier or direct webhook"],
        ["CONVERSION GOALS", "Primary 2",   "Offline Purchase via Zapier",                "CRM-closed ring sales uploaded back to Google"],
        ["CONVERSION GOALS", "Secondary 1", "Online purchase",                            ""],
        ["CONVERSION GOALS", "Secondary 2", "Add to cart",                                ""],
        ["CONVERSION GOALS", "Secondary 3", "Calls from ads",                             ""],
        ["CONVERSION GOALS", "DO NOT ADD",  "Local directions",                           "Caused 68 fake conversions in PMax Local — never add to ring campaigns"],
        [""],
        ["BUDGET RAMP", "Day 1-14",   "$23/day — Maximize Conversion Value (unconstrained)", "Learning period — no tROAS"],
        ["BUDGET RAMP", "Day 14 check","Review: impressions, clicks, asset strength, any conversions", ""],
        ["BUDGET RAMP", "Day 14 action","If ROAS >= 2.5x: increase to $30/day",           "If ROAS < 2.5x: hold at $23/day for another 14 days"],
        ["BUDGET RAMP", "Day 30 check","Review: conversion count",                         ""],
        ["BUDGET RAMP", "Day 30 action","If 5+ conversions: set tROAS 3.5x",              "If fewer than 5: hold Max Conv Value — tROAS needs data"],
    ]
    write_to_sheet(SHEET_ID, "PMax - Campaign", headers, rows)


# ─── TAB 3: PMAX - ASSET GROUPS ───────────────────────────────────────────────

def build_pmax_asset_groups():
    headers = ["Asset Group", "Type", "#", "Text", "Char Count", "Notes"]
    rows = []

    # ── AG1: Solitaire + Classic ──────────────────────────────────────────────
    rows.append(["AG1: Solitaire + Classic", "SETUP", "", "Final URL",
                 "https://globaldiamondmontreal.com/collections/engagement-rings", "Confirm URL is live"])
    rows.append(["AG1: Solitaire + Classic", "SETUP", "", "Creative angle",
                 "Classic design, manufacturer since 1982, no markup, free consultation", ""])
    rows.append(["", "", "", "", "", ""])

    ag1_headlines = [
        ("Engagement Rings Montreal",            22),
        ("Manufacturer Since 1982 — No Markup",  30),
        ("Solitaire Rings — Global Diamond",      28),
        ("Diamonds From 12 Countries",            23),
        ("Free Ring Consultation Included",       30),
        ("Classic Solitaire Engagement Rings",    30),
        ("Oval, Cushion, Round, Princess Cut",    30),
        ("Buy From the Manufacturer — Save More", 33),
        ("Same Quality as Birks — Direct Price",  32),
        ("40+ Years of Ring Expertise",           26),
        ("Halo and Solitaire Ring Specialist",    32),
        ("Montreal Ring Manufacturer Since 1982", 34),
        ("Book a Free Ring Consultation Today",   34),
        ("Natural or Lab-Grown — You Choose",     30),
        ("Engagement Rings — Manufacturer Price", 35),
    ]
    for i, (text, chars) in enumerate(ag1_headlines, 1):
        rows.append(["AG1: Solitaire + Classic", "HEADLINE", str(i), text, str(chars), ""])

    rows.append(["", "", "", "", "", ""])
    ag1_descs = [
        ("Global Diamond Montreal — engagement ring manufacturer since 1982. Diamonds from 12 countries. No retail markup. Book a free consultation in-store or virtual.", 155),
        ("Solitaire, halo, three-stone — every classic style at manufacturer pricing. Choose natural or lab-grown. Free consultation to find the perfect ring.", 143),
        ("Buy direct from the manufacturer. Same diamond quality as Birks, at the price a manufacturer charges. Book your free ring consultation today.", 138),
        ("40+ years of Montreal craftsmanship. Oval, cushion, round, princess cut — any shape, any setting. Manufacturer pricing means your budget goes further.", 150),
        ("Consultation-first approach: walk in with an idea, leave with a plan and a price. No pressure, just expertise. In-person or virtual across Canada.", 147),
    ]
    for i, (text, chars) in enumerate(ag1_descs, 1):
        rows.append(["AG1: Solitaire + Classic", "DESCRIPTION", str(i), text, str(chars), "90 char limit in Google Ads — trim to fit"])

    rows.append(["", "", "", "", "", ""])

    # ── AG2: Custom Design ────────────────────────────────────────────────────
    rows.append(["AG2: Custom Design", "SETUP", "", "Final URL",
                 "https://go.globaldiamondmontreal.com/appointment", "Dedicated ring consultation landing page"])
    rows.append(["AG2: Custom Design", "SETUP", "", "Creative angle",
                 "Custom design process, any shape/cut, global sourcing, free design consultation", ""])
    rows.append(["", "", "", "", "", ""])

    ag2_headlines = [
        ("Custom Engagement Rings Montreal",       27),
        ("Design Your Ring — Free Consultation",   34),
        ("Any Shape, Any Cut — 100% Custom",        30),
        ("Montreal Ring Designer Since 1982",       30),
        ("Bespoke Rings — Manufacturer Pricing",    34),
        ("Global Diamond — Custom Ring Atelier",    33),
        ("Sourced From 12 Countries Worldwide",     30),
        ("No Retail Markup on Custom Rings",        28),
        ("Free Design Consultation Included",       30),
        ("40+ Years of Custom Ring Expertise",      32),
        ("Custom Rings Starting at $2,000",         28),
        ("Design It. We Build It. You Propose.",    33),
        ("Meet Our Diamond Expert — Book Now",      32),
        ("Personalized Ring — Your Vision Built",   33),
        ("In-Person or Virtual Design Session",     30),
    ]
    for i, (text, chars) in enumerate(ag2_headlines, 1):
        rows.append(["AG2: Custom Design", "HEADLINE", str(i), text, str(chars), ""])

    rows.append(["", "", "", "", "", ""])
    ag2_descs = [
        ("Custom engagement rings designed around you. Global Diamond Montreal — manufacturer since 1982. Free design consultation in-store or virtual across Canada.", 155),
        ("We are a manufacturer, not a retailer. No markup, more diamond for your budget, and a ring built exactly the way you want it. Book a free design consultation.", 157),
        ("Any shape, any cut, any setting. We source diamonds from 12 countries — more options than any local jeweller. Free consultation to design your perfect ring.", 152),
        ("40+ years of custom ring craftsmanship. Choose your diamond, your setting, your metal. Manufacturer pricing means the design of your dreams at a real price.", 154),
        ("Not sure where to start? Book a free consultation. We'll guide you through every option — shape, stone, setting, metal — and price it transparently.", 145),
    ]
    for i, (text, chars) in enumerate(ag2_descs, 1):
        rows.append(["AG2: Custom Design", "DESCRIPTION", str(i), text, str(chars), "90 char limit — trim to fit"])

    rows.append(["", "", "", "", "", ""])

    # ── AG3: Lab-Grown ────────────────────────────────────────────────────────
    rows.append(["AG3: Lab-Grown", "SETUP", "", "Final URL",
                 "https://globaldiamondmontreal.com/collections/lab-grown-engagement-rings", "Confirm URL is live"])
    rows.append(["AG3: Lab-Grown", "SETUP", "", "Creative angle",
                 "Lead with choice + value (NOT ethics — Brilliant Earth owns that angle)", ""])
    rows.append(["", "", "", "", "", ""])

    ag3_headlines = [
        ("Lab-Grown Engagement Rings Montreal",    31),
        ("Natural or Lab-Grown — Your Call",        27),
        ("Lab Diamond Rings — Manufacturer Price",  33),
        ("IGI Certified Lab Diamonds Montreal",     30),
        ("D Color VS1 Lab Diamonds — Certified",    30),
        ("Same Sparkle. Manufacturer Pricing.",     29),
        ("CVD + HPHT Diamonds Available",           26),
        ("Global Diamond — Lab Diamond Specialist", 35),
        ("Lab-Grown or Natural — Free Consult",     30),
        ("Oval, Cushion, Round Lab Diamonds",       30),
        ("Lab Diamond Ring From $1,800 Montreal",   33),
        ("Not Just Ethics — Better Value Too",      29),
        ("See Both Lab and Natural Side by Side",   32),
        ("Montreal Manufacturer — Lab Expert",      30),
        ("Book Lab Diamond Consultation Today",     32),
    ]
    for i, (text, chars) in enumerate(ag3_headlines, 1):
        rows.append(["AG3: Lab-Grown", "HEADLINE", str(i), text, str(chars), ""])

    rows.append(["", "", "", "", "", ""])
    ag3_descs = [
        ("Lab-grown or natural — your call. Global Diamond Montreal offers both, with manufacturer pricing on either. IGI certified. Free consultation in Montreal or virtual.", 163),
        ("Lab-grown diamonds: same hardness, same sparkle, same certification. Different price point. We source from 12 countries — more options than most local jewellers.", 160),
        ("Looking for a lab-grown engagement ring? Book a free consultation at Global Diamond Montreal. See D/VS certified lab diamonds side by side with natural stones.", 157),
        ("Montreal manufacturer since 1982 — now with a full lab-grown diamond selection. Your ring, your choice, manufacturer pricing. In-store or virtual consultation.", 156),
        ("CVD, HPHT, IGI certified. Oval, cushion, round — any shape in lab-grown. Same setting options as natural. Manufacturer pricing. Book your free consultation.", 152),
    ]
    for i, (text, chars) in enumerate(ag3_descs, 1):
        rows.append(["AG3: Lab-Grown", "DESCRIPTION", str(i), text, str(chars), "90 char limit — trim to fit"])

    write_to_sheet(SHEET_ID, "PMax - Asset Groups", headers, rows)


# ─── TAB 4: PMAX - SEARCH THEMES ─────────────────────────────────────────────

def build_pmax_search_themes():
    headers = ["Asset Group", "#", "Search Theme"]
    rows = []

    ag1_themes = [
        "engagement rings montreal",
        "diamond engagement ring montreal",
        "solitaire engagement ring montreal",
        "engagement ring boutique montreal",
        "best engagement ring montreal",
        "oval engagement ring montreal",
        "halo engagement ring montreal",
        "cushion cut engagement ring montreal",
        "round diamond engagement ring montreal",
        "engagement ring store montreal",
        "diamond ring montreal",
        "buy engagement ring montreal",
        "three stone engagement ring montreal",
        "engagement ring manufacturer montreal",
        "engagement ring consultation montreal",
        "propose ring montreal",
        "engagement ring from manufacturer",
        "where to buy engagement ring montreal",
        "engagement ring jeweller montreal",
        "diamond ring designer montreal",
        "fine jewelry engagement ring montreal",
        "engagement ring canada",
        "diamond engagement ring canada",
        "best engagement ring canada",
        "engagement ring shopping montreal",
    ]
    for i, theme in enumerate(ag1_themes, 1):
        rows.append(["AG1: Solitaire + Classic", str(i), theme])

    rows.append(["", "", ""])

    ag2_themes = [
        "custom engagement ring montreal",
        "custom diamond ring montreal",
        "bespoke engagement ring montreal",
        "design your own engagement ring montreal",
        "engagement ring designer montreal",
        "custom made engagement ring montreal",
        "engagement ring atelier montreal",
        "custom ring design montreal",
        "personalized engagement ring montreal",
        "custom diamond ring canada",
        "custom engagement ring canada",
        "design engagement ring online canada",
        "virtual engagement ring consultation",
        "engagement ring consultation montreal",
        "custom engagement ring manufacturer",
        "engagement ring workshop montreal",
        "custom proposal ring montreal",
        "handcrafted engagement ring montreal",
        "custom bridal ring montreal",
        "bespoke ring canada",
        "custom made diamond ring montreal",
        "engagement ring from manufacturer montreal",
        "design custom engagement ring",
        "make my own engagement ring montreal",
        "custom ring montreal",
    ]
    for i, theme in enumerate(ag2_themes, 1):
        rows.append(["AG2: Custom Design", str(i), theme])

    rows.append(["", "", ""])

    ag3_themes = [
        "lab grown engagement ring montreal",
        "lab diamond engagement ring montreal",
        "lab created engagement ring montreal",
        "lab grown diamond ring montreal",
        "sustainable engagement ring montreal",
        "lab grown engagement ring canada",
        "lab diamond ring canada",
        "lab grown diamond ring canada",
        "lab created diamond engagement ring",
        "ethical engagement ring montreal",
        "lab grown solitaire ring montreal",
        "lab grown oval ring montreal",
        "lab grown cushion ring montreal",
        "lab grown halo ring montreal",
        "lab grown diamond jewelry montreal",
        "CVD diamond engagement ring montreal",
        "HPHT diamond ring montreal",
        "lab grown diamond vs natural montreal",
        "affordable engagement ring montreal",
        "lab grown diamond certified montreal",
        "IGI certified lab diamond ring",
        "lab grown engagement ring consultation",
        "lab grown ring custom montreal",
        "buy lab diamond ring montreal",
        "lab grown diamond manufacturer montreal",
    ]
    for i, theme in enumerate(ag3_themes, 1):
        rows.append(["AG3: Lab-Grown", str(i), theme])

    write_to_sheet(SHEET_ID, "PMax - Search Themes", headers, rows)


# ─── TAB 5: PMAX - AUDIENCE SIGNALS ──────────────────────────────────────────

def build_pmax_audience_signals():
    headers = ["Signal Type", "Signal Name / Description", "Apply To", "Notes"]
    rows = [
        ["CUSTOMER MATCH",
         "GHL contact list — past ring consultation inquiries",
         "All 3 asset groups",
         "Export from GHL: contacts tagged 'ring consultation' or 'engagement'. Upload as Customer Match."],
        ["CUSTOMER MATCH",
         "Past purchasers (Shopify — order value $2,000+)",
         "All 3 asset groups",
         "High-value past buyers are the best signal for finding ring-intent new users via similar audiences."],
        ["GOOGLE AUDIENCES",
         "In-market: Engagement Rings",
         "AG1 (Solitaire), AG2 (Custom)",
         "Google standard in-market segment. Strong intent signal."],
        ["GOOGLE AUDIENCES",
         "In-market: Jewelry (Fine Jewelry)",
         "All 3 asset groups",
         "Broader coverage — pair with in-market Engagement Rings for layered signal."],
        ["GOOGLE AUDIENCES",
         "Life event: Recently engaged",
         "All 3 asset groups",
         "Target people who have signaled engagement life event in Google properties."],
        ["GOOGLE AUDIENCES",
         "In-market: Wedding Planning",
         "AG1 (Solitaire), AG2 (Custom)",
         "Broader net — ring purchase precedes wedding planning but overlap is high."],
        ["CUSTOM INTENT",
         "Searched for: engagement ring montreal, custom ring montreal, diamond ring manufacturer",
         "AG2 (Custom)",
         "Build custom intent audience from seed URLs: globaldiamondmontreal.com, ecksand.com, flamme-en-rose.com"],
        ["CUSTOM INTENT",
         "Searched for: lab grown engagement ring, lab diamond ring, IGI certified diamond",
         "AG3 (Lab-Grown)",
         "Captures lab-grown research phase users before they convert."],
        ["REMARKETING",
         "GDM website visitors — engagement ring collection pages (90-day window)",
         "All 3 asset groups",
         "Tag pages: /collections/engagement-rings, /collections/lab-grown-engagement-rings. 90-day window per service track default."],
        ["REMARKETING",
         "go.globaldiamondmontreal.com/appointment — page visitors who did NOT convert",
         "All 3 asset groups",
         "Landing page abandoners: highest intent, did not book. Priority re-engagement."],
    ]
    write_to_sheet(SHEET_ID, "PMax - Audience Sigs", headers, rows)


# ─── TAB 6: PMAX - EXTENSIONS ─────────────────────────────────────────────────

def build_pmax_extensions():
    headers = ["Extension Type", "Field", "Value", "Notes"]
    rows = [
        ["SITELINK 1", "Link Text",     "Custom Engagement Rings",                         "30 char max"],
        ["SITELINK 1", "Description 1", "Design any ring, any style",                      "35 char max"],
        ["SITELINK 1", "Description 2", "Free consultation included",                      ""],
        ["SITELINK 1", "Final URL",     "globaldiamondmontreal.com/pages/appointment-1",   "Confirm URL"],
        [""],
        ["SITELINK 2", "Link Text",     "Book a Consultation",                             ""],
        ["SITELINK 2", "Description 1", "In-person or virtual",                            ""],
        ["SITELINK 2", "Description 2", "Montreal manufacturer since 1982",                ""],
        ["SITELINK 2", "Final URL",     "go.globaldiamondmontreal.com/appointment",        ""],
        [""],
        ["SITELINK 3", "Link Text",     "Lab-Grown Diamonds",                              ""],
        ["SITELINK 3", "Description 1", "Natural or lab-grown — your call",               ""],
        ["SITELINK 3", "Description 2", "IGI certified, D/VS quality",                    ""],
        ["SITELINK 3", "Final URL",     "globaldiamondmontreal.com/collections/lab-grown-engagement-rings", "Confirm URL"],
        [""],
        ["SITELINK 4", "Link Text",     "View Ring Collection",                            ""],
        ["SITELINK 4", "Description 1", "Solitaire, halo, three-stone, custom",            ""],
        ["SITELINK 4", "Description 2", "Manufacturer pricing on every style",             ""],
        ["SITELINK 4", "Final URL",     "globaldiamondmontreal.com/collections/engagement-rings", ""],
        [""],
        ["SITELINK 5", "Link Text",     "Free Diamond Gift Offer",                         ""],
        ["SITELINK 5", "Description 1", "Free 0.26ct studs with $2,500+",                 ""],
        ["SITELINK 5", "Description 2", "Free 1.00ct studs with $5,000+",                 ""],
        ["SITELINK 5", "Final URL",     "globaldiamondmontreal.com",                       "Update to offer page if available"],
        [""],
        ["SITELINK 6", "Link Text",     "Virtual Consultation",                            ""],
        ["SITELINK 6", "Description 1", "Design your ring from anywhere",                  ""],
        ["SITELINK 6", "Description 2", "Ships across Canada",                             ""],
        ["SITELINK 6", "Final URL",     "go.globaldiamondmontreal.com/appointment",        ""],
        [""],
        ["CALLOUT 1",  "Text", "Free Design Consultation",       "25 char max — 24 chars"],
        ["CALLOUT 2",  "Text", "Manufacturer Since 1982",         "23 chars"],
        ["CALLOUT 3",  "Text", "No Retail Markup",               "16 chars"],
        ["CALLOUT 4",  "Text", "Diamonds From 12 Countries",     "25 chars"],
        ["CALLOUT 5",  "Text", "Natural + Lab-Grown Available",  "29 chars — trim if needed"],
        ["CALLOUT 6",  "Text", "In-Person or Virtual Consult",   "28 chars"],
        ["CALLOUT 7",  "Text", "Ships Across Canada",            "19 chars"],
        ["CALLOUT 8",  "Text", "40+ Years of Montreal Craft",    "25 chars"],
        [""],
        ["STRUCTURED SNIPPET", "Header type", "Styles",            "Use Google 'Types' or 'Styles' header"],
        ["STRUCTURED SNIPPET", "Value 1",     "Solitaire",         ""],
        ["STRUCTURED SNIPPET", "Value 2",     "Halo",              ""],
        ["STRUCTURED SNIPPET", "Value 3",     "Three-Stone",       ""],
        ["STRUCTURED SNIPPET", "Value 4",     "Cushion Cut",       ""],
        ["STRUCTURED SNIPPET", "Value 5",     "Oval",              ""],
        ["STRUCTURED SNIPPET", "Value 6",     "Custom Design",     ""],
        ["STRUCTURED SNIPPET", "Value 7",     "Pave",              ""],
        ["STRUCTURED SNIPPET", "Value 8",     "Vintage Inspired",  ""],
        [""],
        ["CALL EXTENSION", "Phone Number", "CONFIRM WITH DOC", "Not in client notes — request GDM main line"],
        ["CALL EXTENSION", "Schedule",     "Business hours Monday-Saturday", ""],
        ["CALL EXTENSION", "Call Reporting","Enabled",                        "Required for CallRail attribution"],
        [""],
        ["PROMOTION EXTENSION", "Occasion",    "None (evergreen) or Custom",       ""],
        ["PROMOTION EXTENSION", "Promotion",   "Free 0.26ct studs with $2,500+",   "Confirm diamond gift offer still active before adding"],
        ["PROMOTION EXTENSION", "Min purchase","$2,500 CAD",                        ""],
    ]
    write_to_sheet(SHEET_ID, "PMax - Extensions", headers, rows)


# ─── TAB 7: SEARCH - CAMPAIGN ─────────────────────────────────────────────────

def build_search_campaign():
    headers = ["Field", "Value", "Notes"]
    rows = [
        ["Campaign name",        "Hoski | Search | Engagement Rings | Local + Virtual", ""],
        ["Campaign type",        "Search",                                               ""],
        ["Goal",                 "Appointment Bookings (ring consultation)",             "Primary conversion event"],
        ["Networks",             "Search only",                                          "No Display, no Search Partners — pure Search intent"],
        ["Bid strategy (launch)","Maximize Conversions",                                 "No tCPA for first 30 conversions — need data before constraining"],
        ["Bid strategy (day 30+)","Target CPA $585",                                    "Only activate if 30+ conversions in 30-day window"],
        ["Daily budget",         "$43/day",                                              "$1,300/month allocation"],
        ["Start date",           "2026-04-25",                                           "Can launch before PMax — no feed dependency"],
        [""],
        ["GEO TARGETING",        "",                                                     ""],
        ["Location 1",           "Montreal — 50km radius",                               "In-store consultation zone"],
        ["Location 2",           "Canada-wide",                                          "Virtual consultation — opens national revenue channel"],
        ["Languages",            "English",                                              "French-speaking searchers handled by PMax (FR)"],
        [""],
        ["MATCH TYPE STRATEGY",  "",                                                     ""],
        ["Launch strategy",      "Exact + Phrase only",                                  "New campaign, zero conversion history — no Broad"],
        ["Rationale",            "Broad requires Smart Bidding + conversion data. This campaign has neither at launch.", ""],
        ["30-day review",        "Evaluate search terms. Promote converting phrase terms to Exact. Consider selective Broad after 30 conversions.", ""],
        [""],
        ["Ad rotation",          "Optimize — prefer best performing",                   ""],
        ["Landing page",         "https://go.globaldiamondmontreal.com/appointment",    "All 6 ad groups route to ring consultation landing page"],
        ["UTM tracking",         "utm_campaign=engagement-rings",                       "Required on ALL final URLs for GHL ring consultation tagging"],
        [""],
        ["PRIMARY CONVERSION",   "Appointment booked (ring consultation)",              "This is the only action that matters for campaign optimization"],
        ["SECONDARY CONVERSION", "Calls from ads",                                      ""],
        ["SECONDARY CONVERSION", "Online purchase",                                     ""],
        [""],
        ["AD GROUP PRIORITY",    "",                                                     ""],
        ["Priority 1",           "AG1: Custom Engagement Ring Montreal",                "Highest intent, lowest competition, GDM's strongest differentiator"],
        ["Priority 2",           "AG2: Engagement Rings Montreal",                      "High volume, more competition — needs sharp creative"],
        ["Priority 3",           "AG4: Lab-Grown",                                      "Specific intent — route all lab-grown traffic here"],
        ["Priority 4",           "AG3: Ring Styles",                                    "Shape/style modifiers — bottom funnel"],
        ["Priority 5",           "AG5: Manufacturer Direct",                            "Low competition, very high intent — savvy buyer"],
        ["Priority 6",           "AG6: Canada Virtual",                                 "National reach via virtual consultation"],
    ]
    write_to_sheet(SHEET_ID, "Search - Campaign", headers, rows)


# ─── RSA HELPER ───────────────────────────────────────────────────────────────

def build_search_ag_tab(tab_name, ag_name, priority, theme, lp_url,
                        keywords, headlines, descriptions, cross_negatives):
    headers = ["Section", "Type", "#", "Content", "Match Type / Char Count", "Notes"]
    rows = []

    rows.append(["SETUP", "", "", "Ad Group",    ag_name,   ""])
    rows.append(["SETUP", "", "", "Priority",    priority,  ""])
    rows.append(["SETUP", "", "", "Theme",       theme,     ""])
    rows.append(["SETUP", "", "", "Landing Page",lp_url,    ""])
    rows.append(["", "", "", "", "", ""])

    rows.append(["KEYWORDS", "", "", "Keyword", "Match Type", "Intent"])
    for kw, match_type, intent in keywords:
        rows.append(["KEYWORDS", "", "", kw, match_type, intent])

    rows.append(["", "", "", "", "", ""])
    rows.append(["RSA", "HEADLINE", "", "Text", "Char Count", ""])
    for i, (text, chars) in enumerate(headlines, 1):
        rows.append(["RSA", "HEADLINE", str(i), text, str(chars), ""])

    rows.append(["", "", "", "", "", ""])
    rows.append(["RSA", "DESCRIPTION", "", "Text", "Char Count", ""])
    for i, (text, chars) in enumerate(descriptions, 1):
        rows.append(["RSA", "DESCRIPTION", str(i), text, str(chars), "90 char limit"])

    rows.append(["", "", "", "", "", ""])
    if cross_negatives:
        rows.append(["CROSS-NEGATIVES", "", "", "Negative Keyword", "Match Type", "Reason"])
        for neg, match, reason in cross_negatives:
            rows.append(["CROSS-NEGATIVES", "", "", neg, match, reason])
    else:
        rows.append(["CROSS-NEGATIVES", "", "", "None required", "", "This ad group is specific enough — no cross-negatives needed"])

    write_to_sheet(SHEET_ID, tab_name, headers, rows)


# ─── TAB 8: SEARCH - AG1: CUSTOM RING MTL ────────────────────────────────────

def build_search_ag1():
    keywords = [
        ("[custom engagement ring montreal]",        "Exact",  "Transactional"),
        ('"custom engagement ring montreal"',         "Phrase", "Transactional"),
        ("[custom diamond ring montreal]",            "Exact",  "Transactional"),
        ('"custom diamond engagement ring montreal"', "Phrase", "Transactional"),
        ("[bespoke engagement ring montreal]",        "Exact",  "Transactional"),
        ('"bespoke engagement ring montreal"',        "Phrase", "Transactional"),
        ("[engagement ring designer montreal]",       "Exact",  "Commercial"),
        ('"engagement ring designer montreal"',       "Phrase", "Commercial"),
        ("[custom made engagement ring montreal]",    "Exact",  "Transactional"),
        ('"design your own engagement ring montreal"',"Phrase", "Transactional"),
        ("[engagement ring atelier montreal]",        "Exact",  "Transactional — very low competition"),
        ("[custom engagement ring canada]",           "Exact",  "Transactional — virtual consult"),
    ]
    headlines = [
        ("Custom Engagement Rings Montreal",          27),
        ("Designed Around You — No Compromise",       30),
        ("Manufacturer Since 1982 — No Markup",       30),
        ("Global Diamond — Montreal Atelier",         27),
        ("Sourced From 12 Countries",                 21),
        ("Free Design Consultation Included",         30),
        ("Meet Our Diamond Expert",                   21),
        ("Any Shape, Any Cut — 100% Custom",          28),
        ("Lab-Grown or Natural — Your Choice",        30),
        ("40+ Years of Custom Ring Expertise",        32),
        ("Book Your Free Consultation Today",         31),
        ("Design the Perfect Proposal Ring",          30),
        ("Same Quality as Birks — Manufacturer Price",40),
        ("Custom Rings Starting at $2,000",           26),
        ("No Retail Markup — Direct From Workshop",   35),
    ]
    descriptions = [
        ("Global Diamond Montreal has designed custom engagement rings since 1982. Diamonds from 12 countries. Book a free consultation with our designer in person or virtual.", 163),
        ("We are a manufacturer, not a retailer. No markup, more diamond for your budget, and a ring built exactly the way you want it. See it before you buy.", 151),
        ("Book a free ring consultation. Montreal's most experienced engagement ring manufacturer. In-person at our studio or virtual. No pressure, just expertise.", 153),
        ("Choose your diamond shape, setting style, and metal. We'll build it. 40+ years of craftsmanship. Manufacturer pricing means your budget goes further.", 149),
    ]
    cross_negatives = [
        ("lab grown",  "Exact", "Route lab-grown queries to AG4"),
        ("lab diamond","Exact", "Route lab-grown queries to AG4"),
    ]
    build_search_ag_tab(
        tab_name="Search - AG1",
        ag_name="AG1: Custom Engagement Ring Montreal",
        priority="Priority 1 — build first",
        theme="Buyer wants a custom-designed ring from a manufacturer in Montreal. Highest intent, lowest competition, GDM's strongest angle.",
        lp_url="https://go.globaldiamondmontreal.com/appointment?utm_campaign=engagement-rings",
        keywords=keywords,
        headlines=headlines,
        descriptions=descriptions,
        cross_negatives=cross_negatives,
    )


# ─── TAB 9: SEARCH - AG2: RINGS MONTREAL ─────────────────────────────────────

def build_search_ag2():
    keywords = [
        ("[engagement rings montreal]",              "Exact",  "Commercial"),
        ('"engagement rings montreal"',              "Phrase", "Commercial"),
        ("[engagement ring montreal]",               "Exact",  "Commercial"),
        ('"diamond engagement ring montreal"',       "Phrase", "Commercial"),
        ("[buy engagement ring montreal]",           "Exact",  "Transactional"),
        ('"where to buy engagement ring montreal"',  "Phrase", "Commercial"),
        ("[best engagement rings montreal]",         "Exact",  "Commercial Investigation"),
        ('"engagement ring boutique montreal"',      "Phrase", "Commercial"),
        ("[engagement ring store montreal]",         "Exact",  "Commercial"),
        ('"engagement ring jeweller montreal"',      "Phrase", "Commercial"),
    ]
    headlines = [
        ("Engagement Rings — Montreal Manufacturer",  35),
        ("Global Diamond Montreal Since 1982",         27),
        ("No Retail Markup — Manufacturer Price",      30),
        ("Diamonds From 12 Countries",                 21),
        ("Free Consultation — No Obligation",          28),
        ("40+ Years. Thousands of Rings Made.",         30),
        ("Solitaire, Halo, Three-Stone, Custom",        29),
        ("Same Quality as Birks — Direct Price",        28),
        ("Lab-Grown or Natural — You Decide",           27),
        ("Montreal's Most Experienced Ring Maker",      35),
        ("Book Your Ring Consultation Today",           29),
        ("In-Person or Virtual Consultation",           29),
        ("Oval, Cushion, Round, Princess Cut",          29),
        ("Free Diamond Gift With Purchase",             27),
        ("Design It. We Build It. You Propose.",        31),
    ]
    descriptions = [
        ("Global Diamond Montreal — engagement ring manufacturer since 1982. Diamonds sourced from 12 countries. No retail markup. Free consultation in-store or virtual.", 160),
        ("Six Montreal jewellers say made locally. Only GDM also sources from 12 countries. That means more diamond options at manufacturer pricing. Book a free consult.", 158),
        ("Solitaire to custom halo — every ring style, any diamond shape. Natural or lab-grown. Built in Montreal by a manufacturer, not a retailer. See the difference.", 156),
        ("The engagement ring you want. Manufacturer pricing you'll appreciate. Free consultation — walk in with an idea, leave with a plan. Open in Montreal, available virtually.", 168),
    ]
    cross_negatives = [
        ("custom",     "Exact", "Route custom queries to AG1"),
        ("lab grown",  "Exact", "Route lab-grown to AG4"),
        ("lab diamond","Exact", "Route lab-diamond to AG4"),
    ]
    build_search_ag_tab(
        tab_name="Search - AG2",
        ag_name="AG2: Engagement Rings Montreal",
        priority="Priority 2 — high volume, more competition",
        theme="General engagement ring seeker in Montreal. Ecksand, St-Onge, Flamme en Rose all bid here — needs sharp creative to stand out.",
        lp_url="https://go.globaldiamondmontreal.com/appointment?utm_campaign=engagement-rings",
        keywords=keywords,
        headlines=headlines,
        descriptions=descriptions,
        cross_negatives=cross_negatives,
    )


# ─── TAB 10: SEARCH - AG3: RING STYLES ───────────────────────────────────────

def build_search_ag3():
    keywords = [
        ("[solitaire engagement ring montreal]",      "Exact",  "Transactional"),
        ('"halo engagement ring montreal"',           "Phrase", "Transactional"),
        ("[oval engagement ring montreal]",           "Exact",  "Transactional"),
        ('"cushion cut engagement ring montreal"',    "Phrase", "Transactional"),
        ("[round diamond engagement ring montreal]",  "Exact",  "Transactional"),
        ('"three stone engagement ring montreal"',    "Phrase", "Transactional"),
        ("[pave engagement ring montreal]",           "Exact",  "Transactional"),
        ('"oval diamond ring montreal"',              "Phrase", "Transactional"),
        ("[cushion diamond ring montreal]",           "Exact",  "Transactional"),
        ('"vintage style engagement ring montreal"',  "Phrase", "Commercial"),
    ]
    headlines = [
        ("Oval Diamond Rings — Montreal Maker",        28),
        ("Halo Engagement Rings — No Markup",          28),
        ("Solitaire Rings Since 1982 — Montreal",       30),
        ("Cushion Cut Diamonds — Manufacturer",         29),
        ("Three-Stone Rings — Global Diamond",          28),
        ("Any Cut. Any Shape. Built For You.",           28),
        ("Round, Oval, Cushion, Emerald Cut",           27),
        ("Find Your Diamond Shape — Free Consult",      34),
        ("Manufacturer Pricing on Every Style",         30),
        ("Engagement Ring Styles — Montreal Atelier",   37),
        ("Pave, Prong, Bezel — You Choose",             24),
        ("Diamonds From 12 Countries — See More",       31),
        ("Book a Consultation — See Every Style",       32),
        ("Compare Ring Styles In-Person or Virtual",    36),
        ("Free Consultation — No Pressure",             26),
    ]
    descriptions = [
        ("Looking for a specific ring style? Global Diamond Montreal makes solitaire, halo, pave, three-stone, and fully custom rings. Free consultation. Manufacturer pricing.", 162),
        ("Oval, cushion, round, emerald — we source diamonds in every shape from 12 countries. Montreal manufacturer since 1982. No retail markup. Book your style consultation.", 163),
        ("Not sure between solitaire and halo? Come in. See both in real life. Free consultation, no commitment. Montreal's most experienced engagement ring manufacturer.", 155),
        ("Every ring style at manufacturer pricing. Ecksand and St-Onge source locally — GDM sources from 12 countries. More options. Better value. Same Montreal craftsmanship.", 163),
    ]
    cross_negatives = [
        ("custom",    "Exact", "Route custom queries to AG1"),
        ("lab grown", "Exact", "Route lab-grown to AG4"),
    ]
    build_search_ag_tab(
        tab_name="Search - AG3",
        ag_name="AG3: Ring Styles (Solitaire / Halo / Oval / Cushion)",
        priority="Priority 4",
        theme="Buyer knows exactly what style they want — bottom-funnel intent with shape/style modifier.",
        lp_url="https://go.globaldiamondmontreal.com/appointment?utm_campaign=engagement-rings",
        keywords=keywords,
        headlines=headlines,
        descriptions=descriptions,
        cross_negatives=cross_negatives,
    )


# ─── TAB 11: SEARCH - AG4: LAB-GROWN ─────────────────────────────────────────

def build_search_ag4():
    keywords = [
        ("[lab grown engagement ring montreal]",      "Exact",  "Transactional"),
        ('"lab grown engagement ring montreal"',      "Phrase", "Transactional"),
        ("[lab diamond engagement ring montreal]",    "Exact",  "Transactional"),
        ('"lab created engagement ring montreal"',    "Phrase", "Transactional"),
        ("[lab grown diamond ring montreal]",         "Exact",  "Commercial"),
        ('"sustainable engagement ring montreal"',    "Phrase", "Commercial"),
        ("[lab grown engagement ring canada]",        "Exact",  "Transactional — virtual consult"),
        ('"lab diamond ring canada"',                 "Phrase", "Commercial"),
        ("[lab grown diamond ring canada]",           "Exact",  "Commercial"),
    ]
    headlines = [
        ("Lab-Grown Engagement Rings Montreal",       31),
        ("Natural or Lab-Grown — You Decide",          27),
        ("Lab Diamond Rings — Manufacturer Price",     31),
        ("D Color VS1 Lab Diamonds — Certified",       29),
        ("IGI Certified Lab Diamonds Montreal",        30),
        ("Same Sparkle. Manufacturer Pricing.",        28),
        ("Lab-Grown or Natural — Free Consult",        29),
        ("CVD + HPHT Diamonds Available",              25),
        ("Global Diamond — Lab Diamond Specialist",    34),
        ("Montreal Manufacturer — Lab-Grown Expert",   34),
        ("Oval, Cushion, Round Lab Diamonds",          28),
        ("Lab Diamond Ring From $1,800 Montreal",      31),
        ("Not Just Ethics — Better Value Too",         27),
        ("Book Lab Diamond Consultation Today",        30),
        ("Natural + Lab-Grown — See Both In Person",   33),
    ]
    descriptions = [
        ("Lab-grown or natural — your call. Global Diamond Montreal offers both, with manufacturer pricing on either. IGI certified. Free consultation in Montreal or virtual.", 162),
        ("Lab-grown diamonds: same hardness, same sparkle, same certification. Different price point. We source from 12 countries — more options than most local jewellers.", 160),
        ("Looking for a lab-grown engagement ring? Book a free consultation at Global Diamond Montreal. See D/VS certified lab diamonds side by side with natural stones. No pressure.", 169),
        ("Montreal manufacturer since 1982 — now with a full lab-grown diamond selection. Your ring, your choice, manufacturer pricing. In-store or virtual consultation available.", 165),
    ]
    build_search_ag_tab(
        tab_name="Search - AG4",
        ag_name="AG4: Lab-Grown Engagement Ring Montreal",
        priority="Priority 3 — specific intent, route all lab-grown traffic here",
        theme="Eco/budget-conscious buyer who prefers lab-grown. Do NOT lead with ethics — Brilliant Earth owns that. Lead with choice + value.",
        lp_url="https://go.globaldiamondmontreal.com/appointment?utm_campaign=engagement-rings",
        keywords=keywords,
        headlines=headlines,
        descriptions=descriptions,
        cross_negatives=[],
    )


# ─── TAB 12: SEARCH - AG5: MANUFACTURER DIRECT ───────────────────────────────

def build_search_ag5():
    keywords = [
        ("[engagement ring manufacturer montreal]",    "Exact",  "Transactional"),
        ('"buy engagement ring from manufacturer"',    "Phrase", "Transactional"),
        ("[diamond ring manufacturer montreal]",       "Exact",  "Transactional"),
        ('"engagement ring wholesale montreal"',       "Phrase", "Commercial"),
        ("[custom ring manufacturer montreal]",        "Exact",  "Transactional"),
        ('"buy engagement ring direct montreal"',      "Phrase", "Transactional"),
        ("[diamond engagement ring manufacturer canada]","Exact","Transactional — virtual"),
        ('"direct from manufacturer engagement ring"', "Phrase", "Transactional"),
    ]
    headlines = [
        ("Buy Direct — Engagement Ring Manufacturer",  36),
        ("No Retail Markup — Montreal Maker",           22),
        ("Cut Out the Middleman — Global Diamond",      32),
        ("Direct From Manufacturer Since 1982",         30),
        ("Manufacturer Pricing on Every Ring",          30),
        ("Diamond Engagement Rings — Wholesale Price",  37),
        ("See What a Manufacturer Can Offer You",       33),
        ("Same Quality as Boutiques — No Markup",       31),
        ("Diamonds From 12 Countries — Your Price",     33),
        ("Montreal Ring Manufacturer — Free Consult",   36),
        ("Why Pay Retail? Buy From the Maker.",         31),
        ("40+ Years. Thousands of Rings. No Markup.",   33),
        ("Manufacturer Rings Starting at $2,000",       32),
        ("Book Your Manufacturer Consultation Today",   36),
        ("Skip the Retailer — Same Quality, Less",      32),
    ]
    descriptions = [
        ("Global Diamond Montreal is a manufacturer, not a retailer. That means no markup — your budget buys more diamond. Book a free consultation and see the difference yourself.", 168),
        ("The same quality you'd find at Birks. At the price a manufacturer charges. No retail markup, no commission. Book a consultation at Global Diamond Montreal.", 156),
        ("Since 1982, we've made engagement rings for buyers who know what retail markup costs. Diamonds from 12 countries. Manufacturer pricing. Free consultation, no obligation.", 167),
        ("Skip the retailer. Buy from the manufacturer. Global Diamond Montreal — 40+ years, thousands of rings made, manufacturer pricing on every piece. In-store or virtual consult.", 171),
    ]
    cross_negatives = [
        ("lab grown",  "Exact", "Route lab-grown queries to AG4"),
        ("lab diamond","Exact", "Route lab-grown queries to AG4"),
    ]
    build_search_ag_tab(
        tab_name="Search - AG5",
        ag_name="AG5: Manufacturer / Direct Source",
        priority="Priority 5 — low competition, very high intent",
        theme="Savvy buyer who already knows about retail markup and is specifically looking for a manufacturer. Very low competition, very high intent.",
        lp_url="https://go.globaldiamondmontreal.com/appointment?utm_campaign=engagement-rings",
        keywords=keywords,
        headlines=headlines,
        descriptions=descriptions,
        cross_negatives=cross_negatives,
    )


# ─── TAB 13: SEARCH - AG6: CANADA VIRTUAL ────────────────────────────────────

def build_search_ag6():
    keywords = [
        ('"custom engagement ring canada"',            "Phrase", "Transactional"),
        ("[custom engagement ring canada]",            "Exact",  "Transactional"),
        ('"design engagement ring online canada"',     "Phrase", "Transactional"),
        ("[virtual engagement ring consultation canada]","Exact","Transactional"),
        ('"custom diamond ring canada"',               "Phrase", "Commercial"),
        ("[engagement ring consultation canada]",      "Exact",  "Commercial"),
        ('"lab grown engagement ring canada"',         "Phrase", "Commercial"),
        ('"best custom engagement ring canada"',       "Phrase", "Commercial Investigation"),
        ("[engagement ring manufacturer canada]",      "Exact",  "Transactional"),
        ('"design your own engagement ring canada"',   "Phrase", "Transactional"),
    ]
    headlines = [
        ("Custom Engagement Rings — Ship Canada",      31),
        ("Virtual Ring Consultation — Canada-Wide",    34),
        ("Design Your Ring Online — Free Consult",     30),
        ("Montreal Manufacturer — Ships Canada-Wide",  33),
        ("Custom Diamond Ring — Virtual Design",       29),
        ("Global Diamond — Virtual Consultation",      31),
        ("Design It Remotely — We Build It",           26),
        ("Lab-Grown or Natural — Virtual Consult",     30),
        ("Book a Virtual Ring Consultation Today",     33),
        ("Canada's Manufacturer — No Retail Markup",   33),
        ("Any Diamond Shape Online — Free Consult",    32),
        ("Custom Rings. Montreal Craft. Canada-Wide.", 36),
        ("Free Virtual Consultation — See Live Diamonds", 40),
        ("Build Your Ring From Anywhere in Canada",    32),
        ("Manufacturer Pricing — No Middleman",        28),
    ]
    descriptions = [
        ("Not in Montreal? No problem. Global Diamond Montreal offers virtual ring consultations across Canada. Same manufacturer pricing, same expertise, delivered to your door.", 164),
        ("Design your custom engagement ring over video call with our Montreal diamond expert. See diamonds live, choose your setting, get manufacturer pricing. Ships across Canada.", 165),
        ("Canada's engagement ring manufacturer — now available virtually. Book a free consultation from Toronto, Vancouver, Calgary, or anywhere. No pressure. Just expertise.", 159),
        ("Virtual consultation: show us your inspiration, we show you diamonds. Choose your stone, your setting, your metal. Built in Montreal. Shipped across Canada. Free consult.", 163),
    ]
    build_search_ag_tab(
        tab_name="Search - AG6",
        ag_name="AG6: Canada-Wide Virtual Consultation",
        priority="Priority 6 — national reach via virtual consultation",
        theme="Outside Montreal, wants to design a ring remotely. Opens Canada-wide revenue for the ring funnel per Lever 3 strategy.",
        lp_url="https://go.globaldiamondmontreal.com/appointment?utm_campaign=engagement-rings",
        keywords=keywords,
        headlines=headlines,
        descriptions=descriptions,
        cross_negatives=[],
    )


# ─── TAB 14: EXTENSIONS - SEARCH ─────────────────────────────────────────────

def build_extensions_search():
    headers = ["Extension Type", "Field", "Value", "Notes"]
    rows = [
        ["SITELINK 1", "Link Text",     "Custom Engagement Rings",                         "30 char max"],
        ["SITELINK 1", "Description 1", "Design any ring, any style",                      "35 char max"],
        ["SITELINK 1", "Description 2", "Free consultation included",                      ""],
        ["SITELINK 1", "Final URL",     "globaldiamondmontreal.com/pages/appointment-1",   "Confirm URL"],
        [""],
        ["SITELINK 2", "Link Text",     "Book a Consultation",                             ""],
        ["SITELINK 2", "Description 1", "In-person or virtual",                            ""],
        ["SITELINK 2", "Description 2", "Montreal manufacturer since 1982",                ""],
        ["SITELINK 2", "Final URL",     "go.globaldiamondmontreal.com/appointment",        ""],
        [""],
        ["SITELINK 3", "Link Text",     "Lab-Grown Diamonds",                              ""],
        ["SITELINK 3", "Description 1", "Natural or lab-grown — your call",               ""],
        ["SITELINK 3", "Description 2", "IGI certified, D/VS quality",                    ""],
        ["SITELINK 3", "Final URL",     "globaldiamondmontreal.com/collections/lab-grown-engagement-rings", "Confirm URL"],
        [""],
        ["SITELINK 4", "Link Text",     "View Ring Collection",                            ""],
        ["SITELINK 4", "Description 1", "Solitaire, halo, three-stone, custom",            ""],
        ["SITELINK 4", "Description 2", "Manufacturer pricing on every style",             ""],
        ["SITELINK 4", "Final URL",     "globaldiamondmontreal.com/collections/engagement-rings", ""],
        [""],
        ["SITELINK 5", "Link Text",     "Free Diamond Gift Offer",                         ""],
        ["SITELINK 5", "Description 1", "Free 0.26ct studs with $2,500+",                 ""],
        ["SITELINK 5", "Description 2", "Free 1.00ct studs with $5,000+",                 ""],
        ["SITELINK 5", "Final URL",     "globaldiamondmontreal.com",                       "Update to offer page if available"],
        [""],
        ["SITELINK 6", "Link Text",     "Virtual Consultation",                            ""],
        ["SITELINK 6", "Description 1", "Design your ring from anywhere",                  ""],
        ["SITELINK 6", "Description 2", "Ships across Canada",                             ""],
        ["SITELINK 6", "Final URL",     "go.globaldiamondmontreal.com/appointment",        ""],
        [""],
        ["CALLOUT 1", "Text", "Free Design Consultation",        "24 chars"],
        ["CALLOUT 2", "Text", "Manufacturer Since 1982",          "23 chars"],
        ["CALLOUT 3", "Text", "No Retail Markup",                "16 chars"],
        ["CALLOUT 4", "Text", "Diamonds From 12 Countries",      "25 chars"],
        ["CALLOUT 5", "Text", "Natural + Lab-Grown Available",   "29 chars — trim if needed"],
        ["CALLOUT 6", "Text", "In-Person or Virtual Consult",    "28 chars"],
        ["CALLOUT 7", "Text", "Ships Across Canada",             "19 chars"],
        ["CALLOUT 8", "Text", "40+ Years of Montreal Craft",     "25 chars"],
        [""],
        ["STRUCTURED SNIPPET", "Header type", "Styles",           ""],
        ["STRUCTURED SNIPPET", "Value 1",     "Solitaire",        ""],
        ["STRUCTURED SNIPPET", "Value 2",     "Halo",             ""],
        ["STRUCTURED SNIPPET", "Value 3",     "Three-Stone",      ""],
        ["STRUCTURED SNIPPET", "Value 4",     "Cushion Cut",      ""],
        ["STRUCTURED SNIPPET", "Value 5",     "Oval",             ""],
        ["STRUCTURED SNIPPET", "Value 6",     "Custom Design",    ""],
        ["STRUCTURED SNIPPET", "Value 7",     "Pave",             ""],
        ["STRUCTURED SNIPPET", "Value 8",     "Vintage Inspired", ""],
        [""],
        ["CALL EXTENSION", "Phone Number",  "CONFIRM WITH DOC",             "Not in client notes — request GDM main line"],
        ["CALL EXTENSION", "Schedule",      "Business hours Monday-Saturday",""],
        ["CALL EXTENSION", "Call Reporting","Enabled",                       "Required for CallRail attribution"],
        [""],
        ["LOCATION EXTENSION", "Source", "Google My Business",               ""],
        ["LOCATION EXTENSION", "Status", "CONFIRM GMB ACCESS",               "GMB access was pending as of March 17 — confirm bishal@hoski.ca has access before launch"],
        ["LOCATION EXTENSION", "Action", "Link GDM Google My Business listing",""],
    ]
    write_to_sheet(SHEET_ID, "Extensions - Search", headers, rows)


# ─── TAB 15: NEGATIVE KEYWORDS ────────────────────────────────────────────────

def build_negatives():
    headers = ["Level", "Campaign / Ad Group", "Negative Keyword", "Match Type", "Reason"]
    rows = [
        ["Account", "All Campaigns", "jobs",                  "Broad",  "Employment"],
        ["Account", "All Campaigns", "careers",               "Broad",  "Employment"],
        ["Account", "All Campaigns", "hiring",                "Broad",  "Employment"],
        ["Account", "All Campaigns", "salary",                "Broad",  "Employment"],
        ["Account", "All Campaigns", "resume",                "Broad",  "Employment"],
        ["Account", "All Campaigns", "how to",                "Broad",  "Informational DIY intent"],
        ["Account", "All Campaigns", "tutorial",              "Broad",  "DIY intent"],
        ["Account", "All Campaigns", "free template",         "Broad",  "Non-commercial"],
        ["Account", "All Campaigns", "diy",                   "Broad",  "DIY intent"],
        ["Account", "All Campaigns", "do it yourself",        "Broad",  "DIY intent"],
        ["Account", "All Campaigns", "course",                "Broad",  "Educational"],
        ["Account", "All Campaigns", "training",              "Broad",  "Educational"],
        ["Account", "All Campaigns", "school",                "Broad",  "Educational"],
        ["Account", "All Campaigns", "degree",                "Broad",  "Educational"],
        ["Account", "All Campaigns", "certification",         "Broad",  "Educational"],
        ["Campaign", "Search + PMax", "ecksand",              "Phrase", "Competitor brand"],
        ["Campaign", "Search + PMax", "flamme en rose",       "Phrase", "Competitor brand"],
        ["Campaign", "Search + PMax", "st-onge",              "Phrase", "Competitor brand"],
        ["Campaign", "Search + PMax", "birks",                "Phrase", "Competitor brand"],
        ["Campaign", "Search + PMax", "peoples jewellers",    "Phrase", "Competitor brand"],
        ["Campaign", "Search + PMax", "michael hill",         "Phrase", "Competitor brand"],
        ["Campaign", "Search + PMax", "brilliant earth",      "Phrase", "Competitor brand"],
        ["Campaign", "Search + PMax", "proud diamond",        "Phrase", "Competitor brand"],
        ["Campaign", "Search + PMax", "pandora",              "Phrase", "Competitor brand"],
        ["Campaign", "Search + PMax", "tiffany",              "Phrase", "Competitor brand"],
        ["Campaign", "Search + PMax", "ex aurum",             "Phrase", "Competitor brand"],
        ["Campaign", "Search + PMax", "wedding band",         "Phrase", "Wrong product — not a ring campaign"],
        ["Campaign", "Search + PMax", "wedding ring",         "Phrase", "Wedding bands are a separate category"],
        ["Campaign", "Search + PMax", "eternity ring",        "Phrase", "Wrong product category"],
        ["Campaign", "Search + PMax", "promise ring",         "Phrase", "Lower intent / different category"],
        ["Campaign", "Search + PMax", "anniversary ring",     "Phrase", "Different occasion category"],
        ["Campaign", "Search + PMax", "fashion ring",         "Phrase", "Wrong product — not fine jewelry intent"],
        ["Campaign", "Search + PMax", "cocktail ring",        "Phrase", "Wrong product category"],
        ["Campaign", "Search + PMax", "men's ring",           "Phrase", "Wrong demographic"],
        ["Campaign", "Search + PMax", "class ring",           "Phrase", "Wrong product"],
        ["Campaign", "Search + PMax", "signet ring",          "Phrase", "Wrong product"],
        ["Campaign", "Search + PMax", "pinky ring",           "Phrase", "Wrong product"],
        ["Campaign", "Search + PMax", "repair",               "Phrase", "Service — not a purchase"],
        ["Campaign", "Search + PMax", "resize",               "Phrase", "Service — not a purchase"],
        ["Campaign", "Search + PMax", "appraisal",            "Phrase", "Service — not a purchase"],
        ["Campaign", "Search + PMax", "second hand",          "Phrase", "Pre-owned — wrong intent"],
        ["Campaign", "Search + PMax", "used",                 "Phrase", "Pre-owned — wrong intent"],
        ["Campaign", "Search + PMax", "vintage",              "Phrase", "Pre-owned unless GDM confirmed to sell vintage — check with Doc"],
        ["Campaign", "Search + PMax", "for sale",             "Phrase", "Often signals classifieds / marketplace intent"],
        ["Campaign", "Search + PMax", "pawn",                 "Phrase", "Pre-owned marketplace intent"],
        ["Ad Group", "AG2 (General Montreal)",  "custom",     "Exact", "Route custom queries to AG1"],
        ["Ad Group", "AG2 (General Montreal)",  "lab grown",  "Exact", "Route lab-grown to AG4"],
        ["Ad Group", "AG2 (General Montreal)",  "lab diamond","Exact", "Route lab-diamond to AG4"],
        ["Ad Group", "AG1 (Custom Ring)",       "lab grown",  "Exact", "Route lab-grown to AG4"],
        ["Ad Group", "AG1 (Custom Ring)",       "lab diamond","Exact", "Route lab-grown to AG4"],
        ["Ad Group", "AG3 (Ring Styles)",       "custom",     "Exact", "Route custom queries to AG1"],
        ["Ad Group", "AG3 (Ring Styles)",       "lab grown",  "Exact", "Route lab-grown to AG4"],
        ["Ad Group", "AG5 (Manufacturer)",      "lab grown",  "Exact", "Route lab-grown to AG4"],
        ["Ad Group", "AG5 (Manufacturer)",      "lab diamond","Exact", "Route lab-grown to AG4"],
    ]
    write_to_sheet(SHEET_ID, "Negative Keywords", headers, rows)


# ─── TAB 16: PRE-LAUNCH QA ────────────────────────────────────────────────────

def build_qa_checklist():
    headers = ["Category", "Item", "Status", "Owner", "Notes"]
    rows = [
        ["FEED + MC (PMax only)", "Engagement ring products tagged with custom_label_1 = engagement-rings in Shopify",
         "[ ]", "Doc / Bishal", "BLOCKER — PMax cannot launch without this tag in Shopify"],
        ["FEED + MC (PMax only)", "All tagged products approved in Merchant Center (no disapprovals)",
         "[ ]", "Bishal", "Check Merchant Center diagnostics tab after tagging"],
        ["FEED + MC (PMax only)", "Product prices match Shopify storefront",
         "[ ]", "Bishal", "Price mismatch triggers MC disapproval"],
        ["FEED + MC (PMax only)", "Listing group filter confirmed: Custom Label 1 = engagement-rings (INCLUDE); everything else EXCLUDE",
         "[ ]", "Bishal", "Set in campaign builder — verify before launch"],
        ["FEED + MC (PMax only)", "Product type sub-segments created (Solitaire, Halo, Custom, Lab-Grown)",
         "[ ]", "Bishal", "Enables reporting by product type within PMax"],
        [""],
        ["PMAX CAMPAIGN", "Brand exclusion list active (6 terms)",
         "[ ]", "Bishal", "global diamond montreal, globaldiamondmontreal.com, global diamond, doctor diamond, gdm jewelry, gdm montreal"],
        ["PMAX CAMPAIGN", "Final URL expansion OFF",
         "[ ]", "Bishal", "Critical — must be OFF to prevent URL auto-expansion beyond ring consultation page"],
        ["PMAX CAMPAIGN", "Conversion goals: Appointment (primary), Offline Purchase (primary), others secondary",
         "[ ]", "Bishal", "Do not set local directions as conversion — caused 68 fake conversions in PMax Local"],
        ["PMAX CAMPAIGN", "No local directions as conversion event",
         "[ ]", "Bishal", "Lesson from PMax Local campaign — explicitly exclude"],
        ["PMAX CAMPAIGN", "Audience signals added to all 3 asset groups",
         "[ ]", "Bishal", "See PMax - Audience Sigs tab — Customer Match + In-market + Remarketing"],
        ["PMAX CAMPAIGN", "All 15 headline slots filled per asset group (45 headlines total)",
         "[ ]", "Bishal", "See PMax - Asset Groups tab"],
        ["PMAX CAMPAIGN", "All 5 description slots filled per asset group (15 descriptions total)",
         "[ ]", "Bishal", "See PMax - Asset Groups tab"],
        ["PMAX CAMPAIGN", "Min 1 landscape image + 1 square image per asset group",
         "[ ]", "Bishal / Ana", "Request ring images from Doc or Ana K.A."],
        ["PMAX CAMPAIGN", "Ad strength 'Good' or 'Excellent' before launch",
         "[ ]", "Bishal", "Do not launch on 'Poor' — Google will limit delivery"],
        [""],
        ["SEARCH CAMPAIGN", "All 6 ad groups created with correct keywords and match types",
         "[ ]", "Bishal", "See tabs Search - AG1 through AG6"],
        ["SEARCH CAMPAIGN", "RSA per ad group: 15 headlines + 4 descriptions minimum",
         "[ ]", "Bishal", "Copy from Search - AG tabs"],
        ["SEARCH CAMPAIGN", "UTM utm_campaign=engagement-rings on all final URLs",
         "[ ]", "Bishal", "Required for GHL ring consultation tagging — do not skip"],
        ["SEARCH CAMPAIGN", "Location targeting: Montreal 50km radius + Canada-wide (dual)",
         "[ ]", "Bishal", "Both locations must be added — in-store AND virtual coverage"],
        ["SEARCH CAMPAIGN", "Campaign-level negatives applied (competitor names, wrong product categories)",
         "[ ]", "Bishal", "See Negative Keywords tab — Campaign level rows"],
        ["SEARCH CAMPAIGN", "Ad group cross-negatives applied per cross-negatives table",
         "[ ]", "Bishal", "See Negative Keywords tab — Ad Group level rows"],
        ["SEARCH CAMPAIGN", "Extensions: 6 sitelinks, 8 callouts, structured snippet, call (if GMB confirmed), location",
         "[ ]", "Bishal", "See Extensions - Search tab"],
        ["SEARCH CAMPAIGN", "Conversion goal: Appointment booked (ring consultation) as primary",
         "[ ]", "Bishal", ""],
        ["SEARCH CAMPAIGN", "Bid strategy: Maximize Conversions (no tCPA until 30+ conversions)",
         "[ ]", "Bishal", "Do not set tCPA $585 at launch — wait for conversion data"],
        [""],
        ["CONFLICT CHECK", "No other active campaign bidding on engagement ring keywords without brand exclusions",
         "[ ]", "Bishal", "Check account-level campaign settings and keyword overlap"],
        ["CONFLICT CHECK", "Mother's Day PMax listing group does NOT include engagement rings",
         "[ ]", "Bishal", "Mother's Day PMax filters on custom_label_0 = mothers-day-2026 only — should be clean but verify"],
        ["CONFLICT CHECK", "Brand Search campaign remains active",
         "[ ]", "Bishal", "Brand campaign catches branded traffic that PMax will not receive"],
        ["CONFLICT CHECK", "Confirm show rate above 50% before scaling Lever 2 (prerequisite from strategy)",
         "[ ]", "Bishal", "Independent of this build — check current GHL pipeline show rate"],
        [""],
        ["PRE-REQS", "GMB access confirmed for bishal@hoski.ca",
         "[ ]", "Bishal", "GMB access was pending as of March 17 — needed for Location Extension on Search campaign"],
        ["PRE-REQS", "GDM main phone number confirmed",
         "[ ]", "Doc",    "Not in client notes — request from Doc before adding Call Extension"],
        ["PRE-REQS", "Ring consultation landing page live and loading correctly",
         "[ ]", "Bishal", "go.globaldiamondmontreal.com/appointment — test form submission and GHL tagging"],
        ["PRE-REQS", "Zapier webhook confirmed for offline conversion upload",
         "[ ]", "Bishal / Doc", "Required for Offline Purchase conversion goal in PMax"],
    ]
    write_to_sheet(SHEET_ID, "Pre-Launch QA", headers, rows)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    if SHEET_ID == "REPLACE_WITH_YOUR_SHEET_ID":
        print("ERROR: Set SHEET_ID constant before running.")
        print("  1. Create a new Google Sheet")
        print("  2. Share it with the service account email in sheets-credentials.json")
        print("  3. Copy the sheet ID from the URL and set SHEET_ID in this file")
        return

    print("Building GDM Engagement Rings Campaign Sheet...")
    print(f"Sheet ID: {SHEET_ID}")
    print()

    steps = [
        ("Overview",              build_overview),
        ("PMax - Campaign",       build_pmax_campaign),
        ("PMax - Asset Groups",   build_pmax_asset_groups),
        ("PMax - Search Themes",  build_pmax_search_themes),
        ("PMax - Audience Sigs",  build_pmax_audience_signals),
        ("PMax - Extensions",     build_pmax_extensions),
        ("Search - Campaign",     build_search_campaign),
        ("Search - AG1",          build_search_ag1),
        ("Search - AG2",          build_search_ag2),
        ("Search - AG3",          build_search_ag3),
        ("Search - AG4",          build_search_ag4),
        ("Search - AG5",          build_search_ag5),
        ("Search - AG6",          build_search_ag6),
        ("Extensions - Search",   build_extensions_search),
        ("Negative Keywords",     build_negatives),
        ("Pre-Launch QA",         build_qa_checklist),
    ]

    for tab_name, fn in steps:
        print(f"Writing tab: {tab_name}...")
        fn()

    print()
    print(f"Done. All {len(steps)} tabs written.")
    print(f"Sheet: https://docs.google.com/spreadsheets/d/{SHEET_ID}")


if __name__ == "__main__":
    main()
