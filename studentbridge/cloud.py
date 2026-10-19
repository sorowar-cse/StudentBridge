"""Supabase Auth/PostgREST adapter, scoped to one Streamlit session.

Only a publishable API key is accepted. Every database request also carries the
signed-in user's access token: using a service key here would bypass RLS.
Never cache this object with st.cache_resource and never log its session.
"""

from datetime import datetime, timezone
import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import time

from babel.numbers import get_currency_precision
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import requests

from .broker import SandboxBroker
from .money import FinanceError, currency, minor
from .store import Store, canonical


def configuration():
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_PUBLISHABLE_KEY", "").strip()
    master = os.getenv("STUDENTBRIDGE_MASTER_KEY", "").strip()
    if not re.fullmatch(r"https://[a-z0-9-]+\.supabase\.co", url):
        raise FinanceError("Set SUPABASE_URL to your https://PROJECT.supabase.co URL.")
    # New publishable keys are recommended; allow legacy anon keys, never a privileged JWT.
    if key.startswith("eyJ"):
        try:
            claims = json.loads(base64.urlsafe_b64decode(key.split(".")[1] + "=="))
            if claims.get("role") != "anon":
                raise ValueError("not anon")
        except (ValueError, IndexError):
            raise FinanceError(
                "Use a Supabase publishable key, never a service-role key."
            ) from None
    elif not key.startswith("sb_publishable_"):
        raise FinanceError("Set SUPABASE_PUBLISHABLE_KEY. Secret/service-role keys are rejected.")
    if not re.fullmatch(r"[0-9a-f]{64}", master):
        raise FinanceError("Run scripts/setup_local.py to generate the stable master key.")
    return url, key, bytes.fromhex(master)


class CloudStore(Store):
    """Implements the app's storage interface without touching a local database."""

    def __init__(self, session_state=None, http=None, clock=time.time):
        self.url, self.api_key, self.key = configuration()
        self.sign_key = hmac.new(self.key, b"quote-signing-v1", hashlib.sha256).digest()
        self.state_key = hmac.new(self.key, b"ledger-state-v1", hashlib.sha256).digest()
        self.aes = AESGCM(hmac.new(self.key, b"profile-encryption-v1", hashlib.sha256).digest())
        self.session = session_state if session_state is not None else {}
        self.http = http or requests.Session()
        self.clock = clock

    def _request(self, method, path, *, data=None, authenticated=True, params=None):
        headers = {"apikey": self.api_key, "Content-Type": "application/json"}
        if authenticated:
            token = self._access_token()
            headers["Authorization"] = "Bearer " + token
        try:
            r = self.http.request(
                method,
                self.url + path,
                headers=headers,
                json=data,
                params=params,
                timeout=(5, 25),
                allow_redirects=False,
            )
            if r.status_code in {401, 403}:
                raise FinanceError(
                    "Sign-in or permission check failed. Sign in again or contact the team."
                )
            if r.status_code == 429:
                raise FinanceError("Service request limit reached. Wait before trying again.")
            if not 200 <= r.status_code < 300:
                # Return only explicitly safe errors raised by our SQL, not provider bodies/tokens.
                try:
                    message = r.json().get("message", "")
                except (ValueError, AttributeError):
                    message = ""
                if isinstance(message, str) and message.startswith("SB:"):
                    raise FinanceError(message[3:][:220])
                raise FinanceError(
                    "Cloud request failed. Check project status, SQL setup and credentials."
                )
            if len(r.content) > 2_000_000:
                raise FinanceError("Cloud response exceeds the size limit.")
            return r.json() if r.content else None
        except requests.RequestException:
            raise FinanceError(
                "Cloud connection unavailable. Your data was not replaced locally."
            ) from None

    def _accept_session(self, result):
        if (
            not isinstance(result, dict)
            or not result.get("access_token")
            or not result.get("refresh_token")
        ):
            raise FinanceError("Sign-in failed. Ask the team to create your pilot account.")
        self.session["auth"] = {
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "expires_at": self.clock() + int(result.get("expires_in", 3600)),
        }

    def _access_token(self):
        auth = self.session.get("auth", {})
        if not auth or self.clock() >= self.session.get("absolute_expiry", 0):
            self.session.clear()
            raise FinanceError("Session expired. Please sign in again.")
        if self.clock() >= auth["expires_at"] - 60:
            result = self._request(
                "POST",
                "/auth/v1/token",
                authenticated=False,
                params={"grant_type": "refresh_token"},
                data={"refresh_token": auth["refresh_token"]},
            )
            self._accept_session(result)
        return self.session["auth"]["access_token"]

    def login(self, username, password, **_):
        email = str(username).strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) or not 1 <= len(password) <= 128:
            return None
        try:
            result = self._request(
                "POST",
                "/auth/v1/token",
                authenticated=False,
                params={"grant_type": "password"},
                data={"email": email, "password": password},
            )
            self._accept_session(result)
            self.session["absolute_expiry"] = self.clock() + 1800
            # Enrollment is limited by an atomic SQL lock and a developer-controlled cap.
            self.rpc("sb_enroll", {})
            return "supabase-session"  # Not a bearer token; actual tokens stay in session state.
        except FinanceError:
            self.session.clear()
            return None

    def principal(self, token, *_args, **_kwargs):
        if token != "supabase-session":
            raise FinanceError("Please sign in.")
        # Do not trust decoded JWT metadata or a client-submitted role.
        user = self._request("GET", "/auth/v1/user")
        rows = self._request("GET", "/rest/v1/sb_members", params={"select": "user_id,role"})
        row = next((r for r in rows if r["user_id"] == user["id"]), None)
        if row is None:
            raise FinanceError("Pilot membership unavailable. Contact the team.")
        return {"id": user["id"], "username": user["email"], "role": row["role"]}

    def logout(self, token):
        try:
            if self.session.get("auth"):
                self._request("POST", "/auth/v1/logout", params={"scope": "local"})
        finally:
            self.session.clear()

    def has_users(self):
        return True  # There is deliberately no public first-owner setup in cloud mode.

    def rpc(self, name, data):
        return self._request("POST", "/rest/v1/rpc/" + name, data=data)

    def wallet(self, token):
        self.principal(token)
        rows = self._request("GET", "/rest/v1/sb_wallets", params={"select": "currency,balance"})
        return {r["currency"]: int(r["balance"]) for r in rows}

    def seed_wallet(self, token, code, amount):
        self.principal(token)
        self.rpc("sb_top_up", {"p_currency": currency(code), "p_minor": minor(amount, code)})

    def _save_document(self, token, kind, value):
        user = self.principal(token)
        encrypted = self.encrypt(value, f"cloud:{kind}:{user['id']}")
        self.rpc("sb_save_document", {"p_kind": kind, "p_encrypted": encrypted})

    def _document(self, token, kind):
        user = self.principal(token)
        rows = self._request(
            "GET", "/rest/v1/sb_documents", params={"select": "encrypted", "kind": "eq." + kind}
        )
        if not rows:
            return {}
        try:
            return self.decrypt(rows[0]["encrypted"], f"cloud:{kind}:{user['id']}")
        except Exception:
            raise FinanceError(
                "Profile integrity check failed. Restore the matching master key/backup."
            ) from None

    def save_profile(self, token, value):
        self._save_document(token, "plan", value)

    def profile(self, token):
        return self._document(token, "plan")

    def save_student_profile(self, token, value):
        self._save_document(token, "student", value)

    def student_profile(self, token):
        return self._document(token, "student")

    def clear_personal_data(self, token):
        self.principal(token)
        return self.rpc("sb_clear_personal_data", {})

    def reserve_ai(self, token):
        self.principal(token)
        return self.rpc("sb_reserve_ai", {})

    def export_audit(self, token):
        self.principal(token)
        return self.rpc("sb_export_audit", {})

    def change_password(self, token, current_password, new_password):
        if not 12 <= len(new_password) <= 128:
            raise FinanceError("Use a password of 12–128 characters.")
        user = self.principal(token)
        # Reauthenticate in an isolated adapter; never replace the live user's session on failure.
        other = CloudStore(http=self.http)
        if not other.login(user["username"], current_password):
            raise FinanceError("Current password could not be verified.")
        try:
            self._request("PUT", "/auth/v1/user", data={"password": new_password})
        finally:
            other.logout("supabase-session")


class CloudBroker(SandboxBroker):
    """Python signs a bounded quote; PostgreSQL performs the atomic ledger commit."""

    def create_quote(
        self, token, amount, source, target, provider, *, new_recipient=False, now=None
    ):
        user = self.store.principal(token)
        if user["role"] not in {"planner", "executor"}:
            raise FinanceError("Viewer accounts cannot create executable quotes.")
        selected = next(
            (r for r in self.compare(amount, source, target) if r["provider"] == provider), None
        )
        if selected is None:
            raise FinanceError("Provider is unavailable for this amount.")
        recent = self.store.rpc("sb_recent_count", {})
        now = time.time() if now is None else now
        assessment = self.risk.assess(
            selected["usd"], datetime.fromtimestamp(now, timezone.utc).hour, new_recipient, recent
        )
        payload = {
            **selected,
            "id": secrets.token_hex(16),
            "user_id": user["id"],
            "created": now,
            "expires": now + 180,
            "risk": assessment,
            "new_recipient": bool(new_recipient),
            "scope": "sandbox_transfer_v1",
            "source_digits": get_currency_precision(selected["source"]),
            "target_digits": get_currency_precision(selected["target"]),
        }
        self.store.rpc(
            "sb_create_quote",
            {"p_payload": canonical(payload), "p_signature": self.store.sign(payload)},
        )
        return payload

    def execute(self, token, quote_id, confirmation, *, approved=False, now=None):
        self.store.principal(token)
        # Server time is authoritative in PostgreSQL; the client cannot choose it.
        return self.store.rpc(
            "sb_execute",
            {
                "p_quote_id": str(quote_id),
                "p_confirmation": str(confirmation).strip(),
                "p_approved": bool(approved),
            },
        )
