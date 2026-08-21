# Authoring a Flowershow theme

Written from what actually broke building `material-draft/` and
`codestorage-draft/` (2026-08-08/09) — not written first. If something here
turns out wrong, trust a fresh render over this doc and fix the doc.

**Placement note:** this lives in this repo's `docs/` for now. It was
deferred pending "both draft themes exist and there's real experience to
write from" (see `NEXT.md`) — that's now true. Whether it should move to
the main `flowershow/flowershow` docs is still an open call for a human;
this is the default landing spot because it doesn't require touching
another repo unsupervised. See the companion
[AI cloning skill](./ai-theme-cloning-skill.md) for the agent-facing
version of the same method.

Before creating or refreshing a demo, read the canonical
[standard demo pages and content inventory](./demo-site-content.md). It defines
the routes every theme must publish, where their content comes from, and which
files are shared versus theme-owned.

Start broad visual changes with Flowershow's custom properties. When a theme
needs component-specific selectors, use the published
[semantic theme class reference](https://flowershow.app/docs/reference/theme-class-reference).
It is the stable theme-author API for component hooks, states, variants, and
their DOM ownership; do not infer that every class seen in component source is
part of that contract.

## The method: two stages, never skip stage 1

**Stage 1 — reproduce the target as standalone Tailwind/plain HTML+CSS,
outside Flowershow entirely.** Iterate until it genuinely resembles the
target. Cheap to iterate — no Flowershow deploy, no CDN cache, no `fl`
publish step in the loop.

**Stage 2 — only once stage 1 looks right, extract those measured values
into an actual Flowershow `theme.css`.**

This order matters more than anything else in this doc. The first attempt
at both draft themes skipped stage 1, went straight to writing theme CSS
from the target's *source* (SCSS variables, computed styles read once) and
produced CSS that passed every structural check in `verify.sh` and
resembled nothing. The failure wasn't a knowledge gap — the wrong indigo
palette was even mkdocs-material's own documented default — it was that
**the rendered result was never compared against the rendered target.**
Structural checks only ever answer "does this CSS parse, are the tokens
defined." They cannot answer "does this look like the thing."

## Compare numerically, not by eye

Side-by-side *looking* isn't enough either — screenshots at normal
compression make different fonts and weights look alike, and eyeballing
catches "wrong font" but not "right font, wrong weight relationship."
Relationships are what carry resemblance.

Write one profile extractor and run it against both the reference and your
repro, on matching elements:

```js
function prof(el) {
  const s = getComputedStyle(el);
  return { fs: s.fontSize, fw: s.fontWeight, lh: s.lineHeight,
           ls: s.letterSpacing, mb: s.marginBottom, color: s.color };
}
```

The clearest example this caught: on mkdocs-material the hero `h1` is 700
weight at full strength, but every section `h1` is 300 weight *and*
dimmed (opacity ~0.55). Styling both as one "heading" style flattened the
whole hierarchy — correct font, correct colour, still read as not-Material.
Other misses only numbers caught: a feature grid that's 2 columns not 3,
icons at 44px inheriting text colour rather than 28px accent, buttons at
700 weight not 500, `h2` margin-bottom at 16px not 8px.

**Typographic precision — relative weight, size, spacing ratios — matters
more than font choice.** Get the ratios right before touching anything
else.

## Publishing the standard theme-demo homepage

Stage 1's standalone `.html` reproduction in `_repro/` remains throwaway. A
shipped demo uses Flowershow's shared product homepage, not a copy of the
reference site's landing page.

Add `THEME-DIR/demo-showcase.json` for the theme's name, Preview status,
headline, description, wrapper class, and repository URL. Style the shared
semantic markup in `THEME-DIR/demo-landing.css`, with every landing-only rule
scoped beneath the wrapper. `scripts/demo-site.sh THEME-DIR` renders the shared
template to `/`, retains an identical `/landing` compatibility page, copies the
CSS as `custom.css`, and supplies the real Flowershow navbar.

The exact schema, standard routes, shared sources, migration path, and commands
are in [Standard theme demo pages and content](./demo-site-content.md).

Do not add a second `<header>` or `<nav>` to the homepage. Do not place review
matrices or release gates in marketing copy. Use `--landing-page FILE.md` only
for an exceptional research fixture that cannot use the shared template, and
`--landing FILE.html` only for stage-one comparison outside normal Flowershow
chrome.

## Where to actually get values

Read from the rendered page (`getComputedStyle`) or from the target's own
released source when it's open (real SCSS variables, not a guess), never
from memory of what a design "usually" looks like or from a compressed
screenshot. Both draft themes' license headers name their real source. If
the target is closed-source, computed-style inspection on the live site is
the only source of truth — say so in the theme's header comment so the next
person knows it can't be re-derived from a repo.

## Two caching layers that will lie to you

Both cost real time on this work; check for them before concluding a CSS
change didn't apply.

1. **jsDelivr branch-pinned URLs update unevenly across edges.** One edge
   can serve new CSS while another (including the one your browser hits)
   still serves stale — survives `cache: 'reload'` and a cache-busting
   query string. Fix: pin the demo's theme URL to the **commit SHA**, not
   the branch name. `scripts/demo-site.sh` does this automatically — that's
   why it requires the commit to be pushed first.
2. **Flowershow's own published-page cache** can keep serving a previous
   config (and so a previous theme URL) for a while after `fl` publish.
   Poll until the page actually contains the SHA you expect before judging
   anything:
   ```sh
   SHA=$(git rev-parse HEAD)
   until curl -s "$SITE/docs/kitchen-sink?x=$RANDOM" | grep -q "$SHA"; do sleep 5; done
   ```
   Between the two layers, a genuinely-correct theme change can look
   completely unapplied. Verify what's actually being served before
   debugging CSS that isn't broken.

   One further wrinkle found 2026-08-09: raw `.html` landing pages
   published via `fl` can go stale on Flowershow's *own* site-serving
   cache in a way that isn't jsDelivr and isn't fixable by purging jsDelivr
   — `fl` can report every file current while the served page still isn't.
   No fix was available from this repo; the practical workaround was
   publishing under a new site name (see `material-landing-demo` →
   `material-landing-v2` in `docs/features.yaml`).

## Flowershow component gotchas (none discoverable from the theming docs)

All found by rendering, not by reading `docs/theming.md`:

1. **Callouts are styled by data attributes, not classes.**
   `[data-callout]`, `[data-callout-type="note"]`, `[data-callout-title]`,
   `[data-callout-body]`. A `.callout` / `.callout-note` selector matches
   nothing — a draft used class selectors early on and it silently did
   nothing.
2. **Bare attribute selectors tie the base rule and lose.** The base rule
   is `[data-callout]` at specificity `0,1,0`. A theme rule with the same
   bare selector ties and doesn't reliably win the cascade. Scope theme
   rules to `.rendered-mdx [data-callout]` (`0,2,0`) instead.
3. **`--navbar-height` is not read anywhere.**
   `.site-navbar-inner` hardcodes `height: 4rem` despite the token being
   documented as controlling it (flowershow/flowershow#1341). To actually
   change navbar height, override the class, not the token.
4. **Inline code gets literal backtick pseudo-elements from
   `@tailwindcss/typography`, with `!important`.** They're not in the DOM.
   `content: none` alone loses at any specificity; you need
   `content: none !important` (flowershow/flowershow#1342) — this
   contradicts `docs/theming.md`'s claim that the cascade-layer setup means
   themes never need `!important`.
5. **The navbar doesn't render at all unless configured.** Flowershow only
   shows it if nav title, nav links, CTA, social links, or search is set.
   A demo site without any of those has *no navbar*, so navbar styling is
   silently invisible and the theme looks broken for a reason that has
   nothing to do with the CSS. `nav` is an **object**
   (`{title, links, social, cta}`), not an array. `_demo-content/
   config.base.json` in this repo already covers this — reuse it rather
   than writing a bare config.
6. **Raw `.html` pages 404 on any query string** — the usual
   cache-busting `?v=N` trick breaks them (flowershow/flowershow#1345). Hit
   the bare root when smoke-checking a raw HTML page.

## Licensing

Never reference a commercial or non-redistributable font in a theme's
active `--font-*` stack. `codestorage-draft/theme.css`'s header comment is
the worked example: the reference site uses BerkeleyMono (commercial,
berkeleygraphics.com), substituted with the open IBM Plex Mono, documented
in a comment so a license holder knows they can override
`--font-body`/`--font-heading` locally. Same principle for bespoke artwork
(mkdocs-material's parallax illustration) — reference it only as a local,
unpublished stand-in for fidelity comparison; never ship it.

## Structural ceiling — know when CSS can't do it

Some things are not cloneable with a theme at all, because the component
doesn't exist in Flowershow's core:

- Tabbed content blocks (mkdocs-material-style content tabs)
- Prev/next page footer pagination
- A version selector

These aren't theme bugs — don't burn time trying to CSS your way to a
component that isn't rendered. Document the gap in the theme's
`known_gaps` and move on; see `NEXT.md` item 4 for the open decision on
whether Flowershow core should eventually grow slot/block ordering or full
layout templating to close this ceiling.

## The ledger discipline

`docs/features.yaml`: `passes` is structural only and must equal what
`scripts/verify.sh` actually checked — never hand-edit it to `true`.
`fidelity` is separate, human- or LLM-judged, and never a gate; grade it
`unreviewed` / `reviewed-close` / `reviewed-off` with notes on what was
actually compared and how (screenshot? computed-style diff? which
elements?). Don't infer fidelity from structural checks passing — that's
exactly the mistake this whole method change was written to prevent.
