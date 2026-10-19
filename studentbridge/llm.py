"""Small provider adapters. They return bounded JSON, never execute tool calls.

Groq calls use a server-side key. Ollama calls are fixed to loopback. There is no
automatic switch from a free account to a paid service or another provider.
"""

from dataclasses import dataclass
import json
import os
import re
import time
import requests
from .money import FinanceError


class LLMError(FinanceError):
    """Provider/response failure, distinct from a question needing clarification."""


@dataclass(frozen=True)
class ModelConfig:
    provider: str = "offline"
    planner: str = "openai/gpt-oss-20b"
    reviewer: str = "openai/gpt-oss-120b"


def safe_text(text):
    if not isinstance(text, str) or not 1 <= len(text.strip()) <= 1200:
        raise FinanceError("Use a question of 1–1,200 characters.")
    if re.search(
        r"(?i)(api[_ -]?key\s*[:=]|password\s*[:=]|passport\s*[:=]|\bsk-[a-z0-9]|\bgsk_[a-z0-9])",
        text,
    ):
        raise FinanceError("Remove passwords, API keys and passport identifiers from the question.")
    # Mask common identifiers before any provider request. Do not log original text.
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[EMAIL_REMOVED]", text)
    text = re.sub(r"(?<!\d)(?:\+?\d[\d -]{8,}\d)(?!\d)", "[IDENTIFIER_REMOVED]", text)
    return text.strip()


class JSONClient:
    def __init__(self, config, session=None):
        self.config = config
        self.session = session or requests.Session()
        self.calls = []

    def models(self):
        if self.config.provider == "groq":
            response = self.session.get(
                "https://api.groq.com/openai/v1/models",
                headers=self._headers(),
                timeout=(5, 15),
                allow_redirects=False,
            )
            response.raise_for_status()
            return sorted(row["id"] for row in response.json()["data"])
        if self.config.provider == "ollama":
            response = self.session.get(
                "http://127.0.0.1:11434/api/tags", timeout=(3, 10), allow_redirects=False
            )
            response.raise_for_status()
            return sorted(row["name"] for row in response.json().get("models", []))
        return []

    def _headers(self):
        key = os.getenv("GROQ_API_KEY", "").strip()
        if not key:
            raise LLMError("Set GROQ_API_KEY in your local .env file, then restart the app.")
        return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    def call(self, model, system, user, schema, label):
        start = time.monotonic()
        if self.config.provider == "offline":
            raise FinanceError(
                "No LLM is enabled. Use the offline baseline or configure Groq/Ollama."
            )
        if not re.fullmatch(r"[A-Za-z0-9_./:-]{1,100}", model):
            raise FinanceError("Invalid model name.")
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        try:
            if self.config.provider == "groq":
                response = self.session.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=self._headers(),
                    timeout=(5, 45),
                    allow_redirects=False,
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": 0,
                        "max_completion_tokens": 700,
                        "response_format": {
                            "type": "json_schema",
                            "json_schema": {"name": label, "strict": True, "schema": schema},
                        },
                    },
                )
                # No repeated request on 429: two-model runs must respect the user's quota.
                if response.status_code == 429:
                    raise LLMError(
                        "Groq rate limit reached. Wait for your account quota; the app did not retry."
                    )
                errors = {
                    400: "Groq rejected the structured request (HTTP 400). Check model/schema support and output limits.",
                    401: "Groq rejected the API key (HTTP 401). Update the private Groq key and restart the app.",
                    403: "Groq denied model access (HTTP 403). Check the project's model permissions.",
                    404: "Groq could not find the model (HTTP 404). Check the configured model ID.",
                }
                if response.status_code in errors:
                    raise LLMError(errors[response.status_code])
                response.raise_for_status()
                body = response.json()
                finish = body["choices"][0].get("finish_reason")
                if finish is not None and finish != "stop":
                    raise LLMError("The model did not complete its structured response. No financial action was executed.")
                raw = body["choices"][0]["message"]["content"]
                usage = body.get("usage", {})
            elif self.config.provider == "ollama":
                response = self.session.post(
                    "http://127.0.0.1:11434/api/chat",
                    timeout=(3, 180),
                    allow_redirects=False,
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": False,
                        "format": schema,
                        "options": {"temperature": 0, "num_predict": 700},
                    },
                )
                response.raise_for_status()
                body = response.json()
                raw = body["message"]["content"]
                usage = {
                    "prompt_tokens": body.get("prompt_eval_count"),
                    "completion_tokens": body.get("eval_count"),
                }
            else:
                raise FinanceError("Unsupported LLM provider.")
            if not isinstance(raw, str) or len(raw) > 20_000:
                raise FinanceError("Model response exceeded the structured-output limit.")
            parsed = json.loads(raw)
            self.calls.append(
                {
                    "model": model,
                    "label": label,
                    "seconds": round(time.monotonic() - start, 3),
                    "usage": usage,
                }
            )
            return parsed
        except FinanceError:
            raise
        except (requests.RequestException, KeyError, ValueError, IndexError) as exc:
            raise LLMError(
                "LLM request failed or returned invalid JSON. Check model access, structured-output support and connection. No action was executed."
            ) from exc
