# Lead Quality Optimization - 2026-03-21

**Trigger:** Client feedback from Dr. Joshua Haimovici - callers not answering callbacks, CDCP/government plan inquiries, price shoppers not booking.

---

## Actions Taken

### 1. CDCP Negative Keywords - Added to both active campaigns

Added 5 missing CDCP-related phrase match negatives to both "Dental Patient Acquisition" and "Insurance Accepted" campaigns. These terms were already covered: `cdcp`, `canadian dental care plan`, `government dental`, `free dental`. The following were missing and added:

- low income dental
- dental assistance program
- refugee dental
- subsidized dental
- dental for seniors government

Reasoning: Search term data showed `"refugee dental clinic near me"` and other government-plan queries spending budget and generating calls from patients the practice cannot serve. These callers call, leave a message, then don't answer the callback once they find out CDCP is not accepted.

### 2. Competitor Clinic Negatives - Added to both active campaigns

Added 17 competitor/other clinic name phrase match negatives to both campaigns. Full list: les dentistes du vieux port, denticare atwater, dentwest, terjanian, nuo centre dentaire, oralvie, beydoun, leonard gordon, clinique dentaire université de montréal, centre dentaire université, rockland dental, la perla dentist, warm smiles montreal, dentiste delson, abc dents, centre dentaire lacolle, dentiste jean talon.

Reasoning: Search term data showed significant spend on other clinic names (example: "les dentistes du vieux port" at $23.41, "clinique denticare atwater" at $12.26). These searchers are looking for a specific other clinic, clicking Dentiste by mistake, leaving a voicemail, then not answering the callback because they found who they were actually looking for.

### 3. Insurance Accepted Campaign - Paused

Paused "Hoski | Search | Insurance Accepted 14/3/26" (campaign ID 23648173083).

Reasoning: Campaign spent $181.41 in the last 30 days with 0 conversions. The Blue Cross ad group keywords (`"blue cross dental plans"`, `"blue cross dental insurance"`) were attracting insurance researchers, not patients ready to book. Search terms included US-specific queries (`"blue cross blue shield oregon dental"`, `"anthem blue cross dental phone number"`) with no relevance to a Montreal dental practice. This campaign was a direct driver of price-shopping calls. Will rebuild with appointment-intent keywords before reactivating.

---

## Open Items

- [ ] Rebuild Insurance Accepted campaign with correct intent keywords (e.g. "dentist accepting blue cross montreal")
- [ ] Audit conversion tracking: multiple primary conversions firing simultaneously (Smart Campaign calls, website click-to-call, Thank You page, Offline Purchase via Zapier) - may be inflating reported conversion counts and corrupting bidding signals
