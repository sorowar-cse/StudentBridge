import json
import pytest
from studentbridge.llm import JSONClient, ModelConfig
from studentbridge.agent import Plan, make_plan
from studentbridge.money import FinanceError


class Reply:
    def __init__(self, status=200, data=None):
        self.status_code = status
        self.data = data or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError("fixture failure")

    def json(self):
        return self.data


class ClientSession:
    def __init__(self, reply):
        self.reply, self.last = reply, None

    def post(self, url, **kwargs):
        self.last = (url, kwargs)
        return self.reply


def test_groq_uses_fixed_endpoint_strict_schema_and_server_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fixture-not-a-real-key")
    plan = make_plan("convert", amount="100", source="USD", target="CNY").model_dump()
    session = ClientSession(
        Reply(
            data={
                "choices": [{"message": {"content": json.dumps(plan)}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20},
            }
        )
    )
    client = JSONClient(ModelConfig("groq"), session)
    result = client.call(
        "openai/gpt-oss-20b", "system", "user", Plan.model_json_schema(), "finance_plan"
    )
    assert result == plan
    url, kwargs = session.last
    assert url == "https://api.groq.com/openai/v1/chat/completions"
    assert kwargs["allow_redirects"] is False
    assert kwargs["json"]["response_format"]["json_schema"]["strict"] is True
    assert "Authorization" in kwargs["headers"]
    assert "fixture-not-a-real-key" not in json.dumps(client.calls)


def test_rate_limit_has_no_retry_or_paid_fallback(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fixture-not-a-real-key")
    session = ClientSession(Reply(status=429))
    client = JSONClient(ModelConfig("groq"), session)
    with pytest.raises(FinanceError, match="rate limit"):
        client.call(
            "openai/gpt-oss-20b", "system", "user", Plan.model_json_schema(), "finance_plan"
        )
    assert client.calls == []


def test_ollama_never_uses_a_user_supplied_remote_host():
    plan = make_plan("clarify", question="Which currencies?").model_dump()
    session = ClientSession(Reply(data={"message": {"content": json.dumps(plan)}}))
    client = JSONClient(ModelConfig("ollama"), session)
    assert (
        client.call("qwen3:4b", "system", "user", Plan.model_json_schema(), "finance_plan") == plan
    )
    assert session.last[0] == "http://127.0.0.1:11434/api/chat"
    assert session.last[1]["json"]["stream"] is False
    with pytest.raises(FinanceError):
        client.call("bad model; command", "system", "user", {}, "fixture")
