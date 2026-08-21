# Reusable theme showcase and standard demo-site content

**Date:** 2026-08-21  
**Status:** Approved direction; implementation specification  
**Initial adopter:** `codestorage-draft` (publicly described as the Monospace preview)

## Outcome

Turn a theme demo into an attractive example of a real Flowershow site, not an
internal release report. Establish one reusable Flowershow product story and a
clear standard-page inventory for new themes and meaningful updates to existing
themes.

The first implementation applies the pattern to the Monospace preview. It does
not migrate Material or the four official theme demos, promote a preview theme,
rename a theme directory, or change the canonical Flowershow theme gallery.

## Why the current page needs to change

The current Monospace landing is useful evidence but weak public content. It
leads with terms such as “specimen,” “review matrix,” and “release boundary.” It
also creates a second, artificial bracketed navigation bar below Flowershow's
real site navbar. That makes the page read like a QA artifact and duplicates
the site's navigation hierarchy.

Evidence remains important, but it already has a better home in the readiness,
visual-review, and provenance documents. The public demo should sell the value
of Flowershow and show what the theme feels like on credible content.

## Chosen approach

Use a shared semantic landing template plus small per-theme metadata and
theme-owned presentation CSS.

This is preferable to either copying the full flowershow.app homepage into
every theme (high visual fidelity but immediate content drift) or using a plain
generic Markdown page (easy to maintain but too weak as a theme showcase).

The shared template owns the durable Flowershow story and section structure.
Each theme owns only its identity, short aesthetic description, and visual
interpretation. A renderer assembles the published homepage. This makes content
provenance and maintenance explicit without forcing every theme to look alike.

## Published information architecture

Every new or substantially updated theme demo should contain these pages:

| Route | Purpose | Canonical source |
| --- | --- | --- |
| `/` | Attractive Flowershow product introduction rendered in the candidate theme | shared showcase template + per-theme metadata + theme landing CSS |
| `/docs/kitchen-sink` | Complete Markdown/component stress test | `_demo-content/docs/kitchen-sink.md` |
| `/blog` | Blog listing and repeated-card/list treatment | `_demo-content/blog/index.mdx` and sibling posts |
| `/blog/first-post` | Representative long-form post | `_demo-content/blog/first-post.md` |
| navbar/footer | Real site navigation, mode control, repository link, and Flowershow CTA | `_demo-content/config.base.json`, overlaid with the validated theme name and source URL by the demo builder |

The old `/landing` page is not part of the new standard. During the initial
migration the renderer publishes the same generated source at `/` and
`/landing` so recorded links keep working. The ledger records `/` as the new
landing URL. Removing the compatibility copy is a later cleanup after inbound
links are checked. There must never be two competing navigation bars on a page.

Search remains configured as a review surface but must not be described as
reviewed until the demo has the required entitlement and renders the control.

## Shared homepage content

The shared template should use Flowershow-authored copy derived from the
current product positioning, not copy the full homepage markup, imagery,
customer material, badges, testimonials, or conversion experiments.

The page has six concise sections:

1. **Theme-aware hero**
   - Preview label and theme name.
   - A short theme-specific headline and aesthetic description.
   - General promise: turn Markdown into a live, hosted website without a
     build pipeline or CMS setup.
   - Primary action: “Explore the kitchen sink.”
   - Secondary action: “Publish with Flowershow.”

2. **What can be published**
   - Documentation, blogs, wikis/knowledge bases, and digital gardens.
   - These are credible content examples, not fictional customers.

3. **Why Flowershow**
   - Markdown-native.
   - Fast hosted publishing.
   - Portable, user-owned source files.
   - Themes and ordinary CSS.

4. **How it works**
   - Write or collect Markdown.
   - Publish from the supported Flowershow workflow.
   - Share the resulting site and keep editing the source files.

5. **About this theme**
   - Theme-specific name, visual character, font choices, and light/dark
     behavior.
   - Links to the blog and component specimen.
   - A visible but restrained Preview status. No release checklist prose.

6. **Final Flowershow call to action**
   - A short product reminder and links to publish, inspect the theme source,
     and browse the themes preview site.

The initial Monospace headline is “A sharper home for your Markdown.” Its
description is “A compact monospace theme for docs, notes, blogs, and technical
publishing.” Neither the former code.storage nor Pierre identity appears.

## Navigation and identity

The only top-level navigation is Flowershow's real site navbar. For the initial
demo it should:

- show the Flowershow mark and “Flowershow” title on one visual baseline;
- link to Home, Kitchen Sink, Blog, and the theme repository;
- retain the real light/dark control;
- use a “Publish with Flowershow” call to action;
- remain usable without a second landing-page `<header>` or `<nav>`.

Theme identity belongs in the hero, not in a duplicate application header.
Landing CSS may style the real semantic navbar classes, but landing-only rules
must remain scoped and must not damage the kitchen sink or blog navigation.

## Source architecture

Add the following small, explicit units:

- `_demo-content/theme-showcase.template.md`
  - canonical section order, shared Flowershow copy, accessible semantic markup,
    internal demo links, and stable class hooks;
  - no remote imagery, embedded third-party assets, testimonials, pricing, or
    theme-specific brands.
- `THEME-DIR/demo-showcase.json`
  - schema version `1` and the required string values `name`, `slug`, `status`,
    `headline`, `description`, `wrapperClass`, and `sourceUrl`;
  - `status` accepts only `preview` or `official`; `slug` and `wrapperClass`
    accept only lowercase ASCII identifier forms; `sourceUrl` must be an HTTPS
    URL under `github.com/flowershow/themes`;
  - no arbitrary executable markup.
- `scripts/render-theme-showcase.py`
  - validates the metadata and replaces only the template's documented fields;
  - fails on missing fields, unknown placeholders, unsafe wrapper values, or an
    unsupported status;
  - writes the assembled `index.md` only inside the temporary demo build.
- `THEME-DIR/demo-landing.css`
  - the theme's visual interpretation of the shared semantic page;
  - scoped beneath the declared wrapper class;
  - ordinary CSS-owned decorative geometry only.

`scripts/demo-site.sh` should automatically render the shared homepage when a
theme contains `demo-showcase.json`. Themes without metadata retain the current
shared `_demo-content/index.md` fallback until explicitly migrated. The existing
`--landing-page` option remains an escape hatch for exceptional research or
legacy pages, not the standard authoring path.

For an opted-in theme the builder also overlays the generated config with
`nav.title: "Flowershow"`, a Home/Kitchen Sink/Blog/Theme Source link set, and a
`Publish with Flowershow` CTA to `https://flowershow.app/publish`. The theme name
appears in the document title and hero rather than forming a second navbar.

This opt-in migration avoids silently changing every published demo while
making the intended future path unambiguous.

## Initial Monospace presentation

Reuse the strongest original visual ingredients from the current Flowershow-
owned page:

- compact IBM Plex Mono typography;
- the CSS-authored node mark and soft geometric hero field;
- bracket-like microcopy, restrained rules, and technical labels;
- clear light and dark treatments;
- generous editorial spacing despite the compact type scale.

Remove the artificial `.cs-header`, the large review matrix, release-boundary
section, provenance explanation, configuration dump, and maintainer-oriented
copy. Replace them with the shared product sections. The Flowershow badge or
mark in the hero must align with its surrounding content rather than float at
an unrelated vertical level.

The result should feel like a polished technical publishing homepage that
happens to be useful for theme evaluation.

## Documentation standard

Add `docs/demo-site-content.md` as the canonical human-readable inventory of
demo routes and source ownership. It must explain:

- which routes every theme demo is expected to publish;
- the exact repository source for each route;
- which content is shared and which fields/styles are theme-specific;
- how to create `demo-showcase.json` for a new theme;
- how to refresh an old theme without copying another theme's page;
- how to publish and verify a demo;
- where Preview/readiness/provenance evidence belongs instead of placing it in
  marketing copy;
- how exceptional `--landing-page` fixtures differ from the standard homepage.

Update and link this canonical document from:

- `docs/theme-authoring-tutorial.md` — human theme creation and update path;
- `docs/ai-theme-cloning-skill.md` — mandatory AI workflow and content-source
  constraints;
- `site/contributing.md` — contributor checklist;
- `site/maintainers.md` — review, refresh, publishing, and migration procedure;
- `scripts/demo-site.sh` usage comments — operational source of truth.

The AI guide must explicitly prohibit inventing customer claims, copying the
reference site's marketing identity, or importing its images/logos into a demo
homepage. Inspiration may guide the theme CSS; the shared Flowershow template
supplies the page's product content.

## Verification

Automated checks should prove:

- the metadata schema is complete and rejects invalid input;
- all template placeholders are resolved;
- the rendered homepage contains exactly one `h1` and uses nested headings;
- the rendered page contains the Preview marker and required Flowershow copy;
- it links to `/docs/kitchen-sink`, `/blog`, the theme source, and the real
  Flowershow publishing destination;
- the landing source contains no second `<header>` or `<nav>`;
- shared routes return HTTP 200 on the published demo;
- landing CSS is brace-balanced, scoped, and contains no remote/data-image
  assets;
- the canonical page inventory remains present in all four documentation
  surfaces listed above.

Visual review covers the homepage at desktop/mobile and light/dark, plus a
regression check that the same custom CSS does not break the kitchen sink or
blog. It records evidence without implying release approval.

## Rollout and boundaries

1. Build and verify the reusable renderer and documentation.
2. Migrate only `codestorage-draft` to the standard homepage.
3. Publish the Monospace demo from a review branch and inspect all four landing
   combinations plus representative internal pages.
4. Merge and republish from the exact `main` commit.
5. Evaluate the pattern before migrating Material or official themes.

Both `codestorage-draft` and `material-draft` remain Preview. Search review,
final naming, canonical gallery/dashboard integration, release metadata, and
explicit promotion authorization remain separate readiness gates.

## Acceptance criteria

- The Monospace demo homepage is attractive public-facing Flowershow content,
  not a release-audit report.
- It uses only the real Flowershow navbar, with aligned identity and working
  navigation.
- Shared Flowershow messaging has one canonical template and documented
  ownership.
- Theme-specific text is small, validated metadata; visual expression remains
  theme-owned CSS.
- New-theme and old-theme-update procedures clearly enumerate standard pages,
  canonical sources, publishing commands, and verification.
- Human, AI, contributor, and maintainer docs all point to the canonical
  inventory.
- Existing component/blog fixtures remain shared and unchanged.
- Automated and visual checks pass while the theme remains visibly Preview.
