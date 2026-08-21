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

## Still unavailable or pending

- The shared demo requests search with `enableSearch: true`, but these preview
  sites do not have the Flowershow Search feature entitlement and render no
  `.search-button`. Search therefore remains explicitly unreviewed rather
  than being counted as a visual pass.
- Landing-fixture copy, trademark use, icon/SVG provenance, and attribution
  remain a separate official-release gate.
- This matrix does not approve final names, canonical gallery/dashboard
  integration, release metadata, or a release tag.

## Result

Desktop/mobile and light/dark review is recorded for every currently rendered
surface. Material and code.storage still remain **Preview** because search is
not reviewable in these demos and the provenance, naming, integration, release,
and explicit human-promotion gates remain open.
