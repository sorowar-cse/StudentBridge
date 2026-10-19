from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
from argon2 import PasswordHasher
from studentbridge.store import Store
from studentbridge.fx import FXService
from studentbridge.broker import SandboxBroker


@pytest.fixture(autouse=True)
def isolated_test_settings(monkeypatch, tmp_path):
    """Keep regression tests independent of the owner's running pilot.

    Live Supabase/Groq checks have explicit scripts. The regular pytest suite
    uses temporary local data and fixture HTTP clients, even when a real .env
    exists beside app.py. Individual cloud tests supply their own fake keys.
    """
    for name in list(os.environ):
        if name.startswith(("STUDENTBRIDGE_", "SUPABASE_", "OLLAMA_")) or name in {
            "GROQ_API_KEY", "PLANNER_MODEL", "REVIEWER_MODEL",
        }:
            monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("PYTHON_DOTENV_DISABLED", "1")
    monkeypatch.setenv("STUDENTBRIDGE_BACKEND", "local")
    monkeypatch.setenv("STUDENTBRIDGE_DEPLOYMENT", "local")
    monkeypatch.setenv("STUDENTBRIDGE_AI_PROVIDER", "offline")
    monkeypatch.setenv("STUDENTBRIDGE_FX_MODE", "demo")
    monkeypatch.setenv("STUDENTBRIDGE_DATA_DIR", str(tmp_path / "test_runtime"))

    import requests

    def unexpected_network(*args, **kwargs):
        raise AssertionError("Offline tests must use a fixture HTTP client. Run explicit connection scripts for live checks.")

    monkeypatch.setattr(requests.sessions.Session, "request", unexpected_network)


class AllowedRisk:
    """Ledger tests isolate authorization/atomicity from statistical screening."""

    def assess(self, *args, **kwargs):
        return {"blocked": False, "anomaly": False, "conformal_p": 1, "reasons": []}


@pytest.fixture
def system(tmp_path):
    store = Store(tmp_path)
    # Faster Argon2 parameters only in tests; production defaults stay unchanged.
    store.passwords = PasswordHasher(time_cost=1, memory_cost=8192, parallelism=1)
    store.create_user("student", "test-password-1234")
    token = store.login("student", "test-password-1234")
    broker = SandboxBroker(store, FXService("demo"), AllowedRisk())
    return store, token, broker
