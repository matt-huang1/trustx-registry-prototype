# trustx-registry-prototype

A prototype **open-source registry that classifies AI agents by risk** with
defensible, evidence-backed entries rather than self-asserted labels. A model
*proposes* a score, deterministic checks *decide* wherever a fact can be pinned
down, and an accountable human *ratifies* the rest — with the depth of human
scrutiny scaled to the risk tier. Entries are scored against the **ARC
12-dimension model** (four groups, each dimension tiered 1–3): all 12
dimensions are always scored, and *which* of them drive the rolled-up tier is
an explicit per-system-type weighting profile
([`policy/tier_weighting_profiles.yaml`](policy/tier_weighting_profiles.yaml),
[ADR-0012](docs/adr/0012-arc-12-dimension-schema-and-tier-weighting-profiles.md)).
Working name only — this is **not** an official RAI artifact.

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

## Layout

| Path | Purpose |
|------|---------|
| `schema/`     | JSON Schema for a registry entry + verbatim ARC dimension metadata and standards matrix |
| `policy/`     | Org delegation policy for the runtime gate + per-type tier-weighting profiles |
| `classifier/` | LangGraph maker/checker classification loop + CLI |
| `entries/`    | Ratified registry entries, one YAML file per agent |
| `examples/`   | Plain-text agent descriptions for the demo's cached classifier examples |
| `scripts/`    | `build_registry.py` (compile entries + examples) and `serve_classify.py` (local live endpoint) |
| `docs/`       | Architecture, open-source model, roadmap, ADRs |
| `web/`        | Single-file reference view + interactive classifier hero (zero-build, offline-capable) |

## Web demo

`web/index.html` is a single, zero-build page. Open it by double-click (`file://`), from a
static server, or on GitHub Pages — it renders the registry and a **classifier hero** with
no network call, reading committed data injected as JS globals
([ADR-0004](docs/adr/0004-single-file-web-demo.md),
[ADR-0005](docs/adr/0005-cached-first-classifier-demo.md)).

```bash
# Compile entries/ + examples into web/data/*.js (offline; no key, no network):
python scripts/build_registry.py
python scripts/build_registry.py --check          # CI gate: fails if generated files are stale

# Refresh the cached classifier examples via the live LLM (author-run; needs a key):
python scripts/build_registry.py --rebuild-examples

# Run the live "Classify your own" box locally, then open the URL it prints:
python scripts/serve_classify.py                  # http://localhost:8000  (POST /classify)
```

The hero is **cached-first**: example buttons show committed classifications instantly. The
free-text box classifies live **only** when a local endpoint is configured (via
`serve_classify.py`); elsewhere it degrades gracefully. No API key ever lives in client-side
code.

## Documentation

- [docs/PLAN.md](docs/PLAN.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/OPEN_SOURCE_MODEL.md](docs/OPEN_SOURCE_MODEL.md)
- [docs/ROADMAP.md](docs/ROADMAP.md)
- [docs/DESIGN_DECISIONS.md](docs/DESIGN_DECISIONS.md)

## License

MIT — see [LICENSE](LICENSE).
