#!/usr/bin/env python3
"""Keep and check a theme's coverage ledger: one decision per hook group.

    scripts/coverage-ledger.py sync  <theme-dir> [--ledger FILE]
    scripts/coverage-ledger.py check <theme-dir> [--ledger FILE] [--leaks FILE]
                                     [--core DIR] [--core-ref REF]

hook-coverage.py proves the demo site renders every stable hook. This
ledger records what the theme *did* about each group of them, so nothing
is left to the default theme by accident. The file is
<theme-dir>/coverage.yaml unless --ledger says otherwise. Procedure for
filling it in: docs/coverage-ledger.md.

  sync    create the ledger, or add groups core has gained since. Every
          new group starts as `decision: todo`. Existing decisions are
          never touched; groups core has dropped are reported, not deleted.
  check   exit 1 unless every group has a valid, consistent decision:
            styled       theme.css selects at least one hook in the group
            inherits-ok  theme.css selects none of them, and the note says
                         what was looked at
            gap          known unfinished work (allowed; it's reported)
          plus a non-empty note, and `gaps:` patterns that match hooks in
          their group. Gaps never fail the check: they are the honest
          answer, and the handoff lists them.

With --leaks (the JSON from palette-leaks.py), check also counts the
off-palette colours found in each group and warns when an `inherits-ok`
group has any. That's a report, not a gate.

Hooks and groups come from Flowershow core's theme-class-reference.mjs,
read the same way hook-coverage.py reads them.

coverage.yaml is a strict YAML subset, readable by any YAML parser, that
this script parses without PyYAML: `key: value` lines indented by two
spaces, values plain or double-quoted on one line, `#` comments on their
own line.
"""

import argparse
import fnmatch
import json
import re
import sys
from importlib import import_module
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.dont_write_bytecode = True

_hooks = import_module("hook-coverage")

DECISIONS = ("styled", "inherits-ok", "gap")
TODO = "todo"

HEADER = """\
# Coverage ledger for {theme}/theme.css: one deliberate decision per group
# of stable theme hooks (flowershow.app/docs/reference/theme-class-reference).
# Procedure: docs/coverage-ledger.md
# Check:     scripts/coverage-ledger.py check {theme}
#
#   decision: styled       theme.css has selectors for this group's hooks
#             inherits-ok  no selectors; you looked at the render and the
#                          default theme + this theme's tokens look right
#             gap          needs work; say what in the note or in gaps
#             todo         not decided yet (check fails)
#   note:     what you looked at (routes, modes) and why the decision holds
#   gaps:     optional; hook pattern -> what is still wrong
#
# Quote a value with "..." if it contains ": " or " #", or starts with a
# YAML symbol. Keys starting with * must be quoted too.
"""


class LedgerError(ValueError):
    pass


# --- the YAML subset -------------------------------------------------------

PLAIN_START_FORBIDDEN = set("\"'[]{}&*!|>%@`,?:-#")


def parse_scalar(raw: str, where: str) -> str:
    raw = raw.strip()
    if raw.startswith('"'):
        try:
            value, end = json.JSONDecoder().raw_decode(raw)
        except json.JSONDecodeError as error:
            raise LedgerError(f"{where}: bad quoted string ({error.msg})") from None
        rest = raw[end:].strip()
        if rest and not rest.startswith("#"):
            raise LedgerError(f"{where}: text after the closing quote")
        if not isinstance(value, str):
            raise LedgerError(f"{where}: expected a string")
        return value
    raw = re.split(r"\s#", raw, maxsplit=1)[0].rstrip()
    if raw and raw[0] in PLAIN_START_FORBIDDEN:
        raise LedgerError(f"{where}: quote this value, it starts with {raw[0]!r}")
    if ": " in raw or raw.endswith(":"):
        raise LedgerError(f"{where}: quote this value, it contains ': '")
    return raw


def split_key(line: str, where: str) -> tuple[str, str]:
    if line.startswith('"'):
        try:
            key, end = json.JSONDecoder().raw_decode(line)
        except json.JSONDecodeError as error:
            raise LedgerError(f"{where}: bad quoted key ({error.msg})") from None
        rest = line[end:]
        if not rest.startswith(":"):
            raise LedgerError(f"{where}: expected ':' after the key")
        return key, rest[1:]
    match = re.match(r"([A-Za-z0-9_][^:\s]*):(\s|$)", line)
    if not match:
        raise LedgerError(f"{where}: expected `key: value`")
    return match.group(1), line[match.end(1) + 1:]


def parse_ledger(text: str) -> dict:
    """{'theme': str, 'groups': {id: {'decision', 'note', 'gaps': {pattern: text}}}}"""
    ledger: dict = {"groups": {}}
    group = None
    in_gaps = False
    for number, line in enumerate(text.splitlines(), 1):
        where = f"line {number}"
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "\t" in line[: len(line) - len(line.lstrip())]:
            raise LedgerError(f"{where}: indent with spaces, not tabs")
        indent = len(line) - len(line.lstrip(" "))
        key, rest = split_key(line.strip(), where)
        if indent == 0:
            group, in_gaps = None, False
            if key == "groups":
                if rest.strip():
                    raise LedgerError(f"{where}: `groups:` takes no value")
            elif key == "theme":
                ledger["theme"] = parse_scalar(rest, where)
            else:
                raise LedgerError(f"{where}: unknown top-level key {key!r}")
        elif indent == 2:
            if rest.strip():
                raise LedgerError(f"{where}: a group id takes no value")
            if key in ledger["groups"]:
                raise LedgerError(f"{where}: group {key!r} appears twice")
            group, in_gaps = ledger["groups"].setdefault(key, {"gaps": {}}), False
        elif indent == 4 and group is not None:
            in_gaps = False
            if key == "gaps":
                if rest.strip():
                    raise LedgerError(f"{where}: `gaps:` takes no value")
                in_gaps = True
            elif key in ("decision", "note"):
                group[key] = parse_scalar(rest, where)
            else:
                raise LedgerError(f"{where}: unknown group key {key!r}")
        elif indent == 6 and in_gaps:
            group["gaps"][key] = parse_scalar(rest, where)
        else:
            raise LedgerError(f"{where}: unexpected indent ({indent} spaces)")
    return ledger


def quote(value: str) -> str:
    if value and value[0] not in PLAIN_START_FORBIDDEN and ": " not in value \
            and " #" not in value and not value.endswith(":") and value == value.strip():
        return value
    return json.dumps(value, ensure_ascii=False)


def quote_key(key: str) -> str:
    return key if re.fullmatch(r"[A-Za-z0-9_][^:\s\"]*", key) else json.dumps(key)


def render_ledger(theme: str, groups: dict, order: list[str]) -> str:
    out = [HEADER.format(theme=theme), f"theme: {quote(theme)}", "groups:"]
    for group_id in order:
        entry = groups[group_id]
        out.append(f"  {quote_key(group_id)}:")
        out.append(f"    decision: {entry.get('decision', TODO)}")
        out.append(f"    note: {quote(entry.get('note', ''))}")
        if entry.get("gaps"):
            out.append("    gaps:")
            for pattern, text in entry["gaps"].items():
                out.append(f"      {quote_key(pattern)}: {quote(text)}")
    return "\n".join(out) + "\n"


# --- what the theme selects ------------------------------------------------

def selected_classes(css: str) -> set[str]:
    """Class names theme.css selects; the same extraction core uses."""
    scrubbed = re.sub(r"/\*[\s\S]*?\*/", " ", css)
    scrubbed = re.sub(r"url\((?:\\.|[^)])*\)", " ", scrubbed, flags=re.I)
    scrubbed = re.sub(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'", " ", scrubbed)
    return set(re.findall(r"\.([A-Za-z_][A-Za-z0-9_-]*)\b", scrubbed))


# --- commands --------------------------------------------------------------

def cmd_sync(theme: str, path: Path, groups: dict[str, list[str]]) -> int:
    existing = parse_ledger(path.read_text()) if path.exists() else {"groups": {}}
    merged = dict(existing["groups"])
    added = [g for g in groups if g not in merged]
    for group_id in added:
        merged[group_id] = {"decision": TODO, "note": "", "gaps": {}}
    dropped = [g for g in merged if g not in groups]
    order = list(groups) + dropped
    path.write_text(render_ledger(existing.get("theme", theme), merged, order))
    verb = "updated" if existing["groups"] else "created"
    print(f"{verb} {path}: {len(added)} group(s) added as todo, {len(groups)} in core")
    for group_id in dropped:
        print(f"  NOTE  {group_id!r} is no longer a hook group in core; "
              "check its note still applies elsewhere, then delete it")
    return 0


def cmd_check(theme: str, path: Path, css: str, groups: dict[str, list[str]],
              leaks: dict | None) -> int:
    if not path.exists():
        print(f"no ledger at {path}; run: scripts/coverage-ledger.py sync {theme}", file=sys.stderr)
        return 1
    ledger = parse_ledger(path.read_text())
    errors: list[str] = []
    warnings: list[str] = []
    if ledger.get("theme") != theme:
        errors.append(f"theme is {ledger.get('theme')!r}, expected {theme!r}")
    for group_id in groups:
        if group_id not in ledger["groups"]:
            errors.append(f"{group_id}: missing (core added it; run sync)")
    for group_id in ledger["groups"]:
        if group_id not in groups:
            errors.append(f"{group_id}: not a hook group in core any more")

    selected = selected_classes(css)
    leak_counts = (leaks or {}).get("by_group", {})
    rows = []
    for group_id, hooks in groups.items():
        entry = ledger["groups"].get(group_id)
        if entry is None:
            continue
        decision = entry.get("decision", "")
        note = entry.get("note", "").strip()
        styled = sorted(h for h in hooks if h in selected)
        if decision == TODO or not decision:
            errors.append(f"{group_id}: no decision yet")
        elif decision not in DECISIONS:
            errors.append(f"{group_id}: decision {decision!r} is not one of {', '.join(DECISIONS)}")
        elif decision == "styled" and not styled:
            errors.append(f"{group_id}: marked styled, but theme.css selects none of its "
                          f"{len(hooks)} hooks (inherits-ok or gap?)")
        elif decision == "inherits-ok" and styled:
            errors.append(f"{group_id}: marked inherits-ok, but theme.css selects "
                          f"{', '.join('.' + h for h in styled[:4])}"
                          f"{' …' if len(styled) > 4 else ''} (styled?)")
        if decision != TODO and not note:
            errors.append(f"{group_id}: empty note; say what you looked at")
        for pattern in entry["gaps"]:
            if not any(fnmatch.fnmatchcase(h, pattern) for h in hooks):
                errors.append(f"{group_id}: gap pattern {pattern!r} matches none of this group's hooks")
        leaked = leak_counts.get(group_id, {}).get("elements", 0)
        if leaks is not None and decision == "inherits-ok" and leaked:
            warnings.append(f"{group_id}: inherits-ok, but {leaked} element(s) use off-palette "
                            "colours here (see palette-leaks output)")
        rows.append((group_id, decision or "-", f"{len(styled)}/{len(hooks)}",
                     len(entry["gaps"]) + (decision == "gap"),
                     str(leaked) if leaks is not None else "-"))

    width = max(len(r[0]) for r in rows) if rows else 5
    print(f"  {'group':<{width}}  {'decision':<11}  selects  gaps  leaks")
    for group_id, decision, sel, gap_count, leaked in rows:
        print(f"  {group_id:<{width}}  {decision:<11}  {sel:>7}  {gap_count:>4}  {leaked:>5}")
    for group_id, entry in ledger["groups"].items():
        if entry.get("decision") == "gap":
            print(f"  GAP   {group_id}: {entry.get('note', '')}")
        for pattern, text in entry["gaps"].items():
            print(f"  GAP   {group_id} .{pattern}: {text}")
    for warning in warnings:
        print(f"  WARN  {warning}")
    for error in errors:
        print(f"  FAIL  {error}")

    decided = sum(1 for r in rows if r[1] in DECISIONS)
    gaps = sum(r[3] for r in rows)
    print(f"\n{decided}/{len(groups)} groups decided; {gaps} gap(s); "
          f"{len(errors)} error(s); {len(warnings)} warning(s)")
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=("sync", "check"))
    parser.add_argument("theme_dir")
    parser.add_argument("--ledger", help="ledger file (default: <theme-dir>/coverage.yaml)")
    parser.add_argument("--leaks", help="palette-leaks.py JSON to cross-check (check only)")
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
    path = Path(args.ledger) if args.ledger else theme_dir / "coverage.yaml"
    groups = _hooks.stable_hooks(Path(args.core), args.core_ref)
    leaks = json.loads(Path(args.leaks).read_text()) if args.leaks else None
    try:
        if args.command == "sync":
            return cmd_sync(theme, path, groups)
        return cmd_check(theme, path, css_path.read_text(), groups, leaks)
    except LedgerError as error:
        print(f"{path}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
