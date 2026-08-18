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
- [x] The tier-weighting divergence recorded in ADR-0012 (per-type five-dimension subsets
  vs the paper's all-12 rule) — **resolved by
  [ADR-0019](adr/0019-per-type-profiles-aligned-to-current-all-12-rule.md)** after RAI
  confirmed (2026-08-16, from the framework's author) that the v1.1 subset formulas are
  outdated. Every per-type profile now implements the current rule; the subsets are
  retained as `legacy_<type>_v1_1` for auditability. Two entries re-tiered
  (KYC medium → high, summarisation low → medium) and one cached example
  (public-docs low → medium); all three RAI seed entries reproduce their published tiers
  unchanged.
- [ ] **Governance of weighting changes** (the part ADR-0019 does *not* settle): who owns
  the tier-weighting profiles, what evidence a change must carry, who ratifies it, and
  what is owed to consumers of an entry whose tier is about to move. ADR-0019 arrived as
  a verbal confirmation and re-tiered live entries with no ratification step — cheap to
  change is not the same as safe to change. See PLAN §9.
- [ ] Restore low-tier coverage in the cached classifier examples: the public-docs example
  re-tiered to medium on a `control_authority=2` the challenger flagged as unsupported, so
  the hero currently shows no low-tier run. Needs an author-run
  `build_registry.py --rebuild-examples` against a live model, or a new example
  description. `tests/test_examples_build.py` pins the current `{medium, high}` coverage
  so restoring low is a deliberate update.
