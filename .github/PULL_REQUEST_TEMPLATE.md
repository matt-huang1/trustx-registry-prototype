<!--
Thanks for contributing! If this PR adds or changes a registry entry, the checklist below
mirrors the automated checks CI will run. Ticking it honestly gets your PR merged faster.
-->

## What does this PR do?

<!-- One or two sentences. Link any issue it addresses (e.g. "Closes #12"). -->

## Type of change

- [ ] New registry entry
- [ ] Change to an existing entry (challenge resolution / rationale / evidence)
- [ ] Schema, rules, or tooling change
- [ ] Docs only

## Contributor checklist (entries)

If this PR touches `entries/`, confirm each — these mirror the automated checks:

- [ ] **Schema** — the entry validates against `schema/entry.schema.json`.
- [ ] **Evidence** — every one of the 12 dimensions cites evidence (no empty `evidence` list).
- [ ] **Deterministic floors** — I did not fight a deterministic rule (e.g. money-movement ⇒ Action Authority 3).
- [ ] **Recomputed tier** — `risk_tier` and `tier_derivation` are what the rollup computes (I did not hand-edit them away from the scores).
- [ ] **Trust level** — a new entry is `community-submitted` with a null `review`; I did **not** self-assign `working-group-reviewed` or `verified`.
- [ ] **Generated artifacts** — I ran `python scripts/build_registry.py` and committed the refreshed `web/data/*` if they changed.

## Local checks run

- [ ] `python scripts/build_registry.py --check`
- [ ] `python -m pytest -q`
- [ ] `black --check .`

## For a challenge resolution

- [ ] This supersedes the prior entry as a **new version** (scores, evidence, recomputed tier, and a fresh `review` all updated together).
- [ ] The challenge (issue) that prompted the change is linked above.
