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
technical and documentation foundation plus a responsive/light-dark review
record for every currently rendered surface. Neither has a reviewed search
surface, approved final identity, or prepared integration/release changes. The
demo landing fixtures also need a copy/trademark/icon provenance decision before
they can become official release artifacts.

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
- **Theme source method:** `theme.css` values were measured from the rendered
  Material for MkDocs site and independently authored here. The inspiration is
  [MIT-licensed](https://github.com/squidfunk/mkdocs-material/blob/master/LICENSE).
- **Fonts:** the theme imports Roboto and Roboto Mono; the upstream
  [Roboto license is Apache-2.0](https://github.com/googlefonts/roboto-2/blob/main/LICENSE).
- **Hero illustration:** the landing fixture uses an original gradient
  placeholder rather than redistributing the reference site's parallax art.
- **Known gaps:** tabbed content, previous/next pagination, and a version
  selector remain documented core/out-of-scope differences.

### Completed review gates

- [x] Desktop and mobile visual review is explicitly recorded.
- [x] Light and dark visual review is explicitly recorded.
- [x] Home, kitchen sink, blog listing/post, navbar, sidebar, and landing
      surfaces are explicitly recorded as visually reviewed in the
      [visual review matrix](visual-review-matrix.md).

### Pending gates

- [ ] Search is explicitly visually reviewed once the preview site has the
      Flowershow Search feature entitlement and renders the search control.
- [ ] Landing-fixture marketing copy, brand/trademark use, SVG/icon provenance,
      and required attribution are reviewed; replace anything not cleared for
      an official release.
- [ ] Final public name and directory name are approved.
- [ ] Canonical Flowershow gallery and dashboard changes are prepared.
- [ ] Release metadata, purge coverage, version, and changelog are prepared.
- [ ] A human explicitly authorizes promotion and the release tag.

**Recommendation:** remain Preview. The responsive and mode matrix is complete;
the next useful actions are search-surface enablement and the landing-fixture
provenance review. Release engineering should wait for their results.

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
- **Theme source method:** the reference is a proprietary service, so values
  were measured from the public rendered site and `theme.css` was independently
  authored; no proprietary source code is included in the stylesheet.
- **Fonts:** commercial Berkeley Mono is not redistributed. The theme
  substitutes IBM Plex Mono, whose upstream project uses the
  [SIL Open Font License 1.1](https://github.com/IBM/plex/blob/master/LICENSE.txt).
- **Hero illustration:** the 3D reference art is replaced by an original
  gradient placeholder.
- **Preview-fixture boundary:** `demo-landing.md` deliberately reproduces
  reference brand names, marketing copy/navigation, and an SVG motif for
  fidelity evaluation. Those elements are not declared cleared for an official
  release and remain a gate below.
- **Known gaps:** the reference's bracketed page-copy navigation and bespoke
  3D/diagram content remain explicitly outside the CSS theme.

### Completed review gates

- [x] Desktop and mobile visual review is explicitly recorded.
- [x] Light and dark visual review is explicitly recorded.
- [x] Home, kitchen sink, blog listing/post, navbar, sidebar, and landing
      surfaces are explicitly recorded as visually reviewed in the
      [visual review matrix](visual-review-matrix.md).

### Pending gates

- [ ] Search is explicitly visually reviewed once the preview site has the
      Flowershow Search feature entitlement and renders the search control.
- [ ] Landing-fixture marketing copy, brand/trademark use, SVG/icon provenance,
      and required attribution are reviewed; replace anything not cleared for
      an official release.
- [ ] Final public name and directory name are approved.
- [ ] Canonical Flowershow gallery and dashboard changes are prepared.
- [ ] Release metadata, purge coverage, version, and changelog are prepared.
- [ ] A human explicitly authorizes promotion and the release tag.

**Recommendation:** remain Preview. The font and hero-art substitutions support
continued previewing; promotion still depends on search enablement, the
provenance review, and an explicit product/release decision.

## Promotion boundary

When a theme clears every pending gate, this record may recommend a **separate
promotion proposal**. It must not trigger a rename, dashboard/gallery edit,
release commit, or tag by itself. Follow the [maintainer checklist](/maintainers)
and record the approving decision in #1367.
