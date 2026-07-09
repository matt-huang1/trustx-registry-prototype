# ADR-0010: Classify master column reweighted — free-text input as hero, cached examples as secondary

- Status: Accepted
- Date: 2026-07-09

## Decision
Within the Classify tab's master (left) column only, reorder and reweight:

1. The description **textarea leads the column** under a prompting section-label
   ("Describe an agent to classify"), slightly taller than before (`min-height: 9rem`),
   with the Classify button directly beneath — the unmistakable primary action.
2. The **cached examples are demoted** beneath it under a quiet sentence-case
   subheading ("Or try an example") with no rule — deliberately lighter than the hero's
   section-label — and the example buttons are rendered more compactly (smaller padding
   and type, secondary ink). They keep their name + tier-badge anatomy, borders,
   `aria-pressed` state, and keyboard access.

Nothing else moves: the master–detail grid, column widths (shared with Registry),
the right-side result pane, the live-classify path, and the ≤800px stacking are all
unchanged. Clicking an example still renders into the same detail pane.

## Why
The column read backwards. The examples sat first and largest, so they presented as the
primary action, when they are fallback/demo aids — committed fixtures that exist so the
page always has something to show without a model call (ADR-0005). The point of the tab
is classifying *your* agent; the input is the one action that exercises the actual
pipeline. Hierarchy should follow intent: hero input first, shortcuts second, expressed
through position and weight rather than any new visual device.

## Alternative considered
**Centre the input Google-style** (a lone hero textarea in the middle of the tab, with
examples below it). Rejected: it reintroduces exactly the dead-space imbalance the width
pass removed (ADR-0008), breaks the master–detail symmetry with Registry, and turns a
reference page into a search-engine pastiche. The hierarchy problem is solved by
reordering and reweighting inside the existing envelope, not by abandoning it.
