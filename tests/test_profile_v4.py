from copy import deepcopy
from datetime import date
from decimal import Decimal
from io import BytesIO

import pytest
from pypdf import PdfReader

from studentbridge.documents import forecast_pdf, student_profile_pdf
from studentbridge.fx import FXService
from studentbridge.money import FinanceError
from studentbridge.profile import add_months, forecast, validated_profile


@pytest.fixture
def student_profile():
    def money(amount, code="MYR"):
        return {"amount": amount, "currency": code}

    return dict(
        university="Universiti Kebangsaan Malaysia",
        campus="Bangi",
        department="FKAB",
        programme="Master of Science",
        study_mode="Research",
        city="Bangi",
        country="Malaysia",
        start_date="2026-01-31",
        months=6,
        budget_currency="MYR",
        tuition=money("5000"),
        fee_period="semester",
        billing_interval_months=6,
        next_tuition_date="2026-01-31",
        living={
            k: money(v)
            for k, v in zip(
                ["rent", "food", "transport", "utilities", "other"],
                ["700", "600", "200", "100", "200"],
            )
        },
        one_off=money("1000"),
        savings=money("0"),
        monthly_income=money("0"),
        confirmed_funding=money("0"),
        buffer_percent="10",
        annual_cost_growth_percent="0",
        fx_stress_percent="0",
        source_note="Synthetic test inputs",
        confirmed=True,
    )


def test_forecast_total_and_cashflow(student_profile):
    p = validated_profile(student_profile)
    r = forecast(p, FXService("demo"))
    assert r["total"] == "18480.00"
    assert r["funding_gap"] == "18480.00"
    assert r["upfront_timing_gap"] == "18480.00"
    assert len(r["rows"]) == 6
    assert r["rows"][0]["tuition_due_dates"] == "2026-01-31"
    assert r["references"] == []
    for row in r["rows"]:
        assert sum(Decimal(row[k]) for k in ["living", "tuition", "one_off", "buffer"]) == Decimal(
            row["cost"]
        )


def test_month_end_and_leap_calendar():
    assert add_months(date(2024, 1, 31), 1) == date(2024, 2, 29)
    assert add_months(date(2024, 1, 31), 2) == date(2024, 3, 31)


def test_final_surplus_can_hide_earlier_cash_shortfall(student_profile):
    p = deepcopy(student_profile)
    p["monthly_income"]["amount"] = "4000"
    r = forecast(p, FXService("demo"))
    assert r["funding_gap"] == "0.00"
    assert Decimal(r["upfront_timing_gap"]) > 0
    assert r["first_shortfall"] == "2026-01-31"


def test_foreign_stress_does_not_inflate_income(student_profile):
    p = deepcopy(student_profile)
    p["tuition"] = {"amount": "1000", "currency": "USD"}
    p["monthly_income"] = {"amount": "100", "currency": "USD"}
    r0 = forecast(p, FXService("demo"))
    p["fx_stress_percent"] = "10"
    r1 = forecast(p, FXService("demo"))
    assert r1["resources"] == r0["resources"]
    assert Decimal(r1["total"]) > Decimal(r0["total"])
    assert len(r1["references"]) == 1


@pytest.mark.parametrize(
    "field,value",
    [
        ("confirmed", False),
        ("billing_interval_months", 0),
        ("months", 0),
        ("buffer_percent", "101"),
        ("next_tuition_date", "2025-12-01"),
        ("annual_cost_growth_percent", "-1"),
        ("university", ""),
        ("fx_stress_percent", "NaN"),
    ],
)
def test_reject_invalid_profile(student_profile, field, value):
    p = deepcopy(student_profile)
    p[field] = value
    with pytest.raises(FinanceError):
        validated_profile(p)


def test_once_fee_and_recurrence(student_profile):
    p = deepcopy(student_profile)
    p["months"] = 13
    p["buffer_percent"] = "0"
    r = forecast(p, FXService("demo"))
    assert sum(Decimal(x["tuition"]) for x in r["rows"]) == 15000
    p["fee_period"] = "invoice"
    p["billing_interval_months"] = 0
    r = forecast(p, FXService("demo"))
    assert sum(Decimal(x["tuition"]) for x in r["rows"]) == 5000


def test_pdf_contains_source_assumptions_and_footer(student_profile):
    p = validated_profile(student_profile)
    r = forecast(p, FXService("demo"))
    for data in [student_profile_pdf(p), forecast_pdf(p, r)]:
        assert data.startswith(b"%PDF")
        text = "\n".join(page.extract_text() for page in PdfReader(BytesIO(data)).pages)
        assert "StudentBridge" in text
        assert "Invoice is Computer Generated, NO need signature" in text
        assert "5000" in text or "18,480" in text or "18480" in text


def test_local_profile_isolation_and_delete(system, student_profile):
    store, token, _ = system
    store.save_student_profile(token, validated_profile(student_profile))
    store.create_user("another", "another-pass-12345")
    other = store.login("another", "another-pass-12345")
    assert store.student_profile(other) == {}
    assert store.student_profile(token)["university"].startswith("Universiti")
    assert b"Universiti Kebangsaan" not in store.db.read_bytes()
    store.clear_personal_data(other)
    assert store.student_profile(token)
    store.clear_personal_data(token)
    assert store.student_profile(token) == {}


def test_local_shared_ai_limit(system):
    store, token, _ = system
    for _ in range(3):
        store.reserve_ai(token)
    with pytest.raises(FinanceError, match="allowance"):
        store.reserve_ai(token)
