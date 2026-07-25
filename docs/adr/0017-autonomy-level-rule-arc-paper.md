# 0017 — Autonomy-level rule aligned with ARC paper §3.3; conservative reading of the L3/L4 borderline lift; L1-L5 scale adopted

## Decision

Replace the boolean `use_autonomy_level` on tier-weighting profiles with a
per-profile `autonomy_rule` field (data, in
`policy/tier_weighting_profiles.yaml`):

* **`arc_paper`** — the published ARC rule (Liu, Saxena, and Asthana,
  arXiv:2607.09586, Section 3.3): autonomy level **L5 forces Tier 3 (high)**;
  **L3/L4 lift the tier to at least Tier 2 (medium)** — the rule only ever
  raises a tier, never lowers a dimension-derived one.
* **`none`** — the autonomy level does not affect the tier (faithful to the
  per-type tool spreadsheets, which do not use it).

`recommended_default` gets `autonomy_rule: arc_paper`, so the default profile
now implements Section 3.3 exactly (any dimension at 3 → high; L5 → high;
L3/L4 → at least medium). `transaction_commerce_agent` also gets `arc_paper`:
its per-type tool used the autonomy level, and under the scale migration below
its prior `use_autonomy_level` behaviour (old level 3 forces Tier 3) is exactly
the new rule's L5-forces-high case — same intent, same outcome. All other
per-type tool profiles get `none`, faithful to their spreadsheets.

`TierDerivation` records the rule's effect distinctly from dimension-driven
tiers: `autonomy_level_driven` (L5 forced Tier 3, as before) and the new
`autonomy_level_lifted` (L3/L4 raised an otherwise-low tier to Tier 2).

**Autonomy scale migrated from 1-3 to the paper's L1-L5.** The schema
(`schema/entry.schema.json`), the model metadata
(`schema/dimensions.json`, `assets/arc_reference.json`), the classifier prompt,
all committed entries, and the web view now use L1-L5. Mapping applied to
existing data (old → new): **1 → L1** (human-in-the-loop), **2 → L3**
(human-on-the-loop), **3 → L5** (fully autonomous) — the three old definitions
become the L1/L3/L5 anchors of the five-level scale. The L2 ("checkpoint
approval") and L4 ("supervised autonomy") definition strings are interpolations
between those published anchors, pending the paper's verbatim wording; replace
them if/when the exact text is transcribed.

## Context

ADR-0012 recorded (and its 2026-07-24 addendum confirmed from the published
paper) that the per-type classification tools and the published rule diverge.
The paper's Section 3.3 rule applies the autonomy level to tier determination
for **all** system types; this prototype previously applied it only where the
transaction/commerce tool did. The addendum left alignment as an open item;
this ADR resolves it. Re-deriving every committed entry and cached example
under the new rule changed **no tiers**: the adopted ARC seed entries still
reproduce their published tiers (RAI-OPEN-0001 high, RAI-OPEN-0002 low,
RAI-OPEN-0003 medium), enforced by `tests/test_entries_valid.py` and the
build's re-derivation check.

**Conservative reading of the borderline lift.** The paper says L3/L4 lifts
tiers "borderline between Medium and Low". Deciding what counts as
"borderline" would itself be a judgement call embedded in code, so this design
implements the conservative, unambiguous reading: under `arc_paper`, **L3/L4
always lifts a low tier to at least medium**. This is deliberately stricter
than a literal borderline-only reading — chosen because it is unambiguous and
risk-averse, matching the paper's stated philosophy (a dangerous property
should never be averaged or interpreted away).

## Alternatives considered

1. **Keep the 1-3 scale and the boolean `use_autonomy_level`.** Rejected:
   unfaithful to the published spec — the paper's rule distinguishes L5 from
   L3/L4, which a 3-point scale cannot express.
2. **Literal borderline-only lift** (L3/L4 lifts only entries "borderline"
   between low and medium). Rejected: ambiguous — the paper does not define
   the borderline, so any threshold would be an invented judgement; the
   conservative always-lift reading is unambiguous and never less strict.
3. **Hardcode the paper's rule for every profile.** Rejected: the per-type
   tool profiles are faithful records of the spreadsheets, which do not use
   the autonomy level; forcing the rule onto them would erase the divergence
   ADR-0012 deliberately keeps visible as data.

## Why

* The paper is now the authoritative published source (ADR-0012 addendum);
  the recommended default should implement its rule exactly, not a subset.
* Expressing the rule as per-profile data keeps the ADR-0012 principle:
  which behaviour applies is an inspectable, reviewable configuration choice,
  never an implicit consequence of code.
* Distinct `autonomy_level_driven` / `autonomy_level_lifted` flags keep the
  derivation honest: a reader can always tell whether dimensions or the
  autonomy rule set the tier, and the web view and policy gate say so.
