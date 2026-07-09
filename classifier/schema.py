"""Schema helpers: the ARC 12-dimension model and the risk-tier rollup.

Two ideas are deliberately kept separate here (see docs/adr/0012-*.md):

* SCORING — every entry always scores ALL 12 ARC dimensions (``DIMENSIONS``),
  1/2/3, with rationale and evidence. No dimension is ever skipped.
* TIER WEIGHTING — which of those scores drive the rolled-up ``risk_tier`` is a
  per-system-type profile loaded from ``policy/tier_weighting_profiles.yaml``
  (data, not code). Worst-case-wins over the profile's ``tier_dimensions``:
  any = 3 -> Tier 3 (high); else max = 2 or average >= 1.5 -> Tier 2 (medium);
  else Tier 1 (low). A profile with ``use_autonomy_level`` also forces Tier 3
  when autonomy_level is 3.

Dimension ids, names, groups, and tier labels come verbatim from
``schema/dimensions.json`` (extracted from the ARC reference); nothing here
paraphrases them.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Mapping

_SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schema"
SCHEMA_PATH = _SCHEMA_DIR / "entry.schema.json"
DIMENSIONS_PATH = _SCHEMA_DIR / "dimensions.json"
STANDARDS_MATRIX_PATH = _SCHEMA_DIR / "standards_matrix.json"
PROFILES_PATH = (
    Path(__file__).resolve().parent.parent / "policy" / "tier_weighting_profiles.yaml"
)

# risk_tier string <-> ARC tier number (low/medium/high == Tier 1/2/3).
TIER_NAMES: dict[int, str] = {1: "low", 2: "medium", 3: "high"}

# The profile applied when an entry has no system_type, or a system_type with no
# profile of its own. Overridable in the profiles YAML via ``default_profile``.
FALLBACK_DEFAULT_PROFILE = "recommended_default"


@lru_cache(maxsize=1)
def load_schema() -> dict:
    """Load and cache the entry JSON Schema."""
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_dimension_meta() -> dict:
    """Load and cache the verbatim ARC dimension metadata (schema/dimensions.json)."""
    return json.loads(DIMENSIONS_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_standards_matrix() -> dict:
    """Load and cache the per-dimension standards mappings (schema/standards_matrix.json)."""
    return json.loads(STANDARDS_MATRIX_PATH.read_text(encoding="utf-8"))


# The 12 ARC dimensions, in reference order. Always ALL scored.
DIMENSIONS: tuple[str, ...] = tuple(d["id"] for d in load_dimension_meta()["dimensions"])

SYSTEM_TYPES: tuple[str, ...] = tuple(load_dimension_meta()["system_types"].keys())


@lru_cache(maxsize=1)
def load_tier_weighting_profiles() -> dict:
    """Load the committed tier-weighting profiles, resolving the ALL_12 sentinel.

    Returns ``{"default_profile": str, "profiles": {name: {"tier_dimensions":
    tuple, "use_autonomy_level": bool}}}``. Profiles are DATA: adding or editing
    one is a YAML change, never a code change.
    """
    import yaml  # local import keeps module import light for web-of-imports callers

    raw = yaml.safe_load(PROFILES_PATH.read_text(encoding="utf-8"))
    profiles: dict[str, dict] = {}
    for name, prof in raw["profiles"].items():
        dims = prof["tier_dimensions"]
        if dims == "ALL_12":
            dims = list(DIMENSIONS)
        unknown = set(dims) - set(DIMENSIONS)
        if unknown:
            raise ValueError(
                f"tier_weighting_profiles.yaml: profile '{name}' names unknown "
                f"dimensions {sorted(unknown)}"
            )
        profiles[name] = {
            "tier_dimensions": tuple(dims),
            "use_autonomy_level": bool(prof.get("use_autonomy_level", False)),
        }
    default = raw.get("default_profile", FALLBACK_DEFAULT_PROFILE)
    if default not in profiles:
        raise ValueError(
            f"tier_weighting_profiles.yaml: default_profile '{default}' is not defined"
        )
    return {"default_profile": default, "profiles": profiles}


def resolve_profile(system_type: str | None) -> tuple[str, dict]:
    """Return ``(profile_name, profile)`` for a system type (or the default)."""
    loaded = load_tier_weighting_profiles()
    profiles = loaded["profiles"]
    if system_type is not None and system_type in profiles:
        return system_type, profiles[system_type]
    default = loaded["default_profile"]
    return default, profiles[default]


@dataclass(frozen=True)
class TierDerivation:
    """The inspectable result of the rollup: the tier AND why.

    ``driving_dimensions`` are the profile's tier_dimensions at the
    tier-determining score, and only when that score is ABOVE baseline —
    exactly the ones that set the tier under worst-case-wins. It is empty when
    nothing rose above Tier 1 (a low tier has no driver: the tier is low
    because nothing rose) and when autonomy_level alone forced Tier 3
    (``autonomy_level_driven``).
    """

    tier: str  # "low" | "medium" | "high"
    profile: str
    tier_dimensions: tuple[str, ...]
    driving_dimensions: tuple[str, ...]
    autonomy_level_driven: bool

    def as_dict(self) -> dict:
        """The entry-embeddable shape (schema: tier_derivation)."""
        return {
            "profile": self.profile,
            "tier_dimensions": list(self.tier_dimensions),
            "driving_dimensions": list(self.driving_dimensions),
            "autonomy_level_driven": self.autonomy_level_driven,
        }


def derive_risk_tier(
    dimensions: Mapping[str, Mapping],
    system_type: str | None = None,
    autonomy_level: int | None = None,
) -> TierDerivation:
    """Roll up a tier over the system type's tier-weighting profile.

    ALL 12 dimensions are expected in ``dimensions`` (scoring is total); the
    profile only selects which of them the tier is weighted off. Worst-case-wins
    over the profile's tier_dimensions:

        any score = 3                     -> Tier 3 (high)
        else max = 2 OR average >= 1.5    -> Tier 2 (medium)
        else                              -> Tier 1 (low)

    If the profile has ``use_autonomy_level`` and autonomy_level is 3, the tier
    is forced to Tier 3 regardless of the dimension scores.
    """
    profile_name, profile = resolve_profile(system_type)
    weighted = [d for d in profile["tier_dimensions"] if d in dimensions]
    scores = {d: int(dimensions[d]["score"]) for d in weighted}

    autonomy_forced = bool(
        profile["use_autonomy_level"]
        and autonomy_level is not None
        and autonomy_level == 3
    )

    if not scores:
        tier_num = 3 if autonomy_forced else 1
    else:
        peak = max(scores.values())
        average = sum(scores.values()) / len(scores)
        if peak == 3 or autonomy_forced:
            tier_num = 3
        elif peak == 2 or average >= 1.5:
            tier_num = 2
        else:
            tier_num = 1

    # A dimension "drives" the tier only if it sits at the tier-determining
    # score AND that score is above baseline. An all-baseline profile has no
    # driver — the tier is low because nothing rose, not because of any one
    # dimension.
    if tier_num == 3:
        driving = tuple(d for d in weighted if scores[d] == 3)
    elif scores and max(scores.values()) > 1:
        peak = max(scores.values())
        driving = tuple(d for d in weighted if scores[d] == peak)
    else:
        driving = ()

    return TierDerivation(
        tier=TIER_NAMES[tier_num],
        profile=profile_name,
        tier_dimensions=tuple(profile["tier_dimensions"]),
        driving_dimensions=driving,
        autonomy_level_driven=autonomy_forced,
    )


def roll_up_risk_tier(
    dimensions: Mapping[str, Mapping],
    system_type: str | None = None,
    autonomy_level: int | None = None,
) -> str:
    """Derive just the low/medium/high tier (see :func:`derive_risk_tier`)."""
    if not dimensions:
        return "low"
    return derive_risk_tier(dimensions, system_type, autonomy_level).tier
