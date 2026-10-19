import json
from pathlib import Path

import pytest

from studentbridge.fx import FXService
from studentbridge.profile import forecast

CASES = json.loads(
    (Path(__file__).resolve().parents[1] / "data/profile_test_cases.json").read_text()
)["cases"]


@pytest.mark.parametrize("case", CASES, ids=[c["id"] for c in CASES])
def test_forecast_against_independent_synthetic_expected_totals(case):
    result = forecast(case["profile"], FXService("demo"))
    assert result["total"] == case["expected_total"]
    assert result["resources"] == case["expected_resources"]
    assert result["funding_gap"] == case["expected_gap"]
