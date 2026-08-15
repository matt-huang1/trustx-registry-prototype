# Architecture

The registry turns a free-text agent description into a defensible, evidence-backed
risk entry through a bounded **maker/checker** loop: an LLM *proposer* drafts scores,
an LLM *challenger* red-teams them, **deterministic rules** override the LLM wherever a
fact can be pinned down, and a *human gate* ratifies the result before anything is
written to `entries/`. All LLM access is funnelled through a single OpenAI-compatible
provider so the model is swappable via environment variables only.

Each entry scores an agent on all 12 ARC dimensions and carries the rationale and quoted
evidence behind every score, so a classification can be inspected rather than taken on
faith. The overall risk tier is computed from those scores by a worst-case-wins rule — any
single dimension at the top of the scale carries the whole system — with *which* dimensions
drive the tier held as a per-system-type weighting profile in
`policy/tier_weighting_profiles.yaml` (data, not code) and recorded on every entry as
`tier_derivation`. The same committed data backs a runtime policy gate, which an
orchestrating agent consults before it acts: the gate checks an agent's tier against a
configurable organisational policy and escalates to a human where the policy demands it.

The full architecture is set out in [docs/PLAN.md](PLAN.md) §3.
