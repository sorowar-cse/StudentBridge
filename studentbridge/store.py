"""Local SQLite storage, password authentication, encrypted profiles and audit MACs.

The local key is a trust boundary: someone controlling this OS account can read it.
This module does not claim to protect against a compromised host or rollback of
both the database and its key. A hosted version needs a managed secret store.
"""

from contextlib import contextmanager
from pathlib import Path
import hashlib
import hmac
import json
import re
import secrets
import sqlite3
import time
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .money import FinanceError, minor


def canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class Store:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        try:
            self.directory.chmod(0o700)
        except OSError:
            pass  # On Windows, restrict this folder through the user account's ACL.
        self.key_path = self.directory / "server.key"
        if not self.key_path.exists():
            try:
                with self.key_path.open("xb") as handle:
                    handle.write(secrets.token_bytes(32))
                self.key_path.chmod(0o600)
            except FileExistsError:
                pass
        self.key = self.key_path.read_bytes()
        if len(self.key) != 32:
            raise FinanceError("Server key is invalid. Restore the matching runtime backup.")
        # Domain separation avoids using one raw key for unrelated HMAC/AES purposes.
        self.sign_key = hmac.new(self.key, b"quote-signing-v1", hashlib.sha256).digest()
        self.audit_key = hmac.new(self.key, b"audit-v1", hashlib.sha256).digest()
        self.state_key = hmac.new(self.key, b"ledger-state-v1", hashlib.sha256).digest()
        self.aes = AESGCM(hmac.new(self.key, b"profile-encryption-v1", hashlib.sha256).digest())
        self.passwords = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2)
        self.db = self.directory / "studentbridge.sqlite3"
        with self.connection() as con:
            con.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('viewer','planner','executor')),
                failures INTEGER DEFAULT 0, locked_until REAL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY, user_id TEXT,
                expires REAL NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id));
            CREATE TABLE IF NOT EXISTS wallets (user_id TEXT, currency TEXT, balance INTEGER NOT NULL, mac TEXT NOT NULL,
                PRIMARY KEY(user_id,currency), CHECK(balance >= 0));
            CREATE TABLE IF NOT EXISTS profiles (user_id TEXT PRIMARY KEY, encrypted TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS student_profiles (user_id TEXT PRIMARY KEY, encrypted TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS ai_requests (user_id TEXT NOT NULL, stamp REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS quotes (id TEXT PRIMARY KEY, user_id TEXT NOT NULL,
                payload TEXT NOT NULL, signature TEXT NOT NULL, expires REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS transfers (quote_id TEXT PRIMARY KEY, user_id TEXT,
                receipt TEXT NOT NULL, executed REAL NOT NULL, usd TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS audit (seq INTEGER PRIMARY KEY, user_id TEXT NOT NULL,
                event TEXT NOT NULL, stamp REAL NOT NULL, encrypted TEXT NOT NULL,
                previous TEXT NOT NULL, digest TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS metadata (name TEXT PRIMARY KEY, value TEXT NOT NULL);
            """)
            if not con.execute("SELECT 1 FROM metadata WHERE name='audit_head'").fetchone():
                self._head(con, 0, "0" * 64)
        try:
            self.db.chmod(0o600)
        except OSError:
            pass

    @contextmanager
    def connection(self, *, write=False):
        con = sqlite3.connect(self.db, timeout=15, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA busy_timeout=15000")
        try:
            con.execute("BEGIN IMMEDIATE" if write else "BEGIN")
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def encrypt(self, value, associated: str) -> str:
        nonce = secrets.token_bytes(12)
        ciphertext = self.aes.encrypt(nonce, canonical(value).encode(), associated.encode())
        return (nonce + ciphertext).hex()

    def decrypt(self, value: str, associated: str):
        payload = bytes.fromhex(value)
        return json.loads(self.aes.decrypt(payload[:12], payload[12:], associated.encode()))

    def sign(self, value) -> str:
        return hmac.new(self.sign_key, canonical(value).encode(), hashlib.sha256).hexdigest()

    def state_mac(self, scope, value):
        return hmac.new(
            self.state_key, canonical([scope, value]).encode(), hashlib.sha256
        ).hexdigest()

    def balance(self, con, user_id, code):
        row = con.execute(
            "SELECT * FROM wallets WHERE user_id=? AND currency=?", (user_id, code)
        ).fetchone()
        if not row:
            return 0
        expected = self.state_mac("wallet", [user_id, code, row["balance"]])
        if not hmac.compare_digest(expected, row["mac"]):
            raise FinanceError("Wallet integrity mismatch; balance changes are disabled.")
        return row["balance"]

    def set_balance(self, con, user_id, code, value):
        if not isinstance(value, int) or not 0 <= value <= 9_000_000_000_000_000_000:
            raise FinanceError("Sandbox balance exceeds its storage limit.")
        mac = self.state_mac("wallet", [user_id, code, value])
        con.execute(
            "INSERT INTO wallets VALUES (?,?,?,?) ON CONFLICT(user_id,currency) DO UPDATE SET balance=excluded.balance,mac=excluded.mac",
            (user_id, code, value, mac),
        )

    def _head(self, con, seq, digest):
        head = {"seq": seq, "digest": digest}
        head["mac"] = hmac.new(self.audit_key, canonical(head).encode(), hashlib.sha256).hexdigest()
        con.execute("INSERT OR REPLACE INTO metadata VALUES ('audit_head',?)", (canonical(head),))

    def audit(self, con, user_id, event, payload):
        old = con.execute("SELECT seq,digest FROM audit ORDER BY seq DESC LIMIT 1").fetchone()
        seq, previous = (old["seq"] + 1, old["digest"]) if old else (1, "0" * 64)
        stamp = time.time()
        encrypted = self.encrypt(payload, f"audit:{seq}:{user_id}:{event}")
        body = [seq, user_id, event, stamp, encrypted, previous]
        digest = hmac.new(self.audit_key, canonical(body).encode(), hashlib.sha256).hexdigest()
        con.execute("INSERT INTO audit VALUES (?,?,?,?,?,?,?)", (*body, digest))
        self._head(con, seq, digest)

    def verify_audit(self, con=None):
        if con is None:
            with self.connection() as active:
                return self.verify_audit(active)
        previous, count = "0" * 64, 0
        for row in con.execute("SELECT * FROM audit ORDER BY seq"):
            count += 1
            body = [row[k] for k in ("seq", "user_id", "event", "stamp", "encrypted", "previous")]
            expected = hmac.new(
                self.audit_key, canonical(body).encode(), hashlib.sha256
            ).hexdigest()
            if (
                row["seq"] != count
                or row["previous"] != previous
                or not hmac.compare_digest(expected, row["digest"])
            ):
                return {"valid": False, "rows": count, "reason": "Audit chain mismatch"}
            previous = row["digest"]
        stored = con.execute("SELECT value FROM metadata WHERE name='audit_head'").fetchone()
        if not stored:
            return {"valid": False, "rows": count, "reason": "Audit head missing"}
        try:
            head = json.loads(stored["value"])
            expected = hmac.new(
                self.audit_key,
                canonical({"seq": head["seq"], "digest": head["digest"]}).encode(),
                hashlib.sha256,
            ).hexdigest()
            valid = (
                head["seq"] == count
                and head["digest"] == previous
                and hmac.compare_digest(head["mac"], expected)
            )
        except (ValueError, KeyError, TypeError):
            valid = False
        return {
            "valid": valid,
            "rows": count,
            "head": previous,
            "reason": "Verified against local signed head" if valid else "Audit head mismatch",
        }

    def has_users(self):
        with self.connection() as con:
            return con.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0

    def create_user(self, username, password, role="executor", *, first_only=False):
        username = str(username).lower().strip()
        if not re.fullmatch(r"[a-z0-9_-]{3,32}", username):
            raise FinanceError("Username: 3–32 letters, numbers, underscores or hyphens.")
        if len(password) < 12 or len(password) > 128:
            raise FinanceError("Use a password of 12–128 characters.")
        if role not in {"viewer", "planner", "executor"}:
            raise FinanceError("Unknown role.")
        user_id = secrets.token_hex(16)
        encoded = self.passwords.hash(password)
        try:
            with self.connection(write=True) as con:
                if first_only and con.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
                    raise FinanceError("Initial setup is already complete. Sign in.")
                con.execute(
                    "INSERT INTO users(id,username,password,role) VALUES (?,?,?,?)",
                    (user_id, username, encoded, role),
                )
                self.audit(con, user_id, "account_created", {"role": role})
        except sqlite3.IntegrityError as exc:
            raise FinanceError("Username is already in use.") from exc
        return user_id

    def login(self, username, password, *, now=None):
        now = time.time() if now is None else now
        with self.connection(write=True) as con:
            row = con.execute(
                "SELECT * FROM users WHERE username=?", (str(username).lower().strip(),)
            ).fetchone()
            valid = False
            if row and row["locked_until"] > now:
                return None
            try:
                if row:
                    valid = self.passwords.verify(row["password"], password)
            except (VerificationError, ValueError):
                pass
            if not valid:
                if row:
                    failures = row["failures"] + 1
                    con.execute(
                        "UPDATE users SET failures=?,locked_until=? WHERE id=?",
                        (
                            0 if failures >= 5 else failures,
                            now + 300 if failures >= 5 else 0,
                            row["id"],
                        ),
                    )
                return None
            con.execute("UPDATE users SET failures=0,locked_until=0 WHERE id=?", (row["id"],))
            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            con.execute("DELETE FROM sessions WHERE expires < ?", (now,))
            con.execute("INSERT INTO sessions VALUES (?,?,?)", (token_hash, row["id"], now + 1800))
            self.audit(con, row["id"], "login", {})
            return token

    def principal(self, token, con=None, *, now=None):
        if not isinstance(token, str) or len(token) > 200:
            raise FinanceError("Please sign in.")
        if con is None:
            with self.connection() as active:
                return self.principal(token, active, now=now)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        row = con.execute(
            "SELECT u.id,u.username,u.role FROM sessions s JOIN users u ON s.user_id=u.id WHERE s.token_hash=? AND s.expires>?",
            (token_hash, time.time() if now is None else now),
        ).fetchone()
        if not row:
            raise FinanceError("Session expired. Please sign in again.")
        return dict(row)

    def logout(self, token):
        with self.connection(write=True) as con:
            con.execute(
                "DELETE FROM sessions WHERE token_hash=?",
                (hashlib.sha256(token.encode()).hexdigest(),),
            )

    def wallet(self, token):
        with self.connection() as con:
            user = self.principal(token, con)
            return {
                r["currency"]: self.balance(con, user["id"], r["currency"])
                for r in con.execute("SELECT * FROM wallets WHERE user_id=?", (user["id"],))
            }

    def seed_wallet(self, token, code, amount):
        """An explicit sandbox-only top-up, never a bank deposit."""
        value = minor(amount, code)
        with self.connection(write=True) as con:
            user = self.principal(token, con)
            if user["role"] != "executor":
                raise FinanceError("Only an executor account can top up a sandbox wallet.")
            if not self.verify_audit(con)["valid"]:
                raise FinanceError("Audit integrity failed. Restore the runtime backup.")
            self.set_balance(con, user["id"], code, self.balance(con, user["id"], code) + value)
            self.audit(con, user["id"], "sandbox_top_up", {"currency": code, "minor": value})

    def save_profile(self, token, value):
        with self.connection(write=True) as con:
            user = self.principal(token, con)
            payload = self.encrypt(value, f"profile:{user['id']}")
            con.execute("INSERT OR REPLACE INTO profiles VALUES (?,?)", (user["id"], payload))
            self.audit(con, user["id"], "profile_saved", {"fields": sorted(value)})

    def profile(self, token):
        with self.connection() as con:
            user = self.principal(token, con)
            row = con.execute(
                "SELECT encrypted FROM profiles WHERE user_id=?", (user["id"],)
            ).fetchone()
            return self.decrypt(row["encrypted"], f"profile:{user['id']}") if row else {}

    def export_audit(self, token):
        with self.connection() as con:
            user = self.principal(token, con)
            rows = []
            for r in con.execute("SELECT * FROM audit WHERE user_id=? ORDER BY seq", (user["id"],)):
                rows.append(
                    {
                        "seq": r["seq"],
                        "event": r["event"],
                        "stamp": r["stamp"],
                        "digest": r["digest"],
                        "details": self.decrypt(
                            r["encrypted"], f"audit:{r['seq']}:{user['id']}:{r['event']}"
                        ),
                    }
                )
            return {
                "global_integrity": self.verify_audit(con),
                "own_events": rows,
                "note": "Keep the head externally to detect later rollback. Export contains financial data.",
            }

    def save_student_profile(self, token, value):
        with self.connection(write=True) as con:
            user = self.principal(token, con)
            encrypted = self.encrypt(value, f"student:{user['id']}")
            con.execute(
                "INSERT OR REPLACE INTO student_profiles VALUES (?,?)", (user["id"], encrypted)
            )
            self.audit(con, user["id"], "student_profile_saved", {})

    def student_profile(self, token):
        with self.connection() as con:
            user = self.principal(token, con)
            row = con.execute(
                "SELECT encrypted FROM student_profiles WHERE user_id=?", (user["id"],)
            ).fetchone()
            return self.decrypt(row["encrypted"], f"student:{user['id']}") if row else {}

    def clear_personal_data(self, token):
        with self.connection(write=True) as con:
            user = self.principal(token, con)
            con.execute("DELETE FROM student_profiles WHERE user_id=?", (user["id"],))
            con.execute("DELETE FROM profiles WHERE user_id=?", (user["id"],))
            self.audit(con, user["id"], "personal_profiles_deleted", {})

    def reserve_ai(self, token):
        now = time.time()
        with self.connection(write=True) as con:
            user = self.principal(token, con)
            day = now - now % 86400
            own = con.execute(
                "SELECT count(*) FROM ai_requests WHERE user_id=? AND stamp>=?", (user["id"], day)
            ).fetchone()[0]
            total = con.execute(
                "SELECT count(*) FROM ai_requests WHERE stamp>=?", (day,)
            ).fetchone()[0]
            recent = con.execute(
                "SELECT count(*) FROM ai_requests WHERE stamp>?", (now - 60,)
            ).fetchone()[0]
            if own >= 20 or total >= 100 or recent >= 3:
                raise FinanceError(
                    "StudentBridge AI allowance reached. Wait or use the built-in calculations."
                )
            con.execute("INSERT INTO ai_requests VALUES (?,?)", (user["id"], now))
            con.execute("DELETE FROM ai_requests WHERE stamp<?", (now - 8 * 86400,))
