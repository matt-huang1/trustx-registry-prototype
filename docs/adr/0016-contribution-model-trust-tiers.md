# 0016 — Contribution model: automated verification as the trust-scaling mechanism

## Decision

The registry is open to contribution, and **trust is a scaled, earned, revocable property of
each entry — not a gate on the front door**. Concretely:

1. **Trust tiers live in the schema.** Every entry carries a required `trust_level` of
   `community-submitted` | `working-group-reviewed` | `verified`, plus a `review` block
   (`reviewed_by`, `reviewed_at`, `expires_at`). Trust level is a **separate axis** from
   `risk_tier`: one is how reviewed the *entry* is, the other how risky the *agent* is. The
   web view renders them with deliberately distinct mark families so they never conflate.

2. **Automated verification does the trust-scaling.** Anyone can open a PR. The automated
   pipeline — schema validation, evidence-required per dimension, deterministic floors,
   recomputed tier + derivation, and the challenger pass — admits an entry **on its own** at
   `community-submitted`. That tier is earned by *passing the machine*, not by anyone's
   permission. The 3 curated archetypes enter `working-group-reviewed`; the 3 adopted RAI seed
   entries enter `verified` (traceable to published reference material).

3. **Higher tiers require an identified human, enforced deterministically.**
   `build_registry.py` **fails the build** if an entry claims `working-group-reviewed` or
   `verified` without a non-null `review.reviewed_by`. The label cannot be forged: a
   contribution that arrives asserting `verified` with a null reviewer is rejected in CI. A
   freshly classified entry from `classifier.run` is always emitted as `community-submitted`
   with an empty review — a CLI approval does not mint review it does not have.

4. **Trust is revocable and expires.** `review.expires_at` is a freshness horizon; a lapsed
   entry must be re-ratified. Challenges (adjudicated per `docs/GOVERNANCE.md`) re-issue an
   entry as a new *version* and send it back through review — a changed entry is not
   automatically still reviewed.

5. **Ratification is by identified maintainers, never a vote** (see Alternatives).

## Context

The highest-priority deliverable for an open-source community is that the repo *demonstrates*
the contribution model, not merely describes it. The core project principle — the model
proposes, deterministic checks decide, an accountable human owns the rest, and scrutiny scales
with risk — extends naturally to contributions: the machine can safely admit an evidenced,
tier-consistent entry at a low trust level, but conferring *higher* trust is exactly the
"accountable human" step and must not be automatable or gameable.

## Alternatives considered

1. **Open and unchecked** (any submitted entry is just accepted/displayed). Rejected: it
   destroys the entire value proposition. The registry exists precisely because labels should
   be evidence-backed and checkable; accepting unverified self-asserted scores makes it the
   thing it set out to replace.
2. **Expert-gated only** (nothing enters without up-front maintainer sign-off). Rejected: it
   does not scale, throttles community contribution behind a maintainer bottleneck, and wastes
   the deterministic pipeline that can *already* verify most of what matters (schema, evidence,
   floors, tier). It also conflates "unreviewed" with "worthless" — a community-submitted entry
   that passed every machine check is useful and inspectable now, and reviewable later.
3. **Community voting** (promote entries by upvotes / approvals from anyone). Rejected: a
   vote-based mechanism is **floodable by sock-puppets** — a population of throwaway accounts
   can manufacture "consensus" at near-zero cost. Trust in a classification must rest on
   evidence and on a named human who put their identity behind the review, not on a tally that
   scales with account creation. Scrutiny scales with risk; *authority to confer trust* stays
   with identified maintainers.

## Why

Automated verification is the right trust-scaling mechanism because it is the part that is
*objective and gameable-proof*: schema, evidence presence, deterministic floors, and the tier
rollup are facts a machine can and should decide, uniformly, for every contributor. What a
machine cannot decide — "is this scoring judgement sound, and do I stake my name on it?" — is
exactly what the human tiers encode, and encoding "verified requires a named reviewer" as a
build failure makes the guarantee real rather than aspirational: you can read it in
`scripts/build_registry.py`, and `tests/test_trust_level.py` proves a sock-puppet `verified`
entry fails the build. The mechanism is shipped and testable; the working group owns the
constitution (membership, quorum, appeals) on top of it.
