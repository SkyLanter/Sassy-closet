"""Intake ¥ drift against fixture Taobao pages. No live intake."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from cost_drift import (
    build_report,
    load_cost_fixture,
    main,
    report_json,
    resolve_taobao_item,
)
from intake_flags import IntakeRow, PublicCny, flag_cost_drift

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "scripts" / "fixtures" / "cost-drift.json"
HELD = ROOT / "data" / "held.json"
BANNED = ("corrected", "fixedCny", "fixed_cny", "suggested", "newPrice", "newCny")

EXPECTED = (
    ("K01", "blank_cny", "", None, None),
    ("H01", "blank_cny", "  ", None, None),
    ("O04", "blank_cny", "", None, None),
    ("S07", "garbled_cny", "127;145", None, None),
    ("S09", "drift", "134", "100", "34%"),
    ("S11", "drift", "180", "200", "10%"),
    ("A03", "drift", "108.01", "100", "8.01%"),
    ("P01", "drift", "70", "59.9", "16.86%"),
)


def _walk_keys(value: object):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _walk_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_keys(item)


def test_fixture_flags_blanks_garbled_and_drift_without_rewrites() -> None:
    original = FIXTURE.read_bytes()
    held = HELD.read_bytes()
    loaded = load_cost_fixture(FIXTURE)
    flags = flag_cost_drift(list(loaded.rows), loaded.public)
    found = tuple((flag.ma, flag.kind, flag.stored, flag.public_cny, flag.drift) for flag in flags)
    assert found == EXPECTED
    assert loaded.rows[3].cost_cny == "127;145"
    assert FIXTURE.read_bytes() == original
    assert HELD.read_bytes() == held
    quiet = {flag.ma for flag in flags}
    assert {"A01", "A02", "A04", "A05", "A07", "S06", "P02"}.isdisjoint(quiet)
    s06 = next(row for row in loaded.rows if row.ma == "S06")
    assert s06.sell_usd == "25"
    assert s06.cost_cny == "80"


def test_exact_eight_percent_and_unusable_public_prices_stay_quiet() -> None:
    public = {
        "A02": PublicCny("ok", Decimal("100")),
        "A04": PublicCny("ok", Decimal("100")),
        "A05": PublicCny("ok", Decimal("100")),
        "Z00": PublicCny("ok", Decimal("0")),
        "Z02": PublicCny("ok", Decimal("0")),
    }
    rows = [
        IntakeRow("A02", "108"),
        IntakeRow("A04", "92"),
        IntakeRow("A05", "105"),
        IntakeRow("Z02", "0"),
    ]
    assert flag_cost_drift(rows, public) == []
    zero = flag_cost_drift([IntakeRow("Z00", "10")], public)
    assert len(zero) == 1
    assert zero[0].kind == "drift"
    assert zero[0].stored == "10"
    assert zero[0].public_cny == "0"
    assert zero[0].drift == "over 8%"
    lower = flag_cost_drift([IntakeRow("A06", "91.99")], {"A06": PublicCny("ok", Decimal("100"))})
    assert lower[0].kind == "drift"
    assert lower[0].drift == "8.01%"
    assert lower[0].stored == "91.99"


def test_parsed_page_price_is_the_comparator(tmp_path: Path) -> None:
    html = (
        "var url = 'https://item.taobao.com/item.htm?id=1&sourceType=item&price=59.9&suid=abc';"
        + (" " * 2100)
    )
    code, listed, source = resolve_taobao_item({"ma": "P09", "html": html}, tmp_path)
    assert code == "P09"
    assert source == "parsed"
    assert listed.state == "ok"
    assert listed.value == Decimal("59.9")
    same = flag_cost_drift([IntakeRow("P09", "59.9")], {code: listed})
    assert same == []
    drifted = flag_cost_drift([IntakeRow("P09", "80")], {code: listed})
    assert drifted[0].public_cny == "59.9"
    assert drifted[0].stored == "80"
    assert drifted[0].kind == "drift"

    short = '{"priceText":"10"}'
    _, short_public, short_source = resolve_taobao_item({"ma": "P10", "html": short}, tmp_path)
    assert short_source == "parsed"
    assert short_public.state == "skip"
    assert short_public.value is None
    wall = (
        'window.location.href = "https://login.taobao.com/member/login.jhtml";'
        + '{"priceText":"10"}'
        + (" " * 2100)
    )
    _, wall_public, _source = resolve_taobao_item({"ma": "P11", "html": wall}, tmp_path)
    assert wall_public.state == "skip"
    assert wall_public.value is None
    assert flag_cost_drift(
        [IntakeRow("P10", "80"), IntakeRow("P11", "80")],
        {"P10": short_public, "P11": wall_public},
    ) == []


def test_cli_writes_a_fixture_report_and_leaves_prices(tmp_path: Path) -> None:
    original = FIXTURE.read_bytes()
    held = HELD.read_bytes()
    out = tmp_path / "out"
    code = main(["--fixture", str(FIXTURE), "--out", str(out), "--date", "2026-10-15"])
    assert code == 0
    markdown = (out / "cost-drift-2026-10-15.md").read_text(encoding="utf-8")
    payload = json.loads((out / "cost-drift-2026-10-15.json").read_text(encoding="utf-8"))
    assert payload["readOnly"] is True
    assert payload["liveIntake"] is False
    assert payload["driftAbove"] == "8%"
    assert "127;145" in markdown
    assert "over 8%" in markdown
    assert "K01" in markdown and "H01" in markdown and "O04" in markdown
    body = json.dumps(payload)
    for banned in BANNED:
        assert banned not in body
        assert banned not in list(_walk_keys(payload))
    stored = {row["ma"]: row for row in payload["rows"]}
    fixture = json.loads(original)
    for raw in fixture["intake"]:
        row = stored[raw["ma"]]
        expected = "" if raw["cost_cny"] is None else raw["cost_cny"]
        assert row["intakeCny"] == expected
    assert stored["S06"]["sellUsd"] == "25"
    assert stored["S06"]["intakeCny"] == "80"
    assert stored["S07"]["intakeCny"] == "127;145"
    assert stored["S07"]["flags"] == ["garbled_cny"]
    assert stored["P01"]["source"] == "parsed"
    assert stored["P01"]["publicCny"] == "59.9"
    assert stored["S09"]["source"] == "public"
    assert stored["A07"]["publicCny"] is None
    assert stored["A07"]["flags"] == []
    assert FIXTURE.read_bytes() == original
    assert HELD.read_bytes() == held
    assert {path.name for path in out.iterdir()} == {
        "cost-drift-2026-10-15.md",
        "cost-drift-2026-10-15.json",
    }
    assert "is not corrected" in markdown


def test_cli_refuses_live_and_missing_fixtures(tmp_path: Path, capsys) -> None:
    out = tmp_path / "out"
    assert main(["--out", str(out)]) == 2
    assert main(["--fixture", "https://example.invalid/intake.json", "--out", str(out)]) == 2
    assert main(["--fixture", str(tmp_path / "missing.json"), "--out", str(out)]) == 2
    assert main(["--fixture", str(FIXTURE), "--out", str(out), "--date", "yesterday"]) == 2
    assert not out.exists()
    assert "Live intake is not read." in capsys.readouterr().err
    source = (ROOT / "scripts" / "cost_drift.py").read_text(encoding="utf-8")
    assert "urlopen" not in source
    assert "fetch_live" not in source
    assert "api/submissions" not in source


def test_ci_check_uses_the_fixture() -> None:
    workflow = (ROOT / ".github" / "workflows" / "dataset-checks.yml").read_text(encoding="utf-8")
    assert "scripts/fixtures/cost-drift.json" in workflow
    assert "cost_drift.py" in workflow
    assert "api/submissions" not in workflow
    assert "sassy-closet.vercel.app" not in workflow
    report = report_json(build_report("2026-10-15", load_cost_fixture(FIXTURE)))
    assert report["liveIntake"] is False
    assert any(flag["stored"] == "127;145" and flag["kind"] == "garbled_cny" for flag in report["flags"])
