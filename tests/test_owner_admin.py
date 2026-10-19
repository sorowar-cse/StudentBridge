import importlib.util
from pathlib import Path

import pytest

path = Path(__file__).resolve().parents[1] / "scripts/cloud_account_admin.py"
spec = importlib.util.spec_from_file_location("cloud_account_admin", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_owner_utility_rejects_publishable_key():
    with pytest.raises(ValueError, match="admin key"):
        module.OwnerAuth("https://pilot.supabase.co", "sb_publishable_test")


def test_owner_utility_fixed_host_and_safe_errors():
    with pytest.raises(ValueError, match="URL"):
        module.OwnerAuth("http://127.0.0.1", "sb_secret_synthetic")

    class Reply:
        status_code = 401
        content = b'{"message":"SECRET_KEY_DO_NOT_ECHO"}'

    class HTTP:
        def request(self, *args, **kwargs):
            return Reply()

    admin = module.OwnerAuth("https://pilot.supabase.co", "sb_secret_synthetic", HTTP())
    with pytest.raises(ValueError) as e:
        admin.request("GET", "/synthetic-user")
    assert "SECRET_KEY_DO_NOT_ECHO" not in str(e.value)
