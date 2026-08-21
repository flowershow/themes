# Next

Current state and next actions for Flowershow themes. Keep this concise; use
git history and [`docs/features.yaml`](docs/features.yaml) for detailed work
records.

Branch: `main` after integration. Readiness history and Material tracking:
[flowershow/flowershow#1367](https://github.com/flowershow/flowershow/issues/1367).

## Current state

- The August theme-cloning phase is complete and merged in
  [flowershow/themes#8](https://github.com/flowershow/themes/pull/8).
- Material and Monospace pass structural and live-demo verification. Rufus
  approved Monospace for promotion on 2026-08-21; it is now **Official** under
  the bare config value `monospace`. Material remains **Preview**.
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

1. Answer the concrete product-review questions in
   [#1369](https://github.com/flowershow/flowershow/issues/1369) for the
   [parallel themes site](https://flowershow-themes-preview-rufuspollock.flowershow.me):
   status clarity, theme choice, link correctness, mobile usability, content
   ownership, and its eventual relationship to the canonical Flowershow site.
2. Complete [#1370](https://github.com/flowershow/flowershow/issues/1370): grant
   Search entitlement to the Monospace and Material demos, then review the
   control, modal, results, no-results, focus, desktop/mobile, and light/dark
   surfaces. This is needed because Search is real themed UI but cannot render
   on the demos' current Free plan; absence is not evidence that it looks good.
3. Keep Material visibly **Preview** and use
   [#1367](https://github.com/flowershow/flowershow/issues/1367) for any future
   naming, integration, and explicit promotion decision.

The existing
[Flowershow themes reference](https://flowershow.app/docs/reference/themes)
remains canonical and now includes official Monospace. The parallel site is
still evaluated separately through #1369.

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
- Monospace: https://monospace-theme-demo-rufuspollock.flowershow.me

The detailed next-phase design is
[`docs/plans/2026-08-21-themes-next-phase-design.md`](docs/plans/2026-08-21-themes-next-phase-design.md).
