# Coverage ledger: leaf

Worked example: a dry run on the shipped Leaf theme (2026-10-18), made
against https://leaf-theme-preview-olayway.flowershow.me. Not Leaf's real
ledger. It shows the note detail and the gaps an honest ledger records.
Check: `scripts/coverage-ledger.py check leaf`.

## layout: gap

Looked at /, /blog, /docs/kitchen-sink desktop+mobile, light+dark. The page is white in light mode and default near-black in dark, never Leaf's cream: --color-background is set on a bare :root, and core's :root[data-theme=light|dark] wins (palette-leaks lists it as an inactive token). Set it via --color-l-background / --color-d-background.

## navigation: styled

Olive bar, Cinzel site name, Cormorant links. Looked at / and /features/canvas light+dark, desktop and mobile shots.

- Gap `site-navbar-cta-button`: Near-black text on a black button: .site-navbar * sets every navbar descendant's colour, the CTA included.
- Gap `site-navbar-link`: Pale link text on the olive bar in dark mode; axe flags it (contrast).

## sidebar: inherits-ok

Site tree on / and /features/listings/grid, light+dark: Cormorant via --font-heading, default greys read well on both backgrounds.

## content: styled

Hero (full-height olive, decorative title) and page-header date restyled; body type from --font-heading. Looked at /docs/kitchen-sink, /features/hero light+dark. Callouts and code keep the default colours, which read fine but aren't Leaf's.

- Gap `page-header-breadcrumb*`: Default orange accent (#fb923c): Leaf never sets --color-accent.
- Gap `page-hero-cta`: Primary CTA is the default orange button on the olive hero.
- Gap `page-hero-description`: Grey description on olive is low contrast in dark mode.

## post: inherits-ok

Looked at /blog/fourth-post-with-cover-and-tags light: byline, cover, caption and tag footer sit well in Leaf type. Eyebrow orange is the accent gap recorded under content; tag pills under tags.

## toc: inherits-ok

ToC rail on /docs/kitchen-sink light+dark: default greys, current item clear.

## listings: styled

Legacy and grid cards get the green border and light-green hover; eyebrows in Cinzel. Looked at /features/listings/grid light and /blog.

- Gap `list-component-group-heading`: Group headings are a brown (#915136) from no Leaf token (palette-leaks).

## tags: gap

Looked at /tags dark and the post footer light: tag pills are the default pink (--color-tag-pill-* unset), off-palette for Leaf.

## changelog: gap

Looked at /changelog light: timeline layout is fine, but the entry dots are the default orange accent (same --color-accent gap).

## search: gap

Cannot render on the demo sites (flowershow/flowershow#1370); not reviewed.

## footer: inherits-ok

Footer on every shot, light+dark: Cormorant headings, default greys and rule; reads as part of the page.

## page-actions: inherits-ok

Backlinks and raw-markdown link on /docs/kitchen-sink light+dark: default greys, fine.

## embeds: inherits-ok

Looked at /features/canvas light: node colours come from the canvas file (inline styles, palette-leaks shows them), chrome is neutral. Mermaid tooltip yellow is mermaid's own.

## errors: inherits-ok

Looked at /this-page-does-not-exist light (not in the contact sheet): default card, Leaf type, readable.

## states: inherits-ok

State modifiers seen through their owners (hero has-image, current tree item, scrolled navbar); nothing state-specific looks off.
