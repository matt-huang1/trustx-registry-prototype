"""Compile entries/*.yaml into web/data/registry.json (and registry.js).

Reuses the single source of truth in classifier/schema.py for both schema validation
and the risk_tier rollup — no logic is duplicated here. For every entry we also assert
that the stored ``risk_tier`` equals what the rollup computes from its dimensions, so a
hand-edited tier can never drift from the scores.

Two artifacts are emitted from the same validated data:
  * ``web/data/registry.json`` — the canonical machine-readable artifact.
  * ``web/data/registry.js``   — the identical array assigned to ``window.__REGISTRY__``
    so the single-file web view can read it via a plain ``<script>`` tag, with no
    ``fetch()`` and therefore no CORS constraints (opens from file://, a local server,
    or GitHub Pages alike). See docs/adr/0004-single-file-web-demo.md.

Usage:
    python scripts/build_registry.py           # (re)write both generated files
    python scripts/build_registry.py --check    # verify the committed files are up to date
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
OUTPUT_JSON = ROOT / "web" / "data" / "registry.json"
OUTPUT_JS = ROOT / "web" / "data" / "registry.js"


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


def _canonical_json(entries: list[dict]) -> str:
    """Deterministic JSON body shared by both generated artifacts."""
    return json.dumps(entries, indent=2, ensure_ascii=False, sort_keys=True)


def render_json(entries: list[dict]) -> str:
    """Canonical registry.json content (the machine-readable artifact)."""
    return _canonical_json(entries) + "\n"


def render_js(entries: list[dict]) -> str:
    """registry.js content: the identical array assigned to a browser global.

    Read by web/index.html via a plain <script> tag, so the page renders with no
    fetch()/CORS regardless of how it is opened (file://, local server, Pages).
    """
    return f"window.__REGISTRY__ = {_canonical_json(entries)};\n"


def _check_stale(path: Path, expected: str) -> None:
    if not path.exists():
        _fail(f"{path.relative_to(ROOT)} does not exist; run build_registry.py")
    if path.read_text(encoding="utf-8") != expected:
        _fail(
            f"{path.relative_to(ROOT)} is stale. Regenerate it with "
            f"'python scripts/build_registry.py' and commit the result."
        )


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    check = "--check" in argv

    entries = load_entries()
    json_text = render_json(entries)
    js_text = render_js(entries)

    if check:
        _check_stale(OUTPUT_JSON, json_text)
        _check_stale(OUTPUT_JS, js_text)
        print(
            f"OK: {OUTPUT_JSON.relative_to(ROOT)} and "
            f"{OUTPUT_JS.relative_to(ROOT)} are up to date."
        )
        return 0

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json_text, encoding="utf-8")
    OUTPUT_JS.write_text(js_text, encoding="utf-8")
    print(
        f"Wrote {OUTPUT_JSON.relative_to(ROOT)} and "
        f"{OUTPUT_JS.relative_to(ROOT)} ({len(entries)} entries)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
