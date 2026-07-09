"""The live classify endpoint's core is offline-testable with an injected fake LLM.

We exercise ``classify_to_payload`` (the pure function the HTTP handler calls) — no server,
no network. It must (a) run the real maker/checker loop, (b) enforce the deterministic
money-movement floor on unseen input, and (c) NEVER claim human ratification: the payload
flags ``ratification_required`` and provenance stays unratified.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from classifier.provider import LLMProvider
from classifier.rules import MONEY_MOVEMENT_FLOOR

ROOT = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "serve_classify", ROOT / "scripts" / "serve_classify.py"
)
serve_classify = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(serve_classify)


class FakeProvider:
    """Same shape as tests/test_deterministic_rule.py — canned JSON, no network."""

    def __init__(self, proposer_json: dict, challenge_json: dict) -> None:
        self._proposer = json.dumps(proposer_json)
        self._challenge = json.dumps(challenge_json)

    def complete(self, system: str, user: str) -> str:
        if "skeptical reviewer" in system:
            return self._challenge
        return self._proposer


LOWBALL_DRAFT = {
    "autonomy": {"score": 2, "rationale": "acts with confirmation", "evidence": ["desc"]},
    "delegated_authority": {
        "score": 1,
        "rationale": "no authority",
        "evidence": ["desc"],
    },
    "tool_access": {"score": 2, "rationale": "few tools", "evidence": ["desc"]},
    "data_exposure": {"score": 2, "rationale": "limited data", "evidence": ["desc"]},
}
NO_FLAGS = {"flagged": False, "notes": []}


def test_fake_provider_satisfies_the_protocol():
    assert isinstance(FakeProvider(LOWBALL_DRAFT, NO_FLAGS), LLMProvider)


def test_money_movement_floor_holds_on_the_live_path():
    provider = FakeProvider(LOWBALL_DRAFT, NO_FLAGS)
    payload = serve_classify.classify_to_payload(
        "An agent that will initiate payment to suppliers over ACH.", provider
    )
    entry = payload["entry"]
    # Deterministic floor applies to unseen input even though the LLM lowballed to 1.
    assert entry["dimensions"]["delegated_authority"]["score"] >= MONEY_MOVEMENT_FLOOR
    assert entry["risk_tier"] == "high"
    assert payload[
        "deterministic_notes"
    ], "the override should be reported for the banner"


def test_live_result_is_never_claimed_as_ratified():
    provider = FakeProvider(LOWBALL_DRAFT, NO_FLAGS)
    payload = serve_classify.classify_to_payload(
        "A chatbot that summarises articles.", provider
    )
    assert payload["ratification_required"] is True
    # The human gate is represented, not dropped: nobody ratified this.
    assert payload["entry"]["provenance"]["approved_by"] is None
