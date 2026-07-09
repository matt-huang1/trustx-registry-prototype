"""The rollup separates SCORING (always all 12) from TIER WEIGHTING (per-type profile).

Hermetic: pure functions over the committed policy/tier_weighting_profiles.yaml — no
LLM, no network. This file carries the acceptance test for the divergence finding: a
Data Sensitivity = 3 knowledge asset is Tier 3 (high) under the recommended all-12
default profile but NOT under the 5-dimension knowledge_assistant profile.
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

KNOWLEDGE_PROFILE_DIMS = (
    "autonomy",
    "action_authority",
    "blast_radius",
    "persistence",
    "reversibility",
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
    assert loaded["profiles"]["knowledge_assistant"]["tier_dimensions"] == (
        KNOWLEDGE_PROFILE_DIMS
    )
    assert loaded["profiles"]["transaction_commerce_agent"]["use_autonomy_level"] is True


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
    """An elevated score OUTSIDE the profile neither sets the tier nor drives it."""
    dims = make_dimensions(data_sensitivity=2)  # not in the knowledge profile
    d = derive_risk_tier(dims, system_type="knowledge_assistant")
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
    dims = make_dimensions(data_egress_paths=3)  # not in the knowledge profile
    assert "data_egress_paths" not in KNOWLEDGE_PROFILE_DIMS
    assert roll_up_risk_tier(dims, system_type="knowledge_assistant") == "low"
    # The same scores tier high the moment the weighting covers all 12.
    assert roll_up_risk_tier(dims) == "high"


# --------------------------------------------------------------------------- #
# THE FINDING: Data Sensitivity 3 on a knowledge asset
# --------------------------------------------------------------------------- #
def test_data_sensitivity_3_knowledge_asset_is_high_by_default_but_not_under_knowledge_profile():
    """The AEGIS-derived per-type profiles tier most types off 5 dimensions while the
    reference registry states worst-case-wins across all 12. This is the concrete
    consequence: a knowledge assistant over regulated (crown-jewel) data is Tier 3
    under the recommended all-12 default, but NOT under the 5-dimension knowledge
    profile — see docs/adr/0012-*.md."""
    dims = make_dimensions(data_sensitivity=3)

    default = derive_risk_tier(dims, system_type=None)
    assert default.tier == "high"
    assert default.profile == "recommended_default"
    assert default.driving_dimensions == ("data_sensitivity",)

    knowledge = derive_risk_tier(dims, system_type="knowledge_assistant")
    assert knowledge.tier != "high"
    assert knowledge.tier == "low"
    assert knowledge.profile == "knowledge_assistant"
    assert "data_sensitivity" not in knowledge.tier_dimensions
    # Low under this profile means nothing weighted rose — so nothing drove it.
    assert knowledge.driving_dimensions == ()


# --------------------------------------------------------------------------- #
# Autonomy level in the transaction/commerce profile
# --------------------------------------------------------------------------- #
def test_autonomy_level_3_forces_high_when_the_profile_uses_it():
    dims = make_dimensions()
    d = derive_risk_tier(dims, "transaction_commerce_agent", autonomy_level=3)
    assert d.tier == "high"
    assert d.autonomy_level_driven is True
    assert d.driving_dimensions == ()  # nothing scored 3; autonomy level alone drove it


def test_autonomy_level_3_is_ignored_by_profiles_that_do_not_use_it():
    dims = make_dimensions()
    d = derive_risk_tier(dims, "knowledge_assistant", autonomy_level=3)
    assert d.tier == "low"
    assert d.autonomy_level_driven is False


# --------------------------------------------------------------------------- #
# The derivation is inspectable
# --------------------------------------------------------------------------- #
def test_derivation_records_profile_weighting_and_driver():
    dims = make_dimensions(blast_radius=2, data_sensitivity=3)
    d = derive_risk_tier(dims, system_type="tool_using_agent")
    assert d.tier == "medium"  # data_sensitivity=3 is outside the tool profile
    assert d.profile == "tool_using_agent"
    assert set(d.tier_dimensions) == set(KNOWLEDGE_PROFILE_DIMS)
    assert d.driving_dimensions == ("blast_radius",)
    as_dict = d.as_dict()
    assert as_dict["profile"] == "tool_using_agent"
    assert as_dict["driving_dimensions"] == ["blast_radius"]
    assert as_dict["autonomy_level_driven"] is False
