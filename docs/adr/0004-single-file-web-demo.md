# ADR-0004: Single-file HTML demo with registry data injected as a JS global

- Status: Accepted
- Date: 2026-07-09

## Decision
Ship the browse/registry view as a single self-contained `web/index.html` with no
framework, no build step, and no runtime network dependency. The compiled registry is
read from an injected browser global: `scripts/build_registry.py` emits
`web/data/registry.js` containing exactly `window.__REGISTRY__ = <the same JSON array>;`
alongside the canonical `web/data/registry.json`. The page loads it with a plain
`<script src="data/registry.js"></script>` and reads `window.__REGISTRY__` — it does
**not** `fetch()` the JSON. `build_registry.py --check` fails if *either* generated file
is stale, so both stay in lockstep with `entries/*.yaml`. This is reference mode; the
interactive classifier is deferred to a later handoff and has a marked, empty slot.

## Context
The prototype needs a live, shareable demo that renders the reference entries anywhere:
by double-click from the filesystem (`file://`), from a local static server, and on
GitHub Pages — with zero setup and no console errors. Browsers block `fetch()` of a
local file under the `file://` origin (CORS), so a page that fetched `registry.json`
would render from a server but fail on a plain double-click — exactly the "just open it"
path a demo relies on. Injecting the data as a `<script>`-assigned global sidesteps the
origin entirely: the same file works in all three contexts.

## Alternatives considered
- **`fetch("data/registry.json")` + a local server.** Keeps a single data artifact and
  is the "proper" way to load JSON, but breaks on `file://` double-click (CORS), forcing
  every viewer to run a server. Loses the bulletproof-open property that makes the demo
  useful.
- **A React/Next (or similar) build.** Componentised and familiar, but adds a toolchain,
  a build step, and `node_modules` to a prototype whose data is three static entries —
  weight with no payoff, and it still would not open from `file://` without a server.
  Named as the production direction in the roadmap, not needed now.

## Why chosen
The injected-global approach gives a demo that opens *anywhere* with no server, no build,
and no CORS caveats, while keeping `registry.json` as the canonical machine-readable
artifact (the `.js` file is a derived twin, checked for staleness in CI). Restraint over
tooling for a prototype: the production stack (a real component framework and an API) is
named in the plan and can replace this once the schema and classifier stabilise.
