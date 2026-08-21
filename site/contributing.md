---
title: Contribute a theme
description: Build, verify, preview, and propose a Flowershow theme.
---

Flowershow themes are CSS packages: one directory, one `theme.css`, and a
preview image. A good contribution also proves that the theme works across
representative content and records where visual fidelity deliberately stops.

For the complete method, start with [Authoring a Flowershow theme](/authoring).
If an AI agent is doing the visual translation, give it the
[AI theme-cloning workflow](/ai-theme-cloning) as its operating instructions.
For component-level CSS, use Flowershow's
[semantic class reference](https://flowershow.app/docs/reference/theme-class-reference)
instead of reverse-engineering selectors from an existing theme.

## Contribution path

### 1. Fork and branch

Fork [`flowershow/themes`](https://github.com/flowershow/themes), create a
descriptive branch, and add a new directory using a lowercase, URL-safe name:

```text
your-theme/
├── theme.css
└── preview.png
```

Use a `-draft` suffix while the design is still being evaluated. Do not edit
the four shipped theme directories as part of an unrelated contribution.

### 2. Initialize the repository

```bash
scripts/init.sh
```

This confirms the tools needed for verification and demo publishing. The `fl`
CLI must be installed and authenticated; login is intentionally interactive.

### 3. Build against representative content

Use the shared kitchen-sink, blog, navbar, sidebar, and dark-mode content in
`_demo-content/`. A landing page alone is not enough: it can hide component
classes and typography rules that fail on normal Markdown pages.

If you are translating an existing visual language, reproduce and measure the
target outside Flowershow first. The authoring guide explains why this
two-stage workflow is faster and more reliable than debugging through a
publish/cache loop.

### 4. Record the work

Add the theme to `docs/features.yaml` with:

- source or inspiration;
- directory;
- structural check state;
- demo and landing URLs;
- fidelity state and review notes;
- known gaps; and
- licensing substitutions or attribution.

Structural verification and visual fidelity are separate. A valid stylesheet
does not prove that it resembles its target.

### 5. Verify locally

```bash
scripts/verify.sh
```

Do not weaken checks to make a theme pass. Fix the theme or explain why a
check is wrong in the pull request.

### 6. Publish a preview

Use the repository script rather than assembling a demo by hand:

```bash
scripts/demo-site.sh your-theme-draft
```

The command combines `_demo-content/` with a commit-pinned jsDelivr theme URL
and publishes through `fl`. The branch must be pushed before jsDelivr can
serve it. Record the resulting demo URL in `docs/features.yaml`, then rerun
`scripts/verify.sh` so the live smoke check becomes part of the gate.

### 7. Submit the pull request

Include:

- what the theme is for;
- screenshots and the live preview;
- the reference or inspiration and its license;
- verification output;
- fidelity notes and known gaps; and
- any Flowershow core limitations or bugs discovered.

Reviewers should be able to distinguish a theme defect from a missing core
component. File focused core findings separately instead of hiding fragile
workarounds in theme CSS.

## What acceptance means

A merged preview is not automatically an official release. Promotion adds a
stable public name, dashboard and gallery integration, release metadata, and a
tagged jsDelivr version. Maintainers use the separate
[promotion checklist](/maintainers) and require an explicit release decision.
