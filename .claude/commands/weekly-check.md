# Weekly Check

Run a quick performance check across all active clients and surface anything that needs attention this week.

## Usage
`/weekly-check`

## Instructions

1. **Load the client list** from CLAUDE.md. These are the active accounts to check.

2. **For each client**, pull last 7 days vs prior 7 days using the Google Ads API:
   - Spend, clicks, impressions, conversions, CPA, CTR
   - Flag any metric that changed by more than 20% week-over-week

3. **Flag critical issues** for immediate attention:
   - Spend dropped >30% (campaign paused? billing issue?)
   - Conversions dropped >30%
   - CPA spiked >50% above normal
   - Any campaign showing $0 spend (likely paused or error)
   - Any account with zero conversions this week (if they normally convert)

4. **Flag budget issues:**
   - Campaigns limited by budget
   - Campaigns underspending by >40% of daily budget

5. **Format the output** as a scannable weekly digest:

   ```
   # Weekly Check — [Date]

   ## Needs Immediate Attention 🔴
   [Clients with critical issues — what happened, what to check]

   ## Worth Reviewing 🟡
   [Clients with notable changes — metric, change %, context]

   ## Looking Normal 🟢
   [Clients with no significant changes — one-liner each]

   ## Summary
   - Total accounts checked: X
   - Accounts flagged: X
   - Combined spend this week: $X
   - Combined conversions this week: X
   ```

6. **Do not save** this report — it's a live snapshot. Just output it inline.

7. After the digest, ask: "Want me to dig deeper into any of these?"
