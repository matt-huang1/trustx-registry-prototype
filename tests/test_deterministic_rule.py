"""The deterministic money-movement rule must override the LLM.

No live LLM calls: a fake provider is injected everywhere. This is the acceptance
test for the hybrid principle — a fact we can pin down beats what the model asserts.
Under the ARC model, money movement IS executing transactions: the rule forces
Action Authority to 3 ("Execute transactions"), and worst-case-wins then yields
Tier 3 (high).
"""

from __future__ import annotations

import json

import jsonschema
import pytest

from classifier.graph import classify, propose
from classifier.provider import LLMProvider
from classifier.rules import MONEY_MOVEMENT_DIMENSION, MONEY_MOVEMENT_FLOOR
from classifier.run import build_entry
from classifier.schema import load_schema
from tests.conftest import make_draft


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


# A draft where the LLM deliberately UNDER-scores action_authority to 1.
LOWBALL_DRAFT = make_draft(action_authority=1)
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
    """Regardless of the mocked LLM's low score, Action Authority is forced to 3."""
    provider = FakeProvider(LOWBALL_DRAFT, NO_FLAGS)
    proposal, llm_draft, notes, _system_type, _autonomy_level = propose(
        description, provider
    )

    # The raw LLM draft stays lowballed for the audit trail...
    assert llm_draft[MONEY_MOVEMENT_DIMENSION]["score"] == 1
    # ...but the deterministic rule overrode the final proposal.
    assert proposal[MONEY_MOVEMENT_DIMENSION]["score"] >= MONEY_MOVEMENT_FLOOR
    assert notes, "deterministic override should have produced a note"


def test_rule_does_not_fire_without_money_movement():
    provider = FakeProvider(LOWBALL_DRAFT, NO_FLAGS)
    proposal, _, notes, _, _ = propose(
        "A chatbot that summarises help articles.", provider
    )
    assert proposal[MONEY_MOVEMENT_DIMENSION]["score"] == 1
    assert notes == []


def test_full_loop_entry_is_schema_valid_and_enforces_rule():
    """End-to-end loop with an auto-approving gate yields a schema-valid Tier 3 entry."""
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
    assert entry["dimensions"][MONEY_MOVEMENT_DIMENSION]["score"] == MONEY_MOVEMENT_FLOOR
    # Action Authority = 3 -> Tier 3 (high) under worst-case-wins, whatever the profile.
    assert entry["risk_tier"] == "high"
    assert MONEY_MOVEMENT_DIMENSION in entry["tier_derivation"]["driving_dimensions"]
    assert (
        entry["challenge"]["flagged"] is True
    )  # deterministic override counts as a flag
    assert entry["provenance"]["approved_by"] == "test-operator"
    assert entry["challenge"]["iterations"] >= 1


def test_floor_forces_tier_3_under_every_committed_profile():
    """action_authority is in every committed profile's tier_dimensions, so the
    money-movement floor yields Tier 3 no matter which system type the LLM picks."""
    from classifier.schema import load_tier_weighting_profiles, roll_up_risk_tier
    from tests.conftest import make_dimensions

    dims = make_dimensions(action_authority=3)
    for name, profile in load_tier_weighting_profiles()["profiles"].items():
        assert MONEY_MOVEMENT_DIMENSION in profile["tier_dimensions"], name
    for system_type in (None, "knowledge_assistant", "transaction_commerce_agent"):
        assert roll_up_risk_tier(dims, system_type) == "high"
