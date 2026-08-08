#!/usr/bin/env bash
# Build and publish a demo site for a theme.
#
#   scripts/demo-site.sh <theme-dir> [--landing <file.html>] [--name <site-name>]
#
# Assembles a site from:
#   - _demo-content/          the shared kitchen-sink + blog content, so every
#                             theme is compared on IDENTICAL content
#   - <theme-dir>/theme.css   applied via a jsDelivr URL pinned to the current
#                             git branch (no release/tag needed for drafts)
#   - --landing <file>        optional raw .html landing page, published as
#                             index.html. Used for the stage-1 Tailwind repros,
#                             which are plain HTML and don't need the theme.
#
# then publishes it with `fl` and prints the URL.
#
# Why this exists: config.json's `theme` field is the only theme switch —
# there's no theme switcher in the dashboard — so a demo site per theme is
# the practical way to preview one.
set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

THEME_DIR=""
LANDING=""
SITE_NAME=""

while [ $# -gt 0 ]; do
  case "$1" in
    --landing) LANDING="$2"; shift 2 ;;
    --name)    SITE_NAME="$2"; shift 2 ;;
    -*) echo "unknown flag: $1" >&2; exit 2 ;;
    *) THEME_DIR="$1"; shift ;;
  esac
done

if [ -z "$THEME_DIR" ]; then
  echo "usage: scripts/demo-site.sh <theme-dir> [--landing <file.html>] [--name <site-name>]" >&2
  exit 2
fi

if [ ! -f "$REPO_ROOT/$THEME_DIR/theme.css" ]; then
  echo "no such theme: $THEME_DIR/theme.css" >&2
  exit 1
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
SHA="$(git rev-parse HEAD)"
SITE_NAME="${SITE_NAME:-${THEME_DIR%-draft}-theme-demo}"

# Pin to the COMMIT SHA, not the branch name.
#
# Branch-pinned jsDelivr URLs (@draft/new-themes/...) are mutable, and their
# edge nodes update unevenly: after pushing + purging, one edge served the new
# CSS while another still served a stale copy — even with cache:'reload' and a
# cache-busting query string. That silently makes a theme look unchanged and
# wastes a lot of time chasing a non-existent CSS bug.
#
# A SHA-pinned URL is immutable, so every commit produces a fresh URL that
# cannot be stale. Cost: the site must be republished to pick up new CSS,
# which is exactly what this script does.
THEME_URL="https://cdn.jsdelivr.net/gh/flowershow/themes@${SHA}/${THEME_DIR}/theme.css"

echo "== demo site: $SITE_NAME =="
echo "   theme:  $THEME_DIR"
echo "   branch: $BRANCH"
echo "   commit: ${SHA:0:8}"
echo "   css:    $THEME_URL"

# jsDelivr can only serve commits that are on GitHub.
if ! git branch -r --contains "$SHA" 2>/dev/null | grep -q .; then
  echo ""
  echo "ERROR: commit ${SHA:0:8} is not on any remote branch. jsDelivr cannot"
  echo "serve it. Push first:  git push -u origin $BRANCH"
  exit 1
fi

if [ -n "$(git status --porcelain -- "$THEME_DIR")" ]; then
  echo ""
  echo "WARNING: $THEME_DIR has uncommitted changes. The demo will be built"
  echo "from commit ${SHA:0:8}, NOT your working tree. Commit and push first."
fi

BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "$BUILD_DIR"' EXIT

cp -R "$REPO_ROOT/_demo-content/." "$BUILD_DIR/"

if [ -n "$LANDING" ]; then
  if [ ! -f "$REPO_ROOT/$LANDING" ]; then
    echo "no such landing file: $LANDING" >&2
    exit 1
  fi
  # raw .html is published as-is by Flowershow, so the stage-1 repro renders
  # exactly as authored, untouched by the markdown pipeline or the theme
  rm -f "$BUILD_DIR/index.md"
  cp "$REPO_ROOT/$LANDING" "$BUILD_DIR/index.html"
  echo "   landing: $LANDING -> index.html (raw HTML)"
fi

# Merge the theme URL into the shared base config rather than writing a bare
# config. The base config matters: Flowershow only renders the navbar if a nav
# title, nav links, CTA, social links, or search is configured — so without it
# there is no navbar on the demo at all, and a theme's navbar styling is
# invisible. Same reason the sidebar and mode switch are enabled there.
rm -f "$BUILD_DIR/config.base.json"
python3 - "$REPO_ROOT/_demo-content/config.base.json" "$THEME_URL" "$BUILD_DIR/config.json" <<'PYEOF'
import json, sys
base_path, theme_url, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
with open(base_path) as f:
    cfg = json.load(f)
theme = cfg.get("theme")
if isinstance(theme, dict):
    theme["theme"] = theme_url
else:
    cfg["theme"] = theme_url
with open(out_path, "w") as f:
    json.dump(cfg, f, indent=2)
PYEOF

echo ""
fl "$BUILD_DIR" --name "$SITE_NAME" --yes

echo ""
echo "Record the URL above in docs/features.yaml as this theme's demo_url,"
echo "then re-run scripts/verify.sh to smoke-check it."
