---
title: Preview release readiness
description: Evidence and remaining gates for Material and code.storage.
---

This is the versioned readiness record for the two candidate themes tracked in
[flowershow/flowershow#1367](https://github.com/flowershow/flowershow/issues/1367),
a focused child of the [themes successor epic](https://github.com/flowershow/flowershow/issues/1364).
Passing repository checks does not promote a theme. A maintainer must review
the remaining visual and product decisions, and a human explicitly authorizes
promotion and any release tag.

## Current result

**Material: remain Preview. code.storage: remain Preview.** Both have a solid
technical and documentation foundation, but neither has the explicit
responsive/theme-mode/surface review record, approved final identity, or
prepared integration/release changes required for a promotion proposal.

Status meanings:

- **Verified** — backed by a linked artifact or a repeatable repository check.
- **Pending** — needs a recorded visual, product, integration, or release
  decision; absence is not treated as a pass.
- **Not applicable** — reviewed and deliberately excluded with a reason.

## Material

<div data-readiness-theme="material-draft" data-recommendation="remain-preview"></div>

### Verified evidence

- **Human fidelity:** Rufus reviewed the live preview on 2026-08-21 and said it
  looked okay; the decision is recorded in `docs/features.yaml` as
  `reviewed-close`.
- **Repository contract:** `material-draft/theme.css` and `preview.png` exist;
  required tokens, brace balance, dark-mode declarations, and the preview asset
  pass `scripts/verify.sh`.
- **Live surfaces:** the [demo](https://material-theme-demo-rufuspollock.flowershow.me)
  and [landing page](https://material-theme-demo-rufuspollock.flowershow.me/landing)
  pass HTTP/content smoke checks.
- **Source method:** CSS values were measured from the rendered Material for
  MkDocs site and independently authored here. The inspiration is
  [MIT-licensed](https://github.com/squidfunk/mkdocs-material/blob/master/LICENSE).
- **Fonts and art:** the theme imports Roboto and Roboto Mono; the upstream
  [Roboto license is Apache-2.0](https://github.com/googlefonts/roboto-2/blob/main/LICENSE).
  The shipped landing page uses an original gradient placeholder and does not
  redistribute the reference site's illustration.
- **Known gaps:** tabbed content, previous/next pagination, and a version
  selector remain documented core/out-of-scope differences.

### Pending gates

- [ ] Desktop and mobile visual review is explicitly recorded.
- [ ] Light and dark visual review is explicitly recorded.
- [ ] Kitchen sink, blog listing/post, navbar, sidebar, search, and landing
      surfaces are explicitly recorded as visually reviewed.
- [ ] Final public name and directory name are approved.
- [ ] Canonical Flowershow gallery and dashboard changes are prepared.
- [ ] Release metadata, purge coverage, version, and changelog are prepared.
- [ ] A human explicitly authorizes promotion and the release tag.

**Recommendation:** remain Preview. The next useful action is the explicit
visual review matrix; release engineering should wait for its result.

## code.storage

<div data-readiness-theme="codestorage-draft" data-recommendation="remain-preview"></div>

### Verified evidence

- **Human fidelity:** Rufus reviewed the live preview on 2026-08-21 and said it
  looked okay; the decision is recorded in `docs/features.yaml` as
  `reviewed-close`.
- **Repository contract:** `codestorage-draft/theme.css` and `preview.png`
  exist; required tokens, brace balance, dark-mode declarations, and the
  preview asset pass `scripts/verify.sh`.
- **Live surfaces:** the [demo](https://codestorage-theme-demo-rufuspollock.flowershow.me)
  and [landing page](https://codestorage-theme-demo-rufuspollock.flowershow.me/landing)
  pass HTTP/content smoke checks.
- **Source method:** the reference is a proprietary service, so values were
  measured from the public rendered site and the CSS was independently
  authored. No code, font, logo, or illustration from code.storage is shipped.
- **Fonts and art:** commercial Berkeley Mono is not redistributed. The theme
  substitutes IBM Plex Mono, whose upstream project uses the
  [SIL Open Font License 1.1](https://github.com/IBM/plex/blob/master/LICENSE.txt).
  Bespoke reference illustrations are replaced by an original gradient
  placeholder.
- **Known gaps:** the reference's bracketed page-copy navigation and bespoke
  3D/diagram content remain explicitly outside the CSS theme.

### Pending gates

- [ ] Desktop and mobile visual review is explicitly recorded.
- [ ] Light and dark visual review is explicitly recorded.
- [ ] Kitchen sink, blog listing/post, navbar, sidebar, search, and landing
      surfaces are explicitly recorded as visually reviewed.
- [ ] Final public name and directory name are approved.
- [ ] Canonical Flowershow gallery and dashboard changes are prepared.
- [ ] Release metadata, purge coverage, version, and changelog are prepared.
- [ ] A human explicitly authorizes promotion and the release tag.

**Recommendation:** remain Preview. The font/art substitution is acceptable for
continued previewing; promotion still depends on the visual review matrix and
an explicit product/release decision.

## Promotion boundary

When a theme clears every pending gate, this record may recommend a **separate
promotion proposal**. It must not trigger a rename, dashboard/gallery edit,
release commit, or tag by itself. Follow the [maintainer checklist](/maintainers)
and record the approving decision in #1367.
