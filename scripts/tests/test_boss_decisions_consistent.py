"""Placeholder tests for piece 93: consistent defaults, inputs header, overwrite guard."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import boss_decisions as bd  # noqa: E402
import daily_summary_draft as ds  # noqa: E402

DIG = "- [price_approval] X01  first_seen=2000-01-01  source=out/qc/a.md\n"


def _main(tmp_path, *extra):
    dg = tmp_path / "dig.txt"; dg.write_text(DIG)
    return bd.main(["--date", "2000-01-05", "--root", str(tmp_path), "--digest", str(dg),
                    "--out-dir", str(tmp_path / "o"), *extra])


def test_render_header_has_inputs_and_total():
    D = [{"ma": "X01", "q": "q", "ev": "e", "days": None, "since": None}]
    t = bd.render(D, "2000-01-05", "date=2000-01-05 order=-")
    assert "Inputs: date=2000-01-05 order=- | total=1" in t
    assert bd.INPUTS_LINE.search(t).group(2) == "1"


def test_bare_run_uses_summary_defaults(tmp_path):
    assert _main(tmp_path) == 0
    got = bd.existing_inputs(tmp_path / "o/BOSS-DECISIONS.md")
    for k, v in ds.default_paths().items():
        assert f"{k}={bd.neutral_path(tmp_path, v)}@{bd.sha12(v)}" in got  # piece 94


def test_same_inputs_rerun_ok(tmp_path):
    assert _main(tmp_path) == 0
    assert _main(tmp_path) == 0


def test_different_inputs_refused_without_force(tmp_path):
    assert _main(tmp_path) == 0
    before = (tmp_path / "o/BOSS-DECISIONS.md").read_text()
    assert _main(tmp_path, "--no-defaults") == 2
    assert (tmp_path / "o/BOSS-DECISIONS.md").read_text() == before
    assert _main(tmp_path, "--no-defaults", "--force") == 0
    assert "order=-" in bd.existing_inputs(tmp_path / "o/BOSS-DECISIONS.md")


def test_pre93_file_refused(tmp_path):
    o = tmp_path / "o"; o.mkdir()
    (o / "BOSS-DECISIONS.md").write_text("# old\n\nTOTAL 0\n")
    assert bd.existing_inputs(o / "BOSS-DECISIONS.md") == ""
    assert _main(tmp_path) == 2


def test_runner_calls_boss_decisions_before_summary():
    s = (Path(bd.__file__).parent / "run_daily_summary.sh").read_text()
    assert s.index("boss_decisions.py") < s.index("daily_summary_draft.py\" --defaults")
