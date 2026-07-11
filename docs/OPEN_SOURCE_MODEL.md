# Open-Source Model

This project is intended to be developed in the open under a permissive MIT license so
that the risk taxonomy, the classification method, and the registry entries themselves
can be inspected, challenged, and reused. The value is in a *transparent and defensible*
method — model-agnostic and reproducible on open-weight or on-prem models — not in a
proprietary black-box score.

## The contribution model, shipped

The mechanism is now implemented in the repo, not just described:

- **Contribution & challenge** — how third parties submit and challenge entries:
  [CONTRIBUTING.md](../CONTRIBUTING.md), with structured issue/PR templates under `.github/`.
- **Governance** — who ratifies, how disputes over a score are resolved, and how a resolution
  produces a new *version* of an entry: [GOVERNANCE.md](GOVERNANCE.md).
- **Trust as a scaled, earned, revocable axis** — automated verification admits an entry at
  `community-submitted`; identified maintainers (never a vote) promote to
  `working-group-reviewed` / `verified`, enforced at build time:
  [ADR-0016](adr/0016-contribution-model-trust-tiers.md).
- **Licence split** — code under MIT ([LICENSE](../LICENSE)); registry content under CC BY 4.0
  ([LICENSE-DATA](../LICENSE-DATA)) so reuse carries attribution and provenance.

## Still open
- [ ] Relationship to RAI's forthcoming 12-dimension model and naming/attribution rules.
- [ ] Community review / sign-off process for schema changes.
- [ ] CLA or DCO decision (see a future ADR).
