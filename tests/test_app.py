from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from studentbridge.store import Store
from studentbridge.i18n import Translator

ROOT = Path(__file__).resolve().parents[1]


def app_for(monkeypatch, tmp_path, language="en"):
    directory = tmp_path / "runtime"
    monkeypatch.setenv("STUDENTBRIDGE_DATA_DIR", str(directory))
    monkeypatch.setenv("STUDENTBRIDGE_FX_MODE", "demo")
    store = Store(directory)
    store.create_user("student", "ui-test-password-123")
    token = store.login("student", "ui-test-password-123")
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=25)
    at.session_state["token"] = token
    at.session_state["language"] = language
    return at.run()


def navigate(at, page):
    at.radio(key="nav").set_value(page).run()
    assert not at.exception


def click(at, label):
    next(b for b in at.button if b.label == label).click().run()


@pytest.mark.parametrize("language", ["en", "bn", "zh", "ms"])
def test_converter_and_assistant_in_each_language(monkeypatch, tmp_path, language):
    at = app_for(monkeypatch, tmp_path, language)
    t = Translator(language)
    assert not at.exception
    navigate(at, "converter")
    assert at.text_input(key="convert_amount").value == ""
    at.text_input(key="convert_amount").set_value("12000")
    click(at, t("calculate_conversion"))
    assert not at.exception
    assert at.session_state["conversion"]["converted"] == "698.36"
    assert at.get("download_button")[0].proto.label == t("pdf_statement")
    navigate(at, "assistant")
    assert at.text_area(key="question").value == ""
    at.text_area(key="question").set_value("Convert 12000 BDT to RMB")
    click(at, t("run_assistant"))
    assert not at.exception
    assert at.session_state["answer"]["facts"]["converted"] == "698.36"


@pytest.mark.parametrize("language", ["en", "bn", "zh", "ms"])
def test_budget_wallet_transfer_and_pdf_in_each_language(monkeypatch, tmp_path, language):
    at = app_for(monkeypatch, tmp_path, language)
    t = Translator(language)
    navigate(at, "planner")
    next(c for c in at.checkbox if c.label == t("confirm_fee")).set_value(True)
    click(at, t("calculate_budget"))
    assert not at.exception
    assert "total" in at.session_state["budget"]["result"]
    assert at.get("download_button")[0].proto.label == t("pdf_invoice")
    navigate(at, "wallet")
    at.text_input(key="wallet_amount").set_value("60000")
    click(at, t("add_funds"))
    assert not at.exception
    navigate(at, "transfers")
    at.text_input(key="transfer_amount").set_value("12000")
    click(at, t("compare"))
    click(at, t("create_quote"))
    assert not at.exception
    quote = at.session_state["quote"]
    at.checkbox(key="approve_" + quote["id"]).set_value(True)
    at.text_input(key="confirm_" + quote["id"]).set_value(quote["id"][-6:])
    click(at, t("execute"))
    assert not at.exception
    assert at.session_state["receipt"]["status"].startswith("Sandbox completed")
    assert at.get("download_button")[0].proto.label == t("pdf_receipt")
    # Language changes alter presentation, not the signed quote or posted amounts.
    before = at.session_state["receipt"].copy()
    new_language = "ms" if language != "ms" else "en"
    at.selectbox(key="language").set_value(new_language).run()
    assert not at.exception
    assert at.session_state["receipt"] == before
    quote2 = at.session_state["quote"]
    assert quote2["id"] == quote["id"]


def test_default_is_english_and_guide_contains_examples(monkeypatch, tmp_path):
    at = app_for(monkeypatch, tmp_path)
    assert at.selectbox(key="language").value == "en"
    assert at.session_state["nav"] == "dashboard"
    visible = " ".join(str(e.value) for e in [*at.markdown, *at.caption, *at.info, *at.subheader])
    assert "Try these" not in visible and "demo" not in visible.lower()
    assert not at.code
    navigate(at, "guide")
    assert any("Convert 12000 BDT" in c.value for c in at.code)


@pytest.mark.parametrize("language", ["en", "bn", "zh", "ms"])
def test_developer_and_guide_accessible_without_login(monkeypatch, tmp_path, language):
    monkeypatch.setenv("STUDENTBRIDGE_DATA_DIR", str(tmp_path / "fresh"))
    monkeypatch.setenv("STUDENTBRIDGE_FX_MODE", "demo")
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=25)
    at.session_state["language"] = language
    at.run()
    navigate(at, "developer")
    content = " ".join(str(e.value) for e in [*at.markdown, *at.caption, *at.subheader])
    assert "Md. Sorowar Mahabub Rabby" in content and "XXXXYYYY" in content
    assert "sorowar.cse1@gmail.com" in content and "+60 17-741 7099" in content
    navigate(at, "guide")
    assert any(e.label == Translator(language)("connections") for e in at.expander)


def test_settings_persist_and_currency_change_clears_stale_results(monkeypatch, tmp_path):
    at = app_for(monkeypatch, tmp_path)
    navigate(at, "guide")
    at.selectbox(key="provider_input").set_value("ollama").run()
    assert at.text_input(key="planner_input").value == "qwen3:4b"
    at.text_input(key="planner_input").set_value("qwen3:8b").run()
    navigate(at, "dashboard")
    navigate(at, "guide")
    assert at.text_input(key="planner_input").value == "qwen3:8b"
    at.selectbox(key="provider_input").set_value("groq").run()
    assert at.text_input(key="planner_input").value == "openai/gpt-oss-20b"
    at.session_state["conversion"] = {"old": True}
    at.selectbox(key="fx_mode_input").set_value("live").run()
    assert "conversion" not in at.session_state
    assert at.session_state["settings"]["fx_mode"] == "live"


def test_input_survives_language_change_and_first_setup_validation(monkeypatch, tmp_path):
    at = app_for(monkeypatch, tmp_path)
    navigate(at, "converter")
    at.text_input(key="convert_amount").set_value("222")
    at.selectbox(key="language").set_value("zh").run()
    assert at.text_input(key="convert_amount").value == "222"
    monkeypatch.setenv("STUDENTBRIDGE_DATA_DIR", str(tmp_path / "fresh"))
    fresh = AppTest.from_file(str(ROOT / "app.py"), default_timeout=25).run()
    fresh.text_input(key="setup_password").set_value("short")
    fresh.text_input(key="setup_repeat").set_value("short")
    click(fresh, Translator()("create_account"))
    assert not fresh.exception
    assert any("12–128" in e.value for e in fresh.error)
