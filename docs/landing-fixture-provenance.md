---
title: Landing fixture provenance
description: Source evidence and release disposition for the Material and code.storage preview landing pages.
---

This audit separates the independently authored CSS themes from the marketing
fixtures used to compare their landing-page fidelity. It is a practical release
record, not legal advice. Both fixtures may remain available for preview
evaluation, but neither is cleared unchanged as an official Flowershow theme
landing page.

## Material

<div data-provenance-theme="material-draft" data-disposition="attribution-and-trademark-review"></div>

### Evidence

- The product name, repository identity, headline, feature headings and much of
  the feature copy in `material-draft/demo-landing.md` are adapted from the
  upstream [README](https://github.com/squidfunk/mkdocs-material/blob/master/README.md)
  and documentation sources.
- The upstream repository carries an
  [MIT License](https://github.com/squidfunk/mkdocs-material/blob/master/LICENSE).
  Its copyright notice and license text are now preserved in
  [Third-party notices](/third-party-notices).
- The fixture does not redistribute the upstream parallax illustration. It uses
  an original gradient placeholder.
- The inline SVG paths were created in this repository's earlier draft work,
  but no independent creation record or upstream icon mapping was preserved.
- The testimonial quotations are draft fixture text, not sourced testimonials.
  The industry-name tiles reproduce third-party names from upstream marketing.

### Disposition before an official release

Copyright attribution for the MIT-licensed source text is now present. Before
promotion, a maintainer must still do one of the following:

1. obtain/record approval for the product-name and trademark presentation,
   independently document or replace every inline SVG, and clearly label or
   replace draft testimonials and third-party name tiles; or
2. replace the fixture with Flowershow-authored copy, identity, icons and claims
   while retaining the Material-inspired layout as the visual demonstration.

This audit does not treat an open-source copyright license as a trademark or
endorsement grant.

## code.storage

<div data-provenance-theme="codestorage-draft" data-disposition="replace-before-release"></div>

### Evidence

- `codestorage-draft/demo-landing.md` reproduces the Code Storage and Pierre
  Computer Company names, marketing copy, product claims, pricing, SLA/security
  statements, API example identities, contact details and upstream navigation.
- The official [Code Storage terms](https://code.storage/legal/terms) state that
  the company retains its service and associated intellectual-property rights
  and grants only limited service-access rights to customers.
- No public content-reuse license was found for the landing-page copy, brand,
  logo/motif, or other marketing material.
- Berkeley Mono and the reference 3D artwork are not shipped. The preview uses
  IBM Plex Mono and an original CSS gradient placeholder instead.
- The inline network SVG and pill-label wording have no preserved independent
  provenance record beyond this repository's earlier fidelity draft.

### Disposition before an official release

Attribution alone is not treated as sufficient. Replace the company/product
identity, marketing and product claims, pricing/SLA/security statements,
contacts and upstream links with clearly Flowershow-authored demo material.
Replace the inline SVG and branded pill wording with repository-owned assets
and copy. Keep only the independently authored theme CSS, layout technique,
open-font substitution and original gradient treatment unless separate written
permission is recorded.

## Boundary

Completing these replacements would close the content/provenance gate only. It
would not approve a final theme name, canonical gallery/dashboard integration,
release metadata, or a release tag. Both themes remain **Preview** until every
readiness gate and the explicit human-promotion decision are complete.
