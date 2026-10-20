# Authoring theme.css from design-tokens.json

Phase B reference. The token API is documented at
https://flowershow.app/docs/reference/custom-styles. What core actually
reads is in `../flowershow/apps/flowershow/styles/default-theme.css`,
which has about 100 custom properties and few hard-coded colours. So a
complete token set restyles most of the site, and selectors are for
character.

## File layout

Use `monospace/theme.css` as the model:

1. A header comment: the inspiration URL, the date measured, and every
   font swap or derived palette (from `fontNotes` and `"derived": true`).
2. Font `@import`s (Google Fonts only, open licences).
3. Tokens.
4. Component overrides, grouped by hook group, each with a comment
   saying which screenshot difference it fixes.

## Tokens

- **Mode colours**: set `--color-l-background|foreground|accent` and
  `--color-d-…` on `:root`. Core resolves `--color-background`,
  `--color-foreground` and `--color-accent` from them on
  `:root[data-theme="light|dark"]`, and derives the foreground ramp
  (`-50` … `-900`) and accent shades. To set a resolved token yourself,
  use a `:root[data-theme="light"]` or `:root[data-theme="dark"]`
  selector. Core's `[data-theme]` blocks beat a bare `:root`, which is
  why Leaf's cream background never shows.
- **Accent**: always set both accents. The default orange (`#fb923c`)
  otherwise leaks into breadcrumbs, changelog markers and the hero CTA.
- **Semantic colours** without a measured source: tag pills, code
  backgrounds (`--color-code-bg`, `--color-code-bg-dark`), CTA
  (`--color-cta-*`), `--color-danger`, `--color-warning`, and callouts
  (`styles/callouts.css` in core). Take each from the nearest measured
  role, per EXTRACT.md step 6. Code blocks have a token per mode.
  For the others, set the dark value on `:root[data-theme="dark"]` when
  it differs.
- **Type and shape**: `--font-heading`, `--font-body`, `--font-size-base`,
  `--radius` (core derives `--radius-xs`, `-md`, `-lg` and `-xl` from it;
  set them only if the site's radii don't scale that way), and the line
  heights, all from the measured type scale and radii. The
  `--list-*`, `--post-*` and `--changelog-*` tokens tune those
  surfaces before you need selectors.
- **Link hover** isn't measured by `measure-site.mjs`. Hover a body link
  on the site with `browse` and read its computed colour before you set
  one.

## Overrides

- Select only hooks listed in the
  [theme class reference](https://flowershow.app/docs/reference/theme-class-reference).
  Other classes in the markup aren't API and change without notice.
- Write an override only for a difference you saw in a Phase C
  comparison that tokens can't fix. Each one is a decision you will also
  record in `coverage.yaml`.
- Keep tokens doing the colour work: in an override, use
  `var(--color-…)` rather than a literal, so both modes follow.

## Lessons from the earlier themes

`docs/ai-theme-cloning-skill.md` holds the lessons from building Material
and Monospace. Read these sections before Phase B, since they still
apply:

- "Never judge fidelity by eye or by structural checks alone": the
  computed-style diff that Phase C uses.
- "Flowershow-specific rendering facts": callouts are data attributes
  scoped as `.rendered-mdx [data-callout]`, inline-code backticks need
  `!important`, and the navbar renders only when nav is configured.
- "Licensing checks": open fonts only, no copied artwork or logos.
- "When you hit Flowershow's structural ceiling": what CSS can't do
  becomes a recorded gap. For a draft, record it in the group's
  `gaps:` in `coverage.yaml` and in the hand-off. It goes in
  `features.yaml` as a `known_gap` only at release.
- "Two caching layers": they matter after release, when the theme loads
  from jsDelivr. The `--local` preview serves `custom.css?v=<hash>`, so
  its stylesheet is never stale.

Its "Do not skip stage 1" step (a standalone HTML rebuild) is replaced by
Phase A here. Its showcase-homepage section is for official demos, and a
new theme doesn't need one.
