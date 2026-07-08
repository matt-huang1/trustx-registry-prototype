"""Hermetic checks on the curated reference entries (no LLM, no network).

Reuses classifier.schema for validation and the risk_tier rollup — the same single
source of truth the build script uses.
"""

from __future__ import annotations

from pathlib import Path

import jsonschema
import pytest
import yaml

from classifier.schema import load_schema, roll_up_risk_tier

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
def test_stored_tier_matches_computed_rollup(path):
    """One source of truth: the stored tier must equal the computed rollup."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data["risk_tier"] == roll_up_risk_tier(data["dimensions"])


def test_payments_entry_enforces_money_movement_invariant():
    data = _load("payments-initiation-agent.yaml")
    assert data["dimensions"]["delegated_authority"]["score"] >= 4


@pytest.mark.parametrize(
    "name,expected_tier",
    [
        ("internal-document-summarisation-assistant.yaml", "low"),
        ("kyc-onboarding-triage-agent.yaml", "medium"),
        ("payments-initiation-agent.yaml", "high"),
    ],
)
def test_archetypes_roll_up_to_expected_tier(name, expected_tier):
    data = _load(name)
    assert data["risk_tier"] == expected_tier
    assert roll_up_risk_tier(data["dimensions"]) == expected_tier
