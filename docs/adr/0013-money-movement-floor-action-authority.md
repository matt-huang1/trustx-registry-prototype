# 0013 — Money-movement floor re-mapped to Action Authority = 3

## Decision

The deterministic money-movement rule (`classifier/rules.py`) now forces
**Action Authority = 3 ("Execute transactions")** whenever an agent
description contains money-movement language (initiate payment / transfer
funds / ACH). Under the placeholder schema it forced
`delegated_authority >= 4` on a 1–5 scale; under the ARC model, moving money
*is* executing transactions, so the floor maps to the Action Authority
dimension at its highest tier.

The rule remains an independent deterministic floor: it overrides the LLM's
proposed score (never lowers it), appends a `deterministic-rule:` marker to
the dimension's evidence, and records the override in the challenge notes.
Because `action_authority` is in the `tier_dimensions` of **every** committed
tier-weighting profile (see ADR-0012), worst-case-wins guarantees the floor
alone yields Tier 3 (high) regardless of which system type the model proposes
— `tests/test_deterministic_rule.py` asserts this across profiles.

## Context

The core principle: the model proposes; deterministic checks decide wherever a
fact can be pinned down. "This description says the agent can move money" is
such a fact. The re-mapping had to preserve the rule's guarantee (money
movement ⇒ highest tier) across the schema swap, and the ARC model gives it a
crisper home: Action Authority's Tier 3 label is literally "Execute
transactions".

## Alternatives considered

1. **Floor multiple dimensions** (e.g. also reversibility and
   data_egress_paths to 3). Rejected: those are usually true of money movers
   but are not *entailed* by the description the way execute-transactions is;
   they stay the scorer's judgement, challengeable with evidence.
2. **Drop the floor and trust the 12-dimension prompts.** Rejected: the floor
   exists precisely because the model must never get the last word on a
   pinnable fact.
3. **Map to Action Authority = 3 (chosen).** Same detector
   (`mentions_money_movement`) still shared with the runtime policy gate's
   dual-approval override, so the score floor and the gate can never disagree
   about what counts as moving money.

## Why

One fact, one rule, one dimension: the ARC taxonomy names the exact capability
the rule detects, so the mapping is now definitional rather than heuristic —
easier to defend, easier to challenge, and still guaranteed to escalate at
runtime (the payments archetype and the vendor-payment cached example both
demonstrate the full chain: floor → Tier 3 → escalate + dual approval).
