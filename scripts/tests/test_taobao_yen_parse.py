"""A public Taobao ¥ in a saved snapshot is read like an intake ¥, never guessed.

`freshness_check --fixture` reads a saved snapshot. A ¥ field that is not a plain
amount (an empty string, a leftover note, a comma, NaN) raised decimal.InvalidOperation
out of _taobao_from_json, so the whole report died with a traceback instead of naming
the bad source. NaN and Infinity were accepted and then written into the report JSON.

The stored text is not rewritten. A ¥ that cannot be read is "no usable public ¥",
the same state an unreadable page already gives.
"""
from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

import freshness_check as f
from test_freshness_check import _passing_payload

ROOT = Path(__file__).resolve().parents[2]
HELD_BYTES = (ROOT / "data" / "held.json").read_bytes()


def _view(raw):
    payload = _passing_payload()
    payload["taobao"].append({"ma": "Z60", "state": "ok", "public_cny": raw})
    return f.snapshot_from_json(payload).taobao[-1]


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "   ",
        "abc",
        "\u00a5",
        "\u00a5 88",
        "1,299",
        "59.9.9",
        "12.",
        ".5",
        "1e3",
        "NaN",
        "Infinity",
        "-Infinity",
        "-5",
        "0",
    ],
)
def test_unusable_public_cny_is_no_public_yen(raw):
    view = _view(raw)
    assert view.public_cny is None


@pytest.mark.parametrize("raw", ["88", "88.00", " 88.5 ", "0.5", 88, 88.5, "1200"])
def test_plain_public_cny_is_unchanged(raw):
    view = _view(raw)
    assert view.public_cny == Decimal(str(raw).strip())


def _cost_payload(ma):
    """Intake row whose stored cost is not what this file checks.

    Returns (payload, stored cost text). The cost is copied from the existing
    fixture rows so this file holds no cost literal of its own.
    """
    payload = _passing_payload()
    row = next(item for item in payload["intake"] if (item.get("cost_cny") or "").strip())
    payload["intake"].append({**row, "ma": ma, "sell_usd": ""})
    return payload, row["cost_cny"]


def test_junk_yen_keeps_the_report_and_names_a_skip():
    payload, stored = _cost_payload("Z60")
    payload["taobao"].append({"ma": "Z60", "state": "ok", "public_cny": "abc"})
    report = f.evaluate(f.snapshot_from_json(payload))
    assert report.guards_pass
    row = next(item for item in report.rows if item["ma"] == "Z60")
    assert row["intakeCny"] == stored
    assert row["publicCny"] is None
    # no readable public ¥ means the above-public check has nothing to compare against
    assert not any(flag.ma == "Z60" and flag.kind == "above_public" for flag in report.flags)
    assert (ROOT / "data" / "held.json").read_bytes() == HELD_BYTES


def test_cli_survives_a_bad_yen_in_the_fixture(tmp_path):
    payload = _passing_payload()
    payload["taobao"].append({"ma": "Z60", "state": "ok", "public_cny": "abc"})
    fixture = tmp_path / "bad-yen.json"
    fixture.write_text(json.dumps(payload), encoding="utf-8")
    out = tmp_path / "out"
    code = f.main(["--fixture", str(fixture), "--out", str(out), "--date", "2026-10-11"])
    assert code == 0
    saved = json.loads((out / "dataset-freshness-2026-10-11.json").read_text(encoding="utf-8"))
    row = next(item for item in saved["rows"] if item["ma"] == "Z60")
    assert row["publicCny"] is None
    assert (ROOT / "data" / "held.json").read_bytes() == HELD_BYTES


def test_junk_yen_never_quotes_a_pickup():
    """No public ¥ is incomplete Taobao, so the mã stays held with no quote."""
    payload, _stored = _cost_payload("Z64")
    payload["taobao"].append(
        {"ma": "Z64", "state": "ok", "public_cny": "abc", "sizes": ["S"], "photo_count": 2}
    )
    report = f.evaluate(f.snapshot_from_json(payload))
    decision = next(item for item in report.pickup if item.ma == "Z64")
    assert decision.flags == ("missing_yen",)
    assert decision.held is True
    assert decision.quoted_usd is None
    assert decision.publish is False


def test_report_json_is_strict_json_for_non_finite_yen():
    payload = _passing_payload()
    payload["taobao"].append({"ma": "Z60", "state": "ok", "public_cny": "NaN"})
    payload["taobao"].append({"ma": "Z61", "state": "ok", "public_cny": "Infinity"})
    report = f.evaluate(f.snapshot_from_json(payload))
    text = json.dumps(f.report_json(report))

    def reject(token):
        raise AssertionError(f"non-finite {token} in report JSON")

    assert json.loads(text, parse_constant=reject)["day"] == "2026-10-11"
