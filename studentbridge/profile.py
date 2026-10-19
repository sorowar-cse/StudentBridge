"""Student-owned inputs and deterministic cash-flow forecasts.

There is no learned prediction of future FX or university fees. Future amounts
are scenarios using declared billing dates, costs and explicit stress inputs.
Dates are calendar-month buckets, with due dates retained in the detailed rows.
"""

from calendar import monthrange
from datetime import date, datetime, timezone
from decimal import Decimal, localcontext
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .money import FinanceError, currency, decimal, minor, rounded


class Amount(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount: str = Field(max_length=32)
    currency: str = Field(max_length=3)

    @field_validator("currency")
    @classmethod
    def code(cls, value):
        return currency(value)

    @model_validator(mode="after")
    def valid_money(self):
        minor(self.amount, self.currency)
        return self


class StudentProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: Literal[1] = 1
    university: str = Field(min_length=2, max_length=140)
    campus: str = Field(default="", max_length=100)
    department: str = Field(min_length=1, max_length=140)
    programme: str = Field(min_length=1, max_length=140)
    study_mode: str = Field(default="Research", max_length=50)
    city: str = Field(min_length=1, max_length=100)
    country: str = Field(min_length=1, max_length=80)
    start_date: date
    months: int = Field(default=12, ge=1, le=96)
    budget_currency: str = Field(default="MYR", max_length=3)
    tuition: Amount
    fee_period: Literal["semester", "year", "trimester", "programme", "invoice"]
    billing_interval_months: int = Field(ge=0, le=24)
    next_tuition_date: date
    living: dict[str, Amount]
    one_off: Amount
    savings: Amount
    monthly_income: Amount
    confirmed_funding: Amount
    buffer_percent: str = "10"
    annual_cost_growth_percent: str = "0"
    fx_stress_percent: str = "0"
    source_note: str = Field(
        default="User provided; verify against current invoice", max_length=500
    )
    confirmed: Literal[True]
    updated_at: str = ""

    @field_validator("budget_currency")
    @classmethod
    def valid_currency(cls, value):
        return currency(value)

    @model_validator(mode="after")
    def consistency(self):
        if set(self.living) != {"rent", "food", "transport", "utilities", "other"}:
            raise ValueError("Enter all five monthly living categories.")
        once = self.fee_period in {"programme", "invoice"}
        if once != (self.billing_interval_months == 0):
            raise ValueError(
                "A total/invoice is counted once; recurring tuition needs a billing interval."
            )
        if self.next_tuition_date < self.start_date:
            raise ValueError(
                "Next unpaid tuition date must be on or after the planning start date."
            )
        for name in ("buffer_percent", "annual_cost_growth_percent", "fx_stress_percent"):
            if decimal(getattr(self, name)) > 100:
                raise ValueError("Scenario percentages must be between 0 and 100.")
        if self.start_date.year < 2020 or self.start_date.year > 2090:
            raise ValueError("Choose a supported planning year, 2020–2090.")
        if self.next_tuition_date.year > 2100:
            raise ValueError("Tuition due date is outside the supported range.")
        return self


def validated_profile(value):
    try:
        result = StudentProfile.model_validate(value)
        result.updated_at = datetime.now(timezone.utc).isoformat()
        return result.model_dump(mode="json")
    except ValueError as exc:
        # Pydantic messages include input values; show field messages without echoing secrets.
        messages = [e["msg"] for e in exc.errors()] if hasattr(exc, "errors") else [str(exc)]
        raise FinanceError("Profile: " + "; ".join(messages[:3])) from None


def add_months(day, count):
    month = day.year * 12 + day.month - 1 + count
    year, month0 = divmod(month, 12)
    return date(year, month0 + 1, min(day.day, monthrange(year, month0 + 1)[1]))


def forecast(value, fx):
    p = StudentProfile.model_validate(value)
    code = p.budget_currency
    refs = {}

    def converted(item, *, cost=False):
        if decimal(item.amount) == 0:
            return Decimal(0)  # A waived/zero item needs no external quote.
        if item.currency == code:
            return decimal(item.amount)
        if item.currency not in refs:
            refs[item.currency] = fx.rate(item.currency, code)
        amount = decimal(item.amount) * Decimal(refs[item.currency].rate)
        # Stress foreign outgoings only; uncertain future income is not inflated.
        if cost:
            amount *= 1 + decimal(p.fx_stress_percent) / 100
        return amount

    with localcontext() as ctx:
        ctx.prec = 40
        living = sum((converted(item, cost=True) for item in p.living.values()), Decimal(0))
        tuition = converted(p.tuition, cost=True)
        one_off = converted(p.one_off, cost=True)
        income = converted(p.monthly_income)
        balance = rounded(converted(p.savings) + converted(p.confirmed_funding), code)
        initial_resources = balance
        total = Decimal(0)
        rows, bill_dates = [], []
        end = add_months(p.start_date, p.months)
        due = p.next_tuition_date
        index = 0
        while due < end:
            bill_dates.append(due)
            if p.billing_interval_months == 0:
                break
            index += 1
            # Recalculate from the original date: Jan 31 -> Feb 28 -> Mar 31.
            due = add_months(p.next_tuition_date, index * p.billing_interval_months)
        for i in range(p.months):
            start, stop = add_months(p.start_date, i), add_months(p.start_date, i + 1)
            monthly_living = rounded(
                living * (1 + decimal(p.annual_cost_growth_percent) / 1200) ** i, code
            )
            bills = [d for d in bill_dates if start <= d < stop]
            fee = rounded(tuition * len(bills), code)
            extras = rounded(one_off if i == 0 else Decimal(0), code)
            subtotal = monthly_living + fee + extras
            buffer = rounded(subtotal * decimal(p.buffer_percent) / 100, code)
            # Round each posted month once; aggregate the displayed month amounts.
            costs = rounded(subtotal + buffer, code)
            paid_income = rounded(income, code)
            total += costs
            balance += paid_income - costs
            if abs(total) > Decimal("1000000000000") or abs(balance) > Decimal("1000000000000"):
                raise FinanceError("Forecast exceeds the supported range.")
            rows.append(
                {
                    "month": start.isoformat(),
                    "tuition_due_dates": ", ".join(d.isoformat() for d in bills),
                    "living": format(rounded(monthly_living, code), "f"),
                    "tuition": format(rounded(fee, code), "f"),
                    "one_off": format(rounded(extras, code), "f"),
                    "buffer": format(rounded(buffer, code), "f"),
                    "cost": format(costs, "f"),
                    "income": format(paid_income, "f"),
                    "closing_balance": format(rounded(balance, code), "f"),
                }
            )
        if fx.mode == "live" and len({r.as_of for r in refs.values()}) > 1:
            raise FinanceError(
                "FX observations have different dates. A consistent forecast is unavailable."
            )
        resources = rounded(initial_resources, code) + rounded(income, code) * p.months
        funding_gap = max(Decimal(0), total - resources)
        # A final surplus can hide an earlier tuition shortfall: report timing separately.
        timing_gap = max(Decimal(0), -min(Decimal(r["closing_balance"]) for r in rows))
        return {
            "currency": code,
            "months": p.months,
            "total": format(total, "f"),
            "resources": format(rounded(resources, code), "f"),
            "funding_gap": format(rounded(funding_gap, code), "f"),
            "upfront_timing_gap": format(rounded(timing_gap, code), "f"),
            "first_shortfall": next(
                (r["month"] for r in rows if Decimal(r["closing_balance"]) < 0), None
            ),
            "extra_monthly_saving": format(rounded(funding_gap / p.months, code), "f"),
            "monthly_living": format(rounded(living, code), "f"),
            "rows": rows,
            "references": [r.__dict__ for r in refs.values()],
            "created_at": datetime.now(timezone.utc).timestamp(),
            "source": "User-provided and confirmed inputs; not independently verified",
            "assumptions": [
                "Monthly income arrives before that month's bills; intra-month timing is not modeled.",
                "Cost growth is a user-entered nominal annual percentage / 12, compounded monthly on living costs only.",
                "Tuition uses declared unpaid due dates and actual billing interval; no future fee increases are inferred.",
                "Foreign expenses use today's available reference rate plus the selected stress; future rates are unknown.",
                "Funding is available at the beginning; buffer is a reserve, not a paid expense.",
            ],
        }
