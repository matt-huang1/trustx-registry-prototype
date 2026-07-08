# ADR-0003: Curated reference entries — hand-authored, archetypal, defensible

- Status: Accepted
- Date: 2026-07-09

## Decision
Seed the registry with a small set of **hand-authored, archetypal** reference entries
that describe *representative* systems (e.g. an internal document summariser, a KYC triage
agent, a payments initiation agent) — not named commercial products. Each entry's scores
are reasoned by hand with evidence quoting the entry's own description; the `risk_tier` is
**computed** by the shared rollup (`classifier/schema.py`), not hand-set; and the
deterministic money-movement invariant is honoured in the data. A build step
(`scripts/build_registry.py`) validates every entry and compiles them into
`web/data/registry.json`, with `--check` failing CI if the compiled output drifts.

## Context
A registry with no entries can't be evaluated, demoed, or tested end-to-end, and the
future web UI needs data to render. But seed data for a *risk* registry is itself a
risk: fabricated or mislabeled scores would undermine the project's core principle that
entries must be defensible, not self-asserted.

## Alternatives considered
- **Classifier-generated seed data.** Run the maker/checker loop to produce the seeds.
  Fast, but the scores would be LLM-drafted and un-ratified — self-asserted, non-defensible
  numbers presented as reference truth, and non-deterministic/non-hermetic to reproduce.
- **Entries for named, real commercial products.** Concrete and recognisable, but we'd be
  publicly assigning risk scores to real vendors' products from the outside, with no access
  to their internals — mislabeling risk and inviting disputes we cannot substantiate.

## Why chosen
Hand-authored archetypes let us stand behind every number: defensibility over fabricated
scores. Using representative systems rather than named products avoids mislabeling real
vendors while still exercising the full low/medium/high range and the deterministic
override. Computing the tier from the shared rollup keeps one source of truth (enforced by
the build check and tests). This mirrors how RAI publishes representative reference
entries rather than a leaderboard of named products.
