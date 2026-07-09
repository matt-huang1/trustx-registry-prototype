# Architecture & Plan

> **Scaffold — not finished prose.** Each section below states in one line what it
> must cover and carries a `TODO` marker. Fill each section in place. Where a
> `Draws on:` pointer is given, build on that existing material rather than
> rewriting it from scratch.

## 1. Problem & who it's for

*State why self-attestation fails as a basis for trusting an AI agent's risk
posture, then name the concrete users and the job each brings: the developer
classifying their own build, the risk officer looking up an existing agent, the
auditor who needs evidence, the procurement reviewer assessing a vendor agent,
and the working group curating the standard.*

TODO

## 2. What the registry is

*Define the registry as a set of evidence-backed entries rather than asserted
labels: one source of truth producing two outputs (machine-readable JSON and a
human-readable page), with the computed risk tier as the single source of truth.*

Draws on: [schema/entry.schema.json](../schema/entry.schema.json), [scripts/build_registry.py](../scripts/build_registry.py).

TODO

## 3. Architecture

*Describe the risk-proportionate maker/checker: the model proposes, deterministic
checks decide wherever a fact can be pinned down, and an accountable human owns
the rest with scrutiny scaled to the tier. Use the money-movement override as a
worked example, and present the MCP-queryable core as the forward-looking piece.*

Draws on: [docs/adr/0001-risk-proportionate-maker-checker.md](adr/0001-risk-proportionate-maker-checker.md), [docs/adr/0002-model-agnostic-llm-access.md](adr/0002-model-agnostic-llm-access.md), [classifier/](../classifier/).

TODO

## 4. Open-source structure & contribution model

*Lay out how the registry runs as an open-source project: git-backed YAML/JSON
entries, contributions by PR, CI gates (schema + challenger + standards), human
ratification, trust tiers, signed provenance, expiry/re-review, and the licence
split between code and data.*

Draws on: [docs/OPEN_SOURCE_MODEL.md](OPEN_SOURCE_MODEL.md), [.github/workflows/ci.yml](../.github/workflows/ci.yml).

TODO

## 5. Trust & abuse resistance

*Enumerate the ways the registry could be gamed — self-flattering scores,
sock-puppet contributors, stale entries, tampering — and how the design resists
each.*

TODO

## 6. The demo

*Describe what is built (browse/registry) and the three demonstrated features —
classify-first, runtime policy gate, and x-LOD reporting — saying what each one
is meant to show.*

Draws on: [web/](../web/), [docs/adr/0004-single-file-web-demo.md](adr/0004-single-file-web-demo.md).

TODO

## 7. Productionisation & scale

*Chart the path from prototype to production: single-file HTML → Next.js +
registry API, JSON file → database, model-agnostic/open-weight/on-prem
deployment, LangGraph for durable orchestration, and versioning/drift handling.*

TODO

## 8. Non-goals & limitations

*State what the registry deliberately does not do: it does not decide truth about
the world, it does not replace the accountable human, and its dimensions are
placeholders pending the real schema.*

TODO

## 9. Open questions for the working group

*List the questions left open for the working group: how tiers weight dimensions,
how challenges are adjudicated, and who governs the registry itself.*

TODO

## See also

- [docs/DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) — ADR index.
- [docs/ROADMAP.md](ROADMAP.md) — roadmap.
