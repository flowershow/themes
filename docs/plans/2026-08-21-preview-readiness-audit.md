# Preview Release-Readiness Audit Plan

**Goal:** Record an evidence-backed readiness recommendation for Material and
code.storage while preserving their Preview status and the explicit human
release gate.

**Tracking:** flowershow/flowershow#1367, child of #1364.

## Scope and constraints

- Use one canonical Markdown readiness record and assemble it into the preview
  site; do not maintain a second copy.
- Record verified evidence separately from pending visual/product decisions.
- Correct attribution or documentation defects found by the audit.
- Add automated checks for the record, both theme entries, evidence links, and
  the `remain-preview` recommendation.
- Do not rename a directory, change the dashboard or canonical Flowershow
  gallery, prepare a tag, or promote a theme.

## Implementation

1. Extend preview-site verification first and prove it fails without the
   readiness record.
2. Add `docs/release-readiness.md` with per-theme evidence, completed and
   pending checklist items, licensing sources, and recommendations.
3. Assemble and navigate to the canonical record from the preview site; link it
   from maintainer/status pages and update `NEXT.md`.
4. Correct the code.storage font-substitution header to match shipped CSS.
5. Run local and live verification, independent review, publish the preview,
   merge through a pull request, and update #1367/#1364.
