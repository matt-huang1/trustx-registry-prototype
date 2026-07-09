# ADR-0007: Hash-based tabbed single-page layout; left-aligned horizontal nav

- Status: Accepted
- Date: 2026-07-09

## Decision
Restructure `web/index.html` from three stacked sections into **three tabs shown one at a
time** — Registry, Classify, Policy Gate — driven entirely by the URL hash:

- `#registry` / `#classify` / `#gate` map to three `<section class="panel">` elements;
  switching is plain show/hide over the `hidden` attribute. No hash (or an unknown one)
  falls back to `#registry`. The hash values deliberately match no element `id`, so the
  browser never scroll-jumps on its own.
- The nav is **horizontal and left-aligned**, sitting directly beneath the wordmark in the
  masthead, ordered Registry → Classify → Policy Gate. Tabs are plain `<a href="#…">`
  anchors, so clicking, keyboard activation (Tab + Enter), deep links, and back/forward all
  ride on native hash navigation; the only JS is a `hashchange` listener that toggles
  `hidden` and moves `aria-current="page"`. The active tab is a quiet ink-blue underline
  overlaying the masthead rule — never a filled pill or saturated background.
- All three panels are fully rendered at boot from the injected globals regardless of
  visibility, so tab switching costs nothing and hidden tabs (e.g. the gate's live regions)
  keep their state. Still single-file, zero-build, zero-fetch (ADR-0004): the tabs add no
  framework, no router library, and no network.
- The gate's "View full registry entry" link switches to the Registry tab (updating the
  hash and history) after clearing filters and selecting the entry — one selection model
  across tabs.
- `tests/web/check_page.mjs` (jsdom, driven from `tests/test_web_view.py`) asserts the
  behaviour offline: default tab, deep links, unknown-hash fallback, click / hashchange /
  back-button switching, and that all three tabs' content renders. The pytest wrapper skips
  when Node or jsdom is missing so the Python-only suite stays hermetic; CI installs both.

## Context
The page had grown by accretion: classifier hero, then registry master–detail, then policy
gate, stacked in one long scroll with an anchor-link nav. Three sections built at different
times read as three different pages — mismatched card chrome, three label scales, two
evidence treatments — and the scroll buried the gate (the newest, most argument-carrying
demo) below two screens of content. Each section is also a distinct *mode* of using the
registry (browse, propose, enforce); showing one mode at a time matches how the page is
actually demonstrated and gives each a stable, shareable URL.

## Alternatives considered
- **Keep the single scrolling page with dividers.** Cheapest, and anchors already existed.
  Set aside because it is the layout that produced the incoherence: modes compete on one
  canvas, the gate stays buried, and "link me to the gate" means scrolling past everything
  else. Dividers fix none of that.
- **Show/hide tabs without the hash (JS state only).** Same visual result, less machinery.
  Set aside because it breaks the web: no deep links, no back/forward, refresh forgets the
  tab, and the docs/README can't link to a specific mode. The hash gives all of that for
  free with *less* JS (native anchor navigation replaces click handlers).
- **Vertical sidebar nav.** Scales to more sections and is common in doc sites. Set aside
  because three items don't justify a persistent rail: it would compete with the registry's
  own master–detail index (two vertical lists side by side), steal width from the 66–70ch
  prose column, and read as an app shell — the wrong register for a calm reference
  document. Rejected explicitly per the design brief: horizontal, left-aligned, under the
  wordmark.

## Why
Hash-based tabs keep the single-file, zero-build contract of ADR-0004 while giving each
mode of the registry its own addressable surface. Native anchors mean the router is the
browser: less code than the anchor-scroll nav it replaces, and every navigation behaviour
(deep link, history, keyboard) is inherited rather than reimplemented. One tab at a time
also forces the coherence work the stacked page dodged — the three sections now share one
panel scaffold, one section-label scale, one tier-marker component, and one evidence
treatment, so the page reads as a single considered system.
