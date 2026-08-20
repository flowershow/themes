#!/usr/bin/env bash
# Verify the source, assembled output, and optional live deployment of the
# Flowershow themes preview site.
set -uo pipefail

ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
SITE_DIR="$ROOT/site"
SITE_URL="${SITE_URL:-}"
fail=0
build_dir=""

pass() { echo "  PASS  $1"; }
bad() { echo "  FAIL  $1"; fail=1; }

cleanup() {
  if [ -n "$build_dir" ] && [ -d "$build_dir" ]; then
    rm -rf -- "$build_dir"
  fi
}
trap cleanup EXIT

echo "== flowershow/themes: verify preview site =="

required_sources=(
  "config.json"
  "index.md"
  "themes.md"
  "contributing.md"
  "maintainers.md"
  "status.md"
)

for relative_path in "${required_sources[@]}"; do
  if [ -s "$SITE_DIR/$relative_path" ]; then
    pass "site/$relative_path exists"
  else
    bad "site/$relative_path missing or empty"
  fi
done

if [ -s "$SITE_DIR/config.json" ]; then
  if python3 -m json.tool "$SITE_DIR/config.json" >/dev/null 2>&1; then
    pass "site/config.json parses"
  else
    bad "site/config.json is not valid JSON"
  fi
fi

if [ -s "$SITE_DIR/index.md" ]; then
  for entry in "Choose a theme" "Build a theme" 'href="/themes"' 'href="/authoring"'; do
    if grep -Fq "$entry" "$SITE_DIR/index.md"; then
      pass "home includes $entry"
    else
      bad "home missing $entry"
    fi
  done
fi

if [ -s "$SITE_DIR/themes.md" ]; then
  for theme_name in Letterpress Superstack LessFlowery Leaf Material code.storage; do
    if grep -Fqi "$theme_name" "$SITE_DIR/themes.md"; then
      pass "gallery includes $theme_name"
    else
      bad "gallery missing $theme_name"
    fi
  done

  official_count=$(grep -o 'Official' "$SITE_DIR/themes.md" | wc -l | tr -d ' ')
  preview_count=$(grep -o 'Preview' "$SITE_DIR/themes.md" | wc -l | tr -d ' ')
  [ "$official_count" -ge 4 ] && pass "gallery labels four official themes" || bad "gallery needs four Official labels"
  [ "$preview_count" -ge 2 ] && pass "gallery labels two preview themes" || bad "gallery needs two Preview labels"

  for entry in 'https://letterpress.flowershow.me/' \
               'https://superstack.flowershow.me/' \
               'https://lessflowery.flowershow.me/' \
               'https://leaf.flowershow.me/' \
               'https://material-theme-demo-rufuspollock.flowershow.me' \
               'https://codestorage-theme-demo-rufuspollock.flowershow.me' \
               'https://cdn.jsdelivr.net/gh/flowershow/themes@main/material-draft/theme.css' \
               'https://cdn.jsdelivr.net/gh/flowershow/themes@main/codestorage-draft/theme.css' \
               'href="/contributing"'; do
    if grep -Fq "$entry" "$SITE_DIR/themes.md"; then
      pass "gallery includes $entry"
    else
      bad "gallery missing $entry"
    fi
  done
fi

if [ -s "$SITE_DIR/contributing.md" ] && [ -s "$SITE_DIR/maintainers.md" ]; then
  workflow_text=$(printf '%s\n' "$(cat "$SITE_DIR/contributing.md")" "$(cat "$SITE_DIR/maintainers.md")")
  for anchor in scripts/init.sh scripts/verify.sh scripts/demo-site.sh docs/features.yaml theme.css preview \
                "pull request" release jsDelivr; do
    if grep -Fqi "$anchor" <<< "$workflow_text"; then
      pass "workflow docs include $anchor"
    else
      bad "workflow docs missing $anchor"
    fi
  done
fi

if [ -s "$SITE_DIR/status.md" ]; then
  for entry in 'issues/1364' Material code.storage Preview; do
    if grep -Fq "$entry" "$SITE_DIR/status.md"; then
      pass "status includes $entry"
    else
      bad "status missing $entry"
    fi
  done
fi

if [ -x "$ROOT/scripts/site.sh" ]; then
  build_dir=$(mktemp -d)
  if "$ROOT/scripts/site.sh" build "$build_dir" >/dev/null; then
    pass "site assembles"
    required_output=(
      "config.json"
      "index.md"
      "themes.md"
      "authoring.md"
      "ai-theme-cloning.md"
      "contributing.md"
      "maintainers.md"
      "status.md"
      "assets/themes/letterpress.png"
      "assets/themes/superstack.jpg"
      "assets/themes/lessflowery.jpg"
      "assets/themes/leaf.png"
      "assets/themes/material-preview.png"
      "assets/themes/codestorage-preview.png"
    )
    for relative_path in "${required_output[@]}"; do
      if [ -s "$build_dir/$relative_path" ]; then
        pass "assembled $relative_path exists"
      else
        bad "assembled $relative_path missing or empty"
      fi
    done
  else
    bad "scripts/site.sh build failed"
  fi
else
  bad "scripts/site.sh missing or not executable"
fi

if [ -n "$SITE_URL" ]; then
  base_url="${SITE_URL%/}"
  for route in / /themes /authoring /ai-theme-cloning /contributing /maintainers; do
    status=$(curl -sL -o /dev/null -w '%{http_code}' --max-time 20 "$base_url$route" || echo 000)
    if [ "$status" = "200" ]; then
      pass "live $route responds 200"
    else
      bad "live $route failed (HTTP $status)"
    fi
  done
fi

if [ "$fail" -ne 0 ]; then
  echo "verify-site.sh: FAIL"
  exit 1
fi

echo "verify-site.sh: PASS"
