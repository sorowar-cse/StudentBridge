"""Local owner CLI for role-separated accounts. Never pass passwords in arguments."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import argparse
import getpass
import os
from dotenv import load_dotenv
from studentbridge.store import Store
from studentbridge.money import FinanceError

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
if os.getenv("STUDENTBRIDGE_BACKEND") == "supabase":
    raise SystemExit(
        "Cloud accounts are managed in Supabase > Authentication > Users. See DEVELOPER_GUIDE_BN.md."
    )
p = argparse.ArgumentParser()
p.add_argument("action", choices=["create", "reset-password"])
p.add_argument("username")
p.add_argument("--role", choices=["viewer", "planner", "executor"], default="viewer")
a = p.parse_args()
directory = Path(os.getenv("STUDENTBRIDGE_DATA_DIR", "runtime"))
if not directory.is_absolute():
    directory = ROOT / directory
store = Store(directory)
password = getpass.getpass("New password (12+ characters): ")
if password != getpass.getpass("Repeat password: "):
    p.error("Passwords do not match.")
try:
    if a.action == "create":
        store.create_user(a.username, password, a.role)
        print("Account created. Role:", a.role)
    else:
        if not 12 <= len(password) <= 128:
            raise FinanceError("Use 12–128 characters.")
        hashed = store.passwords.hash(password)
        with store.connection(write=True) as con:
            row = con.execute(
                "SELECT id FROM users WHERE username=?", (a.username.lower().strip(),)
            ).fetchone()
            if not row:
                raise FinanceError("Account not found.")
            con.execute(
                "UPDATE users SET password=?,failures=0,locked_until=0 WHERE id=?",
                (hashed, row["id"]),
            )
            con.execute("DELETE FROM sessions WHERE user_id=?", (row["id"],))
            store.audit(con, row["id"], "password_reset", {})
        print("Password reset; existing sessions were revoked.")
except FinanceError as exc:
    print(str(exc))
    sys.exit(1)
