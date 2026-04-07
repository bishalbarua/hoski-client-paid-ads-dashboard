# Höski Framework Embedding Design

**Date:** 2026-04-05
**Status:** Approved

---

## Context

The Höski Framework - Marketing Playbook codifies the operating doctrine extracted from 1,158 real client engagements. It defines Five Laws (unit economics, creative as primary variable, MER over platform ROAS, calendar as strategy, funnel as product), a weekly operating rhythm, a client lifecycle, and a decision-making mindset.

The current skill and agent system has strong technical depth in Google Ads and Meta mechanics but does not encode this doctrine. Agents make recommendations without defaulting to unit economics first, without surfacing MER, without structuring creative testing by the hypothesis tracker model, and without the calendar-first discipline the framework requires.

The goal is to make every agent and skill operate under the Höski Framework as default behavior, not as something that has to be invoked explicitly.

One addition beyond the playbook: the playbook states "Creative is the variable" universally, but this is channel-specific. For Meta, creative is the primary variable (targeting is commoditized). For Google, landing page is the primary variable (keywords and copy are constrained by search intent; the page is where conversion is won or lost). This distinction is embedded throughout.

---

## Approach

**Approach A: CLAUDE.md as the always-on layer + selective inline absorption.**

A project-root `CLAUDE.md` carries the condensed behavioral doctrine. Every Claude Code session reads it automatically, so every skill and agent inherits the framework without needing to reference it explicitly. The 8 skills where specific laws need to be operationalized get targeted inline additions.

The 38 raw agent prompt files, Python scripts, JS scripts, and `core-ppc-reasoning.md` are not changed. The skills that invoke agents carry the framework. Scripts pull data; the framework governs interpretation.

---

## Layer 1: Project-Root CLAUDE.md

**File to create:** `/Users/bishalbarua/Bishal/AI/antigravity/Hoski Marketing Manager/CLAUDE.md`

Contains the following behavioral defaults, always active:

### The Primary Variable Rule
- Meta: Creative is the variable. Targeting is commoditized. All optimization effort goes to angles, hooks, formats, and volume.
- Google: Landing page is the variable. Keywords and copy are constrained by search intent. Conversion is won or lost on the page after the click.

### Unit Economics Defaults
- Know AOV, COGS, contribution margin, breakeven CPA, and LTV:CAC before making any spend recommendation.
- If these are not documented for a client, surface that gap immediately.
- Target CPA = 70-80% of breakeven CPA (not breakeven itself — the buffer is the profit).
- LTV:CAC below 2:1 is a warning. Below 1:1 is a fire.

### Metrics Hierarchy
- MER (Total Revenue / Total Ad Spend) is the business truth. Always the lead metric for business-level decisions.
- Platform ROAS is for intra-platform optimization only (which campaign to scale, which to kill). Never use it to make a business-level spend decision.
- Healthy MER with weak platform ROAS: the business is fine, attribution is just noisy. Declining MER with strong platform ROAS: there is a real problem.

### Funnel Architecture Defaults
- Budget split: 60-70% prospecting, 20-25% retargeting, 10-15% retention/email.
- Adjust by vertical: DTC ecommerce skews Meta-heavy. Local services skew Google Search-heavy. B2B skews LinkedIn + Google.
- First-order profitability is the North Star. Retention is where margin compounds.

### Calendar Defaults
- Tier 1 events (BFCM, Q5, Valentine's Day, Mother's Day) require a 4-week runway. If a Tier 1 event is within 4 weeks and prep has not started, flag it immediately.
- Q5 (Dec 26 - Jan 7) is never a pause period. CPMs crater, consumers are buying. Scale into it.
- Reactive marketing is amateur marketing. Never scramble.

### Weekly Rhythm
- Monday: review weekend performance, kill underperformers, scale winners, plan creative needs
- Tuesday-Wednesday: creative production, creator briefing
- Thursday: launch new test batch (minimum 4-5 new creatives)
- Friday: performance review, update hypothesis tracker, update marketing calendar, flag red flags

### Creative Testing Defaults
- Each creative gets $100-150 budget, minimum 72-hour run before any kill decision.
- Measure: outbound CTR, hook rate (3-second video view %), cost per result.
- Kill anything below threshold. Move winners to Evergreen campaign.
- Minimum 4-5 new creatives per test cycle. If all creatives look the same, you learned nothing.

### Hypothesis Tracker Default
- No test without a hypothesis. No result without a learning. No learning without a next action.
- Every week: document hypothesis, test run, result, learning, next action.

### Scaling Defaults
- Increase budget 20-30% every 3-5 days on winning campaigns. Never overnight.
- If CPA spikes more than 30% above target for 3+ consecutive days during scaling, pull back.
- Cost cap strategy: set CPA or ROAS target, give campaign 3-5x normal daily budget. It only spends when it can hit the target.

### 5 Stages of Awareness
- Unaware, Problem Aware, Solution Aware, Product Aware, Most Aware.
- Cold prospecting creative targets stages 1-3. Retargeting creative targets stages 4-5.
- Default diagnosis when prospecting underperforms: the creative is probably targeting stages 4-5 and skipping the awareness-building stages.

### Decision Mindset
- Data over feelings. If you cannot point to the data that supports a decision, it is a guess.
- Test, do not debate. Opinions are free. Data costs $150 and 72 hours.
- Think like an owner. Every dollar spent is a dollar the client earned.

---

## Layer 2: Targeted Skill-Level Additions

### 1. `new-client/SKILL.md`

**Add:** Unit economics calculator as a required intake item (Week 1, non-optional). Fields: AOV, COGS, shipping costs, contribution margin, breakeven CPA formula, LTV:CAC ratio. Flag immediately if client cannot provide these numbers.

**Add:** 12-month marketing calendar setup as a Week 1 deliverable. Tier 1 events documented and 4-week prep windows marked.

**Add:** Höski client lifecycle framing for the 30-day plan: Week 1 = foundation, Week 2 = first look, Week 3-4 = first optimization cycle. Month 1 is data, not profit.

**Add to guardrails:** Never launch without unit economics documented (mirrors "never launch without conversion tracking").

### 2. `creative-strategist/SKILL.md`

**Add:** The creative hierarchy (angle > hook > format > offer > targeting). Most time goes to angle and hook. Format, offer, and targeting are downstream.

**Add:** The 7 creative angles with when-to-use guidance: Problem-Solution, Social Proof/Testimonial, Founder Story, Educational, Urgency/Scarcity, Lifestyle/Aspiration, UGC/Organic Feel.

**Add:** 5 stages of awareness mapped to creative mode. Prospecting brief must specify which stages 1-3 the creative targets. Retargeting brief specifies stages 4-5.

**Add:** Testing protocol defaults ($100-150, 72h minimum, three metrics to measure).

**Add:** Whitelisting as a named tactic — when to use it and how it works.

**Add:** Channel split in the skill description. RSA/Google work = landing page is the variable, copy is a support function. Meta work = creative is the variable, everything else is secondary.

### 3. `meta-strategist/SKILL.md`

**Add:** Full funnel architecture with budget splits as the default campaign structure output (not optional context — the deliverable includes funnel allocation).

**Add:** Standard Meta campaign structure: Prospecting (Testing + Evergreen + Cost Cap), Retargeting (DPA 7-14 day + Custom Audiences), Retention (email/SMS suppression from prospecting).

**Add:** Whitelisting as a named strategic recommendation when conditions are met (founder story, UGC-heavy account, branded content showing fatigue).

**Add:** Broad targeting first. Advantage+ first. Never recommend complex interest stacking before testing broad.

### 4. `meta-manager/SKILL.md`

**Add:** Weekly rhythm as the structural skeleton for operational output (Monday kill/scale, Thursday launch, Friday review).

**Add:** Creative fatigue thresholds: frequency above 3 in 7 days + CTR dropping = creative fatigue signal. Escalate to creative-strategist for replacement batch.

**Add:** Hypothesis tracker table format as a required section in the weekly output.

### 5. `weekly-check/SKILL.md`

**Add:** Hypothesis tracker table as a required section of the weekly deliverable (hypothesis, test, result, learning, next action).

**Add:** Red flags table from the framework as the escalation trigger list: CPA rising 3 weeks in a row, MER declining while platform ROAS is stable, AOV dropping, email open rates below 20%, client asking "what are you doing?"

**Add:** Weekly rhythm as the structural reference for what Monday/Thursday/Friday each mean operationally.

### 6. `monthly-report/SKILL.md`

**Add:** MER as the lead metric in the report header. Calculated as Total Revenue / Total Ad Spend. Source: Shopify + all ad spend combined.

**Add:** Full dashboard table as the standard report structure: Breakeven CPA, Actual CPA, MER, New Customer %, AOV, Email Revenue %.

**Add:** Red flags table as the "signals requiring action" section.

**Add:** Monthly optimization checklist from the playbook: creative refresh, calendar review, email flow audit, competitor ad library check, landing page performance, hypothesis tracker update, customer cohort analysis, MER trend direction.

### 7. `cro-strategist/SKILL.md`

**Add:** Landing page as the primary variable for Google Ads traffic. The ad gets the click; the page determines the conversion.

**Add:** 5 landing page requirements that must be present before cold traffic is sent: clear hero above fold, single primary CTA (not three), social proof within first scroll, trust signals (shipping/returns/guarantees), mobile-first design.

**Add:** Cold traffic to an unoptimized product page is a documented failure mode, not an acceptable default.

### 8. `campaign-scaling-expert/SKILL.md`

**Add:** Phase 3 scaling rules: 20-30% budget increase every 3-5 days on winning campaigns. CPA spike threshold: more than 30% above target for 3+ consecutive days = pull back and diagnose.

**Add:** Cost cap strategy as the stable scaling method: set CPA/ROAS target, inflate budget to 3-5x normal daily, let the campaign self-regulate spend.

**Add:** Creative continues feeding testing campaign during scaling. Winners move to Evergreen. Evergreen is never starved for budget while scaling.

---

## Files Changed

| File | Change Type |
|---|---|
| `CLAUDE.md` (project root) | Create |
| `.claude/skills/new-client/SKILL.md` | Update |
| `.claude/skills/creative-strategist/SKILL.md` | Update |
| `.claude/skills/meta-strategist/SKILL.md` | Update |
| `.claude/skills/meta-manager/SKILL.md` | Update |
| `.claude/skills/weekly-check/SKILL.md` | Update |
| `.claude/skills/monthly-report/SKILL.md` | Update |
| `.claude/skills/cro-strategist/SKILL.md` | Update |
| `.claude/skills/campaign-scaling-expert/SKILL.md` | Update |

**Not changed:** All 38 agent prompts in `system-prompts/agents/`, all Python scripts, all JS scripts, `core-ppc-reasoning.md`, all other skills.

---

## Verification

After implementation:

1. Start a new session, run `/new-client` — verify unit economics calculator appears in intake and 12-month calendar setup appears in Week 1 plan.
2. Run `/creative-strategist` with a Meta brief — verify creative hierarchy and angle table appear in output, 5 stages are referenced.
3. Run `/weekly-check` for any client — verify hypothesis tracker table appears and red flags section is present.
4. Run `/monthly-report` — verify MER is the lead metric and the full dashboard table is produced.
5. Run `/cro-strategist` — verify "landing page is the primary variable" framing appears and the 5 LP requirements are listed.
6. Ask a general question mid-session — verify MER is used instead of platform ROAS for any business-level recommendation.
