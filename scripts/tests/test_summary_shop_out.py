"""Placeholder tests for piece 110: one shop out folder (SASSY_OUT), not <worktree>/out."""
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import daily_summary_draft as ds  # noqa: E402


def _run(tmp_path, monkeypatch, extra=()):
    root = tmp_path / "root"
    (root / "out").mkdir(parents=True)
    dg = tmp_path / "digest.txt"
    dg.write_text("", encoding="utf-8")
    gp = tmp_path / "gaps.json"
    gp.write_text("", encoding="utf-8")
    cwd = tmp_path / "worktree"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    argv = ["--date", "2000-01-01", "--root", str(root), "--digest", str(dg),
            "--gaps", str(gp), *extra]
    assert ds.main(argv) == 0
    return cwd


def test_shop_out_default(monkeypatch):
    monkeypatch.delenv("SASSY_OUT", raising=False)
    # Same guarantee (default is the one shared shop out folder, not <worktree>/out),
    # without hardcoding this box's path in the test.
    assert ds.shop_out() == Path(ds.DEFAULT_SHOP_OUT)
    assert ds.shop_out().is_absolute() and ds.shop_out().name == "out"
    assert ds.shop_out().parent.name == "sassy-closet"
    assert ds.shop_out() != Path.cwd() / "out"


def test_shop_out_env(monkeypatch, tmp_path):
    monkeypatch.setenv("SASSY_OUT", str(tmp_path))
    assert ds.shop_out() == tmp_path


def test_summary_goes_to_shop_out_not_cwd(tmp_path, monkeypatch, capsys):
    shop = tmp_path / "shop-out"
    monkeypatch.setenv("SASSY_OUT", str(shop))
    cwd = _run(tmp_path, monkeypatch)
    out = shop / "summaries" / "daily-summary-2000-01-01.md"
    assert out.exists()
    assert not (cwd / "out").exists()
    assert f"wrote {out}" in capsys.readouterr().out


def test_out_dir_override_wins(tmp_path, monkeypatch):
    shop = tmp_path / "shop-out"
    monkeypatch.setenv("SASSY_OUT", str(shop))
    alt = tmp_path / "alt"
    _run(tmp_path, monkeypatch, ["--out-dir", str(alt)])
    assert (alt / "daily-summary-2000-01-01.md").exists()
    assert not (shop / "summaries").exists()


def test_runner_exports_sassy_out_and_prints_path():
    sh = (HERE / "run_daily_summary.sh").read_text()
    assert 'SASSY_OUT="${SASSY_OUT:-/workspace/sassy-closet/out}"' in sh
    assert "export SASSY_OUT" in sh and "echo" in sh


def test_reports_follow_root_not_cwd():
    # reports already resolve from --root (default /workspace/sassy-closet), not cwd
    src = (HERE / "boss_decisions.py").read_text()
    assert 'r / "out/reports" / d' in src
