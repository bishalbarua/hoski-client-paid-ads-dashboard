# Campaign Launch Brief — Park Road Custom Furniture and Decor
**Client:** Park Road Custom Furniture and Decor
**Account ID:** 7228467515
**Date:** 2026-03-21
**Campaigns:** Custom Furniture (London + SW Ontario) | Cottage Furniture (Ontario-wide)
**Prepared by:** Bishal

---

## STOP — PREREQUISITES BEFORE LAUNCHING

Do not build campaigns until both of these are confirmed:

### 1. Landing Pages Live

Both landing pages must be built, QA'd, and live before any campaign goes active.

| Page | URL | Status Needed |
|---|---|---|
| Custom Furniture landing page | `go.parkroadfurniture.com/custom-furniture` | Live + form working |
| Custom Furniture TY1 | `go.parkroadfurniture.com/custom-furniture/thank-you` | Live |
| Custom Furniture TY2 | `go.parkroadfurniture.com/custom-furniture/consultation-booked` | Live |
| Cottage Furniture landing page | `go.parkroadfurniture.com/cottage-furniture` | Live + form working |
| Cottage Furniture TY1 | `go.parkroadfurniture.com/cottage-furniture/thank-you` | Live |
| Cottage Furniture TY2 | `go.parkroadfurniture.com/cottage-furniture/consultation-booked` | Live |

Reference: `clients/Park Road.../notes/project-brief-landing-pages.md` for full build spec.

### 2. Conversion Tracking Verified

All 4 conversion actions must be created and verified before enabling Smart Bidding. See the Conversion Tracking section at the end of this doc.

### 3. Client Confirmation Items

These must be resolved before launch:

- [ ] Phone number confirmed (replaces all `(519) XXX-XXXX` placeholders in landing pages)
- [ ] Offer expiry date confirmed (sets countdown timer on both pages)
- [ ] `$750 off $5,000+` offer approved by client (no exclusions, valid for new orders)
- [ ] Custom Furniture delivery coverage confirmed: Kitchener, Waterloo, Windsor, Guelph, Woodstock
- [ ] Cottage Furniture delivery coverage confirmed: Muskoka, Georgian Bay, Haliburton, Prince Edward County, Kawartha Lakes
- [ ] Whether Park Road makes bunk beds and custom log beds (affects Cottage Bedroom ad group)

---

## ACCOUNT-LEVEL SETUP

### Shared Negative Keyword List

Create a shared negative list named `Park Road — Account Level Negatives` and apply to both campaigns.

**Broad match:**
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

**Phrase match (add to campaign level if shared list doesn't support phrase match negatives):**
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

## CAMPAIGN 1: Custom Furniture

### Campaign Settings

| Setting | Value |
|---|---|
| Campaign name | `Park Road — Custom Furniture` |
| Campaign type | Search |
| Goal | Leads |
| Networks | Search Network only — uncheck Display Network and Search Partners for launch |
| Bidding strategy | Maximize Clicks (launch phase — switch to Target CPA after 30 conversions) |
| Max CPC bid limit | $5.00 |
| Daily budget | $20–27/day ($600–$800/month) |
| Geo targeting | London, Ontario + Southwestern Ontario |
| Geo locations to add | London ON, Kitchener ON, Waterloo ON, Windsor ON, Guelph ON, Woodstock ON, Sarnia ON, St. Thomas ON |
| Language | English |
| Ad schedule | All days, all hours (review after 30 days for optimization) |
| Ad rotation | Optimize (Prefer best performing ads) |
| Conversion goals | `CF - Form Submission` (primary), `CF - Consultation Booked` (secondary) |

**Bidding note:** Start on Maximize Clicks to build impression and click data. Once the account has 30+ `CF - Form Submission` conversions (4–8 weeks at target volume), switch to Target CPA. Initial Target CPA estimate: $60–$80/lead based on projected CPL.

### Ad Group Structure — Campaign 1

Build in this order. Ad Groups 1–5 launch at go-live. Ad Group 6 is Phase 2.

| Priority | Ad Group Name | Theme | Launch Phase |
|---|---|---|---|
| 1 | `Custom Furniture — Core` | Direct custom intent | Launch day |
| 2 | `Furniture Store London` | Local discovery intent | Launch day |
| 3 | `Dining Room` | Dining room buyers | Week 1 |
| 4 | `Canadian Made — Solid Wood` | Quality-conscious buyers | Week 1 |
| 5 | `Living and Bedroom` | Living room and bedroom buyers | Week 2 |
| 6 | `Entertainment and Storage` | Built-ins and storage | Phase 2 (30+ days) |

---

### Ad Group 1: Custom Furniture — Core

**Keywords:**
```
[custom furniture london ontario]
"custom furniture london ontario"
[custom furniture near me]
"custom furniture near me"
[custom made furniture]
"custom made furniture"
[custom built furniture]
[bespoke furniture]
[handcrafted furniture]
[custom wood furniture]
```

**Ad group negatives:**
```
[discount] — exact
[cheap] — exact
[used] — exact
```

**RSA Copy — use as the primary ad:**

*Headlines (15):*
1. Custom Furniture London Ontario
2. $750 Off Your First Custom Order
3. Built to Order in London Ontario
4. Solid Canadian Hardwood Furniture
5. Custom Furniture Built to Your Specs
6. Free In-Home Design Consultation
7. Made-to-Measure for Any Room
8. Hand-Finished in London Ontario
9. 6–12 Week Delivery — Not 3 Months
10. Dining Tables Beds Sofas Built to Order
11. Real Solid Wood — Not Big-Box Quality
12. Custom Size Custom Finish Custom Design
13. Claim $750 Off Orders of $5000 Plus
14. Canadian-Made Furniture That Lasts
15. Perfect Fit Guarantee — Every Piece

*Descriptions (4):*
1. Every piece is made to order using solid Canadian hardwood, custom-fit to your space, and hand-finished in London, Ontario. Book your free consultation today.
2. Stop settling for furniture that almost fits. We size and build every piece to your exact room, style, and finish. $750 off your first order of $5,000 or more.
3. From dining tables to bedroom sets, sofas to entertainment units — all built to order in our London, Ontario workshop. Book a free consultation and claim your $750 discount.
4. In-home design consultations available. We come to you, measure your space, and build exactly what you need. Delivered in 6–12 weeks. Canadian-made.

*Final URL:* `https://go.parkroadfurniture.com/custom-furniture`

---

### Ad Group 2: Furniture Store London

**Keywords:**
```
[furniture store london ontario]
"furniture store london ontario"
[furniture stores london ontario]
[best furniture stores london ontario]
[furniture london ontario]
"local furniture store"
```

**Ad group negatives:**
```
[discount] — exact
[cheap] — exact
[used] — exact
[outlet] — exact
[custom] — exact (route to Ad Group 1)
[solid wood] — exact (route to Ad Group 4)
[tepperman] — exact
[lazy boy] — exact
[lazyboy] — exact
```

**RSA Copy:**

*Headlines (15):*
1. Furniture Store London Ontario
2. London's Custom Furniture Studio
3. $750 Off Your First Custom Order
4. Not Your Average Furniture Store
5. Built to Order — Not Off the Floor
6. Custom Furniture — London Ontario
7. Solid Wood Furniture London ON
8. Free Design Consultation Included
9. Custom Dining Tables and Bedroom Sets
10. Hand-Finished by Local Craftsmen
11. Claim $750 Off Orders of $5000 Plus
12. Canadian-Made Custom Furniture
13. Skip the Showroom — Build to Spec
14. Every Piece Sized to Your Space
15. Furniture Store London — Custom Built

*Descriptions (4):*
1. We're not a showroom — we build every piece of furniture to order using solid Canadian hardwood. Visit us in London or book a free in-home consultation to get started.
2. London's only custom furniture studio offering $750 off your first order of $5,000 or more. Dining tables, sofas, bedroom sets — all built to your exact specs.
3. Looking for a furniture store in London, Ontario? We build everything custom, to your size and finish. Free design consultation included. Book yours today.
4. Real solid wood, custom-built in London, Ontario. No flat-pack, no big-box products. Book a free in-home consultation and claim your $750 discount on orders of $5,000+.

*Final URL:* `https://go.parkroadfurniture.com/custom-furniture`

---

### Ad Group 3: Dining Room

**Keywords:**
```
[custom dining table]
"custom dining table"
[wooden dining table]
[solid wood dining table]
[wooden dining room table]
[round wooden dining table]
[natural wood dining table]
[solid oak dining table]
[solid wood dining room table]
```

**Ad group negatives:**
```
[chair] — exact
[bar stool] — exact
```

**RSA Copy angle:** "Custom Dining Tables Built to Order — $750 Off $5k+"
Use the `/rsa-headline-generator` skill to generate full 15+4 RSA for this group with: keyword = `custom dining table london ontario`, angle = custom-built dining tables, mention solid wood, sizing to space, Canadian-made, $750 offer.

---

### Ad Group 4: Canadian Made — Solid Wood

**Keywords:**
```
[canadian made furniture]
[canadian built furniture]
[canadian furniture]
"canadian made furniture"
[solid wood furniture]
[real wood furniture]
[solid wood dining table]
[couches made in canada]
[sofa made in canada]
```

**RSA Copy angle:** "Canadian-Made Custom Furniture — Solid Wood, Built to Last"
Use `/rsa-headline-generator` with: keyword = `canadian made furniture`, angle = local craftsmanship, real wood, not imported, $750 offer, London Ontario workshop.

---

### Ad Group 5: Living and Bedroom

**Keywords:**
```
[custom sofa]
[custom couch]
[custom sectional sofa]
[custom coffee table]
[wooden coffee table]
[solid wood coffee table]
[custom bedroom furniture]
[wooden bed frame]
[solid wood bed frame]
[wooden bed frame queen]
[solid wood bed]
```

**Ad group negatives:**
```
[dining] — exact (route to Ad Group 3)
[table] — exact (unless coffee table — monitor in search terms)
```

**RSA Copy angle:** "Custom Sofas, Beds and More — Built to Your Specs in London, ON"
Use `/rsa-headline-generator` with: keyword = `custom bedroom furniture london ontario`, angle = custom sofas + beds + bedroom sets, solid wood, Canadian-made, $750 offer.

---

### Ad Group 6: Entertainment and Storage (Phase 2)

Add at 30 days if budget allows and Ad Groups 1–5 are pacing well.

**Keywords:**
```
[custom entertainment unit]
[custom entertainment center]
[built in entertainment center]
[custom bookshelves]
[custom bookcase]
[solid wood bookcase]
[solid wood tv stand]
```

---

## CAMPAIGN 2: Cottage Furniture

### Campaign Settings

| Setting | Value |
|---|---|
| Campaign name | `Park Road — Cottage Furniture` |
| Campaign type | Search |
| Goal | Leads |
| Networks | Search Network only |
| Bidding strategy | Maximize Clicks (switch to Target CPA after 30 conversions) |
| Max CPC bid limit | $5.00 |
| Daily budget | $20–40/day ($600–$1,200/month — scale based on lead volume) |
| Geo targeting | Ontario — all of Ontario, not just London |
| Language | English |
| Ad schedule | All days, all hours |
| Ad rotation | Optimize |
| Conversion goals | `Cottage - Form Submission` (primary), `Cottage - Consultation Booked` (secondary) |

**Geo note:** Cottage buyers are province-wide. Target Toronto metro, Barrie, Kingston, Ottawa, and all of Ontario. They search for cottage furniture from the city and order for their cottages in Muskoka, Georgian Bay, Haliburton, and Prince Edward County. London-only targeting would miss 80%+ of this audience.

**Budget note:** At $800/month (moderate scenario), projected 25–28 leads/month at 5% conversion rate. At $1.50 avg CPC with 8,000–12,000/month addressable volume, $800/month captures roughly half the market. Start at $600–$800/month and scale up if CPL is under $80.

### Campaign-Level Negative Keywords (Cottage Furniture)

Add these on top of the account-level negatives:
```
"plastic"
"resin"
"folding"
"simply cottage" — phrase
"pioneer furniture" — phrase
"hemlock cottage" — phrase
"muskoka chair company" — phrase
"adirondack"
"outdoor"
"patio"
"deck"
"garden"
"picnic"
"flat pack"
"assembly required"
```

### Ad Group Structure — Campaign 2

| Priority | Ad Group Name | Theme | Est. Volume | Launch Phase |
|---|---|---|---|---|
| 1 | `Farmhouse Dining` | Farmhouse/rustic dining tables | 880–4,000/mo | Launch day |
| 2 | `Muskoka Furniture` | Muskoka-branded furniture intent | 140–880/mo | Launch day |
| 3 | `Cottage Furniture — Core` | Direct cottage furniture searches | 70–170/mo | Week 1 |
| 4 | `Cottage Living Room` | Sofas, coffee tables, cottage lounge | 40–260/mo | Week 1 |
| 5 | `Cottage Bedroom` | Beds, bedroom sets, bunk beds | 30–140/mo | Week 2 |
| 6 | `Live Edge and Artisan` | Live edge, reclaimed wood, artisan | 20–30/mo | Phase 2 |

---

### Ad Group 1: Farmhouse Dining

**Keywords:**
```
[farm house dining table]
"farmhouse dining table"
[farmhouse dining set]
[farmhouse dining room sets]
[rustic farmhouse dining table set]
[farmhouse style dining table]
[round dining table farmhouse]
[farmhouse dining table set]
[farmhouse dining table canada]
[modern farmhouse dining room set]
[wood farm dining table]
"farmhouse dining table canada"
[farmhouse table canada]
[farm dining table and chairs]
[farmhouse kitchen dining table]
[rustic farm dining table]
[farm style dining table]
[round farm dining table]
[modern farmhouse furniture canada]
[country style dining table]
```

**Ad group negatives:**
```
[plastic] — exact
[metal] — exact
[folding] — exact
[cheap] — exact
```

**RSA Copy:**

*Headlines (15):*
1. Custom Farmhouse Dining Tables
2. Built to Order in Ontario
3. $750 Off Your First Custom Order
4. Farmhouse Dining Tables Canada
5. Solid Wood Farmhouse Table Sets
6. Made-to-Order Farmhouse Furniture
7. Free Design Consultation Included
8. Wide Plank Tables — Any Size
9. Rustic Dining Tables Built to Last
10. Farmhouse Tables Seats 8 to 12
11. Custom Finish — Custom Size
12. Claim $750 Off Orders of $5000 Plus
13. Canadian-Made Farmhouse Furniture
14. Built in Our London Ontario Workshop
15. Farmhouse Dining Sets — Custom Built

*Descriptions (4):*
1. Custom farmhouse dining tables built to order using solid Canadian hardwood. Any size, any finish, any plank style. Book a free consultation and claim $750 off your first order of $5,000+.
2. Stop settling for a farmhouse table that's almost right. We build to your exact size, wood species, and finish — from our London, Ontario workshop. Delivered across Ontario.
3. Farmhouse dining tables, sets, and benches — all custom-built to order. Solid Canadian hardwood, hand-finished in London, Ontario. $750 off orders of $5,000 or more.
4. We build farmhouse dining tables for real spaces: odd sizes, wide planks, live edge options. Free in-home or virtual consultation. Delivering to Muskoka, Georgian Bay, and across Ontario.

*Final URL:* `https://go.parkroadfurniture.com/cottage-furniture`

---

### Ad Group 2: Muskoka Furniture

**Keywords:**
```
[muskoka furniture]
"muskoka furniture"
[muskoka furniture stores]
[muskoka cottage furniture]
[muskoka table]
[cottage country furniture]
[country cottage furniture]
[cabin furniture canada]
[furniture stores gravenhurst]
"cottage country furniture"
```

**Ad group negatives:**
```
[chair] — exact (Muskoka chair = outdoor seating)
[plastic] — exact
[resin] — exact
[folding] — exact
[adirondack] — exact
[simply cottage] — exact
[pioneer] — exact
```

**RSA Copy:**

*Headlines (15):*
1. Custom Furniture for Muskoka Cottages
2. Furnish Your Muskoka Cottage
3. $750 Off Your First Custom Order
4. Built to Handle Cottage Conditions
5. Muskoka Furniture — Custom Made
6. Solid Wood Built to Last Generations
7. Free Consultation — In-Home or Virtual
8. Cottage Furniture — Ontario Made
9. Dining Tables Beds Sofas for Cottages
10. Heirloom Quality Cottage Furniture
11. Claim $750 Off Orders of $5000 Plus
12. Custom Cottage Furniture Ontario
13. Delivers to Muskoka and Georgian Bay
14. Built for Cottage Life — Not Big Box
15. Canadian Hardwood for Cottage Living

*Descriptions (4):*
1. Custom solid wood furniture built for Muskoka and cottage country. Handles humidity, heavy use, and generations of family life. Book a free consultation and claim $750 off $5,000+.
2. Furnish your cottage with furniture that lasts. We build to order using solid Canadian hardwood — sized to your cottage rooms, finished to your style. Delivering across Ontario.
3. Muskoka-ready furniture, built to order in London, Ontario. Dining tables, cottage beds, sofas, and more. $750 off your first custom order of $5,000 or more. Book a free consultation.
4. No flat-pack furniture that falls apart in cottage humidity. Our pieces are solid hardwood, custom-built, and designed to outlast the cottage itself. Free consultation, $750 off your first order.

*Final URL:* `https://go.parkroadfurniture.com/cottage-furniture`

---

### Ad Group 3: Cottage Furniture — Core

**Keywords:**
```
[cottage furniture]
"cottage furniture"
[cottage furniture ontario]
[cottage furniture canada]
[cottage style furniture]
[cottage type furniture]
[cottage look furniture]
[cottage core furniture]
"cottage furniture ontario"
[custom cottage furniture]
```

**RSA Copy angle:** "Custom Cottage Furniture — Canadian-Made, Built to Order"
Use `/rsa-headline-generator` with: keyword = `cottage furniture ontario`, angle = custom cottage furniture, cottage conditions, durability, Ontario delivery, $750 offer.

---

### Ad Group 4: Cottage Living Room

**Keywords:**
```
[cottage sofa]
[cottage couch]
[cottage style sofa]
[cottage style couch]
[cottage coffee table]
[cottage style coffee table]
[cottage chairs]
[cottage settee]
[cottage style living room]
```

**Ad group negatives:**
```
[muskoka] — exact (route to Ad Group 2)
[adirondack] — exact
[plastic] — exact
[outdoor] — exact
[patio] — exact
```

**Note on `[cottage chairs]`:** This term pulls 260/mo but will likely mix with Muskoka chair (outdoor) queries. Monitor search terms weekly for the first 30 days and add negatives aggressively. Consider a custom ad copy angle that speaks specifically to indoor seating.

**RSA Copy angle:** "Custom Cottage Sofas and Coffee Tables — Built in Ontario"
Use `/rsa-headline-generator` with: keyword = `cottage sofa ontario`, angle = custom indoor living room pieces, solid wood, cottage aesthetic, $750 offer.

---

### Ad Group 5: Cottage Bedroom

**Keywords:**
```
[cottage bed]
[beds for cottages]
[cottage bedroom set]
[cottage bed frame]
[cottage bunk beds]
[bunk beds for cottage]
[cottage nightstand]
[cottage bedside table]
[farmhouse style bedroom set]
[cottage core beds]
[log bed frame canada]
```

**Important:** Only include `[cottage bunk beds]` and `[bunk beds for cottage]` if client confirms Park Road makes custom bunk beds. Hold these keywords until confirmed — add as paused if unsure and activate after client confirmation.

**RSA Copy angle:** "Custom Cottage Beds and Bedroom Furniture — Solid Wood, Ontario-Made"
Use `/rsa-headline-generator` with: keyword = `cottage bed frame ontario`, angle = custom cottage bedroom pieces, solid wood, cottage conditions, farmhouse style, $750 offer.

---

### Ad Group 6: Live Edge and Artisan (Phase 2)

Add at 30 days.

**Keywords:**
```
[live edge table ontario]
[live edge dining table ontario]
[live edge furniture ontario]
[solid wood furniture ontario]
[reclaimed wood furniture ontario]
[custom rustic furniture]
[custom farmhouse furniture]
[handcrafted cottage furniture]
[artisan furniture ontario]
```

---

## CONVERSION TRACKING SETUP

Four conversion actions. All URL-based. No custom tag events needed — the base Google Tag on the GHL subdomain handles it.

### Prerequisite

Confirm the base Google Tag (gtag) is installed and firing on `go.parkroadfurniture.com`. Verify in Tag Assistant or Google Ads Diagnostics before creating conversion actions.

### Conversion Actions to Create

| Conversion Name | URL Match | Type | Designation | Value | Count |
|---|---|---|---|---|---|
| `CF - Form Submission` | URL contains `/custom-furniture/thank-you` | Website | Primary | Not set (or $1 placeholder) | One |
| `CF - Consultation Booked` | URL contains `/custom-furniture/consultation-booked` | Website | Secondary | Not set | One |
| `Cottage - Form Submission` | URL contains `/cottage-furniture/thank-you` | Website | Primary | Not set | One |
| `Cottage - Consultation Booked` | URL contains `/cottage-furniture/consultation-booked` | Website | Secondary | Not set | One |

**Setup notes:**
- Set attribution window: 30-day click, 1-day view (standard for lead gen)
- Keep CF and Cottage conversion actions separate — do not merge. This lets you compare CPL between campaigns cleanly.
- Primary conversions (`CF - Form Submission`, `Cottage - Form Submission`) are the main KPIs that Smart Bidding will optimize toward. Secondary conversions are tracked but not used for bidding.
- After setup: test by submitting a test form on each landing page and verifying the conversion fires within 24 hours in Google Ads conversion diagnostics.

### After Verification

Once conversion actions are verified:
1. Apply `CF - Form Submission` as the conversion goal for Campaign 1
2. Apply `Cottage - Form Submission` as the conversion goal for Campaign 2
3. Do not apply secondary conversions to bidding targets

---

## AD EXTENSIONS (Asset Setup)

Add these to both campaigns at the campaign level.

### Sitelink Assets

| Sitelink | Description 1 | Description 2 | URL |
|---|---|---|---|
| See Our Portfolio | Custom dining tables, bedroom sets | Sofas, beds, and more | `go.parkroadfurniture.com` (homepage or portfolio) |
| Book a Free Consultation | In-home, in-store, or virtual | Available across Ontario | `go.parkroadfurniture.com/custom-furniture` or `/cottage-furniture` |
| Call Us Now | Talk to a designer directly | No obligation | `go.parkroadfurniture.com` (with phone number) |
| Our Offer — $750 Off | On first custom order of $5,000+ | Limited time discount | Landing page |

### Callout Assets
```
Canadian-Made Solid Wood
Custom-Built to Your Specs
Free In-Home Consultation
Delivering Across Ontario
6–12 Week Delivery
Hand-Finished in London ON
No Big-Box Quality
$750 Off Your First Order
```

### Call Asset

Add the Park Road phone number as a call asset (once confirmed with client). Enable during business hours only — set an ad schedule for call assets if calls outside business hours are not monitored.

### Structured Snippet Asset

**Header:** Types
**Values:** Dining Tables, Bedroom Sets, Sofas, Bed Frames, Coffee Tables, Entertainment Units

---

## LAUNCH SEQUENCE

### Week Before Launch

- [ ] Landing pages live and QA'd (all 6 pages)
- [ ] Test form submission on each landing page — confirm redirect to TY1
- [ ] Test calendar booking on TY1 — confirm redirect to TY2
- [ ] Confirm all phone number placeholders replaced with real number
- [ ] Google Tag verified on `go.parkroadfurniture.com`
- [ ] All 4 conversion actions created and verified
- [ ] Client has confirmed offer details (expiry date, delivery coverage)

### Launch Day

- [ ] Campaign 1 (Custom Furniture) set to Active
- [ ] Campaign 2 (Cottage Furniture) set to Active
- [ ] Daily budgets set: $20–27/day (Campaign 1), $20–40/day (Campaign 2)
- [ ] All ad groups set to Active for Priority 1–2 groups
- [ ] Priority 3–5 ad groups set as Paused — activate on schedule below
- [ ] All RSAs submitted (minimum 1 RSA per live ad group)
- [ ] Account-level negative keyword list applied to both campaigns
- [ ] Campaign-level negatives added to Campaign 2

### Week 1 (Days 2–7)

- [ ] Activate Ad Group 3 (Dining Room) in Campaign 1
- [ ] Activate Ad Group 4 (Canadian Made) in Campaign 1
- [ ] Activate Ad Group 3 (Cottage Furniture Core) in Campaign 2
- [ ] Activate Ad Group 4 (Cottage Living Room) in Campaign 2
- [ ] Check search terms for early irrelevant queries — add any obvious negatives

### Week 2 (Days 8–14)

- [ ] Activate Ad Group 5 (Living and Bedroom) in Campaign 1
- [ ] Activate Ad Group 5 (Cottage Bedroom) in Campaign 2
- [ ] First search terms review — use `/search-terms` skill
- [ ] Confirm bunk bed keywords status with client and activate if confirmed

### Day 30 Review

- [ ] Run `/weekly-check` for full account performance sweep
- [ ] Run `/search-terms` to clean up queries and find new keyword opportunities
- [ ] Check Quality Scores on core keywords — if under 7, review landing page message match
- [ ] Evaluate CPL for each campaign — if under $80, consider budget increase
- [ ] Review geo performance (Campaign 1) — is London+SW Ontario delivering or should scope change?
- [ ] Review which ad groups are generating form fills vs. calls vs. nothing
- [ ] Decide on Phase 2 additions: Ad Group 6 (both campaigns), Competitor Campaign (Cottage)
- [ ] If 30+ conversions on either campaign, consider switching to Target CPA

---

## PHASE 2 ROADMAP (After 30+ Days)

| Initiative | Trigger | Notes |
|---|---|---|
| Switch to Target CPA bidding | 30+ primary conversions per campaign | Start with Target CPA = current CPL × 1.2 |
| Add Ad Group 6 — Entertainment & Storage (Campaign 1) | Budget allows + other ad groups stable | Low-competition, good intent |
| Add Ad Group 6 — Live Edge & Artisan (Campaign 2) | Budget allows | Highest buyer quality, lowest volume |
| Competitor campaign (Campaign 2) | 30 days post-launch | Target: Simply Cottage, Pioneer Furniture, Hemlock Cottage brand queries |
| Display remarketing | 500+ website visitors | Show Park Road ads to landing page visitors who did not convert |
| Demand Gen campaign | 60+ days, if budget allows | Muskoka/cottage lifestyle creative, broader Ontario awareness |

---

## BUDGET SUMMARY

| Campaign | Daily Budget | Monthly Estimate | Projected Clicks | Projected Leads (5% CVR) |
|---|---|---|---|---|
| Custom Furniture | $20–27/day | $600–$800 | 360–540 | 18–27 |
| Cottage Furniture | $20–40/day | $600–$1,200 | 400–800 | 20–40 |
| **Total (launch)** | **$40–67/day** | **$1,200–$2,000** | **760–1,340** | **38–67** |

**CPL target:** $50–$80/lead. At $5,000+ average order value, 1 closed sale per month covers the full ad spend.

---

## QUESTIONS? WHO TO ASK

All campaign questions, offer changes, or copy decisions: **Bishal**

Do not change keyword lists, landing page URLs, offer language, or conversion actions without checking the full brief first. Every setting in this doc has a reason tied to tracking integrity or campaign economics.
