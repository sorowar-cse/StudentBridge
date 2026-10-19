from io import BytesIO
from pathlib import Path
from string import Formatter
import pytest
from PIL import Image
from pypdf import PdfReader
from studentbridge.documents import (
    transfer_receipt,
    planning_invoice,
    audit_statement,
    conversion_statement,
    FOOTER,
)
from studentbridge.i18n import CATALOG, LANGUAGES, Translator
from studentbridge.team import members, profile_image
from studentbridge import team
from studentbridge.university import UniversityCatalog, budget_scenario
from studentbridge.fx import FXService
from studentbridge.agent import FinanceAgent
from studentbridge.llm import ModelConfig


def receipt():
    return {
        "quote_id": "a" * 32,
        "source": "BDT",
        "target": "CNY",
        "spent": "12000.00",
        "fee_included": "73.20",
        "received": "690.00",
        "provider": "Value",
        "fx_mode": "demo",
        "executed_at": 1792022400,
        "replayed": False,
    }


def text(data):
    assert data.startswith(b"%PDF-")
    reader = PdfReader(BytesIO(data))
    pages = [page.extract_text() for page in reader.pages]
    assert all("StudentBridge" in page and FOOTER in page for page in pages)
    return "\n".join(pages), len(pages)


def test_receipt_has_requested_header_footer_and_honest_status():
    body, count = text(transfer_receipt(receipt()))
    assert "Transfer Receipt" in body and "Receipt details" in body
    assert "SIMULATED TRANSACTION" in body and "NO REAL MONEY MOVED" in body
    assert "12000.00 BDT" in body and "690.00 CNY" in body
    assert count == 1


def test_replayed_receipt_keeps_original_document_identity():
    original = receipt()
    first, _ = text(transfer_receipt(original))
    repeated, _ = text(transfer_receipt({**original, "replayed": True}))
    identity = "SB-RCP-" + original["quote_id"].upper()
    assert identity in first and identity in repeated
    assert "Yes - no second debit" in repeated


def test_planning_invoice_is_unpaid_estimate_not_payment_confirmation():
    record = UniversityCatalog().get("um_meng_int")
    inputs = dict(
        code="MYR",
        tuition="43200",
        fee_period="programme",
        tuition_periods=1,
        months=24,
        living={
            "rent": "900",
            "food": "550",
            "transport": "150",
            "utilities": "150",
            "other": "200",
        },
        tax_percent="6",
        buffer_percent="10",
        savings="1000",
    )
    result = budget_scenario(**inputs)
    body, count = text(planning_invoice({"inputs": inputs, "result": result}, record))
    assert "Planning Invoice" in body and "UNPAID PLANNING ESTIMATE" in body
    assert "43200" in body and result["total"] in body
    assert "No payment is requested or confirmed" in body
    assert 1 <= count <= 3


def test_multipage_statement_repeats_header_and_footer():
    audit = {
        "global_integrity": {"valid": True, "rows": 150, "head": "a" * 64},
        "own_events": [
            {"seq": i + 1, "stamp": 1792022400 + i, "event": "sandbox_transfer_completed"}
            for i in range(150)
        ],
    }
    body, count = text(audit_statement(audit))
    assert count > 1 and "#150" in body


def test_conversion_preserves_amount_and_reference_date():
    result = FXService().convert("122", "BDT", "CNY")
    body, count = text(conversion_statement(result))
    assert "7.10 CNY" in body and result["reference"]["as_of"] in body
    assert "Illustrative reference dataset" in body
    assert count == 1


def test_all_translation_parameters_match_english():
    for key, english in CATALOG["en"].items():
        expected = {field for _, field, _, _ in Formatter().parse(english) if field is not None}
        for language in LANGUAGES:
            other = CATALOG[language][key]
            assert other.strip()
            assert {
                field for _, field, _, _ in Formatter().parse(other) if field is not None
            } == expected
    assert Translator()("dashboard") == "Dashboard"
    assert Translator("invalid")("dashboard") == "Dashboard"


def test_team_details_and_separate_replaceable_images(monkeypatch, tmp_path):
    first, second = members()
    # Member details and photos are owner-editable; do not freeze the team's
    # names/placeholders or require optional personal images in the test suite.
    assert first["id"] != second["id"]
    for member in (first, second):
        for field in ("name", "degree", "faculty", "university", "email", "phone"):
            assert isinstance(member[field], str) and member[field].strip()
        assert isinstance(member["whatsapp_only"], bool)
        image_path = Path(member["image"])
        assert image_path.name == "profile.png"
        assert not image_path.is_absolute()
        assert image_path.is_relative_to(Path("assets/team"))
        assert ".." not in image_path.parts
    assert Path(first["image"]).parent != Path(second["image"]).parent

    # Exercise the image resolver with isolated fixtures, not the owner's files.
    monkeypatch.setattr(team, "ROOT", tmp_path)
    for member in (first, second):
        image_path = tmp_path / member["image"]
        image_path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (16, 16), "gray").save(image_path, format="PNG")
    leader_image = profile_image(first)
    member_image = profile_image(second)
    assert leader_image is not None and member_image is not None
    assert leader_image.name == member_image.name == "profile.png"
    assert leader_image.parent != member_image.parent

    member_image.unlink()
    assert profile_image(second) is None  # The UI uses initials for no photo.
    member_image.write_bytes(b"not an image")
    assert profile_image(second) is None
    outside = tmp_path / "outside.png"
    Image.new("RGB", (16, 16), "gray").save(outside, format="PNG")
    assert profile_image({"image": "outside.png"}) is None
    assert profile_image({"image": "../../../../etc/passwd"}) is None


@pytest.mark.parametrize(
    "question",
    ["12000 BDT থেকে RMB হিসাব করো", "将 12000 BDT 转换为 RMB", "Tukar 12000 BDT kepada RMB"],
)
def test_multilingual_guide_conversion_examples(question):
    result = FinanceAgent(FXService(), UniversityCatalog(), ModelConfig()).answer(question)
    assert result["status"] == "ok" and result["facts"]["converted"] == "698.36"
