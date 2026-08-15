# Good first issues

Concrete, genuinely useful starter tasks. Each is well-scoped, needs no deep context, and
maps to the contribution flow in [CONTRIBUTING.md](../CONTRIBUTING.md). Maintainers track
these on the issue tracker under the **`good first issue`** label; that label is a promise
that the task is bounded and a maintainer will help you land it.

Pick one, comment on (or open) the tracking issue to claim it, then follow the standard flow:
draft → evidence per dimension → `python scripts/build_registry.py --check` + `pytest` →
open a PR. New entries enter at `community-submitted`.

---

### 1. Add a reference entry for a customer-service triage agent

There's no `knowledge_assistant` / `tool_using_agent` archetype for the very common "reads
inbound tickets, classifies intent, drafts a reply for a human to approve" pattern. Draft one
with the classifier CLI, evidence each of the 12 dimensions from the description, and submit
it. Good for learning the whole pipeline on a low-risk, easy-to-reason-about agent.

- **Files:** new `entries/customer-service-triage-agent.yaml`
- **Why it's useful:** fills a gap in the archetype coverage most readers will look for first.

### 2. Add a reference entry for a code-generation / PR-authoring agent

We have no `code_content_generator` archetype. Classify an agent that opens pull requests
against a repository (writes code, but a human merges). This exercises a different
tier-weighting profile and the `reversibility` / `system_reach` dimensions in an interesting
way.

- **Files:** new `entries/code-authoring-agent.yaml`
- **Why it's useful:** covers a system type with no example, and stress-tests a non-payments profile.

### 3. Add a standards mapping for an under-covered framework

The per-dimension standards matrix ([schema/standards_matrix.json](../schema/standards_matrix.json))
maps dimensions to NIST AI RMF, ISO, the EU AI Act, OWASP, MITRE ATLAS, and SR 11-7. Find a
dimension whose mapping for one framework is thin or missing and add the correct control
reference, with a source. Small, high-leverage, and teaches the schema.

- **Files:** [schema/standards_matrix.json](../schema/standards_matrix.json)
- **Why it's useful:** better standards coverage makes every entry more defensible at once.

### 4. Improve a rationale or add evidence on an existing entry

Read an existing entry (e.g. [entries/kyc-onboarding-triage-agent.yaml](../entries/kyc-onboarding-triage-agent.yaml))
and find a dimension whose one-line `rationale` is terse or whose `evidence` could quote the
description more precisely. Tighten it. This is the gentlest possible first PR and it directly
raises entry quality.

- **Files:** one file in [entries/](../entries/)
- **Why it's useful:** the registry's whole value is rationale + evidence quality.

### 5. File (and evidence) a challenge to an existing score

Disagree with a score? Practise the challenge path: open a challenge issue naming the entry,
the dimension, and evidence that contradicts the current score. Even a *rejected* challenge,
with its reasoning recorded, strengthens the entry's evidence trail.

- **Files:** none (an issue via the [challenge template](../.github/ISSUE_TEMPLATE/challenge-entry.yml))
- **Why it's useful:** exercises the adjudication + versioning mechanism the registry depends on.

---

Not sure which to pick, or want to propose your own? Open a
[Question / discussion issue](https://github.com/matt-huang1/trustx-registry-prototype/issues/new/choose)
and a maintainer will help you scope it.
