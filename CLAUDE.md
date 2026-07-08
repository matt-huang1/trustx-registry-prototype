# trustx-registry-prototype — CLAUDE.md

## What this is
A prototype open-source registry that classifies AI agents by risk with
defensible, evidence-backed entries (not self-asserted labels). Placeholder
schema until RAI's real 12-dimension model lands. Working name only — do NOT
use "ROAR" or imply official RAI status anywhere.

## Core principle (encode this, don't just cite it)
The model proposes; deterministic checks decide wherever a fact can be pinned
down; an accountable human owns the rest — and how much human scrutiny applies
scales with the risk tier. Never let an LLM silently finalise a risk score.

## Commands
- Install:  pip install -e ".[dev]"
- Test (offline, no API):  python -m pytest -q
- Run classifier:  python -m classifier.run "<agent description>"

## Conventions
- Python 3.11+, type-annotated, black-formatted.
- LLM access ONLY via classifier/provider.py (OpenAI-compatible). Never hard-code
  a provider or model elsewhere. Config via env: LLM_BASE_URL, LLM_API_KEY, LLM_MODEL.
- Tests inject a fake LLM — no live API calls in the default suite.
- Registry entries are YAML in entries/, one file per agent, valid against
  schema/entry.schema.json.

## Decisions must be recorded
On any non-obvious design decision, write an ADR in docs/adr/ (NNNN-title.md:
Decision / Context / Alternatives considered / Why) and list it in
docs/DESIGN_DECISIONS.md. If unsure whether something needs an ADR, flag it.

## Never
- Never commit secrets or read .env* or secrets/**.
- Never weaken or delete a test just to make a build pass.
