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
  for theme_name in Letterpress Superstack LessFlowery Leaf Material Monospace; do
    if grep -Fqi "$theme_name" "$SITE_DIR/themes.md"; then
      pass "gallery includes $theme_name"
    else
      bad "gallery missing $theme_name"
    fi
  done

  official_count=$(grep -o 'Official' "$SITE_DIR/themes.md" | wc -l | tr -d ' ')
  preview_count=$(grep -o 'Preview' "$SITE_DIR/themes.md" | wc -l | tr -d ' ')
  [ "$official_count" -ge 5 ] && pass "gallery labels five official themes" || bad "gallery needs five Official labels"
  [ "$preview_count" -ge 1 ] && pass "gallery labels one preview theme" || bad "gallery needs one Preview label"

  card_contracts=(
    "letterpress|official|letterpress|https://letterpress.flowershow.me/|/assets/themes/letterpress.png"
    "superstack|official|superstack|https://superstack.flowershow.me/|/assets/themes/superstack.jpg"
    "lessflowery|official|lessflowery|https://lessflowery.flowershow.me/|/assets/themes/lessflowery.jpg"
    "leaf|official|leaf|https://leaf.flowershow.me/|/assets/themes/leaf.png"
    "material|preview|https://cdn.jsdelivr.net/gh/flowershow/themes@main/material-draft/theme.css|https://material-theme-demo-rufuspollock.flowershow.me|/assets/themes/material-preview.png"
    "monospace|official|monospace|https://monospace-theme-demo-rufuspollock.flowershow.me|/assets/themes/monospace.png"
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
               'https://monospace-theme-demo-rufuspollock.flowershow.me' \
               'https://cdn.jsdelivr.net/gh/flowershow/themes@main/material-draft/theme.css' \
               '"monospace"' \
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

demo_content_source="$ROOT/docs/demo-site-content.md"
if [ -s "$demo_content_source" ]; then
  pass "canonical demo-site content inventory exists"
  for inventory_contract in \
    '| `/` |' \
    '| `/docs/kitchen-sink` |' \
    '| `/blog` |' \
    '| `/blog/first-post` |' \
    'THEME-DIR/demo-showcase.template.md' \
    '_demo-content/docs/kitchen-sink.md' \
    '_demo-content/blog/index.mdx' \
    '_demo-content/blog/first-post.md' \
    'THEME-DIR/demo-showcase.json' \
    'THEME-DIR/demo-landing.css'; do
    if grep -Fq "$inventory_contract" "$demo_content_source"; then
      pass "demo-site inventory includes $inventory_contract"
    else
      bad "demo-site inventory missing $inventory_contract"
    fi
  done
else
  bad "docs/demo-site-content.md missing or empty"
fi

for guide_source in \
  "$ROOT/docs/theme-authoring-tutorial.md" \
  "$ROOT/docs/ai-theme-cloning-skill.md"; do
  if grep -Fq 'demo-site-content.md' "$guide_source"; then
    pass "$(basename "$guide_source") links canonical demo-site content"
  else
    bad "$(basename "$guide_source") missing canonical demo-site content link"
  fi
done

for guide_source in "$SITE_DIR/contributing.md" "$SITE_DIR/maintainers.md"; do
  if grep -Fq '/demo-site-content' "$guide_source"; then
    pass "$(basename "$guide_source") links published demo-site content"
  else
    bad "$(basename "$guide_source") missing published demo-site content link"
  fi
done

for ai_boundary in 'customer claims' 'reference-site marketing identity' 'images or logos'; do
  if grep -Fqi "$ai_boundary" "$ROOT/docs/ai-theme-cloning-skill.md"; then
    pass "AI guide prohibits $ai_boundary"
  else
    bad "AI guide must prohibit $ai_boundary in showcase content"
  fi
done

readiness_source="$ROOT/docs/release-readiness.md"
if [ -s "$readiness_source" ]; then
  pass "release-readiness record exists"
  for readiness_contract in \
    'flowershow/flowershow/issues/1367' \
    'github.com/squidfunk/mkdocs-material/blob/master/LICENSE' \
    'github.com/googlefonts/roboto-2/blob/main/LICENSE' \
    'github.com/IBM/plex/blob/master/LICENSE.txt' \
    'human explicitly authorizes promotion'; do
    if grep -Fq "$readiness_contract" "$readiness_source"; then
      pass "readiness record includes $readiness_contract"
    else
      bad "readiness record missing $readiness_contract"
    fi
  done

  readiness_sections=(
    'material-draft|## Material|## Monospace|Landing-fixture copy, trademark presentation, SVG/icon provenance, and|remain-preview'
    'monospace|## Monospace|## Promotion boundary|Landing-fixture identity, copy, claims, contacts, upstream links, and|official'
  )
  completed_gates=(
    'Desktop and mobile visual review is explicitly recorded.'
    'Light and dark visual review is explicitly recorded.'
    'Home, kitchen sink, blog listing/post, navbar, sidebar, and landing'
  )
  for readiness_spec in "${readiness_sections[@]}"; do
    IFS='|' read -r theme_id start_heading end_heading fixture_gate recommendation <<< "$readiness_spec"
    section=$(awk -v start="$start_heading" -v end="$end_heading" \
      '$0 == start { found=1; next } $0 == end { exit } found' "$readiness_source")
    marker="<div data-readiness-theme=\"$theme_id\" data-recommendation=\"$recommendation\"></div>"
    if grep -Fxq "$marker" <<< "$section"; then
      pass "$theme_id section records $recommendation"
    else
      bad "$theme_id section must record $recommendation on its theme marker"
    fi
    for completed_gate in "${completed_gates[@]}"; do
      if grep -Fq -- "- [x] $completed_gate" <<< "$section"; then
        pass "$theme_id records completed: $completed_gate"
      else
        bad "$theme_id must record completed gate: $completed_gate"
      fi
    done
    if grep -Fq -- "- [x] $fixture_gate" <<< "$section"; then
      pass "$theme_id records completed fixture action: $fixture_gate"
    else
      bad "$theme_id must record completed fixture action: $fixture_gate"
    fi
    if [ "$theme_id" = "material-draft" ]; then
      for pending_gate in \
        'Search is explicitly visually reviewed once the preview site has the' \
        'Final public name and directory name are approved.' \
        'Canonical Flowershow gallery and dashboard changes are prepared.' \
        'Release metadata, purge coverage, version, and changelog are prepared.' \
        'A human explicitly authorizes promotion and the release tag.'; do
        grep -Fq -- "- [ ] $pending_gate" <<< "$section" && \
          pass "$theme_id keeps pending: $pending_gate" || \
          bad "$theme_id must keep unchecked pending gate: $pending_gate"
      done
    else
      for completed_gate in \
        'Final public name and directory name are approved as Monospace / monospace.' \
        'Themes gallery, canonical Flowershow gallery, and dashboard integration are prepared.' \
        'Rufus explicitly authorized promotion on 2026-08-21.'; do
        grep -Fq -- "- [x] $completed_gate" <<< "$section" && \
          pass "$theme_id records completed promotion gate: $completed_gate" || \
          bad "$theme_id must record completed promotion gate: $completed_gate"
      done
      for followup_gate in \
        'Search is visually reviewed after entitlement is enabled in flowershow/flowershow#1370.' \
        'A versioned release tag and changelog are separately approved.'; do
        grep -Fq -- "- [ ] $followup_gate" <<< "$section" && \
          pass "$theme_id records non-blocking follow-up: $followup_gate" || \
          bad "$theme_id must record non-blocking follow-up: $followup_gate"
      done
    fi
  done
else
  bad "docs/release-readiness.md missing or empty"
fi

visual_review_source="$ROOT/docs/visual-review-matrix.md"
if [ -s "$visual_review_source" ]; then
  pass "visual-review matrix exists"
  visual_review_contracts=(
    'Each theme was rendered across all 20 combinations below (40 renders total)'
    'desktop (1280 × 900), mobile (390 × 844)'
    'light, dark'
    'home/navbar/sidebar, kitchen sink, blog list, blog post, landing'
    'requested mode was active'
    'document width equalled the viewport width'
    'local kitchen-sink image was'
    'Search feature entitlement'
    '.search-button'
    'Search therefore remains explicitly unreviewed'
    'Owned landing fixture review'
    'eight renders'
    'data-owned-fixture'
    'code stayed readable'
    'could be mistaken for its'
    'Restrained Monospace homepage correction'
    '20 renders'
    '18px computed H1'
    'one text-first'
    'Material remains **Preview** and Monospace is **Official**'
  )
  for visual_contract in "${visual_review_contracts[@]}"; do
    if grep -Fq "$visual_contract" "$visual_review_source"; then
      pass "visual-review matrix includes $visual_contract"
    else
      bad "visual-review matrix missing evidence: $visual_contract"
    fi
  done
else
  bad "docs/visual-review-matrix.md missing or empty"
fi

provenance_source="$ROOT/docs/landing-fixture-provenance.md"
third_party_notices="$ROOT/THIRD_PARTY_NOTICES.md"
if [ -s "$provenance_source" ] && [ -s "$third_party_notices" ]; then
  pass "landing-fixture provenance record and notices exist"
  material_provenance=$(awk '
    $0 == "## Material" { found=1 }
    $0 == "## code.storage" { exit }
    found
  ' "$provenance_source")
  codestorage_provenance=$(awk '
    $0 == "## code.storage" { found=1 }
    $0 == "## Boundary" { exit }
    found
  ' "$provenance_source")
  material_provenance_contracts=(
    'data-provenance-theme="material-draft" data-disposition="executed-owned-specimen"'
    'github.com/squidfunk/mkdocs-material/blob/master/README.md'
    'github.com/squidfunk/mkdocs-material/blob/master/LICENSE'
    'published fixture now uses Flowershow-authored copy'
    'No inline SVG, upstream logo, repository badge, customer-name tile,'
    'The Material for MkDocs project remains named only as'
    'This disposition is executed'
  )
  for provenance_contract in "${material_provenance_contracts[@]}"; do
    if grep -Fq "$provenance_contract" <<< "$material_provenance"; then
      pass "Material provenance section includes $provenance_contract"
    else
      bad "Material provenance section missing $provenance_contract"
    fi
  done
  codestorage_provenance_contracts=(
    'data-provenance-theme="monospace" data-disposition="executed-owned-specimen"'
    'code.storage/legal/terms'
    'No public content-reuse license was found'
    'published fixture now removes the Code Storage and Pierre'
    'commercial performance, pricing, uptime, security, or customer claims'
    'All navigation and calls to action now point to real Flowershow'
    'unresolved inline SVG was replaced with a repository-authored CSS node mark'
    'This disposition is executed'
  )
  for provenance_contract in "${codestorage_provenance_contracts[@]}"; do
    if grep -Fq "$provenance_contract" <<< "$codestorage_provenance"; then
      pass "code.storage provenance section includes $provenance_contract"
    else
      bad "code.storage provenance section missing $provenance_contract"
    fi
  done

  if grep -Fq 'not legal advice' "$provenance_source"; then
    pass "provenance record states its practical, non-legal boundary"
  else
    bad "provenance record must state that it is not legal advice"
  fi

  material_license_hash=$(awk '/^MIT License$/ { found=1 } found' "$third_party_notices" | shasum -a 256 | awk '{ print $1 }')
  expected_material_license_hash='1d18e1f58419fd7320b4367cbe744fa2ef8189a4627600c92ed81fbb633f3b53'
  if [ "$material_license_hash" = "$expected_material_license_hash" ]; then
    pass "third-party notices preserve the complete Material for MkDocs MIT notice"
  else
    bad "third-party notices must preserve the complete Material for MkDocs MIT notice"
  fi
  if grep -Fq 'inspired the Monospace theme' "$third_party_notices"; then
    pass "third-party notices describe inspiration rather than copied fixture text"
  else
    bad "third-party notices must describe the current inspiration-only boundary"
  fi
else
  bad "landing-fixture provenance record or THIRD_PARTY_NOTICES.md missing"
fi

ledger_specs=(
  'material-draft|material|material|remain-preview'
  'monospace|monospace|codestorage|official'
)
for ledger_spec in "${ledger_specs[@]}"; do
  IFS='|' read -r theme_id readiness_anchor provenance_anchor expected_readiness <<< "$ledger_spec"
  theme_block=$(awk -v id="$theme_id" \
    '$0 == "  - id: " id { found=1 } found && $0 ~ /^  - id: / && $0 != "  - id: " id { exit } found' \
    "$ROOT/docs/features.yaml")
  if grep -Fq "    readiness: $expected_readiness" <<< "$theme_block" && \
     grep -Fq "    readiness_record: docs/release-readiness.md#$readiness_anchor" <<< "$theme_block" && \
     grep -Fq '    visual_review_record: docs/visual-review-matrix.md' <<< "$theme_block" && \
     grep -Fq "    provenance_record: docs/landing-fixture-provenance.md#$provenance_anchor" <<< "$theme_block" && \
     grep -Fq '    landing_fixture: owned-specimen' <<< "$theme_block"; then
    pass "features ledger records $theme_id as $expected_readiness with its readiness record"
  else
    bad "features ledger must bind $theme_id $expected_readiness to #$readiness_anchor"
  fi
done

if [ -s "$SITE_DIR/status.md" ]; then
  for entry in 'issues/1369' 'issues/1370' Material Monospace Official Preview; do
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
      "demo-site-content.md"
      "contributing.md"
      "maintainers.md"
      "readiness.md"
      "visual-review-matrix.md"
      "landing-fixture-provenance.md"
      "third-party-notices.md"
      "status.md"
      "assets/themes/letterpress.png"
      "assets/themes/superstack.jpg"
      "assets/themes/lessflowery.jpg"
      "assets/themes/leaf.png"
      "assets/themes/material-preview.png"
      "assets/themes/monospace.png"
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
    "/demo-site-content|Standard theme demo pages and content"
    "/contributing|Contribute a theme"
    "/maintainers|Maintain and release themes"
    "/readiness|Preview release readiness"
    "/visual-review-matrix|Preview visual review matrix"
    "/landing-fixture-provenance|Landing fixture provenance"
    "/third-party-notices|Third-party notices"
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
    /assets/themes/monospace.png; do
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
