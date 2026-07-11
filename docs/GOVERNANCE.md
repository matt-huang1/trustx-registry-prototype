# Governance

This document describes the **mechanism** by which the registry is maintained, entries are
ratified, and challenges are resolved. The prototype *implements* this mechanism; the
substantive constitution — who the maintainers actually are, the exact quorum, the appeals
body — is for the working group to own and ratify. What is encoded here in code and CI is the
part that must not be left to good intentions: that trust is earned and traceable, never
self-asserted or voted into being.

See [ADR-0016](adr/0016-contribution-model-trust-tiers.md) for the design rationale.

## Maintainers

**Maintainers** are the identified people accountable for the registry. A maintainer can:

- review and ratify a `community-submitted` entry (promote it to `working-group-reviewed`);
- adjudicate a challenge and cut a new version of an entry;
- review and merge changes to the schema, rules, or tooling.

Maintainers are listed by their real, attributable identity (a `MAINTAINERS` file /
`CODEOWNERS` in the working group's instance). **New maintainers are added by consensus of
the existing maintainers**, recorded in a PR — not by application volume, activity count, or
any automatic threshold. Maintainer status can be revoked the same way.

Because identity is the anchor of trust here, a maintainer acts under their own name: every
ratification records `review.reviewed_by`, and every entry version is attributable.

## Who may ratify an entry

**Only identified maintainers / working-group members may ratify an entry.** Ratification is
recorded on the entry (`review.reviewed_by`, `review.reviewed_at`) and promotes its trust
level. The build **refuses** to admit a `working-group-reviewed` or `verified` entry whose
`review.reviewed_by` is null — so the label cannot exist without a named human behind it.

**Trust is not a vote.** We deliberately do **not** promote entries by community upvote,
reaction count, or "N approvals from anyone." A vote-based mechanism is *floodable*: a
population of sock-puppet accounts can manufacture consensus at near-zero cost, and the
whole value of this registry is that a classification is defensible rather than popular.
Scrutiny scales with risk — a high-tier entry warrants more reviewer diligence than a
low-tier one — but the *authority* to confer trust always rests with identified humans who
put their name on the review, never with an anonymous tally.

`verified` is a stricter bar than `working-group-reviewed`: it additionally requires that the
entry be traceable to authoritative source material (e.g. adopted verbatim from a published
reference registry), recorded in `provenance.note`.

## Freshness and expiry

A ratification is not permanent. Every reviewed entry carries `review.expires_at`, a
freshness horizon after which it must be **re-ratified**. An entry past its horizon is stale:
its trust level no longer reflects current review, and it should be re-examined against the
agent's current behaviour and the current model. Re-ratification follows the same path as
initial ratification and is recorded as a new review.

## How challenges are adjudicated

Anyone may challenge an existing entry by opening an issue **with evidence** (see
[CONTRIBUTING.md](../CONTRIBUTING.md) and the challenge issue template). The evidence field
is required; a challenge without evidence is not actionable and is closed as such.

Adjudication:

1. A maintainer triages the challenge and confirms it cites evidence tied to a specific
   dimension and entry.
2. The maintainer weighs the cited evidence against the entry's current scores and rationale.
3. The outcome is one of: **upheld** (the entry changes), **rejected** (the entry stands, with
   the reasoning recorded), or **partially upheld**.

## Resolution produces a new VERSION, not an in-place edit

When a challenge is upheld, the entry is **re-issued as a new version** — the scores,
rationale, evidence, recomputed tier, and a fresh review record change together, and the
provenance of *why* it changed (the challenge) is retained. We do not silently overwrite the
old classification: the history of what an entry claimed, and why it changed, is itself part
of the evidence trail. (In this prototype a version is a commit that supersedes the entry
file; a production instance may keep prior versions addressable.)

A re-issued entry re-enters review: a changed entry is not automatically still
`working-group-reviewed` — the change must be ratified anew.

## How disputes escalate

If a challenger and a maintainer cannot agree on an adjudication, the dispute escalates to
the **maintainer group**, which decides by consensus of identified maintainers. If consensus
cannot be reached, the entry is marked **contested** and held at `community-submitted` (it
cannot carry a review label it no longer has agreement behind) until the working group
resolves it under its own constitution.

## Scope of this prototype

This repository encodes the *mechanism*: trust tiers in the schema, the build-time guarantee
that reviewed/verified requires a named human, evidence-required checks, recomputed tiers, and
the challenge/versioning flow described above. It does **not** presume to fix the working
group's membership, quorum rules, or appeals constitution — those are theirs to own. The
point of shipping the mechanism is that the governance is demonstrable and testable, not
merely described.
