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
