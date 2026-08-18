"""The cached classifier examples must be present, valid, and in lockstep — offline.

No LLM calls: these assert over the COMMITTED web/data/examples.* fixtures (produced by
``build_registry.py --rebuild-examples``, an author-run step). This is the offline gate
CI relies on — it proves the page's cached demo data is schema-valid, its tiers match the
rollup, the .js twin is fresh, and the money-movement example still demonstrates the
deterministic floor.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import jsonschema

from classifier.rules import MONEY_MOVEMENT_DIMENSION, MONEY_MOVEMENT_FLOOR
from classifier.schema import derive_risk_tier, load_schema

ROOT = Path(__file__).resolve().parent.parent

# scripts/ is not a package; load build_registry by path.
_spec = importlib.util.spec_from_file_location(
    "build_registry", ROOT / "scripts" / "build_registry.py"
)
build_registry = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_registry)


def test_examples_exist_and_are_schema_valid():
    examples = build_registry.load_examples()
    assert examples, "web/data/examples.json is missing or empty"
    schema = load_schema()
    for ex in examples:
        jsonschema.validate(instance=ex, schema=schema)
        # Stored tier must equal the rollup — one source of truth, same as registry entries.
        derivation = derive_risk_tier(
            ex["dimensions"], ex.get("system_type"), ex.get("autonomy_level")
        )
        assert ex["risk_tier"] == derivation.tier
        assert ex["tier_derivation"] == derivation.as_dict()


def test_cached_example_tier_coverage_is_exactly_what_is_committed():
    """Pins the hero's tier coverage so it can never drift unnoticed.

    This asserted {low, medium, high} until 2026-08-17. Aligning the per-type profiles
    to the paper's all-12 rule (ADR-0019) re-tiered the public-docs example low →
    medium: its control_authority=2 — a score the challenger pass explicitly flagged as
    unsupported, and which the cached run kept — is weighted under the current rule and
    was not under the superseded knowledge_assistant subset. The cached set therefore no
    longer contains a low-tier run.

    The expectation is pinned to the truth rather than relaxed to a subset check, so
    restoring low coverage (an author-run ``--rebuild-examples``, or a new example
    description) fails here and forces this to be updated deliberately.
    """
    examples = build_registry.load_examples()
    tiers = {ex["risk_tier"] for ex in examples}
    assert tiers == {"medium", "high"}, f"cached example tiers changed: {tiers}"


def test_the_hero_still_spans_tiers_and_includes_the_money_movement_case():
    """What the coverage above exists FOR: the hero must show more than one outcome,
    and must include the high-tier case that demonstrates the deterministic floor."""
    examples = build_registry.load_examples()
    tiers = {ex["risk_tier"] for ex in examples}
    assert "high" in tiers
    assert len(tiers) >= 2, f"the hero would show a single outcome: {tiers}"


def test_examples_js_is_the_committed_json_twin():
    examples = build_registry.load_examples()
    expected_js = build_registry.render_examples_js(examples)
    assert build_registry.OUTPUT_EXAMPLES_JS.read_text(encoding="utf-8") == expected_js


def test_money_movement_example_shows_the_deterministic_floor():
    """The high example must prove the floor holds on real classifier output."""
    examples = build_registry.load_examples()
    high = [ex for ex in examples if ex["risk_tier"] == "high"]
    assert high, "expected a high-tier cached example"
    ex = high[0]
    aa = ex["dimensions"][MONEY_MOVEMENT_DIMENSION]
    assert aa["score"] >= MONEY_MOVEMENT_FLOOR
    # The override must be visible in the audit trail (evidence marker + challenge note).
    assert any("deterministic-rule" in e for e in aa["evidence"])
    assert any(n.startswith("Deterministic override") for n in ex["challenge"]["notes"])


def test_check_passes_offline():
    """The default --check gate (what CI runs) passes on the committed artifacts."""
    assert build_registry.main(["--check"]) == 0
