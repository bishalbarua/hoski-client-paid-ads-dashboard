/**
 * RSA Ad Strength Audit
 * Purpose: Audits all enabled Responsive Search Ads. Flags ads below "GOOD"
 *          ad strength, identifies structural issues (too few headlines,
 *          over-pinning, missing diverse copy), and emails a prioritised fix
 *          list.
 *
 * Setup:
 *   1. Copy into Google Ads UI: Tools > Scripts > + New Script
 *   2. Set ALERT_EMAIL and ACCOUNT_NAME below
 *   3. Schedule: Weekly (Monday at 8am recommended)
 *   4. Authorise when prompted
 *
 * Ad Strength values (Google's scale):
 *   EXCELLENT | GOOD | AVERAGE | POOR | PENDING (not enough data yet)
 *
 * Common fixes:
 *   - Add more unique headlines (target 15)
 *   - Unpin headlines and descriptions to allow more combinations
 *   - Include primary keywords in at least 1-2 headlines
 *   - Vary message types: features, benefits, CTAs, social proof
 *   - Add unique descriptions (target 4, all different)
 *
 * Changelog:
 *   2026-03-23  Initial version — ad strength audit with pinning detection
 *               and headline count check.
 */

// ─── CONFIG ──────────────────────────────────────────────────────────────────

var ALERT_EMAIL        = 'your@email.com';
var ACCOUNT_NAME       = 'Client Name';

// Only flag RSAs below this strength level
// Options: 'EXCELLENT', 'GOOD', 'AVERAGE', 'POOR'
var MINIMUM_STRENGTH   = 'GOOD';

var MAX_EMAIL_ADS      = 50;   // cap email output

// ─── HELPERS ──────────────────────────────────────────────────────────────────

var STRENGTH_RANK = { 'EXCELLENT': 4, 'GOOD': 3, 'AVERAGE': 2, 'POOR': 1, 'PENDING': 0, 'UNSPECIFIED': 0 };

function strengthBelowMinimum(strength) {
  return (STRENGTH_RANK[strength] || 0) < (STRENGTH_RANK[MINIMUM_STRENGTH] || 3);
}

function countPinnedAssets(assets) {
  // An asset is pinned if it has a pinnedField set
  var pinned = 0;
  assets.forEach(function(asset) {
    if (asset.pinnedField && asset.pinnedField !== 'UNSPECIFIED') {
      pinned++;
    }
  });
  return pinned;
}

// ─── MAIN ─────────────────────────────────────────────────────────────────────

function main() {
  var now = new Date();

  var query =
    'SELECT '
    + 'campaign.name, '
    + 'ad_group.name, '
    + 'ad_group_ad.ad.id, '
    + 'ad_group_ad.ad.responsive_search_ad.headlines, '
    + 'ad_group_ad.ad.responsive_search_ad.descriptions, '
    + 'ad_group_ad.ad_strength, '
    + 'ad_group_ad.status, '
    + 'metrics.impressions, '
    + 'metrics.clicks, '
    + 'metrics.conversions '
    + 'FROM ad_group_ad '
    + 'WHERE ad_group_ad.status = ENABLED '
    + 'AND ad_group.status = ENABLED '
    + 'AND campaign.status = ENABLED '
    + 'AND ad_group_ad.ad.type = RESPONSIVE_SEARCH_AD '
    + 'AND segments.date DURING LAST_30_DAYS ';

  var rows   = AdsApp.search(query);
  var adMap  = {};

  while (rows.hasNext()) {
    var row = rows.next();
    var id  = row.ad_group_ad.ad.id;

    if (!adMap[id]) {
      var rsa       = row.ad_group_ad.ad.responsive_search_ad;
      var headlines = rsa ? (rsa.headlines || []) : [];
      var descs     = rsa ? (rsa.descriptions || []) : [];

      adMap[id] = {
        campaign:     row.campaign.name,
        adGroup:      row.ad_group.name,
        adId:         id,
        strength:     row.ad_group_ad.ad_strength || 'UNSPECIFIED',
        numHeadlines: headlines.length,
        numDescs:     descs.length,
        pinnedCount:  countPinnedAssets(headlines.concat(descs)),
        impressions:  0,
        clicks:       0,
        conv:         0,
      };
    }
    adMap[id].impressions += parseInt(row.metrics.impressions) || 0;
    adMap[id].clicks      += parseInt(row.metrics.clicks) || 0;
    adMap[id].conv        += parseFloat(row.metrics.conversions) || 0;
  }

  // Filter to ads below minimum strength
  var flagged = Object.values(adMap).filter(function(ad) {
    return strengthBelowMinimum(ad.strength);
  });

  // Sort by strength (worst first), then by spend
  flagged.sort(function(a, b) {
    return (STRENGTH_RANK[a.strength] || 0) - (STRENGTH_RANK[b.strength] || 0)
        || b.impressions - a.impressions;
  });

  var totalAds = Object.keys(adMap).length;

  Logger.log('RSA Ad Strength Audit — ' + now.toDateString());
  Logger.log('Total active RSAs: ' + totalAds);
  Logger.log('Below ' + MINIMUM_STRENGTH + ': ' + flagged.length);

  if (flagged.length === 0) {
    Logger.log('All RSAs are at ' + MINIMUM_STRENGTH + ' strength or above.');
    return;
  }

  var poor    = flagged.filter(function(a) { return a.strength === 'POOR'; });
  var average = flagged.filter(function(a) { return a.strength === 'AVERAGE'; });
  var pending = flagged.filter(function(a) { return a.strength === 'PENDING' || a.strength === 'UNSPECIFIED'; });

  var body = 'RSA AD STRENGTH AUDIT\n';
  body    += ACCOUNT_NAME + ' — ' + now.toDateString() + '\n';
  body    += 'Total RSAs: ' + totalAds + ' | Below ' + MINIMUM_STRENGTH + ': ' + flagged.length + '\n';
  body    += '====================================\n\n';

  if (poor.length > 0) {
    body += 'POOR STRENGTH (' + poor.length + ') — Fix these first\n';
    poor.slice(0, MAX_EMAIL_ADS).forEach(function(ad) {
      body += '  [' + ad.campaign + '] / [' + ad.adGroup + ']\n';
      body += '  Strength: ' + ad.strength + ' | Headlines: ' + ad.numHeadlines
              + '/15 | Descs: ' + ad.numDescs + '/4 | Pinned: ' + ad.pinnedCount + '\n';
      var fixes = [];
      if (ad.numHeadlines < 10)  fixes.push('Add ' + (15 - ad.numHeadlines) + ' more headlines');
      if (ad.numDescs < 3)       fixes.push('Add ' + (4 - ad.numDescs) + ' more descriptions');
      if (ad.pinnedCount > 4)    fixes.push('Reduce pinning (currently ' + ad.pinnedCount + ' pinned)');
      if (fixes.length > 0)      body += '  Fix: ' + fixes.join(', ') + '\n';
      body += '\n';
    });
  }

  if (average.length > 0) {
    body += 'AVERAGE STRENGTH (' + average.length + ')\n';
    average.slice(0, MAX_EMAIL_ADS).forEach(function(ad) {
      body += '  [' + ad.campaign + '] / [' + ad.adGroup + ']';
      body += ' | ' + ad.numHeadlines + ' headlines | ' + ad.numDescs + ' descs'
              + ' | ' + ad.pinnedCount + ' pinned\n';
    });
    body += '\n';
  }

  body += '====================================\n';
  body += 'Quick fixes:\n';
  body += '  1. Add headlines to reach 15 total (vary: features, CTAs, social proof, offers)\n';
  body += '  2. Add 4 unique descriptions\n';
  body += '  3. Unpin assets unless legally required to pin\n';
  body += '  4. Include primary keyword in 1-2 headlines\n';

  var subject = '[' + ACCOUNT_NAME + '] RSA Strength Alert — '
                + poor.length + ' POOR, ' + average.length + ' AVERAGE — ' + now.toDateString();

  MailApp.sendEmail(ALERT_EMAIL, subject, body);
  Logger.log('Report sent to: ' + ALERT_EMAIL);

  flagged.forEach(function(ad) {
    Logger.log('[' + ad.strength + '] ' + ad.campaign + ' / ' + ad.adGroup
               + ' (' + ad.numHeadlines + ' headlines, ' + ad.pinnedCount + ' pinned)');
  });
}
