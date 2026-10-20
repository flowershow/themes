#!/usr/bin/env bash
# Build and publish a demo site for a theme.
#
#   scripts/demo-site.sh <theme-dir> [--local] [--landing <file.html>] [--landing-page <file.md>] [--name <site-name>] [--build-only <output-dir>]
#
# Assembles a site from (see docs/demo-site-content.md):
#   - _demo-content/          the shared kitchen sink and blog routes
#   - <theme-dir>/theme.css   applied via a jsDelivr URL pinned to the current
#                             git branch (no release/tag needed for drafts)
#   - --local                 preview the WORKING TREE instead: theme.css is
#                             published as the site's custom.css and `theme`
#                             is left unset, so nothing needs committing or
#                             pushing. Flowershow links custom.css right where
#                             theme.css would go (validated on leaf, see
#                             docs/plans/2026-10-17-theme-from-website-handoff.md).
#                             Publishes to a stable <theme>-theme-preview site,
#                             never to the real <theme>-theme-demo.
#   - <theme-dir>/demo-showcase.template.md + demo-showcase.json +
#                             demo-landing.css: a validated theme-specific
#                             homepage, rendered at / with an identical
#                             /landing compatibility page.
#   - --landing <file>        optional raw .html landing page, published as
#                             index.html, REPLACING the site's home page. Used
#                             for stage-1 Tailwind repros — plain HTML with no
#                             theme, no nav/footer, compared like-for-like
#                             against the target before anything is themed.
#   - --landing-page <file>   exceptional `layout: plain` research page,
#                             published at /landing ALONGSIDE the rest of the
#                             site (kitchen sink, blog) rather than replacing
#                             it — one demo site, not a separate one. Prefer
#                             this over --landing whenever the target site has
#                             normal chrome you want: layout:plain still gets
#                             Flowershow's standard nav/footer (see
#                             docs/theme-authoring-tutorial.md), just with
#                             Tailwind typography ("prose") turned off, so the
#                             page is a blank canvas for hand-built HTML+
#                             Tailwind inside the markdown file. --landing
#                             (raw HTML, no nav/footer) is still right for a
#                             target with materially different/no chrome.
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
LANDING_PAGE=""
SITE_NAME=""
BUILD_ONLY_DIR=""
LOCAL=""

while [ $# -gt 0 ]; do
  case "$1" in
    --landing)      LANDING="$2"; shift 2 ;;
    --landing-page) LANDING_PAGE="$2"; shift 2 ;;
    --name)         SITE_NAME="$2"; shift 2 ;;
    --build-only)   BUILD_ONLY_DIR="$2"; shift 2 ;;
    --local)        LOCAL=1; shift ;;
    -*) echo "unknown flag: $1" >&2; exit 2 ;;
    *) THEME_DIR="$1"; shift ;;
  esac
done

if [ -z "$THEME_DIR" ]; then
  echo "usage: scripts/demo-site.sh <theme-dir> [--local] [--landing <file.html>] [--landing-page <file.md>] [--name <site-name>] [--build-only <output-dir>]" >&2
  exit 2
fi

if [ -n "$LANDING" ] && [ -n "$LANDING_PAGE" ]; then
  echo "--landing and --landing-page are mutually exclusive — pick one" >&2
  exit 2
fi

if [ ! -f "$REPO_ROOT/$THEME_DIR/theme.css" ]; then
  echo "no such theme: $THEME_DIR/theme.css" >&2
  exit 1
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
SHA="$(git rev-parse HEAD)"
if [ -n "$LOCAL" ]; then
  SITE_NAME="${SITE_NAME:-${THEME_DIR%-draft}-theme-preview}"
  # --local republishes with --overwrite (below), so it must never be pointed
  # at a real demo site — that would replace it with uncommitted CSS
  case "$SITE_NAME" in
    *-theme-demo)
      echo "--local refuses to publish to a demo site ($SITE_NAME); use a -theme-preview name" >&2
      exit 2 ;;
  esac
else
  SITE_NAME="${SITE_NAME:-${THEME_DIR%-draft}-theme-demo}"
fi

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
if [ -n "$LOCAL" ]; then
  # empty = leave `theme` unset; theme.css goes out as custom.css instead
  THEME_URL=""
else
  THEME_URL="https://cdn.jsdelivr.net/gh/flowershow/themes@${SHA}/${THEME_DIR}/theme.css"
fi

echo "== demo site: $SITE_NAME =="
echo "   theme:  $THEME_DIR"
if [ -n "$LOCAL" ]; then
  echo "   css:    working-tree $THEME_DIR/theme.css -> custom.css (--local)"
else
  echo "   branch: $BRANCH"
  echo "   commit: ${SHA:0:8}"
  echo "   css:    $THEME_URL"
fi

# jsDelivr can only serve commits that are on GitHub.
if [ -z "$LOCAL" ] && [ -z "$BUILD_ONLY_DIR" ] && ! git branch -r --contains "$SHA" 2>/dev/null | grep -q .; then
  echo ""
  echo "ERROR: commit ${SHA:0:8} is not on any remote branch. jsDelivr cannot"
  echo "serve it. Push first:  git push -u origin $BRANCH"
  echo "(or preview the working tree with --local)"
  exit 1
fi

if [ -z "$LOCAL" ] && [ -n "$(git status --porcelain -- "$THEME_DIR")" ]; then
  echo ""
  echo "WARNING: $THEME_DIR has uncommitted changes. The demo will be built"
  echo "from commit ${SHA:0:8}, NOT your working tree. Commit and push first,"
  echo "or preview the working tree with --local."
fi

if [ -n "$BUILD_ONLY_DIR" ]; then
  BUILD_DIR="$BUILD_ONLY_DIR"
  if [ -d "$BUILD_DIR" ] && [ -n "$(find "$BUILD_DIR" -mindepth 1 -maxdepth 1 -print -quit)" ]; then
    echo "build-only output directory must be empty: $BUILD_DIR" >&2
    exit 2
  fi
  mkdir -p "$BUILD_DIR"
else
  BUILD_DIR="$(mktemp -d)"
  trap 'rm -rf "$BUILD_DIR"' EXIT
fi

cp -R "$REPO_ROOT/_demo-content/." "$BUILD_DIR/"

SHOWCASE_METADATA="$REPO_ROOT/$THEME_DIR/demo-showcase.json"
SHOWCASE_TEMPLATE="$REPO_ROOT/$THEME_DIR/demo-showcase.template.md"
if [ -f "$SHOWCASE_METADATA" ] && [ -z "$LANDING" ] && [ -z "$LANDING_PAGE" ]; then
  if [ ! -f "$SHOWCASE_TEMPLATE" ]; then
    echo "showcase metadata requires $THEME_DIR/demo-showcase.template.md" >&2
    exit 1
  fi
  python3 "$REPO_ROOT/scripts/render-theme-showcase.py" \
    "$SHOWCASE_TEMPLATE" \
    "$SHOWCASE_METADATA" \
    "$BUILD_DIR/index.md"
  cp "$BUILD_DIR/index.md" "$BUILD_DIR/landing.md"
  if [ -f "$REPO_ROOT/$THEME_DIR/demo-landing.css" ]; then
    cp "$REPO_ROOT/$THEME_DIR/demo-landing.css" "$BUILD_DIR/custom.css"
  fi
  echo "   showcase: $THEME_DIR/demo-showcase.template.md + demo-showcase.json -> / and /landing"
fi

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

if [ -n "$LANDING_PAGE" ]; then
  if [ ! -f "$REPO_ROOT/$LANDING_PAGE" ]; then
    echo "no such landing-page file: $LANDING_PAGE" >&2
    exit 1
  fi
  # published alongside the rest of _demo-content, not replacing it — the
  # page itself must carry `layout: plain` frontmatter to get Flowershow's
  # nav/footer without prose typography fighting hand-built Tailwind markup
  cp "$REPO_ROOT/$LANDING_PAGE" "$BUILD_DIR/landing.md"
  echo "   landing-page: $LANDING_PAGE -> landing.md (published at /landing)"

  # Convention: a sibling <basename>.css next to the landing-page .md is
  # published as the site's custom.css (Flowershow looks for exactly that
  # filename at content root — server/api/routers/site.ts). Site-wide, so
  # landing-specific rules must be scoped under a wrapper class.
  LANDING_CSS="${LANDING_PAGE%.md}.css"
  if [ -f "$REPO_ROOT/$LANDING_CSS" ]; then
    cp "$REPO_ROOT/$LANDING_CSS" "$BUILD_DIR/custom.css"
    echo "   landing-page css: $LANDING_CSS -> custom.css"
  fi
fi

# --local: theme.css becomes custom.css, so it can't share it with a
# showcase/landing step's custom.css (only Monospace's demo-landing.css today)
if [ -n "$LOCAL" ]; then
  if [ -f "$BUILD_DIR/custom.css" ]; then
    echo "--local can't preview a theme whose showcase or landing page writes custom.css" >&2
    exit 2
  fi
  cp "$REPO_ROOT/$THEME_DIR/theme.css" "$BUILD_DIR/custom.css"
  echo "   custom.css: $THEME_DIR/theme.css"
fi

# Merge the theme URL into the shared base config rather than writing a bare
# config. The base config matters: Flowershow only renders the navbar if a nav
# title, nav links, CTA, social links, or search is configured — so without it
# there is no navbar on the demo at all, and a theme's navbar styling is
# invisible. Same reason the sidebar and mode switch are enabled there.
rm -f "$BUILD_DIR/config.base.json"
python3 - "$REPO_ROOT/_demo-content/config.base.json" "$THEME_URL" "$BUILD_DIR/config.json" "$SHOWCASE_METADATA" <<'PYEOF'
import json, sys
base_path, theme_url, out_path, metadata_path = sys.argv[1:]
with open(base_path) as f:
    cfg = json.load(f)
theme = cfg.get("theme")
if not theme_url:
    # --local: no `theme` at all, or the default theme would be overridden
    # by whatever the base config names instead of our custom.css
    if isinstance(theme, dict):
        theme.pop("theme", None)
    else:
        cfg.pop("theme", None)
elif isinstance(theme, dict):
    theme["theme"] = theme_url
else:
    cfg["theme"] = theme_url
if metadata_path and __import__("os").path.isfile(metadata_path):
    with open(metadata_path) as f:
        metadata = json.load(f)
    cfg["title"] = f"Flowershow — {metadata['name']} theme"
    cfg["nav"] = {
        "title": "Flowershow",
        "links": [
            {"href": "/", "name": "Home"},
            {"href": "/docs/kitchen-sink", "name": "Kitchen Sink"},
            {"href": "/blog", "name": "Blog"},
            {"href": metadata["sourceUrl"], "name": "Theme Source"},
            # keep a dropdown: its hooks only render from a nav group
            {"name": "More", "links": cfg["nav"]["links"][-1]["links"]},
        ],
        "cta": {
            "href": "https://flowershow.app/publish",
            "name": "Publish with Flowershow",
        },
    }
with open(out_path, "w") as f:
    json.dump(cfg, f, indent=2)
PYEOF

if [ -n "$BUILD_ONLY_DIR" ]; then
  echo ""
  echo "Built demo site at $BUILD_DIR"
  exit 0
fi

echo ""
if [ -n "$LOCAL" ]; then
  # the build dir is fresh every run, so fl sees it as unlinked; --overwrite
  # lets it replace the existing preview site instead of refusing
  fl "$BUILD_DIR" --name "$SITE_NAME" --overwrite --yes
  echo ""
  echo "Preview of UNCOMMITTED $THEME_DIR/theme.css. Don't record it as demo_url."
  echo "If a page still shows old CSS, Flowershow's page cache may be stale —"
  echo "hard-reload or wait before assuming the CSS is wrong."
else
  fl "$BUILD_DIR" --name "$SITE_NAME" --yes
  echo ""
  echo "Record the URL above in docs/features.yaml as this theme's demo_url,"
  echo "then re-run scripts/verify.sh to smoke-check it."
fi
