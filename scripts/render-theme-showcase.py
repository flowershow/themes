#!/usr/bin/env python3
"""Render a shared Flowershow theme-showcase template with validated metadata."""

from html import escape
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse


REQUIRED_FIELDS = {
    "schemaVersion",
    "name",
    "slug",
    "status",
    "headline",
    "description",
    "wrapperClass",
    "sourceUrl",
}
IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]*$")
PLACEHOLDER = re.compile(r"{{\s*([^{}]+?)\s*}}")


class ShowcaseMetadataError(ValueError):
    """Raised when showcase metadata or its template is invalid."""


def load_metadata(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ShowcaseMetadataError(f"cannot read {path}: {error}") from error
    if not isinstance(data, dict):
        raise ShowcaseMetadataError("top-level value must be a JSON object")
    return data


def validate_metadata(data: dict[str, object]) -> dict[str, str]:
    supplied = set(data)
    missing = sorted(REQUIRED_FIELDS - supplied)
    unknown = sorted(supplied - REQUIRED_FIELDS)
    if missing:
        raise ShowcaseMetadataError(f"missing fields: {', '.join(missing)}")
    if unknown:
        raise ShowcaseMetadataError(f"unknown fields: {', '.join(unknown)}")
    if data["schemaVersion"] != 1 or isinstance(data["schemaVersion"], bool):
        raise ShowcaseMetadataError("schemaVersion must be integer 1")

    string_fields = REQUIRED_FIELDS - {"schemaVersion"}
    for field in sorted(string_fields):
        if not isinstance(data[field], str) or not data[field].strip():
            raise ShowcaseMetadataError(f"{field} must be a nonempty string")
        if "\n" in data[field] or "\r" in data[field]:
            raise ShowcaseMetadataError(f"{field} must be a single line")

    if data["status"] not in {"preview", "official"}:
        raise ShowcaseMetadataError("status must be preview or official")
    for field in ("slug", "wrapperClass"):
        if not IDENTIFIER.fullmatch(data[field]):
            raise ShowcaseMetadataError(
                f"{field} must match ^[a-z][a-z0-9-]*$"
            )

    source = urlparse(data["sourceUrl"])
    if (
        source.scheme != "https"
        or source.netloc != "github.com"
        or not source.path.startswith("/flowershow/themes")
    ):
        raise ShowcaseMetadataError(
            "sourceUrl must be an HTTPS URL under github.com/flowershow/themes"
        )

    return {
        field: escape(data[field], quote=True)
        for field in string_fields
    }


def render(template: str, metadata: dict[str, str]) -> str:
    rendered = template
    for field, value in metadata.items():
        rendered = rendered.replace("{{" + field + "}}", value)
    unresolved = PLACEHOLDER.search(rendered)
    if unresolved:
        raise ShowcaseMetadataError(
            f"unresolved template field: {unresolved.group(1)}"
        )
    return rendered


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(
            "usage: render-theme-showcase.py TEMPLATE METADATA OUTPUT",
            file=sys.stderr,
        )
        return 2
    template_path, metadata_path, output_path = map(Path, argv[1:])
    try:
        template = template_path.read_text(encoding="utf-8")
        metadata = validate_metadata(load_metadata(metadata_path))
        rendered = render(template, metadata)
        output_path.write_text(rendered, encoding="utf-8")
    except (OSError, ShowcaseMetadataError) as error:
        print(f"showcase metadata: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
