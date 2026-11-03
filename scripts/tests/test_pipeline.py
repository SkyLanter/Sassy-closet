"""Dry-run pickup, Taobao mode, and Meta fixtures. No live writes."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import freshness_check
from autolist import listing_quote
from freshness_check import classify_taobao, evaluate, main, snapshot_from_json
from pickup import landed_usd_from_cny
from test_freshness_check import _passing_payload

ROOT = Path(__file__).resolve().parents[2]
HELD_BYTES = (ROOT / "data" / "held.json").read_bytes()


def _complete(ma: str = "Z99", **overrides: object) -> dict[str, object]:
    event: dict[str, object] = {
        "ma": ma,
        "via": "webhook",
        "action": "create",
        "cost_cny": "80",
        "landed_usd": "16.25",
        "sizes": ["S"],
        "photo_count": 2,
        "public_cny": "59.9",
        "taobao_state": "ok",
        "boss_approved": False,
    }
    event.update(overrides)
    return event


def _report(pickup: list[dict[str, object]] | None = None, **extra: object):
    payload = _passing_payload()
    if pickup is not None:
        payload["pickup"] = pickup
    payload.update(extra)
    return evaluate(snapshot_from_json(payload)), payload


def test_held_file_is_not_rewritten() -> None:
    _report([_complete()])
    assert (ROOT / "data" / "held.json").read_bytes() == HELD_BYTES


def test_new_ma_is_quoted_held_and_not_published() -> None:
    for via in ("webhook", "poll"):
        report, payload = _report([_complete(via=via)])
        assert payload["intake"][0]["cost_cny"] == ""
        decision = report.pickup[0]
        assert decision.ma == "Z99"
        assert decision.via == via
        assert decision.held is True
        assert decision.live is False
        assert decision.publish is False
        assert decision.quoted_usd == 25
        assert decision.flags == ("boss_approval",)
        assert decision.stored_cny == "80"
        assert report.guards_pass
        assert (ROOT / "data" / "held.json").read_bytes() == HELD_BYTES


def test_unapproved_ma_on_blob_fails() -> None:
    payload = _passing_payload()
    payload["blob"]["rows"].append({"ma": "Z99", "price_usd": "25"})
    payload["pickup"] = [_complete()]
    report = evaluate(snapshot_from_json(payload))
    assert report.guards_pass is False
    assert report.pickup[0].publish is False
    assert any(guard.name == "off-live:Z99" and not guard.ok for guard in report.guards)


def test_boss_yes_still_does_not_publish() -> None:
    report, _payload = _report([_complete(boss_approved=True)])
    decision = report.pickup[0]
    assert decision.held is False
    assert decision.live is False
    assert decision.publish is False
    assert decision.quoted_usd == 25
    assert decision.flags == ()


def test_incomplete_taobao_is_held_and_not_quoted() -> None:
    events = [
        _complete("Z91", sizes=[]),
        _complete("Z92", photo_count=0),
        _complete("Z93", public_cny=None, taobao_state="ok"),
    ]
    report, _payload = _report(events)
    by_ma = {decision.ma: decision for decision in report.pickup}
    assert by_ma["Z91"].flags == ("missing_size",)
    assert by_ma["Z92"].flags == ("missing_photos",)
    assert by_ma["Z93"].flags == ("missing_yen",)
    for decision in report.pickup:
        assert decision.held is True
        assert decision.quoted_usd is None
        assert decision.live is False
        assert decision.publish is False
    assert report.guards_pass

    walled, _payload = _report(
        [_complete("Z94", public_cny=None, taobao_state="skip", detail="login-walled or unreachable")]
    )
    assert walled.pickup[0].flags == ("boss_approval",)
    assert "missing_yen" not in walled.pickup[0].flags
    assert walled.pickup[0].quoted_usd == 25


def test_incomplete_ma_on_blob_fails() -> None:
    payload = _passing_payload()
    payload["blob"]["rows"].append({"ma": "Z91", "price_usd": "25"})
    payload["pickup"] = [_complete("Z91", sizes=[])]
    report = evaluate(snapshot_from_json(payload))
    assert report.guards_pass is False
    assert report.pickup[0].quoted_usd is None
    assert any(guard.name == "off-live:Z91" and not guard.ok for guard in report.guards)


def test_logged_out_keeps_public_list_and_login_flags_promo() -> None:
    payload = _passing_payload()
    payload["intake"].append({"ma": "Z99", "cost_cny": "80", "sell_usd": ""})
    payload["taobao"].append(
        {
            "ma": "Z99",
            "state": "ok",
            "public_cny": "59.9",
            "promo_cny": "10",
            "final_cny": "9",
        }
    )
    payload["pickup"] = [_complete()]
    logged_out = evaluate(snapshot_from_json(payload))
    assert not any(flag.kind in {"promo_cny", "final_cny"} for flag in logged_out.flags)
    assert logged_out.pickup[0].quoted_usd == 25
    assert logged_out.pickup[0].stored_cny == "80"

    payload["taobaoMode"] = "login"
    logged_in = evaluate(snapshot_from_json(payload))
    promo = [flag for flag in logged_in.flags if flag.ma == "Z99" and flag.kind == "promo_cny"]
    final = [flag for flag in logged_in.flags if flag.ma == "Z99" and flag.kind == "final_cny"]
    assert len(promo) == 1 and promo[0].stored == "80" and promo[0].public_cny == "10"
    assert len(final) == 1 and final[0].stored == "80" and final[0].public_cny == "9"
    assert logged_in.pickup[0].quoted_usd == 25
    row = next(item for item in logged_in.rows if item["ma"] == "Z99")
    assert row["intakeCny"] == "80"


def test_mode_flag_and_env(tmp_path: Path) -> None:
    fixture = tmp_path / "snap.json"
    payload = _passing_payload()
    payload["taobao"].append(
        {"ma": "S06", "state": "ok", "public_cny": "59.9", "promo_cny": "40", "final_cny": "39"}
    )
    original = json.dumps(payload)
    fixture.write_text(original, encoding="utf-8")
    out = tmp_path / "out"
    base = [
        sys.executable,
        str(ROOT / "scripts" / "freshness_check.py"),
        "--fixture",
        str(fixture),
        "--out",
        str(out),
        "--date",
        "2026-10-11",
    ]
    env = {key: value for key, value in os.environ.items() if key not in {"SASSY_TAOBAO_MODE", "SASSY_META_MODE"}}
    logged_out = subprocess.run(
        [*base, "--mode", "logged-out"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    assert logged_out.returncode == 0, logged_out.stderr
    saved = json.loads((out / "dataset-freshness-2026-10-11.json").read_text(encoding="utf-8"))
    assert not any(flag["kind"] == "promo_cny" for flag in saved["flags"])
    assert fixture.read_text(encoding="utf-8") == original

    login_env = dict(env)
    login_env["SASSY_TAOBAO_MODE"] = "login"
    logged_in = subprocess.run(base, cwd=ROOT, text=True, capture_output=True, check=False, env=login_env)
    assert logged_in.returncode == 0, logged_in.stderr
    saved = json.loads((out / "dataset-freshness-2026-10-11.json").read_text(encoding="utf-8"))
    promo = [flag for flag in saved["flags"] if flag["kind"] == "promo_cny" and flag["ma"] == "S06"]
    assert promo and promo[0]["stored"] == "80"
    assert fixture.read_text(encoding="utf-8") == original

    rejected = subprocess.run(
        [*base, "--mode", "signed-in"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    assert rejected.returncode == 2


def test_meta_logged_out_is_note_and_login_reads_gia() -> None:
    source = (ROOT / "scripts" / "freshness_check.py").read_text(encoding="utf-8")
    assert "graph.facebook.com" not in source
    assert "me/feed" not in source
    assert "create_post" not in source
    posts = [
        {"caption": "A07\nGiá: $26", "held": False},
        {"caption": "K06\nGiá: Inbox giá", "held": True},
    ]
    logged_out, _payload = _report(metaPosts=posts, metaMode="logged-out")
    assert logged_out.guards_pass
    assert logged_out.meta_reads == []
    assert logged_out.sources["meta"].state == "note"
    assert "NOTE" in logged_out.sources["meta"].detail

    logged_in, _payload = _report(metaPosts=posts, metaMode="login")
    assert logged_in.guards_pass
    assert len(logged_in.meta_reads) == 2
    priced, held = logged_in.meta_reads
    assert priced.gia == "$26" and priced.priced is True and priced.held is False
    assert held.gia == "Inbox giá" and held.priced is False and held.held is True
    text = freshness_check.render_markdown(logged_in)
    assert "NOTE" in text
    assert "Giá $26" in text


def test_live_path_does_not_read_meta(monkeypatch, tmp_path: Path) -> None:
    def fake(day: str):
        snap = snapshot_from_json(_passing_payload())
        snap.day = day
        snap.meta_mode = "login"
        snap.meta_posts = freshness_check._meta_posts_from_json(
            [{"caption": "A07\nGiá: $26", "held": False}]
        )
        return snap

    monkeypatch.setattr(freshness_check, "fetch_live", fake)
    code = main(["--date", "2026-10-11", "--out", str(tmp_path), "--meta", "login"])
    assert code == 0
    saved = json.loads((tmp_path / "dataset-freshness-2026-10-11.json").read_text(encoding="utf-8"))
    assert saved["meta"] == []
    assert saved["sources"]["meta"]["state"] == "note"
    assert "NOTE" in saved["sources"]["meta"]["detail"]
    assert "graph.facebook.com" not in json.dumps(saved)


def test_live_ma_still_quotes_but_a_duplicate_is_not_published() -> None:
    quote = listing_quote("A01", "16.25")
    assert quote.action == "quote"
    assert quote.sell_usd == 25
    report, _payload = _report([_complete("A01"), _complete("A01", via="poll")])
    assert len(report.pickup) == 2
    for decision in report.pickup:
        assert decision.quoted_usd is None
        assert decision.publish is False
        assert decision.live is False
        assert decision.flags == ("duplicate",)
    assert report.guards_pass is False


def test_duplicate_and_reused_are_not_quoted() -> None:
    report, _payload = _report([_complete("Z88"), _complete("Z88", via="poll")])
    assert len(report.pickup) == 2
    for decision in report.pickup:
        assert decision.quoted_usd is None
        assert decision.publish is False
        assert decision.live is False
        assert decision.flags == ("duplicate",)
    assert report.guards_pass is False

    reused, _payload = _report([_complete("Z87", reused=True)])
    assert reused.pickup[0].quoted_usd is None
    assert reused.pickup[0].flags == ("reused",)
    assert reused.pickup[0].publish is False
    assert reused.guards_pass is False


def test_second_s06_dollar_fails_even_when_last_row_is_25() -> None:
    payload = _passing_payload()
    rows = payload["blob"]["rows"]
    rows.insert(0, {"ma": "S06", "price_usd": "30"})
    report = evaluate(snapshot_from_json(payload))
    by_name = {guard.name: guard.ok for guard in report.guards}
    assert by_name["s06-price:blob"] is True
    assert by_name["duplicate:blob:S06"] is False
    assert by_name["s06-second-dollar:blob"] is False
    assert report.guards_pass is False


def test_q02_is_quoted_held_for_boss_and_not_live() -> None:
    for action in ("create", "sync", "mint"):
        report, _payload = _report([_complete("Q02", action=action)])
        decision = report.pickup[0]
        assert decision.ma == "Q02", action
        assert decision.held is True, action
        assert decision.live is False, action
        assert decision.publish is False, action
        assert decision.flags == ("boss_approval",), action
        assert decision.quoted_usd is not None, action
        assert report.guards_pass, action

    approved, _payload = _report([_complete("Q02", boss_approved=True)])
    assert approved.pickup[0].held is False
    assert approved.pickup[0].live is False
    assert approved.pickup[0].publish is False
    assert approved.pickup[0].flags == ()

    payload = _passing_payload()
    payload["blob"]["rows"].append({"ma": "Q02", "price_usd": "20"})
    payload["pickup"] = [_complete("Q02")]
    leaked = evaluate(snapshot_from_json(payload))
    assert leaked.pickup[0].publish is False
    assert leaked.pickup[0].live is False
    assert leaked.guards_pass is False
    assert any(guard.name == "off-live:Q02" and not guard.ok for guard in leaked.guards)


def test_s06_held_and_reprice_do_not_publish() -> None:
    blocked = {
        "K06-create": _complete("K06", action="create"),
        "K06-mint": _complete("K06", action="mint"),
        "V05-sync": _complete("V05", action="sync"),
        "S06-30": _complete("S06", action="update", sell_usd="30"),
        "S06-cents": _complete("S06", action="sync", sell_usd="25.50"),
        "A08-edit": _complete(
            "A08",
            action="update",
            already_listed=True,
            listed_sell_usd="28",
            sell_usd="40",
        ),
    }
    expected = {
        "K06-create": "held",
        "K06-mint": "held",
        "V05-sync": "held",
        "S06-30": "s06_lock",
        "S06-cents": "s06_lock",
        "A08-edit": "no_reprice",
    }
    for key, event in blocked.items():
        report, _payload = _report([event])
        decision = report.pickup[0]
        assert decision.quoted_usd is None, key
        assert decision.publish is False, key
        assert decision.live is False, key
        assert decision.flags == (expected[key],), key
        assert report.guards_pass is False, key

    locked, _payload = _report([_complete("S06", action="sync", sell_usd="25")])
    assert locked.pickup[0].quoted_usd == 25
    assert locked.pickup[0].publish is False
    assert locked.pickup[0].flags == ()
    assert locked.guards_pass

    same, _payload = _report(
        [
            _complete(
                "A08",
                action="update",
                already_listed=True,
                listed_sell_usd="28",
                sell_usd="28",
            )
        ]
    )
    assert same.pickup[0].quoted_usd is None
    assert same.pickup[0].publish is False
    assert same.pickup[0].flags == ()
    assert same.guards_pass


def _z99_fixture() -> dict:
    payload = _passing_payload()
    payload["intake"].append(
        {
            "ma": "Z99",
            "cost_cny": "88",
            "sell_usd": "",
            "link": "https://e.tb.cn/h.fixtureZ99",
        }
    )
    payload["taobao"].append(
        {
            "ma": "Z99",
            "state": "ok",
            "public_cny": "88",
            "title": "fixture set",
            "colors": ["den", "trang"],
            "sizes": ["S", "M"],
            "gallery": [
                "https://example.invalid/z99-1.jpg",
                "https://example.invalid/z99-2.jpg",
                "https://example.invalid/z99-3.jpg",
            ],
        }
    )
    assert "pickup" not in payload
    return payload


def test_natural_fixture_quotes_and_holds_new_ma(tmp_path: Path) -> None:
    before = (ROOT / "data" / "held.json").read_bytes()
    payload = _z99_fixture()
    original = json.dumps(payload)
    report = evaluate(snapshot_from_json(payload))
    decision = next(item for item in report.pickup if item.ma == "Z99")
    landed = landed_usd_from_cny("Z99", "88")
    assert listing_quote("Z99", landed).sell_usd == 21
    assert decision.held is True
    assert decision.live is False
    assert decision.publish is False
    assert decision.quoted_usd == 21
    assert decision.flags == ("boss_approval",)
    assert decision.stored_cny == "88"
    assert any(
        flag.ma == "Z99" and flag.kind == "boss_approval" and flag.stored == "88" for flag in report.flags
    )
    assert report.guards_pass
    row = next(item for item in report.rows if item["ma"] == "Z99")
    assert row["intakeCny"] == "88"
    text = freshness_check.render_markdown(report)
    assert "quote=21" in text
    assert "boss_approval" in text
    pickup_section = text.split("## Pickup", 1)[1].split("##", 1)[0]
    assert "None." not in pickup_section
    assert (ROOT / "data" / "held.json").read_bytes() == before

    fixture = tmp_path / "z99.json"
    fixture.write_text(original, encoding="utf-8")
    out = tmp_path / "out"
    env = {key: value for key, value in os.environ.items() if key not in {"SASSY_TAOBAO_MODE", "SASSY_META_MODE"}}
    ran = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "freshness_check.py"),
            "--fixture",
            str(fixture),
            "--out",
            str(out),
            "--date",
            "2026-10-11",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    assert ran.returncode == 0, ran.stderr
    assert fixture.read_text(encoding="utf-8") == original
    saved = json.loads((out / "dataset-freshness-2026-10-11.json").read_text(encoding="utf-8"))
    picked = next(item for item in saved["pickup"] if item["ma"] == "Z99")
    assert picked["quotedUsd"] == 21
    assert picked["held"] is True
    assert picked["publish"] is False
    assert picked["flags"] == ["boss_approval"]
    assert (ROOT / "data" / "held.json").read_bytes() == before


def test_natural_new_ma_on_blob_fails_guards() -> None:
    payload = _z99_fixture()
    payload["blob"]["rows"].append({"ma": "Z99", "price_usd": "21"})
    payload["hub"]["rows"].append({"ma": "Z99", "price_usd": "21"})
    for origin in payload["origins"]:
        payload["pdp"].setdefault("Z99", {})[origin] = {"status": 200, "price_usd": "21"}
    before = (ROOT / "data" / "held.json").read_bytes()
    report = evaluate(snapshot_from_json(payload))
    decision = next(item for item in report.pickup if item.ma == "Z99")
    assert report.guards_pass is False
    assert decision.quoted_usd == 21
    assert decision.held is True
    assert decision.publish is False
    assert decision.live is False
    failed = {guard.name for guard in report.guards if not guard.ok}
    assert "off-live:Z99" in failed
    assert (ROOT / "data" / "held.json").read_bytes() == before


def test_no_public_yen_page_is_not_quoted() -> None:
    page = "Size: S\n<img src=\"photo.jpg\">" + ("." * 2400)
    classified = classify_taobao(200, page)
    assert classified.state == "skip"
    assert classified.public_cny is None
    assert "no public ¥" in classified.detail
    report, _payload = _report(
        [
            _complete("A90", cost_cny="88", landed_usd="19.50", public_cny="88"),
            _complete(
                "A93",
                cost_cny="88",
                landed_usd="19.50",
                sizes=["S", "M"],
                photo_count=2,
                public_cny=None,
                taobao_state=classified.state,
                detail=classified.detail,
            ),
            _complete(
                "A94",
                cost_cny="88",
                landed_usd="19.50",
                sizes=["S", "M"],
                photo_count=2,
                public_cny=None,
                taobao_state="skip",
            ),
        ]
    )
    by_ma = {decision.ma: decision for decision in report.pickup}
    assert by_ma["A90"].quoted_usd == 30
    assert by_ma["A90"].flags == ("boss_approval",)
    assert by_ma["A93"].quoted_usd is None
    assert by_ma["A93"].flags == ("missing_yen",)
    assert by_ma["A93"].held is True
    assert by_ma["A93"].publish is False
    assert by_ma["A94"].quoted_usd is None
    assert by_ma["A94"].flags == ("missing_yen",)
