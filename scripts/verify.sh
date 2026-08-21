#!/usr/bin/env bash
# The done condition. One command, exit 0 or not.
#
# Two layers, per the brief this loop was set up against:
#   1. Structural checks on every theme dir listed in docs/features.yaml —
#      these are real gates. A theme fails the run if any of these fail.
#   2. A live HTTP smoke check against each theme's demo site, IF a
#      demo_url has been recorded in the ledger. Catches "CSS parses but
#      the page is blank/500s" that structural checks alone would miss.
#      A theme with no demo_url yet is WARNED, not failed — standing up a
#      demo site is a deliberate `fl publish` action, not something this
#      script does on your behalf.
#
# Judgement calls (does this theme actually look like its inspiration?) are
# NOT checked here — see docs/features.yaml `fidelity` field. That's a
# review queue, never a boolean gate. Baking a probability into this
# script's exit code would be laundering, not verifying.
set -uo pipefail

REPO_ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

# Required custom-property tokens every theme must define. Hand-maintained
# copy of the core token API documented at
# https://flowershow.app/docs/reference/custom-styles. Component selectors are
# documented separately at /docs/reference/theme-class-reference. Keep this
# token gate aligned with custom-styles when the core API changes.
REQUIRED_TOKENS=(
  "--font-heading"
  "--font-body"
  "--color-l-background"
  "--color-l-foreground"
  "--color-l-accent"
  "--color-d-background"
  "--color-d-foreground"
  "--color-d-accent"
)

fail=0
warn=0

pass() { echo "  PASS  $1"; }
bad()  { echo "  FAIL  $1"; fail=1; }
warning() { echo "  WARN  $1"; warn=1; }

echo "== flowershow/themes: verify =="
echo ""

if python3 - "$REPO_ROOT/_demo-content/config.base.json" <<'PYEOF'
import json, sys
with open(sys.argv[1]) as f:
    config = json.load(f)
raise SystemExit(0 if config.get("enableSearch") is True else 1)
PYEOF
then
  pass "shared demo requests the search review surface"
else
  bad "shared demo must request search for visual review"
fi

if python3 - "$REPO_ROOT/codestorage-draft/demo-landing.css" <<'PYEOF'
import re, sys

css = open(sys.argv[1]).read()

def declarations(selector):
    matches = re.finditer(re.escape(selector) + r"\s*\{([^}]*)\}", css)
    return "".join(re.sub(r"\s+", "", match.group(1)) for match in matches)

contracts = {
    ".cs-landing": ("min-width:0;", "overflow:hidden;"),
    ".cs-landing .ts-wrap": ("min-width:0;",),
    ".cs-landing .ts-hero-copy": ("min-width:0;",),
    ".cs-landing .ts-hero-art": ("min-width:0;",),
    ".cs-landing .ts-document": ("min-width:0;",),
    ".cs-landing .ts-section": ("min-width:0;",),
    ".cs-landing pre": ("max-width:var(--cs-measure);", "overflow-x:auto;"),
    ".cs-landing h1::before": ('content:"#";',),
    ".cs-landing h2::before": ('content:"##";',),
}

obsolete = (".ts-card-grid", ".ts-benefits", ".ts-steps", ".ts-final-cta")

raise SystemExit(0 if all(
    all(required in declarations(selector) for required in requirements)
    for selector, requirements in contracts.items()
) and not any(selector in css for selector in obsolete) else 1)
PYEOF
then
  pass "Monospace showcase keeps heading markers and mobile width guards"
else
  bad "Monospace showcase lost heading markers or mobile width guards"
fi

if python3 "$REPO_ROOT/scripts/verify-monospace-style.py" \
  "$REPO_ROOT/codestorage-draft/demo-landing.css"; then
  pass "Monospace showcase keeps effective restrained type and desktop columns"
else
  bad "Monospace showcase lost effective restrained type or desktop columns"
fi

if python3 - "$REPO_ROOT/material-draft/theme.css" <<'PYEOF'
import re, sys
css = open(sys.argv[1]).read()
match = re.search(r"\.site-footer\s*\{([^}]*)\}", css)
declarations = re.sub(r"\s+", "", match.group(1)) if match else ""
raise SystemExit(0 if "background-color:hsl(225,15%,18%);" in declarations else 1)
PYEOF
then
  pass "Material footer stays dark in both color modes"
else
  bad "Material footer must not use a mode-reversing foreground shade"
fi

if [ -s "$REPO_ROOT/_demo-content/assets/demo-image.svg" ] && \
   grep -Fq '](/assets/demo-image.svg)' "$REPO_ROOT/_demo-content/docs/kitchen-sink.md" && \
   ! grep -Fq 'picsum.photos' "$REPO_ROOT/_demo-content/docs/kitchen-sink.md"; then
  pass "kitchen-sink image review uses a repository-owned fixture"
else
  bad "kitchen-sink image surface must use the local deterministic fixture"
fi

if python3 "$REPO_ROOT/scripts/verify-landing-fixtures.py"; then
  pass "published landing fixtures are Flowershow-owned specimens"
else
  bad "published landing fixtures violate ownership/content contracts"
fi

echo ""

# --- discover theme dirs from the ledger -----------------------------------
theme_ids=$(python3 - "$REPO_ROOT/docs/features.yaml" <<'PYEOF'
import re, sys
text = open(sys.argv[1]).read()
themes_block = text.split("\ndocs:\n")[0]
for m in re.finditer(r'- id: (\S+)\n\s+kind: theme\n(?:.*\n)*?\s+dir: (\S+)', themes_block):
    print(f"{m.group(1)}\t{m.group(2)}")
PYEOF
)

if [ -z "$theme_ids" ]; then
  echo "No theme entries found in docs/features.yaml — nothing to verify."
  exit 0
fi

while IFS=$'\t' read -r id dir; do
  echo "-- $id ($dir) --"
  css="$REPO_ROOT/$dir/theme.css"

  if [ ! -s "$css" ]; then
    bad "$dir/theme.css missing or empty"
    echo ""
    continue
  fi
  pass "theme.css exists and is non-empty"

  # brace balance as a cheap parse check (no node/postcss dependency)
  opens=$(grep -o '{' "$css" | wc -l | tr -d ' ')
  closes=$(grep -o '}' "$css" | wc -l | tr -d ' ')
  if [ "$opens" = "$closes" ]; then
    pass "brace-balanced ($opens open / $closes close)"
  else
    bad "brace mismatch ($opens open / $closes close) — CSS likely malformed"
  fi

  missing_tokens=()
  for tok in "${REQUIRED_TOKENS[@]}"; do
    if ! grep -q -- "$tok:" "$css"; then
      missing_tokens+=("$tok")
    fi
  done
  if [ ${#missing_tokens[@]} -eq 0 ]; then
    pass "all required tokens defined"
  else
    bad "missing tokens: ${missing_tokens[*]}"
  fi

  if grep -q 'data-theme="dark"' "$css"; then
    pass "dark mode block present"
  else
    bad "no :root[data-theme=\"dark\"] block"
  fi

  if find "$REPO_ROOT/$dir" -maxdepth 1 -iname "preview*.png" -o -iname "preview*.jpg" 2>/dev/null | grep -q .; then
    pass "preview asset present"
  else
    warning "no preview asset yet (not a hard gate pre-launch, but required before promoting out of draft)"
  fi

  demo_url=$(python3 "$REPO_ROOT/scripts/read-feature-field.py" \
    "$REPO_ROOT/docs/features.yaml" "$id" demo_url)

  if [ -n "$demo_url" ]; then
    expected_demo_content="Theme Demo Site"
    if [ -s "$REPO_ROOT/$dir/demo-showcase.json" ]; then
      expected_demo_content=$(python3 - "$REPO_ROOT/$dir/demo-showcase.json" <<'PYEOF'
import json, sys
with open(sys.argv[1]) as source:
    print(f'data-theme-showcase="{json.load(source)["slug"]}"')
PYEOF
      )
    fi
    compatibility_url=$(python3 "$REPO_ROOT/scripts/read-feature-field.py" \
      "$REPO_ROOT/docs/features.yaml" "$id" landing_compatibility_url)
    if python3 "$REPO_ROOT/scripts/verify-demo-routes.py" \
      "$demo_url" "$expected_demo_content" "$compatibility_url"; then
      pass "all standard demo routes respond with expected content ($demo_url)"
    else
      bad "one or more standard demo routes failed ($demo_url)"
    fi
  else
    warning "no demo_url recorded yet — live smoke check skipped, not failed"
  fi

  # The landing demo is a separate site (raw .html index). Check it too — it's
  # the primary artifact for stage-1 work, and leaving it unchecked is how a
  # stale copy went unnoticed.
  #
  # NOTE: hit the bare root, NOT /index.html. Raw .html paths 404 when given
  # any query string (flowershow/flowershow#1345), so the usual cache-busting
  # trick breaks them. The bare root serves the same file and tolerates ?cb=.
  landing_url=$(python3 "$REPO_ROOT/scripts/read-feature-field.py" \
    "$REPO_ROOT/docs/features.yaml" "$id" landing_demo_url)

  if [ -n "$landing_url" ]; then
    lcode=$(curl -sL -o /tmp/verify-landing-body.html -w "%{http_code}" --max-time 20 "${landing_url}/?cb=$RANDOM" || echo "000")
    if [ "$lcode" = "200" ] && grep -qi "<html" /tmp/verify-landing-body.html; then
      pass "landing demo responds 200 ($landing_url)"
    else
      bad "landing demo smoke check failed (HTTP $lcode) ($landing_url)"
    fi
  fi

  echo ""
done <<< "$theme_ids"

if [ -d "$REPO_ROOT/site" ]; then
  echo "-- themes preview site --"
  if "$REPO_ROOT/scripts/verify-site.sh"; then
    pass "themes preview site passes"
  else
    bad "themes preview site failed verification"
  fi
  echo ""
fi

echo "== summary =="
if [ "$fail" -ne 0 ]; then
  echo "verify.sh: FAIL"
  exit 1
else
  if [ "$warn" -ne 0 ]; then
    echo "verify.sh: PASS (with warnings — see WARN lines above)"
  else
    echo "verify.sh: PASS"
  fi
  exit 0
fi
