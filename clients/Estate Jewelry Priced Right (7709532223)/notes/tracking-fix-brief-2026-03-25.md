# EJPR: Conversion Tracking Fix — Project Brief
**Account:** Estate Jewelry Priced Right (ID: 7709532223)
**Date:** 2026-03-25
**Priority:** Critical — account is spending ~$200/day with no purchase conversion data

---

## Background

A full conversion tracking audit was conducted on 2026-03-25 as part of fixing the "Eligible (Limited) — Not targeting relevant searches" issue on the Search campaign. The audit revealed that the account has **no working website purchase conversion action**. Smart Bidding has been optimizing toward add-to-cart, form fills, phone calls, and appointments — not purchases. This is the primary driver of the 0.22x blended ROAS.

---

## Issues Found

### Issue 1: No Website Purchase Conversion Action (Critical)
**What:** There is no Google Ads conversion action tracking actual website purchases. The only "Purchases" conversion action in the account is "Google Shopping App Purchase" which tracks app-based purchases, not Shopify website purchases.
**Impact:** Every campaign in the account has 0 purchase conversions recorded. Smart Bidding has no purchase signal to optimize toward.
**Fix:** Import the GA4 `purchase` event into Google Ads conversions as a Primary action (GA4 is confirmed linked to the account).

---

### Issue 2: Shopify Checkout Pages Not Tagged (Critical)
**What:** The Google tag is not firing on Shopify checkout pages. Two checkout URLs are confirmed untagged:
- `estatejewelrypricedright.com/checkouts/cn/hWN9DYCJqe9xF9B1XADm6AZl/en-us`
- `estatejewelrypricedright.com/checkouts/cn/hWN9FlzVPm7mQoloHdFUzseX/en-us`

**Impact:** Even if a purchase conversion action exists, it cannot fire because the tag disappears when a user enters the Shopify checkout flow. Purchases are invisible to Google Ads.
**Fix:** Add Google tag to Shopify checkout via one of:
- Shopify Admin > Settings > Checkout > Additional scripts (paste Google tag)
- Shopify Admin > Online Store > Preferences > connect Google Ads account and enable purchase tracking
- Google & YouTube Sales Channel app in Shopify (recommended for Shopify stores)

---

### Issue 3: Cross-Domain Tracking Not Configured (Critical)
**What:** Google tag is not configured for cross-domain measurement between `estatejewelrypricedright.com` and `c26ba4-04.myshopify.com`. The tag drops when users navigate between these two domains during the checkout flow.
**Impact:** Session continuity breaks at checkout. Conversions attributed to ads are lost even when they do occur.
**Fix:** In Google Ads > Tools > Data Manager > Google Tag > Manage > Configure your domains — accept both suggested domains:
- `c26ba4-04.myshopify.com`
- `estatejewelrypricedright.com`

**Status:** Flagged in Tag Diagnostics. One-click fix available in the UI.

---

### Issue 4: Wrong Primary Conversion Actions (High)
**What:** ~8 conversion actions are set to Primary, meaning Smart Bidding treats all of them equally. The current Primary actions include:
- Form Submission (Calendar Page)
- GTM_Appointment
- Calls from ads
- Calls from Website
- Store visits
- Clicks to call
- Get Directions
- Google Shopping App Purchase

**Impact:** Smart Bidding cannot distinguish a $200 purchase from a $0 map direction click. Budget is being allocated toward micro-actions with no revenue value.
**Fix:** Set all of the above to Secondary. Only keep as Primary:
- GA4 `purchase` event (once imported)
- Offline Purchase (Zapier) — only if it is actively recording real sales

---

### Issue 5: Shopify Data Source Not Pulling Data (Medium)
**What:** Shopify: Estate Jewelry Priced Right is connected in Data Manager but shows "You have not selected any data from this account."
**Impact:** Shopify-native purchase signal is not being used to enrich conversion data.
**Fix:** In Data Manager > Shopify > click "+ Add" and select purchase/order data to pull in. This can serve as a secondary purchase signal alongside GA4.

---

### Issue 6: Collection Pages Not Tagged (Medium)
**What:** Three high-traffic collection pages are confirmed untagged (the Google tag is not detected):
- `estatejewelrypricedright.com/collections/rings/`
- `estatejewelrypricedright.com/collections/bracelets/`
- `estatejewelrypricedright.com/collections/bangle-cuff-bracelets/`

**Impact:** Ad clicks landing on these pages are not being measured. Remarketing audiences from these pages may be incomplete.
**Fix:** Likely a Shopify theme issue. Check that the Google tag is present in the Shopify theme's `theme.liquid` file (should be in the `<head>`). If the tag is in the theme but these pages still show untagged, investigate if a custom template is being used for these collections that doesn't inherit the global tag.

---

### Issue 7: Offline Purchase (Zapier) Inactive (Low)
**What:** The "Offline Purchase (Zapier)" conversion action is set to Secondary but shows as Inactive.
**Impact:** If this was intended to track offline or CRM-confirmed purchases, that data is not flowing.
**Fix:** Investigate whether the Zapier automation is still active. If not in use, set to removed/hidden to keep the conversions view clean.

---

## Fix Priority Order

| # | Task | Owner | Priority | Effort |
|---|---|---|---|---|
| 1 | Accept cross-domain suggestions (c26ba4-04.myshopify.com + estatejewelrypricedright.com) in Google Tag settings | Media buyer | Critical | 2 min |
| 2 | Add Google tag to Shopify checkout (Additional scripts or Google channel app) | Dev / Shopify admin | Critical | 30 min |
| 3 | Import GA4 `purchase` event into Google Ads as Primary conversion action | Media buyer | Critical | 5 min |
| 4 | Set all non-purchase conversion actions to Secondary | Media buyer | High | 10 min |
| 5 | Pull Shopify purchase data via Data Manager > Shopify > Add | Media buyer | Medium | 5 min |
| 6 | Investigate untagged collection pages (rings, bracelets) in Shopify theme | Dev | Medium | 1 hr |
| 7 | Investigate and clean up Zapier offline conversion action | Media buyer | Low | 10 min |

---

## Expected Outcome

Once fixes 1-4 are complete, Google Ads will have a real purchase conversion signal for the first time. Smart Bidding will begin learning actual purchase behavior within 7-14 days. A minimum of 30 purchase conversions is needed before switching to Target ROAS bidding. Until that threshold is reached, campaigns should run on Maximize Conversions (not Maximize Conversion Value) to accumulate data.

---

## Related Work

- Search campaign keyword rebuild completed 2026-03-25 (76 new keywords, 8 ad groups, 8 RSAs)
- Files: `data/ejpr-ad-group-rebuild-keywords-2026-03-25.csv`, `data/ejpr-ad-group-rebuild-rsa-2026-03-25.csv`
