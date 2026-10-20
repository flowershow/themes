#!/usr/bin/env python3
"""Keep and check a theme's coverage ledger: one decision per hook group.

    scripts/coverage-ledger.py sync  <theme-dir> [--core DIR] [--core-ref REF]
    scripts/coverage-ledger.py check <theme-dir> [--core DIR] [--core-ref REF]

hook-coverage.py proves the demo site renders every stable hook. The
ledger, <theme-dir>/coverage.md, records what the theme *did* about each
group of them, so nothing is left to the default theme by accident.
Procedure for filling it in: docs/coverage-ledger.md.

The ledger is plain Markdown, one section per group:

    ## navigation: styled

    What you looked at (routes, modes) and why the decision holds.

    - Gap `site-navbar-cta-button`: what is still wrong.

  sync    create the ledger, or append groups core has gained since as
          `todo`. Existing sections are never touched; groups core has
          dropped are reported, not deleted.
  check   exit 1 unless every core group has a section with a decision of
            styled       theme.css selects at least one hook in the group
            inherits-ok  theme.css selects none of them
            gap          known unfinished work (allowed; it's reported)
          and a non-empty note. Gaps never fail the check: they are the
          honest answer, and the handoff lists them.

Hooks and groups come from Flowershow core's theme-class-reference.mjs,
read the same way hook-coverage.py reads them.
"""

import argparse
import re
import sys
from importlib import import_module
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True

_hooks = import_module("hook-coverage")

DECISIONS = ("styled", "inherits-ok", "gap")
SECTION = re.compile(r"^## (\S+): (\S+)[ \t]*$", re.M)

HEADER = """\
# Coverage ledger: {theme}

One deliberate decision per group of stable theme hooks
(flowershow.app/docs/reference/theme-class-reference). Procedure:
docs/coverage-ledger.md. Check: `scripts/coverage-ledger.py check {theme}`.
Decisions: styled, inherits-ok, gap (todo fails the check).
"""


def parse_ledger(text: str) -> dict[str, tuple[str, str]]:
    """{group id: (decision, body)}; body is the note plus any `- Gap` lines."""
    parts = SECTION.split(text)
    return {parts[i]: (parts[i + 1], parts[i + 2].strip()) for i in range(1, len(parts), 3)}


def selected_classes(css: str) -> set[str]:
    """Class names theme.css selects; the same extraction core uses."""
    scrubbed = re.sub(r"/\*[\s\S]*?\*/", " ", css)
    scrubbed = re.sub(r"url\((?:\\.|[^)])*\)", " ", scrubbed, flags=re.I)
    scrubbed = re.sub(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'", " ", scrubbed)
    return set(re.findall(r"\.([A-Za-z_][A-Za-z0-9_-]*)\b", scrubbed))


def cmd_sync(theme: str, path: Path, groups: dict[str, list[str]]) -> int:
    text = path.read_text() if path.exists() else HEADER.format(theme=theme)
    existing = parse_ledger(text)
    added = [g for g in groups if g not in existing]
    text = text.rstrip("\n") + "\n" + "".join(f"\n## {g}: todo\n" for g in added)
    path.write_text(text)
    print(f"{path}: {len(added)} group(s) added as todo, {len(groups)} in core")
    for group_id in existing:
        if group_id not in groups:
            print(f"  NOTE  {group_id!r} is no longer a hook group in core; "
                  "check its note still applies elsewhere, then delete it")
    return 0


def cmd_check(theme: str, path: Path, css: str, groups: dict[str, list[str]]) -> int:
    if not path.exists():
        print(f"no ledger at {path}; run: scripts/coverage-ledger.py sync {theme}", file=sys.stderr)
        return 1
    ledger = parse_ledger(path.read_text())
    selected = selected_classes(css)
    errors, gaps = [], []
    for group_id in ledger:
        if group_id not in groups:
            errors.append(f"{group_id}: not a hook group in core any more")
    for group_id, hooks in groups.items():
        if group_id not in ledger:
            errors.append(f"{group_id}: missing (core added it; run sync)")
            continue
        decision, body = ledger[group_id]
        styled = sorted(h for h in hooks if h in selected)
        if decision not in DECISIONS:
            errors.append(f"{group_id}: decision {decision!r} is not one of {', '.join(DECISIONS)}")
        elif decision == "styled" and not styled:
            errors.append(f"{group_id}: marked styled, but theme.css selects none of its "
                          f"{len(hooks)} hooks (inherits-ok or gap?)")
        elif decision == "inherits-ok" and styled:
            errors.append(f"{group_id}: marked inherits-ok, but theme.css selects "
                          f"{', '.join('.' + h for h in styled[:4])}"
                          f"{' …' if len(styled) > 4 else ''} (styled?)")
        if decision in DECISIONS and not body:
            errors.append(f"{group_id}: empty note; say what you looked at")
        if decision == "gap":
            gaps.append(f"{group_id}: {body.splitlines()[0] if body else ''}")
        gaps += [f"{group_id} {line[6:]}" for line in body.splitlines() if line.startswith("- Gap ")]
        print(f"  {group_id:<14} {decision:<11} selects {len(styled)}/{len(hooks)}")
    for gap in gaps:
        print(f"  GAP   {gap}")
    for error in errors:
        print(f"  FAIL  {error}")
    print(f"\n{len(gaps)} gap(s); {len(errors)} error(s)")
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=("sync", "check"))
    parser.add_argument("theme_dir")
    parser.add_argument("--core", default=str(HERE.parent.parent / "flowershow"),
                        help="Flowershow core checkout (default: ../flowershow)")
    parser.add_argument("--core-ref", default="origin/main",
                        help="git ref of core to read the hooks from (default: origin/main)")
    args = parser.parse_args()

    theme_dir = Path(args.theme_dir)
    theme = theme_dir.resolve().name
    css_path = theme_dir / "theme.css"
    if not css_path.exists():
        print(f"no theme.css in {theme_dir}", file=sys.stderr)
        return 2
    path = theme_dir / "coverage.md"
    groups = _hooks.stable_hooks(Path(args.core), args.core_ref)
    if args.command == "sync":
        return cmd_sync(theme, path, groups)
    return cmd_check(theme, path, css_path.read_text(), groups)


if __name__ == "__main__":
    sys.exit(main())
