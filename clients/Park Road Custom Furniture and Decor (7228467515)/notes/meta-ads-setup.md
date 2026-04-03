# Park Road Custom Furniture — Meta Ads Campaign Setup
**Client:** Park Road Custom Furniture and Decor
**Account ID:** 7228467515
**Prepared by:** Bishal
**Date:** 2026-03-31
**Campaigns:** hoski_custom_furniture_meta_1apr26 | hoski_cottage_furniture_meta_1apr26

> **STATUS:** Pre-launch. Do not activate campaigns until the Meta Pixel is verified firing on `go.parkroadfurniture.com` and all landing pages are live. Mirror the same prerequisites from the Google Ads campaign brief.

---

## TABLE OF CONTENTS

1. [Strategy Overview](#strategy-overview)
2. [Pixel and Tracking Setup](#pixel-and-tracking-setup)
3. [Campaign 1: Custom Furniture](#campaign-1-custom-furniture)
4. [Campaign 2: Cottage Furniture](#campaign-2-cottage-furniture)
5. [Creative Reference — All Ads](#creative-reference-all-ads)
6. [Audience Library](#audience-library)
7. [Budget Summary](#budget-summary)
8. [Launch Sequence](#launch-sequence)

---

## STRATEGY OVERVIEW

### Objective

Both campaigns use the **Leads** objective, optimizing for the `Lead` conversion event fired on each thank-you page. This matches the Google Ads setup and keeps attribution clean.

**Do not use Instant Forms.** Send all Meta traffic to the campaign-specific landing pages:
- Custom Furniture: `go.parkroadfurniture.com/custom-furniture`
- Cottage Furniture: `go.parkroadfurniture.com/cottage-furniture`

This ensures both Meta and Google leads are tracked through the same form, counted identically, and the CPL comparison is apples-to-apples.

### Meta vs. Google Role

| Platform | Role | Buyer Stage |
|---|---|---|
| Google Search | Capture active demand (hand-raisers) | Actively searching |
| Meta | Create demand + reach cottage/custom lifestyle buyers before they search | Awareness to consideration |

Meta will extend reach to homeowners and cottage owners who match the profile but haven't searched yet. This is particularly powerful for Cottage Furniture where the lifestyle angle (calm, warm, escape) drives aspiration before keyword intent forms.

### Naming Convention

Follow the same Hoski convention:
- Campaigns: `hoski_[topic]_meta_[day][mon][yr]`
- Ad Sets: `[topic]_[audience_type]_[geo]`
- Ads: `static[#]_[description]_[mon][yr]`

---

## PIXEL AND TRACKING SETUP

### Prerequisites

Before launching any Meta ads:

- [ ] Meta Pixel installed on `go.parkroadfurniture.com` (via GHL or direct code)
- [ ] `Lead` event firing on both thank-you pages:
  - `/custom-furniture/thank-you` fires `Lead` with `content_name: "CF - Form Submission"`
  - `/cottage-furniture/thank-you` fires `Lead` with `content_name: "Cottage - Form Submission"`
- [ ] Verify in Events Manager — test each thank-you page and confirm the Lead event appears
- [ ] Conversions API (CAPI) set up if possible — reduces signal loss from iOS 14+ blocking
- [ ] Custom conversion created for each campaign using the `content_name` parameter to separate CF leads from Cottage leads

### Conversion Setup in Meta

| Conversion Name | Event | Filter | Campaign |
|---|---|---|---|
| `CF - Lead (Meta)` | `Lead` | `content_name = CF - Form Submission` | Custom Furniture campaign |
| `Cottage - Lead (Meta)` | `Lead` | `content_name = Cottage - Form Submission` | Cottage Furniture campaign |

**Attribution window:** 7-day click, 1-day view (Meta default — acceptable for considered purchases at this price point).

---

## CAMPAIGN 1: CUSTOM FURNITURE

### Campaign Settings

| Setting | Value |
|---|---|
| Campaign name | `hoski_custom_furniture_meta_1apr26` |
| Objective | Leads |
| Conversion event | `CF - Lead (Meta)` |
| Buying type | Auction |
| Campaign budget | OFF — budget set at ad set level |
| Special ad category | None |

### Ad Set Structure

Two ad sets at launch. Test both. Pause the weaker one after 2 weeks.

---

#### Ad Set 1: custom_furniture_advantageplus_london

| Setting | Value |
|---|---|
| Ad set name | `custom_furniture_advantageplus_london` |
| Conversion location | Website |
| Conversion event | `CF - Lead (Meta)` |
| Budget | $20/day |
| Schedule | Run continuously from launch date |
| Audience | Advantage+ Audience (Meta chooses) |
| Geo | London ON + 60 km radius |
| Age | 30–65+ |
| Gender | All |
| Audience controls (suggestions only) | Home furnishings, Custom furniture, Interior design, Homeowner |
| Placements | Advantage+ Placements (all surfaces) |

**Rationale:** Advantage+ gives Meta full freedom to find converters. With a high-ticket, considered purchase, Meta's audience model outperforms manual targeting once the Pixel has 10+ conversions. Start here to build signal fast.

---

#### Ad Set 2: custom_furniture_interest_london

| Setting | Value |
|---|---|
| Ad set name | `custom_furniture_interest_london` |
| Conversion location | Website |
| Conversion event | `CF - Lead (Meta)` |
| Budget | $15/day |
| Schedule | Run continuously |
| Geo | London ON, Kitchener ON, Waterloo ON, Windsor ON, Guelph ON, Woodstock ON, Sarnia ON, St. Thomas ON |
| Age | 30–65+ |
| Gender | All |
| Detailed targeting | See Audience Library below |
| Placements | Facebook Feed, Instagram Feed, Facebook Stories, Instagram Stories, Instagram Reels |

**Interests to include (OR logic — any of these):**
- Home furnishings
- Interior design
- Home improvement
- Custom furniture
- Dining room furniture
- Bedroom furniture
- Solid wood furniture
- Renovation

**Behaviors to include:**
- Likely to move (next 3 months)
- Homeowners

**Exclusions:**
- Renters (if available in Canada targeting)
- Anyone who completed a Lead event in last 60 days (suppression — do not show to people who already submitted)

---

### Custom Furniture Creative Lineup (Campaign 1)

Four static ads. Run all four in both ad sets. Meta will auto-optimize delivery toward the best performer.

---

#### CF Static 1: "Built for How You Actually Live"

**File name:** `Static1_Custom Furniture $750 Offer_Statics_Apr2026`

**Visual direction:**
- Wide dining table or bedroom set in a clean, well-lit London home
- Warm natural light, real grain and finish visible
- No clutter — furniture is the hero
- Format: 1:1 (1080x1080) + 4:5 (1080x1350) + 9:16 for Stories/Reels
- No text overlay on the photo itself — copy goes in ad text fields

**Primary text (body):**
```
Most furniture is built for a showroom floor. Not your room.

At Park Road, every piece is made to order in London, Ontario — the size you need, the wood you want, the finish that fits your home.

$750 OFF your first custom order of $5,000 or more.

📍 761 Fanshawe Park Rd W, London   📞 (519) 660-0074
```

**Headline:** Built for Your Room. Built in London.

**Description:** Free in-home consultation available.

**CTA button:** Get Quote

**Destination URL:** `https://go.parkroadfurniture.com/custom-furniture`

---

#### CF Static 2: "No More Furniture That Almost Fits"

**File name:** `Static2_Custom Furniture $750 Offer_Statics_Apr2026`

**Visual direction:**
- Close-up on wood grain — table surface, leg joinery, or finish detail
- Texture and craftsmanship are the story
- Warm amber/honey tones
- Format: 1:1 + 4:5

**Primary text (body):**
```
You've been in furniture stores. You've measured. Nothing is quite right.

Wrong size. Wrong wood. Not made to last.

Park Road builds every piece to order using solid Canadian hardwood — custom size, custom finish, hand-built in our London workshop.

$750 OFF orders of $5,000+. Book a free in-home consultation.

📍 761 Fanshawe Park Rd W, London   📞 (519) 660-0074
```

**Headline:** Custom Furniture That Actually Fits

**Description:** Dining tables, beds, sofas — all built to order.

**CTA button:** Learn More

**Destination URL:** `https://go.parkroadfurniture.com/custom-furniture`

---

#### CF Static 3: "$750 OFF Your First Custom Order"

**File name:** `Static3_Custom Furniture $750 Offer_Statics_Apr2026`

**Visual direction:**
- Offer-forward layout — strong visual hierarchy with "$750 OFF" prominent
- Background: dark walnut or rich wood grain texture (client photos or sourced)
- White or cream text overlay
- Format: 1:1 + 9:16 (Stories version with bold offer text centered)

**Primary text (body):**
```
Your first custom order, $750 off.

Solid Canadian hardwood, built to your exact size and finish in London, Ontario. Dining tables, sofas, bedroom sets, and more.

Claim your discount — book a free consultation at the link below.

📍 761 Fanshawe Park Rd W, London   📞 (519) 660-0074
```

**Headline:** $750 OFF — Custom Furniture London ON

**Description:** On first custom order of $5,000 or more.

**CTA button:** Claim Offer

**Destination URL:** `https://go.parkroadfurniture.com/custom-furniture`

---

#### CF Static 4: "Real Wood. Real Craft. Real Difference."

**File name:** `Static4_Custom Furniture $750 Offer_Statics_Apr2026`

**Visual direction:**
- Split or diptych: left side shows flat-pack/big-box (generic, cold, bad light); right side shows Park Road piece (warm, rich grain, real home)
- Or: single lifestyle image of a customer room with a Park Road piece — candid, lived-in, not staged
- Format: 1:1 + 4:5

**Primary text (body):**
```
Big-box furniture is built to sell. Park Road furniture is built to last.

Every piece — dining tables, beds, sofas, entertainment units — is made to order in solid Canadian hardwood. No particle board. No veneers. No compromises.

Custom size. Custom finish. Built in London, Ontario.

$750 OFF your first order of $5,000+. Free in-home consultation included.

📍 761 Fanshawe Park Rd W, London   📞 (519) 660-0074
```

**Headline:** Not Big-Box. Custom Built in London ON.

**Description:** Real solid wood, made to order.

**CTA button:** Get Quote

**Destination URL:** `https://go.parkroadfurniture.com/custom-furniture`

---

## CAMPAIGN 2: COTTAGE FURNITURE

### Campaign Settings

| Setting | Value |
|---|---|
| Campaign name | `hoski_cottage_furniture_meta_1apr26` |
| Objective | Leads |
| Conversion event | `Cottage - Lead (Meta)` |
| Buying type | Auction |
| Campaign budget | OFF — budget set at ad set level |
| Special ad category | None |

### Ad Set Structure

Two ad sets at launch. Cottage Furniture gets broader Ontario geo — this is a province-wide market.

---

#### Ad Set 1: cottage_furniture_advantageplus_ontario

| Setting | Value |
|---|---|
| Ad set name | `cottage_furniture_advantageplus_ontario` |
| Conversion location | Website |
| Conversion event | `Cottage - Lead (Meta)` |
| Budget | $25/day |
| Schedule | Run continuously |
| Audience | Advantage+ Audience |
| Geo | Ontario (province-wide) |
| Age | 35–65+ |
| Gender | All |
| Audience controls (suggestions) | Cottage, Muskoka, Vacation homes, Farmhouse decor, Interior design, Homeowner |
| Placements | Advantage+ Placements |

---

#### Ad Set 2: cottage_furniture_interest_ontario

| Setting | Value |
|---|---|
| Ad set name | `cottage_furniture_interest_ontario` |
| Conversion location | Website |
| Conversion event | `Cottage - Lead (Meta)` |
| Budget | $20/day |
| Schedule | Run continuously |
| Geo | Ontario — exclude London ON (London is served by C1; keep Cottage reach province-wide) |
| Age | 35–65+ |
| Gender | All |
| Placements | Facebook Feed, Instagram Feed, Facebook Stories, Instagram Stories, Instagram Reels |

**Interests to include (OR logic):**
- Cottage
- Muskoka region
- Cottage life
- Vacation home
- Farmhouse decor
- Rustic home decor
- Interior design
- Dining room furniture
- Home furnishings

**Behaviors:**
- Homeowners
- Second home owners / vacation property (if available)
- Engaged shoppers (high-value buyers)

**Exclusions:**
- Anyone who already submitted a Lead in last 60 days

**Geographic note:** Run Ontario-wide. Cottage buyers search from Toronto, Barrie, Ottawa, and everywhere else in the province. London residents who want cottage furniture will overlap — that's fine. Let the algorithm decide.

---

### Cottage Furniture Creative Lineup (Campaign 2)

Four static ads based on the provided creative briefs. All four run in both ad sets.

**Photo source for all Cottage creatives:** `https://drive.google.com/drive/folders/1zfqm-Rr5mYWZvi58Zh7sTHgpnodTwtxb`

---

#### Cottage Static 1: "Bring The Cottage Feeling Home"

**File name:** `Static1_Cottage Furniture $750 Offer_Statics_March2026`
**Reference:** [MotionApp inspo](https://projects.motionapp.com/organization/634fd0f875a08309374b84f9/66019ddea28e1e98cf74e1cb/inspo/ad/966378142501506)

**Overlay text (on image):**
- Headline: **Bring The Cottage Feeling Home**
- Body: A space that feels calm, inviting, and lived in
- Offer badge: **$750 OFF Orders $5,000+**
- Footer: 📍 761 Fanshawe Park Rd W, London   📞 (519) 660-0074

**Photo direction:** Warm cottage dining or living room. Natural light from a window. Wood-toned furniture — farmhouse table or solid wood sofa. Lived-in feel, not staged.

**Format:** 1:1 (1080x1080) primary + 4:5 (1080x1350) + 9:16 (1080x1920) for Stories

**Primary text (body copy in Meta):**
```
Your home can feel like a cottage retreat.

Calm. Warm. Made for the way you actually live.

Park Road builds custom solid wood furniture to order — any size, any finish, delivered across Ontario.

$750 OFF orders of $5,000 or more. Book a free consultation.

📍 761 Fanshawe Park Rd W, London   📞 (519) 660-0074
```

**Headline:** Bring The Cottage Feeling Home

**Description:** Custom solid wood furniture. Built to order.

**CTA button:** Get Quote

**Destination URL:** `https://go.parkroadfurniture.com/cottage-furniture`

---

#### Cottage Static 2: "Clean, Calm, and Inviting"

**File name:** `Static2_Cottage Furniture $750 Offer_Statics_March2026`
**Reference:** [Atria inspo](https://app.tryatria.com/ad/m1308632981290620)

**Overlay text (on image):**
- Headline: **Clean, calm, and inviting**
- Subhead: Designed to feel like a quiet escape from everything else
- Offer: **Get $750 OFF When You Spend $5,000+**
- Footer: 📍 761 Fanshawe Park Rd W, London   📞 (519) 660-0074

**Photo direction:** Minimal, airy cottage living room or bedroom. Light wood tones, natural linen textures, soft morning light. No clutter. The space feels like a deep exhale.

**Format:** 1:1 + 4:5

**Primary text (body copy in Meta):**
```
Designed to feel like a quiet escape from everything else.

Clean lines. Natural wood. A space that slows you down the moment you walk in.

Park Road custom furniture is built to order — your size, your finish, your cottage.

Get $750 OFF when you spend $5,000+.

📍 761 Fanshawe Park Rd W, London   📞 (519) 660-0074
```

**Headline:** Clean, Calm, and Inviting

**Description:** Custom cottage furniture. Built to order in Ontario.

**CTA button:** Learn More

**Destination URL:** `https://go.parkroadfurniture.com/cottage-furniture`

---

#### Cottage Static 3: "$750 OFF When You Spend $5,000+"

**File name:** `Static3_Cottage Furniture $750 Offer_Statics_March2026`
**Reference:** [Atria inspo](https://app.tryatria.com/ad/m1417334119738520)
**Photo source:** `https://drive.google.com/drive/folders/1zfqm-Rr5mYWZvi58Zh7sTHgpnodTwtxb`

**Overlay text (on image):**
- Headline: **$750 OFF When You Spend $5,000+**
- Body: Create a home that feels relaxed, warm, and effortless
- Footer: 📍 761 Fanshawe Park Rd W, London   📞 (519) 660-0074

**Photo direction:** Use client photos from the Google Drive folder linked above. Select the strongest image — ideally a farmhouse table or cottage living room with visible wood grain and warm natural light.

**Format:** 1:1 + 4:5 + 9:16 (offer-forward, works well as Stories)

**Primary text (body copy in Meta):**
```
Create a home that feels relaxed, warm, and effortless.

For a limited time, get $750 OFF your first custom furniture order of $5,000 or more.

Every piece is built to your exact size and finish — solid Canadian hardwood, delivered across Ontario.

Book a free consultation to get started.

📍 761 Fanshawe Park Rd W, London   📞 (519) 660-0074
```

**Headline:** $750 OFF — Custom Cottage Furniture

**Description:** On orders of $5,000 or more. Limited time.

**CTA button:** Claim Offer

**Destination URL:** `https://go.parkroadfurniture.com/cottage-furniture`

---

#### Cottage Static 4: "Make Your Home Feel Warmer"

**File name:** `Static4_Cottage Furniture $750 Offer_Statics_March2026`
**Reference:** [MotionApp inspo](https://projects.motionapp.com/organization/634fd0f875a08309374b84f9/66019ddea28e1e98cf74e1cb/inspo/ad/1351424240158359)

**Overlay text (on image):**
- Headline: **Make Your Home Feel Warmer**
- Body (stacked lines):
  Natural materials
  Thoughtful design
  A space made for you
- Offer: **$750 OFF When You Spend $5,000+**
- Footer: 📍 761 Fanshawe Park Rd W, London   📞 (519) 660-0074

**Photo direction:** Rich, warm-toned image. Dark walnut table or warm oak bedroom set. A candle, a book, a glass — something that signals this space is lived in and loved. Moody warmth, not cold minimalism.

**Format:** 1:1 + 4:5

**Primary text (body copy in Meta):**
```
Natural materials. Thoughtful design. A space made for you.

The right furniture doesn't just fill a room. It changes how the room feels.

Park Road builds custom pieces in solid Canadian hardwood — dining tables, sofas, bedroom sets — all made to order in London, Ontario.

$750 OFF when you spend $5,000+.

📍 761 Fanshawe Park Rd W, London   📞 (519) 660-0074
```

**Headline:** Make Your Home Feel Warmer

**Description:** Solid Canadian hardwood. Built to order.

**CTA button:** Get Quote

**Destination URL:** `https://go.parkroadfurniture.com/cottage-furniture`

---

## CREATIVE REFERENCE — ALL ADS

| # | Campaign | File Name | Headline | CTA | Status |
|---|---|---|---|---|---|
| CF-1 | Custom Furniture | Static1_Custom Furniture $750 Offer_Statics_Apr2026 | Built for Your Room. Built in London. | Get Quote | Needs creative production |
| CF-2 | Custom Furniture | Static2_Custom Furniture $750 Offer_Statics_Apr2026 | Custom Furniture That Actually Fits | Learn More | Needs creative production |
| CF-3 | Custom Furniture | Static3_Custom Furniture $750 Offer_Statics_Apr2026 | $750 OFF — Custom Furniture London ON | Claim Offer | Needs creative production |
| CF-4 | Custom Furniture | Static4_Custom Furniture $750 Offer_Statics_Apr2026 | Not Big-Box. Custom Built in London ON. | Get Quote | Needs creative production |
| C2-1 | Cottage Furniture | Static1_Cottage Furniture $750 Offer_Statics_March2026 | Bring The Cottage Feeling Home | Get Quote | Ready for production |
| C2-2 | Cottage Furniture | Static2_Cottage Furniture $750 Offer_Statics_March2026 | Clean, Calm, and Inviting | Learn More | Ready for production |
| C2-3 | Cottage Furniture | Static3_Cottage Furniture $750 Offer_Statics_March2026 | $750 OFF — Custom Cottage Furniture | Claim Offer | Ready — photos in Drive |
| C2-4 | Cottage Furniture | Static4_Cottage Furniture $750 Offer_Statics_March2026 | Make Your Home Feel Warmer | Get Quote | Ready for production |

**Photo source for Cottage creatives:** `https://drive.google.com/drive/folders/1zfqm-Rr5mYWZvi58Zh7sTHgpnodTwtxb`

**Custom Furniture photos:** Request from client — showroom or workshop photos, real installs preferred. AI prompt brief available if no client photos exist yet.

---

## AUDIENCE LIBRARY

Save these as saved audiences in Meta Ads Manager for reuse.

### Audience 1: London ON Homeowners — Custom Furniture

| Parameter | Value |
|---|---|
| Name | `Park Road — London Homeowners` |
| Geo | London ON + 60 km (covers SW Ontario) |
| Age | 30–65+ |
| Interests | Home furnishings, Interior design, Custom furniture, Home improvement, Bedroom furniture, Dining room |
| Behaviors | Homeowners, Likely to move (next 3 months) |
| Exclusions | Recent lead submitters (30 days) |

### Audience 2: Ontario Cottage Buyers

| Parameter | Value |
|---|---|
| Name | `Park Road — Ontario Cottage Buyers` |
| Geo | Ontario province-wide |
| Age | 35–65+ |
| Interests | Cottage, Muskoka, Vacation home, Farmhouse decor, Rustic home decor, Interior design |
| Behaviors | Homeowners, Engaged shoppers |
| Exclusions | Recent lead submitters (30 days) |

### Audience 3: Website Retargeting (activate at 500+ visitors)

| Parameter | Value |
|---|---|
| Name | `Park Road — Website Visitors 30d` |
| Source | Meta Pixel — All website visitors |
| Window | Last 30 days |
| Exclusions | Anyone who completed Lead event (already converted) |
| Use in | Separate retargeting ad set, lower budget ($10/day), higher urgency copy |

**Retargeting copy angle:** "Still thinking about it? $750 off expires soon."

### Audience 4: Lookalike (activate after 50+ conversions)

Once the Pixel has 50+ Lead events, create:
- 1% Lookalike based on `CF - Lead (Meta)` custom conversion — for Custom Furniture campaign
- 1% Lookalike based on `Cottage - Lead (Meta)` — for Cottage Furniture campaign

Apply to new ad sets. Compare CPL vs. interest targeting and allocate budget to the winner.

---

## BUDGET SUMMARY

| Campaign | Ad Set | Daily Budget | Monthly Est. |
|---|---|---|---|
| Custom Furniture | `custom_furniture_advantageplus_london` | $20/day | $600 |
| Custom Furniture | `custom_furniture_interest_london` | $15/day | $450 |
| Cottage Furniture | `cottage_furniture_advantageplus_ontario` | $25/day | $750 |
| Cottage Furniture | `cottage_furniture_interest_ontario` | $20/day | $600 |
| **Total (launch)** | | **$80/day** | **$2,400/month** |

**Scaling rule:** After 14 days, pause the weaker ad set in each campaign (higher CPL). Reallocate budget to the winner. Do not increase any single ad set budget by more than 20% in a 7-day window — larger increases reset the learning phase.

**CPL target:** $50–$80/lead. At $5,000+ average order value, 1 closed sale per month covers full Meta spend.

---

## LAUNCH SEQUENCE

### Before Launch

- [ ] Meta Pixel installed on `go.parkroadfurniture.com`
- [ ] `Lead` event verified firing on `/custom-furniture/thank-you`
- [ ] `Lead` event verified firing on `/cottage-furniture/thank-you`
- [ ] Two custom conversions created in Events Manager (`CF - Lead (Meta)`, `Cottage - Lead (Meta)`)
- [ ] All 8 static images produced (4 per campaign) in 1:1, 4:5, and 9:16 formats
- [ ] Client photos sourced from Drive or new shoot organized
- [ ] Business Manager / Ad Account access confirmed for Hoski

### Launch Day

- [ ] Create both campaigns in Meta Ads Manager
- [ ] Set up 2 ad sets per campaign with correct geo, audience, and budget
- [ ] Upload all 8 creatives with correct primary text, headlines, and CTAs
- [ ] Set conversion event to `CF - Lead (Meta)` for Campaign 1 and `Cottage - Lead (Meta)` for Campaign 2
- [ ] Set both campaigns to Paused — review targeting one final time
- [ ] Activate both campaigns

### Week 1–2 Review

- [ ] Check delivery — are both campaigns exiting Learning Phase? (Minimum 50 optimization events to exit)
- [ ] Monitor CPL — if over $120, check creative quality, landing page, and audience overlap
- [ ] Check frequency — if above 3.0 within 2 weeks, audience is too small or budget too high
- [ ] Review which creatives are getting the most impressions and conversions
- [ ] Pause weakest creative in each ad set if clear winner emerges

### Day 30 Review

- [ ] Compare CPL: Meta vs. Google Ads (by campaign: CF vs. Cottage)
- [ ] Identify which ad set (Advantage+ vs. Interest) won — consolidate budget to winner
- [ ] If 50+ Lead events per campaign: build Lookalike audiences and launch new ad sets
- [ ] If website has 500+ visitors: activate retargeting ad set with urgency copy
- [ ] Review which creative angle won — brief new creatives based on winning concept
- [ ] Increase budget 20% on any ad set with CPL under $60

---

## NOTES FOR CLIENT HANDOFF

1. **Photos are the biggest lever.** Real customer installs outperform product-only shots. If the client has any photos of furniture in customer homes, get them before launching. AI-generated images are acceptable as a backup but convert worse.

2. **The $750 offer is the hook.** Every ad leads with it or anchors the close with it. Do not dilute by adding too many secondary messages.

3. **Meta and Google target the same buyer at different moments.** Google catches them when they search. Meta catches them before they search. Both are needed to own the full funnel.

4. **Do not combine Custom Furniture and Cottage Furniture into one campaign.** The audiences, geos, and creative angles are different enough that combining them would hurt optimization. Keep them separate.

5. **Pixel signal takes time.** In the first 7–10 days, the ads will be in Learning Phase. Do not judge performance or make significant changes during this window.
