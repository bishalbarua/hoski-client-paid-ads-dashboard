---
name: search-terms
description: Weekly Google Ads search terms review covering four jobs in one pass: negatives to add, new keywords to add, match type promotions (broad→exact/phrase), and ad group segmentation signals. Triggers when user wants to review search terms, do a weekly terms sweep, find wasted spend and missed opportunities in the same session. Accepts CSV/Excel exports, pasted data, or live Google Ads API pull. Outputs four ready-to-act sections with copy-paste keyword lists.
---

# Search Terms Weekly Review

The weekly search terms review is the highest-ROI 30 minutes in PPC management. Every week your broad and phrase match keywords are surfacing new queries — some are waste burning your budget, some are converting gold you haven't captured as exact match keywords, and some are growing fast enough to deserve their own ad group.

This skill runs all four jobs in one pass so nothing gets missed.

## What This Skill Does (And What It Doesn't)

**This skill covers:**
1. **Negatives to add** — irrelevant/wasteful terms grouped by theme
2. **New keyword opportunities** — converting or high-CTR terms not yet in your account as keywords
3. **Match type promotions** — broad/phrase-matched terms converting well → add as exact match keywords
4. **Ad group segmentation signals** — terms with enough volume to justify their own ad group

**This skill does NOT replace:**
- `/negative-keyword-analyzer` — use that for a deep one-time cleanup of a large historical export
- `/campaign-scaling-expert` — use that for campaign-level budget and bid strategy decisions

---

## Core Philosophy

1. **Every term is a vote.** High-impression terms with no clicks are telling you something is misaligned. High-click terms with no conversions are telling you something is broken. Listen before you act.
2. **Opportunities are as important as negatives.** Most PPC managers only use the search terms report for cleanup. The keyword opportunities section is often worth more than the negative savings.
3. **Match type promotion is systematic growth.** When a broad match term converts, adding it as an exact match keyword gives you full control over bid, ad copy, and landing page for that specific query.
4. **Context protects from disaster.** "Jobs" is waste for a plumber, gold for a staffing agency. Never analyze without business context.
5. **Weekly cadence = compound returns.** Catching 5 negatives a week is better than one 500-term cleanup per quarter. Catch opportunities early before competitors discover them.

---

## Critical Context Gathering

**Ask for the following before analyzing. If user provides data without context, ask these questions first.**

### Required (Cannot proceed without)

**1. What does this campaign sell?**
Be specific — not "legal services" but "personal injury attorney — car accidents."
- This determines what's waste vs. opportunity
- Include all services, synonyms, and common variations

**2. Brand name and variations**
All forms the brand appears in search terms:
- Company name, abbreviations, misspellings, domain name
- Example: ["Bishal Law", "bishallaw", "bishal attorney"]
- These are NEVER negated and ALWAYS protected as opportunities

**3. What services do you offer (all of them)?**
Even services in OTHER campaigns — prevents cross-campaign cannibalization mistakes.

### Recommended (Significantly improves analysis)

**4. Target CPA or ROAS**
Used to assess whether terms are economically viable even with low conversions.

**5. Current keyword list (or ad group structure)**
Required for opportunity mining — can't flag "not yet a keyword" without knowing what keywords you have.

**6. Competitor blocking strategy**
- **Block competitors:** Flag their brand terms as negatives
- **Allow competitors:** Skip competitor terms (you're bidding on them intentionally)

**7. Geographic focus**
Identifies location terms that don't match your service area.

### Optional (Nice to have)

**8. Time period of the data**
Defaults to assuming 7-day weekly pull if not specified.

**9. Industry vertical**
Helps apply the right protected pattern library.

---

## Input Format

Accept all of these — normalize before analyzing:

**Option A: Pasted data (most common)**
```
Search term | Impressions | Clicks | CTR | Avg CPC | Cost | Conversions
emergency plumber near me | 312 | 28 | 8.97% | $4.20 | $117.60 | 3
plumbing jobs | 89 | 12 | 13.48% | $3.15 | $37.80 | 0
```

**Option B: CSV/Excel upload**
Any column order, handle messy headers, ignore unknown columns.

**Option C: Google Ads API pull**
If user says "pull search terms for [client]", use the Google Ads API:
```python
query = """
    SELECT
        search_term_view.search_term,
        search_term_view.ad_group,
        campaign.name,
        ad_group.name,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.conversions_value,
        search_term_view.status
    FROM search_term_view
    WHERE segments.date DURING LAST_7_DAYS
    AND metrics.impressions > 0
    ORDER BY metrics.cost_micros DESC
"""
```

**Minimum Required Columns:**
- Search term (the query)
- At least one of: impressions, clicks, cost, conversions

**Ideal Columns:**
`Search term | Campaign | Ad Group | Impressions | Clicks | Cost | Conversions | Conv. Value`

**Data Volume Notes:**
- 7-day pull: 50–300 terms is typical for a healthy account
- Fewer than 20 terms: Data is thin — note low confidence throughout
- More than 500 terms: Prioritize by cost DESC, flag that it's a large pull

---

## Analysis Framework

Work through all four jobs in this order. Each term can appear in multiple jobs (e.g., a term can be both a match type promotion AND trigger an ad group signal).

---

### Job 1: Negatives to Add

**Step 1: Apply universal exclusion patterns (account-level)**

These apply across virtually every industry. Flag with confidence 0.95:

| Category | Keywords | Match Type | Level |
|----------|----------|------------|-------|
| Employment | jobs, careers, hiring, salary, resume, vacancy, glassdoor, indeed, job openings, work at | BROAD | Account |
| Login/Navigation | login, sign in, account, portal, dashboard, password, my account | PHRASE | Account |
| DIY/Educational | how to, tutorial, DIY, course, training, guide, template, example, step by step, learn | PHRASE | Campaign |
| Document Seeking | pdf, template, worksheet, checklist, ppt, powerpoint, spreadsheet | BROAD | Account |
| Wrong Industry | Identify based on business context | BROAD | Account |

**Step 2: Identify alignment waste (campaign-level)**

Intent cannot be fulfilled by this offer regardless of quality:
- "free [service]" when service is paid
- "[service] for [wrong audience]" (e.g., "wedding photography DIY")
- Wrong geography: service area is Chicago, term is "NYC [service]"
- Wrong modality: online service, term is "in person [service]"

**Step 3: Flag performance waste (data-dependent)**

Only flag if 50+ clicks AND 0 conversions AND cost > 2× target CPA:
- Do NOT negative terms with fewer than 50 clicks purely on performance
- DO flag for monitoring if 20–49 clicks with 0 conversions

**Confidence Tiers:**

| Confidence | Criteria | Recommendation |
|------------|----------|----------------|
| 0.90–1.0 | Universal pattern (employment, DIY) or clear misalignment | Add as negative |
| 0.75–0.89 | Strong waste signal, minor edge case risk | Recommend adding, note caveat |
| 0.55–0.74 | Context-dependent, single signal | Consider adding — review first |
| <0.55 | Conflicting signals or low data | Monitor only |

**Protected Patterns — NEVER negative:**
- Brand terms (any form)
- Commercial investigation: "best [service]", "[service] reviews", "[service] near me"
- Comparison shopping: "[service] vs [competitor]", "which [service]"
- Primary service variants and misspellings
- Seasonal terms analyzed in off-season (flag as monitor, not negative)

---

### Job 2: New Keyword Opportunities

Find terms that are NOT in the account as keywords but should be.

**Tier 1: High-intent converters** (add immediately)
- Conversions ≥ 1 AND term not already a keyword
- These are proven buyers — capture them with an exact match keyword for full control
- Flag match type: [exact match]

**Tier 2: High-CTR non-converters** (add and monitor)
- CTR ≥ 5% AND clicks ≥ 5 AND not yet a keyword
- High CTR signals strong relevance — conversion may be a landing page issue, not keyword quality
- Flag: Add as exact match, review landing page alignment

**Tier 3: High-impression, low-CTR** (investigate before adding)
- Impressions ≥ 100, CTR < 2%
- Could be low-intent broad match pollution OR a keyword with an ad copy/bid problem
- Flag: Investigate ad copy alignment before adding as keyword

**For each opportunity, note:**
- Suggested keyword text (use exact search term or clean variation)
- Suggested match type (default: exact match for proven converters, phrase for discovery)
- Suggested ad group placement (which existing ad group, or flag if new ad group needed)
- Why it's an opportunity

---

### Job 3: Match Type Promotions

Identify terms matching through BROAD or PHRASE that are converting well — these deserve an exact match keyword entry for bid control.

**Promotion Criteria:**
- Currently triggered via broad/phrase match (not already an exact match keyword)
- Conversions ≥ 2 in the period, OR clicks ≥ 15 with CTR > 8%
- Term represents the specific intent you want to target

**Why this matters:**
When a broad match keyword triggers a great search term, you cannot bid on that specific term independently. Adding it as [exact match] lets you:
1. Set a higher bid specifically for this proven query
2. Write a tighter ad for this exact intent
3. Measure its performance separately

**Output for each promotion:**
- Current keyword triggering it (broad/phrase)
- Search term to promote
- Recommended new keyword: `[search term as exact match]`
- Suggested bid relative to parent keyword: +20–40% (it's proven)

---

### Job 4: Ad Group Segmentation Signals

Identify terms that have enough volume/spend to justify breaking into their own ad group.

**Segmentation Triggers:**

| Signal | Threshold | Why |
|--------|-----------|-----|
| High impression volume | ≥200 impressions in 7 days | Term deserves dedicated ad copy |
| High spend share | Term = >15% of ad group spend | One term dominating means ad copy isn't optimized for it |
| Distinct intent | Term has clearly different user intent than ad group theme | Message match suffers in combined group |
| Conversion clustering | Term accounts for >30% of ad group conversions | Protect it with dedicated budget control |

**Output for each signal:**
- Term and current ad group
- Reason for segmentation
- Suggested new ad group name
- Keywords to move into new group
- Headline angle to write for the new ad group

---

## Output Format

### Header: Weekly Search Terms Summary

```
📋 SEARCH TERMS WEEKLY REVIEW
Period: [date range]
Client: [name] | Campaign(s): [names]
Terms Analyzed: [X] | Total Spend on Report: $[X]

┌─────────────────────┬──────┬───────────┐
│ Action              │ Count│ Est. Impact│
├─────────────────────┼──────┼───────────┤
│ Negatives to add    │  [X] │ $[X] saved│
│ New keywords to add │  [X] │ Opportunity│
│ Match type promotes │  [X] │ Bid control│
│ Ad group signals    │  [X] │ Structure  │
└─────────────────────┴──────┴───────────┘
```

---

### Section 1: Negatives to Add

**🔴 High Confidence — Add This Week**

Grouped by theme with copy-paste ready lists:

```
[Theme Name] — Account Level, Broad Match
jobs
salary
careers
hiring
```

Full table:
| Term | Impressions | Clicks | Cost | Category | Match Type | Level | Confidence |
|------|-------------|--------|------|----------|------------|-------|------------|

**🟠 Medium Confidence — Review Before Adding**

| Term | Impressions | Clicks | Cost | Why Flagged | Concern | Recommendation |
|------|-------------|--------|------|-------------|---------|----------------|

**⚪ Monitor (Not Enough Data)**
List terms with the threshold they need to hit before deciding.

---

### Section 2: New Keyword Opportunities

**Tier 1: Add Immediately (Proven Converters)**

| Search Term | Clicks | Conv | Cost/Conv | Add As | Ad Group | Priority |
|-------------|--------|------|-----------|--------|----------|----------|

**Tier 2: Add and Monitor (High CTR)**

| Search Term | Impressions | Clicks | CTR | Add As | Note |
|-------------|-------------|--------|-----|--------|------|

**Tier 3: Investigate First**

| Search Term | Impressions | CTR | Issue | Action |
|-------------|-------------|-----|-------|--------|

---

### Section 3: Match Type Promotions

| Search Term | Triggered By | Conv | Promote To | Suggested Bid Delta | Ad Group |
|-------------|--------------|------|------------|--------------------| ---------|

Implementation note: Add the exact match keyword alongside the broad — don't remove the broad until the exact has 30+ days of data.

---

### Section 4: Ad Group Segmentation Signals

For each signal:
```
⚡ SEGMENTATION SIGNAL
Term: [search term]
Current Ad Group: [name]
Trigger: [reason]
Recommended: Create "[suggested ad group name]"
Keywords to move: [list]
Headline angle: [suggested headline for new ad group]
```

---

### Footer: Implementation Checklist

```
THIS WEEK:
☐ Add [X] negatives (high confidence) — [link to copy-paste list above]
☐ Add [X] new keywords — [Tier 1 list]
☐ Promote [X] terms to exact match

NEXT REVIEW:
☐ Check performance of [X] new keywords after 2 weeks
☐ Monitor [X] flagged terms — decide by [date + 2 weeks]
☐ Evaluate [X] segmentation signals after 30 days data
```

---

## Guardrails

❌ **NEVER** suggest negating brand terms — this kills branded search performance
❌ **NEVER** flag a term as waste without understanding the business context first
❌ **NEVER** suggest negating commercial investigation terms ("best X", "X near me", "X reviews")
❌ **NEVER** add a term as a keyword if it's already an exact match keyword in the account
❌ **NEVER** promote to exact match by removing the broad — run them in parallel first
❌ **NEVER** make performance-based negative recommendations on fewer than 50 clicks
❌ **NEVER** treat a comparison query ("[service] vs [competitor]") as waste

✅ **ALWAYS** gather business context before analyzing — no exceptions
✅ **ALWAYS** show the dollar amount at stake for negatives (makes prioritization easy)
✅ **ALWAYS** separate high-confidence from medium-confidence negatives
✅ **ALWAYS** format copy-paste ready keyword lists — don't make the manager reformat
✅ **ALWAYS** note when data volume is too low to make confident recommendations
✅ **ALWAYS** flag if a converting term should be protected even if it looks odd

---

## Edge Cases

### Very Small Accounts (<100 terms/week)
- Lower confidence thresholds for opportunities: CTR ≥ 4%, clicks ≥ 3 for Tier 2
- Note data thinness in summary
- Still apply all guardrails — small accounts are more sensitive to negative mistakes

### Brand Campaign Search Terms
- Most terms should be brand variations — protected automatically
- Flag non-brand terms appearing in brand campaign (possible BMM pollution)
- Segmentation: non-brand terms in brand campaign are misrouted — flag as structural issue

### Very High Volume Accounts (500+ terms/week)
- Analyze top 200 by cost first
- Group and summarize lower-cost terms by theme pattern
- Note in summary that full analysis covers top [X]% of spend

### Terms with 0 Impressions / Filtered Out by Privacy
- Google hides terms with very low volume for privacy
- These cannot be actioned — note this in summary if data appears to have gaps

### eCommerce vs Lead Gen Distinction
- **Lead gen:** 1 conversion = high value, even 1 converting term is worth promoting
- **eCommerce:** High-volume, lower CPC — set higher click thresholds before promoting

### "Price" and "Cost" Terms
Example: "how much does [service] cost"
- Default: KEEP — price-researching users often convert, especially if pricing is competitive
- Exception: Extremely premium product where price-shoppers don't convert → Monitor first
- Never auto-negative without data

### Foreign Language Terms
- If landing page is English-only → alignment waste → flag as negative
- If business serves that language market → opportunity → flag for human decision
- Default without context: FLAG, do not auto-negative

---

## Quality Assurance

Before delivering:
- [ ] Business context collected and applied throughout
- [ ] Brand terms explicitly protected in all four sections
- [ ] Services offered cross-checked against negatives (no false positives)
- [ ] Commercial investigation terms protected
- [ ] Confidence levels assigned to every negative recommendation
- [ ] Copy-paste negative lists formatted correctly (one term per line)
- [ ] New keyword recommendations don't duplicate existing keywords
- [ ] Match type promotion notes parallel-run instruction included
- [ ] Implementation checklist is actionable and dated
- [ ] Summary table accurately reflects all four sections
