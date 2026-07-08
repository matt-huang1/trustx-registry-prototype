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
from .schema import DIMENSIONS, roll_up_risk_tier

MAX_PROPOSER_ITERATIONS = 2

# Short guidance shown to the model for each placeholder dimension.
_DIMENSION_GUIDANCE = {
    "autonomy": "How independently the agent acts without human confirmation per step.",
    "delegated_authority": "The real-world authority/permissions delegated to the agent "
    "(spend money, sign, change records).",
    "tool_access": "Breadth and power of tools/APIs the agent can invoke.",
    "data_exposure": "Sensitivity and volume of data the agent can read or exfiltrate.",
}


class ClassifierState(TypedDict, total=False):
    description: str
    proposal: dict  # {dimension: {score, rationale, evidence}}
    llm_draft: dict  # first raw LLM draft, kept for the audit trail
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
) -> tuple[dict, dict, list[str]]:
    """Draft a proposal with the LLM, then apply deterministic overrides.

    Returns ``(proposal, llm_draft, deterministic_notes)`` where ``llm_draft`` is the
    model's raw scores before any deterministic rule fired.
    """
    dims_doc = "\n".join(f"- {d}: {_DIMENSION_GUIDANCE[d]}" for d in DIMENSIONS)
    system = (
        "You classify AI agents by risk. For EACH dimension, output an integer score "
        "1 (lowest risk) to 5 (highest), a one-line rationale, and an evidence array "
        "quoting or pointing to the part of the description that justifies it. Only use "
        "what the description supports; do not invent capabilities. Respond with STRICT "
        'JSON: {"<dimension>": {"score": int, "rationale": str, '
        '"evidence": [str]}} and nothing else.'
    )
    feedback = ""
    if challenge_notes:
        feedback = (
            "\n\nA reviewer challenged your previous draft. Address these and re-score:\n"
            + "\n".join(f"- {n}" for n in challenge_notes)
        )
    user = f"Dimensions:\n{dims_doc}\n\nAgent description:\n{description}{feedback}"

    raw = provider.complete(system, user)
    llm_draft = _extract_json(raw)

    # Normalise: ensure every dimension is present with a sane shape.
    normalised: dict = {}
    for dim in DIMENSIONS:
        payload = llm_draft.get(dim, {}) or {}
        normalised[dim] = {
            "score": int(payload.get("score", 1)),
            "rationale": str(payload.get("rationale", "")),
            "evidence": list(payload.get("evidence", []) or []),
        }

    result = apply_deterministic_rules(description, normalised)
    return result.proposal, normalised, result.notes


def challenge(
    description: str, proposal: dict, provider: LLMProvider
) -> tuple[bool, list[str]]:
    """Red-team a proposal; return ``(flagged, notes)``."""
    system = (
        "You are a skeptical reviewer. Given an agent description and a proposed risk "
        "scoring, flag ANY dimension whose score is not supported by the description "
        "(too high or too low). Respond with STRICT JSON: "
        '{"flagged": bool, "notes": [str]} and nothing else. If everything is well '
        "supported, return flagged=false with an empty notes array."
    )
    user = (
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
    for dim in DIMENSIONS:
        d = state["proposal"][dim]
        print(f"\n  {dim}: {d['score']}/5")
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
                    proposal[dim]["score"] = max(1, min(5, int(raw)))
                    proposal[dim]["evidence"].append(
                        "human-edit: score adjusted by operator"
                    )
            who = input("Approver name/id: ").strip() or "unknown"
            return {
                "decision": "edit",
                "approved_by": who,
                "proposal": proposal,
                "risk_tier": roll_up_risk_tier(proposal),
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
        proposal, llm_draft, det_notes = propose(
            state["description"], provider, state.get("challenge_notes")
        )
        update: dict = {
            "proposal": proposal,
            "deterministic_notes": det_notes,
            "risk_tier": roll_up_risk_tier(proposal),
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
