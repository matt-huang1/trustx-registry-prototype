# 0018 — Progressive disclosure: glance layer vs full derivation; taught distinction rather than simplified away; one-registry narration

## Decision

Restructure the web view's information hierarchy for the first-time visitor,
without deleting any content:

* **Glance layer.** An open entry's immediately-visible layer is: name + risk
  tier + trust level (+ type/autonomy chips), the description, the one-sentence
  tier-derivation callout, and the grouped tier strip — roughly one screen that
  tells the whole story. The per-dimension detail ledger (rationale, evidence,
  standards per dimension) moves one intentional click deeper: **one collapsed
  `<details>` fold per ARC group**, with an explicit affordance ("Show the full
  derivation for this group") that flips on open, `aria-expanded` mirrored for
  assistive tech. Strip cells double as anchors: clicking a dimension cell
  opens its group's fold and scrolls to that dimension (buttons, so
  keyboard-reachable); on strip-only renders (the gate checker) cells stay
  non-interactive.
* **Teach the driver / not-weighted distinction — do not remove it.** One calm
  sentence directly above the strip ("Every dimension is scored, but only the
  marked dimensions count toward this agent type's tier — the ringed cells are
  the ones that drove it") bridges the first-time reader to the existing
  legend.
* **Claim → because → evidence.** In the detail, the score + verbatim tier
  label is the claim; the rationale now leads with a small "Because"
  connective; the quotes are labelled "From the agent's description" so they
  read as supporting evidence, not decoration.
* **Standards disclosure earns its place.** The collapsed label says what it
  is ("Maps to N governance standards") and the expanded view opens with one
  line of context (the mappings come from the ARC framework).
* **Policy gate reading order.** One-sentence tab intro; the scenario as the
  unmistakable headline with a one-sentence intro; then the active policy and
  the checker, each introduced by a single short line. The gate reason now
  states the rule and the driving fact once — the driving dimensions at their
  verbatim tier labels (`classifier/policy_gate.py`) — while the evidence
  block alone carries the quotes, so decision displays never repeat
  themselves.
* **One-registry narration.** Each tab's intro locates itself against the same
  registry in one clause: Registry — "the entries every other view draws on";
  Classify — "new classifications enter the same registry you can browse";
  Policy gate — "checks agents against the same registry you can browse — at
  the moment an agent acts".
* **Defect fixes in the same pass:** the trust-level legend lays out
  horizontally across the full envelope; master-list badges sit on a wrapping
  row contained inside their entry box; the bottom footnote spans the full
  envelope.

## Context

A design freeze pass judged every choice by one test: does this help a first
viewing, not a tenth one? The record previously opened onto the full
12-dimension ledger — the most information-dense surface in the page — before
a reader had absorbed what the tier even was; the gate tab was the worst
text-density case, saying the deterministic-lookup idea three ways. The calm
paper aesthetic, single-file/offline approach, and all existing content are
retained; things moved behind one intentional click, nothing was cut except
prose that repeated itself.

## Alternatives considered

1. **Remove the driver / not-weighted marks for simplicity.** Rejected: the
   distinction between "scored" and "drives the tier" is the design's central
   finding (ADR-0012/0014/0015) — hiding it would make the page prettier and
   the registry less honest. The fix is teaching, not deletion: one bridging
   sentence plus the existing legend.
2. **A single "Full derivation" expander for the whole ledger.** Considered;
   per-group folds read cleaner (four labelled groups mirror the strip's four
   bands, and a cell anchor can open just its group) and keep expanded runs
   shorter.
3. **Keep the ledger open and move it below provenance.** Rejected: reordering
   without disclosure still buries the glance layer's ending and leaves the
   first screen dense.

## Why

* A first-time visitor should know what to look at, in what order, within ten
  seconds of each tab: intro line → the one main thing.
* Progressive disclosure sequences content instead of deleting it — the full
  evidence trail (the registry's point) remains one click away, and the strip
  cells make that click targeted.
* Stating each fact once (reason vs evidence block; scenario intro vs step
  cards) is a de-duplication of prose, not a reduction of information.
