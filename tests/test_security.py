from concurrent.futures import ThreadPoolExecutor
import json
import time
import pytest
from studentbridge.money import FinanceError


def quote(system, amount="100"):
    store, token, broker = system
    return broker.create_quote(token, amount, "USD", "CNY", "Value")


def test_fee_is_inside_spend_and_receipt_replay(system):
    store, token, broker = system
    store.seed_wallet(token, "USD", "1000")
    q = quote(system)
    # USD100 -> fee .20 + .4 = .60; (100-.6)*7.1*(1-.006) = CNY701.50556 -> 701.51
    assert q["fee_minor"] == 60
    assert q["receive_minor"] == 70151
    one = broker.execute(token, q["id"], q["id"][-6:], approved=True)
    assert one["replayed"] is False
    wallet = store.wallet(token)
    two = broker.execute(token, q["id"], "", approved=False, now=q["expires"] + 100)
    assert two["replayed"] is True
    assert store.wallet(token) == wallet
    assert wallet["USD"] == 90000 and wallet["CNY"] == 70151
    assert store.verify_audit()["valid"]


@pytest.mark.parametrize("approval,confirmation", [(False, "right"), (True, "wrong")])
def test_confirmation_required(system, approval, confirmation):
    store, token, broker = system
    store.seed_wallet(token, "USD", "1000")
    q = quote(system)
    before = store.wallet(token)
    with pytest.raises(FinanceError, match="Review the quote"):
        broker.execute(
            token, q["id"], q["id"][-6:] if confirmation == "right" else "abcdef", approved=approval
        )
    assert store.wallet(token) == before


def test_expired_quote_cannot_move_balance(system):
    store, token, broker = system
    store.seed_wallet(token, "USD", "1000")
    q = quote(system)
    with pytest.raises(FinanceError, match="expired"):
        broker.execute(token, q["id"], q["id"][-6:], approved=True, now=q["expires"])
    assert store.wallet(token)["USD"] == 100000


def test_cross_account_and_forged_session_denied(system):
    store, token, broker = system
    q = quote(system)
    store.create_user("second", "another-test-password")
    second = store.login("second", "another-test-password")
    with pytest.raises(FinanceError, match="does not belong"):
        broker.execute(second, q["id"], q["id"][-6:], approved=True)
    with pytest.raises(FinanceError, match="Session expired"):
        broker.execute("forged-token", q["id"], q["id"][-6:], approved=True)


@pytest.mark.parametrize("role", ["viewer", "planner"])
def test_server_role_cannot_be_promoted_from_ui(system, role):
    store, token, broker = system
    store.create_user(role, "role-test-password", role)
    restricted = store.login(role, "role-test-password")
    if role == "viewer":
        with pytest.raises(FinanceError, match="Viewer"):
            broker.create_quote(restricted, "100", "USD", "CNY", "Value")
    else:
        q = broker.create_quote(restricted, "100", "USD", "CNY", "Value")
        with pytest.raises(FinanceError, match="cannot execute"):
            broker.execute(restricted, q["id"], q["id"][-6:], approved=True)
    with pytest.raises(FinanceError):
        store.seed_wallet(restricted, "USD", "1000")


def test_quote_tampering_and_insufficient_funds(system):
    store, token, broker = system
    q = quote(system)
    with pytest.raises(FinanceError, match="Insufficient"):
        broker.execute(token, q["id"], q["id"][-6:], approved=True)
    store.seed_wallet(token, "USD", "1000")
    with store.connection(write=True) as con:
        q["receive_minor"] += 10000
        con.execute("UPDATE quotes SET payload=? WHERE id=?", (json.dumps(q), q["id"]))
    with pytest.raises(FinanceError, match="signature"):
        broker.execute(token, q["id"], q["id"][-6:], approved=True)
    assert store.wallet(token)["USD"] == 100000


def test_concurrent_replay_is_one_debit(system):
    store, token, broker = system
    store.seed_wallet(token, "USD", "1000")
    q = quote(system)
    with ThreadPoolExecutor(max_workers=8) as pool:
        receipts = list(
            pool.map(
                lambda _: broker.execute(token, q["id"], q["id"][-6:], approved=True), range(8)
            )
        )
    assert sum(not r["replayed"] for r in receipts) == 1
    assert store.wallet(token)["USD"] == 90000
    assert store.verify_audit()["valid"]


def test_concurrent_different_quotes_cannot_overdraw(system):
    store, token, broker = system
    store.seed_wallet(token, "USD", "100")
    quotes = [quote(system, "60"), quote(system, "60")]

    def run(q):
        try:
            return broker.execute(token, q["id"], q["id"][-6:], approved=True)["status"]
        except FinanceError:
            return "denied"

    with ThreadPoolExecutor(max_workers=2) as pool:
        result = list(pool.map(run, quotes))
    assert result.count("denied") == 1
    assert store.wallet(token)["USD"] == 4000


def test_daily_and_frequency_limits(system):
    store, token, broker = system
    store.seed_wallet(token, "USD", "10000")
    for _ in range(3):
        q = quote(system, "1500")
        broker.execute(token, q["id"], q["id"][-6:], approved=True)
    q = quote(system, "1000")
    with pytest.raises(FinanceError, match="Daily"):
        broker.execute(token, q["id"], q["id"][-6:], approved=True)
    for _ in range(2):
        q = quote(system, "100")
        broker.execute(token, q["id"], q["id"][-6:], approved=True)
    q = quote(system, "100")
    with pytest.raises(FinanceError, match="frequency"):
        broker.execute(token, q["id"], q["id"][-6:], approved=True)


def test_audit_edit_and_truncation_detected(system):
    store, token, broker = system
    store.seed_wallet(token, "USD", "1000")
    assert store.verify_audit()["valid"]
    with store.connection(write=True) as con:
        con.execute("DELETE FROM audit WHERE seq=(SELECT MAX(seq) FROM audit)")
    assert not store.verify_audit()["valid"]
    with pytest.raises(FinanceError, match="Audit integrity"):
        quote(system)


def test_encrypted_profile_and_authenticated_ciphertext(system):
    store, token, broker = system
    profile = {"rent": "987.65", "record_id": "zju_cs"}
    store.save_profile(token, profile)
    assert store.profile(token) == profile
    raw = store.db.read_bytes()
    assert b"987.65" not in raw
    with store.connection(write=True) as con:
        row = con.execute("SELECT encrypted FROM profiles").fetchone()[0]
        con.execute("UPDATE profiles SET encrypted=?", (row[:-2] + f"{int(row[-2:], 16) ^ 1:02x}",))
    with pytest.raises(Exception):
        store.profile(token)


def test_lockout_and_logout(system):
    store, token, broker = system
    now = time.time()
    for _ in range(5):
        assert store.login("student", "wrong", now=now) is None
    assert store.login("student", "test-password-1234", now=now + 1) is None
    assert store.login("student", "test-password-1234", now=now + 301)
    store.logout(token)
    with pytest.raises(FinanceError):
        store.principal(token)


def test_wallet_edit_and_receipt_metadata_edit_fail_closed(system):
    store, token, broker = system
    store.seed_wallet(token, "USD", "1000")
    q = quote(system)
    broker.execute(token, q["id"], q["id"][-6:], approved=True)
    with store.connection(write=True) as con:
        con.execute("UPDATE transfers SET usd=? WHERE quote_id=?", ("0", q["id"]))
    with pytest.raises(FinanceError, match="metadata integrity"):
        broker.execute(token, q["id"], "", approved=False)
    with store.connection(write=True) as con:
        con.execute("UPDATE wallets SET balance=99999999 WHERE currency=?", ("USD",))
    with pytest.raises(FinanceError, match="Wallet integrity"):
        store.wallet(token)


def test_receipt_replay_survives_process_restart(system):
    from studentbridge.store import Store
    from studentbridge.broker import SandboxBroker
    from studentbridge.fx import FXService
    from conftest import AllowedRisk

    store, token, broker = system
    store.seed_wallet(token, "USD", "1000")
    q = quote(system)
    broker.execute(token, q["id"], q["id"][-6:], approved=True)
    reopened = Store(store.directory)
    next_token = reopened.login("student", "test-password-1234")
    replay = SandboxBroker(reopened, FXService(), AllowedRisk()).execute(
        next_token, q["id"], "", approved=False
    )
    assert replay["replayed"] and reopened.wallet(next_token)["USD"] == 90000
