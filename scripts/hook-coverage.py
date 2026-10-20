#!/usr/bin/env python3
"""Check that a demo site renders every stable theme hook.

    scripts/hook-coverage.py <base-url> [--route /path ...] [--json FILE]
                             [--core DIR] [--core-ref REF]

A theme can only be checked against the parts of the Flowershow layout the
demo site actually renders. This script answers "does it render all of
them?": it loads every demo route at desktop and mobile width, opens the
menus, drawers and dialogs that only appear on interaction, collects every
class name in the DOM, and diffs that set against the stable hooks in the
generated theme class reference.

  gate    a stable hook that never rendered and isn't on the allowlist
          (scripts/hook-coverage-allowlist.json, one reason per entry).
          Any such hook -> exit 1.

The hook list comes from Flowershow core's own generator,
scripts/theme-class-reference.mjs, run against default-theme.css at
--core-ref (default origin/main: what flowershow.me serves) in a local
checkout (--core, default ../flowershow next to this repo). Without a
checkout both files are fetched from GitHub's main branch. The
compatibility utilities (.prose, .overflow-hidden) are not public API and
are skipped.

Routes default to verify-demo-routes.py's STANDARD_ROUTES plus
FEATURE_ROUTES, like contact-sheet.py, plus a missing page for the 404
hooks. Browsing goes through the gstack `browse` daemon
(BROWSE_BIN overrides its path).
"""

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
import tempfile
from importlib import import_module
from pathlib import Path
from urllib.request import urlopen

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True  # no __pycache__ from importing verify-demo-routes

_routes = import_module("verify-demo-routes")
DEFAULT_ROUTES = [route for route, _ in _routes.STANDARD_ROUTES + _routes.FEATURE_ROUTES]
# Loaded only for coverage: the 404 page has to be a 404, and an unknown
# tag is an odd page to screenshot, so neither is a demo route.
COVERAGE_ONLY_ROUTES = ["/this-page-does-not-exist", "/tags/no-such-tag"]
ALLOWLIST = HERE / "hook-coverage-allowlist.json"

CORE_FILES = {
    "generator": "scripts/theme-class-reference.mjs",
    "css": "apps/flowershow/styles/default-theme.css",
}
CORE_RAW = "https://raw.githubusercontent.com/flowershow/flowershow/main/"

BROWSE = os.environ.get("BROWSE_BIN") or str(
    Path.home() / ".claude/skills/gstack/browse/dist/browse"
)

VIEWPORTS = {"desktop": "1280x900", "mobile": "390x844"}

# Every class on every element, SVG included. Starts with `return` because
# code containing `await` runs as a function body (see contact-sheet.py).
COLLECT_JS = """
return (async () => {
  await new Promise(r => setTimeout(r, %d));
  const names = new Set();
  for (const el of document.querySelectorAll('*')) for (const c of el.classList) names.add(c);
  return JSON.stringify([...names]);
})()
"""

# States that only exist after a visitor does something. Each runs once, on
# a fresh load of the first route where all its steps can run, trying only
# routes where the plain crawl saw the first step's target. `js` steps run
# as page script. The classes seen after every step are recorded. Dialogs
# and menus render the same markup on every page, so one is enough.
#
# The navbar dropdown opens on hover; a click after that closes it again.
INTERACTIONS = (
    ("scrolled", "desktop", [("js", "window.scrollTo(0, 800)")]),
    ("navbar dropdown", "desktop", [("hover", ".site-navbar-dropdown-trigger")]),
    ("image lightbox", "desktop", [("click", ".image-lightbox-trigger")]),
    ("mobile nav", "mobile", [("click", ".site-navbar-mobile-nav-button"),
                              ("click", ".mobile-nav-dropdown-trigger")]),
    ("sidebar drawer", "mobile", [("click", ".site-subnav-menu-button")]),
)


def browse(*args: str) -> str:
    result = subprocess.run([BROWSE, *args], capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"browse {args[0]} failed: {(result.stderr or result.stdout).strip()}")
    return result.stdout.strip()


def collect(settle_ms: int = 300) -> set[str]:
    return set(json.loads(browse("js", COLLECT_JS % settle_ms)))


# Some targets (the graph panel, PDF pages) render a moment after load.
WAIT_JS = """
return (async () => {
  for (let i = 0; i < 25; i++) {
    if (document.querySelector(%s)) return 'true';
    await new Promise(r => setTimeout(r, 200));
  }
  return 'false';
})()
"""


def present(selector: str) -> bool:
    return browse("js", WAIT_JS % json.dumps(selector)) == "true"


def load(url: str) -> None:
    browse("goto", url)
    try:
        browse("wait", "--networkidle")
    except RuntimeError:
        pass  # a page that keeps a connection open still gets collected


def core_sources(core: Path, ref: str) -> dict[str, str]:
    if (core / ".git").exists():
        if ref.startswith("origin/"):
            # a stale remote ref would quietly check against old hooks
            subprocess.run(["git", "-C", str(core), "fetch", "-q", "origin", ref.removeprefix("origin/")],
                           capture_output=True)
        return {
            key: subprocess.run(
                ["git", "-C", str(core), "show", f"{ref}:{path}"],
                capture_output=True, text=True, check=True,
            ).stdout
            for key, path in CORE_FILES.items()
        }
    print(f"no core checkout at {core}; fetching from GitHub main", file=sys.stderr)
    return {key: urlopen(CORE_RAW + path, timeout=20).read().decode() for key, path in CORE_FILES.items()}


def stable_hooks(core: Path, ref: str) -> dict[str, list[str]]:
    """{group id: [class, ...]} as theme-class-reference.mjs groups them."""
    sources = core_sources(core, ref)
    with tempfile.TemporaryDirectory() as tmp:
        generator = Path(tmp) / "theme-class-reference.mjs"
        css = Path(tmp) / "default-theme.css"
        generator.write_text(sources["generator"])
        css.write_text(sources["css"])
        script = (
            "const m = await import(process.argv[1]);"
            "const css = (await import('node:fs')).readFileSync(process.argv[2], 'utf8');"
            "const groups = {};"
            "for (const c of m.extractClassNames(css)) (groups[m.classifyClassName(c)] ??= []).push(c);"
            "console.log(JSON.stringify(groups));"
        )
        out = subprocess.run(
            ["node", "--input-type=module", "-e", script, str(generator), str(css)],
            capture_output=True, text=True, check=True,
        ).stdout
    groups = json.loads(out)
    groups.pop("compatibility", None)
    # in the reference's own order (GROUPS isn't exported, so read its ids)
    order = re.findall(r"^\s*id:\s*'([^']+)'", sources["generator"], flags=re.M)
    rank = {group: i for i, group in enumerate(order)}
    return dict(sorted(groups.items(), key=lambda item: rank.get(item[0], len(rank))))


def crawl(base: str, routes: list[str]) -> dict[str, set[str]]:
    """{class: {where it was first seen, ...}} across routes, viewports and interactions."""
    seen: dict[str, set[str]] = {}

    def record(names: set[str], where: str) -> None:
        for name in names:
            seen.setdefault(name, set()).add(where)

    for viewport, size in VIEWPORTS.items():
        browse("viewport", size)
        for route in routes:
            load(base + route)
            record(collect(), f"{route} {viewport}")
        for label, wanted, steps in INTERACTIONS:
            if wanted != viewport:
                continue
            first = steps[0][1].lstrip(".") if steps[0][0] != "js" else None
            candidates = [r for r in routes if first is None or f"{r} {viewport}" in seen.get(first, ())]
            for route in candidates:
                load(base + route)
                done = 0
                for kind, target in steps:
                    try:
                        if kind == "js":
                            browse("js", target)
                        else:
                            if not present(target):
                                break
                            browse(kind, target)
                    except RuntimeError:
                        break
                    record(collect(500), f"{route} {viewport} after {label}")
                    done += 1
                if done == len(steps):
                    break
            else:
                print(f"  NOTE  interaction {label!r} ({viewport}) found no route to run on")
    return seen


def load_allowlist() -> list[dict]:
    return json.loads(ALLOWLIST.read_text())["hooks"]


def allow_reason(name: str, allowlist: list[dict]) -> str | None:
    for entry in allowlist:
        if fnmatch.fnmatchcase(name, entry["match"]):
            return entry["reason"]
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("base_url")
    parser.add_argument("--route", action="append", dest="routes",
                        help="route to load (repeatable; default: the standard demo routes)")
    parser.add_argument("--core", default=str(HERE.parent.parent / "flowershow"),
                        help="Flowershow core checkout (default: ../flowershow)")
    parser.add_argument("--core-ref", default="origin/main",
                        help="git ref of core to read the hooks from (default: origin/main)")
    parser.add_argument("--json", help="write the full result here")
    args = parser.parse_args()

    if not os.access(BROWSE, os.X_OK):
        print(f"gstack browse not found at {BROWSE} (set BROWSE_BIN)", file=sys.stderr)
        return 2

    base = args.base_url.rstrip("/")
    routes = args.routes or DEFAULT_ROUTES + COVERAGE_ONLY_ROUTES
    groups = stable_hooks(Path(args.core), args.core_ref)
    allowlist = load_allowlist()
    seen = crawl(base, routes)

    result = {"base_url": base, "routes": routes, "core_ref": args.core_ref, "groups": {}}
    missing_total = 0
    for group, hooks in groups.items():
        rendered = sorted(h for h in hooks if h in seen)
        allowed = {h: r for h in hooks if h not in seen and (r := allow_reason(h, allowlist))}
        missing = sorted(h for h in hooks if h not in seen and h not in allowed)
        missing_total += len(missing)
        result["groups"][group] = {
            "rendered": {h: sorted(seen[h]) for h in rendered},
            "allowlisted": allowed,
            "missing": missing,
        }
        status = "FAIL" if missing else "PASS"
        print(f"  {status}  {group}: {len(rendered)}/{len(hooks)} rendered, "
              f"{len(allowed)} allowlisted, {len(missing)} missing")
        for hook in missing:
            print(f"          .{hook}")

    # allowlist entries matching nothing are stale: say so, don't fail
    every_hook = [h for hooks in groups.values() for h in hooks]
    for entry in allowlist:
        if not any(fnmatch.fnmatchcase(h, entry["match"]) for h in every_hook):
            print(f"  NOTE  allowlist entry {entry['match']!r} matches no current hook")
    transient = [e["match"] for e in allowlist if e.get("transient")]
    unexpected_rendered = [
        h for h in every_hook
        if h in seen and allow_reason(h, allowlist)
        and not any(fnmatch.fnmatchcase(h, t) for t in transient)
    ]
    for hook in unexpected_rendered:
        print(f"  NOTE  .{hook} is allowlisted but rendered; the entry may be removable")

    if args.json:
        Path(args.json).write_text(json.dumps(result, indent=2))
    total = len(every_hook)
    print(f"\n{total - missing_total}/{total} stable hooks rendered or allowlisted; "
          f"{missing_total} missing")
    return 1 if missing_total else 0


if __name__ == "__main__":
    sys.exit(main())
