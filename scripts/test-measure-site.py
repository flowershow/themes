#!/usr/bin/env python3
"""Behavior tests for measure-site.mjs against local fixture pages.

Needs node and the Playwright bundled with gstack (see measure-site.mjs).
The Google Fonts lookup goes online; the tests don't depend on its answer.
"""

import json
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "measure-site.mjs"
PROSE = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor. " * 3

# A light site with a media-query dark mode, plus the traps met on real
# sites: a dark feature card before the first plain paragraph (a Framer
# blog), a fixed cookie banner, and link underlines drawn as borders.
MEDIA = f"""<!doctype html><html><head><style>
:root {{ --bg: #fafaf5; --fg: #222222; --link: #0055aa; --muted: #777777; --line: #e0e0e0; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg: #111118; --fg: #dddddd; --link: #66aaff; --muted: #999999; --line: #333333; }}
}}
body {{ background: var(--bg); color: var(--fg); font-family: Georgia, serif; margin: 0; }}
main {{ max-width: 700px; margin: 0 auto; }}
.card {{ background: #333333; color: #ffffff; padding: 20px; }}
.meta {{ color: var(--muted); }}
a {{ color: var(--link); border-bottom: 1px solid #ff0000; text-decoration: none; }}
section {{ border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }}
button {{ background: #cc0033; color: #ffffff; border-radius: 6px; border: 0; }}
#cookie-banner {{ position: fixed; inset: 0; background: #000000; color: #ffffff; }}
</style></head><body>
<header><nav><a href="#">Home</a></nav></header>
<main>
  <div class="card"><p>{PROSE}</p></div>
  <section><p>{PROSE} <a href="#x">a link in prose</a></p></section>
  <section><p class="meta">{PROSE}</p><p class="meta">{PROSE}</p></section>
  <button>Subscribe</button>
</main>
<div id="cookie-banner">{PROSE * 3}</div>
</body></html>"""

TOGGLE = f"""<!doctype html><html><head><style>
body {{ background: #ffffff; color: #111111; }}
html.dark body {{ background: #0d1117; color: #e6edf3; }}
</style></head><body><main><p>{PROSE}</p></main></body></html>"""

DARK_ONLY = f"""<!doctype html><html><head><style>
body {{ background: #0b0b0b; color: #f0f0f0; }}
</style></head><body><main><p>{PROSE}</p></main></body></html>"""

LIGHT_ONLY = f"""<!doctype html><html><head><style>
body {{ background: #ffffff; color: #333333; }}
</style></head><body><main><p>{PROSE}</p></main></body></html>"""


def measure(html: str, shots: Path | None = None) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "index.html"
        page.write_text(html)
        out = Path(tmp) / "tokens.json"
        extra = ["--shots", str(shots)] if shots else []
        result = subprocess.run(
            ["node", str(SCRIPT), page.as_uri(), "--out", str(out), *extra],
            capture_output=True, text=True, timeout=180,
        )
        if result.returncode != 0:
            raise AssertionError(f"measure-site failed:\n{result.stderr}")
        return json.loads(out.read_text())


def first_pixel(png: Path) -> str:
    """Hex colour of a PNG's top-left pixel. Every PNG row filter leaves the
    first pixel of the first row unchanged, so no unfiltering is needed."""
    data = png.read_bytes()
    pos, idat = 8, b""
    while pos < len(data):
        length = int.from_bytes(data[pos:pos + 4], "big")
        kind = data[pos + 4:pos + 8]
        if kind == b"IDAT":
            idat += data[pos + 8:pos + 8 + length]
        pos += 12 + length
    raw = zlib.decompress(idat)
    return "#" + raw[1:4].hex()


def value(mode: dict, role: str):
    r = mode["roles"][role]
    return r and r["value"]


class MediaQueryDarkMode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tokens = measure(MEDIA)

    def test_detects_media_dark_mode(self):
        self.assertEqual(self.tokens["dark"], "media")

    def test_light_roles_come_from_the_light_palette(self):
        light = self.tokens["modes"]["light"]
        self.assertEqual(value(light, "background"), "#fafaf5")
        self.assertEqual(value(light, "link"), "#0055aa")

    def test_dark_roles_come_from_the_dark_palette(self):
        dark = self.tokens["modes"]["dark"]
        self.assertEqual(value(dark, "background"), "#111118")
        self.assertEqual(value(dark, "foreground"), "#dddddd")
        self.assertEqual(value(dark, "link"), "#66aaff")

    def test_foreground_ignores_text_in_a_dark_card(self):
        self.assertEqual(value(self.tokens["modes"]["light"], "foreground"), "#222222")

    def test_cookie_banner_is_ignored(self):
        light = self.tokens["modes"]["light"]
        self.assertNotIn("#000000", [c["color"] for c in light["candidates"]["background"]])

    def test_muted_is_the_quieter_text_colour(self):
        self.assertEqual(value(self.tokens["modes"]["light"], "muted"), "#777777")

    def test_border_skips_link_underlines(self):
        self.assertEqual(value(self.tokens["modes"]["light"], "border"), "#e0e0e0")

    def test_accent_prefers_a_chromatic_button(self):
        light = self.tokens["modes"]["light"]
        self.assertEqual(value(light, "accent"), "#cc0033")
        self.assertEqual(light["shape"]["radius"]["button"], "6px")

    def test_fonts_report_the_rendered_family(self):
        body = self.tokens["modes"]["light"]["type"]["body"]
        self.assertTrue(body["family"].startswith("Georgia"))
        self.assertTrue(body["rendered"])
        families = [f["family"] for f in self.tokens["fonts"]]
        self.assertIn(body["rendered"], families)
        self.assertFalse(next(f for f in self.tokens["fonts"] if f["family"] == body["rendered"])["webfont"])


class OtherDarkModes(unittest.TestCase):
    def test_class_toggle(self):
        tokens = measure(TOGGLE)
        self.assertEqual(tokens["dark"], "toggle:.dark")
        self.assertEqual(value(tokens["modes"]["dark"], "background"), "#0d1117")
        self.assertEqual(value(tokens["modes"]["light"], "background"), "#ffffff")

    def test_dark_only_site_has_no_light_palette(self):
        tokens = measure(DARK_ONLY)
        self.assertEqual(tokens["dark"], "dark-only")
        self.assertIsNone(tokens["modes"]["light"])
        self.assertEqual(value(tokens["modes"]["dark"], "background"), "#0b0b0b")

    def test_light_only_site_has_no_dark_palette(self):
        tokens = measure(LIGHT_ONLY)
        self.assertEqual(tokens["dark"], "none")
        self.assertIsNone(tokens["modes"]["dark"])


class ReferenceShots(unittest.TestCase):
    def shots(self, html: str) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            measure(html, Path(tmp))
            return {p.name.split("--")[1]: first_pixel(p) for p in Path(tmp).glob("*.png")}

    def test_toggle_site_is_shot_in_both_modes(self):
        shots = self.shots(TOGGLE)
        self.assertEqual(shots, {
            "desktop-light.png": "#ffffff", "desktop-dark.png": "#0d1117",
            "mobile-light.png": "#ffffff", "mobile-dark.png": "#0d1117",
        })

    def test_light_only_site_has_no_dark_shots(self):
        self.assertEqual(sorted(self.shots(LIGHT_ONLY)), ["desktop-light.png", "mobile-light.png"])


if __name__ == "__main__":
    unittest.main()
