"""Generate 15 repeatable SYNTHETIC profile cases with independent expected totals.

Institution names are reference metadata. Every amount below is invented for
verification, not an official tuition fee, rent quote, or funding offer.
"""

from decimal import Decimal, ROUND_HALF_UP
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def generate():
    records = json.loads((ROOT / "data/universities.json").read_text())["records"]
    institutions = list({r["abbr"]: r for r in records}.values())
    cases = []
    for i in range(15):
        record = institutions[i % len(institutions)]
        code = record["currency"]
        months = [6, 12, 18][i % 3]
        once = i % 4 == 0
        tuition = 1000 + i * 100
        living = dict(
            zip(
                ["rent", "food", "transport", "utilities", "other"], [300 + i * 10, 200, 80, 50, 70]
            )
        )
        oneoff = i * 25
        buffer = 10 if i % 2 else 0
        savings = 2000 + i * 250
        income = 300 + i * 50
        funding = 1000 if i % 3 == 0 else 0

        def item(value):
            return {"amount": str(value), "currency": code}

        profile = dict(
            version=1,
            university=record["university"],
            campus="Synthetic test campus",
            department="Synthetic test department",
            programme="Synthetic verification programme",
            study_mode="Controlled test",
            city=record["city"],
            country=record["country"],
            start_date="2026-11-01",
            months=months,
            budget_currency=code,
            tuition=item(tuition),
            fee_period="invoice" if once else "semester",
            billing_interval_months=0 if once else 6,
            next_tuition_date="2026-11-01",
            living={k: item(v) for k, v in living.items()},
            one_off=item(oneoff),
            savings=item(savings),
            monthly_income=item(income),
            confirmed_funding=item(funding),
            buffer_percent=str(buffer),
            annual_cost_growth_percent="0",
            fx_stress_percent="0",
            source_note="SYNTHETIC TEST DATA: every amount is invented, not an official university fee.",
            confirmed=True,
        )
        # Independently sum exact monthly examples, without importing the app or FX.
        total = Decimal(0)
        for month in range(months):
            fee = tuition if (month == 0 or (not once and month % 6 == 0)) else 0
            base = Decimal(sum(living.values()) + fee + (oneoff if month == 0 else 0))
            reserve = (base * buffer / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            total += base + reserve
        resources = Decimal(savings + funding + income * months)
        cases.append(
            {
                "id": f"P{i + 1:02d}",
                "label": "Synthetic profile verification",
                "profile": profile,
                "expected_total": format(total.quantize(Decimal("0.01")), "f"),
                "expected_resources": format(resources.quantize(Decimal("0.01")), "f"),
                "expected_gap": format(
                    max(Decimal(0), total - resources).quantize(Decimal("0.01")), "f"
                ),
            }
        )
    return cases


if __name__ == "__main__":
    cases = generate()
    (ROOT / "data/profile_test_cases.json").write_text(
        json.dumps({"scope": __doc__, "cases": cases}, ensure_ascii=False, indent=2)
    )
    with (ROOT / "data/profile_test_expected.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "university",
                "currency",
                "months",
                "expected_total",
                "expected_resources",
                "expected_gap",
            ],
        )
        writer.writeheader()
        for c in cases:
            writer.writerow(
                {k: c[k] for k in ["id", "expected_total", "expected_resources", "expected_gap"]}
                | {
                    "university": c["profile"]["university"],
                    "currency": c["profile"]["budget_currency"],
                    "months": c["profile"]["months"],
                }
            )
    print(
        "Generated 15 synthetic profiles. Amounts are invented and must not be used as official fee data."
    )
