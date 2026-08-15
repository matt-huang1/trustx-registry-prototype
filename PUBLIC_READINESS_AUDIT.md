# Public-Facing Readiness Audit

**Repo:** https://github.com/matt-huang1/trustx-registry-prototype
**Commit audited:** `1bae3de` (`main`)
**Date:** 2026-08-15
**Method:** Read-only. Run against a **fresh clone of the public repo** (`git clone https://github.com/matt-huang1/trustx-registry-prototype`) in a clean venv — i.e. literally what a stranger gets. Working tree untouched.

---

## Summary

| Area | Verdict |
|---|---|
| 1. Front door (README, links) | **PASS** — 0 broken links; disclaimer above the fold |
| 2. Contributor path (CONTRIBUTING) | **PASS** — every command works verbatim on a fresh clone |
| 3. Demo path | **PASS** (double-click stated & works) — Pages not enabled, see P |
| 4. Stranger-visible rough edges | **ATTENTION** — 9 items (A–I) |
| 5. Metadata | **ATTENTION** — description and topics empty; Pages off |
| 6. Final suite | **PASS** — all green |

---

# PASS

### 1. The front door

README's first screen does its job: line 3–4 says what it is, lines 6–10 carry the independence disclaimer (*"not an official RAI registry, product, or endorsement"*) above the fold, and §Framework & attribution lands before any self-promotion.

**Links — all clean.** Scanned 27 rendering markdown files:

- **0 broken relative links.** `CONTRIBUTING.md`, `docs/GOVERNANCE.md`, `LICENSE`, `LICENSE-DATA`, `CITATION.md`, all 18 ADRs, `schema/*.json`, `entries/*` — every target exists.
- Anchor `#framework--attribution` (README:9) matches its heading.
- **No** local paths, `file://`, `vscode-webview`, `localhost`, or private URLs anywhere.
- No images, so no broken images.
- `https://arxiv.org/abs/2607.09586` → **HTTP 200**.

### 2. The contributor path

Every command in CONTRIBUTING.md, as written, on a fresh clone:

| Step | Result |
|---|---|
| `pip install -e ".[dev]"` | OK (pulls pytest + black; `requires-python >=3.11` matches the doc) |
| `python -m pytest -q` | **92 passed, 1 skipped** — the jsdom test skips cleanly with no `node_modules`, by design |
| `python scripts/build_registry.py --check` | OK, artifacts up to date |
| `black --check .` | 18 files unchanged |
| `python -m classifier.run "…"` with no key | Fails with a clear, actionable message: *"No LLM API key found. Set LLM_API_KEY…"* |

CI (`.github/workflows/ci.yml`) runs the same four; the jsdom harness is gated through pytest (`tests/test_web_view.py`), so it does gate merges.

### 3. The demo path

README:56 explicitly states double-click (`file://`). Verified real: `web/data/*.js` are committed, so a fresh clone opens with zero setup.

### 5. Metadata (partials that pass)

LICENSE detected as **MIT** by GitHub. Default branch `main`. **One remote branch only** — no stray junk. `.env` is **not tracked**; no `.DS_Store`, `.venv`, or `node_modules` in the index.

### 6. Final suite on HEAD `1bae3de`

pytest **93 passed** · `build_registry.py --check` OK · `black --check` clean · jsdom **18/18 assertions pass**. All green.

---

# ATTENTION

## Highest impact — a panel will hit these

| # | File:line | Issue | Suggested fix |
|---|---|---|---|
| **A** | [docs/ARCHITECTURE.md:10-15](docs/ARCHITECTURE.md#L10-L15) | README:137 links this as "Architecture"; it's a 15-line stub whose back half is a literal `## TODO` with 5 unchecked boxes. Worst rough edge in the repo. | Replace the TODO list with prose — [docs/PLAN.md](docs/PLAN.md) §3 already contains all five bullets' content; or delete the file and point README:137 at PLAN.md §3. |
| **B** | [web/.gitkeep:1](web/.gitkeep#L1) | *"Placeholder. The web UI is intentionally not built in this milestone"* — flatly contradicted by the shipped `web/index.html`. | `git rm web/.gitkeep` (the dir has tracked content now). |
| **C** | [docs/ROADMAP.md:3-6](docs/ROADMAP.md#L3-L6) | Intro frames the current state as *"a placeholder schema … then RAI's real 12-dimension model … and a web UI"* — both shipped. Reads as an abandoned doc. | Rewrite the intro in present tense to match the `[x]` items directly below it. |
| **D** | [docs/ROADMAP.md:15](docs/ROADMAP.md#L15) | M4 "Web UI in `web/`" sits unchecked beside a working demo. | Narrow to "in-browser submitting/challenging" or mark partially delivered. |

## Internal-only phrasing visible to strangers

| # | File:line | Issue | Suggested fix |
|---|---|---|---|
| **E** | [docs/adr/0004-single-file-web-demo.md:15](docs/adr/0004-single-file-web-demo.md#L15) | *"deferred to a later **handoff** and has a marked, empty slot"* — internal-process word, and stale (ADR-0005 delivered the classifier tab). | "…deferred to a later iteration" + a one-line addendum noting ADR-0005 superseded it. |
| **F** | [docs/PLAN.md:128](docs/PLAN.md#L128) | *"the same reason **the pipeline it grew out of** confirmed its exploits by running them…"* — dangling reference to an unnamed prior project no reader can resolve. | Delete the clause; the sentence before it already makes the point. |
| **G** | [docs/PLAN.md:19](docs/PLAN.md#L19) | *"The twelve dimensions are not something **I** devised."* — the only first-person-singular sentence in the design docs. | "The twelve dimensions are not this project's invention." |
| **H** | [CLAUDE.md:8](CLAUDE.md#L8) | Tracked and public. `do NOT use "ROAR"` leaks an internal alternate working name; the file reads as private agent instructions. | Drop the `"ROAR"` clause (keep the RAI-status caution), or untrack the file. |
| **I** | [docs/DESIGN_DECISIONS.md:30-38](docs/DESIGN_DECISIONS.md#L30-L38) | *"**ahead of the repo going public**, the ARC framework's source **is now** explicitly credited … **is now filled in** at all three locations"* — internal changelog voice that implies the citation was previously blank. | Restate as a standing fact: "The ARC framework's source is credited in README §Framework & attribution, CITATION.md, and assets/arc_reference.json." |

**Cleared on inspection (no action needed):**

- `.github/PULL_REQUEST_TEMPLATE.md:23-26` uses "I did not…" — correct contributor voice, not a leak.
- No hits for Claude / AI-session references, "as discussed", "per the handoff", fellowship / trial / interview / take-home, or RAI-internal filenames.
- Hannah Liu's name appears only in legitimate paper attribution: README:34, CITATION.md:14/21, ADR-0012:81, PLAN.md:35/195, `assets/arc_reference.json`.
- `.placeholder-note` in `web/index.html` is a CSS class name, not placeholder text — the element itself carries the correct RAI attribution and independence disclaimer.

## Links that resolve locally but break on GitHub

| # | File:line | Issue | Suggested fix |
|---|---|---|---|
| **J** | [CONTRIBUTING.md:140](CONTRIBUTING.md#L140), [docs/GOOD_FIRST_ISSUES.md:66](docs/GOOD_FIRST_ISSUES.md#L66) | "Question / discussion **issue**" links to `.github/ISSUE_TEMPLATE/config.yml` — a visitor clicking it gets raw YAML, not an issue form. | Link to `https://github.com/matt-huang1/trustx-registry-prototype/issues/new/choose`. |
| **K** | [CONTRIBUTING.md:141](CONTRIBUTING.md#L141) + [.github/ISSUE_TEMPLATE/config.yml:3-5](.github/ISSUE_TEMPLATE/config.yml#L3-L5) | Both point at GitHub Discussions — **verified HTTP 404**. Discussions is **disabled** on the repo, so the top link in the issue chooser is dead. | Enable Discussions (Settings → Features → checkbox), or remove both references. |
| **L** | [docs/GOOD_FIRST_ISSUES.md:4-6](docs/GOOD_FIRST_ISSUES.md#L4-L6), [CONTRIBUTING.md:134](CONTRIBUTING.md#L134) | Both promise maintainers track these under the `good first issue` label. The label exists; **0 issues are filed**. A panel clicking through finds an empty tracker. | File the 5 issues from GOOD_FIRST_ISSUES.md and apply the label — ~5 minutes, and it makes the contribution story real. |
| **M** | [README.md:70-76](README.md#L70-L76) | Quickstart's third command needs `LLM_API_KEY`; nothing says so, and nothing says the tests *don't*. Confirmed: a fresh clone gets a `RuntimeError` on line 75. (CONTRIBUTING:40 does say it; README doesn't.) | Append to line 75: `# needs LLM_API_KEY (the test suite above does not)`. |

## Metadata & Pages

| # | Item | Current state | Suggested |
|---|---|---|---|
| **O** | Repo description | **empty** | *"An open-source registry that classifies AI agents by risk with evidence-backed, independently checkable entries — scored against the ARC 12-dimension model."* |
| **O** | Topics | **none set** | `ai-safety` · `ai-governance` · `risk-assessment` · `responsible-ai` · `ai-agents` · `open-registry` |
| **N/P** | GitHub Pages | **not enabled** (API returns 404) | See below |
| — | License | MIT, correctly detected | no action |
| — | Default branch | `main` | no action |
| — | Stray branches | none (only `origin/main`) | no action |

### On enabling GitHub Pages (item 3 / N / P)

Worth doing, and it's a two-click change. README:54 is headed "Live demo" but offers only shell commands; a panel scanning for something to click finds nothing.

**What it takes:** Settings → Pages → Source: *Deploy from a branch* → Branch `main`, folder `/ (root)` → Save.

**Resulting URL:** `https://matt-huang1.github.io/trustx-registry-prototype/web/`

The page works unmodified — [ADR-0004](docs/adr/0004-single-file-web-demo.md) built it to inject data as JS globals precisely so it runs identically on `file://`, a static server, and Pages, with no build step and no CORS caveat.

**Not enabled during this audit, per instruction.** If you do enable it, the follow-ups are: add the URL to README:54 and to the repo's Website field.

---

## One judgment call

Items **H** (CLAUDE.md) and **I** (DESIGN_DECISIONS notes) are the two places the repo reads as something being prepared for review rather than a standing open-source project. Neither is disqualifying, and **H** is genuinely a stylistic choice — plenty of public repos ship a CLAUDE.md. The `"ROAR"` clause is the only part that is a clear leak.
