# Handoff: "Create a Flowershow theme inspired by website X"

Status: in progress. Written 2026-10-17 at the end of an exploratory session;
steps 2–6 below are done (uncommitted); see each step for evidence.
Read `CLAUDE.md` (house rules) and `NEXT.md` before starting.

## Goal

The user wants to say one sentence to an agent:

> Create a Flowershow theme inspired by <website X>

and have the agent:

1. **Extract** X's design system (colour, type, spacing, radius, component
   feel) using **OpenDesign** (the `open-design` MCP server).
2. **Author** `<name>-draft/theme.css` from it — tokens first, then only the
   component overrides that are actually needed.
3. **Prove coverage**: every part of the Flowershow layout has been
   *deliberately* handled — either styled by the theme or consciously left to
   inherit the default (which is fine when tokens make it look right). No
   forgotten, unstyled-looking elements. This is **not** "copy the whole
   default theme and tweak it".
4. **Publish a preview site** and hand the user a link plus a screenshot
   contact sheet.
5. **Stop.** Nothing is committed, pushed, or released until the user says
   they are satisfied. Then: commit on a non-`main` branch → PR. Tagging a
   release stays human-only (see `CLAUDE.md` guard rails).

Deliverable of this handoff: the **reusable workflow** (a skill + the scripts
it calls), validated by running it end-to-end once on a real site.

## What exists today (verified in this session)

- A theme is just `<dir>/theme.css`. Everything else in the repo is demo/QA
  scaffolding.
- `scripts/demo-site.sh <dir>` copies `_demo-content/` (kitchen sink, blog
  with 3 posts, image fixture), writes `config.json` with `theme` = a
  jsDelivr URL **pinned to the current commit SHA**, then `fl publish`es.
  It **errors if the commit isn't pushed** — so today previewing requires
  commit + push. That conflicts with goal 5.
- `demo-site.sh --build-only <dir>` assembles the site without publishing.
- Optional per-theme demo homepage (`demo-showcase.json` +
  `demo-showcase.template.md` + `demo-landing.css`) — only Monospace uses
  it. Not needed for new themes; skip it.
- `scripts/verify.sh` — structural only: braces balanced, 8 required tokens,
  a `data-theme="dark"` block, preview asset (warn), demo routes return 200.
  Contains hard-coded Monospace/Material checks (doesn't scale; leave them,
  don't weaken them).
- `docs/ai-theme-cloning-skill.md` + `docs/theme-authoring-tutorial.md` —
  existing agent/human workflow for cloning a site's look. Hard-won lessons
  worth keeping (computed-style diffing, caching traps, selector facts,
  font licensing). Its "stage 1: rebuild in standalone HTML" step is what
  OpenDesign should replace.
- `docs/visual-review-matrix.md` — a 40-render review (desktop/mobile ×
  light/dark × 5 routes) done **ad hoc**; no script is checked in.
- Core app (`../flowershow`):
  - `getThemeUrl()` (`apps/flowershow/lib/get-theme.ts`) accepts any
    `http…` URL as `theme`.
  - The site layout links `theme.css` **then** the site's root `custom.css`
    (`apps/flowershow/app/(public)/site/[user]/[project]/layout.tsx`
    ~L268–273). So publishing theme CSS as `custom.css` with no `theme`
    set previews a theme **without git**. **Validated 2026-10-17 on `leaf`**:
    two anon sites from identical `--build-only` output, one with the
    SHA-pinned jsDelivr `theme`, one with no `theme` and `leaf/theme.css`
    as `custom.css`. Served `custom.css` byte-identical to the source; both
    stylesheets land in the same `<head>` slot (after the app CSS, before
    KaTeX); computed styles of 14 sampled elements identical in light and
    dark; light kitchen-sink screenshots byte-identical, dark visually
    identical; all standard routes pass `verify-demo-routes.py`. Leaf's
    Google Fonts `@import` works from `custom.css` too.
  - `scripts/theme-class-reference.mjs` extracts every class selector from
    `apps/flowershow/styles/default-theme.css` and generates
    `content/flowershow-app/docs/reference/theme-class-reference.md`
    (346 stable hooks + 2 compat utilities, grouped by UI area, CI
    drift-checked). **This is the authoritative inventory for "coverage".**
  - `default-theme.css` (~4.8k lines) reads ~99 distinct CSS custom
    properties and has only ~31 hard-coded colours → a complete token set
    already restyles most components; hooks are for character.
- `fl` CLI: publish / list / delete / settings / whoami / `--anon`
  (7-day throwaway site). **No local preview/dev server.**
- Demo content gaps: kitchen sink has headings, lists, tasks, quote, code,
  table, callouts, image, hr. It does **not** exercise: listing views
  (magazine, square — just added upstream in themes #19/#20, which forced
  edits to all six themes), tags, wiki-links/embeds, math, mermaid, TOC,
  page headers, changelog, footer variants, comments. Search can't render on
  the demo sites (no entitlement — flowershow/flowershow#1370).
- Local `themes/` checkout was 3 commits behind `origin/main` (listing
  styles). **Pull first.**
- The `open-design` MCP server was **disconnected** at the end of this
  session. Confirm it connects before relying on it; if not, tell the user.

## Proposed design

### Phase A — Extract (OpenDesign)

Use OpenDesign to capture X into a project, then pull its tokens/design
system (`get_artifact` returns entry file + tokens CSS in one call). Normalise
into `<dir>/design-tokens.json` (colours incl. dark variants if X has them,
font families + weights + scale, spacing, radius, shadows, link/button/code
treatment) and keep the OpenDesign reference artifact for side-by-side
comparison. Answered in step 6: OpenDesign's picks are unreliable, so it captures
evidence and `scripts/measure-site.mjs` measures the values; see
`docs/extract-design.md`.

### Phase B — Author

1. Map tokens → the ~99 Flowershow custom properties (start from the token
   list in `custom-styles.md` and what `default-theme.css` actually reads).
   Could be a small generator script or agent-done; agent-done is fine for v1.
2. Add component overrides only where tokens aren't enough to match X.
3. Respect existing rules: open fonts only, no copied artwork/logos, dark
   mode required, `.rendered-mdx [data-callout]` scoping, etc. (see the
   cloning skill's "rendering facts").

### Phase C — Coverage (the "nothing forgotten" guarantee)

Two parts:

1. **Fixture completeness (gate).** Extend `_demo-content/` so the demo
   site renders every stable hook group from the class reference (add
   pages for listings in each view, tags, wiki-links/embeds, math, mermaid,
   TOC, page header variants, etc.). Script: load each demo route in a
   headless browser, collect all class names in the DOM, diff against the
   stable-hook list (get it from `theme-class-reference.mjs` — ideally add a
   `--json` output upstream; for v1 parse it locally). Hooks that can't
   render on demo sites (search, comments) go on an explicit allowlist with
   a reason.
2. **Per-theme decision ledger (report, not gate).** For each hook group in
   the class reference: `styled` (theme has selectors for it) /
   `inherits-ok` (agent looked at the render and the defaults + tokens are
   right) / `gap` (needs work). Store as `<dir>/coverage.yaml`. The agent must
   fill every group before handing off — that's what "deliberate" means.
   Also flag computed colours on the page that aren't in the theme's palette
   (default-theme colours leaking through).

### Phase D — Preview (no git)

Add `demo-site.sh --local` (or a new script): copy working-tree `theme.css`
into the build as `custom.css`, leave `theme` unset, skip the push check,
publish with `fl` (`--anon` or a stable `--name <name>-theme-preview`).
Watch for Flowershow's page cache serving stale content after republish
(see cloning skill). Then a screenshot script (Playwright or the gstack
`/browse` skill — user's global rule: use `/browse`, never
`mcp__claude-in-chrome__*`) producing a contact sheet: all routes ×
desktop 1280 / mobile 390 × light / dark, plus OpenDesign reference shots
side by side. Add automated sanity checks: no horizontal overflow on mobile,
contrast (axe), requested mode active.

### Phase E — Approve, then release

Agent stops with: preview URL, contact sheet, `coverage.yaml` summary, known
gaps. After the user approves: branch, commit theme + ledger entry in
`docs/features.yaml`, run `verify.sh`, (optionally switch the demo to the
SHA-pinned path), open a PR. Never push to `main`, never tag.

### Packaging

A skill, e.g. `flowershow-theme-from-website`, that orchestrates A–E and
calls the scripts. Supersedes/absorbs `docs/ai-theme-cloning-skill.md`.
Where it lives (this repo vs `flowershow/skills`) is still an **open
decision** per `CLAUDE.md` — ask the user; default to this repo for now.

## Suggested order of work

1. Pull `origin/main`. Confirm OpenDesign MCP is connected.
2. ~~Validate `custom.css` preview on an existing theme~~ — done (leaf,
   see above). `demo-site.sh --local` added: working-tree theme.css →
   custom.css (theme first, then any landing CSS), `theme` removed from
   config.json, no push check, publishes to a stable named
   `<theme>-theme-preview` site with `fl --overwrite` (refuses
   `*-theme-demo` names). `--build-only` output verified for leaf and
   monospace; non-local builds unchanged. Live-verified 2026-10-17 on
   https://leaf-theme-preview-olayway.flowershow.me: page links only
   `/custom.css?v=<hash>` (no theme stylesheet), served file byte-identical
   to `leaf/theme.css`, all 4 standard routes pass `verify-demo-routes.py`.
   Republishing changed CSS to the same named site works (fl syncs 1 file,
   8 unchanged); the new CSS was served within ~10 s, and the `?v=` hash
   changes with the content, so the stylesheet itself can't be stale.
3. ~~Screenshot contact-sheet script.~~ Done: `scripts/contact-sheet.py
   <url> [--out DIR] [--route /x ...]`. Routes default to
   `verify-demo-routes.py` STANDARD_ROUTES (step 4 extends that list).
   Drives the gstack `browse` daemon (`BROWSE_BIN` overrides). Forces mode
   via `localStorage['theme-preference']`. **Gate** (exit 1): HTTP 200,
   requested `data-theme` active, `scrollWidth <= innerWidth` (offending
   elements named). **Report only**: axe-core colour-contrast. Writes PNGs,
   `checks.json`, `index.html`. Verified on the leaf preview: 16 shots in
   ~19 s, all pass the gate; a 404 route, a page stuck in light mode and an
   injected 900px element all fail it as intended. Leaf shows 96 contrast
   issues (e.g. its navbar on the olive bar in dark mode). Gotchas:
   browse `js` code containing `await` runs as a function body and needs
   an explicit `return`; Flowershow's 404 page ignores the stored dark
   mode. Not yet: OpenDesign reference shots side by side (step 6).
4. ~~Coverage fixture pages + hook-diff script (Phase C.1).~~ Done
   2026-10-17. `_demo-content/` gained a `/features` section (page
   header, hero right/full, rich content, contents-only, plain page,
   standalone canvas, listings in every view plus empty/error/legacy
   states over a 12-story folder), `people/` author pages with avatars,
   a fourth blog post (local cover, caption, tags, two authors), a
   12-entry `changelog/` folder, `releases/CHANGELOG.md`, and generated
   assets (3 covers, 2 avatars, a 2-page PDF). `config.base.json` adds
   footer navigation, `enableRss`, `showRawLink` and a Features/Changelog/
   Tags dropdown; `demo-site.sh` keeps that dropdown on showcase homepages.
   New routes are `FEATURE_ROUTES` in `verify-demo-routes.py` (not yet
   checked by `verify()`/`verify.sh`, since live demos predate them);
   `contact-sheet.py` and the new `scripts/hook-coverage.py` load them.
   `hook-coverage.py <url>` crawls every route at desktop + mobile, runs
   the hover/click/scroll interactions once, diffs DOM classes against
   core's own `theme-class-reference.mjs` at `origin/main` (fetched), and
   fails on any stable hook neither rendered nor in
   `scripts/hook-coverage-allowlist.json` (each entry has a reason).
   Verified on the leaf preview: baseline 136/346 → **346/346** (exit 0;
   ~2:45); with only `/` it exits 1. Contact sheet over all 26 routes:
   104/104 shots pass the gate. Gate scope (user, 2026-10-17): **all
   themes**. The hooks a demo renders depend on content and config, not
   on theme CSS, so one passing run covers every theme built from
   `_demo-content/`. The live Material/Monospace demos still need
   republishing with the new content before they can be checked; that
   publishes to the shared account, so ask first.
   Findings for core (not yet filed):
   - **Inline canvas embed (`![[x.canvas]]`) resets dark mode**: the page
     renders light and `ThemeSwitch` writes `light` back to
     `localStorage['theme-preference']`, so a dark-mode reader stays
     light on every page after it. Bisected on one-feature pages; the
     standalone canvas page is fine. The fixtures leave inline canvas
     out, and `contact-sheet.py` re-sets the mode before every shot.
   - Styled but never emitted on main: `.page-header-image`,
     `.page-header-image-container`, `.graph-mini-panel__label`,
     `.sidebar-drawer-header`, `.sidebar-drawer-close(-icon)`, and
     `.mobile-nav-tree*` (only nav.tsx's unused `TreeView` emits them).
   - The hero's full-width layout is undocumented, and the frontmatter key
     must be lowercase: `hero: { imagelayout: full }`.
   Gotchas: an unquoted `: ` in a frontmatter value makes the page 404
   with no publish error; the navbar dropdown opens on hover and a click
   then closes it; `fl --overwrite` from a fresh build does delete remote
   files that are gone locally.
5. ~~`coverage.yaml` format + agent procedure (Phase C.2).~~ Done
   2026-10-18. `scripts/coverage-ledger.py sync|check <dir>` keeps
   `<dir>/coverage.yaml`, with one entry per core hook group (15). Each
   entry has a `decision` (`styled` / `inherits-ok` / `gap` / `todo`), a
   required `note`, and optional `gaps:` (hook pattern → problem).
   `check` fails on `todo`, on an empty note, on `styled` when theme.css
   selects none of the group's hooks, on `inherits-ok` when it selects
   some, on stray gap patterns, and on groups missing from or dropped by
   core. Gaps pass and are listed. The file is a strict YAML subset
   parsed with the stdlib; the tests cross-check it against Ruby's YAML.
   `scripts/palette-leaks.py <url> <dir>` is report-only. It flags
   element colours outside the palette (every declared custom property
   plus theme.css literals, alpha ignored; a mix of two palette colours
   counts as "derived"), attributed to hook groups; tokens holding a
   colour literal the theme doesn't set; and **inactive** theme tokens,
   whose value the page never uses. `check --leaks` warns on an
   `inherits-ok` group that has leaks. Procedure:
   `docs/coverage-ledger.md`, pointed to from `CLAUDE.md`. Tests:
   `scripts/test-coverage-ledger.py`. `hook-coverage.stable_hooks` now
   returns groups in the reference's order. Dry-run on the leaf preview
   (ledger kept in the session scratchpad, since leaf is shipped): 15/15
   decided, 10 gaps, exit 0. The ledger caught real Leaf bugs.
   `--color-background` on a bare `:root` loses to core's
   `:root[data-theme]`, so the cream page never shows. `.site-navbar *`
   blacks out the CTA's text. `--color-accent` is unset, which leaves
   the default orange in breadcrumbs, changelog dots and the hero CTA.
   Fixture bug found on the way: `nav.cta` used `label`, but the navbar
   reads `name`. Core #1357 (config sanitising) now drops the malformed
   CTA, so the CTA hooks stopped rendering (344/346). Fixed in
   `config.base.json` and the showcase nav in `demo-site.sh`, which was
   already wrong on `main`, so the live Monospace demo lacks its CTA
   until it's republished. After republishing leaf: 346/346. Gotchas:
   the contact sheet skips non-200 routes, so the 404 page needs a
   manual `browse` shot. The inactive-token check needs the `--local`
   preview, because the rules of a jsDelivr stylesheet can't be read.
6. ~~OpenDesign extraction procedure (Phase A).~~ Done 2026-10-19.
   OpenDesign connects (MCP and its local daemon). Its brand extraction
   (`POST /api/brands {url}` on the daemon; the `od brand create` CLI isn't
   on PATH, and `od` there is the Unix tool) runs a deterministic pass in
   ~5 s and writes a project: `brand.json` (7 colour roles, display/body
   font, layout), `prefetch/` (page.html, every stylesheet as styles.css,
   and material.md: colour literals ranked with their selectors), fonts
   plus a manifest with source URLs, logos, imagery, and `system/`
   (tokens derived by an antd-style algorithm from the picks: light, dark,
   compact). Opening the project in the app queues an "enrichment" agent
   run; we don't use it. **The picks are unreliable**, checked against
   the live sites: simonwillison.net got light roles from its dark
   palette and Georgia for a Helvetica Neue body; typesafe.ai/blog got
   black background and white text for a light grey-green page;
   example.com failed ("needs user assistance"); radius and spacing are
   the same `8px` defaults everywhere. So OpenDesign captures evidence
   and a new script measures. `scripts/od-capture.py <url> <dir>` finds
   the daemon (its port changes per launch), extracts, and copies the
   evidence (not `system/`, not font binaries) to
   `<dir>/reference/opendesign/`, now gitignored as `*-draft/reference/`.
   `scripts/measure-site.mjs <url>...` (gstack's Playwright, colour scheme
   emulated) writes `design-tokens.json`: per mode, roles with
   provenance, type scale with the CDP-rendered font, radii, content
   width, and the colour histograms; `dark` = media / toggle:<x> /
   dark-only / none; fonts with `webfont` and `googleFonts` (from the
   Google Fonts catalogue; the css2 API answers 200 for Helvetica Neue).
   Text roles prefer elements on the page background, and consent banners
   are hidden. Tests: `scripts/test-measure-site.py` (12, fixture pages).
   Procedure: `docs/extract-design.md`. Verified on simonwillison.net
   (light `#fdfdfd`/`#000`/link `#0303bb`, dark `#1a1a2e`/`#e8e8e8`/
   `#7eb8ff`) and typesafe.ai (`#abbab9`/`#1e1e1e`, Die Grotesk C flagged
   as a non-Google webfont), both against screenshots. Left in OpenDesign:
   the `simonwillison-77157a` test brand (the example.com one was
   deleted). Not yet: reference shots side by side with the contact
   sheet; link hover colour; the skill (step 7) should absorb the doc.
7. ~~Write the skill tying it together.~~ Done 2026-10-19 (not yet run
   cold). `.claude/skills/flowershow-theme-from-website/`: `SKILL.md`
   (setup, phases A–E, each with a done condition; stops before any
   commit), `AUTHORING.md` (phase B: token rules incl. the `[data-theme]`
   specificity trap, override rules, which sections of
   `docs/ai-theme-cloning-skill.md` still apply), and
   `examples/leaf-coverage.yaml` (the Leaf dry-run ledger). The procedures
   stay single-sourced in `docs/extract-design.md` and
   `docs/coverage-ledger.md`. The cloning doc stays published on the
   themes site (`site.sh`, `verify-site.sh` check it), so it gained a
   pointer to the skill instead of being deleted; its stale
   `--navbar-height` fact was corrected. `CLAUDE.md` points to the skill.
   Step 6 leftovers: `measure-site.mjs --shots DIR` now saves reference
   shots (each page × desktop/mobile × the site's modes, contact-sheet
   naming), tested (14 tests) and checked live on simonwillison.net; link
   hover is a manual `browse` step in `AUTHORING.md`. A cold-read review
   by a fresh agent found 10 issues; the 9 in scope were fixed. Not fixed:
   `CLAUDE.md` and the `demo-site.sh` header still say demos pin to the
   branch, though the code pins to the SHA.
8. Dry-run end-to-end on one real site the user picks; stop for approval.
   Run 2026-10-19 on https://typesafe.ai/blog (user's pick) by a fresh
   agent following the skill cold: theme `sage-draft/` (uncommitted),
   preview https://sage-theme-preview-olayway.flowershow.me (served CSS
   byte-identical to the working tree), ledger check exit 0 (15/15, 11
   gaps), about 47 min, of which Phase D took 26. Fonts: Die Grotesk C →
   Inter Tight, LisaTerminal → JetBrains Mono; dark mode fully derived.
   Self-judged fidelity: reviewed-close (LLM). OpenDesign brand
   `typesafe-457b6f` created by the run. It reported 18 skill-friction
   items (not yet fixed); the main ones: no style-compare script, a link
   role picked from a dark card, the derived dark palette with no
   contrast rule, missing core facts (`--color-foreground-600` is body
   text, `--tw-prose-*` lives on `.rendered-mdx:not(.is-plain)`, Prism's
   dark inline code beats theme selectors), contact sheet shooting
   loading skeletons, and the 404 that can't be forced dark. **Awaiting
   the user's review of the preview.**

## Open questions for the user

- ~~Which website for the first end-to-end run?~~ typesafe.ai/blog
  (user, 2026-10-19).
- ~~Skill location: this repo or `flowershow/skills`?~~ This repo
  (user, 2026-10-19).
- ~~Preview sites: `--anon` or named?~~ Named `<theme>-theme-preview`
  (user, 2026-10-17).
- ~~Should the coverage fixture gate apply to existing themes too?~~ All
  themes (user, 2026-10-17); see step 4.
