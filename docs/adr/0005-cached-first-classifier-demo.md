# ADR-0005: Cached-first classifier demo; live path via an optional local endpoint; no client-side keys

- Status: Accepted
- Date: 2026-07-09

## Decision
Add the interactive classifier to `web/index.html` as a **cached-first, live-secondary**
hero above the registry:

1. **Cached (primary).** A small set of plain-text agent descriptions in `examples/`
   (a low, a medium, and a money-movement high case) are classified *at build time by the
   author* through the existing maker/checker loop, and the ratified results are committed
   as `web/data/examples.json` (canonical) and `web/data/examples.js`
   (`window.__EXAMPLES__ = <array>;`, the same injected-global pattern as `registry.js`).
   The page renders a clicked example instantly, with no model call, in the same visual
   style as a registry entry. Generating these calls the live LLM, so it is gated behind
   `python scripts/build_registry.py --rebuild-examples`; the default build and `--check`
   are offline (they only re-derive `examples.js` from the committed `examples.json` and
   verify freshness). CI runs the offline path only.

2. **Live (progressive enhancement).** The "Classify" box POSTs to
   `window.__CLASSIFY_ENDPOINT__` **only if one is configured** (empty by default).
   `scripts/serve_classify.py` is a tiny local server that wraps the same classifier loop,
   returns the ratified-shape result as JSON, and — when it serves the page — injects the
   endpoint. Opened any other way (`file://`, GitHub Pages) the endpoint stays empty and the
   box shows a clear message pointing back to the cached examples. No API key ever appears in
   any committed file or client-side code. On the live path the proposal is auto-accepted
   **only for display**: `provenance.approved_by` stays null and a banner states it "would
   require human ratification before entering the registry", so the loop's human gate is
   represented, not dropped. Deterministic floors apply on this path too — a pasted
   money-movement description shows `delegated_authority` pinned to the floor.

## Context
The registry page (ADR-0004) is a single-file, zero-build, offline-capable artifact that
must open identically from `file://`, a local server, and GitHub Pages. The interactive
classifier needs a model, but a static page cannot call one securely — embedding a key in
client code would leak it to anyone who opens the page. The demo also needs to be reliable
for a viewer with no setup: a live-only classifier would fail on Pages, need a key, cost
tokens, and vary run to run. And the classifier's integrity rests on a human ratification
gate that must remain visible even in a browser demo.

## Alternatives considered
- **Live-only classifier.** Simplest conceptually, but breaks the offline/Pages story
  entirely (needs a server + key), is non-deterministic, costs tokens per view, and gives no
  reliable primary demo path. Rejected as the primary; kept as optional enhancement.
- **Embed an API key in the client.** Would make live classification work anywhere with no
  server. Rejected outright: it exposes the key to every viewer — an unacceptable secret leak.
- **A serverless proxy (e.g. a function that holds the key).** The right production answer —
  keeps the key server-side and works on a static host — but it is infrastructure this
  prototype does not have. Deferred to production; `serve_classify.py` is the local stand-in
  and the client contract (`window.__CLASSIFY_ENDPOINT__`) is already the shape a proxy would
  satisfy.

## Why chosen
Cached-first gives a bulletproof primary demo: instant, identical every run, no key, no
network, and it proves the whole pipeline (scores + rationale + evidence, the deterministic
override, the challenge record, the rolled-up tier) on committed data — including a
money-movement example where the model under-rated authority and the deterministic floor
overrode it to `high`. The live path is a genuine progressive enhancement that reuses the
exact same classifier, schema, rules, and rollup (no duplicated scoring logic), degrades
gracefully where it cannot run, never handles a client-side key, and keeps the human gate
visible. This matches the core principle — the model proposes, deterministic checks decide
where a fact can be pinned down, and an accountable human owns the rest.
