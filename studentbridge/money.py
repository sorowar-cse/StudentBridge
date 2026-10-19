"""Decimal arithmetic and currency-specific rounding shared by every tool.

Keep amounts as strings at boundaries and integers in the wallet ledger.
Binary floats are acceptable in charts, never in a posted money calculation.
"""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
import re
from babel.numbers import get_currency_precision, get_currency_name

MAX_AMOUNT = Decimal("1000000000000")
ALIASES = {"RMB": "CNY", "YUAN": "CNY", "人民币": "CNY", "TAKA": "BDT", "RINGGIT": "MYR"}


class FinanceError(ValueError):
    """An actionable validation error safe to display to the user."""


def currency(value: str) -> str:
    code = ALIASES.get(str(value).strip().upper(), str(value).strip().upper())
    if not re.fullmatch(r"[A-Z]{3}", code):
        raise FinanceError("Use an ISO currency code, such as BDT, MYR or CNY (RMB).")
    return code


def decimal(value, *, positive=False) -> Decimal:
    # Disallow scientific notation, separators and excessive input length.
    text = str(value).strip()
    if len(text) > 32 or not re.fullmatch(r"-?\d+(\.\d{1,12})?", text):
        raise FinanceError("Enter a plain number with at most 12 decimal places.")
    try:
        result = Decimal(text)
    except InvalidOperation as exc:
        raise FinanceError("Invalid amount.") from exc
    if not result.is_finite() or abs(result) > MAX_AMOUNT:
        raise FinanceError("Amount is outside the supported range.")
    if result < 0 or (positive and result == 0):
        raise FinanceError("Amount must be positive." if positive else "Amount cannot be negative.")
    return result


def quantum(code: str) -> Decimal:
    return Decimal(1).scaleb(-get_currency_precision(currency(code)))


def rate_decimal(value) -> Decimal:
    """Rates need more precision than user-entered money and may use exponents."""
    text = str(value).strip()
    if len(text) > 80 or not re.fullmatch(r"\d+(\.\d+)?([eE][+-]?\d{1,3})?", text):
        raise FinanceError("Invalid exchange-rate representation.")
    value = Decimal(text)
    if not value.is_finite() or value <= 0 or not -18 <= value.adjusted() <= 12:
        raise FinanceError("Exchange rate is outside the supported range.")
    return value


def rounded(value: Decimal, code: str) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = 40
        return value.quantize(quantum(code), rounding=ROUND_HALF_UP)


def minor(value, code: str, *, exact=True) -> int:
    amount = decimal(value)
    result = rounded(amount, code)
    if exact and result != amount:
        raise FinanceError(f"{code} accepts {get_currency_precision(code)} decimal places.")
    return int(result / quantum(code))


def major(value: int, code: str) -> str:
    return format(Decimal(value) * quantum(code), "f")


def convert_amount(amount, rate, target: str) -> str:
    with localcontext() as ctx:
        ctx.prec = 40
        value = decimal(amount) * rate_decimal(rate)
        if value > MAX_AMOUNT:
            raise FinanceError("Converted amount is too large.")
        return format(rounded(value, target), "f")


def currency_label(code: str) -> str:
    if code == "CNH":
        return "CNH — Offshore yuan (separate from CNY/RMB)"
    label = get_currency_name(code, locale="en")
    return f"{code} — {label}" + (" (RMB)" if code == "CNY" else "")
