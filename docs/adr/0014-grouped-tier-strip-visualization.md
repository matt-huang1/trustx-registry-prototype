# 0014 — Grouped tier-strip visualization (peak-forward, driver + not-weighted marked)

> Amended by [ADR-0015](0015-record-layout-revamp.md): cells now lead with one
> number-in-box mark (no separate square + figure), "scored · not
> tier-weighted" is a daggered cell state explained in the legend rather than
> an inline tag, and the four bands lay out as a container-responsive
> 4 → 2×2 → 1 grid. The peak-forward ordering, driver ring, and
> radar/bar rejections below stand.

## Decision

Add a grouped **tier strip** as the scannable top layer of the shared entry
renderer, above the full per-dimension detail, rendered identically on the
registry detail, the classify result, and the gate checker:

* All 12 dimensions render as compact cells (dimension name + tier score) in
  their four ARC groups, each group a labelled band. Within each band, cells
  order by score **descending**, so the hottest dimension in each group reads
  first.
* Cells reuse the existing restrained tier tones (`--tier-low` /
  `--tier-medium` / `--tier-high`) and the shared square-marker metrics — no
  new palette.
* The dimension(s) in `tier_derivation.driving_dimensions` carry an accent
  ring and a "drives tier" tag.
* Any dimension scored 3 — or above the driver's score — that is **not** in
  the profile's `tier_dimensions` carries a dashed outline and an explicit
  "scored · not tier-weighted" tag. This surfaces the scoring-vs-weighting
  finding (ADR-0012) on the entry itself; the KYC agent's Data Sensitivity = 3
  under the `tool_using_agent` profile is the canonical case.
* The existing tier-derivation sentence stays directly above the strip, so the
  sentence and the strip agree; one small legend (Low/Medium/High, drives
  tier, scored · not tier-weighted) renders once per record.
* The full per-dimension breakdown — tier label, rationale, evidence quotes,
  standards mappings — remains fully visible beneath the strip, unchanged.
  The strip summarises; it deletes nothing.

Plain HTML/CSS in the single-file page; cells flex-wrap inside the container,
so the strip never forces horizontal scroll.

## Context

An entry's 12 scores were only readable by scanning twelve full ledger blocks.
The most important facts — where the peaks are, which dimension actually drove
the tier, and where a high score was scored but *not* tier-weighted — were
buried in per-dimension flags. Worst-case-wins (ADR-0012) means a single spiky
dimension decides the tier, so the visualization must keep the peak legible,
not smooth it away.

## Alternatives considered

* **12-spoke radar chart** — rejected. A radar's enclosed area visually
  averages a spiky profile: one dimension at 3 among eleven at 1 reads as a
  small, calm shape, which contradicts worst-case-wins. Twelve spoke labels
  also crowd illegibly at the widths this page supports, and a chart library
  (or hand-rolled SVG trigonometry) fights the single-file, no-dependency
  constraint.
* **Grouped bar chart** — rejected. Bar height invites reading the group's
  average and comparing totals; the tier is decided by the maximum, not the
  mass. Bars also demand an axis and gridlines — chart chrome this calm page
  avoids.
* **Strip ordered by schema position (not score)** — rejected. Keeping schema
  order makes cells findable but hides the peak mid-row; the detail ledger
  below already provides the stable schema-ordered reading.

## Why

The strip is peak-forward: descending order within each band puts the maximum
— the only score that can decide the tier — first, where a scan lands. Marking
the driver and the scored-but-not-weighted peaks turns `tier_derivation` from
a sentence into something visible on every record, including the case the
registry exists to surface: a dimension can be at its worst while the
weighting profile deliberately looks elsewhere. Reusing the existing tier
tones and marker family keeps the page one system (ADR-0009).
