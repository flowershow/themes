# Next

Current state and next actions for Flowershow themes. Keep this concise; use
git history and [`docs/features.yaml`](docs/features.yaml) for detailed work
records.

Branch: `main` after integration. Current tracking home:
[flowershow/flowershow#1364](https://github.com/flowershow/flowershow/issues/1364).

## Current state

- The August theme-cloning phase is complete and merged in
  [flowershow/themes#8](https://github.com/flowershow/themes/pull/8).
- Material and code.storage pass structural and live-demo verification. Rufus
  completed the human fidelity review on 2026-08-21 and reported both looked
  okay. They remain **preview/beta**, not released themes.
- The deployed fix for flowershow/flowershow#1349 was checked and works.
- The human authoring tutorial and AI theme-cloning workflow currently live in
  [`docs/`](docs/).
- Theme demos now have a canonical standard-route and content-quality
  inventory in
  [`docs/demo-site-content.md`](docs/demo-site-content.md). The Monospace
  preview is the first theme-specific real-content homepage; other homepages
  remain unchanged until several good examples reveal what is genuinely common.
- The parallel themes discovery and authoring site is live at
  https://flowershow-themes-preview-rufuspollock.flowershow.me with all six
  themes, full authoring guides, and contributor/maintainer workflows.
- The generated
  [semantic theme class reference](https://flowershow.app/docs/reference/theme-class-reference)
  shipped in [flowershow/flowershow#1366](https://github.com/flowershow/flowershow/pull/1366),
  closing #1338 with 228 stable semantic hooks and drift checking.

## Now

1. Evaluate and iterate on the parallel preview site without changing the
   canonical Flowershow reference gallery yet.
2. Enable and review the currently unavailable search surface when entitlement
   is available. The Flowershow-owned landing-fixture dispositions are complete;
   keep both candidates visibly marked preview/beta while final naming,
   integration, and release decisions remain open.
3. Use the checklist evidence to decide whether either preview is ready for a
   separate promotion proposal; do not rename, list, or release either theme
   without that explicit decision.

The existing
[Flowershow themes reference](https://flowershow.app/docs/reference/themes)
remains unchanged and canonical while the new site is evaluated.

## Separate follow-ups

- [#1348](https://github.com/flowershow/flowershow/issues/1348): fix the
  unstyled `.site-subnav-breadcrumb-link` base state in Flowershow core.
- [#1343](https://github.com/flowershow/flowershow/issues/1343): fix the
  malformed `.is-linked` author hook and semantic-markup leaks in core.
- L4 slot ordering/layout templating remains separate research; see
  [`docs/l4-structural-decision.md`](docs/l4-structural-decision.md).
- [#854](https://github.com/flowershow/flowershow/issues/854) remains the broad
  historical themes/customization epic and is not the implementation scope for
  this phase.

## Live preview themes

- Themes discovery and authoring site:
  https://flowershow-themes-preview-rufuspollock.flowershow.me
- Material: https://material-theme-demo-rufuspollock.flowershow.me
- code.storage: https://codestorage-theme-demo-rufuspollock.flowershow.me

The detailed next-phase design is
[`docs/plans/2026-08-21-themes-next-phase-design.md`](docs/plans/2026-08-21-themes-next-phase-design.md).
