#!/usr/bin/env python3
"""Find colours on a theme's demo site that don't come from the theme.

    scripts/palette-leaks.py <base-url> <theme-dir> [--route /path ...]
                             [--json FILE] [--core DIR] [--core-ref REF]

A theme that sets the tokens but misses a hard-coded colour in the
default theme (an orange badge, a pink highlight) leaves that colour on
the page. This script loads each demo route at desktop width in light and
dark mode and checks every visible element's text, background and border
colour against the theme's palette:

  palette  the computed value, in that mode, of every custom property
           the page's stylesheets declare (theme.css and the default
           theme's own tokens, most of which derive from the theme's;
           Tailwind's built-in colour scale excluded), plus every colour
           literal in theme.css. Alpha is ignored: a token at 10% opacity
           is still the token.
  derived  not in the palette, but a mix of two palette colours (what
           color-mix() of two tokens gives). Listed, not counted.
  leak     anything else. Each one is attributed to the nearest stable
           hook on the element or an ancestor, and to that hook's group,
           so coverage-ledger.py check --leaks can line it up with the
           ledger. Elements under no hook count as `unhooked`.

Because default tokens count as palette, a default token that hard-codes
a colour (rather than deriving it) would hide from the page scan. So it
also lists every custom property, in any of the page's stylesheets, set
to a colour literal that theme.css doesn't declare (the tag-pill pinks,
the callout colours): each is a token-level decision for the ledger.

And it lists theme tokens set to a colour literal whose value the page
doesn't end up using, usually because a core rule with a stronger
selector wins (core sets tokens on `:root[data-theme="light"]`, which
beats a bare `:root`). Such a token silently does nothing.

Report only, never a gate: some leaks are deliberate (an author's inline
colour, syntax highlighting), and deciding that is judgement. Exit 0
unless the run itself fails.

Routes default to the same demo routes contact-sheet.py loads. Browsing
goes through the gstack `browse` daemon (BROWSE_BIN overrides its path);
don't run it while hook-coverage.py or contact-sheet.py is running.
"""

import argparse
import json
import os
import re
import sys
from importlib import import_module
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True

_hooks = import_module("hook-coverage")
browse = _hooks.browse
BROWSE = _hooks.BROWSE

MODES = ("light", "dark")
COLOUR_LITERAL = re.compile(
    r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?|hwb|oklch|oklab|lab|lch)\([^()]*\)"
)

# Starts with `return`: code containing `await` runs as a function body.
SCAN_JS = """
return (async () => {
  await document.fonts.ready;
  await new Promise(r => setTimeout(r, 300));
  const PROPS = %s, LITERALS = %s, HOOKS = %s, TOL = 6;

  // any CSS colour -> [r, g, b, a] via a 1x1 canvas, so oklch(), color()
  // and color-mix() results all compare in one space
  const ctx = Object.assign(document.createElement('canvas'), {width: 1, height: 1})
    .getContext('2d', {willReadFrequently: true});
  const cache = new Map();
  const rgb = (css) => {
    if (cache.has(css)) return cache.get(css);
    let out = null;
    ctx.fillStyle = '#010203';
    ctx.fillStyle = css;
    if (ctx.fillStyle !== '#010203' || css === '#010203') {
      ctx.clearRect(0, 0, 1, 1);
      ctx.fillRect(0, 0, 1, 1);
      out = [...ctx.getImageData(0, 0, 1, 1).data.slice(0, 3)];
    }
    cache.set(css, out);
    return out;
  };
  // a computed colour -> [r, g, b, a]. rgb()/rgba() parse directly; other
  // spaces go through the canvas with their alpha stripped, so a translucent
  // colour isn't blended into the channels
  const parse = (computed) => {
    const m = computed.match(/^rgba?\\(([^)]+)\\)$/);
    if (m) {
      const p = m[1].split(/[\\s,\\/]+/).filter(Boolean).map(parseFloat);
      return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1];
    }
    const alpha = (computed.match(/\\/\\s*([\\d.]+)\\s*\\)$/) || [])[1];
    const opaque = rgb(computed.replace(/\\s*\\/\\s*[\\d.]+\\s*\\)$/, ')'));
    return opaque && [opaque[0], opaque[1], opaque[2], alpha === undefined ? 1 : parseFloat(alpha)];
  };

  const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);

  const holder = document.createElement('div');
  holder.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden;color:rgb(1, 2, 3)';
  const probe = document.createElement('span');
  holder.appendChild(probe);
  document.body.appendChild(holder);
  const palette = [];
  const add = (c, from) => { if (c && c[3] > 0) palette.push({rgb: c.slice(0, 3), from}); };
  // every custom property any stylesheet declares: the default theme's own
  // tokens are derived from the theme's (its foreground scale, tag pills),
  // so they belong in the palette. Tailwind's built-in palette and the
  // utility internals (--tw-*, UnoCSS's --un-*) don't.
  const names = new Set(PROPS);
  const declared = {};  // name -> raw values, for the literal-token list
  const walk = (rules) => {
    for (const rule of rules) {
      if (rule.style) for (const p of rule.style) if (p.startsWith('--')) {
        names.add(p);
        (declared[p] ??= new Set()).add(rule.style.getPropertyValue(p).trim());
      }
      if (rule.cssRules) walk(rule.cssRules);
    }
  };
  for (const sheet of document.styleSheets) {
    try { walk(sheet.cssRules); } catch (e) { /* cross-origin: skip */ }
  }
  const TAILWIND = /^--(tw-|un-|color-(red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose|slate|gray|zinc|neutral|stone)-\\d+$|color-(white|black)$)/;
  for (const prop of [...names].filter(p => !TAILWIND.test(p) || PROPS.includes(p))) {
    probe.style.color = 'var(' + prop + ')';
    const v = getComputedStyle(probe).color;
    if (v !== 'rgb(1, 2, 3)') add(parse(v), prop);
  }
  for (const lit of LITERALS) {
    probe.style.color = '';
    probe.style.color = lit;
    if (probe.style.color) add(parse(getComputedStyle(probe).color), lit);
  }
  // tokens the theme doesn't declare whose value is a colour literal, not
  // derived from another token: in the palette, but not the theme's choice
  // tokens the theme sets to a colour literal that the page doesn't end up
  // using: a core rule with a stronger selector (:root[data-theme="light"]
  // beats a bare :root) wins, and the theme's value never applies
  const themeDeclared = {};
  for (const sheet of document.styleSheets) {
    if (!/\\/(custom|theme)\\.css(\\?|$)/.test(sheet.href || '')) continue;
    const collect = (rules) => {
      for (const rule of rules) {
        if (rule.style) for (const p of rule.style) if (p.startsWith('--')) {
          (themeDeclared[p] ??= []).push(rule.style.getPropertyValue(p).trim());
        }
        if (rule.cssRules) collect(rule.cssRules);
      }
    };
    try { collect(sheet.cssRules); } catch (e) { /* cross-origin */ }
  }
  const inactiveTokens = {};
  for (const [name, values] of Object.entries(themeDeclared)) {
    const literals = values.filter(v => !v.includes('var('));
    probe.style.color = 'var(' + name + ')';
    const now = getComputedStyle(probe).color;
    if (!literals.length || now === 'rgb(1, 2, 3)') continue;
    const actual = parse(now);
    const wanted = literals.map(v => { probe.style.color = ''; probe.style.color = v;
      return probe.style.color ? parse(getComputedStyle(probe).color) : null; }).filter(Boolean);
    if (wanted.length && actual && !wanted.some(w => dist(w, actual) <= TOL)) {
      inactiveTokens[name] = {declared: literals, computed: now};
    }
  }
  const literalTokens = {};
  for (const [name, values] of Object.entries(declared)) {
    if (PROPS.includes(name) || TAILWIND.test(name)) continue;
    for (const v of values) {
      if (v.includes('var(')) continue;
      probe.style.color = '';
      probe.style.color = v;
      if (probe.style.color) (literalTokens[name] ??= []).push(v);
    }
  }
  holder.remove();

  const inPalette = (c) => palette.some(p => dist(p.rgb, c) <= TOL);
  const derived = (c) => {
    for (let i = 0; i < palette.length; i++) for (let j = i + 1; j < palette.length; j++) {
      const a = palette[i].rgb, b = palette[j].rgb;
      const ab = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
      const len = ab[0] ** 2 + ab[1] ** 2 + ab[2] ** 2;
      if (!len) continue;
      const t = Math.max(0, Math.min(1, ((c[0] - a[0]) * ab[0] + (c[1] - a[1]) * ab[1] + (c[2] - a[2]) * ab[2]) / len));
      if (dist([a[0] + t * ab[0], a[1] + t * ab[1], a[2] + t * ab[2]], c) <= TOL + 2) return true;
    }
    return false;
  };

  const owner = (el) => {
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      for (const c of n.classList) if (HOOKS[c]) return [c, HOOKS[c]];
    }
    return ['', 'unhooked'];
  };
  const label = (el) => el.tagName.toLowerCase() + [...el.classList].slice(0, 2).map(c => '.' + c).join('');
  const hasText = (el) => [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());

  const found = [];
  for (const el of document.body.querySelectorAll('*')) {
    if (el instanceof SVGElement && !(el instanceof SVGSVGElement)) continue;
    if (!el.getClientRects().length) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.display === 'none') continue;
    const checks = [];
    if (hasText(el)) checks.push(['color', cs.color]);
    checks.push(['background-color', cs.backgroundColor]);
    for (const side of ['top', 'right', 'bottom', 'left']) {
      if (parseFloat(cs.getPropertyValue('border-' + side + '-width')) > 0
          && cs.getPropertyValue('border-' + side + '-style') !== 'none') {
        checks.push(['border-color', cs.getPropertyValue('border-' + side + '-color')]);
      }
    }
    const seen = new Set();
    for (const [prop, value] of checks) {
      const c = parse(value);
      if (!c || c[3] === 0) continue;
      const key = prop + value;
      if (seen.has(key)) continue;
      seen.add(key);
      if (inPalette(c)) continue;
      const [hook, group] = owner(el);
      found.push({
        kind: derived(c) ? 'derived' : 'leak',
        prop, value,
        rgb: '#' + c.slice(0, 3).map(x => Math.round(x).toString(16).padStart(2, '0')).join(''),
        alpha: Math.round(c[3] * 100) / 100,
        hook, group, element: label(el),
        inline: !!(el.getAttribute('style') || '').match(/color|background/),
      });
    }
  }
  const nav = performance.getEntriesByType('navigation')[0];
  return JSON.stringify({
    status: nav ? nav.responseStatus : 0,
    dataTheme: document.documentElement.getAttribute('data-theme'),
    palette: palette.length,
    literalTokens,
    inactiveTokens,
    found,
  });
})()
"""


def theme_palette_sources(css: str) -> tuple[list[str], list[str]]:
    scrubbed = re.sub(r"/\*[\s\S]*?\*/", " ", css)
    props = sorted(set(re.findall(r"(--[A-Za-z0-9_-]+)\s*:", scrubbed)))
    literals = sorted(set(COLOUR_LITERAL.findall(scrubbed)) - {""})
    # relative colours (oklch(from var(--x) ...)) can't be resolved out of
    # context; the tokens they're built on are already in the palette
    literals = [lit for lit in literals if "var(" not in lit and "from " not in lit]
    return props, literals


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("base_url")
    parser.add_argument("theme_dir")
    parser.add_argument("--route", action="append", dest="routes",
                        help="route to load (repeatable; default: the demo routes)")
    parser.add_argument("--json", help="write the full result here (coverage-ledger.py --leaks reads it)")
    parser.add_argument("--core", default=str(HERE.parent.parent / "flowershow"),
                        help="Flowershow core checkout (default: ../flowershow)")
    parser.add_argument("--core-ref", default="origin/main",
                        help="git ref of core to read the hooks from (default: origin/main)")
    args = parser.parse_args()

    if not os.access(BROWSE, os.X_OK):
        print(f"gstack browse not found at {BROWSE} (set BROWSE_BIN)", file=sys.stderr)
        return 2
    css_path = Path(args.theme_dir) / "theme.css"
    if not css_path.exists():
        print(f"no theme.css in {args.theme_dir}", file=sys.stderr)
        return 2

    base = args.base_url.rstrip("/")
    routes = args.routes or _hooks.DEFAULT_ROUTES
    props, literals = theme_palette_sources(css_path.read_text())
    groups = _hooks.stable_hooks(Path(args.core), args.core_ref)
    hook_group = {hook: group for group, hooks in groups.items() for hook in hooks}
    scan = SCAN_JS % (json.dumps(props), json.dumps(literals), json.dumps(hook_group))

    browse("viewport", "1280x900")
    browse("goto", base + "/")  # localStorage needs the site's origin
    pages = []
    for mode in MODES:
        for route in routes:
            # re-set before every load: a page can overwrite the stored mode
            browse("js", f"localStorage.setItem('theme-preference', {json.dumps(mode)})")
            _hooks.load(base + route)
            page = json.loads(browse("js", scan))
            page.update(route=route, mode=mode)
            problems = []
            if page["status"] != 200:
                problems.append(f"HTTP {page['status']}")
            if page["dataTheme"] != mode:
                problems.append(f"mode is {page['dataTheme']!r}")
            leaks = [f for f in page["found"] if f["kind"] == "leak"]
            print(f"  {route} {mode}: {len(leaks)} leak(s), "
                  f"{len(page['found']) - len(leaks)} derived, palette {page['palette']}"
                  + (f"  ({'; '.join(problems)})" if problems else ""))
            pages.append(page)

    by_group: dict[str, dict] = {}
    for page in pages:
        for f in page["found"]:
            if f["kind"] != "leak":
                continue
            entry = by_group.setdefault(f["group"], {"elements": 0, "colours": {}})
            entry["elements"] += 1
            colour = entry["colours"].setdefault(
                f["rgb"], {"count": 0, "props": [], "modes": [], "samples": [], "inline": False})
            colour["count"] += 1
            for key, value in (("props", f["prop"]), ("modes", page["mode"])):
                if value not in colour[key]:
                    colour[key].append(value)
            colour["inline"] |= f["inline"]
            sample = f"{page['route']} {f['element']}" + (f" (in .{f['hook']})" if f["hook"] else "")
            if len(colour["samples"]) < 3 and sample not in colour["samples"]:
                colour["samples"].append(sample)

    order = list(groups) + ["unhooked"]
    print()
    for group in sorted(by_group, key=lambda g: order.index(g) if g in order else len(order)):
        entry = by_group[group]
        print(f"  {group}: {entry['elements']} element(s)")
        for rgb, colour in sorted(entry["colours"].items(), key=lambda kv: -kv[1]["count"]):
            flags = ", ".join(colour["props"] + colour["modes"]) + (", inline style" if colour["inline"] else "")
            print(f"    {rgb}  ×{colour['count']}  ({flags})  e.g. {colour['samples'][0]}")

    unset: dict[str, list[str]] = {}
    for page in pages:
        for name, values in page["literalTokens"].items():
            for value in values:
                if value not in unset.setdefault(name, []):
                    unset[name].append(value)
    if unset:
        print("\n  tokens set to a colour literal that this theme doesn't declare:")
        for name, values in unset.items():
            print(f"    {name}: {' | '.join(values)}")

    inactive: dict[str, dict] = {}
    for page in pages:
        for name, info in page["inactiveTokens"].items():
            entry = inactive.setdefault(name, {"declared": info["declared"], "computed": {}})
            entry["computed"].setdefault(page["mode"], info["computed"])
    if inactive:
        print("\n  theme tokens whose value the page doesn't use (a stronger core selector wins?):")
        for name, entry in inactive.items():
            seen = ", ".join(f"{mode}: {value}" for mode, value in entry["computed"].items())
            print(f"    {name}: declared {' | '.join(entry['declared'])}; computed {seen}")

    total = sum(e["elements"] for e in by_group.values())
    print(f"\n{total} off-palette element colour(s) in {len(by_group)} group(s); "
          f"{len(unset)} unset literal token(s); {len(inactive)} inactive theme token(s); report only")
    if args.json:
        Path(args.json).write_text(json.dumps(
            {"base_url": base, "theme": Path(args.theme_dir).resolve().name,
             "by_group": by_group, "unset_literal_tokens": unset,
             "inactive_tokens": inactive, "pages": pages}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
