# P1 — Cross-Client Weekly Roll-Up Report

## Problem
`full_audit.py` audits one account at a time. With 13 clients under MCC 4781259815, there is no way to see a comparative view across all accounts simultaneously. Every Monday requires running audits individually.

## What to Build
A single script (`scripts/mcc_rollup.py`) that queries all 13 client accounts in one pass and produces a ranked summary table.

## Desired Output
```
Week of 2026-03-16

Client                          | Spend   | Conv | CPA    | CTR   | Alert
--------------------------------|---------|------|--------|-------|------
Voit Dental (1)                 | $1,240  | 18   | $68    | 4.2%  | -
Anand Desai Law Firm            | $890    | 6    | $148   | 2.1%  | ⚠️ CPA up 40%
Hoski.ca                        | $620    | 22   | $28    | 5.8%  | -
...
```

## Key Metrics to Include
- Spend (WoW delta %)
- Conversions (WoW delta %)
- CPA (WoW delta %)
- CTR
- Impression Share
- Any client with a >20% negative swing flagged with a warning icon

## Implementation Notes
- Use the MCC customer ID (4781259815) as `login_customer_id`
- Loop through all client IDs defined in CLAUDE.md
- Run queries in parallel using `concurrent.futures.ThreadPoolExecutor`
- Save output to `reports/mcc-rollup-YYYY-MM-DD.md`
- Should complete in under 60 seconds for all 13 accounts

## Files to Create
- `scripts/mcc_rollup.py` — main script
- Update `/weekly-check` skill to reference this rollup as the starting point

## Status
- [ ] Not started
