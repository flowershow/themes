---
title: Standard theme demo pages and content
description: Canonical routes, sources, and ownership for Flowershow theme demos.
---

# Standard theme demo pages and content

A theme demo is both a useful example website and a repeatable test surface.
Every new theme—and every existing theme receiving a substantial refresh—uses
the same standard pages. Shared content makes visual differences attributable
to the theme rather than to different copy.

## Standard routes and canonical sources

| Route | What it demonstrates | Canonical repository source |
| --- | --- | --- |
| `/` | Flowershow product homepage interpreted by the theme | `_demo-content/theme-showcase.template.md` + `THEME-DIR/demo-showcase.json` + `THEME-DIR/demo-landing.css` |
| `/docs/kitchen-sink` | Markdown, typography, code, tables, callouts, media, and responsive content | `_demo-content/docs/kitchen-sink.md` |
| `/blog` | Blog listing, metadata, summaries, and repeated content | `_demo-content/blog/index.mdx` plus sibling posts |
| `/blog/first-post` | Focused long-form article reading | `_demo-content/blog/first-post.md` |
| navbar and footer | Real site identity, navigation, mode control, source link, and publishing CTA | `_demo-content/config.base.json`, overlaid by `scripts/demo-site.sh` |

The homepage is the public landing page. A newly migrated theme also publishes
the same generated source at `/landing` as a compatibility path; `/` remains
canonical. Do not create a second navbar inside the homepage.

## What is shared and what belongs to a theme

Flowershow owns the shared product story, semantic landing markup, kitchen
sink, blog posts, navigation structure, and publishing links. Change shared
copy only when the product message changes for every theme demo.

Each theme owns:

- `theme.css` for the actual site-wide theme;
- `demo-showcase.json` for its small identity and description layer;
- `demo-landing.css` for the shared homepage's visual interpretation; and
- its preview image and ledger evidence.

Landing CSS is loaded site-wide as `custom.css`, so every rule must be scoped
beneath the metadata's `wrapperClass`. It must not restyle the kitchen sink or
blog accidentally. The verifier permits only the documented
`.site-navbar-site-name` and `.site-navbar-site-title` selectors outside that
wrapper for aligning the real navbar identity. Adding a second `<header>` or
`<nav>` to the landing is not allowed. CSS images must be repository-owned,
local paths; remote and data URLs are rejected.

## Showcase metadata

Create `THEME-DIR/demo-showcase.json` with exactly these fields:

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

`status` is `preview` or `official`. `slug` and `wrapperClass` are lowercase
ASCII identifiers. `sourceUrl` is an HTTPS path within
`github.com/flowershow/themes` (not a similarly prefixed repository or a path
containing dot segments). The renderer rejects missing or extra fields, unsafe
identifiers, unsupported states, and unresolved template placeholders. It
escapes frontmatter and HTML independently, so metadata remains valid in both
contexts.

## Add a new theme

1. Create `THEME-DIR/theme.css`, a stable preview image,
   `THEME-DIR/demo-showcase.json`, and scoped `THEME-DIR/demo-landing.css`.
2. Build the theme against the standard content without publishing:

   ```bash
   output_dir=$(mktemp -d)
   scripts/demo-site.sh THEME-DIR --build-only "$output_dir"
   ```

3. Confirm the output contains `index.md`, `docs/kitchen-sink.md`,
   `blog/index.mdx`, `blog/first-post.md`, `custom.css`, and `config.json`.
4. Add the theme and its Preview state to `docs/features.yaml`.
5. Run `scripts/verify.sh`, push the commit, then publish:

   ```bash
   scripts/demo-site.sh THEME-DIR --name YOUR-DEMO-SITE
   ```

6. Review the homepage, kitchen sink, blog list, and post on desktop/mobile
   and in light/dark mode. Record the evidence; do not promote automatically.

## Refresh an existing theme

Do not copy another theme's completed homepage. Add or update
`demo-showcase.json`, retain the shared template, and rewrite only the scoped
landing CSS needed to express the theme. If the theme still has a bespoke
`demo-landing.md`, migrate its useful theme description into metadata, move
general Flowershow content to the shared template, and remove duplicate
navigation and QA/release prose.

Keep an old `/landing` URL as the generated compatibility copy while recorded
links are updated. Set `landing_demo_url` to the demo root and record the
compatibility URL separately in `docs/features.yaml`.

## Standard homepage versus exceptional fixtures

`demo-showcase.json` is the normal shipped path. `scripts/demo-site.sh`
automatically renders it to the homepage.

`--landing-page FILE.md` remains an explicit exception for a research fixture
whose structure cannot use the shared product template. `--landing FILE.html`
is only for the disposable stage-one fidelity reproduction outside normal
Flowershow chrome. Neither exception changes the standard page inventory or
justifies a second demo site.

## Content and provenance boundary

The public homepage should be credible Flowershow marketing content. Never add
fictional customer claims, copy a reference site's marketing identity, or
import its images or logos. A reference may inspire theme CSS when its source
and license are recorded.

Release matrices, licensing audits, source provenance, naming decisions, and
promotion gates belong in `docs/visual-review-matrix.md`,
`docs/landing-fixture-provenance.md`, `docs/release-readiness.md`, and
`docs/features.yaml`. They should not dominate the public demo homepage.

## Verification commands

```bash
python3 scripts/test-render-theme-showcase.py
python3 scripts/verify-landing-fixtures.py
scripts/verify.sh
```

For live verification, set `SITE_URL` to the themes preview site. A green
structural or live check is evidence, not release authorization. The verifier
automatically discovers every `*/demo-showcase.json`, validates its rendered
structure and scoped CSS, then checks `/`, `/docs/kitchen-sink`, `/blog`,
`/blog/first-post`, and any recorded `/landing` compatibility URL on each
published demo.
