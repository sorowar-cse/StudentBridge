"""Interactive local setup. Keys are hidden; generated private files never enter Git."""

from pathlib import Path
from getpass import getpass
import hashlib
import hmac
import json
import os
import secrets
import sys
from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def write_private(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass


def build_configuration(values):
    """Pure builder so tests can check stable keys without using actual credentials."""
    master = values.get("STUDENTBRIDGE_MASTER_KEY") or secrets.token_hex(32)
    raw = bytes.fromhex(master)
    if len(raw) != 32:
        raise ValueError(
            "Master key must be 64 hexadecimal characters. Preserve your original key."
        )
    result = {
        "STUDENTBRIDGE_BACKEND": values.get("STUDENTBRIDGE_BACKEND", "supabase"),
        "STUDENTBRIDGE_DEPLOYMENT": "local",
        "SUPABASE_URL": values.get("SUPABASE_URL", ""),
        "SUPABASE_PUBLISHABLE_KEY": values.get("SUPABASE_PUBLISHABLE_KEY", ""),
        "STUDENTBRIDGE_MASTER_KEY": master,
        "GROQ_API_KEY": values.get("GROQ_API_KEY", ""),
        "STUDENTBRIDGE_AI_PROVIDER": "groq" if values.get("GROQ_API_KEY") else "offline",
        "PLANNER_MODEL": "openai/gpt-oss-20b",
        "REVIEWER_MODEL": "openai/gpt-oss-120b",
        "OLLAMA_PLANNER_MODEL": "qwen3:4b",
        "OLLAMA_REVIEWER_MODEL": "gemma3:4b",
        "STUDENTBRIDGE_FX_MODE": "live",
        "STUDENTBRIDGE_DATA_DIR": "runtime",
    }
    quote = hmac.new(raw, b"quote-signing-v1", hashlib.sha256).hexdigest()
    audit = hmac.new(raw, b"audit-v1", hashlib.sha256).hexdigest()
    sql = f"""-- PRIVATE: run AFTER supabase/schema.sql. Never upload this file.
begin;
do $$ begin
 if exists(select 1 from sb_private.settings where singleton and
   ((quote_key is not null and quote_key<>decode('{quote}','hex')) or
    (audit_key is not null and audit_key<>decode('{audit}','hex')))) then
   raise exception 'Different existing keys: restore the original .env. Do not overwrite the database keys.';
 end if;
end $$;
update sb_private.settings set quote_key=decode('{quote}','hex'),audit_key=decode('{audit}','hex') where singleton;
commit;
"""
    return result, sql


def main():
    path = ROOT / ".env"
    existing = dict(dotenv_values(path)) if path.exists() else {}
    print("StudentBridge v4 setup | secrets stay on your computer")
    if existing:
        print("An existing .env was found. Enter keeps current values AND the master key.")
    mode = input("Backend: Supabase (Enter) or local preview (type local): ").strip().lower()
    values = {**existing, "STUDENTBRIDGE_BACKEND": "local" if mode == "local" else "supabase"}
    if values["STUDENTBRIDGE_BACKEND"] == "supabase":
        values["SUPABASE_URL"] = input(
            "Supabase project URL (Enter keeps current): "
        ).strip() or existing.get("SUPABASE_URL", "")
        values["SUPABASE_PUBLISHABLE_KEY"] = getpass(
            "Supabase PUBLISHABLE key (hidden; Enter keeps current): "
        ).strip() or existing.get("SUPABASE_PUBLISHABLE_KEY", "")
    values["GROQ_API_KEY"] = getpass(
        "Groq key (hidden; optional; Enter keeps current): "
    ).strip() or existing.get("GROQ_API_KEY", "")
    result, sql = build_configuration(values)
    if result["STUDENTBRIDGE_BACKEND"] == "supabase":
        from studentbridge.cloud import configuration

        previous = {k: os.environ.get(k) for k in result}
        try:
            os.environ.update(result)
            configuration()
        finally:
            for k, value in previous.items():
                if value is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = value
    # JSON-quoted strings work in dotenv and TOML for these scalar values.
    write_private(path, "\n".join(f"{k}={json.dumps(v)}" for k, v in result.items()) + "\n")
    cloud = {**result, "STUDENTBRIDGE_BACKEND": "supabase", "STUDENTBRIDGE_DEPLOYMENT": "cloud"}
    write_private(
        ROOT / "runtime/cloud_secrets.toml",
        "\n".join(f"{k} = {json.dumps(v)}" for k, v in cloud.items()) + "\n",
    )
    write_private(ROOT / "runtime/setup_private.sql", sql)
    print("Saved .env, runtime/cloud_secrets.toml and runtime/setup_private.sql.")
    print("Cloud route: run schema.sql, then setup_private.sql in Supabase SQL Editor.")
    print("Disable public signups. Create confirmed accounts in Authentication > Users.")
    print("Preserve .env and the master key when moving to another PC or deploying.")


if __name__ == "__main__":
    main()
