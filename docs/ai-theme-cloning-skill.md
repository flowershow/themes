---
name: flowershow-theme-cloning
description: >-
  Clone the visual look of a reference website into a Flowershow theme
  (theme.css). Use when asked to "clone the look of <url>", build a
  Flowershow theme inspired by an existing site, or improve an existing
  draft theme's fidelity to its reference.
compatibility: Designed for Claude Code (or similar products)
metadata:
  author: flowershow
  status: draft — derived from building material-draft/ and codestorage-draft/
    in flowershow/themes, not yet used cold by anyone else
---

# Cloning a site's look into a Flowershow theme

**Placement note:** this is written as an agent-facing skill but currently
lives in `flowershow/themes/docs/` rather than `flowershow/skills`, because
writing it required no access outside this repo and the destination repo
was an open question (see `NEXT.md`). If invoked from `flowershow/skills`
in the future, port this file there with its frontmatter as-is. The
human-readable companion is
[theme-authoring-tutorial.md](./theme-authoring-tutorial.md) — same
content, prose form.

Before creating or updating demo content, follow the canonical
[standard demo pages and content inventory](./demo-site-content.md). It defines
the required routes, exact source files, metadata schema, and ownership
boundary.

## Do not skip stage 1

Build the target's look as **standalone HTML + Tailwind (or plain CSS),
completely outside Flowershow**, before writing a single line of
`theme.css`. This is not an optional shortcut — the first pass at this
exact task skipped it, went straight to `theme.css`, and produced CSS that
passed every structural check and looked nothing like the target. Iterating
on a bare HTML file is cheap: no Flowershow deploy, no CDN cache, no `fl`
publish round-trip. Iterating on a published theme is expensive and every
one of those costs will disguise itself as "the CSS isn't applying" — see
the caching section below.

Only once the standalone repro genuinely resembles the target, in a
side-by-side render, extract the measured values into `theme.css`.

## Never judge fidelity by eye or by structural checks alone

Structural checks (does the CSS parse, are the required custom properties
defined, does a dark-mode block exist) tell you the theme is well-formed.
They tell you nothing about whether it resembles the target — a theme can
pass every one of them and still be visibly wrong.

Eyeballing a screenshot is also insufficient: compression makes different
fonts and weights look similar, and "right font, wrong weight
relationship" reads as correct at a glance but isn't. Instead:

1. Render both the reference and your repro.
2. On matching elements, extract computed style, not source values:
   ```js
   function prof(el) {
     const s = getComputedStyle(el);
     return { fs: s.fontSize, fw: s.fontWeight, lh: s.lineHeight,
              ls: s.letterSpacing, mb: s.marginBottom, color: s.color };
   }
   ```
3. Diff the numbers, not the vibe. Pay particular attention to *weight and
   size relationships between element types* (hero heading vs. section
   heading vs. body), not just each element in isolation — a flattened
   hierarchy is the single most common way a technically-correct clone
   still reads as wrong.
4. If the reference site is closed-source, computed-style inspection on
   the live page is your only source of truth — do not guess from a
   design system's *typical* look. If it's open-source, pull real values
   from its actual source (SCSS variables, tokens file), not from memory
   of what that kind of site "usually" does.

## Publish the shared Flowershow showcase, not the reference landing page

The stage-one standalone HTML reproduction is throwaway. For the shipped demo:

1. create the validated `THEME-DIR/demo-showcase.json` identity layer;
2. style `_demo-content/theme-showcase.template.md` through scoped
   `THEME-DIR/demo-landing.css`;
3. run `scripts/demo-site.sh THEME-DIR`; and
4. verify `/`, `/docs/kitchen-sink`, `/blog`, and `/blog/first-post`.

Never invent customer claims, copy the reference-site marketing identity, or
import its images or logos into the demo homepage. Visual inspiration belongs
in theme CSS; Flowershow product content comes from the shared template. Use
the real Flowershow navbar and never add a second page-level `<header>` or
`<nav>`.

The `--landing-page` and raw `--landing` options are exceptional research tools,
not the normal shipped path. Their use does not replace any standard route.

## Two caching layers that will make correct CSS look broken

Check these before concluding a change "didn't apply":

- **jsDelivr branch-pinned URLs (`@branch-name/...`) update unevenly
  across edges** — can survive `cache: 'reload'` and a cache-busting query
  string. Pin demo theme URLs to the **commit SHA**, not the branch.
- **Flowershow's published-page cache** can keep serving a stale config
  (and so a stale theme URL) for a while after `fl` publish. Poll for the
  current commit SHA in the served HTML before judging anything:
  ```sh
  SHA=$(git rev-parse HEAD)
  until curl -s "$SITE/docs/kitchen-sink?x=$RANDOM" | grep -q "$SHA"; do sleep 5; done
  ```
- Raw `.html` pages published via `fl` have been observed to go stale on
  Flowershow's *own* site-serving cache in a way that is neither of the
  above and has no known fix from the theme repo — `fl` can report every
  file current while the served page still isn't. If this happens,
  publishing under a new site name is the practical workaround (there is
  no cache-purge lever available for it, unlike jsDelivr).

## Flowershow-specific rendering facts (check before assuming a selector works)

Use the
[semantic theme class reference](https://flowershow.app/docs/reference/theme-class-reference)
as the authoritative selector inventory. It separates stable component/state
hooks from non-contract compatibility utilities and records their owners. Do
not guess selectors from names or treat arbitrary component-source classes as
stable API.

- Callouts are styled via **data attributes**, not classes:
  `[data-callout]`, `[data-callout-type="note"]`, `[data-callout-title]`,
  `[data-callout-body]`. A `.callout` selector matches nothing.
- Bare `[data-callout]` in your theme ties the base rule's specificity
  (`0,1,0`) and doesn't reliably win. Scope to `.rendered-mdx [data-callout]`.
- `--navbar-height` is not read by `.site-navbar-inner` (hardcodes
  `height: 4rem`) despite being documented as controlling it — override the
  class if you need a different navbar height, not the token.
- `@tailwindcss/typography` injects backtick pseudo-elements on inline
  `code` with `!important`; removing them requires
  `content: none !important`, not just `content: none`.
- The navbar renders **only if** nav title, links, CTA, social links, or
  search is configured in `config.json`. A demo/test site without any of
  those has no navbar at all — this is a config problem, not a CSS
  problem, and will look like "navbar styling isn't working" if you don't
  know this. `nav` is an object (`{title, links, social, cta}`), not an
  array.
- Raw `.html` pages 404 on any query string — don't cache-bust them with
  `?v=N`; hit the bare root instead.

## Licensing checks before shipping any font or artwork choice

- Never put a commercial/non-redistributable font in a theme's active
  `--font-*` stack. If the reference uses one, substitute an open font
  with similar proportions, and say so in a comment so a license holder
  knows they can override `--font-body`/`--font-heading` locally.
- Bespoke illustration/artwork from the reference site is not yours to
  ship. Reference it only as a local, unpublished stand-in during stage-1
  fidelity comparison; a shipped theme needs original art or an honest
  placeholder, documented as a known gap.

## When you hit Flowershow's structural ceiling

Some things cannot be cloned with CSS because the component doesn't exist
in Flowershow core (as of 2026-08): tabbed content blocks, prev/next page
footer pagination, a version selector. Recognize this early rather than
spending cycles trying to CSS a component into existing markup that isn't
there. Record it as a `known_gap` in the ledger and move on — don't
silently drop the feature without noting it, and don't attempt a core
Flowershow change unsupervised to work around it.

## Ledger discipline (if the target repo uses one like `flowershow/themes`)

Keep "does this parse" (structural, checked by tooling) and "does this
look like the target" (fidelity, human- or LLM-judged) as two separate
fields. Never let one imply the other. When you do an LLM-judged fidelity
pass, say so explicitly in the notes (what was compared, how, and that it
isn't a human sign-off) rather than presenting it as equivalent to human
review.
