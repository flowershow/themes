#!/usr/bin/env python3
"""Read one scalar field from a theme entry in docs/features.yaml."""

from pathlib import Path
import re
import sys


def read_field(text: str, theme_id: str, field: str) -> str:
    active = False
    item_indent = -1
    for line in text.splitlines():
        item = re.match(r"^(\s*)- id:\s*(\S+)\s*$", line)
        if item:
            if active and len(item.group(1)) == item_indent:
                break
            active = item.group(2) == theme_id
            item_indent = len(item.group(1))
            continue
        if active:
            match = re.match(rf"^\s+{re.escape(field)}:\s*(\S+)", line)
            if match:
                value = match.group(1)
                return "" if value == "null" else value
    return ""


def main(argv: list[str]) -> int:
    if len(argv) != 4 or not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", argv[3]):
        print("usage: read-feature-field.py FEATURES_YAML THEME_ID FIELD", file=sys.stderr)
        return 2
    try:
        value = read_field(Path(argv[1]).read_text(encoding="utf-8"), argv[2], argv[3])
    except OSError as error:
        print(error, file=sys.stderr)
        return 2
    if value:
        print(value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
