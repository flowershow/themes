---
name: flowershow-theme-from-website
description: Builds a Flowershow theme (theme.css) inspired by a website: measures its design, authors the theme, proves every hook group was handled, publishes a preview, and stops for approval. Use when asked to create a Flowershow theme inspired by, cloned from, or looking like a site or URL.
---

# Flowershow theme from a website

Work in the `flowershow/themes` checkout. Its `CLAUDE.md` guard rails apply
throughout. The run ends at a **stop**: the user gets a preview link and a
hand-off, and nothing is committed until they approve.

Two words carry the whole procedure:

- **Measured**: every value in `theme.css` traces to `design-tokens.json`
  or to a note saying why it was derived. A value you picked because it
  looks nice is a bug, because unmeasured choices drift to the average of
  every site.
- **Deliberate**: every hook group was looked at in the render and has a
  decision in `coverage.md`. A decision made without looking, or made
  against an older render, doesn't count.

## Tools

All in `scripts/`. For flags, run a script with `--help`, or read the
header comment of a `.sh` script. The phase docs say exactly when to run
each one.

| Script | Phase | What it does |
|---|---|---|
| `measure-site.mjs` | A | Measures colours, type, radii and fonts in light and dark into `design-tokens.json`. `--shots` saves reference screenshots |
| `demo-site.sh --local` | C, D | Publishes the working-tree `theme.css` to `<name>-theme-preview` |
| `contact-sheet.py` | D | Screenshots every demo route at desktop and mobile, in light and dark. Fails on wrong mode, non-200 or mobile overflow |
| `hook-coverage.py` | D | Checks that the demo rendered every stable theme hook |
| `palette-leaks.py` | D | Finds off-palette colours, unset literal tokens and inactive theme tokens |
| `coverage-ledger.py` | D | `sync` creates `coverage.md`, and `check` gates it |
| `verify.sh` | E | The repo's structural done condition |

Run the `browse`-based ones (contact-sheet, hook-coverage, palette-leaks)
one at a time, because they share one browser.

## Setup

1. `scripts/init.sh` passes (`fl` is installed and logged in), the gstack
   `browse` binary works.
2. Pick the theme name: short, lowercase, describing the look rather than
   the site's brand. The draft lives in `<name>-draft/`. Put scratch output
   in a scratch directory outside the repo. Branch off an up-to-date
   `main` (`theme/<name>`) before writing any files.

## Phase A: extract

Follow [EXTRACT.md](EXTRACT.md). Done when
`<name>-draft/design-tokens.json` exists, you can defend every role from a
screenshot, every font has an open source or a recorded stand-in, and the
mode the site lacks is derived and marked `"derived": true`.

Run `measure-site.mjs` with `--shots <scratch>/reference` as well. It
saves the **reference shots**: each page at desktop and mobile, in each
mode the site has. They go next to the contact sheet in the hand-off.

## Phase B: author

Write `<name>-draft/theme.css` following [AUTHORING.md](AUTHORING.md):
tokens first, then only the overrides the screenshots show you need. Done
when every value is measured and the file passes `verify.sh`'s structural
checks. `verify.sh` only checks themes listed in `features.yaml`, which a
draft isn't yet, so check them by hand: the 8 `REQUIRED_TOKENS` at the
top of `verify.sh` are all set, and a `:root[data-theme="dark"]` block
exists.

## Phase C: preview and compare

1. Publish with `scripts/demo-site.sh <name>-draft --local`. Done when the
   URL that `fl` prints for `<name>-theme-preview` serves the current
   `theme.css`.
2. Compare the preview with the site using **computed styles**, not by
   eye: body text, h1, h2, link, inline code, code block, blockquote, page
   background, in both modes. The method is in the cloning doc's "Never
   judge fidelity by eye" section (see AUTHORING.md). Fix `theme.css` and
   republish until every difference is either fixed or something CSS
   can't reach (see "structural ceiling" in AUTHORING.md). Done when you
   can list each remaining difference with its reason.

## Phase D: coverage

Follow [docs/coverage-ledger.md](../../../docs/coverage-ledger.md) from its
step 1, against the final render. A worked example (Leaf, 15 groups,
10 gaps) is in [examples/leaf-coverage.md](examples/leaf-coverage.md).
Done when `scripts/coverage-ledger.py check <name>-draft` exits 0. If you change `theme.css` here, go back to
Phase C step 1.

## Phase E: stop, then release on approval

**Stop** and hand the user:

- the preview URL;
- the contact sheet's `index.html`, with the reference shots beside it;
- the `coverage-ledger.py check` table and its `GAP` lines;
- font swaps, derived palettes, and the differences left over from
  Phase C;
- a fidelity verdict, labelled as LLM-judged and not a human review.

Commit, push and publish nothing until the user says they're satisfied.
Changes they ask for send you back to Phase B. After approval:

1. Commit `<name>-draft/` (theme.css, design-tokens.json, coverage.md) on the `theme/<name>` branch, then push the
   branch.
2. Publish the real demo with `scripts/demo-site.sh <name>-draft`, which
   pins the theme to the pushed commit.
3. Add the theme to `docs/features.yaml` (copy an existing entry's shape)
   with `demo_url`, `inspiration` and `fidelity: unreviewed`. Run
   `scripts/verify.sh`, and set `passes`/`checks` from what it actually
   reported.
4. Commit, push, and open a PR against `main`. Tagging a release stays
   with a human.
