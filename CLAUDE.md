# flowershow/themes — house rules

This repo holds Flowershow themes: pure CSS files, one directory per theme,
distributed via jsDelivr off git tags. See README.md for the user-facing
theme format. This file is for anyone (human or agent) doing unattended or
semi-unattended work in this repo.

## The done condition

```
scripts/verify.sh
```

Exit 0 = pass. Exit non-zero = fail. It checks every theme listed in
`docs/features.yaml`: CSS parses (brace-balanced), all required custom
properties are defined, a dark-mode block exists, a preview asset exists
(warning only pre-launch), and — if a `demo_url` is recorded — that the
live demo site actually responds and renders (not just "CSS is valid").

Bootstrap a fresh checkout with `scripts/init.sh` first — it checks that
`fl` (the Flowershow CLI) is installed and authenticated, since demo-site
verification depends on it. `fl login` is interactive and cannot be
automated; if init.sh fails on that step, stop and report, don't try to
work around it.

## The ledger

`docs/features.yaml`. One entry per theme/doc/skill. `passes` must always
match what `verify.sh` actually checked — never hand-flip it to `true`.
`fidelity` (does this theme actually look like its inspiration) is a
**separate, human/LLM-judged field, never a gate**. Structural correctness
and visual fidelity are different questions; don't let one stand in for
the other.

## Scope, as of 2026-08-08

Focus is **new** themes (currently: `material-draft/`, `codestorage-draft/`
— cloning mkdocs-material and code.storage), not the four existing shipped
themes (`leaf/`, `letterpress/`, `lessflowery/`, `superstack/`). Those are
explicitly out of scope for this round of work — do not edit them.

Draft themes live in `*-draft/` directories and are worked on a non-`main`
branch until explicitly promoted. `getThemeUrl()` in the main Flowershow
app supports a full URL as the `theme` config value (not just
`name@version`), so a draft can be demoed via a pinned jsDelivr URL
(`https://cdn.jsdelivr.net/gh/flowershow/themes@<branch>/<dir>/theme.css`)
without ever touching the official release list.

## Demo sites

Every theme gets a demo site, published with `fl` from the shared content
in `_demo-content/` (a fixed kitchen-sink page + a 3-post blog, so themes
are compared on identical content, not different content).

Use the script — don't do it by hand:

```sh
scripts/demo-site.sh <theme-dir> [--landing <file.html>] [--name <site-name>]

# theme applied to the shared demo content:
scripts/demo-site.sh material-draft

# same, but with a stage-1 raw-HTML landing page as index:
scripts/demo-site.sh material-draft --landing _repro/material-landing.html \
  --name material-landing-demo
```

It assembles `_demo-content/` + a `config.json` pointing `theme` at a
jsDelivr URL pinned to the **current git branch**, then publishes with `fl`.
Record the printed URL in `docs/features.yaml` and re-run `scripts/verify.sh`.

The branch must be pushed — jsDelivr can only serve what's on GitHub. The
script warns if it isn't. After changing a theme's CSS on an already-published
branch, purge the CDN:

```sh
curl -X POST https://purge.jsdelivr.net/ -H 'Content-Type: application/json' \
  -d '{"path":["/gh/flowershow/themes@<branch>/<dir>/theme.css"]}'
```

This is also the answer to "how do you preview a theme without a live
theme-switcher in the dashboard" — config.json's `theme` field is the only
switch, so a demo site per theme is the practical substitute.

Raw `.html` files publish as-is (verified), so a stage-1 Tailwind repro can
live at `index.html` on the same site as the themed Markdown pages.

## Guard rails — never do these unattended

- Never edit `leaf/`, `letterpress/`, `lessflowery/`, `superstack/`
  (existing shipped themes) — out of scope this round, see above.
- Never push to `main`, never create or push a `v*.*.*` git tag. Tagging
  is a real release (triggers `.github/workflows/release.yml`, which
  purges the public jsDelivr cache) — human-only action.
- Never edit `docs/features.yaml`'s `passes` field to make an entry look
  done without `verify.sh` actually passing for it.
- Never remove or weaken a check in `scripts/verify.sh` to make a theme
  pass — if a check seems wrong, say so and stop, don't quietly delete it.
- Never reference a commercial/non-redistributable font in a theme's
  active `--font-*` stack (see `codestorage-draft/theme.css` header for
  why this came up — BerkeleyMono). Substitute an open font and say so in
  a comment; don't silently `@import` something unlicensed.
- Never delete an `fl`-published demo site without recording the deletion
  in `docs/features.yaml`.
- **Stop and report after 3 identical consecutive `verify.sh` failures**
  on the same theme/check. That's a sign of a wrong assumption, not a
  problem three more attempts will fix.

## Judgement vs structure

"Does this theme parse and define the right tokens" is structural —
`verify.sh` owns it. "Does this theme actually look like mkdocs-material"
is judgement — it goes in `docs/features.yaml`'s `fidelity` field as
`unreviewed` / `reviewed-close` / `reviewed-off`, decided by a human
looking at the rendered demo site (or an LLM doing an explicit visual
comparison), never inferred from the structural checks passing.

## Open decisions not yet made (do not guess past these)

- Where the theme-authoring tutorial and the AI theme-cloning skill
  actually live: this repo, the main `flowershow/flowershow` docs, or
  `flowershow/skills`. Deferred until both draft themes exist and there's
  real experience to write from.
- Canonical preview-asset convention going forward (`preview.png` vs the
  `fs-<name>-<view>-<mode>.jpg` set both currently used across the
  existing four themes) — not resolved, only newly-required for themes
  promoted out of draft.
- Per-theme versioning vs the current repo-global git tags — existing
  themes are on repo-global tags; whether draft themes need their own
  versioning scheme on promotion is unresolved.

## Related

- [What's Actually Changeable in Flowershow Theming, and by Whom](https://flowershow.app/blog/2026-08-08-whats-actually-changeable-in-theming) — the L1–L4 layer analysis this work is built on.
- flowershow/flowershow#1337, #1338 — themes gallery page, semantic class list docs.
