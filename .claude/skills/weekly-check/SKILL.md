---
name: weekly-check
description: Monday morning operational review for one Google Ads client. Checks week-over-week performance, budget pacing, conversion tracking health, learning period status, ad disapprovals, and bid strategy signals — then produces a prioritized action list for the week and an optional client-facing status note. Triggers when the user says "weekly check", "check [client] this week", "how did [client] do", or "Monday review". Pulls data via Google Ads API or accepts pasted/uploaded data. Designed to run in under 10 minutes.
---

# Weekly Check

The weekly check is the operational heartbeat of PPC management. It's not a deep audit — it's a systematic sweep of everything that could be on fire, everything that changed, and everything that needs a decision this week.

Run every Monday (or first working day of the week) for each active client.

## How This Skill Differs From Other Skills

| Skill | When To Use |
|---|---|
| `/weekly-check` | Every week — operational sweep, WoW changes, pacing, tracking health |
| `/ppc-account-health-check` | One-time deep assessment of account strategy and structure |
| `/search-terms` | Weekly or as needed — dedicated search terms sweep for negatives and opportunities |
| `/campaign-scaling-expert` | Quarterly or when ready to grow — strategic scaling roadmap |

**Rule:** Run `/weekly-check` first. If it surfaces something deep, escalate to the appropriate specialist skill.

---

## Core Philosophy

1. **Operational first, strategic second.** If conversion tracking is broken, nothing else matters. Check the pipes before optimizing the faucets.
2. **Week-over-week is the signal.** Monthly trends hide problems. WoW changes catch issues before they become expensive.
3. **Pacing protects the relationship.** Clients notice overbilling and underspend before they notice CPA fluctuations. Always check pacing.
4. **The checklist exists for consistency.** A good weekly check done consistently beats a brilliant audit done quarterly.
5. **Flag fast, fix specifically.** The output is a prioritized action list, not a report. Every item should be executable.

---

## Critical Context Gathering

### Required

**1. Client name (or account ID)**
Used to pull data from the Google Ads API. If not recognized, ask for the account ID.

**2. What week are we reviewing?**
Default: the 7 days ending yesterday (Mon–Sun or Sun–Sat depending on client).
Clarify if the user specifies a different window.

**3. Targets (ask if not already known for this client)**
- Target CPA: $___
- Target ROAS: ___
- Monthly budget: $___

If targets aren't known, infer from prior-period data and note the assumption.

### Recommended

**4. Any changes made last week?**
- Budget changes, bid strategy switches, new campaigns launched, landing page updates
- This prevents misattributing performance changes to the wrong cause

**5. Known external factors**
- Seasonality, promotions running, holidays, competitor activity
- Example: "Black Friday week — CTR spike is expected"

---

## Data Pull (Google Ads API)

When the user provides a client name, look up the account ID in CLAUDE.md and pull data automatically.

### Query 1: Weekly + Prior Week Campaign Performance

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
        metrics.search_impression_share,
        metrics.search_budget_lost_impression_share,
        metrics.search_rank_lost_impression_share,
        segments.date
    FROM campaign
    WHERE segments.date DURING LAST_14_DAYS
      AND campaign.status != 'REMOVED'
    ORDER BY metrics.cost_micros DESC
"""
```

Split into THIS_WEEK (last 7 days) vs PRIOR_WEEK (days 8–14) manually after pulling.

### Query 2: Conversion Tracking Health

```python
query = """
    SELECT
        conversion_action.name,
        conversion_action.status,
        conversion_action.category,
        conversion_action.counting_type,
        metrics.conversions,
        segments.date
    FROM conversion_action
    WHERE segments.date DURING LAST_14_DAYS
      AND conversion_action.status = 'ENABLED'
"""
```

### Query 3: Ad Disapprovals

```python
query = """
    SELECT
        ad_group_ad.ad.id,
        ad_group_ad.ad.name,
        ad_group_ad.policy_summary.approval_status,
        ad_group_ad.policy_summary.policy_topic_entries,
        campaign.name,
        ad_group.name
    FROM ad_group_ad
    WHERE ad_group_ad.policy_summary.approval_status != 'APPROVED'
      AND ad_group_ad.status = 'ENABLED'
      AND campaign.status = 'ENABLED'
"""
```

### Query 4: Campaign Learning Status

```python
query = """
    SELECT
        campaign.name,
        campaign.status,
        campaign.bidding_strategy_type,
        campaign_budget.amount_micros,
        metrics.cost_micros,
        metrics.conversions,
        metrics.impressions
    FROM campaign
    WHERE campaign.status = 'ENABLED'
      AND segments.date DURING LAST_7_DAYS
"""
```

Note: Learning period is inferred from low impression share + recent bid strategy change context. Google doesn't expose a direct "in learning" field in GAQL.

### Query 5: Budget Pacing

```python
# Calculate days elapsed and projected spend
from datetime import date

today = date.today()
days_in_month = 30  # approximate
days_elapsed = today.day
days_remaining = days_in_month - days_elapsed

query = """
    SELECT
        campaign.name,
        campaign_budget.amount_micros,
        campaign_budget.total_amount_micros,
        metrics.cost_micros,
        segments.month
    FROM campaign
    WHERE segments.date DURING THIS_MONTH
      AND campaign.status = 'ENABLED'
"""
```

Pacing formula:
```
Expected Spend = (Monthly Budget / Days in Month) × Days Elapsed
Pacing % = Actual Spend / Expected Spend × 100

Underpacing: < 85%
On track:    85–115%
Overpacing:  > 115%
```

---

## Analysis Framework

Run all six checks in this order. Each generates pass/warn/alert signals that feed into the final action list.

---

### Check 1: Conversion Tracking Health 🩺

**Why first:** If tracking is broken, every other metric is meaningless.

| Signal | Threshold | Status |
|--------|-----------|--------|
| This week conversions vs last week | Drop > 40% with stable clicks | 🔴 ALERT |
| This week CVR vs last week | Drop > 30% with stable traffic | 🔴 ALERT |
| Conversion actions with 0 conversions this week | Any primary conversion action | 🟡 WARN |
| All conversion actions returning data | All enabled actions firing | 🟢 PASS |

**Distinguish tracking issues from real performance drops:**
- Tracking issue: Clicks normal, impressions normal, conversions → 0 suddenly
- Real performance drop: Conversions down + CTR down + impression share down together

**If ALERT:** Do not make any optimization changes until tracking is verified. Flag immediately.

---

### Check 1B: Service Business Lead Quality (non-eCommerce clients only)

Run this check for all service business clients immediately after Check 1.

| Signal | Threshold | Status |
|--------|-----------|--------|
| CPL this week vs target CPL | > 30% above target | 🟡 WARN |
| CPL this week vs target CPL | > 50% above target | 🔴 ALERT |
| Show rate (from GHL pipeline) | < 60% | 🟡 WARN — lead quality issue, check follow-up speed first |
| Show rate (from GHL pipeline) | < 45% | 🔴 ALERT — check targeting, ad copy, LP, and GHL follow-up speed |
| Speed-to-lead (GHL average response time) | > 5 minutes | 🟡 WARN — qualification probability drops 80% after 5 min |
| CallRail avg call duration this week | Below qualified threshold (typically < 2 min) | 🟡 WARN — low-quality calls coming in |

**Diagnosis order:**
1. If show rate is low: check GHL follow-up speed FIRST, before adjusting the campaign. Operational problem comes before media problem.
2. If call duration is short: pull 5 calls in CallRail and review manually. Diagnose whether targeting, landing page, or ad copy is attracting unqualified prospects before making any campaign changes.
3. If CPL is high but show rate is healthy: campaign problem. Proceed to campaign analysis.
4. If CPL is on target but cost per acquired client is rising: show rate or close rate is degrading downstream. Pull GHL pipeline data.

---

### Check 2: Budget Pacing 💰

For each campaign (and account total):

| Pacing | Status | Action |
|--------|--------|--------|
| < 70% of expected spend | 🔴 ALERT | Campaign likely paused, limited, or budget too high |
| 70–85% | 🟡 WARN | Review for unexpected pauses or IS issues |
| 85–115% | 🟢 ON TRACK | No action needed |
| 115–130% | 🟡 WARN | Monitor — will overspend if trend continues |
| > 130% | 🔴 ALERT | Actively overspending — reduce budget or check bid strategy |

**Monthly pacing math:**
- Days elapsed in month / days in month = % of month consumed
- Actual spend / monthly budget = % of budget consumed
- If spend% >> time%: overpacing. If spend% << time%: underpacing.

**Flag:** Any campaign with 0 spend this week that was active last week.

---

### Check 3: Week-Over-Week Performance 📊

For each campaign, calculate:
- Impressions WoW %
- Clicks WoW %
- CTR WoW (absolute change)
- CPA WoW % (if conversions > 0)
- Conversion volume WoW

**Thresholds for flagging:**

| Metric | Warn | Alert |
|--------|------|-------|
| Impressions drop | >20% | >40% |
| CTR drop | >15% | >25% |
| CPA increase | >20% | >40% |
| Conversions drop | >20% | >40% |
| Cost increase with no conversion increase | >15% | >30% |

**Always calculate:** Account-level blended CPA this week vs last week vs target.

**Segment drops — when WoW looks bad, check if it's:**
1. A single campaign dragging the average
2. A seasonal dip (lower impressions = reduced demand, not account problem)
3. A bid strategy change causing reduced volume during learning

---

### Check 4: Campaign Status & Operational Issues ⚙️

Quick operational pass — things that kill performance silently:

| Check | What To Look For | Action If Found |
|-------|------------------|-----------------|
| Paused campaigns | Any ENABLED campaign that ran last week now shows 0 impressions | Investigate — accidental pause? |
| Ad disapprovals | Any ads with policy violations on ENABLED campaigns | Fix or remove immediately |
| Missing bid strategy | Any campaign on Manual CPC with >30 conversions/month | Flag as optimization opportunity |
| Budget exhaustion | Daily budget hitting limit by early afternoon | Increase budget or check for bid inflation |
| Zero-impression ad groups | Ad groups with 0 impressions, all keywords active | Investigate — possibly paused or no search volume |

---

### Check 5: Bid Strategy Performance 🎯

For Smart Bidding campaigns, assess whether the algorithm is working:

| Signal | Healthy | Needs Attention |
|--------|---------|-----------------|
| CPA vs target (Target CPA strategy) | Within ±20% of target | >30% above target for 2+ weeks |
| ROAS vs target (Target ROAS strategy) | Within ±15% | >25% below target for 2+ weeks |
| Conversion volume (Smart Bidding min) | ≥15 conversions in 30 days | <10 conversions — learning may be impaired |
| Impressions trend after strategy change | Growing week 2–3 post-change | Declining after 3 weeks — reconsider |

**Learning period flag:**
If a bid strategy was changed in the last 1–2 weeks:
- Do NOT optimize — let it learn
- Note: "Campaign X in learning period following [change] on [date] — check again next week"
- Learning typically stabilizes in 1–2 weeks for Target CPA, up to 4 weeks for Target ROAS

**Manual CPC flag:**
Any campaign with > 30 conversions/month still on Manual CPC is leaving Smart Bidding gains on the table. Flag as an opportunity (not urgent, but include in action list).

---

### Check 6: Impression Share Signals 👁️

| Signal | Threshold | Interpretation |
|--------|-----------|----------------|
| Lost IS (Budget) | > 20% | Budget is capping reach — increase budget or reduce bids |
| Lost IS (Rank) | > 25% | Quality Score or bid issue — don't just raise bids |
| Top-of-page IS (brand campaigns) | < 85% | Brand is losing top position — increase brand bids |
| Absolute Top IS drop WoW | > 15% | Competitor aggression or Quality Score drop |

**Only flag IS issues for campaigns that are at or below target CPA.** High-CPA campaigns losing IS is fine — they should be losing share.

---

## Output Format

### Header Block

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WEEKLY CHECK — [CLIENT NAME]
Week: [Mon DD] – [Sun DD, YYYY]
Reviewed: [Today's date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### Section 1: Status at a Glance

```
OVERALL STATUS: 🟢 GOOD / 🟡 WATCH / 🔴 ACTION NEEDED

Tracking:   🟢 / 🟡 / 🔴   [one-line note]
Pacing:     🟢 / 🟡 / 🔴   [X% of budget used, X% of month elapsed]
WoW Perf:   🟢 / 🟡 / 🔴   [CPA this week vs last week vs target]
Operations: 🟢 / 🟡 / 🔴   [disapprovals, pauses, etc.]
Bid Strat:  🟢 / 🟡 / 🔴   [smart bidding health]
```

---

### Section 2: Performance Summary Table

| Campaign | Spend (W) | Conv (W) | CPA (W) | vs Target | WoW Spend | WoW Conv | WoW CPA | Status |
|----------|-----------|----------|---------|-----------|-----------|----------|---------|--------|
| Campaign A | $X | X | $X | -8% | +5% | +12% | -6% | 🟢 |
| Campaign B | $X | X | $X | +22% | -3% | -18% | +19% | 🟡 |

**Footer line (eCommerce/DTC clients):**
```
TOTAL: $X spend | X conversions | $X blended CPA | Target: $X | Budget used: X% ($X of $X/mo)
```

**Footer line (service business clients):**
```
TOTAL: $X spend | X leads | $X CPL | Show rate: X% | Cost per acquired client: $X | Budget used: X% ($X of $X/mo)
```

---

### Section 3: Alerts (Action Required This Week)

For each alert, one block:

```
🔴 [ALERT TYPE] — [Campaign Name or Account]
What: [Specific observation with numbers]
Impact: [Why this matters — cost/conversion impact]
Action: [Exact step to take, in Google Ads]
By: [Today / Tomorrow / End of week]
```

Example:
```
🔴 OVERPACING — Campaign: Emergency Plumbing
What: $1,240 spent in 12 days vs $1,050 expected ($1,800/mo budget)
Impact: On track to spend $3,100 this month — 72% over budget
Action: Reduce daily budget from $60 to $46 in Google Ads → Campaigns → Budget
By: Today
```

---

### Section 4: Watches (Monitor This Week)

```
🟡 [WATCH TYPE] — [Campaign Name]
What: [Observation]
Threshold: [Escalate to alert if X happens]
Check: [When to check again]
```

---

### Section 5: What's Working (Don't Touch)

Brief list of positives to preserve:
```
✅ [Campaign A]: CPA $X, X% below target, stable for 3 weeks — don't change anything
✅ [Pattern]: CTR increased +18% WoW following RSA update on [date] — note for future tests
```

---

### Section 6: This Week's Action List

Numbered, ranked by urgency:

```
THIS WEEK:
1. [Action] — TODAY (🔴 alert)
2. [Action] — TODAY (🔴 alert)
3. [Action] — by Wednesday (🟡 watch escalated)
4. [Action] — by Friday (optimization opportunity)
5. Run /search-terms for [client] — [X days since last run]

NEXT WEEK:
- [Item to revisit]
- [Learning period check — Campaign X on [date]]
```

---

### Section 6.5: Hypothesis Tracker Update

Between the Action List and the Client Status Note, include a brief hypothesis tracker update:

```
ACTIVE TESTS:
Test: [What we're testing — angle, copy, bid strategy, etc.]
Hypothesis: [What we expected to happen]
Status: [Running X days | X conversions | CPA: $X vs control $X]
Decision: [Continue / Declare winner / Kill — and why]
Next: [What launches or changes as a result]

If no tests are active:
⚠️ No active hypothesis on this account. Recommend next test: [specific angle or change to test next week]
```

No test running = no learning. Flag it and propose the next one.

---

### Section 7: Client Status Note (Optional)

One paragraph, 2–4 sentences, non-technical. Copy-paste ready for client email or Slack:

```
[Client name] — Week of [dates]

[Performance sentence: conversions, CPA vs goal, spend]
[Notable positive]
[One thing in progress or being watched]
```

Example:
```
Hoski — Week of Mar 10–16

Strong week — 14 leads at $48 average, 12% below your $55 target. The Emergency Plumbing campaign is performing especially well and we've kept it running at full budget. One campaign is slightly overpacing for the month so we've adjusted the daily budget to land on target by month end.
```

---

## Guardrails

❌ **NEVER** make optimization changes if conversion tracking shows an anomaly — verify tracking first
❌ **NEVER** pause a campaign without flagging it as high-risk and confirming with context
❌ **NEVER** recommend bid strategy changes for campaigns in an active learning period
❌ **NEVER** skip the pacing check — overspend is the fastest way to damage client trust
❌ **NEVER** treat a single bad week as a trend — note "1 week of data — monitor" for all WoW flags

✅ **ALWAYS** check tracking health before any other analysis
✅ **ALWAYS** include specific numbers — "CPA increased" is useless, "$62 vs $48 last week (+29%)" is actionable
✅ **ALWAYS** rank actions by urgency (today vs. this week vs. next week)
✅ **ALWAYS** note known external factors (seasonality, promotions) that explain anomalies
✅ **ALWAYS** flag if /search-terms hasn't been run in more than 7 days

## Red Flags: Escalate Immediately

These signals require immediate escalation outside the standard action list:

| Signal | What It Means | Escalation |
|--------|--------------|------------|
| Conversions drop to zero with normal click volume | Tracking broken | Stop all optimization — run /conversion-tracking-audit |
| Show rate declining 2+ consecutive weeks (service clients) | Lead quality deteriorating upstream | Check follow-up speed in GHL, then check targeting and LP before touching campaigns |
| Cost per acquired client rising even though CPL is stable | Show rate or close rate degrading in GHL pipeline | Pull GHL data — if show rate falling, it is operational not campaign |
| CPA > 2x target for 2+ consecutive weeks | Structural account problem | Escalate to /ppc-account-health-check or /campaign-scaling-expert |
| Budget exhausted by midday consistently | Budget-constrained impression share | Recommend budget increase or reallocation before any bid changes |

---

## Edge Cases

### New Client (First Weekly Check)
No WoW comparison available. Run the check but note "Week 1 — no prior period for WoW comparison." Focus on: tracking verification, pacing, and operational status. Skip WoW deltas.

### Client Made Major Changes Last Week
Note changes prominently at the top. Flag that WoW comparisons may not be meaningful due to the changes. Don't optimize — observe.

### Zero Conversions This Week
Before flagging as a performance issue:
1. Check conversion tracking health (broken tracking mimics zero performance)
2. Check if campaigns were paused/limited
3. Check impression levels (if impressions also dropped, it's a traffic issue, not conversion issue)
4. Only flag as performance alert if tracking is confirmed healthy

### Very Low Activity Account (< $500/week)
WoW variances will be noisy. Lower the alert thresholds (alert at >60% drop rather than >40%). Note: "Low-volume account — small absolute changes create large % swings."

### Multiple Campaign Types in One Account
Separate Search from Performance Max from Display in the performance table. Never blend CPAs across campaign types without noting this. PMax CPA is typically not directly comparable to Search CPA.

### Account Running Multiple Goals (Leads + Calls + Purchases)
Calculate a blended CPA only if all conversions have assigned values. Otherwise, show each conversion type separately in the summary table.

---

## Quality Assurance

Before delivering:
- [ ] Tracking health checked first — no optimizations flagged if tracking is suspect
- [ ] Pacing calculated with exact numbers (spend, expected, %)
- [ ] Every campaign included in performance table (no campaigns omitted)
- [ ] WoW deltas calculated correctly (not vs target, vs PRIOR WEEK)
- [ ] All alerts have specific actions with "by when"
- [ ] Learning period campaigns flagged and excluded from optimization recommendations
- [ ] Client status note is non-technical and copy-paste ready
- [ ] Action list includes reminder to run /search-terms if due
- [ ] Known external factors noted to explain anomalies
