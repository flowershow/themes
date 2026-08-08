# Next

Working state for the theme-cloning work. **This file is the source of truth
for what's next** — keep it current, and prefer editing it over leaving
status in issue comments.

Branch: `draft/new-themes`. Tracking issue:
[flowershow/flowershow#1339](https://github.com/flowershow/flowershow/issues/1339).
Full method, measurements and gotchas:
[the plan doc](https://github.com/flowershow/flowershow/blob/main/docs/plans/2026-08-08-theme-cloning-fidelity-method.md).

## Now

1. **Human fidelity review of the Material theme.** `fidelity` is
   `unreviewed` in `docs/features.yaml` and deliberately not self-graded.
   Both surfaces match the reference numerically; whether they *read* as
   Material is a human call.
   - Landing: https://material-landing-v2-rufuspollock.flowershow.me
   - Docs page: https://material-landing-demo-rufuspollock.flowershow.me/docs/kitchen-sink
   - Reference: https://squidfunk.github.io/mkdocs-material/

2. **code.storage clone** — tracked in
   [#1344](https://github.com/flowershow/flowershow/issues/1344). Rufus is
   iterating separately and will bring files over. Drop them in
   `codestorage-draft/` and `_repro/`, then:
   ```sh
   scripts/demo-site.sh codestorage-draft --landing _repro/<file>.html
   ```
   Simpler target than Material — near-monochrome, one font, no illustration
   system.

## After that

3. **Authoring tutorial + AI cloning skill**, written from what actually
   broke. The gotchas list in the plan doc is the spine; "compare
   numerically, not by eye" is the core method. Open: does this live here, in
   the main docs, or in `flowershow/skills`?

4. **Structural / L4 decision.** Confirmed unclonable without core changes:
   content tabs (no component), prev/next page pagination, version selector.
   Unresolved: accept the fixed skeleton and document it honestly, add
   slot/block ordering, or go to full layout templating.

5. **Preview images** for both themes — `verify.sh` warns; required before
   promoting out of draft.

6. **Fix or retire `material-landing-demo`.** Its `index.html` is stuck on an
   old CDN copy. `fl` reports all files current and a freshly-named site
   (`material-landing-v2`) picked up new markup immediately, so the upload is
   fine — it's purely cache.

## Not blockers (previously mis-called)

- **Artwork.** mkdocs-material's parallax illustration is bespoke and can't
  ship, so an original replacement is eventually needed — but it was *not*
  what made the landing read as not-Material. Typographic precision was.
  Don't treat it as gating.

## Open questions for a human

- Where do the tutorial and AI skill live? (see 3)
- Which L4 direction? (see 4)
- Should theme work be tracked in this repo's issues rather than
  `flowershow/flowershow`? Everything is currently filed there (#1337, #1338,
  #1339, #1340–#1344) because this repo doesn't use issues.

## Filed from this work

| Issue | |
| --- | --- |
| [#1337](https://github.com/flowershow/flowershow/issues/1337) | themes gallery / feature page |
| [#1338](https://github.com/flowershow/flowershow/issues/1338) | publish the semantic CSS class list |
| [#1340](https://github.com/flowershow/flowershow/issues/1340) | leaf theme uses dashboard-only tokens |
| [#1341](https://github.com/flowershow/flowershow/issues/1341) | `--navbar-height` never read |
| [#1342](https://github.com/flowershow/flowershow/issues/1342) | forced inline-code backticks need `!important` |
| [#1343](https://github.com/flowershow/flowershow/issues/1343) | `.is-linked` dot bug, Tailwind leak, unstyled classes |
| [#1344](https://github.com/flowershow/flowershow/issues/1344) | code.storage theme |
