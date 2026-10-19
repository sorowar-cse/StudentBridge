"""Curated university retrieval and transparent budget scenarios."""

from decimal import Decimal, localcontext
from pathlib import Path
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .money import FinanceError, decimal, rounded, currency, minor

DATA = Path(__file__).resolve().parent.parent / "data"


class UniversityCatalog:
    def __init__(self):
        self.records = json.loads((DATA / "universities.json").read_text(encoding="utf-8"))[
            "records"
        ]
        self.by_id = {r["id"]: r for r in self.records}
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode")
        self.matrix = self.vectorizer.fit_transform(
            [
                " ".join(
                    str(r[k])
                    for k in (
                        "university",
                        "abbr",
                        "city",
                        "country",
                        "programme",
                        "level",
                        "mode",
                        "language",
                        "student_type",
                    )
                )
                for r in self.records
            ]
        )

    def search(self, query, limit=4):
        scores = cosine_similarity(self.vectorizer.transform([str(query)]), self.matrix)[0]
        ranked = sorted(zip(scores, self.records), key=lambda pair: pair[0], reverse=True)
        return [{"score": round(float(s), 4), **r} for s, r in ranked[:limit] if s > 0]

    def get(self, record_id):
        if record_id not in self.by_id:
            raise FinanceError("Programme reference not found.")
        return self.by_id[record_id]


def budget_scenario(
    *,
    code,
    tuition,
    fee_period,
    tuition_periods,
    months,
    living,
    one_off="0",
    tax_percent="0",
    buffer_percent="10",
    savings="0",
    monthly_income="0",
    confirmed_funding="0",
):
    code = currency(code)
    if fee_period not in {"programme", "year", "semester", "trimester", "invoice"}:
        raise FinanceError("Confirm the tuition fee period before calculating.")
    if not isinstance(months, int) or not 1 <= months <= 96:
        raise FinanceError("Planning horizon must be 1–96 months.")
    if not isinstance(tuition_periods, int) or not 1 <= tuition_periods <= 24:
        raise FinanceError("Use 1–24 tuition periods.")
    if fee_period in {"programme", "invoice"} and tuition_periods != 1:
        raise FinanceError("A programme total or invoice must be counted once.")
    if not living or set(living) != {"rent", "food", "transport", "utilities", "other"}:
        raise FinanceError("Enter all five monthly expense categories.")
    for amount in [tuition, *living.values(), one_off, savings, monthly_income, confirmed_funding]:
        minor(amount, code)
    tax, buffer = decimal(tax_percent), decimal(buffer_percent)
    if tax > 100 or buffer > 100:
        raise FinanceError("Tax and buffer must be between 0% and 100%.")
    with localcontext() as ctx:
        ctx.prec = 40
        monthly = sum((decimal(v) for v in living.values()), Decimal(0))
        fee = decimal(tuition) * tuition_periods
        tax_amount = fee * tax / 100
        costs_before_buffer = fee + tax_amount + monthly * months + decimal(one_off)
        contingency = costs_before_buffer * buffer / 100
        total = costs_before_buffer + contingency
        resources = decimal(savings) + decimal(monthly_income) * months + decimal(confirmed_funding)
        gap = max(Decimal(0), total - resources)
        result = {
            "currency": code,
            "months": months,
            "fee_period": fee_period,
            "tuition_periods": tuition_periods,
            "monthly_living": monthly,
            "tuition": fee,
            "tax_assumption": tax_amount,
            "living_total": monthly * months,
            "one_off": decimal(one_off),
            "contingency": contingency,
            "total": total,
            "resources": resources,
            "funding_gap": gap,
            "extra_monthly_saving": gap / months,
        }
        for key, value in list(result.items()):
            if isinstance(value, Decimal):
                if value > Decimal("1000000000000"):
                    raise FinanceError("Scenario total exceeds the supported range.")
                result[key] = format(rounded(value, code), "f")
    result["assumptions"] = [
        "Living costs and tax basis are user-editable assumptions.",
        "Only confirmed funding is included; no scholarship or admission is assumed.",
        "Programme extension, inflation and employment restrictions are not inferred.",
    ]
    return result


def due_plan(amount, savings, months, code):
    if not isinstance(months, int) or not 1 <= months <= 60:
        raise FinanceError("Months until payment must be between 1 and 60.")
    minor(amount, code)
    minor(savings, code)
    gap = max(Decimal(0), decimal(amount) - decimal(savings))
    return {
        "currency": currency(code),
        "due": str(amount),
        "available": str(savings),
        "gap": format(rounded(gap, code), "f"),
        "save_per_month": format(rounded(gap / months, code), "f"),
        "months": months,
    }


def suggestions(result, record):
    items = [
        f"Confirm {record['programme']} and its {record['student_type']} fee classification against your offer.",
        f"Replace the illustrative living costs for {record['city']} with rent and expenses you actually expect.",
    ]
    if Decimal(result["funding_gap"]) > 0:
        items.append(
            f"This scenario has a {result['currency']} {result['funding_gap']} gap. To spread it over {result['months']} months, an additional {result['extra_monthly_saving']} per month is needed."
        )
    else:
        items.append(
            "Declared resources cover this scenario; keep the contingency available for changes."
        )
    items.append(
        "Check the university's official funding and instalment options. Enter a scholarship only after an award is confirmed."
    )
    return items
