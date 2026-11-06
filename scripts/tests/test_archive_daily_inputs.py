"""Placeholder tests for piece 92: dated input archive (box only) + first-seen from archive."""
import io
import os
import subprocess
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import archive_daily_inputs as ar  # noqa: E402
import boss_decisions as bd  # noqa: E402
import privacy_scan as ps  # noqa: E402

D = "2000-01-02"


def _root(tmp_path):
    (tmp_path / "out/reports" / D).mkdir(parents=True)
    (tmp_path / "out/reports" / D / "COST-BASIS.md").write_text("placeholder\n")
    (tmp_path / "out/reports" / D / "BOSS-DECISIONS.md").write_text("- Z99 | Q? | x | ?\n")
    (tmp_path / "out/midnight-qc" / D).mkdir(parents=True)
    (tmp_path / "out/midnight-qc" / D / "summary.md").write_text("placeholder\n")
    (tmp_path / "out/muse").mkdir(parents=True)
    (tmp_path / "out/muse/TODAY.md").write_text("placeholder\n")
    order = tmp_path / "order.json"
    order.write_text("[]\n")
    return order


def test_archive_copies_present_and_reports_missing(tmp_path):
    order = _root(tmp_path)
    res = dict((n, s) for s, n in ar.archive(tmp_path, D, order))
    assert res["COST-BASIS.md"] == "copied"
    assert res["popular-order.json"] == "copied"
    assert res["muse/TODAY.md"] == "copied"
    assert res["midnight-qc-summary.json"] == "missing"
    assert (tmp_path / "out/archive" / D / "BOSS-DECISIONS.md").is_file()


def test_archive_never_overwrites_without_force(tmp_path):
    order = _root(tmp_path)
    ar.archive(tmp_path, D, order)
    kept = tmp_path / "out/archive" / D / "COST-BASIS.md"
    kept.write_text("older\n")
    assert ("kept", "COST-BASIS.md") in ar.archive(tmp_path, D, order)
    assert kept.read_text() == "older\n"
    assert ("overwritten", "COST-BASIS.md") in ar.archive(tmp_path, D, order, force=True)
    assert kept.read_text() == "placeholder\n"


def test_first_seen_from_archive(tmp_path):
    a = tmp_path / "out/archive/2000-01-01"
    a.mkdir(parents=True)
    (a / "BOSS-DECISIONS.md").write_text("- Z99 | Q? | x | ?\n- Z98 | Other | x | ?\n")
    future = tmp_path / "out/archive/2000-01-09"
    future.mkdir(parents=True)
    (future / "BOSS-DECISIONS.md").write_text("- Z97 | Q? | x | ?\n")
    Dl = [{"ma": "Z99", "q": "Q?", "since": None, "days": None},
          {"ma": "Z98", "q": "Q?", "since": D, "days": 0},
          {"ma": "Z97", "q": "Q?", "since": None, "days": None}]
    bd.apply_archive(Dl, tmp_path, D)
    assert (Dl[0]["since"], Dl[0]["days"]) == ("2000-01-01", 1)
    assert Dl[1]["days"] == 0  # different question
    assert Dl[2]["since"] is None  # archive dated after D is ignored


def test_privacy_scan_blocks_archive_in_bundle_dir(tmp_path):
    p = tmp_path / "bundle/out/archive" / D
    p.mkdir(parents=True)
    (p / "x.md").write_text("placeholder\n")
    hits = ps.scan_path(str(tmp_path / "bundle"), [])
    assert [h.rule for h in hits] == ["archive_path"]


def test_privacy_scan_blocks_archive_in_tar_and_patch(tmp_path):
    t = tmp_path / "b.tgz"
    patch = b"+++ b/out/archive/2000-01-02/x.md\n@@ -0,0 +1 @@\n+placeholder\n"
    with tarfile.open(t, "w:gz") as tf:
        for name, data in (("92/out/archive/x.md", b"p\n"), ("92/patches/0001.patch", patch)):
            ti = tarfile.TarInfo(name)
            ti.size = len(data)
            tf.addfile(ti, io.BytesIO(data))
    rules = sorted(h.rule for h in ps.scan_path(str(t), []))
    assert rules == ["archive_path", "archive_path"]


def test_privacy_scan_ignores_archive_mentions_in_text(tmp_path):
    (tmp_path / "notes.md").write_text("archive lives at out/archive/<date>/\n")
    assert ps.scan_path(str(tmp_path), []) == []


def test_second_pass_keeps_the_first_snapshot_and_copies_new_boss_decisions(tmp_path):
    """The daily runner archives, writes BOSS-DECISIONS.md, then archives again."""
    order = _root(tmp_path)
    report = tmp_path / "out/reports" / D / "BOSS-DECISIONS.md"
    report.unlink()
    first = dict((n, s) for s, n in ar.archive(tmp_path, D, order))
    assert first["BOSS-DECISIONS.md"] == "missing"
    assert first["COST-BASIS.md"] == "copied"
    report.write_text("- Z99 | Q? | x | ?\n")
    (tmp_path / "out/reports" / D / "COST-BASIS.md").write_text("newer\n")
    second = dict((n, s) for s, n in ar.archive(tmp_path, D, order))
    assert second["BOSS-DECISIONS.md"] == "copied"
    assert second["COST-BASIS.md"] == "kept"
    archived = tmp_path / "out/archive" / D
    assert (archived / "BOSS-DECISIONS.md").read_text() == "- Z99 | Q? | x | ?\n"
    assert (archived / "COST-BASIS.md").read_text() == "placeholder\n"
    nxt = [{"ma": "Z99", "q": "Q?", "since": None, "days": None}]
    bd.apply_archive(nxt, tmp_path, "2000-01-03")
    assert (nxt[0]["since"], nxt[0]["days"]) == (D, 1)


def test_runner_archives_again_after_boss_decisions_on_the_same_date(tmp_path):
    log = tmp_path / "calls.log"
    stub = tmp_path / "py"
    stub.write_text("#!/bin/sh\n" f"printf '%s\\n' \"$*\" >> {str(log)!r}\n" "exit 0\n")
    stub.chmod(0o755)
    runner = Path(__file__).resolve().parents[1] / "run_daily_summary.sh"
    env = {k: v for k, v in os.environ.items() if k != "NO_ARCHIVE"}
    env["PYTHON"] = str(stub)
    ran = subprocess.run(
        ["bash", str(runner), "--date", "2026-10-22"],
        env=env, capture_output=True, text=True, check=False,
    )
    assert ran.returncode == 0, ran.stderr
    lines = [ln for ln in log.read_text().splitlines() if ln.strip()]
    names = [Path(ln.split()[0]).name for ln in lines]
    assert names == [
        "archive_daily_inputs.py",
        "boss_decisions.py",
        "archive_daily_inputs.py",
        "daily_summary_draft.py",
    ]
    assert lines[0].endswith("archive_daily_inputs.py --date 2026-10-22")
    assert "--date 2026-10-22" in lines[1]
    assert lines[2].endswith("archive_daily_inputs.py --date 2026-10-22")
    assert lines[3].endswith("daily_summary_draft.py --defaults --date 2026-10-22")


def test_runner_skips_both_archives_when_asked(tmp_path):
    log = tmp_path / "calls.log"
    stub = tmp_path / "py"
    stub.write_text("#!/bin/sh\n" f"printf '%s\\n' \"$*\" >> {str(log)!r}\n" "exit 0\n")
    stub.chmod(0o755)
    runner = Path(__file__).resolve().parents[1] / "run_daily_summary.sh"
    env = dict(os.environ)
    env["PYTHON"] = str(stub)
    env["NO_ARCHIVE"] = "1"
    ran = subprocess.run(
        ["bash", str(runner), "--date=2000-01-02"],
        env=env, capture_output=True, text=True, check=False,
    )
    assert ran.returncode == 0, ran.stderr
    names = [Path(ln.split()[0]).name for ln in log.read_text().splitlines() if ln.strip()]
    assert names == ["boss_decisions.py", "daily_summary_draft.py"]
    assert "archive_daily_inputs.py" not in log.read_text()


def test_same_day_archive_adds_no_history(tmp_path):
    a = tmp_path / "out/archive" / D
    a.mkdir(parents=True)
    (a / "BOSS-DECISIONS.md").write_text("- Z99 | Q? | x | ?\n")
    Dl = [{"ma": "Z99", "q": "Q?", "since": None, "days": None}]
    bd.apply_archive(Dl, tmp_path, D)
    assert Dl[0]["since"] is None
