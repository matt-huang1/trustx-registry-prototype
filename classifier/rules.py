"""Deterministic checks — the "checker" half of maker/checker.

The core principle of this registry is that an entry's score must be *defensible*,
not self-asserted. Wherever a fact can be pinned down deterministically, a rule here
decides it and OVERRIDES the LLM — the model never gets the last word on something we
can verify from the description itself.

This module currently implements one demonstrative rule (money movement). Add more as
the taxonomy firms up; each rule is a pure function of (description, proposal) so it is
trivially testable with no LLM.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import MutableMapping

# Capabilities that, if present in the description, imply the agent can move money —
# in ARC terms it can "Execute transactions" — regardless of how the LLM scored it.
MONEY_MOVEMENT_PATTERNS: tuple[str, ...] = (
    r"initiate\s+payment",
    r"transfer\s+funds",
    r"\bACH\b",
)

# Moving money IS executing transactions: Action Authority tier 3 by definition
# ("Execute transactions"). Under worst-case-wins this alone yields Tier 3 (high)
# for every committed tier-weighting profile, since action_authority is in all of
# them. See docs/adr/0013-*.md.
MONEY_MOVEMENT_DIMENSION = "action_authority"
MONEY_MOVEMENT_FLOOR = 3  # action_authority must be at least this if money moves.


@dataclass(frozen=True)
class RuleResult:
    """Outcome of applying deterministic rules to a proposal."""

    proposal: dict  # possibly-mutated copy of the proposal
    notes: list[str]  # human-readable notes for each override that fired
    fired: bool  # True if any deterministic rule changed or flagged the proposal


def mentions_money_movement(description: str) -> bool:
    """Does ``description`` trip the money-movement rule?

    The single detector for money-movement capability, shared by the classifier's
    deterministic override (below) and the runtime policy gate
    (:mod:`classifier.policy_gate`). Keeping one function means the score floor and the
    gate's dual-approval override can never disagree about what counts as moving money.
    """
    return any(
        re.search(pattern, description, flags=re.IGNORECASE)
        for pattern in MONEY_MOVEMENT_PATTERNS
    )


# Back-compat private alias; prefer the public :func:`mentions_money_movement`.
_mentions_money_movement = mentions_money_movement


def apply_deterministic_rules(description: str, proposal: MutableMapping) -> RuleResult:
    """Apply every deterministic rule to ``proposal`` for the given ``description``.

    Returns a :class:`RuleResult` with a *copy* of the proposal (never mutates the
    input), the notes describing what fired, and whether anything fired. The proposal
    shape is ``{dimension: {"score": int, "rationale": str, "evidence": [str, ...]}}``.
    """
    # Deep-ish copy so callers keep the original LLM draft for the audit trail.
    updated = {
        dim: {
            "score": int(payload["score"]),
            "rationale": payload.get("rationale", ""),
            "evidence": list(payload.get("evidence", [])),
        }
        for dim, payload in proposal.items()
    }
    notes: list[str] = []

    # RULE: money-movement capability forces action_authority >= MONEY_MOVEMENT_FLOOR
    # (= 3, "Execute transactions") — worst-case-wins then yields Tier 3 (high).
    if _mentions_money_movement(description):
        aa = updated.get(MONEY_MOVEMENT_DIMENSION)
        if aa is not None:
            llm_score = aa["score"]
            if llm_score < MONEY_MOVEMENT_FLOOR:
                aa["score"] = MONEY_MOVEMENT_FLOOR
                aa["evidence"].append(
                    "deterministic-rule: money-movement capability detected in description"
                )
                notes.append(
                    "Deterministic override: description implies money movement "
                    f"(initiate payment / transfer funds / ACH), which is executing "
                    f"transactions; the LLM scored action_authority={llm_score} but it "
                    f'was forced to {MONEY_MOVEMENT_FLOOR} ("Execute transactions"). '
                    f"Under worst-case-wins this yields Tier 3 (high)."
                )

    return RuleResult(proposal=updated, notes=notes, fired=bool(notes))
