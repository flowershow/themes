# Reusable Theme Showcase Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reusable Flowershow product homepage for theme demos, migrate the Monospace preview to it, and document the standard pages and content ownership for every new or updated theme.

**Architecture:** A validated JSON file supplies the small theme-specific layer to a shared Markdown/HTML template. A Python renderer creates the demo homepage, and `scripts/demo-site.sh` assembles it with the existing shared kitchen sink and blog while overlaying the real Flowershow navbar configuration. Theme-scoped CSS owns visual expression; canonical docs own the standard-page inventory.

**Tech Stack:** Python 3 standard library, Bash, JSON, Markdown/HTML, CSS, existing Flowershow CLI, existing shell/Python verification scripts.

## Global Constraints

- The shared template owns Flowershow product content; per-theme metadata contains only `schemaVersion`, `name`, `slug`, `status`, `headline`, `description`, `wrapperClass`, and `sourceUrl`.
- `status` accepts only `preview` or `official`; identifiers use lowercase ASCII; the source URL is HTTPS under `github.com/flowershow/themes`.
- The landing contains exactly one `h1`, no nested `<header>` or `<nav>`, no remote/data-image assets, and no copied reference-site marketing identity.
- The real Flowershow navbar links Home, Kitchen Sink, Blog, and Theme Source and uses a `Publish with Flowershow` CTA.
- `/`, `/docs/kitchen-sink`, `/blog`, and `/blog/first-post` are the standard routes; `/landing` is a temporary identical compatibility copy for the initial migration.
- Material and Monospace remain Preview. Search, naming, canonical integration, release metadata, and promotion authorization stay pending.

---

### Task 1: Validated shared showcase renderer

**Files:**
- Create: `_demo-content/theme-showcase.template.md`
- Create: `scripts/render-theme-showcase.py`
- Create: `scripts/test-render-theme-showcase.py`
- Create: `codestorage-draft/demo-showcase.json`

**Interfaces:**
- Consumes: `render-theme-showcase.py TEMPLATE METADATA OUTPUT`
- Produces: a complete `layout: plain` Markdown homepage and exit code `2` with a concise error for invalid metadata or unresolved placeholders.

- [ ] **Step 1: Write failing renderer tests**

Use `unittest`, `subprocess.run`, and `tempfile.TemporaryDirectory` to assert:

```python
class RenderShowcaseTests(unittest.TestCase):
    def test_renders_complete_owned_showcase(self):
        result = run_renderer(VALID_METADATA)
        self.assertEqual(result.returncode, 0, result.stderr)
        page = Path(result.output_path).read_text()
        self.assertIn('data-theme-showcase="monospace"', page)
        self.assertIn('data-theme-status="preview"', page)
        self.assertIn('<h1>A sharper home for your Markdown</h1>', page)
        self.assertEqual(page.lower().count('<h1'), 1)
        self.assertNotIn('{{', page)

    def test_rejects_missing_unknown_and_unsafe_metadata(self):
        for mutation in (missing_name, unknown_field, bad_wrapper, bad_source_url):
            result = run_renderer(mutation(VALID_METADATA))
            self.assertEqual(result.returncode, 2)
            self.assertIn('showcase metadata:', result.stderr)
```

- [ ] **Step 2: Run the tests and confirm the red state**

Run: `python3 scripts/test-render-theme-showcase.py`

Expected: FAIL because the renderer and template do not exist.

- [ ] **Step 3: Implement the template and renderer**

The renderer must define `REQUIRED_FIELDS` with the eight fields above and use
these exact callable interfaces: `load_metadata(path: Path) -> dict[str,
object]`, `validate_metadata(data: dict[str, object]) -> dict[str, str]`,
`render(template: str, metadata: dict[str, str]) -> str`, and `main(argv:
list[str]) -> int`.

Use `html.escape(value, quote=True)` before replacement. Reject extra fields,
schema versions other than integer `1`, unsupported status, identifiers outside
`^[a-z][a-z0-9-]*$`, and source URLs outside
`https://github.com/flowershow/themes`. After replacement reject any remaining
any unresolved double-brace template expression.

The shared template must contain the six sections from the design, real links
to `/docs/kitchen-sink`, `/blog`, `https://flowershow.app/publish`, and the
metadata source URL, plus one wrapper:

```html
<div class="{{wrapperClass}} theme-showcase"
     data-theme-showcase="{{slug}}" data-theme-status="{{status}}">
```

Do not include `<header>`, `<nav>`, copied homepage images, badges, customers,
testimonials, pricing, or release-audit prose.

- [ ] **Step 4: Add Monospace metadata**

```json
{
  "schemaVersion": 1,
  "name": "Monospace",
  "slug": "monospace",
  "status": "preview",
  "headline": "A sharper home for your Markdown",
  "description": "A compact monospace theme for docs, notes, blogs, and technical publishing.",
  "wrapperClass": "cs-landing",
  "sourceUrl": "https://github.com/flowershow/themes/tree/main/codestorage-draft"
}
```

- [ ] **Step 5: Run focused tests**

Run:

```bash
python3 scripts/test-render-theme-showcase.py
tmpfile=$(mktemp)
python3 scripts/render-theme-showcase.py _demo-content/theme-showcase.template.md codestorage-draft/demo-showcase.json "$tmpfile"
python3 scripts/verify-landing-fixtures.py
```

Expected: renderer tests PASS; rendered file has no placeholders. The existing
landing verifier may fail until Task 3 updates its contract.

- [ ] **Step 6: Commit**

```bash
git add -- _demo-content/theme-showcase.template.md scripts/render-theme-showcase.py scripts/test-render-theme-showcase.py codestorage-draft/demo-showcase.json
git commit -m "feat: add reusable theme showcase renderer"
```

### Task 2: Demo-site assembly and real navbar

**Files:**
- Modify: `scripts/demo-site.sh`
- Modify: `_demo-content/config.base.json`
- Modify: `scripts/test-render-theme-showcase.py`

**Interfaces:**
- Consumes: `THEME-DIR/demo-showcase.json`, shared template, theme CSS, and `--build-only OUTPUT_DIR`.
- Produces: an assembled site with identical generated `index.md` and `landing.md`, an overlaid `config.json`, and no external publish when build-only mode is used.

- [ ] **Step 1: Add failing assembly tests**

Add a subprocess test that runs:

```python
subprocess.run([
    "bash", "scripts/demo-site.sh", "codestorage-draft",
    "--build-only", str(output_dir),
], cwd=ROOT, capture_output=True, text=True)
```

Assert `index.md == landing.md`, both contain the generated showcase marker,
the kitchen sink and blog files exist, and `config.json` contains:

```python
self.assertEqual(config["nav"]["title"], "Flowershow")
self.assertEqual(config["nav"]["cta"], {
    "href": "https://flowershow.app/publish",
    "label": "Publish with Flowershow",
})
self.assertIn({"name": "Theme Source", "href": metadata["sourceUrl"]}, config["nav"]["links"])
```

- [ ] **Step 2: Run the tests and confirm the red state**

Run: `python3 scripts/test-render-theme-showcase.py`

Expected: FAIL because `--build-only` and metadata-driven assembly do not exist.

- [ ] **Step 3: Implement deterministic assembly**

Extend argument parsing with `--build-only OUTPUT_DIR`. Extract the existing
assembly into a `build_demo()` Bash function. For a theme with
`demo-showcase.json`:

1. call the renderer into both `index.md` and `landing.md`;
2. copy sibling `demo-landing.css` to `custom.css`;
3. load `name` and `sourceUrl` while creating `config.json`;
4. overlay the real navbar and CTA exactly as specified;
5. skip `fl` and preserve the output directory in build-only mode.

Reject a nonempty build-only output directory. Keep existing behavior for a
theme without showcase metadata and keep `--landing-page` as an explicit legacy
override.

- [ ] **Step 4: Run assembly and shell checks**

Run:

```bash
python3 scripts/test-render-theme-showcase.py
bash -n scripts/demo-site.sh
build_dir=$(mktemp -d)
scripts/demo-site.sh codestorage-draft --build-only "$build_dir"
test -s "$build_dir/index.md"
test -s "$build_dir/docs/kitchen-sink.md"
test -s "$build_dir/blog/first-post.md"
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add -- scripts/demo-site.sh _demo-content/config.base.json scripts/test-render-theme-showcase.py
git commit -m "feat: assemble standard theme demo homepage"
```

### Task 3: Migrate the Monospace landing presentation

**Files:**
- Modify: `codestorage-draft/demo-landing.css`
- Delete: `codestorage-draft/demo-landing.md`
- Modify: `scripts/verify-landing-fixtures.py`
- Modify: `docs/features.yaml`

**Interfaces:**
- Consumes: stable semantic classes from the shared template under `.cs-landing`.
- Produces: the polished Monospace homepage at `/`, with `/landing` as an identical compatibility copy.

- [ ] **Step 1: Update the verifier first**

Change the Monospace contract to render the shared template with
`demo-showcase.json`, then assert:

```python
assert '<h1>A sharper home for your Markdown</h1>' in rendered
assert rendered.lower().count('<h1') == 1
assert '<header' not in rendered.lower()
assert '<nav' not in rendered.lower()
for route in ('/docs/kitchen-sink', '/blog'):
    assert f'href="{route}"' in rendered
for stale in ('Review matrix', 'Release boundary', 'FLOWERSHOW THEME LAB'):
    assert stale.casefold() not in rendered.casefold()
```

Keep combined Markdown/CSS provenance checks, brace balance, forbidden upstream
identities, and remote/data-image rejection.

- [ ] **Step 2: Run the focused verifier and confirm it fails**

Run: `python3 scripts/verify-landing-fixtures.py`

Expected: FAIL against the old landing and CSS contracts.

- [ ] **Step 3: Redesign the scoped CSS**

Delete rules for `.cs-header`, review/pricing tables, release-audit sections,
and old content structure. Style the shared semantic hooks for:

- editorial two-column hero and aligned CSS node artwork;
- compact use-case grid;
- Flowershow benefit cards;
- three-step publishing flow;
- theme-detail block;
- final CTA and restrained Preview note;
- desktop/mobile and light/dark modes.

Style the real Flowershow navbar only through existing semantic theme classes;
do not create landing markup for it. Retain IBM Plex Mono and all required theme
tokens. Delete the obsolete theme-owned Markdown because the generated template
is now canonical.

- [ ] **Step 4: Point the ledger landing URL at the homepage**

Set `landing_demo_url` for `codestorage-draft` to
`https://codestorage-theme-demo-rufuspollock.flowershow.me/` and record
`/landing` as a compatibility path rather than a separate canonical landing.
Keep `status: Preview` and `readiness: remain-preview` unchanged.

- [ ] **Step 5: Run focused and full local checks**

Run:

```bash
python3 scripts/test-render-theme-showcase.py
python3 scripts/verify-landing-fixtures.py
scripts/verify.sh
git diff --check
```

Expected: PASS (live checks still describe the previously published site until
Task 5 publishes the branch).

- [ ] **Step 6: Commit**

```bash
git add -- codestorage-draft/demo-landing.css scripts/verify-landing-fixtures.py docs/features.yaml
git rm -- codestorage-draft/demo-landing.md
git commit -m "feat: migrate Monospace to shared showcase"
```

### Task 4: Canonical page inventory and authoring guidance

**Files:**
- Create: `docs/demo-site-content.md`
- Modify: `docs/theme-authoring-tutorial.md`
- Modify: `docs/ai-theme-cloning-skill.md`
- Modify: `site/contributing.md`
- Modify: `site/maintainers.md`
- Modify: `scripts/demo-site.sh`
- Modify: `scripts/verify-site.sh`

**Interfaces:**
- Consumes: the exact source paths, metadata schema, routes, and commands built in Tasks 1–3.
- Produces: one canonical inventory linked from all human, AI, contributor, maintainer, and operational entry points.

- [ ] **Step 1: Add failing documentation contracts**

In `verify-site.sh`, require `docs/demo-site-content.md` to list all standard
routes and canonical sources. Require each of the four guide surfaces to link
the canonical path. Require the AI guide to include the exact prohibitions:
`customer claims`, `reference-site marketing identity`, and `images or logos`.

- [ ] **Step 2: Run the verifier and confirm the red state**

Run: `scripts/verify-site.sh`

Expected: FAIL because the inventory and links do not exist.

- [ ] **Step 3: Write the canonical inventory**

Create `docs/demo-site-content.md` with:

- the route/source table from the design;
- shared versus theme-owned responsibilities;
- the exact JSON schema and a complete Monospace example;
- new-theme steps;
- existing-theme refresh/migration steps;
- build-only, publish, and verify commands;
- standard homepage versus exceptional `--landing-page` explanation;
- the rule that audit/readiness/provenance content belongs in `docs/`, not the
  public marketing page.

- [ ] **Step 4: Update every entry point**

Link and summarize the inventory in the human tutorial, AI guide, contributor
guide, maintainer guide, and `demo-site.sh` top-level usage comments. Remove any
instruction that describes a bespoke `/landing` page as the normal shipped
path. Preserve the raw-HTML research-fixture guidance as explicitly exceptional.

- [ ] **Step 5: Run documentation and full checks**

Run:

```bash
scripts/verify-site.sh
python3 scripts/test-render-theme-showcase.py
scripts/verify.sh
git diff --check
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add -- docs/demo-site-content.md docs/theme-authoring-tutorial.md docs/ai-theme-cloning-skill.md site/contributing.md site/maintainers.md scripts/demo-site.sh scripts/verify-site.sh
git commit -m "docs: standardize theme demo content"
```

### Task 5: Publish, visually verify, review, and integrate

**Files:**
- Modify: `docs/visual-review-matrix.md`
- Modify: `docs/release-readiness.md` only if the new homepage evidence changes an existing completed gate
- Modify: `NEXT.md` only to record shipped work and remaining gates

**Interfaces:**
- Consumes: completed branch and existing Flowershow preview sites.
- Produces: live branch preview, recorded evidence, reviewed PR, merged `main`, and exact-main deployments.

- [ ] **Step 1: Push and publish the branch preview**

Run:

```bash
git push -u origin design/reusable-theme-showcase
scripts/demo-site.sh codestorage-draft --name codestorage-theme-demo
scripts/site.sh publish flowershow-themes-preview
```

- [ ] **Step 2: Run browser verification**

Render `/`, `/docs/kitchen-sink`, `/blog`, and `/blog/first-post` at 1280×900
and 390×844 in light and dark. Assert HTTP 200, requested `data-theme`, exactly
one homepage `h1`, visible Preview marker, no horizontal overflow, working CTA
targets, and absence of the artificial header/release-audit copy. Manually
inspect the homepage captures and at least one internal page in each mode.

- [ ] **Step 3: Record evidence without promotion**

Update the visual matrix with the routes, viewports, modes, assertions, manual
review result, and any defect/fix loop. Record that Search and all existing
promotion gates remain pending.

- [ ] **Step 4: Run final branch verification**

Run:

```bash
SITE_URL=https://flowershow-themes-preview-rufuspollock.flowershow.me scripts/verify.sh
python3 scripts/test-render-theme-showcase.py
git diff --check
git status --short
```

Expected: PASS and clean after committing the evidence.

- [ ] **Step 5: Request independent review and open a PR**

The review must inspect content ownership, renderer safety, route/source
documentation, navbar hierarchy, responsive/light-dark behavior, and unchanged
Preview boundaries. Fix all Critical and Important findings and rerun Step 4.

- [ ] **Step 6: Merge and republish exact main**

After a Ready review, merge the PR, update local `main`, republish the Monospace
demo and preview hub from the merge commit, and rerun the full live verifier.

- [ ] **Step 7: Update tracking and clean up**

Comment on flowershow/flowershow#1364 and #1367 with the PR, merge SHA, live
homepage, documentation, and verification evidence. Keep both themes Preview
and leave the remaining readiness gates open. Remove only the merged feature
worktree/branch.
