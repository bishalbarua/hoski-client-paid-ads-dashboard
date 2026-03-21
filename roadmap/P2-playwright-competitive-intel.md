# P2 — Playwright Competitive Intelligence Skill

## Problem
The Playwright MCP server is already connected but is only used ad hoc. There is no structured workflow to systematically research competitors — their ad copy, landing pages, offers, and positioning — for any client.

## What to Build
A `/competitor-serp-scan` skill that uses Playwright to:
1. Search Google for a client's target keywords
2. Scrape the visible ad copy from the SERP (headlines, descriptions, display URLs)
3. Visit competitor landing pages and extract their headline, CTA, offer, and trust signals
4. Return a structured competitive brief

## Desired Output
```
Competitor SERP Scan — "emergency dentist toronto" — 2026-03-19

Ads Found (top 4):
1. Dentaly Toronto
   Headline: "Emergency Dentist — Open Today | Same-Day Appointments Available"
   Description: "Walk-ins welcome. No referral needed. Call now."
   Landing page H1: "Toronto's #1 Emergency Dentist"
   CTA: "Book Same-Day Appointment"
   Offer: First exam $0 with treatment

2. ...

Gaps vs. Your Current Ads:
- Competitors lead with "same-day" — your ads don't mention speed
- Two competitors offer a price anchor ($0 exam) — you don't
- No competitor mentions insurance accepted — opportunity
```

## Implementation Notes
- Use Playwright MCP tools: navigate, screenshot, extract text
- Scope: top 4-5 paid ads on page 1 only (not organic)
- Save output to `clients/[client]/analysis/competitor-serp-YYYY-MM-DD.md`
- Integrate with existing `/competitor-messaging-analysis` skill as a data source

## Skill File to Create
- `.claude/skills/competitor-serp-scan/` — new skill directory
- `.claude/skills/competitor-serp-scan/skill.md` — skill prompt
- Register in CLAUDE.md skills table

## Status
- [x] Complete — 2026-03-21
  - Covers both Google SERP and Meta Ad Library
  - Playwright-driven: navigate, screenshot, extract verbatim ad copy
  - Visits top 2-3 competitor landing pages per scan
  - Outputs messaging frequency matrix + gap analysis + 3 ad test recommendations
  - Saves to `clients/[client]/analysis/competitor-serp-YYYY-MM-DD.md`
  - Integrates as data source for `/competitor-messaging-analysis`, `/rsa-headline-generator`, `/creative-director`
