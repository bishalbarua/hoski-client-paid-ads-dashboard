---
name: facebook-ads-performance-analyzer
description: Analyze Facebook/Meta Ads campaign performance and deliver a prioritized, actionable improvement roadmap. Triggers when a user wants to audit Facebook ad results, diagnose underperformance, optimize spend, or scale winning campaigns. Accepts campaign-level exports, pasted data tables, or manually typed metrics. Outputs a tiered action plan with confidence scores and implementation steps.
---

# Facebook Ads Performance Analyzer

Diagnose what's working and what's broken in a Facebook/Meta Ads account, then deliver an implementation-ready action plan ranked by impact. This skill goes beyond surface-level metrics to identify structural, creative, audience, and bidding issues — the four root causes behind 90% of underperforming Meta accounts.

## Core Philosophy

1. **Creative is the variable that matters most** — On Meta, audience targeting has been commoditized by broad targeting + ML. Creative is now the primary lever. Analysis must prioritize creative health above all else.
2. **Context before diagnosis** — A 3% CTR is great for cold traffic and terrible for warm retargeting. Never benchmark without knowing the funnel stage.
3. **Frequency kills before CPMs do** — Ad fatigue is the silent account killer. Flag it early.
4. **Structure problems cause performance problems** — Campaign objective mismatches, broad vs. narrow audiences, and broken pixel events silently destroy ROAS.
5. **Confidence-weighted recommendations only** — Low-data accounts get conservative, reversible recommendations. High-data accounts get aggressive optimization.

---

## Critical Context Gathering

### Required Context (Ask if not provided)

**1. Business Model & Conversion Goal**
What is the account selling, and what action counts as a conversion? (e.g., e-commerce purchase, lead form submit, phone call, app install). This determines which metrics matter and what good looks like.
*Example:* "Direct-to-consumer supplements" + "Purchase" is very different from "B2B SaaS" + "Demo booked."

**2. Funnel Stage Mix**
Are the campaigns being analyzed TOF (cold traffic), MOF (warm/retargeting), or BOF (hot/purchase-intent)? Or all three? Benchmarks, creative strategy, and bid targets differ entirely by stage.
*Example:* A TOF campaign at $60 CPA might be fine; BOF at $60 CPA for the same product might be failing.

**3. Target CPA or ROAS**
What does a profitable conversion cost, or what ROAS keeps the business healthy? Without this, optimization direction is a guess.

### Recommended Context

**4. Monthly Budget & Account Spend**
Helps assess whether recommendations are data-backed (≥$5K/mo = sufficient signal) or tentative (< $1K/mo = limited data, test conservatively).

**5. Pixel / Conversion Event Status**
Is the Meta pixel firing correctly? Are conversion events verified in Events Manager? Broken tracking is the #1 silent killer — must be ruled out before any bidding or budget advice.

**6. Creative Types in Use**
Are they running static images, video, carousel, or collection ads? Single creative per ad set or multiple? This determines whether creative fatigue or creative diversity is the issue.

### Optional Context

**7. Competitor & Industry**
Used to contextualize CPM benchmarks. Apparel CPMs are very different from financial services CPMs.

**8. Audience Strategy**
Broad (no detailed targeting), interest-based, lookalike, or retargeting lists? Size of each audience? Helps identify audience saturation vs. creative fatigue.

---

## Input Format

Acceptable formats (flexible — use whatever you have):

**Option A — Campaign Export CSV/Table**
Paste or upload with columns: Campaign, Ad Set, Ad, Spend, Impressions, Clicks, CTR, CPC, Conversions, CPA, ROAS, Frequency, Reach. Date range must be stated.

**Option B — Ad Set Level Summary**
Paste a table of ad set names + key metrics. Minimum: Spend, Conversions or Leads, CPA or CPL, Frequency.

**Option C — Manually Described Metrics**
"We're spending $8K/mo, getting 40 purchases at $200 CPA, targeting lookalike audiences, running 2 creatives per ad set, frequency is 4.2 on our main campaign." This is enough to begin.

**Option D — Screenshot**
Upload a screenshot of Ads Manager. Key metrics will be read directly.

**Minimum Viable Input:** Total spend, total conversions, CPA or ROAS, and at least 1 campaign's structure described.

---

## Analysis Framework

### Phase 1: Account Health Triage

Run this before any deeper analysis. Identify anything that must be fixed before optimization matters.

| Check | Healthy Signal | Warning | Critical |
|---|---|---|---|
| Pixel firing | Events verified in Events Manager | Unverified events | No pixel / 0 conversions tracked |
| Attribution window | 7-day click selected | 1-day click only | No attribution set |
| Campaign objective | Matches conversion goal | Slight mismatch | Wrong objective (e.g., Traffic for purchases) |
| Conversion volume | ≥50 conversions/ad set/week | 20-49/week | <20/week (insufficient for ML) |
| Learning phase | Out of learning | In learning (< 7 days) | Learning Limited |

**If any Critical flag exists → fix before optimizing bids or budgets. State this clearly.**

---

### Phase 2: Funnel Stage Benchmarking

Apply the correct benchmarks per funnel stage. Never mix-and-match.

**TOF (Cold Traffic) Benchmarks:**

| Metric | Strong | Average | Weak |
|---|---|---|---|
| CTR (Link) | > 2.0% | 1.0–2.0% | < 1.0% |
| CPM | < $15 | $15–$30 | > $30 |
| CPC | < $1.00 | $1.00–$2.50 | > $2.50 |
| Frequency | 1.5–3.0 | 3.0–5.0 | > 5.0 |
| Hook Rate (3s video view / impressions) | > 30% | 20–30% | < 20% |

**MOF (Warm Retargeting) Benchmarks:**

| Metric | Strong | Average | Weak |
|---|---|---|---|
| CTR (Link) | > 3.0% | 1.5–3.0% | < 1.5% |
| Frequency | 3–7 | 7–12 | > 12 |
| CPA | < 1.5× TOF CPA | 1.5–2.5× TOF | > 2.5× TOF |
| ROAS | > 3× | 2–3× | < 2× |

**BOF (Cart Abandonment / High-Intent Retargeting) Benchmarks:**

| Metric | Strong | Average | Weak |
|---|---|---|---|
| ROAS | > 5× | 3–5× | < 3× |
| Frequency | 5–15 | 15–25 | > 25 |
| CPA | < 0.8× target | 0.8–1.2× target | > 1.2× target |

---

### Phase 3: Creative Health Assessment

Creative is the primary lever. Assess each of these:

**3a. Creative Fatigue Detection**

| Frequency | CTR Trend | Diagnosis | Action |
|---|---|---|---|
| < 3.0 | Stable / rising | Healthy | Monitor |
| 3.0–5.0 | Flat | Early fatigue | Introduce 1–2 new creatives |
| > 5.0 | Declining | Fatigued | Refresh immediately, rotate out |
| > 7.0 | Declining sharply | Burned | Pause ad set, full creative refresh |

**3b. Creative Diversity Score**
Count unique creative concepts (not just ad copies) per ad set:
- 1 concept → single point of failure. High risk.
- 2–3 concepts → moderate. Algorithm can test.
- 4+ concepts → healthy. Creative testing at scale.

**3c. Creative Format Mix**
Flag if account is running only one format. Meta's algorithm rewards format diversity.

| Situation | Recommendation |
|---|---|
| Only static images | Test UGC video or short-form video |
| Only video | Test static testimonial cards |
| Only carousel | Test single image with strong hook |
| No UGC at all | High priority — UGC consistently outperforms polished creative for most DTC brands |

---

### Phase 4: Audience & Targeting Assessment

**4a. Audience Saturation Check**

| Audience Size | Campaign Spend/Day | Risk |
|---|---|---|
| < 200K | > $200/day | Saturated — expand or broaden |
| 200K–1M | > $500/day | Monitor frequency weekly |
| 1M–5M | > $2K/day | Monitor frequency |
| > 5M (Broad) | Any | Low saturation risk |

**4b. Audience Overlap Risk**
If running 3+ ad sets targeting similar interests → overlap is likely. Consolidate using Advantage+ audience or broader targeting.

**4c. Retargeting Audience Freshness**
- Website visitors from 180+ days ago are cold again. Tighten to 30 or 60-day windows.
- Engaged audiences older than 90 days should be refreshed or suppressed.

---

### Phase 5: Budget & Bid Strategy Assessment

| Bid Strategy | Best For | Risk If Misused |
|---|---|---|
| Lowest Cost (no cap) | Scaling, learning phase, new campaigns | Can overpay in unconstrained accounts |
| Cost Cap | Mature campaigns with proven CPA | Can stall delivery if cap is too tight |
| Bid Cap | Experienced buyers only | Easy to kill delivery accidentally |
| ROAS Cap | E-commerce with strong conversion history | Requires 50+ conversions/week minimum |
| Advantage+ Shopping | E-commerce scaling | Reduce manual control — only if account has conversion history |

**Budget Consolidation Signal:**
If more than 5 ad sets are spending < 20% of budget each → consolidate. Fragmented budgets prevent ML optimization.

---

### Phase 6: Conversion & Pixel Verification

Before trusting any CPA or ROAS number, verify:

1. Are standard events (Purchase, Lead, Add to Cart) firing on the correct pages?
2. Is there deduplication set up for server-side (CAPI) + pixel? (Duplicate events inflate conversions)
3. Is the attribution window set consistently across all campaigns?
4. Are Value optimization events passing revenue values (for ROAS campaigns)?

**If CAPI is not implemented:** Flag as high priority. iOS 14+ has significantly degraded browser-only tracking. Estimate 20–40% conversion underreporting is likely.

---

## Output Format

Deliver in this exact structure:

---

### 📊 Facebook Ads Performance Analysis — [Account/Brand Name]
**Date Range Analyzed:** [X]
**Total Spend:** $X | **Conversions:** X | **CPA:** $X | **ROAS:** X

---

### 🚨 Critical Issues (Fix Before Anything Else)
*Issues that are silently destroying performance right now.*

| Issue | Impact | Fix | Effort |
|---|---|---|---|
| [Issue] | [What it's costing] | [Specific fix] | Low/Med/High |

---

### 🎯 Account Health Score
| Dimension | Status | Score |
|---|---|---|
| Tracking & Pixel | 🟢/🟡/🔴 | /10 |
| Creative Health | 🟢/🟡/🔴 | /10 |
| Audience Strategy | 🟢/🟡/🔴 | /10 |
| Campaign Structure | 🟢/🟡/🔴 | /10 |
| Bid Strategy | 🟢/🟡/🔴 | /10 |
| **Overall** | | **/50** |

---

### 🔥 Top 3 Highest-Impact Opportunities
*Ranked by expected improvement, with confidence scores.*

**#1 — [Opportunity Name]** *(Confidence: 0.XX)*
- **What:** [Specific issue identified]
- **Why it matters:** [Impact on performance]
- **Action:** [Exact step to take]
- **Expected outcome:** [Specific, realistic improvement]

**#2 — [Opportunity Name]** *(Confidence: 0.XX)*
*(same structure)*

**#3 — [Opportunity Name]** *(Confidence: 0.XX)*
*(same structure)*

---

### ✅ What's Working (Protect These)
- [Winning element]: [Why it's working, don't touch]
- [Winning element]: [Why it's working, don't touch]

---

### 📋 Full Priority Action List

| Priority | Action | Effort | Expected Impact | Confidence |
|---|---|---|---|---|
| 1 | [Specific action] | Low/Med/High | [Impact] | 0.XX |
| 2 | ... | | | |
| 3 | ... | | | |

---

### ⚠️ Data Quality Notes
*Limitations that affect recommendation confidence.*
- [Note any data gaps, short date ranges, low conversion volume, etc.]

---

## Guardrails

❌ **NEVER** recommend increasing budget on campaigns in Learning Limited status — fix the learning limitation first.

❌ **NEVER** recommend Cost Cap or ROAS Cap bid strategies on ad sets with fewer than 50 conversions/week — the ML doesn't have enough signal and delivery will stall.

❌ **NEVER** recommend pausing a retargeting campaign without first checking if it's the only BOF campaign — removing it could eliminate bottom-of-funnel recovery entirely.

❌ **NEVER** give a confident ROAS recommendation if pixel/conversion tracking hasn't been verified — the number might be meaningless.

❌ **NEVER** recommend audience exclusions without understanding what audiences are already in use — exclusions on overlapping ad sets can accidentally kill reach.

✅ **ALWAYS** flag if conversion volume is below the 50/week threshold for ML-based bidding — and recommend switching to manual or Lowest Cost until volume is reached.

✅ **ALWAYS** state confidence score with every recommendation — especially when data is limited.

✅ **ALWAYS** check creative frequency before diagnosing a CPM or CPA problem — fatigue is often the root cause.

✅ **ALWAYS** recommend CAPI implementation if it's not in place — iOS 14+ data loss is structural, not fixable with campaign changes alone.

✅ **ALWAYS** end analysis with a "What's Working" section — high-performing campaigns and ad sets must be identified and protected before any changes.

---

## Edge Cases

### Edge Case 1: Brand New Account (< $1,000 Spend)
Insufficient data for most ML-based recommendations. Focus on:
- Tracking verification (pixel, CAPI, standard events)
- Campaign objective correctness
- Creative diversity (minimum 3 concepts)
- Audience size appropriateness
Flag all recommendations as "Monitor, not yet actionable" until $3K+ spend is reached.

### Edge Case 2: Account With Zero Conversions Tracked
Do not analyze CPA or ROAS — these numbers are unreliable. Instead:
1. Diagnose pixel installation
2. Verify standard events are firing
3. Check attribution window settings
4. Recommend switching to a top-of-funnel objective temporarily to generate trackable engagement while tracking is fixed

### Edge Case 3: High Spend, Low Conversion Volume (e.g., $10K/mo, 15 purchases)
The account is spending above its conversion signal. Recommendations:
- Consolidate to fewer campaigns to concentrate signal
- Consider optimizing for an earlier funnel event (Add to Cart or Initiate Checkout) to give the ML more signal
- Do not recommend advanced bid strategies — insufficient data

### Edge Case 4: Scaling Account That Was Performing and Suddenly Dropped
Prioritize these checks in order:
1. Frequency spike (creative fatigue)
2. Audience exhaustion (reach declining despite spend)
3. Platform-level CPM increase (external, seasonal)
4. Tracking/pixel change (conversion drop may be tracking loss, not real drop)
5. Competitor activity / market shift

### Edge Case 5: Lead Generation (Not E-Commerce)
Adjust all ROAS benchmarks — ROAS doesn't apply. Use CPL (Cost Per Lead) and Lead Quality Score instead. Ask user for their target CPL and lead close rate to derive an effective CPA.

---

## Quality Assurance

Before delivering analysis:
- [ ] Critical tracking issues flagged first, before any optimization recommendations
- [ ] All benchmarks applied to the correct funnel stage (not mixed)
- [ ] Confidence scores assigned to every recommendation
- [ ] Creative frequency checked for every ad set mentioned
- [ ] At least one "What's Working" item identified and protected
- [ ] Data quality limitations called out explicitly
- [ ] No high-confidence recommendations given on < 20 conversion data points
- [ ] CAPI status checked and flagged if missing
- [ ] Action items are specific and implementable (exact ad set names, budget numbers, creative format types), not generic
