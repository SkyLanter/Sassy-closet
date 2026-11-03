from pathlib import Path
S = (Path(__file__).resolve().parents[1] / "hard_recheck.sh").read_text()

def test_tip_status_step_is_informational():
    assert 'record tip-status 0 INFO' in S

def test_tip_status_has_fallback_and_timeout():
    assert "Recommended tip: none found" in S
    assert "timeout \"${TIP_TIMEOUT:-30}\" bash" in S and "< /dev/null" in S

def test_tip_status_before_summary():
    assert S.index("record tip-status") < S.index("TOTAL=$((")

def test_tip_status_missing_script_and_timeout_notes():
    assert "overnight_tip_status.sh not found, skipped" in S
    assert "timeout unavailable, skipped" in S
    assert '"$TIPRC" = 124' in S and "timed out after" in S

def test_tip_footer_block_never_fails(tmp_path):
    import subprocess
    start = S.index("# i. read-only tip-status footer"); end = S.index("TOTAL=$((")
    d = tmp_path / "scripts"; d.mkdir()
    (d / "overnight_tip_status.sh").write_text("sleep 5\n")
    steps = tmp_path / "steps"
    body = ("record() { printf '%s\\t' \"$@\" >> " + str(steps) + "; echo >> " + str(steps) + "; }\n"
            + S[start:end])
    sh = d / "blk.sh"; sh.write_text(body)
    r = subprocess.run(["bash", str(sh)], env={"PATH": "/usr/bin:/bin", "TIP_TIMEOUT": "1"}, capture_output=True, text=True, timeout=20)
    assert r.returncode == 0
    out = steps.read_text()
    assert "INFO" in out and "none found" in out and "timed out" in out
    (d / "overnight_tip_status.sh").unlink(); steps.unlink()
    subprocess.run(["bash", str(sh)], env={"PATH": "/usr/bin:/bin"}, timeout=20)
    assert "not found, skipped" in steps.read_text()
