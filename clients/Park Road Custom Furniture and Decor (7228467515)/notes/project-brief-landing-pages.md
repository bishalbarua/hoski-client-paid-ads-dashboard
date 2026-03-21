# Project Brief: Park Road — Two New Google Ads Landing Pages
**Client:** Park Road Custom Furniture and Decor
**Project type:** Landing page design, build, and GHL automation setup
**Date:** 2026-03-21
**Assigned by:** Bishal

---

## STOP — READ THIS BEFORE YOU START BUILDING

These landing pages are connected to paid Google Ads campaigns. Every element — copy, images, form fields, URLs, page flow, and conversion tracking — has been intentionally designed for a specific reason tied to search intent and lead tracking. **Do not make copy, layout, or structural changes without checking first.**

If something in the copy doc is unclear, seems wrong, or conflicts with how GHL normally works, **ask before you change it.** A wrong assumption here costs the client real ad spend.

The full copy, image direction, mobile specs, user journey, and conversion tracking setup for both pages are documented in the copy docs linked below. Read them fully before opening GHL.

---

## COPY DOCUMENTS (read before building)

| Page | Copy Document | Format |
|---|---|---|
| Custom Furniture landing page + TY pages | `clients/Park Road.../notes/landing-page-copy-custom-furniture.md` | `.md` and `.docx` |
| Cottage Furniture landing page + TY pages | `clients/Park Road.../notes/landing-page-copy-cottage-furniture.md` | `.md` and `.docx` |

Both docs contain: full section-by-section copy, image direction with AI prompts, mobile optimization specs, form field details, user journey flow, conversion tracking setup, URL structure, and thank you page copy.

---

## SCOPE OF WORK — PAGE INVENTORY

6 pages total across 2 campaigns. All pages live under `go.parkroadfurniture.com`.

### Campaign 1: Custom Furniture

| Page | URL | Purpose |
|---|---|---|
| Landing page | `/custom-furniture` | Primary ad destination — form fill |
| Thank You Page 1 | `/custom-furniture/thank-you` | Post-form confirmation + calendar CTA |
| Thank You Page 2 | `/custom-furniture/consultation-booked` | Post-calendar booking confirmation |

### Campaign 2: Cottage Furniture

| Page | URL | Purpose |
|---|---|---|
| Landing page | `/cottage-furniture` | Primary ad destination — form fill |
| Thank You Page 1 | `/cottage-furniture/thank-you` | Post-form confirmation + calendar CTA |
| Thank You Page 2 | `/cottage-furniture/consultation-booked` | Post-calendar booking confirmation |

---

## USER JOURNEY (applies to both campaigns)

```
Ad click
    ↓
Landing page (/custom-furniture or /cottage-furniture)
    ↓
User submits 4-field form
    ↓
Thank You Page 1 (/thank-you)   ← PRIMARY Google Ads conversion fires here
    ↓ (user's choice — optional next step)
User clicks "Book My Free Consultation"
    ↓
GHL Calendar (embedded or linked)
    ↓
Thank You Page 2 (/consultation-booked)   ← SECONDARY Google Ads conversion fires here
```

**Why this flow matters:** The previous go.parkroadfurniture.com flow sends users from the form directly to the calendar. This breaks conversion tracking — leads who fill the form but abandon the calendar are invisible in Google Ads. The new flow fires the primary conversion at TY1 (form fill), regardless of whether the user books the calendar. This is intentional and must not be changed.

---

## ROLE BREAKDOWN

### UX Designer

**Responsibility:** Page design — layout, visual direction, image sourcing/generation, mobile responsiveness.

**Pages to design:** Both landing pages (6 total including TY pages, though TY pages are simpler layouts).

**Key instructions:**

1. **Base template:** Clone the existing `go.parkroadfurniture.com` page in GHL. Do not start from scratch. The structure (section order, layout blocks) stays mostly the same. You are swapping content, not redesigning.

2. **The two landing pages must look visually distinct from each other.** The Custom Furniture page uses a contemporary home interior aesthetic. The Cottage Furniture page uses a Muskoka/cottage country aesthetic — warm wood tones, rustic interiors, natural light. See the Image Direction section in each copy doc for full details.

3. **Images:** AI-generated images are approved for hero backgrounds, consultation section photos, and accent images. Do not use AI for the portfolio section — use Park Road's own portfolio photos. Full AI prompts are in the copy docs. If the output quality is not right, escalate to the creative director.

4. **Hero image is the highest-stakes creative decision on the Cottage Furniture page.** A Muskoka/cottage interior that makes the visitor feel "I want that at my cottage" does message match work before they read a single word. Take time to get this right.

5. **Mobile is the primary viewport.** The majority of traffic will be on mobile. All layout decisions must be mobile-first. Specific mobile rules per section are in the copy docs. The key ones:
   - Sticky header: logo left, phone (tap-to-call) + CTA button right. Max 56px height.
   - All CTA buttons full width on mobile, minimum 52px height.
   - Hero headline 36px on mobile.
   - Pain point cards: single column, no horizontal scroll.
   - Comparison table: convert to 2-column Park Road checklist on mobile — the full 4-column table does not render well at 375px.
   - FAQ: accordion/collapse format on mobile, all questions collapsed by default.
   - Portfolio: single-column image grid. Lazy-load below the fold.

6. **Form:** 4 fields only (Name, Phone, Email, What are you looking for?). The dropdown options differ between the two pages — see the Form section in each copy doc. Do not add the budget range or meeting preference fields from the existing page.

7. **Sticky header:** This does not exist on the current go.parkroadfurniture.com page and must be added. It should persist at all scroll depths.

8. **Questions before building?** Read the copy doc first, then ask Bishal before making any design decisions not covered in the doc.

---

### Web / GHL Builder

**Responsibility:** Building all 6 pages in GoHighLevel, configuring forms, wiring the user journey flow, and ensuring URL structure is correct.

**Key instructions:**

1. **Clone the existing `go.parkroadfurniture.com` funnel as the starting point.** Build two separate funnel paths within the same GHL sub-account: one under `/custom-furniture` and one under `/cottage-furniture`.

2. **URL structure must exactly match the table in the copy docs.** Google Ads conversion tracking is configured to fire on specific page URLs. If the URLs are wrong, conversions won't track. The URLs are:
   - `/custom-furniture` → `/custom-furniture/thank-you` → `/custom-furniture/consultation-booked`
   - `/cottage-furniture` → `/cottage-furniture/thank-you` → `/cottage-furniture/consultation-booked`

3. **Form setup:**
   - 4 fields: Full Name, Phone Number, Email Address, What are you looking for? (dropdown)
   - Dropdown options differ per page — see the Form section in each copy doc for the exact option labels
   - On form submit: redirect to the campaign's TY1 page (`/thank-you`), NOT the calendar
   - Do NOT wire the form to redirect to the calendar directly

4. **Thank You Page 1 (TY1):**
   - Show confirmation copy (see copy doc)
   - Include calendar embed or button link below the confirmation copy
   - If the GHL calendar embed does not render properly on mobile, use a full-width button that opens the calendar in a new tab
   - Calendar booking should redirect to TY2 (`/consultation-booked`) on completion

5. **Thank You Page 2 (TY2):**
   - Simple confirmation page — headline, sub-text, 3 prep points, phone number, optional Instagram/portfolio link
   - No form, no calendar, no hard sell

6. **Sticky header:** Must be added to both landing pages. It does not exist on the current page. Logo left, phone tap-to-call + CTA button right. Confirm with UX designer on implementation in GHL.

7. **Countdown timer:** Both landing pages have a countdown timer section. The expiry date has not been confirmed with the client yet — build the timer block but leave the date as a placeholder. Flag this to Bishal before launch so the date can be set.

8. **No navigation menu** on any of the 6 pages. No links that take users away from the page (except the optional Instagram/portfolio link on TY2).

9. **Questions before building?** Read the copy doc fully, then ask Bishal before deviating from anything in the doc.

---

### GHL Automation Team

**Responsibility:** Setting up all post-form-submission automations in GoHighLevel.

**Key instructions:**

1. **Two separate form triggers** — one for Custom Furniture form submissions, one for Cottage Furniture form submissions. Keep these as separate workflows. Do not merge them.

2. **Lead tagging:** When a form is submitted, tag the contact with the campaign source:
   - Custom Furniture form → tag: `Lead - Custom Furniture`
   - Cottage Furniture form → tag: `Lead - Cottage Furniture`

3. **Lead notification:** On form submission, send an internal notification to the Park Road team (confirm recipient email with client) so they can follow up within 24 hours. The TY1 page tells the user "one of our designers will reach out within 24 hours" — this must actually happen.

4. **Lead follow-up sequence (confirm with Bishal before building):**
   - If the user does NOT book the calendar within 24 hours of the form fill, trigger a follow-up SMS or email: "Hi [First Name], just checking in — have you had a chance to book your free consultation? Your $750 discount is still reserved: [calendar link]"
   - Suggested timing: 24 hours after form fill, if no consultation booked tag exists

5. **Consultation booked trigger:** When TY2 (`/consultation-booked`) is visited, tag the contact with:
   - Custom Furniture: `Consultation Booked - Custom Furniture`
   - Cottage Furniture: `Consultation Booked - Cottage Furniture`
   - Use these tags to suppress the follow-up sequence — do not send a follow-up nudge to someone who has already booked.

6. **CRM pipeline:** Add form fill leads to a pipeline stage "New Lead — Awaiting Contact" and move them to "Consultation Booked" when TY2 is visited. Confirm pipeline name and stage labels with Park Road or Bishal.

7. **Questions before building?** Ask Bishal to confirm the follow-up sequence timing, recipient email for notifications, and pipeline setup before building automations.

---

## CONVERSION TRACKING (for Bishal / Google Ads setup — not the build team)

These are Google Ads conversion actions to be created after pages are live. Listed here for reference.

| Conversion Name | Trigger | Type | Designation |
|---|---|---|---|
| `CF - Form Submission` | Visit to `/custom-furniture/thank-you` | URL-based | Primary |
| `CF - Consultation Booked` | Visit to `/custom-furniture/consultation-booked` | URL-based | Secondary |
| `Cottage - Form Submission` | Visit to `/cottage-furniture/thank-you` | URL-based | Primary |
| `Cottage - Consultation Booked` | Visit to `/cottage-furniture/consultation-booked` | URL-based | Secondary |

Prerequisite: Base Google Tag must be active on the GHL subdomain (`go.parkroadfurniture.com`). Confirm this is already installed before creating URL-based conversion actions.

---

## THINGS TO CONFIRM WITH CLIENT BEFORE LAUNCH

The build team can proceed without these, but these must be resolved before the pages go live:

- [ ] **Phone number** — replace all `(519) XXX-XXXX` placeholders in both landing pages and TY pages
- [ ] **Offer expiry date** — needed to set the countdown timer on both pages
- [ ] **$750 off $5,000+ offer confirmed** — no exclusions, valid for new orders, no end date issues
- [ ] **Delivery coverage** — Custom page: confirm Kitchener, Waterloo, Windsor, Guelph, Woodstock. Cottage page: confirm Muskoka, Georgian Bay, Haliburton, Prince Edward County, Kawartha Lakes
- [ ] **Bunk beds and log beds** — does Park Road make these? Determines FAQ Q6 on cottage page
- [ ] **Cottage-specific portfolio photos** — do they have rustic/farmhouse/cottage pieces photographed? Needed for cottage page portfolio
- [ ] **Cottage customer testimonials** — any testimonials from cottage or Muskoka customers? Surfaced on cottage TY1 page
- [ ] **GHL notification recipient** — who receives the internal lead notification email when a form is submitted?
- [ ] **CRM pipeline** — does a pipeline already exist in GHL, or does one need to be created?

---

## DEFINITION OF DONE (pre-launch QA checklist)

Complete all of these before flagging as ready to launch:

**UX / Design**
- [ ] Both landing pages visually distinct from each other and from the existing go.parkroadfurniture.com page
- [ ] Cottage page hero image passes the "I want that at my cottage" test — not a city showroom
- [ ] All mobile layouts reviewed at 375px and 414px screen width
- [ ] Sticky header persists on scroll on both pages
- [ ] CTA buttons full width on mobile, minimum 52px height
- [ ] Comparison table renders as 2-column checklist on mobile

**Build / GHL**
- [ ] All 6 page URLs match the URL structure exactly
- [ ] Form on each landing page has exactly 4 fields with correct dropdown options
- [ ] Form submit redirects to TY1 (not calendar)
- [ ] Calendar on TY1 redirects to TY2 on booking completion
- [ ] No navigation menu on any of the 6 pages
- [ ] Countdown timer block in place (date to be set — flagged to Bishal)
- [ ] Phone numbers are tap-to-call on mobile (href="tel:...")
- [ ] Page speed tested — images lazy-loaded below fold

**Automation**
- [ ] Two separate form workflows (Custom Furniture, Cottage Furniture)
- [ ] Lead tagging fires on form submit
- [ ] Internal notification fires on form submit
- [ ] Follow-up sequence built and tested (confirm timing with Bishal before activating)
- [ ] Consultation booked tag fires when TY2 is visited
- [ ] Follow-up suppressed for contacts with consultation booked tag

**Conversion Tracking (Bishal)**
- [ ] Google Tag confirmed active on go.parkroadfurniture.com
- [ ] 4 conversion actions created in Google Ads
- [ ] Test form submission fires `CF - Form Submission` or `Cottage - Form Submission` correctly
- [ ] Test calendar booking fires `CF - Consultation Booked` or `Cottage - Consultation Booked` correctly

---

## QUESTIONS? WHO TO ASK

All questions about copy, strategy, offer details, or client preferences: **ask Bishal before making any assumptions.**

Do not make creative or structural changes based on personal preference or "this is how we usually do it." These pages are built around a specific ad strategy and every decision has a reason. When in doubt, ask.
