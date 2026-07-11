# Contributing

## What this registry is

This is an open-source registry that classifies AI agents by risk with **defensible,
evidence-backed entries** rather than self-asserted labels. Every entry scores an agent
against the ARC 12-dimension model, and each score must cite the evidence behind it. A
model *proposes* scores, deterministic checks *decide* wherever a fact can be pinned down,
and an accountable human *ratifies* the rest — so no label is ever just someone's say-so.

Working name only — this is an independent prototype, **not** an official RAI registry.

## The two axes an entry carries

Every entry has two independent marks; don't conflate them:

- **Risk tier** (`low` / `medium` / `high`) — how risky the *agent* is. Computed, not chosen.
- **Trust level** — how reviewed the *entry* is. Earned, labelled, and revocable:
  | Trust level | What it means |
  |-------------|---------------|
  | `community-submitted` | Passed every automated check, but no identified maintainer has reviewed it yet. **This is where your contribution enters.** |
  | `working-group-reviewed` | An identified maintainer / working-group member has reviewed the scoring and evidence and ratified it. |
  | `verified` | Reviewed **and** traceable to authoritative source material (e.g. adopted from a published reference registry). |

You cannot self-assign `working-group-reviewed` or `verified`: the build **fails** if an
entry claims either without a human reviewer recorded in `review.reviewed_by`. See
[docs/GOVERNANCE.md](docs/GOVERNANCE.md) and [ADR-0016](docs/adr/0016-contribution-model-trust-tiers.md).

## How to contribute an entry

### 1. Fork and set up

```bash
# Fork on GitHub, then:
git clone https://github.com/<you>/trustx-registry-prototype
cd trustx-registry-prototype
pip install -e ".[dev]"      # Python 3.11+
python -m pytest -q          # confirm a clean baseline (offline, no API key)
```

### 2. Draft your entry with the classifier

Don't hand-write YAML from scratch. Let the classifier generate a first draft from a
plain-text description of the agent, then refine it:

```bash
python -m classifier.run "A customer-service triage agent that reads inbound emails,
classifies them by intent, and drafts a reply for a human agent to approve. It has
read-only access to the ticketing system and cannot send anything itself."
```

This runs the maker/checker loop and, on approval, writes `entries/<slug>.yaml`. The draft
already has all 12 dimensions scored with rationales. (LLM access is configured purely via
environment variables — see [classifier/provider.py](classifier/provider.py); no key ever
lives in the repo.) If you don't have model access, copy an existing file in
[entries/](entries/) as a template and score by hand.

### 3. Fill in the evidence per dimension

For **each** of the 12 dimensions, the `evidence` array must point at what backs the score
— a direct quote from the agent's description, a link to documentation, or a doc reference.
An entry with an empty `evidence` list on any dimension **will fail the build**. This is the
whole point: a score you can't evidence is not a classification, it's an opinion.

Set your entry's `trust_level` to `community-submitted` and leave `review` null:

```yaml
trust_level: community-submitted
review:
  reviewed_by: null
  reviewed_at: null
  expires_at: null
```

### 4. Run the local checks BEFORE opening a PR

```bash
python scripts/build_registry.py --check    # schema + evidence + recomputed tier + trust rules
python -m pytest -q                          # full offline suite
black --check .                              # formatting (Python)
```

If `--check` complains that generated files are stale, run `python scripts/build_registry.py`
(no flag) to recompile `web/data/*` and commit the result alongside your entry.

### 5. Open the PR

Push your branch and open a pull request. The [PR template](.github/PULL_REQUEST_TEMPLATE.md)
has a checklist mirroring the automated checks — tick it honestly.

## What the automated checks do to your submission

Every PR that touches `entries/` is gated by CI. A failure means the entry is not yet
admissible — read the message, fix the entry, and push again.

| Check | What it verifies | What a failure means |
|-------|------------------|----------------------|
| **Schema** | The entry matches [schema/entry.schema.json](schema/entry.schema.json) | A field is missing, misnamed, or malformed. |
| **Evidence required** | Every one of the 12 dimensions cites evidence | A dimension has an empty `evidence` list. |
| **Standards mapping** | Dimensions map to the committed standards matrix | (Rendered from [schema/standards_matrix.json](schema/standards_matrix.json).) |
| **Deterministic floors** | Pinnable facts override the model — e.g. money-movement language forces Action Authority = 3 | Your score contradicts a deterministic rule; the rule wins ([ADR-0013](docs/adr/0013-money-movement-floor-action-authority.md)). |
| **Recomputed tier** | The stored `risk_tier` and `tier_derivation` equal what the rollup computes | You hand-edited a tier away from its scores. Fix the scores or the tier. |
| **Challenger (red-team)** | A challenger pass flags unsupported scores | Recorded on the entry's `challenge` block. |
| **Trust level** | `verified` / `working-group-reviewed` require a human reviewer | You claimed a trust level you can't have. New entries enter at `community-submitted`. |

## What happens after you open the PR

1. Your entry enters at **`community-submitted`** once the automated checks pass.
2. A maintainer reviews the scoring and the evidence — not whether they *like* the score,
   but whether each score is supported by what you cited.
3. On ratification, an identified maintainer records themselves in `review.reviewed_by` and
   the level is promoted to **`working-group-reviewed`**. Entries traceable to authoritative
   published source material may be promoted to **`verified`**.
4. Entries **expire** (`review.expires_at`) and must be re-ratified — a classification that
   was fresh two years ago is not evidence today.

## How to challenge an existing entry

Disagree with a score? **Open an issue with evidence** using the
[challenge template](.github/ISSUE_TEMPLATE/challenge-entry.yml): name the entry, the
dimension, and the specific evidence that contradicts the current score. A resolved
challenge produces a **new version** of the entry, not a silent in-place edit
([docs/GOVERNANCE.md](docs/GOVERNANCE.md)).

**Challenges without evidence are not actioned.** This is by design and is enforced by the
issue form (the evidence field is required). "I think this feels too low" is not a challenge;
"the linked docs show it initiates payments, so Action Authority should be 3" is.

## Good first issues

New here? See [docs/GOOD_FIRST_ISSUES.md](docs/GOOD_FIRST_ISSUES.md) for concrete, genuinely
useful starter tasks. Maintainers label these `good first issue` on the tracker — that label
means the task is well-scoped, needs no deep context, and a maintainer is on hand to help.

## Code of conduct & asking a question

Be respectful, assume good faith, and argue about evidence, not people. To ask a question,
open a [Question / discussion issue](.github/ISSUE_TEMPLATE/config.yml) or start a GitHub
Discussion — there are no bad questions about how to score a dimension.
