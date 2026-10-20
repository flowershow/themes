#!/usr/bin/env python3
"""Capture a website's brand evidence with OpenDesign's brand extraction.

    scripts/od-capture.py <url> <theme-dir> [--brand ID] [--timeout SECS]

Phase A of the theme-from-website workflow. Asks the local OpenDesign app
to extract a brand from <url> (the same deterministic pass its "extract a
brand" button runs; no agent, a few seconds) and copies the evidence into
<theme-dir>/reference/opendesign/:

  brand.json      OpenDesign's picks: 7 colour roles, display/body font,
                  layout. Treat as a hint. On the sites tried so far it took
                  light-mode roles from the dark palette, named a font that
                  isn't the one rendered, and on a light Framer site put
                  black as the background. scripts/measure-site.mjs is the
                  source of truth; brand.json is a cross-check.
  brand.html      the kit page, for a side-by-side look (opens best in the
                  OpenDesign app, where its fonts and logos resolve)
  prefetch/       the raw capture: page.html, styles.css (every stylesheet
                  the page loaded, concatenated) and material.md (colour
                  literals ranked by frequency with the selector or custom
                  property each came from; fonts by declaration count).
                  styles.css is where a site's own token names and its dark
                  palette's selectors can be read.
  fonts/manifest.json   every self-hosted webfont: family, weight, style
                  and the URL it was served from, which helps a licence
                  check. The font files themselves are not copied: they're
                  often proprietary and must not be committed.
  logos/, imagery/      logo candidates and large images. Reference only;
                  never ship a site's artwork in a theme.
  capture.json    brand id, project id, source URL, status, file list.

The whole reference/ directory is gitignored. The brand stays registered
in OpenDesign as a design system; remove it there, or with
`curl -X DELETE <daemon>/api/brands/<id>`, when done. --brand ID re-copies
an existing extraction instead of starting a new one.

The daemon listens on a port that changes per launch. OD_DAEMON_URL wins;
otherwise the script probes the OpenDesign app's listening ports for
/api/brands. The app must be running.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# copied from the project; system/ (tokens derived by algorithm from the
# picks, plus generated landing/deck/email pages) and font binaries are not
KEEP = re.compile(r"^(brand\.json|brand\.html|DESIGN\.md|guide\.md|prefetch/.*|fonts/manifest\.json|logos/.*|imagery/.*)$")


def request(base: str, path: str, method: str = "GET", body=None, timeout: float = 30):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        base + path, data=data, method=method,
        headers={"content-type": "application/json", "accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def daemon_url() -> str:
    env = os.environ.get("OD_DAEMON_URL")
    if env:
        return env.rstrip("/")
    try:
        out = subprocess.run(
            ["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"], capture_output=True, text=True, timeout=10,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        out = ""
    ports = []
    for line in out.splitlines():
        # lsof escapes the space in "Open Design" as \x20
        if line.startswith(("Open\\x20D", "Open D")):
            m = re.search(r":(\d+) \(LISTEN\)", line)
            if m:
                ports.append(m.group(1))
    for port in dict.fromkeys(ports):
        base = f"http://127.0.0.1:{port}"
        try:
            if "brands" in request(base, "/api/brands", timeout=3):
                return base
        except (urllib.error.URLError, ValueError, OSError):
            continue
    sys.exit("OpenDesign daemon not found: is the OpenDesign app running? (or set OD_DAEMON_URL)")


def wait_ready(base: str, brand_id: str, timeout: float) -> dict:
    deadline = time.time() + timeout
    while True:
        meta = request(base, f"/api/brands/{brand_id}")["meta"]
        status = meta.get("status")
        if status != "extracting":
            return meta
        if time.time() > deadline:
            sys.exit(f"brand {brand_id} still extracting after {timeout:.0f}s")
        time.sleep(3)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("url")
    ap.add_argument("theme_dir", type=Path)
    ap.add_argument("--brand", help="copy an existing OpenDesign brand instead of extracting again")
    ap.add_argument("--timeout", type=float, default=180)
    args = ap.parse_args()

    base = daemon_url()
    if args.brand:
        brand_id = args.brand
    else:
        created = request(base, "/api/brands", "POST", {"url": args.url}, timeout=120)
        brand_id = created["id"]
        print(f"OpenDesign brand {brand_id} (project {created['projectId']}) extracting…", file=sys.stderr)
    meta = wait_ready(base, brand_id, args.timeout)
    if meta.get("status") != "ready":
        sys.exit(f"extraction ended with status {meta.get('status')}: {meta.get('error') or 'no error given'}")

    project = meta["projectId"]
    listing = request(base, f"/api/projects/{project}/files")
    files = listing.get("files", listing) if isinstance(listing, dict) else listing
    dest = args.theme_dir / "reference" / "opendesign"
    if dest.exists():
        shutil.rmtree(dest)
    copied = []
    for f in files:
        if f.get("type") != "file" or not KEEP.match(f["path"]):
            continue
        target = dest / f["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f["localPath"], target)
        copied.append(f["path"])
    copied.sort()

    capture = {
        "brandId": brand_id,
        "projectId": project,
        "sourceUrl": meta.get("sourceUrl"),
        "status": meta.get("status"),
        "designSystemId": meta.get("designSystemId"),
        "daemon": base,
        "files": copied,
    }
    (dest / "capture.json").write_text(json.dumps(capture, indent=2) + "\n")
    print(f"copied {len(copied)} files to {dest}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
