# ADR-0001: Risk-proportionate maker/checker with deterministic override

- Status: Accepted
- Date: 2026-07-08

## Decision
Classify agents with a bounded **maker/checker** loop: an LLM *proposer* drafts scores
with rationale and evidence; an LLM *challenger* red-teams the draft and can send it back
to the proposer **once** (max 2 proposer iterations); **deterministic rules override the
LLM wherever a fact can be pinned down**; and an accountable human ratifies the result,
with the depth of that human review scaled to the risk tier. An LLM never silently
finalises a score.

## Context
The registry's value depends on entries being *defensible*, not self-asserted. LLMs are
useful for reading a messy description and drafting a structured score, but they
hallucinate, can be prompt-injected via the description, and cannot be held accountable.
Some facts (e.g. "this agent moves money") are checkable and should not be left to a
model's judgement. Review effort should also be proportionate — trivial low-risk agents
should not cost the same human attention as high-risk ones.

## Alternatives considered
- **Fully manual classification.** Most defensible per entry, but does not scale and
  throws away the LLM's genuine drafting value; reviewers face a blank page every time.
- **Full LLM autonomy (model finalises the score).** Fast and scalable, but produces
  self-asserted, non-defensible scores; no accountability; silent failure under prompt
  injection or hallucination. Directly violates the core principle.
- **LLM-as-judge deciding (a second model ratifies the first).** Removes the human owner
  and still cannot pin down checkable facts deterministically; two models can share the
  same blind spot, and neither can be held accountable.

## Why chosen
The hybrid keeps each component doing what it is best at: the LLM drafts and critiques,
deterministic rules decide the checkable facts, and a human owns the residual judgement.
Bounding the loop (2 iterations) keeps cost/latency predictable and prevents two models
from arguing indefinitely. Scaling human scrutiny to risk tier makes the process
economical without lowering the bar where it matters. The deterministic money-movement
override in `classifier/rules.py` is the concrete demonstration of the principle.
