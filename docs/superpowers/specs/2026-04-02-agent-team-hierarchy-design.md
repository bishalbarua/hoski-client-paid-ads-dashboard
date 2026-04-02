# Agent Team Hierarchy Design
**Date:** 2026-04-02
**Approach:** Hybrid Layer Architecture (Approach C)
**Status:** Approved for implementation

---

## Overview

Rebuild the management layer of the paid media agent team with a proper corporate hierarchy. Keep the 31 existing Google/Meta specialist agent files unchanged as the knowledge engine. Add new Strategist/Manager channel roles, Creative Strategist, CRO Strategist, and Client Communication Manager. Consolidate fragmented operational skills into unified role-based skills. Retire 9 skills absorbed by the new roles.

**Scope:** 12 new or updated skills, 7 kept skills, 9 retired skills, 31 specialist agent files untouched.

---

## Hierarchy

```
CMO (/cmo)
  Marketing Director (/marketing-director)
    Project Manager (/pm)
      Google Ads Strategist (/google-strategist)
        Google Ads Manager (/google-manager)
      Meta Ads Strategist (/meta-strategist)
        Meta Ads Manager (/meta-manager)
      Creative Strategist (/creative-strategist)
      CRO Strategist (/cro-strategist)
      Competitive Specialist (/competitive)
      QA Manager (/qa)
    Client Communication Manager (/client-comms)
```

The 31 existing specialist agents (`google-*.md`, `meta-*.md`, `cross-*.md`) sit beneath their respective Strategist/Manager roles as the knowledge engine. They are not invoked directly by the user.

---

## Role Definitions

### Chief Marketing Officer — `/cmo`
**Status:** New
**System prompt:** `system-prompts/agents/cross-cmo.md`
**Skill:** `.claude/skills/cmo/SKILL.md`

**Purpose:** Agency-level strategic view. Never touches individual campaign execution. Answers: how is the agency performing, where should we focus, which clients need attention.

**Inputs:**
- MCC rollup data (all client snapshots)
- Monthly reports from all clients
- Weekly check summaries (flagged items only)
- Agency targets and growth goals

**Outputs:**
- Cross-client health scorecard
- Quarterly priority list (P1/P2/P3 by client)
- Agency performance narrative
- Escalation decisions routed to Marketing Director

**Does NOT do:** Touch individual campaigns, replace the Marketing Director for client work, write client-facing communication.

**Trigger phrases:** "agency overview", "how are all clients doing", "which clients need attention", "quarterly priorities", "agency health"

---

### Marketing Director — `/marketing-director`
**Status:** Refactor
**System prompt:** `system-prompts/agents/cross-marketing-director.md` (update)
**Skill:** `.claude/skills/marketing-director/SKILL.md` (update)

**Purpose:** Per-client orchestration. Routes work to the Strategist/Manager layer (not raw specialists directly). Enforces the dependency graph. Detects cross-specialist contradictions. Synthesizes into a prioritized action plan.

**What changes from current version:**
- Delegates to `/google-strategist`, `/meta-strategist`, `/creative-strategist`, `/cro-strategist`, `/competitive`, `/qa` — not raw specialist agents directly.
- Explicitly aware it reports to CMO and escalates cross-client patterns upward.
- Scope filter tightened: single-client work only. Cross-client decisions escalate to CMO.

**What stays the same:**
- Dependency graph enforcement
- Contradiction detection between specialists
- 3-tier priority triage (P1/P2/P3)
- QA gate before final output
- Business translation of technical outputs

**Dependency sequence (unchanged):**
```
Conversion Tracking Guardian (blocking)
  Keyword Intelligence
    Campaign Architect
      Ad Copy Strategist
        Bid/Budget Optimizer
Competitive Intelligence (parallel, no upstream dependency)
QA Specialist (always last)
```

---

### Project Manager — `/pm`
**Status:** New
**System prompt:** `system-prompts/agents/cross-pm.md`
**Skill:** `.claude/skills/pm/SKILL.md`

**Purpose:** Operational backbone. Two modes in one role.

**Mode A — Internal sequencing (single client):**
- Enforces the dependency graph within a client project
- Flags when a downstream task is blocked by an upstream blocker
- Produces a sequenced task list with owners and dependencies marked

**Mode B — Cross-client scheduling:**
- Tracks all clients: what is overdue, upcoming, in-flight
- Surfaces which clients need a weekly check, monthly report, or campaign review
- Flags clients that have gone quiet (no review in X days)
- Produces a weekly agency workload view

**Inputs:** All `client-info.md` files, report history (last monthly/weekly date), current task request from Marketing Director, known blockers.

**Outputs:** Sequenced task list with dependency map, cross-client status board, blocker report, overdue items flagged with urgency.

**Trigger phrases:** "what needs to happen this week", "what's the order of operations for [client]", "which clients need attention", "sequence this project", "what's overdue"

---

### Google Ads Strategist — `/google-strategist`
**Status:** New
**System prompt:** `system-prompts/agents/google-strategist.md`
**Skill:** `.claude/skills/google-strategist/SKILL.md`

**Purpose:** Designs the Google Ads plan. Owns all strategic decisions: campaign architecture, keyword strategy, bid strategy, audience approach. Produces a brief that the Google Manager executes.

**Wraps agents:** `google-campaign-architect`, `google-keyword-intelligence`, `google-bid-budget-optimizer`, `google-audience-architect`, `google-pmax-intelligence`

**Inputs:** `client-info.md`, budget and CPA targets, business context/URL, historical performance data.

**Outputs:** Campaign structure brief, keyword strategy with intent map, bid strategy recommendation, audience segmentation plan.

---

### Google Ads Manager — `/google-manager`
**Status:** New
**System prompt:** `system-prompts/agents/google-manager.md`
**Skill:** `.claude/skills/google-manager/SKILL.md`

**Purpose:** Executes and monitors Google campaigns. Implements what the Strategist designed. Runs all weekly operational tasks: pacing, search terms, copy performance, negatives, bid health.

**Wraps agents:** `google-account-health-monitor`, `google-search-terms-analyst`, `google-budget-pacing`, `google-negative-keyword`, `google-ad-copy-strategist`, `google-reporting-analyst`

**Consolidates:** `/weekly-check` + `/search-terms` + `/ad-copy-testing-analyzer`

**Inputs:** Strategy brief from Google Strategist, live account data via API, search term exports, weekly performance snapshots.

**Outputs:** Weekly action list, search term report (4 sections: negatives, new keywords, match type promotions, segmentation signals), pacing alert if off-track, copy swap recommendations.

---

### Meta Ads Strategist — `/meta-strategist`
**Status:** New
**System prompt:** `system-prompts/agents/meta-strategist.md`
**Skill:** `.claude/skills/meta-strategist/SKILL.md`

**Purpose:** Designs the Meta plan. Owns campaign architecture, full-funnel structure (ToFu/MoFu/BoFu), audience strategy, and creative direction brief.

**Wraps agents:** `meta-campaign-strategist`, `meta-audience-architect`, `meta-creative-strategist`, `meta-bid-budget-optimizer`, `meta-conversion-optimizer`

**Inputs:** `client-info.md`, funnel goals and budget, pixel/conversion event status, existing audience data.

**Outputs:** Campaign architecture, audience strategy (cold/warm/retargeting), creative brief for Creative Strategist, bid and budget allocation plan.

---

### Meta Ads Manager — `/meta-manager`
**Status:** New
**System prompt:** `system-prompts/agents/meta-manager.md`
**Skill:** `.claude/skills/meta-manager/SKILL.md`

**Purpose:** Executes and monitors Meta campaigns. Tracks creative fatigue, pacing, pixel health, audience performance, and scaling signals.

**Wraps agents:** `meta-account-health-monitor`, `meta-creative-performance-analyst`, `meta-scaling-diagnosis`, `meta-pixel-events-guardian`, `meta-ad-library-intelligence`

**Consolidates:** `/facebook-ads-performance-analyzer`

**Inputs:** Strategy brief from Meta Strategist, live Meta account data, creative performance signals, pixel/event data.

**Outputs:** Weekly action list, creative fatigue alerts, scaling signals (up/down), pixel health report.

---

### Creative Strategist — `/creative-strategist`
**Status:** New
**System prompt:** `system-prompts/agents/cross-creative-strategist.md`
**Skill:** `.claude/skills/creative-strategist/SKILL.md`

**Purpose:** Full creative ownership across both channels. Audit what is running, analyze what is working, ideate new angles, brief concepts for image/video/copy, build the testing framework.

**Wraps agents:** `google-ad-copy-strategist`, `meta-creative-strategist`, `meta-creative-performance-analyst`, `meta-ad-library-intelligence`

**Consolidates:** `/rsa-headline-generator` + `/ad-copy-testing-analyzer` + `/creative-director`

**Scope:**
- **Audit:** RSA asset performance (BEST/GOOD/LOW), Meta creative fatigue signals, winning pattern extraction
- **Ideation:** New copy angles and hooks, image and video concepts, UGC direction
- **Strategy:** Creative testing framework, awareness continuum mapping, competitive creative gap analysis

**Inputs:** Current creative assets and performance data, competitor creative, brand guidelines from `client-info.md`.

**Outputs:** Creative audit report, creative strategy brief, new concepts with copy and visual direction, testing framework with hypothesis per concept.

---

### CRO Strategist — `/cro-strategist`
**Status:** New
**System prompt:** `system-prompts/agents/cross-cro-strategist.md`
**Skill:** `.claude/skills/cro-strategist/SKILL.md`

**Purpose:** Full landing page ownership. Audits current pages, identifies conversion leaks, ideates improvements, builds the CRO strategy. Ensures message match between ads and landing pages across all channels.

**Wraps agents:** `cross-landing-page-cro`

**Replaces:** `/landing-page-quick-audit` (significantly expanded scope)

**Scope:**
- **Audit:** Above-the-fold analysis, message match vs. ad copy, trust signal inventory, mobile experience, form friction
- **Ideation:** Headline and CTA alternatives, layout recommendations, social proof placement
- **Strategy:** Per-campaign landing page prescriptions, A/B test prioritization, funnel drop-off diagnosis, post-click experience map

**Inputs:** Landing page URL or screenshots, current ad copy, campaign goals, conversion rate data.

**Outputs:** CRO audit with severity-ranked issues, optimization roadmap, A/B test hypothesis list, message match scorecard per campaign.

---

### Competitive Specialist — `/competitive`
**Status:** Refactor (consolidation)
**System prompt:** `system-prompts/agents/cross-competitive-intelligence.md` (update)
**Skill:** `.claude/skills/competitive/SKILL.md` (new, replaces two)

**Purpose:** Single source of competitive intelligence across both channels. Delivers SERP ad analysis, competitor website messaging audit, and gap analysis in one pass.

**Wraps agents:** `cross-competitive-intelligence`, `meta-ad-library-intelligence`

**Consolidates:** `/competitor-serp-scan` + `/competitor-messaging-analysis`

**Inputs:** Client URL, 2-3 competitor URLs, target keywords, client's current ad copy.

**Outputs:** Live SERP ad copy analysis, competitor messaging audit, positioning gap map, exploitable angles the client is missing. Saved to `clients/[name]/analysis/competitor-YYYY-MM-DD.md`.

---

### QA Manager — `/qa`
**Status:** Refactor (standalone extraction)
**System prompt:** `system-prompts/agents/cross-qa-specialist.md` (update)
**Skill:** `.claude/skills/qa/SKILL.md` (new standalone)

**Purpose:** Adversarial review gate. Runs before any output reaches the client. Previously embedded only inside the Marketing Director workflow. Now also callable as a standalone skill to QA any document independently.

**The 6 review categories (unchanged):**
1. **Data Hallucinations** — numbers cited not in the session data
2. **Logical Gaps** — recommendations that contradict their own stated thresholds
3. **Cross-Specialist Contradictions** — conflicts between two specialists' outputs
4. **Strategy-Context Mismatch** — correct advice that is wrong for this specific client
5. **PPC Risk Flags** — hidden efficiency cliffs, tracking gaps, data below smart bidding thresholds
6. **Completeness Failures** — missing context, incomplete coverage, symptom vs. root cause

**Output:** PASS / CONDITIONAL PASS / FAIL with specific items to fix before delivery.

---

### Client Communication Manager — `/client-comms`
**Status:** New
**System prompt:** `system-prompts/agents/cross-client-comms.md`
**Skill:** `.claude/skills/client-comms/SKILL.md`

**Purpose:** Owns the full client-facing voice. Translates technical team output into polished client language. Manages the ongoing relationship thread.

**Always references:** `client-info.md` (tone, goals, relationship history), most recent report or analysis, PPC no-jargon rule (zero technical acronyms unless client is confirmed technical).

**Relationship modes:**
- **Proactive:** Monthly narrative, weekly status note, campaign launch announcement
- **Reactive:** Response to client question, concern, or escalation
- **Milestone:** New campaign live, budget change, strategic pivot explanation

**Inputs:** Any technical output (weekly check, monthly report, analysis, QA-passed plan).

**Outputs:** Polished client email, status update, report narrative, response draft. Tone calibrated per `client-info.md`.

---

## Skill Command Map

| Command | Role | Status |
|---|---|---|
| `/cmo` | Chief Marketing Officer | New |
| `/marketing-director` | Marketing Director | Refactor |
| `/pm` | Project Manager | New |
| `/google-strategist` | Google Ads Strategist | New |
| `/google-manager` | Google Ads Manager | New |
| `/meta-strategist` | Meta Ads Strategist | New |
| `/meta-manager` | Meta Ads Manager | New |
| `/creative-strategist` | Creative Strategist | New |
| `/cro-strategist` | CRO Strategist | New |
| `/competitive` | Competitive Specialist | Refactor |
| `/qa` | QA Manager | Refactor |
| `/client-comms` | Client Communication Manager | New |
| `/new-client` | New Client Onboarding | Keep |
| `/ads-strategy-architect` | Strategy Architect | Keep |
| `/conversion-tracking-audit` | Tracking Audit | Keep |
| `/keyword-research` | Keyword Research | Keep |
| `/campaign-scaling-expert` | Scaling Expert | Keep |
| `/ppc-account-health-check` | Account Health | Keep |
| `/pmax-shopping-analyzer` | PMax Analyzer | Keep |
| `/monthly-report` | Monthly Report | Keep |
| `/weekly-check` | — | Retire (absorbed by /google-manager) |
| `/search-terms` | — | Retire (absorbed by /google-manager) |
| `/rsa-headline-generator` | — | Retire (absorbed by /creative-strategist) |
| `/ad-copy-testing-analyzer` | — | Retire (absorbed by /creative-strategist) |
| `/creative-director` | — | Retire (absorbed by /creative-strategist) |
| `/landing-page-quick-audit` | — | Retire (absorbed by /cro-strategist) |
| `/competitor-serp-scan` | — | Retire (absorbed by /competitive) |
| `/competitor-messaging-analysis` | — | Retire (absorbed by /competitive) |
| `/facebook-ads-performance-analyzer` | — | Retire (absorbed by /meta-manager) |

---

## Common Invocation Patterns

### New client setup
1. `/new-client` — intake and workspace creation
2. `/ads-strategy-architect` — full channel strategy
3. `/pm` — sequence the build tasks
4. `/google-strategist` and `/meta-strategist` — channel-specific plans
5. `/qa` — review before anything goes live
6. `/client-comms` — kickoff note to client

### Weekly operations (per client)
1. `/google-manager` — weekly check, search terms, pacing, copy
2. `/meta-manager` — creative fatigue, pacing, pixel health
3. `/client-comms` — draft weekly status note
4. If issues flagged: escalate to `/marketing-director`

### Monthly reporting
1. `/monthly-report` — internal analysis
2. `/qa` — review the report
3. `/client-comms` — client-facing version

### Creative refresh
1. `/competitive` — what are competitors running
2. `/creative-strategist` — audit and new concepts
3. `/cro-strategist` — message match check
4. `/qa` — before sending to client

### Performance investigation
1. `/marketing-director` — scope and deploy team
2. Director routes to relevant specialists
3. `/qa` — adversarial review
4. `/client-comms` — findings summary to client

### Agency-level monthly review
1. `/cmo` — cross-client health scorecard
2. CMO flags priority clients to Director
3. `/pm` — reprioritize workload

---

## File Structure Changes

### system-prompts/agents/ — new and updated files
```
cross-cmo.md                      NEW
cross-marketing-director.md       UPDATE (delegation pattern change)
cross-pm.md                       NEW
google-strategist.md              NEW
google-manager.md                 NEW
meta-strategist.md                NEW
meta-manager.md                   NEW
cross-creative-strategist.md      NEW
cross-cro-strategist.md           NEW
cross-competitive-intelligence.md UPDATE (consolidation)
cross-qa-specialist.md            UPDATE (standalone extraction)
cross-client-comms.md             NEW
google-*.md (16 files)            UNCHANGED
meta-*.md (10 files)              UNCHANGED
```

### .claude/skills/ — new, updated, and retired
```
cmo/SKILL.md                      NEW
marketing-director/SKILL.md       UPDATE
pm/SKILL.md                       NEW
google-strategist/SKILL.md        NEW
google-manager/SKILL.md           NEW
meta-strategist/SKILL.md          NEW
meta-manager/SKILL.md             NEW
creative-strategist/SKILL.md      NEW
cro-strategist/SKILL.md           NEW
competitive/SKILL.md              NEW (consolidates 2 existing)
qa/SKILL.md                       NEW (standalone extraction)
client-comms/SKILL.md             NEW
weekly-check/SKILL.md             RETIRE
search-terms/SKILL.md             RETIRE
rsa-headline-generator/SKILL.md   RETIRE
ad-copy-testing-analyzer/SKILL.md RETIRE
creative-director/SKILL.md        RETIRE
landing-page-quick-audit/SKILL.md RETIRE
competitor-serp-scan/SKILL.md     RETIRE
competitor-messaging-analysis/SKILL.md RETIRE
facebook-ads-performance-analyzer/SKILL.md RETIRE
new-client/SKILL.md               KEEP
ads-strategy-architect/SKILL.md   KEEP
conversion-tracking-audit/SKILL.md KEEP
keyword-research/SKILL.md         KEEP
campaign-scaling-expert/SKILL.md  KEEP
ppc-account-health-check/SKILL.md KEEP
pmax-shopping-analyzer/SKILL.md   KEEP
monthly-report/SKILL.md           KEEP
```

---

## Constraints and Non-Negotiables

- The 31 existing specialist agent files (`google-*.md`, `meta-*.md`) are not modified. They are the knowledge layer.
- The Marketing Director still enforces the dependency graph and QA gate — these are not removed, only the delegation target changes.
- `/conversion-tracking-audit` remains a standalone blocking skill — it is never absorbed into the Manager roles because it must be run independently before any optimization work.
- All write operations to Google Ads or Meta require user approval before execution (existing rule, unchanged).
- New entities created via any skill must be set to PAUSED or DRAFT status (existing rule, unchanged).
