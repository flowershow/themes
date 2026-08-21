#!/usr/bin/env bash
# Assemble or publish the Flowershow themes preview site.
set -euo pipefail

ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"

usage() {
  echo "Usage: scripts/site.sh build OUTPUT_DIR" >&2
  echo "       scripts/site.sh publish [SITE_NAME]" >&2
  exit 2
}

build_site() {
  local output_dir="$1"

  if [ -d "$output_dir" ] && [ -n "$(find "$output_dir" -mindepth 1 -maxdepth 1 -print -quit)" ]; then
    echo "Output directory must be empty: $output_dir" >&2
    exit 1
  fi

  mkdir -p "$output_dir/assets/themes"
  cp -R "$ROOT/site/." "$output_dir/"
  cp "$ROOT/docs/theme-authoring-tutorial.md" "$output_dir/authoring.md"
  cp "$ROOT/docs/ai-theme-cloning-skill.md" "$output_dir/ai-theme-cloning.md"
  cp "$ROOT/docs/demo-site-content.md" "$output_dir/demo-site-content.md"
  cp "$ROOT/docs/release-readiness.md" "$output_dir/readiness.md"
  cp "$ROOT/docs/visual-review-matrix.md" "$output_dir/visual-review-matrix.md"
  cp "$ROOT/docs/landing-fixture-provenance.md" "$output_dir/landing-fixture-provenance.md"
  cp "$ROOT/THIRD_PARTY_NOTICES.md" "$output_dir/third-party-notices.md"

  cp "$ROOT/letterpress/preview.png" "$output_dir/assets/themes/letterpress.png"
  cp "$ROOT/superstack/fs-superstack-page-light.jpg" "$output_dir/assets/themes/superstack.jpg"
  cp "$ROOT/lessflowery/fs-lessflowery-page-light.jpg" "$output_dir/assets/themes/lessflowery.jpg"
  cp "$ROOT/leaf/preview.png" "$output_dir/assets/themes/leaf.png"
  cp "$ROOT/material-draft/preview.png" "$output_dir/assets/themes/material-preview.png"
  cp "$ROOT/monospace/preview.png" "$output_dir/assets/themes/monospace.png"
}

command_name="${1:-}"
case "$command_name" in
  build)
    [ "$#" -eq 2 ] || usage
    build_site "$2"
    ;;
  publish)
    [ "$#" -le 2 ] || usage
    site_name="${2:-flowershow-themes-preview}"
    publish_dir=$(mktemp -d)
    trap 'rm -rf -- "$publish_dir"' EXIT
    "$ROOT/scripts/init.sh"
    "$ROOT/scripts/verify-site.sh"
    build_site "$publish_dir"
    fl "$publish_dir" --name "$site_name" --yes
    ;;
  *)
    usage
    ;;
esac
