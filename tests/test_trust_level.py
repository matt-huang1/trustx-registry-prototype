"""Trust levels: the entry-review axis, its labelling rules, and the build-time
guarantee that a 'verified' (or 'working-group-reviewed') label can never be minted
without an identified human reviewer.

Hermetic: no LLM, no network, no key. Covers the schema field, the committed entries'
levels, the build_registry enforcement (a verified entry with a null reviewer fails the
build), and the classifier's default (a fresh classification enters community-submitted).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

from classifier.run import build_entry
from classifier.schema import DIMENSIONS

from tests.conftest import make_dimensions

ROOT = Path(__file__).resolve().parent.parent
ENTRIES_DIR = ROOT / "entries"

# scripts/ is not a package; load build_registry by path (mirrors test_policy_gate).
_spec = importlib.util.spec_from_file_location(
    "build_registry", ROOT / "scripts" / "build_registry.py"
)
build_registry = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_registry)

TRUST_LEVELS = {"community-submitted", "working-group-reviewed", "verified"}
REVIEWED_LEVELS = {"working-group-reviewed", "verified"}

ENTRY_PATHS = sorted(ENTRIES_DIR.glob("*.yaml"))


def _load(name: str) -> dict:
    return yaml.safe_load((ENTRIES_DIR / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", ENTRY_PATHS, ids=lambda p: p.name)
def test_every_entry_carries_a_valid_trust_level_and_review(path):
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert data["trust_level"] in TRUST_LEVELS
    review = data["review"]
    assert set(review) == {"reviewed_by", "reviewed_at", "expires_at"}


@pytest.mark.parametrize("path", ENTRY_PATHS, ids=lambda p: p.name)
def test_reviewed_entries_name_a_human_reviewer(path):
    """The core invariant: a working-group-reviewed / verified entry MUST record a
    reviewer. community-submitted entries may have a null reviewer."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data["trust_level"] in REVIEWED_LEVELS:
        assert data["review"]["reviewed_by"], f"{path.name}: reviewed but no reviewer"
        assert data["review"][
            "expires_at"
        ], f"{path.name}: reviewed but no freshness horizon"


@pytest.mark.parametrize(
    "name,expected",
    [
        # The three adopted RAI seed entries enter VERIFIED (published reference material).
        ("trustwise-commerce-agent.yaml", "verified"),
        ("internal-knowledge-assistant.yaml", "verified"),
        ("invoice-triage-agent.yaml", "verified"),
        # The three curated archetypes enter WORKING-GROUP-REVIEWED (hand-authored, ratified).
        ("kyc-onboarding-triage-agent.yaml", "working-group-reviewed"),
        ("internal-document-summarisation-assistant.yaml", "working-group-reviewed"),
        ("payments-initiation-agent.yaml", "working-group-reviewed"),
    ],
)
def test_seed_and_archetype_trust_levels(name, expected):
    assert _load(name)["trust_level"] == expected


def test_verified_seed_entries_note_their_provenance():
    """A verified entry must say WHY it is trusted — traceable to RAI reference material."""
    for name in (
        "trustwise-commerce-agent.yaml",
        "internal-knowledge-assistant.yaml",
        "invoice-triage-agent.yaml",
    ):
        note = _load(name)["provenance"].get("note", "")
        assert "RAI" in note and "verified" in note.lower()


# --- The build-time guarantee: no human reviewer ⇒ cannot be verified -------------
def _verified_entry_without_reviewer() -> dict:
    """A schema-valid entry that CLAIMS verified but records no reviewer."""
    return {
        "agent": {
            "slug": "sockpuppet-verified",
            "description": "claims verified with no reviewer",
        },
        "dimensions": make_dimensions(),
        "risk_tier": "low",
        "tier_derivation": {
            "profile": "recommended_default",
            "tier_dimensions": list(DIMENSIONS),
            "driving_dimensions": [],
            "autonomy_level_driven": False,
        },
        "trust_level": "verified",
        "review": {"reviewed_by": None, "reviewed_at": None, "expires_at": None},
        "provenance": {
            "submitted_by": "attacker",
            "approved_by": None,
            "timestamp": "2026-07-11T00:00:00+00:00",
        },
    }


def test_build_fails_when_verified_entry_has_no_reviewer():
    entry = _verified_entry_without_reviewer()
    with pytest.raises(SystemExit) as exc:
        build_registry.enforce_trust_rules(entry, "sockpuppet.yaml")
    assert exc.value.code == 1


def test_build_fails_when_working_group_reviewed_has_no_reviewer():
    entry = _verified_entry_without_reviewer()
    entry["trust_level"] = "working-group-reviewed"
    with pytest.raises(SystemExit):
        build_registry.enforce_trust_rules(entry, "sockpuppet.yaml")


def test_community_submitted_may_have_a_null_reviewer():
    entry = _verified_entry_without_reviewer()
    entry["trust_level"] = "community-submitted"
    # Must NOT raise — community-submitted is exactly the no-reviewer state.
    build_registry.enforce_trust_rules(entry, "ok.yaml")


def test_full_build_check_passes_with_committed_entries():
    """The committed registry (verified seeds + reviewed archetypes) survives --check."""
    assert build_registry.main(["--check"]) == 0


# --- The classifier default: a fresh classification is community-submitted ---------
def test_fresh_classification_enters_community_submitted():
    state = {
        "description": "an agent",
        "proposal": make_dimensions(),
        "system_type": None,
        "autonomy_level": 1,
        "iterations": 1,
    }
    entry = build_entry(state, slug="fresh", approver="operator-x")
    assert entry["trust_level"] == "community-submitted"
    assert entry["review"] == {
        "reviewed_by": None,
        "reviewed_at": None,
        "expires_at": None,
    }
