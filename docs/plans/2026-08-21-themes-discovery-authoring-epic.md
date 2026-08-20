## Outcome

Make Flowershow themes equally easy to **choose** and to **build**.

This succeeds the completed August theme-cloning phase tracked in
[#1339](https://github.com/flowershow/flowershow/issues/1339). That work built
and verified two new preview themes, produced human and AI authoring guidance,
and documented the boundary between theme CSS and core layout structure. The
implementation landed in
[flowershow/themes#8](https://github.com/flowershow/themes/pull/8).

The next phase turns those results into a coherent discovery, contribution,
maintenance, and eventual release experience.

## Workstreams

### 1. Themes preview site

Build a deployable Flowershow site from `flowershow/themes/site/` with two
equally prominent paths:

- choose and preview a theme;
- build or contribute a theme.

The gallery will show the four official themes plus Material and code.storage,
clearly labeled **Preview**. The current
[Flowershow themes reference](https://flowershow.app/docs/reference/themes)
remains unchanged and canonical while this parallel site is evaluated.

### 2. Theme authoring hub

Publish the full human theme-authoring guide and AI theme-cloning workflow as
browsable pages. Add contributor and maintainer instructions covering the
complete path from a new `theme.css` through preview, review, listing, and
release.

The existing source material is in:

- [theme-authoring tutorial](https://github.com/flowershow/themes/blob/main/docs/theme-authoring-tutorial.md)
- [AI theme-cloning workflow](https://github.com/flowershow/themes/blob/main/docs/ai-theme-cloning-skill.md)

### 3. Preview-theme readiness

Keep Material and code.storage in preview/beta status while making them easy to
try. Define and run a readiness checklist covering fidelity, responsive and
light/dark review, licensing, naming, demo health, assets, documentation,
dashboard integration, gallery integration, and release metadata.

Passing the checklist makes a theme eligible for a later explicit promotion
decision; it does not automatically publish a release.

### 4. Flowershow integration

Document the changes required when a preview becomes official: dashboard
selector, galleries, documentation, release metadata, and jsDelivr tagging.
Do not change `/docs/reference/themes` during the preview-site phase.

### 5. Theme-author API documentation

Keep [#1338](https://github.com/flowershow/flowershow/issues/1338) as a
separate near-term child issue. The semantic CSS classes are the principal
authoring API beyond tokens, so the authoring path is not complete until that
reference is published and protected against drift.

## Acceptance criteria

- [ ] `flowershow/themes/site/` builds and deploys through a documented command.
- [ ] The live preview has equally clear “Choose a theme” and “Build a theme” paths.
- [ ] All four official themes and both preview themes have accurate status,
      imagery, demo links, and configuration guidance.
- [ ] Human and AI authoring guides are readable on the published site without
      maintaining divergent source copies.
- [ ] Contributor instructions cover creation, verification, demo publishing,
      fidelity records, assets, and pull-request review.
- [ ] Demo-site source/configuration and ownership are discoverable, resolving
      the documentation gap tracked in #916.
- [ ] Maintainer instructions cover preview, promotion, dashboard/gallery
      updates, release metadata, and the explicit tag/release gate.
- [ ] Material and code.storage remain visibly marked preview/beta.
- [ ] #1338 is completed or has a concrete implementation path linked here.
- [ ] The historical #854 epic receives a bounded triage, without importing
      unrelated implementation into this issue.
- [ ] Existing theme and site verification passes, including live smoke checks.

## Related and predecessor issues

- [#1339](https://github.com/flowershow/flowershow/issues/1339) — completed
  theme-cloning and authoring-method phase
- [#1337](https://github.com/flowershow/flowershow/issues/1337) — current
  Flowershow themes gallery
- [#1338](https://github.com/flowershow/flowershow/issues/1338) — semantic CSS
  class reference
- [#854](https://github.com/flowershow/flowershow/issues/854) — broad historical
  themes/customization epic
- [#916](https://github.com/flowershow/flowershow/issues/916) — where theme demo
  sites and their configuration live; directly addressed by the site and
  maintainer-guide workstream
- [#1348](https://github.com/flowershow/flowershow/issues/1348) — separate
  breadcrumb-link core defect
- [Approved design](https://github.com/flowershow/themes/blob/main/docs/plans/2026-08-21-themes-next-phase-design.md)

## Non-goals

- No L4 slot ordering, component-tree customization, or layout templating.
- No decision yet to replace `/docs/reference/themes` with the new site.
- No official release, directory rename, dashboard listing, or release tag for
  Material or code.storage without a later explicit decision.
- No broad implementation sweep of #854.
- No work on #1348 in this epic.
