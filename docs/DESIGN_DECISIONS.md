# Design Decisions

An index of Architecture Decision Records (ADRs). Each non-obvious design decision gets an
ADR in [docs/adr/](adr/) (Decision / Context / Alternatives considered / Why) and a line
here. If you are unsure whether a decision needs an ADR, err toward writing one.

| ADR | Title | Status |
|-----|-------|--------|
| [0001](adr/0001-risk-proportionate-maker-checker.md) | Risk-proportionate maker/checker with deterministic override | Accepted |
| [0002](adr/0002-model-agnostic-llm-access.md) | Model-agnostic LLM access via an OpenAI-compatible interface | Accepted |
| [0003](adr/0003-curated-reference-entries.md) | Curated reference entries: hand-authored, archetypal, defensible | Accepted |
| [0004](adr/0004-single-file-web-demo.md) | Single-file HTML demo; registry data injected as a JS global for zero-dependency offline rendering | Accepted |
| [0005](adr/0005-cached-first-classifier-demo.md) | Cached-first classifier demo; live path via an optional local endpoint; no client-side keys | Accepted |
| [0006](adr/0006-runtime-policy-gate.md) | Runtime policy gate: deterministic tier-to-action enforcement over committed registry data; client-side display of pre-computed decisions; MCP endpoint deferred | Accepted |
| [0007](adr/0007-hash-based-tabs.md) | Hash-based tabbed single-page layout; left-aligned horizontal nav | Accepted |
| [0008](adr/0008-content-envelope-widths.md) | Centered content envelope; structured content uses full width, prose stays at readable measure | Accepted |
| [0009](adr/0009-consistent-active-state-and-record-treatment.md) | Consistent restrained active-state and unified record treatment across tabs | Accepted |
| [0010](adr/0010-classify-input-as-hero.md) | Classify master column reweighted: free-text input as hero, cached examples as secondary | Accepted |
| [0011](adr/0011-classify-vertical-flow.md) | Classify uses vertical flow (centered input, full-width result below), not master-detail | Accepted |
| [0012](adr/0012-arc-12-dimension-schema-and-tier-weighting-profiles.md) | Adopt ARC 12-dimension schema + worst-case-wins; tier-weighting as explicit per-type profiles (scoring vs weighting separated) | Accepted |
| [0013](adr/0013-money-movement-floor-action-authority.md) | Money-movement floor re-mapped to Action Authority = 3 ("Execute transactions") | Accepted |
| [0014](adr/0014-grouped-tier-strip-visualization.md) | Grouped tier-strip visualization: peak-forward summary above the per-dimension detail, driver + scored-not-tier-weighted marked (radar/bars rejected as visually averaging) | Accepted |
| [0015](adr/0015-record-layout-revamp.md) | Record-layout revamp: derivation callout, number-in-box tier cells, not-weighted as cell state, collapsible standards (reusable seam for future consolidated coverage), gate scenario-first; includes the driving_dimensions above-baseline correctness fix | Accepted |

## Notes

- Extension of ADR-0009 (unified marker family): each dimension's score in the shared
  record renderer now carries the tier-toned square marker (same metrics as the `.tier`
  and `.pg-outcome` marks) plus a bolder verbatim tier label, so the tier reads at least
  as prominently as the dimension name everywhere a dimension renders. Rebalance only —
  no new treatment family, so no separate ADR.
- Refinement of ADR-0014/0015 (one score mark): the per-dimension detail rows reuse the
  strip cells' number-in-a-tier-toned-box mark (`.scorebox`) — the former square marker,
  "n / 3" figure, and 3-pip scale are gone, so strip and detail encode a score exactly
  one way across registry, classify, and gate. Same pass: standards folds became
  explicit whole-row disclosure controls (rotating caret, hover, `aria-expanded`), and
  the record/policy descriptions span the full content width.
