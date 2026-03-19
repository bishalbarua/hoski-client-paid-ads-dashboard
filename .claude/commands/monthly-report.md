# Monthly Report

Generate a full monthly performance report for a client and save it to their reports folder.

## Usage
`/monthly-report [client name or account ID]`

## Instructions

1. **Identify the client** from $ARGUMENTS by matching against the client list in CLAUDE.md. If ambiguous, ask for clarification. Get the Google Ads account ID.

2. **Read the client context** — read `Google Ads Manager/clients/[client folder]/notes/client-info.md` so you understand their goals, CPA targets, vertical, and any quirks before analyzing.

3. **Pull last 30 days of data** using the Google Ads API (Python, gRPC):
   - Campaign performance: impressions, clicks, cost, conversions, CPA, CTR, conversion rate
   - Ad group breakdown for top campaigns
   - Top 10 keywords by spend
   - Top 10 search terms by spend
   - Device breakdown (mobile vs desktop vs tablet)
   - Day-of-week performance

4. **Compare to prior 30 days** — calculate MoM change for: spend, conversions, CPA, CTR, conversion rate.

5. **Analyze against targets** from the client-info.md:
   - Are they hitting their lead/conversion goal?
   - Is CPA on target?
   - Is budget being fully utilized?

6. **Run the audit checklist**:
   - Any keywords with spend > $50 and 0 conversions (last 30 days)?
   - Any campaigns limited by budget?
   - Any ad groups with only 1 active RSA?
   - Quality Score issues (keywords with QS < 5)?
   - Any new irrelevant search terms that need negatives?

7. **Write the report** with this structure:
   ```
   # [Client Name] — Monthly Report
   ## Period: [Month Year]

   ### Executive Summary (3–5 sentences)
   ### Key Metrics vs Prior Period (table)
   ### Performance vs Goals
   ### Campaign Breakdown
   ### Top Keywords
   ### Search Terms Highlights + Recommended Negatives
   ### Issues Found
   ### Recommended Actions (prioritized, specific)
   ### What's Working — Do Not Change
   ```

8. **Save the report** to:
   `Google Ads Manager/clients/[client folder]/reports/[YYYY-MM]_monthly-report.md`

9. Confirm the file was saved and show the executive summary inline.
