---
title: Maintain and release themes
description: Internal workflow for reviewing previews, updating galleries, and promoting a Flowershow theme.
---

This page is the operational path for Flowershow maintainers. It complements
the public [contribution guide](/contributing) and the method in
[Authoring a Flowershow theme](/authoring).

## Where theme demos live

Demo content is versioned here:

- `_demo-content/` contains the shared kitchen sink and blog;
- `THEME-DIR/demo-landing.md` and `demo-landing.css` contain an optional
  theme-specific landing page;
- `scripts/demo-site.sh` assembles and publishes the demo;
- `docs/features.yaml` records the public URL and retired-site history.

The currently deployed sites are Flowershow-managed sites under the maintainer
account; they are not separate template repositories. Their reproducible
source is this repository. Never delete a demo without recording the deletion
and reason in `docs/features.yaml`.

## Review a contribution

1. Read `CLAUDE.md` and the theme's ledger entry.
2. Run `scripts/init.sh` in a clean checkout.
3. Run `scripts/verify.sh` without modifying the verifier.
4. Inspect the preview on desktop and mobile, in light and dark modes.
5. Compare every supported page type, not only a custom landing page.
6. Check source licenses, fonts, artwork, and attribution.
7. Confirm fidelity and known gaps are stated honestly.
8. Review the pull request as a preview contribution unless promotion was
   separately approved.

## Publish or refresh a preview

Push the exact branch commit first, then run:

```bash
scripts/demo-site.sh THEME-DIR
```

For a shipped `layout: plain` landing page:

```bash
scripts/demo-site.sh THEME-DIR --landing-page THEME-DIR/demo-landing.md
```

The script pins the theme to a commit SHA on jsDelivr. After publishing, update
`docs/features.yaml` and rerun `scripts/verify.sh`. If a live page appears
stale, verify the served commit before changing CSS; the authoring guide
documents both CDN and Flowershow cache behavior.

## Preview-to-official readiness

Run this checklist separately for each candidate. Material and code.storage
remain **Preview** until every required item is reviewed and a human explicitly
approves promotion.

Their evidence and open gates are maintained in the canonical
[preview release-readiness record](/readiness), tracked by
[flowershow/flowershow#1367](https://github.com/flowershow/flowershow/issues/1367).
Update that record when completing the checklist; do not rely on an ephemeral
review comment alone.

- [ ] Human fidelity decision is current in `docs/features.yaml`.
- [ ] Desktop and mobile layouts have been reviewed.
- [ ] Light and dark behavior has been reviewed.
- [ ] Kitchen sink, blog listing, post, navbar, sidebar, search, and landing
      surfaces have been checked.
- [ ] Font, artwork, source, and attribution licensing is acceptable.
- [ ] Final public name and directory name are approved.
- [ ] `theme.css` and the preview asset follow the public directory contract.
- [ ] Live demo and landing URLs pass `scripts/verify.sh`.
- [ ] Known Flowershow structural gaps remain accurate.
- [ ] The themes preview site and canonical Flowershow gallery changes are
      prepared.
- [ ] The Flowershow dashboard selector change is prepared.
- [ ] `.github/workflows/release.yml` release text and purge coverage include
      the theme.
- [ ] A version and changelog are agreed.
- [ ] A human explicitly authorizes the release tag.

Passing the list makes the theme eligible for promotion. It does not itself
authorize a rename, dashboard listing, tag, release, or cache purge.

## Promote and release

Only after approval:

1. rename the `-draft` directory to the approved stable name;
2. update repository gallery/site content and preview assets;
3. update the hard-coded dashboard selector in `flowershow/flowershow`;
4. update canonical Flowershow documentation when its owners choose;
5. update release metadata and jsDelivr purge coverage;
6. merge all required pull requests;
7. run the full verifier from the merged commit; and
8. create the approved version tag through the human-controlled release flow.

Never push a `v*.*.*` tag merely because the code is green. Tags are public
releases and trigger the release workflow.

## Add a theme to this gallery

For previews, add a clearly labeled card to `site/themes.md`, copy a stable
preview asset through `scripts/site.sh`, and extend `scripts/verify-site.sh`.
For official themes, also add the bare-name configuration value and complete
the promotion steps above. Rebuild and publish the preview site, then verify
its live routes before merging.
