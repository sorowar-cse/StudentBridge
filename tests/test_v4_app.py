from pathlib import Path
import time

import pytest
from streamlit.testing.v1 import AppTest

from studentbridge.cloud import CloudStore
from studentbridge.i18n import Translator
from studentbridge.store import Store

ROOT = Path(__file__).resolve().parents[1]


def navigate(app, page):
    app.radio(key="nav").set_value(page).run()
    assert not app.exception


@pytest.mark.parametrize("language", ["en", "bn", "zh", "ms"])
def test_new_profile_forecast_and_account_pages(monkeypatch, tmp_path, language):
    monkeypatch.setenv("STUDENTBRIDGE_BACKEND", "local")
    monkeypatch.setenv("STUDENTBRIDGE_FX_MODE", "demo")
    monkeypatch.setenv("STUDENTBRIDGE_DATA_DIR", str(tmp_path))
    store = Store(tmp_path)
    store.create_user("student", "v4-ui-test-password")
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=25)
    app.session_state["token"] = store.login("student", "v4-ui-test-password")
    app.session_state["language"] = language
    app.run()
    t = Translator(language)
    navigate(app, "profile")
    for key, value in {
        "p_university": "UKM",
        "p_department": "FKAB",
        "p_programme": "Master of Science",
        "p_city": "Bangi",
        "p_country": "Malaysia",
        "p_tuition": "5000",
        "p_rent": "700",
        "p_food": "600",
        "p_transport": "200",
        "p_utilities": "100",
        "p_other": "200",
    }.items():
        app.text_input(key=key).set_value(value)
    app.checkbox(key="p_confirmed").set_value(True)
    next(b for b in app.button if b.label == t("profile_save")).click().run()
    assert not app.exception
    assert store.student_profile(app.session_state["token"])["university"] == "UKM"
    navigate(app, "forecast")
    app.button(key="forecast_run").click().run()
    assert not app.exception
    assert len(app.session_state["personal_forecast"]["result"]["rows"]) == 12
    assert app.get("download_button")[0].proto.label == t("forecast_pdf")
    navigate(app, "account")
    app.checkbox(key="delete_profiles_confirm").set_value(True).run()
    app.button(key="delete_profiles").click().run()
    assert not app.exception
    assert store.student_profile(app.session_state["token"]) == {}


def test_switching_accounts_clears_previous_private_results(monkeypatch, tmp_path):
    monkeypatch.setenv("STUDENTBRIDGE_BACKEND", "local")
    monkeypatch.setenv("STUDENTBRIDGE_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("STUDENTBRIDGE_FX_MODE", "demo")
    store = Store(tmp_path)
    store.create_user("second", "second-pass-1234")
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=25)
    app.session_state["budget"] = {"private": "previous-user"}
    app.session_state["quote"] = {"private": "previous-user"}
    app.run()
    app.text_input(key="login_username").set_value("second")
    app.text_input(key="login_password").set_value("second-pass-1234")
    next(b for b in app.button if b.label == "Sign in").click().run()
    assert not app.exception
    assert "budget" not in app.session_state and "quote" not in app.session_state
    assert "login_password" not in app.session_state


def test_cloud_wallet_ui_uses_own_audit_without_sqlite(monkeypatch):
    monkeypatch.setenv("STUDENTBRIDGE_BACKEND", "supabase")
    monkeypatch.setenv("SUPABASE_URL", "https://test-project.supabase.co")
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "sb_publishable_test")
    monkeypatch.setenv("STUDENTBRIDGE_MASTER_KEY", "12" * 32)
    monkeypatch.setenv("STUDENTBRIDGE_FX_MODE", "demo")

    def request(self, method, path, **kwargs):
        if path == "/auth/v1/user":
            return {"id": "user-a", "email": "student@example.org"}
        if path == "/rest/v1/sb_members":
            return [{"user_id": "user-a", "role": "executor"}]
        if path == "/rest/v1/sb_wallets":
            return []
        if path == "/rest/v1/sb_documents":
            return []
        if path == "/rest/v1/rpc/sb_export_audit":
            return {
                "global_integrity": {"valid": True, "rows": 1, "head": "a" * 64},
                "own_events": [
                    {
                        "seq": 1,
                        "stamp": time.time(),
                        "event": "account_enrolled",
                        "digest": "a" * 64,
                        "details": {},
                    }
                ],
            }
        raise AssertionError(path)

    monkeypatch.setattr(CloudStore, "_request", request)
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=25)
    app.session_state["token"] = "supabase-session"
    app.run()
    navigate(app, "wallet")
    assert not app.exception
    assert app.get("download_button")[0].proto.label == Translator()("pdf_statement")


def test_cloud_config_failure_is_closed_but_public_guide_works(monkeypatch):
    monkeypatch.setenv("STUDENTBRIDGE_BACKEND", "supabase")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=25).run()
    assert not app.exception and any("Configuration incomplete" in e.value for e in app.error)
    navigate(app, "guide")
    assert any(e.label == Translator()("guide_v4_title") for e in app.expander)
