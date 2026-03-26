/**
 * Search Term Negative Candidate Finder
 * Purpose: Finds search terms with significant clicks but zero conversions
 *          in the last 30 days that are not already in any negative keyword
 *          list. Outputs a review list to Logger and email for manual approval.
 *
 *          IMPORTANT: This script does NOT automatically add negative keywords.
 *          It produces a candidate list for human review and approval only.
 *          Review before adding to avoid blocking legitimate traffic.
 *
 * Setup:
 *   1. Copy into Google Ads UI: Tools > Scripts > + New Script
 *   2. Set ALERT_EMAIL, ACCOUNT_NAME below
 *   3. Tune MIN_CLICKS to adjust sensitivity
 *   4. Schedule: Weekly (Monday at 8am recommended)
 *   5. Authorise when prompted
 *
 * Output per candidate:
 *   Search Term | Clicks | Cost | Campaign | Campaign Type
 *
 * Before adding negatives, ask:
 *   - Could this term convert on a longer window (check attribution)?
 *   - Is this a brand term for a related product we serve?
 *   - Does this term appear in top converting queries with slight variations?
 *
 * Changelog:
 *   2026-03-23  Initial version — zero-conversion candidates, existing negative
 *               check, cost-sorted output.
 */

// ─── CONFIG ──────────────────────────────────────────────────────────────────

var ALERT_EMAIL      = 'your@email.com';
var ACCOUNT_NAME     = 'Client Name';

var MIN_CLICKS       = 5;      // minimum clicks to surface a term
var LOOKBACK_DAYS    = 30;     // search term data window
var MAX_EMAIL_ROWS   = 100;    // cap email output

// ─── HELPERS ──────────────────────────────────────────────────────────────────

function dateString(daysAgo) {
  var d = new Date();
  d.setDate(d.getDate() - daysAgo);
  return Utilities.formatDate(d, AdsApp.currentAccount().getTimeZone(), 'yyyyMMdd');
}

function getExistingNegatives() {
  // Collect all campaign-level and account-level negative keyword texts
  var negatives = new Set();

  // Account-level negative lists
  var sharedSets = AdsApp.negativeKeywordLists().get();
  while (sharedSets.hasNext()) {
    var list = sharedSets.next();
    var kws  = list.negativeKeywords().get();
    while (kws.hasNext()) {
      negatives.add(kws.next().getText().toLowerCase().replace(/[+"\[\]]/g, ''));
    }
  }

  // Campaign-level negatives
  var campaigns = AdsApp.campaigns().withCondition('Status = ENABLED').get();
  while (campaigns.hasNext()) {
    var campaign = campaigns.next();
    var negKws   = campaign.negativeKeywords().get();
    while (negKws.hasNext()) {
      negatives.add(negKws.next().getText().toLowerCase().replace(/[+"\[\]]/g, ''));
    }
  }

  return negatives;
}

// ─── MAIN ─────────────────────────────────────────────────────────────────────

function main() {
  var now       = new Date();
  var startDate = dateString(LOOKBACK_DAYS);
  var endDate   = dateString(1);

  // Pull all search terms with their performance
  var query =
    'SELECT '
    + 'search_term_view.search_term, '
    + 'campaign.name, '
    + 'campaign.advertising_channel_type, '
    + 'metrics.clicks, '
    + 'metrics.conversions, '
    + 'metrics.cost_micros '
    + 'FROM search_term_view '
    + 'WHERE segments.date BETWEEN \'' + startDate + '\' AND \'' + endDate + '\' '
    + 'AND search_term_view.status = NONE '   // NONE = not already a keyword
    + 'AND campaign.status = ENABLED ';

  var rows    = AdsApp.search(query);
  var termMap = {};

  while (rows.hasNext()) {
    var row  = rows.next();
    var term = row.search_term_view.search_term;
    var key  = term + '|||' + row.campaign.name;

    if (!termMap[key]) {
      termMap[key] = {
        term:     term,
        campaign: row.campaign.name,
        type:     row.campaign.advertising_channel_type,
        clicks:   0,
        conv:     0,
        cost:     0,
      };
    }
    termMap[key].clicks += parseInt(row.metrics.clicks) || 0;
    termMap[key].conv   += parseFloat(row.metrics.conversions) || 0;
    termMap[key].cost   += (parseInt(row.metrics.cost_micros) || 0) / 1000000;
  }

  // Get existing negatives to filter them out
  var existingNegatives = getExistingNegatives();

  // Filter: min clicks, zero conversions, not already negative
  var candidates = Object.values(termMap).filter(function(t) {
    return t.clicks >= MIN_CLICKS
        && t.conv === 0
        && !existingNegatives.has(t.term.toLowerCase());
  });

  // Sort by cost descending (highest wasted spend first)
  candidates.sort(function(a, b) { return b.cost - a.cost; });

  Logger.log('Search Term Negative Candidates — ' + now.toDateString());
  Logger.log('Window: last ' + LOOKBACK_DAYS + ' days');
  Logger.log('Candidates (>= ' + MIN_CLICKS + ' clicks, 0 conv, not already negative): '
             + candidates.length);

  if (candidates.length === 0) {
    Logger.log('No negative candidates found matching criteria.');
    return;
  }

  var totalWasted = candidates.reduce(function(sum, t) { return sum + t.cost; }, 0);
  Logger.log('Total spend on candidates: $' + totalWasted.toFixed(2));

  candidates.slice(0, 30).forEach(function(t) {
    Logger.log('  $' + t.cost.toFixed(2) + ' | ' + t.clicks + ' clicks | '
               + t.campaign + ' | "' + t.term + '"');
  });

  // Build email
  var shown = candidates.slice(0, MAX_EMAIL_ROWS);

  var body = 'NEGATIVE KEYWORD CANDIDATES — REVIEW REQUIRED\n';
  body    += ACCOUNT_NAME + ' — ' + now.toDateString() + '\n';
  body    += 'Window: last ' + LOOKBACK_DAYS + ' days\n';
  body    += 'IMPORTANT: Review each term before adding as a negative.\n';
  body    += '====================================\n\n';
  body    += 'Total candidates: ' + candidates.length + '\n';
  body    += 'Total wasted spend: $' + totalWasted.toFixed(2) + '\n\n';
  body    += 'Sorted by cost (highest wasted spend first):\n\n';
  body    += 'Cost | Clicks | Campaign | Search Term\n';
  body    += '----------------------------------------------------\n';

  shown.forEach(function(t) {
    body += '$' + t.cost.toFixed(2) + ' | ' + t.clicks + ' | ' + t.campaign
            + ' | "' + t.term + '"\n';
  });

  if (candidates.length > MAX_EMAIL_ROWS) {
    body += '\n... and ' + (candidates.length - MAX_EMAIL_ROWS) + ' more (truncated)\n';
  }

  body += '\n====================================\n';
  body += 'DO NOT add all of these as negatives automatically.\n';
  body += 'Review each term for:\n';
  body += '  - Brand terms for products/services you actually offer\n';
  body += '  - Terms that may convert on longer attribution windows\n';
  body += '  - Informational queries that could be retargeting opportunities\n';

  var subject = '[' + ACCOUNT_NAME + '] ' + candidates.length + ' Negative Candidates ($'
                + totalWasted.toFixed(0) + ' wasted) — ' + now.toDateString();

  MailApp.sendEmail(ALERT_EMAIL, subject, body);
  Logger.log('Report sent to: ' + ALERT_EMAIL);
}
