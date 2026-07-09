# ADR-0011: Classify uses vertical flow (centered input, full-width result below), not master-detail

- Status: Accepted
- Date: 2026-07-09

## Decision
The Classify tab drops the master–detail grid (introduced by ADR-0008, reweighted by
ADR-0010) in favour of a vertical flow:

1. **A centered, contained input block** (~42rem, balanced margins — the one
   deliberately-contained element on the page): the "Describe an agent to classify"
   section-label, the textarea as the clear focal point, the Classify button beneath
   it, then a quiet "Or try an example" row of compact cached-example buttons
   (name + tier badge, `aria-pressed`, keyboard access — all unchanged).
2. **The result region below at full envelope width**, rendered by the same shared
   open `.record` renderer used by the registry detail and gate checker. Before any
   selection it shows a quiet empty state ("Select an example or classify a
   description to see its full risk record") instead of auto-selecting the first
   example; clicking an example or running a live classification populates it.

Registry keeps master–detail; the Policy Gate is untouched.

## Why
Layout should follow the tab's job. Registry is **browse-many / inspect-one** — a
persistent index beside a detail pane is the right shape, because the list is a
navigation surface you keep returning to. Classify is a **single action → single
result**: you describe an agent once, you read one record. Rendered as master–detail,
the input read as a permanent sidebar — furniture — while the result dominated the
stage, inverting the tab's intent even after the ADR-0010 reweighting. A top-to-bottom
flow puts the action first and its consequence after it, which is how the task actually
runs. The two tabs now differ intentionally, and each difference is explainable by the
work the tab does. The width principle of ADR-0008 survives: the result (structured
content) fills the envelope; the input block is contained because a ~42rem measure is
what a form wants, not because the layout forgot the space.

## Alternatives considered
- **Keep master–detail.** Maximum symmetry with Registry. Rejected: symmetry of layout
  misrepresented an asymmetry of purpose — the input is not an index, and pinning it in
  a sidebar makes the primary action read as secondary chrome.
- **Centre the input Google-style with no full-width result region.** Puts the hero
  front and centre. Rejected: without the result filling the envelope beneath, the tab
  reverts to the centered-dead-space layout the width pass (ADR-0008) removed.
