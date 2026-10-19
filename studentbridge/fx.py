"""Frankfurter v2 reference rates, with an explicit synthetic offline mode."""

from dataclasses import dataclass, asdict
from datetime import date, datetime, timezone
from decimal import Decimal, localcontext
from pathlib import Path
import json
import requests
from .money import FinanceError, currency, rate_decimal, convert_amount, minor
from babel.numbers import get_currency_name

DATA = Path(__file__).resolve().parent.parent / "data"


@dataclass(frozen=True)
class Rate:
    base: str
    quote: str
    rate: str
    as_of: str
    source: str
    mode: str
    fetched_at: str

    def validate(self, today=None):
        rate_decimal(self.rate)
        try:
            stamp = date.fromisoformat(self.as_of)
        except (ValueError, TypeError) as exc:
            raise FinanceError("FX observation has an invalid date.") from exc
        if self.mode == "live":
            age = ((today or date.today()) - stamp).days
            # Weekend/publication gaps are allowed, but stale observations are not hidden.
            if age < 0 or age > 10:
                raise FinanceError(f"Reference rate dated {self.as_of} is stale or in the future.")
        return self


class FXService:
    API = "https://api.frankfurter.dev/v2"

    def __init__(self, mode="demo", session=None):
        if mode not in {"demo", "live"}:
            raise FinanceError("Unknown FX mode.")
        self.mode = mode
        self.session = session or requests.Session()
        self.demo = json.loads((DATA / "demo_fx.json").read_text(encoding="utf-8"))

    def _get(self, path, params=None):
        # URLs are fixed by code; users and models cannot send the server to arbitrary URLs.
        try:
            response = self.session.get(
                self.API + path, params=params, timeout=(10, 20), allow_redirects=False
            )
            response.raise_for_status()
            if len(response.content) > 2_000_000:
                raise FinanceError("FX response exceeds the size limit.")
            return response.json(parse_float=Decimal)
        except (requests.RequestException, ValueError) as exc:
            raise FinanceError(
                "Live FX unavailable. Retry or review reference settings in Guide for User."
            ) from exc

    def currencies(self):
        if self.mode == "demo":
            return sorted(self.demo["per_usd"])
        data = self._get("/currencies")
        if not isinstance(data, list):
            raise FinanceError("Unexpected currency catalogue response.")
        # v2's default scope excludes legacy currencies. Pair availability is still checked.
        codes = {
            currency(row["iso_code"])
            for row in data
            if isinstance(row, dict) and row.get("iso_code")
        }
        if not codes:
            raise FinanceError("The provider returned no active currencies.")
        return sorted(codes)

    def rate(self, base: str, target: str) -> Rate:
        base, target = currency(base), currency(target)
        fetched = datetime.now(timezone.utc).isoformat()
        if base == target:
            if (get_currency_name(base, locale="en") == base and base != "CNH") or (
                self.mode == "demo" and base not in self.demo["per_usd"]
            ):
                raise FinanceError("Unknown or unavailable currency for identity conversion.")
            return Rate(
                base,
                target,
                "1",
                date.today().isoformat(),
                "Identity conversion",
                self.mode,
                fetched,
            )
        if self.mode == "demo":
            values = self.demo["per_usd"]
            if base not in values or target not in values:
                raise FinanceError("This pair is not in the synthetic demo. Try Live FX.")
            with localcontext() as ctx:
                ctx.prec = 32
                rate = Decimal(values[target]) / Decimal(values[base])
            return Rate(
                base,
                target,
                format(rate, "f"),
                self.demo["as_of"],
                "Synthetic teaching snapshot — not a market quote",
                "demo",
                fetched,
            )
        data = self._get(f"/rate/{base.lower()}/{target.lower()}")
        if not isinstance(data, dict) or not all(
            k in data for k in ("base", "quote", "date", "rate")
        ):
            raise FinanceError("The provider has no usable observation for this pair.")
        if currency(data["base"]) != base or currency(data["quote"]) != target:
            raise FinanceError("Currency mismatch in provider response.")
        return Rate(
            base,
            target,
            str(data["rate"]),
            data["date"],
            "Frankfurter v2, blended official reference rates",
            "live",
            fetched,
        ).validate()

    def convert(self, amount, base, target):
        base, target = currency(base), currency(target)
        minor(amount, base)  # Reject sub-minor units instead of silently changing the request.
        rate = self.rate(base, target)
        return {
            "amount": str(amount),
            "base": base,
            "target": target,
            "converted": convert_amount(amount, rate.rate, target),
            "reference": asdict(rate),
        }
