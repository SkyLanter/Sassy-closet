"""The freshness report must count the intake's own photo list.

An intake submission keeps its photos in ``photo_paths`` (see
``sassy-closet/lib/types.ts`` and the CSV export). ``_photo_field`` only
looked at ``photo_count`` and the catalog key names, so every real intake
row was read as having no photos. The pickup plan then held the row with
``missing_photos`` and the report listed a photo gap that was not there.
"""

from __future__ import annotations

import json

import freshness_check as f

INTAKE_ROW = {
    "ma": "A31",
    "kind": "A",
    "size": "M",
    "sell_usd": "",
    "photo_paths": ["A31/001.jpg", "A31/002.jpg"],
    "photo_hashes": ["a" * 64, "b" * 64],
    "created_at": "2026-11-20T00:00:00Z",
}


def test_intake_photo_paths_are_counted():
    assert f._photo_field({"photo_paths": ["A31/001.jpg", "A31/002.jpg"]}) == 2
    assert f._photo_field({"photo_paths": []}) == 0
    assert f._photo_field({"photo_paths": ["A31/001.jpg", " ", ""]}) == 1


def test_photo_count_wins_over_the_list():
    assert f._photo_field({"photo_count": 3, "photo_paths": ["a.jpg"]}) == 3
    assert f._photo_field({"photo_count": 0, "photo_paths": ["a.jpg"]}) == 0


def test_photo_paths_must_be_a_list():
    assert f._photo_field({"photo_paths": "A31/001.jpg"}) is None
    assert f._photo_field({"photo_paths": None}) is None


def test_intake_row_with_photos_is_not_held_for_a_photo_gap():
    snapshot = f.snapshot_from_json(
        {
            "day": "2026-11-26",
            "origins": ["https://sassycloset.vercel.app"],
            "intake": [INTAKE_ROW],
            "blob": {"state": "skip"},
            "hub": {"state": "skip"},
            "pdp": {},
            "taobao": [],
        }
    )
    assert snapshot.intake[0].photo_count == 2
    decisions = f.plan_pickups(f.intake_pickup_events(snapshot), f.load_held_policy())
    assert [decision.ma for decision in decisions] == ["A31"]
    assert "missing_photos" not in decisions[0].flags
    kinds = [flag.kind for flag in f.evaluate(snapshot).flags if flag.ma == "A31"]
    assert "missing_photos" not in kinds


def test_live_fetch_reads_the_same_size_and_photo_fields_as_the_fixture(monkeypatch):
    body = {"submissions": [INTAKE_ROW]}
    monkeypatch.setattr(f, "_http_get", lambda url, timeout=20: (200, json.dumps(body), None))
    rows, state = f._fetch_intake()
    assert state.state == "ok"
    assert rows[0].sizes == ("M",)
    assert rows[0].photo_count == 2
    from_fixture = f._intake_from_json([INTAKE_ROW])[0]
    assert rows[0] == from_fixture
