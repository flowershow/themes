---
title: Theme release readiness
description: Promotion evidence for Monospace and remaining gates for Material.
---

This is the versioned readiness record for the themes tracked in
[flowershow/flowershow#1367](https://github.com/flowershow/flowershow/issues/1367),
a focused child of the [themes successor epic](https://github.com/flowershow/flowershow/issues/1364).
Passing repository checks does not promote a theme. A maintainer must review
the remaining visual and product decisions, and a human explicitly authorizes
promotion and any release tag.

## Current result

**Material: remain Preview. Monospace: Official.** Both have a solid technical
and documentation foundation plus a responsive/light-dark review record for
every currently rendered surface. Rufus approved the final Monospace name and
promotion on 2026-08-21. Search is still unavailable on the demo sites and is
tracked transparently in
[flowershow/flowershow#1370](https://github.com/flowershow/flowershow/issues/1370)
as a non-blocking visual-review follow-up.

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
- **Owned landing fixture:** the published page uses Flowershow-authored copy,
  CSS geometry, specimen cards and claims. It names Material for MkDocs only as
  open-source inspiration, links upstream, and retains the required notice. The
  [landing-fixture provenance audit](landing-fixture-provenance.md) records the
  removed badge, SVGs, testimonials and third-party name tiles.

### Completed review gates

- [x] Desktop and mobile visual review is explicitly recorded.
- [x] Light and dark visual review is explicitly recorded.
- [x] Home, kitchen sink, blog listing/post, navbar, sidebar, and landing
      surfaces are explicitly recorded as visually reviewed in the
      [visual review matrix](visual-review-matrix.md).
- [x] Landing-fixture copy, trademark presentation, SVG/icon provenance, and
      representations use the recorded Flowershow-owned specimen disposition.

### Pending gates

- [ ] Search is explicitly visually reviewed once the preview site has the
      Flowershow Search feature entitlement and renders the search control.
- [ ] Final public name and directory name are approved.
- [ ] Canonical Flowershow gallery and dashboard changes are prepared.
- [ ] Release metadata, purge coverage, version, and changelog are prepared.
- [ ] A human explicitly authorizes promotion and the release tag.

**Recommendation:** remain Preview. The landing provenance action and current
responsive/mode matrix are complete. Search enablement, naming, integration,
release preparation and explicit human authorization remain outstanding.

## Monospace

<div data-readiness-theme="monospace" data-recommendation="official"></div>

### Verified evidence

- **Human decision:** Rufus reviewed the finished Monospace homepage on
  2026-08-21, said it was good to advance beyond Preview, and approved the
  public name **Monospace** with the bare config value `monospace`.
- **Repository contract:** `monospace/theme.css` and `preview.png`
  exist; required tokens, brace balance, dark-mode declarations, and the
  preview asset pass `scripts/verify.sh`.
- **Live surfaces:** the [demo and canonical showcase](https://monospace-theme-demo-rufuspollock.flowershow.me/),
  kitchen sink, blog list, post, and `/landing` compatibility path pass
  HTTP/content smoke checks.
- **Theme source method:** the reference is a proprietary service, so values
  were measured from the public rendered site and `theme.css` was independently
  authored; no proprietary source code is included in the stylesheet.
- **Fonts:** commercial Berkeley Mono is not redistributed. The theme
  substitutes IBM Plex Mono, whose upstream project uses the
  [SIL Open Font License 1.1](https://github.com/IBM/plex/blob/master/LICENSE.txt).
- **Hero illustration:** the 3D reference art is replaced by an original
  CSS-authored node/orbit composition and soft geometric field.
- **Owned landing fixture:** the theme-local Flowershow showcase template plus
  `demo-showcase.json` supplies a restrained, real-content homepage with
  theme-owned, scoped presentation CSS. It contains no copied service identity, commercial
  claims, pricing, contacts, upstream navigation or unresolved SVG.
- **Known gaps:** the reference's bracketed page-copy navigation and bespoke
  3D/diagram content remain explicitly outside the CSS theme.
- **Fixture provenance audit:** no public content-reuse license was found for
  the earlier copied landing material, so it was replaced rather than merely
  attributed. The [landing-fixture provenance audit](landing-fixture-provenance.md)
  records the executed disposition.

### Completed review gates

- [x] Desktop and mobile visual review is explicitly recorded.
- [x] Light and dark visual review is explicitly recorded.
- [x] Home, kitchen sink, blog listing/post, navbar, sidebar, and landing
      surfaces are explicitly recorded as visually reviewed in the
      [visual review matrix](visual-review-matrix.md).
- [x] Landing-fixture identity, copy, claims, contacts, upstream links, and
      unresolved SVG use the recorded Flowershow-owned specimen disposition.

### Completed promotion gates

- [x] Final public name and directory name are approved as Monospace / monospace.
- [x] Themes gallery, canonical Flowershow gallery, and dashboard integration are prepared.
- [x] Rufus explicitly authorized promotion on 2026-08-21.

### Non-blocking follow-ups

- [ ] Search is visually reviewed after entitlement is enabled in flowershow/flowershow#1370.
- [ ] A versioned release tag and changelog are separately approved.

**Recommendation:** Official. The font, hero-art and landing-content
substitutions are approved, the stable identity is Monospace, and the bare
configuration value is `monospace`. This promotion does not create a version
tag; Search review continues separately because entitlement is unavailable.

## Promotion boundary

Material still requires a separate promotion decision. Monospace was explicitly
approved and promoted without creating a version tag. Future tags remain a
separate release action under the [maintainer checklist](/maintainers).
