# P1 — Anomaly Detection

## Problem
There is no proactive monitoring. Issues like conversion tracking failures, sudden spend spikes, impression share crashes, or zero-conversion days are only discovered when manually running an audit — often after the client has already lost money.

## What to Build
A script (`scripts/anomaly_monitor.py`) that scans all accounts daily and flags anything that looks wrong.

## Anomalies to Detect

### Conversion Tracking
- 0 conversions recorded in last 48 hours for an account that normally converts daily
- Conversion count dropped >50% vs same day last week
- New conversion action with 0 conversions after 7+ days running

### Spend
- Daily spend >120% of average daily budget (overpacing)
- Daily spend <20% of average daily budget (underpacing / campaigns may have stopped)
- Single campaign consuming >80% of total account spend (concentration risk)

### Traffic Quality
- CTR dropped >30% WoW on a previously stable campaign
- Impression Share dropped >15 points WoW
- Average CPC increased >40% WoW without bid changes

### Ad Health
- Any ad disapproved in the last 7 days
- Ad group with 0 impressions in 7 days despite active keywords and budget

## Desired Output
```
ANOMALY REPORT — 2026-03-19

🔴 CRITICAL
  Anand Desai Law Firm (5865660247)
    - 0 conversions in last 48h (avg: 2.1/day). Possible tracking breakage.

⚠️ WARNING
  Hoski.ca (5544702166)
    - Brand campaign CPCs up 43% WoW ($1.20 → $1.72). Check competitor activity.

✅ All clear: Voit Dental (1), Voit Dental (2), Dentiste, FaBesthetics, ...
```

## Alerting
- Save report to `reports/anomaly-YYYY-MM-DD.md`
- Optionally: send Gmail draft via Gmail MCP for each critical anomaly

## Implementation Notes
- Compare against a 7-day rolling average baseline, not a fixed threshold
- Use `segments.date DURING LAST_7_DAYS` for trend data
- Suppress alerts if campaign is intentionally paused (check campaign status)

## Files to Create
- `scripts/anomaly_monitor.py` — main detection script
- `scripts/anomaly_config.py` — thresholds config (easy to tune per client)

## Status
- [x] Complete (2026-03-23): `scripts/anomaly_monitor.py` + `scripts/anomaly_config.py`
