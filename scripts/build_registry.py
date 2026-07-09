"""Compile entries/*.yaml into web/data/registry.json (and registry.js), and keep
the cached classifier examples (web/data/examples.json / examples.js) in lockstep.

Reuses the single source of truth in classifier/schema.py for both schema validation
and the risk_tier rollup — no logic is duplicated here. For every entry we also assert
that the stored ``risk_tier`` equals what the rollup computes from its dimensions, so a
hand-edited tier can never drift from the scores.

Artifacts, all emitted from the same validated data:
  * ``web/data/registry.json`` — canonical machine-readable registry.
  * ``web/data/registry.js``   — the identical array on ``window.__REGISTRY__`` so the
    single-file web view reads it via a plain ``<script>`` (no fetch/CORS; opens from
    file://, a local server, or GitHub Pages alike). See docs/adr/0004-*.md.
  * ``web/data/examples.json`` — canonical cached classifier examples (the ratified
    results of running examples/*.txt through the maker/checker loop).
  * ``web/data/examples.js``   — the identical array on ``window.__EXAMPLES__``, read by
    the classifier hero the same zero-fetch way. See docs/adr/0005-*.md.

OFFLINE by default. The default command and ``--check`` make NO network calls and need
no API key: they compile the registry and re-derive examples.js from the committed
examples.json. Only ``--rebuild-examples`` calls the live LLM — it re-classifies
examples/*.txt through the real provider and rewrites examples.json. That is an
author-run step; CI runs the offline path only. The committed examples.* are the source
of truth the page reads.

Usage:
    python scripts/build_registry.py                    # (re)write generated files (offline)
    python scripts/build_registry.py --check            # verify committed files are fresh (offline)
    python scripts/build_registry.py --rebuild-examples # re-classify examples via the live LLM (author-run)
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
EXAMPLES_DIR = ROOT / "examples"
OUTPUT_JSON = ROOT / "web" / "data" / "registry.json"
OUTPUT_JS = ROOT / "web" / "data" / "registry.js"
OUTPUT_EXAMPLES_JSON = ROOT / "web" / "data" / "examples.json"
OUTPUT_EXAMPLES_JS = ROOT / "web" / "data" / "examples.js"

# Display order for the cached examples in the hero (low → medium → high).
_TIER_RANK = {"low": 0, "medium": 1, "high": 2}


def _fail(message: str) -> "NoReturn":  # type: ignore[valid-type]
    print(f"build_registry: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_entry(data: dict, label: str) -> None:
    """Schema-validate an entry and assert its stored tier matches the rollup.

    Shared by registry entries and cached examples so both hold to one source of truth.
    """
    schema = load_schema()
    if not isinstance(data, dict):
        _fail(f"{label}: top-level value must be a mapping")
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as exc:
        location = "/".join(str(p) for p in exc.absolute_path) or "<root>"
        _fail(f"{label}: schema validation failed at '{location}': {exc.message}")
    computed = roll_up_risk_tier(data["dimensions"])
    if data["risk_tier"] != computed:
        _fail(
            f"{label}: risk_tier '{data['risk_tier']}' does not match the value "
            f"computed by classifier.schema.roll_up_risk_tier ('{computed}'). "
            f"Fix the tier (or the scores) so there is one source of truth."
        )


def load_entries() -> list[dict]:
    """Load, validate, and return every registry entry (sorted by filename)."""
    entries: list[dict] = []
    paths = sorted(ENTRIES_DIR.glob("*.yaml"))
    if not paths:
        _fail(f"no entries found in {ENTRIES_DIR}")
    for path in paths:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            _fail(f"{path.name}: could not parse YAML: {exc}")
        validate_entry(data, path.name)
        entries.append(data)
    return entries


def load_examples() -> list[dict] | None:
    """Load and validate the committed cached examples, or None if not generated yet."""
    if not OUTPUT_EXAMPLES_JSON.exists():
        return None
    try:
        data = json.loads(OUTPUT_EXAMPLES_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _fail(f"{OUTPUT_EXAMPLES_JSON.relative_to(ROOT)}: invalid JSON: {exc}")
    if not isinstance(data, list):
        _fail(
            f"{OUTPUT_EXAMPLES_JSON.relative_to(ROOT)}: top-level value must be an array"
        )
    for example in data:
        slug = (example.get("agent") or {}).get("slug", "<unknown>")
        validate_entry(example, f"examples.json[{slug}]")
    return data


def _canonical_json(items: list[dict]) -> str:
    """Deterministic JSON body shared by the generated artifacts."""
    return json.dumps(items, indent=2, ensure_ascii=False, sort_keys=True)


def render_json(entries: list[dict]) -> str:
    """Canonical registry.json content (the machine-readable artifact)."""
    return _canonical_json(entries) + "\n"


def render_js(entries: list[dict]) -> str:
    """registry.js content: the identical array assigned to a browser global."""
    return f"window.__REGISTRY__ = {_canonical_json(entries)};\n"


def render_examples_json(examples: list[dict]) -> str:
    """Canonical examples.json content."""
    return _canonical_json(examples) + "\n"


def render_examples_js(examples: list[dict]) -> str:
    """examples.js content: the identical array assigned to ``window.__EXAMPLES__``."""
    return f"window.__EXAMPLES__ = {_canonical_json(examples)};\n"


def _check_stale(path: Path, expected: str) -> None:
    if not path.exists():
        _fail(f"{path.relative_to(ROOT)} does not exist; run build_registry.py")
    if path.read_text(encoding="utf-8") != expected:
        _fail(
            f"{path.relative_to(ROOT)} is stale. Regenerate it with "
            f"'python scripts/build_registry.py' and commit the result."
        )


# --------------------------------------------------------------------------- #
# Live examples rebuild (author-run only — this is the ONLY networked path)
# --------------------------------------------------------------------------- #
def rebuild_examples_live() -> list[dict]:
    """Re-classify every examples/*.txt through the real maker/checker loop.

    Makes live LLM calls, so it is never run in CI — only by an author refreshing the
    cached examples. Imports and .env loading are done HERE (not at module import) so the
    default/offline paths stay hermetic and key-free.
    """
    from dotenv import load_dotenv

    from classifier.graph import classify
    from classifier.provider import provider_from_env
    from classifier.run import build_entry

    paths = sorted(EXAMPLES_DIR.glob("*.txt"))
    if not paths:
        _fail(f"no example descriptions found in {EXAMPLES_DIR}")

    load_dotenv()  # CLI entry point only — mirrors classifier/run.py
    provider = provider_from_env()

    def auto_accept(state: dict) -> dict:
        # Auto-accept so the loop completes unattended; these committed fixtures stand in
        # for a ratified result. The live in-browser path (scripts/serve_classify.py) shows
        # the human-ratification gate explicitly instead of finalising silently.
        return {"decision": "approve", "approved_by": None}

    examples: list[dict] = []
    for path in paths:
        description = path.read_text(encoding="utf-8").strip()
        if not description:
            _fail(f"{path.name}: empty example description")
        print(f"  classifying {path.name} …", file=sys.stderr)
        state = classify(description, provider, human_gate=auto_accept)
        entry = build_entry(state, slug=path.stem, approver="example-build")
        validate_entry(entry, path.name)
        examples.append(entry)

    examples.sort(key=lambda e: (_TIER_RANK.get(e["risk_tier"], 99), e["agent"]["slug"]))
    return examples


# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    check = "--check" in argv
    rebuild = "--rebuild-examples" in argv
    if check and rebuild:
        _fail("--check and --rebuild-examples cannot be combined")

    # Registry: always compiled from entries/ (offline).
    entries = load_entries()
    json_text = render_json(entries)
    js_text = render_js(entries)

    if rebuild:
        # The ONLY path that touches the network. Rewrite examples.json from live results.
        examples = rebuild_examples_live()
        OUTPUT_EXAMPLES_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_EXAMPLES_JSON.write_text(render_examples_json(examples), encoding="utf-8")
        print(
            f"Rebuilt {OUTPUT_EXAMPLES_JSON.relative_to(ROOT)} "
            f"({len(examples)} examples) via the live provider.",
            file=sys.stderr,
        )

    # Examples: read the canonical committed (or just-rebuilt) examples.json and derive
    # examples.js from it — a purely offline twin, kept in lockstep with the JSON.
    examples = load_examples()
    examples_js_text = render_examples_js(examples) if examples is not None else None

    if check:
        _check_stale(OUTPUT_JSON, json_text)
        _check_stale(OUTPUT_JS, js_text)
        if examples is None:
            _fail(
                f"{OUTPUT_EXAMPLES_JSON.relative_to(ROOT)} is missing; generate it with "
                f"'python scripts/build_registry.py --rebuild-examples' and commit it."
            )
        _check_stale(OUTPUT_EXAMPLES_JSON, render_examples_json(examples))
        _check_stale(OUTPUT_EXAMPLES_JS, examples_js_text)
        print(
            f"OK: {OUTPUT_JSON.relative_to(ROOT)}, {OUTPUT_JS.relative_to(ROOT)}, "
            f"{OUTPUT_EXAMPLES_JSON.relative_to(ROOT)} and "
            f"{OUTPUT_EXAMPLES_JS.relative_to(ROOT)} are up to date."
        )
        return 0

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json_text, encoding="utf-8")
    OUTPUT_JS.write_text(js_text, encoding="utf-8")
    written = f"{OUTPUT_JSON.relative_to(ROOT)} and {OUTPUT_JS.relative_to(ROOT)} ({len(entries)} entries)"
    if examples is not None:
        OUTPUT_EXAMPLES_JS.write_text(examples_js_text, encoding="utf-8")
        written += f"; {OUTPUT_EXAMPLES_JS.relative_to(ROOT)} ({len(examples)} examples)"
    else:
        written += "; examples.js skipped (no examples.json yet — run --rebuild-examples)"
    print(f"Wrote {written}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
