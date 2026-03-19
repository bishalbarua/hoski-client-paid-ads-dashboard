# P3 — Scheduled Auto-Runs (Cron / Automation)

## Problem
All scripts and skills run on-demand only. Weekly checks, pacing monitors, anomaly detection, and search terms sweeps require manual initiation. This creates operational risk — things get missed when you're busy.

## What to Build
A scheduling layer that automatically triggers key scripts on a defined cadence without manual intervention.

## Proposed Schedule

| Cadence | Script / Task | Output |
|---|---|---|
| Daily (8am) | `anomaly_monitor.py` | `reports/anomaly-YYYY-MM-DD.md` |
| Daily (2pm) | `daily_pacing_monitor.py` | Console / alert if off-pace |
| Monday (7am) | `mcc_rollup.py` | `reports/mcc-rollup-YYYY-MM-DD.md` |
| Monday (7:30am) | `smart_bidding_health.py` (all clients) | Per-client bid health notes |
| 1st of month | `full_audit.py` (all clients) | Per-client full audit reports |

## Implementation Options

### Option A — macOS launchd (Recommended for local machine)
Native macOS scheduler. More reliable than cron on macOS, survives sleep/wake cycles.
- Create `.plist` files in `~/Library/LaunchAgents/`
- One plist per scheduled job
- Logs to `reports/logs/`

### Option B — cron (Simple, portable)
Standard cron jobs via `crontab -e`.
```
0 8 * * * cd /path/to/workspace && python3 scripts/anomaly_monitor.py >> reports/logs/anomaly.log 2>&1
0 7 * * 1 cd /path/to/workspace && python3 scripts/mcc_rollup.py >> reports/logs/rollup.log 2>&1
```

### Option C — GitHub Actions (Cloud, no local machine needed)
Runs in the cloud on schedule even if your Mac is off.
- Requires storing API credentials as GitHub Secrets
- `.github/workflows/daily-anomaly.yml`, `weekly-rollup.yml`, etc.
- Best if you want zero local infrastructure

## Files to Create
- `scripts/run_daily.sh` — wrapper that runs all daily tasks in sequence
- `scripts/run_weekly.sh` — wrapper for Monday morning tasks
- `launchd/com.ppc.daily-monitor.plist` — macOS launchd config (Option A)
- `.github/workflows/daily-anomaly.yml` — GitHub Actions config (Option C)
- `reports/logs/` — log directory for output

## Dependencies
- Requires P1 scripts to be built first (anomaly_monitor.py, mcc_rollup.py)
- Requires environment variables to be available in whichever scheduler is chosen

## Status
- [ ] Not started
- Blocked by: P1-cross-client-rollup, P1-anomaly-detection
