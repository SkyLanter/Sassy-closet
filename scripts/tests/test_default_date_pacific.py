"""Piece 180: default --date is the Pacific shop day even on a UTC host.

Fake clock: a host on UTC at 01:30Z on 2026-10-29 (6:30 PM PDT on 2026-10-28).
date.today() there says 10-29; the shop day is 10-28.
"""
import argparse
import datetime as real_dt
import json

import pytest

INSTANT = real_dt.datetime(2026, 10, 29, 1, 30, tzinfo=real_dt.timezone.utc)
PT_DAY = "2026-10-28"


class FakeDate(real_dt.date):
    @classmethod
    def today(cls):
        return real_dt.date(2026, 10, 29)  # UTC host's local date


class FakeDatetime(real_dt.datetime):
    @classmethod
    def now(cls, tz=None):
        return INSTANT.replace(tzinfo=None) if tz is None else INSTANT.astimezone(tz)


class Parsed(Exception):
    pass


@pytest.fixture
def utc_host(monkeypatch):
    monkeypatch.setattr(real_dt, "date", FakeDate)
    monkeypatch.setattr(real_dt, "datetime", FakeDatetime)


@pytest.fixture
def capture(monkeypatch):
    seen = {}
    orig = argparse.ArgumentParser.parse_args

    def fake(self, *a, **k):
        ns = orig(self, *a, **k)
        seen["date"] = ns.date
        raise Parsed

    monkeypatch.setattr(argparse.ArgumentParser, "parse_args", fake)
    return seen


def _default(module, argv, capture):
    with pytest.raises(Parsed):
        module.main(argv)
    return capture["date"]


def test_daily_summary_draft(utc_host, capture):
    import daily_summary_draft as m
    assert _default(m, [], capture) == PT_DAY


def test_run_shop_drafts(utc_host, capture):
    import run_shop_drafts as m
    assert _default(m, [], capture) == PT_DAY


def test_cost_basis_reconcile(utc_host, capture, monkeypatch):
    import cost_basis_reconcile as m
    monkeypatch.setattr(m, "date", FakeDate, raising=False)
    assert _default(m, ["--live", "x.json", "--intake", "y.csv"], capture) == PT_DAY


def test_held_price_proposal(utc_host, tmp_path):
    import held_price_proposal as m
    intake = tmp_path / "i.json"
    intake.write_text("[]")
    live = tmp_path / "l.json"
    live.write_text(json.dumps({"prices": {}}))
    held = tmp_path / "held.json"
    held.write_text(json.dumps({"heldIncomplete": ["K03"], "neverList": []}))
    out = tmp_path / "p"
    assert m.main(["--intake", str(intake), "--live", str(live), "--held", str(held),
                   "--proposal-dir", str(out)]) == 0
    assert sorted(p.name for p in out.iterdir()) == [
        f"held-price-proposal-{PT_DAY}.json", f"held-price-proposal-{PT_DAY}.md"]
