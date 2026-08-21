# Flowershow-owned preview landing fixtures

Date: 2026-08-21  
Status: approved design  
Tracking: [flowershow/flowershow#1367](https://github.com/flowershow/flowershow/issues/1367)

## Outcome

Replace the two preview landing pages' borrowed or ambiguous marketing material
with useful Flowershow-owned theme specimens. Preserve each theme's visual
language and content density, but make the pages clearly demonstrations rather
than replicas or real product offers.

Material and code.storage remain **Preview**. This work closes only the recorded
landing-fixture content/provenance actions. It does not approve final names,
change the canonical Flowershow gallery or dashboard, prepare a release tag, or
authorize promotion. Search review remains deferred until the demo sites receive
the required Flowershow Search entitlement.

## Chosen approach

Use **theme-specimen pages**, not minimal placeholders or invented products.

- A minimal page would be legally simple but would no longer test the visual
  systems under realistic content density.
- A fictional product would preserve density but replace one set of questionable
  claims with another and would be less useful to theme authors.
- A theme specimen can truthfully explain what the preview demonstrates while
  exercising headings, body copy, lists, code, cards, calls to action, links,
  responsive composition, and light/dark presentation.

Both pages will use only repository-authored copy, CSS, and geometric decoration.
Links will point to real pages in the demo, the themes preview hub, Flowershow
documentation, or the `flowershow/themes` repository.

## Shared content boundary

Each page must:

- visibly say that it is a preview theme specimen;
- identify its inspiration without presenting itself as the upstream product;
- use Flowershow-owned factual copy about the specimen and authoring workflow;
- avoid commercial performance, pricing, uptime, security, customer, or
  testimonial claims;
- avoid third-party company names, personal contacts, upstream account data,
  and upstream navigation masquerading as local navigation;
- avoid SVG paths or images without a preserved repository provenance record;
- preserve useful links to `/`, `/kitchen-sink`, and `/blog`, plus relevant
  Flowershow authoring or repository pages;
- remain structurally rich enough to exercise the existing responsive layouts.

The stage-1 files under `_repro/` remain historical, unpublished comparison
artifacts and are not changed by this work. The published `demo-landing.md`
files are the release artifacts governed by this design.

## Material-inspired specimen

### Identity and copy

The page identity becomes **Flowershow — Material-inspired preview**. It will
state plainly that the layout is inspired by Material for MkDocs and link to the
upstream open-source project and the local third-party notice. It will not reuse
the upstream product headline, repository badge/statistics, feature marketing,
customer-name tiles, fabricated testimonials, or sponsorship pitch.

The hero introduces a bright, structured Flowershow documentation theme. The
body becomes a tour of real specimen surfaces:

1. readable Markdown and navigation;
2. responsive desktop/mobile composition;
3. light/dark presentation;
4. theme tokens and semantic classes;
5. links to the kitchen sink, blog, authoring guide, and theme repository;
6. an explicit preview and inspiration note.

The page should feel polished and welcoming, not like a compliance notice. The
attribution belongs in a concise inspiration block and footer.

### Visual treatment

Keep the current color system, typography, large gradient hero, alternating
dark/light sections, grid rhythm, spotlight rows, and button treatment. Replace
all inline SVG icons with repository-authored CSS geometry, numbered markers,
or typographic symbols. Replace company/testimonial grids with specimen cards
and review-state cards. No upstream illustration or logo is introduced.

## Monospace specimen

### Identity and copy

The published page no longer uses the Code Storage or Pierre Computer Company
identity. Its visible identity becomes **Flowershow Theme Lab — Monospace
specimen**. The provenance record may still name code.storage as visual
inspiration, but the page itself will say only that its terminal-like layout is
inspiration-led and independently authored.

The hero describes a technical, monospace Flowershow theme for Markdown sites.
The current product sections map to truthful specimen sections:

1. **Surfaces** — home, kitchen sink, blog list, and post;
2. **Review matrix** — desktop/mobile and light/dark coverage;
3. **Theme ingredients** — tokens, semantic classes, and CSS-only layout;
4. **Configuration** — a real Flowershow theme configuration example and an
   ASCII support matrix instead of pricing;
5. **Release boundary** — Preview status and the remaining search/naming/release
   gates instead of security claims;
6. **About this specimen** — repository ownership, open-font substitution, and
   contribution links instead of company biography and contacts.

All login, signup, pricing, SLA/status, support email, legal, social, and
upstream account links are removed. Navigation uses real demo and Flowershow
destinations.

### Visual treatment

Keep the narrow monospace scale, pale background, bracketed navigation, hero
grid, code block, long-form sections, ASCII tables, and existing original
gradient blob. Remove the unresolved inline network SVG. Replace it with an
`aria-hidden` HTML/CSS node mark whose circles and connectors are drawn entirely
with CSS. Replace the two upstream-derived pill labels with specimen labels such
as `CSS-ONLY THEME` and `PREVIEW / NOT RELEASED`.

## Verification and evidence

Repository verification will enforce the content boundary instead of relying on
memory:

- require a structured ownership/status marker in each landing page;
- require the new identities, inspiration disclosure, internal demo links, and
  repository-owned visual markers;
- reject the known upstream product/company identities, contacts, claims,
  customer/testimonial text, upstream URLs, and unresolved inline SVGs from the
  published landing files;
- keep existing structural, theme, assembled-site, and live smoke checks;
- update the provenance audit to record the executed replacements while
  retaining the Material inspiration and MIT notice;
- update the readiness record and feature ledger without changing
  `readiness: remain-preview`;
- publish both branch previews and capture a focused eight-render landing matrix:
  two themes × desktop/mobile × light/dark;
- after review, merge through a pull request, republish exact merged `main`, and
  run the full live verifier again.

The landing review must confirm that every requested mode is active, document
width equals viewport width, content remains legible, real links are present,
and neither page is easily mistaken for the upstream product.

## Failure handling

If content removal breaks layout, adjust only the landing-specific HTML/CSS;
do not weaken the provenance checks or edit the shared theme CSS unless a test
demonstrates a theme-level defect. If a live publish serves stale CSS, follow the
existing SHA-pinned demo workflow rather than adding cache workarounds. Three
identical verification failures trigger the repository stop rule.

## Acceptance criteria

- Both published landing pages use Flowershow-owned copy and visuals.
- Material is clearly described as inspired by, not identical to, Material for
  MkDocs; its upstream link and notice remain available.
- The monospace page contains no Code Storage/Pierre identity, commercial
  claims, contacts, upstream navigation, or unresolved SVG.
- Both pages retain a polished, content-rich visual demonstration.
- Automated checks prevent the removed material from silently returning.
- The focused eight-render landing review is recorded and passes.
- Full local and live verification passes from exact merged `main`.
- Both themes remain visibly labeled **Preview** and no canonical gallery,
  dashboard, rename, release, or tag action occurs.
