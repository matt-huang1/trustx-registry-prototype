# ADR-0008: Centered content envelope; structured content uses full width, prose stays at readable measure

- Status: Accepted
- Date: 2026-07-09

## Decision
All three tabs of `web/index.html` share one centered content envelope (the `.shell`,
max-width 1160px with symmetric margins), and within it the rule is:

- **Structured and interactive content fills the envelope.** Inputs, results, dimension
  records, evidence blocks, tables, and scenario steps span their available column. Two
  scaffolds carry this: a shared `.master-detail` grid (fixed ~300px master column |
  fluid detail) used identically by Registry (index | record) and Classify (inputs |
  result), and on the gate a two-column row (`.pg-columns`) pairing the Active policy
  with the check-any-agent picker, above a scenario player whose steps lay out
  left-to-right across the full envelope on wide screens (`grid-auto-flow: column`).
- **Only running prose is narrow.** Ledes, notes, descriptions, and rationales keep a
  ~66ch measure via per-element `max-width` — the measure travels with the text, not
  with its container.
- **One breakpoint family.** Both scaffolds stack to a single column ≤800px (the
  registry's existing breakpoint); the scenario row additionally requires ≥960px so
  step cards are never squashed at mid widths.
- *Refinement:* the short intro lede directly under each tab heading (all three tabs)
  is exempt from the 66ch cap and spans the envelope (`.panel-note--wide`),
  left-aligned; all body prose keeps the readable measure.

## Context
After the tab restructure (ADR-0007), Classify and Policy Gate were capped at ~70ch and
left-aligned, leaving roughly 40% of the envelope empty on the right while Registry
filled it with master–detail — three tabs, two different ideas about width. The narrow
columns were an over-application of the readable-measure rule: it protects paragraphs,
but example pickers, forms, decision cards, and tables are not paragraphs, and capping
them just relocated their content into a dead-space layout.

## Alternatives considered
- **Keep the left-aligned narrow columns.** Zero work and maximally safe for the prose.
  Set aside because the imbalance is the defect: two tabs read as unfinished drafts next
  to Registry, and wide monitors get a page that looks dumped against the left margin.
- **Center the narrow column instead of widening it.** Fixes the left-dumped look
  cheaply. Set aside because it centres the dead space instead of removing it, breaks
  the shared left edge with the masthead and Registry (the strongest alignment line on
  the page), and still refuses the width to content that can use it.
- **Go full-width edge-to-edge (drop the envelope max-width).** Uses every pixel. Set
  aside because an unbounded canvas destroys the reference-document register: prose
  lines and tables sprawl on large monitors, and the page loses the deliberate margins
  that make it read as a set document rather than an app shell.

## Why
The envelope keeps the page a centered, bounded document; the structured/prose split
gives each kind of content the width it actually benefits from. Reusing Registry's
master–detail grid for Classify makes the two tabs siblings rather than lookalikes —
same column widths, same gap, same sticky master — and the gate's two-column row plus
full-width scenario removes the last dead column without inventing any new visual
language. The readable measure survives exactly where it matters: in sentences.
