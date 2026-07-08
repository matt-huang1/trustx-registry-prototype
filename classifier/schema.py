"""Schema helpers: the placeholder dimensions and the risk-tier rollup.

NOTE: ``DIMENSIONS`` are the four PLACEHOLDER sample dimensions. They must be
swapped for RAI's real 12-dimension model (see schema/entry.schema.json and
docs/ROADMAP.md M1). Nothing in the loop hard-codes anything beyond this list, so
extending it is a matter of editing ``DIMENSIONS`` and the JSON Schema.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Mapping

# Placeholder sample dimensions. SWAP FOR RAI'S REAL 12.
DIMENSIONS: tuple[str, ...] = (
    "autonomy",
    "delegated_authority",
    "tool_access",
    "data_exposure",
)

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema" / "entry.schema.json"


@lru_cache(maxsize=1)
def load_schema() -> dict:
    """Load and cache the entry JSON Schema."""
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def roll_up_risk_tier(dimensions: Mapping[str, Mapping]) -> str:
    """Derive a low/medium/high tier from the per-dimension scores.

    Placeholder rollup: the tier is driven by the single highest-risk dimension
    (a max, not an average) so that one severe dimension cannot be diluted by
    several benign ones. This is intentionally conservative and will be revisited
    with RAI's real model.
    """
    if not dimensions:
        return "low"
    peak = max(int(d["score"]) for d in dimensions.values())
    if peak >= 4:
        return "high"
    if peak == 3:
        return "medium"
    return "low"
