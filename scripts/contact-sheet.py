#!/usr/bin/env python3
"""Screenshot every demo route at desktop/mobile x light/dark into a contact sheet.

    scripts/contact-sheet.py <base-url> [--out DIR] [--route /path ...]

For each route x viewport x mode it saves a full-page PNG and checks:

  gate    the page responds 200, the requested mode is the active
          `data-theme`, and the document is no wider than the viewport
          (no horizontal scroll on mobile). Any failure -> exit 1.
  report  axe-core colour-contrast violations. Listed, never a gate —
          several shipped themes have known contrast misses, and
          "does it look right" is judgement, not structure (CLAUDE.md).

Output: DIR/index.html (the contact sheet, open it in a browser),
DIR/checks.json, and DIR/<route>--<viewport>-<mode>.png.

Routes default to verify-demo-routes.py's STANDARD_ROUTES plus
FEATURE_ROUTES, so new fixture pages only need adding in one place.
Browsing goes through the gstack `browse` daemon (set BROWSE_BIN to
override its path) — no Playwright or second Chromium to install.

Mode is forced the way the site's own mode switch does it: Flowershow's
inline head script reads localStorage['theme-preference'] and sets
<html data-theme> before first paint.
"""

import argparse
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True  # no __pycache__ from importing verify-demo-routes
from importlib import import_module

_routes = import_module("verify-demo-routes")
DEFAULT_ROUTES = [route for route, _ in _routes.STANDARD_ROUTES + _routes.FEATURE_ROUTES]

VIEWPORTS = (("desktop", 1280, 900), ("mobile", 390, 844))
MODES = ("light", "dark")
AXE_URL = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js"

BROWSE = os.environ.get("BROWSE_BIN") or str(
    Path.home() / ".claude/skills/gstack/browse/dist/browse"
)

# Waits for webfonts and a settled layout, then measures. Elements sticking
# out past the viewport are named so an overflow failure is debuggable
# without re-opening the page.
#
# Both snippets start with `return`: when code contains `await`, browse's
# `js` runs it as a function body, and without an explicit return the
# result is silently empty.
PROBE_JS = """
return (async () => {
  await document.fonts.ready;
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  const vw = window.innerWidth;
  const offenders = [...document.querySelectorAll('body *')]
    .filter(el => el.getBoundingClientRect().right > vw + 1)
    .filter(el => !el.parentElement || el.parentElement.getBoundingClientRect().right <= vw + 1)
    .slice(0, 5)
    .map(el => el.tagName.toLowerCase() + (el.className && typeof el.className === 'string'
      ? '.' + el.className.trim().split(/\\s+/).slice(0, 2).join('.') : ''));
  const nav = performance.getEntriesByType('navigation')[0];
  return JSON.stringify({
    status: nav ? nav.responseStatus : 0,
    dataTheme: document.documentElement.getAttribute('data-theme'),
    scrollWidth: document.documentElement.scrollWidth,
    innerWidth: vw,
    offenders,
  });
})()
"""

AXE_JS = """
return (async () => {
  if (!window.axe) {
    await new Promise((res, rej) => {
      const s = document.createElement('script');
      s.src = %s;
      s.onload = res;
      s.onerror = () => rej(new Error('axe-core failed to load'));
      document.head.appendChild(s);
    });
  }
  const r = await axe.run(document, { runOnly: ['color-contrast'] });
  return JSON.stringify(r.violations.flatMap(v => v.nodes).map(n => ({
    target: n.target.join(' '),
    message: (n.any[0] && n.any[0].message) || '',
  })));
})()
""" % json.dumps(AXE_URL)


def browse(*args: str) -> str:
    result = subprocess.run([BROWSE, *args], capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"browse {args[0]} failed: {(result.stderr or result.stdout).strip()}")
    return result.stdout.strip()


def browse_json(expr: str):
    return json.loads(browse("js", expr))


def slug(route: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", route.lower()).strip("-") or "home"


def shoot(base: str, route: str, viewport, mode: str, out: Path) -> dict:
    name, width, height = viewport
    url = base + route
    png = f"{slug(route)}--{name}-{mode}.png"
    shot = {"route": route, "viewport": name, "mode": mode, "url": url, "png": png,
            "failures": [], "contrast": []}

    # re-set before every load: a page can overwrite the stored preference
    # (an inline canvas embed resets it to light), and that mustn't carry
    # over to the shots after it
    browse("js", f"localStorage.setItem('theme-preference', {json.dumps(mode)})")
    browse("goto", url)
    probe = browse_json(PROBE_JS)
    shot["probe"] = probe
    if probe["status"] != 200:
        shot["failures"].append(f"HTTP {probe['status']}")
    if probe["dataTheme"] != mode:
        shot["failures"].append(f"mode is {probe['dataTheme']!r}, wanted {mode!r}")
    if probe["scrollWidth"] > probe["innerWidth"]:
        shot["failures"].append(
            f"horizontal overflow: {probe['scrollWidth']}px > {probe['innerWidth']}px"
            + (f" ({', '.join(probe['offenders'])})" if probe["offenders"] else "")
        )

    browse("screenshot", str(out / png))

    try:
        shot["contrast"] = browse_json(AXE_JS)
    except (RuntimeError, json.JSONDecodeError) as error:
        shot["contrast_error"] = str(error)
    return shot


def render_sheet(base: str, shots: list, out: Path) -> None:
    columns = [(v[0], m) for v in VIEWPORTS for m in MODES]
    by_key = {(s["route"], s["viewport"], s["mode"]): s for s in shots}
    rows = []
    for route in dict.fromkeys(s["route"] for s in shots):
        cells = []
        for viewport, mode in columns:
            s = by_key.get((route, viewport, mode))
            if not s:
                cells.append("<td></td>")
                continue
            badges = "".join(f'<li class="fail">{html.escape(f)}</li>' for f in s["failures"])
            if s["contrast"]:
                badges += f'<li class="warn">{len(s["contrast"])} contrast issue(s)</li>'
            if s.get("contrast_error"):
                badges += '<li class="warn">contrast not checked</li>'
            if not badges:
                badges = '<li class="ok">checks pass</li>'
            cells.append(
                f'<td class="{viewport}"><a class="thumb" href="{html.escape(s["png"])}">'
                f'<img loading="lazy" src="{html.escape(s["png"])}" alt="{html.escape(route)} {viewport} {mode}"></a>'
                f"<ul>{badges}</ul></td>"
            )
        rows.append(
            f'<tr><th scope="row"><a href="{html.escape(base + route)}">{html.escape(route)}</a></th>'
            + "".join(cells) + "</tr>"
        )

    contrast_rows = "".join(
        f"<tr><td>{html.escape(s['route'])}</td><td>{s['viewport']}</td><td>{s['mode']}</td>"
        f"<td><code>{html.escape(c['target'])}</code></td><td>{html.escape(c['message'])}</td></tr>"
        for s in shots for c in s["contrast"]
    )
    failed = sum(1 for s in shots if s["failures"])
    head = "".join(f"<th scope=\"col\">{v} · {m}</th>" for v, m in columns)
    host = urlparse(base).netloc

    (out / "index.html").write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Contact sheet · {html.escape(host)}</title>
<style>
  :root {{ --bg:#f6f6f4; --fg:#1d1d1b; --muted:#6b6b66; --line:#d9d9d4; --ok:#1f7a3a; --fail:#b42318; --warn:#9a6700; }}
  @media (prefers-color-scheme: dark) {{ :root {{ --bg:#161615; --fg:#ececea; --muted:#a3a39d; --line:#3a3a37; --ok:#5cc97f; --fail:#ff7b6e; --warn:#e3b341; }} }}
  body {{ margin:0; padding:24px 16px; background:var(--bg); color:var(--fg); font:14px/1.45 system-ui, sans-serif; }}
  h1 {{ font-size:20px; margin:0 0 4px; }} h2 {{ font-size:16px; margin:32px 0 8px; }}
  p {{ margin:0 0 16px; color:var(--muted); }} a {{ color:inherit; }}
  .wrap {{ overflow-x:auto; }}
  table {{ border-collapse:collapse; }}
  th, td {{ border-bottom:1px solid var(--line); padding:8px; vertical-align:top; text-align:left; }}
  thead th {{ font-weight:600; white-space:nowrap; }}
  tbody th {{ white-space:nowrap; font-weight:600; }}
  /* fixed width, capped at about two viewports tall: long pages crop to
     their top, short ones show whole — neither shrinks nor zooms */
  .thumb {{ display:block; width:400px; max-height:562px; overflow:hidden; border:1px solid var(--line); background:#fff; }}
  td.mobile .thumb {{ width:180px; max-height:779px; }}
  .thumb img {{ display:block; width:100%; height:auto; }}
  ul {{ list-style:none; margin:6px 0 0; padding:0; font-size:12px; max-width:400px; }}
  .ok {{ color:var(--ok); }} .fail {{ color:var(--fail); font-weight:600; }} .warn {{ color:var(--warn); }}
  .contrast td {{ font-size:12px; }} code {{ font-size:12px; }}
</style></head><body>
<h1>Contact sheet · <a href="{html.escape(base)}">{html.escape(host)}</a></h1>
<p>{len(shots)} screenshots · {failed} with failed checks · {sum(len(s['contrast']) for s in shots)} contrast issues (report only). Thumbnails are cropped to the top of the page; click for the full-page PNG.</p>
<div class="wrap"><table><thead><tr><th></th>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<h2>Contrast issues (axe-core, report only)</h2>
{f'<div class="wrap"><table class="contrast"><thead><tr><th>Route</th><th>Viewport</th><th>Mode</th><th>Element</th><th>Detail</th></tr></thead><tbody>{contrast_rows}</tbody></table></div>' if contrast_rows else '<p>None found.</p>'}
</body></html>
""")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("base_url")
    parser.add_argument("--out", help="output directory (default: a fresh temp dir)")
    parser.add_argument("--route", action="append", dest="routes",
                        help="route to capture (repeatable; default: the standard demo routes)")
    args = parser.parse_args()

    if not os.access(BROWSE, os.X_OK):
        print(f"gstack browse not found at {BROWSE} (set BROWSE_BIN)", file=sys.stderr)
        return 2

    base = args.base_url.rstrip("/")
    routes = args.routes or DEFAULT_ROUTES
    out = Path(args.out) if args.out else Path(tempfile.mkdtemp(prefix="contact-sheet-"))
    out.mkdir(parents=True, exist_ok=True)

    shots = []
    for mode in MODES:
        # set the stored preference once per mode; every later page load on
        # this origin picks it up before first paint
        browse("goto", base + "/")
        browse("js", f"localStorage.setItem('theme-preference', {json.dumps(mode)})")
        for viewport in VIEWPORTS:
            browse("viewport", f"{viewport[1]}x{viewport[2]}")
            for route in routes:
                shot = shoot(base, route, viewport, mode, out)
                status = "FAIL" if shot["failures"] else "PASS"
                extra = "; ".join(shot["failures"])
                if shot["contrast"]:
                    extra += ("; " if extra else "") + f"{len(shot['contrast'])} contrast issue(s)"
                print(f"  {status}  {route} {viewport[0]} {mode}" + (f"  ({extra})" if extra else ""))
                shots.append(shot)

    (out / "checks.json").write_text(json.dumps(shots, indent=2))
    render_sheet(base, shots, out)
    print(f"\nContact sheet: {out / 'index.html'}")
    return 1 if any(s["failures"] for s in shots) else 0


if __name__ == "__main__":
    sys.exit(main())
