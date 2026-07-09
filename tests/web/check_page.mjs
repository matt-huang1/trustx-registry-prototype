// Offline jsdom checks for web/index.html — the hash-driven tabbed layout.
//
// Loads the committed single-file page (plus its data/*.js globals) in jsdom and
// asserts the tab behaviour end to end: default tab with no hash, deep links,
// unknown-hash fallback, click + hashchange switching, and that all three tabs'
// content actually renders. No network: everything resolves from file:// URLs.
//
// Run directly (node check_page.mjs) or via pytest (tests/test_web_view.py), which
// skips when node/jsdom are unavailable. Install deps with: npm ci --prefix tests/web

import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { JSDOM, VirtualConsole } from "jsdom";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const INDEX = path.join(ROOT, "web", "index.html");

let failures = 0;
function check(cond, label) {
  if (cond) {
    console.log(`ok - ${label}`);
  } else {
    failures += 1;
    console.error(`FAIL - ${label}`);
  }
}

async function loadPage(hash = "") {
  // Surface real page errors as failures; ignore jsdom's expected "Not implemented:
  // Window's scrollTo()" (layout-less jsdom has no scrolling — the page guards nothing
  // else behind it).
  const virtualConsole = new VirtualConsole();
  virtualConsole.on("jsdomError", (err) => {
    if (!String(err.message).includes("Not implemented")) {
      failures += 1;
      console.error(`FAIL - page error: ${err.message}`);
    }
  });
  const dom = await JSDOM.fromFile(INDEX, {
    url: pathToFileURL(INDEX).href + hash,
    runScripts: "dangerously",
    resources: "usable",
    pretendToBeVisual: true,
    virtualConsole,
  });
  await new Promise((resolve, reject) => {
    dom.window.addEventListener("load", resolve);
    dom.window.addEventListener("error", (e) => reject(e.error ?? new Error(e.message)));
  });
  return dom;
}

function visiblePanel(dom) {
  const shown = ["panel-registry", "panel-classify", "panel-gate"].filter(
    (id) => !dom.window.document.getElementById(id).hidden
  );
  return shown.length === 1 ? shown[0] : `(${shown.length} visible: ${shown})`;
}

function activeTabLink(dom) {
  const link = dom.window.document.querySelector('nav.tabs a[aria-current="page"]');
  return link ? link.getAttribute("data-tab") : null;
}

// Wait one macrotask so an async hashchange dispatch settles.
const tick = () => new Promise((r) => setTimeout(r, 0));

// Poll until cond() holds (hash navigation dispatches asynchronously in jsdom).
async function waitFor(cond, ms = 1000) {
  const deadline = Date.now() + ms;
  while (!cond() && Date.now() < deadline) await tick();
  return cond();
}

// ---- 1. No hash: registry is the default, and every tab's content rendered ----
{
  const dom = await loadPage();
  check(visiblePanel(dom) === "panel-registry", "no hash: registry panel is shown");
  check(activeTabLink(dom) === "registry", "no hash: Registry tab marked current");

  const doc = dom.window.document;
  check(
    doc.querySelectorAll("#entryList button.entry").length >= 3,
    "registry tab: entry list rendered"
  );
  check(
    doc.querySelector("#record .rec-title") !== null,
    "registry tab: detail record rendered"
  );

  // ---- ARC 12-dimension record anatomy (the real model, not the placeholder) ----
  check(
    doc.querySelectorAll("#record .dimension").length === 12,
    "record: all 12 ARC dimensions rendered"
  );
  check(
    doc.querySelectorAll("#record .dim-group").length === 4,
    "record: dimensions grouped under the four ARC groups"
  );
  const groupNames = Array.from(doc.querySelectorAll("#record .dim-group")).map(
    (h) => h.textContent
  );
  check(
    groupNames[0] === "Autonomy & Decision Power" &&
      groupNames[3] === "Data Authority & Confidentiality",
    "record: group headings carry the verbatim ARC group names"
  );
  check(
    doc.querySelector("#record .derivation") !== null &&
      /Weighting profile/.test(doc.querySelector("#record .derivation").textContent),
    "record: tier derivation names the weighting profile"
  );
  check(
    doc.querySelectorAll("#record .standards").length === 12 &&
      /NIST AI RMF/.test(doc.querySelector("#record .standards").textContent),
    "record: every dimension shows its standards mappings"
  );
  // Standards render as discrete framework+refs units inside a wrapping flex
  // group, so long mapping rows flow onto new lines instead of overflowing.
  check(
    Array.from(doc.querySelectorAll("#record .standards")).every(
      (p) => p.querySelectorAll(".std-item").length >= 1
    ),
    "record: standards mappings are discrete wrapping units"
  );
  // ---- Standards folds (ADR-0015): collapsed by default, expandable chips ----
  const folds = Array.from(doc.querySelectorAll("#record details.standards-fold"));
  check(folds.length === 12, "standards: one fold per dimension");
  check(folds.every((f) => !f.open), "standards: folds are collapsed by default");
  check(
    folds.every((f) => /^Standards \(\d+\)$/.test(f.querySelector("summary").textContent)),
    "standards: summaries read 'Standards (n)'"
  );
  // The whole summary row is the disclosure control, and it carries the state
  // for assistive tech: aria-expanded false while collapsed, true once open.
  check(
    folds.every(
      (f) => f.querySelector("summary").getAttribute("aria-expanded") === "false"
    ),
    "standards: collapsed summaries carry aria-expanded=false"
  );
  folds[0].open = true;
  check(
    folds[0].open && folds[0].querySelectorAll(".std-ref").length >= 1,
    "standards: an expanded fold shows framework→control chips"
  );
  check(
    await waitFor(
      () => folds[0].querySelector("summary").getAttribute("aria-expanded") === "true"
    ),
    "standards: opening a fold flips its summary to aria-expanded=true"
  );
  folds[0].open = false;
  check(
    await waitFor(
      () => folds[0].querySelector("summary").getAttribute("aria-expanded") === "false"
    ),
    "standards: closing a fold flips its summary back to aria-expanded=false"
  );
  // The tier is the key fact of each dimension block: every detail row uses
  // THE score mark — the number-in-a-tier-toned-box (.scorebox), identical to
  // the strip cells — plus its score--N tier class. No separate square marker
  // and no pip scale remain anywhere.
  check(
    doc.querySelectorAll("#record .dimension .score .scorebox").length === 12 &&
      Array.from(doc.querySelectorAll("#record .dimension .score")).every((s) =>
        /score--[123]/.test(s.className)
      ),
    "record: every dimension score carries the number-in-box mark + score class"
  );
  check(
    doc.querySelectorAll("#record .score .mark").length === 0 &&
      doc.querySelectorAll("#record .pip").length === 0 &&
      doc.querySelectorAll("#record .score .figure").length === 0,
    "record: no separate square marker, pip scale, or figure remains"
  );
  check(
    doc.querySelectorAll("#record .rec-chip").length >= 2,
    "record: system type and autonomy level chips rendered"
  );
  check(
    Array.from(doc.querySelectorAll("#record .dimension .score .scorebox")).every(
      (b) => /^[123]$/.test(b.textContent)
    ),
    "record: detail score marks carry the 1-3 figure inside the box"
  );
  // ---- Grouped tier strip (ADR-0014): the record's scannable top layer ----
  const strip = doc.querySelector("#record .tier-strip");
  check(strip !== null, "tier strip: rendered on the registry record");
  check(
    strip !== null &&
      strip.querySelectorAll(".ts-band").length === 4 &&
      strip.querySelectorAll(".ts-cell").length === 12,
    "tier strip: 12 dimension cells across the four ARC bands"
  );
  check(
    Array.from(strip.querySelectorAll(".ts-band")).every((band) => {
      const scores = Array.from(band.querySelectorAll(".ts-cell")).map((c) =>
        Number(c.getAttribute("data-score"))
      );
      return scores.every((s, i) => i === 0 || scores[i - 1] >= s);
    }),
    "tier strip: cells order by score descending within each band"
  );
  check(
    doc.querySelectorAll("#record .ts-legend").length === 1,
    "tier strip: exactly one legend per record"
  );
  // ADR-0015 cell anatomy: ONE mark carries colour AND value — a tier-toned box
  // containing the score figure. No separate square+number redundancy.
  check(
    Array.from(strip.querySelectorAll(".ts-cell")).every(
      (c) =>
        c.querySelector(".scorebox") !== null &&
        c.querySelector(".scorebox").textContent === c.getAttribute("data-score") &&
        c.querySelector(".mark") === null
    ),
    "tier strip: cells lead with the score figure in a tier box (no separate mark)"
  );
  // The strip is container-responsive: 4 band columns on a wide record, 2×2,
  // then 1 as the record narrows (jsdom does no layout; assert the declared CSS).
  const css = doc.querySelector("style").textContent;
  check(
    /\.tier-strip\s*\{[^}]*grid-template-columns:\s*repeat\(4, minmax\(0, 1fr\)\)/.test(css) &&
      /@container \(max-width: 56rem\)\s*\{\s*\.tier-strip\s*\{\s*grid-template-columns:\s*repeat\(2, minmax\(0, 1fr\)\)/.test(css) &&
      /@container \(max-width: 27rem\)\s*\{\s*\.tier-strip\s*\{\s*grid-template-columns:\s*minmax\(0, 1fr\)/.test(css),
    "tier strip: 4-col → 2×2 → 1 container-responsive layout declared"
  );
  // The tier-derivation summary reads as a distinct callout, not blended prose.
  check(
    /\.derivation\s*\{[^}]*background:\s*var\(--paper-2\);[^}]*border-left:\s*3px solid var\(--accent\)/.test(css),
    "derivation: renders as a tinted, accent-ruled callout"
  );
  // Record description and active-policy description span the full content
  // width — deliberately uncapped (max-width: none), unlike rationale prose.
  check(
    /\.record \.description\s*\{[^}]*max-width:\s*none/.test(css) &&
      /\.pg-policy \.pg-policy-desc\s*\{[^}]*max-width:\s*none/.test(css),
    "widths: record description and policy description are full-width"
  );
  // The strip summarises; the full per-dimension detail stays below it.
  check(
    !!(
      strip.compareDocumentPosition(doc.querySelector("#record .dimension")) &
      dom.window.Node.DOCUMENT_POSITION_FOLLOWING
    ),
    "tier strip: sits above the per-dimension detail"
  );

  // An all-baseline low entry has NO driver: the tier is low because nothing
  // rose, so no cell carries the ring and the callout says so (ADR-0015).
  doc
    .querySelector('#entryList button.entry[data-slug="internal-knowledge-assistant"]')
    .click();
  check(
    doc.querySelectorAll("#record .ts-cell--driver").length === 0 &&
      doc.querySelectorAll("#record .dim-flag.drives").length === 0,
    "all-baseline entry: no dimension is marked as driving the tier"
  );
  check(
    /nothing drives the tier/i.test(doc.querySelector("#record .derivation").textContent),
    "all-baseline entry: derivation callout says nothing rose above baseline"
  );

  // KYC is the canonical peak-not-weighted case: Data Sensitivity is scored 3
  // but the tool_using_agent profile does not tier off it; Blast Radius (2) drives.
  doc
    .querySelector('#entryList button.entry[data-slug="kyc-onboarding-triage-agent"]')
    .click();
  const kycDriver = doc.querySelector('#record .ts-cell[data-dim="blast_radius"]');
  check(
    kycDriver !== null &&
      kycDriver.classList.contains("ts-cell--driver") &&
      /drives tier/i.test(kycDriver.textContent),
    "KYC strip: driver cell (Blast Radius) carries the drives-tier mark"
  );
  check(
    doc.querySelectorAll("#record .ts-cell--driver").length === 1,
    "KYC strip: Blast Radius is the sole driver"
  );
  // Not-tier-weighted is a CELL STATE (dashed/muted + dagger), explained once
  // in the legend — never an inline chip crammed into the cell (ADR-0015).
  const kycDS = doc.querySelector('#record .ts-cell[data-dim="data_sensitivity"]');
  check(
    kycDS !== null &&
      kycDS.classList.contains("ts-cell--unweighted") &&
      kycDS.querySelector("sup.ts-uw") !== null,
    "KYC strip: Data Sensitivity 3 renders as the daggered not-weighted cell state"
  );
  check(
    kycDS !== null &&
      !/not tier-weighted/i.test(kycDS.textContent) &&
      /† scored · not tier-weighted/.test(
        doc.querySelector("#record .ts-legend").textContent
      ),
    "KYC strip: the not-weighted state is explained once in the legend, not in the cell"
  );
  check(
    kycDS !== null && kycDS.closest(".ts-cells").firstElementChild === kycDS,
    "KYC strip: the peak dimension leads its band"
  );

  // Adopted seed entries appear alongside the archetypes (6 committed entries).
  check(
    doc.querySelectorAll("#entryList button.entry").length === 6,
    "registry tab: archetypes plus adopted seed entries listed"
  );
  check(
    doc.querySelectorAll("#clsExamples button").length >= 3,
    "classify tab: cached example buttons rendered (even while hidden)"
  );
  check(
    doc.querySelector("#clsResult .rec-title") === null &&
      doc.querySelector("#clsResult .panel-note") !== null,
    "classify tab: quiet empty state before any selection"
  );
  check(
    doc.querySelectorAll("#pgPlan > li").length === 3 &&
      doc.querySelectorAll("#pgPolicy table.pg-table tbody tr").length === 3 &&
      doc.querySelector("#pgDecision .pg-verdict") !== null,
    "gate tab: policy table, scenario plan, and check decision rendered"
  );

  // Layout scaffolds: Classify is a vertical flow (ADR-0011) — a centered input
  // block, then the result region below it; no master-detail grid on this tab.
  // The gate keeps its two-column row with the scenario spanning full width.
  const FOLLOWS = dom.window.Node.DOCUMENT_POSITION_FOLLOWING;
  const inputBlock = doc.querySelector("#panel-classify .cls-input-block");
  check(
    inputBlock !== null &&
      inputBlock.querySelector("#clsForm") !== null &&
      doc.querySelector("#panel-classify .master-detail") === null &&
      !!(inputBlock.compareDocumentPosition(doc.getElementById("clsResult")) & FOLLOWS),
    "classify tab: centered input block precedes the full-width result region"
  );
  // ADR-0010: the free-text input is the hero — it precedes the cached examples.
  check(
    !!(
      doc.getElementById("clsForm").compareDocumentPosition(
        doc.getElementById("clsExamples")
      ) & FOLLOWS
    ),
    "classify input block: input leads, cached examples follow as secondary"
  );
  // Clicking an example populates the result region below it.
  doc.querySelector("#clsExamples button").click();
  check(
    doc.querySelector("#clsResult .rec-title") !== null &&
      doc.querySelector('#clsExamples button[aria-pressed="true"]') !== null,
    "clicking an example renders its record in the result region"
  );
  // Shared renderer: the classify result carries the same grouped tier strip.
  check(
    doc.querySelectorAll("#clsResult .tier-strip .ts-cell").length === 12,
    "classify result: grouped tier strip renders identically"
  );
  // ADR-0015: the scenario player leads the gate tab, then the stated policy,
  // then the full-width checker — no two-column row, no lopsided empty column.
  check(
    !!(
      doc.getElementById("pgScenario").compareDocumentPosition(
        doc.getElementById("pgPolicy")
      ) & FOLLOWS
    ) &&
      !!(
        doc.getElementById("pgPolicy").compareDocumentPosition(
          doc.getElementById("pgDecision")
        ) & FOLLOWS
      ) &&
      doc.querySelector("#panel-gate .pg-columns") === null,
    "gate tab: scenario first, then policy, then the full-width checker"
  );
  // ADR-0009: the checked decision is an open record (shared .record/.rec-title
  // classes), the same treatment as the registry detail and classify result.
  check(
    doc.querySelector("#pgDecision.record .rec-head .rec-title") !== null,
    "gate tab: checker decision uses the open record treatment"
  );
  // Shared renderer: the checked decision carries the same grouped tier strip.
  check(
    doc.querySelectorAll("#pgDecision .tier-strip .ts-cell").length === 12,
    "gate checker: grouped tier strip renders identically"
  );

  // Gate decisions must show the tier once (the marker), never restated in the reason.
  const reasons = Array.from(doc.querySelectorAll("#pgDecision .pg-reason"));
  check(reasons.length > 0, "gate tab: decision reason present");
  check(
    reasons.every((p) => !/tier\s+(LOW|MEDIUM|HIGH)/.test(p.textContent)),
    "gate tab: reason does not restate the tier"
  );

  // ---- Tab switching in one document: click, then programmatic hash change ----
  dom.window.document.querySelector('nav.tabs a[data-tab="classify"]').click();
  check(
    await waitFor(() => visiblePanel(dom) === "panel-classify"),
    "clicking Classify tab shows classify panel"
  );
  check(activeTabLink(dom) === "classify", "clicking Classify tab moves aria-current");
  check(dom.window.location.hash === "#classify", "clicking Classify tab updates the hash");

  dom.window.location.hash = "#gate";
  check(
    await waitFor(() => visiblePanel(dom) === "panel-gate"),
    "hashchange to #gate shows gate panel"
  );

  dom.window.history.back();
  check(
    await waitFor(() => visiblePanel(dom) === "panel-classify"),
    "history back returns to classify panel"
  );

  // ---- Registry empty state: a filter that matches nothing clears the detail ----
  const nameInput = doc.getElementById("nameFilter");
  nameInput.value = "zzz-no-such-agent";
  nameInput.dispatchEvent(new dom.window.Event("input", { bubbles: true }));
  check(
    doc.querySelector("#entryList .empty") !== null,
    "registry filter with no match shows the empty list note"
  );
  check(
    doc.querySelector("#record .rec-title") === null &&
      doc.querySelector("#record .panel-note") !== null,
    "registry detail shows a quiet empty state instead of a filtered-out record"
  );
  nameInput.value = "";
  nameInput.dispatchEvent(new dom.window.Event("input", { bubbles: true }));
  check(
    doc.querySelector("#record .rec-title") !== null,
    "clearing the filter restores the detail record"
  );
}

// ---- 2. Deep link straight to the gate ----
{
  const dom = await loadPage("#gate");
  check(visiblePanel(dom) === "panel-gate", "deep link #gate: gate panel is shown");
  check(activeTabLink(dom) === "gate", "deep link #gate: Policy Gate tab marked current");
}

// ---- 3. Deep link to classify ----
{
  const dom = await loadPage("#classify");
  check(visiblePanel(dom) === "panel-classify", "deep link #classify: classify panel is shown");
}

// ---- 4. Unknown hash falls back to registry ----
{
  const dom = await loadPage("#nonsense");
  check(visiblePanel(dom) === "panel-registry", "unknown hash: falls back to registry");
  check(activeTabLink(dom) === "registry", "unknown hash: Registry tab marked current");
}

if (failures > 0) {
  console.error(`\n${failures} check(s) failed`);
  process.exit(1);
}
console.log("\nall web view checks passed");
