"""The maker/checker classification loop, as a LangGraph state machine.

Flow (bounded to MAX_PROPOSER_ITERATIONS proposer passes):

    START -> proposer -> challenger --(flagged & under budget)--> proposer
                              |
                              +----(clean or budget spent)------> human_gate -> END

- proposer   (maker):   an LLM drafts a score + one-line rationale + evidence pointer
                        per dimension, then DETERMINISTIC rules override it where a fact
                        can be pinned down (classifier/rules.py).
- challenger (checker):  a second LLM pass red-teams the draft and flags any score not
                        supported by the description. A flag loops back to the proposer
                        ONCE.
- human_gate (owner):   an accountable human approves / edits / rejects and is recorded
                        into provenance. The LLM never finalises a score on its own.
"""

from __future__ import annotations

import json
from typing import Callable, TypedDict

from langgraph.graph import END, START, StateGraph

from .provider import LLMProvider
from .rules import apply_deterministic_rules
from .schema import (
    DIMENSIONS,
    SYSTEM_TYPES,
    load_dimension_meta,
    roll_up_risk_tier,
)

MAX_PROPOSER_ITERATIONS = 2


def _dimensions_doc() -> str:
    """One line per ARC dimension, using the verbatim names, groups, and tier labels."""
    meta = load_dimension_meta()
    group_names = dict(meta["groups"])
    lines = []
    for dim in meta["dimensions"]:
        tiers = dim["tiers"]
        lines.append(
            f"- {dim['id']} — {dim['name']} ({group_names[dim['group']]}): "
            f"1 = {tiers['1']}; 2 = {tiers['2']}; 3 = {tiers['3']}."
        )
    return "\n".join(lines)


def _system_types_doc() -> str:
    meta = load_dimension_meta()
    return "\n".join(f"- {k}: {v}" for k, v in meta["system_types"].items())


def _autonomy_levels_doc() -> str:
    meta = load_dimension_meta()
    return "\n".join(f"- {k}: {v}" for k, v in meta["autonomy_level_defs"].items())


class ClassifierState(TypedDict, total=False):
    description: str
    proposal: dict  # {dimension: {score, rationale, evidence}}
    llm_draft: dict  # first raw LLM draft, kept for the audit trail
    system_type: str | None  # ARC system type proposed by the model (or None)
    autonomy_level: int | None  # ARC autonomy level 1-3 proposed by the model
    deterministic_notes: list[str]
    challenge_flagged: bool
    challenge_notes: list[str]
    iterations: int  # number of proposer passes that have run
    risk_tier: str
    decision: str  # "approve" | "edit" | "reject"
    approved_by: str | None


# --------------------------------------------------------------------------- #
# JSON helpers
# --------------------------------------------------------------------------- #
def _extract_json(text: str) -> dict:
    """Best-effort JSON extraction from an LLM response (tolerates code fences)."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[len("json") :]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in model output: {text!r}")
    return json.loads(text[start : end + 1])


# --------------------------------------------------------------------------- #
# Maker / checker core (pure-ish functions, provider injected — directly testable)
# --------------------------------------------------------------------------- #
def propose(
    description: str,
    provider: LLMProvider,
    challenge_notes: list[str] | None = None,
) -> tuple[dict, dict, list[str], str | None, int | None]:
    """Draft a proposal with the LLM, then apply deterministic overrides.

    Returns ``(proposal, llm_draft, deterministic_notes, system_type,
    autonomy_level)`` where ``llm_draft`` is the model's raw scores before any
    deterministic rule fired. ALL 12 ARC dimensions are always scored; which of
    them drive the tier is the rollup's concern (classifier/schema.py), never
    the model's.
    """
    system = (
        "You classify AI agents against the ARC 12-dimension risk model. For EACH of "
        "the 12 dimensions, output an integer tier score 1 (Tier 1 Low), 2 (Tier 2 "
        "Medium), or 3 (Tier 3 High) using the per-dimension tier definitions given, a "
        "one-line rationale, and an evidence array quoting or pointing to the part of "
        "the description that justifies it. Score ALL 12 dimensions — never skip one. "
        "Also classify the system_type (one of the listed ids, or null if none fits) "
        "and the autonomy_level (1, 2, or 3 per the definitions given). Only use what "
        "the description supports; do not invent capabilities. Respond with STRICT "
        'JSON: {"dimensions": {"<dimension_id>": {"score": int, "rationale": str, '
        '"evidence": [str]}}, "system_type": str | null, "autonomy_level": int} '
        "and nothing else."
    )
    feedback = ""
    if challenge_notes:
        feedback = (
            "\n\nA reviewer challenged your previous draft. Address these and re-score:\n"
            + "\n".join(f"- {n}" for n in challenge_notes)
        )
    user = (
        f"Dimensions (id — name (group): tier definitions):\n{_dimensions_doc()}\n\n"
        f"System types:\n{_system_types_doc()}\n\n"
        f"Autonomy levels:\n{_autonomy_levels_doc()}\n\n"
        f"Agent description:\n{description}{feedback}"
    )

    raw = provider.complete(system, user)
    llm_draft = _extract_json(raw)

    # Tolerate both the nested shape requested above and a flat {dim: {...}} map.
    dims_payload = llm_draft.get("dimensions") or {
        k: v for k, v in llm_draft.items() if k in DIMENSIONS
    }

    # Normalise: ensure every dimension is present with a sane shape, scores in 1..3.
    normalised: dict = {}
    for dim in DIMENSIONS:
        payload = dims_payload.get(dim, {}) or {}
        normalised[dim] = {
            "score": max(1, min(3, int(payload.get("score", 1)))),
            "rationale": str(payload.get("rationale", "")),
            "evidence": list(payload.get("evidence", []) or []),
        }

    system_type = llm_draft.get("system_type")
    system_type = str(system_type) if system_type in SYSTEM_TYPES else None
    autonomy_level_raw = llm_draft.get("autonomy_level")
    try:
        autonomy_level: int | None = max(1, min(3, int(autonomy_level_raw)))
    except (TypeError, ValueError):
        autonomy_level = None

    result = apply_deterministic_rules(description, normalised)
    return result.proposal, normalised, result.notes, system_type, autonomy_level


def challenge(
    description: str, proposal: dict, provider: LLMProvider
) -> tuple[bool, list[str]]:
    """Red-team a proposal; return ``(flagged, notes)``."""
    system = (
        "You are a skeptical reviewer. Given an agent description and a proposed "
        "scoring against the ARC 12-dimension risk model (each dimension tiered 1/2/3 "
        "per the definitions given), flag ANY dimension whose score is not supported "
        "by the description (too high or too low). Respond with STRICT JSON: "
        '{"flagged": bool, "notes": [str]} and nothing else. If everything is well '
        "supported, return flagged=false with an empty notes array."
    )
    user = (
        f"Dimensions (id — name (group): tier definitions):\n{_dimensions_doc()}\n\n"
        f"Agent description:\n{description}\n\nProposed scoring:\n"
        f"{json.dumps(proposal, indent=2)}"
    )
    raw = provider.complete(system, user)
    parsed = _extract_json(raw)
    flagged = bool(parsed.get("flagged", False))
    notes = [str(n) for n in parsed.get("notes", []) or []]
    return flagged, notes


# --------------------------------------------------------------------------- #
# CLI human gate (default implementation; injectable for tests / automation)
# --------------------------------------------------------------------------- #
def cli_human_gate(state: ClassifierState) -> dict:
    """Print the proposal + challenge, then ask the operator to approve/edit/reject.

    Returns a state update with ``decision``, ``approved_by`` and a possibly-edited
    ``proposal``. This is the only interactive node; tests inject a non-interactive
    replacement.
    """
    print("\n" + "=" * 70)
    print("PROPOSED RISK SCORING")
    print("=" * 70)
    print(f"\n  system_type: {state.get('system_type') or '(none)'}")
    print(f"  autonomy_level: {state.get('autonomy_level') or '(none)'}")
    for dim in DIMENSIONS:
        d = state["proposal"][dim]
        print(f"\n  {dim}: {d['score']}/3")
        print(f"    rationale: {d['rationale']}")
        for ev in d["evidence"]:
            print(f"    evidence:  {ev}")
    print(f"\n  => rolled-up risk_tier: {state.get('risk_tier')}")

    print("\n" + "-" * 70)
    print("CHALLENGER (red-team) RESULT")
    print("-" * 70)
    if state.get("deterministic_notes"):
        for n in state["deterministic_notes"]:
            print(f"  [deterministic] {n}")
    if state.get("challenge_flagged"):
        for n in state.get("challenge_notes", []):
            print(f"  [llm-challenge] {n}")
    else:
        print("  LLM challenger raised no flags.")

    print("\n" + "-" * 70)
    while True:
        choice = input("Decision — [a]pprove / [e]dit / [r]eject: ").strip().lower()
        if choice in {"a", "approve"}:
            who = input("Approver name/id: ").strip() or "unknown"
            return {"decision": "approve", "approved_by": who}
        if choice in {"e", "edit"}:
            proposal = {k: dict(v) for k, v in state["proposal"].items()}
            for dim in DIMENSIONS:
                cur = proposal[dim]["score"]
                raw = input(f"  {dim} score [{cur}]: ").strip()
                if raw:
                    proposal[dim]["score"] = max(1, min(3, int(raw)))
                    proposal[dim]["evidence"].append(
                        "human-edit: score adjusted by operator"
                    )
            who = input("Approver name/id: ").strip() or "unknown"
            return {
                "decision": "edit",
                "approved_by": who,
                "proposal": proposal,
                "risk_tier": roll_up_risk_tier(
                    proposal, state.get("system_type"), state.get("autonomy_level")
                ),
            }
        if choice in {"r", "reject"}:
            who = input("Rejector name/id: ").strip() or "unknown"
            return {"decision": "reject", "approved_by": who}
        print("  Please enter a, e, or r.")


# --------------------------------------------------------------------------- #
# Graph assembly
# --------------------------------------------------------------------------- #
def build_graph(
    provider: LLMProvider,
    human_gate: Callable[[ClassifierState], dict] = cli_human_gate,
):
    """Compile the maker/checker graph with an injected provider and human gate."""

    def proposer_node(state: ClassifierState) -> dict:
        proposal, llm_draft, det_notes, system_type, autonomy_level = propose(
            state["description"], provider, state.get("challenge_notes")
        )
        update: dict = {
            "proposal": proposal,
            "deterministic_notes": det_notes,
            "system_type": system_type,
            "autonomy_level": autonomy_level,
            "risk_tier": roll_up_risk_tier(proposal, system_type, autonomy_level),
            "iterations": state.get("iterations", 0) + 1,
        }
        if "llm_draft" not in state:  # keep the very first raw draft for provenance
            update["llm_draft"] = llm_draft
        return update

    def challenger_node(state: ClassifierState) -> dict:
        flagged, notes = challenge(state["description"], state["proposal"], provider)
        return {"challenge_flagged": flagged, "challenge_notes": notes}

    def route_after_challenge(state: ClassifierState) -> str:
        if (
            state.get("challenge_flagged")
            and state["iterations"] < MAX_PROPOSER_ITERATIONS
        ):
            return "proposer"
        return "human_gate"

    def human_gate_node(state: ClassifierState) -> dict:
        return human_gate(state)

    graph = StateGraph(ClassifierState)
    graph.add_node("proposer", proposer_node)
    graph.add_node("challenger", challenger_node)
    graph.add_node("human_gate", human_gate_node)
    graph.add_edge(START, "proposer")
    graph.add_edge("proposer", "challenger")
    graph.add_conditional_edges(
        "challenger",
        route_after_challenge,
        {"proposer": "proposer", "human_gate": "human_gate"},
    )
    graph.add_edge("human_gate", END)
    return graph.compile()


def classify(
    description: str,
    provider: LLMProvider,
    human_gate: Callable[[ClassifierState], dict] = cli_human_gate,
) -> ClassifierState:
    """Run the full loop and return the final state."""
    app = build_graph(provider, human_gate)
    initial: ClassifierState = {"description": description, "iterations": 0}
    return app.invoke(initial)  # type: ignore[return-value]
