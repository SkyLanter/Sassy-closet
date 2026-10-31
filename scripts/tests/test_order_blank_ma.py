"""Fixture order lines with a blank mã. No mã or price is invented."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from held_policy import HeldPolicy, load_held_policy
from order_blank_ma import (
    BLANK_MA,
    EMPTY,
    HELD,
    MISSING,
    NEVER_LIST,
    NO_PRICE,
    NULL,
    WHITESPACE,
    BlankFlag,
    BlankResult,
    OmittedLine,
    flag_fixture,
    main,
    render_report,
    write_outputs,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "order_blank_ma.json"
HELD_PATH = ROOT / "data" / "held.json"
PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"
SCRIPT = ROOT / "scripts" / "order_blank_ma.py"

CLEAN_PRICES = (25, "25", "25.00", "25.0", "$25", "25.000", 25.0)


def _s06(price: object = 25) -> dict[str, object]:
    return {"lines": [{"ma": "S06", "title": "Satin skirt", "priceUsd": price}]}


def _open_policy() -> HeldPolicy:
    return HeldPolicy(held=(), never_list=())


def test_fixture_flags_blank_mas_and_leaves_s06() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    before = json.dumps(payload)
    held_before = HELD_PATH.read_bytes()
    products_before = PRODUCTS.read_bytes()
    result = flag_fixture(payload)
    assert json.dumps(payload) == before
    assert HELD_PATH.read_bytes() == held_before
    assert PRODUCTS.read_bytes() == products_before
    assert [(item.line, item.ma, item.price_usd) for item in result.lines] == [
        (1, "S06", "25"),
        (7, "A01", "28"),
    ]
    assert [(item.line, item.blank, item.stored_ma, item.price_usd) for item in result.flags] == [
        (2, EMPTY, "", "30"),
        (3, WHITESPACE, "   ", "18"),
        (4, NULL, None, "22"),
        (5, MISSING, None, "19"),
        (6, EMPTY, "", None),
    ]
    assert [(item.line, item.ma, item.reason) for item in result.omitted] == [
        (8, "K06", HELD),
    ]
    assert payload["lines"][0]["priceUsd"] == 25
    assert payload["lines"][0]["ma"] == "S06"
    assert payload["lines"][1]["ma"] == ""
    assert payload["lines"][1]["priceUsd"] == 30
    assert payload["lines"][2]["ma"] == "   "
    assert payload["lines"][2]["priceUsd"] == "18"
    assert payload["lines"][3]["ma"] is None
    assert "ma" not in payload["lines"][4]
    assert "priceUsd" not in payload["lines"][5]
    assert payload["lines"][6]["priceUsd"] == 28
    assert payload["lines"][7]["ma"] == "K06"
    assert payload["lines"][7]["priceUsd"] == 48
    for item in result.flags:
        assert item.kind == BLANK_MA
        assert item.stored_ma in ("", "   ", None)
        assert "ma" not in item.as_json()


def test_blank_line_does_not_receive_a_ma_from_the_title_or_a_neighbor() -> None:
    payload = {
        "lines": [
            {"ma": "S06", "title": "Satin skirt", "priceUsd": 25},
            {"ma": "", "title": "S06", "priceUsd": 25},
            {"title": "A01", "priceUsd": 28},
            {"ma": "   ", "title": "K06"},
        ]
    }
    before = json.dumps(payload)
    result = flag_fixture(payload, _open_policy())
    assert json.dumps(payload) == before
    assert [item.ma for item in result.lines] == ["S06"]
    assert result.lines[0].price_usd == "25"
    assert [item.stored_ma for item in result.flags] == ["", None, "   "]
    assert [item.title for item in result.flags] == ["S06", "A01", "K06"]
    body = json.dumps([item.as_json() for item in result.flags])
    assert '"ma": "S06"' not in body
    assert '"ma": "A01"' not in body
    assert '"ma": "K06"' not in body
    assert "suggestedMa" not in body
    assert "replacement" not in body
    for item in result.flags:
        stored = item.stored_ma or ""
        assert stored.strip() == ""


def test_missing_price_is_not_invented() -> None:
    payload = {
        "lines": [
            {"ma": "S06", "title": "Satin skirt", "priceUsd": 25},
            {"ma": ""},
            {"ma": "A01", "title": "Ivory blouse"},
            {"ma": None, "priceUsd": None},
            {"title": "Missing", "priceUsd": "  "},
        ]
    }
    before = json.dumps(payload)
    result = flag_fixture(payload, _open_policy())
    assert json.dumps(payload) == before
    assert "priceUsd" not in payload["lines"][1]
    assert "priceUsd" not in payload["lines"][2]
    assert payload["lines"][3]["priceUsd"] is None
    assert payload["lines"][4]["priceUsd"] == "  "
    assert [(item.line, item.price_usd) for item in result.flags] == [
        (2, None),
        (4, None),
        (5, None),
    ]
    assert result.omitted == (OmittedLine(3, "A01", NO_PRICE),)
    report = render_report(result)
    assert "No price was on the line. No price was added." in report
    assert "No price was added." in report
    assert "$0" not in report
    flag_body = json.dumps([item.as_json() for item in result.flags])
    assert '"priceUsd": null' in flag_body
    assert "corrected" not in flag_body
    assert "filledPrice" not in flag_body


@pytest.mark.parametrize("price", CLEAN_PRICES)
def test_s06_at_25_stays_clean_and_file_stays(tmp_path: Path, price: object) -> None:
    payload = _s06(price)
    raw = json.dumps(payload)
    path = tmp_path / "clean.json"
    path.write_text(raw, encoding="utf-8")
    before = path.read_bytes()
    held_before = HELD_PATH.read_bytes()
    products_before = PRODUCTS.read_bytes()
    result = flag_fixture(json.loads(raw), _open_policy())
    assert result.flags == ()
    assert result.omitted == ()
    assert len(result.lines) == 1
    assert result.lines[0].ma == "S06"
    assert result.lines[0].line == 1
    assert path.read_bytes() == before
    assert HELD_PATH.read_bytes() == held_before
    assert PRODUCTS.read_bytes() == products_before
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored["lines"][0]["ma"] == "S06"
    assert stored["lines"][0]["priceUsd"] == price


def test_other_s06_dollar_is_not_rewritten(tmp_path: Path) -> None:
    payload = {
        "lines": [
            {"ma": "S06", "title": "Satin skirt", "priceUsd": 30},
            {"ma": "", "title": "No code", "priceUsd": 12},
        ]
    }
    path = tmp_path / "other.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    before = path.read_bytes()
    result = flag_fixture(json.loads(path.read_text(encoding="utf-8")), _open_policy())
    assert path.read_bytes() == before
    assert result.lines[0].ma == "S06"
    assert result.lines[0].price_usd == "30"
    assert result.flags[0].stored_ma == ""
    assert result.flags[0].price_usd == "12"
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored["lines"][0]["priceUsd"] == 30
    assert stored["lines"][0]["ma"] == "S06"
    assert stored["lines"][1]["ma"] == ""
    report = render_report(result)
    assert "Line 1 S06 — Satin skirt — $30" in report
    assert "$25" not in report


def test_spaced_s06_at_25_stays_clean() -> None:
    payload = {"lines": [{"ma": " s06 ", "title": "Satin skirt", "priceUsd": "25.00"}]}
    before = json.dumps(payload)
    result = flag_fixture(payload, _open_policy())
    assert json.dumps(payload) == before
    assert result.flags == ()
    assert result.lines[0].ma == "S06"
    assert result.lines[0].price_usd == "25.00"
    assert payload["lines"][0]["ma"] == " s06 "
    assert payload["lines"][0]["priceUsd"] == "25.00"


def test_held_and_never_list_stay_off_without_writing_held() -> None:
    before = HELD_PATH.read_bytes()
    policy = HeldPolicy(held=("K06",), never_list=("Z98",))
    payload = {
        "lines": [
            {"ma": "S06", "title": "Satin skirt", "priceUsd": 25},
            {"ma": "", "title": "Blank", "priceUsd": 11},
            {"ma": "K06", "title": "Held knit", "priceUsd": 48},
            {"ma": "Z98", "title": "Skipped", "priceUsd": 31},
        ]
    }
    result = flag_fixture(payload, policy)
    assert [item.ma for item in result.lines] == ["S06"]
    assert result.lines[0].price_usd == "25"
    assert result.flags[0].stored_ma == ""
    assert result.flags[0].line == 2
    assert [(item.ma, item.reason) for item in result.omitted] == [
        ("K06", HELD),
        ("Z98", NEVER_LIST),
    ]
    report = render_report(result)
    assert "K06 is held and stays off the order." in report
    assert "Z98 is on the never-list and stays off the order." in report
    assert "$48" not in report
    assert "$31" not in report
    assert HELD_PATH.read_bytes() == before
    assert payload["lines"][2]["ma"] == "K06"
    assert payload["lines"][2]["priceUsd"] == 48
    assert payload["lines"][1]["ma"] == ""


def test_two_blank_lines_stay_two_flags() -> None:
    payload = {
        "lines": [
            {"ma": "S06", "priceUsd": 25, "title": "Satin skirt"},
            {"ma": ""},
            {"ma": ""},
        ]
    }
    result = flag_fixture(payload, _open_policy())
    assert [item.line for item in result.flags] == [2, 3]
    assert result.flags[0].stored_ma == ""
    assert result.flags[1].stored_ma == ""
    assert len(result.lines) == 1
    assert payload["lines"][1] == {"ma": ""}
    assert payload["lines"][2] == {"ma": ""}


def test_invalid_ma_is_rejected_without_a_replacement(tmp_path: Path) -> None:
    payload = {"lines": [{"ma": "S6A", "title": "Short", "priceUsd": 25}]}
    path = tmp_path / "bad-ma.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    before = path.read_bytes()
    with pytest.raises(ValueError, match="invalid mã"):
        flag_fixture(json.loads(path.read_text(encoding="utf-8")))
    assert path.read_bytes() == before
    number = {"lines": [{"ma": 6, "priceUsd": 25}]}
    with pytest.raises(ValueError, match="mã must be a string"):
        flag_fixture(number)
    assert number["lines"][0]["ma"] == 6


def test_bad_price_is_rejected_without_rewriting(tmp_path: Path) -> None:
    payload = {"lines": [{"ma": "", "priceUsd": "thirty"}]}
    path = tmp_path / "bad-price.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    before = path.read_bytes()
    with pytest.raises(ValueError, match="price must be a number"):
        flag_fixture(json.loads(path.read_text(encoding="utf-8")))
    assert path.read_bytes() == before
    assert json.loads(path.read_text(encoding="utf-8"))["lines"][0]["ma"] == ""


def test_unknown_kind_and_reason_are_rejected() -> None:
    with pytest.raises(ValueError, match="unknown finding kind"):
        render_report(
            BlankResult(
                None,
                (),
                (BlankFlag(1, "nope", EMPTY, "", None, None),),
                (),
            )
        )
    with pytest.raises(ValueError, match="unknown blank form"):
        render_report(
            BlankResult(
                None,
                (),
                (BlankFlag(1, BLANK_MA, "gap", "", None, None),),
                (),
            )
        )
    with pytest.raises(ValueError, match="unknown omit reason"):
        render_report(BlankResult(None, (), (), (OmittedLine(1, "A01", "sold"),)))


def test_report_names_the_blank_and_leaves_s06() -> None:
    result = flag_fixture(json.loads(FIXTURE.read_text(encoding="utf-8")))
    report = render_report(result)
    assert "Read-only" in report
    assert "No mã was invented." in report
    assert "No price was invented." in report
    assert "The fixture file was not rewritten." in report
    assert "Line 1 S06 — Satin skirt — $25" in report
    assert "Line 2 has a blank mã. Stored mã is empty. Price stays $30. No mã was invented." in report
    assert "Line 3 has a blank mã. Stored mã is '   '. Price stays $18. No mã was invented." in report
    assert "Line 4 has a blank mã. The mã field is null. Price stays $22. No mã was invented." in report
    assert "Line 5 has a blank mã. The mã field is missing. Price stays $19. No mã was invented." in report
    assert "Line 6 has a blank mã. Stored mã is empty. No price was on the line. No price was added. No mã was invented." in report
    assert "Line 7 A01 — Ivory blouse — $28" in report
    assert "Line 8 K06 is held and stays off the order." in report
    assert "suggested" not in report
    assert "replacement" not in report


def test_outputs_are_the_report_files(tmp_path: Path) -> None:
    result = flag_fixture(json.loads(FIXTURE.read_text(encoding="utf-8")))
    write_outputs(result, tmp_path)
    assert sorted(path.name for path in tmp_path.iterdir()) == ["flags.json", "report.md"]
    payload = json.loads((tmp_path / "flags.json").read_text(encoding="utf-8"))
    assert payload["lines"][0] == {
        "line": 1,
        "ma": "S06",
        "title": "Satin skirt",
        "priceUsd": "25",
    }
    assert payload["flags"][0]["kind"] == BLANK_MA
    assert payload["flags"][0]["storedMa"] == ""
    assert "suggestedMa" not in json.dumps(payload)


def test_cli_flags_the_fixture_and_leaves_the_file(tmp_path: Path) -> None:
    before_held = HELD_PATH.read_bytes()
    before_products = PRODUCTS.read_bytes()
    before_fixture = FIXTURE.read_bytes()
    out = tmp_path / "blank"
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(FIXTURE), "--out", str(out)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 1, completed.stderr
    report = (out / "report.md").read_text(encoding="utf-8")
    payload = json.loads((out / "flags.json").read_text(encoding="utf-8"))
    assert "Line 1 S06 — Satin skirt — $25" in report
    assert "Line 2 has a blank mã. Stored mã is empty." in report
    assert payload["flags"][0]["storedMa"] == ""
    assert payload["flags"][0]["priceUsd"] == "30"
    assert payload["lines"][0]["priceUsd"] == "25"
    assert HELD_PATH.read_bytes() == before_held
    assert PRODUCTS.read_bytes() == before_products
    assert FIXTURE.read_bytes() == before_fixture


def test_cli_clean_s06_fixture_exits_zero(tmp_path: Path) -> None:
    fixture = tmp_path / "clean.json"
    original = json.dumps(_s06(25))
    fixture.write_text(original, encoding="utf-8")
    out = tmp_path / "out"
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(fixture), "--out", str(out)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    report = (out / "report.md").read_text(encoding="utf-8")
    assert "Flags: 0" in report
    assert "No flags." in report
    assert "Line 1 S06 — Satin skirt — $25" in report
    assert fixture.read_text(encoding="utf-8") == original
    stored = json.loads(fixture.read_text(encoding="utf-8"))
    assert stored["lines"][0]["ma"] == "S06"
    assert stored["lines"][0]["priceUsd"] == 25


def test_cli_without_fixture_does_not_write(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["--out", str(tmp_path / "unused")])
    assert code == 2
    assert not (tmp_path / "unused").exists()
    message = capsys.readouterr().out
    assert "fixture" in message
    assert "does not invent a mã or a price" in message


def test_cli_rejects_a_bad_fixture(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    code = main(["--fixture", str(bad), "--out", str(tmp_path / "out")])
    assert code == 2
    assert not (tmp_path / "out").exists()


def test_cli_refuses_remote_shop_and_held_targets(tmp_path: Path) -> None:
    fixture = tmp_path / "order.json"
    fixture.write_text(json.dumps(_s06(25)), encoding="utf-8")
    before = fixture.read_bytes()
    held_before = HELD_PATH.read_bytes()
    code = main(["--fixture", "https://example.test/order.json", "--out", str(tmp_path / "out")])
    assert code == 2
    assert not (tmp_path / "out").exists()
    targets = (
        ROOT / "data" / "order-blank-out",
        ROOT / "sassy-closet-shop" / "order-blank-out",
        ROOT / "sassy-closet" / "order-blank-out",
        HELD_PATH,
    )
    for target in targets:
        code = main(["--fixture", str(fixture), "--out", str(target)])
        assert code == 2
        assert not (ROOT / "data" / "order-blank-out").exists()
        assert not (ROOT / "sassy-closet-shop" / "order-blank-out").exists()
        assert not (ROOT / "sassy-closet" / "order-blank-out").exists()
    assert fixture.read_bytes() == before
    assert HELD_PATH.read_bytes() == held_before
    code = main(["--fixture", str(fixture), "--out", str(fixture)])
    assert code == 2
    assert fixture.read_bytes() == before


def test_real_held_list_matches_origin_and_is_not_written() -> None:
    policy = load_held_policy()
    raw = json.loads(HELD_PATH.read_text(encoding="utf-8"))
    assert list(policy.held) == raw["heldIncomplete"]
    assert "S06" not in policy.held
    assert "K06" in policy.held
    assert "V05" in policy.held
    assert "S16" in policy.held
    assert "A27" in policy.held
    before = HELD_PATH.read_bytes()
    flag_fixture(json.loads(FIXTURE.read_text(encoding="utf-8")))
    assert HELD_PATH.read_bytes() == before


def test_source_stays_fixture_only() -> None:
    source = SCRIPT.read_text(encoding="utf-8").lower()
    for banned in (
        "urllib",
        "requests",
        "httpx",
        "http.client",
        "vercel",
        "facebook",
        "instagram",
        "order_price_mismatch",
        "suggestedma",
        "replacement",
    ):
        assert banned not in source
