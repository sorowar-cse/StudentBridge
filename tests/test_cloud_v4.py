from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest
import requests

from studentbridge.cloud import CloudStore, configuration
from studentbridge.money import FinanceError


@pytest.fixture
def cloud_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://test-project.supabase.co")
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "sb_publishable_test")
    monkeypatch.setenv("STUDENTBRIDGE_MASTER_KEY", "12" * 32)


class Reply:
    def __init__(self, body, status=200):
        self.body = body
        self.status_code = status
        self.content = json.dumps(body).encode()

    def json(self):
        return self.body


class HTTP:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        result = self.replies.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


def test_auth_tokens_only_in_session_and_user_bearer_on_database(cloud_env):
    http = HTTP(
        [
            Reply({"access_token": "USER_TOKEN", "refresh_token": "REFRESH", "expires_in": 3600}),
            Reply({"enrolled": True}),
            Reply({"id": "u1", "email": "one@example.org"}),
            Reply([{"user_id": "u1", "role": "executor"}]),
        ]
    )
    state = {}
    s = CloudStore(state, http, clock=lambda: 100)
    token = s.login("one@example.org", "long-test-password")
    assert token == "supabase-session"
    assert s.principal(token)["id"] == "u1"
    assert http.calls[0][2]["headers"] == {
        "apikey": "sb_publishable_test",
        "Content-Type": "application/json",
    }
    assert http.calls[1][2]["headers"]["Authorization"] == "Bearer USER_TOKEN"
    assert state["auth"]["refresh_token"] == "REFRESH"


def test_two_sessions_never_share_tokens(cloud_env):
    a = CloudStore(
        {
            "auth": {"access_token": "A", "refresh_token": "RA", "expires_at": 2000},
            "absolute_expiry": 3000,
        },
        HTTP([]),
        clock=lambda: 100,
    )
    b = CloudStore(
        {
            "auth": {"access_token": "B", "refresh_token": "RB", "expires_at": 2000},
            "absolute_expiry": 3000,
        },
        HTTP([]),
        clock=lambda: 100,
    )
    assert a._access_token() == "A" and b._access_token() == "B"
    a.session.clear()
    assert b._access_token() == "B"


def test_refresh_rotates_and_absolute_session_expiry(cloud_env):
    http = HTTP(
        [Reply({"access_token": "NEW", "refresh_token": "NEW_REFRESH", "expires_in": 3600})]
    )
    state = {
        "auth": {"access_token": "OLD", "refresh_token": "OLD_REFRESH", "expires_at": 100},
        "absolute_expiry": 1900,
    }
    s = CloudStore(state, http, clock=lambda: 100)
    assert s._access_token() == "NEW"
    assert state["auth"]["refresh_token"] == "NEW_REFRESH"
    s.clock = lambda: 2000
    with pytest.raises(FinanceError, match="expired"):
        s._access_token()
    assert not state


def test_privileged_key_and_bad_url_rejected(cloud_env, monkeypatch):
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "sb_secret_do_not_use")
    with pytest.raises(FinanceError):
        configuration()
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "sb_publishable_test")
    monkeypatch.setenv("SUPABASE_URL", "http://127.0.0.1:8080")
    with pytest.raises(FinanceError):
        configuration()


def test_cloud_encryption_binds_document_to_user_and_kind(cloud_env):
    a = CloudStore(http=HTTP([]))
    encrypted = a.encrypt({"tuition": "12345"}, "cloud:student:user-a")
    assert "12345" not in encrypted
    assert a.decrypt(encrypted, "cloud:student:user-a") == {"tuition": "12345"}
    with pytest.raises(Exception):
        a.decrypt(encrypted, "cloud:student:user-b")
    with pytest.raises(Exception):
        a.decrypt(encrypted, "cloud:plan:user-a")


def test_provider_error_never_echoes_tokens(cloud_env):
    s = CloudStore(http=HTTP([Reply({"message": "internal detail SECRET_TOKEN"}, 500)]))
    with pytest.raises(FinanceError) as e:
        s._request("GET", "/auth/v1/settings", authenticated=False)
    assert "SECRET_TOKEN" not in str(e.value)


def test_no_local_fallback_on_network_failure(cloud_env, tmp_path):
    s = CloudStore(http=HTTP([requests.ConnectionError("private network internals")]))
    with pytest.raises(FinanceError, match="not replaced locally"):
        s._request("GET", "/auth/v1/settings", authenticated=False)


def test_setup_preserves_master_and_generates_private_sql():
    path = Path(__file__).resolve().parents[1] / "scripts/setup_local.py"
    spec = importlib.util.spec_from_file_location("setup_local", path)
    setup = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(setup)
    first, sql = setup.build_configuration({"STUDENTBRIDGE_MASTER_KEY": "12" * 32})
    second, sql2 = setup.build_configuration(deepcopy(first))
    assert first["STUDENTBRIDGE_MASTER_KEY"] == second["STUDENTBRIDGE_MASTER_KEY"]
    assert "12" * 32 not in sql  # Only signing/audit subkeys are placed in the database.
    assert sql == sql2
