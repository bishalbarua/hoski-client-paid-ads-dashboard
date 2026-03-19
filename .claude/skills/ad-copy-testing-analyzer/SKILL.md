---
name: ad-copy-testing-analyzer
description: Analyze RSA (Responsive Search Ad) asset performance for an account or specific campaigns. Pulls asset-level BEST/GOOD/LOW/LEARNING labels via API, categorizes each asset by copy angle type, identifies patterns in winning vs. losing copy, flags structural issues (over-pinning, low variety, poor ad strength), and delivers specific swap recommendations with replacement copy. Triggers when user wants to know which ad copy is working, what headlines to replace, or how to improve RSA performance. Distinct from /rsa-headline-generator (which creates new ads) — this analyzes what's already running.
---

# Ad Copy Testing Analyzer

Most RSA audits stop at "this headline is LOW, change it." That's useless. This skill goes deeper: it finds *why* certain assets underperform by categorizing every asset by its copy angle (keyword insertion, benefit, proof, urgency, CTA, etc.) and looking for patterns. If your LOW-performing assets are all CTAs and your BEST assets are all proof points — that's a strategic insight, not a list of headlines to rewrite. This skill delivers that pattern analysis along with specific, character-counted replacement copy ready to load into Google Ads.

## How This Skill Differs from Similar Skills

| | Ad Copy Testing Analyzer | RSA Headline Generator | Weekly Check | PPC Account Health Check |
|---|---|---|---|---|
| **When to use** | After ads have run 30+ days and have data | When building a new ad from scratch | Every Monday — operational sweep | One-time strategic audit |
| **Input** | Live RSA asset performance data (API or pasted) | Business context, proof points | Account performance data | Campaign-level metrics |
| **Output** | Asset scorecard, pattern analysis, specific swaps with replacement copy | 15 headlines + 4 descriptions | Status flags + weekly action list | Health score + fix list |
| **Ad strength focus** | Deep: individual asset labels, variety, pinning, angle distribution | N/A (creates assets) | Surface: any "Poor" ads flagged | Surface: ad strength mentioned if critical |

---

## Core Philosophy

1. **A LOW label is a symptom, not a diagnosis.** Before recommending changes, understand *why* it's LOW — is it a copy problem, a volume problem, or a structural problem? Each has a different fix.
2. **Patterns beat individual assets.** One BEST headline is a data point. Five BEST headlines all using proof points is a strategy. Find the pattern, replicate it.
3. **Protect BEST assets like they're revenue.** BEST-labeled assets are Google's signal that this copy resonates. Never remove a BEST asset without replacing it with the same angle, tested against a variation.
4. **Pinning is the enemy of learning.** Pins prevent Google from testing combinations. Every pinned position is a test you're not running. Flag aggressively.
5. **Low data is not low performance.** A LEARNING label on a campaign with 300 impressions is not a problem — it's a waiting room. Don't optimize what hasn't been tested.

---

## Critical Context Gathering

### Required Context (Ask if not provided)

**1. Client Name or Account ID**
Which account to pull asset data from. Look up ID in CLAUDE.md if client name provided.

**2. Scope**
Audit the full account, a specific campaign, or a specific ad group?
- Full account: good for finding cross-campaign patterns
- Campaign level: good for focused optimization before a budget increase
- Ad group level: good for a specific underperforming ad

### Recommended Context

**3. Business and Service Context**
What does this business sell, and who is the target customer?

Why it matters: Copy angle classification requires understanding what counts as a "benefit" vs. a "differentiator" for *this* business. "Same day service" is urgency for a plumber but a differentiator for a law firm.

**4. Time Period**
Default: last 30 days. Longer periods give more data for LEARNING assets; shorter periods are more current.

**5. Any Known Issues**
Is there a specific problem triggering this audit?
- "Ad strength is Poor on all ads"
- "CTR dropped last month"
- "Client says the ads sound generic"

### Optional Context

**6. Current CPA or CTR Targets**
If available, helps frame whether the copy issues are directly impacting performance or are latent issues to fix proactively.

**7. Competitor Ad Copy**
If you've seen competitors' ads (from Auction Insights or manual search), knowing their messaging helps identify differentiation gaps in the current copy.

---

## Input Format

**API pull (preferred):** Client name or account ID — I'll run both the asset view query and the ad-level query.

**Manual paste:** Export from Google Ads UI → Ads → Columns → Add "Asset details" → copy the asset performance table. Include asset text, field type (headline/description), and performance label.

**Minimum viable:** A list of headlines and descriptions with their BEST/GOOD/LOW/LEARNING labels. Even without impression data, angle analysis and structural checks are possible.

---

## API Queries

### Query 1: Asset-Level Performance

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
        ad_group.name,
        ad_group_ad.ad.id,
        ad_group_ad.ad_strength,
        ad_group_ad_asset_view.field_type,
        ad_group_ad_asset_view.performance_label,
        ad_group_ad_asset_view.pinned_field,
        ad_group_ad_asset_view.enabled,
        asset.text_asset.text,
        metrics.impressions,
        metrics.clicks
    FROM ad_group_ad_asset_view
    WHERE segments.date DURING LAST_30_DAYS
    AND ad_group_ad_asset_view.enabled = TRUE
    AND ad_group_ad.status = 'ENABLED'
    AND ad_group.status = 'ENABLED'
    AND campaign.status = 'ENABLED'
    ORDER BY campaign.name, ad_group.name
"""

response = ga_service.search(customer_id=customer_id, query=query)

for row in response:
    print(f"Campaign: {row.campaign.name}")
    print(f"  Ad Group: {row.ad_group.name}")
    print(f"  Ad Strength: {row.ad_group_ad.ad_strength.name}")
    print(f"  Field Type: {row.ad_group_ad_asset_view.field_type.name}")
    print(f"  Performance: {row.ad_group_ad_asset_view.performance_label.name}")
    print(f"  Pinned: {row.ad_group_ad_asset_view.pinned_field.name}")
    print(f"  Text: {asset.text_asset.text}")
    print(f"  Impressions: {row.metrics.impressions}")
    print(f"  Clicks: {row.metrics.clicks}")
    print()
```

### Query 2: Ad-Level Summary (Ad Strength + Approval Status)

```python
query = """
    SELECT
        campaign.name,
        ad_group.name,
        ad_group_ad.ad.id,
        ad_group_ad.ad.name,
        ad_group_ad.ad_strength,
        ad_group_ad.policy_summary.approval_status,
        ad_group_ad.status,
        metrics.impressions,
        metrics.clicks,
        metrics.ctr,
        metrics.conversions,
        metrics.cost_micros,
        metrics.cost_per_conversion
    FROM ad_group_ad
    WHERE segments.date DURING LAST_30_DAYS
    AND ad_group_ad.status = 'ENABLED'
    AND ad_group_ad.ad.type = 'RESPONSIVE_SEARCH_AD'
    AND campaign.status = 'ENABLED'
    ORDER BY metrics.impressions DESC
"""
```

---

## Analysis Framework

### Step 1: Data Quality Gate

Before analyzing, determine if there's enough data to trust the labels.

| Condition | Assessment | Action |
|---|---|---|
| Ad total impressions < 1,000 (30 days) | Insufficient data | Flag all labels as unreliable; don't recommend changes based on labels |
| Ad total impressions 1,000–5,000 | Low data | Caveated analysis; focus on structural issues over label-based swaps |
| Ad total impressions > 5,000 | Sufficient data | Full analysis, labels are meaningful |
| >60% of assets in LEARNING | Volume problem, not copy | Don't swap assets — increase budget/bids or wait |
| All assets in LEARNING | Campaign is new or very low traffic | Skip label analysis; only do structural checks |

---

### Step 2: Copy Angle Classification

Classify every asset (headline and description) into a primary angle. One asset = one primary angle.

| Angle | Definition | Example Signals |
|---|---|---|
| **Keyword** | Contains or closely mirrors the target keyword | Service name in headline, exact match to ad group theme |
| **Benefit** | Outcome or result the customer gets | "Feel Better in 3 Visits", "Get Your Refund Faster", "Save 2 Hours a Week" |
| **Proof** | Evidence of quality, trust, or scale | "500+ 5-Star Reviews", "20 Years of Experience", "Google Guaranteed" |
| **CTA** | Direct call to action | "Call Now", "Book a Free Consultation", "Get a Quote Today" |
| **Differentiator** | What sets this business apart from competitors | "Only Board-Certified in [City]", "No Hidden Fees — Ever" |
| **Urgency** | Time pressure or scarcity | "Same Day Appointments", "Limited Spots Available", "Emergency Service 24/7" |
| **Price/Value** | Cost signals or value framing | "Starting at $49", "Free First Visit", "Affordable Plans Available" |
| **Trust/Credential** | Certification, licensing, affiliation | "Licensed & Insured", "BBB Accredited", "Award-Winning Practice" |
| **Location** | Geo signal | "Serving [City] Since 2005", "Your Local [Service] Experts", "Near [Landmark]" |

If an asset spans two angles (e.g., "500 Happy Customers — Call Today" = Proof + CTA), assign the **dominant** angle and note the secondary.

---

### Step 3: Performance Label Interpretation

| Label | Meaning | Action |
|---|---|---|
| **BEST** | Google shows this most often; it outperforms alternatives | Protect — do not remove. Identify angle. Replicate in other ads. |
| **GOOD** | Solid performer, rotated regularly | Keep. Note the angle for reference. |
| **LOW** | Underperforms other assets in the same ad | Remove and replace — but analyze angle first. Is the whole angle category losing, or just this execution? |
| **LEARNING** | Not enough data to rate | Do not remove — wait. Flag if >60% of assets are in LEARNING. |
| **PENDING** | Awaiting review | Wait for label assignment. |
| **UNAVAILABLE** | Not enough impressions to rate (often <10) | Treat as LEARNING. |

---

### Step 4: Pattern Analysis

After classifying all assets, build the angle distribution table:

**Per ad group:**

| Angle | BEST | GOOD | LOW | LEARNING | Total | Signal |
|---|---|---|---|---|---|---|
| Benefit | 2 | 1 | 0 | 1 | 4 | ✅ Strong — this angle wins |
| Proof | 1 | 2 | 0 | 0 | 3 | ✅ Solid |
| Keyword | 0 | 1 | 1 | 0 | 2 | ⚠️ Mixed — keyword angle may be too generic |
| CTA | 0 | 0 | 2 | 0 | 2 | 🔴 Failing — CTAs consistently LOW |
| Urgency | 0 | 0 | 0 | 1 | 1 | ⚠️ Learning — not enough data |

**Pattern insights to extract:**
- If a specific angle has 2+ LOW and 0 BEST → that angle is consistently underperforming for this audience. Replace with the winning angle type.
- If BEST assets are concentrated in 1-2 angles → double down on those angles in new assets
- If no angle has a BEST → copy may be too similar across all assets (low variety score)
- If Keyword angle is LOW → the headline may be too generic or keyword-stuffed; differentiate with benefit or proof

---

### Step 5: Structural Issue Audit

Beyond individual asset labels, check for structural problems that limit testing quality.

**Issue 1: Over-Pinning**

| Pins Found | Assessment |
|---|---|
| 0 pins | ✅ Full testing flexibility |
| 1 pin (e.g., brand in H1) | ⚠️ Minor restriction — usually acceptable |
| 2+ pins across H1/H2/H3 | 🔴 Severely limits Google's testing ability — most combinations are locked |
| Descriptions both pinned | 🔴 No description testing at all |

**Issue 2: Asset Variety**

| Unique angles present | Assessment |
|---|---|
| 5+ distinct angles | ✅ Good variety |
| 3–4 distinct angles | ⚠️ Moderate variety — room to expand |
| 1–2 distinct angles | 🔴 Low variety — Google has little to test; ad strength will suffer |

**Issue 3: Ad Strength**

| Ad Strength | Meaning | Action |
|---|---|---|
| Excellent | 15 headlines, 4 descriptions, high variety | ✅ No structural changes needed |
| Good | Minor gaps | ⚠️ Add 1-2 assets in underrepresented angles |
| Average | Missing headlines or variety | 🔴 Add assets — especially in angles you don't currently have |
| Poor | Very few assets or highly repetitive | 🔴 Priority fix — add variety across multiple angle types |

**Issue 4: Headline Count**

Google allows up to 15 headlines and 4 descriptions. Fewer = less testing.

| Headlines | Descriptions | Assessment |
|---|---|---|
| 15 | 4 | ✅ Maximum testing surface |
| 12–14 | 4 | ⚠️ Add 1-3 more headlines |
| <12 | <4 | 🔴 Significant missed testing — fill to max |

---

### Step 6: Swap Recommendations

For each LOW-performing asset:
1. State what angle it was trying to use
2. State why it likely failed (too generic, wrong audience signal, competing with a better BEST asset in same angle)
3. Write a specific replacement in the winning angle(s) with character count

**Replacement logic:**
- If the LOW asset is the only one in its angle category → the angle itself may be right but the execution is weak. Write a better version of the same angle.
- If the LOW asset's angle category consistently shows LOW → replace with a different angle entirely (use the winning angle pattern instead).
- Replacement headlines: aim for 25–30 characters to enable full display on mobile; flag if under 20 or over 30.

---

## Output Format

```
# Ad Copy Testing Analysis — [Client Name]
**Account ID:** [ID]
**Scope:** [Full account / Campaign: X / Ad Group: Y]
**Period:** Last 30 Days
**Date:** [Date]

---

## Quick Summary

| Metric | Value |
|---|---|
| Total RSAs analyzed | [N] |
| Ads with Excellent/Good strength | [N] ([%]) |
| Ads with Average/Poor strength | [N] ([%]) |
| Total assets analyzed | [N] |
| BEST assets | [N] ([%]) |
| GOOD assets | [N] ([%]) |
| LOW assets | [N] ([%]) |
| LEARNING assets | [N] ([%]) |
| Data quality | ✅ Sufficient / ⚠️ Low / 🔴 Insufficient |

---

## Winning Copy Patterns

[2-3 sentences identifying the dominant pattern in BEST assets across the account]

| Angle | Win Rate (BEST/Total) | Interpretation |
|---|---|---|
| Benefit | 3/4 (75%) | ✅ Strongest angle — lead with outcomes |
| Proof | 2/3 (67%) | ✅ Strong — numbers and credentials resonate |
| CTA | 0/3 (0%) | 🔴 CTAs consistently underperform — likely too generic |
| Keyword | 1/3 (33%) | ⚠️ Mixed — keyword headlines need differentiation |

---

## Ad-by-Ad Breakdown

### Campaign: [Campaign Name] → Ad Group: [Ad Group Name]

**Ad Strength:** [Poor / Average / Good / Excellent]
**Total Impressions (30d):** [N] — [Sufficient / Low / Insufficient for analysis]

**Structural Issues:**
- [e.g., "2 pins detected in H1 and H2 — limits testing combinations"]
- [e.g., "Only 11 headlines — add 4 more to reach maximum testing surface"]
- [e.g., "No Urgency or Location angles present — consider adding"]

**Asset Scorecard:**

| Asset | Type | Angle | Label | Impressions | Notes |
|---|---|---|---|---|---|
| "Get Back Pain Relief Today" | H | Benefit | BEST | 2,847 | ✅ Protect — outcome-focused wins |
| "Voted #1 Chiropractor in Austin" | H | Proof | BEST | 2,341 | ✅ Protect — social proof with location |
| "Schedule Your Appointment" | H | CTA | LOW | 891 | 🔴 Generic CTA — no urgency or value |
| "Synergy Spine & Nerve Center" | H | Keyword | GOOD | 1,204 | Brand anchor — keep |
| "Call Us Today" | D | CTA | LOW | 445 | 🔴 Weakest description — pure CTA, no value |

---

## Swap Recommendations

### Remove → Replace

| Remove | Angle | Why Failing | Replacement | Chars | New Angle |
|---|---|---|---|---|---|
| "Schedule Your Appointment" | CTA | Generic — no differentiation from any other CTA; CTA angle is 0% BEST in this account | "Same-Day Appointments Available" | 32 | Urgency + CTA |
| "Call Us Today" | CTA | Weak, no value offer; description slot wasted on a pure CTA | "Most patients see results in 3 visits. Call now." | 49 | Benefit + CTA |
| [Asset] | [Angle] | [Reason] | [New copy] | [N] | [New angle] |

---

## What to Protect (Do Not Remove)

| Asset | Label | Angle | Why |
|---|---|---|---|
| "Get Back Pain Relief Today" | BEST | Benefit | Top-performing headline — outcome-focused message is resonating |
| "Voted #1 Chiropractor in Austin" | BEST | Proof + Location | Proof + geo combo performing well — replicate this pattern |

---

## Missing Angles to Add

Based on winning patterns and current gaps:

| Angle | Priority | Suggested Copy | Chars |
|---|---|---|---|
| Price/Value | High | "Free Consultation — No Commitment" | 35 |
| Trust/Credential | Medium | "Licensed Chiropractor — 15 Years in Austin" | 43 |
| Differentiator | Medium | "No Referral Needed — Walk-Ins Welcome" | 37 |

---

## Cross-Campaign Patterns (Account-Level Insight)

[If multiple campaigns analyzed: 2-3 sentences on what patterns are consistent across campaigns — e.g., "Benefit and Proof angles are the strongest performers across all 3 campaigns. CTAs are LOW everywhere — the account's audience responds to outcome messaging, not action commands."]

---

## Implementation Checklist

**This week:**
- [ ] Remove [specific LOW asset] from [Ad Group] → replace with [specific copy]
- [ ] Remove [specific LOW asset] from [Ad Group] → replace with [specific copy]
- [ ] Add missing angle headlines: [list]

**Structural fixes:**
- [ ] Unpin [position] in [Ad Group] to restore testing flexibility
- [ ] Add [N] headlines to [Ad Group] to reach 15

**After 30 days:**
- [ ] Re-run /ad-copy-testing-analyzer to see if new assets earn BEST or GOOD labels
- [ ] If new benefit/proof angles earn BEST, write 2-3 more variations of the winning formula
- [ ] If replacement CTAs are still LOW, consider whether CTA belongs in descriptions only
```

---

## Guardrails

❌ **NEVER** recommend removing a BEST-labeled asset under any circumstances — not for "freshness," not because it sounds repetitive to you, not because the client wants a refresh. BEST assets are data-validated winners.

❌ **NEVER** recommend changes on ads with fewer than 1,000 total impressions in the period — labels are statistically unreliable and changes may hurt a campaign that just needs more time.

❌ **NEVER** treat a LEARNING label as a problem that needs fixing — it means the asset hasn't been shown enough to rate. Removing LEARNING assets before they're evaluated wastes the test.

❌ **NEVER** recommend removing all CTA-angled assets just because the angle performs poorly — Google requires a functional CTA in descriptions. Flag underperforming CTAs for replacement with stronger versions, not elimination.

✅ **ALWAYS** distinguish between "this specific copy is weak" and "this entire angle type fails for this audience" — the fix is different.

✅ **ALWAYS** check data quality first — flag the analysis as low-confidence if total ad impressions are under 1,000.

✅ **ALWAYS** provide character counts for every suggested replacement headline and description.

✅ **ALWAYS** include a "What to Protect" section — recommendations to change things are only useful alongside explicit guardrails on what not to touch.

---

## Edge Cases

### All Assets in LEARNING (New or Low-Traffic Campaign)
Don't analyze labels — there's nothing to analyze. Instead:
- Do a structural audit only: count headlines/descriptions, check pins, check angle variety
- Flag if headline count is below 15 or descriptions below 4
- Recommend returning for label analysis after 30 days with sufficient budget to generate 5,000+ impressions

### Only One RSA Per Ad Group
If there's only one active RSA (Google's minimum), the labels reflect that ad's performance in isolation — there's no comparison set, so BEST/LOW ratings are relative to nothing meaningful. Flag this and recommend adding a second RSA with a different copy approach (different angle distribution) to create a real test.

### All Headlines Are Keyword-Insertion Variants
A common inherited account problem: all 15 headlines are variations of the target keyword with no benefits, proof, or CTAs. This shows as low ad strength + all LEARNING or all GOOD (no strong differentiation to rank BEST).
- Flag as "angle collapse" — no variety for Google to test
- Recommend replacing 6-8 keyword headlines with benefit, proof, and differentiator angles
- Keep 2-3 keyword headlines as anchor

### Client Objects to Removing a "LOW" Asset (It's Their Favorite)
If the client wants to keep copy they like even though it's LOW-labeled:
- Don't argue — note it as a protected asset in the analysis
- Suggest adding new assets alongside it rather than removing it
- Reframe: "We'll keep this headline and add 2 new ones to give Google more to work with"

### Pinning Required for Compliance (Legal, Medical, Financial)
Some regulated industries require specific disclaimers or required language in H1 or D1 by law or platform policy. In these cases:
- Accept the pin as a hard constraint
- Flag the reduced testing surface but don't recommend unpinning
- Focus optimization on the unpinned positions only

### High-Performing Ad With Poor Strength Score
Ad strength and actual performance don't always align — Google can show a "Poor" strength ad that converts excellently. In this case:
- Prioritize conversion data over ad strength
- Don't add assets just to improve the strength score if it means diluting a high-converting ad
- Note the discrepancy: "Ad strength is Poor but CPA is [X] vs. account average [Y] — optimize with care"

---

## Quality Assurance

Before delivering:
- [ ] Data quality gate confirmed — labeled with impression volume and confidence level
- [ ] Every asset classified with a copy angle
- [ ] Pattern analysis table built — angle win rates calculated
- [ ] Every LOW asset has a specific replacement with character count and new angle label
- [ ] BEST assets explicitly listed in "What to Protect" — not touched
- [ ] Structural issues checked: pin count, headline count, angle variety, ad strength
- [ ] No recommendations made on LEARNING assets (only structural checks)
- [ ] Implementation checklist is copy-paste actionable with exact ad group names
- [ ] If multiple campaigns: cross-account patterns synthesized in a summary statement
