#!/usr/bin/env python3
"""
gmail_invoice_dl.py — Download PDF invoice attachments from Gmail label to local folder.

Usage:
    python3 tools/gmail_invoice_dl.py [--dest /path/to/folder]

Auth setup:
    Place client_secret.json in ~/.config/gmail-invoice-dl/
    On first run, a browser window opens for OAuth authorization.
"""

import argparse
import base64
import hashlib
import json
import os
import sys
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

LABEL_NAME = "Propria GmbH/Rechnungen"
DEFAULT_DEST = "/Users/dister/Library/CloudStorage/GoogleDrive-ilja.disterheft@gmail.com/Shared drives/Propria/Propria GmbH/0. Inbox Propria"
CONFIG_DIR = Path.home() / ".config" / "gmail-invoice-dl"
TOKEN_FILE = CONFIG_DIR / "token.json"
CLIENT_SECRET_FILE = CONFIG_DIR / "client_secret.json"
STATE_FILE = CONFIG_DIR / "state.json"
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_state() -> set:
    if STATE_FILE.exists():
        data = json.loads(STATE_FILE.read_text())
        return set(data.get("hashes", []))
    return set()


def save_state(hashes: set):
    STATE_FILE.write_text(json.dumps({"hashes": sorted(hashes)}, indent=2))


def get_gmail_service():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET_FILE.exists():
                print(
                    "ERROR: client_secret.json not found.\n"
                    "\n"
                    "To create one:\n"
                    "  1. Go to https://console.cloud.google.com/apis/credentials\n"
                    "  2. Create a project (or select existing)\n"
                    "  3. Enable Gmail API: APIs & Services -> Enable APIs -> Gmail API\n"
                    "  4. Create credentials: Credentials -> Create Credentials -> OAuth client ID\n"
                    "  5. Application type: Desktop app\n"
                    "  6. Download the JSON file\n"
                    f"  7. Save it to: {CLIENT_SECRET_FILE}\n"
                    "\n"
                    "Also add your email as a test user under OAuth consent screen if the app is in testing mode."
                )
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRET_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def find_label_id(service, label_name: str) -> str:
    result = service.users().labels().list(userId="me").execute()
    for label in result.get("labels", []):
        if label["name"] == label_name:
            return label["id"]
    print(f"ERROR: Gmail label '{label_name}' not found.")
    print("Available labels:")
    for label in result.get("labels", []):
        print(f"  {label['name']}")
    sys.exit(1)


def get_message_date(headers: list) -> str:
    for h in headers:
        if h["name"].lower() == "date":
            try:
                dt = parsedate_to_datetime(h["value"])
                return dt.strftime("%Y-%m-%d")
            except Exception:
                pass
    return "0000-00-00"


def get_sender_domain(headers: list) -> str:
    for h in headers:
        if h["name"].lower() == "from":
            value = h["value"]
            # Extract email address from "Name <email>" or plain "email"
            if "<" in value and ">" in value:
                addr = value.split("<")[1].split(">")[0].strip()
            else:
                addr = value.strip()
            if "@" in addr:
                return addr.split("@")[1].lower()
            return addr.lower()
    return "unknown"


def build_filename(date: str, domain: str, original_name: str) -> str:
    # Strip .pdf extension to avoid double extension, then re-add
    stem = original_name
    if stem.lower().endswith(".pdf"):
        stem = stem[:-4]
    return f"{date}_{domain}_{stem}.pdf"


def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download_invoices(dest_folder: str):
    ensure_config_dir()
    dest = Path(dest_folder)
    if not dest.exists():
        print(f"ERROR: Destination folder does not exist: {dest}")
        sys.exit(1)

    known_hashes = load_state()
    service = get_gmail_service()
    label_id = find_label_id(service, LABEL_NAME)

    # Fetch all message IDs under the label
    messages = []
    page_token = None
    while True:
        kwargs = {"userId": "me", "labelIds": [label_id], "q": "is:unread", "maxResults": 500}
        if page_token:
            kwargs["pageToken"] = page_token
        result = service.users().messages().list(**kwargs).execute()
        messages.extend(result.get("messages", []))
        page_token = result.get("nextPageToken")
        if not page_token:
            break

    downloaded = 0
    skipped = 0

    for msg_ref in messages:
        msg_id = msg_ref["id"]
        msg = service.users().messages().get(
            userId="me", id=msg_id, format="full"
        ).execute()

        headers = msg.get("payload", {}).get("headers", [])
        date = get_message_date(headers)
        domain = get_sender_domain(headers)

        # Collect all PDF parts recursively
        pdf_parts = []

        def collect_parts(payload):
            mime = payload.get("mimeType", "")
            filename = payload.get("filename", "")
            body = payload.get("body", {})
            attachment_id = body.get("attachmentId")

            if mime == "application/pdf" and filename and attachment_id:
                pdf_parts.append((filename, attachment_id))

            for part in payload.get("parts", []):
                collect_parts(part)

        collect_parts(msg.get("payload", {}))

        if not pdf_parts:
            continue

        any_downloaded = False
        for original_name, attachment_id in pdf_parts:
            attachment = (
                service.users()
                .messages()
                .attachments()
                .get(userId="me", messageId=msg_id, id=attachment_id)
                .execute()
            )
            data = base64.urlsafe_b64decode(attachment["data"])
            file_hash = sha256_of_bytes(data)
            final_name = build_filename(date, domain, original_name)

            if file_hash in known_hashes:
                print(f"[SKIP] {final_name} — duplicate")
                skipped += 1
                continue

            dest_path = dest / final_name
            dest_path.write_bytes(data)
            known_hashes.add(file_hash)
            save_state(known_hashes)
            print(f"[DOWNLOAD] {final_name}")
            downloaded += 1
            any_downloaded = True

        if any_downloaded:
            service.users().messages().modify(
                userId="me",
                id=msg_id,
                body={"removeLabelIds": ["UNREAD"]},
            ).execute()

    print(f"\nDone. Downloaded: {downloaded}, Skipped: {skipped}")


def main():
    parser = argparse.ArgumentParser(
        description="Download PDF invoices from Gmail label to local folder."
    )
    parser.add_argument(
        "--dest",
        default=DEFAULT_DEST,
        help="Destination folder (default: Google Drive Propria inbox)",
    )
    args = parser.parse_args()
    download_invoices(args.dest)


if __name__ == "__main__":
    main()
