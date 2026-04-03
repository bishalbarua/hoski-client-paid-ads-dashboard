---
name: google-drive-sync
description: Sync client folders and documents to Google Drive. Creates mirrored folder structure (clients/{name}/notes, reports, analysis, data) and uploads all local files using the service account. Zero file content passes through Claude's context. Triggers when user says "upload to Drive", "sync to Drive", "create Drive folder for [client]", "push docs to Drive", or similar.
---

# Google Drive Sync

Uploads local client documentation to Google Drive using the service account in `sheets-credentials.json`. The Python script handles all file I/O at the OS level — no file content enters Claude's context window, keeping token usage minimal regardless of how many files are synced.

---

## Prerequisites Check

Before running, verify:

1. `GOOGLE_DRIVE_ROOT_FOLDER_ID` is set in `.env`
2. The service account has Editor access to that Drive folder
3. Dependencies are installed: `pip install -r requirements.txt`

If `GOOGLE_DRIVE_ROOT_FOLDER_ID` is missing, tell the user:
> To set this up: create a folder in Google Drive, share it with the service account email in `sheets-credentials.json` (Editor access), then copy the folder ID from the URL into your `.env` file as `GOOGLE_DRIVE_ROOT_FOLDER_ID`.

---

## Commands

### List available clients
```bash
python3 scripts/drive_sync.py --list
```

### Sync one client
```bash
python3 scripts/drive_sync.py --client "Client Name (AccountID)"
```

### Sync all clients
```bash
python3 scripts/drive_sync.py --all
```

### Re-upload existing files (overwrite mode)
```bash
python3 scripts/drive_sync.py --all --overwrite
python3 scripts/drive_sync.py --client "Client Name (AccountID)" --overwrite
```

---

## Workflow

**Step 1: Understand the request**

Determine scope from the user's message:
- Named client ("sync Park Road to Drive") → use `--client`
- "all clients" / "everyone" → use `--all`
- "new client" or post-onboarding → use `--client` with the new client name

**Step 2: Check prerequisites**

```bash
python3 -c "
import os; from dotenv import load_dotenv; load_dotenv()
fid = os.environ.get('GOOGLE_DRIVE_ROOT_FOLDER_ID','')
print('Root folder ID:', fid if fid else 'NOT SET')
"
```

If not set, stop and give the user setup instructions above.

**Step 3: Run the sync**

Run the appropriate command. The script outputs a line per file:
- `[+]` = newly uploaded
- `[~]` = updated (overwrite mode)
- `[.]` = skipped (already exists)
- `[!]` = error

**Step 4: Report results**

Summarize what was synced:
- How many files uploaded/updated/skipped/errored
- Any `[!]` errors to flag
- Confirm the folder structure created in Drive

---

## Folder Structure in Drive

```
Google Ads Manager/          (your root folder, shared with service account)
└── clients/
    └── {Client Name} ({Account ID})/
        ├── notes/
        ├── reports/
        ├── analysis/
        └── data/
```

---

## File Handling

| File type | Drive behavior |
|---|---|
| `.docx` | Converted to Google Doc |
| `.xlsx` | Converted to Google Sheet |
| All others | Uploaded as-is |

By default the script skips files that already exist in Drive. Use `--overwrite` to re-upload changed files.

---

## Token Efficiency Note

This skill is designed to cost ~1-5K tokens regardless of file count. The script reads files from disk at the OS/Python level — file content never enters this conversation. Only the script's stdout (file names and counts) is returned to Claude.
