# ADR-0009: Consistent restrained active-state and unified record treatment across tabs

- Status: Accepted
- Date: 2026-07-09

## Decision
Two refinements to `web/index.html`, both resolving inconsistencies flagged in the
ADR-0008 self-audit and decided by the author:

1. **One active-state language.** The tier filter's active segment (All / Low / Medium /
   High) no longer fills with solid ink. It uses the same quiet treatment as the tab
   nav's active tab: an ink-blue underline (drawn as an inset shadow so the segmented
   box stays intact) with the label in the accent colour. Buttons, `aria-pressed`, and
   keyboard behaviour are unchanged — only the visual state changed.
2. **One record treatment everywhere.** The gate's "check any agent" decision renders
   with the same open record treatment as the registry detail and the classify result —
   shared `.record` / `.rec-head` / `.rec-title` classes, no boxed chrome. The scenario
   step cards deliberately keep their borders: they are steps in a plan (a card family),
   not standalone records.

## Why
Coherence over per-section invention. The page had two ways of saying "this is active"
(a filled ink block in the toolbar, a quiet accent underline in the nav) and two ways of
presenting the same kind of content (classification/decision records open in Registry
and Classify, boxed in the gate checker). A reader should learn each convention once:
active means accent underline, wherever it appears; a record looks like a record,
whichever tab produced it. Both changes remove a variant rather than adding one, which
is the direction this design should always move — restraint over decoration.
