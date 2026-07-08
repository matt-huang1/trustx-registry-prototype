"""Compile entries/*.yaml into web/data/registry.json.

Reuses the single source of truth in classifier/schema.py for both schema validation
and the risk_tier rollup — no logic is duplicated here. For every entry we also assert
that the stored ``risk_tier`` equals what the rollup computes from its dimensions, so a
hand-edited tier can never drift from the scores.

Usage:
    python scripts/build_registry.py           # (re)write web/data/registry.json
    python scripts/build_registry.py --check    # verify the committed file is up to date
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
import yaml

# Import from the installed package so this works regardless of cwd.
from classifier.schema import load_schema, roll_up_risk_tier

ROOT = Path(__file__).resolve().parent.parent
ENTRIES_DIR = ROOT / "entries"
OUTPUT = ROOT / "web" / "data" / "registry.json"


def _fail(message: str) -> "NoReturn":  # type: ignore[valid-type]
    print(f"build_registry: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_entries() -> list[dict]:
    """Load, validate, and return every entry (sorted by filename for stability)."""
    schema = load_schema()
    entries: list[dict] = []
    paths = sorted(ENTRIES_DIR.glob("*.yaml"))
    if not paths:
        _fail(f"no entries found in {ENTRIES_DIR}")
    for path in paths:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            _fail(f"{path.name}: could not parse YAML: {exc}")
        if not isinstance(data, dict):
            _fail(f"{path.name}: top-level YAML must be a mapping")
        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.ValidationError as exc:
            location = "/".join(str(p) for p in exc.absolute_path) or "<root>"
            _fail(f"{path.name}: schema validation failed at '{location}': {exc.message}")
        # One source of truth: the stored tier must match the computed rollup.
        computed = roll_up_risk_tier(data["dimensions"])
        if data["risk_tier"] != computed:
            _fail(
                f"{path.name}: risk_tier '{data['risk_tier']}' does not match the value "
                f"computed by classifier.schema.roll_up_risk_tier ('{computed}'). "
                f"Fix the tier (or the scores) so there is one source of truth."
            )
        entries.append(data)
    return entries


def render(entries: list[dict]) -> str:
    """Deterministic JSON rendering used for both writing and --check comparison."""
    return json.dumps(entries, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    check = "--check" in argv

    rendered = render(load_entries())

    if check:
        if not OUTPUT.exists():
            _fail(f"{OUTPUT.relative_to(ROOT)} does not exist; run build_registry.py")
        current = OUTPUT.read_text(encoding="utf-8")
        if current != rendered:
            _fail(
                f"{OUTPUT.relative_to(ROOT)} is stale. Regenerate it with "
                f"'python scripts/build_registry.py' and commit the result."
            )
        print(f"OK: {OUTPUT.relative_to(ROOT)} is up to date.")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({len(rendered.splitlines())} lines).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
