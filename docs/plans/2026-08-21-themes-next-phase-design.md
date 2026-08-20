# Flowershow themes: next-phase design

Date: 2026-08-21
Status: approved design; implementation not yet started
Tracking home: `flowershow/flowershow` GitHub issues

## Outcome

Close the completed August theme-cloning project cleanly, then establish a
single next-phase epic for making Flowershow themes easier to discover and
easier to create.

The first visible product will be a deployable Flowershow site in this
repository's `site/` directory. It will serve two audiences equally:

1. people choosing and previewing a theme; and
2. people building, contributing, and maintaining themes.

The existing Flowershow reference gallery remains unchanged and canonical for
now. The new site is a parallel experiment. Which surface becomes canonical is
explicitly deferred until the new site is live and has been evaluated.

## Why this phase exists

The August 8–10 work achieved its original core goals:

- built and verified Material-inspired and code.storage-inspired draft themes;
- derived a human theme-authoring tutorial and an AI-oriented workflow;
- documented the boundary between CSS theming and structural layout changes;
- improved the main Flowershow themes reference page; and
- filed concrete core defects discovered during theme development.

The remaining work is no longer primarily "clone two themes." It is to turn
those results into a coherent discovery, authoring, contribution, and release
experience. Continuing to use the old session issue and stale `NEXT.md` would
hide that change in purpose.

## Chosen approach

### Closeout first, then build the preview site

This is preferred over either building the site before cleaning up tracking or
only expanding documentation. It gives the new work one current source of
truth without delaying the concrete product work.

The sequence is:

1. create the successor epic in `flowershow/flowershow`;
2. update the historical blog post and local `NEXT.md` to point to current
   outcomes and the successor;
3. close completed issues with evidence and successor links;
4. build and publish the themes-site preview;
5. evaluate it before changing the role of the existing Flowershow reference
   gallery; and
6. promote preview themes only after a separate readiness decision.

### Alternatives considered

- **Site first, tracking later:** faster to start coding, but leaves agents and
  humans following stale issue comments and `NEXT.md` while the purpose has
  already changed.
- **Documentation only:** cheaper, but does not create the visual discovery
  surface or a testable home for the contributor journey.

## Tracking and closeout

All issues remain in `flowershow/flowershow` for now, even when implementation
lives in `flowershow/themes`. Cross-repository paths and pull requests should
be linked from the epic.

### Successor epic

Create one epic covering these workstreams:

1. **Theme discovery site** — deployable `themes/site/`, gallery, theme detail
   pages, preview labels, and live-demo links.
2. **Theme authoring hub** — full human guide, AI workflow, contribution path,
   and internal maintenance/release instructions.
3. **Preview-theme readiness** — make Material and code.storage easy to try,
   while retaining preview/beta status until the final release gate.
4. **Flowershow integration** — document the eventual changes needed for
   dashboard selection, release metadata, and galleries. Do not change the
   existing `/docs/reference/themes` page during this phase.
5. **Theme-author API documentation** — retain #1338 as a separate linked child
   issue and complete it as near-term work for the authoring path.

The epic must state explicit non-goals:

- no L4 layout templating or slot-ordering implementation;
- no decision yet about whether the new site replaces the reference gallery;
- no official release of Material or code.storage without a later readiness
  decision; and
- no broad implementation sweep of the historical #854 epic.

### Existing issue disposition

- **#1339:** close as completed. Summarize the merged work, link themes PR #8,
  the authoring documents, structural findings, and successor epic.
- **#1337:** close as substantially delivered by the current visual themes
  reference page. Link the deployed page and successor epic for the parallel
  themes-site experiment.
- **#1338:** keep open as a linked, near-term child of the successor epic.
- **#854:** keep open. Perform only a bounded triage and link high-priority
  independent issues from the successor if directly relevant.
- **#1348:** keep separate from this phase; it is a focused core CSS defect.

### Historical blog update

Update
`content/flowershow-app/blog/2026-08-08-whats-actually-changeable-in-theming.md`
near the top with a short dated follow-up note linking:

- the completed #1339 project;
- the successor epic;
- the current Flowershow themes reference gallery; and
- the resulting authoring material where useful.

Do not rewrite the historical argument. The note should make the post's
current status discoverable without making old prose pretend it was written
after the follow-up work.

## Preview-site product design

### Information architecture

The home page presents two equally prominent routes:

- **Choose a theme**
- **Build a theme**

Neither audience is treated as secondary. A visitor should be able to identify
the relevant route from the first screen.

The initial site contains:

- home page;
- theme gallery;
- one detail page per listed theme, or an equivalently clear gallery-detail
  pattern if Flowershow's content model makes separate pages unnecessarily
  repetitive;
- authoring overview;
- full human theme-authoring guide;
- AI-assisted theme-cloning workflow;
- contributing guide;
- maintainer guide for adding, previewing, promoting, listing, and releasing a
  theme; and
- a compact status/roadmap page linking the successor epic.

### Theme catalog

The gallery includes:

- Letterpress;
- Superstack;
- LessFlowery;
- Leaf;
- Material (preview/beta); and
- code.storage (preview/beta).

Official and preview status must be visually and textually unambiguous.
Preview themes link to their current live demos and can be tried with explicit
full theme URLs. They must not be added to the dashboard selector or presented
as released themes during this phase.

Catalog information should have one repository-local source of truth that the
site can render or that can be mechanically checked against the rendered
content. Avoid creating several hand-maintained lists that can silently drift.
The implementation plan will choose the smallest mechanism supported cleanly
by Flowershow.

### Authoring content

The site publishes the full human guide and AI workflow as browsable pages,
not merely links to Markdown on GitHub. Existing material in
`docs/theme-authoring-tutorial.md` and `docs/ai-theme-cloning-skill.md` should
be reused rather than rewritten from scratch.

The contributor and maintainer instructions must answer, end to end:

1. how to create a theme directory;
2. how to run local and structural verification;
3. how to publish and inspect a preview demo;
4. how to record fidelity and known gaps;
5. how a contribution is reviewed;
6. how a preview becomes official;
7. how a theme is added to the site and Flowershow UI/docs; and
8. how a repository release/tag affects jsDelivr distribution.

The semantic-class reference tracked in #1338 is part of making this path
credible, but remains its own implementation issue because its source and
drift-checking mechanism live in the main Flowershow repository.

### Deployment

`site/` is a normal Flowershow content directory with its own `config.json`.
It should be publishable with `fl` using a documented repository command. The
first deployment is a preview and should use a name that does not imply it has
already replaced the canonical Flowershow documentation.

Publishing must be repeatable. Record the selected site name and public URL in
the repository, along with the exact publish command and any prerequisites.
Do not delete or replace existing demo sites as part of this work.

## Preview-theme release boundary

Material and code.storage have passed the current structural and live-demo
verifier and received an informal human visual check. They remain preview/beta
because promotion has repository-wide effects that have not yet been reviewed
as a release unit.

The epic will define a release-readiness checklist including at least:

- current human fidelity decision recorded in `docs/features.yaml`;
- final public names and directory names;
- licensing and attribution review;
- representative desktop/mobile and light/dark review;
- live demo health;
- documentation and preview assets;
- dashboard selector changes in `flowershow/flowershow`;
- themes gallery/site changes;
- release-workflow metadata; and
- an explicit human decision to tag/release.

Passing the checklist makes the themes eligible for a separate promotion
decision. It does not automatically authorize a tag or release.

## #854 triage boundary

Review #854 and its open children once, categorizing each as:

- directly relevant to the successor epic;
- independent and already well tracked; or
- stale/needs later product triage.

Only directly relevant dependencies may be linked into the successor epic.
Do not turn this bounded review into implementation of unrelated theme,
template, or core-UI requests.

## Autonomous execution rules

Routine decisions should not block progress. Use the following defaults:

- prefer reversible additions over migrations;
- preserve existing public URLs and docs;
- use branches and pull requests rather than direct pushes to `main`;
- keep preview status explicit;
- reuse existing content and assets;
- run repository verification before and after integration; and
- log non-blocking uncertainties in `docs/decisions.md` or the successor epic
  instead of stopping implementation.

Stop only for a consequential blocker such as missing credentials, an
irreversible release/tag decision, destructive changes to public sites, a
material licensing problem, or a choice that would contradict this design.

## Verification and acceptance

The phase is successful when:

- #1339 and #1337 are closed with evidence and successor links;
- the historical blog has a prominent, accurate follow-up note;
- `NEXT.md` points to the successor epic and no longer claims completed checks
  are pending;
- the successor epic is the clear tracking home in `flowershow/flowershow`;
- `themes/site/` publishes successfully as a live preview;
- all six themes appear with accurate status and working previews/demos;
- both audience paths expose useful, complete content;
- contribution and maintainer workflows are documented end to end;
- #1338 and any relevant #854 follow-ups are linked without being conflated
  with L4 research; and
- repository verification passes without weakening existing checks.

## Deferred decisions

Record these for evaluation after the preview is live:

- whether the themes site or `/docs/reference/themes` becomes canonical;
- whether either preview theme should be officially promoted;
- whether authoring content should ultimately move, be generated, or remain
  site-local;
- whether a catalog file should later drive the dashboard and both galleries;
  and
- whether Flowershow should support L4 slot ordering or layout templating.
