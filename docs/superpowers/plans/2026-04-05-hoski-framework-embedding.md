# Höski Framework Embedding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Embed the Höski Framework as silent default behavior across the marketing manager system via a project-root CLAUDE.md (always-on doctrine) and targeted additions to 8 skill files.

**Architecture:** A new project-root `CLAUDE.md` carries the behavioral defaults that every session inherits automatically. Eight skill files receive targeted inline additions — the specific laws that apply to each specialist role are absorbed as default behavior, not named citations.

**Tech Stack:** Markdown files only. No code changes. No script changes. All edits are content insertions to existing `.md` files.

---

## File Map

| File | Action | What Changes |
|---|---|---|
| `CLAUDE.md` (project root) | Create | Full always-on doctrine |
| `.claude/skills/new-client/SKILL.md` | Edit | Unit economics intake block, calendar setup in 30-day plan, guardrail |
| `.claude/skills/creative-strategist/SKILL.md` | Edit | Channel variable section, creative hierarchy, 7 angles, 5 stages, testing protocol, whitelisting |
| `.claude/skills/meta-strategist/SKILL.md` | Edit | Funnel architecture with budget splits, campaign structure, broad-first rule, whitelisting |
| `.claude/skills/meta-manager/SKILL.md` | Edit | Creative fatigue thresholds, hypothesis tracker as required output, weekly rhythm note |
| `.claude/skills/weekly-check/SKILL.md` | Edit | Hypothesis tracker section in output format, red flags escalation table |
| `.claude/skills/monthly-report/SKILL.md` | Edit | MER as lead metric in internal analysis and client report, red flags table, monthly optimization checklist |
| `.claude/skills/cro-strategist/SKILL.md` | Edit | Landing page as primary variable section before Step 0, 5 LP requirements in Step 2 |
| `.claude/skills/campaign-scaling-expert/SKILL.md` | Edit | 20-30% scaling rule in Tier 1, cost cap strategy in Lever B, CPA spike threshold in guardrails |

---

## Task 1: Create Project-Root CLAUDE.md

**Files:**
- Create: `CLAUDE.md` (at project root `/Users/bishalbarua/Bishal/AI/antigravity/Hoski Marketing Manager/CLAUDE.md`)

- [ ] **Step 1: Create the file with full always-on doctrine**

Write the following content exactly:

```markdown
# Höski Marketing Manager — Operating Doctrine

Every agent, skill, and analysis in this system operates under the following defaults. These are not guidelines to reference — they are the default way we think and work.

---

## The Primary Variable Rule

**Meta Ads:** Creative is the primary variable. Targeting is commoditized — broad targeting works, Advantage+ works, the algorithm finds the audience. All optimization effort goes to angles, hooks, formats, and creative volume. When Meta underperforms, look at creative first.

**Google Ads:** Landing page is the primary variable. Keywords constrain intent, ad copy is bounded by character limits — but what happens after the click determines whether the business makes money. When Google underperforms and tracking is confirmed healthy, the landing page is the first place to look.

---

## Unit Economics First

Before recommending any spend, scaling any campaign, or setting any target, the following must be known:

- **AOV** — average order value (or average transaction value for lead gen)
- **COGS** — cost of goods sold including shipping and fulfillment
- **Contribution Margin** — what's left after COGS
- **Breakeven CPA** — (AOV × margin%) = the maximum you can pay and not lose money
- **Target CPA** — 70-80% of breakeven (never at breakeven — the buffer is the profit)
- **LTV:CAC Ratio** — below 2:1 is a warning, below 1:1 is a fire

If these numbers are not in `client-info.md`, surface that gap immediately. Never set a CPA target without running the math.

---

## Metrics Hierarchy

**MER (Media Efficiency Ratio) = Total Revenue / Total Ad Spend**

MER is the business truth. It is the lead metric for any business-level decision about whether marketing is working.

Platform ROAS is for intra-platform optimization only: which campaign to scale, which to kill, whether a bid strategy is working. Never use platform ROAS to make a business-level spend decision.

If MER is healthy and platform ROAS looks weak: attribution is noisy, the business is fine.
If MER is declining and platform ROAS looks strong: there is a real problem — likely over-retargeting and under-prospecting.

---

## Funnel Architecture Defaults

Budget splits unless the client's vertical or data says otherwise:

- **60-70% Prospecting** — awareness and new customer acquisition
- **20-25% Retargeting** — convert warm traffic
- **10-15% Retention** — email, SMS, loyalty (where margin compounds)

Vertical adjustments:
- DTC eCommerce: skews Meta-heavy (70% Meta, 25% Google Shopping, 5% testing)
- Local Services: skews Google Search-heavy (70% Google, 20% Meta awareness/retargeting, 10% LSA)
- B2B Lead Gen: 40% LinkedIn, 30% Google, 30% Meta retargeting

First-order profitability is the North Star. The goal from ads is to acquire customers who are profitable on the first order. Retention channels (email, SMS) are where repeat purchase margin compounds.

---

## Calendar Defaults

**Tier 1 Events** (BFCM, Q5, Valentine's Day, Mother's Day): require a 4-week runway.
- Week -4: Creative production begins, briefs to creators
- Week -3: Email sequences drafted, landing pages built
- Week -2: Creatives in review, campaigns structured, audiences built
- Week -1: Everything scheduled, test runs live, final QA
- Week 0: Launch, monitor hourly for first 48 hours

If a Tier 1 event is within 4 weeks and prep has not started: flag it immediately. Do not wait to be asked.

**Q5 (Dec 26 - Jan 7):** Never a pause period. CPMs crater while consumers are home with gift cards. Scale into it.

Reactive marketing is not acceptable. If work is happening the week before an event, something went wrong.

---

## Weekly Operating Rhythm

- **Monday:** Review weekend performance. Kill underperformers. Scale winners. Plan creative needs for the week.
- **Tuesday-Wednesday:** Creative production. Brief creators. New assets in pipeline.
- **Thursday:** Launch new test batch (minimum 4-5 new creatives).
- **Friday:** Performance review. Update hypothesis tracker. Update marketing calendar. Flag red flags.

---

## Creative Testing Defaults

- Each creative gets **$100-150 budget**, minimum **72-hour run** before any kill decision
- Measure: outbound CTR, hook rate (3-second video view %), cost per result
- Kill anything below threshold. Move winners to Evergreen.
- Minimum **4-5 new creatives per test cycle** — if all creatives look the same, nothing was learned
- Budget increase on winners: **20-30% every 3-5 days**, never overnight

---

## Hypothesis Tracker Default

Every test must have these five fields documented:

| Week | Hypothesis | Test | Result | Learning | Next Action |
|---|---|---|---|---|---|

No test without a hypothesis. No result without a learning. No learning without a next action.

---

## Scaling Defaults

- Budget increases: 20-30% every 3-5 days on winning campaigns. Never overnight.
- CPA spike threshold: if CPA is more than 30% above target for 3+ consecutive days during scaling, pull back and diagnose before continuing.
- **Cost cap strategy for stable scaling:** Set CPA or ROAS target, give the campaign 3-5x the normal daily budget. It only spends when it can hit the target. This prevents runaway spend during scaling.

---

## 5 Stages of Awareness

Every piece of creative targets a specific awareness stage. Default map:

| Stage | What They Know | What the Creative Does |
|---|---|---|
| Unaware | Nothing about the problem | Educate. Surface the problem. |
| Problem Aware | They have a problem | Agitate the problem. Introduce that a solution exists. |
| Solution Aware | Solutions exist | Position the product as the best solution. |
| Product Aware | The product exists | Differentiate. Social proof. Offer. |
| Most Aware | Ready to buy | Close. Urgency. Best deal. |

Cold prospecting creative targets stages 1-3.
Retargeting creative targets stages 4-5.

Default diagnosis when prospecting underperforms: check whether creative is stuck at stages 4-5 and skipping the awareness-building stages.

---

## Red Flags Requiring Immediate Action

| Red Flag | What It Means | What to Do |
|---|---|---|
| CPA rising 3 weeks in a row | Creative fatigue or market shift | New creative batch. Test new angles. Check competitors. |
| MER declining while platform ROAS is stable | Over-retargeting. Not acquiring new customers. | Check new customer %. Shift budget to prospecting. |
| AOV dropping | Customers buying cheaper items or less per order | Review product mix. Test bundles. Check offer structure. |
| Email open rates below 20% | List health issues or subject line problems | Clean list. Segment. A/B test subject lines. |
| Client asking "what are you doing?" | Communication gap | Send a proactive update immediately. Don't wait for the next scheduled report. |

---

## Decision Mindset

- **Data over feelings.** If you cannot point to the specific data that supports a decision, it is a guess, not a decision.
- **Test, do not debate.** Opinions are free. Data costs $150 and 72 hours.
- **Think like an owner.** Every dollar spent is a dollar the client earned. Treat it that way.
- **Speed wins.** The team that tests 20 creatives a month beats the team that tests 5. Don't be reckless, but don't be slow.
```

- [ ] **Step 2: Verify the file was created and is readable**

Run: `cat "CLAUDE.md" | head -5`
Expected: First line reads `# Höski Marketing Manager — Operating Doctrine`

- [ ] **Step 3: Commit**

```bash
cd "/Users/bishalbarua/Bishal/AI/antigravity/Hoski Marketing Manager"
git add CLAUDE.md
git commit -m "feat: add project CLAUDE.md with Höski Framework operating doctrine"
```

---

## Task 2: Update new-client/SKILL.md — Unit Economics + Calendar

**Files:**
- Modify: `.claude/skills/new-client/SKILL.md`

The file currently has section `**1d. What's the typical customer value?**` at around line 67. This section partially captures unit economics but is missing the full Höski formula. It also has a `### Week 1: Foundation` section in the 30-day plan (around line 479) that needs the 12-month calendar added.

- [ ] **Step 1: Expand section 1d with the full unit economics block**

Find the text:
```
**1d. What's the typical customer value?**
- Lead gen: What's a lead worth? What % close? What's average transaction size?
- eCommerce: Average order value? Repeat purchase rate? LTV?

This unlocks the maximum viable CPA calculation:
```
Max CPA = Avg Transaction Value × Gross Margin × Lead-to-Close Rate
```
Flag if the client doesn't know — they need to know their numbers.
```

Replace with:
```
**1d. What's the unit economics?**

For every client, gather these numbers in Week 1. Without them, any CPA target is a guess.

- **AOV** (Average Order Value) — what a customer spends per transaction
- **COGS** — cost of goods sold including shipping and fulfillment
- **Contribution Margin** — AOV minus COGS and fulfillment (what's left)
- **Breakeven CPA** — (AOV × contribution margin %) = maximum you can pay per acquisition and not lose money
- **Target CPA** — set at 70-80% of breakeven, not at breakeven itself. The buffer is the profit.
- **LTV:CAC Ratio** — customer lifetime value divided by acquisition cost. Below 2:1 is a warning. Below 1:1 is a fire.

For lead gen clients, the calculation chain is:
```
Max CPA = Avg Transaction Value × Gross Margin × Lead-to-Close Rate
```

For eCommerce clients:
```
Breakeven CPA = AOV × Contribution Margin %
Target CPA = Breakeven CPA × 0.75  (25% profit buffer)
```

If the client doesn't know their margins or AOV: flag this immediately. Do not set a CPA target until the math is done. Document the numbers (or the gap) in client-info.md before leaving the onboarding session.
```

- [ ] **Step 2: Add 12-month calendar setup to Week 1 of the 30-day plan**

Find the text:
```
### Week 1: Foundation
**Goal:** Access, tracking, and first campaign live.

- Day 1–2: Finalize all account access
- Day 2–3: Conversion tracking installed and verified
- Day 3–5: Build first campaign (using `/ads-strategy-architect` for full strategy)
- Day 5–7: Campaign live — first data starts flowing

**Deliverable:** Campaign live, tracking verified, client confirmation sent.
```

Replace with:
```
### Week 1: Foundation
**Goal:** Access, tracking, first campaign live, and 12-month calendar drafted.

- Day 1–2: Finalize all account access
- Day 2–3: Conversion tracking installed and verified
- Day 3–4: Draft 12-month marketing calendar — map Tier 1 events (BFCM, Q5, Valentine's Day, Mother's Day), Tier 2 brand-specific dates, and Tier 3 opportunistic moments. Note any Tier 1 event within 4 weeks and flag prep status immediately.
- Day 3–5: Build first campaign (using `/ads-strategy-architect` for full strategy)
- Day 5–7: Campaign live — first data starts flowing

**Deliverable:** Campaign live, tracking verified, 12-month calendar drafted in client folder, client confirmation sent.
```

- [ ] **Step 3: Add unit economics guardrail**

Find the guardrails section containing:
```
❌ **NEVER** set a target CPA before understanding what a customer is worth to the business
```

Add a new line directly after it:
```
❌ **NEVER** set a target CPA at the breakeven number — the target must be 70-80% of breakeven to preserve a profit margin
```

- [ ] **Step 4: Commit**

```bash
cd "/Users/bishalbarua/Bishal/AI/antigravity/Hoski Marketing Manager"
git add .claude/skills/new-client/SKILL.md
git commit -m "feat: add unit economics formula, calendar setup, and profit-buffer guardrail to new-client skill"
```

---

## Task 3: Update creative-strategist/SKILL.md — Channel Variable + Full Creative System

**Files:**
- Modify: `.claude/skills/creative-strategist/SKILL.md`

The file currently has Step 0 (Load Context) followed by Step 1 (Identify Mode). Additions go: a new Channel Context section before Step 0, and a new Creative System section after Step 2 (Context Check).

- [ ] **Step 1: Add the channel variable section before Step 0**

Find the text:
```
## Step 0: Load Context
```

Insert the following block immediately before it:

```markdown
## Channel Context: What the Primary Variable Is

**For Meta creative work (Modes C/D):** Creative is the primary variable. Targeting is commoditized — the algorithm finds the audience if the creative is right. All effort goes to angle, hook, format, and volume. The creative IS the strategy.

**For Google RSA work (Modes A/B):** Ad copy is a support function, not the primary lever. The landing page is the primary variable for Google — the copy gets the click, the page determines whether the business makes money. When diagnosing Google underperformance (and tracking is healthy), always check message match and landing page before blaming ad copy.

This distinction changes what you optimize first.

---
```

- [ ] **Step 2: Add the full creative system after Step 2 (Context Check)**

Find the text:
```
## Step 3:
```
(This is whatever section follows the Context Check in the file. Insert before it.)

Actually find the exact text after the Context Check section ends. Look for the heading `## Step 3` or equivalent that follows Step 2. Insert the following block immediately before that heading:

```markdown
## Creative System Defaults

### The Creative Hierarchy

Optimization effort goes in this order. The money is in the top two.

```
1. Angle (what you're saying — which awareness stage, which emotion, which problem)
2. Hook (first 3 seconds of video / first line of copy / image scroll-stop element)
3. Format (video, static, carousel, UGC, founder-led)
4. Offer (discount, bundle, free shipping, urgency)
5. Targeting (broad, lookalike, interest)
```

Most teams obsess over #5. Never spend more time on targeting than on angle and hook.

### The 7 Creative Angles

Every Meta creative brief must specify which angle it uses. Every batch must test more than one.

| Angle | When to Use | Example Structure |
|---|---|---|
| Problem-Solution | Product solves a clear pain point | "Tired of [problem]? Here's what changed." |
| Social Proof / Testimonial | Product has real reviews and results | Customer video, screenshot of review |
| Founder Story | Brand has a compelling origin | Founder on camera, authentic, unpolished |
| Educational | Complex product or new category | "3 things you didn't know about [product]" |
| Urgency / Scarcity | Sale event or limited inventory | Countdown, "only X left", seasonal push |
| Lifestyle / Aspiration | Premium or fashion brand | Product in context, aspirational setting |
| UGC / Organic Feel | DTC eCommerce, younger demographic | Shot on phone, no branding, native to feed |

No test batch where all creatives use the same angle. That is not testing — that is repetition.

### 5 Stages of Awareness — Mapped to Creative

Every brief must specify which awareness stage the creative targets.

| Stage | Cold/Warm | What the Creative Does |
|---|---|---|
| Unaware | Cold only | Educate. Surface the problem. Do not mention the product in the first 3 seconds. |
| Problem Aware | Cold | Agitate the problem hard. Introduce that a solution exists. |
| Solution Aware | Cold/Warm | Position the product as the best solution among alternatives. |
| Product Aware | Warm | Differentiate. Social proof. Handle objections. Make an offer. |
| Most Aware | Retargeting | Close. Urgency. Best deal. Direct CTA. |

Prospecting campaigns target stages 1-3. Retargeting campaigns target stages 4-5.

Default diagnosis when prospecting creative is underperforming: it is probably targeting stages 4-5 and assuming the audience already knows they have a problem.

### Creative Testing Protocol

- **Budget per creative:** $100-150
- **Minimum run time:** 72 hours before any kill decision
- **Metrics to evaluate:** outbound CTR, hook rate (3-second video view %), cost per result
- **Kill threshold:** CPA at 3x target after $150 spend
- **Move to Evergreen:** any creative that clears target CPA threshold after the test period
- **Batch minimum:** 4-5 new creatives per test cycle — test multiple angles in every batch

### Whitelisting

Running ads from the brand handle signals "ad." Running the same creative from a founder's personal account or an influencer's account looks native and authentic. Use whitelisting when:

- The brand has a strong founder story
- The product benefits from personal endorsement
- UGC-heavy accounts where creator content outperforms branded content
- Branded content is showing frequency-driven fatigue

How it works: Creator grants ad permissions to the brand's ad account. The ad runs under the creator's handle. Engagement accumulates on their post (social proof compounds over time).

---
```

- [ ] **Step 3: Commit**

```bash
cd "/Users/bishalbarua/Bishal/AI/antigravity/Hoski Marketing Manager"
git add .claude/skills/creative-strategist/SKILL.md
git commit -m "feat: add channel variable context, creative hierarchy, 7 angles, 5 stages, testing protocol, and whitelisting to creative-strategist skill"
```

---

## Task 4: Update meta-strategist/SKILL.md — Funnel Architecture + Broad First + Whitelisting

**Files:**
- Modify: `.claude/skills/meta-strategist/SKILL.md`

The file has a Step 4 (Produce the Strategy) section that lists the 5 phases. The Campaign Architecture phase (phase 2 in the list) needs the standard funnel architecture and campaign structure appended. The Guardrails section needs the broad-first rule and whitelisting guardrail added.

- [ ] **Step 1: Add funnel architecture and campaign structure after Step 5 (Manager Brief)**

Find the text:
```
## Guardrails
```

Insert the following block immediately before it:

```markdown
## Funnel Architecture and Campaign Structure Defaults

Every new Meta account build and every full restructure outputs this structure unless client data justifies a deviation. Document the deviation rationale in the Manager Brief if the standard structure is not used.

### Funnel Architecture

```
┌─────────────────────────────────────────────┐
│  TOP OF FUNNEL (Prospecting)                │
│  Goal: Awareness + qualified new customers  │
│  Campaigns: Broad, DCT, Advantage+, white-  │
│             listed creative                 │
│  Budget: 60-70% of total Meta spend         │
├─────────────────────────────────────────────┤
│  MIDDLE (Retargeting)                       │
│  Goal: Convert warm traffic                 │
│  Campaigns: DPA, social proof, testimonials │
│  Window: 7-14 days (short cycles), up to   │
│           30 days (longer consideration)    │
│  Budget: 20-25% of total Meta spend        │
├─────────────────────────────────────────────┤
│  BOTTOM (Retention)                         │
│  Goal: Repeat purchase + LTV               │
│  Channels: Email/SMS (suppressed from TOF)  │
│  Budget: 10-15% of total Meta spend        │
└─────────────────────────────────────────────┘
```

### Standard Campaign Structure

```
PROSPECTING
  ├── Testing (CBO, $100-150/creative per ad set, broad targeting)
  ├── Evergreen (winning creatives from testing, scaled budget)
  └── Cost Cap (CPA/ROAS target set, budget inflated 3-5x daily target)

RETARGETING
  ├── DPA (7-14 day window, dynamic product catalog)
  └── Custom Audiences (site visitors, add-to-cart, email list, video viewers)

RETENTION
  └── Email/SMS list excluded from prospecting (prevent cannibalizing owned channels)
```

### Broad Targeting First

Start every new account with broad targeting before considering interest stacking or lookalikes. The algorithm is smarter than manual interest segmentation at scale. Broad + strong creative outperforms interest-stacked + weak creative consistently.

Never recommend complex interest stacking before testing broad. If the client pushes back, document the test: broad vs. interest-stacked, same creative, same budget, 2-week run.

### Whitelisting as a Strategic Tactic

Recommend whitelisting in the creative brief and Manager brief when any of these conditions apply:

- The brand has a founder with a story worth telling
- The product benefits from personal endorsement (health, lifestyle, beauty)
- UGC content has outperformed branded content in testing
- Branded content frequency is rising and CTR is declining

Document in the Manager brief: which handle to whitelist, which creative to run under it, and how to set up ad permissions.

---
```

- [ ] **Step 2: Commit**

```bash
cd "/Users/bishalbarua/Bishal/AI/antigravity/Hoski Marketing Manager"
git add .claude/skills/meta-strategist/SKILL.md
git commit -m "feat: add funnel architecture, standard campaign structure, broad-first rule, and whitelisting to meta-strategist skill"
```

---

## Task 5: Update meta-manager/SKILL.md — Creative Fatigue + Hypothesis Tracker + Weekly Rhythm

**Files:**
- Modify: `.claude/skills/meta-manager/SKILL.md`

- [ ] **Step 1: Add creative fatigue thresholds to Step 4 (Creative Performance check)**

Find the text:
```
**Creative priority:** Check 3 (creative fatigue) is the most important monitoring signal on Meta. When WoW performance deteriorates, always check frequency before diagnosing any other cause.
```

Add the following block immediately after it:

```markdown
**Creative fatigue thresholds:**

| Signal | Threshold | Status |
|---|---|---|
| Frequency (7-day) | > 3.0 | 🟡 Monitor — refresh incoming |
| Frequency (7-day) | > 4.5 | 🔴 Fatigue — brief to creative-strategist now |
| WoW CTR drop with frequency > 3 | > 15% drop | 🔴 Fatigue confirmed — replace this week |
| Hook rate (3-sec video view %) | < 20% | 🟡 Hook is failing — creative review needed |
| Hook rate (3-sec video view %) | < 10% | 🔴 Kill this creative — below minimum viable threshold |

When creative fatigue is diagnosed (🔴 status): add an escalation block routing to `/creative-strategist` with a brief that includes: the fatigued creative names, the angle each used, the frequency and CTR data, and a request for a new test batch using different angles.
```

- [ ] **Step 2: Add hypothesis tracker as a required output section in Step 6**

Find the text:
```
End every full weekly session with a client status note (2-4 sentences, non-technical, copy-paste ready for client communication).
```

Add the following block immediately before it:

```markdown
**Hypothesis Tracker Update (required for Mode A — Full Weekly Session):**

Append to or create the hypothesis tracker in `clients/[client folder]/notes/hypothesis-tracker.md`. One row per test that ran or concluded this week:

| Week | Hypothesis | Test | Result | Learning | Next Action |
|---|---|---|---|---|---|
| [Week of date] | [What we expected] | [What we ran] | [CTR, CPA, hook rate — specific numbers] | [What the data tells us] | [Exact next step] |

If no new test concluded this week: note "No tests concluded this week" and document what is currently running and when results are expected.

```

- [ ] **Step 3: Add weekly rhythm note to Step 0**

Find the text:
```
## Step 0: Identify Mode
```

Add the following block immediately after the `## Step 0: Identify Mode` heading (before the Mode A description):

```markdown
**Weekly rhythm context:** Monday sessions are the primary operational review (Mode A). Thursday is when new test batches launch. Friday is the hypothesis tracker update. If this session is happening mid-week, focus on the specific job at hand (pacing check, creative issue, brief execution) rather than running the full weekly sweep.

```

- [ ] **Step 4: Commit**

```bash
cd "/Users/bishalbarua/Bishal/AI/antigravity/Hoski Marketing Manager"
git add .claude/skills/meta-manager/SKILL.md
git commit -m "feat: add creative fatigue thresholds, hypothesis tracker output, and weekly rhythm context to meta-manager skill"
```

---

## Task 6: Update weekly-check/SKILL.md — Hypothesis Tracker Section + Red Flags Table

**Files:**
- Modify: `.claude/skills/weekly-check/SKILL.md`

The output format currently has 7 sections. A new Section 6.5 (Hypothesis Tracker Update) needs to be inserted between Section 6 (Action List) and Section 7 (Client Status Note). The red flags escalation table from the framework needs to be added to the Quality Assurance section.

- [ ] **Step 1: Add Hypothesis Tracker as a new output section**

Find the text:
```
### Section 7: Client Status Note (Optional)
```

Insert the following block immediately before it:

```markdown
### Section 6.5: Hypothesis Tracker Update

Update or create `clients/[client folder]/notes/hypothesis-tracker.md` as part of every weekly check. One row per test that ran or concluded this week.

```
| Week | Hypothesis | Test | Result | Learning | Next Action |
|---|---|---|---|---|---|
| [Week of date] | [What we expected] | [What we ran] | [Metric — specific numbers] | [What the data shows] | [Exact next step] |
```

**Rules:**
- If a test is still running: document it as in-progress with expected conclusion date
- If no tests ran this week: note it explicitly and identify what should be tested next week
- If a result came in: document the learning and the next action before closing the session — never leave a result without a follow-up

This is not optional. An account that is not compounding learnings week over week is not being managed — it is being monitored.

---
```

- [ ] **Step 2: Add red flags escalation table to the Quality Assurance section**

Find the text:
```
## Quality Assurance

Before delivering:
```

Insert the following block immediately before the `## Quality Assurance` heading:

```markdown
## Red Flags: Escalate Immediately

These patterns require immediate action beyond the standard weekly check. If any are present, add them to the Action List as Priority 1 items and note the escalation path.

| Red Flag | What It Signals | Escalation |
|---|---|---|
| CPA rising for 3+ consecutive weeks | Creative fatigue or structural shift | New creative batch + run `/campaign-scaling-expert` |
| MER declining while Google ROAS is stable | Over-retargeting, not acquiring new customers | Check new customer %. Increase prospecting allocation. |
| MER declining while Meta ROAS is stable | Attribution overlap or organic cannibalization | Review channel split. Pull new customer % from Shopify. |
| AOV dropping month-over-month | Product mix shift or offer structure problem | Review top-selling products. Check if bundle offers are in play. |
| Zero new keyword negatives for 3+ weeks | Search terms sweep has been skipped | Run `/search-terms` immediately |
| Conversion tracking showed anomaly 2+ weeks ago and is still unresolved | Tracking issue left open | Stop all optimization. Fix tracking first. |

---
```

- [ ] **Step 3: Commit**

```bash
cd "/Users/bishalbarua/Bishal/AI/antigravity/Hoski Marketing Manager"
git add .claude/skills/weekly-check/SKILL.md
git commit -m "feat: add hypothesis tracker section and red flags escalation table to weekly-check skill"
```

---

## Task 7: Update monthly-report/SKILL.md — MER as Lead Metric + Dashboard + Optimization Checklist

**Files:**
- Modify: `.claude/skills/monthly-report/SKILL.md`

Three additions: (1) MER calculation added to Section A of the Internal Analysis Framework, (2) MER Dashboard table added to the client report template, (3) Monthly optimization checklist and red flags added to the Quality Assurance section.

- [ ] **Step 1: Add MER to Section A of the Internal Analysis Framework**

Find the text:
```
### Section A: Account-Level Summary

Calculate and note:
- Total spend this month vs prior month vs budget (pacing %)
- Total conversions this month vs prior month
- Blended CPA this month vs prior month vs target
- For eCommerce: total revenue, ROAS this month vs prior month vs target
- Overall MoM direction: improving / declining / stable
```

Replace with:
```
### Section A: Account-Level Summary

Calculate and note:
- **MER (Media Efficiency Ratio)** = Total Revenue / Total Ad Spend (all channels combined, pulled from Shopify or source of truth + total spend across all platforms). This is the lead metric. Document MER direction: improving / declining / stable.
- Total spend this month vs prior month vs budget (pacing %)
- Total conversions this month vs prior month
- Blended CPA this month vs prior month vs target
- For eCommerce: total revenue, ROAS this month vs prior month vs target
- New customer % this month (are we acquiring or just retargeting?)
- Email/SMS revenue % of total revenue (is retention carrying its weight?)
- Overall MoM direction: improving / declining / stable

**MER interpretation:**
- MER healthy, platform ROAS weak: attribution is noisy, business is fine
- MER declining, platform ROAS strong: real problem — likely over-retargeting and under-prospecting
- MER declining, CPA rising, new customer % falling: structural issue — escalate to strategist
```

- [ ] **Step 2: Add MER Dashboard to the client report template**

Find the text:
```
## Month at a Glance

[Use a metrics table. Adapt columns to lead gen vs. eCommerce.]
```

Add the following block immediately after that heading (before the Lead Gen Table):

```markdown
### Business Performance Dashboard (eCommerce only — adapt for lead gen where noted)

| Metric | This Month | Prior Month | Change | Source |
|---|---|---|---|---|
| MER (Total Revenue / Total Ad Spend) | X.Xx | X.Xx | +/-X% | Shopify + all spend |
| Total Ad Spend (all channels) | $X | $X | +/-X% | All platforms |
| New Customer % | X% | X% | +/-X pts | Shopify / Triple Whale |
| Average Order Value | $X | $X | +/-X% | Shopify |
| Email Revenue % of Total | X% | X% | +/-X pts | Klaviyo |

This table is the business-level view. The campaign tables below are the platform-level view.

```

- [ ] **Step 3: Add monthly optimization checklist and red flags to Quality Assurance**

Find the text:
```
## Quality Assurance

Before finalizing:
```

Insert the following block immediately before the `## Quality Assurance` heading:

```markdown
## Monthly Optimization Checklist

Complete before finalizing the report and before closing out the month:

- [ ] Creative refresh confirmed (new batch launched in the past 2-3 weeks — if not, flag in "Plan for Next Month")
- [ ] 12-month marketing calendar reviewed and updated (any Tier 1 events in next 60 days with prep status documented)
- [ ] Email flows audited (welcome, abandoned cart, post-purchase performing at expected rates)
- [ ] Competitor ad libraries checked (Meta Ad Library + Google — any new angles or offers from direct competitors)
- [ ] Landing page performance reviewed (bounce rate, conversion rate — flag if CVR dropped more than 15% MoM)
- [ ] Hypothesis tracker updated with all concluded tests from the month
- [ ] Customer cohort analysis: are repeat purchase rates improving or declining?
- [ ] MER trend: is the blended number moving in the right direction?

## Red Flags Requiring Escalation in the Report

If any of these are present, they must appear in "What We're Working On" with a specific action plan — not buried in internal notes.

| Red Flag | Required Response in Report |
|---|---|
| MER declining for 2+ consecutive months | Name it. Explain prospecting vs. retargeting imbalance. State the fix. |
| CPA rising 3+ consecutive weeks | Name the creative fatigue. State the new creative batch plan and timeline. |
| AOV dropping | Name the product mix shift. State whether bundles or offers are being tested. |
| New customer % below 30% | Flag over-retargeting. State the prospecting budget reallocation plan. |
| Email open rate below 20% | Flag list health. State segmentation or cleaning plan. |

---
```

- [ ] **Step 4: Commit**

```bash
cd "/Users/bishalbarua/Bishal/AI/antigravity/Hoski Marketing Manager"
git add .claude/skills/monthly-report/SKILL.md
git commit -m "feat: add MER as lead metric, business dashboard, monthly optimization checklist, and red flags to monthly-report skill"
```

---

## Task 8: Update cro-strategist/SKILL.md — Landing Page as Primary Variable

**Files:**
- Modify: `.claude/skills/cro-strategist/SKILL.md`

A new "Channel Context" section goes before Step 0. The 5 LP requirements get added as a mandatory pre-check gate in Step 2. A guardrail is added for cold traffic to unoptimized pages.

- [ ] **Step 1: Add Channel Context section before Step 0**

Find the text:
```
## Step 0: Identify Mode
```

Insert the following block immediately before it:

```markdown
## Channel Context: Why Landing Pages Matter More for Google

**Google Ads:** The landing page is the primary variable. Ad copy is constrained by character limits and keyword relevance requirements — there is limited creative surface area. The page is where conversion happens or doesn't. When a Google campaign has healthy CTR but poor CVR, the landing page is almost always the diagnosis, not the ad.

**Meta Ads:** Landing pages matter, but they are secondary to creative. If Meta performance is weak, check creative first. If creative is strong and CVR is still poor, then the landing page is the issue.

This skill is critical for Google campaigns. It is important but secondary for Meta campaigns.

**The 5 non-negotiables for any landing page receiving cold traffic:**
1. Clear hero image or video above the fold — the product or outcome is immediately visible
2. One primary CTA — not three, not two, one. Ambiguity kills conversion.
3. Social proof within the first scroll (reviews, logos, press coverage, number of customers)
4. Trust signals below the hero (shipping policy, returns, guarantees, certifications)
5. Mobile-first design — 70%+ of traffic is mobile; if the mobile experience is broken, nothing else matters

Any LP missing one or more of these five elements is not ready for paid traffic.

---
```

- [ ] **Step 2: Add 5 LP requirements check gate to Step 2**

Find the text:
```
If required inputs are missing, ask with a numbered list. Do not produce a generic audit when specificity is available.
```

Add the following block immediately after it:

```markdown
**Pre-audit gate — 5 non-negotiables check:**

Before running a full audit, do a quick pass on these five elements. If any are missing, flag them at the top of the audit output as "Blocking Issues" before proceeding to detailed analysis. These are not Tier 1 fixes — they are launch blockers.

| Element | Present? | Notes |
|---|---|---|
| Clear hero above fold (product/outcome visible) | Yes / No / Partial | |
| Single primary CTA (not multiple competing CTAs) | Yes / No | |
| Social proof within first scroll | Yes / No | |
| Trust signals (shipping, returns, guarantees) | Yes / No | |
| Mobile-first design (check mobile view) | Yes / No / Partial | |

Any "No" on this checklist is more important than any Tier 1 fix in the detailed audit.

```

- [ ] **Step 3: Add cold traffic guardrail**

Find the guardrails section containing:
```
❌ Never recommend a homepage as a landing page for PPC traffic (except navigational/brand)
```

Add a new line directly after it:
```
❌ Never approve cold traffic going to a landing page missing any of the 5 non-negotiables (hero, single CTA, social proof, trust signals, mobile-first) — flag as a launch blocker, not a future optimization
```

- [ ] **Step 4: Commit**

```bash
cd "/Users/bishalbarua/Bishal/AI/antigravity/Hoski Marketing Manager"
git add .claude/skills/cro-strategist/SKILL.md
git commit -m "feat: add channel context (LP as primary variable for Google), 5 non-negotiables gate, and cold traffic guardrail to cro-strategist skill"
```

---

## Task 9: Update campaign-scaling-expert/SKILL.md — Scaling Rules + Cost Cap + CPA Spike Threshold

**Files:**
- Modify: `.claude/skills/campaign-scaling-expert/SKILL.md`

Note: The skill description frontmatter uses `name: campaign-scale-analyzer`. The internal title is "Google Ads Campaign Scale Analyzer." Additions go into Phase 2 (Tier 1 Strategic Action column), Lever B (Bid Strategy Optimization), and the Guardrails section.

- [ ] **Step 1: Add precise scaling rules to Phase 2 Tier 1 row**

Find the text:
```
| **Tier 1** | Scale Now | CPA ≤ target AND conversions ≥ 20 | Increase budget 20–30%, test bid strategy upgrades |
```

Replace with:
```
| **Tier 1** | Scale Now | CPA ≤ target AND conversions ≥ 20 | Increase budget 20-30% every 3-5 days (never overnight). Monitor CPA daily. If CPA spikes more than 30% above target for 3+ consecutive days, pull back and diagnose before continuing. |
```

- [ ] **Step 2: Add cost cap strategy to Lever B**

Find the text:
```
#### Lever B — Bid Strategy Optimization
Evaluate current bid strategy against conversion volume:

| Conversions (30d) | Recommended Bid Strategy | Rationale |
|---|---|---|
| < 15 | Maximize Conversions (no target) | Smart bidding needs data; constraints hurt learning |
| 15–30 | Target CPA (set 20% above actual CPA) | Enough data; don't over-constrain |
| > 30 | Target CPA at goal OR Target ROAS | Full smart bidding leverage |

Flag campaigns running Manual CPC with > 30 conversions — this is a clear missed scaling opportunity.
```

Replace with:
```
#### Lever B — Bid Strategy Optimization
Evaluate current bid strategy against conversion volume:

| Conversions (30d) | Recommended Bid Strategy | Rationale |
|---|---|---|
| < 15 | Maximize Conversions (no target) | Smart bidding needs data; constraints hurt learning |
| 15–30 | Target CPA (set 20% above actual CPA) | Enough data; don't over-constrain |
| > 30 | Target CPA at goal OR Target ROAS | Full smart bidding leverage |

Flag campaigns running Manual CPC with > 30 conversions — this is a clear missed scaling opportunity.

**Cost Cap Strategy for Stable Scaling (Tier 1 campaigns ready to scale):**

When a Tier 1 campaign is ready to scale but there is risk of CPA inflation at higher budgets, use the cost cap approach:
1. Set a CPA target (or ROAS target) on the campaign equal to the target CPA
2. Set the daily budget to 3-5x the normal daily budget
3. The campaign only spends when it can acquire at or below the target — self-regulating spend
4. Monitor for 3-5 days. If spend is too constrained (campaign not spending), the target is too aggressive — loosen by 10-15%.

This prevents runaway spend while scaling and avoids the need for manual bid adjustments.
```

- [ ] **Step 3: Add CPA spike threshold to Guardrails**

Find the text:
```
❌ **NEVER** recommend increasing budget on a campaign with CPA > 1.3× target without first identifying why.
```

Add two new lines directly after it:
```
❌ **NEVER** increase budget by more than 30% in a single day — budget increases above 30% reset Smart Bidding learning. Use 20-30% increments every 3-5 days.
❌ **NEVER** continue scaling when CPA has been more than 30% above target for 3+ consecutive days — pause, diagnose, then resume.
```

- [ ] **Step 4: Commit**

```bash
cd "/Users/bishalbarua/Bishal/AI/antigravity/Hoski Marketing Manager"
git add .claude/skills/campaign-scaling-expert/SKILL.md
git commit -m "feat: add 20-30% scaling rule, cost cap strategy, and CPA spike threshold to campaign-scaling-expert skill"
```

---

## Verification

After all tasks are complete, verify the framework is functioning as expected:

- [ ] **New session test:** Start a new Claude Code session in this project. Confirm the project CLAUDE.md loads (check that unit economics and MER defaults are present in session context).

- [ ] **new-client test:** Run `/new-client` for a test client. Verify: (a) intake asks for AOV, COGS, contribution margin, and breakeven CPA, (b) 30-day plan includes 12-month calendar setup in Week 1, (c) guardrails include the profit-buffer rule.

- [ ] **creative-strategist test:** Run `/creative-strategist` with a Meta brief. Verify: (a) channel variable section appears (Meta = creative is primary variable), (b) creative hierarchy is referenced, (c) angle table appears, (d) 5 stages of awareness are present.

- [ ] **meta-strategist test:** Run `/meta-strategist` for a new account build. Verify: (a) funnel architecture with budget splits appears in output, (b) broad targeting first is stated, (c) whitelisting is in the Manager brief when conditions apply.

- [ ] **meta-manager test:** Run `/meta-manager` for a weekly check. Verify: (a) creative fatigue thresholds appear in the creative check, (b) hypothesis tracker table is updated as part of Mode A output.

- [ ] **weekly-check test:** Run `/weekly-check` for any client. Verify: (a) Section 6.5 (Hypothesis Tracker Update) appears in the output, (b) red flags table is present.

- [ ] **monthly-report test:** Run `/monthly-report` for any client. Verify: (a) MER is the first metric in Section A, (b) Business Performance Dashboard table appears in the client report, (c) monthly optimization checklist is referenced in QA.

- [ ] **cro-strategist test:** Run `/cro-strategist` for an LP audit. Verify: (a) channel context section appears (LP = primary variable for Google), (b) 5 non-negotiables gate runs before the detailed audit.

- [ ] **campaign-scaling-expert test:** Run `/campaign-scaling-expert` for any account. Verify: (a) 20-30% scaling rule appears in Tier 1, (b) cost cap strategy is described in Lever B, (c) CPA spike threshold guardrails are present.
