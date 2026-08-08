#!/usr/bin/env bash
# Bootstrap a fresh checkout to a state where verify.sh can run.
# This repo has no build step (pure CSS + Markdown) — init.sh's job is to
# confirm the *external* tools verify.sh depends on are present and working,
# so a red verify.sh run means a real problem, not a missing dependency.
set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

fail=0

echo "== flowershow/themes: init =="

check() {
  local name="$1"; shift
  if "$@" >/dev/null 2>&1; then
    echo "  ok    $name"
  else
    echo "  MISS  $name"
    fail=1
  fi
}

check "yq or python3 (yaml ledger)"    bash -c 'command -v yq || command -v python3'
check "curl (demo-site smoke check)"   command -v curl
check "fl CLI installed"               command -v fl

if command -v fl >/dev/null 2>&1; then
  if fl whoami >/dev/null 2>&1; then
    echo "  ok    fl authenticated ($(fl whoami 2>/dev/null | tail -1))"
  else
    echo "  MISS  fl not authenticated — run 'fl login' interactively (cannot be automated)"
    fail=1
  fi
fi

if [ "$fail" -ne 0 ]; then
  echo ""
  echo "init.sh: one or more dependencies missing. Fix the above, then re-run."
  echo "Note: 'fl login' requires an interactive browser session and cannot be"
  echo "run unattended — this is an intentional stop-and-report point, not a bug."
  exit 1
fi

echo ""
echo "init.sh: green. Run scripts/verify.sh next."
