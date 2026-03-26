/**
 * Conversion Drop Alert
 * Purpose: Compares conversions in the last 3 complete days against the prior
 *          3 days at the campaign level. Sends an email alert if any campaign
 *          drops more than the threshold — or if the account drops entirely.
 *
 * Setup:
 *   1. Copy into Google Ads UI: Tools > Scripts > + New Script
 *   2. Set ALERT_EMAIL and ACCOUNT_NAME below
 *   3. Schedule: Daily (run at midnight or first thing in the morning)
 *   4. Authorise the script when prompted
 *
 * Detection logic:
 *   Current window:  yesterday, day-before-yesterday, 3 days ago
 *   Prior window:    4, 5, and 6 days ago
 *   Alert if:        current conversions < prior * (1 - DROP_THRESHOLD)
 *   Also alert if:   account has current_conv = 0 and prior_conv > MIN_ACCOUNT_CONV
 *
 * Changelog:
 *   2026-03-23  Initial version — campaign-level and account-level checks.
 */

// ─── CONFIG ──────────────────────────────────────────────────────────────────

var ALERT_EMAIL          = 'your@email.com';
var ACCOUNT_NAME         = 'Client Name';

var DROP_THRESHOLD       = 0.40;   // alert if conversions drop >40%
var MIN_CAMPAIGN_CONV    = 1;      // minimum prior-period conversions to flag a campaign
var MIN_ACCOUNT_CONV     = 2;      // minimum prior-period account convs to flag zero-conv

// ─── HELPERS ──────────────────────────────────────────────────────────────────

function getDateRange(daysAgoStart, daysAgoEnd) {
  // Returns [startDate, endDate] strings in YYYYMMDD format for AdsApp
  var end   = new Date();
  var start = new Date();
  end.setDate(end.getDate() - daysAgoStart);
  start.setDate(start.getDate() - daysAgoEnd);
  return [
    Utilities.formatDate(start, AdsApp.currentAccount().getTimeZone(), 'yyyyMMdd'),
    Utilities.formatDate(end,   AdsApp.currentAccount().getTimeZone(), 'yyyyMMdd')
  ];
}

function getConversionsByCampaign(startDate, endDate) {
  var result = {};
  var query = 'SELECT campaign.name, metrics.conversions '
            + 'FROM campaign '
            + 'WHERE segments.date BETWEEN \'' + startDate + '\' AND \'' + endDate + '\' '
            + 'AND campaign.status = ENABLED';

  var rows = AdsApp.search(query);
  while (rows.hasNext()) {
    var row  = rows.next();
    var name = row.campaign.name;
    var conv = parseFloat(row.metrics.conversions) || 0;
    result[name] = (result[name] || 0) + conv;
  }
  return result;
}

// ─── MAIN ─────────────────────────────────────────────────────────────────────

function main() {
  var now = new Date();

  // Current: 1-3 days ago | Prior: 4-6 days ago
  var currentRange = getDateRange(1, 3);
  var priorRange   = getDateRange(4, 6);

  var currentConv = getConversionsByCampaign(currentRange[0], currentRange[1]);
  var priorConv   = getConversionsByCampaign(priorRange[0],   priorRange[1]);

  // Account totals
  var accountCurrent = Object.values(currentConv).reduce(function(a, b) { return a + b; }, 0);
  var accountPrior   = Object.values(priorConv).reduce(function(a, b) { return a + b; }, 0);

  var issues = [];

  // Account-level zero conversion check
  if (accountPrior >= MIN_ACCOUNT_CONV && accountCurrent === 0) {
    issues.push({
      level:    'CRITICAL',
      campaign: 'ACCOUNT TOTAL',
      current:  accountCurrent,
      prior:    accountPrior,
      message:  'ZERO CONVERSIONS in last 3 days (prior 3 days had '
                + accountPrior.toFixed(0) + '). Possible tag breakage.'
    });
  }

  // Campaign-level drop checks
  var allCampaigns = new Set(Object.keys(currentConv).concat(Object.keys(priorConv)));
  allCampaigns.forEach(function(name) {
    var curr = currentConv[name] || 0;
    var prev = priorConv[name]   || 0;

    if (prev < MIN_CAMPAIGN_CONV) return;
    if (curr === 0 && accountCurrent === 0) return; // already flagged at account level

    var drop = (prev - curr) / prev;
    if (drop >= DROP_THRESHOLD) {
      var level = (curr === 0) ? 'CRITICAL' : 'WARNING';
      issues.push({
        level:    level,
        campaign: name,
        current:  curr,
        prior:    prev,
        message:  'Conversions down ' + (drop * 100).toFixed(0) + '%: '
                  + curr.toFixed(0) + ' (last 3d) vs '
                  + prev.toFixed(0) + ' (prior 3d)'
      });
    }
  });

  Logger.log('Conversion Drop Check — ' + now.toDateString());
  Logger.log('Account: ' + accountCurrent.toFixed(0) + ' conv (last 3d) vs '
             + accountPrior.toFixed(0) + ' (prior 3d)');
  Logger.log('Issues: ' + issues.length);

  if (issues.length === 0) {
    Logger.log('No significant conversion drops detected.');
    return;
  }

  // Build email
  var critical = issues.filter(function(i) { return i.level === 'CRITICAL'; });
  var warnings = issues.filter(function(i) { return i.level === 'WARNING'; });

  var body = 'CONVERSION DROP ALERT\n';
  body    += ACCOUNT_NAME + ' — ' + now.toDateString() + '\n';
  body    += 'Comparing last 3 days vs prior 3 days\n';
  body    += '====================================\n\n';

  if (critical.length > 0) {
    body += 'CRITICAL (' + critical.length + ')\n';
    critical.forEach(function(i) {
      body += '  [' + i.campaign + ']\n  ' + i.message + '\n\n';
    });
  }

  if (warnings.length > 0) {
    body += 'WARNING (' + warnings.length + ')\n';
    warnings.forEach(function(i) {
      body += '  [' + i.campaign + ']\n  ' + i.message + '\n\n';
    });
  }

  body += '====================================\n';
  body += 'Account total: ' + accountCurrent.toFixed(0) + ' conv (last 3d) vs '
          + accountPrior.toFixed(0) + ' (prior 3d)\n';
  body += 'Log into Google Ads to investigate.\n';

  var subject = '[' + ACCOUNT_NAME + '] Conversion Drop Alert — '
                + issues.length + ' campaign(s) — ' + now.toDateString();

  MailApp.sendEmail(ALERT_EMAIL, subject, body);
  Logger.log('Alert sent to: ' + ALERT_EMAIL);

  issues.forEach(function(i) {
    Logger.log('[' + i.level + '] ' + i.campaign + ': ' + i.message);
  });
}
