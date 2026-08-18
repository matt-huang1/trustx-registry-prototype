"""Hermetic checks on the committed reference entries (no LLM, no network).

Reuses classifier.schema for validation and the risk-tier rollup — the same single
source of truth the build script uses. Covers both the hand-scored archetypes and
the three seed entries adopted from the RAI ARC reference registry, whose published
overall tiers must reproduce under our rollup with their per-type profiles.
"""

from __future__ import annotations

from pathlib import Path

import jsonschema
import pytest
import yaml

from classifier.schema import DIMENSIONS, derive_risk_tier, load_schema

ENTRIES_DIR = Path(__file__).resolve().parent.parent / "entries"
ENTRY_PATHS = sorted(ENTRIES_DIR.glob("*.yaml"))


def _load(name: str) -> dict:
    return yaml.safe_load((ENTRIES_DIR / name).read_text(encoding="utf-8"))


def test_there_are_reference_entries():
    assert ENTRY_PATHS, "expected curated entries in entries/*.yaml"


@pytest.mark.parametrize("path", ENTRY_PATHS, ids=lambda p: p.name)
def test_entry_validates_against_schema(path):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    jsonschema.validate(instance=data, schema=load_schema())


@pytest.mark.parametrize("path", ENTRY_PATHS, ids=lambda p: p.name)
def test_all_12_dimensions_are_always_scored_with_evidence(path):
    """Scoring is total: every entry scores every ARC dimension, with evidence."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert set(data["dimensions"]) == set(DIMENSIONS)
    for dim_id, dim in data["dimensions"].items():
        assert dim["evidence"], f"{path.name}: {dim_id} has no evidence"


@pytest.mark.parametrize("path", ENTRY_PATHS, ids=lambda p: p.name)
def test_stored_tier_and_derivation_match_computed_rollup(path):
    """One source of truth: the stored tier AND recorded driver must equal the rollup."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    derivation = derive_risk_tier(
        data["dimensions"], data.get("system_type"), data.get("autonomy_level")
    )
    assert data["risk_tier"] == derivation.tier
    assert data["tier_derivation"] == derivation.as_dict()


def test_payments_entry_enforces_money_movement_invariant():
    """Money movement == Action Authority 3 ("Execute transactions") -> Tier 3."""
    data = _load("payments-initiation-agent.yaml")
    assert data["dimensions"]["action_authority"]["score"] == 3
    assert data["risk_tier"] == "high"
    assert "action_authority" in data["tier_derivation"]["driving_dimensions"]


@pytest.mark.parametrize(
    "name,system_type,expected_tier",
    [
        (
            "internal-document-summarisation-assistant.yaml",
            "knowledge_assistant",
            "medium",
        ),
        ("kyc-onboarding-triage-agent.yaml", "tool_using_agent", "high"),
        (
            "payments-initiation-agent.yaml",
            "transaction_commerce_agent",
            "high",
        ),
    ],
)
def test_archetypes_carry_their_system_type_and_tier(name, system_type, expected_tier):
    data = _load(name)
    assert data["system_type"] == system_type
    assert data["risk_tier"] == expected_tier


def test_kyc_archetype_embodies_the_weighting_finding_as_resolved_history():
    """The KYC agent scores data_sensitivity=3 (regulated PII) and now tiers HIGH.

    It tiered medium until 2026-08-17, when the per-type profiles were aligned to the
    paper's Section 3.3 all-12 rule after RAI confirmed the v1.1 subset formulas are
    outdated (ADR-0019). Both halves are asserted on the one entry: the live tier under
    the current rule, and — on the same unchanged scores — the medium the superseded
    weighting produced. The finding survives its own resolution as a regression test.
    """
    data = _load("kyc-onboarding-triage-agent.yaml")
    assert data["dimensions"]["data_sensitivity"]["score"] == 3

    # Current rule: data_sensitivity is weighted, and it alone forces Tier 3.
    assert data["risk_tier"] == "high"
    assert "data_sensitivity" in data["tier_derivation"]["tier_dimensions"]
    assert data["tier_derivation"]["driving_dimensions"] == ["data_sensitivity"]
    assert derive_risk_tier(data["dimensions"], system_type=None).tier == "high"

    # Superseded v1.1 weighting, same numbers: medium, driven by blast_radius.
    legacy = derive_risk_tier(
        data["dimensions"], system_type="legacy_tool_using_agent_v1_1"
    )
    assert legacy.tier == "medium"
    assert "data_sensitivity" not in legacy.tier_dimensions
    assert legacy.driving_dimensions == ("blast_radius",)


@pytest.mark.parametrize(
    "name,registry_id,expected_tier",
    [
        ("trustwise-commerce-agent.yaml", "RAI-OPEN-0001", "high"),
        ("internal-knowledge-assistant.yaml", "RAI-OPEN-0002", "low"),
        ("invoice-triage-agent.yaml", "RAI-OPEN-0003", "medium"),
    ],
)
def test_adopted_seed_entries_reproduce_their_published_tiers(
    name, registry_id, expected_tier
):
    """The published overall tier (Tier 3/1/2) must reproduce under OUR rollup with
    the entry's per-type tier-weighting profile — adopted, then re-derived."""
    data = _load(name)
    assert data["agent"]["registry_id"] == registry_id
    assert data["provenance"]["submitted_by"] == "RAI-ARC-reference"
    derivation = derive_risk_tier(
        data["dimensions"], data["system_type"], data["autonomy_level"]
    )
    assert derivation.tier == expected_tier
    assert data["risk_tier"] == expected_tier
    assert data["tier_derivation"]["profile"] == data["system_type"]
