# Next

Working state for the theme-cloning work. **This file is the source of truth
for what's next** — keep it concise: current state and next actions, not a
log of everything that's been done (see git history / `docs/features.yaml`
`fidelity_notes` for that).

Branch: `draft/new-themes`. Tracking issue:
[flowershow/flowershow#1339](https://github.com/flowershow/flowershow/issues/1339).
Full method, measurements and gotchas:
[the plan doc](https://github.com/flowershow/flowershow/blob/main/docs/plans/2026-08-08-theme-cloning-fidelity-method.md)
and [docs/theme-authoring-tutorial.md](docs/theme-authoring-tutorial.md).

## Now

1. **Human fidelity review of both draft themes.** Both `fidelity:
   unreviewed` in `docs/features.yaml` — deliberately not self-graded.
   - Material: https://material-theme-demo-rufuspollock.flowershow.me
     (`/landing` + `/docs/kitchen-sink`) vs. https://squidfunk.github.io/mkdocs-material/
   - code.storage: https://codestorage-theme-demo-rufuspollock.flowershow.me
     (`/landing` + `/docs/kitchen-sink`) vs. https://code.storage/

2. **Verify flowershow/flowershow#1349 fix once deployed.** Pushed straight
   to `main` (c2ddbf23) — check the "More" navbar dropdown on
   `material-theme-demo` renders white (matching other nav links) instead
   of dark.

3. **#1348 still open** (`.site-subnav-breadcrumb-link` unstyled, browser
   default blue/underline) — filed, not fixed. Same core-not-theme call as
   #1349.

## Open questions for a human

- Where do the authoring tutorial and AI skill actually live long-term —
  this repo's `docs/`, main `flowershow/flowershow` docs, or
  `flowershow/skills`? Currently parked here (`docs/theme-authoring-tutorial.md`,
  `docs/ai-theme-cloning-skill.md`) since writing them needed no access
  outside this repo.
- L4 (structural ceiling — content tabs, prev/next pagination, version
  selector): default call was "accept it, document it" — see
  [docs/l4-structural-decision.md](docs/l4-structural-decision.md). Slot
  ordering / full layout templating remain open if a human wants to
  pursue either.
- Should theme work move to this repo's own issues instead of
  `flowershow/flowershow`'s? Everything is filed there today (see below)
  because this repo doesn't use issues yet.

## Filed from this work

| Issue | | Status |
| --- | --- | --- |
| [#1337](https://github.com/flowershow/flowershow/issues/1337) | themes gallery / feature page | open |
| [#1338](https://github.com/flowershow/flowershow/issues/1338) | publish the semantic CSS class list | open |
| [#1340](https://github.com/flowershow/flowershow/issues/1340) | leaf theme uses dashboard-only tokens | open |
| [#1341](https://github.com/flowershow/flowershow/issues/1341) | `--navbar-height` never read | open |
| [#1342](https://github.com/flowershow/flowershow/issues/1342) | forced inline-code backticks need `!important` | open |
| [#1343](https://github.com/flowershow/flowershow/issues/1343) | `.is-linked` dot bug, Tailwind leak, unstyled classes | open |
| [#1344](https://github.com/flowershow/flowershow/issues/1344) | code.storage theme | open |
| [#1345](https://github.com/flowershow/flowershow/issues/1345) | raw `.html` pages 404 with any query string | open |
| [#1347](https://github.com/flowershow/flowershow/issues/1347) | `fl`-published raw-HTML page can serve stale content | open |
| [#1348](https://github.com/flowershow/flowershow/issues/1348) | `.site-subnav-breadcrumb-link` has no base style | open |
| [#1349](https://github.com/flowershow/flowershow/issues/1349) | navbar dropdown trigger doesn't track link color | **fixed on main, pending deploy verification (see item 2 above)** |
