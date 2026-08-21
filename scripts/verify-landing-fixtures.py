#!/usr/bin/env python3
"""Enforce ownership and release-boundary contracts for published fixtures."""

from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
import re
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class FixtureContract:
    path: str
    css_path: str
    label: str
    required: tuple[str, ...]
    forbidden: tuple[str, ...]
    template_path: str = ""
    metadata_path: str = ""
    css_required: tuple[str, ...] = ()
    css_forbidden: tuple[str, ...] = ()


CONTRACTS = (
    FixtureContract(
        path="material-draft/demo-landing.md",
        css_path="material-draft/demo-landing.css",
        label="Material-inspired",
        required=(
            'data-owned-fixture="material-inspired"',
            'data-theme-status="preview"',
            "Material-inspired preview",
            "https://squidfunk.github.io/mkdocs-material/",
            "/docs/kitchen-sink",
            "/blog",
        ),
        forbidden=(
            "squidfunk/mkdocs-material",
            "Documentation that simply works",
            "Trusted in the industry",
            "What our users say",
            "Become a sponsor",
            "AWS",
            "Google",
            "Microsoft",
            "Netflix",
            "<svg",
            "<path",
            'href="/kitchen-sink"',
            "url(data:image/svg",
            "url(http",
        ),
    ),
)

ALLOWED_GLOBAL_SELECTORS = {
    ".site-navbar-site-name",
    ".site-navbar-site-title",
}
SHOWCASE_FORBIDDEN = (
    "<svg",
    "<path",
    'href="/kitchen-sink"',
    "Review matrix",
    "Release boundary",
    "FLOWERSHOW THEME LAB",
    "<header",
    "<nav",
)
THEME_FORBIDDEN = {
    "monospace": (
        "Code Storage",
        "Pierre Computer Company",
        "code.storage",
        "pierre.co",
        "99.99%",
        "60x faster",
        "$1.00",
        "$0.15",
        "SLA",
        "Cloudflare",
        "Coinbase",
        "Discord",
        "Stripe",
    ),
}
THEME_REQUIRED = {
    "monospace": ('class="ts-node-mark"',),
}


def verify(contract: FixtureContract) -> list[str]:
    markdown, render_error = load_markdown(contract)
    if render_error:
        return [f"{contract.label}: {render_error}"]
    css = (ROOT / contract.css_path).read_text(encoding="utf-8")
    folded_markdown = markdown.casefold()
    folded_artifacts = f"{markdown}\n{css}".casefold()
    failures = [
        f'{contract.label}: missing required content: {value}'
        for value in contract.required
        if value.casefold() not in folded_markdown
    ]
    failures.extend(
        f'{contract.label}: forbidden content remains: {value}'
        for value in contract.forbidden
        if contains_forbidden(folded_artifacts, value)
    )
    failures.extend(
        f'{contract.label}: landing CSS missing required selector: {value}'
        for value in contract.css_required
        if value.casefold() not in css.casefold()
    )
    failures.extend(
        f'{contract.label}: obsolete landing CSS remains: {value}'
        for value in contract.css_forbidden
        if value.casefold() in css.casefold()
    )
    if css.count("{") != css.count("}"):
        failures.append(
            f"{contract.label}: landing CSS braces are not balanced "
            f"({css.count('{')} open / {css.count('}')} close)"
        )
    h1_count = len(re.findall(r"<h1(?:\s|>)", markdown, flags=re.IGNORECASE))
    if h1_count != 1:
        failures.append(
            f"{contract.label}: landing must have exactly one h1 (found {h1_count})"
        )
    return failures


def load_markdown(contract: FixtureContract) -> tuple[str, str]:
    if not contract.metadata_path:
        return (ROOT / contract.path).read_text(encoding="utf-8"), ""
    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary) / "index.md"
        result = subprocess.run(
            [
                "python3",
                str(ROOT / "scripts/render-theme-showcase.py"),
                str(ROOT / contract.template_path),
                str(ROOT / contract.metadata_path),
                str(output),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            return "", f"showcase rendering failed: {result.stderr.strip()}"
        return output.read_text(encoding="utf-8"), ""


def contains_forbidden(folded_text: str, value: str) -> bool:
    """Match identifiers as terms while keeping markup/fragments literal."""
    folded_value = value.casefold()
    if folded_value[0].isalnum() and folded_value[-1].isalnum():
        return re.search(
            rf"(?<!\w){re.escape(folded_value)}(?!\w)", folded_text
        ) is not None
    return folded_value in folded_text


def _next_css_delimiter(css: str, start: int) -> tuple[int, str]:
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


def _matching_css_brace(css: str, opening: int) -> int:
    depth = 1
    quote = ""
    escaped = False
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


def _split_css_selectors(header: str) -> list[str]:
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


def _walk_css_rules(css: str) -> list[str]:
    selectors = []
    cursor = 0
    while cursor < len(css):
        delimiter, kind = _next_css_delimiter(css, cursor)
        if not kind:
            break
        header = css[cursor:delimiter].strip()
        if kind == ";":
            cursor = delimiter + 1
            continue
        closing = _matching_css_brace(css, delimiter)
        body = css[delimiter + 1 : closing]
        if header.startswith("@"):
            at_rule = header.split(None, 1)[0].casefold()
            if at_rule not in {"@font-face", "@page", "@property"} and not (
                at_rule.endswith("keyframes")
            ):
                selectors.extend(_walk_css_rules(body))
        elif header:
            selectors.extend(_split_css_selectors(header))
        cursor = closing + 1
    return selectors


def css_rule_selectors(css: str) -> list[str]:
    """Return ordinary selectors from a brace-aware recursive CSS walk."""
    without_comments = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    return _walk_css_rules(without_comments)


def css_urls(css: str) -> list[str]:
    """Extract normalized url(...) values regardless of quotes or whitespace."""
    values = []
    for match in re.finditer(r"url\(\s*([^)]*?)\s*\)", css, flags=re.IGNORECASE):
        value = match.group(1).strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1].strip()
        values.append(value)
    return values


def verify_showcase(metadata_path: Path) -> tuple[str, list[str]]:
    relative = metadata_path.relative_to(ROOT)
    label = str(relative.parent)
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if isinstance(metadata, dict) and isinstance(metadata.get("name"), str):
            label = metadata["name"]
    except (OSError, json.JSONDecodeError):
        metadata = {}

    css_path = metadata_path.with_name("demo-landing.css")
    template_path = metadata_path.with_name("demo-showcase.template.md")
    if not css_path.is_file():
        return label, [f"{label}: missing demo-landing.css"]
    if not template_path.is_file():
        return label, [f"{label}: missing demo-showcase.template.md"]

    contract = FixtureContract(
        path="",
        css_path=str(css_path.relative_to(ROOT)),
        label=label,
        required=(),
        forbidden=(),
        template_path=str(template_path.relative_to(ROOT)),
        metadata_path=str(relative),
    )
    markdown, render_error = load_markdown(contract)
    if render_error:
        return label, [f"{label}: {render_error}"]

    css = css_path.read_text(encoding="utf-8")
    wrapper = metadata.get("wrapperClass", "")
    slug = metadata.get("slug", "")
    status = metadata.get("status", "")
    required = (
        f'data-theme-showcase="{escape(str(slug), quote=True)}"',
        f'data-theme-status="{escape(str(status), quote=True)}"',
        "Publish with Flowershow",
        "/docs/kitchen-sink",
        "/blog",
    ) + THEME_REQUIRED.get(str(slug), ())
    failures = [
        f"{label}: missing required showcase content: {value}"
        for value in required
        if value.casefold() not in markdown.casefold()
    ]
    artifacts = f"{markdown}\n{css}".casefold()
    forbidden = SHOWCASE_FORBIDDEN + THEME_FORBIDDEN.get(str(slug), ())
    failures.extend(
        f"{label}: forbidden content remains: {value}"
        for value in forbidden
        if contains_forbidden(artifacts, value)
    )
    h1_count = len(re.findall(r"<h1(?:\s|>)", markdown, flags=re.IGNORECASE))
    if h1_count != 1:
        failures.append(f"{label}: showcase must have exactly one h1 (found {h1_count})")
    if css.count("{") != css.count("}"):
        failures.append(f"{label}: showcase CSS braces are not balanced")
    if wrapper:
        unscoped = [
            selector
            for selector in css_rule_selectors(css)
            if f".{wrapper}" not in selector
            and selector not in ALLOWED_GLOBAL_SELECTORS
        ]
        failures.extend(
            f"{label}: showcase CSS selector is not scoped under .{wrapper}: {selector}"
            for selector in unscoped
        )
    for value in css_urls(css):
        normalized = value.casefold()
        if normalized.startswith(("http:", "https:", "//", "data:")):
            failures.append(f"{label}: external CSS URL is not allowed: {value}")
    return label, failures


def main() -> int:
    failed = False
    for contract in CONTRACTS:
        failures = verify(contract)
        if failures:
            failed = True
            for failure in failures:
                print(f"  FAIL  {failure}")
        else:
            print(f"  PASS  {contract.label} landing is a Flowershow-owned specimen")
    for metadata_path in sorted(ROOT.glob("*/demo-showcase.json")):
        label, failures = verify_showcase(metadata_path)
        if failures:
            failed = True
            for failure in failures:
                print(f"  FAIL  {failure}")
        else:
            print(f"  PASS  {label} showcase passes the theme-local fixture contract")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
