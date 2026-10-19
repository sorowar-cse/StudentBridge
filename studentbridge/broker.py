"""Signed sandbox quotes and atomic, authenticated execution.

Only this service can move simulated balances. The AI agent has no reference to
it. A quote's primary key is the durable idempotency key, so refreshing a browser
or inventing a new client key cannot double-debit a completed quote.
"""

from datetime import datetime, timezone
from decimal import Decimal, localcontext
from dataclasses import asdict
import hmac
import json
import secrets
import time
from .money import FinanceError, currency, decimal, minor, major, rounded
from .store import canonical

PROVIDERS = {
    "Campus": {"fixed_usd": "0.50", "percent": "0.008", "spread": "0.003", "minutes": 60},
    "Value": {"fixed_usd": "0.20", "percent": "0.004", "spread": "0.006", "minutes": 240},
    "Swift": {"fixed_usd": "1.00", "percent": "0.012", "spread": "0.002", "minutes": 10},
}


class SandboxBroker:
    def __init__(self, store, fx, risk):
        self.store, self.fx, self.risk = store, fx, risk

    def _verified_receipt(self, row, user_id):
        try:
            receipt = json.loads(row["receipt"])
            mac = receipt.pop("ledger_mac")
            expected = self.store.state_mac("receipt", [user_id, receipt])
            if not hmac.compare_digest(mac, expected):
                raise FinanceError("Receipt integrity mismatch.")
            if (
                receipt["quote_id"] != row["quote_id"]
                or receipt["executed_at"] != row["executed"]
                or receipt["usd_equivalent"] != row["usd"]
                or row["user_id"] != user_id
            ):
                raise FinanceError("Transfer metadata integrity mismatch.")
            return {**receipt, "ledger_mac": mac}
        except (KeyError, ValueError, TypeError) as exc:
            if isinstance(exc, FinanceError):
                raise
            raise FinanceError("Receipt data is corrupt.") from exc

    def compare(self, amount, source, target):
        source, target = currency(source), currency(target)
        if source == target:
            raise FinanceError("Choose different source and destination currencies for remittance.")
        spend = decimal(amount, positive=True)
        minor(amount, source)
        rate = self.fx.rate(source, target)
        usd_rate = self.fx.rate(source, "USD")
        # Blended references for different dates must not silently become one quote.
        if source != "USD" and rate.mode == "live" and rate.as_of != usd_rate.as_of:
            raise FinanceError(
                "FX observations have different dates. A consistent quote is unavailable."
            )
        rows = []
        with localcontext() as ctx:
            ctx.prec = 40
            usd = spend * Decimal(usd_rate.rate)
            for name, p in PROVIDERS.items():
                fixed_source = Decimal(p["fixed_usd"]) / Decimal(usd_rate.rate)
                fee = rounded(fixed_source + spend * Decimal(p["percent"]), source)
                if fee >= spend:
                    continue
                effective = Decimal(rate.rate) * (1 - Decimal(p["spread"]))
                received = rounded((spend - fee) * effective, target)
                if received <= 0:
                    continue
                rows.append(
                    {
                        "provider": name,
                        "source": source,
                        "target": target,
                        "spend_minor": minor(amount, source),
                        "fee_minor": minor(fee, source),
                        "receive_minor": minor(received, target),
                        "usd": format(usd, ".8f"),
                        "effective_rate": format(effective, "f"),
                        "reference": asdict(rate),
                        "minutes": p["minutes"],
                        "provider_type": "Fictional sandbox provider",
                    }
                )
        if not rows:
            raise FinanceError("Amount is too small to cover the simulated fee.")
        return sorted(rows, key=lambda row: row["receive_minor"], reverse=True)

    def create_quote(
        self, token, amount, source, target, provider, *, new_recipient=False, now=None
    ):
        now = time.time() if now is None else now
        # Authentication precedes networking and quote calculation.
        user = self.store.principal(token)
        if user["role"] not in {"planner", "executor"}:
            raise FinanceError(
                "Viewer accounts can compare, but cannot create an executable quote."
            )
        options = self.compare(amount, source, target)
        selected = next((row for row in options if row["provider"] == provider), None)
        if selected is None:
            raise FinanceError("Provider is not available for this amount.")
        with self.store.connection(write=True) as con:
            user = self.store.principal(token, con)
            if not self.store.verify_audit(con)["valid"]:
                raise FinanceError("Audit integrity failed; quote creation is disabled.")
            recent = con.execute(
                "SELECT COUNT(*) FROM transfers WHERE user_id=? AND executed>?",
                (user["id"], now - 1800),
            ).fetchone()[0]
            hour = datetime.fromtimestamp(now, timezone.utc).hour
            assessment = self.risk.assess(selected["usd"], hour, new_recipient, recent)
            payload = {
                **selected,
                "id": secrets.token_hex(16),
                "user_id": user["id"],
                "created": now,
                "expires": now + 180,
                "risk": assessment,
                "new_recipient": bool(new_recipient),
                "scope": "sandbox_transfer_v1",
            }
            signature = self.store.sign(payload)
            con.execute(
                "INSERT INTO quotes VALUES (?,?,?,?,?)",
                (payload["id"], user["id"], canonical(payload), signature, payload["expires"]),
            )
            self.store.audit(
                con,
                user["id"],
                "quote_created",
                {"id": payload["id"], "risk": assessment, "mode": self.fx.mode},
            )
            return payload

    def execute(self, token, quote_id, confirmation, *, approved=False, now=None):
        try:
            return self._execute(token, quote_id, confirmation, approved=approved, now=now)
        except FinanceError as exc:
            # Record denials after the failed transaction has rolled back.
            try:
                user = self.store.principal(token)
                with self.store.connection(write=True) as con:
                    if self.store.verify_audit(con)["valid"]:
                        self.store.audit(
                            con,
                            user["id"],
                            "execution_denied",
                            {"quote_id": str(quote_id)[:32], "reason": str(exc)},
                        )
            except FinanceError:
                pass
            raise

    def _execute(self, token, quote_id, confirmation, *, approved=False, now=None):
        now = time.time() if now is None else now
        with self.store.connection(write=True) as con:
            user = self.store.principal(token, con)
            if user["role"] != "executor":
                raise FinanceError("This account cannot execute sandbox transfers.")
            if not self.store.verify_audit(con)["valid"]:
                raise FinanceError("Audit integrity failed; execution is disabled.")
            row = con.execute(
                "SELECT * FROM quotes WHERE id=? AND user_id=?", (str(quote_id), user["id"])
            ).fetchone()
            if row is None:
                raise FinanceError("Quote does not belong to this session's account.")
            try:
                q = json.loads(row["payload"])
            except ValueError as exc:
                raise FinanceError("Quote data is corrupt.") from exc
            if not hmac.compare_digest(self.store.sign(q), row["signature"]):
                raise FinanceError("Quote signature mismatch.")
            if (
                q["user_id"] != user["id"]
                or q["id"] != quote_id
                or q["scope"] != "sandbox_transfer_v1"
            ):
                raise FinanceError("Quote capability mismatch.")
            existing = con.execute(
                "SELECT * FROM transfers WHERE quote_id=?", (quote_id,)
            ).fetchone()
            if existing:
                return {**self._verified_receipt(existing, user["id"]), "replayed": True}
            if now >= q["expires"] or q["expires"] != row["expires"]:
                raise FinanceError("Quote expired. Generate a fresh quote.")
            if not approved or not hmac.compare_digest(str(confirmation).strip(), quote_id[-6:]):
                raise FinanceError(
                    "Review the quote, tick approval and enter its final six characters."
                )
            if Decimal(q["usd"]) > Decimal("2000"):
                raise FinanceError("Per-transfer sandbox limit of USD 2,000 equivalent reached.")
            if q["risk"]["blocked"]:
                raise FinanceError(
                    "Risk gate requires review. Try a smaller amount; no override is available."
                )
            history = [
                self._verified_receipt(r, user["id"])
                for r in con.execute("SELECT * FROM transfers WHERE user_id=?", (user["id"],))
            ]
            recent = sum(r["executed_at"] > now - 1800 for r in history)
            if recent >= 5:
                raise FinanceError("Transfer frequency limit reached.")
            midnight = now - (now % 86400)
            daily = sum(
                (Decimal(r["usd_equivalent"]) for r in history if r["executed_at"] >= midnight),
                Decimal(0),
            )
            if daily + Decimal(q["usd"]) > Decimal("5000"):
                raise FinanceError("Daily sandbox limit of USD 5,000 equivalent reached.")
            source_balance = self.store.balance(con, user["id"], q["source"])
            target_balance = self.store.balance(con, user["id"], q["target"])
            if source_balance < q["spend_minor"]:
                raise FinanceError(
                    "Insufficient sandbox balance. Add simulated funds in the Wallet page."
                )
            self.store.set_balance(con, user["id"], q["source"], source_balance - q["spend_minor"])
            self.store.set_balance(
                con, user["id"], q["target"], target_balance + q["receive_minor"]
            )
            receipt = {
                "quote_id": quote_id,
                "source": q["source"],
                "target": q["target"],
                "spent": major(q["spend_minor"], q["source"]),
                "fee_included": major(q["fee_minor"], q["source"]),
                "received": major(q["receive_minor"], q["target"]),
                "provider": q["provider"],
                "fx_mode": q["reference"]["mode"],
                "executed_at": now,
                "usd_equivalent": q["usd"],
                "status": "Sandbox completed — no real money moved",
                "replayed": False,
            }
            receipt["ledger_mac"] = self.store.state_mac("receipt", [user["id"], receipt])
            con.execute(
                "INSERT INTO transfers VALUES (?,?,?,?,?)",
                (quote_id, user["id"], canonical(receipt), now, q["usd"]),
            )
            self.store.audit(con, user["id"], "sandbox_transfer_completed", receipt)
            return receipt
