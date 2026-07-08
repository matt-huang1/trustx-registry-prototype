"""Thin, model-agnostic LLM interface.

This is the ONLY place in the codebase that talks to an LLM. Everything downstream
depends on the small :class:`LLMProvider` protocol below, so the concrete model can
be swapped without touching any classifier logic. See docs/adr/0002-*.md.

Configuration is read entirely from environment variables — no provider name, base
URL, or model id is hard-coded anywhere else:

    LLM_BASE_URL   OpenAI-compatible base URL   (default: https://api.openai.com/v1)
    LLM_API_KEY    API key / token              (required for live calls)
    LLM_MODEL      Model name                   (default: gpt-4o-mini)

Because we use an OpenAI-*compatible* client, pointing at an open-weight or on-prem
model is a config change only — no code change:

    # OpenAI (default)
    export LLM_BASE_URL="https://api.openai.com/v1"
    export LLM_API_KEY="sk-..."
    export LLM_MODEL="gpt-4o-mini"

    # An open-weight model via OpenRouter (e.g. GLM-5.2)
    export LLM_BASE_URL="https://openrouter.ai/api/v1"
    export LLM_API_KEY="sk-or-..."
    export LLM_MODEL="z-ai/glm-5.2"

    # A local Ollama endpoint (fully offline / on-prem)
    export LLM_BASE_URL="http://localhost:11434/v1"
    export LLM_API_KEY="ollama"          # Ollama ignores the key but the client wants one
    export LLM_MODEL="llama3.1"

Tests never construct a live provider; they inject a fake that satisfies the same
:class:`LLMProvider` protocol (see tests/).
"""

from __future__ import annotations

import os
from typing import Protocol, runtime_checkable

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"


@runtime_checkable
class LLMProvider(Protocol):
    """Minimal LLM surface the classifier depends on.

    Any object with a matching ``complete`` method — the real client or a test
    fake — is a valid provider. Keeping this deliberately tiny is what makes the
    system model-agnostic and offline-testable.
    """

    def complete(self, system: str, user: str) -> str:
        """Return the model's text completion for a system + user prompt."""
        ...


class OpenAICompatibleProvider:
    """Concrete provider backed by any OpenAI-compatible chat-completions API.

    All connection details come from the environment (see module docstring). The
    ``openai`` client is imported lazily so that importing this module — and thus
    running the offline test suite — never requires the dependency or a network.
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.base_url = base_url or os.environ.get("LLM_BASE_URL", DEFAULT_BASE_URL)
        self.api_key = api_key or os.environ.get("LLM_API_KEY")
        self.model = model or os.environ.get("LLM_MODEL", DEFAULT_MODEL)
        if not self.api_key:
            raise RuntimeError(
                "No LLM API key found. Set LLM_API_KEY (and optionally LLM_BASE_URL / "
                "LLM_MODEL) in the environment, or inject a fake provider in tests."
            )
        self._client = None  # lazily created on first call

    def _ensure_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:  # pragma: no cover - env-dependent
                raise RuntimeError(
                    "The 'openai' package is required for live LLM calls. "
                    "Install it with: pip install -e '.[dev]'"
                ) from exc
            self._client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        return self._client

    def complete(self, system: str, user: str) -> str:
        client = self._ensure_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0,
        )
        return response.choices[0].message.content or ""


def provider_from_env() -> LLMProvider:
    """Build the default provider from environment variables."""
    return OpenAICompatibleProvider()
