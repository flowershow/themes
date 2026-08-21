# Flowershow-Owned Landing Fixtures Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace both preview landing pages with polished Flowershow-owned theme specimens while preserving their visual languages and Preview status.

**Architecture:** Keep the existing `layout: plain` Markdown plus landing-scoped CSS architecture. Add a small standard-library Python verifier for ownership/content contracts, call it from the repository done-condition script, then update the two fixtures, evidence records, and live demos in independently reviewable commits.

**Tech Stack:** Markdown/HTML, landing-scoped CSS, Python 3 standard library, Bash verification, Flowershow CLI, Playwright/Chromium visual capture where available.

## Global Constraints

- Both pages visibly identify themselves as preview theme specimens.
- Material is explicitly inspired by Material for MkDocs, not presented as that product; retain its upstream link and MIT notice.
- Published fixtures use only repository-authored copy, CSS, and geometric decoration.
- No commercial performance, pricing, uptime, security, customer, testimonial, personal-contact, or endorsement claims.
- No unresolved inline SVG paths or upstream images.
- Preserve useful links to `/`, `/kitchen-sink`, and `/blog`.
- Do not edit the four official theme directories, canonical Flowershow gallery/docs, dashboard listing, final names, release metadata, or tags.
- Keep both ledger entries at `readiness: remain-preview`; Search remains pending until entitlement is granted.

---

### Task 1: Enforce the published-fixture ownership boundary

**Files:**
- Create: `scripts/verify-landing-fixtures.py`
- Modify: `scripts/verify.sh`

**Interfaces:**
- Consumes: `material-draft/demo-landing.md` and `codestorage-draft/demo-landing.md` as UTF-8 text.
- Produces: exit `0` plus one PASS line per fixture when required and forbidden contracts hold; exit `1` plus actionable failures otherwise.

- [ ] **Step 1: Write the failing verifier**

Create a Python script with two `FixtureContract` records. Require these exact markers:

```python
required = {
    "material-draft/demo-landing.md": (
        'data-owned-fixture="material-inspired"',
        'data-theme-status="preview"',
        "Material-inspired preview",
        "https://squidfunk.github.io/mkdocs-material/",
        "/kitchen-sink",
        "/blog",
    ),
    "codestorage-draft/demo-landing.md": (
        'data-owned-fixture="monospace-specimen"',
        'data-theme-status="preview"',
        "FLOWERSHOW THEME LAB",
        "MONOSPACE SPECIMEN",
        "/kitchen-sink",
        "/blog",
        'class="cs-node-mark"',
    ),
}
```

Reject case-insensitively from the Material fixture: `squidfunk/mkdocs-material`,
`Documentation that simply works`, `Trusted in the industry`, `What our users
say`, `Become a sponsor`, the four old company tiles, `<svg`, and `<path`.

Reject case-insensitively from the monospace fixture: `Code Storage`, `Pierre
Computer Company`, `code.storage`, `pierre.co`, `99.99%`, `60x faster`, `$1.00`,
`$0.15`, `SLA`, `Cloudflare`, `Coinbase`, `Discord`, `Stripe`, `<svg`, and `<path`.

The script must print every missing/forbidden item, not stop at the first one.

- [ ] **Step 2: Run the verifier and confirm the old fixtures fail**

Run: `python3 scripts/verify-landing-fixtures.py`

Expected: non-zero with missing ownership markers and forbidden upstream text
for both files.

- [ ] **Step 3: Bind the verifier into the done condition**

Add this block near the existing landing-specific checks in `scripts/verify.sh`:

```bash
if python3 "$REPO_ROOT/scripts/verify-landing-fixtures.py"; then
  pass "published landing fixtures are Flowershow-owned specimens"
else
  bad "published landing fixtures violate ownership/content contracts"
fi
```

- [ ] **Step 4: Confirm the repository done condition now fails for the same reason**

Run: `scripts/verify.sh`

Expected: FAIL only at the new published-fixture ownership contract; existing
theme, demo, visual-evidence, and site checks continue to pass.

- [ ] **Step 5: Commit the red test**

```bash
git add scripts/verify-landing-fixtures.py scripts/verify.sh
git commit -m "test: define owned landing fixture contracts"
```

### Task 2: Replace the monospace fixture content and unresolved icon

**Files:**
- Modify: `codestorage-draft/demo-landing.md`
- Modify: `codestorage-draft/demo-landing.css`

**Interfaces:**
- Consumes: the monospace contracts from Task 1 and the current `.cs-*` layout classes.
- Produces: a content-rich, repository-owned monospace specimen with a CSS-only `cs-node-mark`.

- [ ] **Step 1: Replace the page identity and navigation**

Use frontmatter title `Flowershow Theme Lab — Monospace specimen` and description
`A technical preview theme for Markdown sites`. Put these attributes on the
outer wrapper:

```html
<div class="cs-landing" data-owned-fixture="monospace-specimen" data-theme-status="preview">
```

The header lines are `FLOWERSHOW THEME LAB`, `MONOSPACE SPECIMEN`, and `PREVIEW
2026`. Navigation links are `[ HOME ]`, `[ KITCHEN SINK ]`, `[ BLOG ]`, and
`[ THEME REPO ]`, pointing respectively to `/`, `/kitchen-sink`, `/blog`, and
`https://github.com/flowershow/themes`.

- [ ] **Step 2: Replace the hero and code example**

Use headline `A TECHNICAL THEME FOR MARKDOWN SITES`. Explain that the page tests
the independently authored theme across real Flowershow surfaces. Replace the
Git-storage code with a real configuration example containing:

```json
{
  "theme": {
    "theme": "https://cdn.jsdelivr.net/gh/flowershow/themes@main/codestorage-draft/theme.css",
    "showModeSwitch": true
  }
}
```

Use pill text `CSS-ONLY THEME` and `PREVIEW / NOT RELEASED`.

- [ ] **Step 3: Replace every commercial section with the approved specimen sections**

Keep the existing section/grid class structure and write the six sections from
the design: `Surfaces`, `Review matrix`, `Theme ingredients`, `Configuration`,
`Release boundary`, and `About this specimen`. The ASCII table lists rows for
Home, Kitchen sink, Blog list, and Blog post, with columns Desktop, Mobile,
Light, and Dark and value `reviewed`; it contains no prices.

The footer links to `/`, `/kitchen-sink`, `/blog`,
`https://flowershow-themes-preview-rufuspollock.flowershow.me/authoring`, and
`https://github.com/flowershow/themes`, followed by `FLOWERSHOW THEME LAB —
PREVIEW SPECIMEN`.

- [ ] **Step 4: Replace the SVG with CSS-only geometry**

Replace the inline SVG with:

```html
<div class="cs-node-mark" aria-hidden="true">
  <span class="cs-node cs-node-center"></span>
  <span class="cs-node cs-node-nw"></span>
  <span class="cs-node cs-node-ne"></span>
  <span class="cs-node cs-node-sw"></span>
  <span class="cs-node cs-node-se"></span>
</div>
```

In `demo-landing.css`, make `.cs-node-mark` a 48px relative circle and draw its
outer ring, four diagonal connectors, center node, and corner nodes with
borders, pseudo-elements, and positioned spans. Keep all rules under
`.cs-landing`.

- [ ] **Step 5: Run the focused verifier**

Run: `python3 scripts/verify-landing-fixtures.py`

Expected: monospace PASS; Material still FAILS.

- [ ] **Step 6: Commit the independently testable fixture**

```bash
git add codestorage-draft/demo-landing.md codestorage-draft/demo-landing.css
git commit -m "feat: replace code storage fixture with theme specimen"
```

### Task 3: Replace the Material fixture with an inspiration-led specimen

**Files:**
- Modify: `material-draft/demo-landing.md`
- Modify: `material-draft/demo-landing.css`

**Interfaces:**
- Consumes: the Material contracts from Task 1 and the current `.mat-landing` layout system.
- Produces: a polished Flowershow landing page that credits its inspiration without impersonating it.

- [ ] **Step 1: Replace identity, repo badge, and navigation**

Use frontmatter title `Flowershow — Material-inspired preview` and description
`A bright, structured preview theme for Markdown publishing`. Put these
attributes on the wrapper:

```html
<div class="mat-landing" data-owned-fixture="material-inspired" data-theme-status="preview">
```

The header title is `Flowershow` with a visible `Material-inspired preview`
label. Remove repository statistics and all inline SVG. Navigation links to
`/`, `/kitchen-sink`, `/blog`, the themes authoring page, and the themes repo.

- [ ] **Step 2: Rewrite the hero and feature content**

Use hero headline `A bright, structured home for Markdown` with factual copy
about previewing a Flowershow theme. Use calls to action `Explore the specimen`
(`/kitchen-sink`) and `Read the blog` (`/blog`).

Replace upstream sections with:

1. `Designed for real Markdown` — six numbered feature items covering content,
   devices, tokens, navigation, modes, and open authoring;
2. `Explore the theme` — four alternating spotlights linking home, kitchen sink,
   blog list/post, and authoring guidance;
3. `Review coverage` — four cards for Desktop, Mobile, Light, and Dark;
4. `Built in the open` — repository and contribution links, no testimonials;
5. `Inspired, not identical` — explicit upstream attribution and link to
   `/third-party-notices`;
6. `Try the preview` — CTA to `/kitchen-sink`, explicitly not a release claim.

- [ ] **Step 3: Replace icons with CSS/typographic markers**

Use elements such as `<span class="expect-marker" aria-hidden="true">01</span>`
and review cards; add landing-scoped CSS for markers. Preserve the current hero,
dark/light alternation, grids, spotlights, typography, and buttons. Remove icon
rules that become unused.

- [ ] **Step 4: Run the focused and full local verification**

Run:

```bash
python3 scripts/verify-landing-fixtures.py
scripts/verify.sh
git diff --check
```

Expected: all PASS.

- [ ] **Step 5: Commit the independently testable fixture**

```bash
git add material-draft/demo-landing.md material-draft/demo-landing.css
git commit -m "feat: make Material landing inspiration-led"
```

### Task 4: Close the executed provenance actions without promoting themes

**Files:**
- Modify: `docs/landing-fixture-provenance.md`
- Modify: `THIRD_PARTY_NOTICES.md`
- Modify: `docs/release-readiness.md`
- Modify: `docs/features.yaml`
- Modify: `NEXT.md`
- Modify: `scripts/verify-site.sh`

**Interfaces:**
- Consumes: the owned fixtures from Tasks 2–3.
- Produces: consistent provenance/readiness records and guardrails, with both themes still `remain-preview`.

- [ ] **Step 1: Change provenance verification before changing the records**

Update `scripts/verify-site.sh` to require disposition markers
`executed-owned-specimen` for both theme sections and require text recording:
Material upstream copy/icons/testimonials/company tiles replaced; Material
inspiration link and notice retained; monospace identity/copy/claims/contacts/
links/SVG replaced. Keep the complete MIT-notice hash check.

- [ ] **Step 2: Confirm the new evidence contract fails**

Run: `scripts/verify-site.sh`

Expected: FAIL because the old audit still records pre-release actions rather
than executed dispositions.

- [ ] **Step 3: Update evidence records**

Change both provenance markers to `data-disposition="executed-owned-specimen"`.
Record the exact replacements and retain historical source evidence. Change the
Material notice introduction from “adapts text” to “credits the open-source
project that inspired the preview theme”; retain the complete MIT text.

In readiness, move the landing-fixture action into completed evidence for each
theme and remove only that unchecked gate. Keep Search, final naming, canonical
integration, release metadata, and explicit human authorization unchecked.

In `docs/features.yaml`, add `landing_fixture: owned-specimen` to both entries,
leave `readiness: remain-preview`, and update audit notes/date without changing
`passes`. Update `NEXT.md` so the next actions start with Search entitlement and
the later product/release decisions.

- [ ] **Step 4: Run all repository checks**

Run:

```bash
scripts/verify-site.sh
scripts/verify.sh
git diff --check
```

Expected: all PASS and both ledger entries remain Preview.

- [ ] **Step 5: Commit the closed content/provenance gate**

```bash
git add docs/landing-fixture-provenance.md THIRD_PARTY_NOTICES.md docs/release-readiness.md docs/features.yaml NEXT.md scripts/verify-site.sh
git commit -m "docs: close landing fixture provenance actions"
```

### Task 5: Publish and review the changed landing surfaces

**Files:**
- Modify: `docs/visual-review-matrix.md`

**Interfaces:**
- Consumes: pushed branch commits and the existing demo-site workflow.
- Produces: live branch previews plus an eight-render landing addendum.

- [ ] **Step 1: Push the branch and publish both demo sites**

```bash
git push -u origin HEAD
scripts/demo-site.sh material-draft --landing-page material-draft/demo-landing.md --name material-theme-demo
scripts/demo-site.sh codestorage-draft --landing-page codestorage-draft/demo-landing.md --name codestorage-theme-demo
```

- [ ] **Step 2: Capture the focused matrix**

Render `/landing` for each demo at desktop `1280×900` and mobile `390×844`, in
requested `light` and `dark` modes. For every render record: HTTP success,
active `data-theme`, `document.scrollWidth === window.innerWidth`, readable
content, working real links, the visible Preview label, and no upstream-product
impersonation.

- [ ] **Step 3: Fix only defects demonstrated by the matrix**

Write a failing selector/content/overflow contract before each code fix, apply
the smallest landing-scoped HTML/CSS change, and rerun the affected render plus
`scripts/verify.sh`.

- [ ] **Step 4: Record the review addendum**

Append a dated `Owned landing fixture review` section to
`docs/visual-review-matrix.md` containing all eight combinations, observed
results, any fixes, and the explicit statement that Search remains unreviewed
because the two sites are Free.

- [ ] **Step 5: Commit visual evidence**

```bash
git add docs/visual-review-matrix.md
git commit -m "docs: record owned landing fixture review"
```

### Task 6: Review, merge, and verify exact merged main

**Files:**
- No new implementation files; GitHub PR/issue state and live deployments change.

**Interfaces:**
- Consumes: a clean, pushed branch with all checks passing.
- Produces: merged `main`, exact-main live demos/site, and updated issue evidence.

- [ ] **Step 1: Create the pull request**

The PR body must summarize both redesigns, provenance closure, visual evidence,
Preview boundary, and `flowershow/flowershow#1367`. Include commands and live
URLs used for verification.

- [ ] **Step 2: Request independent Critical/Important review**

Review factual copy, forbidden-material coverage, CSS/HTML accessibility,
mobile overflow, readiness consistency, and whether either page could be
mistaken for the upstream product. Fix every valid Critical/Important finding
test-first and rerun the full suite.

- [ ] **Step 3: Merge through GitHub and update local main**

Use a normal merge commit; do not push directly to `main` and do not tag.

- [ ] **Step 4: Republish exact merged main**

Republish both theme demo sites and the themes preview hub from exact merged
`main`, then run:

```bash
SITE_URL=https://flowershow-themes-preview-rufuspollock.flowershow.me scripts/verify.sh
git diff --check
git status --short --branch
```

Expected: all PASS and clean `main...origin/main`.

- [ ] **Step 5: Update tracking**

Comment on #1367 and #1364 with the merged PR/SHA, live landing links, matrix,
and remaining gates. Check only the two theme-specific provenance actions in
#1367. Keep the issue open for Search, naming, integration/release preparation,
and explicit human promotion authorization.
