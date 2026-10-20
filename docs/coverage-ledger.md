# Filling a theme's coverage ledger

`<theme-dir>/coverage.yaml` records one **deliberate** decision for every
group of stable theme hooks: the theme styles it, or you looked and the
default theme plus the theme's tokens already get it right, or it is a
known gap. Deliberate means you saw the render. The ledger is what lets a
theme hand-off claim "nothing forgotten", so a decision written without
looking is worse than `todo`.

The scripts own the mechanics. `scripts/coverage-ledger.py` creates the
file, keeps its groups in step with core, and checks it. Its `--help`
and header comment define the format.

## Decisions

- **styled**: `theme.css` selects at least one hook in the group. The
  check enforces that. The note says what the styling does and which of
  the group's surfaces you checked.
- **inherits-ok**: `theme.css` selects none of the group's hooks, and in
  the screenshots the group reads as part of this theme: its colours,
  type and radius. The note names the routes and modes you looked at.
- **gap**: the group, or part of it, still looks like the default theme
  or is broken. For a part, keep the group's decision and add a `gaps:`
  entry (hook pattern → what is wrong). Gaps pass the check, and the
  hand-off lists them. An honest gap beats a hopeful `inherits-ok`.

A group can be `styled` and still have gaps, for example cards styled
while pagination is left in the default grey. Record that as `styled`
plus a `gaps:` entry for `list-component-pagination*`.

## Steps

Run the browser scripts one at a time, because they share one `browse`
daemon. Put their output in a scratch directory rather than the repo.

1. **Publish the working tree.** Run `scripts/demo-site.sh <dir> --local`
   and wait 10–20 s. Done when the printed preview URL serves the
   current `theme.css`.
2. **Gather the evidence.** For `<url>`, run all three:
   - `scripts/contact-sheet.py <url> --out <scratch>/sheet`
   - `scripts/hook-coverage.py <url> --json <scratch>/hooks.json`
   - `scripts/palette-leaks.py <url> <dir> --json <scratch>/leaks.json`

   Done when hook-coverage exits 0. If it doesn't, the demo content is
   missing a surface, which is a fixture problem and not the theme's.
   Fix that first (see `CLAUDE.md`, Demo sites).
3. **Sync the ledger.** Run `scripts/coverage-ledger.py sync <dir>`. Done
   when every core group is in the file.
4. **Decide each group.** For each group, `hooks.json` lists the routes
   and viewports where its hooks rendered (`groups.<id>.rendered`).
   Open those shots in the contact sheet in both modes. The shots are
   named `<route-slug>--<viewport>-<mode>.png`. Check the group's
   `leaks.json` entries (`by_group.<id>`). Then write the decision and
   a note that names the routes and modes you looked at. Done when no
   group says `todo`.

   Some routes have no shot because the contact sheet only takes pages
   that return 200: the 404 page (`errors`) and `/tags/no-such-tag`.
   Screenshot those with `browse` (`goto`, then `screenshot`). Search
   can't render on the demos (flowershow/flowershow#1370), so record it
   as a `gap` that says it wasn't reviewed.
5. **Decide the tokens.** `palette-leaks.py` ends with two token lists.
   - **Inactive theme tokens**: tokens the theme sets but the page never
     uses. Usually core sets the same token on
     `:root[data-theme="light"]` / `[data-theme="dark"]`, which beats a
     bare `:root`. Every one is a bug. Fix it in `theme.css`, or record
     it as a gap. This list needs the `--local` preview, because the
     browser can't read a jsDelivr stylesheet's rules.
   - **Unset literal tokens**: tokens holding a hard-coded colour that
     this theme doesn't set, such as tag-pill pinks, callout colours,
     code backgrounds, the default accent, danger and warning. For each
     one, either set it in `theme.css`, or record it as fine or as a gap
     in the note of the group that shows it (tag pills → `tags`,
     callouts and code → `content`).

   Done when every token in both lists is accounted for, either in
   `theme.css` or in a note.
6. **Check.** Run `scripts/coverage-ledger.py check <dir> --leaks
   <scratch>/leaks.json`. Done when it exits 0 and each `WARN` line is
   resolved: either the theme now covers it, or the group's note
   explains why the off-palette colour is right (for example, syntax
   highlighting kept on purpose).
7. **Hand off.** Include check's table and its `GAP` lines in the
   hand-off, next to the preview URL and the contact sheet.

After any change to `theme.css`, repeat from step 1. A decision made
against an older render no longer counts as deliberate.
