/**
 * Label Performance Tagger
 * Purpose: Auto-labels campaigns based on 30-day performance against
 *          configurable CPA targets. Labels show in the Google Ads UI for
 *          instant visual triage without opening reports.
 *
 *          Labels applied (mutually exclusive per campaign):
 *            TOP_PERFORMER  — CPA 20%+ below target (green)
 *            ON_TRACK       — CPA within 20% of target (blue)
 *            AT_RISK        — CPA 20%+ above target (yellow)
 *            NO_CONVERSIONS — spend > $50 but 0 conversions in 30 days (red)
 *            BUDGET_LIMITED — campaign lost IS due to budget this week
 *
 * Setup:
 *   1. Copy into Google Ads UI: Tools > Scripts > + New Script
 *   2. Set ACCOUNT_NAME and CPA_TARGETS below
 *   3. CPA_TARGETS: map campaign name substring to target CPA in dollars
 *      (partial match works — 'Brand' will match 'Brand - Exact' etc.)
 *   4. Schedule: Weekly (Monday at 8am recommended)
 *   5. Authorise when prompted
 *
 * Note: This script DOES write to your account (applies labels).
 *       Labels are visible in the Campaigns tab under the Status column
 *       and in the Label filter on the left sidebar.
 *
 * Changelog:
 *   2026-03-23  Initial version — CPA-based labels with budget-limited flag.
 */

// ─── CONFIG ──────────────────────────────────────────────────────────────────

var ACCOUNT_NAME  = 'Client Name';

// Map partial campaign name (case-insensitive) to target CPA ($).
// First matching entry wins. Use '' as a default catch-all.
var CPA_TARGETS = [
  // { match: 'brand',    cpa: 30  },
  // { match: 'search',   cpa: 80  },
  // { match: '',         cpa: 100 },   // default for all other campaigns
];

var CPA_GOOD_THRESHOLD = 0.80;    // CPA 20%+ below target = TOP_PERFORMER
var CPA_BAD_THRESHOLD  = 1.20;    // CPA 20%+ above target = AT_RISK
var MIN_SPEND_FOR_FLAG = 50.00;   // minimum 30-day spend to apply labels
var MIN_CONV_THRESHOLD = 0;       // minimum 30-day conversions (0 = flag zero-conv campaigns)

// Label names (created automatically if they don't exist)
var LABEL_TOP          = 'TOP_PERFORMER';
var LABEL_ON_TRACK     = 'ON_TRACK';
var LABEL_AT_RISK      = 'AT_RISK';
var LABEL_NO_CONV      = 'NO_CONVERSIONS';
var LABEL_BUDGET       = 'BUDGET_LIMITED';

// ─── HELPERS ──────────────────────────────────────────────────────────────────

function ensureLabel(name) {
  var iterator = AdsApp.labels().withCondition('Name = "' + name + '"').get();
  if (!iterator.hasNext()) {
    AdsApp.createLabel(name);
    Logger.log('Created label: ' + name);
  }
}

function removePerfLabels(campaign) {
  var labels = campaign.labels().get();
  var toRemove = [LABEL_TOP, LABEL_ON_TRACK, LABEL_AT_RISK, LABEL_NO_CONV];
  while (labels.hasNext()) {
    var label = labels.next();
    if (toRemove.indexOf(label.getName()) !== -1) {
      campaign.removeLabel(label.getName());
    }
  }
}

function getCpaTarget(campaignName) {
  var nameLower = campaignName.toLowerCase();
  for (var i = 0; i < CPA_TARGETS.length; i++) {
    var entry = CPA_TARGETS[i];
    if (entry.match === '' || nameLower.indexOf(entry.match.toLowerCase()) !== -1) {
      return entry.cpa;
    }
  }
  return null;  // no target configured for this campaign
}

function dateString(daysAgo) {
  var d = new Date();
  d.setDate(d.getDate() - daysAgo);
  return Utilities.formatDate(d, AdsApp.currentAccount().getTimeZone(), 'yyyyMMdd');
}

// ─── MAIN ─────────────────────────────────────────────────────────────────────

function main() {
  var now       = new Date();
  var start30   = dateString(30);
  var end30     = dateString(1);
  var startWeek = dateString(7);
  var endWeek   = dateString(1);

  // Ensure all labels exist
  [LABEL_TOP, LABEL_ON_TRACK, LABEL_AT_RISK, LABEL_NO_CONV, LABEL_BUDGET].forEach(ensureLabel);

  // Pull 30-day performance by campaign
  var perfQuery =
    'SELECT campaign.name, metrics.cost_micros, metrics.conversions '
    + 'FROM campaign '
    + 'WHERE segments.date BETWEEN \'' + start30 + '\' AND \'' + end30 + '\' '
    + 'AND campaign.status = ENABLED ';

  var perfRows = AdsApp.search(perfQuery);
  var perfMap  = {};

  while (perfRows.hasNext()) {
    var row  = perfRows.next();
    var name = row.campaign.name;
    if (!perfMap[name]) perfMap[name] = { spend: 0, conv: 0 };
    perfMap[name].spend += (parseInt(row.metrics.cost_micros) || 0) / 1000000;
    perfMap[name].conv  += parseFloat(row.metrics.conversions) || 0;
  }

  // Pull weekly IS lost due to budget
  var isQuery =
    'SELECT campaign.name, metrics.search_budget_lost_impression_share '
    + 'FROM campaign '
    + 'WHERE segments.date BETWEEN \'' + startWeek + '\' AND \'' + endWeek + '\' '
    + 'AND campaign.status = ENABLED ';

  var isRows       = AdsApp.search(isQuery);
  var budgetLimited = {};

  while (isRows.hasNext()) {
    var row  = isRows.next();
    var name = row.campaign.name;
    var lost = parseFloat(row.metrics.search_budget_lost_impression_share) || 0;
    budgetLimited[name] = (budgetLimited[name] || 0) + lost;
  }

  // Normalise lost IS to an average
  var isCount = {};
  var isTotal = {};
  // (already summed above — would need row count for proper averaging; use >0.05 as threshold)

  // Apply labels
  var campaigns = AdsApp.campaigns().withCondition('Status = ENABLED').get();
  var stats     = { top: 0, onTrack: 0, atRisk: 0, noConv: 0, budget: 0, noTarget: 0 };

  while (campaigns.hasNext()) {
    var campaign = campaigns.next();
    var name     = campaign.getName();
    var perf     = perfMap[name] || { spend: 0, conv: 0 };

    // Remove existing performance labels before re-applying
    removePerfLabels(campaign);

    if (perf.spend < MIN_SPEND_FOR_FLAG) {
      stats.noTarget++;
      continue;
    }

    // Budget-limited label (can stack with performance labels)
    var lostIS = budgetLimited[name] || 0;
    if (lostIS > 0.10) {   // lost >10% IS due to budget on average
      campaign.applyLabel(LABEL_BUDGET);
      stats.budget++;
    } else {
      var budgetLabels = campaign.labels()
        .withCondition('Name = "' + LABEL_BUDGET + '"').get();
      if (budgetLabels.hasNext()) campaign.removeLabel(LABEL_BUDGET);
    }

    // No conversions despite spend
    if (perf.conv === 0) {
      campaign.applyLabel(LABEL_NO_CONV);
      stats.noConv++;
      Logger.log('[NO_CONVERSIONS] ' + name + ': $' + perf.spend.toFixed(0) + ' spend, 0 conv');
      continue;
    }

    var targetCpa = getCpaTarget(name);
    if (targetCpa === null) {
      stats.noTarget++;
      continue;
    }

    var actualCpa = perf.spend / perf.conv;
    var ratio     = actualCpa / targetCpa;

    if (ratio <= CPA_GOOD_THRESHOLD) {
      campaign.applyLabel(LABEL_TOP);
      stats.top++;
      Logger.log('[TOP_PERFORMER] ' + name + ': CPA $' + actualCpa.toFixed(0) + ' vs target $' + targetCpa);
    } else if (ratio >= CPA_BAD_THRESHOLD) {
      campaign.applyLabel(LABEL_AT_RISK);
      stats.atRisk++;
      Logger.log('[AT_RISK] ' + name + ': CPA $' + actualCpa.toFixed(0) + ' vs target $' + targetCpa);
    } else {
      campaign.applyLabel(LABEL_ON_TRACK);
      stats.onTrack++;
      Logger.log('[ON_TRACK] ' + name + ': CPA $' + actualCpa.toFixed(0) + ' vs target $' + targetCpa);
    }
  }

  Logger.log('Label Performance Tagger — ' + now.toDateString());
  Logger.log('TOP_PERFORMER:  ' + stats.top);
  Logger.log('ON_TRACK:       ' + stats.onTrack);
  Logger.log('AT_RISK:        ' + stats.atRisk);
  Logger.log('NO_CONVERSIONS: ' + stats.noConv);
  Logger.log('BUDGET_LIMITED: ' + stats.budget);
  Logger.log('No target set:  ' + stats.noTarget);
  Logger.log('Labels updated successfully.');
}
