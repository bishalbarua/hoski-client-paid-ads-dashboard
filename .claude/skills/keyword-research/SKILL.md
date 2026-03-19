---
name: keyword-research
description: Build Google Ads keyword lists from scratch for a specific campaign or full account. Takes business context, services, geo, and budget — then generates seed keywords, expands by theme, classifies intent, assigns match types, organizes into ad groups, and produces a starter negative keyword list. Use this when launching new campaigns, adding new ad groups, or expanding into a new service line. Distinct from /search-terms (which reviews live search queries in an existing account) and /negative-keyword-analyzer (which cleans up existing search term exports).
---

# Keyword Research

Keyword research for Google Ads is not SEO keyword research. The goal is not volume. The goal is **finding the highest-intent, lowest-waste queries for a specific conversion event, organized into themes that allow tightly matched ad copy and landing pages.** This skill does that end-to-end: seeds → expansion → intent classification → match type assignment → ad group structure → starter negatives — ready to load into Google Ads.

## How This Skill Differs from Similar Skills

| | Keyword Research | Search Terms | Negative Keyword Analyzer | Ads Strategy Architect |
|---|---|---|---|---|
| **When to use** | Before or during campaign build | Weekly, on live account | One-time deep cleanup on live account | High-level strategy from URL |
| **Input** | Business context, services, geo | Search term export or API pull | Search term export | Business URL |
| **Output** | Keyword lists with match types, ad group structure, starter negatives | Four operational outputs (negatives, new KWs, promotions, segmentation signals) | Grouped negative recommendations | Campaign strategy, ad group topics, audience targets |
| **Granularity** | Granular: individual keywords, match types, ad group assignments | Operational: what to add/remove this week | Deep negative analysis | Strategic: campaign names, themes, structure |

---

## Core Philosophy

1. **Intent over volume.** A keyword with 50 monthly searches and clear transactional intent beats one with 5,000 searches and ambiguous intent every time.
2. **Tight themes = better Quality Score = lower CPC.** Organize ad groups so every keyword in the group shares the same landing page, the same ad copy angle, and the same searcher intent. One clear theme per ad group.
3. **Match type is a risk dial, not a quality dial.** Broad match gives Google more control. Exact gives you control. Neither is inherently better — it depends on how much conversion data you have and how much you trust Smart Bidding.
4. **Negatives from day one.** Every campaign should launch with a starter negative list. Waiting until you see bad search terms is burning money that you'll never get back.
5. **Build the minimum viable keyword list first.** 20 great keywords beats 200 mediocre ones. Start focused, expand with search term data after launch.

---

## Critical Context Gathering

### Required Context (Ask if not provided)

**1. Business and Services**
What does this business do, and what specific services are being advertised in this campaign? Be specific — "a law firm" is insufficient; "a personal injury law firm specializing in car accidents and slip-and-fall" changes everything.

Why it matters: Service specificity determines the seed keyword universe, intent signals, and what to negatively match.

**2. Geo Targeting**
Is this a local, regional, or national campaign? What city/metro/state?

Why it matters:
- Local service businesses get large volume from "[service] near me", "[service] [city]" — these become priority keywords
- National campaigns can't use "[city]" modifiers — structure is fundamentally different
- Local competitors are irrelevant for national campaigns and vice versa

**3. Campaign Goal (Conversion Type)**
What does a conversion look like? Phone call? Form submit? Purchase? Appointment booking?

Why it matters: Determines which intent signals are "good" (transactional, urgency) vs. waste (informational, DIY).

### Recommended Context

**4. Monthly Budget**
What's the monthly spend available for this campaign?

Why it matters: Budget directly determines match type strategy.
- Low (<$30/day): Exact + phrase only, very tight themes
- Medium ($30–$100/day): Phrase + selective broad, weekly monitoring
- High (>$100/day): Can start broad with Smart Bidding if conversion data exists

**5. Existing Keywords or Campaigns**
Are there already campaigns running for this client? What keywords are already active?

Why it matters: Prevents keyword cannibalization (two campaigns bidding against each other on the same terms).

**6. Competitor Names**
Key competitors in the market.

Why it matters: Determines whether to build a competitor campaign and which brand names to either target (competitor campaign) or negative (generic campaigns).

### Optional Context

**7. Brand Terms**
The client's own brand name and any common misspellings.

Why it matters: Ensures brand terms are never negated and helps scope a separate brand campaign if needed.

**8. Typical CPA Target or Max CPC**
What's the acceptable cost per lead or cost per acquisition?

Why it matters: Helps prioritize high-volume/competitive keywords (which cost more) vs. long-tail (which convert cheaper). Informs which ad groups to build first.

**9. Business Website URL**
If available, I'll scan it to extract service terminology, differentiators, and location signals.

---

## Input Format

**Minimum (manual research mode):**
- Business type and services
- Geo (city/region/national)
- Conversion goal

**Better:**
- All of the above + budget + any existing campaigns

**Best:**
- All of the above + business URL + competitor names + CPA target

**With API:** Provide client name or account ID. I'll run Keyword Planner queries to pull volume, competition, and bid estimates for generated keywords.

---

## Keyword Planner API Query

Use this to get volume, competition, and bid estimates for seed keywords. Run against the MCC or specific account.

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

keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
geo_service = client.get_service("GeoTargetConstantService")

# Build request
request = client.get_type("GenerateKeywordIdeasRequest")
request.customer_id = "[ACCOUNT_ID]"

# Language: English (1000)
request.language = "languageConstants/1000"

# Geo: Use geo target constant ID (US = 2840, Canada = 2124, UK = 2826)
# For specific city/metro, look up ID: https://developers.google.com/google-ads/api/data/geotargets
request.geo_target_constants.append("geoTargetConstants/[GEO_ID]")

request.include_adult_keywords = False
request.keyword_plan_network = (
    client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH
)

# Seed keywords — replace with your seeds
request.keyword_seed.keywords.extend([
    "[seed keyword 1]",
    "[seed keyword 2]",
    "[seed keyword 3]",
])

results = keyword_plan_idea_service.generate_keyword_ideas(request=request)

print(f"{'Keyword':<50} {'Avg Monthly':<15} {'Competition':<15} {'Low Bid':<12} {'High Bid':<12}")
print("-" * 104)

for idea in results:
    metrics = idea.keyword_idea_metrics
    low_bid = metrics.low_top_of_page_bid_micros / 1_000_000 if metrics.low_top_of_page_bid_micros else 0
    high_bid = metrics.high_top_of_page_bid_micros / 1_000_000 if metrics.high_top_of_page_bid_micros else 0
    print(
        f"{idea.text:<50} "
        f"{metrics.avg_monthly_searches:<15} "
        f"{metrics.competition.name:<15} "
        f"${low_bid:<11.2f} "
        f"${high_bid:<11.2f}"
    )
```

**Common geo target IDs:**
| Location | ID |
|---|---|
| United States | 2840 |
| Canada | 2124 |
| United Kingdom | 2826 |
| New York, NY | 1023191 |
| Los Angeles, CA | 1013962 |
| Chicago, IL | 1016367 |
| Houston, TX | 1014491 |
| Phoenix, AZ | 1023232 |
| Philadelphia, PA | 1025041 |
| Dallas, TX | 1014505 |
| Toronto, Canada | 1002214 |

---

## Analysis Framework

### Step 1: Seed Generation

Generate seeds from the business context using four angles:

**Angle 1: Core Service Terms**
The direct name of what the business offers.
- Examples: "family doctor", "chiropractor", "personal injury lawyer", "custom furniture", "plumber"
- Include common synonyms and alternate industry terms

**Angle 2: Problem/Symptom Terms**
What problem is the customer trying to solve? What do they search for before they know the solution?
- Examples: "back pain relief", "water heater not working", "hurt in car accident", "need a will"
- High intent, often overlooked, frequently less competitive

**Angle 3: Location + Service Combinations**
For local businesses: city, neighborhood, "near me" combinations.
- "[Service] [city]", "[service] near me", "[service] in [neighborhood]"
- "[city] [service]", "best [service] in [city]"

**Angle 4: Urgency + Qualifier Terms**
Modifiers that signal buying intent.
- Urgency: "emergency", "same day", "24 hour", "now", "today"
- Commercial: "affordable", "cost", "price", "cheap", "best", "top rated"
- Action: "book", "schedule", "call", "hire", "find", "get"

---

### Step 2: Intent Classification

Every keyword gets an intent label. Use this to decide include/exclude/separate.

| Intent Label | Signal Patterns | Action |
|---|---|---|
| **Transactional** | book, schedule, call, hire, get, buy, order, quote | ✅ Include — highest priority |
| **Commercial Investigation** | best, top rated, reviews, affordable, cost, price, compare | ✅ Include — strong candidates |
| **Local + Geo** | near me, [city], [neighborhood], in [location] | ✅ Include — priority for local businesses |
| **Problem/Symptom** | pain relief, not working, broken, need help, emergency | ✅ Include — often underused |
| **Navigational** | [brand] login, [brand] website, [brand] number | ⚠️ Brand campaign only |
| **Informational** | how to, what is, what causes, types of, history of | ❌ Exclude — negative these |
| **DIY** | how to fix, template, guide, free, do it yourself | ❌ Exclude — negative these |
| **Employment** | jobs, careers, salary, hiring, internship | ❌ Exclude — universal negatives |
| **Educational** | class, course, degree, certification, school, study | ❌ Exclude — negative if relevant |

---

### Step 3: Ad Group Organization

**Grouping principle:** Every keyword in an ad group must share:
1. The same searcher intent (what they want to accomplish)
2. The same logical landing page destination
3. The same ad copy theme (headline 1 can reference all keywords in the group)

**Grouping heuristics:**

| Split Trigger | Example | Why Split |
|---|---|---|
| Different service lines | "back pain chiropractor" vs. "car accident chiropractor" | Different landing pages, different ad copy |
| Different intent signals | "emergency plumber" vs. "plumber cost" | Urgency vs. price-shoppers — different offers in ad copy |
| Different geo modifiers | "dentist near me" vs. "dentist Chicago" | Can test different messages about proximity |
| Different qualification levels | "family lawyer" vs. "family lawyer free consultation" | Second group has a clear CTA signal — different description |
| Brand vs. generic | "Nike running shoes" vs. "running shoes" | Always separate — different CPCs, different strategies |

**Target ad group size:** 5–20 keywords per ad group. Under 5 = too narrow (unless exact match brand). Over 20 = themes are drifting, split further.

**Priority ad groups (build first):**
1. Highest-intent, highest-volume, core service terms
2. Problem/symptom + emergency terms (high urgency = high conversion rate)
3. Location + service combinations
4. Commercial investigation terms (reviews, best, affordable)
5. Competitor campaigns (separate campaign entirely)

---

### Step 4: Match Type Assignment

**The match type decision framework:**

| Scenario | Recommended Match Type | Reasoning |
|---|---|---|
| Launch, low budget (<$30/day) | Exact + Phrase | Control spend while gathering data |
| Launch, medium budget, new to Smart Bidding | Phrase + Broad | Allow some expansion, monitor weekly |
| Launch, high budget, tCPA with conversion history | Broad | Smart Bidding handles expansion, needs volume |
| Competitor keywords | Phrase | Catch brand name variations without over-expanding |
| Brand keywords | Exact | Control is paramount — own your brand |
| Long-tail / specific modifier | Exact | Already specific enough, no need for expansion |
| Core service (post-30-day data review) | Consider upgrading to Broad | Use search term data to decide |

**Match type per keyword format for output:**
```
[exact match keyword]
"phrase match keyword"
broad match keyword
```

---

### Step 5: Starter Negative Keyword List

Every new campaign should launch with these negatives already in place.

**Account-Level Negatives (Broad Match — Add to Account Negative List):**
```
jobs
careers
hiring
salary
resume
how to
tutorial
free
diy
do it yourself
course
training
school
degree
certification
```

**Campaign-Level Negatives (Phrase Match):**
Add competitors (if not running a competitor campaign), services you don't offer, and geographic exclusions:
```
"[competitor brand name]"
"[service you don't offer]"
"[cities outside geo target]"
```

**Ad Group-Level Negatives (Exact Match):**
Cross-negatives between ad groups to prevent cannibalization. When two ad groups could match the same query, add exact negatives to ensure each query routes to the right ad group.

Example: If ad group 1 = "emergency plumber" and ad group 2 = "plumber cost" — add `[emergency]` as an exact negative to ad group 2 so urgency queries always route to ad group 1.

---

## Output Format

```
# Keyword Research — [Campaign or Client Name]
**Date:** [Date]
**Campaign:** [Campaign Name]
**Geo:** [Targeting]
**Goal:** [Conversion type]
**Match Type Strategy:** [e.g., "Exact + Phrase for launch, review broad after 30 days"]

---

## Campaign Structure Overview

[2-3 sentences: how many ad groups, what's the priority build order, any notes on phasing]

| Priority | Ad Group Name | Theme | # Keywords | Match Types |
|---|---|---|---|---|
| 1 | [Name] | [e.g., Emergency Plumbing] | 12 | Exact + Phrase |
| 2 | [Name] | [e.g., Plumbing Cost/Price] | 8 | Phrase |
| 3 | [Name] | [e.g., Local Plumber Near Me] | 10 | Exact + Phrase |

---

## Ad Group 1: [Ad Group Name]

**Theme:** [One sentence describing what this group targets]
**Landing Page:** [Recommended page type or URL if known]
**Ad Copy Angle:** [What the headline should emphasize for this theme]

| Keyword | Match Type | Intent | Est. Volume | Notes |
|---|---|---|---|---|
| [emergency plumber] | Exact | Transactional | 1,200/mo | Core term |
| "emergency plumber near me" | Phrase | Transactional + Local | 880/mo | Geo-modified priority |
| 24 hour emergency plumber | Broad | Urgency | 320/mo | Requires Smart Bidding |

**Cross-negatives for this ad group:**
- [cost] — exact (route price queries to Cost ad group)
- [cheap] — exact (route to Cost ad group)

---

## Ad Group 2: [Ad Group Name]
[Same structure]

---

## [Continue for all ad groups]

---

## Starter Negative Keyword List

### Account Level (Broad Match)
```
jobs
careers
[full list]
```

### Campaign Level (Phrase Match)
```
"[competitor name]"
"[out-of-geo city]"
"[service not offered]"
```

### Ad Group Cross-Negatives
| Ad Group | Negative Keyword | Match Type | Reason |
|---|---|---|---|
| [Emergency] | [cost] | Exact | Route price queries to Cost ad group |
| [Cost/Price] | [emergency] | Exact | Route urgency queries to Emergency ad group |

---

## Keywords NOT Included (and Why)

| Keyword | Intent | Reason Excluded |
|---|---|---|
| how to fix [service] | Informational | DIY intent — add as negative |
| [service] school | Educational | Not a conversion query |
| [service] jobs | Employment | Universal negative |

---

## Build Order and Notes

**Build in this order:**
1. [Priority 1 ad group] — highest intent, most likely to convert immediately
2. [Priority 2 ad group]
3. [Priority 3 ad group]

**After 30 days:**
- [ ] Run /search-terms to review actual queries and find new negatives
- [ ] Identify any search terms ready to promote to exact match keywords
- [ ] Review which ad groups are generating conversions and expand those first
- [ ] Consider upgrading performing broad match keywords (if using Smart Bidding with tCPA)

**Keyword Planner Data Notes:**
[If API was used: note any keywords with unusually high/low volume, CPC outliers, or competitive gaps to exploit]
[If API was not used: "Volume estimates not available — use Google Ads Keyword Planner in UI to verify before launch"]
```

---

## Guardrails

❌ **NEVER** include brand terms in generic campaigns — brand terms must live in a dedicated brand campaign to protect Quality Score and control CPCs.

❌ **NEVER** put competitor keywords in the same campaign as generic terms — competitor campaigns need separate budgets, bidding strategies, and ad copy.

❌ **NEVER** produce a flat undifferentiated keyword list — every keyword must have an ad group assignment. A list without structure is not actionable.

❌ **NEVER** recommend broad match on a new account or campaign with fewer than 30 conversions — Smart Bidding needs conversion data to work. Without it, broad match = uncontrolled spend.

❌ **NEVER** skip the starter negative list — launching without negatives is burning money. Employment, DIY, and informational terms appear in almost every account from day one.

✅ **ALWAYS** check `clients/[client]/notes/client-info.md` first for brand terms, services offered, geo targeting, and any existing campaign notes — never build keywords without knowing what's already running.

✅ **ALWAYS** include cross-negatives when multiple ad groups could match the same query — cannibalization between your own ad groups wastes budget and hurts QS.

✅ **ALWAYS** state the match type rationale — not just what match type, but why given the budget and account maturity.

✅ **ALWAYS** include a "30 days after launch" review checklist so the keyword list doesn't sit static.

---

## Edge Cases

### Very Local / Single Location Business with Small Geo
If targeting a single city or small metro with a tight budget:
- Lean heavily on exact match — broad match in small geos can exhaust daily budget on one irrelevant query
- "Near me" terms often outperform "[city]" terms for service businesses — prioritize them
- Geo modifiers in keywords (e.g., "Chicago plumber") may be redundant if geo targeting is already set to that city — test both but don't double-bid without reason

### National Campaign With No Geo Signal
If the business targets the whole country (eCommerce, SaaS, national service):
- Remove all location-modified keywords from generic campaigns
- Build a separate "branded geo" ad group only if the brand name is city-specific (e.g., "Austin Mattress Company")
- Volume is much higher — budget allows broader match from launch IF conversion data exists

### Inherited Account With Existing Keywords
If there are already keywords running:
- Pull existing keyword list via API first (keyword_view query in CLAUDE.md) before generating new ones
- Flag duplicates and near-duplicates (same query, different match type in same ad group)
- Identify gaps (service lines with no keywords at all) vs. expansion opportunities (service lines with keywords but no long-tail coverage)

### Highly Competitive Vertical (Legal, Medical, Financial)
In verticals where CPCs are $20–$200+:
- Long-tail keyword depth is critical — "Houston car accident lawyer free consultation" at $15 CPC beats "car accident lawyer" at $80 CPC if intent is equal
- Problem/symptom keywords are often significantly cheaper than direct service terms
- Geo-specific terms reduce competition (fewer advertisers bid on "[suburb] + [service]" vs. "[city] + [service]")

### eCommerce (Product Keywords)
For product-focused campaigns:
- Separate branded product terms from generic category terms
- Include model numbers and SKUs as exact match in Shopping supplement
- "Best [product]" and "[product] reviews" are high-value for consideration stage — include in phrase
- Price-comparison terms ("[product] price", "[product] cheap") signal high purchase intent — include

### B2B / Long Sales Cycle
For B2B where conversions are demo requests, form fills, or calls:
- Informational terms are not always waste — "how to [solve problem]" can work if the LP is a landing page with a content offer and lead capture
- Job title modifiers ("for [industry]", "for [role]") reduce waste significantly
- "Free trial", "demo", "ROI calculator" terms are B2B transactional signals

---

## Quality Assurance

Before delivering:
- [ ] Every keyword has an ad group assignment — no orphaned keywords
- [ ] Every ad group has a clear single theme — can write one headline that applies to all keywords
- [ ] Brand terms are isolated to a separate brand campaign or flagged as absent
- [ ] Competitor keywords are in their own campaign (or explicitly excluded)
- [ ] Cross-negatives exist wherever two ad groups could match overlapping queries
- [ ] Starter negative list includes at minimum: employment, DIY/how-to, informational, out-of-geo
- [ ] Match type rationale given for each ad group, tied to budget and account maturity
- [ ] "Keywords NOT included and why" section captures intent classification decisions
- [ ] 30-day post-launch review checklist is present
- [ ] If API was used: volume and CPC data included; if not: explicitly noted
