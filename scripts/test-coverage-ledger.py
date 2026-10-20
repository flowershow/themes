#!/usr/bin/env python3
"""Behavior tests for the coverage ledger's sync and check rules."""

import contextlib
import io
import sys
import tempfile
import unittest
from importlib import import_module
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
ledger = import_module("coverage-ledger")

GROUPS = {
    "navigation": ["site-navbar", "site-navbar-link", "mobile-nav"],
    "listings": ["list-component", "list-component-pagination", "list-component-pagination-button"],
    "footer": ["site-footer", "site-footer-copyright"],
}
CSS = ".site-navbar { color: red; }\n.list-component-pagination-button:hover { color: blue; }\n"
NOTE = "Looked at / and /blog, light and dark: odd | chars: and ## inside are fine."


def section(group, decision, body=NOTE):
    return f"## {group}: {decision}\n\n{body}\n\n"


def complete(**overrides):
    sections = {"navigation": section("navigation", "styled"),
                "listings": section("listings", "styled"),
                "footer": section("footer", "inherits-ok")}
    sections.update(overrides)
    return "# Coverage ledger: demo\n\n" + "".join(sections.values())


def run(command, text=None, groups=GROUPS):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "coverage.md"
        if text is not None:
            path.write_text(text)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = (ledger.cmd_check("demo", path, CSS, groups) if command == "check"
                    else ledger.cmd_sync("demo", path, groups))
        return code, out.getvalue(), path.read_text() if path.exists() else ""


class Check(unittest.TestCase):
    def test_complete_ledger_passes(self):
        code, out, _ = run("check", complete())
        self.assertEqual(code, 0, out)
        self.assertIn("0 gap(s); 0 error(s)", out)

    def test_gaps_are_reported_not_failed(self):
        code, out, _ = run("check", complete(
            footer=section("footer", "gap", "Copyright is default grey."),
            listings=section("listings", "styled", NOTE + "\n\n- Gap `list-component-pagination*`: no hover"),
        ))
        self.assertEqual(code, 0, out)
        self.assertIn("GAP   footer: Copyright is default grey.", out)
        self.assertIn("GAP   listings `list-component-pagination*`: no hover", out)
        self.assertIn("2 gap(s)", out)

    def test_failures(self):
        cases = {
            "todo": (complete(footer=section("footer", "todo", "")), "decision 'todo' is not one of"),
            "styled with no selectors": (complete(footer=section("footer", "styled")),
                                         "footer: marked styled, but theme.css selects none"),
            "inherits-ok with selectors": (complete(navigation=section("navigation", "inherits-ok")),
                                           "navigation: marked inherits-ok, but theme.css selects .site-navbar"),
            "empty note": (complete(footer=section("footer", "inherits-ok", "")), "footer: empty note"),
            "missing group": (complete(footer=""), "footer: missing (core added it; run sync)"),
            "dropped group": (complete(old=section("old", "gap")), "old: not a hook group in core"),
        }
        for name, (text, message) in cases.items():
            with self.subTest(name):
                code, out, _ = run("check", text)
                self.assertEqual(code, 1, out)
                self.assertIn(message, out)


class Sync(unittest.TestCase):
    def test_sync_creates_then_appends_without_touching_decisions(self):
        _, _, text = run("sync", groups={"navigation": GROUPS["navigation"]})
        self.assertIn("## navigation: todo", text)
        decided = text.replace("## navigation: todo", "## navigation: styled\n\nChecked.")
        _, out, text = run("sync", decided)
        self.assertIn("## navigation: styled\n\nChecked.", text)
        self.assertEqual(list(ledger.parse_ledger(text)), list(GROUPS))
        self.assertIn("2 group(s) added as todo", out)


class SelectedClasses(unittest.TestCase):
    def test_ignores_comments_strings_and_urls(self):
        css = """
        /* .commented-out { } */
        .real-hook > .child:hover { background: url(img/.not-a-class.png); }
        [data-x=".in-string"] .after { content: ".nope"; }
        """
        self.assertEqual(ledger.selected_classes(css), {"real-hook", "child", "after"})


if __name__ == "__main__":
    unittest.main()
