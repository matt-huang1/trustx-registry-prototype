"""Shared offline test fixtures: ARC-shaped fake drafts, no LLM, no network."""

from __future__ import annotations

from classifier.schema import DIMENSIONS


def make_dimensions(**overrides: int) -> dict:
    """A full 12-dimension scoring map, all Tier 1 unless overridden by id."""
    unknown = set(overrides) - set(DIMENSIONS)
    assert not unknown, f"unknown dimension ids: {sorted(unknown)}"
    return {
        dim: {
            "score": int(overrides.get(dim, 1)),
            "rationale": f"test rationale for {dim}",
            "evidence": ["desc"],
        }
        for dim in DIMENSIONS
    }


def make_draft(
    system_type: str | None = None,
    autonomy_level: int | None = 1,
    **overrides: int,
) -> dict:
    """A proposer-shaped LLM draft: nested dimensions + system_type + autonomy_level."""
    return {
        "dimensions": make_dimensions(**overrides),
        "system_type": system_type,
        "autonomy_level": autonomy_level,
    }
