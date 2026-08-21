---
title: Preview site status
description: What is official, what is experimental, and what comes next for Flowershow themes.
---

This site is an experiment in giving theme users and theme authors one coherent
home. Product evaluation is tracked in
[flowershow/flowershow#1369](https://github.com/flowershow/flowershow/issues/1369),
and Search review is tracked separately in
[flowershow/flowershow#1370](https://github.com/flowershow/flowershow/issues/1370).

Live preview: https://flowershow-themes-preview-rufuspollock.flowershow.me

## Current boundary

- The [Flowershow themes reference](https://flowershow.app/docs/reference/themes)
  remains canonical for now and is not being replaced in this phase.
- Letterpress, Superstack, LessFlowery, Leaf, and Monospace are **Official** themes.
- Material is a **Preview** theme.
- Monospace was inspired by code.storage and uses the bare config value
  `monospace`.
- Preview themes can be tried with a full CSS URL but are not available in the
  dashboard theme picker and have not been included in a tagged release.

## Completed foundation

The August theme-cloning phase built both previews, tested them against shared
content, published live demos, produced a human authoring tutorial and AI
workflow, and documented the structural ceiling of CSS-only theming. See the
completed [tracking issue](https://github.com/flowershow/flowershow/issues/1339)
and [themes pull request](https://github.com/flowershow/themes/pull/8).

The stable component, state, and variant hooks are now published in the
[semantic theme class reference](https://flowershow.app/docs/reference/theme-class-reference),
with automatic drift checking. That work closed
[#1338](https://github.com/flowershow/flowershow/issues/1338) in
[flowershow/flowershow#1366](https://github.com/flowershow/flowershow/pull/1366).

## Current work

- answer the concrete review questions in
  [#1369](https://github.com/flowershow/flowershow/issues/1369);
- make contribution and maintenance steps reproducible;
- complete the pending visual and product gates in the
  [release-readiness record](/readiness) for Material; and
- enable and visually verify Search through
  [#1370](https://github.com/flowershow/flowershow/issues/1370).

## Deferred decisions

- whether this site or the existing reference gallery becomes canonical;
- whether Material becomes official;
- whether a shared catalog should eventually drive the site, dashboard, and
  documentation;
- whether authoring guidance stays here or is generated elsewhere; and
- whether Flowershow should add L4 slot ordering or layout templating.

These are recorded decisions to revisit, not blockers for improving the
preview site.
