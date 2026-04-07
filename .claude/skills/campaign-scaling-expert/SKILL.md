---
name: campaign-scale-analyzer
description: Analyze Google Ads campaign performance across an entire account and deliver a prioritized, actionable scaling roadmap. Triggers when a user wants to grow revenue/conversions from existing campaigns, increase budget efficiency before expanding spend, or diagnose what's holding performance back. Accepts campaign-level exports, pasted data tables, or manually typed metrics. Outputs a tiered scaling plan with confidence scores and implementation steps.
---

# Google Ads Campaign Scale Analyzer

This skill performs a structured diagnostic of your Google Ads account to identify the highest-leverage actions for scaling performance — not just fixing problems, but systematically unlocking growth. It separates what to protect, what to accelerate, and what to restructure, then delivers a ranked action plan you can execute immediately.

## Core Philosophy

1. **Scale winners before fixing losers.** Most accounts have 1–2 campaigns ready to scale today. Find those first.
2. **Efficiency before volume.** Pouring budget into a leaky funnel doesn't scale — it burns. Confirm unit economics are sound before recommending spend increases.
3. **Structure enables scale.** Poor campaign architecture creates invisible ceilings. Surface structural issues that will block growth at higher spend.
4. **Data drives confidence.** Every recommendation is tagged with a confidence level based on data volume. Low data = low confidence = monitor, not act.
5. **One account, many businesses.** Context about the business model changes every recommendation. Never analyze in a vacuum.

---

## Critical Context Gathering

### Required Context (Ask if not provided)

**1. Business Model & Conversion Goal**
What does a conversion mean for this business — lead form, phone call, purchase, trial signup? What's the average order value or customer lifetime value if known? Is it B2B or B2C? This single piece of context changes every threshold and recommendation.

*Example:* A $50 CPA is great for a $500 product, catastrophic for a $60 product.

**2. Target CPA or ROAS**
What's the goal? If none exists, ask: "What does a conversion need to cost to be profitable?" Use this as the benchmark for every campaign evaluation. If the user doesn't know, note this and calculate an implied target from the data.

**3. Time Period of Data**
At minimum 30 days. 90 days is ideal for seasonal patterns. Ask the user what window they're sharing and flag if it's less than 30 days (low-confidence mode).

### Recommended Context

**4. Monthly Budget (Total & Per Campaign)**
Needed to assess whether campaigns are budget-constrained vs. impression-share constrained. If not provided, estimate from spend data.

**5. Current Bid Strategy Per Campaign**
Manual CPC, Target CPA, Target ROAS, Maximize Conversions — the scaling playbook differs significantly by strategy. If not provided, ask or infer from the data.

**6. Top Competitors or Industry**
Helps contextualize benchmark CTR, CVR, and CPC. Not required, but improves the relevance of observations.

### Optional Context

**7. Historical Performance Trend**
Is the account growing, declining, or flat over the past 6–12 months? Provides directional context for whether issues are structural or situational.

**8. Any Recent Major Changes**
Budget cuts, landing page changes, new campaigns launched, bid strategy switches in the past 60 days. Prevents misattributing structural problems to recent experiments.

---

## Input Format

Accept any of the following — be flexible:

- **CSV/Excel export** from Google Ads (Campaign or Ad Group report)
- **Pasted table** from the Google Ads UI
- **Manual summary** (e.g., "Campaign A: $5,000 spend, 80 conversions, $62 CPA, 3.2% CVR")
- **Screenshot description** (user describes what they see)

**Minimum fields needed:**
Campaign Name | Spend | Conversions | CPA | Impressions | Clicks | CTR

**Ideal fields (for deeper analysis):**
+ Impression Share | Lost IS (Budget) | Lost IS (Rank) | Search Top IS | CVR | Avg CPC | Quality Score (if available)

If critical fields are missing, note what analysis will be limited and proceed with what's available.

---

## Analysis Framework

### Phase 1: Account-Level Health Triage

Before campaign-level analysis, establish the overall account state.

| Metric | 🟢 Healthy | 🟡 Watch | 🔴 Critical |
|---|---|---|---|
| Overall CPA vs Target | ≤ target | 1.0–1.3× target | > 1.3× target |
| Overall CVR | ≥ industry avg | 50–80% of avg | < 50% of avg |
| Budget Utilization | 80–95% | < 70% or > 98% | Consistently 100% (constrained) |
| Conversion Volume (30d) | ≥ 50 total | 20–49 | < 20 (low data) |
| Spend Concentration | No single campaign > 60% | 60–75% | > 75% in one campaign |

**Declare overall account health status: 🟢 / 🟡 / 🔴**

---

### Phase 2: Campaign Tiering

Classify every campaign into one of four tiers based on CPA performance and conversion volume:

| Tier | Label | Criteria | Strategic Action |
|---|---|---|---|
| **Tier 1** | Scale Now | CPA ≤ target AND conversions ≥ 20 | Increase budget 20-30% every 3-5 days (never more than 30% in a single day — this resets Smart Bidding learning). Confirm CPA stays within target before each increment. |
| **Tier 2** | Optimize to Scale | CPA 1.0–1.3× target OR conversions 10–19 | Fix efficiency first, then scale |
| **Tier 3** | Restructure or Pause | CPA > 1.3× target AND low volume | Audit structure, creative, landing page before more spend |
| **Tier 4** | Monitor | < 10 conversions in period | Insufficient data — do not make structural changes |

Assign each campaign a tier. Flag if all campaigns are Tier 3/4 — this indicates an account-level structural issue, not a campaign-level one.

---

### Phase 3: Scaling Lever Analysis

For each Tier 1 and Tier 2 campaign, evaluate the following scaling levers in order:

#### Lever A — Budget Constraint Check
- Is Lost IS (Budget) > 15%? If yes: campaign is budget-constrained. Increasing budget is the highest-confidence scaling action.
- Confidence: **0.90** if Lost IS (Budget) > 20% AND CPA is at or below target.

#### Lever B — Bid Strategy Optimization
Evaluate current bid strategy against conversion volume:

| Conversions (30d) | Recommended Bid Strategy | Rationale |
|---|---|---|
| < 15 | Maximize Conversions (no target) | Smart bidding needs data; constraints hurt learning |
| 15–30 | Target CPA (set 20% above actual CPA) | Enough data; don't over-constrain |
| > 30 | Target CPA at goal OR Target ROAS | Full smart bidding leverage |

Flag campaigns running Manual CPC with > 30 conversions — this is a clear missed scaling opportunity.

**Cost Cap strategy for scaling with efficiency protection:**
When a campaign has achieved stable CPA and you want to scale without CPA degradation: set a Cost Cap equal to the target CPA and inflate the budget 3-5x the actual expected daily spend. The campaign self-regulates — it will only spend when it can meet the cost cap. This is the preferred scaling mechanism for campaigns where CPA protection is the priority over volume maximization.

#### Lever C — Impression Share Gap
- Search Impression Share < 60% AND Lost IS (Rank) > 20%: Quality Score or bid issue. Fix before scaling budget.
- Search Impression Share < 60% AND Lost IS (Budget) > 20%: Budget is limiting reach. Scaling budget = scaling conversions.
- Top-of-page IS < 40% for brand campaigns: Brand control problem — fix immediately.

#### Lever D — Creative Performance
- CTR < 3% on Search: Headlines likely missing intent match. Flag for RSA audit.
- CTR ≥ 3% but CVR < 2%: Landing page problem, not ad problem.
- CTR ≥ 3% AND CVR ≥ 3%: Funnel is working — scaling lever is budget or bids.

#### Lever E — Structural Efficiency
- Single ad group with > 20 keywords: Too broad, reducing relevance.
- Ad groups mixing branded + non-branded: Contaminating CPA data.
- No exact match variants for top-converting terms: Missing control over best performers.

---

### Phase 4: Scaling Roadmap Construction

After tiering campaigns and evaluating levers, build a prioritized roadmap:

**Prioritization Logic:**

| Action Type | Priority | Rationale |
|---|---|---|
| Fix budget-constrained Tier 1 campaigns | P1 — This Week | Highest confidence, immediate ROI |
| Upgrade bid strategies on data-rich campaigns | P1 — This Week | Unlocks algorithmic scaling |
| Restructure Tier 3 campaigns | P2 — This Month | Removes structural ceiling |
| Address Impression Share gaps | P2 — This Month | Enables more efficient scaling |
| Creative audit for low-CTR ad groups | P2 — This Month | Improves funnel entry |
| Expand Tier 1 campaigns (new keywords, ad groups) | P3 — Next Quarter | Build on proven winners |
| Launch net-new campaigns | P3 — Next Quarter | Only after existing efficiency confirmed |

---

## Output Format

Deliver in this exact structure:

---

### 📊 Account Snapshot
> **Overall Health:** 🟢/🟡/🔴
> **Period Analyzed:** [X days]
> **Total Spend:** $X | **Total Conversions:** X | **Blended CPA:** $X | **Target CPA:** $X
> **Key Finding (1 sentence):** [The single most important thing about this account right now]

---

### 🏷️ Campaign Tiers

| Campaign | Spend | Conv. | CPA | vs. Target | Tier | Primary Lever |
|---|---|---|---|---|---|---|
| Campaign A | $X | X | $X | -12% | 🟢 Tier 1 | Budget constrained |
| Campaign B | $X | X | $X | +8% | 🟡 Tier 2 | Bid strategy |
| Campaign C | $X | X | $X | +45% | 🔴 Tier 3 | Restructure |

---

### 🚀 Scaling Roadmap

#### P1 — Act This Week
**[Action Title]** | Confidence: 0.XX
- **What:** [Specific change — e.g., "Increase Campaign A daily budget from $150 to $185"]
- **Why:** [Data-backed reason — e.g., "Lost IS (Budget) = 28%, CPA is 12% below target"]
- **How:** [Exact steps in Google Ads — e.g., "Campaigns → Campaign A → Settings → Budget → $185"]
- **Expected Impact:** [Conservative estimate — e.g., "+15–20 conversions/month at current CPA"]

*(Repeat for each P1 action)*

#### P2 — This Month
*(Same format as P1)*

#### P3 — Next Quarter
*(Same format, but framed as planning items)*

---

### ⚠️ Risks & Watch Items
- [Any campaigns or metrics to monitor closely before acting]
- [Data confidence warnings if conversion volume is low]

---

### ❓ Open Questions
- [Any context gaps that would change the recommendations if answered]

---

## Guardrails

❌ **NEVER** recommend increasing budget on a campaign with CPA > 1.3× target without first identifying why.

❌ **NEVER** recommend pausing a campaign with > $5K historical spend without flagging it as a high-risk action requiring human review.

❌ **NEVER** set specific Target CPA recommendations without knowing the business's actual CPA goal or margin.

❌ **NEVER** label a campaign "failing" based on fewer than 10 conversions — call out low data explicitly.

❌ **NEVER** recommend switching bid strategies during a known peak season without flagging the learning period risk.

✅ **ALWAYS** rank actions by expected impact × confidence, not just impact alone.
❌ **NEVER** recommend a budget increase of more than 30% in a single day for Smart Bidding campaigns — this resets learning and can spike CPA for 1-2 weeks. Scale in increments of 20-30% every 3-5 days.
❌ **NEVER** recommend scaling budget when CPA has risen more than 20% week-over-week — diagnose the CPA spike before adding fuel. Scaling an inefficient campaign is not scaling, it is accelerating waste.

✅ **ALWAYS** protect brand campaigns from aggressive optimization recommendations — they operate differently.

✅ **ALWAYS** note when a recommendation requires A/B testing vs. direct implementation.

✅ **ALWAYS** flag if the account has fewer than 50 total conversions — full smart bidding is likely premature.

✅ **ALWAYS** distinguish between "scale budget" (more of the same) and "scale structure" (new campaigns/ad groups).

---

## Edge Cases

### New Account (< 90 days old)
Treat all campaigns as Tier 4 regardless of early CPA. Prioritize conversion tracking verification, smart bidding learning period completion, and search term data collection over optimization. Scaling too early locks in inefficiency.

### All Campaigns Are Tier 3 or 4
This signals a systemic problem, not individual campaign failures. Shift analysis to: conversion tracking accuracy, landing page quality, keyword intent match, and account structure. Do not recommend scaling spend — recommend a conversion audit first.

### Single Campaign Account
Skip tiering. Focus entirely on lever analysis (Budget, Bids, IS, Creative, Structure). Emphasize the risk concentration of having no diversification.

### Wildly Different Campaign Types (Search + Display + Shopping + PMax)
Analyze separately by campaign type. Never blend Search CPA benchmarks with Display or PMax without noting the comparison is invalid. PMax requires its own scaling framework (asset quality, audience signals, conversion goals).

### Budget Constrained at Account Level
If total account Lost IS (Budget) > 30%, the first recommendation is always "increase total budget or reallocate from Tier 3 campaigns to Tier 1." Structure advice is secondary until budget is adequate.

---

## Quality Assurance

Before delivering the output:
- [ ] Every campaign has a tier assignment with data-backed rationale
- [ ] Every P1 action includes specific numbers (not "increase budget" but "increase to $X")
- [ ] Confidence scores are applied consistently using the 0.5–1.0 scale
- [ ] No recommendation contradicts another (e.g., don't say "pause" and "optimize" the same campaign)
- [ ] Brand campaigns are treated separately from non-brand
- [ ] Low data campaigns are flagged, not optimized
- [ ] Open questions section captures anything that would materially change recommendations
- [ ] Output is ready to hand to a media buyer without additional translation
