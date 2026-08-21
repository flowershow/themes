# Monospace Promotion Design

## Decision

Promote the code.storage-inspired preview as the official **Monospace** theme.
Its stable directory and bare configuration value are `monospace`. Material
remains Preview.

The approval was recorded by Rufus on 2026-08-21 after reviewing the finished
Monospace homepage and parallel themes site. Search remains a transparent,
non-blocking follow-up in flowershow/flowershow#1370 because the demo sites do
not currently have the entitlement needed to render that surface.

## Themes repository

- Rename `codestorage-draft/` to `monospace/` without changing the reviewed
  theme or homepage design.
- Record Monospace as official in the feature ledger, readiness record, status
  page, gallery and verifier contracts.
- Use the bare config value `monospace` and a dedicated Monospace demo URL.
- Retain code.storage references only where they document inspiration,
  provenance or historical URLs.
- Add Monospace to release metadata and CDN purge coverage, but do not create a
  version tag in this change.

## Flowershow repository

- Add `monospace` to the dashboard theme selector.
- Add Monospace to the canonical `/docs/reference/themes` gallery and document
  the bare configuration value.
- Reuse the repository-owned preview asset; do not reuse code.storage artwork.

## Follow-up tracking

- flowershow/flowershow#1369 evaluates the parallel themes site with concrete
  questions and keeps the canonical-site decision open.
- flowershow/flowershow#1370 owns Search entitlement and visual review.
- flowershow/flowershow#1367 remains the readiness history and Material
  promotion tracker.

## Success criteria

- `monospace` resolves as an official bare-name theme from the dashboard and
  documentation.
- The stable demo passes the standard route contract.
- Material remains Preview and unchanged.
- Both repositories pass their relevant automated checks and independent
  review before merge.

