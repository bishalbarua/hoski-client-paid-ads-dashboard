# P2 — Google Ads JavaScript Scripts (In-Platform)

## Problem
The `google-ads-scripts/` folder exists but is empty. Google Ads Scripts run natively inside the Google Ads UI on a schedule — they can trigger alerts, make bid adjustments, and send emails without any external infrastructure. This is a capability gap.

## Why This Matters
Google Ads Scripts have access to real-time data and can run on hourly/daily schedules directly inside the platform. They are free, require no server, and can email alerts or make changes instantly. This is separate from and complementary to the Python API setup.

## Scripts to Build

### 1. Budget Pacing Alert (`budget-pacing-alert.js`)
Runs daily at 2pm. If any campaign is on pace to over- or under-spend by >15%, sends an email alert.

### 2. Conversion Drop Alert (`conversion-drop-alert.js`)
Runs daily. If conversions in the last 3 days are down >40% vs the prior 3 days, sends an email with the affected campaigns listed.

### 3. Impression Share Monitor (`impression-share-monitor.js`)
Runs weekly. Flags any campaign where IS dropped >10 points WoW. Useful for catching competitor spend increases early.

### 4. Zero Impression Keywords (`zero-impression-keywords.js`)
Runs weekly. Lists all active keywords with 0 impressions in the last 14 days — candidates for pausing or match type changes.

### 5. Quality Score Tracker (`quality-score-tracker.js`)
Runs weekly. Logs quality scores to a Google Sheet over time to track improvement trends.

## Implementation Notes
- Each script must include a header block: purpose, setup steps, changelog (per CLAUDE.md preferences)
- Scripts should use `MailApp.sendEmail()` for alerts, not just Logger output
- Target email: configure as a constant at the top of each script
- Scripts go in `google-ads-scripts/` — one file per script
- Each script designed to be copy-pasted directly into Google Ads UI (Tools > Scripts)

## Files to Create
- `google-ads-scripts/budget-pacing-alert.js`
- `google-ads-scripts/conversion-drop-alert.js`
- `google-ads-scripts/impression-share-monitor.js`
- `google-ads-scripts/zero-impression-keywords.js`
- `google-ads-scripts/quality-score-tracker.js`

## Status
- [ ] Not started
