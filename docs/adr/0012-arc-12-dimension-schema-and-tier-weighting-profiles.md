# 0012 — Adopt the ARC 12-dimension schema + worst-case-wins; tier weighting as explicit per-type profiles (scoring vs weighting separated)

## Decision

Replace the four placeholder dimensions with the real ARC 12-dimension model
(four groups, each dimension tiered 1/2/3), with ids, names, groups, and
per-tier labels taken **verbatim** from the reference material
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

> The AEGIS classification tools tier off different dimension sets by system
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
