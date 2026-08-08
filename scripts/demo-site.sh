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
SITE_NAME="${SITE_NAME:-${THEME_DIR%-draft}-theme-demo}"
THEME_URL="https://cdn.jsdelivr.net/gh/flowershow/themes@${BRANCH}/${THEME_DIR}/theme.css"

echo "== demo site: $SITE_NAME =="
echo "   theme:  $THEME_DIR"
echo "   branch: $BRANCH"
echo "   css:    $THEME_URL"

# Warn if the branch isn't pushed — jsDelivr can only see what's on GitHub.
if ! git ls-remote --exit-code --heads origin "$BRANCH" >/dev/null 2>&1; then
  echo ""
  echo "WARNING: branch '$BRANCH' is not on origin. jsDelivr cannot serve the"
  echo "theme CSS until you push it. Run: git push -u origin $BRANCH"
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

cat > "$BUILD_DIR/config.json" <<JSON
{
  "theme": "$THEME_URL"
}
JSON

echo ""
fl "$BUILD_DIR" --name "$SITE_NAME" --yes

echo ""
echo "Record the URL above in docs/features.yaml as this theme's demo_url,"
echo "then re-run scripts/verify.sh to smoke-check it."
