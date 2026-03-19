---
name: negative-keyword-analyzer
description: Analyze Google Ads search terms and recommend negative keywords to reduce wasted spend. Triggers when user uploads search terms data, wants to find negative keywords, clean up search queries, reduce wasted ad spend, or improve campaign efficiency. Accepts CSV/Excel exports or pasted data. Groups recommendations by theme with match type suggestions and confidence levels. Includes guardrails to protect brand terms and legitimate traffic.
---

# Negative Keyword Analyzer

Identify wasted spend in search terms and generate actionable negative keyword recommendations with match types, confidence levels, and implementation-ready output.

## Critical Context Gathering

Before analyzing, I MUST understand your business to avoid blocking legitimate traffic:

### Required Context (Ask if not provided)

**1. Primary Service Keywords**
What service/product does THIS campaign advertise?
- Be specific: "laser liposuction" not "cosmetic surgery"
- Include synonyms: ["laser lipo", "smart lipo", "lipo laser"]
- This is what I'll PROTECT from false positives

**2. Brand Terms**
Your brand name and variations (NEVER negated):
- Company name, abbreviations, common misspellings
- Example: ["acme plumbing", "acme", "acmeplumbing"]

**3. All Services Offered**
Everything your business provides:
- Prevents negating services you actually sell
- Even if in different campaigns

**4. Adjacent Services (Other Campaigns)**
Services you offer but advertise in DIFFERENT campaigns:
- Helps identify cross-campaign cannibalization
- Example: This campaign is "laser lipo" but you also run "tummy tuck" campaigns

**5. Competitor Strategy**
- **Block**: Competitor traffic is unintentional waste → I'll flag for negation
- **Allow**: You're intentionally bidding on competitors → I won't suggest negating
- **Mixed**: Some allowed, some blocked → Specify which

### Optional Context (Improves Analysis)

- **Target CPA**: Helps assess cost-effectiveness of borderline terms
- **Expected Conversion Rate**: Enables CPC break-even analysis
- **Geographic Focus**: Identifies location mismatches

---

## Input Format

Upload CSV/Excel or paste data. I handle messy formats.

**Minimum Required Columns:**
- Search term (the query)
- At least ONE metric: clicks, cost, or conversions

**Ideal Columns:**
```
Search term | Impressions | Clicks | Cost | Conversions
```

**Data Quality Notes:**
- 30-90 days of data preferred
- Sort by cost (highest first) for impact-focused analysis
- Include 100-300 terms for meaningful patterns

---

## Analysis Framework

### Three Types of Waste

**1. Alignment Waste** (Intent mismatch - high confidence)
Search intent CANNOT be fulfilled by your offer:
- "free smart lipo" when service costs $5,000
- "laser lipo jobs" (employment, not customer)
- No conversion possible regardless of ad/landing page quality

**2. Audience Waste** (Wrong person - medium-high confidence)
Right service, wrong buyer:
- B2B software appearing for "personal use" searches
- Premium service appearing for "cheap" or "DIY" searches
- Structural mismatch between searcher and offer

**3. Performance Waste** (Economics don't work - requires data)
CAN convert but cost exceeds value:
- Term converts at 0.5% when you need 2% to hit CPA
- Requires 50+ clicks minimum to assess confidently

---

## Universal Exclusion Patterns

These indicate alignment waste across virtually ALL industries:

### Employment Intent (Account-Level, Broad Match)
**Pattern:** jobs, careers, hiring, salary, employment, resume, vacancy, recruitment, glassdoor, indeed
**Why:** User seeking work, not purchasing
**Match Type:** BROAD - catches all variations
**Confidence:** 0.95+

### Navigation/Login Intent (Account-Level, Phrase Match)
**Pattern:** login, sign in, account, portal, dashboard, password reset
**Why:** Existing customer accessing account, not new acquisition
**Match Type:** PHRASE
**Confidence:** 0.90+

### DIY/Educational Intent (Campaign-Level, Phrase Match)
**Pattern:** how to, tutorial, DIY, course, training, template, example, guide, wiki
**Why:** Seeking free information, not paid service
**Match Type:** PHRASE
**Level:** Campaign (some B2B businesses want awareness traffic)
**Confidence:** 0.85

### Document Seeking (Account-Level, Broad Match)
**Pattern:** pdf, template, worksheet, checklist, ppt, powerpoint
**Why:** Seeking downloadable resources, not services
**Match Type:** BROAD
**Confidence:** 0.90

### Wrong Industry (Account-Level, Broad Match)
**Pattern:** Varies by business - identify terms from completely unrelated verticals
**Why:** Fundamental category mismatch
**Match Type:** BROAD
**Confidence:** 0.95

---

## Protected Patterns (NEVER Auto-Negative)

### Commercial Investigation (High Intent Despite Question Format)
**Pattern:** best [service], top [service], [service] reviews, [service] near me, compare [service]
**Why:** Active purchase consideration - these convert well
**Action:** KEEP or MONITOR, never negative
**Confidence Override:** Always protect

### Comparison Shopping
**Pattern:** [service] vs [competitor], [your service] or [alternative], which [service]
**Why:** User deciding between options - high intent
**Action:** KEEP even if competitor mentioned
**Special Rule:** If term contains BOTH your service AND competitor with "vs/or/compare", protect it

### Brand + Service Combinations
**Pattern:** Any term containing brand name + service offered
**Why:** Branded intent is highest value traffic
**Action:** KEEP regardless of other signals
**Confidence Override:** Always protect

### Primary Service Variants
**Pattern:** Misspellings, word order variations of your core service
**Why:** Same intent as correctly spelled term
**Examples:** "lazer lipo" = "laser lipo", "lipo laser" = "laser lipo"
**Action:** Treat as primary service, protect from negation

---

## Match Type Decision Framework

| Scenario | Match Type | Level | Rationale |
|----------|------------|-------|-----------|
| Universal waste (jobs, DIY) | BROAD | Account | Catches all variations efficiently |
| Competitor brands | PHRASE | Campaign | Blocks "sono bello" but not "bello" |
| Specific location mismatch | PHRASE | Campaign | "chicago plumber" not "chicago style" |
| Ambiguous single term | EXACT | Ad Group | Surgical precision, minimizes risk |
| Wrong service modality | PHRASE | Campaign | Context preserved |

### Match Type Defaults
- **80% of negatives should be PHRASE** - balanced coverage
- **BROAD** only for universal categories (employment, DIY)
- **EXACT** for surgical precision on ambiguous terms

---

## Confidence Scoring

### High Confidence (0.85-1.0)
- Universal waste pattern (employment, DIY)
- Clear competitor brand (if blocking strategy)
- Explicit wrong industry
- **Action:** Recommend negation confidently

### Medium-High Confidence (0.70-0.85)
- Likely waste with some edge case risk
- Multiple negative signals present
- **Action:** Recommend with brief review note

### Medium Confidence (0.50-0.70)
- Context-dependent interpretation
- Single negative signal
- Limited data volume
- **Action:** Recommend as "consider" with rationale

### Low Confidence (<0.50)
- Conflicting signals
- Contains protected patterns
- Insufficient data
- **Action:** MONITOR, don't negative

---

## CPC Context Analysis

When target CPA and expected conversion rate are provided:

**Target CPC = Target CPA × Expected Conversion Rate**

| CPC vs Target | Assessment | Implication |
|---------------|------------|-------------|
| ≤50% of target | Cost-effective to test | Even low CVR might work |
| 50-100% of target | Near break-even | Monitor closely |
| >100% of target | Above break-even | Needs higher CVR to profit |

**Without targets, compare to account median:**
- Below 25th percentile → Low cost, worth testing
- Above 75th percentile → Premium pricing, higher bar

---

## Output Format

### Summary Statistics
```
Terms Analyzed: [X]
Negative Recommendations: [X] ($[X] flagged spend)
Monitor Recommendations: [X]
Keep Recommendations: [X]
```

### Recommendations Table

| Term | Clicks | Cost | Action | Category | Negative | Match | Level | Confidence | Rationale |
|------|--------|------|--------|----------|----------|-------|-------|------------|-----------|

### Grouped by Theme

**🔴 Employment Intent (X terms, $X spend)**
| Term | Negative | Match Type |
|------|----------|------------|

Copy-paste ready:
```
jobs
salary
careers
hiring
```

**🔴 DIY/Educational (X terms, $X spend)**
...

**🟠 Competitor Traffic (X terms, $X spend)**
...

**🟡 Geographic Mismatch (X terms, $X spend)**
...

**🟢 Protected - Commercial Investigation (X terms)**
These contain your service + buying signals. Keep them.
...

**⚪ Monitor - Insufficient Data (X terms)**
Flag for review after more volume.
...

---

## Guardrails (Hard Rules)

❌ **NEVER** suggest negating brand terms
❌ **NEVER** suggest negating services in `services_offered`
❌ **NEVER** auto-negative comparison queries ("[service] vs [competitor]")
❌ **NEVER** auto-negative commercial investigation ("best [service] near me")
❌ **NEVER** make recommendations without business context

✅ **ALWAYS** ask for context before analyzing
✅ **ALWAYS** protect primary service variants
✅ **ALWAYS** note confidence level
✅ **ALWAYS** provide rationale for each recommendation
✅ **ALWAYS** flag terms that need human review

---

## Edge Cases & Nuances

### Branded Competitor + Your Service
"smart lipo at sono bello"
- Contains competitor (Sono Bello)
- Contains your service (smart lipo)
- **Assessment:** User seeking competitor's offering specifically
- **Action:** NEGATIVE (even with competitor blocking off) - targeted competitor shopping

### Service Misspellings
"lazer lipo near me"
- Misspelled but same intent
- **Action:** KEEP - treat as primary service variant
- **Note:** Ensure primary service patterns include common misspellings

### Price Research Terms
"how much does laser lipo cost"
- Earlier funnel stage
- **Context-dependent:**
  - Tight budget, BOFU focus → Consider negating
  - Scale campaigns, broad match → May keep
  - Price is competitive differentiator → Keep
- **Default:** MONITOR with note about conversion data

### Foreign Language Variants
Same service in different language:
- If landing page is English-only → Language mismatch = alignment waste
- If business serves that language → Qualified traffic
- **Default:** Flag for human decision

### Seasonal Terms
"summer body laser lipo" analyzed in January:
- Low volume now, high in May-June
- **Action:** MONITOR, don't negative based on off-season data
- **Note:** Flag for seasonal bid adjustments

---

## Data Requirements

### Minimum for Pattern Analysis
```
clicks >= 1 OR impressions >= 20
```
Terms with clicks consumed budget. Terms with 20+ impressions but 0 clicks indicate CTR/intent issues.

### Minimum for Performance Conclusions
- **1-19 clicks:** Pattern matching only - no performance judgments
- **20-49 clicks:** Gray area - consider negating if 0 conversions AND other signals
- **50+ clicks:** Sufficient for performance-based decisions

### Statistical Confidence Note
At 50 clicks with 0 conversions:
- If true CVR were 3%, probability of 0 conversions is <22%
- If true CVR were 2%, probability of 0 conversions is <36%
- You likely have a problem, not bad luck

---

## Implementation Notes

### Copy-Paste Format
All negative lists formatted for direct import into Google Ads Editor:
```
keyword1
keyword2
keyword3
```

### Match Type Formatting
Google Ads format for bulk upload:
- Broad: `keyword`
- Phrase: `"keyword"`
- Exact: `[keyword]`

### Recommended Application Order
1. Add account-level negatives first (employment, DIY, wrong industry)
2. Add campaign-level negatives (competitors, adjacent services)
3. Add ad group-level negatives (specific mismatches)
4. Monitor flagged terms for 2 weeks before final decisions

---

## Quality Assurance

Before finalizing recommendations:
- [ ] Business context gathered and applied
- [ ] Brand terms excluded from all recommendations
- [ ] Services offered excluded from recommendations
- [ ] Primary service variants protected
- [ ] Commercial investigation terms protected
- [ ] Comparison queries protected
- [ ] Confidence levels assigned to all recommendations
- [ ] Rationale provided for each negative
- [ ] Match types logically assigned
- [ ] Output formatted for easy implementation
