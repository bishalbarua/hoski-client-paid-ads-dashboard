# Park Road Custom Furniture — Complete Campaign Setup Sheet
**Client:** Park Road Custom Furniture and Decor
**Account ID:** 7228467515
**Prepared by:** Bishal
**Date:** 2026-03-31
**Campaigns:** hoski_custom_furniture_search_1apr26 | hoski_cottage_furniture_search_1apr26

> **STATUS:** Pre-launch. Do not activate campaigns until all prerequisites in the Campaign Launch Brief are confirmed. See `campaign-launch-brief.md` for the full checklist.

---

## TABLE OF CONTENTS

1. [Account-Level Setup](#account-level-setup)
2. [Conversion Actions](#conversion-actions)
3. [Campaign 1: Custom Furniture](#campaign-1-custom-furniture)
4. [Campaign 2: Cottage Furniture](#campaign-2-cottage-furniture)
5. [Assets — Both Campaigns](#assets-both-campaigns)
6. [Image Assets Summary](#image-assets-summary)
7. [Launch Sequence](#launch-sequence)

---

## ACCOUNT-LEVEL SETUP

### Shared Negative Keyword List

**Name:** `Park Road — Account Level Negatives`
**Apply to:** Both campaigns.

**Broad match negatives:**
```
jobs
careers
hiring
how to
tutorial
diy
do it yourself
free
used
second hand
vintage
antique
thrift
repair
refinish
reupholster
plans
template
blueprint
school
course
degree
training
class
```

**Phrase match negatives (add at campaign level if shared list does not support phrase match):**
```
"tepperman"
"lazy boy"
"lazyboy"
"ikea"
"ashley furniture"
"wayfair"
"structube"
"rooms to go"
"wholesale"
"discount"
"cheap"
"outlet"
"clearance"
"rental"
"rent to own"
"kitchen cabinet"
"bathroom vanity"
"mattress"
"appliance"
"flooring"
"outdoor furniture"
"patio furniture"
"garden furniture"
"garden bench"
"picnic table"
```

---

## CONVERSION ACTIONS

All URL-based. Requires base Google Tag (gtag) firing on `go.parkroadfurniture.com`. Verify in Tag Assistant before creating.

| Conversion Name | URL Match Rule | Type | Designation | Value | Count | Attribution |
|---|---|---|---|---|---|---|
| `CF - Form Submission` | URL contains `/custom-furniture/thank-you` | Website | **Primary** | Not set | One | 30-day click, 1-day view |
| `CF - Consultation Booked` | URL contains `/custom-furniture/consultation-booked` | Website | Secondary | Not set | One | 30-day click, 1-day view |
| `Cottage - Form Submission` | URL contains `/cottage-furniture/thank-you` | Website | **Primary** | Not set | One | 30-day click, 1-day view |
| `Cottage - Consultation Booked` | URL contains `/cottage-furniture/consultation-booked` | Website | Secondary | Not set | One | 30-day click, 1-day view |

**Notes:**
- Keep CF and Cottage conversion actions separate. Do not merge.
- Primary conversions are the KPIs Smart Bidding will optimize toward. Secondary are tracked only.
- After setup: submit a test form on each landing page and verify the conversion fires within 24 hours in Google Ads conversion diagnostics.
- Apply `CF - Form Submission` as the conversion goal for Campaign 1.
- Apply `Cottage - Form Submission` as the conversion goal for Campaign 2.

---

## CAMPAIGN 1: CUSTOM FURNITURE

### Campaign Settings

| Setting | Value |
|---|---|
| Campaign name | `hoski_custom_furniture_search_1apr26` |
| Campaign type | Search |
| Goal | Leads |
| Networks | Search Network only (uncheck Display Network and Search Partners) |
| Bidding strategy | Maximize Clicks |
| Max CPC bid limit | $5.00 |
| Daily budget | $20–27/day ($600–$800/month) |
| Geo targeting | London ON, Kitchener ON, Waterloo ON, Windsor ON, Guelph ON, Woodstock ON, Sarnia ON, St. Thomas ON |
| Language | English |
| Ad schedule | All days, all hours (review at 30 days) |
| Ad rotation | Optimize (Prefer best performing ads) |
| Conversion goals | `CF - Form Submission` (primary), `CF - Consultation Booked` (secondary) |

**Bidding note:** Start on Maximize Clicks to build impression and click data. Once the account has 30+ `CF - Form Submission` conversions (4–8 weeks), switch to Target CPA. Initial Target CPA estimate: $60–$80 per lead.

---

### Ad Group Structure (Campaign 1)

| Priority | Ad Group Name | Theme | Launch Phase |
|---|---|---|---|
| 1 | `custom_furniture_core` | Direct custom intent | Launch day |
| 2 | `furniture_store_london` | Local discovery intent | Launch day |
| 3 | `dining_room` | Dining room buyers | Week 1 |
| 4 | `canadian_made_solid_wood` | Quality-conscious buyers | Week 1 |
| 5 | `living_and_bedroom` | Living room and bedroom buyers | Week 2 |
| 6 | `entertainment_and_storage` | Built-ins and storage | Phase 2 (30+ days) |

---

### C1 — Ad Group 1: custom_furniture_core

**Launch phase:** Day 1
**Theme:** Direct custom-built furniture intent — highest-quality clicks in this market.

**Keywords:**

| Keyword | Match Type | Vol/mo | CPC Range |
|---|---|---|---|
| [custom furniture london ontario] | Exact | 30 | $0.67–$1.73 |
| "custom furniture london ontario" | Phrase | 30 | $0.67–$1.73 |
| [custom furniture near me] | Exact | 10 | — |
| "custom furniture near me" | Phrase | 10 | — |
| [custom made furniture] | Exact | 10 | — |
| "custom made furniture" | Phrase | 10 | — |
| [custom built furniture] | Exact | 10 | — |
| [bespoke furniture] | Exact | 10 | — |
| [handcrafted furniture] | Exact | 10 | — |
| [custom wood furniture] | Exact | 10 | — |

**Ad group negatives:**

| Negative | Match Type |
|---|---|
| [discount] | Exact |
| [cheap] | Exact |
| [used] | Exact |

**RSA — Primary Ad:**

*Headlines (15):*
1. Custom Furniture London ON
2. $750 Off First Custom Order
3. Built to Order in London ON
4. Canadian Hardwood Furniture
5. Built to Your Exact Specs
6. Free In-Home Consultation
7. Made-to-Measure for Any Room
8. Hand-Finished in London ON
9. Delivered in 6 to 12 Weeks
10. Dining Tables Beds Custom Made
11. Real Wood Not Big-Box Quality
12. Custom Size Finish and Design
13. Claim $750 Off $5000 or More
14. Furniture That Lasts Decades
15. Perfect Fit for Every Room

*Descriptions (4):*
1. Custom furniture built to order in solid hardwood. Free in-home consultation available.
2. Stop settling for furniture that almost fits. Custom size and finish. $750 off $5,000+.
3. Dining tables, sofas, beds, all built to order in London, ON. Book a consultation today.
4. In-home consultations available. We measure and build to fit. Delivered in 6 to 12 weeks.

*Final URL:* `https://go.parkroadfurniture.com/custom-furniture`

---

### C1 — Ad Group 2: furniture_store_london

**Launch phase:** Day 1
**Theme:** Local discovery — highest volume in this market (1,900+/mo).

**Keywords:**

| Keyword | Match Type | Vol/mo | CPC Range |
|---|---|---|---|
| [furniture store london ontario] | Exact | 1,900 | $0.70–$2.59 |
| "furniture store london ontario" | Phrase | 1,900 | $0.70–$2.59 |
| [furniture stores london ontario] | Exact | 1,900 | $0.70–$2.59 |
| [best furniture stores london ontario] | Exact | 70 | $0.89–$2.55 |
| [furniture london ontario] | Exact | 140 | $0.89–$3.48 |
| "local furniture store" | Phrase | 10 | — |

**Ad group negatives:**

| Negative | Match Type | Reason |
|---|---|---|
| [discount] | Exact | Price-shoppers |
| [cheap] | Exact | Price-shoppers |
| [used] | Exact | Wrong intent |
| [outlet] | Exact | Wrong intent |
| [custom] | Exact | Route to Ad Group 1 |
| [solid wood] | Exact | Route to Ad Group 4 |
| [tepperman] | Exact | Competitor brand |
| [lazy boy] | Exact | Competitor brand |
| [lazyboy] | Exact | Competitor brand |

**RSA:**

*Headlines (15):*
1. Furniture Store London Ontario
2. London's Custom Furniture Shop
3. $750 Off First Custom Order
4. Not Your Average Furniture Co
5. Built to Order Not Off Floor
6. Custom Furniture London ON
7. Solid Wood Furniture London ON
8. Free Design Consultation
9. Custom Dining Tables and Beds
10. Hand-Finished by Local Makers
11. Claim $750 Off $5000 or More
12. Canadian-Made Custom Furniture
13. Skip Showroom Build to Spec
14. Every Piece Fits Your Space
15. Furniture Store London Custom

*Descriptions (4):*
1. We build every piece to order in solid Canadian hardwood. Book a consultation today.
2. London custom furniture. $750 off first order of $5,000+. Dining tables to bedroom sets.
3. Furniture store in London ON. Custom size, custom finish. Free design consultation.
4. Solid wood, custom-built in London ON. No flat-pack. Free consultation. $750 off $5,000+.

*Final URL:* `https://go.parkroadfurniture.com/custom-furniture`

---

### C1 — Ad Group 3: dining_room

**Launch phase:** Week 1
**Theme:** Dining room buyers — solid wood tables, custom sizing.

**Keywords:**

| Keyword | Match Type | Vol/mo | CPC Range |
|---|---|---|---|
| [custom dining table] | Exact | 10 | — |
| "custom dining table" | Phrase | 10 | — |
| [wooden dining table] | Exact | 40 | $0.76–$1.51 |
| [solid wood dining table] | Exact | 20 | $0.47–$2.03 |
| [wooden dining room table] | Exact | 40 | $0.76–$1.51 |
| [round wooden dining table] | Exact | 20 | $0.71–$1.38 |
| [natural wood dining table] | Exact | 10 | — |
| [solid oak dining table] | Exact | 10 | — |
| [solid wood dining room table] | Exact | 20 | $0.47–$2.03 |

**Ad group negatives:**

| Negative | Match Type | Reason |
|---|---|---|
| [chair] | Exact | Route to separate group if added |
| [bar stool] | Exact | Low ticket, not custom |

**RSA:**

*Headlines (15):*
1. Custom Dining Tables London ON
2. Built to Your Exact Dimensions
3. $750 Off Orders of $5000 Plus
4. Solid Wood Dining Tables ON
5. Dining Tables Built to Order
6. Free Design Consultation
7. Wide Plank Tables Any Size
8. Canadian Hardwood Dining Table
9. Custom Size Wood and Finish
10. Seats 6 to 12 Built to Order
11. Hand-Finished in London ON
12. Oak Walnut Maple Custom Tables
13. Custom Dining Room Furniture
14. Delivered Across SW Ontario
15. Claim $750 Off Custom Order

*Descriptions (4):*
1. Custom dining tables, any size and finish. Book a consultation. $750 off first order.
2. Stop settling for a table that almost fits. Built to exact dimensions. $750 off $5,000+.
3. Round or wide plank, we build dining tables to your specs. Solid hardwood, 6 to 12 weeks.
4. Custom dining tables for London and SW Ontario. Choose wood, size, finish. Free consult.

*Final URL:* `https://go.parkroadfurniture.com/custom-furniture`

---

### C1 — Ad Group 4: canadian_made_solid_wood

**Launch phase:** Week 1
**Theme:** Quality-conscious buyers who care about origin and materials.

**Keywords:**

| Keyword | Match Type | Vol/mo | CPC Range |
|---|---|---|---|
| [canadian made furniture] | Exact | 30 | $0.67–$2.22 |
| [canadian built furniture] | Exact | 30 | $0.67–$2.22 |
| [canadian furniture] | Exact | 30 | $0.66–$2.68 |
| "canadian made furniture" | Phrase | 30 | $0.67–$2.22 |
| [solid wood furniture] | Exact | 10 | $0.46–$1.71 |
| [real wood furniture] | Exact | 10 | — |
| [solid wood dining table] | Exact | 20 | $0.47–$2.03 |
| [couches made in canada] | Exact | 30 | $0.67–$2.22 |
| [sofa made in canada] | Exact | 20 | $0.83–$2.51 |

**RSA:**

*Headlines (15):*
1. Canadian-Made Furniture London
2. Built in London ON Workshop
3. $750 Off Orders of $5000 Plus
4. Not Imported Not Flat-Pack
5. Real Solid Wood Built to Last
6. Custom Built in London Ontario
7. Free In-Home Consultation
8. Canadian Hardwood Furniture ON
9. Solid Wood Not Big-Box Quality
10. Claim $750 Off Custom Order
11. Custom Made by Local Craftsmen
12. Built to Order Not the Floor
13. Sofas Beds Tables Canada Made
14. Furniture That Lasts Decades
15. Hand-Finished in London ON

*Descriptions (4):*
1. Built in London ON using solid hardwood. No flat-pack, no imports. Claim $750 off $5,000.
2. Canadian-made, real solid wood. No particle board, no veneers. Custom size and finish.
3. Canadian-made solid hardwood furniture, built to your specs. $750 off your first order.
4. Dining tables, sofas, bedroom sets, all built in solid Canadian hardwood. Free consult.

*Final URL:* `https://go.parkroadfurniture.com/custom-furniture`

---

### C1 — Ad Group 5: living_and_bedroom

**Launch phase:** Week 2
**Theme:** Living room and bedroom buyers — sofas, bed frames, bedroom sets.

**Keywords:**

| Keyword | Match Type | Vol/mo | CPC Range |
|---|---|---|---|
| [custom sofa] | Exact | 10 | — |
| [custom couch] | Exact | 10 | $0.46–$2.32 |
| [custom sectional sofa] | Exact | 10 | — |
| [custom coffee table] | Exact | 10 | — |
| [wooden coffee table] | Exact | 70 | $0.50–$1.44 |
| [solid wood coffee table] | Exact | 10 | $0.53–$1.67 |
| [custom bedroom furniture] | Exact | 10 | — |
| [wooden bed frame] | Exact | 90 | $0.47–$1.64 |
| [solid wood bed frame] | Exact | 10 | $0.91–$2.79 |
| [wooden bed frame queen] | Exact | 20 | $0.83–$5.46 |
| [solid wood bed] | Exact | 10 | $0.97–$3.32 |

**Ad group negatives:**

| Negative | Match Type | Reason |
|---|---|---|
| [dining] | Exact | Route to Dining Room group |
| [table] | Exact | Route to Dining Room (monitor coffee table in search terms) |

**RSA:**

*Headlines (15):*
1. Custom Sofas and Beds London
2. Custom Bedroom Furniture ON
3. $750 Off Orders of $5000 Plus
4. Custom Sofas to Your Specs
5. Solid Wood Bed Frames to Order
6. Free In-Home Consultation
7. Custom Sectionals and Sofas ON
8. Built for Your Exact Room Size
9. Solid Wood Beds Bedroom Sets
10. Canadian-Made Bedroom Pieces
11. Claim $750 Off Custom Order
12. Built to Order in London ON
13. Sofas Beds Frames Custom Made
14. Bedroom Sets to Your Style
15. Hand-Finished in London ON

*Descriptions (4):*
1. Custom sofas and beds built to order in solid hardwood. Free consult. $750 off $5,000+.
2. Stop settling. We build to exact dimensions. Solid wood, custom finish, 6 to 12 weeks.
3. Custom sofas, beds, and bedroom sets built in London ON. Free consult. $750 off $5,000+.
4. Living room and bedroom furniture in solid hardwood. Custom size and finish. $750 off.

*Final URL:* `https://go.parkroadfurniture.com/custom-furniture`

---

### C1 — Ad Group 6: entertainment_and_storage (Phase 2)

**Launch phase:** Day 30+ (activate if budget allows and Ad Groups 1–5 are pacing well)
**Theme:** Custom built-ins and entertainment units.

**Keywords:**

| Keyword | Match Type |
|---|---|
| [custom entertainment unit] | Exact |
| [custom entertainment center] | Exact |
| [built in entertainment center] | Exact |
| [custom bookshelves] | Exact |
| [custom bookcase] | Exact |
| [solid wood bookcase] | Exact |
| [solid wood tv stand] | Exact |

**RSA angle:** "Custom Entertainment Units, Built-Ins and Storage — London, ON"
Build RSA at activation using same structure as other ad groups.

---

## CAMPAIGN 2: COTTAGE FURNITURE

### Campaign Settings

| Setting | Value |
|---|---|
| Campaign name | `hoski_cottage_furniture_search_1apr26` |
| Campaign type | Search |
| Goal | Leads |
| Networks | Search Network only |
| Bidding strategy | Maximize Clicks (switch to Target CPA after 30 conversions) |
| Max CPC bid limit | $5.00 |
| Daily budget | $20–40/day ($600–$1,200/month) |
| Geo targeting | Ontario — all of Ontario (Toronto metro, Barrie, Kingston, Ottawa, and province-wide) |
| Language | English |
| Ad schedule | All days, all hours |
| Ad rotation | Optimize |
| Conversion goals | `Cottage - Form Submission` (primary), `Cottage - Consultation Booked` (secondary) |

**Geo note:** Cottage buyers are province-wide. They search from Toronto, Barrie, Ottawa, etc. for cottages in Muskoka, Georgian Bay, Haliburton, PEC, and Kawartha Lakes. London-only targeting misses 80%+ of this audience.

**Budget note:** At $800/month, projected 25–28 leads/month at 5% CVR. Start at $600–$800/month and scale if CPL stays under $80.

---

### Campaign-Level Negative Keywords (Campaign 2 only)

In addition to account-level negatives, add these at the campaign level:

```
"plastic"
"resin"
"folding"
"simply cottage"
"pioneer furniture"
"hemlock cottage"
"muskoka chair company"
"adirondack"
"outdoor"
"patio"
"deck"
"garden"
"picnic"
"flat pack"
"assembly required"
```

---

### Ad Group Structure (Campaign 2)

| Priority | Ad Group Name | Theme | Est. Volume | Launch Phase |
|---|---|---|---|---|
| 1 | `farmhouse_dining` | Farmhouse/rustic dining tables | 880–4,000/mo | Launch day |
| 2 | `muskoka_furniture` | Muskoka-branded furniture intent | 140–880/mo | Launch day |
| 3 | `cottage_furniture_core` | Direct cottage furniture searches | 70–170/mo | Week 1 |
| 4 | `cottage_living_room` | Sofas, coffee tables, cottage lounge | 40–260/mo | Week 1 |
| 5 | `cottage_bedroom` | Beds, bedroom sets, bunk beds | 30–140/mo | Week 2 |
| 6 | `live_edge_and_artisan` | Live edge, reclaimed wood, artisan | 20–30/mo | Phase 2 |

---

### C2 — Ad Group 1: farmhouse_dining

**Launch phase:** Day 1
**Theme:** Highest-volume cluster in the campaign. Farmhouse and rustic dining tables.

**Keywords:**

| Keyword | Match Type | Vol/mo | CPC Range |
|---|---|---|---|
| [farm house dining table] | Exact | 880 | $0.54–$1.95 |
| "farmhouse dining table" | Phrase | 880 | $0.54–$1.95 |
| [farmhouse dining set] | Exact | 170 | $0.53–$1.59 |
| [farmhouse dining room sets] | Exact | 170 | $0.53–$1.59 |
| [rustic farmhouse dining table set] | Exact | 140 | $0.48–$1.28 |
| [farmhouse style dining table] | Exact | 110 | $0.56–$1.43 |
| [round dining table farmhouse] | Exact | 110 | $0.56–$1.45 |
| [farmhouse dining table set] | Exact | 70 | $0.58–$1.69 |
| [farmhouse dining table canada] | Exact | 70 | $0.46–$1.31 |
| [modern farmhouse dining room set] | Exact | 40 | $0.60–$2.14 |
| [wood farm dining table] | Exact | 40 | $0.69–$1.78 |
| "farmhouse dining table canada" | Phrase | 70 | $0.46–$1.31 |
| [farmhouse table canada] | Exact | 40 | $0.55–$1.75 |
| [farm dining table and chairs] | Exact | 210 | $0.54–$1.60 |
| [farmhouse kitchen dining table] | Exact | 260 | $0.54–$1.34 |
| [rustic farm dining table] | Exact | 90 | $0.47–$1.36 |
| [farm style dining table] | Exact | 70 | $0.55–$1.46 |
| [round farm dining table] | Exact | 50 | $0.53–$1.50 |
| [modern farmhouse furniture canada] | Exact | 30 | $0.38–$1.32 |
| [country style dining table] | Exact | 30 | $0.45–$1.33 |

**Ad group negatives:**

| Negative | Match Type |
|---|---|
| [plastic] | Exact |
| [metal] | Exact |
| [folding] | Exact |
| [cheap] | Exact |

**RSA:**

*Headlines (15):*
1. Custom Farmhouse Dining Tables
2. Built to Order in Ontario
3. $750 Off First Custom Order
4. Farmhouse Dining Tables Canada
5. Solid Wood Farmhouse Tables
6. Made-to-Order Farmhouse Tables
7. Free Design Consultation
8. Wide Plank Tables — Any Size
9. Rustic Dining Tables to Last
10. Farmhouse Tables Seats 8 to 12
11. Custom Finish — Custom Size
12. Claim $750 Off $5000 or More
13. Canadian-Made Farmhouse Tables
14. Built in London ON Workshop
15. Custom Farmhouse Dining Sets

*Descriptions (4):*
1. Custom farmhouse tables, any size or plank style. Book a consult. $750 off $5,000+.
2. Stop settling for a table that is almost right. Built to exact size and finish. Ontario.
3. Farmhouse tables and sets, custom-built to order. Solid hardwood, hand-finished. $750 off.
4. We build for real spaces: odd sizes, wide planks, live edge. Free consult. Ships Ontario.

*Final URL:* `https://go.parkroadfurniture.com/cottage-furniture`

---

### C2 — Ad Group 2: muskoka_furniture

**Launch phase:** Day 1
**Theme:** Muskoka-branded searches — most geographically specific, highest buyer quality.

**Keywords:**

| Keyword | Match Type | Vol/mo | CPC Range |
|---|---|---|---|
| [muskoka furniture] | Exact | 880 | $0.86–$1.76 |
| "muskoka furniture" | Phrase | 880 | $0.86–$1.76 |
| [muskoka furniture stores] | Exact | 140 | $1.12–$2.35 |
| [muskoka cottage furniture] | Exact | 40 | $0.84–$1.74 |
| [muskoka table] | Exact | 30 | — |
| [cottage country furniture] | Exact | 30 | $0.45–$1.37 |
| [country cottage furniture] | Exact | 30 | $0.45–$1.37 |
| [cabin furniture canada] | Exact | 20 | $0.50–$1.39 |
| [furniture stores gravenhurst] | Exact | 40 | $1.12–$1.96 |
| "cottage country furniture" | Phrase | 30 | $0.45–$1.37 |

**Ad group negatives:**

| Negative | Match Type | Reason |
|---|---|---|
| [chair] | Exact | Muskoka chair = outdoor seating |
| [plastic] | Exact | Wrong product |
| [resin] | Exact | Wrong product |
| [folding] | Exact | Wrong product |
| [adirondack] | Exact | Outdoor seating |
| [simply cottage] | Exact | Competitor brand |
| [pioneer] | Exact | Competitor brand |

**RSA:**

*Headlines (15):*
1. Furniture for Muskoka Cottages
2. Furnish Your Muskoka Cottage
3. $750 Off First Custom Order
4. Built for Cottage Conditions
5. Muskoka Furniture Custom Made
6. Solid Wood Built to Last
7. In-Home or Virtual Consult
8. Cottage Furniture Ontario Made
9. Tables Beds Sofas for Cottages
10. Heirloom Cottage Furniture
11. Claim $750 Off $5000 or More
12. Custom Cottage Furniture ON
13. Ships Muskoka and Georgian Bay
14. Built for Cottage Not Big Box
15. Canadian Hardwood for Cottages

*Descriptions (4):*
1. Solid wood furniture for Muskoka cottages. Handles humidity and family life. $750 off.
2. Furnish your cottage with furniture that lasts. Built to order in solid hardwood. Ontario.
3. Muskoka-ready furniture built to order in London ON. Tables, beds, sofas. $750 off.
4. No flat-pack that falls apart in cottage humidity. Solid hardwood, outlasts the cottage.

*Final URL:* `https://go.parkroadfurniture.com/cottage-furniture`

---

### C2 — Ad Group 3: cottage_furniture_core

**Launch phase:** Week 1
**Theme:** Direct cottage furniture searches — general intent buyers.

**Keywords:**

| Keyword | Match Type | Vol/mo | CPC Range |
|---|---|---|---|
| [cottage furniture] | Exact | 170 | $0.54–$1.77 |
| "cottage furniture" | Phrase | 170 | $0.54–$1.77 |
| [cottage furniture ontario] | Exact | 70 | $0.62–$2.22 |
| [cottage furniture canada] | Exact | 30 | $0.32–$1.89 |
| [cottage style furniture] | Exact | 40 | $0.39–$1.44 |
| [cottage type furniture] | Exact | 40 | $0.39–$1.44 |
| [cottage look furniture] | Exact | 40 | $0.39–$1.44 |
| [cottage core furniture] | Exact | 20 | $0.67–$1.82 |
| "cottage furniture ontario" | Phrase | 70 | $0.62–$2.22 |
| [custom cottage furniture] | Exact | 10 | — |

**RSA:**

*Headlines (15):*
1. Custom Cottage Furniture ON
2. Built for Cottage Not Big Box
3. $750 Off Orders of $5000 Plus
4. Solid Wood Cottage Conditions
5. Cottage Furniture Canada Made
6. Free Design Consultation
7. Handles Humidity and Heavy Use
8. Cottage Furniture Delivers ON
9. Heirloom Quality Furniture
10. Custom Cottage Tables Beds
11. Claim $750 Off Custom Order
12. Canadian-Made Cottage Pieces
13. Built to Order in London ON
14. Cottage Furniture That Lasts
15. Custom Built for Cottage Rooms

*Descriptions (4):*
1. Custom cottage furniture in solid hardwood. Handles humidity and heavy use. $750 off.
2. Furnish your cottage with custom solid wood pieces sized to your rooms. Free consult.
3. Cottage furniture built to last generations, not summers. Free consult. $750 off.
4. Custom cottage furniture: tables to bedroom sets, delivered Ontario. $750 off $5,000+.

*Final URL:* `https://go.parkroadfurniture.com/cottage-furniture`

---

### C2 — Ad Group 4: cottage_living_room

**Launch phase:** Week 1
**Theme:** Sofas, coffee tables, and cottage lounge pieces.

**Keywords:**

| Keyword | Match Type | Vol/mo | CPC Range |
|---|---|---|---|
| [cottage sofa] | Exact | 90 | $0.47–$1.40 |
| [cottage couch] | Exact | 90 | $0.47–$1.40 |
| [cottage style sofa] | Exact | 30 | $0.41–$1.38 |
| [cottage style couch] | Exact | 30 | $0.41–$1.38 |
| [cottage coffee table] | Exact | 40 | $0.57–$1.66 |
| [cottage style coffee table] | Exact | 20 | $0.57–$2.46 |
| [cottage chairs] | Exact | 260 | $0.62–$4.02 |
| [cottage settee] | Exact | 90 | $0.47–$1.40 |
| [cottage style living room] | Exact | 40 | — |

**Note on [cottage chairs]:** This term pulls 260/mo but will likely mix with Muskoka chair (outdoor) queries. Monitor search terms weekly for the first 30 days and add negatives aggressively.

**Ad group negatives:**

| Negative | Match Type | Reason |
|---|---|---|
| [muskoka] | Exact | Route to Muskoka ad group |
| [adirondack] | Exact | Outdoor seating |
| [plastic] | Exact | Wrong product |
| [outdoor] | Exact | Not relevant |
| [patio] | Exact | Not relevant |

**RSA:**

*Headlines (15):*
1. Custom Cottage Sofas Ontario
2. Cottage Style Sofas to Order
3. $750 Off Orders of $5000 Plus
4. Custom Cottage Coffee Tables
5. Solid Wood Cottage Living Room
6. Free Design Consultation
7. Built for Cozy Cottage Living
8. Custom Cottage Couches Ontario
9. Cottage Sofas Any Size Finish
10. Built for Your Cottage Lounge
11. Claim $750 Off Custom Order
12. Canadian-Made Cottage Sofas
13. Cottage Living Room Furniture
14. Cottage Style Solid Wood
15. Cottage Furniture Delivers ON

*Descriptions (4):*
1. Custom cottage sofas and coffee tables built to order. Sized to your room. $750 off.
2. Stop settling for a sofa that falls apart. Solid wood built for cottage life. $750 off.
3. Custom sofas and coffee tables for cottage living rooms. Solid hardwood. $750 off.
4. Cottage living room furniture, custom-built to order. Your choice of fabric and finish.

*Final URL:* `https://go.parkroadfurniture.com/cottage-furniture`

---

### C2 — Ad Group 5: cottage_bedroom

**Launch phase:** Week 2
**Theme:** Beds, bedroom sets, bunk beds for cottage rooms.

**Keywords:**

| Keyword | Match Type | Vol/mo | CPC Range |
|---|---|---|---|
| [cottage bed] | Exact | 110 | $0.31–$1.56 |
| [beds for cottages] | Exact | 110 | $0.31–$1.56 |
| [cottage bedroom set] | Exact | 30 | $0.32–$0.98 |
| [cottage bed frame] | Exact | 20 | $0.48–$2.06 |
| [cottage bunk beds]* | Exact | 40 | $0.54–$2.73 |
| [bunk beds for cottage]* | Exact | 40 | $0.54–$2.73 |
| [cottage nightstand] | Exact | 20 | — |
| [cottage bedside table] | Exact | 20 | — |
| [farmhouse style bedroom set] | Exact | 20 | $0.19–$1.34 |
| [cottage core beds] | Exact | 40 | $0.38–$3.04 |
| [log bed frame canada] | Exact | 20 | — |

> **\* HOLD:** Add [cottage bunk beds] and [bunk beds for cottage] as PAUSED keywords until client confirms Park Road makes custom bunk beds. Activate only after confirmation.

**RSA:**

*Headlines (15):*
1. Custom Cottage Beds Ontario
2. Solid Wood Cottage Bed Frames
3. $750 Off Orders of $5000 Plus
4. Cottage Bedroom Sets to Order
5. Farmhouse Bed Frames Custom
6. Free Design Consultation
7. Custom Cottage Beds Any Size
8. Solid Wood Beds Cottage Life
9. Cottage Bedroom Furniture ON
10. Built for Cottage Conditions
11. Claim $750 Off Custom Order
12. Canadian-Made Cottage Beds
13. Log and Farmhouse Bed Frames
14. Cottage Beds Delivering ON
15. Hand-Finished in London ON

*Descriptions (4):*
1. Custom cottage beds built to order in solid hardwood. Handles humidity. $750 off.
2. Solid wood cottage beds and bedroom sets, built to order. Free consult. $750 off.
3. Cottage bedroom furniture in solid hardwood. Bed frames to nightstands, made to order.
4. Stop settling for a bed that squeaks. Solid wood cottage sets to exact specs. $750 off.

*Final URL:* `https://go.parkroadfurniture.com/cottage-furniture`

---

### C2 — Ad Group 6: live_edge_and_artisan (Phase 2)

**Launch phase:** Day 30+ (activate if budget allows)
**Theme:** Premium buyers seeking live edge, reclaimed wood, or artisan-crafted pieces. Lowest volume, highest buyer quality.

**Keywords:**

| Keyword | Match Type | Vol/mo | CPC Range |
|---|---|---|---|
| [live edge table ontario] | Exact | 30 | — |
| [live edge dining table ontario] | Exact | 30 | $0.69–$2.34 |
| [live edge furniture ontario] | Exact | 10 | — |
| [solid wood furniture ontario] | Exact | 110 | $0.65–$2.04 |
| [reclaimed wood furniture ontario] | Exact | 10 | — |
| [custom rustic furniture] | Exact | 10 | — |
| [custom farmhouse furniture] | Exact | 10 | — |
| [handcrafted cottage furniture] | Exact | 10 | — |
| [artisan furniture ontario] | Exact | 10 | — |

**RSA angle:** "Live Edge and Custom Solid Wood Furniture — Made in London, Ontario"
Build RSA at activation.

---

## ASSETS — BOTH CAMPAIGNS

Add all assets at the campaign level on both campaigns unless otherwise noted.

---

### Sitelinks

| Sitelink Text | Description 1 | Description 2 | URL |
|---|---|---|---|
| See Our Portfolio | Custom dining tables, bedroom sets | Sofas, beds, and more | `https://parkroadfurniture.com` (or portfolio page) |
| Book a Free Consultation | In-home, in-store, or virtual | Available across Ontario | Campaign-specific: `/custom-furniture` or `/cottage-furniture` |
| Call Us Now | Talk to a designer directly | No obligation | `https://parkroadfurniture.com` (with phone number) |
| Our Offer — $750 Off | On first custom order of $5,000+ | Limited time discount | Campaign-specific landing page |

**Note:** Replace "Call Us Now" URL with the correct tracked phone number page or enable call extension separately once phone is confirmed with client.

---

### Callout Assets

```
Canadian-Made Solid Wood
Built to Your Exact Specs
Free In-Home Consultation
Delivering Across Ontario
6–12 Week Delivery
Hand-Finished in London
No Big-Box Quality
$750 Off Your First Order
```

---

### Call Asset

Add Park Road's confirmed phone number as a call asset. **Phone number placeholder:** `(519) XXX-XXXX` — replace once confirmed with client.

- Enable call reporting
- Set call asset ad schedule to business hours only (Mon–Sat 10am–5pm, Sun 11am–4:30pm, effective April 1, 2026)

---

### Structured Snippet Asset

| Header | Values |
|---|---|
| Types | Dining Tables, Bedroom Sets, Sofas, Bed Frames, Coffee Tables, Entertainment Units |

---

## IMAGE ASSETS SUMMARY

Add image assets at the campaign level. Google Ads does not guarantee they show on every impression but they improve CTR when they do.

### Required Formats (per campaign)

| Format | Dimensions | Aspect Ratio |
|---|---|---|
| Landscape | 1200 x 628px | 1.91:1 |
| Square | 1200 x 1200px | 1:1 |

Recommended: 3 landscape + 3 square per campaign (6 images per campaign). Max 20 images per campaign.

**Rules:** No text, logos, or overlaid copy on Google image assets. Subject centered within safe zone.

---

### Campaign 1 — Custom Furniture Image Assets

**Audience feel:** London/SW Ontario homeowners. Contemporary, real, skilled craftsperson. Not luxury-aspirational, not catalogue.

| Asset | Subject | Format | File Name |
|---|---|---|---|
| Asset 1 | Hero product: best dining table or bed frame photo from client drive. Warm natural light, clean room context. No text. | Landscape + Square | `c1-google-landscape-product.jpg` / `c1-google-square-product.jpg` |
| Asset 2 | Offer asset: close-up wood grain background with text overlay `$750 Off Your First Custom Order`. Warm honey/amber tones. | Square | `c1-google-square-offer.jpg` |
| Asset 3 | Social proof/lifestyle: Park Road piece in a real customer home (living room or bedroom). Warm, lived-in. If no client photo available, generate from brief. | Square | `c1-google-square-lifestyle.jpg` |

**AI prompt for Asset 1 (landscape) if generating:**
> Photorealistic close-medium shot of a solid wood custom dining table in a warm contemporary Canadian home. Wide plank top, natural grain visible, hand-finished. Warm afternoon light. Simple chairs. No people, no clutter. Warm honey and cream tones. Camera at seated eye level. For 1.91:1: wider angle showing the full dining room setting.

---

### Campaign 2 — Cottage Furniture Image Assets

**Audience feel:** Ontario cottage owners. Muskoka lifestyle, lived-in, heirloom quality. Warm and rustic, not Pinterest-perfect.

| Asset | Subject | Format | File Name |
|---|---|---|---|
| Asset 1 | Hero lifestyle: farmhouse dining table in a cottage dining room. Exposed beams, trees or lake through windows, warm light. Table is the hero. | Landscape + Square | `c2-google-landscape-cottage.jpg` / `c2-google-square-cottage.jpg` |
| Asset 2 | Offer asset: close-up rustic wood grain (deeper color, knots, character) with text overlay `Furnish Your Cottage. $750 Off.`. Amber and deep tones. | Square | `c2-google-square-offer.jpg` |
| Asset 3 | Social proof: cottage dining or living scene. Family or couple visible in background — candid, not posed. Real cottage context. | Square | `c2-google-square-lifestyle.jpg` |

**AI prompt for Asset 1 (landscape) if generating:**
> Photorealistic interior of a rustic Ontario cottage dining room. Large solid wood farmhouse dining table, wide plank top, visible grain, seats 8 to 10. Exposed wood ceiling beams. Warm afternoon light from wide windows showing trees or a lake. Simple farmhouse chairs. No people, no clutter. Warm amber and green tones. For 1.91:1: full room wide angle.

---

## LAUNCH SEQUENCE

### Week Before Launch

- [ ] Landing pages live and QA'd (all 6 pages — see `campaign-launch-brief.md`)
- [ ] Test form submission on each landing page — confirm redirect to TY1
- [ ] Test calendar booking on TY1 — confirm redirect to TY2
- [ ] All phone number placeholders `(519) XXX-XXXX` replaced with confirmed number
- [ ] Google Tag verified on `go.parkroadfurniture.com`
- [ ] All 4 conversion actions created and verified
- [ ] Client confirmed: offer details, expiry date, delivery coverage areas
- [ ] Client confirmed: whether Park Road makes custom bunk beds and custom log beds

### Launch Day

- [ ] hoski_custom_furniture_search_1apr26 set to Active
- [ ] hoski_cottage_furniture_search_1apr26 set to Active
- [ ] Daily budgets set: $20–27/day (C1), $20–40/day (C2)
- [ ] Ad groups 1–2 set to Active in both campaigns
- [ ] Ad groups 3–5 set to Paused (activate on schedule below)
- [ ] Ad group 6 (both campaigns) set to Paused (Phase 2)
- [ ] Minimum 1 RSA submitted per live ad group
- [ ] Account-level negative list applied to both campaigns
- [ ] Campaign-level negatives added to hoski_cottage_furniture_search_1apr26
- [ ] All assets added (sitelinks, callouts, call asset, structured snippets, image assets)
- [ ] Conversion goals applied: C1 = `CF - Form Submission`, C2 = `Cottage - Form Submission`

### Week 1 (Days 2–7)

- [ ] Activate `dining_room` (C1)
- [ ] Activate `canadian_made_solid_wood` (C1)
- [ ] Activate `cottage_furniture_core` (C2)
- [ ] Activate `cottage_living_room` (C2)
- [ ] Review search terms — add any obvious early negatives

### Week 2 (Days 8–14)

- [ ] Activate `living_and_bedroom` (C1)
- [ ] Activate `cottage_bedroom` (C2)
- [ ] First full search terms review
- [ ] Confirm bunk bed keywords status with client — activate if confirmed

### Day 30 Review

- [ ] Run `/weekly-check` full account sweep
- [ ] Run `/search-terms` for negatives and new keyword opportunities
- [ ] Check Quality Scores on core keywords (target 7+)
- [ ] Evaluate CPL per campaign (target under $80 — consider budget increase if hitting it)
- [ ] Review geo performance (C1): is London + SW Ontario delivering or adjust scope?
- [ ] Decide on Phase 2: Ad Group 6 (both campaigns), competitor campaign (C2)
- [ ] If 30+ conversions: switch to Target CPA (initial target = current CPL x 1.2)

---

## BUDGET SUMMARY

| Campaign | Daily Budget | Monthly Estimate | Projected Clicks | Projected Leads (5% CVR) |
|---|---|---|---|---|
| Custom Furniture | $20–27/day | $600–$800 | 360–540 | 18–27 |
| Cottage Furniture | $20–40/day | $600–$1,200 | 400–800 | 20–40 |
| **Total (launch)** | **$40–67/day** | **$1,200–$2,000** | **760–1,340** | **38–67** |

CPL target: $50–$80/lead. At $5,000+ AOV, 1 closed sale per month covers full ad spend.

---

## PHASE 2 ROADMAP

| Initiative | Trigger | Notes |
|---|---|---|
| Switch to Target CPA | 30+ primary conversions per campaign | Start at current CPL x 1.2 |
| Add `Entertainment and Storage` (C1 AG6) | Budget allows, AG 1–5 stable | Low competition, good intent |
| Add `Live Edge and Artisan` (C2 AG6) | Budget allows | Highest buyer quality, lowest volume |
| Competitor campaign (C2) | 30 days post-launch | Simply Cottage, Pioneer Furniture, Hemlock Cottage brand queries |
| Display remarketing | 500+ website visitors | Retarget landing page visitors who did not convert |
| Demand Gen | 60+ days, budget allows | Muskoka/cottage lifestyle creative, broader Ontario awareness |

---

*All questions, offer changes, or copy decisions: Bishal. Do not change keyword lists, landing page URLs, offer language, or conversion actions without reviewing this sheet and the campaign launch brief.*
