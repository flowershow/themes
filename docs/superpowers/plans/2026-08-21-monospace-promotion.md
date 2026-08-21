# Monospace Promotion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote the reviewed Monospace theme from Preview to an official bare-name Flowershow theme.

**Architecture:** Land the stable theme contract in `flowershow/themes` first, including the rename, gallery, demo and release metadata. Then land the consumer-facing dashboard and canonical documentation changes in `flowershow/flowershow`. Search remains a separately tracked non-blocking follow-up.

**Tech Stack:** CSS, Markdown/MDX, YAML, Bash, Python verification, Flowershow CLI, GitHub pull requests.

## Global Constraints

- Final public name and configuration value: `Monospace` / `monospace`.
- Material remains Preview and its theme files are unchanged.
- Do not create or push a version tag.
- Preserve code.storage references only for provenance, inspiration and historical URLs.

---

### Task 1: Encode the stable themes-repository contract

**Files:**
- Rename: `codestorage-draft/` to `monospace/`
- Modify: `docs/features.yaml`
- Modify: `docs/release-readiness.md`
- Modify: `site/themes.md`
- Modify: `site/status.md`
- Modify: `NEXT.md`
- Modify: `scripts/verify-site.sh`
- Modify: `scripts/verify.sh`
- Modify: `scripts/test-render-theme-showcase.py`
- Modify: `.github/workflows/release.yml`
- Modify: `.github/scripts/purge-jsdelivr-cache.js`

- [ ] Change verifier/test expectations first and confirm they fail against the Preview state.
- [ ] Rename the theme and update official status, bare config, stable demo URL and release metadata.
- [ ] Record the explicit promotion decision and link #1369 and #1370 from `NEXT.md`.
- [ ] Publish the branch-pinned stable demo and run `scripts/verify.sh`.
- [ ] Commit, push, review and merge the themes PR.

### Task 2: Expose Monospace in Flowershow

**Files:**
- Modify: `apps/flowershow/app/(cloud)/dashboard/site/[id]/settings/page.tsx`
- Modify: `content/flowershow-app/docs/reference/themes.md`
- Add or modify: canonical Monospace preview asset under `content/flowershow-app/assets/`
- Test: relevant dashboard/docs tests discovered in the repository

- [ ] Add failing dashboard/docs expectations for `monospace` where practical.
- [ ] Add the dashboard option and canonical gallery card.
- [ ] Run focused tests and the repository-required checks.
- [ ] Commit, push, review and merge the Flowershow PR.

### Task 3: Publish and record the integrated result

- [ ] Republish the Monospace demo from merged themes `main`.
- [ ] Republish the parallel themes site.
- [ ] Verify live standard routes and the bare jsDelivr theme URL.
- [ ] Update #1367, #1369 and #1370 with the resulting status and links.

