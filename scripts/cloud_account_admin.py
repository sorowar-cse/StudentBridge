"""Local OWNER ONLY utility for controlled accounts; never imported by app.py.

The privileged Auth key is entered with getpass, is not saved, and is never a
Streamlit secret. Review the project and target before each explicit mutation.
Uses Supabase Auth's documented admin API; no direct auth.users SQL edits.
"""

import argparse
import base64
from getpass import getpass
import json
import os
from pathlib import Path
import re
import sys

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


class OwnerAuth:
    def __init__(self, url, key, http=None):
        if not re.fullmatch(r"https://[a-z0-9-]+\.supabase\.co", url):
            raise ValueError("Invalid Supabase project URL.")
        legacy = False
        if key.startswith("eyJ"):
            try:
                legacy = (
                    json.loads(base64.urlsafe_b64decode(key.split(".")[1] + "==")).get("role")
                    == "service_role"
                )
            except (ValueError, IndexError):
                pass
        if not key.startswith("sb_secret_") and not legacy:
            raise ValueError(
                "This owner-only utility requires a secret Auth admin key; not the publishable key."
            )
        self.url = url + "/auth/v1/admin/users"
        self.key = key
        self.http = http or requests.Session()

    def request(self, method, suffix="", data=None):
        try:
            r = self.http.request(
                method,
                self.url + suffix,
                headers={
                    "apikey": self.key,
                    "Authorization": "Bearer " + self.key,
                    "Content-Type": "application/json",
                },
                json=data,
                timeout=(5, 25),
                allow_redirects=False,
            )
            if not 200 <= r.status_code < 300:
                raise ValueError(
                    f"Auth admin request failed (HTTP {r.status_code}). Check project/key and dashboard. No automatic retry."
                )
            return r.json() if r.content else {}
        except requests.RequestException:
            raise ValueError(
                "Auth admin connection failed. Check the dashboard before retrying a creation."
            ) from None


def main():
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["create", "reset-password"])
    args = parser.parse_args()
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    print("OWNER ONLY. Project:", url)
    print(
        "Use the separate Supabase secret key here only. It will not be saved or sent to Streamlit."
    )
    key = getpass("Supabase secret admin key (hidden): ").strip()
    admin = OwnerAuth(url, key)
    if args.action == "create":
        email = input("Controlled pilot email: ").strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            raise ValueError("Invalid email.")
        print(
            "This creates a confirmed test account without sending email; verify the intended tester yourself."
        )
        suffix = ""
        payload = {"email": email, "email_confirm": True}
        method = "POST"
        target = email
    else:
        uid = input("User UUID copied from Supabase Authentication > Users: ").strip()
        if not re.fullmatch(r"[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}", uid):
            raise ValueError("Invalid UUID.")
        user = admin.request("GET", "/" + uid)
        target = user.get("email") or user.get("user", {}).get("email")
        if not target:
            raise ValueError("Target email was not returned; inspect the dashboard.")
        print("Reset target:", target)
        suffix = "/" + uid
        payload = {}
        method = "PUT"
    password = getpass("New password (12–128 characters, hidden): ")
    if not 12 <= len(password) <= 128 or password != getpass("Repeat new password (hidden): "):
        raise ValueError("Passwords must match and contain 12–128 characters.")
    if input("Type the target email to confirm this action: ").strip().lower() != target.lower():
        raise ValueError("Target confirmation did not match; no account change made.")
    payload["password"] = password
    result = admin.request(method, suffix, payload)
    password = ""
    payload.clear()
    key = ""
    admin.key = ""
    print(
        "Account action completed. User ID:",
        result.get("id") or result.get("user", {}).get("id", "see dashboard"),
    )
    print(
        "Share the temporary password privately. The app cap applies when the account first enrolls."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
