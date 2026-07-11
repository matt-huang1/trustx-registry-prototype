# trustx-registry-prototype

A prototype **open-source registry that classifies AI agents by risk** — with entries you can
*check*, not just labels you're asked to trust.

> **Independent working prototype — not an official RAI registry.** "trustx" is a working name
> only. Entries are scored against the ARC 12-dimension model adopted from RAI's published
> reference material, but this project is not endorsed by or affiliated with RAI.

## What this is

Most "AI risk" labels are self-asserted: a vendor declares a score and you take it on faith.
This registry does the opposite. Each agent is scored against the **ARC 12-dimension model**
(four groups, each dimension tiered 1–3), and **every score carries the evidence behind it**.
A model *proposes* scores, deterministic checks *decide* wherever a fact can be pinned down,
and an accountable human *ratifies* the rest — with the depth of scrutiny scaled to the risk.

**The thesis, in two sentences:** A classification is defensible because every one of its 12
dimension scores cites the evidence that backs it, and the overall risk tier is *computed*
from those scores by an inspectable rollup — not declared. Trust in an entry is a separate,
earned, revocable axis: it starts at community-submitted and is promoted only by a named human
reviewer, never by an anonymous vote.

## Live demo

`web/index.html` is a single, zero-build page — open it by double-click (`file://`), from a
static server, or on GitHub Pages. It renders the registry, an interactive classifier hero,
and a runtime policy gate with no network call (data is injected as JS globals; see
[ADR-0004](docs/adr/0004-single-file-web-demo.md)).

```bash
python scripts/build_registry.py     # compile entries/ → web/data/*.js (offline; no key)
open web/index.html                  # or serve the web/ directory
```

Each entry shows two independent marks: a **risk tier** (how risky the agent is — square mark)
and a **trust level** (how reviewed the entry is — rounded pill). They are different axes and
are shown distinctly.

## Quickstart

```bash
pip install -e ".[dev]"           # install (Python 3.11+)
python -m pytest -q               # offline test suite (no API calls)
python -m classifier.run "An agent that reads invoices and initiates ACH payments"
```

Configure LLM access purely via environment variables (see
[classifier/provider.py](classifier/provider.py)):

```bash
export LLM_BASE_URL="https://api.openai.com/v1"
export LLM_API_KEY="sk-..."
export LLM_MODEL="gpt-4o-mini"
```

## How to contribute

The registry is meant to be built by a community, and the repo *demonstrates* that model
rather than just describing it. A stranger can go from zero to an open PR by:

1. Drafting an entry from a plain-text description with the classifier CLI.
2. Evidencing each of the 12 dimensions.
3. Running the local checks (`python scripts/build_registry.py --check` and `pytest`).
4. Opening a PR — where CI re-runs those same checks.

New entries enter at **`community-submitted`**; promotion to `working-group-reviewed` or
`verified` requires a named human reviewer (the build fails otherwise). Full walkthrough:
**[CONTRIBUTING.md](CONTRIBUTING.md)**. Starter tasks: **[docs/GOOD_FIRST_ISSUES.md](docs/GOOD_FIRST_ISSUES.md)**.
To contest a score, open an evidence-backed challenge (evidence is required, by design).

## Governance

Who maintains the registry, who may ratify an entry (identified maintainers only — trust is
**not** a floodable vote), how challenges are adjudicated into new *versions* of an entry, and
how entries expire and must be re-ratified: **[docs/GOVERNANCE.md](docs/GOVERNANCE.md)** and
[ADR-0016](docs/adr/0016-contribution-model-trust-tiers.md).

## Layout

| Path | Purpose |
|------|---------|
| `schema/`     | JSON Schema for a registry entry + verbatim ARC dimension metadata and standards matrix |
| `policy/`     | Org delegation policy for the runtime gate + per-type tier-weighting profiles |
| `classifier/` | LangGraph maker/checker classification loop + CLI |
| `entries/`    | Ratified registry entries, one YAML file per agent |
| `examples/`   | Plain-text agent descriptions for the demo's cached classifier examples |
| `scripts/`    | `build_registry.py` (compile + validate entries + examples) and `serve_classify.py` |
| `docs/`       | Architecture, contribution model, governance, roadmap, ADRs |
| `web/`        | Single-file reference view + interactive classifier hero (zero-build, offline-capable) |

## Licences

This project is deliberately split across **two** licences:

- **Code — MIT** ([LICENSE](LICENSE)): the classifier, schema, rules, scripts, and web view.
- **Registry content — CC BY 4.0** ([LICENSE-DATA](LICENSE-DATA)): the entries in `entries/`
  and the registry artifacts generated from them.

**Why the split:** the code is permissively reusable, but the *classifications* are the point —
they should be reusable **with attribution**, so that provenance travels with the classification.
If someone republishes an entry, CC BY 4.0 keeps the credit (and the evidence trail) attached.

## Documentation

- [docs/PLAN.md](docs/PLAN.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md) · [docs/GOVERNANCE.md](docs/GOVERNANCE.md) · [docs/GOOD_FIRST_ISSUES.md](docs/GOOD_FIRST_ISSUES.md)
- [docs/OPEN_SOURCE_MODEL.md](docs/OPEN_SOURCE_MODEL.md)
- [docs/ROADMAP.md](docs/ROADMAP.md)
- [docs/DESIGN_DECISIONS.md](docs/DESIGN_DECISIONS.md)
