---
title: Features
description: Fixture pages that make every themeable part of Flowershow appear at least once.
---

The [kitchen sink](/docs/kitchen-sink) covers Markdown. These pages cover the rest of the layout, so a theme can be checked against every component a reader can meet. `scripts/hook-coverage.py` checks that together they render every stable theme hook.

## Pages and headers

- [Page header](/features/page-header): authors with photos, date, reading time, tags, breadcrumbs
- [Hero](/features/hero) and [full-width hero](/features/hero-full)
- [Rich content](/features/rich-content): wiki links, embeds, math, a diagram, a PDF, the knowledge graph
- [Contents only](/features/contents-only): the table of contents without the sidebar
- [Plain page](/features/plain-page): `layout: plain` with the navbar hidden
- [Canvas](/features/canvas): an Obsidian canvas as its own page. (Not embedded inline: an inline canvas embed resets dark mode to light, a Flowershow bug.)

## Listings

- [Magazine](/features/listings/magazine), [grid](/features/listings/grid), [compact](/features/listings/compact) and [people](/features/listings/people) views
- [Stories](/features/listings/stories): a `layout: list` page; its stories use the post layout
- [Empty and broken lists](/features/listings/states)
- [Legacy `<List />` component](/features/listings/legacy)

## Generated pages

- [Tags](/tags) and a [tag page](/tags/design)
- [Changelog](/changelog) from a folder, and a [single entry](/changelog/2026-08-10-dark-mode)
- [CHANGELOG.md](/releases/CHANGELOG) from one file
- [A missing page](/this-page-does-not-exist)
