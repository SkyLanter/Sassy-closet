import os
"""Guards for scripts/pre_deploy_privacy_checklist.sh (read-only, no network)."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "pre_deploy_privacy_checklist.sh"


def test_bash_syntax():
    subprocess.run(["bash", "-n", str(SCRIPT)], check=True)


def test_is_executable():
    assert SCRIPT.stat().st_mode & 0o111


def test_runs_clean_and_lists_sections():
    r = subprocess.run(["bash", str(SCRIPT)], cwd=ROOT, capture_output=True,
                       text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    out = r.stdout
    for marker in ("[1]", "[2]", "[3]", "[4]", "=== END (read-only; zero writes) ==="):
        assert marker in out
    assert len(re.findall(r"^\s+\d+\. ", out, re.M)) >= 1
    assert "12. OneDrive" in out
    assert "S06 $25" in out


def test_output_has_no_cost_or_private_values():
    out = subprocess.run(["bash", str(SCRIPT)], cwd=ROOT, capture_output=True,
                         text=True, timeout=60).stdout
    assert not re.search(r"cost_(cny|usd)\"?\s*[:=]\s*\d", out)
    assert ("tao" + "bao.com") not in out.lower()
    assert not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", out)


def test_script_never_deploys_or_writes():
    src = SCRIPT.read_text()
    for bad in ("vercel deploy", "vercel --prod", "git push", "gh pr", "curl -X POST",
                "curl -X PATCH", "BLOB_READ_WRITE_TOKEN", "graph.facebook.com"):
        assert bad not in src, bad
    assert "WRITE_PROBES=0" in src


def test_section1_recommends_tip_286_not_stale():
    out = subprocess.run(["bash", str(SCRIPT)], cwd=ROOT, capture_output=True,
                         text=True, timeout=60).stdout
    sec1 = out.split("[1]", 1)[1].split("[2]", 1)[0]
    lines = [l.strip() for l in sec1.splitlines()]
    primary = [l for l in lines if l.startswith("- PRIMARY:")]
    assert primary == ["- PRIMARY: piece-286-overnight-merge-ready (d9f53c7): 282 + 284 checklist tip fix (merge this alone)"]
    for stale in ("piece-266", "piece-272", "piece-275", "piece-280", "piece-281", "piece-282", "piece-284", "166da87", "93bfb5d", "633d24e", "c58f9ca", "83f6f94", "9a0b730"):
        assert stale not in primary[0], stale
    assert "piece-266-overnight-all-docs (" not in sec1
    assert "piece-272-overnight-ops:" not in sec1
    assert "piece-275-overnight-merge-ready (" not in sec1
    assert "local piece-286-overnight-merge-ready ->" in sec1
    assert "266/270/271/272/274/275/280/281" in sec1 and "240-281" in sec1 and "#188/#189" in sec1


def test_section1_has_live_secondary_from_tip_status(tmp_path):
    env = dict(os.environ, PROOF_ROOT=str(tmp_path))  # empty proof root -> deterministic
    out = subprocess.run(["bash", str(SCRIPT)], cwd=ROOT, capture_output=True,
                         text=True, env=env, check=True).stdout
    sec1 = out.split("[2]")[0]
    assert "SECONDARY (live, overnight_tip_status.sh):" in sec1
    assert "Recommended tip: none found with PASS proof" in sec1
