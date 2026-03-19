# Search Terms Analysis

Pull and analyze search terms for a client, identify waste, and build a negative keyword list.

## Usage
`/search-terms [client name or account ID] [optional: last 30 | last 60 | last 90]`

## Instructions

1. **Identify the client** from $ARGUMENTS. Match against the client list in CLAUDE.md. Default date range is last 30 days unless specified.

2. **Read the client context** — read `Google Ads Manager/clients/[client folder]/notes/client-info.md`. Note:
   - Their industry/vertical (to understand what is and isn't relevant)
   - Their brand terms (NEVER add these as negatives)
   - Any competitor campaign notes

3. **Pull search terms data** via Google Ads API:
   ```sql
   SELECT search_term_view.search_term, search_term_view.status,
          campaign.name, ad_group.name,
          metrics.impressions, metrics.clicks, metrics.cost_micros,
          metrics.conversions, metrics.conversions_value
   FROM search_term_view
   WHERE segments.date DURING LAST_30_DAYS
   ORDER BY metrics.cost_micros DESC
   ```
   Adjust the date range if the user specified last 60 or last 90.

4. **Categorize search terms** into:
   - ✅ **Relevant & converting** — keep, consider adding as exact match keywords
   - ⚠️ **Relevant but not converting** — flag for review (may need more data)
   - ❌ **Irrelevant — recommend as negative** — group by theme:
     - Wrong intent (informational, how-to, DIY)
     - Wrong audience (students, job seekers, etc.)
     - Competitor terms (flag separately — may want competitor campaigns)
     - Geographic mismatch
     - Brand terms of unrelated businesses
     - Other / miscellaneous irrelevant

5. **Never add as negatives:**
   - Any brand terms listed in client-info.md
   - High-converting terms even if they look unusual

6. **Calculate waste** — total spend on recommended negatives during the period.

7. **Build the negative keyword list** — for each recommended negative, specify:
   - Keyword text
   - Recommended match type (exact or phrase)
   - Theme / reason
   - Spend in period

8. **Identify top converters** to consider for exact match expansion.

9. **Save the output** to:
   `Google Ads Manager/clients/[client folder]/analysis/[YYYY-MM-DD]_search-terms-analysis.md`

   Format:
   ```
   # [Client Name] — Search Terms Analysis
   ## Period: [date range]

   ### Summary
   - Total search terms reviewed: X
   - Total spend analyzed: $X
   - Estimated wasted spend: $X (X% of total)

   ### Recommended Negatives by Theme
   [grouped table with match type + spend]

   ### Top Converting Terms (Consider Exact Match)
   [table]

   ### Terms to Monitor (Relevant but No Conversions Yet)
   [table]
   ```

10. Confirm the file was saved and show the summary section inline.
