# FaBesthetics — Meta Instant Form Copy
**Client:** FaBesthetics Face & Body Med Spa
**Offer:** 15% off when booking 4 or more laser sessions
**Prepared by:** Creative Strategist
**Date:** 2026-04-06

> This document is a field-by-field build reference. Every line below maps to an exact field in Meta's Instant Form builder. Copy-paste directly — no interpretation needed.

---

## HOW TO CREATE A FORM IN META

Meta Ads Manager → **Ads** tab → Create or edit an ad → Under "Destination," select **Instant Form** → Click **Create Form**

Or: Go to **Ads Manager → All Tools → Instant Forms** to build forms in the Forms Library before attaching them to ads.

---

## FORM INDEX

| Form | Used With | Form Type | File Name |
|---|---|---|---|
| [Form 1: Prospecting](#form-1-prospecting) | Ad 1 (problem-first static), Ad 2 (social proof carousel), Ad 3 (Becky video) | Higher Intent | `FAB_LHR_15off_Prospecting_Apr2026` |
| [Form 2: Retargeting](#form-2-retargeting) | Ad 4 (offer reminder static) | More Volume | `FAB_LHR_15off_Retargeting_Apr2026` |

**Why two different form types:**
- **Higher Intent** adds a review screen before submission. Users see their answers and must confirm before sending. Reduces volume by ~15-20% but meaningfully filters out accidental taps — critical for Becky's lead quality.
- **More Volume** removes the review step for a faster path to submission. Retargeting audiences already know FaBesthetics — they don't need extra convincing and the review step just adds friction.

---

## FORM 1: PROSPECTING

### Meta Builder Settings

| Setting | Value |
|---|---|
| **Form name** | `FAB_LHR_15off_Prospecting_Apr2026` |
| **Form type** | Higher Intent |
| **Language** | English (US) |
| **Sharing** | Restricted (only use with this ad account) |

---

### SECTION 1 — Intro

**Image**
Use the same image as the ad this form is attached to. If attaching to Ad 2 (carousel), use Card 1's image.

---

**Headline**
```
Save 15% on Your Laser Hair Removal Package
```
*(44 characters — max 60)*

---

**Layout**
Select: **Paragraph** (not Bullet Points — paragraph reads warmer and more personal for this brand)

---

**Description**
```
Book 4 or more laser sessions at FaBesthetics and save 15% on your package.

Becky Pfeifer, BSN will design a personalized treatment plan around your goals. Every client at FaBesthetics is treated as a VIP — from your first consultation through your last session.

Fill out the short form below and Becky will reach out personally, usually the same business day.
```
*(297 characters)*

---

**Button text** *(optional — appears on intro card if enabled)*
```
Request My Savings
```

---

### SECTION 2 — Questions

Meta pre-fills these from the user's Facebook profile. Keep all three — phone is Becky's primary follow-up channel.

| Order | Field | Type | Required |
|---|---|---|---|
| 1 | Full Name | Pre-filled | Yes |
| 2 | Phone Number | Pre-filled | Yes |
| 3 | Email | Pre-filled | Yes |

---

**Custom Question 1**

| Setting | Value |
|---|---|
| **Question type** | Multiple Choice |
| **Question text** | `Which area are you looking to treat?` *(37 chars — max 80)* |
| **Selection type** | Single select |

Options *(enter in this order)*:
```
Full Legs
Underarms
Bikini / Brazilian
Face or Upper Lip
Multiple areas / Not sure yet
```

> **Why this question:** Gives Becky a personal opener on the follow-up call. A client who selects "Bikini / Brazilian" gets a different conversation than one who selects "Face or Upper Lip." Also flags which services drive Meta leads vs. Google leads over time.

---

**Custom Question 2**

| Setting | Value |
|---|---|
| **Question type** | Multiple Choice |
| **Question text** | `When are you looking to get started?` *(36 chars — max 80)* |
| **Selection type** | Single select |

Options *(enter in this order)*:
```
As soon as possible
Within the next month
In the next 2–3 months
Just exploring for now
```

> **Why this question:** Segments leads by urgency for Becky's follow-up queue. Anyone who selects "As soon as possible" should receive a call within the hour. "Just exploring" leads go into a longer-term nurture sequence in GHL — do not drop them.

---

### SECTION 3 — Privacy Policy

| Setting | Value |
|---|---|
| **Custom disclaimer** | `By submitting this form, you agree that FaBesthetics may contact you by phone or email to discuss your inquiry and confirm your appointment details.` |
| **Link text** | `FaBesthetics Privacy Policy` |
| **Link URL** | `https://fabestheticsny.com` *(update to /privacy-policy if a dedicated page exists)* |

---

### SECTION 4 — Review Screen

*(This screen appears automatically for Higher Intent forms — Meta handles the layout. No copy input needed. It shows the user a summary of their answers and a "Submit" button.)*

The confirm button reads "Submit" by default. No change needed.

---

### SECTION 5 — Thank You Screen

**Headline**
```
You're All Set — We'll Be in Touch Today
```
*(40 characters — max 60)*

---

**Description**
```
Becky Pfeifer, BSN will personally reach out to discuss your goals, answer any questions, and confirm your 15% savings on your laser package.

Most clients hear back the same business day. We look forward to meeting you at FaBesthetics.
```
*(239 characters)*

---

**Button 1**

| Setting | Value |
|---|---|
| **Button type** | Visit Website |
| **Button text** | `See Our Services` |
| **URL** | `https://fabestheticsny.com` |

**Button 2** *(optional — add if CallRail number is available)*

| Setting | Value |
|---|---|
| **Button type** | Call Business |
| **Button text** | `Call FaBesthetics` |
| **Phone number** | *(enter Becky's CallRail tracking number)* |

---

## FORM 2: RETARGETING

### Meta Builder Settings

| Setting | Value |
|---|---|
| **Form name** | `FAB_LHR_15off_Retargeting_Apr2026` |
| **Form type** | More Volume |
| **Language** | English (US) |
| **Sharing** | Restricted |

---

### SECTION 1 — Intro

**Image**
Use the same image as Ad 4 (retargeting static). If no distinct retargeting creative yet, use the Ad 1 static image.

---

**Headline**
```
Your 15% Savings Is Still Available
```
*(36 characters — max 60)*

---

**Layout**
Select: **Paragraph**

---

**Description**
```
You've looked at FaBesthetics before. Your 15% off a laser hair removal package is still on the table.

Book 4 or more sessions with Becky Pfeifer, BSN and lock in your savings. No commitment required — a free consultation is always the first step.

Takes less than 60 seconds to request your spot.
```
*(298 characters)*

---

**Button text** *(optional)*
```
Claim My Savings
```

---

### SECTION 2 — Questions

| Order | Field | Type | Required |
|---|---|---|---|
| 1 | Full Name | Pre-filled | Yes |
| 2 | Phone Number | Pre-filled | Yes |
| 3 | Email | Pre-filled | Yes |

---

**Custom Question 1** *(keep retargeting forms to one custom question — remove all friction)*

| Setting | Value |
|---|---|
| **Question type** | Multiple Choice |
| **Question text** | `What's been on your mind about getting started?` *(47 chars — max 80)* |
| **Selection type** | Single select |

Options *(enter in this order)*:
```
Wondering if it works for my skin / hair type
Thinking through the cost
Waiting for the right time
Nothing — I'm ready to book
```

> **Why this question:** Surfaces the objection Becky should address on the follow-up call before she dials. "Wondering if it works for my skin/hair type" = lead needs clinical reassurance. "Thinking through the cost" = lead needs to understand the package value. "Nothing — I'm ready to book" = hot lead, call within 5 minutes.

---

### SECTION 3 — Privacy Policy

| Setting | Value |
|---|---|
| **Custom disclaimer** | `By submitting this form, you agree that FaBesthetics may contact you by phone or email to follow up on your inquiry.` |
| **Link text** | `FaBesthetics Privacy Policy` |
| **Link URL** | `https://fabestheticsny.com` |

---

### SECTION 4 — Thank You Screen

*(More Volume forms do not have a review screen. Submission goes directly here.)*

**Headline**
```
We'll Be in Touch Today
```
*(23 characters — max 60)*

---

**Description**
```
Becky will personally reach out to lock in your 15% savings and answer any questions before your first appointment.

You'll hear back the same business day. See you soon at FaBesthetics in Mahopac.
```
*(198 characters)*

---

**Button**

| Setting | Value |
|---|---|
| **Button type** | Visit Website |
| **Button text** | `Visit FaBesthetics` |
| **URL** | `https://go.fabestheticsny.com/laser-hair-removal-mahopac-offer/` |

---

## AD COPY ADJUSTMENTS WHEN USING INSTANT FORMS

When an ad points to an Instant Form instead of the landing page URL, make these two changes before publishing. Everything else in the ad copy stays the same.

### CTA Button

Change from → to:

| Ad | Original CTA | Instant Form CTA |
|---|---|---|
| Ad 1 (problem-first static) | Book Now | Get Quote |
| Ad 2 (social proof carousel) — all cards | Book Now / Claim Offer / Learn More | Get Quote |
| Ad 3 (Becky video) | Book Now | Get Quote |
| Ad 4 (retargeting static) | Book Now | Claim Offer |

> "Get Quote" and "Claim Offer" set the right expectation. "Book Now" implies the user will land on a booking page — clicking it and seeing a form instead creates a disconnect that increases drop-off.

---

### Closing Line of Primary Text

Swap the last line of each ad's body copy to match the form action:

**Ad 1 — Problem-first static**

Original closing line:
```
Save 15% when you book 4 or more sessions.
```

Instant Form version:
```
Request your 15% savings below — takes less than 60 seconds.
```

---

**Ad 2 — Carousel, Card 3 (offer card)**

Original closing line:
```
Claim your savings at fabestheticsny.com
```

Instant Form version:
```
Fill out the quick form below to claim your 15% savings.
```

---

**Ad 3 — Becky video, end card overlay text**

Original overlay:
```
Save 15% — Book 4+ Sessions
```

Instant Form version:
```
Request your consultation below — I'll reach out personally.
```

---

**Ad 4 — Retargeting static**

Original closing line:
```
Becky Pfeifer, BSN is ready when you are. Free consultation, no commitment required to start.
```

Instant Form version:
```
Fill in the form below — takes 60 seconds to claim your spot.
```

---

## CONNECTING INSTANT FORM LEADS TO GHL

Instant Form submissions do not automatically appear in GHL. Set up before running these forms at volume.

### Option A: Zapier (Recommended)

| Step | Action |
|---|---|
| Trigger | New Meta Lead Form Submission |
| Filter | Form name contains "FAB_LHR" |
| Action 1 | Create Contact in GHL |
| Action 2 | Send notification email to fab@fabestheticsny.com + iamherznerd@gmail.com |

**Field mapping:**

| Meta Form Field | GHL Field |
|---|---|
| Full Name | Contact Name |
| Phone Number | Phone |
| Email | Email |
| Treatment area answer | Custom Field: "Treatment Area Interest" |
| Timing answer | Custom Field: "Lead Urgency" |
| Objection answer (Form 2) | Custom Field: "Primary Objection" |

> Map the custom question answers as custom fields in GHL so Becky's follow-up call prep shows what service the lead is interested in and how urgent they are. This is what separates a personalized follow-up from a cold script.

### Option B: Manual Download (Backup Only)

Ads Manager → Forms Library → Click form → **Download** (CSV)
Check daily. Not sustainable for Becky's 5-minute response window.

### Owner

Bishal or Avi — confirm who handles GHL integrations for this client. Must be set up before instant form ads go live at any meaningful budget.

---

## LEAD ROUTING IN GHL AFTER FORM SUBMISSION

Once Zapier pipes Instant Form leads into GHL, the lead should trigger the same automation Becky already has for landing page form submissions. Confirm the GHL automation covers both sources:

- [ ] Immediate automated SMS from GHL within 60 seconds: "Hi [First Name], this is FaBesthetics — thanks for your interest in laser hair removal! Becky will personally follow up with you today. Talk soon."
- [ ] Immediate automated email confirmation
- [ ] Human follow-up task assigned to Becky (or Dan) within 5 minutes during business hours
- [ ] If no contact after 48 hours: lead moves to long-term nurture sequence, not dead

> Speed-to-lead on Meta leads is especially critical. Meta users are in scroll mode — they submitted a form in a moment of interest that will fade fast. The probability of qualifying a Meta lead drops by ~80% if the first contact is delayed beyond 5 minutes.
