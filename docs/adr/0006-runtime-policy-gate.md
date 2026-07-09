# ADR-0006: Runtime policy gate — deterministic tier-to-action enforcement over committed registry data

- Status: Accepted
- Date: 2026-07-09

## Decision
Add a **runtime policy gate**: the point at which the registry stops being a catalogue and
becomes something an orchestrator consults *at the moment an agent tries to act*. Given a
committed registry entry (its evidence-backed risk tier) and a stated org policy, the gate
returns a decision — **allow / allow_with_logging / escalate_to_human** — plus capability
overrides. The gate is a **pure, deterministic function** with no network and no LLM:

- **`policy/example-bank-policy.yaml`** — a readable, configurable org policy: a name and a
  `tier_actions` map (`low → allow`, `medium → allow_with_logging`, `high → escalate_to_human`),
  plus a `capability_overrides` map (`money_movement → require_dual_approval`) applied *on top
  of* the tier rule when an entry trips the money-movement rule.
- **`classifier/policy_gate.py`** — `decide(entry, policy) -> {action, reason, tier,
  policy_rule, evidence_refs, overrides, slug}`. The `reason` is human-readable and names WHY:
  the tier rule applied and the actual evidence quotes that drove the tier (the peak-scoring
  dimension's evidence). Money-movement detection reuses the *same*
  `classifier.rules.mentions_money_movement` the deterministic score floor uses, so the floor
  and the gate can never disagree about what counts as moving money.
- **`scripts/build_registry.py`** runs the gate over every entry and over a scripted scenario,
  emitting `web/data/policy.json` (canonical bundle) and `web/data/policy.js`
  (`window.__POLICY__` / `window.__GATE_DECISIONS__` / `window.__SCENARIO__`). This is offline
  and deterministic; `--check` fails if either artifact is stale, exactly like the registry and
  examples artifacts (ADR-0004, ADR-0005).
- **`web/index.html`** gains a *Policy Gate* section (with a light Registry / Classify / Policy
  Gate in-page nav) that only *displays* pre-computed decisions: a scenario player that steps
  an invoice-payment workflow (read invoice → look up vendor → initiate payment) and halts
  visibly on the escalate step, and a "check any agent against the policy" picker. The browser
  does no deciding — it looks decisions up by slug.

**Production note:** in production this same `decide` function is exposed as an **MCP/A2A
endpoint** that any agent queries at runtime before it acts; the committed `policy.json` here
is the offline, display-time projection of that endpoint's answers. (Also noted in ROADMAP M6.)

## Context
The registry's whole thesis is that a risk tier is a *defensible, evidence-backed* fact, not a
self-asserted label. That fact is only worth something if something *enforces* it when an agent
tries to act. Enforcement has one hard requirement: it must be deterministic, reproducible, and
auditable. A gate that let a model decide, at runtime, whether money may move would reintroduce
exactly the non-determinism the registry exists to remove — and would violate the core
principle (the model proposes; deterministic checks decide where a fact can be pinned down; a
human owns the rest, scaled to risk). The demo must also stay single-file, zero-build, and
offline (ADR-0004): no server or key at view time.

## Alternatives considered
- **LLM-driven gate** (ask a model "should this be allowed?" at enforcement time). *Rejected:*
  non-deterministic enforcement — the same agent could be allowed one minute and blocked the
  next, with no auditable rule. Enforcement is precisely where the model must not have the last
  word.
- **Hardcoded allow/deny blocks** in the page or classifier. *Rejected:* not configurable and
  not auditable — an org cannot read, review, or change its own policy, and there is no stated
  rule to point to when a decision is challenged. The policy must be data an accountable owner
  edits.
- **A live MCP/A2A server** the browser queries at runtime. *The right production answer* — the
  gate genuinely is a runtime service — but it is infrastructure this prototype does not have,
  and it breaks the offline/Pages story. *Deferred to production;* `decide` already has the
  exact shape such an endpoint would serve, and `policy.json` is its offline projection.

## Why chosen
Computing every decision offline over committed data gives a bulletproof, reproducible demo:
open `web/index.html` from `file://` with no network and no key, and the scenario runs end to
end — safe steps pass, the money-movement step halts and escalates with an evidence-linked
reason that names the tier and quotes the driving evidence. It enforces a **stated, configurable
policy** (visible as a tier→action table in the UI), not a hardcoded verdict, so a decision can
always be traced to a rule an owner can read and change. It reuses the existing schema, rollup,
and money-movement detector — no scoring logic is duplicated — and keeps determinism, the
audit trail, and the human gate front and centre, matching the core principle. The client-side
contract (`window.__GATE_DECISIONS__`) is already the shape a production MCP/A2A endpoint would
satisfy, so the prototype and the production design are the same design.
