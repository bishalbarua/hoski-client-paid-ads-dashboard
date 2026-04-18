#!/usr/bin/env python3
"""
GDM Mother's Day 2026 PMax Campaign Excel Generator
Creates a comprehensive Excel sheet for easy copy-paste campaign setup
"""

import pandas as pd
from datetime import datetime

# Create Excel writer with multiple sheets
output_file = f"/Users/bishalbarua/Bishal/AI/antigravity/Hoski Marketing Manager/clients/GDM Google Ads (7087867966)/notes/pmax-mothers-day-campaign-build-{datetime.now().strftime('%Y-%m-%d')}.xlsx"

with pd.ExcelWriter(output_file, engine='openpyxl') as writer:

    # ============================================
    # SHEET 1: CAMPAIGN SETTINGS
    # ============================================
    campaign_settings = [
        ['Setting', 'Value', 'Notes'],
        ['Account', 'Global Diamond Montreal (7087867966)', ''],
        ['Campaign Type', 'Performance Max', ''],
        ['Campaign Name', 'Hoski | PMax Mother\'s Day 2026 | Feed Only', ''],
        ['Goal', 'Sales - Online Purchase (Shopify)', ''],
        ['Bid Strategy', 'Maximize Conversion Value (no tROAS first 7 days)', 'Then 3.5x tROAS after day 7'],
        ['Daily Budget', '$45/day (Apr 16-22) -> $65/day (Apr 23-30) -> $90/day (May 1-11)', 'See Budget Schedule sheet'],
        ['Start Date', 'April 16, 2026', ''],
        ['End Date', 'May 11, 2026', ''],
        ['Locations', 'Canada - all provinces', ''],
        ['Languages', 'English + French', ''],
        ['Final URL Expansion', 'OFF', 'Traffic to collection/product pages only'],
        ['Merchant Center Feed', 'Linked - custom_label_0 = mothers-day-2026', ''],
        ['Brand Exclusions', 'Global Diamond Montreal, globaldiamondmontreal.com, Global Diamond, Doctor Diamond, GDM Jewelry, gdm jewelry', 'Prevents branded search cannibalization']
    ]
    pd.DataFrame(campaign_settings).to_excel(writer, sheet_name='1. Campaign Settings', index=False, header=False)

    # ============================================
    # SHEET 2: LISTING GROUPS
    # ============================================
    listing_groups = [
        ['Filter Type', 'Filter Value', 'Action', 'Notes'],
        ['All Products', '', 'Include All', ''],
        ['Custom Label 0', 'mothers-day-2026', 'INCLUDE - Bid Everything', 'Main feed filter'],
        ['Product Type', 'Diamond Studs', 'Segment', 'Earrings asset group'],
        ['Product Type', 'Diamond Pendant', 'Segment', 'Pendants asset group'],
        ['Product Type', 'Diamond Bracelets', 'Segment', 'Bracelets asset group'],
        ['Product Type', 'Gemstone Bracelets', 'Segment', 'Bracelets asset group'],
        ['Everything else', '', 'EXCLUDE', 'All non-Mother\'s Day products']
    ]
    pd.DataFrame(listing_groups).to_excel(writer, sheet_name='2. Listing Groups', index=False, header=True)

    # ============================================
    # SHEET 3: ASSET GROUP 1 - EARRINGS
    # ============================================
    earrings_data = []

    # Basic Info
    earrings_data.append(['ASSET GROUP 1: DIAMOND EARRINGS - MOTHER\'S DAY', '', ''])
    earrings_data.append(['Final URL', 'https://globaldiamondmontreal.com/collections/diamond-earrings', ''])
    earrings_data.append(['Listing Group Filter', 'Product Type = Diamond Studs + custom_label_0 = mothers-day-2026', ''])
    earrings_data.append(['', '', ''])

    # Headlines (15)
    earrings_data.append(['HEADLINES (15 - use all slots)', '', ''])
    headlines_earrings = [
        'Diamond Earrings for Mom',
        'Lab-Grown Diamond Studs',
        'Mother\'s Day Diamond Gift',
        '14K Gold Diamond Studs',
        'Diamond Stud Earrings Canada',
        'Free Shipping. 30-Day Returns.',
        'Manufacturer Price - No Markup',
        'Global Diamond Montreal',
        'Since 1982 - 40+ Years',
        'From $390 - Real Diamonds',
        'Diamond Earrings Gift for Her',
        'White Gold Diamond Studs',
        'VS Clarity. F Color. Certified.',
        'Gift-Wrapped Free',
        'Mother\'s Day - Shop Now'
    ]
    for i, hl in enumerate(headlines_earrings, 1):
        earrings_data.append([f'Headline {i}', hl, ''])

    earrings_data.append(['', '', ''])

    # Descriptions (5)
    earrings_data.append(['DESCRIPTIONS (5 - use all slots)', '', ''])
    descs_earrings = [
        'Real diamonds, manufacturer pricing. Studs starting at $390 in 14k gold. Free Canadian shipping. Perfect gift for Mom.',
        'Lab-grown or natural diamond studs from $390. Gift-wrapped. Ships within 14 business days. 30-day returns.',
        'Global Diamond Montreal - manufacturer since 1982. No retail markup. VS clarity, F color diamond studs for Mother\'s Day.',
        'Diamond studs in white or yellow gold. 0.10ct to 0.26ct. Free gift packaging included. Buy direct from the manufacturer.',
        'Give Mom real diamonds this Mother\'s Day. Manufacturer pricing means better quality for the same money. Ships across Canada.'
    ]
    for i, desc in enumerate(descs_earrings, 1):
        earrings_data.append([f'Description {i}', desc, ''])

    earrings_data.append(['', '', ''])
    earrings_data.append(['IMAGES REQUIRED', '', ''])
    earrings_data.append(['1.91:1 Landscape (1200x628)', 'Product on white background - diamond studs', ''])
    earrings_data.append(['1:1 Square (1200x1200)', 'Product lifestyle - earrings worn or in gift box', ''])
    earrings_data.append(['4:5 Portrait (960x1200)', 'Gift occasion image - if available', ''])

    pd.DataFrame(earrings_data).to_excel(writer, sheet_name='3. AG1 - Earrings', index=False, header=False)

    # ============================================
    # SHEET 4: ASSET GROUP 2 - PENDANTS
    # ============================================
    pendants_data = []

    pendants_data.append(['ASSET GROUP 2: DIAMOND PENDANTS - MOTHER\'S DAY', '', ''])
    pendants_data.append(['Final URL', 'https://globaldiamondmontreal.com/collections/diamond-pendants', ''])
    pendants_data.append(['Listing Group Filter', 'Product Type = Diamond Pendant + custom_label_0 = mothers-day-2026', ''])
    pendants_data.append(['', '', ''])

    pendants_data.append(['HEADLINES (15 - use all slots)', '', ''])
    headlines_pendants = [
        'Diamond Necklace for Mom',
        'Heart Pendant - Mother\'s Day Gift',
        '14K Gold Diamond Pendant',
        'Diamond Heart Necklace Canada',
        'Gold Necklace Gift for Her',
        'Chain Included - Ready to Gift',
        'Manufacturer Price - No Markup',
        'Diamond Pendant from $1,100',
        'Natural Diamond Pendants',
        'Free Shipping Across Canada',
        'Global Diamond Montreal',
        'Greek Key Diamond Pendant',
        'Since 1982 - Fine Jewelry',
        'Gift-Wrapped Free. Ships Fast.',
        'Mother\'s Day - Shop Pendants'
    ]
    for i, hl in enumerate(headlines_pendants, 1):
        pendants_data.append([f'Headline {i}', hl, ''])

    pendants_data.append(['', '', ''])
    pendants_data.append(['DESCRIPTIONS (5 - use all slots)', '', ''])
    descs_pendants = [
        'Diamond heart pendants from $1,100. Chain included. Gift-wrapped free. Ships across Canada. 30-day money-back guarantee.',
        'Natural and lab-grown diamond pendants in 10k and 14k gold. Manufacturer pricing - no retail markup. Mother\'s Day collection.',
        'Global Diamond Montreal - manufacturer since 1982. Heart, cross, and halo diamond pendants. Free Canadian shipping.',
        'Give Mom a diamond pendant with chain included - ready to gift. Prices from $1,100. Ships within 14 business days.',
        'Heart, greek key, and halo diamond pendants. White, yellow, and rose gold. Buy direct from the manufacturer since 1982.'
    ]
    for i, desc in enumerate(descs_pendants, 1):
        pendants_data.append([f'Description {i}', desc, ''])

    pendants_data.append(['', '', ''])
    pendants_data.append(['IMAGES REQUIRED', '', ''])
    pendants_data.append(['1.91:1 Landscape', 'Heart pendant product on white or lifestyle', 'SKU 1400-0503 recommended'])
    pendants_data.append(['1:1 Square', 'Pendant close-up or worn lifestyle', ''])
    pendants_data.append(['4:5 Portrait', 'Gift occasion / flatlay if available', ''])

    pd.DataFrame(pendants_data).to_excel(writer, sheet_name='4. AG2 - Pendants', index=False, header=False)

    # ============================================
    # SHEET 5: ASSET GROUP 3 - BRACELETS
    # ============================================
    bracelets_data = []

    bracelets_data.append(['ASSET GROUP 3: DIAMOND BRACELETS - MOTHER\'S DAY', '', ''])
    bracelets_data.append(['Final URL', 'https://globaldiamondmontreal.com/collections/diamond-bracelets', ''])
    bracelets_data.append(['Listing Group Filter', 'Product Type = Diamond Bracelets + Gemstone Bracelets + custom_label_0 = mothers-day-2026', ''])
    bracelets_data.append(['', '', ''])

    bracelets_data.append(['HEADLINES (15 - use all slots)', '', ''])
    headlines_bracelets = [
        'Diamond Bracelet for Mom',
        'Tennis Bracelet - Mother\'s Day',
        'Diamond Tennis Bracelet Canada',
        'Gemstone Bracelet Gift for Her',
        '14K Gold Tennis Bracelet',
        'Manufacturer Price - No Markup',
        'Diamond Bracelets from $2,080',
        'Ruby + Diamond Gold Bracelet',
        'Sapphire + Diamond Bracelet',
        'Free Shipping. 30-Day Returns.',
        'Global Diamond Montreal',
        'Fine Diamond Bracelet Since 1982',
        'Tennis Bracelet 1.90 CTW',
        'Gift-Wrapped. Ships Across Canada.',
        'Mother\'s Day - Shop Bracelets'
    ]
    for i, hl in enumerate(headlines_bracelets, 1):
        bracelets_data.append([f'Headline {i}', hl, ''])

    bracelets_data.append(['', '', ''])
    bracelets_data.append(['DESCRIPTIONS (5 - use all slots)', '', ''])
    descs_bracelets = [
        'Diamond tennis bracelets and gemstone bracelets from $2,080. 14k gold. Free Canadian shipping. 30-day returns.',
        'Natural diamond tennis bracelets in white gold. Ruby and sapphire gemstone bracelets in yellow gold. Manufacturer pricing.',
        'Global Diamond Montreal - manufacturer since 1982. 1.90ctw tennis bracelet. 9.7ct ruby bracelet. Ships across Canada.',
        'Give Mom a diamond or gemstone bracelet this Mother\'s Day. Prices from $2,080 in 14k gold. Free gift-wrapping included.',
        'Manufacturer-direct diamond and gemstone bracelets. No retail markup. White and yellow gold. Buy from Global Diamond Montreal.'
    ]
    for i, desc in enumerate(descs_bracelets, 1):
        bracelets_data.append([f'Description {i}', desc, ''])

    bracelets_data.append(['', '', ''])
    bracelets_data.append(['IMAGES REQUIRED', '', ''])
    bracelets_data.append(['1.91:1 Landscape', 'Tennis bracelet (SKU 1070-0013) - strongest visual', ''])
    bracelets_data.append(['1:1 Square', 'Bracelet worn on wrist lifestyle', ''])
    bracelets_data.append(['4:5 Portrait', 'Flatlay or gift occasion - bracelet in box', ''])

    pd.DataFrame(bracelets_data).to_excel(writer, sheet_name='5. AG3 - Bracelets', index=False, header=False)

    # ============================================
    # SHEET 6: SEARCH THEMES (ALL ASSET GROUPS)
    # ============================================
    search_themes = []

    search_themes.append(['ASSET GROUP 1 - EARRINGS SEARCH THEMES (15)', '', ''])
    earrings_themes = [
        'mothers day diamond earrings',
        'diamond stud earrings gift',
        'lab grown diamond studs canada',
        'mothers day earring gift ideas',
        'diamond earrings for mom',
        '14k gold stud earrings canada',
        'diamond stud earrings mothers day',
        'gift diamond earrings women',
        'earrings for mom mothers day',
        'white gold diamond stud earrings',
        'diamond earring gift canada',
        'mothers day jewellery earrings',
        'mothers day gift fine jewelry',
        'best jewelry gift for mom',
        'real diamond earrings canada'
    ]
    for i, theme in enumerate(earrings_themes, 1):
        search_themes.append([f'Theme {i}', theme, 'Earrings'])

    search_themes.append(['', '', ''])
    search_themes.append(['ASSET GROUP 2 - PENDANTS SEARCH THEMES (15)', '', ''])
    pendants_themes = [
        'mothers day diamond necklace',
        'heart pendant mothers day gift',
        'diamond heart necklace canada',
        'gold necklace gift for mom',
        'mothers day necklace pendant',
        'diamond pendant necklace gift',
        'necklace for mom mothers day',
        'heart necklace diamond gift',
        'mothers day jewellery necklace',
        'gold diamond necklace canada',
        'diamond pendant gift ideas',
        'personalized jewelry for mom',
        'fine jewelry necklace canada',
        'mothers day gift ideas jewelry',
        'necklace gift for her canada'
    ]
    for i, theme in enumerate(pendants_themes, 1):
        search_themes.append([f'Theme {i}', theme, 'Pendants'])

    search_themes.append(['', '', ''])
    search_themes.append(['ASSET GROUP 3 - BRACELETS SEARCH THEMES (15)', '', ''])
    bracelets_themes = [
        'mothers day diamond bracelet',
        'tennis bracelet mothers day gift',
        'diamond tennis bracelet canada',
        'gemstone bracelet gift for mom',
        'mothers day bracelet gift',
        'ruby diamond bracelet gift',
        'gold bracelet mothers day',
        'mothers day bracelets montreal',
        'diamond bracelet for women canada',
        'fine jewelry bracelet gift',
        'tennis bracelet canada',
        'sapphire diamond bracelet gift',
        'mothers day luxury jewelry gift',
        'gemstone bracelet women',
        'bracelet gift for mom canada'
    ]
    for i, theme in enumerate(bracelets_themes, 1):
        search_themes.append([f'Theme {i}', theme, 'Bracelets'])

    pd.DataFrame(search_themes).to_excel(writer, sheet_name='6. Search Themes', index=False, header=False)

    # ============================================
    # SHEET 7: AUDIENCE SIGNALS (ALL ASSET GROUPS)
    # ============================================
    audience_signals = [
        ['Signal Type', 'Audience / Details', 'Notes'],
        ['SIGNAL 1: WEBSITE VISITORS (Custom Audience)', '', 'Add to ALL asset groups'],
        ['Audience', 'All website visitors - globaldiamondmontreal.com - last 90 days', 'Requires minimum 100 users'],
        ['Where to Add', 'Existing remarketing list if tagged via Google tag', ''],
        ['', '', ''],
        ['SIGNAL 2: CUSTOMER MATCH LIST', '', 'Add to ALL asset groups'],
        ['Audience', 'Existing customer email list from Shopify/GHL', ''],
        ['Action', 'Export customer emails from Shopify admin -> upload to Google Ads Audience Manager -> Customer Match', 'Requires minimum 1,000 matched emails'],
        ['Owner', 'Bishal / Faseeh', ''],
        ['', '', ''],
        ['SIGNAL 3: CUSTOM INTENT - GIFT BUYER SEARCH SIGNALS', '', 'Add to ALL asset groups'],
        ['Search Terms', 'mothers day jewelry gift', 'Custom Segment in Audience Manager'],
        ['Search Terms', 'mothers day gift ideas canada', ''],
        ['Search Terms', 'diamond earrings mothers day', ''],
        ['Search Terms', 'heart pendant necklace gift', ''],
        ['Search Terms', 'tennis bracelet mothers day', ''],
        ['Search Terms', 'jewelry gift for mom canada', ''],
        ['Search Terms', 'diamond bracelet gift women', ''],
        ['Search Terms', 'diamond necklace gift canada', ''],
        ['Search Terms', 'mothers day fine jewelry', ''],
        ['Search Terms', 'gold jewelry gift for her', ''],
        ['Search Terms', 'lab grown diamond earrings', ''],
        ['Search Terms', 'diamond studs gift', ''],
        ['Search Terms', 'fine jewelry mothers day', ''],
        ['Search Terms', 'jewellery gift mom', ''],
        ['Search Terms', 'best gift for mom 2026', ''],
        ['', '', ''],
        ['Competitor URLs (Intent Signals)', 'pandora.net/en-ca/mothers-day', ''],
        ['Competitor URLs (Intent Signals)', 'brilliantearth.com mothers day collection', ''],
        ['', '', ''],
        ['SIGNAL 4: IN-MARKET AUDIENCES', '', 'Add to ALL asset groups'],
        ['In-Market', 'Jewelry & Watches (Jewelry > Fine Jewelry)', ''],
        ['In-Market', 'Gift Shoppers (Occasions > Mother\'s Day gifts)', 'If available in Canada'],
        ['In-Market', 'Luxury Goods', ''],
        ['Life Event', 'New parent', 'Catches recent moms buying for grandmothers'],
        ['', '', ''],
        ['SIGNAL 5: INTEREST + DEMOGRAPHICS', '', 'Add to ALL asset groups'],
        ['Age', '25-65', 'Gift buyers - adults buying for their mothers'],
        ['Gender', 'All', 'Male gift buyers are a major segment'],
        ['Household Income', 'Top 50%', 'Aligns with $390-$3,360 price range'],
        ['Interests', 'Fashion & Jewelry enthusiasts, Luxury Shoppers', '']
    ]
    pd.DataFrame(audience_signals).to_excel(writer, sheet_name='7. Audience Signals', index=False, header=True)

    # ============================================
    # SHEET 8: CAMPAIGN EXTENSIONS
    # ============================================
    extensions_data = []

    extensions_data.append(['CAMPAIGN EXTENSIONS (Ad Assets)', '', 'Set at campaign level - apply to all asset groups'])
    extensions_data.append(['', '', ''])

    extensions_data.append(['SITELINKS (6 minimum)', '', ''])
    sitelinks = [
        ['Diamond Earrings', 'Lab-grown & natural diamond studs', '14k gold from $390', '/collections/diamond-earrings'],
        ['Diamond Necklaces', 'Heart & halo diamond pendants', 'Chain included. From $1,100.', '/collections/pendants'],
        ['Diamond Bracelets', 'Tennis & gemstone bracelets', '14k gold from $2,080', '/collections/diamond-bracelets'],
        ['Free Diamond Studs Offer', 'Free 0.26ct studs with $2,500+', 'Free 0.50ct studs with $3,500+', '/pages/free-diamond-offer'],
        ['Shop All Mother\'s Day Gifts', 'Earrings, pendants, bracelets', 'Gift-wrapped. Ships across Canada.', '/collections'],
        ['Book an Appointment', 'Visit our Montreal showroom', 'See the full collection in person', '/pages/appointment-1']
    ]
    extensions_data.append(['Sitelink Text', 'Description Line 1', 'Description Line 2', 'URL'])
    for sl in sitelinks:
        extensions_data.append(sl)

    extensions_data.append(['', '', ''])
    extensions_data.append(['CALLOUT EXTENSIONS (8)', '', ''])
    callouts = [
        'Free Canadian Shipping',
        '30-Day Money-Back Guarantee',
        'Manufacturer Pricing - No Markup',
        'Since 1982 - 40+ Years',
        'Natural + Lab-Grown Diamonds',
        'Free Gift Packaging',
        'Sourced from 12 Countries',
        'Ships Within 14 Business Days'
    ]
    for i, co in enumerate(callouts, 1):
        extensions_data.append([f'Callout {i}', co, ''])

    extensions_data.append(['', '', ''])
    extensions_data.append(['STRUCTURED SNIPPETS', '', ''])
    extensions_data.append(['Header', 'Types', ''])
    extensions_data.append(['Values', 'Diamond Earrings | Heart Pendants | Tennis Bracelets | Ruby Bracelets | Lab-Grown Diamonds | Gold Necklaces', ''])

    extensions_data.append(['', '', ''])
    extensions_data.append(['PROMOTION EXTENSION', '', ''])
    extensions_data.append(['Promotion', 'Mother\'s Day', ''])
    extensions_data.append(['Promotion Type', 'Free gift with purchase', ''])
    extensions_data.append(['Details', 'Free diamond studs with $2,500+ purchase', ''])
    extensions_data.append(['Occasion', 'Mother\'s Day', ''])
    extensions_data.append(['Start Date', 'April 16, 2026', ''])
    extensions_data.append(['End Date', 'May 11, 2026', ''])

    extensions_data.append(['', '', ''])
    extensions_data.append(['CALL EXTENSION', '', ''])
    extensions_data.append(['Phone', 'GDM main number (confirm with Doc)', ''])
    extensions_data.append(['Schedule', 'Business hours Monday-Saturday', ''])

    extensions_data.append(['', '', ''])
    extensions_data.append(['IMAGE EXTENSIONS', '', 'Upload at campaign level'])
    extensions_data.append(['1.91:1 Landscape', 'Diamond heart pendant lifestyle', ''])
    extensions_data.append(['1:1 Square', 'Diamond stud earrings on white', ''])
    extensions_data.append(['4:5 Portrait', 'Tennis bracelet if available', ''])

    pd.DataFrame(extensions_data).to_excel(writer, sheet_name='8. Extensions', index=False, header=False)

    # ============================================
    # SHEET 9: BUDGET SCHEDULE
    # ============================================
    budget_schedule = [
        ['Phase', 'Dates', 'Daily Budget', 'Total Phase Spend', 'Rationale'],
        ['Learning Phase', 'Apr 16-22 (7 days)', '$45/day', '$315', 'No tROAS target. Let algorithm learn. No changes.'],
        ['Scale Phase', 'Apr 23-30 (8 days)', '$65/day', '$520', '+44% increase if ROAS >= 2.5x after day 7. Add tROAS target of 3.5x.'],
        ['Final Sprint', 'May 1-11 (11 days)', '$90/day', '$990', 'Peak Mother\'s Day intent. Budget spike aligned to gift-buying urgency.'],
        ['', '', '', '', ''],
        ['TOTAL CAMPAIGN SPEND ESTIMATE', '', '', '~$1,825', 'Fits within $2,500/month Mother\'s Day overlay budget']
    ]
    pd.DataFrame(budget_schedule).to_excel(writer, sheet_name='9. Budget Schedule', index=False, header=True)

    # ============================================
    # SHEET 10: CONVERSION ACTIONS
    # ============================================
    conversion_actions = [
        ['Conversion Action', 'Type', 'Priority', 'Notes'],
        ['Google Shopping App - Purchase', 'App / Shopping', 'PRIMARY', ''],
        ['Offline Purchase via Zapier upload', 'Offline', 'PRIMARY', ''],
        ['Add to cart (/cart pageview)', 'Webpage', 'SECONDARY', 'Do NOT make primary - will confuse algorithm'],
        ['Book appointment - In-Store', 'Webpage', 'SECONDARY', ''],
        ['Calls from ads', 'Call', 'SECONDARY', ''],
        ['', '', '', ''],
        ['CRITICAL', '', '', 'Do NOT include Local Directions as conversion - was polluting PMax with 68 fake conversions'],
        ['Feed-only PMax should optimize for', '', '', 'Purchase and offline value only']
    ]
    pd.DataFrame(conversion_actions).to_excel(writer, sheet_name='10. Conversion Actions', index=False, header=True)

    # ============================================
    # SHEET 11: BRAND EXCLUSIONS
    # ============================================
    brand_exclusions = [
        ['Brand Term to Exclude', 'Notes'],
        ['global diamond montreal', ''],
        ['globaldiamondmontreal.com', ''],
        ['global diamond', ''],
        ['doctor diamond', ''],
        ['gdm jewelry', ''],
        ['gdm montreal', ''],
        ['', ''],
        ['Location in UI', 'Campaign Settings -> Brand Exclusions'],
        ['Why', 'Prevents PMax from absorbing branded search queries (should go to Brand Search campaign)']
    ]
    pd.DataFrame(brand_exclusions).to_excel(writer, sheet_name='11. Brand Exclusions', index=False, header=True)

    # ============================================
    # SHEET 12: MOTHER'S DAY PRODUCTS (FROM FEED)
    # ============================================
    products_data = [
        ['Category', 'SKU', 'Product Name', 'Price', 'Compare At', 'CTW'],
        ['EARRINGS', '1100-0030', 'Studs earrings 0.26ct lab-grown diamonds VS F screw back 14k white gold', '$500', '$620', '0.26ct'],
        ['EARRINGS', '1102-0010', 'Studs earrings 0.20 CTW diamonds VS screw back 14k white gold (white + yellow gold)', '$480', '$560', '0.20ct'],
        ['EARRINGS', '1102-0005', 'Lab-grown diamond stud earrings 0.10 CT 14k white gold', '$390', '-', '0.10ct'],
        ['', '', '', '', '', ''],
        ['PENDANTS', '1400-0503', 'Diamond heart pendant 0.32 ctw 14k white gold (chain included)', '$1,300', '$1,600', '0.32ct'],
        ['PENDANTS', '1400-0015', 'Diamond greek key heart pendant 10k white/yellow/rose gold (chain included)', '$1,100', '$1,300', '0.20ct'],
        ['PENDANTS', '1400-0004', 'Exquisite 0.18ct natural diamond halo pendant 14k white/yellow gold (chain included)', '$1,200', '$1,460', '0.18ct'],
        ['PENDANTS', '1400-0013', 'Diamond cross pendant 0.20ct 10k white gold greek key (chain included)', '$1,500', '-', '0.20ct'],
        ['', '', '', '', '', ''],
        ['BRACELETS - DIAMOND', '1070-0013', 'Chic diamond tennis bracelet 1.90 ctw 14k white gold', '$3,360', '$4,200', '1.90ct'],
        ['BRACELETS - GEMSTONE', '1070-0011', 'Diamonds + 9.7ct marquis cut ruby bracelet 14k yellow gold', '$2,080', '-', '9.7ct + diamonds'],
        ['BRACELETS - GEMSTONE', '1070-1012', 'Yellow sapphire + diamond 4.70 ctw bracelet 14k yellow gold', '$2,080', '-', '4.70ct'],
        ['BRACELETS - GEMSTONE', '1073-2950', 'Marquise cut diamonds & ruby bracelet 2.2 ctw white gold', '$2,000', '$2,200', '2.2ct'],
        ['', '', '', '', '', ''],
        ['PRICE RANGE', '', '', '$390 - $3,360', '', ''],
        ['ESTIMATED AOV', '', '', '~$1,500-$1,800', '', 'Earrings pull down, bracelets pull up']
    ]
    pd.DataFrame(products_data).to_excel(writer, sheet_name='12. Products Feed', index=False, header=True)

    # ============================================
    # SHEET 13: PRE-LAUNCH QA CHECKLIST
    # ============================================
    qa_checklist = [
        ['Category', 'Task', 'Status (Done/Pending)', 'Notes'],
        ['FEED + MERCHANT CENTER', 'Confirm all mothers-day-2026 products APPROVED in Merchant Center', '', ''],
        ['FEED + MERCHANT CENTER', 'Confirm product prices in feed match Shopify storefront prices', '', ''],
        ['FEED + MERCHANT CENTER', 'Confirm custom_label_0 = mothers-day-2026 on all intended products', '', 'Check MC -> Products -> All Products'],
        ['FEED + MERCHANT CENTER', 'Confirm Merchant Center feed linked to Google Ads account 7087867966', '', ''],
        ['', '', '', ''],
        ['LISTING GROUPS', 'Campaign listing group set to: Custom Label 0 = mothers-day-2026 (INCLUDE)', '', ''],
        ['LISTING GROUPS', 'Everything else excluded', '', ''],
        ['LISTING GROUPS', 'Product-type sub-segments created and verified', '', ''],
        ['', '', '', ''],
        ['ASSETS - EARRINGS AG', 'All 15 headline slots filled', '', ''],
        ['ASSETS - EARRINGS AG', 'All 5 description slots filled', '', ''],
        ['ASSETS - EARRINGS AG', 'Minimum 1 landscape + 1 square image uploaded', '', ''],
        ['', '', '', ''],
        ['ASSETS - PENDANTS AG', 'All 15 headline slots filled', '', ''],
        ['ASSETS - PENDANTS AG', 'All 5 description slots filled', '', ''],
        ['ASSETS - PENDANTS AG', 'Minimum 1 landscape + 1 square image uploaded', '', ''],
        ['', '', '', ''],
        ['ASSETS - BRACELETS AG', 'All 15 headline slots filled', '', ''],
        ['ASSETS - BRACELETS AG', 'All 5 description slots filled', '', ''],
        ['ASSETS - BRACELETS AG', 'Minimum 1 landscape + 1 square image uploaded', '', ''],
        ['', '', '', ''],
        ['ASSETS - ALL', 'Logo uploaded (GDM brand mark)', '', ''],
        ['ASSETS - ALL', 'Video provided OR note that Google will auto-generate', '', 'FLAG to Doc - auto-generated quality is low'],
        ['ASSETS - ALL', 'Ad strength shows Good or Excellent on all 3 asset groups', '', ''],
        ['', '', '', ''],
        ['EXTENSIONS', '6 sitelinks created with descriptions and URLs', '', ''],
        ['EXTENSIONS', '8 callout extensions added', '', ''],
        ['EXTENSIONS', 'Structured snippet (Types) added', '', ''],
        ['EXTENSIONS', 'Promotion extension (Mother\'s Day) added with correct dates', '', ''],
        ['EXTENSIONS', 'Call extension added (once phone number confirmed)', '', ''],
        ['', '', '', ''],
        ['SETTINGS', 'Brand exclusion list active', '', ''],
        ['SETTINGS', 'Final URL expansion OFF', '', ''],
        ['SETTINGS', 'Conversion goals confirmed: Purchase (primary), Offline Purchase (primary)', '', ''],
        ['SETTINGS', 'Start date: April 16 | End date: May 11', '', ''],
        ['SETTINGS', 'Budget: $45/day for launch', '', ''],
        ['', '', '', ''],
        ['CONFLICT CHECK', 'No other PMax campaign running All Products without exclusions', '', ''],
        ['CONFLICT CHECK', 'Brand Search campaign is active (to capture branded traffic)', '', '']
    ]
    pd.DataFrame(qa_checklist).to_excel(writer, sheet_name='13. Pre-Launch QA', index=False, header=True)

    # ============================================
    # SHEET 14: POST-LAUNCH MONITORING
    # ============================================
    monitoring_schedule = [
        ['Day', 'Date', 'What to Check', 'Action Threshold', 'Notes'],
        ['Day 3', 'Apr 19', 'Impressions, clicks. Are products serving?', 'If 0 impressions: check feed approval status and listing group filter', ''],
        ['Day 7', 'Apr 23', 'Conversion count. Any purchases?', 'If 0 conversions with 200+ clicks: check conversion tracking', ''],
        ['Day 7', 'Apr 23', 'Add tROAS target', 'Only if 5+ conversions. Set at 3.5x', ''],
        ['Day 10', 'Apr 26', 'ROAS vs. 3.5x target', 'If actual ROAS <2x: check CPA for shopping vs. other channels', ''],
        ['Day 10', 'Apr 26', 'Budget increase check', 'If ROAS >4x: increase budget to $65/day early', ''],
        ['May 1', 'May 1', 'Final sprint budget increase', 'Move to $90/day regardless of ROAS', 'Last 10 days are peak intent'],
        ['May 12', 'May 12', 'Post-campaign review', 'Pause campaign. Pull final ROAS, product-level click data', '']
    ]
    pd.DataFrame(monitoring_schedule).to_excel(writer, sheet_name='14. Post-Launch Monitoring', index=False, header=True)

    # ============================================
    # SHEET 15: CAMPAIGN NOTES
    # ============================================
    notes_data = [
        ['Key Notes for This Build', '', ''],
        ['', '', ''],
        ['1. Mother\'s Day 2026 is May 11 (Sunday).', 'Peak shopping traffic is May 1-9.', 'Budget should front-load the final sprint.'],
        ['', '', ''],
        ['2. Price range consideration:', 'Earrings ($390-$500) are lowest friction, will drive most volume.', 'Pendants ($1,100-$1,500) are sweet spot. Bracelets ($2,080-$3,360) are aspirational.'],
        ['', '', 'Watch product-level impressions after day 7 - if bracelets are suppressed, check ROAS target.'],
        ['', '', ''],
        ['3. Free studs offer:', 'GDM offers free diamond studs with purchase ($2,500+ / $3,500+ thresholds).', 'Bracelet and pendant items qualify. Promote in extensions.'],
        ['', '', ''],
        ['4. Bilingual note:', 'This campaign uses English assets only.', 'If budget allows, duplicate asset groups with French copy.'],
        ['', '', 'Target: EN + FR language at campaign level.'],
        ['', '', ''],
        ['5. No video risk:', 'Without real video, Google auto-generates one.', 'Auto-generated video quality is low. Flag to Victor or Ana.'],
        ['', '', 'A 20-second product + gifting video shot on iPhone is better than auto-generation.'],
        ['', '', ''],
        ['6. tROAS Strategy:', 'No tROAS for first 7 days - campaign needs clean learning.', 'Locking 3.5x tROAS on day 1 with zero conversion history will strangle impressions.'],
        ['', '', 'Run Maximize Conversion Value for 7 days, then layer in tROAS once there are 5+ conversions.']
    ]
    pd.DataFrame(notes_data).to_excel(writer, sheet_name='15. Campaign Notes', index=False, header=False)

print(f"Excel file created: {output_file}")
