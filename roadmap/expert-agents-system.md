# Expert Agents System Roadmap

A team of specialist AI agents covering the full paid ads workflow — each encoded with deep domain expertise, mental models, failure patterns, and explicit decision logic.

## Architecture

```
Account Manager Agent (Orchestrator)
├── Tier 1 — Core Operating Agents (daily/weekly use)
├── Tier 2 — Deep Specialist Agents (campaign-level)
├── Tier 3 — Intelligence & Research Agents
└── Tier 4 — Client & Business Agents
```

---

## Tier 1 — Core Operating Agents

These run constantly and touch every client.

| Agent | Role | Core Expertise | Location | Status |
|---|---|---|---|---|
| **Search Terms Analyst** | Weekly query mining sweep | Intent classification, negative patterns, match type logic, query-to-ad-group fit | `system-prompts/agents/search-terms-analyst.md` | ✅ Built |
| **Campaign Architect** | Design campaign structures from scratch | Account structure, campaign types, budget allocation, segmentation logic | `system-prompts/agents/campaign-architect.md` | ✅ Built |
| **Ad Copy Strategist** | RSA creation, testing, rotation | Copywriting frameworks, asset performance patterns, angle diversification, pin strategy | `system-prompts/agents/ad-copy-strategist.md` | ✅ Built |
| **Bid & Budget Optimizer** | Bid strategy selection + pacing | Smart bidding signals, tROAS/tCPA math, portfolio strategies, auction theory | `system-prompts/agents/bid-budget-optimizer.md` | ✅ Built |
| **Conversion Tracking Guardian** | Audit + protect data integrity | Tag implementation, attribution models, primary/secondary designation, double-counting | `system-prompts/agents/conversion-tracking-guardian.md` | ✅ Built |

---

## Tier 2 — Deep Specialist Agents

| Agent | Role | Core Expertise | Status |
|---|---|---|---|
| **PMax Intelligence Agent** | PMax diagnosis + optimization | Asset group scoring, channel distribution, brand cannibalization, PMax vs Search conflict | ☐ Not started |
| **Shopping Feed Optimizer** | Product feed quality + performance | Feed attributes, title optimization, product group sculpting, merchant center issues | ☐ Not started |
| **Audience Architect** | Audience strategy across platforms | In-market, affinity, RLSA, Customer Match, lookalike logic, exclusion strategy | ☐ Not started |
| **Meta Ads Specialist** | Facebook/Instagram campaign strategy | Creative-led performance, pixel health, campaign objectives, iOS signal loss | ☐ Not started |
| **Quality Score Engineer** | QS diagnosis + improvement | CTR expectations by position, ad relevance signals, landing page experience factors | ☐ Not started |

---

## Meta Ads Agent System

Meta requires its own agent team. The platform has fundamentally different operating logic from Google: creative is the targeting mechanism, attribution is broken post-iOS 14+ and requires triangulation, the learning algorithm is fragile and punishes edits, and audience decay is faster and more consequential. One generic "Meta Ads Specialist" agent is insufficient.

### Meta Tier 1 — Core Operating Agents (daily/weekly)

| Agent | Role | Core Expertise | Location | Status |
|---|---|---|---|---|
| **Meta Pixel & Events Guardian** | Audit pixel health, CAPI setup, event quality | EMQ score, CAPI deduplication, AEM priority, iOS 14+ attribution, view-through inflation | `system-prompts/agents/meta-pixel-events-guardian.md` | ✅ Built |
| **Meta Campaign Strategist** | Campaign structure, objective selection, account architecture | Objective-to-outcome alignment, learning algorithm, CBO vs ABO, funnel layer architecture, audience exclusion logic | `system-prompts/agents/meta-campaign-strategist.md` | ✅ Built |
| **Meta Creative Performance Analyst** | Read creative data, diagnose winners/losers, drive testing decisions | Creative lifecycle, hook/hold/CTR/CVR diagnostic framework, frequency as leading indicator, format and angle pattern recognition | `system-prompts/agents/meta-creative-performance-analyst.md` | ✅ Built |

### Meta Tier 2 — Deep Specialist Agents

| Agent | Role | Core Expertise | Status |
|---|---|---|---|
| **Meta Bid & Budget Optimizer** | CBO vs ABO decisions, bid caps, cost caps, budget allocation | Cost cap vs bid cap vs lowest cost mechanics, CBO spend distribution, minimum viable budget per ad set for learning exit | `system-prompts/agents/meta-bid-budget-optimizer.md` | ✅ Built |
| **Meta Audience Architect** | Cold/warm/retention audience strategy | Broad vs interest vs LAL trade-offs, custom audience decay rates, exclusion strategy, audience overlap detection, iOS 14+ audience signal degradation | `system-prompts/agents/meta-audience-architect.md` | ✅ Built |
| **Meta Creative Strategist** | Conceive and brief creative before production | Hook archetypes by funnel stage, UGC vs polished creative theory, video structure, platform-native formats (Reels vs Feed vs Stories), creative testing design | `system-prompts/agents/meta-creative-strategist.md` | ✅ Built |
| **Meta Conversion Optimizer** | Diagnose conversion rate and attribution issues | Post-iOS attribution windows, blended ROAS vs Meta-reported gap, view-through attribution risks, MER vs ROAS framing | `system-prompts/agents/meta-conversion-optimizer.md` | ✅ Built |

### Meta Tier 3 — Intelligence & Research Agents

| Agent | Role | Core Expertise | Status |
|---|---|---|---|
| **Meta Ad Library Intelligence Agent** | Scrape and analyze competitor creatives | Creative longevity signals, angle mining, share-of-voice estimation, format benchmarking | `system-prompts/agents/meta-ad-library-intelligence.md` | ✅ Built |
| **Meta Scaling Diagnosis Agent** | Identify why a campaign plateaued and how to break through | Audience saturation vs creative fatigue vs bid constraint vs offer problem, horizontal vs vertical scaling, duplication strategy | `system-prompts/agents/meta-scaling-diagnosis.md` | ✅ Built |

### Meta Tier 4 — Operations & Client Layer

| Agent | Role | Core Expertise | Status |
|---|---|---|---|
| **Meta Account Health Monitor** | Ongoing surveillance: disapprovals, frequency, pacing, signal drops | Frequency thresholds by objective, spend pacing math, delivery health signals, policy risk patterns | `system-prompts/agents/meta-account-health-monitor.md` | ✅ Built |
| **Meta Reporting Analyst** | Internal and client-facing Meta reports | Which metrics to surface by objective, how to frame iOS-impacted data to clients, MER reporting alongside Meta-reported ROAS | `system-prompts/agents/meta-reporting-analyst.md` | ✅ Built |

### Meta Build Priority

```
Phase 1 — Foundation (done)
  ✅ Meta Pixel & Events Guardian     (bad data = wrong decisions everywhere)
  ✅ Meta Campaign Strategist         (structural foundation)
  ✅ Meta Creative Performance Analyst (creative is the primary lever on Meta)

Phase 2 — Optimization (done)
  ✅ Meta Bid & Budget Optimizer
  ✅ Meta Audience Architect
  ✅ Meta Account Health Monitor

Phase 3 — Intelligence (done)
  ✅ Meta Creative Strategist
  ✅ Meta Conversion Optimizer
  ✅ Meta Ad Library Intelligence Agent

Phase 4 — Client Layer (done)
  ✅ Meta Scaling Diagnosis Agent
  ✅ Meta Reporting Analyst
```

---

## Tier 3 — Intelligence & Research Agents

| Agent | Role | Core Expertise | Status |
|---|---|---|---|
| **Keyword Intelligence Agent** | Seed expansion + intent mapping | GAQL mining, intent layers (TOFU/MOFU/BOFU), ad group clustering | ☐ Not started |
| **Competitive Intelligence Agent** | Monitor competitor ads + positioning across Google SERP and Meta Ad Library | Creative longevity signals, SERP signal reading, angle mining, saturation vs. white space framework, cross-channel synthesis | `system-prompts/agents/competitive-intelligence-agent.md` | ✅ Built |
| **Landing Page CRO Agent** | Pre- and post-launch page audits | Message match, above-the-fold, trust signals, CTA hierarchy, load speed | ☐ Not started |
| **Market Research Agent** | Industry trends + seasonality | Search trend analysis, seasonal demand curves, emerging query patterns | ☐ Not started |

---

## Tier 4 — Client & Business Agents

| Agent | Role | Core Expertise | Status |
|---|---|---|---|
| **Account Health Monitor** | Ongoing account surveillance | Anomaly detection, disapprovals, budget exhaustion, conversion drop alerts | ☐ Not started (see P1-anomaly-detection.md) |
| **Reporting Analyst** | Internal + client report generation | Data narrative framing, YoY/MoM analysis, client-facing translation | ☐ Not started |
| **Client Onboarding Agent** | New account intake + audit | Intake questionnaires, existing account audit, first 30-day plan | ☐ Not started |
| **Budget Pacing Agent** | Monthly budget tracking + forecasting | Pacing math, reallocation logic, end-of-month projections | ☐ Not started |

---

## What Makes Each Agent "Super Experienced"

Each agent needs three components beyond basic task instructions:

1. **Mental models** — How a senior practitioner actually thinks about the domain, not just what steps to follow. E.g., the Bid Optimizer needs to know *when* to switch from tCPA to Maximize Conversions and why (learning period, conversion volume thresholds, auction volatility).

2. **Failure pattern library** — What commonly goes wrong, what it looks like in data, and how to distinguish it from normal variance. This is the hardest domain knowledge to encode.

3. **Decision trees** — Explicit if/then/except logic so the agent makes the same call a senior analyst would, including edge cases that would trip up a junior analyst.

---

## Build Priority Order

```
Phase 1 — Foundation (build first)
  ✅ Search Terms Analyst
  ✅ Conversion Tracking Guardian
  ✅ Upgrade Ad Copy Strategist

Phase 2 — Optimization (build next)
  ✅ Bid & Budget Optimizer
  ✅ Campaign Architect
  ☐ Account Health Monitor

Phase 3 — Intelligence (build when Phase 2 done)
  ☐ Keyword Intelligence Agent
  ☐ Competitor Intelligence Agent
  ☐ PMax Intelligence Agent

Phase 4 — Client Layer
  ☐ Reporting Analyst
  ☐ Landing Page CRO Agent
  ☐ Orchestrator / Account Manager Agent
```

---

## Agent vs Skill Distinction

- **Skills** (`.claude/skills/`) — Procedural workflows. Tell Claude *what steps to take* for a specific task. Invoked by the user with `/skill-name`.
- **Agents** (`system-prompts/agents/`) — Expert personas. Encode *how to think* about a domain. Used as sub-agents, specialist prompts, or called by an orchestrator. Much deeper domain knowledge — mental models, failure patterns, decision trees.

Skills call on agents. An agent can power multiple skills.
