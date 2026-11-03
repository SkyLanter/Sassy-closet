"""Placeholder tests for piece 86: --defaults mode and 'Generated with' footer."""
import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import daily_summary_draft as ds  # noqa: E402


def _ns(**kw):
    base = {k: None for k in ds.PATH_FLAGS}
    base.update(date="2000-01-01", root=Path("/tmp/root"), out_dir=Path("out/summaries"))
    base.update(kw)
    return argparse.Namespace(**base)


def test_today_pt_crosses_midnight_utc():
    now = dt.datetime(2026, 10, 23, 3, 0, tzinfo=dt.timezone.utc)  # 20:00 PT on 10-22
    assert ds.today_pt(now) == "2026-10-22"


def test_defaults_resolve_from_repo(tmp_path):
    a = ds.apply_defaults(_ns(), [], repo=tmp_path,
                          now=dt.datetime(2026, 10, 22, 17, 0, tzinfo=dt.timezone.utc))
    assert a.date == "2026-10-22"
    assert a.order == tmp_path / "sassy-closet-shop/data/popular-order.json"
    assert a.held == tmp_path / "data/held.json"


def test_explicit_flags_win(tmp_path):
    a = ds.apply_defaults(_ns(date="2026-01-02", order=Path("/x/o.json")),
                          ["--date", "2026-01-02", "--order", "/x/o.json"], repo=tmp_path)
    assert a.date == "2026-01-02" and a.order == Path("/x/o.json")
    assert a.held == tmp_path / "data/held.json"


def test_generated_with_paths_only():
    cmd = ds.generated_with(_ns(order=Path("/r/o.json"), held=Path("/r/h.json")))
    assert cmd.startswith(str(Path(ds.__file__).resolve()))
    assert "--date 2000-01-01" in cmd and "--order /r/o.json" in cmd and "--held /r/h.json" in cmd
    assert "--qc" not in cmd and "http" not in cmd and "@" not in cmd


def test_footer_is_last_line():
    out = ds.add_footer("body\n- Mini Boss\n", "x --date 2000-01-01")
    assert out.endswith("\n\nGenerated with: x --date 2000-01-01\n")
    assert out.startswith("body\n- Mini Boss\n")


def test_runner_script_uses_defaults():
    sh = (Path(ds.__file__).resolve().parent / "run_daily_summary.sh").read_text()
    assert "--defaults" in sh and "daily_summary_draft.py" in sh
