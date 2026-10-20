#!/usr/bin/env python3
"""Behavior tests for the coverage ledger: its YAML subset and its check rules."""

import contextlib
import io
import json
import shutil
import subprocess
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


def entry(decision, note="looked at / and /blog, light and dark", gaps=None):
    return {"decision": decision, "note": note, "gaps": gaps or {}}


class YamlSubset(unittest.TestCase):
    def roundtrip(self, groups):
        text = ledger.render_ledger("demo", groups, list(groups))
        return text, ledger.parse_ledger(text)

    def test_roundtrip_keeps_awkward_values(self):
        groups = {
            "navigation": entry("styled", 'Navbar: border #ccc, "quoted" — fine'),
            "listings": entry("gap", "plain note", {"*-pagination*": "default grey: needs accent"}),
            "footer": entry("todo", ""),
        }
        _, parsed = self.roundtrip(groups)
        self.assertEqual(parsed["theme"], "demo")
        self.assertEqual(parsed["groups"], groups)

    @unittest.skipUnless(shutil.which("ruby"), "ruby not installed")
    def test_real_yaml_parser_agrees(self):
        groups = {
            "navigation": entry("styled", 'Navbar: border #ccc, "quoted" — fine'),
            "listings": entry("gap", "- starts with a dash", {"*-pagination*": "grey: wrong"}),
            "footer": entry("inherits-ok", "plain words, a comma, 50% done"),
        }
        text, parsed = self.roundtrip(groups)
        ruby = subprocess.run(
            ["ruby", "-ryaml", "-rjson", "-e", "puts JSON.generate(YAML.safe_load(STDIN.read))"],
            input=text, capture_output=True, text=True, check=True,
        )
        theirs = json.loads(ruby.stdout)
        for group in theirs["groups"].values():
            group.setdefault("gaps", {})
        self.assertEqual(theirs, parsed)

    def test_hand_edits_parse(self):
        text = (
            "# comment\n"
            "theme: demo\n"
            "groups:\n"
            "  navigation:\n"
            "    decision: styled   # trailing comment\n"
            '    note: "Checked: all routes"\n'
            "    gaps:\n"
            "      mobile-nav: drawer keeps the default shadow\n"
        )
        parsed = ledger.parse_ledger(text)["groups"]["navigation"]
        self.assertEqual(parsed["decision"], "styled")
        self.assertEqual(parsed["note"], "Checked: all routes")
        self.assertEqual(parsed["gaps"], {"mobile-nav": "drawer keeps the default shadow"})

    def test_rejects_what_yaml_would_read_differently(self):
        for bad in (
            "theme: demo\ngroups:\n  footer:\n    note: Checked: all routes\n",  # unquoted ': '
            "theme: demo\ngroups:\n  footer:\n    note: [a, b]\n",  # a flow list
            "theme: demo\ngroups:\n  footer:\n   decision: styled\n",  # 3-space indent
            "theme: demo\ngroups:\n  footer:\n    colour: red\n",  # unknown key
            "theme: demo\ngroups:\n  footer:\n  footer:\n",  # duplicate group
        ):
            with self.subTest(bad=bad), self.assertRaises(ledger.LedgerError):
                ledger.parse_ledger(bad)


class Check(unittest.TestCase):
    def run_check(self, groups_in_ledger, leaks=None, theme="demo"):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coverage.yaml"
            path.write_text(ledger.render_ledger(theme, groups_in_ledger, list(groups_in_ledger)))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = ledger.cmd_check("demo", path, CSS, GROUPS, leaks)
        return code, out.getvalue()

    def complete(self, **overrides):
        groups = {
            "navigation": entry("styled"),
            "listings": entry("styled"),
            "footer": entry("inherits-ok"),
        }
        groups.update(overrides)
        return groups

    def test_complete_ledger_passes(self):
        code, out = self.run_check(self.complete())
        self.assertEqual(code, 0, out)
        self.assertIn("3/3 groups decided; 0 gap(s); 0 error(s)", out)

    def test_gaps_are_reported_not_failed(self):
        code, out = self.run_check(self.complete(
            footer=entry("gap", "copyright is default grey"),
            listings=entry("styled", gaps={"list-component-pagination*": "no hover state"}),
        ))
        self.assertEqual(code, 0, out)
        self.assertIn("GAP   footer: copyright is default grey", out)
        self.assertIn("GAP   listings .list-component-pagination*: no hover state", out)
        self.assertIn("2 gap(s)", out)

    def test_failures(self):
        cases = {
            "todo": (self.complete(footer=entry("todo", "")), "footer: no decision yet"),
            "unknown decision": (self.complete(footer=entry("fine")), "decision 'fine' is not one of"),
            "styled with no selectors": (self.complete(footer=entry("styled")),
                                         "footer: marked styled, but theme.css selects none"),
            "inherits-ok with selectors": (self.complete(navigation=entry("inherits-ok")),
                                           "navigation: marked inherits-ok, but theme.css selects .site-navbar"),
            "empty note": (self.complete(footer=entry("inherits-ok", "")), "footer: empty note"),
            "stray gap pattern": (self.complete(footer=entry("gap", "x", {"site-navbar*": "y"})),
                                  "gap pattern 'site-navbar*' matches none"),
            "missing group": ({k: v for k, v in self.complete().items() if k != "footer"},
                              "footer: missing (core added it; run sync)"),
            "dropped group": ({**self.complete(), "old": entry("gap")}, "old: not a hook group in core"),
        }
        for name, (groups, message) in cases.items():
            with self.subTest(name):
                code, out = self.run_check(groups)
                self.assertEqual(code, 1, out)
                self.assertIn(message, out)

    def test_wrong_theme_fails(self):
        code, out = self.run_check(self.complete(), theme="other")
        self.assertEqual(code, 1)
        self.assertIn("theme is 'other', expected 'demo'", out)

    def test_leaks_warn_on_inherits_ok_only(self):
        leaks = {"by_group": {"footer": {"elements": 4}, "navigation": {"elements": 2}}}
        code, out = self.run_check(self.complete(), leaks=leaks)
        self.assertEqual(code, 0, out)
        self.assertIn("WARN  footer: inherits-ok, but 4 element(s) use off-palette colours", out)
        self.assertNotIn("WARN  navigation", out)


class Sync(unittest.TestCase):
    def test_sync_creates_then_adds_without_touching_decisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coverage.yaml"
            with contextlib.redirect_stdout(io.StringIO()):
                ledger.cmd_sync("demo", path, {"navigation": GROUPS["navigation"]})
            text = path.read_text().replace("decision: todo", "decision: styled") \
                                   .replace('note: ""', "note: checked")
            path.write_text(text)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                ledger.cmd_sync("demo", path, GROUPS)
            groups = ledger.parse_ledger(path.read_text())["groups"]
        self.assertEqual(groups["navigation"], entry("styled", "checked"))
        self.assertEqual(groups["footer"]["decision"], "todo")
        self.assertEqual(list(groups), list(GROUPS))
        self.assertIn("2 group(s) added as todo", out.getvalue())


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
