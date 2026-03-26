/**
 * Zero Impression Keywords
 * Purpose: Finds all active keywords that received 0 impressions in the last
 *          14 days. Logs results and sends an email with the full list.
 *          These keywords are dead weight — candidates for pausing, bid
 *          increases, or match type changes.
 *
 * Setup:
 *   1. Copy into Google Ads UI: Tools > Scripts > + New Script
 *   2. Set ALERT_EMAIL and ACCOUNT_NAME below
 *   3. Schedule: Weekly (Monday at 8am recommended)
 *   4. Authorise when prompted
 *
 * Output per keyword:
 *   Campaign | Ad Group | Keyword | Match Type | Bid | Quality Score | Status
 *
 * Possible fixes for zero-impression keywords:
 *   - Low QS / low bid: increase bid or improve landing page relevance
 *   - Too restrictive match type: loosen to broad or phrase match
 *   - Poor ad relevance: rewrite ads to match keyword intent
 *   - Overlapping negatives: check account and campaign-level negative lists
 *   - Insufficient search volume: keyword may not have enough searches
 *
 * Changelog:
 *   2026-03-23  Initial version — 14-day zero-impression check with QS and bid.
 */

// ─── CONFIG ──────────────────────────────────────────────────────────────────

var ALERT_EMAIL    = 'your@email.com';
var ACCOUNT_NAME   = 'Client Name';

var LOOKBACK_DAYS  = 14;           // days to check for zero impressions
var MAX_EMAIL_ROWS = 200;          // cap the email output to keep it readable

// ─── HELPERS ──────────────────────────────────────────────────────────────────

function dateString(daysAgo) {
  var d = new Date();
  d.setDate(d.getDate() - daysAgo);
  return Utilities.formatDate(d, AdsApp.currentAccount().getTimeZone(), 'yyyyMMdd');
}

// ─── MAIN ─────────────────────────────────────────────────────────────────────

function main() {
  var now       = new Date();
  var startDate = dateString(LOOKBACK_DAYS);
  var endDate   = dateString(1);

  // Pull all active keywords with their impression counts
  var query =
    'SELECT '
    + 'campaign.name, '
    + 'ad_group.name, '
    + 'ad_group_criterion.keyword.text, '
    + 'ad_group_criterion.keyword.match_type, '
    + 'ad_group_criterion.cpc_bid_micros, '
    + 'ad_group_criterion.quality_info.quality_score, '
    + 'ad_group_criterion.status, '
    + 'metrics.impressions '
    + 'FROM keyword_view '
    + 'WHERE segments.date BETWEEN \'' + startDate + '\' AND \'' + endDate + '\' '
    + 'AND ad_group_criterion.status = ENABLED '
    + 'AND ad_group.status = ENABLED '
    + 'AND campaign.status = ENABLED ';

  var rows     = AdsApp.search(query);
  var keyMap   = {};  // deduplicate across multiple days

  while (rows.hasNext()) {
    var row  = rows.next();
    var key  = row.campaign.name + '|||'
             + row.ad_group.name + '|||'
             + row.ad_group_criterion.keyword.text + '|||'
             + row.ad_group_criterion.keyword.match_type;

    if (!keyMap[key]) {
      keyMap[key] = {
        campaign:   row.campaign.name,
        adGroup:    row.ad_group.name,
        keyword:    row.ad_group_criterion.keyword.text,
        matchType:  row.ad_group_criterion.keyword.match_type,
        bidMicros:  parseInt(row.ad_group_criterion.cpc_bid_micros) || 0,
        qs:         parseInt(row.ad_group_criterion.quality_info.quality_score) || 0,
        impressions: 0,
      };
    }
    keyMap[key].impressions += parseInt(row.metrics.impressions) || 0;
  }

  // Filter to zero-impression keywords only
  var zeroKeys = Object.values(keyMap).filter(function(k) {
    return k.impressions === 0;
  });

  // Sort by campaign then ad group
  zeroKeys.sort(function(a, b) {
    return a.campaign.localeCompare(b.campaign) || a.adGroup.localeCompare(b.adGroup);
  });

  Logger.log('Zero Impression Keywords — ' + now.toDateString());
  Logger.log('Lookback: ' + startDate + ' to ' + endDate + ' (' + LOOKBACK_DAYS + ' days)');
  Logger.log('Zero-impression active keywords: ' + zeroKeys.length);

  if (zeroKeys.length === 0) {
    Logger.log('No zero-impression keywords found. All active keywords received traffic.');
    return;
  }

  // Log to script output
  zeroKeys.slice(0, 50).forEach(function(k) {
    Logger.log(k.campaign + ' | ' + k.adGroup + ' | [' + k.matchType + '] '
               + k.keyword + ' | QS: ' + (k.qs || 'n/a')
               + ' | Bid: $' + (k.bidMicros / 1000000).toFixed(2));
  });

  // Build email
  var body = 'ZERO IMPRESSION KEYWORDS REPORT\n';
  body    += ACCOUNT_NAME + ' — ' + now.toDateString() + '\n';
  body    += 'Lookback: last ' + LOOKBACK_DAYS + ' days\n';
  body    += '====================================\n\n';
  body    += 'Total zero-impression active keywords: ' + zeroKeys.length + '\n\n';

  if (zeroKeys.length > MAX_EMAIL_ROWS) {
    body += '(Showing first ' + MAX_EMAIL_ROWS + ' of ' + zeroKeys.length + ')\n\n';
  }

  body += 'Campaign | Ad Group | Match | Keyword | QS | Bid\n';
  body += '------------------------------------------------------\n';

  var shown = zeroKeys.slice(0, MAX_EMAIL_ROWS);
  shown.forEach(function(k) {
    var bid = k.bidMicros > 0 ? '$' + (k.bidMicros / 1000000).toFixed(2) : 'auto';
    body += k.campaign + ' | ' + k.adGroup + ' | ' + k.matchType
            + ' | ' + k.keyword + ' | ' + (k.qs || '?') + ' | ' + bid + '\n';
  });

  body += '\n====================================\n';
  body += 'Recommended actions:\n';
  body += '  QS 1-4:  Improve ad relevance and landing page. Consider pausing.\n';
  body += '  QS 5-6:  Increase bid or improve ad copy alignment.\n';
  body += '  QS 7+:   Keyword may lack search volume — check Keyword Planner.\n';
  body += '  No QS:   New keyword or insufficient data — wait 30 days before acting.\n';

  var subject = '[' + ACCOUNT_NAME + '] Zero Impression Keywords — '
                + zeroKeys.length + ' keyword(s) — ' + now.toDateString();

  MailApp.sendEmail(ALERT_EMAIL, subject, body);
  Logger.log('Report sent to: ' + ALERT_EMAIL);
}
