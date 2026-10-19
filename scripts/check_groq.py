"""Diagnose StudentBridge v4 Groq requests using synthetic inputs only.

Place this file in StudentBridge/scripts and run it with the project's Python.
It makes up to four small inference requests using the app's original adapter
and schemas. It does not access Supabase, profiles, wallets, or audit records.
API credentials and generated model text are never intentionally printed.
"""

from pathlib import Path
import json
import os
import re
import sys


def redact(value, private_values):
    """Keep provider diagnostics useful while removing known credentials."""
    text = str(value)
    for secret in sorted(set(private_values), key=len, reverse=True):
        if len(secret) >= 8:
            text = text.replace(secret, "[REDACTED]")
    text = re.sub(
        r"\b(?:gsk_|sb_secret_|sb_publishable_)[A-Za-z0-9_-]+",
        "[REDACTED]",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\bBearer\s+\S+", "Bearer [REDACTED]", text, flags=re.IGNORECASE)
    return text.replace("\r", " ").replace("\n", " ")[:1200]


def describe_response(response, private_values):
    """Report status and selected error fields, never headers or raw output."""
    if response is None:
        print("  HTTP response: none received")
        return
    print("  HTTP status:", response.status_code)
    try:
        body = response.json()
    except ValueError:
        print("  Response body was not JSON; body omitted.")
        return
    if not isinstance(body, dict):
        print("  Unexpected JSON body shape; body omitted.")
        return
    error = body.get("error")
    if isinstance(error, dict):
        for field in ("type", "code", "message"):
            if error.get(field) is not None:
                print("  Provider " + field + ":", redact(error[field], private_values))
    # A length finish can explain valid HTTP responses with incomplete JSON.
    choices = body.get("choices")
    if isinstance(choices, list) and choices and isinstance(choices[0], dict):
        print("  Finish reason:", redact(choices[0].get("finish_reason"), private_values))


def main():
    root = Path(__file__).resolve().parents[1]
    if not (root / "app.py").is_file():
        print("Put this file in the StudentBridge/scripts folder, then run again.")
        return 1
    sys.path.insert(0, str(root))

    # Imports stay here so the redaction helpers can be tested independently.
    import requests
    from dotenv import dotenv_values, load_dotenv
    from studentbridge.agent import AdviceSelection, Plan, Review
    from studentbridge.llm import JSONClient, ModelConfig

    env_path = root / ".env"
    file_values = dict(dotenv_values(env_path)) if env_path.is_file() else {}
    # Match the application's normal precedence: existing environment wins.
    load_dotenv(env_path)
    private_values = [
        value
        for source in (file_values, dict(os.environ))
        for name, value in source.items()
        if value and any(word in name.upper() for word in ("KEY", "TOKEN", "SECRET", "PASSWORD"))
    ]
    if not os.getenv("GROQ_API_KEY", "").strip():
        print("FAIL: GROQ_API_KEY is missing. Keep its value private.")
        return 1

    class RecordingSession(requests.Session):
        """Retain the response in memory when the app wraps an HTTP error."""

        def __init__(self):
            super().__init__()
            self.last_response = None

        def post(self, *args, **kwargs):
            self.last_response = None
            response = super().post(*args, **kwargs)
            self.last_response = response
            return response

    config = ModelConfig(
        "groq",
        os.getenv("PLANNER_MODEL", "openai/gpt-oss-20b"),
        os.getenv("REVIEWER_MODEL", "openai/gpt-oss-120b"),
    )
    plan = {
        "intent": "convert", "amount": "100", "source": "MYR", "target": "CNY",
        "university_id": None, "source_ids": [], "question": None,
    }
    probes = [
        ("Forecast planner", config.planner, AdviceSelection, "budget_actions",
         {"actions": ["VERIFY_FEE", "CHECK_DUE_DATE"]}),
        ("Forecast reviewer", config.reviewer, AdviceSelection, "budget_actions_review",
         {"actions": ["VERIFY_FEE", "CHECK_DUE_DATE"]}),
        ("Assistant planner", config.planner, Plan, "finance_plan", plan),
        ("Assistant reviewer", config.reviewer, Review, "finance_review",
         {"decision": "accept", "plan": plan, "reason": "Matches the synthetic request."}),
    ]
    print("StudentBridge Groq diagnostic | synthetic inputs | original v4 request settings")
    print("No database access. Up to four API calls. No automatic retries.")
    failures = 0
    completed = 0
    for title, model, schema_type, label, expected in probes:
        print("\nCHECK:", title, "|", redact(model, private_values))
        with RecordingSession() as session:
            client = JSONClient(config, session=session)
            try:
                result = client.call(
                    model,
                    "Return only the supplied synthetic JSON object, following the response schema.",
                    json.dumps(expected),
                    schema_type.model_json_schema(),
                    label,
                )
                schema_type.model_validate(result)
            except Exception as exc:
                failures += 1
                print("FAIL:", type(exc).__name__)
                if exc.__cause__ is not None:
                    print("  Underlying exception:", type(exc.__cause__).__name__)
                describe_response(session.last_response, private_values)
            else:
                print("PASS: valid JSON and application schema validation")
                describe_response(session.last_response, private_values)
            completed += 1
            response = session.last_response
            if response is None or response.status_code in (401, 403, 429) or response.status_code >= 500:
                print("Stopped to avoid repeated authentication, quota or connection failures.")
                break
    print(f"\nSUMMARY: {completed} checks attempted; {failures} failed.")
    print("Share this diagnostic output only. Do not share .env or private configuration files.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
