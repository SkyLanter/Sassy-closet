import subprocess, sys
from pathlib import Path
import shop_health as sh

HERE = Path(__file__).parent
FX = HERE / "fixtures" / "health"


def test_ok_fixture():
    text, problems = sh.build_report(FX / "ok")
    assert problems == []
    assert "live count: 3" in text
    assert "S06 price: $25 (OK)" in text
    assert "held list: S14 A24" in text and "held count: 2" in text
    assert "STATUS: OK" in text


def test_bad_fixture_flags_s06_and_held_leak():
    text, problems = sh.build_report(FX / "bad")
    assert any("S06 is $19" in p for p in problems)
    assert any("S14" in p for p in problems)
    assert "PROBLEMS:" in text


def test_missing_files_is_a_problem(tmp_path):
    text, problems = sh.build_report(tmp_path)
    assert len(problems) == 2


def test_cli_exit_codes():
    s = str(HERE / "shop_health.py")
    ok = subprocess.run([sys.executable, s, "--root", str(FX / "ok")], capture_output=True, text=True)
    bad = subprocess.run([sys.executable, s, "--root", str(FX / "bad")], capture_output=True, text=True)
    assert ok.returncode == 0 and bad.returncode == 1
