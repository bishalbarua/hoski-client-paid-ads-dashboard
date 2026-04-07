# FaBesthetics — Meta Ads Campaign Setup
**Client:** FaBesthetics Face & Body Med Spa
**Google Ads Account ID:** 9304117954
**Prepared by:** Marketing Director / Meta Ads Manager
**Date:** 2026-04-06
**Campaigns:** hoski_lhr_prospecting_meta_6apr26 | hoski_lhr_retargeting_meta_6apr26

> **STATUS:** Ready to build. Meta Pixel confirmed working on both domains. Do not activate campaigns until: (1) Meta budget confirmed with Dan, (2) Business Manager account access confirmed, (3) Instagram account linked to Business Manager, (4) creative assets approved.

---

## TABLE OF CONTENTS

1. [Strategy Overview](#strategy-overview)
2. [Pixel and Tracking](#pixel-and-tracking)
3. [Campaign 1: Prospecting — Laser Hair Removal](#campaign-1-prospecting)
4. [Campaign 2: Retargeting — Laser Hair Removal](#campaign-2-retargeting)
5. [Creative Reference — All Ads](#creative-reference)
6. [Audience Library](#audience-library)
7. [Budget Summary](#budget-summary)
8. [Launch Sequence](#launch-sequence)
9. [Learning Phase Rules](#learning-phase-rules)

---

## STRATEGY OVERVIEW

### Why Meta

Google captures demand. Meta creates it. FaBesthetics' Google Search campaign is only capturing 10% of available impressions — budget constraints mean 90% of people searching for laser hair removal in the area never see the ad. Meta reaches the much larger group who would book laser hair removal but haven't searched yet. These two channels are additive, not competitive.

### The Offer

**15% off when booking 4 or more laser sessions.**
Landing page: `go.fabestheticsny.com/laser-hair-removal-mahopac-offer/`

This offer is identical to what runs on Google. This is intentional: attribution will be cross-channel, and some leads will see a Meta ad first and then convert via Google search. Total lead volume is the right metric, not Meta-only leads.

### Objective

Both campaigns use the **Leads** objective, optimizing for the `Lead` conversion event (form submission on the GHL landing page). Do not use Instant Forms — the landing page has a proven conversion form and pixel tracking in place.

### Naming Convention

- Campaigns: `hoski_[topic]_meta_[day][mon][yr]`
- Ad Sets: `lhr_[audience_type]_[geo_descriptor]`
- Ads: `static[#]_[angle]_[mon][yr]` or `carousel[#]_[angle]_[mon][yr]` or `video[#]_[angle]_[mon][yr]`

### Lead Quality Constraint

**Critical:** FaBesthetics had a lead quality problem with the $99 special — it attracted price-shoppers, not package buyers. All creative must signal premium, personalized care. Do NOT use language like "SALE," "DEAL," "DISCOUNT," or "CHEAP." Frame the 15% as saving on a package — not as a bargain.

---

## PIXEL AND TRACKING

### Status

| Item | Status |
|---|---|
| Meta Pixel on fabestheticsny.com | CONFIRMED WORKING |
| Meta Pixel on go.fabestheticsny.com/laser-hair-removal-mahopac-offer/ | CONFIRMED WORKING |
| Lead event on form submission (GHL landing page) | CONFIRMED |

### Quick Sanity Check Before Launch

Before activating campaigns, run the Test Events tool in Meta Events Manager:
1. Open the landing page in a browser
2. Submit the form (use a test entry)
3. Confirm the `Lead` event appears in Events Manager within 5 minutes

This takes 5 minutes and eliminates any risk of launching with a broken optimization signal.

### Attribution Window

Set to: **7-day click, 1-day view** (Meta default). This is appropriate for a considered local service purchase.

### CAPI Note

Conversions API (CAPI) is not confirmed implemented. CAPI reduces iOS 14+ signal loss (estimated 20-40% underreporting without it). Flag for implementation after launch is stable. Not a launch blocker but should be set up within 30 days.

---

## CAMPAIGN 1: PROSPECTING

### Campaign Settings

| Setting | Value |
|---|---|
| Campaign name | `hoski_lhr_prospecting_meta_6apr26` |
| Objective | Leads |
| Conversion location | Website |
| Conversion event | Lead |
| Buying type | Auction |
| Campaign budget | OFF — budget set at ad set level (ABO) |
| Special ad category | None |
| A/B test | Off at launch |

---

### Ad Set 1A: lhr_interests_mahopac_25mi

This is the launch ad set. Interest-based with geographic guardrails while the pixel accumulates conversion signal.

| Setting | Value |
|---|---|
| Ad set name | `lhr_interests_mahopac_25mi` |
| Conversion location | Website |
| Conversion event | Lead |
| Budget | $75/day |
| Schedule | Run continuously from launch date |
| Geo | Mahopac, NY + 25-mile radius |
| Age | 25–54 |
| Gender | Female |
| Detailed targeting (OR logic — any) | See Audience Library — Audience 1 |
| Placements | Advantage+ Placements (all surfaces — let Meta optimize) |

**Audience note:** Mahopac + 25 miles covers Peekskill, Yorktown, Carmel, White Plains, parts of Westchester, Putnam, and Dutchess counties. If Meta reports "Audience too small" or delivery throttles in the first week, immediately widen radius to 35 miles — do not add more interest layers (that narrows the audience further).

**Exclusions (required):**
- All website visitors — fabestheticsny.com and go.fabestheticsny.com — any date window
- Facebook + Instagram page engagers — last 60 days
- Customer list (if Becky provides one — upload before launch if available)

---

### Ad Set 1B: lhr_broad_mahopac_25mi — HOLD (Test After 20 Conversions)

Do not launch this ad set at the same time as 1A. After 1A has accumulated 20+ Lead events, test Broad targeting (no interest filters — geo + age + gender only) against 1A to see which produces lower CPL.

| Setting | Value |
|---|---|
| Ad set name | `lhr_broad_mahopac_25mi` |
| Budget | $75/day (same as 1A — pause 1A when launching 1B test, or split budget) |
| Geo | Mahopac, NY + 25-mile radius |
| Age | 25–54 |
| Gender | Female |
| Detailed targeting | None (broad — let Meta find buyers autonomously) |
| Exclusions | Same as 1A |

---

### Campaign 1 Creative Lineup

Run all Tier 1 ads in Ad Set 1A at launch. Meta will auto-optimize delivery toward top performers. Do not manually pause underperformers until 7 days of data with 1,000+ impressions per ad.

---

#### Ad 1 — Static 1: Problem-First

**File name:** `static1_problem_first_lhr_apr2026`
**Format:** 1:1 (1080x1080) primary + 4:5 (1080x1350) for feed + 9:16 (1080x1920) for Stories/Reels

**Visual direction:**
Clean, relatable image connected to the waxing/shaving routine — a bathroom counter with a razor and shaving products, a woman's legs with visible razor bumps, or a waxing strip. No nudity. The pain point is the visual hook. Alternatively: a before/after lifestyle comparison (shaving routine chaos vs. smooth confident woman in a summer dress). FaBesthetics brand colors (pink/magenta) in text overlay if applicable.

**Primary text (body copy):**
```
You've been shaving since you were a teenager.

Waxing every 4 weeks. Ingrowns. Razor burn. The same cycle, every single time.

There's a permanent way out of it.

At FaBesthetics in Mahopac, Becky Pfeifer BSN delivers laser hair removal with the kind of personal attention most clinics don't offer. Every client, every time — treated like a VIP.

⭐⭐⭐⭐⭐ "I can't believe I waited this long to do this."

Save 15% when you book 4 or more sessions.
```

**Headline:** Say Goodbye to the Waxing Routine.

**Description:** Laser hair removal in Mahopac, NY. Performed by Becky Pfeifer, BSN.

**CTA button:** Book Now

**Destination URL:** `https://go.fabestheticsny.com/laser-hair-removal-mahopac-offer/`

---

#### Ad 2 — Carousel 1: Social Proof / Local Signal

**File name:** `carousel1_social_proof_lhr_apr2026`
**Format:** 3-card carousel. Each card: 1:1 (1080x1080)

**Primary text (shown above all carousel cards):**
```
Mahopac women are switching from waxing to laser — here's why.

FaBesthetics Face & Body Med Spa. Becky Pfeifer, BSN. Right here in Mahopac, NY.

Save 15% when you book 4+ sessions. See what clients are saying below.
```

**Card 1:**

Visual: 5-star rating graphic (⭐⭐⭐⭐⭐ shown visually, large) on a brand-pink background. Pull a real review quote in large white text.

Headline: "From the Moment You Walk in the Door..."

Description: Real reviews. Real results. Mahopac, NY.

Suggested review quote for visual (use actual verbatim Google review text — pull from Becky's Google Business Profile): *"From the moment you walk through the door, beautifully decorated and impeccably clean."*

CTA: Learn More
URL: `https://go.fabestheticsny.com/laser-hair-removal-mahopac-offer/`

---

**Card 2:**

Visual: Professional photo of Becky in a clinical/spa setting — white coat or professional attire, clean spa background. If no photo is available, use a clean image of the FaBesthetics treatment room or spa interior.

Headline: Performed by Becky Pfeifer, BSN

Description: Licensed nurse. Personalized care. Every client is a VIP.

CTA: Book Now
URL: `https://go.fabestheticsny.com/laser-hair-removal-mahopac-offer/`

---

**Card 3:**

Visual: Clean offer card — pink/magenta background (FaBesthetics brand color), white bold text. "15% OFF" large and prominent, followed by "When You Book 4+ Laser Sessions."

Headline: 15% Off — Book Your Package Today

Description: Claim your savings at fabestheticsny.com

CTA: Claim Offer
URL: `https://go.fabestheticsny.com/laser-hair-removal-mahopac-offer/`

---

#### Ad 3 — Video 1: Becky On-Camera (Tier 2 — Launch Week 3-4)

**File name:** `video1_becky_objection_handler_lhr_apr2026`
**Format:** 9:16 vertical (1080x1920) for Reels/Stories primary + 4:5 (1080x1350) for Feed

**Production note:** This is a talking-to-camera video with Becky. Phone quality is acceptable — authenticity matters more than production value. Becky should speak naturally, not read a script. Use a clean, well-lit treatment room or front desk as the backdrop.

**Video script outline (30-45 seconds):**

> **[0-3 seconds — HOOK]**
> "The question I get most often is: does laser hair removal actually hurt?"
> *(Becky looks directly at camera, warm and direct)*

> **[3-15 seconds — ANSWER]**
> "Honestly? Most people are surprised. It feels like a rubber band snap — quick, manageable, and it gets easier with each session. As a nurse, I've worked with all kinds of clients and all kinds of concerns. My whole approach is making sure you feel comfortable and informed before we do anything."

> **[15-30 seconds — PROOF + DIFFERENTIATOR]**
> "I've been doing this [X years / since YEAR] at FaBesthetics here in Mahopac, and what I hear most is that people wish they'd done it sooner. Real results, real sessions, and I'm with you every step of the way."

> **[30-45 seconds — OFFER + CTA]**
> "Right now we have a special — save 15% when you book four or more sessions. If you've been on the fence, book a consultation and just ask me anything. The link is below."

**On-screen text overlay (for silent viewing):**
- Hook text at top: "Does laser hair removal hurt?"
- Name bar: "Becky Pfeifer, BSN | FaBesthetics, Mahopac NY"
- End screen: "Save 15% — Book 4+ Sessions" + CTA button

**Primary text (ad copy fields):**
```
"The number one question I get: does laser hair removal actually hurt?"

Watch Becky Pfeifer, BSN — the nurse behind FaBesthetics — answer that question and everything else you've been wondering about.

Real expertise. Personalized care. Right here in Mahopac, NY.

Save 15% when you book 4 or more sessions. Book a free consultation below — and ask me anything.
```

**Headline:** Ask the Nurse: Everything You Want to Know About Laser

**Description:** Becky Pfeifer, BSN | FaBesthetics, Mahopac NY

**CTA button:** Book Now

**Destination URL:** `https://go.fabestheticsny.com/laser-hair-removal-mahopac-offer/`

---

## CAMPAIGN 2: RETARGETING

**STATUS: HOLD — Do not build until Day 35 post-launch. Activate only when the retargeting custom audience reaches 500+ people in Meta Ads Manager.**

### Campaign Settings

| Setting | Value |
|---|---|
| Campaign name | `hoski_lhr_retargeting_meta_6apr26` |
| Objective | Leads |
| Conversion location | Website |
| Conversion event | Lead |
| Buying type | Auction |
| Campaign budget | OFF — budget set at ad set level (ABO) |
| Special ad category | None |

---

### Ad Set 2A: lhr_warm_visitors_engagers_30d

| Setting | Value |
|---|---|
| Ad set name | `lhr_warm_visitors_engagers_30d` |
| Conversion location | Website |
| Conversion event | Lead |
| Budget | $25/day |
| Schedule | Run continuously |
| Audience | Custom audience (see Audience Library — Audience 3) |
| Age | No restriction (let custom audience define it) |
| Gender | No restriction |
| Placements | Facebook Feed, Instagram Feed, Facebook Stories, Instagram Stories |

**Audience combination:**
- INCLUDE: Website visitors (all pages, fabestheticsny.com + go.fabestheticsny.com, last 30 days)
- INCLUDE: Facebook + Instagram page engagers (last 60 days)

**Exclusions (required):**
- People who already submitted the Lead form — Lead event custom audience, last 60 days (already in pipeline)
- Customer list (if available — already a client, wrong message)

**Retargeting window rationale:** Laser hair removal is a considered purchase. 30-day visitor window captures active consideration. 60-day engager window captures people who interacted with content but haven't clicked through.

**Important:** Evaluate this campaign on reach, frequency, and assisted conversions — NOT standalone CPL. At $25/day it will not exit Meta's learning phase in a normal timeline (~137 days to 50 conversions). Its job is to keep FaBesthetics visible to warm contacts, not to optimize the algorithm.

---

### Campaign 2 Creative Lineup

---

#### Ad 4 — Static 2: Retargeting Offer Reminder

**File name:** `static2_retargeting_reminder_lhr_apr2026`
**Format:** 1:1 (1080x1080) + 4:5 (1080x1350)

**Visual direction:**
Clean, simple branded image. FaBesthetics logo or spa interior image. Minimal text overlay: "Your 15% Off Is Still Here." No heavy messaging needed — this audience already knows the brand.

**Primary text (body copy):**
```
Still thinking about laser hair removal?

Your 15% savings is still available — book 4 or more sessions at FaBesthetics and claim your discount.

Becky Pfeifer, BSN is ready when you are. Free consultation, no commitment required to start.
```

**Headline:** Your 15% Off Is Still Waiting.

**Description:** Book 4+ laser sessions at FaBesthetics, Mahopac NY.

**CTA button:** Book Now

**Destination URL:** `https://go.fabestheticsny.com/laser-hair-removal-mahopac-offer/`

---

## CREATIVE REFERENCE

| # | Campaign | File Name | Format | Angle | Headline | CTA | Tier | Status |
|---|---|---|---|---|---|---|---|---|
| Ad 1 | Prospecting | `static1_problem_first_lhr_apr2026` | Static 1:1 + 4:5 + 9:16 | Problem-first | Say Goodbye to the Waxing Routine. | Book Now | Tier 1 | Needs production |
| Ad 2 | Prospecting | `carousel1_social_proof_lhr_apr2026` | 3-card carousel 1:1 | Social proof / local | Mahopac women switching to laser | Learn More / Book Now / Claim Offer | Tier 1 | Needs production |
| Ad 3 | Prospecting | `video1_becky_objection_handler_lhr_apr2026` | Vertical video 9:16 + 4:5 | Becky on camera / objection handler | Ask the Nurse: Everything You Want to Know | Book Now | Tier 2 | Needs Becky availability confirmation |
| Ad 4 | Retargeting | `static2_retargeting_reminder_lhr_apr2026` | Static 1:1 + 4:5 | Offer reminder | Your 15% Off Is Still Waiting. | Book Now | Tier 2 | Build when retargeting campaign is activated |

**Creative production notes:**

- **Ad 1 (Static):** Needs a strong visual tied to the waxing/shaving pain point OR a clean lifestyle "after" image. Request from Becky/Dan: does FaBesthetics have any client photos or high-quality spa/treatment room photos? Real photos outperform stock. If none available, AI-generated image is a backup.
- **Ad 2 (Carousel):** Card 1 needs a real Google review quote — pull verbatim from Becky's Google Business Profile. Card 2 needs a photo of Becky (professional headshot or clinical setting). Card 3 is a designed offer card — no photography needed.
- **Ad 3 (Video):** Requires Becky on camera. Confirm with Dan/Becky before scheduling production. Phone quality is fine — Becky should speak naturally. Goal is authenticity, not polish.
- **Ad 4 (Retargeting static):** Simplest production requirement — logo, clean background, short copy. Can be produced quickly once retargeting campaign is ready to activate.

---

## AUDIENCE LIBRARY

Save these as saved audiences in Meta Ads Manager for reuse.

### Audience 1: Women — Mahopac 25mi — Beauty Interests (Prospecting)

| Parameter | Value |
|---|---|
| Name | `FAB — Women LHR Interests 25mi` |
| Geo | Mahopac, NY + 25-mile radius |
| Age | 25–54 |
| Gender | Female |
| Detailed targeting (OR — any of these) | Laser hair removal, Waxing, Beauty salon, Skincare, Spa, Medical spa, Personal care, Beauty treatments |
| Exclusions | All website visitors (any window) + Page engagers (60 days) + Customer list (if available) |

**Audience size note:** Target is 100,000–200,000. If Meta shows "Audience too small" or frequency spikes above 3.0 within the first two weeks, immediately widen radius to 35 miles. Do not add more interests to compensate — that narrows, not widens.

---

### Audience 2: Broad — Mahopac 25mi (Test After 20 Conversions)

| Parameter | Value |
|---|---|
| Name | `FAB — Women LHR Broad 25mi` |
| Geo | Mahopac, NY + 25-mile radius |
| Age | 25–54 |
| Gender | Female |
| Detailed targeting | None (broad — Meta finds buyers autonomously) |
| Exclusions | Same as Audience 1 |

Do not activate until prospecting campaign has 20+ Lead events.

---

### Audience 3: Website Visitors + Page Engagers (Retargeting)

| Parameter | Value |
|---|---|
| Name | `FAB — Warm Visitors + Engagers 30-60d` |
| Source 1 | Meta Pixel — all website visitors (fabestheticsny.com + go.fabestheticsny.com) — last 30 days |
| Source 2 | Facebook + Instagram page engagers — last 60 days |
| Exclusions | Lead event custom audience (last 60 days) + Customer list (if available) |

Activate retargeting campaign when this audience reaches 500+ people in Meta Audiences tab.

---

### Audience 4: 1% Lookalike (Activate After 50 Conversions)

| Parameter | Value |
|---|---|
| Name | `FAB — 1% LAL from Leads` |
| Seed | Lead event custom audience (all-time) |
| Size | 1% (tightest match) |
| Geo | Mahopac, NY + 25-mile radius (or expand to full Westchester if size is insufficient) |

Do not create or activate until pixel has recorded 50+ Lead events. A lookalike built before 50 seed events is too noisy to be useful.

---

### Audience 5: Customer List Lookalike (Activate If List Available)

If Becky can provide a CSV of past client emails/phone numbers (even 50+ records):
- Upload as a customer list in Meta Audiences
- Create 1% Lookalike from the list
- Test against the pixel-based lookalike

This is a Q3 initiative — flag with PM to ask Becky/Dan.

---

## BUDGET SUMMARY

| Campaign | Ad Set | Daily Budget | Monthly Est. | Status |
|---|---|---|---|---|
| Prospecting | `lhr_interests_mahopac_25mi` | $75/day | $2,250 | Launch (after pre-launch gates cleared) |
| Retargeting | `lhr_warm_visitors_engagers_30d` | $25/day | $750 | HOLD (Day 35+) |
| **Launch total** | | **$75/day** | **$2,250** | (Retargeting not active at launch) |
| **Full total** | | **$100/day** | **$3,000** | (After retargeting activates) |

**Budget assumption:** $100/day total ($3,000/month) based on Dan's prior Meta spend. Must be confirmed with Dan before campaign activation.

**If confirmed budget is different:**
- Under $60/day: Run prospecting only. No retargeting until budget increases.
- $60–$100/day: Structure above (adjust $75/$25 split proportionally).
- $150+/day: Add men's LHR prospecting ad set at $20-25/day after 30 days of data.

**Scaling rule:** After 14 days, if interest-based ad set is delivering at <$100 CPL, increase budget by maximum 20% in a 7-day window. Never increase by more than 20% in one move — larger increases reset the learning phase.

---

## LAUNCH SEQUENCE

### Pre-Launch Checklist

- [x] Meta Pixel installed and working on fabestheticsny.com
- [x] Meta Pixel + Lead event working on go.fabestheticsny.com/laser-hair-removal-mahopac-offer/
- [ ] Run Test Events tool — confirm Lead event fires on form submission (5 min) | Bishal
- [ ] Confirm Meta budget with Dan: is $100/day confirmed? | PM (Dess/Zara)
- [ ] Confirm Meta Business Manager account: same account as Dan's prior campaigns, or new setup? | PM + Bishal
- [ ] Confirm FaBesthetics Instagram account linked to Meta Business Manager | Bishal
- [ ] Check Audiences tab in Business Manager: do engager/visitor custom audiences from prior campaigns exist? | Bishal
- [ ] Creative production: Tier 1 (Ad 1 static + Ad 2 carousel) — confirm photos and review text available | PM outreach to Dan/Becky
- [ ] Confirm Becky is available and willing to record a 30-45 sec talking-to-camera video (Ad 3) | PM
- [ ] Build campaign structure in Ads Manager — do NOT activate | Ghufran

### Launch Day

- [ ] Create Campaign 1 (`hoski_lhr_prospecting_meta_6apr26`) with Leads objective
- [ ] Build Ad Set 1A (`lhr_interests_mahopac_25mi`) with targeting, budget, and exclusions per this document
- [ ] Upload Ad 1 (static) in 1:1 + 4:5 formats — confirm primary text, headline, CTA, URL
- [ ] Upload Ad 2 (carousel) — 3 cards, confirm each card's headline, CTA, and URL
- [ ] Set campaign to Paused — review all settings one final time
- [ ] Activate campaign

### First 3 Days (Manager Monitoring)

- [ ] Day 1: Confirm campaign is delivering (spend > $0) — if zero delivery, check: disapprovals, audience too small, payment method issue
- [ ] Day 2: Check for any ad disapprovals in Ads Manager — review and resolve immediately
- [ ] Day 3: Check early frequency — if frequency already above 2.0 in 3 days, audience is too small — widen radius to 35 miles immediately
- [ ] Do NOT make any other changes for the first 7 days — learning phase is active

### Week 2 Review

- [ ] Check delivery and early CPL — do not judge performance yet (learning phase)
- [ ] Check frequency — if above 2.0 at 7 days, widen radius or remove tightest interest filter
- [ ] Check for any disapprovals or policy issues
- [ ] Confirm Ad 3 (Becky video) production timeline — target launch Week 3-4
- [ ] Begin checking retargeting audience size in Audiences tab (targeting activation at 500+)

### Day 35 Review

- [ ] Check prospecting CPL trend over last 2 weeks — is it stabilizing?
- [ ] Check retargeting audience size — at 500+, build and activate Campaign 2
- [ ] If prospecting has 20+ Lead events: plan Ad Set 1B (Broad) test
- [ ] Review ad-level performance: which of Ad 1 vs Ad 2 is delivering lower CPL?
- [ ] Allocate 70% of impressions to winner, add a new Tier 2 creative challenger

### Day 60 Review

- [ ] Compare Meta CPL vs. Google CPL for the same offer
- [ ] Review total lead volume (blended Google + Meta) vs. pre-Meta baseline
- [ ] If pixel has 50+ Lead events: create 1% Lookalike audience and test as new ad set
- [ ] Evaluate men's LHR audience test (separate ad set with men's creative if budget allows)
- [ ] Review retargeting audience frequency — if above 5.0, audience is saturating (consider pausing or refreshing creative)

---

## LEARNING PHASE RULES

**Editing freeze:** Once campaigns are activated, do NOT make any changes to active ad sets for the first 7 days minimum. Any edit (budget change, audience change, adding or pausing an ad) resets Meta's learning clock.

**One change at a time:** After the freeze period, make one change per ad set per week maximum. Document every change with date and reason.

**Changes that always reset learning:**
- Changing audience targeting
- Changing budget by more than 20%
- Adding or removing ads within an ad set
- Changing bid strategy or optimization event

**Changes that do NOT reset learning:**
- Editing ad copy or creative (adds a new ad, old ad continues)
- Pausing an ad at the ad level (not ad set level)
- Adding a new ad to a healthy ad set (does not reset if ad set has been out of learning)

**CPL during learning phase:** Do not evaluate CPA or CPL in the first 5 weeks. Expected learning exit at $75/day with ~$68 target CPL: approximately 34-40 days. CPL during learning will be volatile and unreliable.

---

## INSTANT FORM COPY

Two forms — one for prospecting ads, one for retargeting. Each section below is copy-paste ready for the Meta Forms Library.

### How Instant Forms Work With This Setup

**Instant Forms vs. Landing Page — choose per ad:**

| Option | How It Works | Use When |
|---|---|---|
| Landing page (current setup) | Ad clicks → `go.fabestheticsny.com/laser-hair-removal-mahopac-offer/` → GHL form | Pixel is confirmed; higher-intent traffic preferred; landing page is the source of truth |
| Instant Form | Form opens inside Facebook/Instagram — no redirect | Testing Meta lead volume against landing page CPL; or as a secondary option on the same campaign |

**Attribution note:** Instant Form submissions fire a `Lead` event directly from Meta (separate from the pixel Lead event on the landing page). Meta Ads Manager will count both, but GHL will only receive leads submitted through the landing page form. Instant Form leads must be downloaded from Meta's leads center or connected via Zapier/webhook to GHL. Confirm this integration is set up before running instant form ads at volume.

**When to use instant forms:** Run them as a separate ad pointing to the form (not the landing page) on the same ad set. Compare CPL between landing page ads and instant form ads after 2 weeks. Keep the lower CPL winner.

**CTA button change:** When an ad uses an Instant Form, change the CTA button from "Book Now" to "Get Quote" — this better matches the form action and avoids the disconnect of clicking "Book Now" and landing inside a form instead of a booking page.

---

### FORM 1: Prospecting — Save 15% on Laser Hair Removal

**Used with:** Ad 1 (problem-first static), Ad 2 (social proof carousel), Ad 3 (Becky video)
**Form name in Meta:** `FAB_LHR_15off_Prospecting_Apr2026`
**Form type:** Higher Intent

> Choose **Higher Intent** (not More Volume). Higher Intent adds a review/confirmation step before final submission. This reduces volume by ~15-20% but significantly improves lead quality — exactly what Becky needs given the history with low-intent leads.

---

#### Intro Card

**Headline:** Save 15% on Laser Hair Removal
*(30 characters — max 60)*

**Description:**
```
Book 4 or more laser sessions at FaBesthetics and save 15%.

Becky Pfeifer, BSN will guide you through a personalized treatment plan. Every client is treated as a VIP — always all about you.

Takes less than 60 seconds to request your spot.
```

**Image:** Use the same creative image as the ad this form is attached to.

---

#### Questions

Meta will pre-fill the following from the user's profile. Keep all three — phone and email are required for Becky's follow-up.

| # | Field | Type | Notes |
|---|---|---|---|
| 1 | Full Name | Pre-filled | Required |
| 2 | Phone Number | Pre-filled | Required — Becky's primary follow-up channel |
| 3 | Email | Pre-filled | Required — backup contact + GHL entry |

**Custom Question 4:**

```
Question: Which area are you looking to treat?
Type: Multiple choice — single select
Options:
  - Full Legs
  - Underarms
  - Bikini / Brazilian
  - Face or Upper Lip
  - Multiple areas / Not sure yet
```

*Why this question:* Lets Becky open the follow-up call with a personalized line ("I saw you're interested in Brazilian laser — great choice, let me tell you what to expect") rather than a cold opener. Also helps identify which services drive Meta leads vs. Google leads.*

**Custom Question 5:**

```
Question: When are you looking to get started?
Type: Multiple choice — single select
Options:
  - As soon as possible
  - Within the next month
  - In the next 2–3 months
  - Just exploring for now
```

*Why this question:* Flags urgency for Becky's follow-up prioritization. Anyone who picks "as soon as possible" should receive a callback within the hour.*

---

#### Privacy Policy

**Link text:** FaBesthetics Privacy Policy
**URL:** `https://fabestheticsny.com` *(update to specific /privacy-policy page if one exists)*

---

#### Thank You Screen

**Headline:** You're All Set — We'll Be in Touch Soon
*(38 characters — max 60)*

**Description:**
```
Becky Pfeifer, BSN will personally reach out to discuss your treatment options and confirm your 15% savings.

Most clients hear back the same business day. We look forward to meeting you.
```

**Button 1 label:** Visit Our Website
**Button 1 URL:** `https://fabestheticsny.com`

**Button 2 label:** Call Us Now *(optional — use CallRail tracking number if available)*
**Button 2 URL:** `tel:+1XXXXXXXXXX` *(replace with Becky's CallRail number)*

---

### FORM 2: Retargeting — Your 15% Off Is Still Available

**Used with:** Ad 4 (retargeting static reminder)
**Form name in Meta:** `FAB_LHR_15off_Retargeting_Apr2026`
**Form type:** More Volume

> Choose **More Volume** for retargeting. This audience already knows FaBesthetics — they visited the site or engaged with the page. Remove friction. Fewer steps = more completions.

---

#### Intro Card

**Headline:** Still Thinking About Laser?
*(28 characters — max 60)*

**Description:**
```
Your 15% savings is still on the table.

Book 4 or more sessions at FaBesthetics and lock in your discount. Becky Pfeifer, BSN is ready to answer all your questions — no commitment required to start.
```

**Image:** Same as Ad 4 retargeting creative.

---

#### Questions

| # | Field | Type | Notes |
|---|---|---|---|
| 1 | Full Name | Pre-filled | Required |
| 2 | Phone Number | Pre-filled | Required |
| 3 | Email | Pre-filled | Required |

**Custom Question 4 (single qualifying question — keep retargeting form short):**

```
Question: What's been on your mind about getting started?
Type: Multiple choice — single select
Options:
  - Wondering if it'll work for my skin / hair
  - Thinking through the cost
  - Just waiting for the right time
  - Nothing — I'm ready now
```

*Why this question:* Gives Becky a natural follow-up opener ("I saw you were wondering about results for your skin type — here's what I'd say...") and surfaces the objection to address on the call. Leads who select "Nothing — I'm ready now" are the hottest — call them first.*

---

#### Privacy Policy

**Link text:** FaBesthetics Privacy Policy
**URL:** `https://fabestheticsny.com`

---

#### Thank You Screen

**Headline:** We'll Be in Touch Today
*(23 characters — max 60)*

**Description:**
```
Becky will personally reach out to answer your questions and lock in your 15% savings.

You'll hear back the same business day. Looking forward to connecting with you.
```

**Button label:** See Our Services
**Button URL:** `https://fabestheticsny.com`

---

### Instant Form — Ad Copy Adjustments

When running an ad with an Instant Form instead of the landing page URL, make two changes to the ad copy:

**Change 1 — CTA button:** Switch from "Book Now" → **"Get Quote"**
(Matches the form action better. "Book Now" implies they'll land on a booking page — an instant form is a quote request, not a booking.)

**Change 2 — Last line of primary text:** Replace the URL-directing closing line with a form-directing one.

| Ad | Original closing line | Instant Form version |
|---|---|---|
| Ad 1 (problem-first) | "Save 15% when you book 4 or more sessions." | "Request your 15% savings below — takes less than 60 seconds." |
| Ad 2 (carousel Card 3) | "Claim your savings at fabestheticsny.com" | "Fill out the form below to claim your 15% savings." |
| Ad 3 (Becky video end card) | "Save 15% — Book 4+ Sessions" + CTA | "Request your consultation below — I'll reach out personally." |
| Ad 4 (retargeting) | "Becky Pfeifer, BSN is ready when you are." | "Request your spot below — 60 seconds to claim your savings." |

All other primary text, headlines, and descriptions remain unchanged.

---

### Lead Delivery — Instant Forms to GHL

Instant Form submissions do not automatically appear in GHL. Set up one of these integrations before running instant form ads at volume:

**Option A (Recommended): Zapier**
- Trigger: New Meta Lead Form submission
- Action: Create contact in GHL
- Map fields: Name → Name, Phone → Phone, Email → Email, Q4 answer → Custom field "Treatment Area", Q5 answer → Custom field "Timing / Urgency"
- Notify: Trigger the same lead notification email Becky already receives for GHL form fills

**Option B: Meta native download**
- Go to Meta Ads Manager → Forms Library → Download leads (CSV)
- Manual process — not recommended for a high-response-time business like Becky's
- Only use as a backup if Zapier is not set up yet

**Owner for integration setup:** Bishal or Avi — confirm which system handles GHL integrations for this client.

---

## NOTES FOR TEAM

1. **Lead quality is the top priority.** The creative tone must stay premium. If any ad copy feels like a "deal" rather than a "package savings," revise it before launch. Becky's experience with the $99 special was exactly what we are protecting against.

2. **Becky's BSN credential is the strongest trust signal available.** Every ad should reference it. It distinguishes FaBesthetics from walk-in laser chains and positions Becky as a clinical expert, not just a technician.

3. **Small market — audience size is a real constraint.** Mahopac + 25 miles is not Westchester County. Watch frequency closely in the first two weeks. Widen the radius before pulling other levers.

4. **Meta and Google will cross-attribute.** Some Meta leads will click through from the ad and then Google FaBesthetics and convert via Google. The Google campaign will take credit for those. This is fine — look at total lead volume, not Meta-only.

5. **Becky's follow-up speed matters more on Meta than on Google.** Google leads are actively searching — they want to book now. Meta leads saw an ad while scrolling — they are interested but not urgent. They will go cold fast if Becky doesn't follow up within the hour. This is not an ad problem; it's a sales process issue worth flagging to Dan.

6. **Do not launch the retargeting campaign on Day 1.** The retargeting audience does not exist yet. Building the campaign is fine; activating it before the audience reaches 500 people burns budget on effectively no one.
