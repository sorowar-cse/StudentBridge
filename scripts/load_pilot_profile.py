"""Load one synthetic profile into a blank dedicated Supabase test account."""

import argparse
from getpass import getpass
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
from studentbridge.cloud import CloudStore
from studentbridge.profile import validated_profile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True, help="P01 to P15")
    args = parser.parse_args()
    cases = json.loads((ROOT / "data/profile_test_cases.json").read_text())["cases"]
    case = next((c for c in cases if c["id"] == args.case.upper()), None)
    if case is None:
        parser.error("Choose P01 to P15.")
    print("SYNTHETIC: all amounts are invented; this is not an official university fee.")
    print(
        "Case:",
        case["id"],
        "| currency:",
        case["profile"]["budget_currency"],
        "| expected total:",
        case["expected_total"],
    )
    if input("Type SYNTHETIC to save into a blank dedicated test account: ").strip() != "SYNTHETIC":
        return 1
    load_dotenv(ROOT / ".env")
    store = CloudStore()
    token = store.login(
        input("Dedicated test account email: ").strip(), getpass("Password (hidden): ")
    )
    if not token:
        raise SystemExit("Sign-in failed; no profile saved.")
    try:
        if store.student_profile(token) or store.profile(token):
            raise SystemExit("Account already has personal data; refusing to overwrite.")
        store.save_student_profile(token, validated_profile(case["profile"]))
        print(
            "Saved. Open My Forecast in this account and compare with data/profile_test_expected.csv."
        )
    finally:
        store.logout(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
