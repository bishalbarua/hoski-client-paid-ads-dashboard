---
name: monthly-report
description: Generates the monthly Google Ads performance report for a client — pulls 30-day vs prior 30-day data via API, builds an internal performance analysis, then produces a polished client-facing report in business language. Triggers when user says "monthly report for [client]", "run the [month] report", or "prepare [client] report". Pulls data automatically from Google Ads API using the client name from CLAUDE.md. Saves the report to clients/[client]/reports/. Handles both lead gen and eCommerce clients.
---

# Monthly Report

The monthly report is the primary client deliverable. It tells the story of the month — what was achieved, what work was done, and what's coming next — in language a business owner understands. It is not a PPC audit. It is not a data dump. It is a narrative built on data.

Two outputs are produced every time:
1. **Internal analysis** — full data pull with MoM deltas, campaign-level breakdown, and optimization notes (stays in the workspace)
2. **Client report** — polished, non-technical document in business language (delivered to client)

---

## How This Skill Differs From Other Skills

| Skill | Purpose | Audience |
|---|---|---|
| `/monthly-report` | Monthly client deliverable — story of the month | Client + internal |
| `/weekly-check` | Operational monitoring — what's on fire, action list | Internal only |
| `/ppc-account-health-check` | One-time deep strategy assessment | Internal only |
| `/campaign-scaling-expert` | Strategic scaling roadmap | Internal only |

**Rule:** Monthly report is the client-facing skin over the operational work done all month.

---

## Core Philosophy

1. **Clients buy results, not tactics.** Lead with conversions, cost per lead, and spend vs. budget. Never lead with CTR or Quality Score.
2. **Every number needs a sentence.** "18 leads at $54 average" means nothing without "versus your $65 target — 17% more efficient." Always add the business context.
3. **Show the work.** Clients don't see the daily work. The "what we did" section builds trust and justifies the retainer. Be specific: "Added 14 negative keywords targeting free-seeking traffic, saving an estimated $180."
4. **Honesty builds retention.** If a campaign underperformed, say so clearly and explain what's being done. Spin erodes trust.
5. **Forward is as important as backward.** Every report ends with next month's plan. Clients need to know the work continues.
6. **Two audiences, two documents.** The internal analysis can be blunt and technical. The client report must be clear to a non-marketer reading it in 2 minutes.

---

## Critical Context Gathering

### Required

**1. Client name and report month**
Look up the account ID from CLAUDE.md. Default report period is the full prior calendar month (e.g., if today is March 18, report covers February 1–28).

If the user specifies a different period ("last 30 days", "March so far"), use that instead.

**2. Conversion goal type**
Pull from `clients/[client]/notes/client-info.md` if available. Otherwise ask:
- **Lead gen** (form fills, calls, appointments) — report on leads and cost per lead
- **eCommerce** (purchases, revenue) — report on ROAS, revenue, and transactions
- **Mixed** — handle each conversion action separately

**3. Targets**
Pull from client-info.md:
- Target CPA / target ROAS
- Monthly budget
- Any campaign-specific targets

If not in client-info.md, check if the user states them, or note "Targets not on file" and assess relative to prior period.

### Recommended

**4. Work notes from the month**
What optimizations, tests, or changes were made? Ask: "Any changes or work this month I should include in the report?"
Or pull from any notes in `clients/[client]/` created during the month.

**5. Known external factors**
Seasonality, promotions, holidays, competitor activity that affected performance. Without this, anomalies look unexplained.

**6. Client preferences**
Pull from client-info.md:
- Report delivery method (email? Slack? Google Doc?)
- Level of detail preferred
- Anything the client is sensitive about

---

## Data Pull (Google Ads API)

Pull all queries using the account ID from CLAUDE.md for the named client.

### Query 1: Monthly Campaign Performance (This Month + Prior Month)

```python
query_this_month = """
    SELECT
        campaign.id,
        campaign.name,
        campaign.status,
        campaign.advertising_channel_type,
        campaign.bidding_strategy_type,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.conversions_value,
        metrics.ctr,
        metrics.average_cpc,
        metrics.search_impression_share,
        metrics.search_budget_lost_impression_share,
        metrics.search_rank_lost_impression_share
    FROM campaign
    WHERE segments.date DURING LAST_MONTH
      AND campaign.status != 'REMOVED'
    ORDER BY metrics.cost_micros DESC
"""

query_prior_month = """
    SELECT
        campaign.id,
        campaign.name,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.conversions_value
    FROM campaign
    WHERE segments.date DURING TWO_MONTHS_AGO
      AND campaign.status != 'REMOVED'
    ORDER BY metrics.cost_micros DESC
"""
```

### Query 2: Conversion Actions Breakdown

```python
query_conversions = """
    SELECT
        conversion_action.name,
        conversion_action.category,
        metrics.conversions,
        metrics.conversions_value,
        metrics.cost_per_conversion,
        segments.conversion_action_name
    FROM campaign
    WHERE segments.date DURING LAST_MONTH
      AND metrics.conversions > 0
"""
```

### Query 3: Top Keywords This Month

```python
query_keywords = """
    SELECT
        ad_group_criterion.keyword.text,
        ad_group_criterion.keyword.match_type,
        campaign.name,
        ad_group.name,
        metrics.impressions,
        metrics.clicks,
        metrics.cost_micros,
        metrics.conversions,
        metrics.average_cpc
    FROM keyword_view
    WHERE segments.date DURING LAST_MONTH
      AND metrics.clicks > 0
    ORDER BY metrics.conversions DESC, metrics.cost_micros DESC
    LIMIT 20
"""
```

### Query 4: Ad Performance

```python
query_ads = """
    SELECT
        ad_group_ad.ad.id,
        campaign.name,
        ad_group.name,
        metrics.impressions,
        metrics.clicks,
        metrics.ctr,
        metrics.conversions,
        metrics.cost_micros,
        ad_group_ad.policy_summary.approval_status
    FROM ad_group_ad
    WHERE segments.date DURING LAST_MONTH
      AND metrics.impressions > 0
    ORDER BY metrics.conversions DESC
"""
```

### MoM Delta Calculation

After pulling both months:
```python
def mom_delta(this, prior):
    if prior == 0:
        return "N/A (no prior data)"
    return round((this - prior) / prior * 100, 1)

# Key deltas to calculate:
# spend_delta, conversions_delta, cpa_delta, clicks_delta, impressions_delta
# For ROAS clients: roas_delta, revenue_delta
```

---

## Internal Analysis Framework

Build this first. It feeds into the client report but stays in the workspace.

### Section A: Account-Level Summary

Calculate and note:
- Total spend this month vs prior month vs budget (pacing %)
- Total conversions this month vs prior month
- Blended CPA this month vs prior month vs target
- For eCommerce: total revenue, ROAS this month vs prior month vs target
- Overall MoM direction: improving / declining / stable

**For service business clients (dental, medical, legal, aesthetics, construction, high-ticket retail, B2B):**

MER does not apply — most cannot produce a clean total revenue figure from a unified source.

Use the service business dashboard instead:

| Metric | This Month | Prior Month | Change | Target |
|---|---|---|---|---|
| Total Leads | X | X | +/-X% | — |
| Cost Per Lead (blended) | $X | $X | +/-X% | $X (from client-info.md) |
| Show Rate | X% | X% | +/-X pts | 65%+ |
| Lead-to-Close Rate | X% | X% | +/-X pts | [from client data] |
| Cost Per Acquired Client | $X | $X | +/-X% | $X |
| Total Ad Spend | $X | $X | +/-X% | $X (budget) |

**Service dashboard notes:**
- Target CPL comes from the unit economics calculation in client-info.md
- Show Rate comes from GHL pipeline: booked leads who attended / total booked
- Lead-to-Close Rate comes from GHL pipeline: closed clients / leads who showed
- Cost Per Acquired Client = CPL / (show rate × lead-to-close rate)
- Call Duration Distribution from CallRail: what % of calls are above the qualified-call threshold?
- Channel split: which platform is driving qualified outcomes, not just leads?

If show rate is below 60%: lead quality problem. Check targeting, ad copy, landing page, and follow-up speed. Report this clearly to the client — do not bury it.

If show rate is healthy but close rate is low: sales or offer problem, not an ads problem. Communicate this clearly and sensitively. The ads are doing their job.

### Section B: Campaign-Level Breakdown

For each campaign with spend > $0:

| Campaign | Spend | Spend MoM | Conv | Conv MoM | CPA | CPA MoM | vs Target | Status |
|---------|-------|-----------|------|----------|-----|---------|-----------|--------|

Tier each campaign:
- **Star** (CPA ≤ target, volume ≥ prior month)
- **Solid** (CPA ≤ target, volume declining)
- **Watch** (CPA 1.0–1.3× target)
- **Problem** (CPA > 1.3× target)
- **Inactive** (0 spend — note why if known)

### Section C: Conversion Quality Check

- Any sudden conversion drops mid-month? (Flag potential tracking issue)
- Conversion split by type (calls vs forms vs purchases)?
- Any conversion actions with unusually high or low volume?

### Section D: Notable Events This Month

Compile from work notes + weekly checks + any known changes:
- Bid strategy changes made
- Budget changes made
- Negative keywords added (estimate waste prevented)
- New keywords or ad groups launched
- Ad copy changes
- Landing page changes
- External factors (seasonality, promos)

### Section E: What Needs Attention Next Month

Internal priority list (not for client) — top 3 things that need focus:
1. Campaigns to improve
2. Tests to run
3. Structural changes needed

---

## Client Report Template

After the internal analysis, generate the client-facing report. Use this structure exactly — it is consistent month-to-month so clients know what to expect.

**Tone:** Clear, confident, professional. No PPC jargon. Write as if explaining to a smart non-marketer.

**Length:** Long enough to show the work, short enough to be read in 3–5 minutes.

---

```markdown
# [CLIENT NAME] — Google Ads Monthly Report
**Period:** [Month Year] ([Start Date] – [End Date])
**Prepared:** [Today's Date]

---

## Summary

[2–4 sentences covering the month. Lead with the headline result — did we hit the goal? What was the most notable outcome? What's the forward momentum?]

Example (lead gen):
"February delivered 24 leads at an average cost of $51 — 22% below your $65 target. Spend came in at $1,224 against a $1,200 budget. The Emergency Plumbing campaign accounted for 70% of leads and continues to be our strongest performer. March is set up well with two new ad tests running."

Example (eCommerce):
"February generated $14,800 in attributed revenue from $2,100 in ad spend — a 7.0 ROAS, up from 5.8 last month. Total orders increased 18% month-over-month. The Rings collection continues to outperform and we've scaled budget there heading into March."

---

## Month at a Glance

[Use a metrics table. Adapt columns to lead gen vs. eCommerce.]

### Lead Gen Table
| Metric | [This Month] | [Prior Month] | Change | Target |
|---|---|---|---|---|
| Total Leads | X | X | +/-X% | X |
| Cost Per Lead | $X | $X | +/-X% | $X |
| Total Spend | $X | $X | +/-X% | $X (budget) |
| Total Clicks | X | X | +/-X% | — |
| Avg. Cost Per Click | $X | $X | +/-X% | — |

### eCommerce Table
| Metric | [This Month] | [Prior Month] | Change | Target |
|---|---|---|---|---|
| Revenue (attributed) | $X | $X | +/-X% | — |
| ROAS | X.X | X.X | +/-X% | X.X |
| Total Orders | X | X | +/-X% | — |
| Total Spend | $X | $X | +/-X% | $X (budget) |
| Cost Per Order | $X | $X | +/-X% | $X |

---

## Campaign Results

[One paragraph per active campaign. Business language — no PPC jargon. Include: what it does, how it performed, key change or observation.]

### [Campaign Name]
[2–3 sentences: What this campaign targets → How it performed this month (leads/revenue/CPA) vs. target and vs. prior month → One notable observation or action taken.]

Example:
"**Emergency Plumbing** — Our primary lead driver, targeting homeowners with urgent plumbing problems. This month it generated 17 leads at $44 each — well under the $65 target — with spend of $748. We added 8 negative keywords mid-month to cut out informational traffic, and that appears to have improved lead quality."

Example (underperformer):
"**General Plumbing Services** — This campaign targets broader plumbing searches and delivered 4 leads at $112 each, above the $65 target. We're investigating whether the landing page is the bottleneck or the keyword mix — more on that in the plan section below."

[Repeat for each campaign with spend > 0.]

---

## Work Done This Month

[This is the "show the work" section. Clients often don't realize how much ongoing optimization goes into the account. Be specific and frame everything in terms of outcome.]

- **[Action taken]** — [Why it was done and what outcome it should produce]

Examples:
- **Added 14 negative keywords targeting "free" and "DIY" searches** — These were attracting people not looking to hire a plumber. Removing them is estimated to save $80–120/month in wasted clicks.
- **Increased budget on Emergency Plumbing by $15/day** — The campaign was hitting its daily cap by midday. With more room, it delivered 4 additional leads at the same cost per lead.
- **Updated ad headlines on General Plumbing** — Previous headlines weren't mentioning same-day service, which is a key differentiator. New headlines emphasize this and we're watching for a CTR improvement.
- **Paused 3 underperforming keywords** — Three keywords had spent $180 combined with zero leads over 60 days. Budget reallocated to top performers.

[If no major work was done, be honest but still list maintenance tasks: "Reviewed search terms weekly and added 6 negatives. Monitored bid strategies and confirmed they're tracking toward target."]

---

## What's Working

[2–4 bullets. Specific, with numbers. Frame as "things to continue and protect."]

- **[Campaign or element]**: [Why it's working, with the number that proves it]

Example:
- **Emergency Plumbing campaign**: Consistently delivering leads at $40–50, 30–40% below target. We're protecting this budget and not touching the structure.
- **"Same-day plumber near me" keyword**: Highest-converting term in the account — 8 leads at $38 average. We've added exact match to lock in the bid.
- **New ad copy emphasizing free estimates**: CTR up 22% vs. the previous version and driving more conversions. We'll use this framing in other campaigns.

---

## What We're Working On

[1–3 bullets. Be honest about what's underperforming and what's being done about it. Frame as "in progress" not "broken."]

- **[Issue]**: [What we're doing about it]

Example:
- **General Plumbing campaign CPA is high**: We believe the landing page isn't converting well for broad searches. We're testing a simplified landing page version in March with a direct call CTA — expecting to see results within 2–3 weeks.
- **Conversion tracking for phone calls is incomplete**: Some calls are likely not being counted, which is making the CPA look worse than it is. We're setting up call tracking through Google's forwarding number this week.

---

## Plan for Next Month

[3 clear priorities for next month. Written as forward momentum, not a technical task list.]

1. **[Priority 1]** — [What will be done and why it matters]
2. **[Priority 2]** — [What will be done and why it matters]
3. **[Priority 3]** — [What will be done and why it matters]

Example:
1. **Launch a dedicated landing page for General Plumbing** — A tighter landing page (call CTA + local trust signals) should bring the CPA in line with Emergency Plumbing. We expect to have this live by March 10.
2. **Test a new ad angle: 24/7 availability** — Competitor research shows no one in your market is leading with 24-hour service. We'll test this as a headline theme and see if it moves CTR.
3. **Set up call tracking** — Getting full conversion visibility will let us optimize more precisely. This is a one-time setup that improves every future decision.

---

## Budget Summary

| | Amount |
|---|---|
| Monthly Budget | $X |
| Actual Spend | $X |
| Over/Under | +/-$X (+/-X%) |

[One sentence explaining any meaningful variance.]
Example: "Spend came in $48 under budget (4%) due to lower search volume over the Presidents Day weekend — normal seasonal dip."

---

*Report prepared by [Your Name/Agency] | Data from Google Ads | [Client Name], Account [Account ID]*
```

---

## Handling Common Situations

### Month with No Conversions
Do not hide this. Address it directly:
- Confirm tracking is working (if tracking is broken, say so and fix it before sending)
- If tracking is fine, explain the situation clearly and what's being investigated
- Never send a report attributing zero conversions to "seasonal variation" without evidence

### First Month of a New Campaign
Lower expectations language: "This was the first full month running. We're in the data-gathering phase — the goal right now is learning what works before optimizing spend efficiency. Here's what we observed..."

### MoM Comparisons Distorted by Seasonality
Flag it: "March is typically slower for plumbing than January (seasonal demand). To give a fair read, here's how [this March] compares to [last March] if available, or note the expected seasonal pattern."

### Client Is Sensitive About a Bad Month
Be honest, not defensive. Frame around:
1. What happened (data)
2. Why it happened (explanation)
3. What's being done (action)
Never spin. Clients can smell it, and it destroys trust faster than a bad month does.

### eCommerce vs. Lead Gen Language Swap

| eCommerce | Lead Gen |
|-----------|----------|
| Revenue | Leads |
| ROAS | Cost per lead |
| Orders / Transactions | Inquiries / Bookings / Calls |
| Return on ad spend | Lead efficiency |
| Average order value | Average lead value |

---

## File Output

After generating both documents, save them:

```
clients/[Client Name] ([Account ID])/reports/[client-slug]-[YYYY-MM]-monthly-report.md
```

Example:
```
clients/FaBesthetics (9304117954)/reports/fabesthetics-2026-02-monthly-report.md
```

The file contains:
1. Internal analysis (full data, campaign tiers, optimization notes)
2. Client report (polished, non-technical, copy-paste ready)

Separate the two sections with a clear divider:
```
---
# INTERNAL — ANALYSIS NOTES
[internal content]

---
# CLIENT REPORT — SEND THIS
[client content]
```

---

## Guardrails

❌ **NEVER** send a report without verifying conversion tracking is working — zero leads on a healthy account is almost always a tracking issue first
❌ **NEVER** use PPC jargon in the client report (CTR, QS, IS, ROAS acronym without spelling out, Smart Bidding, ad rank, broad match, etc.)
❌ **NEVER** omit the "what we're working on" section — hiding underperformance destroys trust when the client notices
❌ **NEVER** fabricate work done — if it was a quiet month, be honest about it
❌ **NEVER** compare months without noting known distortions (seasonality, budget changes, tracking gaps)
❌ **NEVER** report blended CPA across lead gen and eCommerce conversion actions — separate them

✅ **ALWAYS** lead with the business outcome, not the platform metric
✅ **ALWAYS** include both MoM change AND vs. target — one without the other is incomplete
✅ **ALWAYS** put the plan for next month — every report ends forward, not backward
✅ **ALWAYS** save the report to the client's folder
✅ **ALWAYS** read client-info.md before writing — tone, targets, and preferences live there
✅ **ALWAYS** note if data confidence is low (< 20 conversions makes CPA conclusions fragile)
✅ **ALWAYS** use the service business dashboard (CPL, show rate, lead-to-close, cost per acquired client) for non-eCommerce clients — MER and ROAS are not applicable
✅ **ALWAYS** distinguish between a media problem (high CPL) and an operational problem (low show rate) in service business reports — clients need to know which lever to pull

---

## Edge Cases

### No client-info.md on file
Proceed with what's available from the API. Note which targets are missing and ask the user to confirm or supply them for accuracy.

### Report period spans a major budget change
Split the analysis: "For the first 12 days of February, the monthly budget was $800. On February 13 we increased to $1,200. The full-month numbers reflect both periods."

### Client uses both Google Ads and Meta Ads
This skill covers Google Ads only. If the client runs Meta, note: "Meta Ads performance not included in this report — covered separately." Do not blend cross-platform metrics.

### Multiple accounts under one client (e.g., Voit Dental 1 + 2)
Report each account separately, then optionally add a combined summary. Never blend account IDs in calculations.

### Report month is the current month (partial month)
Label clearly: "[Month] Month-to-Date Report (through [date])." Do not annualize or project — just report actuals with the date qualifier.

---

## Quality Assurance

Before finalizing:
- [ ] Internal analysis: all active campaigns included with correct MoM deltas
- [ ] Conversion tracking verified healthy (or issue flagged)
- [ ] Client targets pulled from client-info.md or confirmed with user
- [ ] Client report: zero PPC jargon — read it as if you're the client
- [ ] Every metric in the client report has a sentence of context
- [ ] "Work done" section has at least 3 specific items
- [ ] "Plan for next month" has exactly 3 actionable priorities
- [ ] Budget summary matches API spend data
- [ ] Report saved to correct client folder with correct filename
- [ ] Tone is honest — underperformance addressed, not hidden
