from datetime import date, timedelta
from decimal import Decimal
import json
import pytest
import requests
from studentbridge.money import FinanceError, decimal, minor, major, rounded, currency
from studentbridge.fx import FXService


@pytest.mark.parametrize(
    "bad", ["NaN", "Infinity", "-1", "1e5", "1,000", "  ", "1000000000001", "0.1234567890123"]
)
def test_invalid_amounts(bad):
    with pytest.raises(FinanceError):
        decimal(bad)


def test_currency_precision_and_aliases():
    assert currency("RMB") == "CNY"
    assert minor("12.345", "KWD") == 12345
    assert major(12345, "KWD") == "12.345"
    assert rounded(Decimal("1.5"), "JPY") == Decimal("2")
    with pytest.raises(FinanceError):
        minor("1.01", "JPY")
    assert currency("CNH") == "CNH" and currency("CNH") != currency("RMB")
    with pytest.raises(FinanceError):
        FXService().rate("CNH", "CNY")  # No invented offshore rate in the demo snapshot.


def test_hand_calculated_demo_conversion():
    fx = FXService()
    assert fx.convert("122", "BDT", "CNY")["converted"] == "7.10"
    assert fx.convert("7.10", "CNY", "BDT")["converted"] == "122.00"
    assert fx.convert("12000", "BDT", "CNY")["converted"] == "698.36"
    assert fx.convert("100", "USD", "JPY")["converted"] == "15000"
    assert fx.convert("100", "USD", "KWD")["converted"] == "30.700"
    assert fx.convert("12.34", "MYR", "MYR")["converted"] == "12.34"
    with pytest.raises(FinanceError):
        fx.rate("XYZ", "XYZ")


@pytest.mark.parametrize("code", FXService().currencies())
def test_every_demo_currency_to_and_from_cny(code):
    fx = FXService()
    outward = fx.convert("100", "CNY", code)
    inward = fx.convert("100", code, "RMB")
    assert Decimal(outward["converted"]) > 0
    assert Decimal(inward["converted"]) > 0
    assert outward["reference"]["mode"] == "demo"
    # Reciprocal rate consistency before target-currency rounding.
    product = Decimal(outward["reference"]["rate"]) * Decimal(inward["reference"]["rate"])
    assert abs(product - 1) < Decimal("1e-26")


class Response:
    status_code = 200

    def __init__(self, data):
        self.data = data
        self.content = json.dumps(data).encode()

    def json(self, **kwargs):
        return self.data

    def raise_for_status(self):
        pass


class Session:
    def __init__(self, data):
        self.data = data

    def get(self, url, **kwargs):
        assert url.startswith("https://api.frankfurter.dev/v2/")
        assert kwargs["allow_redirects"] is False
        return Response(self.data)


def test_live_response_schema_and_provenance():
    row = {"base": "CNY", "quote": "MYR", "rate": 0.6, "date": date.today().isoformat()}
    result = FXService("live", Session(row)).convert("100", "CNY", "MYR")
    assert result["converted"] == "60.00"
    assert result["reference"]["mode"] == "live"
    codes = FXService("live", Session([{"iso_code": "CNY"}, {"iso_code": "MYR"}])).currencies()
    assert codes == ["CNY", "MYR"]


@pytest.mark.parametrize(
    "row",
    [
        {"base": "EUR", "quote": "MYR", "rate": 0.6, "date": date.today().isoformat()},
        {"base": "CNY", "quote": "MYR", "rate": 0, "date": date.today().isoformat()},
        {
            "base": "CNY",
            "quote": "MYR",
            "rate": 0.6,
            "date": (date.today() - timedelta(days=11)).isoformat(),
        },
        {
            "base": "CNY",
            "quote": "MYR",
            "rate": 0.6,
            "date": (date.today() + timedelta(days=1)).isoformat(),
        },
        {"error": "not supported"},
    ],
)
def test_bad_live_data_fails_closed(row):
    with pytest.raises(FinanceError):
        FXService("live", Session(row)).rate("CNY", "MYR")


def test_network_failure_never_falls_back_to_demo():
    class Broken:
        def get(self, *a, **k):
            raise requests.ConnectionError("offline")

    with pytest.raises(FinanceError, match="Live FX unavailable"):
        FXService("live", Broken()).rate("CNY", "MYR")
