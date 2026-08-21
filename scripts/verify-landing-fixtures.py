#!/usr/bin/env python3
"""Enforce ownership and release-boundary contracts for published fixtures."""

from dataclasses import dataclass
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class FixtureContract:
    path: str
    css_path: str
    label: str
    required: tuple[str, ...]
    forbidden: tuple[str, ...]


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
    FixtureContract(
        path="codestorage-draft/demo-landing.md",
        css_path="codestorage-draft/demo-landing.css",
        label="Monospace",
        required=(
            'data-owned-fixture="monospace-specimen"',
            'data-theme-status="preview"',
            "FLOWERSHOW THEME LAB",
            "MONOSPACE SPECIMEN",
            "/docs/kitchen-sink",
            "/blog",
            'class="cs-node-mark"',
        ),
        forbidden=(
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
            "<svg",
            "<path",
            'href="/kitchen-sink"',
            "url(data:image/svg",
            "url(http",
        ),
    ),
)


def verify(contract: FixtureContract) -> list[str]:
    markdown = (ROOT / contract.path).read_text(encoding="utf-8")
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


def contains_forbidden(folded_text: str, value: str) -> bool:
    """Match identifiers as terms while keeping markup/fragments literal."""
    folded_value = value.casefold()
    if folded_value[0].isalnum() and folded_value[-1].isalnum():
        return re.search(
            rf"(?<!\w){re.escape(folded_value)}(?!\w)", folded_text
        ) is not None
    return folded_value in folded_text


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
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
