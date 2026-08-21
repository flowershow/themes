#!/usr/bin/env python3
"""Behavior tests for the theme showcase renderer."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "scripts/render-theme-showcase.py"

VALID_METADATA = {
    "schemaVersion": 1,
    "name": "Monospace",
    "slug": "monospace",
    "status": "preview",
    "headline": "A sharper home for your Markdown",
    "description": (
        "A compact monospace theme for docs, notes, blogs, and technical publishing."
    ),
    "wrapperClass": "cs-landing",
    "sourceUrl": "https://github.com/flowershow/themes/tree/main/codestorage-draft",
}

VALID_TEMPLATE = """---
title: {{name}}
---
<div class="{{wrapperClass}}" data-theme-showcase="{{slug}}" data-theme-status="{{status}}">
<h1>{{headline}}</h1>
<p>{{description}}</p>
<a href="{{sourceUrl}}">Source</a>
</div>
"""


def run_renderer(metadata, template=VALID_TEMPLATE):
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        template_path = directory / "template.md"
        metadata_path = directory / "metadata.json"
        output_path = directory / "index.md"
        template_path.write_text(template, encoding="utf-8")
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
        result = subprocess.run(
            [
                "python3",
                str(RENDERER),
                str(template_path),
                str(metadata_path),
                str(output_path),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        output = output_path.read_text(encoding="utf-8") if output_path.exists() else ""
        return result, output


class RenderShowcaseTests(unittest.TestCase):
    def test_repository_template_keeps_nested_html_in_one_markdown_block(self):
        template = (
            ROOT / "_demo-content/theme-showcase.template.md"
        ).read_text(encoding="utf-8")
        html_block = template[template.index('<div class="{{wrapperClass}}') :]

        self.assertNotIn("\n\n", html_block)

    def test_renders_valid_metadata_and_escapes_text(self):
        metadata = dict(VALID_METADATA)
        metadata["headline"] = "Write <share> & publish"

        result, page = run_renderer(metadata)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('data-theme-showcase="monospace"', page)
        self.assertIn('data-theme-status="preview"', page)
        self.assertIn("<h1>Write &lt;share&gt; &amp; publish</h1>", page)
        self.assertEqual(page.lower().count("<h1"), 1)
        self.assertNotIn("{{", page)

    def test_rejects_missing_and_unknown_fields(self):
        missing = dict(VALID_METADATA)
        missing.pop("name")
        unknown = dict(VALID_METADATA, invented="value")

        for label, metadata in (("missing", missing), ("unknown", unknown)):
            with self.subTest(label=label):
                result, page = run_renderer(metadata)
                self.assertEqual(result.returncode, 2)
                self.assertIn("showcase metadata:", result.stderr)
                self.assertEqual(page, "")

    def test_rejects_invalid_schema_status_identifiers_and_source(self):
        mutations = {
            "schema": {"schemaVersion": 2},
            "status": {"status": "beta"},
            "slug": {"slug": "Mono Space"},
            "wrapper": {"wrapperClass": "CS_Landing"},
            "source-host": {"sourceUrl": "https://example.com/theme"},
            "source-scheme": {
                "sourceUrl": "http://github.com/flowershow/themes/tree/main/theme"
            },
        }

        for label, updates in mutations.items():
            with self.subTest(label=label):
                result, page = run_renderer(dict(VALID_METADATA, **updates))
                self.assertEqual(result.returncode, 2)
                self.assertIn("showcase metadata:", result.stderr)
                self.assertEqual(page, "")

    def test_rejects_unresolved_template_fields(self):
        result, page = run_renderer(
            VALID_METADATA,
            template=VALID_TEMPLATE + "\n<p>{{notDeclared}}</p>\n",
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("unresolved template field", result.stderr)
        self.assertEqual(page, "")

    def test_build_only_assembles_standard_showcase_and_real_nav(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "site"
            output.mkdir()

            result = subprocess.run(
                [
                    "bash",
                    "scripts/demo-site.sh",
                    "codestorage-draft",
                    "--build-only",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            home = (output / "index.md").read_text(encoding="utf-8")
            compatibility = (output / "landing.md").read_text(encoding="utf-8")
            self.assertEqual(home, compatibility)
            self.assertIn('data-theme-showcase="monospace"', home)
            self.assertTrue((output / "custom.css").is_file())
            self.assertTrue((output / "docs/kitchen-sink.md").is_file())
            self.assertTrue((output / "blog/first-post.md").is_file())

            config = json.loads((output / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["nav"]["title"], "Flowershow")
            self.assertEqual(
                config["nav"]["cta"],
                {
                    "href": "https://flowershow.app/publish",
                    "label": "Publish with Flowershow",
                },
            )
            self.assertEqual(
                config["nav"]["links"],
                [
                    {"href": "/", "name": "Home"},
                    {"href": "/docs/kitchen-sink", "name": "Kitchen Sink"},
                    {"href": "/blog", "name": "Blog"},
                    {
                        "href": VALID_METADATA["sourceUrl"],
                        "name": "Theme Source",
                    },
                ],
            )


if __name__ == "__main__":
    unittest.main()
