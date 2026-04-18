# GDM — PMax Mother's Day 2026 Campaign Setup Spec
**Account:** Global Diamond Montreal (7087867966)
**Campaign Name:** Hoski | PMax | Mother's Day 2026 | Feed Only
**Prepared:** 2026-04-16
**Flight:** April 16 – May 11, 2026
**Feed Filter:** `custom_label_0 = mothers-day-2026`

---

## Products in the mothers-day-2026 Feed

All products carry `custom_label_0 = mothers-day-2026` in the Shopify feed. Confirm all are approved and active in Merchant Center before launching.

### Earrings (3 SKUs)

| SKU | Product | Price | Compare At |
|---|---|---|---|
| 1100-0030 | Studs earrings total 0.26ct lab-grown diamonds VS F screw back 14k white gold | $500 | $620 |
| 1102-0010 | Studs earrings total 0.20 CTW diamonds VS screw back 14k white gold (white + yellow gold) | $480 | $560 |
| 1102-0005 | Lab-grown diamond stud earrings total 0.10 CT 14k white gold | $390 | — |

### Pendants / Necklaces (4 SKUs)

| SKU | Product | Price | Compare At |
|---|---|---|---|
| 1400-0503 | Diamond heart pendant 0.32 ctw 14k white gold (chain included) | $1,300 | $1,600 |
| 1400-0015 | Diamond greek key heart pendant 10k white/yellow/rose gold (chain included) | $1,100 | $1,300 |
| 1400-0004 | Exquisite 0.18ct natural diamond halo pendant 14k white/yellow gold (chain included) | $1,200 | $1,460 |
| 1400-0013 | Diamond cross pendant 0.20ct 10k white gold greek key (chain included) | $1,500 | — |

### Bracelets (3+ SKUs confirmed, remainder pending full CSV scan)

| SKU | Product | Price | Compare At |
|---|---|---|---|
| 1070-0013 | Chic diamond tennis bracelet 1.90 ctw 14k white gold | $3,360 | $4,200 |
| 1070-0011 | Diamonds + 9.7ct marquis cut ruby bracelet 14k yellow gold | $2,080 | — |
| 1070-1012 | Yellow sapphire + diamond 4.70 ctw bracelet 14k yellow gold | $2,080 | — |

**Price range across the feed: $390 – $3,360**
**AOV estimate: ~$1,500–1,800 (earrings pull down, bracelets pull up)**

---

## Campaign Settings

| Setting | Value |
|---|---|
| Campaign type | Performance Max |
| Campaign name | Hoski \| PMax \| Mother's Day 2026 \| Feed Only |
| Goal | Sales — Online Purchase (Shopify) |
| Bid strategy | Maximize Conversion Value — no tROAS target for first 7 days |
| tROAS target (after day 7) | 3.5x (aligned to account ROAS target) |
| Daily budget | $45/day (Weeks 1–2) → $65/day (Week 3, Apr 25) → $90/day (Final sprint May 1–11) |
| Start date | April 16, 2026 |
| End date | May 11, 2026 |
| Locations | Canada — all provinces |
| Languages | English + French |
| Final URL expansion | OFF — all traffic to collection page or product pages only |
| Brand exclusions | Global Diamond Montreal, globaldiamondmontreal.com, Global Diamond, Doctor Diamond, GDM Jewelry, gdm jewelry |
| Ad schedule | All days / all hours |
| Merchant Center feed | Linked — filter by custom_label_0 = mothers-day-2026 |
| Inventory filter | Custom Label 0 equals "mothers-day-2026" |

**Why no tROAS for first 7 days:** The campaign needs clean learning. Locking a 3.5x tROAS target on day 1 on a new campaign with zero conversion history for this feed will strangle impressions. Run Maximize Conversion Value for 7 days, then layer in the tROAS target once there are 5+ conversions from this campaign.

---

## Listing Group Setup (Shopping Inventory Filter)

**Location in UI:** Campaign → Asset Groups → Listing Groups

Set the listing group on the campaign level to subdivide ONLY products tagged `mothers-day-2026` in `custom_label_0`. Do not use "All Products" — this campaign should only serve the Mother's Day feed.

### Listing Group Tree

```
All Products
└── Custom Label 0 = mothers-day-2026 [INCLUDE — bid everything]
    ├── Product Type = Diamond Studs [segment — earrings]
    ├── Product Type = Diamond Pendant [segment — pendants/necklaces]
    ├── Product Type = Diamond Bracelets [segment — diamond bracelets]
    └── Product Type = Gemstone Bracelets [segment — ruby + sapphire bracelets]
└── Everything else [EXCLUDE]
```

**Why segment by product type:** Allows monitoring impression + click share by category. If earrings ($390–$500) are absorbing all impressions because of lower price point friction, you can identify the pattern and adjust ROAS targets per asset group.

---

## Asset Groups

Run three asset groups — one per product category. Each gets its own landing URL, themed creative, and audience signal stack. This allows Google to surface category-relevant creative to category-relevant searchers.

---

### Asset Group 1: Diamond Earrings — Mother's Day

**Final URL:** `https://globaldiamondmontreal.com/collections/diamond-earrings`
_(Confirm this collection page exists and filters correctly. If not, use individual product URLs or build a Mother's Day earrings collection page.)_

**Listing group filter:** Product Type = Diamond Studs (custom_label_0 = mothers-day-2026)

#### Headlines (15 — use all 15 slots)

1. Diamond Earrings for Mom
2. Lab-Grown Diamond Studs
3. Mother's Day Diamond Gift
4. 14K Gold Diamond Studs
5. Diamond Stud Earrings Canada
6. Free Shipping. 30-Day Returns.
7. Manufacturer Price — No Markup
8. Global Diamond Montreal
9. Since 1982 — 40+ Years
10. From $390 — Real Diamonds
11. Diamond Earrings Gift for Her
12. White Gold Diamond Studs
13. VS Clarity. F Color. Certified.
14. Gift-Wrapped Free
15. Mother's Day — Shop Now

#### Descriptions (5 — use all 5 slots)

1. Real diamonds, manufacturer pricing. Studs starting at $390 in 14k gold. Free Canadian shipping. Perfect gift for Mom.
2. Lab-grown or natural diamond studs from $390. Gift-wrapped. Ships within 14 business days. 30-day returns.
3. Global Diamond Montreal — manufacturer since 1982. No retail markup. VS clarity, F color diamond studs for Mother's Day.
4. Diamond studs in white or yellow gold. 0.10ct to 0.26ct. Free gift packaging included. Buy direct from the manufacturer.
5. Give Mom real diamonds this Mother's Day. Manufacturer pricing means better quality for the same money. Ships across Canada.

#### Images

Provide the following image formats (minimum):
- 1.91:1 landscape (1200×628): Product on white background — diamond studs
- 1:1 square (1200×1200): Product lifestyle — earrings worn or in gift box
- 4:5 portrait (960×1200): Gift occasion image — if available

**Image sourcing:** Use existing product images from SKUs 1100-0030, 1102-0010, 1102-0005. Request lifestyle shots from Ana or Doc if product-on-white-background-only images are all that's available.

#### Video

If no video exists: request a 15–30 second vertical video from Victor showing the earrings in a gift context. Without a real video, Google auto-generates from static images — quality is significantly worse. Minimum: provide a YouTube link to any existing GDM video (even general brand video is better than auto-generated).

---

### Asset Group 2: Diamond Pendants — Mother's Day

**Final URL:** `https://globaldiamondmontreal.com/collections/diamond-pendants`
_(Confirm this URL. Alternatively: `globaldiamondmontreal.com/collections/pendants` — verify in Shopify.)_

**Listing group filter:** Product Type = Diamond Pendant (custom_label_0 = mothers-day-2026)

#### Headlines (15)

1. Diamond Necklace for Mom
2. Heart Pendant — Mother's Day Gift
3. 14K Gold Diamond Pendant
4. Diamond Heart Necklace Canada
5. Gold Necklace Gift for Her
6. Chain Included — Ready to Gift
7. Manufacturer Price — No Markup
8. Diamond Pendant from $1,100
9. Natural Diamond Pendants
10. Free Shipping Across Canada
11. Global Diamond Montreal
12. Greek Key Diamond Pendant
13. Since 1982 — Fine Jewelry
14. Gift-Wrapped Free. Ships Fast.
15. Mother's Day — Shop Pendants

#### Descriptions (5)

1. Diamond heart pendants from $1,100. Chain included. Gift-wrapped free. Ships across Canada. 30-day money-back guarantee.
2. Natural and lab-grown diamond pendants in 10k and 14k gold. Manufacturer pricing — no retail markup. Mother's Day collection.
3. Global Diamond Montreal — manufacturer since 1982. Heart, cross, and halo diamond pendants. Free Canadian shipping.
4. Give Mom a diamond pendant with chain included — ready to gift. Prices from $1,100. Ships within 14 business days.
5. Heart, greek key, and halo diamond pendants. White, yellow, and rose gold. Buy direct from the manufacturer since 1982.

#### Images

- 1.91:1 landscape: Heart pendant product on white or lifestyle
- 1:1 square: Pendant close-up or worn lifestyle
- Portrait 4:5: Gift occasion / flatlay if available

**Recommended hero image:** SKU 1400-0503 (diamond heart pendant — the heart motif is the strongest Mother's Day visual).

---

### Asset Group 3: Diamond Bracelets — Mother's Day

**Final URL:** `https://globaldiamondmontreal.com/collections/diamond-bracelets`

**Listing group filter:** Product Type = Diamond Bracelets + Gemstone Bracelets (custom_label_0 = mothers-day-2026)

#### Headlines (15)

1. Diamond Bracelet for Mom
2. Tennis Bracelet — Mother's Day
3. Diamond Tennis Bracelet Canada
4. Gemstone Bracelet Gift for Her
5. 14K Gold Tennis Bracelet
6. Manufacturer Price — No Markup
7. Diamond Bracelets from $2,080
8. Ruby + Diamond Gold Bracelet
9. Sapphire + Diamond Bracelet
10. Free Shipping. 30-Day Returns.
11. Global Diamond Montreal
12. Fine Diamond Bracelet Since 1982
13. Tennis Bracelet 1.90 CTW
14. Gift-Wrapped. Ships Across Canada.
15. Mother's Day — Shop Bracelets

#### Descriptions (5)

1. Diamond tennis bracelets and gemstone bracelets from $2,080. 14k gold. Free Canadian shipping. 30-day returns.
2. Natural diamond tennis bracelets in white gold. Ruby and sapphire gemstone bracelets in yellow gold. Manufacturer pricing.
3. Global Diamond Montreal — manufacturer since 1982. 1.90ctw tennis bracelet. 9.7ct ruby bracelet. Ships across Canada.
4. Give Mom a diamond or gemstone bracelet this Mother's Day. Prices from $2,080 in 14k gold. Free gift-wrapping included.
5. Manufacturer-direct diamond and gemstone bracelets. No retail markup. White and yellow gold. Buy from Global Diamond Montreal.

#### Images

- 1.91:1 landscape: Tennis bracelet (SKU 1070-0013) — strongest visual, white gold on white bg
- 1:1 square: Bracelet worn on wrist lifestyle
- 4:5 portrait: Flatlay or gift occasion — bracelet in box

---

## Search Themes

Search themes signal to Google's algorithm what intent categories to target on Search. These are not keywords — they are themes that guide impression matching. Add all of the following under Campaign → Search themes.

**Note:** Max 25 search themes per asset group. Distribute across asset groups as shown.

### Asset Group 1 — Earrings Search Themes (15)

1. mothers day diamond earrings
2. diamond stud earrings gift
3. lab grown diamond studs canada
4. mothers day earring gift ideas
5. diamond earrings for mom
6. 14k gold stud earrings canada
7. diamond stud earrings mothers day
8. gift diamond earrings women
9. earrings for mom mothers day
10. white gold diamond stud earrings
11. diamond earring gift canada
12. mothers day jewellery earrings
13. mothers day gift fine jewelry
14. best jewelry gift for mom
15. real diamond earrings canada

### Asset Group 2 — Pendants Search Themes (15)

1. mothers day diamond necklace
2. heart pendant mothers day gift
3. diamond heart necklace canada
4. gold necklace gift for mom
5. mothers day necklace pendant
6. diamond pendant necklace gift
7. necklace for mom mothers day
8. heart necklace diamond gift
9. mothers day jewellery necklace
10. gold diamond necklace canada
11. diamond pendant gift ideas
12. personalized jewelry for mom
13. fine jewelry necklace canada
14. mothers day gift ideas jewelry
15. necklace gift for her canada

### Asset Group 3 — Bracelets Search Themes (15)

1. mothers day diamond bracelet
2. tennis bracelet mothers day gift
3. diamond tennis bracelet canada
4. gemstone bracelet gift for mom
5. mothers day bracelet gift
6. ruby diamond bracelet gift
7. gold bracelet mothers day
8. mothers day bracelets montreal
9. diamond bracelet for women canada
10. fine jewelry bracelet gift
11. tennis bracelet canada
12. sapphire diamond bracelet gift
13. mothers day luxury jewelry gift
14. gemstone bracelet women
15. bracelet gift for mom canada

---

## Audience Signals

Add to ALL three asset groups. These are signals, not targeting — Google will expand beyond them.

### Signal 1: Website Visitors (Custom Audience)

**Audience:** All website visitors — globaldiamondmontreal.com — last 90 days
**Where to add:** Existing remarketing list if tagged via Google tag. Minimum 100 users required for PMax to accept it.

### Signal 2: Customer Match List

**Audience:** Existing customer email list from Shopify/GHL
**Action:** Export customer emails from Shopify admin → upload to Google Ads Audience Manager → Customer Match. Requires minimum 1,000 matched emails.
**Owner to action:** Bishal / Faseeh

### Signal 3: Custom Intent — Gift Buyer Search Signals

**Create a custom audience with these search terms (Customer Intent audience in Google Ads):**

Paste these into a new Custom Segment (Audience Manager → Custom Segments → People with any of these interests or purchase intentions):

- mothers day jewelry gift
- mothers day gift ideas canada
- diamond earrings mothers day
- heart pendant necklace gift
- tennis bracelet mothers day
- jewelry gift for mom canada
- diamond bracelet gift women
- diamond necklace gift canada
- mothers day fine jewelry
- gold jewelry gift for her
- lab grown diamond earrings
- diamond studs gift
- fine jewelry mothers day
- jewellery gift mom
- best gift for mom 2026

**Also add URLs the audience might visit:**
- pandora.net/en-ca/mothers-day (competitor — intent signal)
- brilliant earth mothersday collection URL (intent signal)

### Signal 4: In-Market Audiences

Add all of the following:
- In-market: Jewelry & Watches (Jewelry > Fine Jewelry)
- In-market: Gift Shoppers (Occasions > Mother's Day gifts — if available in Canada)
- In-market: Luxury Goods
- Life event: New parent (catches recent moms buying for grandmothers)

### Signal 5: Interest + Demographics Layering

- Age: 25–65 (gift buyers — adults buying for their mothers)
- Gender: All (male gift buyers are a major segment for Mother's Day jewelry)
- Household income: Top 50% (aligns with $390–$3,360 price range)
- Interest: Fashion & Jewelry enthusiasts, Luxury Shoppers

---

## Extensions (Ad Assets)

Set at the campaign level. All extensions apply to all asset groups.

---

### Sitelinks (6 minimum)

| Sitelink Text | Description Line 1 | Description Line 2 | URL |
|---|---|---|---|
| Diamond Earrings | Lab-grown & natural diamond studs | 14k gold from $390 | /collections/diamond-earrings |
| Diamond Necklaces | Heart & halo diamond pendants | Chain included. From $1,100. | /collections/pendants |
| Diamond Bracelets | Tennis & gemstone bracelets | 14k gold from $2,080 | /collections/diamond-bracelets |
| Free Diamond Studs Offer | Free 0.26ct studs with $2,500+ | Free 0.50ct studs with $3,500+ | /pages/free-diamond-offer (or homepage if page doesn't exist) |
| Shop All Mother's Day Gifts | Earrings, pendants, bracelets | Gift-wrapped. Ships across Canada. | /collections (or create Mother's Day collection page) |
| Book an Appointment | Visit our Montreal showroom | See the full collection in person | /pages/appointment-1 |

---

### Callout Extensions (8)

1. Free Canadian Shipping
2. 30-Day Money-Back Guarantee
3. Manufacturer Pricing — No Markup
4. Since 1982 — 40+ Years
5. Natural + Lab-Grown Diamonds
6. Free Gift Packaging
7. Sourced from 12 Countries
8. Ships Within 14 Business Days

---

### Structured Snippets

**Header:** Types
**Values:**
- Diamond Earrings
- Heart Pendants
- Tennis Bracelets
- Ruby Bracelets
- Lab-Grown Diamonds
- Gold Necklaces

---

### Promotion Extension

**Promotion:** Mother's Day
**Promotion type:** Free gift with purchase (or Percent off)
**Details:** Free diamond studs with $2,500+ purchase
**Occasion:** Mother's Day
**Start:** April 16, 2026
**End:** May 11, 2026

---

### Call Extension

**Phone:** GDM main number (confirm with Doc — not listed in brief)
**Call schedule:** Business hours Monday–Saturday

---

### Image Extensions

Upload the following assets as image extensions at campaign level:
- Landscape (1.91:1): Diamond heart pendant lifestyle
- Square (1:1): Diamond stud earrings on white
- Portrait (4:5): Tennis bracelet if available

---

## Budget Schedule

| Phase | Dates | Daily Budget | Rationale |
|---|---|---|---|
| Learning phase | Apr 16–22 | $45/day | No tROAS target. Let algorithm learn. No changes. |
| Scale phase | Apr 23–30 | $65/day | +44% increase if ROAS ≥ 2.5x after day 7. Add tROAS target of 3.5x. |
| Final sprint | May 1–11 | $90/day | Peak Mother's Day intent. Budget spike aligned to gift-buying urgency. |

**Total campaign spend estimate:**
- Apr 16–22: $315
- Apr 23–30: $520
- May 1–11: $990
- **Total: ~$1,825**

This fits within the $2,500/month Mother's Day overlay budget from the three-lever strategy doc (remainder goes to Search EN+FR).

---

## Conversion Actions

Ensure all of the following are set as Primary conversions on this campaign:

| Conversion Action | Type | Priority |
|---|---|---|
| Google Shopping App — Purchase | App / Shopping | Primary |
| Offline Purchase via Zapier upload | Offline | Primary |
| Add to cart (/cart pageview) | Webpage | Secondary (do NOT make primary — will confuse algorithm) |
| Book appointment — In-Store | Webpage | Secondary |
| Calls from ads | Call | Secondary |

**Critical:** Do NOT include Local Directions as a conversion here. That was polluting PMax Local with 68 fake "conversions." Feed-only PMax should optimize for purchase and offline value only.

---

## Brand Exclusion List

Add before launch. Location: Campaign settings → Brand exclusions.

| Brand Term to Exclude |
|---|
| global diamond montreal |
| globaldiamondmontreal.com |
| global diamond |
| doctor diamond |
| gdm jewelry |
| gdm montreal |

This prevents the PMax campaign from absorbing branded search queries (which should be going to the Brand Search campaign).

---

## Pre-Launch QA Checklist

Complete every item before setting campaign to ENABLED.

### Feed + Merchant Center

- [ ] Confirm all mothers-day-2026 custom_label_0 products are APPROVED in Merchant Center (no disapprovals)
- [ ] Confirm product prices in feed match Shopify storefront prices
- [ ] Confirm "mothers-day-2026" custom label is populated on all intended products (check Merchant Center → Products → All Products → filter by custom label)
- [ ] Confirm Merchant Center feed linked to Google Ads account 7087867966

### Listing Groups

- [ ] Campaign listing group set to: Custom Label 0 = mothers-day-2026 (INCLUDE)
- [ ] Everything else excluded
- [ ] Product-type sub-segments created and verified

### Assets

- [ ] All 15 headline slots filled per asset group (45 total across 3 asset groups)
- [ ] All 5 description slots filled per asset group (15 total)
- [ ] Minimum 1 landscape + 1 square image per asset group (6 images total)
- [ ] Logo uploaded (GDM brand mark)
- [ ] Video provided OR note that Google will auto-generate (flag this to Doc — auto-generated video quality is low)
- [ ] Ad strength shows "Good" or "Excellent" on all 3 asset groups before launch

### Extensions

- [ ] 6 sitelinks created with descriptions and URLs
- [ ] 8 callout extensions added
- [ ] Structured snippet (Types) added
- [ ] Promotion extension (Mother's Day) added with correct dates
- [ ] Call extension added (once phone number confirmed)

### Settings

- [ ] Brand exclusion list active
- [ ] Final URL expansion OFF
- [ ] Conversion goals confirmed: Purchase (primary), Offline Purchase (primary), all others secondary
- [ ] Start date: April 16 | End date: May 11
- [ ] Budget: $45/day for launch

### Conflict Check

- [ ] Confirm no other PMax campaign is running "All Products" without exclusions that would compete with this campaign's feed
- [ ] Confirm brand Search campaign is active as a separate campaign (to capture branded traffic this PMax will not receive due to exclusions)

---

## Post-Launch Monitoring Schedule

| Day | What to Check | Action Threshold |
|---|---|---|
| Day 3 (Apr 19) | Impressions, clicks. Are products serving? | If 0 impressions: check feed approval status and listing group filter. |
| Day 7 (Apr 23) | Conversion count. Any purchases? | If 0 conversions with 200+ clicks: check conversion tracking. If <5 conversions: hold at Maximize Conv Value, no tROAS yet. |
| Day 7 (Apr 23) | Add tROAS target | Only if 5+ conversions. Set at 3.5x. |
| Day 10 (Apr 26) | ROAS vs. 3.5x target | If actual ROAS <2x: check CPA for shopping vs. other channels. If ROAS >4x: increase budget to $65/day. |
| May 1 | Final sprint budget increase | Move to $90/day regardless of ROAS — last 10 days are peak intent, accept more spend. |
| May 12 | Post-campaign review | Pause campaign. Pull final ROAS, product-level click data, search term categories. |

---

## Notes for This Build

1. **Mother's Day 2026 is May 11 (Sunday).** Peak shopping traffic is May 1–9. Budget should front-load the final sprint.
2. **Price range consideration:** The earrings ($390–$500) are the lowest friction items and will likely drive the most volume. Pendants ($1,100–$1,500) are the sweet spot for Mother's Day gifting. Bracelets ($2,080–$3,360) are aspirational. Watch product-level impressions after day 7 — if bracelets are suppressed, check whether the ROAS target is too aggressive for those price points.
3. **Free studs offer:** GDM offers free diamond studs with purchase ($2,500+ / $3,500+ thresholds). The bracelet and pendant items qualify. This should be prominent in the promotion extension and callout — it's a genuine differentiator no competitor runs.
4. **Bilingual note:** This campaign uses English assets only. If budget allows, duplicate asset groups with French copy (same product structure, French headlines/descriptions). Target: Lever 3 of the strategy doc allocated $50/day to FR search — PMax can serve both EN and FR if language targeting is set to EN + FR at campaign level.
5. **No video risk:** Without a real video, Google auto-generates one. The auto-generated video is low quality and may suppress Performance Max on YouTube placements. Flag this to Victor or Ana — a 20-second product + gifting video shot on iPhone is dramatically better than auto-generation.
