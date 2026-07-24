# Roadmap

A staged path from this classification-loop prototype to a usable open registry: first a
credible, testable maker/checker classifier over a placeholder schema (this milestone),
then RAI's real 12-dimension model, persistence, and a web UI for browsing and submitting
entries.

## TODO
- [x] M0: Repo skeleton, memory, runnable maker/checker loop, deterministic override, ADRs.
- [x] M1: Swap placeholder dimensions for RAI's real 12 dimensions — done as the ARC
  12-dimension model with per-type tier-weighting profiles (ADR-0012) and the
  money-movement floor re-mapped to Action Authority = 3 (ADR-0013).
- [ ] M2: Risk-tier-driven human gate (auto-approve low tier, mandatory review for high).
- [ ] M3: Persistence + entry lifecycle (draft/challenged/ratified/published).
- [ ] M4: Web UI in `web/` for browsing, submitting, and challenging entries.
- [ ] M5: Batch classification + evidence-source ingestion.
- [ ] M6: Expose the runtime policy gate (ADR-0006) as a live **MCP/A2A endpoint** any agent
  queries at the moment it tries to act — the prototype's offline `decide()` and
  `web/data/policy.json` are the display-time projection of this service.

## Open items

- [ ] Autonomy-level alignment with the published ARC paper (arXiv:2607.09586; see the
  2026-07-24 addendum to ADR-0012): the paper applies autonomy level to tier
  determination for all system types (L5 → Tier 3; L3/L4 lift borderline Low/Medium),
  whereas this prototype applies it only where the per-type tools did
  (transaction/commerce). Whether to align `recommended_default` with the paper is a
  pending maintainer decision — a weighting-behaviour change that would re-tier
  entries, so it needs its own ADR when decided.
