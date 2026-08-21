#!/usr/bin/env python3
"""Enforce ownership and release-boundary contracts for published fixtures."""

from dataclasses import dataclass
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
    FixtureContract(
        path="codestorage-draft/demo-landing.md",
        css_path="codestorage-draft/demo-landing.css",
        label="Monospace",
        required=(
            'data-theme-showcase="monospace"',
            'data-theme-status="preview"',
            "A sharper home for your Markdown",
            "Publish with Flowershow",
            "/docs/kitchen-sink",
            "/blog",
            'class="ts-node-mark"',
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
            "Review matrix",
            "Release boundary",
            "FLOWERSHOW THEME LAB",
            "<header",
            "<nav",
        ),
        template_path="_demo-content/theme-showcase.template.md",
        metadata_path="codestorage-draft/demo-showcase.json",
        css_required=(
            ".cs-landing .ts-hero",
            ".cs-landing .ts-card-grid",
            ".cs-landing .ts-steps",
            ".cs-landing .ts-theme-grid",
            ".cs-landing .ts-final-cta",
        ),
        css_forbidden=(
            ".cs-landing .cs-header",
            ".cs-landing .cs-pricing-grid",
            ".cs-landing .cs-ascii-table",
            ".cs-landing .cs-footer",
        ),
    ),
)


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
