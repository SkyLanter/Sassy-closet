#!/usr/bin/env bash
# Repo-root alias. Real kit lives in excel-kit/kit.sh.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT/excel-kit/kit.sh" "$@"
