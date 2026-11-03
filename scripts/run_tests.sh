#!/usr/bin/env bash
# Run pytest, saving a timestamped junit XML so a flaky failure's name is kept.
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python}"
mkdir -p out/test-results
xml="out/test-results/junit-$(date +%Y%m%d-%H%M%S)-$$.xml"
"$PY" -m pytest --junitxml="$xml" "$@"
rc=$?
echo "junit: $xml"
exit $rc
