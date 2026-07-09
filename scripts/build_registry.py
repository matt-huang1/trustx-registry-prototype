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
  * ``web/data/policy.json``   — canonical runtime-policy-gate bundle: the org policy, the
    deterministic gate decision for every entry (keyed by slug), and the scripted scenario.
  * ``web/data/policy.js``     — the same bundle on ``window.__POLICY__`` /
    ``window.__GATE_DECISIONS__`` / ``window.__SCENARIO__`` for the Policy Gate web section.
    Decisions are computed here (offline, deterministic — no LLM); the browser only looks
    them up. See docs/adr/0006-*.md.

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
from classifier.policy_gate import decide as gate_decide
from classifier.schema import load_schema, roll_up_risk_tier

ROOT = Path(__file__).resolve().parent.parent
ENTRIES_DIR = ROOT / "entries"
EXAMPLES_DIR = ROOT / "examples"
POLICY_PATH = ROOT / "policy" / "example-bank-policy.yaml"
OUTPUT_JSON = ROOT / "web" / "data" / "registry.json"
OUTPUT_JS = ROOT / "web" / "data" / "registry.js"
OUTPUT_EXAMPLES_JSON = ROOT / "web" / "data" / "examples.json"
OUTPUT_EXAMPLES_JS = ROOT / "web" / "data" / "examples.js"
OUTPUT_POLICY_JSON = ROOT / "web" / "data" / "policy.json"
OUTPUT_POLICY_JS = ROOT / "web" / "data" / "policy.js"

# The scripted "cinematic" demo path: an invoice-payment workflow whose steps reference
# real registry slugs across the tiers, so safe steps pass and the money-movement step
# halts. Represented as data; the gate decision for each slug is looked up, never computed
# in the browser. If the registry's low/medium archetypes change slug, update these.
SCENARIO_STEPS: tuple[dict, ...] = (
    {
        "slug": "internal-document-summarisation-assistant",
        "task": "Read the vendor invoice and extract the amount, payee, and line items.",
    },
    {
        "slug": "kyc-onboarding-triage-agent",
        "task": "Look up the vendor's records to confirm identity and banking details.",
    },
    {
        "slug": "payments-initiation-agent",
        "task": "Initiate the ACH payment of the invoiced amount to the vendor.",
    },
)

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


# --------------------------------------------------------------------------- #
# Policy gate (offline, deterministic)
# --------------------------------------------------------------------------- #
def load_policy() -> dict:
    """Load and lightly validate the committed org policy."""
    try:
        policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        _fail(f"{POLICY_PATH.relative_to(ROOT)}: could not parse YAML: {exc}")
    if not isinstance(policy, dict) or "tier_actions" not in policy:
        _fail(f"{POLICY_PATH.relative_to(ROOT)}: must be a mapping with 'tier_actions'")
    for tier in ("low", "medium", "high"):
        if tier not in policy["tier_actions"]:
            _fail(f"{POLICY_PATH.relative_to(ROOT)}: tier_actions missing '{tier}'")
    return policy


def build_gate_decisions(entries: list[dict], policy: dict) -> dict:
    """Run the deterministic gate over every entry, keyed by slug."""
    return {e["agent"]["slug"]: gate_decide(e, policy) for e in entries}


def build_scenario(entries: list[dict]) -> dict:
    """Assemble the scripted orchestrator task plan, asserting each slug exists."""
    known = {e["agent"]["slug"] for e in entries}
    for step in SCENARIO_STEPS:
        if step["slug"] not in known:
            _fail(
                f"scenario references unknown slug '{step['slug']}'. Update SCENARIO_STEPS "
                f"in build_registry.py to reference a committed registry entry."
            )
    return {
        "name": "Invoice payment workflow",
        "task": "An orchestrator is asked to pay a vendor invoice end to end.",
        "steps": [
            {"n": i + 1, "slug": step["slug"], "task": step["task"]}
            for i, step in enumerate(SCENARIO_STEPS)
        ],
    }


def build_policy_payload(entries: list[dict]) -> dict:
    """The full gate bundle: the policy, per-slug decisions, and the scripted scenario."""
    policy = load_policy()
    return {
        "policy": policy,
        "gate_decisions": build_gate_decisions(entries, policy),
        "scenario": build_scenario(entries),
    }


def render_policy_json(payload: dict) -> str:
    """Canonical policy.json content (the machine-readable gate bundle)."""
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def render_policy_js(payload: dict) -> str:
    """policy.js content: the same bundle split across three browser globals."""
    body = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)
    obj = json.loads(body)
    policy_js = json.dumps(obj["policy"], indent=2, ensure_ascii=False, sort_keys=True)
    decisions_js = json.dumps(
        obj["gate_decisions"], indent=2, ensure_ascii=False, sort_keys=True
    )
    scenario_js = json.dumps(
        obj["scenario"], indent=2, ensure_ascii=False, sort_keys=True
    )
    return (
        f"window.__POLICY__ = {policy_js};\n"
        f"window.__GATE_DECISIONS__ = {decisions_js};\n"
        f"window.__SCENARIO__ = {scenario_js};\n"
    )


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

    # Policy gate: deterministic decisions over every entry + the scripted scenario.
    # Purely offline — no network, no LLM, no key.
    policy_payload = build_policy_payload(entries)
    policy_json_text = render_policy_json(policy_payload)
    policy_js_text = render_policy_js(policy_payload)

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
        _check_stale(OUTPUT_POLICY_JSON, policy_json_text)
        _check_stale(OUTPUT_POLICY_JS, policy_js_text)
        if examples is None:
            _fail(
                f"{OUTPUT_EXAMPLES_JSON.relative_to(ROOT)} is missing; generate it with "
                f"'python scripts/build_registry.py --rebuild-examples' and commit it."
            )
        _check_stale(OUTPUT_EXAMPLES_JSON, render_examples_json(examples))
        _check_stale(OUTPUT_EXAMPLES_JS, examples_js_text)
        print(
            f"OK: {OUTPUT_JSON.relative_to(ROOT)}, {OUTPUT_JS.relative_to(ROOT)}, "
            f"{OUTPUT_EXAMPLES_JSON.relative_to(ROOT)}, {OUTPUT_EXAMPLES_JS.relative_to(ROOT)}, "
            f"{OUTPUT_POLICY_JSON.relative_to(ROOT)} and {OUTPUT_POLICY_JS.relative_to(ROOT)} "
            f"are up to date."
        )
        return 0

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json_text, encoding="utf-8")
    OUTPUT_JS.write_text(js_text, encoding="utf-8")
    OUTPUT_POLICY_JSON.write_text(policy_json_text, encoding="utf-8")
    OUTPUT_POLICY_JS.write_text(policy_js_text, encoding="utf-8")
    written = f"{OUTPUT_JSON.relative_to(ROOT)} and {OUTPUT_JS.relative_to(ROOT)} ({len(entries)} entries)"
    written += (
        f"; {OUTPUT_POLICY_JSON.relative_to(ROOT)} and {OUTPUT_POLICY_JS.relative_to(ROOT)} "
        f"({len(policy_payload['gate_decisions'])} gate decisions)"
    )
    if examples is not None:
        OUTPUT_EXAMPLES_JS.write_text(examples_js_text, encoding="utf-8")
        written += f"; {OUTPUT_EXAMPLES_JS.relative_to(ROOT)} ({len(examples)} examples)"
    else:
        written += "; examples.js skipped (no examples.json yet — run --rebuild-examples)"
    print(f"Wrote {written}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
