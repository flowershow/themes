# Monospace Restrained Showcase Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the oversized generic Monospace homepage with a compact, text-heavy, two-column technical landing page without changing any other theme homepage.

**Architecture:** Keep the validated metadata renderer but move homepage markup ownership into `codestorage-draft/demo-showcase.template.md`. Standardize demo routes and verification rather than universal homepage HTML. The theme-local CSS supplies the restrained visual language and remains scoped under `.cs-landing`.

**Tech Stack:** Markdown/semantic HTML, scoped CSS, Python standard-library renderer/tests, Bash demo assembly, Flowershow CLI.

## Global Constraints

- Change only the Monospace homepage; Material and official theme homepages remain untouched.
- Keep the real Flowershow navbar and do not add `<header>` or `<nav>` inside the page.
- Keep a two-column opening on desktop and text-first single-column flow on mobile.
- Keep H1 at 17–20px, section headings at 15–17px, and body copy at 13–15px.
- Render visible `#` and `##` heading markers with CSS.
- Use linear text, lists, code and links; no card grid, dark promo band, boxed steps or oversized CTA.
- Use only Flowershow-owned copy and CSS-authored imagery; no copied reference identity, assets or claims.
- Keep Monospace in Preview and preserve `/`, `/landing`, kitchen sink and blog routes.

---

### Task 1: Give Monospace ownership of its homepage structure

**Files:**
- Create: `codestorage-draft/demo-showcase.template.md`
- Delete: `_demo-content/theme-showcase.template.md`
- Modify: `scripts/demo-site.sh`
- Modify: `scripts/verify-landing-fixtures.py`
- Modify: `scripts/test-render-theme-showcase.py`

**Interfaces:**
- Consumes: `codestorage-draft/demo-showcase.json` and `scripts/render-theme-showcase.py`.
- Produces: theme-local template rendering to identical `index.md` and `landing.md`.

- [ ] **Step 1: Write failing ownership and structure tests**

Update `scripts/test-render-theme-showcase.py` to require the repository template at `codestorage-draft/demo-showcase.template.md`, require build-only output to contain compact linear section markers, and reject `ts-card-grid`, `ts-benefits`, `ts-steps`, and `ts-final-cta` in the rendered page.

- [ ] **Step 2: Run the tests and verify RED**

Run: `python3 scripts/test-render-theme-showcase.py`

Expected: FAIL because the theme-local template does not exist and the shared template still contains card/promo structures.

- [ ] **Step 3: Add the local semantic template and assembly path**

Create one raw-HTML block containing:

- `.ts-hero-grid` with `.ts-hero-copy` and `.ts-hero-art`;
- compact Preview/name/headline/description/product copy;
- understated kitchen-sink and publishing links;
- linear `.ts-document` sections for publishing uses, Flowershow benefits, three publishing steps, theme description, source and publishing links;
- the existing CSS node/orbit illustration markup.

Change `scripts/demo-site.sh` and `scripts/verify-landing-fixtures.py` to render `THEME-DIR/demo-showcase.template.md`. Remove the unused shared template.

- [ ] **Step 4: Run tests and verify GREEN**

Run:

```bash
python3 scripts/test-render-theme-showcase.py
python3 scripts/verify-landing-fixtures.py
```

Expected: all tests and fixture contracts pass.

- [ ] **Step 5: Commit**

```bash
git add -- codestorage-draft/demo-showcase.template.md _demo-content/theme-showcase.template.md scripts/demo-site.sh scripts/verify-landing-fixtures.py scripts/test-render-theme-showcase.py
git commit -m "refactor: make Monospace showcase theme-specific"
```

### Task 2: Restore the restrained Monospace visual language

**Files:**
- Modify: `codestorage-draft/demo-landing.css`
- Modify: `scripts/test-render-theme-showcase.py`
- Modify: `scripts/verify.sh`

**Interfaces:**
- Consumes: semantic `ts-*` markup from Task 1.
- Produces: scoped responsive light/dark presentation with compact Markdown hierarchy.

- [ ] **Step 1: Write failing visual-contract tests**

Require:

- `.cs-landing h1` to declare `font-size: 18px`;
- `.cs-landing h2` to declare `font-size: 16px`;
- H1/H2 pseudo-elements to contain `# ` and `## `;
- `.ts-hero-grid` to declare a two-column grid;
- the mobile media block to collapse that grid to one column without reordering the visual first;
- no card-grid, dark benefits, boxed-step, display-heading or oversized CTA selectors.

- [ ] **Step 2: Run the tests and verify RED**

Run: `python3 scripts/test-render-theme-showcase.py`

Expected: FAIL against the current display-scale/card-oriented CSS.

- [ ] **Step 3: Replace the Monospace landing CSS**

Base the scale and rhythm on the earlier repository-owned specimen:

- 14px body, 18px H1, 16px H2 and 14px H3;
- maximum text measure of 70ch;
- two-column opening with a restrained 420px maximum visual;
- plain inline links with underline-on-hover;
- single-column document sections separated by hairline rules;
- simple lists with dash markers and compact code treatment;
- light/dark variables and no remote/data assets;
- responsive breakpoint at 800px, retaining text before visual.

- [ ] **Step 4: Run focused and full structural verification**

Run:

```bash
python3 scripts/test-render-theme-showcase.py
python3 scripts/verify-landing-fixtures.py
scripts/verify.sh
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add -- codestorage-draft/demo-landing.css scripts/test-render-theme-showcase.py scripts/verify.sh
git commit -m "fix: restore restrained Monospace landing design"
```

### Task 3: Correct the documentation boundary and verify the live page

**Files:**
- Modify: `docs/demo-site-content.md`
- Modify: `docs/features.yaml`
- Modify: `docs/release-readiness.md`
- Modify: `docs/visual-review-matrix.md`
- Modify: `scripts/verify-site.sh`

**Interfaces:**
- Consumes: the finished Monospace homepage and standard demo routes.
- Produces: accurate guidance that standardizes content quality/routes without claiming a universal homepage layout.

- [ ] **Step 1: Update documentation contracts**

Document that homepage structure is theme-specific and that the current
Monospace example lives in `codestorage-draft/demo-showcase.template.md`.
Require real Flowershow content, real navbar, no copied identity/assets,
standard routes and recorded visual checks. Remove instructions that tell new
themes to retain one shared landing template.

- [ ] **Step 2: Build and verify locally**

Run:

```bash
output_dir=$(mktemp -d)
scripts/demo-site.sh codestorage-draft --build-only "$output_dir"
cmp "$output_dir/index.md" "$output_dir/landing.md"
SITE_URL=https://flowershow-themes-preview-rufuspollock.flowershow.me scripts/verify.sh
git diff --check
```

Expected: PASS with identical root/compatibility sources.

- [ ] **Step 3: Publish the exact pushed SHA**

Push the feature branch, then run:

```bash
scripts/demo-site.sh codestorage-draft --name codestorage-theme-demo
scripts/site.sh publish flowershow-themes-preview
```

- [ ] **Step 4: Perform browser review**

Review `/`, `/landing`, `/docs/kitchen-sink`, `/blog`, and
`/blog/first-post` at 1280×900 and 390×844 in light and dark modes. Confirm
compact heading scale, two columns only on desktop, text-first mobile flow,
no horizontal overflow, no CSS leakage, and unchanged Preview status.

- [ ] **Step 5: Record evidence and commit**

Update `docs/visual-review-matrix.md` with the exact SHA and review result,
then commit all documentation changes with:

```bash
git add -- docs/demo-site-content.md docs/features.yaml docs/release-readiness.md docs/visual-review-matrix.md scripts/verify-site.sh
git commit -m "docs: define theme-specific demo homepages"
```

- [ ] **Step 6: Final review and integration**

Run the full verifier on the final SHA, request independent review, merge via
a pull request, republish from the merge commit, update issue #1367, and leave
Monospace as Preview.
