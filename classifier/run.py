"""CLI: run the maker/checker loop and write a ratified entry.

Usage:
    python -m classifier.run "<agent description>"

Reads LLM config from the environment via classifier.provider. On approval/edit it
writes a schema-valid YAML entry to entries/<slug>.yaml; on rejection nothing is
written.

A .env file (if present) is loaded here at the CLI entry point ONLY — never in
provider.py or in tests — so the offline test suite stays hermetic and never reads .env.
"""

from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import jsonschema
import yaml
from dotenv import load_dotenv

from .graph import ClassifierState, classify, cli_human_gate
from .provider import provider_from_env
from .schema import DIMENSIONS, derive_risk_tier, load_schema

ENTRIES_DIR = Path(__file__).resolve().parent.parent / "entries"


def slugify(description: str) -> str:
    """Make a short URL-safe slug from the first few words of the description."""
    words = re.findall(r"[a-z0-9]+", description.lower())
    slug = "-".join(words[:6]) or "agent"
    return slug[:60].strip("-")


def build_entry(state: ClassifierState, slug: str, approver: str | None) -> dict:
    """Assemble a schema-shaped entry dict from the final classifier state.

    The tier and its derivation are recomputed here from the (possibly
    human-edited) proposal — the entry always records WHICH profile weighted the
    tier and WHICH dimensions drove it, so the derivation is inspectable.
    """
    notes = list(state.get("deterministic_notes", [])) + list(
        state.get("challenge_notes", [])
    )
    dimensions = {dim: state["proposal"][dim] for dim in DIMENSIONS}
    system_type = state.get("system_type")
    autonomy_level = state.get("autonomy_level")
    derivation = derive_risk_tier(dimensions, system_type, autonomy_level)
    entry: dict = {
        "agent": {"slug": slug, "description": state["description"]},
        "dimensions": dimensions,
        "risk_tier": derivation.tier,
        "tier_derivation": derivation.as_dict(),
    }
    if system_type is not None:
        entry["system_type"] = system_type
    if autonomy_level is not None:
        entry["autonomy_level"] = autonomy_level
    entry |= {
        "challenge": {
            "flagged": bool(state.get("challenge_flagged", False))
            or bool(state.get("deterministic_notes")),
            "notes": notes,
            "iterations": int(state.get("iterations", 1)),
        },
        "provenance": {
            "submitted_by": "classifier",
            "approved_by": approver,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
    return entry


def write_entry(entry: dict, slug: str) -> Path:
    """Validate against the schema and write entries/<slug>.yaml."""
    jsonschema.validate(instance=entry, schema=load_schema())
    ENTRIES_DIR.mkdir(parents=True, exist_ok=True)
    path = ENTRIES_DIR / f"{slug}.yaml"
    path.write_text(yaml.safe_dump(entry, sort_keys=False), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 1 or not argv[0].strip():
        print('Usage: python -m classifier.run "<agent description>"', file=sys.stderr)
        return 2

    # Load a .env (if any) HERE — at the CLI entry point only, before the provider is
    # built — so importing this module stays side-effect-free and the test suite (which
    # imports helpers from here) never reads .env.
    load_dotenv()

    description = argv[0].strip()
    provider = provider_from_env()
    state = classify(description, provider, human_gate=cli_human_gate)

    decision = state.get("decision")
    if decision == "reject":
        print("\nEntry REJECTED by operator — nothing written.")
        return 0

    slug = slugify(description)
    entry = build_entry(state, slug, state.get("approved_by"))
    path = write_entry(entry, slug)
    print(f"\nWrote ratified entry: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
