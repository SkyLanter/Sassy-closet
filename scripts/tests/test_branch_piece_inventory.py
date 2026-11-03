import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "branch_piece_inventory.sh"


def _git(repo, *a):
    subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)


def test_lists_only_piece_branches(tmp_path):
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "first | pipe")
    _git(tmp_path, "branch", "piece-001-a")
    _git(tmp_path, "branch", "other")
    out = subprocess.run(["bash", str(SCRIPT), "--repo", str(tmp_path)], check=True, capture_output=True, text=True).stdout
    assert "`piece-001-a`" in out
    assert "other" not in out
    assert "first \\| pipe" in out
    assert "Total: 1" in out
