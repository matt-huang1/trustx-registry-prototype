"""The rollup separates SCORING (always all 12) from TIER WEIGHTING (per-type profile).

Hermetic: pure functions over the committed policy/tier_weighting_profiles.yaml — no
LLM, no network.

Every LIVE per-type profile now implements the current rule (the paper's Section 3.3:
worst-case-wins over all 12 plus the autonomy provisions) after RAI confirmed on
2026-08-16 that the v1.1 per-type five-dimension formulas are outdated (ADR-0019). The
superseded subsets survive as inert ``legacy_<type>_v1_1`` profiles, and this file keeps
the divergence finding alive against them: the SAME Data Sensitivity = 3 numbers that
tier high under the current rule tier low under the legacy knowledge profile. That is
now a regression-proof statement of history rather than a live disagreement.
"""

from __future__ import annotations

from classifier.schema import (
    DIMENSIONS,
    derive_risk_tier,
    load_tier_weighting_profiles,
    resolve_profile,
    roll_up_risk_tier,
)
from tests.conftest import make_dimensions

# The five "critical dimensions" the v1.1 per-type classification tools tiered most
# system types off. Superseded (ADR-0019); preserved as legacy_*_v1_1 profiles.
LEGACY_V1_1_PROFILE_DIMS = (
    "autonomy",
    "action_authority",
    "blast_radius",
    "persistence",
    "reversibility",
)

# The system types that carry a live profile of their own in the committed YAML.
LIVE_SYSTEM_TYPE_PROFILES = (
    "autonomous_agent",
    "coding_assistant",
    "decision_support_system",
    "embedded_physical_ai",
    "knowledge_assistant",
    "tool_using_agent",
    "transaction_commerce_agent",
)


# --------------------------------------------------------------------------- #
# Profiles are data
# --------------------------------------------------------------------------- #
def test_profiles_load_from_committed_yaml():
    loaded = load_tier_weighting_profiles()
    assert loaded["default_profile"] == "recommended_default"
    default = loaded["profiles"]["recommended_default"]
    # The recommended default weights ALL 12 scored dimensions.
    assert set(default["tier_dimensions"]) == set(DIMENSIONS)
    assert default["autonomy_rule"] == "arc_paper"


def test_every_live_profile_implements_the_current_all_12_rule():
    """ADR-0019: after RAI's confirmation, no live per-type profile tiers off a subset.

    A per-type profile that quietly reintroduced a subset would silently re-tier
    entries, so this asserts the current rule over EVERY live profile — not just the
    recommended default.
    """
    profiles = load_tier_weighting_profiles()["profiles"]
    live = {n: p for n, p in profiles.items() if not n.startswith("legacy_")}
    assert set(live) == {*LIVE_SYSTEM_TYPE_PROFILES, "recommended_default"}
    for name, prof in live.items():
        assert set(prof["tier_dimensions"]) == set(DIMENSIONS), name
        assert prof["autonomy_rule"] == "arc_paper", name


def test_legacy_v1_1_profiles_are_retained_verbatim_and_inert():
    """The superseded v1.1 weighting stays inspectable, but tiers no live entry.

    ``resolve_profile`` only ever selects a profile whose key IS the system type, and
    no ARC system type is named ``legacy_*``, so these can never silently apply.
    """
    profiles = load_tier_weighting_profiles()["profiles"]
    for system_type in LIVE_SYSTEM_TYPE_PROFILES:
        legacy = profiles[f"legacy_{system_type}_v1_1"]
        if system_type == "transaction_commerce_agent":
            # The one type whose v1.1 tool already weighted all 12 + the autonomy level.
            assert set(legacy["tier_dimensions"]) == set(DIMENSIONS)
            assert legacy["autonomy_rule"] == "arc_paper"
        else:
            assert legacy["tier_dimensions"] == LEGACY_V1_1_PROFILE_DIMS
            assert legacy["autonomy_rule"] == "none"
        # Inert: asking for the system type resolves to the CURRENT profile.
        assert resolve_profile(system_type)[0] == system_type


def test_missing_or_unknown_system_type_uses_the_default_profile():
    name, _ = resolve_profile(None)
    assert name == "recommended_default"
    # code_content_generator is a valid ARC system type with no committed profile.
    name, _ = resolve_profile("code_content_generator")
    assert name == "recommended_default"


# --------------------------------------------------------------------------- #
# Worst-case-wins over the profile's tier_dimensions
# --------------------------------------------------------------------------- #
def test_all_baseline_is_low():
    assert roll_up_risk_tier(make_dimensions()) == "low"


def test_all_baseline_has_no_driving_dimensions():
    """A low tier has no driver: the tier is low because NOTHING rose above
    baseline, so no dimension can honestly be said to have driven it."""
    d = derive_risk_tier(make_dimensions())
    assert d.tier == "low"
    assert d.driving_dimensions == ()


def test_low_tier_with_an_unweighted_2_still_has_no_driver():
    """An elevated score OUTSIDE the profile neither sets the tier nor drives it.

    No live profile weights a subset any more (ADR-0019), so the subset behaviour is
    exercised through the retained legacy profile — the mechanism still has to work,
    since a working group may deliberately commit a narrower profile in future.
    """
    dims = make_dimensions(data_sensitivity=2)  # not in the legacy knowledge profile
    d = derive_risk_tier(dims, system_type="legacy_knowledge_assistant_v1_1")
    assert d.tier == "low"
    assert d.driving_dimensions == ()


def test_any_dimension_at_3_forces_high_under_the_default_profile():
    for dim in DIMENSIONS:
        assert roll_up_risk_tier(make_dimensions(**{dim: 3})) == "high", dim


def test_max_2_is_medium():
    assert roll_up_risk_tier(make_dimensions(persistence=2)) == "medium"


def test_average_at_least_1_5_is_medium():
    # Half the dimensions at 2: average exactly 1.5, no dimension at 3.
    twos = dict.fromkeys(DIMENSIONS[:6], 2)
    assert roll_up_risk_tier(make_dimensions(**twos)) == "medium"


def test_scoring_is_always_all_12_but_weighting_is_the_profile():
    """A 3 OUTSIDE the profile's tier_dimensions never drives the tier."""
    dims = make_dimensions(data_egress_paths=3)  # not in the legacy knowledge profile
    assert "data_egress_paths" not in LEGACY_V1_1_PROFILE_DIMS
    assert roll_up_risk_tier(dims, system_type="legacy_knowledge_assistant_v1_1") == "low"
    # The same scores tier high the moment the weighting covers all 12.
    assert roll_up_risk_tier(dims) == "high"


# --------------------------------------------------------------------------- #
# THE FINDING, now history: Data Sensitivity 3 on a knowledge asset
# --------------------------------------------------------------------------- #
def test_legacy_v1_1_weighting_tiers_a_data_sensitivity_3_knowledge_asset_low():
    """The historical divergence, preserved as a regression-proof fact.

    The v1.1 per-type classification tools tiered most system types off 5 dimensions
    while the published paper (Section 3.3) states worst-case-wins across all 12. RAI
    confirmed on 2026-08-16 that the subset formulas are an outdated version of the
    model, so the live knowledge_assistant profile now tiers a knowledge assistant over
    regulated (crown-jewel) data at Tier 3. These are the SAME numbers that the
    superseded weighting placed at Tier 1 — the finding does not disappear because it
    was resolved; it is kept here so a regression back to the subset would fail loudly.
    See docs/adr/0012-*.md and docs/adr/0019-*.md.
    """
    dims = make_dimensions(data_sensitivity=3)

    # Current rule — under the default AND under the live per-type profile.
    default = derive_risk_tier(dims, system_type=None)
    assert default.tier == "high"
    assert default.profile == "recommended_default"
    assert default.driving_dimensions == ("data_sensitivity",)

    current = derive_risk_tier(dims, system_type="knowledge_assistant")
    assert current.tier == "high"
    assert current.profile == "knowledge_assistant"
    assert "data_sensitivity" in current.tier_dimensions
    assert current.driving_dimensions == ("data_sensitivity",)

    # Superseded v1.1 weighting — the divergence, on the same numbers.
    legacy = derive_risk_tier(dims, system_type="legacy_knowledge_assistant_v1_1")
    assert legacy.tier == "low"
    assert legacy.profile == "legacy_knowledge_assistant_v1_1"
    assert "data_sensitivity" not in legacy.tier_dimensions
    # Low under that profile meant nothing weighted rose — so nothing drove it.
    assert legacy.driving_dimensions == ()


# --------------------------------------------------------------------------- #
# The ARC paper's autonomy-level rule (Section 3.3; ADR-0017)
# --------------------------------------------------------------------------- #
def test_autonomy_level_5_forces_high_under_the_recommended_default():
    dims = make_dimensions()
    d = derive_risk_tier(dims, system_type=None, autonomy_level=5)
    assert d.profile == "recommended_default"
    assert d.tier == "high"
    assert d.autonomy_level_driven is True
    assert d.autonomy_level_lifted is False
    assert d.driving_dimensions == ()  # nothing scored 3; autonomy level alone drove it


def test_autonomy_level_5_forces_high_under_transaction_commerce():
    """Preserves the prior use_autonomy_level intent (old level 3 == new L5)."""
    dims = make_dimensions()
    d = derive_risk_tier(dims, "transaction_commerce_agent", autonomy_level=5)
    assert d.tier == "high"
    assert d.autonomy_level_driven is True


def test_autonomy_level_4_lifts_an_all_baseline_entry_to_medium():
    dims = make_dimensions()
    d = derive_risk_tier(dims, system_type=None, autonomy_level=4)
    assert d.tier == "medium"
    assert d.autonomy_level_lifted is True
    assert d.autonomy_level_driven is False
    assert d.driving_dimensions == ()  # the lift, not a dimension, set the tier


def test_autonomy_level_3_lifts_an_all_baseline_entry_to_medium():
    dims = make_dimensions()
    d = derive_risk_tier(dims, system_type=None, autonomy_level=3)
    assert d.tier == "medium"
    assert d.autonomy_level_lifted is True


def test_autonomy_level_4_never_lowers_a_dimension_derived_tier():
    high = derive_risk_tier(make_dimensions(action_authority=3), None, autonomy_level=4)
    assert high.tier == "high"
    assert high.autonomy_level_lifted is False  # nothing to lift: dims already above low
    assert high.driving_dimensions == ("action_authority",)
    medium = derive_risk_tier(make_dimensions(persistence=2), None, autonomy_level=4)
    assert medium.tier == "medium"
    assert medium.autonomy_level_lifted is False


def test_autonomy_level_is_ignored_by_profiles_with_rule_none():
    """``autonomy_rule: none`` is still honoured — exercised via a legacy profile,
    the only remaining place it is set (every live profile is arc_paper, ADR-0019)."""
    dims = make_dimensions()
    d = derive_risk_tier(dims, "legacy_knowledge_assistant_v1_1", autonomy_level=5)
    assert d.tier == "low"
    assert d.autonomy_level_driven is False
    assert d.autonomy_level_lifted is False


def test_autonomy_level_5_now_forces_high_for_every_live_system_type():
    """Under the current rule the autonomy provisions apply to all types, not just
    transaction/commerce — the second half of the ADR-0019 alignment."""
    for system_type in LIVE_SYSTEM_TYPE_PROFILES:
        d = derive_risk_tier(make_dimensions(), system_type, autonomy_level=5)
        assert d.tier == "high", system_type
        assert d.autonomy_level_driven is True, system_type


# --------------------------------------------------------------------------- #
# The derivation is inspectable
# --------------------------------------------------------------------------- #
def test_derivation_records_profile_weighting_and_driver():
    """The KYC archetype's numbers: the derivation names the profile and the driver."""
    dims = make_dimensions(blast_radius=2, data_sensitivity=3)
    d = derive_risk_tier(dims, system_type="tool_using_agent")
    assert d.tier == "high"  # data_sensitivity=3 is weighted under the current rule
    assert d.profile == "tool_using_agent"
    assert set(d.tier_dimensions) == set(DIMENSIONS)
    assert d.driving_dimensions == ("data_sensitivity",)
    as_dict = d.as_dict()
    assert as_dict["profile"] == "tool_using_agent"
    assert as_dict["driving_dimensions"] == ["data_sensitivity"]
    assert as_dict["autonomy_level_driven"] is False
    assert as_dict["autonomy_level_lifted"] is False


def test_derivation_under_the_legacy_profile_records_the_narrower_weighting():
    """Same numbers, superseded weighting: a narrower tier_dimensions set and a
    different driver. This is the data the web view's "scored · not tier-weighted"
    cell state renders from — ``data_sensitivity`` is scored but absent from
    ``tier_dimensions`` — so the marker logic stays covered now that no live entry
    exhibits it (ADR-0019)."""
    dims = make_dimensions(blast_radius=2, data_sensitivity=3)
    d = derive_risk_tier(dims, system_type="legacy_tool_using_agent_v1_1")
    assert d.tier == "medium"
    assert set(d.tier_dimensions) == set(LEGACY_V1_1_PROFILE_DIMS)
    assert d.driving_dimensions == ("blast_radius",)
    # The marker's precondition: scored, but outside the weighted set.
    assert "data_sensitivity" in dims
    assert "data_sensitivity" not in d.as_dict()["tier_dimensions"]
