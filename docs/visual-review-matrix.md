# Preview visual review matrix — 2026-08-21

This records an AI-assisted visual and browser-layout review of the live
Material and code.storage preview demos. It supplements Rufus's earlier
fidelity review; it is not approval to promote or release either theme.

## Matrix

Each theme was rendered across all 20 combinations below (40 renders total):

| Dimension | Values |
| --- | --- |
| Viewport | desktop (1280 × 900), mobile (390 × 844) |
| Mode | light, dark |
| Surface | home/navbar/sidebar, kitchen sink, blog list, blog post, landing |

For every combination, a headless Chrome audit confirmed that the requested mode was active
and the document width equalled the viewport width. Full-page
captures were then inspected for layout, typography, contrast, component
styling, wrapping, and responsive behavior. The local kitchen-sink image was
scrolled into view and confirmed loaded in both themes.

Live artifacts:

- [Material demo](https://material-theme-demo-rufuspollock.flowershow.me)
- [Material landing](https://material-theme-demo-rufuspollock.flowershow.me/landing)
- [code.storage demo](https://codestorage-theme-demo-rufuspollock.flowershow.me)
- [code.storage landing](https://codestorage-theme-demo-rufuspollock.flowershow.me/landing)

## Findings resolved during the review

1. code.storage's non-wrapping ASCII pricing tables expanded the mobile
   document beyond its 390 px viewport. Intrinsic-width guards and contained
   horizontal scrolling now keep every route at the viewport width.
2. Material's footer used a foreground shade that reversed in dark mode,
   producing a pale footer behind low-contrast white text. It now uses a
   stable dark Material surface in both modes.
3. The kitchen-sink image depended on an external random-image service and
   rendered as a blank review surface. It now uses the repository-owned
   `_demo-content/assets/demo-image.svg` fixture.

## Owned landing fixture review

After the published landing fixtures were rewritten with Flowershow-owned copy
and visuals, a focused addendum rendered both changed pages at desktop and
mobile sizes in light and dark modes: eight renders total.

| Theme specimen | Viewport | Mode | Result |
| --- | --- | --- | --- |
| Material-inspired | 1280 × 900 | light | pass |
| Material-inspired | 1280 × 900 | dark | pass |
| Material-inspired | 390 × 844 | light | pass |
| Material-inspired | 390 × 844 | dark | pass |
| Monospace | 1280 × 900 | light | pass |
| Monospace | 1280 × 900 | dark | pass |
| Monospace | 390 × 844 | light | pass |
| Monospace | 390 × 844 | dark | pass |

For every render, headless Chrome confirmed HTTP 200, the requested active
`data-theme`, a visible `data-owned-fixture` marker with Preview status, visible
fixture links to home, kitchen sink, and blog, and document width exactly equal
to viewport width. It also confirmed the removed upstream identities and
headlines were absent.

Full-page captures were manually inspected. The Material-inspired page retains
its gradient hero, strong hierarchy, alternating dark/light sections, feature
grid, spotlights, and calls to action while reading clearly as Flowershow. The
monospace page retains its bracketed navigation, compact type, code, CSS-only
blob/node composition, long-form sections, and ASCII matrix while reading as a
theme lab rather than a service offer. Neither page could be mistaken for its
upstream visual reference.

The first monospace dark-mode capture exposed a generated syntax-highlighting
background that striped the configuration example. A landing-scoped override
now keeps the generated code wrapper transparent and block-level. Configuration
code stayed readable in the repeated desktop/mobile and light/dark runs.

Independent review then caught three structural defects: the landing calls to
action used a nonexistent `/kitchen-sink` route, the monospace landing CSS had
one unmatched closing brace, and the Material-inspired page used section
headings as additional `h1` elements. The links now use the live
`/docs/kitchen-sink` route, the CSS is balanced, and each landing has one `h1`
with nested section headings. A repeated eight-render audit confirmed the
linked specimen responds HTTP 200 and the corrected pages retain their visual
hierarchy in both modes and viewports.

## Still unavailable or pending

- The shared demo requests search with `enableSearch: true`, but these preview
  sites do not have the Flowershow Search feature entitlement and render no
  `.search-button`. Search therefore remains explicitly unreviewed rather
  than being counted as a visual pass.
- This matrix does not approve final names, canonical gallery/dashboard
  integration, release metadata, or a release tag.

## Result

Desktop/mobile and light/dark review is recorded for every currently rendered
surface. Material and code.storage still remain **Preview** because search is
not reviewable in these demos and the naming, integration, release, and explicit
human-promotion gates remain open. The landing-fixture provenance actions are
complete and recorded separately.
