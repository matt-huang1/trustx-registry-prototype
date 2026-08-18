# 0012 — Adopt the ARC 12-dimension schema + worst-case-wins; tier weighting as explicit per-type profiles (scoring vs weighting separated)

## Decision

Replace the four placeholder dimensions with the real ARC 12-dimension model
(four groups, each dimension tiered 1/2/3), with ids, names, groups, and
per-tier labels taken **verbatim** from the reference material — RAI's published
ARC working paper (*TrustX Agent Risk Classification Framework (ARC):
Risk-Tiering Internally Created Agentic AI Systems*; full citation in
[CITATION.md](../../CITATION.md)) —
(`assets/arc_reference.json` → `schema/dimensions.json`). Entries additionally
carry `system_type` (the seven ARC system types) and `autonomy_level` (1–3).

Split the rollup into two separately-owned ideas:

* **Scoring is total.** Every entry always scores ALL 12 dimensions, each with
  rationale and evidence. The classifier prompts demand all 12; the schema
  requires all 12; the build fails on fewer.
* **Tier weighting is a per-type profile, committed as data.** Which of those
  scores drive the rolled-up `risk_tier` is defined in
  `policy/tier_weighting_profiles.yaml`, seeded from the reference profiles.
  The rule over a profile's `tier_dimensions` is worst-case-wins: any = 3 →
  Tier 3 (high); else max = 2 or average ≥ 1.5 → Tier 2 (medium); else Tier 1
  (low). A profile with `use_autonomy_level: true` also forces Tier 3 when
  `autonomy_level` is 3. An entry with no `system_type`, or a type without a
  profile, uses the `recommended_default` profile: worst-case-wins over ALL 12.

Every entry records its derivation (`tier_derivation`: the profile applied, the
weighted dimension set, the dimensions that actually drove the tier, and
whether autonomy level forced it), and the build re-derives and asserts it, so
the tier is always inspectable and never drifts from the scores.

## Context

The reference material contains a real divergence, surfaced while extracting
the model:

> The ARC per-type classification tools tier off different dimension sets by system
> type — five critical dimensions (Autonomy, Action Authority, Blast Radius,
> Persistence, Reversibility) for most types; all 12 plus the autonomy level
> for transaction/commerce agents — while the reference registry states
> worst-case-wins across all 12 dimensions.

This is recorded respectfully as a **divergence surfaced, not a bug**: tiering
most system types off the five dimensions that most directly measure an
agent's ability to do harm is a defensible design; so is the registry's
stated all-12 rule. But left implicit, the two silently disagree — e.g. a
knowledge assistant over regulated, crown-jewel data (Data Sensitivity = 3) is
Tier 3 under the stated all-12 rule and Tier 1 under the five-dimension
knowledge profile. `tests/test_rollup.py` proves exactly this case, and the
KYC archetype embodies it on a real entry.

## Alternatives considered

1. **Hardcode the registry's stated all-12 rule** and ignore the per-type tool
   formulas. Simple, but silently discards observable reference behaviour and
   makes the divergence undiscussable.
2. **Hardcode the per-type tool formulas.** Reproduces the tools, but then the
   registry's own stated rule is false for our data, and the weighting logic
   is buried in code.
3. **Per-type profiles as committed data (chosen).** The divergence becomes an
   explicit, reviewable configuration choice. Both behaviours are expressible;
   swapping a profile is a YAML change with tests; each entry names the
   profile that tiered it.

## Why

* The registry's thesis is *defensible, evidence-backed entries*. A tier whose
  weighting rule is invisible is not defensible; `tier_derivation` makes the
  "why" part of the record.
* **Recommended default: worst-case-wins over all 12** (as the reference
  registry states), because no dangerous dimension — e.g. Data
  Sensitivity = 3 — should be ignorable by construction. Narrower per-type
  profiles remain available, but as a deliberate, visible choice.
* Scoring all 12 regardless of weighting means changing a profile later never
  requires re-scoring: the evidence is already on record.

## Addendum (2026-07-24) — published paper confirms the divergence

The reference material this ADR extracted from is now a published arXiv working
paper — Hannah M. Liu, Rhea Saxena, and Shiv Asthana, "TrustX Agent Risk
Classification Framework (ARC): Risk-Tiering Internally Created Agentic AI
Systems", arXiv:2607.09586 [cs.AI], 2026 (full citation in
[CITATION.md](../../CITATION.md)) — and is the authoritative published source.
This addendum is documentation only; no rollup code or profile data changed.

* **The published rule (Section 3.3).** The paper specifies the tier rule with
  no dimension-subset restriction: any dimension at 3 yields Tier 3. The paper
  names this the **"critical dimension" approach**. This matches this repo's
  `recommended_default` (all-12) profile.
* **The paper's own example confirms the divergence (Section 5.2).** The
  paper's illustrative Decision Support example scores Data Sensitivity 3 with
  average 1.42 and places the system at Tier 3 — a result the corresponding
  per-type tool's 5-dimension weighting would not produce, since
  `data_sensitivity` is outside that subset. The divergence between the
  published rule and the per-type tool formulas is therefore confirmed by the
  paper's own worked example.
* **Terminology.** Docs adopt the paper's term "critical dimension approach"
  alongside "worst-case-wins".
* **OPEN ITEM — RESOLVED by [ADR-0017](0017-autonomy-level-rule-arc-paper.md)
  (2026-07-24).** The paper applies autonomy level to tier determination for
  all system types (L5 → Tier 3; L3/L4 lift borderline Low/Medium), whereas
  this prototype applied autonomy level only where the per-type tools did
  (transaction/commerce). ADR-0017 aligns `recommended_default` with the
  paper's rule, adopts the L1-L5 scale, and records the conservative reading
  of the L3/L4 lift; the matching ROADMAP open item is closed.

## Addendum (2026-08-17) — the divergence is RESOLVED; the subsets were outdated

**THE FINDING RECORDED IN THIS ADR IS NOW CLOSED.** On 2026-08-16 RAI confirmed,
verbally and from the framework's author, that the per-type five-dimension tier
formulas carried by the v1.1 classification spreadsheets are an **outdated
version** of the model, and that the paper's Section 3.3 rule — all twelve
dimensions, worst-case-wins, with the autonomy-level provisions — is the current
one. The divergence this ADR surfaced was an implementation artefact of the
tooling, not a second defensible reading of the framework.

[ADR-0019](0019-per-type-profiles-aligned-to-current-all-12-rule.md) acts on
that: every per-type profile now implements the current rule, and the superseded
subsets are retained under `legacy_<type>_v1_1` keys for auditability. Two
committed entries and one cached example re-tiered (KYC medium → high;
summarisation assistant low → medium; the public-docs example low → medium); all
three adopted RAI seed entries reproduce their published tiers unchanged. No
scores were re-scored and no rollup code changed — see ADR-0019 for the full
before/after.

What this ADR decided still stands, and is what made the correction cheap:
scoring stays total, weighting stays inspectable per-type data, and every entry
still records the derivation that produced its tier. The specific per-type
*values* seeded from the v1.1 tools are what became history. The remaining open
question is no longer *which* weighting is correct, but who owns weighting
changes and how one is ratified, since a change like this re-tiers entries across
the registry (PLAN §9).
