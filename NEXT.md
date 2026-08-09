# Next

Working state for the theme-cloning work. **This file is the source of truth
for what's next** — keep it current, and prefer editing it over leaving
status in issue comments.

Branch: `draft/new-themes`. Tracking issue:
[flowershow/flowershow#1339](https://github.com/flowershow/flowershow/issues/1339).
Full method, measurements and gotchas:
[the plan doc](https://github.com/flowershow/flowershow/blob/main/docs/plans/2026-08-08-theme-cloning-fidelity-method.md).

## Now (in progress, unattended run 2026-08-09)

1. **Human fidelity review of the Material theme.** LLM-judged pass done
   this run (`fidelity: reviewed-close` in `docs/features.yaml`, screenshot
   comparison via the Chrome tool) — but that's not a substitute for your
   own look. Still open for a human.
   - Landing: https://material-landing-v2-rufuspollock.flowershow.me
   - Docs page: https://material-landing-demo-rufuspollock.flowershow.me/docs/kitchen-sink
   - Reference: https://squidfunk.github.io/mkdocs-material/

2. **code.storage clone** — DONE this pass. Ported Rufus's independent
   static repro (`tmp/code-storage.html` + `tmp/theme.css` +
   `tmp/example-text-page.html`) into `_repro/codestorage-landing.html`
   (self-contained) and re-measured `codestorage-draft/theme.css` against
   it (paler bg, lighter fg, line-height 1.6 not 2, semibold not bold
   headings, hover-only link underlines). Both demo sites republished,
   `verify.sh` passes.
   - Landing: https://codestorage-landing-demo-rufuspollock.flowershow.me
   - Docs page: https://codestorage-theme-demo-rufuspollock.flowershow.me/docs/kitchen-sink
   - Reference: https://code.storage/

## After that

3. **Authoring tutorial + AI cloning skill** — DONE this pass. Written to
   `docs/theme-authoring-tutorial.md` (prose) and
   `docs/ai-theme-cloning-skill.md` (agent-facing, `flowershow/skills`
   SKILL.md frontmatter shape so it ports directly if that ends up being
   the right home). Default call: parked in this repo's `docs/` rather than
   `flowershow/flowershow` or `flowershow/skills`, since it required no
   access outside this repo. Human can move it later — see "Open questions"
   below, still open.

4. **Structural / L4 decision.** DONE this pass — documented in
   [docs/l4-structural-decision.md](docs/l4-structural-decision.md).
   Default call: accept the fixed skeleton, document gaps honestly, no
   core-app changes made unsupervised (that's a `flowershow/flowershow`
   architecture decision, not this repo's to make speculatively).
   Slot/block ordering or full layout templating remain open for a human
   to pursue later — the doc lays out what evidence would justify each.

5. **Preview images** for both themes — DONE this pass, via
   `screenshotit.app` (above-the-fold capture of each landing demo,
   converted webp→png with `sips`). `verify.sh` no longer warns.

6. **`material-landing-demo` retired.** DONE this pass — `fl delete`d it.
   The staleness was Flowershow's own site-serving cache (not jsDelivr;
   `fl` confirmed uploaded files were current), so no fix was available from
   this repo. Superseded by `material-landing-v2`, which is current. See
   `docs/features.yaml` `landing_demo_url_retired`.

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
| [#1345](https://github.com/flowershow/flowershow/issues/1345) | raw `.html` pages 404 with any query string |
| [#1347](https://github.com/flowershow/flowershow/issues/1347) | `fl`-published raw-HTML page can serve stale content while `fl` reports all files current |
