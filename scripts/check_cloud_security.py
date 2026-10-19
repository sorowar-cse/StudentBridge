"""Live two-account checks after YOUR Supabase setup. Uses synthetic profile markers.

Run only with two dedicated test accounts, never existing real student profiles.
This script creates/overwrites and then removes those accounts' student profile
documents. It leaves enrollment and audit events as execution evidence.
"""

from getpass import getpass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
from studentbridge.cloud import CloudStore
from studentbridge.money import FinanceError
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def main():
    print(__doc__)
    if input("Type SYNTHETIC to continue: ").strip() != "SYNTHETIC":
        return 1
    stores = []
    for label in ["A", "B"]:
        store = CloudStore()
        email = input(f"Test account {label} email: ").strip()
        token = store.login(email, getpass("Password (hidden): "))
        if not token:
            raise SystemExit("Login failed; no live security score was recorded.")
        if store.student_profile(token) or store.profile(token):
            store.logout(token)
            raise SystemExit(
                "Account already has saved personal data. Use dedicated blank test accounts."
            )
        stores.append((store, token, store.principal(token)["id"]))
    a, ta, ua = stores[0]
    b, tb, ub = stores[1]
    if ua == ub:
        raise SystemExit("Use two different accounts.")
    checks = []

    def passed(name):
        print("PASS:", name)
        checks.append({"name": name, "passed": True})

    try:
        a.save_student_profile(ta, {"test_marker": "A-owned synthetic record"})
        assert a.student_profile(ta)["test_marker"].startswith("A-owned")
        passed("Own profile round trip and AES authentication")
        rows = b._request(
            "GET", "/rest/v1/sb_documents", params={"select": "encrypted", "user_id": "eq." + ua}
        )
        assert rows == []
        passed("B cannot SELECT A profile through the actual REST API")
        try:
            b._request(
                "PATCH",
                "/rest/v1/sb_members",
                params={"user_id": "eq." + ub},
                data={"role": "executor"},
            )
        except FinanceError:
            passed("Direct role update denied by database grants")
        else:
            raise AssertionError("Direct role update was not denied")
        try:
            a._request("GET", "/rest/v1/sb_documents", authenticated=False)
        except FinanceError:
            passed("Anonymous document access denied")
        else:
            raise AssertionError("Anonymous access was not denied")
        b.clear_personal_data(tb)
        assert a.student_profile(ta)
        passed("B deletion does not affect A")
        assert a.export_audit(ta)["global_integrity"]["valid"]
        assert b.export_audit(tb)["global_integrity"]["valid"]
        passed("Both per-user audit chains verify")
        result = {
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "scope": "YOUR hosted Supabase, synthetic dedicated accounts",
            "checks": checks,
            "note": "No JWTs, passwords, emails or private profile values exported.",
        }
        out = ROOT / "evaluation/cloud_security_private.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(result, indent=2))
        print(
            "Saved private evidence to evaluation/cloud_security_private.json. Review before sharing."
        )
    finally:
        for store, token, _ in stores:
            try:
                store.clear_personal_data(token)
                store.logout(token)
            except FinanceError:
                print("Cleanup unavailable. Remove synthetic documents using the Account page.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
