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
# copy of the ~10-token core API found in apps/flowershow/styles/
# default-theme.css during the 2026-08-08 audit. THIS WILL DRIFT — refresh
# it against flowershow/flowershow#1338 (publish the semantic class list)
# once that ships. Until then this is the best available source of truth.
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

  demo_url=$(python3 - "$REPO_ROOT/docs/features.yaml" "$id" <<'PYEOF'
import re, sys
text = open(sys.argv[1]).read()
target = sys.argv[2]
m = re.search(rf'- id: {re.escape(target)}\n(?:.*\n)*?\s+demo_url: (\S+)', text)
url = m.group(1) if m else "null"
print("" if url == "null" else url)
PYEOF
  )

  if [ -n "$demo_url" ]; then
    code=$(curl -s -o /tmp/verify-demo-body.html -w "%{http_code}" --max-time 20 "$demo_url" || echo "000")
    if [ "$code" = "200" ] && grep -q "Theme Demo Site" /tmp/verify-demo-body.html; then
      pass "demo site responds 200 and renders expected content ($demo_url)"
    else
      bad "demo site smoke check failed (HTTP $code) ($demo_url)"
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
  landing_url=$(python3 - "$REPO_ROOT/docs/features.yaml" "$id" <<'PYEOF'
import re, sys
text = open(sys.argv[1]).read()
target = sys.argv[2]
m = re.search(rf'- id: {re.escape(target)}\n(?:.*\n)*?\s+landing_demo_url: (\S+)', text)
url = m.group(1) if m else "null"
print("" if url == "null" else url)
PYEOF
  )

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
