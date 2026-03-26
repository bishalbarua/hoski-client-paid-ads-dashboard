/**
 * Auction Insights Tracker
 * Purpose: Logs weekly Auction Insights data (competitor impression share,
 *          overlap rate, outranking share, position above rate, top of page
 *          rate) to a Google Sheet. Builds a historical view of who is
 *          entering and exiting your auctions over time.
 *
 * Setup:
 *   1. Create a Google Sheet and note the Spreadsheet ID from the URL
 *   2. Copy into Google Ads UI: Tools > Scripts > + New Script
 *   3. Set SPREADSHEET_ID, ACCOUNT_NAME below
 *   4. Schedule: Weekly (Monday at 8am recommended)
 *   5. Authorise when prompted (requires Sheets access)
 *
 * Sheet structure (one row per competitor per campaign per run):
 *   Date | Account | Campaign | Competitor Domain | Impression Share |
 *   Overlap Rate | Outranking Share | Position Above Rate | Top-of-Page Rate
 *
 * Use this to:
 *   - Spot new competitors entering your auctions
 *   - Track when a competitor increases or decreases budget
 *   - Diagnose IS drops caused by competitor aggression vs budget constraints
 *
 * Changelog:
 *   2026-03-23  Initial version — campaign-level auction insights to Sheets.
 */

// ─── CONFIG ──────────────────────────────────────────────────────────────────

var SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID';
var SHEET_NAME     = 'Auction Insights';
var ACCOUNT_NAME   = 'Client Name';

// ─── HELPERS ──────────────────────────────────────────────────────────────────

function getOrCreateSheet(spreadsheet, sheetName) {
  var sheet = spreadsheet.getSheetByName(sheetName);
  if (!sheet) {
    sheet = spreadsheet.insertSheet(sheetName);
    sheet.appendRow([
      'Date', 'Account', 'Campaign',
      'Competitor', 'Impression Share (%)', 'Overlap Rate (%)',
      'Outranking Share (%)', 'Position Above Rate (%)', 'Top-of-Page Rate (%)'
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

function pct(val) {
  var n = parseFloat(val) || 0;
  return (n * 100).toFixed(1);
}

// ─── MAIN ─────────────────────────────────────────────────────────────────────

function main() {
  var now     = new Date();
  var runDate = Utilities.formatDate(now, AdsApp.currentAccount().getTimeZone(), 'yyyy-MM-dd');
  var start   = dateString(7);
  var end     = dateString(1);

  var query =
    'SELECT '
    + 'campaign.name, '
    + 'auction_insight.domain, '
    + 'metrics.auction_insight_search_impression_share, '
    + 'metrics.auction_insight_search_overlap_rate, '
    + 'metrics.auction_insight_search_outranking_share, '
    + 'metrics.auction_insight_search_position_above_rate, '
    + 'metrics.auction_insight_search_top_impression_percentage '
    + 'FROM auction_insight_campaign '
    + 'WHERE segments.date BETWEEN \'' + start + '\' AND \'' + end + '\' '
    + 'AND campaign.status = ENABLED ';

  var rows   = AdsApp.search(query);
  var data   = {};  // deduplicate by campaign+domain, averaging across days

  while (rows.hasNext()) {
    var row = rows.next();
    var key = row.campaign.name + '|||' + row.auction_insight.domain;

    if (!data[key]) {
      data[key] = {
        campaign:        row.campaign.name,
        competitor:      row.auction_insight.domain,
        is_total:        0,
        overlap_total:   0,
        outrank_total:   0,
        pos_above_total: 0,
        top_total:       0,
        count:           0,
      };
    }
    var d = data[key];
    d.is_total        += parseFloat(row.metrics.auction_insight_search_impression_share) || 0;
    d.overlap_total   += parseFloat(row.metrics.auction_insight_search_overlap_rate) || 0;
    d.outrank_total   += parseFloat(row.metrics.auction_insight_search_outranking_share) || 0;
    d.pos_above_total += parseFloat(row.metrics.auction_insight_search_position_above_rate) || 0;
    d.top_total       += parseFloat(row.metrics.auction_insight_search_top_impression_percentage) || 0;
    d.count           += 1;
  }

  var entries = Object.values(data).map(function(d) {
    var n = d.count;
    return {
      campaign:    d.campaign,
      competitor:  d.competitor,
      is:          (d.is_total / n * 100).toFixed(1),
      overlap:     (d.overlap_total / n * 100).toFixed(1),
      outrank:     (d.outrank_total / n * 100).toFixed(1),
      pos_above:   (d.pos_above_total / n * 100).toFixed(1),
      top:         (d.top_total / n * 100).toFixed(1),
    };
  });

  Logger.log('Auction Insights Tracker — ' + runDate);
  Logger.log('Window: ' + start + ' to ' + end);
  Logger.log('Competitor entries found: ' + entries.length);

  if (entries.length === 0) {
    Logger.log('No auction insights data found. Ensure campaigns have enough impressions.');
    return;
  }

  var spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
  var sheet       = getOrCreateSheet(spreadsheet, SHEET_NAME);

  var rows_to_write = entries.map(function(e) {
    return [
      runDate, ACCOUNT_NAME, e.campaign,
      e.competitor, e.is, e.overlap,
      e.outrank, e.pos_above, e.top
    ];
  });

  sheet.getRange(
    sheet.getLastRow() + 1,
    1,
    rows_to_write.length,
    rows_to_write[0].length
  ).setValues(rows_to_write);

  Logger.log('Wrote ' + rows_to_write.length + ' rows to: ' + SHEET_NAME);

  // Log top competitors by IS
  entries.sort(function(a, b) { return parseFloat(b.is) - parseFloat(a.is); });
  Logger.log('Top competitors by IS this week:');
  entries.slice(0, 10).forEach(function(e) {
    Logger.log('  ' + e.competitor + ': ' + e.is + '% IS | '
               + e.overlap + '% overlap | ' + e.outrank + '% outranking share');
  });
}
