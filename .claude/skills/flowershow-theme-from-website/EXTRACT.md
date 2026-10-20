# Extracting a website's design for a theme

This is phase A of building a theme "inspired by website X". Its output
is two things in the theme's draft directory:

- `design-tokens.json`: measured values. This file is what the theme
  copies.
- `reference/opendesign/`: OpenDesign's capture of the site. It is
  evidence to read and look at, never values to copy.

Every value that goes into `theme.css` must trace back to something
measured. An agent left alone drifts towards Inter, an indigo accent and
a radius of 8px. Those are the averages of every site, so they fit none
of them.

## Why two tools

OpenDesign's brand extraction is good at **collecting** a site: the raw
CSS, the webfonts with the URLs they came from, logos and large images,
and a kit page you can look at. Its role picks (`brand.json`) are
**not reliable**. It ranks colour literals by how often they appear in
all the stylesheets, then guesses which one plays which role. Results on
three sites (2026-10-19):

- **simonwillison.net**: the light roles were filled from the dark
  palette (accent `#64387f`, which is the dark-mode purple; the real
  light one is `#8148a3`). The body font was given as Georgia, but
  Helvetica Neue renders.
- **typesafe.ai/blog**: the background was given as `#000000` and the
  text as `#ffffff`. The page is actually a light grey-green
  (`#abbab9`) with near-black text.
- **example.com**: the extraction failed with "needs user assistance".

Every site got the same radius and spacing (`8px`, "8px baseline grid"),
which means those weren't measured. And everything under its `system/`
directory is derived by an algorithm from those picks.

`scripts/measure-site.mjs` loads the live pages with `prefers-color-scheme`
emulated as light and then as dark. It reads computed styles, and asks
the browser which font actually rendered. Its picks are heuristic too,
but each value is something a visitor sees. Each comes with a `from`,
and with the histogram behind it, so a wrong pick is easy to spot and
overrule.

## Steps

`<dir>` is the theme's draft directory, `<name>-draft/`, which may not
exist yet. Put scratch output outside the repo.

1. **Pick the pages.** You need the homepage, plus one long article or
   docs page. The article is where body text, headings, links, code and
   quotes are. A Flowershow site is mostly articles, so the article page
   matters more. Done when both URLs answer with HTTP 200.
2. **Capture with OpenDesign.** The OpenDesign app must be running. Run
   `scripts/od-capture.py <homepage> <dir>`. Done when
   `<dir>/reference/opendesign/capture.json` exists.
   - If it fails with "needs user assistance", the site is behind a bot
     wall or the page is too bare. Either ask the user to open that
     brand's project in OpenDesign and let its agent finish, then re-run
     with `--brand <id>`, or go on without a capture. Capture is
     evidence only; step 3 doesn't need it.
   - Never get past a bot wall or CAPTCHA by yourself.
3. **Measure.** Run
   `node scripts/measure-site.mjs <homepage> <article> --out <dir>/design-tokens.json --shots <scratch>/reference`.
   Done when the file exists, `dark` is set, and the reference shots are
   saved (each page at desktop and mobile, in each mode the site has).
4. **Check the picks.** Open the reference shots. Check every role in
   `modes.<mode>.roles` against what you see. Where a pick is wrong (it
   came from a banner, a card or a button), replace it with the right
   colour from `candidates`, and change its `from` to say so, for example
   `"from": "overruled: sidebar tint, candidates.background[2]"`. Then
   cross-check with the capture:
   - `material.md` lists the site's own custom properties, with
     selectors. A `--color-link` under `:root`, against one under
     `[data-theme="dark"]`, confirms which palette a value belongs to.
   - `brand.json` disagreeing with you is a reason to look again, not
     a reason to change your value.

   Done when you can defend every role from a screenshot.
5. **Settle the fonts.** `fonts[]` lists each family that rendered.
   - `googleFonts: true`: the theme may `@import` it from Google Fonts.
   - `googleFonts: false` and `webfont: true`: the face is the site's own
     and probably commercial (for example Die Grotesk on typesafe.ai).
     Its source URL is in `reference/opendesign/fonts/manifest.json`.
     Pick an open stand-in that matches its build: grotesk or humanist,
     x-height, width. Record the swap in a `fontNotes` key in
     `design-tokens.json`.
   - `googleFonts: null`: the Google Fonts catalogue couldn't be fetched.
     Re-run step 3, or look the family up at fonts.google.com.
   - `googleFonts: false` and `webfont: false`: a system font, such as
     Helvetica Neue or Georgia. Use the site's own stack, since a
     system font needs no licence.

   Never copy font files out of `reference/`. See "Licensing checks" in
   `docs/ai-theme-cloning-skill.md`. Done when every family has an open
   source or a stand-in.
6. **Note what the site lacks.** Flowershow themes need a light **and** a
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

Phase B (authoring `theme.css`) starts from `design-tokens.json`. Keep
`reference/opendesign/brand.html` for the side-by-side comparison in the
hand-off.

## Gotchas

- The OpenDesign daemon's port changes every time the app starts.
  `od-capture.py` finds it, or you can set `OD_DAEMON_URL`. The `od`
  on `PATH` is the Unix octal-dump tool, not OpenDesign's CLI.
- A capture registers the brand as an OpenDesign design system. Delete
  test captures (`curl -X DELETE <daemon>/api/brands/<id>`); keep the
  one the theme is built from.
- `measure-site.mjs` uses gstack's bundled Playwright directly
  (`PLAYWRIGHT_DIR` overrides it), not the `browse` daemon. It can run
  alongside the coverage scripts.
- Framer, Webflow and similar site builders hash their token names
  (`--token-<uuid>`). For those sites, `material.md` gives you values
  and selectors, but no meaning.
- Dark modes behind a toggle are found by trying common classes and
  attributes on `<html>` (`.dark`, `[data-theme=dark]` and others). If a
  site has a toggle and `dark` still says `none`, find the mechanism in
  `prefetch/styles.css` and measure that mode by hand.
