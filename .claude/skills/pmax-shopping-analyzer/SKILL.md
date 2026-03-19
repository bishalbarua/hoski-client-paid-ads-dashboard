---
name: pmax-shopping-analyzer
description: Deep audit of Performance Max and Standard Shopping campaigns. Analyzes asset group performance, channel distribution, brand cannibalization, feed quality signals, product group performance, PMax vs. Search/Shopping campaign conflicts, audience signal health, and learning period status. Triggers when a user wants to audit a PMax campaign, diagnose underperformance, evaluate PMax vs. Standard Shopping trade-offs, or understand where PMax spend is actually going. Distinct from /ppc-account-health-check (broad strategic audit) and /campaign-scaling-expert (scaling roadmap) — this is a technical deep dive specific to PMax and Shopping campaign mechanics.
---

# PMax & Shopping Analyzer

Performance Max is Google's highest-automation campaign type, and it's also the hardest to audit. Google surfaces very little — no keywords, limited placement data, no per-asset conversion data, and opaque channel allocation. This skill extracts maximum signal from what IS visible: asset group performance, network distribution, brand/non-brand traffic patterns, product group data, feed quality signals, and audience signal health. It also diagnoses the most dangerous PMax failure modes that standard account audits miss entirely: brand cannibalization, channel imbalance, learning period churn, and feed-quality conversion drag.

## How This Skill Differs from Similar Skills

| | PMax & Shopping Analyzer | PPC Account Health Check | Campaign Scaling Expert | Search Terms |
|---|---|---|---|---|
| **Scope** | PMax and Shopping campaigns, deep technical | All campaigns, strategic overview | All campaigns, scaling roadmap | Search query analysis (not applicable to PMax Shopping) |
| **PMax depth** | Full: asset groups, channels, brand split, feed, audience signals | Surface: PMax health flag if CPA is off | Surface: scale/pause recommendation | N/A |
| **When to use** | PMax/Shopping underperforming, new PMax audit, pre-scaling check | Quarterly account review, new client | Before increasing budget | Weekly operational sweep |
| **Output** | PMax-specific diagnostics + fix sequence | Traffic-light health score | P1/P2/P3 scaling plan | Keyword action lists |

---

## Core Philosophy

1. **PMax is a black box, but it leaks signals.** Channel distribution, asset group impression share, brand traffic erosion, and product group data all reveal what Google is doing with your budget — even without keyword or placement transparency.
2. **Learning period is sacred.** PMax needs 6 weeks and 30–50 conversions to stabilize. One budget cut, one conversion action change, one major asset group edit resets the clock. Every recommendation must weigh whether it triggers a reset.
3. **Brand cannibalization is the #1 silent PMax problem.** PMax has priority over all other campaign types for search traffic. Without a brand exclusion list, it will absorb your branded queries — inflating PMax conversion numbers and making it look better than it is.
4. **Channel imbalance is the #1 PMax waste vector.** PMax will happily spend 70% of budget on Display and YouTube if that's where Google's automated bidding finds cheap "conversions." If those aren't real conversions, the campaign is destroying money while reporting great numbers.
5. **For Shopping, feed quality is campaign quality.** The product feed is the keyword list. Bad titles, missing attributes, and uncompetitive pricing drag CTR and conversion rate regardless of bidding.

---

## Critical Context Gathering

### Required Context (Ask if not provided)

**1. Client Name or Account ID**
Which account to audit. Look up ID in CLAUDE.md.

**2. Campaign Type Scope**
- Audit PMax only
- Audit Standard Shopping only
- Audit both and compare (recommended — need to understand interaction)

**3. Business Model**
- eCommerce / retail (product feed, ROAS optimization)
- Lead gen with PMax (asset groups, CPA optimization)
- Local service business using PMax (store visits, calls)

Why it matters: The entire analysis framework changes. eCommerce PMax is about feed quality and product groups. Lead gen PMax is about asset groups, audience signals, and channel distribution. Local PMax has unique store visit conversion considerations.

### Recommended Context

**4. Conversion Goals Active on PMax**
What conversions is PMax optimizing for? How many per month?

Why it matters:
- PMax needs 30–50 conversions/month minimum to exit learning. Below that, recommendations are fundamentally different.
- If PMax is optimizing for soft conversions (page views, scroll depth), the ROAS/CPA numbers are fiction.

**5. Other Campaign Types Running Simultaneously**
Are there Search, Standard Shopping, or Display campaigns running alongside PMax?

Why it matters: PMax has priority in the ad auction over all other campaign types for the same queries. If Search and PMax are running on the same service/product, they're competing — and PMax almost always wins.

**6. Brand Exclusion Status**
Has a brand exclusion list been applied to PMax? Do they have a separate brand Search campaign?

Why it matters: Without brand exclusions, PMax steals branded query traffic from brand Search campaigns and claims those easy conversions as PMax performance.

### Optional Context

**7. ROAS or CPA Target**
Current target and whether the campaign is hitting it.

**8. Feed Management Platform**
For eCommerce: Shopify, WooCommerce, custom feed, DataFeedWatch, etc.
Helps identify feed quality fix options.

**9. Time Since PMax Launch**
How long has this PMax campaign been running?

Determines whether issues are learning-period noise vs. genuine structural problems.

---

## Input Format

**API pull (preferred):** Client name or account ID — I'll run all queries.

**Manual data paste:** Campaign performance export + any asset group data available from Google Ads UI (Performance Max → Asset Groups tab).

**Minimum viable:** Campaign names, spend, conversions, CPA/ROAS for the period, and whether brand exclusions are active.

---

## API Queries

### Query 1: PMax Campaign Performance Overview

```python
from google.ads.googleads.client import GoogleAdsClient
import os

client = GoogleAdsClient.load_from_dict({
    "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
    "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
    "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
    "refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
    "login_customer_id": os.environ["GOOGLE_ADS_CUSTOMER_ID"],
    "use_proto_plus": True
})

ga_service = client.get_service("GoogleAdsService")
customer_id = "[ACCOUNT_ID]"

query = """
    SELECT
        campaign.name,
        campaign.status,
        campaign.advertising_channel_type,
        campaign.bidding_strategy_type,
        campaign.target_roas.target_roas,
        campaign.target_cpa.target_cpa_micros,
        campaign_budget.amount_micros,
        metrics.impressions,
        metrics.clicks,
        metrics.ctr,
        metrics.conversions,
        metrics.conversions_value,
        metrics.cost_micros,
        metrics.cost_per_conversion,
        metrics.value_per_conversion,
        metrics.search_impression_share,
        metrics.search_budget_lost_impression_share,
        metrics.search_rank_lost_impression_share
    FROM campaign
    WHERE segments.date DURING LAST_30_DAYS
    AND campaign.advertising_channel_type IN ('PERFORMANCE_MAX', 'SHOPPING')
    AND campaign.status != 'REMOVED'
    ORDER BY metrics.cost_micros DESC
"""
```

### Query 2: Asset Group Performance (PMax)

```python
query = """
    SELECT
        campaign.name,
        asset_group.name,
        asset_group.status,
        asset_group.ad_strength,
        metrics.impressions,
        metrics.clicks,
        metrics.conversions,
        metrics.cost_micros,
        metrics.cost_per_conversion,
        metrics.conversions_value
    FROM asset_group
    WHERE segments.date DURING LAST_30_DAYS
    AND campaign.advertising_channel_type = 'PERFORMANCE_MAX'
    AND asset_group.status != 'REMOVED'
    ORDER BY metrics.impressions DESC
"""
```

### Query 3: Channel Distribution (Ad Network Type)

```python
query = """
    SELECT
        campaign.name,
        segments.ad_network_type,
        metrics.impressions,
        metrics.clicks,
        metrics.ctr,
        metrics.conversions,
        metrics.cost_micros,
        metrics.cost_per_conversion,
        metrics.conversions_value
    FROM campaign
    WHERE segments.date DURING LAST_30_DAYS
    AND campaign.advertising_channel_type = 'PERFORMANCE_MAX'
    ORDER BY campaign.name, metrics.cost_micros DESC
"""
```

### Query 4: Product Group Performance (eCommerce PMax + Standard Shopping)

```python
query = """
    SELECT
        campaign.name,
        asset_group.name,
        asset_group_product_group_view.path,
        metrics.impressions,
        metrics.clicks,
        metrics.ctr,
        metrics.conversions,
        metrics.conversions_value,
        metrics.cost_micros,
        metrics.cost_per_conversion,
        metrics.value_per_conversion
    FROM asset_group_product_group_view
    WHERE segments.date DURING LAST_30_DAYS
    ORDER BY metrics.cost_micros DESC
"""
```

### Query 5: Search Impression Share — PMax vs. Brand Campaign Comparison

```python
query = """
    SELECT
        campaign.name,
        campaign.advertising_channel_type,
        campaign.bidding_strategy_type,
        metrics.search_impression_share,
        metrics.search_absolute_top_impression_share,
        metrics.search_budget_lost_impression_share,
        metrics.search_rank_lost_impression_share,
        metrics.impressions,
        metrics.conversions,
        metrics.cost_micros
    FROM campaign
    WHERE segments.date DURING LAST_30_DAYS
    AND campaign.status = 'ENABLED'
    ORDER BY metrics.impressions DESC
"""
```

### Query 6: PMax Search Term Categories (Limited Visibility)

```python
# Note: Google only exposes aggregated search categories for PMax, not individual terms
query = """
    SELECT
        campaign.name,
        search_term_insight.category_label,
        metrics.impressions,
        metrics.clicks,
        metrics.conversions,
        metrics.cost_micros
    FROM search_term_insight
    WHERE segments.date DURING LAST_30_DAYS
    AND campaign.advertising_channel_type = 'PERFORMANCE_MAX'
    ORDER BY metrics.cost_micros DESC
"""
```

---

## Analysis Framework

### Check 1: Learning Period Status

This must be assessed first. If PMax is still learning, most optimization recommendations are harmful.

| Condition | Status | Action |
|---|---|---|
| Campaign < 6 weeks old | In learning | Do structural fixes only. No budget cuts, no conversion action changes, no major asset group edits. |
| Campaign 6+ weeks, <30 conversions/month | Effectively in perpetual learning | PMax cannot work with this conversion volume. Consider pausing — Standard Shopping may outperform. |
| Campaign 6+ weeks, 30–50 conversions/month | Marginal learning | PMax is functional but fragile. Any significant change resets learning. Proceed with extreme caution. |
| Campaign 6+ weeks, >50 conversions/month | Graduated learning | Full optimization available. Smart Bidding has sufficient signal. |
| Conversion action changed in last 6 weeks | Learning reset | Treat as new campaign regardless of age. |
| Budget cut >20% in last 6 weeks | Learning disrupted | Flag as potential cause of performance drop. |

**Learning period budget check:**
Minimum daily budget = 2× target CPA (for tCPA) or (target revenue ÷ target ROAS) × 2 (for tROAS).
If current daily budget < this minimum, PMax cannot learn efficiently.

---

### Check 2: Brand Cannibalization Audit

The most important PMax-specific check. PMax has priority in the auction over all other campaign types.

**Detection signals:**

| Signal | What to Look For | Cannibalization Risk |
|---|---|---|
| Brand Search campaign IS% | Dropped after PMax launch | 🔴 High — PMax absorbing brand queries |
| PMax search term categories | Contains "[brand name]" category | 🔴 Confirmed — brand traffic in PMax |
| PMax conversion rate >> account average | PMax CvR 2–3× higher than non-brand Search | 🔴 PMax is cherry-picking easy branded conversions |
| PMax cost per conversion < brand campaign | PMax CPA lower than brand campaign CPA | ⚠️ Check if brand traffic is inflating PMax metrics |
| No brand exclusion list active | N/A | 🔴 Brand cannibalization is virtually certain |

**Fix:** Add brand terms to the account-level "Brand exclusions" list for PMax campaigns (Google Ads UI → Campaigns → [PMax] → Settings → Brand exclusions). This does NOT require a separate negative keyword list — it's a specific PMax setting.

---

### Check 3: Channel Distribution Analysis

PMax runs across Search, Shopping, Display, YouTube, Gmail, Maps, and Discover. Healthy distribution varies by goal.

**Pull from Query 3. Segment results by ad_network_type.**

Ad network type values:
- `SEARCH` — Google Search
- `CONTENT` — Google Display Network (GDN)
- `YOUTUBE_WATCH` — YouTube
- `GOOGLE_SHOPPING` — Shopping tab / surfaces

**Distribution benchmarks by business type:**

| Business Type | Healthy Search/Shopping % | Warning Threshold | Critical Threshold |
|---|---|---|---|
| Lead gen | >60% of spend on Search | <50% on Search | <35% on Search |
| eCommerce | >50% on Shopping + Search | <40% on Shopping+Search | <25% on Shopping+Search |
| Local service (store visits) | Mix acceptable — check conversion type | All on Display = no local intent | — |

**Channel red flags:**

| Pattern | Issue |
|---|---|
| >40% spend on Content/GDN, low conversion rate from that channel | GDN is bleeding budget with no ROI — PMax chasing cheap impressions |
| YouTube taking >25% spend on lead gen with 0 conversions | Video budget without video conversions |
| Search <30% of total spend on lead gen | PMax not capturing search intent — the highest-value channel |
| Shopping 0% of spend on eCommerce PMax | Feed may be disconnected or disapproved |

---

### Check 4: Asset Group Health

Asset groups are the primary optimization lever inside PMax. Each asset group = a targeting theme (audience signal + creative assets).

**From Query 2:**

| Asset Group Pattern | Assessment |
|---|---|
| 1 asset group getting >90% of impressions | Google has collapsed testing — other groups aren't viable. Check ad strength on losing groups. |
| All asset groups in LEARNING | Campaign is too new or too low volume — no optimization possible |
| Asset group with 0 impressions in 30 days | Audience signal may be too narrow, OR assets disapproved, OR this theme has no traffic |
| Ad strength "Poor" on any asset group | Critical — missing headlines, descriptions, images, or videos. PMax deprioritizes Poor groups. |
| Multiple asset groups all similar themes | Redundant structure — Google can't differentiate; consolidate |

**Ad strength requirements per asset group:**
- Minimum: 1 final URL, 3 headlines, 2 descriptions, 1 image (landscape), 1 logo
- For Good/Excellent strength: 5 headlines, 5 descriptions, multiple image formats, at least 1 video (YouTube link)
- No video = Google auto-generates one from your images. Auto-generated videos are low quality — always provide a real one.

---

### Check 5: Audience Signal Evaluation

Audience signals are suggestions to Google, not targeting. Google will expand beyond them. But bad signals slow learning.

**Signal quality framework:**

| Signal Type | Quality | Notes |
|---|---|---|
| Customer list (CRM upload) | ✅ Excellent | Your actual converters — strongest signal possible |
| Website visitors (remarketing) | ✅ Strong | Past intent signal |
| Custom intent (search terms list) | ✅ Strong | Tell PMax what search queries your buyers use |
| In-market audience (relevant) | ⚠️ Moderate | OK starting point, not specific to your buyers |
| Affinity audience | ⚠️ Weak | Too broad — Google will likely ignore it |
| Similar audiences (based on CRM) | ✅ Good | Works well if source list has 1,000+ members |
| No audience signals | 🔴 Poor | PMax starts cold with no hints — learning takes longer |

**Red flags:**
- Only affinity audiences as signals (too vague)
- No custom intent signals (missing the search query angle)
- No customer list uploaded (highest-quality signal being ignored)
- Audience signals from irrelevant demographics (e.g., teen audiences for B2B software)

---

### Check 6: PMax vs. Standard Shopping Conflict

Running both PMax and Standard Shopping on the same products creates auction conflict. PMax wins the auction by default.

**Detection:**

| Scenario | Issue |
|---|---|
| PMax and Standard Shopping running same product set | PMax wins every auction — Standard Shopping spend will drop to near 0 |
| Standard Shopping IS% dropped after PMax launch | PMax is cannibalizing Standard Shopping |
| Standard Shopping CPA was lower than PMax | You may have sacrificed a better-performing campaign for PMax |

**Resolution options:**

| Approach | When to Use | How |
|---|---|---|
| Pause Standard Shopping | PMax is outperforming on all metrics | Confirm PMax CPA/ROAS is better WITHOUT brand traffic included |
| Segment by product | Some products better in Standard, others in PMax | Standard Shopping: Bestsellers or high-margin products; PMax: long-tail catalog |
| Priority + campaign exclusions | Want both running | Standard Shopping at High priority with brand exact excluded; PMax handles everything else |

---

### Check 7: Feed Quality Signals (eCommerce)

For retail PMax and Standard Shopping, the feed IS the campaign. Poor feed quality = poor performance regardless of bidding.

**Check via Google Merchant Center (outside API) or Shopping campaign impression/CTR patterns:**

| Signal | Healthy | Warning | Critical |
|---|---|---|---|
| Product title format | Brand + Type + Key Attribute | Title is just product name | Title is generic (e.g., "Product 1") |
| Product description | 150–500 chars, includes key search terms | Short (<100 chars) | Missing or generic |
| Product images | High-res, white background, product-only | Lifestyle images (lower CTR for Shopping) | Placeholder or missing |
| GTIN / MPN | Present for branded products | Missing for branded items | Missing for most items |
| Product type taxonomy | Detailed (e.g., Apparel > Shoes > Running Shoes > Men's) | 1-2 level (Apparel > Shoes) | No taxonomy |
| Price competitiveness | At or below market | Slightly above market | Significantly above market |
| Disapproved products | 0–2% of catalog | 5–10% | >10% |
| Missing required attributes | 0 | 1–3 attributes | Multiple attributes |

**Feed quality impact on PMax:**
- Missing GTINs = lower Shopping eligibility and lower auction priority
- Poor titles = low CTR = Google learns your products don't convert = reduced impressions
- Disapproved products = wasted feed slots + compliance risk

---

### Check 8: Conversion Goal Alignment

PMax optimizes for what you tell it to optimize for. Wrong conversion goals = wrong behavior.

| Scenario | Risk | Fix |
|---|---|---|
| Optimizing for soft conversions (page view, scroll, session) | PMax drives junk traffic that triggers micro-conversions | Switch primary goal to purchase/lead/call |
| Multiple primary conversion actions including low-quality ones | PMax optimizes for easiest conversions, not business-value ones | Set macro conversion as only primary, micro as secondary |
| eCommerce without conversion value | PMax can't run tROAS — forced to use maximize conversion value with no target | Implement dynamic value passing (required for tROAS) |
| CPA target set far below actual achievable CPA | PMax severely limits impressions to find "cheap" conversions | Adjust target to ±20% of recent actual CPA |
| ROAS target set far above achievable ROAS | Same — PMax throttles to chase unrealistic ROAS, impression share collapses | Adjust to ±20% of recent actual ROAS |

---

## Output Format

```
# PMax & Shopping Audit — [Client Name]
**Account ID:** [ID]
**Scope:** [PMax only / Shopping only / Both]
**Period:** Last 30 Days
**Date:** [Date]

---

## Executive Summary

[3-4 sentences: overall health, the most critical issue, and the one thing to do first]

**Overall Status:** 🟢 Healthy / 🟡 Issues Found / 🔴 Critical Problems

---

## Campaign Inventory

| Campaign | Type | Budget/Day | Bid Strategy | Target | Conversions | CPA/ROAS | Status |
|---|---|---|---|---|---|---|---|
| [Name] | PMax | $[X] | tCPA | $[X] | [N] | $[X] | 🟢/🟡/🔴 |
| [Name] | Standard Shopping | $[X] | tROAS | [X]x | [N] | [X]x | 🟢/🟡/🔴 |

---

## Check 1: Learning Period

**Status:** [In Learning / Graduated / Perpetual Learning / Reset Triggered]
**Weeks Live:** [N]
**30-Day Conversions:** [N] ([Sufficient / Marginal / Insufficient])
**Budget vs. Minimum Required:** $[actual]/day vs. $[minimum]/day ([Above/Below threshold])

[If in learning: specific recommendation on what NOT to change]
[If graduated: confirm optimization is appropriate]

---

## Check 2: Brand Cannibalization

**Brand Exclusion List Active:** ✅ Yes / 🔴 No
**Brand Search IS% Trend:** [Stable / Declined after PMax launch / Unknown]
**PMax Conversion Rate vs. Account Average:** [X%] vs. [Y%] — [Normal / Suspiciously higher — brand traffic likely]

**Verdict:** [Clean / 🔴 Brand cannibalization detected]
**Fix:** [Specific steps to add brand exclusion list]

---

## Check 3: Channel Distribution

| Channel | Spend | % of Total | Conversions | Conv Rate | CPA/ROAS | Assessment |
|---|---|---|---|---|---|---|
| Search | $[X] | [X%] | [N] | [X%] | $[X] | ✅/⚠️/🔴 |
| Shopping | $[X] | [X%] | [N] | [X%] | $[X] | ✅/⚠️/🔴 |
| Display (GDN) | $[X] | [X%] | [N] | [X%] | $[X] | ✅/⚠️/🔴 |
| YouTube | $[X] | [X%] | [N] | [X%] | $[X] | ✅/⚠️/🔴 |
| Gmail / Discover | $[X] | [X%] | [N] | [X%] | $[X] | ✅/⚠️/🔴 |

**Channel verdict:** [e.g., "GDN absorbing 45% of budget with 2% conversion rate — PMax is optimizing for cheap Display impressions, not conversions"]

---

## Check 4: Asset Group Health

| Asset Group | Ad Strength | Impressions | Conversions | CPA | Issues |
|---|---|---|---|---|---|
| [Name] | Excellent | [N] | [N] | $[X] | ✅ None |
| [Name] | Poor | 0 | 0 | — | 🔴 Missing images, no video |
| [Name] | Average | [N] | [N] | $[X] | ⚠️ Add video |

**Structural issues:**
- [e.g., "Asset group 'General' receiving 94% of impressions — PMax has effectively collapsed to 1 theme"]
- [e.g., "2 asset groups have no video — Google is auto-generating video from images"]

---

## Check 5: Audience Signal Quality

| Asset Group | Signals Present | Signal Quality | Recommendation |
|---|---|---|---|
| [Name] | Customer list, Custom intent | ✅ Strong | None |
| [Name] | Affinity only | 🔴 Weak | Add customer list + custom intent search terms |
| [Name] | None | 🔴 No signals | Add at minimum: custom intent with top search terms |

---

## Check 6: PMax vs. Shopping Conflict

**Conflict detected:** ✅ No conflict / 🔴 Conflict — [description]

[If conflict: specific recommendation on how to resolve with product segmentation or priority settings]

---

## Check 7: Feed Quality (eCommerce)

| Attribute | Status | Issue | Fix |
|---|---|---|---|
| Product titles | ⚠️ | 340/500 products missing brand in title | Update feed: prepend brand to title |
| GTINs | 🔴 | 180 branded products missing GTIN | Source GTINs from manufacturer; add to feed |
| Images | ✅ | — | — |
| Disapprovals | ⚠️ | 23 products (4.6%) | Review Merchant Center diagnostics |

---

## Check 8: Conversion Goal Alignment

**Primary conversion goals:** [List]
**Conversion volume (30d):** [N]
**Bid target vs. actual:** Target $[X] CPA / Actual $[X] CPA — [Reasonable / Too aggressive / Too conservative]

**Issues:**
- [e.g., "tROAS target is 800% but actual ROAS is 340% — campaign is severely impression-throttled"]
- [e.g., "Page view is set as primary conversion — PMax is optimizing for traffic, not leads"]

---

## PMax Search Term Categories

[From Query 6 — top categories by spend]

| Category | Impressions | Conversions | Cost | Assessment |
|---|---|---|---|---|
| [Brand name] | [N] | [N] | $[X] | 🔴 Brand traffic in PMax — add exclusion |
| [Core service] | [N] | [N] | $[X] | ✅ Right traffic |
| [Irrelevant category] | [N] | [N] | $[X] | ⚠️ Review |

---

## Priority Action List

**Fix Immediately (before any other optimization):**
1. [Action] — [Why: risk if not fixed] — [Exact UI location or code to run]
2. [Action] — [Why] — [Location]

**Fix This Week:**
3. [Action] — [Why] — [Location]
4. [Action] — [Why] — [Location]

**Fix This Month:**
5. [Action] — [Why] — [Location]

**Do NOT change (would disrupt learning):**
- [Specific setting to leave alone]
- [Specific setting to leave alone]
```

---

## Guardrails

❌ **NEVER** recommend pausing a PMax campaign that is mid-learning without explicitly warning that performance may drop for 2–4 weeks and may not recover to previous levels — PMax learning is not fully recoverable.

❌ **NEVER** recommend more than 1 significant change at a time to a live PMax campaign — each change (budget >20%, bid target, conversion action, major asset group edit) independently resets the learning period.

❌ **NEVER** recommend removing a PMax campaign based solely on high CPA without first checking whether brand cannibalization is inflating PMax's reported conversion numbers — stripping brand traffic may reveal PMax is actually performing well on non-brand queries.

❌ **NEVER** recommend Standard Shopping over PMax purely because "you have more control" — control is only valuable if you're using it correctly. For accounts with sufficient conversion volume and a good feed, PMax can outperform Standard Shopping at scale.

✅ **ALWAYS** check learning period status before any other recommendation — all other analysis is secondary if PMax is still learning.

✅ **ALWAYS** verify brand exclusion list status — it's the single most impactful PMax configuration that's most commonly missing.

✅ **ALWAYS** include a "Do NOT change" section — in PMax, things to avoid changing are as important as things to fix.

✅ **ALWAYS** distinguish between "PMax is underperforming" and "PMax reporting looks inflated" — the fix is the opposite in each case.

---

## Edge Cases

### PMax With No Conversions (Brand New or Zero-Volume)
If PMax has been running for 30+ days with 0 conversions:
- Check conversion tracking first (run /conversion-tracking-audit before touching PMax)
- Check if products are all disapproved in Merchant Center (for eCommerce)
- Check if geo targeting is too narrow (PMax geo settings are under-documented and easy to misconfigure)
- Check if audience signals are so narrow that Google can't find any traffic
- Do NOT interpret as a PMax failure until tracking and feed are confirmed clean

### eCommerce PMax With No Shopping Component
PMax should always have a product feed linked for eCommerce accounts. If PMax is running without a feed:
- It becomes a pure creative ad serving tool (images, headlines, descriptions only)
- It cannot show Shopping ads — a massive channel gap for retail
- Link the Merchant Center feed to the PMax campaign immediately

### PMax Cannibalizing High-ROAS Standard Shopping Campaigns
If Standard Shopping was previously achieving 400%+ ROAS and PMax is now at 200%:
- PMax absorbed the highest-converting (brand + high-intent) traffic
- Standard Shopping lost its best traffic and now looks worse
- Solution: pause Standard Shopping, add brand exclusions to PMax, run PMax alone, and evaluate true non-brand PMax performance over 30 days before concluding which is better

### Local Service Business PMax (Store Visit / Call Goals)
Local PMax has unique considerations:
- "Store visit" conversions are modeled estimates, not measured — treat with skepticism
- Call conversions are usually real — weight these more heavily
- Google Maps placement is critical for local — check if Maps is in the channel mix
- Location extensions must be linked to the campaign

### PMax Asset Group With All Videos Disapproved
If videos are disapproved, Google auto-generates a "video" from the static images:
- Auto-generated videos perform significantly worse than real video
- Flag this as a critical creative gap
- Recommend producing even a simple 15–30 second video (smartphone-quality is sufficient)
- Short-term: upload existing brand video to YouTube even if not specifically made for ads

### Segmenting PMax by Product Margin (Advanced Retail)
High-margin products deserve their own PMax asset group with a more aggressive tROAS target. Low-margin products should have a conservative target or be excluded.
- Create separate asset groups per product category or margin tier
- Set different ROAS targets per asset group (PMax allows this)
- Exclude unprofitable products from PMax entirely and run them in Standard Shopping with manual bids

---

## Quality Assurance

Before delivering:
- [ ] Learning period status assessed and noted at the top
- [ ] Brand exclusion status explicitly confirmed (yes/no), not assumed
- [ ] Channel distribution table completed with conversion data per channel
- [ ] Every asset group listed with ad strength status
- [ ] Audience signal quality rated for each asset group
- [ ] PMax vs. Standard Shopping conflict check completed
- [ ] Feed quality section present (eCommerce) or noted as N/A (lead gen)
- [ ] Conversion goal alignment verified
- [ ] "Do NOT change" list explicitly included in output
- [ ] Priority action list ordered: learning-safe fixes first, high-disruption changes last
- [ ] All recommendations include exact UI location or specific next step
