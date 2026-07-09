# 0015 — Record-layout revamp: derivation callout, number-in-box tier cells, not-weighted as cell state, collapsible standards, gate scenario-first

## Decision

One coherent pass over the shared record renderer and the Classify / Policy
Gate tab layouts (amends ADR-0014's cell anatomy; everything below applies
identically to the registry detail, the classify result, and the gate checker):

* **`driving_dimensions` correctness fix (upstream, in
  `classifier/schema.py`)** — a dimension "drives" the tier only when it sits
  at the tier-determining score AND that score is above baseline (> 1). An
  all-baseline Tier 1 entry has NO driver: the tier is low because nothing
  rose, not because of any one dimension. Previously every low entry listed
  its whole weighting profile as drivers. The gate
  (`classifier/policy_gate.py`) treats an empty driver list on a derived
  entry as meaningful — its reason states that nothing rose above baseline —
  and only falls back to peak-score dimensions when an entry has no
  `tier_derivation` at all.
* **Tier-derivation summary as a callout** — the "Weighting profile … tier
  driven by …" sentence is the record's key why-this-tier summary, so it
  renders as a distinct tinted strip (the existing `paper-2` surface with the
  3px accent left rule — the same callout family as `.evidence` and
  `.cls-banner`), spanning the full content width, instead of blending into
  body prose. No-driver records state "No weighted dimension rises above
  baseline — nothing drives the tier."
* **Number-in-box tier cells** — each strip cell previously showed a coloured
  square AND a score figure, both encoding tier. Merged: one tier-toned box
  containing the score figure leads the cell, followed by the dimension name.
  The legend's tier entries mirror the same mark. Descending-by-score order
  within each group band is unchanged.
* **"Scored · not tier-weighted" as a CELL STATE** — dashed muted cell, the
  score box outlined instead of filled, plus a small superscript dagger (†),
  explained once in the per-record legend — never an inline chip crammed into
  the cell. The state now also requires the score to be above baseline, so
  all-baseline records don't dagger every out-of-profile dimension.
* **Collapsible per-dimension standards** — the inline run-on standards line
  becomes a `<details>` fold ("Standards (n) ▸"), collapsed by default so the
  12-dimension ledger stays scannable, expanding to light framework→control
  chip groups.
* **Standards data seam for future consolidation** — the folds render through
  one reusable helper, `standardsFor(dimId)`, the single accessor over the
  committed matrix (`schema/standards_matrix.json` via `window.__ARC_META__`)
  returning a dimension's framework→controls mappings in framework order. A
  future consolidated "Standards coverage" section (all dimensions ×
  frameworks in one matrix) must reuse this same helper and data without
  rework; it is deliberately NOT built now.
* **Container-responsive tier strip** — the four ARC group bands are columns
  of one grid: 4-up on a wide record, 2×2, then a single column, via
  `@container` queries over the record's own width
  (`.record { container-type: inline-size }`), so the narrow registry detail
  pane and the full-width classify result each wrap at the right point. No
  horizontal scroll at any width.
* **Classify uses the full width** — the derivation callout and the strip span
  the whole content envelope below the centered input block (per ADR-0011's
  vertical flow), eliminating the dead right half.
* **Policy Gate: scenario first, stacked sections** — the scenario player (the
  tab's highlight) moves to the top, followed by the Active policy table and
  the check-any-agent checker, each full width. The former two-column row is
  removed: the checker renders a whole record (tier strip and all) and is far
  taller than the short policy table, so the columns left a large empty scroll
  gap beside the checker.

## Context

The record accreted three visual debts: the tier-derivation sentence — the one
line that explains the tier — read as ordinary prose; strip cells encoded the
tier twice (square + figure) while jamming a long "scored · not tier-weighted"
chip inline; and twelve run-on standards lines dominated the ledger. Layout-
wise, the classify result used half its width, and the gate buried its scenario
under a lopsided two-column row. Underneath all of it sat a correctness bug:
`derive_risk_tier` marked the profile's peak-score dimensions as drivers even
when the peak was baseline 1, so every Tier 1 entry claimed its entire
weighting profile "drove" a tier that nothing drove — and the strip dutifully
ringed five cells on the calmest records.

## Alternatives considered

* **Keep baseline drivers, hide them in the UI** — rejected. `tier_derivation`
  is recorded on every committed entry and validated by `--check`; a display
  filter would leave false driver claims in the audit trail the registry
  exists to keep truthful. Fixed at the derivation, data rebuilt.
* **Viewport media queries for the strip breakpoints** — rejected. The same
  renderer draws into containers of very different widths (registry pane vs
  full-width classify result); one viewport breakpoint is wrong for at least
  one of them. Container queries measure the record itself.
* **Auto-fit grid (`repeat(auto-fit, minmax(...))`) for the bands** —
  rejected. With exactly four bands, auto-fit passes through a 3+1 wrap state
  that reads as a mistake; explicit 4 → 2 → 1 keeps the bands paired.
* **Standards as an always-visible chip row (option a)** — rejected. Twelve
  expanded chip groups re-create the wall of text the fold exists to remove;
  the mappings are reference material, not per-entry findings.
* **Building the consolidated standards matrix now** — rejected as scope; the
  seam (`standardsFor` + the committed matrix) is the deliverable, so the
  future section is a pure addition.
* **Gate: aligning the two columns instead of stacking** — rejected. The
  checker's height varies with the selected entry (strip + evidence +
  overrides); any static column pairing re-creates the empty-gap imbalance on
  some selection.

## Why

The derivation is the record's headline argument — it should look like one.
One mark per cell that carries both colour and value removes a redundancy the
eye had to reconcile twelve times per record. Making not-tier-weighted a quiet
cell state (with a single legend explanation) keeps the scoring-vs-weighting
finding visible (ADR-0012/0014) without shouting it in every affected cell.
And with the driver fix, the accent ring finally means what it says: it only
ever marks a dimension that genuinely set the tier. Scenario-first on the gate
puts the demo's payoff where a reader lands. All changes reuse the existing
tokens and callout family — no new palette, no chart library, single file.
