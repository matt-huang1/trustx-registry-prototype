# trustx-registry-prototype

A prototype **open-source registry that classifies AI agents by risk** with
defensible, evidence-backed entries rather than self-asserted labels. A model
*proposes* a score, deterministic checks *decide* wherever a fact can be pinned
down, and an accountable human *ratifies* the rest — with the depth of human
scrutiny scaled to the risk tier. The schema here is a placeholder until RAI's
real 12-dimension model lands. Working name only — this is **not** an official
RAI artifact.

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
| `schema/`     | JSON Schema for a registry entry (placeholder dimensions) |
| `classifier/` | LangGraph maker/checker classification loop + CLI |
| `entries/`    | Ratified registry entries, one YAML file per agent |
| `docs/`       | Architecture, open-source model, roadmap, ADRs |
| `web/`        | (empty) future web UI — not built yet |

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/OPEN_SOURCE_MODEL.md](docs/OPEN_SOURCE_MODEL.md)
- [docs/ROADMAP.md](docs/ROADMAP.md)
- [docs/DESIGN_DECISIONS.md](docs/DESIGN_DECISIONS.md)

## License

MIT — see [LICENSE](LICENSE).
