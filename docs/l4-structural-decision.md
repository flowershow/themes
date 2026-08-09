# L4 decision: what to do about the fixed component skeleton

Status: **default call made 2026-08-09, not a final human decision.** This
documents the choice and its reasoning so a human can accept, override, or
revisit it — it is not a substitute for that review.

## The problem

Building `material-draft/` and `codestorage-draft/` confirmed three things
that no theme can clone, because the underlying component doesn't exist in
Flowershow core (checked against the actual component source, not assumed):

- **Tabbed content blocks** — mkdocs-material-style content tabs. No
  component renders this at all.
- **Prev/next page footer pagination.** Not present in `page.tsx`.
- **A version selector.** Not core to most sites' look, but confirmed
  absent too.

These are logged individually in `docs/features.yaml`
(`structural_findings: no-content-tabs`, `no-prev-next-pagination`). This
doc is about what to *do* about the pattern, not the individual items.

The underlying cause (see [What's Actually Changeable in Flowershow
Theming, and by
Whom](https://flowershow.app/blog/2026-08-08-whats-actually-changeable-in-theming)):
Flowershow's theming surface is L1 (tokens) + L2 (semantic CSS classes) +
L3 (`config.json`). There is no L4 — no way for a theme or config to
change *which components render or in what order/slots*. A theme can
restyle every pixel of what's there; it cannot add a component that isn't,
or reorder the ones that are.

## Three options

1. **Accept the fixed skeleton and document it honestly.** Themes clone
   what CSS can clone (L1/L2/L3), list what they can't as `known_gaps` in
   the ledger, and that's the whole scope of "theme" going forward. No core
   changes.
2. **Add slot/block ordering.** Give `page.tsx` (and equivalents) a
   config-driven way to reorder or omit existing blocks — still no *new*
   component types, but themes/configs could e.g. move pagination above
   content or hide a sidebar per-page. Smaller core change than (3).
3. **Full layout templating.** Let a theme (or per-page config) supply
   real alternate component trees — closer to how e.g. Hugo/Jekyll themes
   can restructure a page, not just restyle it. Largest core change; would
   make tabs/pagination/version-selectors themeable, but is a genuine
   Flowershow architecture decision, not a themes-repo one.

## Default call for this pass: option 1

Accepted the fixed skeleton and documented it — no core-app changes were
made. Reasoning:

- Options 2 and 3 are changes to `flowershow/flowershow` (the app core),
  not this repo. Making either unsupervised, without a human weighing the
  architectural tradeoff, would be exactly the kind of irreversible,
  cross-repo, unauthorized-scope action the house rules in `CLAUDE.md` and
  the autonomous-loop guidance both warn against — this isn't a themes
  question, it's a product-architecture one with consequences (API
  surface, every existing theme's behavior, docs) well beyond what's in
  scope here.
- Option 1 costs nothing beyond honest documentation, which was already
  the house style (`known_gaps` per theme, `structural_findings` in the
  ledger) before this decision was made explicit.
- Nothing found while building either draft theme was blocked *only* by
  the lack of slot ordering specifically (option 2) rather than by the
  lack of the component entirely (which options 2 and 3 both require) —
  so there's no evidence yet that the smaller option 2 change would have
  unblocked anything on its own.

## What would change this default

If a future theme clone is blocked specifically by *ordering* (component
exists, but in the wrong place/slot) rather than by a *missing* component,
that's a concrete data point for option 2 specifically, worth escalating.
If several future clones are blocked by missing components, that's a case
for a human to weigh option 3 against just continuing to document gaps.
Either way, this is a decision to bring to a human with real examples, not
one to make speculatively.
