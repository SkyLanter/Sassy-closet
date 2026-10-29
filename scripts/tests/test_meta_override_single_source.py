"""Piece 80 placeholder tests: Meta overrides are single-source, never PASS."""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import daily_summary_draft as d

R = "override pass needs Luxubu + Mini Boss record"


def test_override_pass_becomes_unchecked():
    assert d.single_source_override("pass") == ("unchecked", R)
    assert d.single_source_override("PASS")[0] == "unchecked"


def test_override_fail_and_unchecked_kept():
    assert d.single_source_override("fail")[0] == "fail"
    assert d.single_source_override("unchecked")[0] == "unchecked"
    assert d.single_source_override(None)[0] == "unchecked"


def test_build_override_pass_not_shown_as_pass():
    t = d.build(None, None, {}, None, None, "pass", "pass", "2000-01-01")
    assert R in t
    assert "Instagram: PASS" not in t and "Facebook: PASS" not in t
    assert "NOT CLEAR" in t


def test_build_override_fail_shows_fail():
    t = d.build(None, None, {}, None, None, "fail", "unchecked", "2000-01-01")
    assert "FAIL" in t


def test_cli_flags_removed():
    src = (Path(d.__file__)).read_text(encoding="utf-8")
    assert 'add_argument("--meta-ig"' not in src and 'add_argument("--meta-fb"' not in src
    r = subprocess.run([sys.executable, d.__file__, "--help"], capture_output=True, text=True)
    assert "--meta-ig" not in r.stdout and "--meta-fb" not in r.stdout
