# Themes Preview Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish a Flowershow preview site that makes themes equally easy to choose and to build.

**Architecture:** Keep hand-authored navigation and gallery content in `site/`, retain canonical long-form authoring sources in `docs/`, and assemble a publishable directory through `scripts/site.sh`. A verifier checks content, assets, preview labels, reused guides, links, and the optional live deployment without adding a frontend build system.

**Tech Stack:** Flowershow Markdown content, JSON configuration, POSIX shell, `fl` CLI, `curl`

## Global Constraints

- The existing Flowershow `/docs/reference/themes` page remains unchanged and canonical for now.
- The preview site is a parallel experiment with equal “choose” and “build” paths.
- Material and code.storage are labeled preview/beta everywhere.
- Do not add preview themes to the Flowershow dashboard selector.
- Do not rename preview directories, create tags, or publish a themes release.
- Reuse the two existing long-form guides; do not maintain divergent copies.
- Do not delete or replace existing demo sites.
- Use a preview deployment name that does not imply canonical status.

---

### Task 1: Define the site contract with a failing verifier

**Files:**
- Create: `scripts/verify-site.sh`
- Modify: `scripts/verify.sh`

**Interfaces:**
- Consumes: `site/`, repository theme directories, and optional `SITE_URL`
- Produces: exit 0 only when site sources and optional live pages are complete

- [ ] **Step 1: Write `scripts/verify-site.sh`**

The executable shell script accumulates failures and checks:

- required source pages and `config.json` exist;
- JSON parses;
- home contains and links both `Choose a theme` and `Build a theme`;
- all six theme names occur in the gallery;
- four shipped themes say `Official` and two new themes say `Preview`;
- every gallery image resolves in an assembled site;
- the two canonical long-form guides appear in an assembled site; and
- when `SITE_URL` is set, six required public routes return HTTP 200.

- [ ] **Step 2: Call the site verifier from `scripts/verify.sh`**

Append without weakening existing checks:

```sh
if [ -d "$ROOT/site" ]; then
  "$ROOT/scripts/verify-site.sh"
fi
```

- [ ] **Step 3: Prove the test fails before implementation**

```bash
scripts/verify-site.sh
```

Expected: non-zero with clear missing-`site/` messages.

- [ ] **Step 4: Commit the failing contract**

```bash
git add -- scripts/verify-site.sh scripts/verify.sh
git commit -m "test: define themes preview site contract"
```

### Task 2: Implement repeatable site assembly

**Files:**
- Create: `scripts/site.sh`
- Create: `site/config.json`
- Create: `site/.gitignore`
- Modify: `scripts/verify-site.sh`

**Interfaces:**
- Consumes: `site/`, both canonical guides, and six preview assets
- Produces: `build OUTPUT_DIR` and `publish [SITE_NAME]` commands

- [ ] **Step 1: Add a failing assembly test**

In `verify-site.sh`, use `mktemp -d` and a trap, call
`scripts/site.sh build "$tmp_dir"`, then require:

```text
config.json
index.md
themes.md
authoring.md
ai-theme-cloning.md
contributing.md
maintainers.md
status.md
assets/themes/letterpress.png
assets/themes/superstack.jpg
assets/themes/lessflowery.jpg
assets/themes/leaf.png
assets/themes/material-preview.png
assets/themes/codestorage-preview.png
```

- [ ] **Step 2: Run and confirm failure**

```bash
scripts/verify-site.sh
```

Expected: non-zero because `scripts/site.sh` does not exist.

- [ ] **Step 3: Implement `scripts/site.sh`**

Support exactly:

```text
scripts/site.sh build OUTPUT_DIR
scripts/site.sh publish [site-name]
```

`build` rejects an existing non-empty output directory, copies `site/`, copies
the canonical guides as `authoring.md` and `ai-theme-cloning.md`, and copies
six selected preview images to the stable names above. `publish` runs init and
verification, assembles in `mktemp -d`, invokes
`fl ASSEMBLED_DIR --name SITE_NAME --yes`, defaults to
`flowershow-themes-preview`, and
prints the resulting URL without exposing credentials.

- [ ] **Step 4: Add site configuration**

Create valid `site/config.json` titled `Flowershow Themes Preview`, with nav
links for Themes, Build a theme, AI workflow, Contributing, and Maintainers.
Use no custom theme dependency.

- [ ] **Step 5: Verify partial success and commit**

```bash
scripts/verify-site.sh
git add -- scripts/site.sh scripts/verify-site.sh site/config.json site/.gitignore
git commit -m "feat: add repeatable themes site assembly"
```

Expected: assembly and JSON pass; only remaining content checks fail.

### Task 3: Build the dual-path home and full gallery

**Files:**
- Create: `site/index.md`
- Create: `site/themes.md`
- Modify: `scripts/verify-site.sh`

**Interfaces:**
- Consumes: six themes, preview assets, live demos, and theme config syntax
- Produces: the public choose/build entry and complete theme catalog

- [ ] **Step 1: Add failing content assertions**

Require home links to `/themes` and `/authoring`; shipped themes to say
`Official`; preview themes to say `Preview`; every theme to contain a demo URL
and config value; preview config to use a full URL; and gallery to link to
`/contributing`.

- [ ] **Step 2: Run and confirm failure**

```bash
scripts/verify-site.sh
```

Expected: home/gallery assertions fail.

- [ ] **Step 3: Write `site/index.md`**

Add a concise hero and two equal cards:

- `Choose a theme` → `/themes`
- `Build a theme` → `/authoring`

Explain that this is a preview of a dedicated themes home and link the current
canonical Flowershow reference gallery.

- [ ] **Step 4: Write `site/themes.md`**

Create consistent sections/cards for Letterpress, Superstack, LessFlowery,
Leaf, Material, and code.storage. Include name, status, preview image, use case,
demo, configuration, and attribution. Preview configurations use explicit full
theme URLs and never imply dashboard availability.

- [ ] **Step 5: Verify and commit discovery content**

```bash
scripts/verify-site.sh
git add -- site/index.md site/themes.md scripts/verify-site.sh
git commit -m "feat: add themes preview gallery"
```

Expected: discovery checks pass; author-path pages remain failing.

### Task 4: Build contributor and maintainer paths

**Files:**
- Create: `site/contributing.md`
- Create: `site/maintainers.md`
- Create: `site/status.md`
- Modify: `scripts/verify-site.sh`

**Interfaces:**
- Consumes: assembled guides, repository scripts, ledger, release workflow,
  and successor epic URL
- Produces: complete public contribution and internal promotion instructions

- [ ] **Step 1: Add failing workflow assertions**

Require assembled content to mention `scripts/init.sh`, `scripts/verify.sh`,
`scripts/demo-site.sh`, `docs/features.yaml`, `theme.css`, preview, pull
request, release, and jsDelivr. Require status to link the successor and label
both new themes as preview.

- [ ] **Step 2: Run and confirm failure**

```bash
scripts/verify-site.sh
```

Expected: missing author-path files and workflow anchors fail.

- [ ] **Step 3: Write `site/contributing.md`**

Cover fork/branch, directory structure, local checks, preview/demo, fidelity
notes, assets, PR, and review. Link the assembled full authoring and AI pages.

- [ ] **Step 4: Write `site/maintainers.md`**

Cover verification, preview publishing, ledger updates, preview/official
decision, promotion-only rename, dashboard/gallery/release metadata, and the
explicit approval required before tags. Include the readiness checklist for
Material and code.storage.

- [ ] **Step 5: Write `site/status.md`**

State that the site is experimental, the main reference remains canonical,
both new themes remain previews, and work is tracked in the successor epic.

- [ ] **Step 6: Verify and commit authoring content**

```bash
scripts/verify-site.sh
scripts/verify.sh
git add -- site/contributing.md site/maintainers.md site/status.md scripts/verify-site.sh
git commit -m "docs: add theme contribution and maintenance paths"
```

Expected: all local site and existing theme checks pass.

### Task 5: Publish and integrate the preview

**Files:**
- Modify: `README.md`
- Modify: `NEXT.md`
- Modify: `site/status.md`

**Interfaces:**
- Consumes: complete assembled site and authenticated `fl`
- Produces: live preview URL, repository discovery links, and merged PR

- [ ] **Step 1: Review a local assembly**

```bash
site_build_dir=$(mktemp -d)
scripts/site.sh build "$site_build_dir"
find "$site_build_dir" -maxdepth 3 -type f -print | sort
scripts/verify-site.sh
scripts/verify.sh
```

Expected: complete file list and all checks pass. Remove only the exact
temporary directory after review.

- [ ] **Step 2: Publish using the preview name**

```bash
scripts/site.sh publish flowershow-themes-preview
```

Expected: `fl` prints a successful public URL.

- [ ] **Step 3: Verify the exact live URL**

```bash
SITE_URL="https://flowershow-themes-preview-rufuspollock.flowershow.me" \
  scripts/verify-site.sh
```

Expected: home, themes, authoring, AI workflow, contributing, and maintainer
pages all return HTTP 200.

- [ ] **Step 4: Record and republish the URL**

Add it to `README.md`, `NEXT.md`, `site/status.md`, and the successor epic.
Republish with the same name, rerun live verification, and run `scripts/verify.sh`.

- [ ] **Step 5: Commit deployment metadata**

```bash
git add -- README.md NEXT.md site/status.md
git commit -m "docs: record themes preview site"
```

- [ ] **Step 6: Push and open a non-draft PR**

```bash
git push -u origin feat/themes-preview-site
gh pr create --repo flowershow/themes --base main --head feat/themes-preview-site \
  --title "feat: add Flowershow themes preview site" \
  --body "Builds and publishes a dual-path themes preview site for choosing and authoring themes, with repeatable assembly and verification. Material and code.storage remain previews."
```

- [ ] **Step 7: Await checks, merge, and verify `main`**

Run `gh pr checks --watch`, merge normally with branch deletion, switch to
`main`, pull with `--ff-only`, then run local and live site verification.

Expected: merged PR, clean local `main`, passing checks, healthy live preview.
