# TSWC Google Ads Conversion Tracking Fix Guide

**Date:** 2026-04-11
**Account:** Google Ads 155-039-0384
**Platform:** Shopify + Google & YouTube App

---

## Summary of Issues

| Issue | Severity | Impact |
|-------|----------|--------|
| Enhanced Conversions + Google tag both enabled | CRITICAL | Double-counting all conversions |
| Multiple events set as Primary | HIGH | Smart Bidding optimizing on noise |
| Google tag shows "Needs Attention" | MEDIUM | Tag may not be firing correctly |
| 5 tags flagged in Tag Assistant | MEDIUM | Potential broken/misconfigured tags |

---

## Step 1: Fix Enhanced Conversions Conflict (Shopify)

**Time:** 5 minutes
**Location:** Shopify Admin → Sales Channels → Google & YouTube → Settings

### Current State (Broken)
- Enhanced conversions for web: **ENABLED**
- Google tag setup for conversions: **ALSO ENABLED**
- Result: Every purchase fires twice

### Fix Steps

1. Open Shopify Admin
2. Go to **Sales Channels** → **Google & YouTube**
3. Click **Settings**
4. Scroll to **"Data sharing and tag management"**
5. Find **"Enhanced conversion measurement"** section
6. You should see:
   - ✅ Enhanced conversions for web — ENABLED (keep this)
   - ⚠️ Google tag setup — also enabled (this causes the conflict)

7. **Click "Manage" on the Google tag section**
8. **Disable conversion tracking via Google tag** (keep Enhanced Conversions enabled)
9. Save changes

### Expected Result
- Enhanced conversions: ENABLED
- Google tag for conversions: DISABLED
- Warning message should disappear

---

## Step 2: Set Correct Primary/Secondary Conversion Actions (Google Ads)

**Time:** 10 minutes
**Location:** Google Ads → Tools → Conversions

### Current State (Broken)
All these events may be set as Primary:
- Checkout completed
- Add to cart
- Begin checkout
- Contact
- Product view
- Product added to wishlist
- Search submitted

### Fix Steps

1. Log into Google Ads account **155-039-0384**
2. Click **Tools** (wrench icon) → **Conversions**
3. You'll see a list of all conversion actions

4. For **each conversion action**, click on it and check the **"Include in conversions"** setting:

| Conversion Action | Include in Conversions? | Setting |
|-------------------|------------------------|---------|
| Checkout completed / Purchase | YES | **Primary** |
| Add to cart | NO | **Secondary** |
| Begin checkout | NO | **Secondary** |
| Contact | NO | **Secondary** |
| Product view | NO | **Secondary** |
| Product added to wishlist | NO | **Secondary** |
| Search submitted | NO | **Secondary** |

5. To change a conversion action:
   - Click on the conversion action name
   - Click **Edit settings**
   - Under **"Include in 'Conversions'"**:
     - Select **Yes** for Purchase only
     - Select **No** for all others
   - Save

### Expected Result
- Only 1 conversion action shows "Primary" (Purchase/Checkout)
- All others show "Secondary"
- Smart Bidding will now optimize for purchases only

---

## Step 3: Reconnect Google Tag (Shopify)

**Time:** 5 minutes
**Location:** Shopify Admin → Google & YouTube → Settings

### Fix Steps

1. In Shopify Admin, go to **Sales Channels** → **Google & YouTube**
2. Click **Settings**
3. Find the **"Google tag"** section (should show "Needs Attention")
4. Click **Manage**
5. Click **Disconnect** (or Remove account)
6. Wait 5 seconds
7. Click **Connect** (or Link account)
8. Select the correct Google Ads account (**155-039-0384**)
9. Confirm **Auto-tagging** is enabled
10. Save changes

### Expected Result
- Google tag status changes from "Needs Attention" to "Active"
- Connected account shows correct Google Ads ID

---

## Step 4: Verify Conversion Measurement Settings (Shopify)

**Time:** 5 minutes
**Location:** Shopify Admin → Google & YouTube → Settings → Conversion measurement

### Fix Steps

1. In Shopify Google & YouTube app, go to **Settings**
2. Scroll to **"Conversion measurement settings"**
3. Click **Manage** (or view settings)
4. You should see a list of events being tracked:
   - Checkout completed
   - Add to cart
   - Begin checkout
   - Contact
   - Product view
   - etc.

5. For each event, check the **"Send to Google Ads"** setting:
   - **Checkout completed**: Send to Google Ads ✅
   - **All other events**: Either disable or leave as Secondary only

6. If there's an option to set events as Primary/Secondary directly in Shopify:
   - Set only Checkout completed as Primary
   - Set all others as Secondary or don't send to Google Ads

### Expected Result
- Only Purchase/Checkout events are sent as Primary conversions
- Other events are either not sent or marked as Secondary

---

## Step 5: Test with Tag Assistant

**Time:** 10 minutes
**Tool:** Google Tag Assistant Chrome Extension

### Test Steps

1. Install **Tag Assistant Companion** Chrome extension (if not already installed)
2. Open Chrome Incognito window
3. Navigate to TSWC Shopify store
4. Click **Tag Assistant** extension → **Record**
5. Browse the site and complete a **test purchase** (use a real product, you can refund yourself later)
6. After purchase completes, stop recording in Tag Assistant
7. Review the results

### What to Check

1. **Google Ads Conversion Tag** should fire exactly **once** on the thank-you page
2. **No duplicate conversion tags** should fire
3. **Enhanced Conversions** should show as active
4. **No error messages** in Tag Assistant

### Expected Result
- 1 purchase conversion fired
- No duplicate tags
- No warnings

---

## Step 6: Verify in Google Ads (24-48 Hours Later)

**Time:** 5 minutes (after 24-48 hours)
**Location:** Google Ads → Tools → Conversions

### Verification Steps

1. Log into Google Ads **155-039-0384**
2. Go to **Tools** → **Conversions**
3. Check the conversion table for the last 24-48 hours

### What to Check

| Metric | Expected |
|--------|----------|
| Purchase conversions | Should match Shopify order count (within 10%) |
| Add to cart conversions | Still tracked (if Secondary) but not inflating Purchase count |
| Conversion rate | Should be realistic (1-4% for eCommerce) |
| Smart Bidding campaigns | Show "Eligible" or "Active" status |

---

## Troubleshooting

### If conversions drop to zero after the fix:
- Enhanced Conversions may not be passing data correctly
- Check that the Google tag is still firing on the thank-you page
- Verify the Google Ads account ID is correct in Shopify settings

### If conversions are still double what Shopify shows:
- There may be another duplicate tag (GTM container + Shopify app)
- Check if there's a Google Tag Manager container also firing conversion tags
- If GTM exists, remove the conversion tracking from one source

### If Google tag still shows "Needs Attention":
- Wait 24 hours for Google to propagate the changes
- If still showing after 24 hours, disconnect and reconnect again
- Verify the Google Ads account has admin access

---

## Post-Fix Monitoring

**Week 1 after fix:**
- Check conversion volume daily
- Compare Google Ads conversions vs. Shopify orders
- Flag any discrepancy >20%

**Week 2-4:**
- Monitor Smart Bidding performance
- CPA may fluctuate as the algorithm learns with clean data
- Expect CPA to stabilize or improve after the initial learning period

---

## Checklist

- [ ] Step 1: Disabled duplicate Google tag setup in Shopify (Enhanced Conversions only)
- [ ] Step 2: Set only Purchase as Primary in Google Ads
- [ ] Step 3: Reconnected Google tag in Shopify
- [ ] Step 4: Verified conversion measurement settings
- [ ] Step 5: Tested with Tag Assistant (1 conversion fired)
- [ ] Step 6: Verified conversion volume matches Shopify orders (24-48 hours later)

---

## Notes

**Test order details:**
- Date of test: ___________
- Order number: ___________
- Tag Assistant result: ___________

**Post-fix conversion volume:**
- Date: ___________
- Shopify orders (24h): ___________
- Google Ads conversions (24h): ___________
- Discrepancy: ___________
