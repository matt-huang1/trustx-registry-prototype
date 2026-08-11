"""Runtime policy gate — the deterministic decision an orchestrator gets when an
agent tries to act.

The registry says *what an agent is* (its evidence-backed risk tier). An org policy
says *what may be delegated at what tier*. This module joins the two: given a committed
registry ``entry`` and a ``policy``, :func:`decide` returns the gate decision — allow,
log, or escalate — and names WHY: the reason states the driving dimensions at their
verbatim tier labels, and ``evidence_refs`` carries the quotes that back them (stated
once each, never both in the same sentence).

It is intentionally a **pure function with no network and no LLM**. The maker/checker
loop may use a model to *propose* an entry, but once an entry is committed the runtime
decision about whether to let an agent act must be deterministic, reproducible, and
auditable. The model never gets to decide, at runtime, whether money may move.

The money-movement capability override reuses the *same* detector the classifier's
deterministic score floor uses (:func:`classifier.rules.mentions_money_movement`), so the
score floor and the gate's dual-approval requirement can never disagree about what counts
as moving money.

In production this same function would sit behind an MCP/A2A endpoint any agent queries
at the moment it tries to act (see docs/adr/0006-*.md); here it is compiled offline over
the committed registry for display.
"""

from __future__ import annotations

from typing import Mapping

from classifier.rules import mentions_money_movement
from classifier.schema import load_dimension_meta

_TIER_ADJECTIVE = {"low": "Low-risk", "medium": "Medium-risk", "high": "High-risk"}

# Policy sentence for each tier action, so the reason reads like a stated policy being
# applied rather than a bare label. The reason never restates the tier or the action
# headline: the caller displaying a decision already labels both (tier marker + outcome),
# so the reason carries only the justification — the policy applied and the evidence.
_TIER_POLICY_SENTENCE = {
    "allow": "Policy permits low-risk delegations to proceed automatically.",
    "allow_with_logging": "Policy permits medium-risk delegations but logs them for audit.",
    "escalate_to_human": "Policy requires human approval for high-risk delegations.",
}


def _driving_evidence(entry: Mapping) -> tuple[list[str], list[str]]:
    """Return (driving dimension names, their evidence quotes).

    The entry's ``tier_derivation`` records which dimensions actually drove the
    tier under its tier-weighting profile (classifier.schema.derive_risk_tier),
    so citing their evidence is citing WHY the gate acted — deduped,
    order-preserved. An empty driver list on an entry WITH a derivation is
    meaningful (nothing rose above baseline, or autonomy level alone drove it)
    and is passed through as-is; only entries without a derivation at all fall
    back to the dimensions at the peak score.
    """
    dims = entry.get("dimensions") or {}
    if not dims:
        return [], []
    derivation = entry.get("tier_derivation")
    if derivation is not None:
        driving = list(derivation.get("driving_dimensions") or [])
    else:
        peak = max(int(d["score"]) for d in dims.values())
        driving = [name for name, d in dims.items() if int(d["score"]) == peak]
    evidence: list[str] = []
    for name in driving:
        if name not in dims:
            continue
        for quote in dims[name].get("evidence", []):
            if quote not in evidence:
                evidence.append(quote)
    return driving, evidence


def decide(entry: Mapping, policy: Mapping) -> dict:
    """Decide the runtime gate action for ``entry`` under ``policy``.

    Deterministic: no network, no LLM. Returns a dict with, at minimum, the keys
    ``action``, ``reason``, ``tier``, ``policy_rule`` and ``evidence_refs`` (plus
    ``slug`` and any capability ``overrides`` that fired). The ``reason`` is
    human-readable and carries the justification only — the policy sentence applied and
    the evidence that drove the tier. It deliberately does not restate the tier or the
    action: displays label those from the structured ``tier``/``action`` fields, and a
    reason that repeated them would show the tier twice everywhere it renders.
    """
    slug = (entry.get("agent") or {}).get("slug", "")
    tier = entry["risk_tier"]
    tier_actions = policy["tier_actions"]
    action = tier_actions[tier]

    driving, evidence_refs = _driving_evidence(entry)

    policy_sentence = _TIER_POLICY_SENTENCE.get(
        action, f"Policy maps this tier to '{action}'."
    )
    adjective = _TIER_ADJECTIVE.get(tier, f"{tier.capitalize()}-risk")
    derivation = entry.get("tier_derivation") or {}
    if driving:
        # The reason states the driving FACT once — the dimensions that set the
        # tier, at their verbatim tier labels. The evidence quotes live only in
        # evidence_refs, so a display showing both never says the same thing
        # twice (ADR-0018).
        dim_meta = {d["id"]: d for d in load_dimension_meta()["dimensions"]}
        dims = entry.get("dimensions") or {}
        parts = []
        for dim_id in driving:
            meta = dim_meta.get(dim_id)
            label = meta["name"] if meta else dim_id
            score = (dims.get(dim_id) or {}).get("score")
            tier_text = meta["tiers"].get(str(score)) if meta and score else None
            parts.append(f'{label} at "{tier_text}"' if tier_text else label)
        because = "driven by " + ", ".join(parts)
    elif derivation.get("autonomy_level_driven"):
        because = "autonomy level L5 alone forces Tier 3 under this weighting profile"
    elif derivation.get("autonomy_level_lifted"):
        because = (
            "autonomy level L3/L4 lifts the tier to at least Tier 2 under this "
            "weighting profile"
        )
    elif derivation and not derivation.get("driving_dimensions"):
        because = "no weighted dimension rises above baseline (all Tier 1)"
    else:
        because = "no dimension evidence recorded"
    reason = f"{policy_sentence} {adjective} because: {because}."

    # Capability overrides: applied ON TOP OF the tier rule. Money movement pins
    # Action Authority to 3, "Execute transactions" (classifier.rules) AND, per policy,
    # demands a second human — regardless of what the tier action alone would allow.
    overrides: list[dict] = []
    description = (entry.get("agent") or {}).get("description", "")
    override_action = (policy.get("capability_overrides") or {}).get("money_movement")
    if override_action and mentions_money_movement(description):
        overrides.append(
            {
                "capability": "money_movement",
                "action": override_action,
                "reason": (
                    "Money-movement capability detected: Action Authority is pinned to 3 "
                    '("Execute transactions") by the deterministic money-movement rule, '
                    "and policy requires dual human approval before any funds move."
                ),
            }
        )
        reason += (
            " Money-movement rule fired: Action Authority pinned to 3 "
            '("Execute transactions"); policy additionally requires dual human approval.'
        )

    return {
        "slug": slug,
        "tier": tier,
        "action": action,
        "policy_rule": f"{tier} → {action}",
        "reason": reason,
        "evidence_refs": evidence_refs,
        "overrides": overrides,
    }
