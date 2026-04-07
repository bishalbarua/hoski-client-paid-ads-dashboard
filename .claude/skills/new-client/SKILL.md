---
name: new-client
description: Full new client onboarding workflow. Gathers intake information through structured questions, checks for and audits any existing Google Ads account, creates the client workspace (folder + populated client-info.md), generates a pre-launch checklist, and produces a first 30-day plan. Triggers when user says "new client", "onboard [client]", "set up [client]", or "I have a new client". Handles both brand-new accounts and inherited existing accounts. Entry point that feeds into /ads-strategy-architect for campaign strategy.
---

# New Client Onboarding

Every client relationship is defined in the first 30 days. Sloppy onboarding — missing targets, no conversion tracking, unclear goals — creates compounding problems that are hard to undo. This skill runs the full intake so nothing gets missed.

## What This Skill Does

1. **Intake** — gather everything needed to run this account well
2. **Existing account check** — if they have a Google Ads history, pull and audit it
3. **Create workspace** — folder structure + fully populated `client-info.md`
4. **Pre-launch checklist** — what must be done before any campaign goes live
5. **First 30-day plan** — what happens in month one
6. **Kickoff note** — what to send the client to set expectations

## How It Relates to Other Skills

```
/new-client          → Intake, setup, and documentation
   ↓
/ads-strategy-architect  → Build the campaign strategy (run after new-client)
   ↓
/weekly-check        → Ongoing weekly management once live
/search-terms        → Weekly search terms sweep
/monthly-report      → Monthly client deliverable
```

**Never skip new-client.** Running ads without completing onboarding means no targets to measure against, no tracking to verify, and no baseline to learn from.

---

## Core Philosophy

1. **Documentation is infrastructure.** A fully populated client-info.md means every future skill — weekly-check, monthly-report, search-terms — has the context it needs without asking again.
2. **Tracking before traffic.** The first task of every onboarding is conversion tracking setup. Spending money before tracking is confirmed working is burning money without learning.
3. **Understand the business before touching the account.** Every optimization decision requires knowing what a conversion is worth, who the ideal customer is, and what makes this business different.
4. **Two scenarios, one workflow.** Brand-new account and inherited account have different paths — but both end with the same output: a fully documented, ready-to-run client workspace.
5. **Set expectations early.** Clients who are misaligned on timelines and results churn. The kickoff note aligns before the first dollar is spent.

---

## Intake: What to Gather

Ask these questions. For each piece of information the user provides upfront (URL, account ID, notes), skip the corresponding question and note what was inferred.

### Block 1: The Business

**1a. What does the business do?**
Capture: primary service/product, target customer, geography.

Probe if vague:
- "What's the one thing that makes up 70%+ of revenue?"
- "Who's the ideal customer — age, situation, urgency level?"
- "Is this local, regional, or national?"

**1b. What's the website URL?**
Fetch and review. Identify: primary CTA, main services, location, differentiators, trust signals.
Note any obvious landing page issues (no phone number, no form, generic homepage).

**1c. What are the key differentiators / USPs?**
What would make someone choose this business over competitors?
If unclear from the website, ask: "What do your best customers say about you? What keeps them coming back?"

**1d. What's the typical customer value?**
- eCommerce: Average order value? Repeat purchase rate? LTV?
- Lead gen (DTC): What's a lead worth? What % close? What's average transaction size?
- Service business (dental, medical, legal, aesthetics, construction, high-ticket retail): Ask all four of these:
  1. What's the average revenue per new client? (not per visit — per client relationship)
  2. What's your show rate? (what % of booked appointments actually show up?)
  3. What's your lead-to-close rate? (what % of people who show up become paying clients?)
  4. What's your gross margin on a new client?

For service businesses, this unlocks the CPL target:
```
Max CPL = Avg Revenue per New Client × Lead-to-Close Rate × Show Rate × Gross Margin %
Target CPL = Max CPL × 0.75
```

For DTC/eCommerce:
```
Max CPA = Avg Transaction Value × Gross Margin × Lead-to-Close Rate
```

Flag if the client doesn't know their numbers — they need to know them. Even rough estimates unlock better targeting decisions than no target at all.

**1e. Any seasonality?**
Peak months? Slow months? Any events, promotions, or deadlines that affect demand?

---

### Block 2: The Goals

**2a. What's the primary conversion goal?**
- Phone calls
- Form fills / contact requests
- Appointments / bookings
- Purchases / transactions
- Foot traffic / store visits

Get specific: "When someone clicks your ad, what's the ideal action?"

**2b. What's the monthly budget?**
If they say "we don't know yet" — give guidance:
```
Minimum viable budget guidelines:
- Local service (1 campaign): $500–$1,000/mo
- Local service (2–3 campaigns): $1,000–$2,500/mo
- eCommerce (search only): $1,500–$3,000/mo
- Competitive verticals (legal, dental, home services): $2,000–$5,000/mo+
```
Note: Budget below $500/month makes optimization very slow — flag this.

**2c. What's the target cost per lead/sale?**
If they don't have one, help them calculate it from 2d above.
If they won't share margins, note: "We'll use implied targets based on performance data."

**2d. What does success look like at 90 days?**
This reveals true expectations. Common misalignments to catch:
- "I want to be #1 on Google" (impression share goal, not conversion goal)
- "I want 100 leads in month 1" (unrealistic for most budgets — flag)
- "I want to spend $200/month and get 50 leads" (economics don't work — educate)

---

### Block 3: Account Access & History

**3a. Do they have an existing Google Ads account?**

**If YES (Inherited account):**
- Get the account ID or request MCC access
- Pull historical data (see Existing Account Audit section)
- Ask: "How long has it been running? What worked? What didn't? Why are you switching managers?"

**If NO (Brand new account):**
- Create new account under MCC 4781259815
- Note: New accounts have a 30-day learning period before Smart Bidding is reliable
- Flag: First 30 days = data collection, not optimization

**3b. Do they have Google Analytics? Google Tag Manager?**
- Analytics: needed for conversion tracking and audience data
- GTM: preferred for conversion tag deployment (faster, cleaner)
- If neither: plan for setup in Week 1

**3c. What tracking is currently in place?**
- Any existing conversion actions in Google Ads?
- Call tracking? Which provider?
- Form tracking? Which form plugin/platform?
- CRM? (HubSpot, Salesforce, etc. — may need offline conversion import)

**3d. Has Google Ads been run before? By whom?**
If by a previous agency:
- Were there structural issues? (Common: too many broad match keywords, no negatives, single campaign for everything)
- Were there tracking issues?
- Was the previous manager taking anything with them? (Landing pages, tracking setups they own)

---

### Block 4: Assets & Creative

**4a. What landing pages exist?**
- Is there a dedicated landing page or will ads go to the homepage?
- Dedicated landing page = better Quality Score + conversion rate
- Homepage = flag as a Week 1 priority to build or recommend a LP

**4b. What ad creative assets exist?**
- Logo, brand colors, brand fonts
- Photos (professional? stock?)
- Videos?
- These are needed if running Display, Demand Gen, or Meta Ads in future

**4c. Any offers or promotions?**
- Free consultation, free estimate, discount, guarantee?
- These make compelling ad copy and should be in headlines

---

### Block 5: Client Relationship

**5a. Who's the main contact?**
Name, email, phone, timezone.

**5b. How often do they want to hear from you?**
- Weekly updates? Monthly reports only?
- Proactive notifications for big changes?

**5c. How do they prefer to communicate?**
Email, Slack, WhatsApp, text, phone?

**5d. Any sensitivities or preferences?**
- Past bad experiences with agencies?
- Things they specifically don't want done?
- Anything they're anxious about?

---

## Existing Account Audit (Inherited Accounts Only)

If the client has an existing Google Ads account, run these API queries before the kickoff to understand the baseline:

### Query 1: 90-Day Campaign Performance History

```python
query = """
    SELECT
        campaign.id,
        campaign.name,
        campaign.status,
        campaign.bidding_strategy_type,
        campaign.advertising_channel_type,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.conversions_value,
        metrics.ctr,
        metrics.average_cpc
    FROM campaign
    WHERE segments.date DURING LAST_90_DAYS
    ORDER BY metrics.cost_micros DESC
"""
```

### Query 2: Conversion Tracking Status

```python
query = """
    SELECT
        conversion_action.id,
        conversion_action.name,
        conversion_action.status,
        conversion_action.category,
        conversion_action.counting_type,
        conversion_action.tag_snippets,
        metrics.conversions,
        segments.date
    FROM conversion_action
    WHERE segments.date DURING LAST_30_DAYS
"""
```

### Query 3: Account-Level Quality Score Health

```python
query = """
    SELECT
        ad_group_criterion.keyword.text,
        ad_group_criterion.quality_info.quality_score,
        ad_group_criterion.quality_info.creative_quality_score,
        ad_group_criterion.quality_info.post_click_quality_score,
        ad_group_criterion.quality_info.search_predicted_ctr,
        campaign.name,
        ad_group.name
    FROM keyword_view
    WHERE ad_group_criterion.quality_info.quality_score IS NOT NULL
      AND segments.date DURING LAST_30_DAYS
    ORDER BY ad_group_criterion.quality_info.quality_score ASC
    LIMIT 50
"""
```

### Query 4: Ad Disapprovals and Policy Issues

```python
query = """
    SELECT
        ad_group_ad.ad.id,
        ad_group_ad.policy_summary.approval_status,
        ad_group_ad.policy_summary.policy_topic_entries,
        ad_group_ad.status,
        campaign.name,
        ad_group.name
    FROM ad_group_ad
    WHERE ad_group_ad.policy_summary.approval_status != 'APPROVED'
      AND campaign.status != 'REMOVED'
"""
```

### Inherited Account Quick Assessment

After pulling data, note:

| Dimension | What to Check | Red Flags |
|-----------|--------------|-----------|
| Conversion tracking | Are conversions firing? Count per month | 0 conversions with significant spend = tracking broken |
| Campaign structure | Number of campaigns, types, budget allocation | Single campaign for everything, all budgets equal |
| Keyword strategy | Match types in use, keyword count | All broad match, thousands of keywords, no negatives |
| Negative keywords | Count at account + campaign level | < 20 negatives total = almost certainly wasting money |
| Bid strategies | What strategies are active | Manual CPC on high-volume campaigns = missed Smart Bidding |
| Quality Scores | Average QS, # of keywords below 5 | >30% of spend on QS ≤ 4 keywords |
| Ad copy | RSA completion, ad variety | Single ad per ad group, <10 headlines |
| Spend history | Monthly spend trend | Wildly inconsistent = reactive management |

Summarize in 3–5 bullets: "Here's what the previous account looks like and what the biggest issues are."

---

## Workspace Setup

After intake, create the client workspace.

### Step 1: Create folder structure

```bash
mkdir -p "clients/[Client Name] ([Account ID])/notes"
mkdir -p "clients/[Client Name] ([Account ID])/reports"
mkdir -p "clients/[Client Name] ([Account ID])/data"
```

### Step 2: Create populated client-info.md

Write the file at `clients/[Client Name] ([Account ID])/notes/client-info.md` using all information gathered in intake. Use this template, filling in every field:

```markdown
# [Client Name]

**Account ID:** [ID]
**Industry / Vertical:** [Specific vertical — e.g., "Healthcare — Chiropractic" not just "Healthcare"]
**Account Status:** [New / Active / Inherited]
**Onboarded:** [Date]

---

## Goals & Targets

| Metric | Target |
|---|---|
| Primary Conversion Goal | [Phone call / Form / Appointment / Purchase] |
| Target CPA | $[X] (or "TBD — establish in first 60 days") |
| Monthly Budget | $[X] |
| ROAS (if eCommerce) | [X.X] |
| Max Viable CPA | $[X] (based on: $[AOV] × [margin%] × [close rate%]) |

---

## Business Info

- **Services / products offered:** [List all, primary first]
- **Primary location / geo targeting:** [City, state, radius, or national]
- **Key differentiators / USPs:** [What makes them different — specific, not generic]
- **Typical customer value:** [LTV or avg transaction value]
- **Seasonality notes:** [Peak months, slow months, key dates]
- **Business hours:** [For call extension scheduling]
- **Special notes:** [Insurance, licensing, regulations, anything unusual]

---

## Brand Terms

<!-- These keywords must NEVER be negated in any campaign -->
- [brand name]
- [brand name variations]
- [owner/doctor name if relevant]
- [domain name]

---

## Competitor Notes

- **Known competitors:**
  - [Competitor 1] — [what they're known for, any notes]
  - [Competitor 2]
- **Competitor blocking strategy:** [Block / Allow / Mixed]
- **Competitor keywords to protect against:** [if applicable]

---

## Campaign Overview

| Campaign Name | Type | Budget | Goal | Status | Notes |
|---|---|---|---|---|---|
| [Name] | Search | $[X]/mo | [Leads/Sales] | [Active/Planned] | [Notes] |

---

## Conversion Tracking

| Conversion Action | Type | Assigned Value | Counting | Status | Verified |
|---|---|---|---|---|---|
| Phone Call (Google) | Call | $[X] or 1 | One per click | [Active/Needed] | [Yes/No] |
| Contact Form Submit | Page/Event | $[X] or 1 | One per conversion | [Active/Needed] | [Yes/No] |
| [Other] | | | | | |

**Tracking Setup Notes:**
- GTM: [Installed / Not installed / Needed]
- Google Analytics: [Connected / Not connected / Needed]
- Call tracking: [Google forwarding / CallRail / None]
- CRM integration: [None / HubSpot / Salesforce / Other]

---

## Account Access

- **Google Ads:** [MCC linked / Direct access / Pending]
- **Google Analytics:** [Access granted / Needed]
- **Google Tag Manager:** [Access granted / Needed / Not using]
- **Website access (for tracking):** [Yes / No / Not needed]

---

## Client Communication

- **Main contact:** [Name, email, phone]
- **Timezone:** [Timezone]
- **Reporting frequency:** [Weekly status + monthly report / Monthly only]
- **Report delivery method:** [Email / Slack / Google Doc / Other]
- **Communication channel:** [Email / Slack / WhatsApp / Phone]
- **Notes on client preferences:** [Anything notable — sensitivities, priorities, communication style]

---

## Account Quirks & History

<!-- Inherited account issues, past approaches that worked/didn't, client context -->
[If new account: "New account — no prior history."]
[If inherited: Summary of key findings from audit]

---

## Ongoing To-Dos

- [ ] Conversion tracking verified working
- [ ] Pre-launch checklist completed (see onboarding doc)
- [ ] First campaign live
- [ ] First weekly check run
- [ ] First monthly report delivered

---

*Last updated: [Date]*
```

### Step 3: Add client to CLAUDE.md (if not already listed)

If the client doesn't exist in the CLAUDE.md account table, note: "Add this client to the MCC table in CLAUDE.md once account ID is confirmed."

---

## Service Business Onboarding Track

For service business clients (dental, medical, chiropractic, legal, med spa, aesthetics, construction, high-ticket retail, B2B), run this track in addition to the standard onboarding above.

### Week 1 Service Business Checklist

**Tracking Setup**
- [ ] CallRail confirmed active — call recording enabled
- [ ] Tracking numbers assigned per source: Google Ads / Meta / organic (separate numbers per source)
- [ ] CallRail whisper message configured ("This call came from Google Ads" or similar)
- [ ] Google Ads call conversion actions verified: call extensions + landing page calls both tracked
- [ ] Meta lead form or website conversion events verified and firing
- [ ] GA4 goal events verified: form submissions, call clicks, appointment bookings
- [ ] Booking tool tracking confirmed if applicable (Calendly, Jane, NexHealth, etc.)

**CRM and Pipeline Setup**
- [ ] GHL sub-account confirmed active — pipeline stages defined with client
- [ ] GHL automated follow-up sequence reviewed or built (target: respond within 60 seconds of lead submission)
- [ ] Lead source tracking in GHL aligned with CallRail and platform UTMs

**Business Intelligence**
- [ ] Unit economics conversation completed — CPL target calculated and documented in client-info.md
- [ ] "What makes a lead qualified?" defined and documented (this is the quality anchor for all future diagnosis)
- [ ] Show rate and lead-to-close rate asked of client — documented either way (even if unknown, note that)
- [ ] Competitor audit completed: Google Ads Transparency, Meta Ad Library, local LSA listings
- [ ] 12-month calendar started with vertical-specific peaks noted

**Baseline Documentation**
- [ ] LSA account checked or created if applicable (dental, medical, legal, home services)
- [ ] Current volume of monthly leads / calls documented (baseline before ads)

---

### Week 2 Service Business Checklist

- [ ] First campaign structure built (Google Search is priority for most service verticals — high-intent queries first)
- [ ] Negative keyword list seeded with irrelevant service types, competitor names to block, and geographic exclusions
- [ ] Landing page audit complete using service business requirements (credentials above fold, objection handling, compliance reviewed)
- [ ] CallRail spot-check: pull 5 recent calls, review for lead quality, document findings
- [ ] GHL pipeline populated with any existing leads for baseline comparison
- [ ] Client expectations set clearly: month 1 is establishing CPL baseline and defining lead quality — not scaling
- [ ] First test batch launched with hypothesis documented (angle, audience, expected CPL)

---

## Pre-Launch Checklist

This checklist must be completed before the first campaign goes live. Generate a copy and save it in the client's notes folder.

### Access & Setup ✅
- [ ] Google Ads account created or MCC access granted
- [ ] Account linked to MCC (4781259815)
- [ ] Google Analytics property connected to Google Ads
- [ ] Google Tag Manager installed on website (if using)
- [ ] Billing confirmed and payment method active

### Conversion Tracking ✅
- [ ] Primary conversion action created in Google Ads
- [ ] Conversion tag installed and firing (test with Tag Assistant)
- [ ] Phone call tracking set up (Google forwarding number or CallRail)
- [ ] Form submission tracking verified (submit a test form, confirm conversion fires)
- [ ] Conversion value assigned ($ value or use 1 if unknown)
- [ ] Conversion window set appropriately (30–90 days for service businesses)
- [ ] At least one test conversion recorded before going live

### Campaign Foundation ✅
- [ ] Brand terms list documented in client-info.md
- [ ] Competitor blocking strategy decided
- [ ] Foundational negative keyword list built (50+ terms minimum)
- [ ] Ad schedule set (if business hours restrict when ads should run)
- [ ] Geographic targeting confirmed (radius, zip codes, or state)
- [ ] Language targeting set (English only vs. multilingual)
- [ ] Device bid adjustments considered (mobile vs. desktop split based on service type)

### Ad Copy & Landing Pages ✅
- [ ] Landing page confirmed and reviewed (not homepage if possible)
- [ ] Landing page has: phone number, contact form, CTA above fold
- [ ] Mobile experience confirmed (loads fast, click-to-call works)
- [ ] First RSA written: 15 headlines, 4 descriptions
- [ ] Ad extensions set up: sitelinks (4+), callouts (4+), call extension, location extension

### Client Alignment ✅
- [ ] Monthly budget confirmed in writing
- [ ] Target CPA/ROAS confirmed or learning period explained
- [ ] Reporting schedule communicated (weekly + monthly)
- [ ] Timeline expectations set: "You'll start seeing data in 2 weeks, optimization in 4–6 weeks"
- [ ] Client knows what they need to do (respond to leads fast, update us on lead quality)

---

## First 30-Day Plan

Generate a specific, dated plan for the client's first month.

### Week 1: Foundation
**Goal:** Access, tracking, and first campaign live.

- Day 1–2: Finalize all account access
- Day 2–3: Conversion tracking installed and verified
- Day 3–5: Build first campaign (using `/ads-strategy-architect` for full strategy)
- Day 5–7: Campaign live — first data starts flowing

**Deliverable:** Campaign live, tracking verified, client confirmation sent.

### Week 2: First Look
**Goal:** Initial data review, first optimizations.

- Run `/search-terms` — first search terms review
- Add initial negative keywords from irrelevant traffic
- Verify conversion tracking is firing on real conversions (not just test)
- Check budget pacing
- Brief client update: "Here's what we're seeing in the first week"

**Deliverable:** First search terms cleanup, client status note.

### Week 3–4: First Optimization Cycle
**Goal:** Stabilize performance, begin learning what works.

- Run `/weekly-check`
- Second `/search-terms` review
- Assess keyword performance — any with high spend, 0 conversions?
- Check ad copy CTR — any headlines not getting impressions?
- Check Quality Scores — any below 5?
- Adjust bids if on Manual CPC

**Deliverable:** Weekly check report, early performance signal summary.

### End of Month 1: Foundation Review
**Goal:** Assess what month 1 taught us, set month 2 plan.

- Run `/monthly-report` (even if a partial first month)
- Document what worked, what didn't, what to test in month 2
- Confirm whether target CPA is realistic or needs adjustment based on first data
- Present to client: "Here's what we learned and here's month 2's plan"

**Deliverable:** Month 1 report, month 2 plan.

---

## Kickoff Note (Client-Facing)

Generate a short note to send to the client after onboarding is complete. Adapt tone to match client preferences.

```
Subject: [Client Name] — Google Ads Kickoff Summary

Hi [Name],

Great to be working together. Here's a quick summary of where things stand and what happens next.

**What we've set up:**
- Google Ads account [linked / created]
- Conversion tracking installed for [phone calls / form submissions / etc.]
- Geographic targeting set to [area]
- Monthly budget: $[X]

**What's launching:**
[Campaign 1 name] — targeting [description] — live [date]
[Campaign 2 name if applicable]

**What to expect in the first 30 days:**
The first few weeks are the data-gathering phase. Google's system is learning who to show your ads to and which searches work best. You'll start seeing activity immediately, but the best performance usually comes in weeks 3–6 as the system optimizes.

**What we need from you:**
When you get leads from ads, please let us know: Did they become a customer? Were they a good fit? This feedback helps us optimize toward quality, not just volume.

I'll send you a weekly status note and a full monthly report at the end of [month].

Any questions — just reply here.

[Your name]
```

---

## Guardrails

❌ **NEVER** launch a campaign without verified conversion tracking — this is the single most expensive mistake in PPC
❌ **NEVER** skip documenting brand terms — future negative keyword work depends on this
❌ **NEVER** set a target CPA before understanding what a customer is worth to the business
❌ **NEVER** promise specific lead volume or CPA before the first 30 days of data
❌ **NEVER** create a client folder without populating client-info.md — empty templates are useless
❌ **NEVER** run ads for a service business client without defining "what makes a lead qualified" with the client — this is the lead quality anchor for all future diagnosis. A cheap lead that never shows is worse than an expensive lead that converts.

✅ **ALWAYS** calculate max viable CPA from the client's business economics
✅ **ALWAYS** document brand terms immediately — they're needed by search-terms, negative-keyword-analyzer, and monthly-report
✅ **ALWAYS** flag if budget is below minimum viable for the vertical
✅ **ALWAYS** check for an existing account before assuming it's new — existing accounts have history that matters
✅ **ALWAYS** save client-info.md before closing the conversation — it's the foundation for everything else
✅ **ALWAYS** note the account's currency (CAD, AUD, GBP vs USD — this affects all cost targets)

---

## Edge Cases

### Client Has an Existing Account with Problems
Don't try to fix everything in week 1. Note what's broken in client-info.md, prioritize by impact, and put fixes in the 30-day plan. The exception: broken conversion tracking — fix this before anything else, regardless of other issues.

### Client Has No Website or a Terrible Website
Flag immediately: ads pointing to a poor landing page waste money. Options:
1. Pause strategy discussion until a landing page is built
2. Use a simple lead capture page (Unbounce, Leadpages) as a stopgap
3. Use Google's lead form extensions as a conversion mechanism if the budget is small

### Very Small Budget (Under $500/month)
Be honest: at $300–400/month, you'll have enough data to learn in ~60 days, not 30. Set expectations. Recommend starting with one very tight, high-intent campaign rather than spreading thin.

### Inherited Account That's a Complete Mess
Don't try to "fix it" — pause and rebuild. Document what's there, pause the worst campaigns, and start fresh with proper structure. Timeline: 2 weeks to audit and plan, 2 weeks to build and launch clean campaigns.

### Client Doesn't Know Their Customer Value
Common. Help them estimate:
- "What does a typical job/sale/appointment bring in revenue?"
- "What % of that is profit?"
- "What % of leads that call or fill out a form actually become customers?"
- Even rough numbers (e.g., "$2,000 revenue, 40% margin, 30% close = $240 per lead max viable CPA") are better than no target.

### Multiple Locations or Multi-Location Franchise
Document each location separately if budgets are separate. Consider: one campaign per location with location-specific landing pages vs. consolidated campaign with location extensions. Note this decision and rationale in client-info.md.

---

## Quality Assurance

Before closing onboarding:
- [ ] All intake blocks completed (business, goals, access, assets, relationship)
- [ ] client-info.md created with zero empty fields (N/A is acceptable, blank is not)
- [ ] Brand terms documented
- [ ] Max viable CPA calculated or flagged as unknown with action to find out
- [ ] Existing account audited if inherited (or confirmed new)
- [ ] Pre-launch checklist generated and saved
- [ ] First 30-day plan is specific (named campaigns, dated milestones)
- [ ] Kickoff note generated for client
- [ ] Client added to CLAUDE.md account table if not already there
- [ ] Currency noted (CAD vs USD vs other)
- [ ] Next action clear: "Run /ads-strategy-architect with [URL] to build campaign strategy"
