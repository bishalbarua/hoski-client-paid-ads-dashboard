"""
Google Drive Client Folder Sync
Purpose: Create mirrored client folder structure in Google Drive and upload
         local client files authenticated as your Google user account. Zero
         file content passes through Claude's context — all uploads are
         OS-level file reads.

Setup:
    1. Run: python3 scripts/get_drive_refresh_token.py
    2. Copy the printed token into .env as GOOGLE_DRIVE_REFRESH_TOKEN.
    3. Set GOOGLE_DRIVE_ROOT_FOLDER_ID in .env (folder ID from Drive URL).
    4. pip install google-api-python-client google-auth-httplib2

Usage:
    python3 scripts/drive_sync.py --list
    python3 scripts/drive_sync.py --client "Park Road Custom Furniture and Decor (7228467515)"
    python3 scripts/drive_sync.py --all
    python3 scripts/drive_sync.py --all --overwrite
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv()

# ─── CONFIG ──────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.parent
CLIENTS_DIR = PROJECT_ROOT / "clients"

# MIME types for Google-native conversion
CONVERT_MIME = {
    ".docx": "application/vnd.google-apps.document",
    ".xlsx": "application/vnd.google-apps.spreadsheet",
}

# Files to skip
SKIP_PATTERNS = {".DS_Store", "__pycache__", ".git"}


# ─── AUTH ─────────────────────────────────────────────────────────────────────

def get_drive_service():
    refresh_token = os.environ.get("GOOGLE_DRIVE_REFRESH_TOKEN")
    client_id = os.environ.get("GOOGLE_ADS_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_ADS_CLIENT_SECRET")

    if not refresh_token:
        print("[Drive] GOOGLE_DRIVE_REFRESH_TOKEN not set in .env")
        print("        Run: python3 scripts/get_drive_refresh_token.py")
        sys.exit(1)
    if not client_id or not client_secret:
        print("[Drive] GOOGLE_ADS_CLIENT_ID or GOOGLE_ADS_CLIENT_SECRET not set in .env")
        sys.exit(1)

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/drive"],
    )
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds)


# ─── FOLDER HELPERS ───────────────────────────────────────────────────────────

def find_folder(service, name: str, parent_id: str) -> str | None:
    """Return folder ID if it exists under parent, else None."""
    query = (
        f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
        f" and '{parent_id}' in parents and trashed=false"
    )
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    return files[0]["id"] if files else None


def get_or_create_folder(service, name: str, parent_id: str) -> str:
    """Return existing folder ID or create and return new one."""
    folder_id = find_folder(service, name, parent_id)
    if folder_id:
        return folder_id
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


# ─── FILE HELPERS ─────────────────────────────────────────────────────────────

def find_file(service, name: str, parent_id: str) -> str | None:
    """Return file ID if it exists under parent, else None."""
    safe_name = name.replace("'", "\\'")
    query = (
        f"name='{safe_name}' and '{parent_id}' in parents"
        f" and mimeType!='application/vnd.google-apps.folder' and trashed=false"
    )
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    return files[0]["id"] if files else None


def upload_file(service, local_path: Path, parent_id: str, overwrite: bool) -> str:
    """Upload a file to Drive. Returns 'uploaded', 'updated', or 'skipped'."""
    suffix = local_path.suffix.lower()
    convert_mime = CONVERT_MIME.get(suffix)

    metadata = {"name": local_path.name, "parents": [parent_id]}
    media = MediaFileUpload(str(local_path), resumable=False)

    existing_id = find_file(service, local_path.name, parent_id)

    if existing_id:
        if not overwrite:
            return "skipped"
        # Update existing file content
        service.files().update(
            fileId=existing_id,
            media_body=media,
        ).execute()
        return "updated"

    if convert_mime:
        metadata["mimeType"] = convert_mime

    service.files().create(body=metadata, media_body=media, fields="id").execute()
    return "uploaded"


# ─── SYNC LOGIC ───────────────────────────────────────────────────────────────

def sync_client(service, client_dir: Path, root_folder_id: str, overwrite: bool):
    """Sync one client directory to Drive."""
    client_name = client_dir.name
    print(f"\n[Drive] Syncing: {client_name}")

    # Create top-level client folder
    client_folder_id = get_or_create_folder(service, client_name, root_folder_id)

    counts = {"uploaded": 0, "updated": 0, "skipped": 0, "errors": 0}

    for subdir in sorted(client_dir.iterdir()):
        if not subdir.is_dir() or subdir.name in SKIP_PATTERNS:
            continue

        subfolder_id = get_or_create_folder(service, subdir.name, client_folder_id)

        for file_path in sorted(subdir.iterdir()):
            if not file_path.is_file() or file_path.name in SKIP_PATTERNS:
                continue

            try:
                result = upload_file(service, file_path, subfolder_id, overwrite)
                counts[result] += 1
                status_icon = {"uploaded": "+", "updated": "~", "skipped": "."}.get(result, "?")
                print(f"  [{status_icon}] {subdir.name}/{file_path.name}")
            except Exception as e:
                counts["errors"] += 1
                print(f"  [!] {subdir.name}/{file_path.name} — {e}")

    print(
        f"  Done: {counts['uploaded']} uploaded, {counts['updated']} updated, "
        f"{counts['skipped']} skipped, {counts['errors']} errors"
    )


def list_clients():
    """Print available client directories."""
    if not CLIENTS_DIR.exists():
        print(f"[Drive] clients/ directory not found at {CLIENTS_DIR}")
        sys.exit(1)
    clients = sorted(d.name for d in CLIENTS_DIR.iterdir() if d.is_dir())
    print(f"Available clients ({len(clients)}):")
    for name in clients:
        print(f"  {name}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Sync client docs to Google Drive")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="List available clients")
    group.add_argument("--client", metavar="NAME", help="Sync a specific client folder")
    group.add_argument("--all", action="store_true", help="Sync all client folders")
    parser.add_argument(
        "--overwrite", action="store_true",
        help="Re-upload files that already exist in Drive"
    )
    args = parser.parse_args()

    if args.list:
        list_clients()
        return

    root_folder_id = os.environ.get("GOOGLE_DRIVE_ROOT_FOLDER_ID")
    if not root_folder_id:
        print("[Drive] GOOGLE_DRIVE_ROOT_FOLDER_ID not set in .env")
        print("        Share a Drive folder with your service account and paste its ID.")
        sys.exit(1)

    service = get_drive_service()

    if args.all:
        client_dirs = sorted(d for d in CLIENTS_DIR.iterdir() if d.is_dir())
        print(f"[Drive] Syncing all {len(client_dirs)} clients to Drive...")
        for client_dir in client_dirs:
            sync_client(service, client_dir, root_folder_id, args.overwrite)
    else:
        target = CLIENTS_DIR / args.client
        if not target.exists():
            print(f"[Drive] Client folder not found: {target}")
            print("        Run --list to see available clients.")
            sys.exit(1)
        sync_client(service, target, root_folder_id, args.overwrite)

    print("\n[Drive] Sync complete.")


if __name__ == "__main__":
    main()
