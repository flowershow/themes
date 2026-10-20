# Extracting a website's design for a theme

This is phase A of building a theme "inspired by website X". Its output
is `design-tokens.json` in the theme's draft directory: measured values,
which the theme copies.

Every value that goes into `theme.css` must trace back to something
measured. An agent left alone drifts towards Inter, an indigo accent and
a radius of 8px. Those are the averages of every site, so they fit none
of them.

`scripts/measure-site.mjs` loads the live pages with `prefers-color-scheme`
emulated as light and then as dark. It reads computed styles, and asks
the browser which font actually rendered. Don't rank colour literals from
the site's stylesheets instead: tried on three sites (2026-10-19), that
filled the light roles from the dark palette on simonwillison.net and
made typesafe.ai's light grey-green page black. The script's picks are
heuristic too, but each value is something a visitor sees. Each comes
with a `from`, and with the histogram behind it, so a wrong pick is easy
to spot and overrule.

## Steps

`<dir>` is the theme's draft directory, `<name>-draft/`, which may not
exist yet. Put scratch output outside the repo.

1. **Pick the pages.** You need the homepage, plus one long article or
   docs page. The article is where body text, headings, links, code and
   quotes are. A Flowershow site is mostly articles, so the article page
   matters more. Done when both URLs answer with HTTP 200.
2. **Measure.** Run
   `node scripts/measure-site.mjs <homepage> <article> --out <dir>/design-tokens.json --shots <scratch>/reference`.
   Done when the file exists, `dark` is set, and the reference shots are
   saved (each page at desktop and mobile, in each mode the site has).
3. **Check the picks.** Open the reference shots. Check every role in
   `modes.<mode>.roles` against what you see. Where a pick is wrong (it
   came from a banner, a card or a button), replace it with the right
   colour from `candidates`, and change its `from` to say so, for example
   `"from": "overruled: sidebar tint, candidates.background[2]"`. If a
   role is still unclear, read the site's stylesheets: a `--color-link`
   under `:root`, against one under `[data-theme="dark"]`, confirms which
   palette a value belongs to.

   Done when you can defend every role from a screenshot.
4. **Settle the fonts.** `fonts[]` lists each family that rendered.
   - `googleFonts: true`: the theme may `@import` it from Google Fonts.
   - `googleFonts: false` and `webfont: true`: the face is the site's own
     and probably commercial (for example Die Grotesk on typesafe.ai).
     Its source URL is in the site's `@font-face` rules.
     Pick an open stand-in that matches its build: grotesk or humanist,
     x-height, width. Record the swap in a `fontNotes` key in
     `design-tokens.json`.
   - `googleFonts: null`: the Google Fonts catalogue couldn't be fetched.
     Re-run step 2, or look the family up at fonts.google.com.
   - `googleFonts: false` and `webfont: false`: a system font, such as
     Helvetica Neue or Georgia. Use the site's own stack, since a
     system font needs no licence.

   Never copy the site's font files. See "Licensing checks" in
   `docs/ai-theme-cloning-skill.md`. Done when every family has an open
   source or a stand-in.
5. **Note what the site lacks.** Flowershow themes need a light **and** a
   dark mode.
   - `dark: "none"`: the theme must design a dark palette.
   - `dark: "dark-only"`: the theme must design a light one.

   Derive the missing palette from the measured one (same hues, inverted
   lightness). Write it into the empty `modes.light` or `modes.dark`,
   with the same role keys as the measured mode, and add
   `"derived": true` to each role you invent. Many
   Flowershow surfaces have no counterpart on the site: callouts, tags,
   tables, the TOC, footnotes. Take those from the nearest measured role,
   not from the default theme.

Phase B (authoring `theme.css`) starts from `design-tokens.json`.

## Gotchas

- `measure-site.mjs` uses gstack's bundled Playwright directly
  (`PLAYWRIGHT_DIR` overrides it), not the `browse` daemon. It can run
  alongside the coverage scripts.
- Framer, Webflow and similar site builders hash their token names
  (`--token-<uuid>`). For those sites, the stylesheets give you values
  and selectors, but no meaning.
- Dark modes behind a toggle are found by trying common classes and
  attributes on `<html>` (`.dark`, `[data-theme=dark]` and others). If a
  site has a toggle and `dark` still says `none`, find the mechanism in
  the site's stylesheets and measure that mode by hand.
