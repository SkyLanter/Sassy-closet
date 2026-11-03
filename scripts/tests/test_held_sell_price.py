"""Flag a held mã that a catalog fixture still prices. The price stays. No file writes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from held_policy import HeldPolicy, default_held_path, load_held_policy
from held_sell_price import (
    CatalogRow,
    SellPriceFlag,
    flag_files,
    flag_held_sell_price,
    load_catalog,
    load_held_fixture,
    main,
    parse_catalog,
)

ROOT = Path(__file__).resolve().parents[2]
HELD_FIXTURE = ROOT / "scripts" / "fixtures" / "held-sell-price" / "held.json"
CATALOG_FIXTURE = ROOT / "scripts" / "fixtures" / "held-sell-price" / "catalog.json"
HELD = ROOT / "data" / "held.json"
SHOP_CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
SCRIPT = ROOT / "scripts" / "held_sell_price.py"
S06 = "S06"
PRICED = "K06"
STORED_PRICE = 48


def test_fixture_flags_k06_and_leaves_the_price() -> None:
    held_bytes = HELD_FIXTURE.read_bytes()
    catalog_bytes = CATALOG_FIXTURE.read_bytes()
    live_held = HELD.read_bytes()
    policy = load_held_policy()
    fixture_policy = load_held_fixture(HELD_FIXTURE)
    catalog_text = CATALOG_FIXTURE.read_text(encoding="utf-8")
    payload = json.loads(catalog_text)
    before = json.dumps(payload)
    rows = parse_catalog(payload)
    report = flag_held_sell_price(fixture_policy, rows)
    assert json.dumps(payload) == before
    assert "K06" in fixture_policy.held
    assert "S16" in policy.held and "A27" in policy.held
    assert set(policy.held) != set(fixture_policy.held)
    assert report.flags == (SellPriceFlag(PRICED, STORED_PRICE, "hold"),)
    assert report.flags[0].as_json()["kind"] == "held_sell_price"
    assert report.s06_price_usd == 25
    assert report.s06_status == "available"
    assert report.s06_on_held is False
    assert S06 not in fixture_policy.held
    assert S06 not in fixture_policy.never_list
    assert S06 not in policy.held
    assert S06 not in [flag.ma for flag in report.flags]
    stored = {row["ma"]: row for row in payload["products"]}
    assert stored[PRICED]["priceUsd"] == STORED_PRICE
    assert stored[PRICED]["status"] == "hold"
    assert stored[S06]["priceUsd"] == 25
    assert stored[S06]["status"] == "available"
    assert stored["V05"]["priceUsd"] is None
    assert stored["V05"]["status"] == "hold"
    assert stored["A01"]["priceUsd"] == 27
    assert HELD_FIXTURE.read_bytes() == held_bytes
    assert CATALOG_FIXTURE.read_bytes() == catalog_bytes
    assert HELD.read_bytes() == live_held


def test_s06_stays_25_and_stays_clean() -> None:
    policy = load_held_policy()
    fixture = json.loads(HELD_FIXTURE.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG_FIXTURE.read_text(encoding="utf-8"))
    held_codes = [code.strip().upper() for code in fixture["heldIncomplete"]]
    assert fixture["neverList"] == []
    assert S06 not in held_codes
    assert S06 not in policy.held
    assert S06 not in policy.never_list
    assert "K06" in held_codes
    assert "S16" in policy.held
    assert "S16" not in held_codes
    s06 = next(row for row in catalog["products"] if row["ma"] == S06)
    assert s06["priceUsd"] == 25
    assert s06["status"] == "available"
    report = flag_files(HELD_FIXTURE, CATALOG_FIXTURE)
    assert S06 not in [flag.ma for flag in report.flags]
    assert [flag.ma for flag in report.flags] == [PRICED]
    assert report.flags[0].price_usd == STORED_PRICE
    body = json.dumps(report.as_json())
    assert '"priceUsd": 25' in body
    assert '"priceUsd": 48' in body
    assert '"onHeldList": false' in body
    assert '"writes": []' in body
    assert "corrected" not in body
    assert "cleared" not in body


def test_cli_prints_the_flag_and_writes_nothing() -> None:
    held_bytes = HELD_FIXTURE.read_bytes()
    catalog_bytes = CATALOG_FIXTURE.read_bytes()
    live_held = HELD.read_bytes()
    shop_bytes = SHOP_CATALOG.read_bytes()
    data_names = sorted(path.name for path in (ROOT / "data").iterdir())
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--held",
            str(HELD_FIXTURE),
            "--catalog",
            str(CATALOG_FIXTURE),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 1, completed.stderr
    body = json.loads(completed.stdout)
    assert body["readOnly"] is True
    assert body["writes"] == []
    assert body["flags"] == [
        {"ma": PRICED, "kind": "held_sell_price", "priceUsd": STORED_PRICE, "status": "hold"}
    ]
    assert body["s06"] == {"priceUsd": 25, "status": "available", "onHeldList": False}
    assert S06 not in [flag["ma"] for flag in body["flags"]]
    stored = json.loads(CATALOG_FIXTURE.read_text(encoding="utf-8"))
    priced = next(row for row in stored["products"] if row["ma"] == PRICED)
    assert priced["priceUsd"] == STORED_PRICE
    assert HELD_FIXTURE.read_bytes() == held_bytes
    assert CATALOG_FIXTURE.read_bytes() == catalog_bytes
    assert HELD.read_bytes() == live_held
    assert SHOP_CATALOG.read_bytes() == shop_bytes
    assert sorted(path.name for path in (ROOT / "data").iterdir()) == data_names
    assert default_held_path() == HELD
    assert PRICED in HELD.read_text(encoding="utf-8")
    assert S06 not in json.loads(HELD.read_text(encoding="utf-8"))["heldIncomplete"]


def test_clean_catalog_has_no_flags(tmp_path: Path) -> None:
    held_bytes = HELD_FIXTURE.read_bytes()
    catalog_bytes = CATALOG_FIXTURE.read_bytes()
    live_held = HELD.read_bytes()
    clean = tmp_path / "catalog.json"
    payload = json.loads(CATALOG_FIXTURE.read_text(encoding="utf-8"))
    for row in payload["products"]:
        if row["ma"] == PRICED:
            row["priceUsd"] = None
    clean.write_text(json.dumps(payload), encoding="utf-8")
    clean_bytes = clean.read_bytes()
    report = flag_files(HELD_FIXTURE, clean)
    assert report.flags == ()
    assert report.s06_price_usd == 25
    assert report.s06_on_held is False
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--held", str(HELD_FIXTURE), "--catalog", str(clean)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["flags"] == []
    assert json.loads(completed.stdout)["s06"]["priceUsd"] == 25
    assert clean.read_bytes() == clean_bytes
    assert HELD_FIXTURE.read_bytes() == held_bytes
    assert CATALOG_FIXTURE.read_bytes() == catalog_bytes
    assert HELD.read_bytes() == live_held
    committed = json.loads(CATALOG_FIXTURE.read_text(encoding="utf-8"))
    k06 = next(row for row in committed["products"] if row["ma"] == PRICED)
    assert k06["priceUsd"] == STORED_PRICE
    assert k06["status"] == "hold"


def test_in_memory_flags_only_held_rows_with_a_price() -> None:
    policy = HeldPolicy(held=("V05", "K06", "S14"), never_list=("Z02",))
    rows = {
        "K06": _row("k06", "hold", STORED_PRICE),
        "V05": _row("V05", "hold", None),
        "S14": _row("S14", "sold", None),
        "A01": _row("A01", "available", 27),
        "Z02": _row("Z02", "available", 22),
        "S06": _row("S06", "available", 25),
    }
    before_held = policy.held
    before_prices = {ma: rows[ma].price_usd for ma in rows}
    report = flag_held_sell_price(policy, rows)
    assert [flag.ma for flag in report.flags] == [PRICED]
    assert report.flags[0].price_usd == STORED_PRICE
    assert report.flags[0].status == "hold"
    assert report.s06_price_usd == 25
    assert S06 not in [flag.ma for flag in report.flags]
    assert policy.held == before_held
    assert {ma: rows[ma].price_usd for ma in rows} == before_prices

    both = dict(rows)
    both["V05"] = _row("V05", "hold", 40)
    both["S14"] = _row("S14", "sold", 19)
    flagged = flag_held_sell_price(policy, both)
    assert [(flag.ma, flag.price_usd, flag.status) for flag in flagged.flags] == [
        ("K06", STORED_PRICE, "hold"),
        ("S14", 19, "sold"),
        ("V05", 40, "hold"),
    ]
    assert both["K06"].price_usd == STORED_PRICE
    assert both["V05"].price_usd == 40
    assert both["S14"].price_usd == 19
    assert both["A01"].price_usd == 27
    assert both["S06"].price_usd == 25


def test_held_without_a_price_and_priced_unheld_are_quiet() -> None:
    policy = HeldPolicy(held=("K02", "K03"), never_list=())
    rows = {
        "K02": _row("K02", "hold", None),
        "D05": _row("D05", "available", 26),
        "A01": _row("A01", "available", 27),
        "S06": _row("S06", "available", 25),
    }
    report = flag_held_sell_price(policy, rows)
    assert report.flags == ()
    assert rows["K02"].price_usd is None
    assert rows["D05"].price_usd == 26
    assert rows["A01"].price_usd == 27
    assert rows["S06"].price_usd == 25

    zero = dict(rows)
    zero["K03"] = _row("K03", None, 0)
    zero_report = flag_held_sell_price(policy, zero)
    assert [flag.as_json() for flag in zero_report.flags] == [
        {"ma": "K03", "kind": "held_sell_price", "priceUsd": 0, "status": None}
    ]
    assert zero["K03"].price_usd == 0


def test_s06_price_and_held_list_are_refused(tmp_path: Path) -> None:
    held_bytes = HELD_FIXTURE.read_bytes()
    catalog_bytes = CATALOG_FIXTURE.read_bytes()
    live_held = HELD.read_bytes()
    priced = tmp_path / "priced.json"
    payload = json.loads(catalog_bytes)
    for row in payload["products"]:
        if row["ma"] == S06:
            row["priceUsd"] = 26
    priced.write_text(json.dumps(payload), encoding="utf-8")
    priced_bytes = priced.read_bytes()
    try:
        flag_files(HELD_FIXTURE, priced)
    except ValueError as error:
        assert str(error) == "S06 stays $25"
    else:
        raise AssertionError("S06 price change was accepted")
    assert priced.read_bytes() == priced_bytes
    assert json.loads(priced.read_text(encoding="utf-8"))
    s06 = next(
        row
        for row in json.loads(priced.read_text(encoding="utf-8"))["products"]
        if row["ma"] == S06
    )
    assert s06["priceUsd"] == 26

    held_with_s06 = tmp_path / "held.json"
    held_payload = json.loads(held_bytes)
    held_payload["heldIncomplete"] = ["K06", "s06"]
    held_with_s06.write_text(json.dumps(held_payload), encoding="utf-8")
    held_with_s06_bytes = held_with_s06.read_bytes()
    try:
        flag_files(held_with_s06, CATALOG_FIXTURE)
    except ValueError as error:
        assert str(error) == "S06 stays off the held list"
    else:
        raise AssertionError("S06 on the held list was accepted")
    assert held_with_s06.read_bytes() == held_with_s06_bytes
    assert json.loads(held_with_s06.read_text(encoding="utf-8"))["heldIncomplete"] == ["K06", "s06"]
    assert HELD_FIXTURE.read_bytes() == held_bytes
    assert CATALOG_FIXTURE.read_bytes() == catalog_bytes
    assert HELD.read_bytes() == live_held
    committed = json.loads(CATALOG_FIXTURE.read_text(encoding="utf-8"))
    k06 = next(row for row in committed["products"] if row["ma"] == PRICED)
    assert k06["priceUsd"] == STORED_PRICE

    never = HeldPolicy(held=("K06",), never_list=(S06,))
    try:
        flag_held_sell_price(
            never,
            {
                "S06": _row(S06, "available", 25),
                "K06": _row("K06", "hold", 48),
            },
        )
    except ValueError as error:
        assert str(error) == "S06 stays off the held list"
    else:
        raise AssertionError("S06 on the never list was accepted")


def test_cli_refuses_live_files_and_bad_fixtures(tmp_path: Path, capsys) -> None:
    held_bytes = HELD_FIXTURE.read_bytes()
    catalog_bytes = CATALOG_FIXTURE.read_bytes()
    live_held = HELD.read_bytes()
    shop_bytes = SHOP_CATALOG.read_bytes()

    refused_held = main(["--held", str(HELD), "--catalog", str(CATALOG_FIXTURE)])
    assert refused_held == 2
    assert "data/held.json" in capsys.readouterr().err
    assert HELD.read_bytes() == live_held

    remote = main(
        ["--held", "https://example.invalid/held.json", "--catalog", str(CATALOG_FIXTURE)]
    )
    assert remote == 2
    assert "local fixtures only" in capsys.readouterr().err

    shop = main(["--held", str(HELD_FIXTURE), "--catalog", str(SHOP_CATALOG)])
    assert shop == 2
    assert "Shop catalog files are not read." in capsys.readouterr().err
    assert SHOP_CATALOG.read_bytes() == shop_bytes

    missing = main(["--held", str(tmp_path / "missing.json"), "--catalog", str(CATALOG_FIXTURE)])
    assert missing == 2
    assert "missing held-list fixture" in capsys.readouterr().err

    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert main(["--held", str(HELD_FIXTURE), "--catalog", str(broken)]) == 2
    assert "not catalog JSON" in capsys.readouterr().err
    assert broken.read_text(encoding="utf-8") == "{"

    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text(
        json.dumps(
            {
                "schema": "catalog.v1",
                "version": 1,
                "products": [
                    {"ma": "K06", "priceUsd": 48, "status": "hold"},
                    {"ma": "k06", "priceUsd": 48, "status": "hold"},
                ],
            }
        ),
        encoding="utf-8",
    )
    try:
        load_catalog(duplicate)
    except ValueError as error:
        assert "K06" in str(error)
    else:
        raise AssertionError("duplicate mã was accepted")
    stored_duplicate = json.loads(duplicate.read_text(encoding="utf-8"))
    assert stored_duplicate["products"][0]["priceUsd"] == 48
    assert stored_duplicate["products"][1]["priceUsd"] == 48

    invalid = tmp_path / "invalid.json"
    invalid.write_text(
        json.dumps({"products": [{"ma": "S6A", "priceUsd": 25, "status": "available"}]}),
        encoding="utf-8",
    )
    try:
        load_catalog(invalid)
    except ValueError as error:
        assert "invalid" in str(error)
    else:
        raise AssertionError("invalid mã was accepted")

    fractional = tmp_path / "fraction.json"
    fractional.write_text(
        json.dumps({"products": [{"ma": "K06", "priceUsd": 48.5, "status": "hold"}]}),
        encoding="utf-8",
    )
    try:
        load_catalog(fractional)
    except ValueError as error:
        assert "integer or null" in str(error)
    else:
        raise AssertionError("fractional price was accepted")
    assert json.loads(fractional.read_text(encoding="utf-8"))["products"][0]["priceUsd"] == 48.5

    assert HELD_FIXTURE.read_bytes() == held_bytes
    assert CATALOG_FIXTURE.read_bytes() == catalog_bytes
    assert HELD.read_bytes() == live_held


def test_lowercase_catalog_ma_matches_the_held_list(tmp_path: Path) -> None:
    held = tmp_path / "held.json"
    catalog = tmp_path / "catalog.json"
    held.write_text(
        json.dumps({"heldIncomplete": ["k06", "V05"], "neverList": []}),
        encoding="utf-8",
    )
    catalog.write_text(
        json.dumps(
            {
                "schema": "catalog.v1",
                "version": 1,
                "products": [
                    {"ma": "s06", "priceUsd": 25, "status": "available"},
                    {"ma": "k06", "priceUsd": 48, "status": "hold"},
                    {"ma": "v05", "priceUsd": None, "status": "hold"},
                ],
            }
        ),
        encoding="utf-8",
    )
    held_bytes = held.read_bytes()
    catalog_bytes = catalog.read_bytes()
    report = flag_files(held, catalog)
    assert [flag.as_json() for flag in report.flags] == [
        {"ma": "K06", "kind": "held_sell_price", "priceUsd": 48, "status": "hold"}
    ]
    assert report.s06_price_usd == 25
    assert S06 not in [flag.ma for flag in report.flags]
    assert held.read_bytes() == held_bytes
    assert catalog.read_bytes() == catalog_bytes
    assert json.loads(catalog.read_text(encoding="utf-8"))["products"][1]["priceUsd"] == 48
    assert load_held_fixture(held).held == ("K06", "V05")


def test_script_has_no_write_or_network_calls() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    folded = source.casefold()
    for token in (
        "write_text",
        "write_bytes",
        "urlopen",
        "urllib",
        "urlretrieve",
        "mkdir",
        "requests",
        "open(",
        "held_available",
        "catalog_diff",
        "held_diff",
    ):
        assert token not in source
    assert "tesla" not in folded
    assert "vercel.app" not in folded


def _row(ma: str, status: str | None, price: int | None) -> CatalogRow:
    return CatalogRow(ma.strip().upper(), price, status)
