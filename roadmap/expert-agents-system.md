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

## Tier 3 — Intelligence & Research Agents

| Agent | Role | Core Expertise | Status |
|---|---|---|---|
| **Keyword Intelligence Agent** | Seed expansion + intent mapping | GAQL mining, intent layers (TOFU/MOFU/BOFU), ad group clustering | ☐ Not started |
| **Competitor Intelligence Agent** | Monitor competitor ads + positioning | Auction insights, ad copy scraping, landing page analysis, messaging gaps | ☐ Not started |
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
