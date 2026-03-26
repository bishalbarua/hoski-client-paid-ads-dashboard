# Script Scheduler Configuration

## Overview

This file documents the recommended schedule for each script in the automation
suite. Once Tier 1 scripts are stable (running cleanly for 2 weeks), use the
cron or launchd setup below to run everything automatically.

---

## Recommended Schedule

| Script | Frequency | Time | Purpose |
|---|---|---|---|
| `anomaly_monitor.py` | Daily | 8:00am | Catch overnight issues before the workday starts |
| `mcc_rollup.py` | Weekly (Mon) | 7:30am | Cross-client overview ready for Monday check |
| `client_health_scorecard.py` | Weekly (Mon) | 7:45am | Portfolio health scores before client calls |
| `google_daily_pacing_monitor.py` | Daily | 2:00pm | Intraday budget check |
| `weekly_performance_report.py` | Weekly (Mon) | 6:00am | Sheets data ready before office opens |

---

## macOS cron setup

Open cron with:
```
crontab -e
```

Add these lines (adjust paths to your actual project location):

```cron
# Google Ads Automation Scripts
# Format: minute hour day-of-month month day-of-week command

# Load .env automatically by running via a shell wrapper
# Daily anomaly check at 8am
0 8 * * * cd "/Users/bishalbarua/Bishal/AI/antigravity/Google Ads Manager" && /usr/bin/python3 scripts/anomaly_monitor.py --save >> logs/cron.log 2>&1

# Daily pacing check at 2pm
0 14 * * * cd "/Users/bishalbarua/Bishal/AI/antigravity/Google Ads Manager" && /usr/bin/python3 scripts/google_daily_pacing_monitor.py >> logs/cron.log 2>&1

# Monday 7:30am — MCC rollup
30 7 * * 1 cd "/Users/bishalbarua/Bishal/AI/antigravity/Google Ads Manager" && /usr/bin/python3 scripts/mcc_rollup.py --save >> logs/cron.log 2>&1

# Monday 7:45am — Health scorecard
45 7 * * 1 cd "/Users/bishalbarua/Bishal/AI/antigravity/Google Ads Manager" && /usr/bin/python3 scripts/client_health_scorecard.py >> logs/cron.log 2>&1

# Monday 6:00am — Weekly performance report
0 6 * * 1 cd "/Users/bishalbarua/Bishal/AI/antigravity/Google Ads Manager" && /usr/bin/python3 scripts/weekly_performance_report.py >> logs/cron.log 2>&1
```

**Note:** cron does NOT load your shell's environment. If scripts fail to find
environment variables, use a wrapper script:

```bash
#!/bin/bash
# run_script.sh — cron-safe wrapper
cd "/Users/bishalbarua/Bishal/AI/antigravity/Google Ads Manager"
set -a
source .env
set +a
python3 "$@"
```

Then reference the wrapper in cron:
```
0 8 * * * /Users/bishalbarua/Bishal/AI/antigravity/Google\ Ads\ Manager/run_script.sh scripts/anomaly_monitor.py --save >> logs/cron.log 2>&1
```

---

## macOS launchd alternative (more reliable than cron)

Create a plist file at `~/Library/LaunchAgents/com.antigravity.anomaly.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.antigravity.anomaly</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/bishalbarua/Bishal/AI/antigravity/Google Ads Manager/scripts/anomaly_monitor.py</string>
        <string>--save</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/bishalbarua/Bishal/AI/antigravity/Google Ads Manager</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/bishalbarua/Bishal/AI/antigravity/Google Ads Manager/logs/anomaly.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/bishalbarua/Bishal/AI/antigravity/Google Ads Manager/logs/anomaly.err</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HOME</key>
        <string>/Users/bishalbarua</string>
    </dict>
</dict>
</plist>
```

Load with: `launchctl load ~/Library/LaunchAgents/com.antigravity.anomaly.plist`

---

## Create logs directory

Run once before enabling cron:

```bash
mkdir -p "/Users/bishalbarua/Bishal/AI/antigravity/Google Ads Manager/logs"
```

---

## Verify a script runs correctly before scheduling

Always test manually first:

```bash
cd "/Users/bishalbarua/Bishal/AI/antigravity/Google Ads Manager"
source .env
python3 scripts/anomaly_monitor.py --customer-id 5216656756  # single client test
python3 scripts/anomaly_monitor.py --save                    # full run with file output
```

---

## Google Ads JS Script Schedules

These run inside the Google Ads UI. Set the schedule in each script's settings:

| Script | Schedule | Account level |
|---|---|---|
| `budget-pacing-alert.js` | Daily at 2pm | Per client account |
| `conversion-drop-alert.js` | Daily at 8am | Per client account |
| `impression-share-monitor.js` | Weekly (Mon) | Per client account |
| `zero-impression-keywords.js` | Weekly (Mon) | Per client account |
| `quality-score-tracker.js` | Weekly (Mon) | Per client account |
| `auction-insights-tracker.js` | Weekly (Mon) | Per client account |
| `search-term-auto-negatives.js` | Weekly (Mon) | Per client account |
| `rsa-ad-strength-audit.js` | Weekly (Mon) | Per client account |
| `label-performance-tagger.js` | Weekly (Mon) | Per client account |

To set a schedule in Google Ads: Tools > Scripts > click the script > Edit > Schedule

---

## Prerequisites before enabling full automation

1. Anomaly monitor running cleanly for 7 days (no false positives)
2. MCC rollup tested against all 13 accounts (check for API errors)
3. Log directory created
4. .env accessible from cron (test with wrapper script)
5. `reports/` directory exists (scripts create it automatically)
