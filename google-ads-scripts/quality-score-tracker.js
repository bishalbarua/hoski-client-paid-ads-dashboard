/**
 * Quality Score Tracker
 * Purpose: Logs keyword-level Quality Scores (QS, Expected CTR, Ad Relevance,
 *          Landing Page Experience) to a Google Sheet each week. Builds a
 *          historical trend so you can track QS improvement over time.
 *
 * Setup:
 *   1. Create a Google Sheet and note the Spreadsheet ID from the URL
 *      (the long string between /d/ and /edit)
 *   2. Copy into Google Ads UI: Tools > Scripts > + New Script
 *   3. Set SPREADSHEET_ID, SHEET_NAME, ACCOUNT_NAME, and ALERT_EMAIL below
 *   4. Schedule: Weekly (Monday at 8am recommended)
 *   5. Authorise when prompted (requires Sheets access)
 *
 * Sheet structure (one row per keyword per run):
 *   Date | Account | Campaign | Ad Group | Keyword | Match Type |
 *   QS | Expected CTR | Ad Relevance | Landing Page | Bid | Impressions (30d)
 *
 * QS component values:
 *   ABOVE_AVERAGE = 3  |  AVERAGE = 2  |  BELOW_AVERAGE = 1  |  UNKNOWN = 0
 *
 * Changelog:
 *   2026-03-23  Initial version — weekly QS snapshot with all components.
 */

// ─── CONFIG ──────────────────────────────────────────────────────────────────

var SPREADSHEET_ID  = 'YOUR_SPREADSHEET_ID';   // from sheet URL
var SHEET_NAME      = 'QS Tracker';            // tab name (created if it does not exist)
var ACCOUNT_NAME    = 'Client Name';
var ALERT_EMAIL     = 'your@email.com';        // optional: email on completion

var MIN_IMPRESSIONS = 0;   // set to 100 to only track keywords with some traffic
var MAX_KEYWORDS    = 2000; // safety cap to avoid Sheets quota errors

// ─── HELPERS ──────────────────────────────────────────────────────────────────

function componentScore(value) {
  // Convert GAQL enum string to numeric 1-3 for easier trending
  if (value === 'ABOVE_AVERAGE') return 3;
  if (value === 'AVERAGE')       return 2;
  if (value === 'BELOW_AVERAGE') return 1;
  return 0;
}

function componentLabel(value) {
  if (value === 'ABOVE_AVERAGE') return 'Above Avg';
  if (value === 'AVERAGE')       return 'Average';
  if (value === 'BELOW_AVERAGE') return 'Below Avg';
  return 'Unknown';
}

function getOrCreateSheet(spreadsheet, sheetName) {
  var sheet = spreadsheet.getSheetByName(sheetName);
  if (!sheet) {
    sheet = spreadsheet.insertSheet(sheetName);
    // Write header row
    sheet.appendRow([
      'Date', 'Account', 'Campaign', 'Ad Group', 'Keyword', 'Match Type',
      'QS', 'Expected CTR', 'Ad Relevance', 'Landing Page',
      'QS Score (1-10)', 'CTR Score (1-3)', 'Rel Score (1-3)', 'LP Score (1-3)',
      'Bid ($)', 'Impressions (30d)'
    ]);
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function dateString(daysAgo) {
  var d = new Date();
  d.setDate(d.getDate() - daysAgo);
  return Utilities.formatDate(d, AdsApp.currentAccount().getTimeZone(), 'yyyyMMdd');
}

// ─── MAIN ─────────────────────────────────────────────────────────────────────

function main() {
  var now       = new Date();
  var runDate   = Utilities.formatDate(now, AdsApp.currentAccount().getTimeZone(), 'yyyy-MM-dd');
  var start30   = dateString(30);
  var end30     = dateString(1);

  // Pull keyword QS data — QS fields don't require a date segment
  var query =
    'SELECT '
    + 'campaign.name, '
    + 'ad_group.name, '
    + 'ad_group_criterion.keyword.text, '
    + 'ad_group_criterion.keyword.match_type, '
    + 'ad_group_criterion.cpc_bid_micros, '
    + 'ad_group_criterion.quality_info.quality_score, '
    + 'ad_group_criterion.quality_info.creative_quality_score, '
    + 'ad_group_criterion.quality_info.post_click_quality_score, '
    + 'ad_group_criterion.quality_info.search_predicted_ctr, '
    + 'metrics.impressions '
    + 'FROM keyword_view '
    + 'WHERE segments.date BETWEEN \'' + start30 + '\' AND \'' + end30 + '\' '
    + 'AND ad_group_criterion.status = ENABLED '
    + 'AND ad_group.status = ENABLED '
    + 'AND campaign.status = ENABLED ';

  var rows   = AdsApp.search(query);
  var keyMap = {};

  while (rows.hasNext()) {
    var row = rows.next();
    var key = row.campaign.name + '|||'
            + row.ad_group.name + '|||'
            + row.ad_group_criterion.keyword.text + '|||'
            + row.ad_group_criterion.keyword.match_type;

    if (!keyMap[key]) {
      keyMap[key] = {
        campaign:    row.campaign.name,
        adGroup:     row.ad_group.name,
        keyword:     row.ad_group_criterion.keyword.text,
        matchType:   row.ad_group_criterion.keyword.match_type,
        bidMicros:   parseInt(row.ad_group_criterion.cpc_bid_micros) || 0,
        qs:          parseInt(row.ad_group_criterion.quality_info.quality_score) || 0,
        expectedCtr: row.ad_group_criterion.quality_info.search_predicted_ctr,
        adRelevance: row.ad_group_criterion.quality_info.creative_quality_score,
        landingPage: row.ad_group_criterion.quality_info.post_click_quality_score,
        impressions: 0,
      };
    }
    keyMap[key].impressions += parseInt(row.metrics.impressions) || 0;
  }

  var keywords = Object.values(keyMap)
    .filter(function(k) { return k.impressions >= MIN_IMPRESSIONS; })
    .sort(function(a, b) { return a.qs - b.qs || a.campaign.localeCompare(b.campaign); })
    .slice(0, MAX_KEYWORDS);

  Logger.log('Quality Score Tracker — ' + runDate);
  Logger.log('Keywords to log: ' + keywords.length);

  if (keywords.length === 0) {
    Logger.log('No keywords found matching criteria.');
    return;
  }

  // Open Sheets
  var spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet       = getOrCreateSheet(spreadsheet, SHEET_NAME);

  // Build rows to append
  var rows_to_write = keywords.map(function(k) {
    var bid = k.bidMicros > 0 ? (k.bidMicros / 1000000).toFixed(2) : '';
    return [
      runDate,
      ACCOUNT_NAME,
      k.campaign,
      k.adGroup,
      k.keyword,
      k.matchType,
      componentLabel(k.expectedCtr),
      componentLabel(k.adRelevance),
      componentLabel(k.landingPage),
      k.qs || '',
      componentScore(k.expectedCtr),
      componentScore(k.adRelevance),
      componentScore(k.landingPage),
      bid,
      k.impressions,
    ];
  });

  sheet.getRange(
    sheet.getLastRow() + 1,
    1,
    rows_to_write.length,
    rows_to_write[0].length
  ).setValues(rows_to_write);

  Logger.log('Wrote ' + rows_to_write.length + ' rows to: ' + SHEET_NAME);

  // Summary stats
  var withQS    = keywords.filter(function(k) { return k.qs > 0; });
  var avgQS     = withQS.length > 0
    ? (withQS.reduce(function(sum, k) { return sum + k.qs; }, 0) / withQS.length).toFixed(1)
    : 'n/a';
  var lowQS     = keywords.filter(function(k) { return k.qs > 0 && k.qs <= 4; }).length;
  var highQS    = keywords.filter(function(k) { return k.qs >= 8; }).length;

  Logger.log('Account avg QS: ' + avgQS + ' | QS 1-4: ' + lowQS + ' | QS 8-10: ' + highQS);

  if (ALERT_EMAIL) {
    var body = 'QUALITY SCORE SNAPSHOT — ' + runDate + '\n'
             + ACCOUNT_NAME + '\n'
             + '====================================\n\n'
             + 'Keywords logged:   ' + keywords.length + '\n'
             + 'Account avg QS:    ' + avgQS + '\n'
             + 'Low QS (1-4):      ' + lowQS + '\n'
             + 'High QS (8-10):    ' + highQS + '\n\n'
             + 'Full data logged to Google Sheet: ' + SHEET_NAME + '\n';
    MailApp.sendEmail(ALERT_EMAIL, '[' + ACCOUNT_NAME + '] QS Snapshot — ' + runDate, body);
  }
}
