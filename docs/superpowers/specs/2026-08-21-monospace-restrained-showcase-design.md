# Restrained Monospace showcase design

## Outcome

Correct the Monospace demo homepage so it feels like the Monospace theme and
the earlier code.storage-inspired specimen rather than a generic marketing
template. Keep Flowershow-owned content, the real Flowershow navbar, the
two-column opening, and the standard demo routes. Change only Monospace in
this phase; do not impose its homepage structure on other themes.

## Root cause

The reusable showcase migration preserved the two-column hero but replaced the
previous compact document typography with display-scale headings, large
vertical sections, card grids, a dark promotional panel, and oversized calls
to action. Those rules overrode the theme's restrained 13–17px typographic
system and made the page read like a conventional startup landing page.

The code.storage reference is useful only as visual inspiration: it uses a
small heading hierarchy, literal technical content, lists, code, tables, and a
mostly linear text flow. Its identity, copy, claims, imagery, logos, and assets
must not be copied.

## Page structure

The Monospace showcase remains one generated semantic HTML document, but its
structure becomes deliberately plain and lives with the Monospace theme.

1. The real Flowershow navbar remains the only navbar.
2. The opening remains a two-column composition on desktop:
   - left: Preview label, compact H1, theme description, brief Flowershow
     introduction, and understated text links;
   - right: the existing repository-authored CSS node/orbit illustration.
3. Below the opening, content becomes a single readable text column with
   ordinary sections for:
   - what can be published;
   - why Flowershow;
   - how publishing works;
   - about the current theme;
   - final publishing and source links.
4. Lists replace the four-card grid and boxed step layout.
5. The dark benefits band, large theme specimen card, and oversized CTA panel
   are removed.
6. `/landing` remains an identical compatibility rendering of `/`.

The Monospace template uses stable `ts-*` semantic classes without encoding a
card-based design. It is a successful theme-specific example, not the default
HTML contract for every future theme.

## Monospace visual language

- Body copy stays compact, approximately 13–15px with a calm monospace line
  height and a readable measure near 70ch.
- H1 is approximately 17–20px, not display-sized.
- Section headings are approximately 15–17px.
- CSS-generated `#` and `##` prefixes make the heading hierarchy feel native
  to Markdown.
- Links look like technical text links, not large filled buttons.
- Hairline borders and whitespace separate sections; cards and shadows do not.
- The opening uses two columns above the mobile breakpoint and one column on
  narrow screens. On mobile, text remains first and the visual follows it.
- The node/orbit illustration is quieter and smaller than the screenshot's
  current oversized disc. It remains CSS-authored and contains no borrowed
  artwork.
- Light and dark modes retain sufficient contrast and the same hierarchy.

## Scope and reuse boundary

This phase changes only `codestorage-draft`. Material, official theme demos,
and their landing pages remain untouched. The current shared template is not
silently rewritten for all themes. Monospace receives a local showcase
template alongside its metadata and scoped presentation CSS.

What is common today is the demo contract, not homepage layout:

- every theme has real, useful content rather than a decorative shell;
- the real Flowershow navbar and standard kitchen-sink/blog routes remain;
- sources, Preview status, responsive modes, and provenance are verifiable;
- no fictional claims or copied reference identity/assets are allowed.

Homepage structure stays theme-specific. A blogging-oriented theme may use a
blog-like homepage; a documentation theme may lead with documentation; this
technical theme uses a compact text document with a supporting visual. After
several homepages work well, a later design can extract only proven common
content or structure.

The landing remains a real Flowershow page rather than a Tailwind-style bundle
of bespoke utility markup. Raw HTML is limited to the structural wrapper and
semantic elements needed for the two-column opening and scoped styling.

## Non-goals

- Do not reproduce code.storage branding, copy, claims, logos, customer names,
  artwork, pricing, or service identity.
- Do not alter the Material-inspired landing page.
- Do not redesign or migrate any official theme homepage.
- Do not define a universal landing-page layout in this phase.
- Do not change the canonical Flowershow gallery or
  `/docs/reference/themes`.
- Do not promote Monospace beyond Preview.
- Do not address search entitlement or release preparation.

## Verification

Automated contracts must fail if the Monospace showcase reintroduces:

- display-scale H1/H2 values;
- the card grid, boxed steps, dark benefits panel, or oversized CTA layout;
- missing `#`/`##` heading markers;
- a desktop opening that is not two columns;
- horizontal overflow at the 390px viewport;
- duplicate header or navigation markup;
- external or data-URL landing assets.

Build-only output must still produce identical `/` and `/landing` sources.
The full repository verifier must pass. The published homepage must then be
reviewed at desktop and mobile widths in both light and dark modes, with the
standard kitchen sink and blog routes smoke-checked for leakage.

## Acceptance criteria

- The first screen reads as a compact technical document with a supporting
  right-hand visual, not a conventional oversized marketing hero.
- H1 and section headings use restrained natural sizes and visible Markdown
  markers.
- Content after the opening is predominantly linear text, lists, and links.
- No four-across card layout or equivalent boxed marketing pattern remains.
- The real Flowershow navbar, validated metadata/rendering path, Preview
  status, and all standard routes remain intact.
- Both supported color modes and desktop/mobile layouts are visually sound.
