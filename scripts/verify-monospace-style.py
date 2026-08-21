#!/usr/bin/env python3
"""Verify effective desktop declarations for the restrained Monospace page."""

from dataclasses import dataclass
from pathlib import Path
import re
import sys


DESKTOP_WIDTH = 1280


@dataclass(frozen=True)
class Rule:
    selector: str
    declarations: dict[str, str]
    order: int


def remove_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)


def next_delimiter(css: str, start: int) -> tuple[int, str]:
    quote = ""
    escaped = False
    parentheses = 0
    for index in range(start, len(css)):
        character = css[index]
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif quote:
            if character == quote:
                quote = ""
        elif character in "\"'":
            quote = character
        elif character == "(":
            parentheses += 1
        elif character == ")" and parentheses:
            parentheses -= 1
        elif not parentheses and character in "{;":
            return index, character
    return len(css), ""


def matching_brace(css: str, opening: int) -> int:
    quote = ""
    escaped = False
    depth = 1
    for index in range(opening + 1, len(css)):
        character = css[index]
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif quote:
            if character == quote:
                quote = ""
        elif character in "\"'":
            quote = character
        elif character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return index
    return len(css)


def split_selectors(header: str) -> list[str]:
    selectors = []
    start = 0
    quote = ""
    escaped = False
    parentheses = 0
    brackets = 0
    for index, character in enumerate(header):
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif quote:
            if character == quote:
                quote = ""
        elif character in "\"'":
            quote = character
        elif character == "(":
            parentheses += 1
        elif character == ")" and parentheses:
            parentheses -= 1
        elif character == "[":
            brackets += 1
        elif character == "]" and brackets:
            brackets -= 1
        elif character == "," and not parentheses and not brackets:
            selectors.append(header[start:index].strip())
            start = index + 1
    selectors.append(header[start:].strip())
    return selectors


def parse_declarations(body: str) -> dict[str, str]:
    declarations = {}
    for match in re.finditer(r"(?:^|;)\s*([a-zA-Z-]+)\s*:\s*([^;]+)", body):
        declarations[match.group(1).casefold()] = match.group(2).strip()
    return declarations


def media_applies(header: str, width: int) -> bool:
    for value in re.findall(r"max-width\s*:\s*(\d+)px", header, flags=re.I):
        if width > int(value):
            return False
    for value in re.findall(r"min-width\s*:\s*(\d+)px", header, flags=re.I):
        if width < int(value):
            return False
    return True


def parse_rules(css: str, width: int = DESKTOP_WIDTH) -> list[Rule]:
    rules: list[Rule] = []

    def walk(block: str) -> None:
        cursor = 0
        while cursor < len(block):
            delimiter, kind = next_delimiter(block, cursor)
            if not kind:
                break
            header = block[cursor:delimiter].strip()
            if kind == ";":
                cursor = delimiter + 1
                continue
            closing = matching_brace(block, delimiter)
            body = block[delimiter + 1 : closing]
            if header.casefold().startswith("@media"):
                if media_applies(header, width):
                    walk(body)
            elif header.startswith("@"):
                at_rule = header.split(None, 1)[0].casefold()
                if at_rule not in {"@font-face", "@page", "@property"} and not (
                    at_rule.endswith("keyframes")
                ):
                    walk(body)
            elif header:
                declarations = parse_declarations(body)
                for selector in split_selectors(header):
                    rules.append(Rule(selector, declarations, len(rules)))
            cursor = closing + 1

    walk(remove_comments(css))
    return rules


def specificity(selector: str) -> tuple[int, int, int]:
    ids = len(re.findall(r"#[a-zA-Z0-9_-]+", selector))
    classes = len(re.findall(r"\.[a-zA-Z0-9_-]+|\[[^]]+\]|:(?!:)[a-zA-Z-]+", selector))
    elements = len(
        re.findall(r"(?<![-_#.a-zA-Z0-9])(?:h1|h2)(?![-_a-zA-Z0-9])|::[a-zA-Z-]+", selector)
    )
    return ids, classes, elements


def matching_target(selector: str, target: str) -> bool:
    compact = re.sub(r"\s+", " ", selector.strip())
    if ".cs-landing" not in compact:
        return False
    if target == "h1":
        return re.search(r"(?:^|[ >+~])h1$", compact) is not None
    if target == "h2":
        return re.search(r"(?:^|[ >+~])h2$", compact) is not None
    if target == "hero":
        return compact.endswith(".ts-hero-grid")
    raise ValueError(target)


def effective_property(rules: list[Rule], target: str, property_name: str) -> str:
    candidates = []
    for rule in rules:
        if matching_target(rule.selector, target) and property_name in rule.declarations:
            value = rule.declarations[property_name]
            important = int("!important" in value.casefold())
            normalized = re.sub(r"\s*!important\s*$", "", value, flags=re.I)
            candidates.append((important, specificity(rule.selector), rule.order, normalized))
    return max(candidates)[-1] if candidates else ""


def verify(css: str) -> list[str]:
    rules = parse_rules(css)
    contracts = (
        ("h1", "font-size", "18px"),
        ("h2", "font-size", "16px"),
        (
            "hero",
            "grid-template-columns",
            "minmax(0, 1fr) minmax(280px, 420px)",
        ),
    )
    failures = []
    for target, property_name, expected in contracts:
        actual = effective_property(rules, target, property_name)
        if re.sub(r"\s+", "", actual) != re.sub(r"\s+", "", expected):
            failures.append(
                f"{target} effective {property_name} is {actual or '<missing>'}; "
                f"expected {expected}"
            )
    return failures


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: verify-monospace-style.py CSS", file=sys.stderr)
        return 2
    try:
        css = Path(argv[1]).read_text(encoding="utf-8")
    except OSError as error:
        print(error, file=sys.stderr)
        return 2
    failures = verify(css)
    for failure in failures:
        print(f"  FAIL  {failure}")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
