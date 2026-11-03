import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "run_daily_shop_check.sh"
WORKFLOW = ROOT / ".github" / "workflows" / "daily-shop-check.yml"

STUB = """import json, sys
a = sys.argv[1:]
md, js = a[a.index('--out-md') + 1], a[a.index('--out-json') + 1]
mode = a[a.index('--mode') + 1] if '--mode' in a else 'PASS'
if mode == 'CRASH':
    sys.exit(2)
open(md, 'w').write('# x\\n' + mode + '\\n')
json.dump({'overall': mode, 'sections': {}, 'writes': 'none', 'network': 'none'}, open(js, 'w'))
sys.exit({'PASS': 0, 'WARN': 1, 'FAIL': 2}.get(mode, 0))
"""


@pytest.fixture
def stubdir(tmp_path):
    d = tmp_path / "scripts"
    d.mkdir()
    shutil.copy(RUNNER, d / RUNNER.name)
    (d / "daily_shop_check.py").write_text(STUB)
    return d


def run(stubdir, tmp_path, *check_args, date="2026-10-20", extra=()):
    out = tmp_path / "out"
    cmd = ["bash", str(stubdir / RUNNER.name), "--out-dir", str(out), "--date", date,
           "--python", sys.executable, *extra, "--", *check_args]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, out, p


@pytest.mark.parametrize("mode,rc", [("PASS", 0), ("WARN", 0), ("FAIL", 1)])
def test_exit_only_nonzero_on_fail(stubdir, tmp_path, mode, rc):
    got, out, p = run(stubdir, tmp_path, "--mode", mode)
    assert got == rc, p.stderr
    assert json.loads((out / "daily-2026-10-20.json").read_text())["overall"] == mode
    assert (out / "daily-2026-10-20.md").read_text().startswith("# x")
    assert f"2026-10-20: {mode}" in p.stdout


def test_crash_without_report_is_error_3(stubdir, tmp_path):
    got, out, _ = run(stubdir, tmp_path, "--mode", "CRASH")
    assert got == 3 and not (out / "daily-2026-10-20.json").exists()


def test_stale_report_removed_before_run(stubdir, tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "daily-2026-10-20.json").write_text('{"overall": "PASS"}')
    got, _, _ = run(stubdir, tmp_path, "--mode", "CRASH")
    assert got == 3 and not (out / "daily-2026-10-20.json").exists()


def test_bad_date_and_unknown_option_and_out_override(stubdir, tmp_path):
    assert run(stubdir, tmp_path, date="20261020")[0] == 3
    assert run(stubdir, tmp_path, extra=("--bogus",))[0] == 3
    assert run(stubdir, tmp_path, "--out-md", "x.md")[0] == 3


@pytest.mark.skipif(not WORKFLOW.exists(), reason="daily-shop-check.yml left out of the safe-frame merge (scheduled workflow needs Boss OK)")
def test_workflow_is_read_only_and_scheduled():
    w = WORKFLOW.read_text()
    assert "schedule:" in w and "workflow_dispatch:" in w
    assert "permissions:\n  contents: read" in w
    assert "secrets." not in w and "persist-credentials: false" in w
    for bad in ("git push", "gh pr", ": write", "vercel", "BLOB_", "META_", "SQUARE"):
        assert bad not in w, bad
    assert "scripts/run_daily_shop_check.sh" in w and "upload-artifact" in w
