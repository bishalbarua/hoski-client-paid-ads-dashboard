# GTM Tracking Plan — Park Road Landing Pages
**Container:** GTM-K3M5DHR3 (go.parkroadfurniture.com)
**Proposed workspace:** workspace6
**Prepared:** 2026-04-02

---

## Design Principle

Two conversion actions, two tags, two triggers. Google Ads attributes conversions to the correct campaign automatically via GCLID — no need to split tags by campaign. Any future landing page on `go.parkroadfurniture.com` that follows the `/thank-you` and `/consultation-booked` URL convention will be tracked automatically with zero new GTM work.

---

## What Was Wrong With the Old Config (workspace5)

| Issue | Detail |
|---|---|
| Triggers too broad or wrong | Triggers 5/8/9/10 all matched "thank-you" in different ways and fired the same single conversion tag — no campaign attribution possible and multiple triggers created duplicate fire risk. |
| Calendar trigger was wrong | Trigger 11 matched a GHL embed hash (`hcwbxW8u9P12eduR9EFo`). The new landing pages redirect to `/consultation-booked` instead. |
| No Meta Pixel | Pixel 1800838594156042 was not installed on this container. |
| No GA4 | No visibility into landing page behaviour in GA4. |

---

## New Config Summary (workspace6)

### Tags (8 total)

| Tag ID | Tag Name | Type | Fires On |
|---|---|---|---|
| 4 | Google Tag | googtag (AW-16808971588) | All Pages (init) |
| 7 | Google Ads - Conversion Linker | gclidw | All Pages (DOM ready) |
| 8 | GA4 - Landing Page Config | googtag (G-8JPPTDQDKK) | All Pages (init) |
| 9 | Meta Pixel - Base Code | Custom HTML | All Pages (init) |
| 10 | Google Ads - Form Submission | awct | Any `/thank-you` page |
| 11 | Google Ads - Consultation Booked | awct | Any `/consultation-booked` page |
| 12 | Meta Pixel - Lead (Form Submission) | Custom HTML | Any `/thank-you` page |
| 13 | Meta Pixel - Lead (Consultation Booked) | Custom HTML | Any `/consultation-booked` page |

**Removed from old config:** Tags 6, 12 (old broad appointment tags) and old triggers 5, 8, 9, 10, 11.

### Triggers (2 total)

| Trigger ID | Name | Match Rule |
|---|---|---|
| 10 | All - Form Submission | Page Path CONTAINS `/thank-you` |
| 11 | All - Consultation Booked | Page Path CONTAINS `/consultation-booked` |

Triggers use `{{Page Path}}` so they match cleanly regardless of UTM parameters or query strings.

---

## Step-by-Step Implementation

### Step 1 — Create 2 Conversion Actions in Google Ads

In Google Ads account 7228467515, go to Goals > Conversions > New conversion action > Website.

| Conversion Name | URL Match Rule | Category | Designation | Value | Count |
|---|---|---|---|---|---|
| Form Submission | Page URL contains `/thank-you` | Submit lead form | Primary | Not set | One |
| Consultation Booked | Page URL contains `/consultation-booked` | Book appointment | Secondary | Not set | One |

Attribution: 30-day click, 1-day view-through.

After creating each, copy the conversion label from the tag snippet (looks like `AbCdEfGhIjKlMnOp`).

### Step 2 — Fill In Conversion Labels in the Proposed JSON

Open `GTM-K3M5DHR3_workspace6_proposed.json` and replace two placeholders:

| Placeholder | Replace With | Tag |
|---|---|---|
| `REPLACE_FORM_LABEL` | Label from "Form Submission" conversion action | Tag 10 |
| `REPLACE_CONSULT_LABEL` | Label from "Consultation Booked" conversion action | Tag 11 |

Conversion ID stays as `16808971588` for both — do not change.

### Step 3 — Import Into GTM

1. Go to GTM-K3M5DHR3 workspace
2. Admin > Import Container
3. Select `GTM-K3M5DHR3_workspace6_proposed.json`
4. Workspace: existing or create new named "workspace6"
5. Import option: **Overwrite** (not Merge — replaces old tags/triggers cleanly)
6. Review the diff — confirm old tags 6, 12 and old triggers 5, 8, 9, 10, 11 are removed, new tags 8-13 are added
7. Confirm import

### Step 4 — Preview and Test Before Publishing

Use GTM Preview mode:

| Test URL | Expected Tags to Fire |
|---|---|
| `/custom-furniture` | Google Tag, Conversion Linker, GA4, Meta Pixel Base only |
| `/custom-furniture/thank-you` | + Google Ads Form Submission (tag 10), Meta Pixel Lead Form (tag 12) |
| `/custom-furniture/consultation-booked` | + Google Ads Consultation Booked (tag 11), Meta Pixel Lead Consult (tag 13) |
| `/cottage-furniture/thank-you` | + Google Ads Form Submission (tag 10), Meta Pixel Lead Form (tag 12) |
| `/cottage-furniture/consultation-booked` | + Google Ads Consultation Booked (tag 11), Meta Pixel Lead Consult (tag 13) |

Also verify in Google Ads: Goals > Conversions > Diagnostics. Use Meta Pixel Helper to confirm PageView on all pages and Lead on thank-you pages.

### Step 5 — Publish

Once verified in preview:
- Submit workspace
- Version name: "workspace6 — universal form + consultation tracking, Meta Pixel, GA4"

---

## Conversion Funnel (Both Campaigns)

```
/custom-furniture  OR  /cottage-furniture
        |
        | form fill + redirect
        v
  /*/thank-you  -->  Form Submission fires (primary — Google Ads + Meta Lead)
        |
        | user books consultation via calendar on TY1
        v
  /*/consultation (calendar page — no conversion tag)
        |
        | booking confirmed + redirect
        v
  /*/consultation-booked  -->  Consultation Booked fires (secondary — Google Ads + Meta Lead)
```

Campaign attribution happens automatically via GCLID. Google Ads knows which campaign drove the click and assigns the conversion correctly even though both campaigns share the same tags.

---

## Adding Future Landing Pages

If a new campaign (e.g., `/bedroom-furniture`) is added with the same URL structure:
- `/bedroom-furniture/thank-you` fires Form Submission automatically
- `/bedroom-furniture/consultation-booked` fires Consultation Booked automatically
- No new GTM tags, triggers, or conversion actions needed

---

## Key IDs Reference

| Property | ID |
|---|---|
| GTM Container (landing page) | GTM-K3M5DHR3 |
| GTM Container (main site) | GTM-T4KKTMXN |
| Google Ads Conversion ID | 16808971588 |
| Google Ads Tag ID | AW-16808971588 |
| GA4 Measurement ID | G-8JPPTDQDKK |
| Meta Pixel ID | 1800838594156042 |

---

## Open Question Before Publishing

Confirm with Paulo that the GHL calendar on `/*/consultation` redirects to `/consultation-booked` after a booking is confirmed. If GHL fires a virtual page within the embed instead of redirecting, the Consultation Booked trigger won't fire and the old embed hash approach needs to be added as a fallback trigger.
