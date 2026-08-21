#!/usr/bin/env bash
# Verify the source, assembled output, and optional live deployment of the
# Flowershow themes preview site.
set -uo pipefail

ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
SITE_DIR="$ROOT/site"
SITE_URL="${SITE_URL:-}"
fail=0
build_dir=""
live_body=""

pass() { echo "  PASS  $1"; }
bad() { echo "  FAIL  $1"; fail=1; }

cleanup() {
  if [ -n "$build_dir" ] && [ -d "$build_dir" ]; then
    rm -rf -- "$build_dir"
  fi
  if [ -n "$live_body" ] && [ -f "$live_body" ]; then
    rm -f -- "$live_body"
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

  if grep -Fq '"href": "/readiness"' "$SITE_DIR/config.json"; then
    pass "site navigation links preview readiness"
  else
    bad "site navigation missing preview readiness"
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

  card_contracts=(
    "letterpress|official|letterpress|https://letterpress.flowershow.me/|/assets/themes/letterpress.png"
    "superstack|official|superstack|https://superstack.flowershow.me/|/assets/themes/superstack.jpg"
    "lessflowery|official|lessflowery|https://lessflowery.flowershow.me/|/assets/themes/lessflowery.jpg"
    "leaf|official|leaf|https://leaf.flowershow.me/|/assets/themes/leaf.png"
    "material|preview|https://cdn.jsdelivr.net/gh/flowershow/themes@main/material-draft/theme.css|https://material-theme-demo-rufuspollock.flowershow.me|/assets/themes/material-preview.png"
    "codestorage|preview|https://cdn.jsdelivr.net/gh/flowershow/themes@main/codestorage-draft/theme.css|https://codestorage-theme-demo-rufuspollock.flowershow.me|/assets/themes/codestorage-preview.png"
  )
  for contract in "${card_contracts[@]}"; do
    IFS='|' read -r card_id card_status card_config card_demo card_image <<< "$contract"
    card_line=$(grep -F "data-theme-card=\"$card_id\"" "$SITE_DIR/themes.md" || true)
    if [ -z "$card_line" ]; then
      bad "gallery missing structured $card_id card"
      continue
    fi
    for attribute in \
      "data-theme-status=\"$card_status\"" \
      "data-theme-config=\"$card_config\"" \
      "data-theme-demo=\"$card_demo\"" \
      "data-theme-image=\"$card_image\""; do
      if grep -Fq "$attribute" <<< "$card_line"; then
        pass "$card_id card includes $attribute"
      else
        bad "$card_id card missing $attribute"
      fi
    done
  done

  if grep -Fq '{`{' "$SITE_DIR/themes.md"; then
    bad "gallery contains a literal MDX wrapper around JSON"
  else
    pass "gallery JSON has no literal MDX wrapper"
  fi

  for entry in 'https://letterpress.flowershow.me/' \
               'https://superstack.flowershow.me/' \
               'https://lessflowery.flowershow.me/' \
               'https://leaf.flowershow.me/' \
               'https://material-theme-demo-rufuspollock.flowershow.me' \
               'https://codestorage-theme-demo-rufuspollock.flowershow.me' \
               'https://cdn.jsdelivr.net/gh/flowershow/themes@main/material-draft/theme.css' \
               'https://cdn.jsdelivr.net/gh/flowershow/themes@main/codestorage-draft/theme.css' \
               '/contributing'; do
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

theme_class_reference="https://flowershow.app/docs/reference/theme-class-reference"
for authoring_source in \
  "$ROOT/docs/theme-authoring-tutorial.md" \
  "$ROOT/docs/ai-theme-cloning-skill.md" \
  "$SITE_DIR/contributing.md" \
  "$SITE_DIR/status.md"; do
  if grep -Fq "$theme_class_reference" "$authoring_source"; then
    pass "$(basename "$authoring_source") links the semantic class reference"
  else
    bad "$(basename "$authoring_source") missing semantic class reference"
  fi
done

readiness_source="$ROOT/docs/release-readiness.md"
if [ -s "$readiness_source" ]; then
  pass "release-readiness record exists"
  for readiness_contract in \
    'data-readiness-theme="material-draft"' \
    'data-readiness-theme="codestorage-draft"' \
    'data-recommendation="remain-preview"' \
    'flowershow/flowershow/issues/1367' \
    'github.com/squidfunk/mkdocs-material/blob/master/LICENSE' \
    'github.com/googlefonts/roboto-2/blob/main/LICENSE' \
    'github.com/IBM/plex/blob/master/LICENSE.txt' \
    'Desktop and mobile visual review' \
    'Light and dark visual review' \
    'Landing-fixture marketing copy' \
    'human explicitly authorizes promotion'; do
    if grep -Fq "$readiness_contract" "$readiness_source"; then
      pass "readiness record includes $readiness_contract"
    else
      bad "readiness record missing $readiness_contract"
    fi
  done
else
  bad "docs/release-readiness.md missing or empty"
fi

for readiness_anchor in material codestorage; do
  if grep -Fq "readiness_record: docs/release-readiness.md#$readiness_anchor" "$ROOT/docs/features.yaml"; then
    pass "features ledger links $readiness_anchor readiness record"
  else
    bad "features ledger missing $readiness_anchor readiness record"
  fi
done
readiness_status_count=$(grep -c 'readiness: remain-preview' "$ROOT/docs/features.yaml" || true)
if [ "$readiness_status_count" -eq 2 ]; then
  pass "features ledger keeps both candidates in Preview"
else
  bad "features ledger must record two remain-preview decisions"
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
      "readiness.md"
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
  live_routes=(
    "/|Make your Markdown feel like yours."
    "/themes|data-theme-card=\"letterpress\""
    "/authoring|Authoring a Flowershow theme"
    "/ai-theme-cloning|Cloning a site"
    "/contributing|Contribute a theme"
    "/maintainers|Maintain and release themes"
    "/readiness|Preview release readiness"
  )
  live_body=$(mktemp)
  for route_contract in "${live_routes[@]}"; do
    IFS='|' read -r route expected_text <<< "$route_contract"
    status=$(curl -sL -o "$live_body" -w '%{http_code}' --max-time 20 "$base_url$route?verify=$RANDOM" || echo 000)
    if [ "$status" = "200" ] && grep -Fq "$expected_text" "$live_body"; then
      pass "live $route responds 200 with expected content"
    else
      bad "live $route failed content check (HTTP $status)"
    fi
  done

  for authoring_route in /authoring /ai-theme-cloning /contributing /status; do
    status=$(curl -sL -o "$live_body" -w '%{http_code}' --max-time 20 "$base_url$authoring_route?verify=$RANDOM" || echo 000)
    if [ "$status" = "200" ] && grep -Fq "$theme_class_reference" "$live_body"; then
      pass "live $authoring_route links the semantic class reference"
    else
      bad "live $authoring_route missing semantic class reference (HTTP $status)"
    fi
  done

  status=$(curl -sL -o "$live_body" -w '%{http_code}' --max-time 20 "$base_url/themes?verify=$RANDOM" || echo 000)
  if [ "$status" = "200" ] && grep -Fq '{`{' "$live_body"; then
    bad "live gallery renders a literal MDX wrapper around JSON"
  else
    pass "live gallery JSON renders without an MDX wrapper"
  fi

  for image_path in \
    /assets/themes/letterpress.png \
    /assets/themes/superstack.jpg \
    /assets/themes/lessflowery.jpg \
    /assets/themes/leaf.png \
    /assets/themes/material-preview.png \
    /assets/themes/codestorage-preview.png; do
    image_result=$(curl -sL -o /dev/null -w '%{http_code}|%{content_type}' --max-time 20 "$base_url$image_path" || echo '000|')
    IFS='|' read -r image_status image_type <<< "$image_result"
    if [ "$image_status" = "200" ] && [[ "$image_type" == image/* ]]; then
      pass "live $image_path responds with an image"
    else
      bad "live $image_path failed image check (HTTP $image_status, $image_type)"
    fi
  done
fi

if [ "$fail" -ne 0 ]; then
  echo "verify-site.sh: FAIL"
  exit 1
fi

echo "verify-site.sh: PASS"
