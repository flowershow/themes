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

## Now

1. Build and publish the parallel themes preview site from `site/`, with equal
   “choose a theme” and “build a theme” paths.
2. Publish the full human and AI authoring workflows through that site and add
   contributor/maintainer instructions.
3. Define and run the release-readiness checklist for Material and
   code.storage while keeping both visibly marked preview/beta.
4. Complete the semantic class reference tracked in
   [flowershow/flowershow#1338](https://github.com/flowershow/flowershow/issues/1338).

The existing
[Flowershow themes reference](https://flowershow.app/docs/reference/themes)
remains unchanged and canonical while the new site is evaluated.

## Separate follow-ups

- [#1348](https://github.com/flowershow/flowershow/issues/1348): fix the
  unstyled `.site-subnav-breadcrumb-link` base state in Flowershow core.
- L4 slot ordering/layout templating remains separate research; see
  [`docs/l4-structural-decision.md`](docs/l4-structural-decision.md).
- [#854](https://github.com/flowershow/flowershow/issues/854) remains the broad
  historical themes/customization epic and is not the implementation scope for
  this phase.

## Live preview themes

- Material: https://material-theme-demo-rufuspollock.flowershow.me
- code.storage: https://codestorage-theme-demo-rufuspollock.flowershow.me

The detailed next-phase design is
[`docs/plans/2026-08-21-themes-next-phase-design.md`](docs/plans/2026-08-21-themes-next-phase-design.md).
