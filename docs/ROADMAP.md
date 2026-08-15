# Roadmap

A staged path from this prototype to a usable open registry. The maker/checker classifier,
the ARC 12-dimension model with per-type tier-weighting profiles, the web view, and the
contribution machinery (schema, evidence checks, trust tiers, governance, CI gates) are
shipped. What remains, tracked below, is the path to production: persistence and entry
lifecycle, a risk-tier-driven human gate, and exposing the registry as a live service any
agent can query.

## TODO
- [x] M0: Repo skeleton, memory, runnable maker/checker loop, deterministic override, ADRs.
- [x] M1: Swap placeholder dimensions for RAI's real 12 dimensions — done as the ARC
  12-dimension model with per-type tier-weighting profiles (ADR-0012) and the
  money-movement floor re-mapped to Action Authority = 3 (ADR-0013).
- [ ] M2: Risk-tier-driven human gate (auto-approve low tier, mandatory review for high).
- [ ] M3: Persistence + entry lifecycle (draft/challenged/ratified/published).
- [x] M4: Web UI in `web/` for browsing entries — delivered as the single-file view
  (ADR-0004) with the classifier tab (ADR-0005) and the runtime policy gate (ADR-0006).
  Remaining scope: in-browser submitting and challenging of entries.
- [ ] M5: Batch classification + evidence-source ingestion.
- [ ] M6: Expose the runtime policy gate (ADR-0006) as a live **MCP/A2A endpoint** any agent
  queries at the moment it tries to act — the prototype's offline `decide()` and
  `web/data/policy.json` are the display-time projection of this service.

## Open items

- [x] Autonomy-level alignment with the published ARC paper (arXiv:2607.09586; see the
  2026-07-24 addendum to ADR-0012) — **resolved by
  [ADR-0017](adr/0017-autonomy-level-rule-arc-paper.md)**: `recommended_default` now
  implements the paper's Section 3.3 autonomy rule (L5 forces high; L3/L4 lift to at
  least medium), the autonomy scale is the paper's L1-L5 end to end, and per-profile
  behaviour is expressed as `autonomy_rule` data. No committed entry changed tier.
