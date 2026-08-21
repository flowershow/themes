#!/usr/bin/env python3
"""Enforce ownership and release-boundary contracts for published fixtures."""

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class FixtureContract:
    path: str
    label: str
    required: tuple[str, ...]
    forbidden: tuple[str, ...]


CONTRACTS = (
    FixtureContract(
        path="material-draft/demo-landing.md",
        label="Material-inspired",
        required=(
            'data-owned-fixture="material-inspired"',
            'data-theme-status="preview"',
            "Material-inspired preview",
            "https://squidfunk.github.io/mkdocs-material/",
            "/kitchen-sink",
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
        ),
    ),
    FixtureContract(
        path="codestorage-draft/demo-landing.md",
        label="Monospace",
        required=(
            'data-owned-fixture="monospace-specimen"',
            'data-theme-status="preview"',
            "FLOWERSHOW THEME LAB",
            "MONOSPACE SPECIMEN",
            "/kitchen-sink",
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
        ),
    ),
)


def verify(contract: FixtureContract) -> list[str]:
    text = (ROOT / contract.path).read_text(encoding="utf-8")
    folded = text.casefold()
    failures = [
        f'{contract.label}: missing required content: {value}'
        for value in contract.required
        if value.casefold() not in folded
    ]
    failures.extend(
        f'{contract.label}: forbidden content remains: {value}'
        for value in contract.forbidden
        if value.casefold() in folded
    )
    return failures


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
