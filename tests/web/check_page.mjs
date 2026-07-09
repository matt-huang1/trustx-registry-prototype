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
  // The tier is the key fact of each dimension block: every score carries the
  // tier-toned marker and its score--N class (shared with classify + gate).
  check(
    doc.querySelectorAll("#record .dimension .score .mark").length === 12 &&
      Array.from(doc.querySelectorAll("#record .dimension .score")).every((s) =>
        /score--[123]/.test(s.className)
      ),
    "record: every dimension score carries the tier marker + score class"
  );
  check(
    doc.querySelectorAll("#record .rec-chip").length >= 2,
    "record: system type and autonomy level chips rendered"
  );
  check(
    doc.querySelectorAll("#record .score .pip").length === 12 * 3 &&
      doc.querySelector("#record .score .figure").textContent.includes("/ 3"),
    "record: scores render on the 1-3 ARC scale"
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
  check(
    doc.querySelector("#panel-gate .pg-columns #pgPolicy") !== null &&
      doc.querySelector("#panel-gate .pg-columns #pgDecision") !== null &&
      doc.querySelector("#panel-gate .pg-columns #pgPlan") === null,
    "gate tab: policy and checker share the two-column row; scenario outside it"
  );
  // ADR-0009: the checked decision is an open record (shared .record/.rec-title
  // classes), the same treatment as the registry detail and classify result.
  check(
    doc.querySelector("#pgDecision.record .rec-head .rec-title") !== null,
    "gate tab: checker decision uses the open record treatment"
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
