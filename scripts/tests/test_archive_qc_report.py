"""The daily archive must copy the midnight QC report the QC run really writes.

`midnight_qc.py` writes `data-ok.md` next to `summary.json`; there is no
`summary.md` in that folder. The archive looked for `summary.md`, so every
archived day kept the QC JSON and silently reported the readable QC verdict as
`missing` — the dated copy lost the one file a reader opens.
"""

from __future__ import annotations

import json
from pathlib import Path

import archive_daily_inputs as ar
import midnight_qc as mq

DAY = "2026-11-26"
QC_FIXTURE = {
    "day": DAY,
    "checkedAt": f"{DAY}T09:00:00Z",
    "origins": ["https://sassycloset.vercel.app", "https://sassy-closet-shop.vercel.app"],
    "blob": {"state": "skip"},
    "hub": {"state": "skip"},
    "intake": [],
}


def _qc_run(tmp_path: Path) -> Path:
    """Run the real midnight QC so the test never assumes its output names."""
    fixture = tmp_path / "night.json"
    fixture.write_text(json.dumps(QC_FIXTURE), encoding="utf-8")
    out = tmp_path / "out/midnight-qc" / DAY
    mq.main(["--date", DAY, "--out", str(out), "--fixture", str(fixture)])
    return out


def test_archive_copies_the_qc_report_midnight_qc_writes(tmp_path: Path) -> None:
    qc = _qc_run(tmp_path)
    report = next((p for p in qc.iterdir() if p.suffix == ".md"), None)
    assert report is not None, sorted(p.name for p in qc.iterdir())

    res = dict((name, status) for status, name in ar.archive(tmp_path, DAY, tmp_path / "order.json"))
    assert res["midnight-qc-summary.md"] == "copied"
    assert res["midnight-qc-summary.json"] == "copied"
    archived = tmp_path / "out/archive" / DAY
    assert (archived / "midnight-qc-summary.md").read_text() == report.read_text()


def test_qc_sources_point_at_files_that_can_exist(tmp_path: Path) -> None:
    names = [name for _src, name in ar.sources(tmp_path, DAY)]
    srcs = {name: src for src, name in ar.sources(tmp_path, DAY)}
    assert srcs["midnight-qc-summary.md"].name == "data-ok.md"
    assert "midnight-qc-summary.md" in names
