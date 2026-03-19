# New Client

Scaffold a new client folder with all standard structure and a pre-filled notes template.

## Usage
`/new-client [client name] [account ID]`

## Instructions

1. **Parse $ARGUMENTS** — extract the client name and Google Ads account ID. If either is missing, ask before proceeding.

2. **Create the client folder** at:
   `Google Ads Manager/clients/[Client Name] ([Account ID])/`

   With subfolders:
   - `reports/`
   - `analysis/`
   - `data/`
   - `notes/`

3. **Create `notes/client-info.md`** pre-filled with:
   - Client name and account ID at the top
   - All standard sections: Goals & Targets, Business Info, Brand Terms, Competitor Notes, Campaign Overview, Conversion Tracking, CRM & Tech Stack, Account Quirks, Client Communication, Ongoing To-Dos
   - Today's date in the Last updated field
   - Leave fields blank — do not guess or infer anything not provided

4. **Add the client to CLAUDE.md** — append a new row to the Client Accounts table in `Google Ads Manager/CLAUDE.md`:
   ```
   | [Client Name] | [Account ID] |
   ```

5. **Confirm** what was created and show the path to client-info.md so the user can open it and fill in the details.

6. Remind the user: "Fill in the client-info.md with goals, budget, CPA targets, brand terms, and tracking setup so Claude has full context for future work on this account."
