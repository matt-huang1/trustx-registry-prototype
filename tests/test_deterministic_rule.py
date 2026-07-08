"""The deterministic money-movement rule must override the LLM.

No live LLM calls: a fake provider is injected everywhere. This is the acceptance
test for the hybrid principle — a fact we can pin down beats what the model asserts.
"""

from __future__ import annotations

import json

import jsonschema
import pytest

from classifier.graph import classify, propose
from classifier.provider import LLMProvider
from classifier.rules import MONEY_MOVEMENT_FLOOR
from classifier.run import build_entry
from classifier.schema import load_schema


class FakeProvider:
    """Satisfies the LLMProvider protocol; returns canned JSON, never hits network.

    Distinguishes the proposer call from the challenger call by the system prompt so
    it works regardless of how many proposer iterations run.
    """

    def __init__(self, proposer_json: dict, challenge_json: dict) -> None:
        self._proposer = json.dumps(proposer_json)
        self._challenge = json.dumps(challenge_json)
        self.calls = 0

    def complete(self, system: str, user: str) -> str:
        self.calls += 1
        if "skeptical reviewer" in system:
            return self._challenge
        return self._proposer


# A draft where the LLM deliberately UNDER-scores delegated_authority to 1.
LOWBALL_DRAFT = {
    "autonomy": {"score": 2, "rationale": "acts with confirmation", "evidence": ["desc"]},
    "delegated_authority": {
        "score": 1,
        "rationale": "no real authority",
        "evidence": ["desc"],
    },
    "tool_access": {"score": 2, "rationale": "few tools", "evidence": ["desc"]},
    "data_exposure": {"score": 2, "rationale": "limited data", "evidence": ["desc"]},
}
NO_FLAGS = {"flagged": False, "notes": []}

MONEY_DESCRIPTIONS = [
    "An agent that reads invoices and will initiate payment to vendors.",
    "It can transfer funds between the treasury accounts nightly.",
    "Handles payroll via ACH runs each fortnight.",
]


def test_fake_provider_is_a_valid_llm_provider():
    assert isinstance(FakeProvider(LOWBALL_DRAFT, NO_FLAGS), LLMProvider)


@pytest.mark.parametrize("description", MONEY_DESCRIPTIONS)
def test_money_movement_rule_overrides_lowball_llm(description):
    """Regardless of the mocked LLM's low score, delegated_authority is forced up."""
    provider = FakeProvider(LOWBALL_DRAFT, NO_FLAGS)
    proposal, llm_draft, notes = propose(description, provider)

    # The raw LLM draft stays lowballed for the audit trail...
    assert llm_draft["delegated_authority"]["score"] == 1
    # ...but the deterministic rule overrode the final proposal.
    assert proposal["delegated_authority"]["score"] >= MONEY_MOVEMENT_FLOOR
    assert notes, "deterministic override should have produced a note"


def test_rule_does_not_fire_without_money_movement():
    provider = FakeProvider(LOWBALL_DRAFT, NO_FLAGS)
    proposal, _, notes = propose("A chatbot that summarises help articles.", provider)
    assert proposal["delegated_authority"]["score"] == 1
    assert notes == []


def test_full_loop_entry_is_schema_valid_and_enforces_rule():
    """End-to-end loop with an auto-approving gate yields a schema-valid entry."""
    provider = FakeProvider(LOWBALL_DRAFT, NO_FLAGS)

    def auto_approve(state):
        return {"decision": "approve", "approved_by": "test-operator"}

    state = classify(
        "An agent that will initiate payment to suppliers automatically.",
        provider,
        human_gate=auto_approve,
    )
    entry = build_entry(state, slug="invoice-payer", approver=state["approved_by"])

    jsonschema.validate(instance=entry, schema=load_schema())
    assert entry["dimensions"]["delegated_authority"]["score"] >= MONEY_MOVEMENT_FLOOR
    assert (
        entry["challenge"]["flagged"] is True
    )  # deterministic override counts as a flag
    assert entry["provenance"]["approved_by"] == "test-operator"
    assert entry["challenge"]["iterations"] >= 1
