"""Piece 178: the default report date is the Pacific shop day, not the UTC day.

After 5 PM PDT (4 PM PST) the UTC date is already tomorrow, so an evening run
was stamped and filed under the next day.
"""
import json
from datetime import datetime, timezone

import pytest

import freshness_check
from test_freshness_check import _passing_payload


def _fake_now(instant):
    class FakeDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return instant if tz is None else instant.astimezone(tz)
    return FakeDatetime


@pytest.mark.parametrize("utc, pt_day", [
    (datetime(2026, 10, 29, 1, 30, tzinfo=timezone.utc), "2026-10-28"),  # 6:30 PM PDT
    (datetime(2026, 12, 1, 7, 30, tzinfo=timezone.utc), "2026-11-30"),   # 11:30 PM PST
    (datetime(2026, 10, 28, 18, 0, tzinfo=timezone.utc), "2026-10-28"),  # same day both zones
])
def test_default_date_is_pacific_day(tmp_path, monkeypatch, utc, pt_day):
    monkeypatch.setattr(freshness_check, "datetime", _fake_now(utc))
    fixture = tmp_path / "pass.json"
    fixture.write_text(json.dumps(_passing_payload()), encoding="utf-8")
    out = tmp_path / "out"
    assert freshness_check.main(["--fixture", str(fixture), "--out", str(out)]) == 0
    assert sorted(p.name for p in out.glob("dataset-freshness-*.md")) == [f"dataset-freshness-{pt_day}.md"]
