/**
 * Impression Share Monitor
 * Purpose: Compares Search Impression Share (IS) and Lost IS (budget/rank)
 *          for the current week vs prior week at campaign level. Sends an
 *          email alert if IS dropped more than the threshold — early warning
 *          for competitor budget increases or Quality Score problems.
 *
 * Setup:
 *   1. Copy into Google Ads UI: Tools > Scripts > + New Script
 *   2. Set ALERT_EMAIL and ACCOUNT_NAME below
 *   3. Schedule: Weekly (Monday at 8am recommended)
 *   4. Authorise when prompted
 *
 * Detection logic:
 *   This week:   last 7 complete days (yesterday through 7 days ago)
 *   Prior week:  8 through 14 days ago
 *   Alert if:    IS dropped >IS_DROP_THRESHOLD absolute points WoW
 *   Also shows:  Lost IS (Budget) and Lost IS (Rank) for diagnosis
 *
 * Changelog:
 *   2026-03-23  Initial version — campaign-level IS WoW with diagnosis fields.
 */

// ─── CONFIG ──────────────────────────────────────────────────────────────────

var ALERT_EMAIL        = 'your@email.com';
var ACCOUNT_NAME       = 'Client Name';

var IS_DROP_THRESHOLD  = 10;    // alert if IS dropped >10 absolute percentage points
var MIN_IMPRESSIONS    = 100;   // minimum prior-week impressions to include a campaign

// ─── HELPERS ──────────────────────────────────────────────────────────────────

function getIsByDateRange(startDate, endDate) {
  var result = {};
  var query  =
    'SELECT campaign.name, metrics.impressions, '
    + 'metrics.search_impression_share, '
    + 'metrics.search_budget_lost_impression_share, '
    + 'metrics.search_rank_lost_impression_share '
    + 'FROM campaign '
    + 'WHERE segments.date BETWEEN \'' + startDate + '\' AND \'' + endDate + '\' '
    + 'AND campaign.status = ENABLED '
    + 'AND campaign.advertising_channel_type = SEARCH';

  var rows = AdsApp.search(query);
  while (rows.hasNext()) {
    var row         = rows.next();
    var name        = row.campaign.name;
    var impressions = parseInt(row.metrics.impressions) || 0;
    var is_share    = parseFloat(row.metrics.search_impression_share) || 0;
    var lost_budget = parseFloat(row.metrics.search_budget_lost_impression_share) || 0;
    var lost_rank   = parseFloat(row.metrics.search_rank_lost_impression_share) || 0;

    if (!result[name]) {
      result[name] = { impressions: 0, is_total: 0, lost_budget_total: 0, lost_rank_total: 0, rows: 0 };
    }
    result[name].impressions         += impressions;
    result[name].is_total            += is_share;
    result[name].lost_budget_total   += lost_budget;
    result[name].lost_rank_total     += lost_rank;
    result[name].rows                += 1;
  }

  // Average the IS values (they're daily rates, not sums)
  Object.keys(result).forEach(function(name) {
    var d = result[name];
    if (d.rows > 0) {
      d.is          = d.is_total          / d.rows;
      d.lost_budget = d.lost_budget_total / d.rows;
      d.lost_rank   = d.lost_rank_total   / d.rows;
    }
  });

  return result;
}

function dateString(daysAgo) {
  var d = new Date();
  d.setDate(d.getDate() - daysAgo);
  return Utilities.formatDate(d, AdsApp.currentAccount().getTimeZone(), 'yyyyMMdd');
}

// ─── MAIN ─────────────────────────────────────────────────────────────────────

function main() {
  var now = new Date();

  var thisStart  = dateString(7);
  var thisEnd    = dateString(1);
  var priorStart = dateString(14);
  var priorEnd   = dateString(8);

  var thisWeek  = getIsByDateRange(thisStart,  thisEnd);
  var priorWeek = getIsByDateRange(priorStart, priorEnd);

  var issues   = [];
  var allNames = new Set(Object.keys(thisWeek).concat(Object.keys(priorWeek)));

  allNames.forEach(function(name) {
    var curr = thisWeek[name]  || { is: 0, lost_budget: 0, lost_rank: 0, impressions: 0 };
    var prev = priorWeek[name] || { is: 0, lost_budget: 0, lost_rank: 0, impressions: 0 };

    if (prev.impressions < MIN_IMPRESSIONS) return;
    if (prev.is === 0) return;

    var drop = (prev.is - curr.is) * 100;  // convert to percentage points
    if (drop >= IS_DROP_THRESHOLD) {
      var diagnosis = '';
      if (curr.lost_budget > curr.lost_rank) {
        diagnosis = 'Budget-constrained (increase daily budget to recover IS)';
      } else if (curr.lost_rank > curr.lost_budget) {
        diagnosis = 'Rank-limited (improve QS or increase bids to recover IS)';
      } else {
        diagnosis = 'Mixed budget/rank loss';
      }

      issues.push({
        campaign:    name,
        drop:        drop,
        thisIs:      curr.is * 100,
        priorIs:     prev.is * 100,
        lostBudget:  curr.lost_budget * 100,
        lostRank:    curr.lost_rank * 100,
        diagnosis:   diagnosis,
      });
    }
  });

  // Sort by drop severity
  issues.sort(function(a, b) { return b.drop - a.drop; });

  Logger.log('Impression Share Monitor — ' + now.toDateString());
  Logger.log('This week: ' + thisStart + ' to ' + thisEnd);
  Logger.log('Prior week: ' + priorStart + ' to ' + priorEnd);
  Logger.log('Campaigns with IS drop >' + IS_DROP_THRESHOLD + 'pts: ' + issues.length);

  if (issues.length === 0) {
    Logger.log('No significant IS drops detected.');
    return;
  }

  var body = 'IMPRESSION SHARE DROP ALERT\n';
  body    += ACCOUNT_NAME + ' — ' + now.toDateString() + '\n';
  body    += 'This week: ' + thisStart + ' to ' + thisEnd + '\n';
  body    += 'Prior week: ' + priorStart + ' to ' + priorEnd + '\n';
  body    += '====================================\n\n';

  issues.forEach(function(i) {
    body += '[' + i.campaign + ']\n';
    body += '  IS: ' + i.priorIs.toFixed(1) + '% (prior) -> ' + i.thisIs.toFixed(1) + '% (this week) '
            + '(dropped ' + i.drop.toFixed(1) + ' pts)\n';
    body += '  Lost IS (Budget): ' + i.lostBudget.toFixed(1) + '%\n';
    body += '  Lost IS (Rank):   ' + i.lostRank.toFixed(1) + '%\n';
    body += '  Diagnosis: ' + i.diagnosis + '\n\n';
  });

  body += '====================================\n';
  body += 'Log into Google Ads to investigate.\n';

  var subject = '[' + ACCOUNT_NAME + '] IS Drop Alert — '
                + issues.length + ' campaign(s) — ' + now.toDateString();

  MailApp.sendEmail(ALERT_EMAIL, subject, body);
  Logger.log('Alert sent to: ' + ALERT_EMAIL);

  issues.forEach(function(i) {
    Logger.log(i.campaign + ': -' + i.drop.toFixed(1) + ' pts IS (' + i.diagnosis + ')');
  });
}
