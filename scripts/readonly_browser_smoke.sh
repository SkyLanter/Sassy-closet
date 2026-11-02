#!/usr/bin/env bash
# Read-only Playwright smoke for both sell hosts and intake.
# GET only: held PDP 404, S06 PDP $25, noindex. No cookies, no deploy.
#
# Usage: scripts/readonly_browser_smoke.sh [--dry-run|--self-test]
#   --dry-run    print every check; no browser and no network.
#   --self-test  run the local stub browser once; no live hosts.
# Env: SHOP_HOSTS, INTAKE_BASE, HELD_MAS, CHECK_TIMEOUT.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
MODE=""
for arg in "$@"; do
  case "$arg" in
    --dry-run|--self-test)
      if [ -n "$MODE" ]; then echo "unknown arg $arg" >&2; exit 2; fi
      MODE="$arg"
      ;;
    *) echo "unknown arg $arg" >&2; exit 2 ;;
  esac
done
if [ "$MODE" = --self-test ]; then
  exec node "$ROOT/scripts/browser-smoke/self-test.mjs"
fi
if [ "$MODE" = --dry-run ]; then
  exec node "$ROOT/scripts/browser-smoke/smoke.mjs" --dry-run
fi
if [ ! -d "$ROOT/scripts/browser-smoke/node_modules/playwright" ]; then
  echo "FAIL playwright is not installed; run npm ci in scripts/browser-smoke" >&2
  exit 1
fi
cd "$ROOT/scripts/browser-smoke" || exit 1
exec node smoke.mjs
