"""The runtime policy gate is deterministic, evidence-citing, and committed offline.

Hermetic: no LLM, no network, no key. These assert the pure decide() function over the
committed registry entries and the committed org policy, and that the generated
web/data/policy.* artifacts are fresh (the offline --check gate CI relies on).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

from classifier.policy_gate import decide

ROOT = Path(__file__).resolve().parent.parent

# scripts/ is not a package; load build_registry by path (mirrors test_examples_build).
_spec = importlib.util.spec_from_file_location(
    "build_registry", ROOT / "scripts" / "build_registry.py"
)
build_registry = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_registry)


def _policy() -> dict:
    return yaml.safe_load(
        (ROOT / "policy" / "example-bank-policy.yaml").read_text(encoding="utf-8")
    )


def _entries_by_tier() -> dict[str, dict]:
    entries = build_registry.load_entries()
    return {e["risk_tier"]: e for e in entries}


def test_low_tier_allows():
    entry = _entries_by_tier()["low"]
    d = decide(entry, _policy())
    assert d["action"] == "allow"
    assert d["tier"] == "low"
    assert d["policy_rule"] == "low → allow"
    assert not d["overrides"]


def test_low_no_driver_entry_reason_says_nothing_rose():
    """A low entry with an (honest) empty driver list must not fall back to citing
    every baseline dimension's evidence — the reason states that nothing rose."""
    entry = _entries_by_tier()["low"]
    assert entry["tier_derivation"]["driving_dimensions"] == []
    d = decide(entry, _policy())
    assert d["evidence_refs"] == []
    assert "no weighted dimension rises above baseline" in d["reason"]


def test_medium_tier_allows_with_logging():
    entry = _entries_by_tier()["medium"]
    d = decide(entry, _policy())
    assert d["action"] == "allow_with_logging"
    assert d["tier"] == "medium"
    assert d["policy_rule"] == "medium → allow_with_logging"
    assert not d["overrides"]


def test_high_tier_escalates_to_human():
    entry = _entries_by_tier()["high"]
    d = decide(entry, _policy())
    assert d["action"] == "escalate_to_human"
    assert d["tier"] == "high"
    assert d["policy_rule"] == "high → escalate_to_human"


def test_adopted_commerce_entry_still_escalates():
    """The gate reads the new tiers unchanged: the adopted transaction/commerce seed
    entry (Tier 3) maps straight to escalate_to_human."""
    entries = {e["agent"]["slug"]: e for e in build_registry.load_entries()}
    d = decide(entries["trustwise-commerce-agent"], _policy())
    assert d["action"] == "escalate_to_human"
    assert d["tier"] == "high"


def test_payments_entry_escalates_and_triggers_money_movement_override():
    """The money-movement high entry both escalates AND trips the capability override."""
    entries = {e["agent"]["slug"]: e for e in build_registry.load_entries()}
    entry = entries["payments-initiation-agent"]
    d = decide(entry, _policy())

    assert d["action"] == "escalate_to_human"
    # The capability override fired, on top of the tier rule.
    caps = [ov["capability"] for ov in d["overrides"]]
    assert "money_movement" in caps
    money = [ov for ov in d["overrides"] if ov["capability"] == "money_movement"][0]
    assert money["action"] == "require_dual_approval"


def test_reason_names_the_driving_evidence():
    """The escalate reason must surface the evidence that drove the tier, not just a label."""
    entries = {e["agent"]["slug"]: e for e in build_registry.load_entries()}
    entry = entries["payments-initiation-agent"]
    d = decide(entry, _policy())

    reason = d["reason"]
    # The reason must NOT restate the tier — the structured 'tier' field owns it, and any
    # display already labels it. It starts from the policy justification instead.
    assert "tier HIGH" not in reason
    assert reason.startswith("Policy requires human approval")
    # An actual evidence quote from the driving dimension is surfaced in the reason.
    assert "ACH and wire" in reason
    assert d["evidence_refs"], "evidence_refs must be populated"
    assert all(ref in " ".join(entry_evidence(entry)) for ref in d["evidence_refs"])
    # The money-movement rule and its dual-approval requirement are named.
    assert "money-movement" in reason.lower()
    assert "dual" in reason.lower()


def entry_evidence(entry: dict) -> list[str]:
    quotes: list[str] = []
    for dim in entry["dimensions"].values():
        quotes.extend(dim.get("evidence", []))
    return quotes


def test_no_llm_or_network_import_in_policy_gate():
    """The gate module must not pull in the provider (its whole point is determinism)."""
    src = (ROOT / "classifier" / "policy_gate.py").read_text(encoding="utf-8")
    assert "provider" not in src
    assert "import openai" not in src


def test_check_passes_offline_on_committed_policy_artifacts():
    """The default --check gate (what CI runs) passes on the committed policy.* files."""
    assert build_registry.main(["--check"]) == 0
