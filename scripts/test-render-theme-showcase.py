#!/usr/bin/env python3
"""Behavior tests for the theme showcase renderer."""

import json
import http.server
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest


ROOT = Path(__file__).resolve().parents[1]
RENDERER = ROOT / "scripts/render-theme-showcase.py"
FIXTURE_VERIFIER = ROOT / "scripts/verify-landing-fixtures.py"
ROUTE_VERIFIER = ROOT / "scripts/verify-demo-routes.py"
FEATURE_FIELD_READER = ROOT / "scripts/read-feature-field.py"

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
    def test_monospace_owns_its_showcase_template(self):
        template_path = ROOT / "codestorage-draft/demo-showcase.template.md"
        self.assertTrue(template_path.is_file())
        template = template_path.read_text(encoding="utf-8")

        self.assertNotIn("IBM Plex Mono", template)
        self.assertNotIn("Monospace theme specimen", template)
        self.assertIn('aria-label="A small {{name}} theme specimen"', template)

    def test_monospace_template_keeps_nested_html_in_one_markdown_block(self):
        template_path = ROOT / "codestorage-draft/demo-showcase.template.md"
        self.assertTrue(template_path.is_file())
        template = template_path.read_text(encoding="utf-8")
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

    def test_uses_context_specific_yaml_and_html_escaping(self):
        metadata = dict(VALID_METADATA)
        metadata["name"] = 'A & B \\ "quoted" {theme}'
        metadata["description"] = 'Plain & portable \\ "copy" {today}'
        template = """---
title: "Flowershow — {{yaml:name}} theme"
description: "{{yaml:description}}"
---
<h1>{{name}}</h1>
<p>{{description}}</p>
"""

        result, page = run_renderer(metadata, template=template)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('title: "Flowershow — A & B \\\\ \\"quoted\\" {theme} theme"', page)
        self.assertIn('description: "Plain & portable \\\\ \\"copy\\" {today}"', page)
        self.assertIn("<h1>A &amp; B \\ &quot;quoted&quot; {theme}</h1>", page)
        self.assertIn("<p>Plain &amp; portable \\ &quot;copy&quot; {today}</p>", page)

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
            "source-prefix-confusion": {
                "sourceUrl": "https://github.com/flowershow/themes-malicious"
            },
            "source-dot-segments": {
                "sourceUrl": "https://github.com/flowershow/themes/../../evil"
            },
            "source-encoded-dot-segments": {
                "sourceUrl": "https://github.com/flowershow/themes/%2e%2e/evil"
            },
            "source-backslash-dot-segments": {
                "sourceUrl": "https://github.com/flowershow/themes/foo\\..\\..\\evil"
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
            self.assertIn("ts-document", home)
            self.assertNotIn("ts-card-grid", home)
            self.assertNotIn("ts-benefits", home)
            self.assertNotIn("ts-steps", home)
            self.assertNotIn("ts-final-cta", home)
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

    def test_fixture_verifier_discovers_new_showcases_and_rejects_remote_css_urls(self):
        with tempfile.TemporaryDirectory(prefix="showcase-test-", dir=ROOT) as temporary:
            theme_dir = Path(temporary)
            metadata = dict(
                VALID_METADATA,
                name="Test Theme",
                slug="test-theme",
                wrapperClass="test-landing",
            )
            (theme_dir / "demo-showcase.json").write_text(
                json.dumps(metadata), encoding="utf-8"
            )
            (theme_dir / "demo-showcase.template.md").write_text(
                (ROOT / "codestorage-draft/demo-showcase.template.md").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            (theme_dir / "demo-landing.css").write_text(
                '.test-landing { background-image: url("https://example.com/art.png"); }\n',
                encoding="utf-8",
            )

            result = subprocess.run(
                ["python3", str(FIXTURE_VERIFIER)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("Test Theme", result.stdout)
            self.assertIn("external CSS URL", result.stdout)

            nested_cases = {
                "multiple media blocks": """.test-landing { color: black; }
@media (max-width: 900px) { .test-landing { color: gray; } }
@media (max-width: 600px) { body { color: red; } }
""",
                "supports block": """.test-landing { color: black; }
@supports (display: grid) { body { display: grid; } }
""",
            }
            for label, css in nested_cases.items():
                with self.subTest(label=label):
                    (theme_dir / "demo-landing.css").write_text(css, encoding="utf-8")
                    result = subprocess.run(
                        ["python3", str(FIXTURE_VERIFIER)],
                        cwd=ROOT,
                        capture_output=True,
                        text=True,
                        check=False,
                    )

                    self.assertEqual(result.returncode, 1)
                    self.assertIn(
                        "showcase CSS selector is not scoped", result.stdout
                    )
                    self.assertIn("body", result.stdout)

            (theme_dir / "demo-landing.css").write_text(
                """.test-landing { color: black; }
@supports (display: grid) {
  .test-landing :is(.primary, .secondary) { display: grid; }
}
@-webkit-keyframes pulse { from { opacity: 0; } to { opacity: 1; } }
""",
                encoding="utf-8",
            )
            result = subprocess.run(
                ["python3", str(FIXTURE_VERIFIER)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_route_verifier_checks_every_standard_and_compatibility_route(self):
        responses = {
            "/": 'data-theme-showcase="monospace"',
            "/docs/kitchen-sink": "Kitchen Sink",
            "/blog": "Blog",
            "/blog/first-post": "The First Post",
            "/landing": 'data-theme-showcase="monospace"',
        }

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                body = responses.get(self.path.split("?", 1)[0])
                self.send_response(200 if body is not None else 404)
                self.end_headers()
                self.wfile.write((body or "missing").encode())

            def log_message(self, *_args):
                pass

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{server.server_port}"
        try:
            result = subprocess.run(
                [
                    "python3",
                    str(ROUTE_VERIFIER),
                    base_url,
                    'data-theme-showcase="monospace"',
                    f"{base_url}/landing",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            del responses["/blog/first-post"]
            result = subprocess.run(
                [
                    "python3",
                    str(ROUTE_VERIFIER),
                    base_url,
                    'data-theme-showcase="monospace"',
                    f"{base_url}/landing",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("/blog/first-post", result.stdout)
        finally:
            server.shutdown()
            server.server_close()

    def test_feature_field_reader_does_not_bleed_into_the_next_theme(self):
        ledger = """themes:
  - id: first
    kind: theme
    demo_url: https://first.example
  - id: second
    kind: theme
    landing_compatibility_url: https://second.example/landing
"""
        with tempfile.TemporaryDirectory() as temporary:
            ledger_path = Path(temporary) / "features.yaml"
            ledger_path.write_text(ledger, encoding="utf-8")
            result = subprocess.run(
                [
                    "python3",
                    str(FEATURE_FIELD_READER),
                    str(ledger_path),
                    "first",
                    "landing_compatibility_url",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
