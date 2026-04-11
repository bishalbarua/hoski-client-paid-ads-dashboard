# GDM Campaign Strategy — Three-Lever Architecture
**Prepared:** April 11, 2026
**Goal:** $54K/month → $200K/month (3.7x growth required)
**Budget:** $25K/month (step-up from current $10.8K)

---

## The Core Problem With the Previous Strategy

The previous strategy treated GDM as a single funnel. It wasn't wrong — but it was incomplete. GDM has three distinct revenue levers that require separate campaign architectures, separate conversion events, separate creative briefs, and separate CPL targets. Running them as one undifferentiated campaign plan means the algorithm is optimizing for the wrong signal on at least two of three levers at any given time.

---

## Data Foundation

### Province Performance (GA4, Jan 1–Apr 11, 2026)

Aggregated from city-level GA4 data. This is the answer to "what data backs province-wide targeting?":

| Province | Est. Revenue (3.5 mo.) | Active Users | CVR Signal |
|---|---|---|---|
| Ontario | ~$25,000+ | 14,000+ | Highest absolute revenue. Toronto $7,875, Ottawa $6,630, Richmond Hill $4,883. |
| Quebec | ~$13,000+ | 12,000+ | Montreal high engagement — much of it is in-store intent, not e-commerce. |
| BC | ~$8,000+ | 3,000+ | Best revenue-to-user ratio. Vancouver $6,910 with 1,196 users = highest CVR in Canada. |
| Alberta | ~$4,500 | 2,600+ | Consistent. Calgary $3,620. |
| Atlantic (NS + NB) | ~$5,700 | 1,500+ | Outperforming relative to size. Halifax $3,402. Worth testing. |
| Manitoba, SK, PEI | Low | 1,500+ | Traffic present, revenue near zero. Do not over-invest. |

**Conclusion:** The case for province-wide targeting is not "some revenue comes from everywhere." It's that Ontario + BC have demonstrated purchase conversion at meaningful scale, and Atlantic provinces are overperforming relative to their traffic size. Blanket Canada-wide equal budget allocation ignores this entirely.

### GHL Pipeline (March 2026)

**Appointment funnel leads:** 13
**Attended:** 4
**Purchased:** 2 (Renaud Fréchette-Brien, Sylvain Proulx)

| Metric | Actual | Target | Status |
|---|---|---|---|
| Show rate | 31% | 65% | Critical problem |
| Close rate (from attendees) | 50% | 40-60% | Healthy |
| CPL | ~$398 | $365 | Slightly above target |
| Cost per acquired client | ~$2,561 | ~$1,095 | High — show rate is why |

**Average purchase value (30 offline transactions in GHL):** $2,135
**Average engagement ring consultation value (pipeline data):** $4,000–$6,000

---

## The Three Levers

---

### Lever 1: Province-Wide E-Commerce

**Purpose:** Drive online Shopify purchases across Canada with budget tiered by demonstrated revenue conversion.

**Who this is for:** Buyers who find GDM online and purchase without a consultation. Gift buyers, repeat customers, self-gifters.

**Geography:** All of Canada. Do not restrict targeting by province — algorithmic campaigns (Advantage+ and PMax) need the full audience pool to find buyers. Restricting to Ontario + Quebec reduces signal and cuts off the algorithm from discovering high-CVR markets like BC.

The province tiers below are a monitoring and optimization framework, not a campaign build instruction:
- **Watch Ontario + Quebec first** — highest revenue, any performance drop here is a problem
- **Watch BC closely** — highest revenue-to-user ratio, best CVR in the country relative to traffic
- **Monitor Alberta weekly** — solid but smaller, flag if CPA climbs
- **Atlantic (NS + NB): let it run** — outperforming relative to size, don't interfere
- **Manitoba, SK, PEI: watch for waste** — traffic present, revenue near zero; exclude if 30 days of spend with no conversions

**Channels:**
- Meta: Advantage+ Shopping campaign — Canada-wide targeting, monitor province-level breakdown weekly in Meta reporting
- Google: PMax Bestsellers (was at 8.06x ROAS before pause — this is the lead campaign to scale)

**Budget:** $11,000/month — Meta $6,500 / Google PMax $4,500

**Primary conversion event:** Shopify online purchase

**Reporting metric:** MER (total Shopify revenue / total ad spend). Platform ROAS is for intra-campaign use only — which campaign to scale, not whether the business is healthy.

**Active offers:** Free diamond studs with purchase (0.26ct with $2,500+, 0.50ct with $3,500+, 1.00ct with $5,000+), 10% off for new customers

**Creative angles for e-commerce (priority order, competitive-informed):**

| Rank | Angle | Hook | Why It Works |
|---|---|---|---|
| 1 | Manufacturer pricing | "Same quality as Birks. Manufacturer price — no retail markup." | Birks and Peoples cannot say this; Ecksand won't say it (they position premium) |
| 2 | Free studs offer | Tiered free diamond studs with purchase threshold | Unique offer — no competitor is running this |
| 3 | Global + Montreal trust | "Sourced from 12 countries. Made in Montreal." | Trust signal for Ontario and BC buyers purchasing online without visiting the store |

**Province monitoring triggers (check weekly):**

| Province | Expected share of revenue | Action if underperforming for 30+ days |
|---|---|---|
| Ontario | ~35% | Investigate creative relevance, check CPAs |
| Quebec | ~25% | Check FR language targeting is reaching QC |
| BC | ~20% | High CVR market — if spend is low here, check algo allocation |
| Alberta | ~12% | Add geo bid reduction if CPA is 30%+ above target |
| Atlantic | ~8% | Let run — outperforming relative to size |
| Manitoba / SK / PEI | Near zero | Exclude if 30 days spend with zero conversions |

---

### Lever 2: Local Montreal — Appointment Funnel

**Purpose:** Drive in-store visits and virtual consultations for any product category (not ring-specific). In-store revenue was $31K in March (confirmed by client — corrects an earlier internal figure of $65K). This is the lever with the most room to grow.

**Who this is for:** Montreal-area buyers who want to see pieces in person, need guidance, or are buying something substantial enough to want a consultation before committing.

**Geography:** 50km radius from GDM Montreal store (covers Montreal, Laval, Longueuil, South Shore, West Island)

**Landing page:** Needs to be built. Both existing appointment pages (go.globaldiamondmontreal.com/appointment and globaldiamondmontreal.com/pages/appointment-1) are ring-focused — headline is "Looking to propose to that special someone?" Sending bracelet, Mother's Day, or general jewelry traffic to a proposal page kills conversions. Lever 2 needs a general consultation LP: "See our full collection in person" framing, gift-buyer and repeat-customer social proof, same booking form underneath.

**Channels:**
- Google Search: Local high-intent keywords — "jewelry store Montreal," "jeweler Montreal," "diamond bracelet Montreal," "custom ring Montreal"
- Meta: Radius targeting (50km), consultation-focused creative
- LSA: Maintain — "jewelry store near me" queries

**Budget:** $7,500/month — Google Search $4,500 / Meta radius $3,000

**Primary conversion event:** Appointment booked (GHL calendar)

**Reporting metric:** Cost per attended appointment (not cost per booking — booking rate means nothing with 31% show rate)

**CPL math:**
- Average purchase value: $2,135
- Target show rate: 65% / Close rate: 50% / Estimated margin: 70%
- Max CPL: $2,135 × 0.65 × 0.50 × 0.70 = **$487**
- Target CPL: $487 × 0.75 = **$365**

**PRE-LAUNCH GATE — Show Rate Must Be Fixed First**

Current show rate is 31%. The target is 65%. At 31%, every $365 CPL costs $2,561 per acquired client against a $2,135 average sale — we are underwater. Scaling spend before fixing show rate is the single fastest way to make the account look profitable on CPL while losing money on outcomes.

Required before scaling Lever 2 beyond $3,000/month:
1. Faseeh confirms GHL automation fires SMS + email within 60 seconds of form submission
2. Trevor is executing human follow-up within 5 minutes during business hours
3. 3-attempt sequence documented and running over 48 hours
4. Show rate at or above 50% for two consecutive weeks

If show rate stays below 50% after the sequence is confirmed live: the problem is lead quality, not follow-up. Investigate creative angle and form question qualification before spending more.

---

### Lever 3: Engagement Rings — Dedicated Funnel

**Purpose:** Dedicated campaign architecture for custom and bridal. Separate from Lever 2 because the consideration cycle, average value, creative approach, and retargeting window are fundamentally different.

**Who this is for:** People actively researching engagement rings — typically 4-8 weeks before purchasing. High-intent, high-consideration, longest sales cycle in the business.

**Why engagement rings cannot share a campaign with bracelets or Mother's Day:**
- Consideration cycle: 4-8 weeks vs. 1-2 weeks for gifting
- Retargeting window: 60-90 days vs. 30 days for general jewelry
- Average purchase value: $4,000-6,000 vs. $2,135 blended average
- CPL ceiling: $585 vs. $365 — shared campaigns will kill ring bids when the algorithm sees bracelet-level CPAs as "normal"
- Creative angle: Manufacturer/process credibility vs. gift appeal

**Geography:** Montreal metro (in-store) + Canada-wide for virtual consultations

**Landing page:** https://go.globaldiamondmontreal.com/appointment (confirmed live, ring-specific)

**How this lever is differentiated from Lever 2 in execution:**
- Dedicated landing page with ring-specific messaging ("Looking to propose to that special someone?") vs. Lever 2 which needs a general consultation LP
- Separate campaigns with separate bid strategies — $585 CPA target vs. $365 for Lever 2 (cannot share a campaign without the algorithm collapsing to one signal)
- UTM parameters (`utm_campaign=engagement-rings`) auto-tag GHL opportunities as ring consultations — tracked separately from general appointments
- Different keywords, creative, and retargeting window (60-90 days vs. 30 days)
- Canada-wide virtual consult targeting not present in Lever 2

**Channels:**
- Google Search (priority keywords, updated after competitive research):
  - "custom engagement ring montreal" — medium competition, manufacturer angle wins here
  - "engagement ring designer montreal" — same intent cluster, designer framing suits GDM
  - "engagement ring montreal atelier" — very low competition, high intent
  - "diamond engagement ring manufacturer montreal" — bottom-funnel, essentially zero competition
  - "engagement rings montreal" — higher competition (Ecksand, St-Onge, Flamme en Rose all bid here), viable but needs sharp creative to stand out
  - "lab grown engagement rings montreal" — viable but Brilliant Earth dominates nationally; use only if budget allows after priority keywords are covered
- Meta: Couples/relationship interest targeting, radius for local + broader Canada for virtual consult offer
- Retargeting: 60-90 day window (2-3x the default)

**Budget:** $4,000/month — Google $2,000 / Meta $2,000 (scales as funnel data comes in)

**Primary conversion event:** Appointment booked — tagged separately in GHL as "ring consultation"

**Reporting metric:** Cost per ring consultation + cost per ring closed (separate from general appointment CPL)

**CPL math:**
- Estimated average ring sale: $5,000
- Target show rate: 60% / Close rate: 40% / Estimated margin: 65%
- Max CPL: $5,000 × 0.60 × 0.40 × 0.65 = **$780**
- Target CPL: $780 × 0.75 = **$585**

At $585 CPL, a ring consultation costs $585. If 60% show and 40% close, cost per ring sold = $585 / (0.60 × 0.40) = $2,438. On a $5,000 average sale at 65% margin ($3,250 gross), that's a 1.33:1 gross margin to CAC ratio — profitable on first order.

**Creative angles (priority order, updated after competitive research):**

Note: "Made in Montreal" alone is not a differentiator. Six competitors claim the same thing (Ecksand, St-Onge, Flamme en Rose, Maidor, MYEL, Deux Lions). The angle that is genuinely unique is the combination of global sourcing AND Montreal manufacturing. Ecksand and St-Onge specifically position on local/recycled/Canadian-only sourcing — GDM's 12-country network is the gap they cannot close.

| Rank | Angle | Hook | Why It Wins vs. Competition |
|---|---|---|---|
| 1 | Global sourcing + manufacturer | "Diamonds from 12 countries. Set in Montreal since 1982." | No competitor can claim both — Ecksand and St-Onge source locally only |
| 2 | Price transparency | "No retail markup. You deal directly with the manufacturer." | Differentiates vs. Ecksand (premium, opaque) and chains (impersonal) |
| 3 | Heritage | "40+ years. Thousands of rings. Montreal's most experienced manufacturer." | Oldest in the competitive set — St-Onge (1977) is close, all others are newer |
| 4 | Process demystification | "Here's exactly what happens at your first appointment." | Reduces fear of custom process — relevant to all local competitors |
| 5 | Lab-grown as choice | "Natural or lab-grown — your call. Same quality, manufacturer pricing." | Do NOT position as the ethical lab-grown brand — Brilliant Earth owns that with 20+ years of brand investment |

---

## Budget Summary ($25K/month)

| Lever | Monthly Budget | % | Google | Meta |
|---|---|---|---|---|
| Lever 1: Province-wide e-commerce | $11,000 | 44% | $4,500 (PMax) | $6,500 (Advantage+) |
| Lever 2: Local appointment funnel | $7,500 | 30% | $4,500 (Search) | $3,000 (radius) |
| Lever 3: Engagement rings | $4,000 | 16% | $2,000 (Search) | $2,000 |
| Mother's Day overlay (Apr–May 11) | $2,500 | 10% | $1,350 (Search EN+FR) | $1,150 |
| **Total** | **$25,000** | 100% | **$12,350** | **$12,650** |

Mother's Day budget reallocates to Lever 1 and Lever 3 after May 11.

---

## Sequencing

### Week 1 (Apr 11–17): Activate the Foundation
- Enable Mother's Day campaigns (built, in paused state — activate now)
- Reactivate PMax Bestsellers at $25/day — scale 30% every 5 days if ROAS stays above 3x
- Faseeh: audit GHL automation — confirm 60-second SMS/email trigger on form submission
- Confirm CallRail is live — currently blocking all call attribution to Google

### Week 2 (Apr 17–24): Launch Lever 2 + Ring LP
- Launch Google Search local appointment campaigns (Lever 2)
- Launch Meta local radius campaign for appointments (Lever 2)
- Sabby: build engagement ring landing page (unblock stalled ClickUp task) — required before Lever 3 is a true separate funnel
- Faseeh: configure UTM-to-GHL auto-tagging so ring consultations are tracked separately now, even before the new LP is live
- Document baseline show rate, CPL, and call duration from CallRail
- Run search terms audit on reactivated PMax campaigns — negate zero-converting terms

### Weeks 3–4 (Apr 25–May 10): Scale and Launch Lever 3
- If show rate exceeds 50%: increase Lever 2 budget by 30%
- Launch Lever 3 engagement ring campaigns (Google + Meta)
- Mother's Day final sprint: EN campaign $75/day, FR campaign $50/day
- First province-level cut: assess Ontario vs. BC CVR in Lever 1

### Post May 11: Full Three-Lever Architecture Live
- Reallocate Mother's Day budget to Lever 1 (scale PMax) and Lever 3 (scale ring funnel)
- Confirm Zapier offline conversion import is attributing in-store closes back to campaigns
- 30-day milestone check: tracking toward $130-150K with $25K spend?

---

## Infrastructure Gaps (Fix Before Scaling)

| Gap | Why It Matters | Owner | Priority |
|---|---|---|---|
| General consultation LP missing | Lever 2 has no landing page. Both existing appointment pages are ring-focused ("Looking to propose?") — wrong message for bracelet/gift traffic. Needs new LP built. | Sabby (Web Dev) | P0 — Week 2 |
| CallRail not live | All call conversions missing from Google — bidding on incomplete signals | Faseeh + Bishal | P0 — this week |
| Show rate at 31% | Scaling Lever 2 without fixing this is losing money on every appointment | Faseeh (GHL) + Trevor (SDR) | P0 — this week |
| Offline Zapier conversion lag | In-store revenue not feeding back — algorithms optimizing for online-only signals | Faseeh | P1 — Week 2 |
| Meta account ID discrepancy | act_101893403864525 vs. 1229672268157520 — must confirm before scaling Meta spend | Bishal | P1 — this week |
| Zero-converting keywords | "buy diamond rings online" ($158), "diamond montreal" ($137), "gold necklaces" ($111), "gemstone rings" ($97) — all $0 conv value | Bishal | P1 — this week |

---

## How We Know This Is Working

**Lever 1 (E-commerce):** MER improving week-over-week. PMax Bestsellers ROAS holding above 3x after scale.

**Lever 2 (Appointments):** Show rate reaches 50%, then 65%. Cost per attended appointment under $500. GHL pipeline stages moving forward with fewer "closed due to inactivity."

**Lever 3 (Rings):** Ring consultations tracked separately in GHL. Cost per ring consultation under $600. At least 2 ring consultations per week from ads within 30 days of launch.

**Overall:** At $25K spend with $200K target, we need a blended MER of 8x. With in-store sales not fully attributable through ads, we should see Shopify revenue growing (Lever 1 measurable) while GHL pipeline grows (Lever 2 and 3 measurable). MER will be understated until offline conversion import is confirmed healthy — flag this to Antonio.

---

## Competitive Landscape (April 2026)

Research conducted across 8 Google keyword searches, 10+ competitor website audits, and Meta intelligence.

### Primary Threat: Ecksand

The single most dangerous competitor. Montreal manufacturer, similar price point, similar consultation model, similar ethical positioning. Appears in 4 of 8 keyword searches researched.

**What Ecksand claims:** "Fully vertical Montreal atelier," handcrafted, recycled gold, ethical diamonds, boutiques in Montreal and Toronto.

**How GDM beats Ecksand specifically:**
- Older heritage: GDM 1982, Ecksand is significantly newer
- Global sourcing: GDM sources from 12 countries / 4 continents. Ecksand positions on Canadian/recycled-only sourcing — they cannot claim a global network.
- Scale: 35,000+ craftsmanship hours suggests higher volume and more pricing flexibility
- The ad that beats Ecksand: "Sourcing diamonds from 12 countries. Making them in Montreal since 1982." Ecksand cannot match either claim.

### Competitive Map

| Competitor | Type | Strength | GDM Advantage |
|---|---|---|---|
| Ecksand | Montreal manufacturer | Same model, ethical positioning | Heritage + global sourcing — Ecksand cannot say both |
| St-Onge Jeweller | Montreal manufacturer (since 1977) | "100% made in Quebec" | Global sourcing network; GDM has more scale and wider diamond selection |
| Flamme en Rose | Montreal workshop, women-owned | Eco/ethical narrative | GDM doesn't need the ethics story — price transparency + manufacturer angle is stronger |
| Birks | National luxury chain | 145 years of Canadian heritage, luxury positioning | Manufacturer pricing: "Same quality. No retail markup." Birks cannot say this. |
| Peoples Jewellers | National mass market chain | 150+ locations, volume | Expertise and personalization — Peoples is a chain, GDM is a manufacturer with consultation |
| Brilliant Earth | Lab-grown specialist | Owns ethical/sustainable narrative, 20+ years brand investment | Do not compete here. Lab-grown is a choice GDM offers, not the primary story. |
| Michael Hill | National mid-market chain | Physical presence, promotions | Manufacturer credibility — GDM makes it, Michael Hill just sells it |
| Proud Diamond | Montreal lab-grown specialist | Lab-grown focused, local | Global sourcing + custom design — Proud Diamond is narrow (lab-grown only) |

### What "Made in Montreal" Is Worth

Six Montreal competitors claim manufacturing status: Ecksand, St-Onge, Flamme en Rose, Maidor, MYEL Design, Deux Lions. This claim is table stakes in the local market. It must be combined with a second differentiator to mean anything:

- GDM's combination: **manufacturer + global sourcing network (12 countries)**. This is genuinely unique — no Montreal competitor can match it.
- Secondary combination: **manufacturer + heritage (oldest in the competitive set) + price transparency**

### Keyword Competitive Landscape

| Keyword | Who Dominates | GDM Play |
|---|---|---|
| "jewelry store montreal" | Birks, boutiques | Skip — wrong intent, outgunned on brand |
| "engagement rings montreal" | Ecksand, St-Onge, Flamme en Rose | Viable, but needs global sourcing + manufacturer creative to stand out |
| "custom engagement ring montreal" | Ex Aurum, St-Onge, Ecksand | Best bet — medium competition, GDM's manufacturer angle wins here |
| "lab grown engagement rings montreal" | Proud Diamond, Flamme en Rose | Viable, but Brilliant Earth dominates Canada-wide — secondary priority |
| "diamond bracelet canada" | Michael Hill, Glamira, Diamonds Factory, Tiffany | Tough — free studs offer + manufacturer pricing is the differentiation |
| "mothers day jewelry canada" | Pandora, Brilliant Earth, David Yurman | Skip — outspent at this budget |
| "mothers day bracelets montreal" | Almost no one | Own this |
| "personalized jewelry for mom" | Almost no one | Own this — confirmed low competition in keyword research |
| "custom engagement ring montreal atelier" | No one | Own this |
| "buy engagement ring from manufacturer" | No one | Own this — bottom-funnel, high intent |

### Positioning Statement for Creative Briefs

GDM sits in the gap between mass-market chains (Michael Hill, Peoples — accessible but impersonal) and ultra-premium boutiques (Birks, Ecksand — beautiful but expensive). GDM is the manufacturer that gives buyers access to premium diamonds at manufacturer pricing, backed by a global sourcing network that local boutiques don't have and 40+ years of Montreal expertise.

**Target buyer:** Knows enough to know retail markups exist. Wants quality without being extracted from. Responds to transparency, expertise, and authenticity — not luxury theater.
