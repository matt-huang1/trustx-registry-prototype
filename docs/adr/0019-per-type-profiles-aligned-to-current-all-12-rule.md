# 0019 — Per-type profiles aligned to the current all-12 rule following RAI confirmation that the v1.1 subset formulas are outdated; legacy profiles retained as auditable history

## Decision

Every per-system-type tier-weighting profile in
`policy/tier_weighting_profiles.yaml` now implements the **current** ARC rule —
`tier_dimensions: ALL_12` with `autonomy_rule: arc_paper`, i.e. the published
paper's Section 3.3 critical-dimension rule (worst-case-wins across all twelve
dimensions) together with the autonomy-level provisions (L5 forces Tier 3;
L3/L4 lift to at least Tier 2). `recommended_default` is unchanged: it already
was the current rule.

The superseded five-dimension subsets are **preserved verbatim** under renamed
keys, `legacy_<system_type>_v1_1`, carrying the comment:

> historical behaviour of the v1.1 classification tools; confirmed superseded by
> RAI 2026-08-16; retained for auditability.

They are inert. `classifier.schema.resolve_profile` only selects a profile whose
key *is* the entry's `system_type`, and no ARC system type is named `legacy_*`,
so a legacy profile can never silently tier a live entry. They remain loadable,
inspectable, and directly testable.

No code changed. The rollup, the derivation record, and the build's re-derivation
gate are exactly as they were.

## Context

[ADR-0012](0012-arc-12-dimension-schema-and-tier-weighting-profiles.md) recorded
a divergence in the reference material: the v1.1 per-type classification
spreadsheets tier most system types off five "critical dimensions" (Autonomy,
Action Authority, Blast Radius, Persistence, Reversibility), while the published
paper (arXiv:2607.09586 Section 3.3) states worst-case-wins across all twelve.
Rather than silently pick one, that ADR made weighting explicit, per-type data
and defaulted to all twelve, and its 2026-07-24 addendum showed the paper's own
Section 5.2 example confirms the divergence.

**On 2026-08-16 RAI confirmed, verbally and from the framework's author, that the
per-type five-dimension formulas in the classification spreadsheets are an
OUTDATED version of the model, and that Section 3.3 is the current rule.** The
divergence is therefore resolved, and resolved in a specific direction: it was an
implementation artefact of the tooling, not a second defensible reading of the
framework. Keeping the subsets live would mean knowingly tiering entries by a
formula the framework's author has said is superseded.

### Entries re-tiered

The alignment re-tiered two committed registry entries and one cached classifier
example. Scores did not change — not one dimension was re-scored. Only which of
the already-recorded scores the rollup weights changed.

| Record | Type | Before | After | Why |
|---|---|---|---|---|
| `kyc-onboarding-triage-agent` | entry | medium | **high** | `data_sensitivity` = 3 (regulated identity PII) is weighted under the current rule; it was outside the v1.1 subset, which tiered the entry medium off `blast_radius` = 2 |
| `internal-document-summarisation-assistant` | entry | low | **medium** | `data_sensitivity` = 2 (internal documents) is now weighted; every dimension in the v1.1 subset is 1 |
| `public-docs-assistant` | cached example | low | **medium** | `control_authority` = 2 is now weighted |
| `internal-knowledge-assistant` (RAI-OPEN-0002) | entry | low | low | unchanged |
| `invoice-triage-agent` (RAI-OPEN-0003) | entry | medium | medium | unchanged; driver set widened to every dimension scored 2 |
| `trustwise-commerce-agent` (RAI-OPEN-0001) | entry | high | high | unchanged |
| `payments-initiation-agent` | entry | high | high | unchanged; its type already weighted all twelve |
| `medium-support-triage-agent` | cached example | medium | medium | unchanged; driver set widened |

All three adopted RAI seed entries reproduce their **published** tiers under the
current rule — Tier 1 / Tier 2 / Tier 3 respectively — as they did under the
superseded weighting. That the seeds are stable across the change is the
strongest available evidence the alignment is right.

The KYC entry deserves comment, because it was the prototype's worked example of
the divergence: a triage agent that reads regulated identity PII, cannot act, and
was consequently filed as medium risk. Under the current rule it is high. That is
the intended behaviour of worst-case-wins — a crown-jewel data holding is not
averaged away by the calm dimensions around it — and it is the outcome the
paper's own Section 5.2 example produces.

### This migration is the design working

The whole point of [ADR-0012](0012-arc-12-dimension-schema-and-tier-weighting-profiles.md)
separating scoring from weighting was that a correction like this should be
*possible, cheap, and visible*. It was:

* **A data change, not a code change.** One YAML file. No rollup logic touched.
* **Nothing needed re-scoring.** Scoring is total — all twelve dimensions were
  already scored with rationale and evidence on every entry, including the ones
  the old profiles ignored. The evidence for `data_sensitivity` = 3 on the KYC
  agent was already on the record; only its weight changed.
* **Every re-tier is attributable.** Each entry records `tier_derivation`, and
  the build re-derives and asserts it, so the diff shows exactly which entries
  moved and which dimension moved them.
* **The old behaviour is still runnable.** The legacy profiles let anyone
  reproduce the pre-alignment tiers on demand, which is what makes an audit of
  "what did this registry say in July, and why?" answerable.

Conversely, it exposes the governance gap the change makes concrete: a weighting
edit re-tiers entries across the registry, and this one arrived as a verbal
confirmation. Who owns weighting changes and how they are ratified remains open
(PLAN §9).

## Alternatives considered

1. **Edit the profiles in place and drop the subsets.** Simplest diff, and the
   subsets are superseded, so arguably dead weight. Rejected: it would erase the
   ability to reproduce why an entry was tiered medium last month, which is
   precisely the auditability the registry sells. Deleting the losing side of a
   resolved question also makes the resolution unfalsifiable.
2. **Keep the subsets live and add an opt-in flag.** Rejected: it leaves a
   confirmed-outdated formula able to tier a real entry, and defers the decision
   RAI has already made.
3. **Rename the subsets to `legacy_*_v1_1` and point every type at the current
   rule (chosen).** The registry tiers by the current rule everywhere; the
   superseded behaviour stays loadable, testable, and clearly labelled with when
   and by whom it was superseded.
4. **Re-score the affected entries so their tiers stay put.** Rejected outright.
   That is exactly the self-flattering-score failure the registry exists to
   prevent, arrived at from the other direction.

## Why

* The registry's claim is *defensible* classifications. Tiering by a formula the
  framework's author has confirmed is outdated is not defensible, whatever the
  convenience of stable tiers.
* Re-tiering entries is the correct, expected consequence, not damage to be
  contained. A tier is a consequence of scores and a stated rule; when the stated
  rule is corrected, tiers that move were wrong before, not broken now.
* Retaining the legacy profiles keeps the finding *falsifiable*. The divergence
  is now asserted as history in `tests/test_rollup.py` and
  `tests/test_entries_valid.py`: the same numbers, the two weightings, the two
  answers. A regression back to a subset fails loudly.
* Nothing here is silent. The affected entries carry a dated tier-weighting note,
  the profiles file carries the confirmation and date, and this ADR carries the
  before/after.

## Consequences

* **Registry:** four of six entries are unchanged; two moved up a tier. No entry
  moved down.
* **Policy gate:** the `kyc-onboarding-triage-agent` step of the scripted invoice
  scenario now escalates rather than logging, and the summarisation assistant now
  logs rather than allowing. `SCENARIO_STEPS` was repointed at the still-low
  knowledge-assistant seed (step 1) and the still-medium invoice-triage seed
  (step 2) so the demo keeps its allow → allow_with_logging → escalate arc. The
  gate itself is unchanged: it reads whatever tier the registry holds.
* **Cached examples:** the public-docs example is now medium, so the cached hero
  no longer contains a low-tier run. It was re-tiered from its **unchanged**
  scores; its LLM-produced scores, rationales, evidence, and challenger notes were
  not hand-edited. Restoring low coverage needs an author-run
  `--rebuild-examples` against a live model, or a new example description. Its
  slug lost the now-false `low-` prefix (`low-public-docs-assistant` →
  `public-docs-assistant`) so the record does not contradict its own badge.
  `tests/test_examples_build.py` pins the coverage to `{medium, high}` so that
  restoring low has to be a deliberate update.
* There is a wrinkle worth recording: the score that re-tiered that example,
  `control_authority` = 2, is one the challenger pass explicitly flagged as
  unsupported ("The system does not supervise agents"). Under the old weighting
  the flag was inconsequential, so nothing forced the question. Under the current
  rule an unsupported score decides a tier. That is an argument for the challenge
  resolution flow being load-bearing, not decorative.
