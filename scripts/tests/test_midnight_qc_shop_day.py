"""Default midnight QC --date is the Pacific shop day. An explicit --date wins.

UTC is already the next calendar day at 5:00 PM PDT and 4:00 PM PST. The
12:00 AM PT run files that same Pacific day (which matches the UTC date then).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

import midnight_qc
from test_midnight_qc import ROOT, _passing_payload

PT = ZoneInfo("America/Los_Angeles")

HELD_BYTES = (ROOT / "data" / "held.json").read_bytes()

# (UTC instant, Pacific shop day)
CLOCKS = [
    pytest.param(datetime(2026, 7, 16, 0, 0, tzinfo=timezone.utc), "2026-07-15", id="5pm-pdt"),
    pytest.param(datetime(2026, 12, 16, 0, 0, tzinfo=timezone.utc), "2026-12-15", id="4pm-pst"),
    pytest.param(datetime(2026, 7, 16, 6, 59, 59, tzinfo=timezone.utc), "2026-07-15", id="before-midnight-pdt"),
    pytest.param(datetime(2026, 7, 16, 7, 0, tzinfo=timezone.utc), "2026-07-16", id="midnight-pdt"),
    pytest.param(datetime(2026, 12, 16, 7, 59, 59, tzinfo=timezone.utc), "2026-12-15", id="before-midnight-pst"),
    pytest.param(datetime(2026, 12, 16, 8, 0, tzinfo=timezone.utc), "2026-12-16", id="midnight-pst"),
    pytest.param(datetime(2026, 3, 8, 9, 59, 59, tzinfo=timezone.utc), "2026-03-08", id="dst-start-before"),
    pytest.param(datetime(2026, 3, 8, 10, 0, tzinfo=timezone.utc), "2026-03-08", id="dst-start-after"),
    pytest.param(datetime(2026, 11, 1, 0, 0, tzinfo=timezone.utc), "2026-10-31", id="last-5pm-pdt"),
    pytest.param(datetime(2026, 11, 1, 8, 30, tzinfo=timezone.utc), "2026-11-01", id="dst-end-first-130"),
    pytest.param(datetime(2026, 11, 1, 9, 30, tzinfo=timezone.utc), "2026-11-01", id="dst-end-second-130"),
    pytest.param(datetime(2026, 11, 2, 0, 0, tzinfo=timezone.utc), "2026-11-01", id="first-4pm-pst"),
]


def _fake_now(instant: datetime):
    class FakeDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return instant if tz is None else instant.astimezone(tz)

    return FakeDatetime


@pytest.mark.parametrize("utc, pt_day", CLOCKS)
def test_default_files_the_pacific_day(tmp_path, monkeypatch, utc, pt_day) -> None:
    monkeypatch.setattr(midnight_qc, "datetime", _fake_now(utc))
    monkeypatch.chdir(tmp_path)
    fixture = tmp_path / "night.json"
    fixture.write_text(json.dumps(_passing_payload()), encoding="utf-8")
    assert midnight_qc.today_pt() == pt_day
    assert midnight_qc.main(["--fixture", str(fixture)]) == 0
    report = tmp_path / "out" / "midnight-qc" / pt_day
    summary = json.loads((report / "summary.json").read_text(encoding="utf-8"))
    assert summary["date"] == pt_day
    assert summary["timezone"] == "America/Los_Angeles"
    assert summary["s06Usd"] == 25
    assert f"Midnight QC {pt_day}" in (report / "data-ok.md").read_text(encoding="utf-8")
    utc_day = utc.date().isoformat()
    if utc_day != pt_day:
        assert not (tmp_path / "out" / "midnight-qc" / utc_day).exists()
    assert (ROOT / "data" / "held.json").read_bytes() == HELD_BYTES


@pytest.mark.parametrize(
    "utc",
    [
        datetime(2026, 7, 16, 7, 0, tzinfo=timezone.utc),  # 12:00 AM PDT
        datetime(2026, 12, 16, 8, 0, tzinfo=timezone.utc),  # 12:00 AM PST
    ],
)
def test_midnight_run_files_that_pacific_day(tmp_path, monkeypatch, utc) -> None:
    monkeypatch.setattr(midnight_qc, "datetime", _fake_now(utc))
    monkeypatch.chdir(tmp_path)
    fixture = tmp_path / "night.json"
    fixture.write_text(json.dumps(_passing_payload()), encoding="utf-8")
    pt_day = utc.astimezone(PT).date().isoformat()
    assert pt_day == utc.date().isoformat()
    assert midnight_qc.main(["--fixture", str(fixture)]) == 0
    assert (tmp_path / "out" / "midnight-qc" / pt_day / "summary.json").is_file()
    assert list((tmp_path / "out" / "midnight-qc").iterdir()) == [tmp_path / "out" / "midnight-qc" / pt_day]


def test_explicit_date_wins_over_pacific_default(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        midnight_qc,
        "datetime",
        _fake_now(datetime(2026, 7, 16, 0, 0, tzinfo=timezone.utc)),
    )
    monkeypatch.chdir(tmp_path)
    fixture = tmp_path / "night.json"
    fixture.write_text(json.dumps(_passing_payload()), encoding="utf-8")
    assert midnight_qc.main(["--fixture", str(fixture), "--date", "2026-01-02"]) == 0
    summary = json.loads(
        (tmp_path / "out" / "midnight-qc" / "2026-01-02" / "summary.json").read_text(encoding="utf-8")
    )
    assert summary["date"] == "2026-01-02"
    assert summary["s06Usd"] == 25
    assert not (tmp_path / "out" / "midnight-qc" / "2026-07-15").exists()
    assert not (tmp_path / "out" / "midnight-qc" / "2026-07-16").exists()
    assert (ROOT / "data" / "held.json").read_bytes() == HELD_BYTES
