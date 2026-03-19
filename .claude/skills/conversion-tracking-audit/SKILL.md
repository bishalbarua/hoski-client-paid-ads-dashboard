---
name: conversion-tracking-audit
description: Audit Google Ads conversion tracking setup for a single client account. Pulls all conversion actions via API, checks tag health, detects double-counting and misconfigured primary/secondary designations, validates attribution windows, and flags any issues that would corrupt optimization data. Run this before any campaign builds, bid strategy changes, or performance analysis. Outputs a per-action health scorecard and prioritized fix list.
---

# Conversion Tracking Audit

Conversion tracking is the single most important foundation of Google Ads. If tracking is wrong, every bid strategy, performance report, and optimization decision is built on a lie. This skill systematically audits every conversion action in an account and surfaces issues before they corrupt optimization data or mislead clients.

Run this skill:
- Before onboarding a new client (especially inherited accounts)
- Before switching bid strategies (e.g., manual → tCPA)
- When conversion volume looks wrong (too high, too low, or suddenly changed)
- As a quarterly hygiene check on active accounts

## How This Skill Differs from Weekly Check

| | Conversion Tracking Audit | Weekly Check |
|---|---|---|
| **Scope** | Deep technical audit of all conversion actions | Operational health snapshot for the week |
| **Tracking check depth** | Full: tag status, double-counting, attribution, value, primary/secondary | Surface: is tracking recording? any 0-conversion anomalies? |
| **When to run** | Before major changes, new client onboarding, quarterly hygiene | Every Monday morning |
| **Output** | Per-action scorecard + root cause diagnosis + fix instructions | Status flag (✅/⚠️/🔴) + "check this" note |

---

## Core Philosophy

1. **Tracking is binary.** If it's broken, nothing else matters. Fix tracking before touching bids, budgets, or keywords.
2. **Over-counting is worse than under-counting.** Inflated conversions cause Smart Bidding to overspend. Under-counting is conservative. Over-counting is actively harmful.
3. **Primary vs. secondary is a bid strategy signal, not a label.** Anything marked "primary" feeds tCPA/tROAS targets. Misclassification breaks bid optimization.
4. **Double-counting is the most common silent killer.** A thank-you page view AND a form submit for the same lead = 2 conversions for 1 event. Extremely common in inherited accounts.
5. **"Active" does not mean "correct."** A tag can fire and still track the wrong thing (wrong page, wrong trigger, wrong value).

---

## Critical Context Gathering

### Required Context (Ask if not provided)

**1. Client Name or Account ID**
Which account to audit. If client name given, look up the ID in CLAUDE.md.
Example: "Anand Desai Law Firm" → ID 5865660247

**2. Business Model**
Lead gen or eCommerce? This determines:
- Whether conversion value tracking matters (eCommerce: yes, required; lead gen: optional)
- Expected conversion actions (form submit, call, purchase, etc.)
- What counts as a "primary" conversion

### Recommended Context

**3. What Conversions Should Exist**
What does this business actually want to track? Examples:
- Law firm: phone calls + contact form + chat
- eCommerce: purchase (with value)
- Healthcare: appointment booking + phone call

If the user doesn't know, I'll flag "expected vs. actual" as part of the audit output.

**4. Any Known Issues**
Has the client or account manager noticed anomalies?
- "Conversions doubled last month"
- "We see calls in the call log but 0 conversions in Google Ads"
- "Smart Bidding isn't working"

### Optional Context

**5. Tag Implementation Method**
- Google Tag Manager (most common)
- Direct gtag.js on site
- Third-party (Shopify, HubSpot, Squarespace pixel)
- Google Analytics import

Helps narrow down root cause faster when issues are found.

---

## Input Format

**API pull (preferred):** Just provide the client name or account ID. I'll run all queries automatically.

**Manual data paste:** If API access isn't available, paste the contents of:
- Google Ads UI → Tools → Conversions (export or screenshot)
- Any error messages from the Tag Assistant

**Minimum for manual audit:** Conversion action names, status (active/inactive), last 30-day conversion count, and whether each is set to "primary" or "secondary."

---

## API Queries

Run all queries against the target account ID.

### Query 1: Conversion Action Inventory

```python
from google.ads.googleads.client import GoogleAdsClient
import os

client = GoogleAdsClient.load_from_dict({
    "developer_token": os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"],
    "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
    "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
    "refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
    "login_customer_id": os.environ["GOOGLE_ADS_CUSTOMER_ID"],
    "use_proto_plus": True
})

ga_service = client.get_service("GoogleAdsService")
customer_id = "[ACCOUNT_ID]"

query = """
    SELECT
        conversion_action.id,
        conversion_action.name,
        conversion_action.status,
        conversion_action.category,
        conversion_action.type,
        conversion_action.counting_type,
        conversion_action.include_in_conversions_metric,
        conversion_action.value_settings.default_value,
        conversion_action.value_settings.always_use_default_value,
        conversion_action.attribution_model_settings.attribution_model,
        conversion_action.click_through_lookback_window_days,
        conversion_action.view_through_lookback_window_days,
        conversion_action.tag_snippets
    FROM conversion_action
    WHERE conversion_action.status != 'REMOVED'
    ORDER BY conversion_action.name
"""

response = ga_service.search(customer_id=customer_id, query=query)
for row in response:
    ca = row.conversion_action
    print(f"Name: {ca.name}")
    print(f"  Status: {ca.status.name}")
    print(f"  Category: {ca.category.name}")
    print(f"  Type: {ca.type_.name}")
    print(f"  Counting: {ca.counting_type.name}")
    print(f"  Include in conversions: {ca.include_in_conversions_metric}")
    print(f"  Default value: {ca.value_settings.default_value}")
    print(f"  Always use default value: {ca.value_settings.always_use_default_value}")
    print(f"  Click window: {ca.click_through_lookback_window_days} days")
    print(f"  View window: {ca.view_through_lookback_window_days} days")
    print()
```

### Query 2: Conversion Performance (Last 30 Days)

```python
query = """
    SELECT
        conversion_action.name,
        conversion_action.status,
        conversion_action.include_in_conversions_metric,
        metrics.conversions,
        metrics.conversions_value,
        metrics.all_conversions,
        metrics.view_through_conversions
    FROM conversion_action
    WHERE segments.date DURING LAST_30_DAYS
    AND conversion_action.status != 'REMOVED'
    ORDER BY metrics.conversions DESC
"""
```

### Query 3: Campaign-Level Conversion Breakdown

```python
query = """
    SELECT
        campaign.name,
        campaign.status,
        campaign.bidding_strategy_type,
        metrics.conversions,
        metrics.conversions_value,
        metrics.all_conversions,
        metrics.cost_micros,
        metrics.cost_per_conversion
    FROM campaign
    WHERE segments.date DURING LAST_30_DAYS
    AND campaign.status != 'REMOVED'
    ORDER BY metrics.cost_micros DESC
"""
```

### Query 4: Conversion Action Tag Status

```python
query = """
    SELECT
        conversion_action.name,
        conversion_action.status,
        conversion_action.category,
        conversion_action.tag_snippets
    FROM conversion_action
    WHERE conversion_action.status = 'ENABLED'
    AND conversion_action.type = 'WEBPAGE'
"""
```

---

## Analysis Framework

### Check 1: Primary vs. Secondary Designation

This is the most impactful check. Everything marked "primary" (include_in_conversions_metric = true) feeds Smart Bidding.

| Scenario | Issue | Severity |
|---|---|---|
| 0 primary conversion actions | Smart Bidding has no signal — cannot optimize | 🔴 Critical |
| Only micro-conversions are primary (page views, scroll depth) | Bidding optimizing for engagement, not business outcomes | 🔴 Critical |
| Both macro AND micro conversions are primary | Double-counting inflating conversion volume | 🔴 Critical |
| Multiple macro conversions all primary (form + call + chat) | Potentially fine if each is a unique lead — verify no overlap | 🟡 Review |
| Purchase is secondary instead of primary | eCommerce: ROAS bidding has no signal | 🔴 Critical |
| Everything is primary (includes informational events) | Over-counting, bid strategy chasing noise | 🔴 Critical |

**Rule:** For lead gen, exactly 1-3 primary actions representing unique, qualified leads. For eCommerce, Purchase (with value) must be primary.

---

### Check 2: Double-Counting Detection

Double-counting is when the same lead event fires 2+ conversion actions. Common patterns:

| Pattern | Example | Double Counting? |
|---|---|---|
| Form submit page + thank-you page view | Both tracking same form submission | ✅ Yes — remove one |
| GTM event + gtag.js direct tag | Same trigger, two implementations | ✅ Yes — remove one |
| GA4 import + native Google Ads tag | Importing GA4 AND firing a parallel native tag | ✅ Yes — remove one |
| Phone call from ads + call extension call | Different call sources (click-to-call vs. extension) | ❌ No — can be valid |
| Form submit + email notification | Different systems, same event trigger | ✅ Yes — remove one |
| Purchase + checkout complete page view | eCommerce: both fire on order confirmation | ✅ Yes — remove one |

**Detection logic:**
1. Look for conversion actions with identical or highly similar names
2. Check if `all_conversions` >> `conversions` — large gap suggests double-tracking
3. Compare conversion count vs. business's actual lead volume (ask client)
4. For any two actions that could represent the same event, flag for review

---

### Check 3: Conversion Category Audit

Google uses the category to understand what the conversion represents. Wrong category doesn't break tracking but misleads reports.

| Category | Should Be Used For | Red Flags |
|---|---|---|
| PURCHASE | Actual transactions with revenue | Used for lead gen "contact form" |
| LEAD | Form submissions, sign-ups | Used for "page view" events |
| SIGNUP | Account creation | Used for "add to cart" |
| PAGE_VIEW | Someone visited a page | Marked as primary — almost always wrong |
| ADD_TO_CART | Shopping cart add | Marked as primary without purchase also primary |
| DOWNLOAD | File downloads | Marked as primary for non-content sites |
| OTHER | Miscellaneous | Should investigate — likely misconfigured |

---

### Check 4: Counting Type

| Counting Type | Appropriate For | Issue If Wrong |
|---|---|---|
| ONE_PER_CLICK | Lead gen (1 lead = 1 conversion per click) | Set to MANY for forms = multiple conversions per single lead session |
| MANY_PER_CLICK | eCommerce purchases (1 user can buy twice) | Set to ONE for eCommerce = missed revenue tracking |

**Rule:** Lead gen = ONE_PER_CLICK. eCommerce purchase = MANY_PER_CLICK. Everything else = ONE_PER_CLICK unless there's a specific reason.

---

### Check 5: Attribution Window

| Business Type | Typical Sales Cycle | Recommended Click Window |
|---|---|---|
| Emergency services (plumber, locksmith) | Same day | 7-14 days |
| Healthcare appointment | 1-7 days | 30 days |
| Legal / high-consideration | Days to weeks | 60-90 days |
| eCommerce (impulse) | Same session to 3 days | 7-30 days |
| eCommerce (high-ticket) | Days to weeks | 30-60 days |
| B2B SaaS | Weeks to months | 90 days |

Flag any window that is shorter than the expected sales cycle. A 7-day window for a law firm means all clients who converted after 7 days show as 0 conversions — causing Smart Bidding to underbid on keywords that actually drove conversions.

---

### Check 6: Conversion Value Audit (eCommerce)

| Setting | What to Check |
|---|---|
| `always_use_default_value = true` | Is dynamic value being passed? If yes, this overrides it — revenue will be wrong |
| `default_value = 0` | No value tracking at all — ROAS bidding cannot function |
| `default_value` set to avg order value | Valid workaround if dynamic passing isn't possible, but must match reality |
| Value varies by product but `always_use_default_value = true` | All orders show same revenue — ROAS data is fiction |

---

### Check 7: Tag Status Signals

From Query 1 + 4 (`tag_snippets`), assess:

| Signal | Meaning |
|---|---|
| Status = ENABLED, 0 conversions in 30 days | Tag may not be firing — investigate |
| Status = ENABLED, conversions dropping sharply mid-month | Site change may have broken tag |
| Status = ENABLED, conversion spike mid-month | Possible tag duplication introduced |
| Type = WEBPAGE, 0 conversions but site has traffic | Tag is enabled but not firing — likely broken |
| Type = PHONE_CALL, 0 conversions | Check if call extension is active on campaigns |
| Type = ANALYTICS (GA import), 0 conversions | GA4 property linked? Import rule configured? |

---

### Check 8: Account-Level Settings

These aren't conversion actions but affect tracking integrity:

| Setting | Location | Issue If Wrong |
|---|---|---|
| Auto-tagging | Account Settings → Auto-tagging | If disabled, GCLID not passed, no conversion attribution |
| Cross-device conversions | Measurement → Attribution | Should be on for most accounts |
| Attribution model | Per conversion action | Data-driven preferred; last-click understates top-of-funnel |
| Conversion window consistency | All primary actions | Should match sales cycle, not vary randomly per action |

---

## Scoring Framework

Score each conversion action individually, then produce an overall account score.

### Per-Action Score

| Check | Pass | Flag | Fail |
|---|---|---|---|
| Primary/Secondary designation | Correct for business model | Unclear — needs review | Wrong designation |
| Counting type | Correct for conversion type | | Wrong type |
| Attribution window | Matches sales cycle | Slightly short | Much too short |
| Category | Correct | Minor mismatch | Wrong (page view as primary) |
| Value (eCommerce only) | Dynamic value passing | Default value workaround | No value / always default |
| 30-day volume | Non-zero, plausible | Suspiciously low | Zero conversions |
| Double-counting | No overlap detected | Possible overlap | Clear duplication |

**Status labels:**
- ✅ Healthy — no action needed
- ⚠️ Review — minor concern, investigate but not urgent
- 🔴 Fix Now — actively corrupting data or bid optimization

### Overall Account Tracking Health

| Score | Label | Meaning |
|---|---|---|
| All primary actions ✅ | 🟢 Tracking Healthy | Safe to optimize, run reports, trust data |
| 1+ primary action ⚠️ | 🟡 Tracking Questionable | Review before making bid strategy changes |
| Any primary action 🔴 | 🔴 Tracking Broken | Fix before ANY optimization work |

---

## Output Format

```
# Conversion Tracking Audit — [Client Name]
**Account ID:** [ID]
**Audit Date:** [Date]
**Overall Status:** 🟢 Healthy / 🟡 Questionable / 🔴 Broken

---

## Overall Summary

[2-3 sentence plain-English verdict. E.g.: "Tracking is fundamentally broken — the account is counting both a form submit and thank-you page view as separate conversions, inflating lead counts by ~2x. Smart Bidding is optimizing on noise. Fix the double-counting before changing any bids or budgets."]

---

## Conversion Action Scorecard

| Action Name | Category | Primary? | Count (30d) | Counting Type | Window | Double-Count Risk | Status |
|---|---|---|---|---|---|---|---|
| [Name] | LEAD | ✅ Yes | 47 | ONE_PER_CLICK | 30 days | None detected | ✅ Healthy |
| [Name] | PAGE_VIEW | ⚠️ Yes — wrong | 89 | ONE_PER_CLICK | 30 days | Overlaps with form submit | 🔴 Fix Now |
| [Name] | LEAD | ✅ Yes | 12 | ONE_PER_CLICK | 7 days (too short) | None | ⚠️ Review |

---

## Critical Issues (Fix Before Any Optimization)

### Issue 1: [Issue Name]
**What's happening:** [Description]
**Why it matters:** [Impact on bids/reports]
**How to fix:** [Step-by-step instructions]
**Confidence:** 0.95

### Issue 2: [Issue Name]
[Same structure]

---

## Warnings (Review This Month)

### Warning 1: [Warning Name]
**What's happening:** [Description]
**Why it matters:** [Potential impact]
**Recommended action:** [What to do]

---

## What's Healthy

- [Conversion action]: ✅ [Why it's fine]
- [Account setting]: ✅ [Why it's fine]

---

## Implementation Checklist

**Fix Now (before next campaign change):**
- [ ] [Action 1 with exact location: Tools → Conversions → [Action Name] → Edit]
- [ ] [Action 2]

**Fix This Month:**
- [ ] [Action 3]

**Verify After Fixing:**
- [ ] Use Google Tag Assistant to confirm tags firing correctly
- [ ] Check 7-day conversion volume matches expected business volume
- [ ] Confirm Smart Bidding campaigns show "Learning" → "Eligible" (may take 1-2 weeks)
```

---

## Guardrails

❌ **NEVER** delete a conversion action without first confirming it isn't the only action recording data for a campaign using Smart Bidding — removing it drops the campaign into "no conversions" learning mode.

❌ **NEVER** recommend switching from one primary action to another mid-flight without flagging that bid strategies will enter a learning period — this is a significant account disruption.

❌ **NEVER** mark all conversion issues as 🔴 if some are only minor or stylistic mismatches. False alarms erode trust in the audit output.

❌ **NEVER** diagnose "tag not firing" based solely on 0 conversions — low-traffic accounts legitimately have periods of 0 conversions. Cross-reference with site traffic volume.

✅ **ALWAYS** read `clients/[client]/notes/client-info.md` first for business type, expected conversion actions, and any known tracking notes before pulling API data.

✅ **ALWAYS** distinguish between "this action is wrong" and "this action is missing" — both are issues but require different fixes.

✅ **ALWAYS** flag auto-tagging status — it's the most commonly overlooked account-level issue.

✅ **ALWAYS** produce a concrete implementation checklist, not just a diagnosis. The audit is only useful if the person knows what to actually do next.

---

## Edge Cases

### New Account With Zero Conversions
If an account has never tracked conversions (all actions show 0, account is <30 days old):
- Skip volume-based checks (0 conversions is expected, not a bug)
- Focus audit on: tag setup correctness, primary/secondary designation, counting type, attribution window
- Flag as "Setup Review" rather than "Tracking Broken"

### Imported GA4 Conversions
GA4 imports are common and frequently misconfigured:
- Check if the GA4 property is still linked (link breaks silently when GA4 property is recreated)
- Check if GA4 events imported are the right ones (easy to import "session_start" instead of "generate_lead")
- Verify the imported action's volume matches what GA4 itself reports for the same event

### Google Ads Calls vs. Website Call Tracking
Two separate systems often both active:
- Google Ads call extension reporting (tracks calls from the call extension phone number)
- Website call tracking (tracks calls from a dynamically swapped number on the site, powered by GCLID)
- Both can be enabled simultaneously without double-counting IF they track different call paths
- Double-counting occurs when the same call is recorded by both

### Smart Bidding Already Deployed on Broken Tracking
When campaigns are live with broken tracking and Smart Bidding:
- Don't immediately remove broken conversion actions — bid strategy loses all signal and campaigns enter deep learning
- Recommended approach: fix tag first, verify for 7-14 days, THEN remove the broken action
- Flag this in the output with a specific sequencing recommendation

### eCommerce With No Value Tracking
If purchase is tracked but `default_value = 0` and `always_use_default_value = true`:
- ROAS bidding is completely non-functional
- Recommend either: (a) implement dynamic value passing, or (b) set a realistic average order value as the default and use tCPA instead of tROAS until dynamic values are in place

---

## Quality Assurance

Before delivering the audit:
- [ ] Every conversion action has a status (✅/⚠️/🔴)
- [ ] Overall account status matches the worst individual status
- [ ] Every 🔴 issue has step-by-step fix instructions with exact UI location
- [ ] Double-counting check explicitly performed (not skipped)
- [ ] Primary/secondary designation verified against business model
- [ ] Attribution windows evaluated against sales cycle
- [ ] Auto-tagging status confirmed
- [ ] Implementation checklist is copy-paste actionable
- [ ] Output distinguishes "Fix Now" from "Review" — not everything is urgent
