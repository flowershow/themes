# Stage-1 landing page repros

Standalone Tailwind + HTML reproductions of the sites we're cloning. These
exist to get **fidelity** right cheaply, before any of it is extracted into
actual Flowershow theme CSS.

Two-stage method (see
[the plan doc](https://github.com/flowershow/flowershow/blob/main/docs/plans/2026-08-08-theme-cloning-fidelity-method.md)):

1. Reproduce the target here as plain Tailwind + HTML, iterate until it
   genuinely resembles the target.
2. Only then extract into a Flowershow theme.

## Running

Serve **from this directory** — `_repro/`:

```sh
cd _repro && python3 -m http.server 8899
# then open http://localhost:8899/material-landing.html
```

Two traps, both of which cost time already:

- `file://` URLs don't work with the browser automation tooling. Serve over
  localhost.
- If a server is already running on 8899 from a *different* directory, you
  will silently get that directory's files and think your edits did nothing.
  Check with `lsof -ti:8899` and kill it first. Always append a
  cache-busting `?v=N` when reloading, too.

## Method note

**Compare renders side by side.** Load the target and the repro and look at
both. Structural checks ("does the CSS load", "are the tokens defined") do
not tell you whether something resembles the target — the first attempt at
these themes passed every structural check and looked nothing like the
originals.

For typography specifically, don't judge from screenshots — compression
makes different fonts look alike. Use `getComputedStyle` on the live page.

## Artwork licensing

`material-landing.html` references mkdocs-material's own parallax
illustration PNGs **as a temporary stand-in only**, so the composition can be
compared like-for-like. That artwork is bespoke and is not ours to ship. Any
version that gets published needs original art.

The reusable part is the technique, not the art:

- container `perspective: 50px`
- each layer `translateZ(-N)` with compensating `scale((50+N)/50)`
- measured layers: -400/9, -250/6, -100/3, -50/2
- square layer images (100vw x 100vw), `object-fit: cover`, per-layer
  `object-position`
- top blend layer: `linear-gradient(transparent, #1e2129)`

## Status

| Repro | Fidelity |
| --- | --- |
| `material-landing.html` | hero composition close; structure/type/color measured from live site. Foreground plant layers frame smaller than reference, blend washes the sky more than it should. Sections below hero are structurally right, placeholder imagery. |
