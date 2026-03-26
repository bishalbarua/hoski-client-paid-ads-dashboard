/**
 * Budget Pacing Alert
 * Purpose: Checks all enabled campaigns against their daily budgets at the
 *          time the script runs. If any campaign is on pace to over- or
 *          under-spend by more than the threshold, sends an email alert.
 *
 * Setup:
 *   1. Copy this script into Google Ads UI: Tools > Scripts > + New Script
 *   2. Set ALERT_EMAIL below to your email address
 *   3. Set ACCOUNT_NAME to a human-readable label (used in email subject)
 *   4. Schedule: Daily at 2pm (account timezone)
 *   5. Authorise the script when prompted
 *
 * Pacing logic:
 *   Expected spend = daily_budget * (hours_elapsed / 24)
 *   Pacing ratio   = actual_today_spend / expected_spend
 *   OVERPACING     if ratio > OVERPACE_THRESHOLD  (will overspend)
 *   UNDERPACING    if ratio < UNDERPACE_THRESHOLD (will underspend)
 *   ZERO SPEND     if spend = $0 and day is >20% elapsed
 *
 * Changelog:
 *   2026-03-23  Initial version.
 */

// ─── CONFIG ──────────────────────────────────────────────────────────────────

var ALERT_EMAIL          = 'your@email.com';
var ACCOUNT_NAME         = 'Client Name';  // used in email subject line

var OVERPACE_THRESHOLD   = 1.15;   // >115% of expected spend
var UNDERPACE_THRESHOLD  = 0.60;   // <60% of expected spend
var MIN_DAY_ELAPSED      = 0.20;   // only flag underpacing after 20% of day has passed
var MIN_BUDGET_THRESHOLD = 1.00;   // ignore campaigns with daily budget below $1

// ─── MAIN ─────────────────────────────────────────────────────────────────────

function main() {
  var now         = new Date();
  var dayFraction = (now.getHours() * 3600 + now.getMinutes() * 60 + now.getSeconds()) / 86400;

  var issues    = [];
  var campaigns = AdsApp.campaigns()
    .withCondition('Status = ENABLED')
    .get();

  while (campaigns.hasNext()) {
    var campaign = campaigns.next();
    var budget   = campaign.getBudget();

    if (!budget) continue;

    var dailyBudget = budget.getAmount();
    if (dailyBudget < MIN_BUDGET_THRESHOLD) continue;

    var stats       = campaign.getStatsFor('TODAY');
    var actualSpend = stats.getCost();

    var expectedSpend = dailyBudget * dayFraction;
    var pacingRatio   = (expectedSpend > 0) ? (actualSpend / expectedSpend) : 0;

    var name = campaign.getName();

    if (actualSpend === 0 && dayFraction >= MIN_DAY_ELAPSED) {
      issues.push({
        level:   'CRITICAL',
        campaign: name,
        message: 'ZERO SPEND — $' + dailyBudget.toFixed(2) + ' budget, $0 spent '
                 + '(' + (dayFraction * 100).toFixed(0) + '% of day elapsed)'
      });
    } else if (pacingRatio > OVERPACE_THRESHOLD) {
      issues.push({
        level:   'WARNING',
        campaign: name,
        message: 'OVERPACING ' + (pacingRatio * 100).toFixed(0) + '% — '
                 + 'spent $' + actualSpend.toFixed(2)
                 + ' of $' + dailyBudget.toFixed(2) + ' budget '
                 + '(expected $' + expectedSpend.toFixed(2) + ')'
      });
    } else if (pacingRatio < UNDERPACE_THRESHOLD && dayFraction >= MIN_DAY_ELAPSED) {
      issues.push({
        level:   'WARNING',
        campaign: name,
        message: 'UNDERPACING ' + (pacingRatio * 100).toFixed(0) + '% — '
                 + 'spent $' + actualSpend.toFixed(2)
                 + ' of $' + dailyBudget.toFixed(2) + ' budget '
                 + '(expected $' + expectedSpend.toFixed(2) + ')'
      });
    }
  }

  var timeStr = now.toLocaleTimeString();
  Logger.log('Budget Pacing Check — ' + timeStr);
  Logger.log('Day elapsed: ' + (dayFraction * 100).toFixed(1) + '%');
  Logger.log('Issues found: ' + issues.length);

  if (issues.length === 0) {
    Logger.log('All campaigns pacing normally.');
    return;
  }

  // Build email body
  var critical = issues.filter(function(i) { return i.level === 'CRITICAL'; });
  var warnings = issues.filter(function(i) { return i.level === 'WARNING'; });

  var body = 'BUDGET PACING ALERT\n';
  body    += ACCOUNT_NAME + ' — ' + now.toDateString() + ' at ' + timeStr + '\n';
  body    += '====================================\n\n';

  if (critical.length > 0) {
    body += 'CRITICAL (' + critical.length + ')\n';
    critical.forEach(function(i) {
      body += '  [' + i.campaign + ']\n';
      body += '  ' + i.message + '\n\n';
    });
  }

  if (warnings.length > 0) {
    body += 'WARNING (' + warnings.length + ')\n';
    warnings.forEach(function(i) {
      body += '  [' + i.campaign + ']\n';
      body += '  ' + i.message + '\n\n';
    });
  }

  body += '====================================\n';
  body += 'Total issues: ' + issues.length + '\n';
  body += 'Check Google Ads to investigate.\n';

  var subject = '[' + ACCOUNT_NAME + '] Budget Pacing Alert — '
                + issues.length + ' issue(s) — ' + now.toDateString();

  MailApp.sendEmail(ALERT_EMAIL, subject, body);
  Logger.log('Alert email sent to: ' + ALERT_EMAIL);

  issues.forEach(function(i) {
    Logger.log('[' + i.level + '] ' + i.campaign + ': ' + i.message);
  });
}
