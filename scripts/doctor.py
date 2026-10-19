"""Connection checks without printing secrets. --login enrolls the supplied pilot user."""

import argparse
from getpass import getpass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
from studentbridge.cloud import CloudStore
from studentbridge.fx import FXService
from studentbridge.llm import JSONClient, ModelConfig
import os

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--login",
        action="store_true",
        help="Prompt for a pilot account; enroll and verify its own RLS/RPC access",
    )
    args = parser.parse_args()
    failed = []

    def check(label, fn):
        try:
            detail = fn()
            print("PASS:", label, detail or "")
        except Exception as exc:
            failed.append(label)
            # Application/provider exception bodies are deliberately not printed.
            print(
                "FAIL:", label, "(" + type(exc).__name__ + "). See Developer Guide troubleshooting."
            )

    backend = os.getenv("STUDENTBRIDGE_BACKEND", "local")
    print("StudentBridge v4 | backend:", backend)
    cloud = None
    if backend == "supabase":
        try:
            cloud = CloudStore()
            print("PASS: cloud configuration shape; privileged API keys rejected")
        except Exception:
            failed.append("cloud configuration")
            print(
                "FAIL: cloud configuration. Run setup_local.py and preserve the original master key."
            )
        if cloud:

            def settings():
                result = cloud._request("GET", "/auth/v1/settings", authenticated=False)
                if result.get("disable_signup") is False:
                    raise ValueError("Disable public signups in Supabase.")
                return "Confirm public signups are OFF in the dashboard."

            check("Supabase Auth endpoint", settings)
    else:
        print("NOTE: local mode does not verify cloud persistence or Supabase login.")

    def fxcheck():
        ref = FXService("live").rate("MYR", "CNY")
        return "MYR/CNY observation " + ref.as_of + " (not a bank execution price)"

    check("Published FX reference", fxcheck)
    if os.getenv("GROQ_API_KEY"):
        check(
            "Groq model catalogue (no inference request)",
            lambda: f"{len(JSONClient(ModelConfig('groq')).models())} models visible",
        )
    else:
        print("NOTE: Groq not configured; built-in calculators remain usable.")
    if args.login and cloud:
        email = input("Pilot account email: ").strip()
        password = getpass("Pilot account password (hidden): ")
        token = cloud.login(email, password)
        password = ""
        if token:
            try:
                check(
                    "Confirmed pilot membership", lambda: "role " + cloud.principal(token)["role"]
                )

                def audit():
                    result = cloud.export_audit(token)
                    if not result["global_integrity"]["valid"]:
                        raise ValueError("Audit mismatch")
                    return "own-account chain verified"

                check("Database RPC and audit", audit)
            finally:
                cloud.logout(token)
        else:
            failed.append("pilot login")
            print(
                "FAIL: pilot login. Check account/password, confirmation, SQL keys and 15-member limit."
            )
    print(
        "Result:",
        "CHECK FAILED ITEMS BEFORE THE COMPETITION"
        if failed
        else "Requested checks passed; read the stated scope above.",
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
