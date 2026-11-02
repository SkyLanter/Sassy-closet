"""Read-only parity checker: planted mismatches fail, the repo's known splits are Boss notes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from parity_check import (
    DRIFT,
    EXTRAS,
    GIA,
    LIVE_FIXTURE,
    PRODUCTS,
    SNAPSHOT,
    TAOBAO,
    TAOBAO_PUBLIC,
    Example,
    build_report,
    decimal_shoe_misses,
    decimal_shoe_window,
    dollar_text,
    dual_cost_findings,
    import_size_findings,
    intake_decimal_findings,
    intake_g_decimal_expected,
    main,
    price_disagreements,
    quote_examples,
    render_text,
)

ROOT = Path(__file__).resolve().parents[2]
HELD = ROOT / "data" / "held.json"
WATCHED = (PRODUCTS, EXTRAS, SNAPSHOT, DRIFT, LIVE_FIXTURE, GIA, TAOBAO, TAOBAO_PUBLIC, HELD)

BOSS_CODES = (
    "shoe-window",
    "kind-o-scale",
    "shop-parse-ignores-kind",
    "shoe-letter-size",
    "short-ma-quote",
    "shop-normalize-no-pad",
    "shop-debox-unknown",
    "shop-prefers-yen",
    "import-kind-o",
    "cost-currency-default",
    "caption-vs-intake-tier",
    "excel-letter-gap",
    "shoe-decimal-window",
    "seed-vs-live-price",
    "seed-missing-live",
    "extras-vs-live-price",
    "extras-s06-lock",
)


@pytest.fixture(scope="module")
def report():
    return build_report()


def test_dollar_text_accepts_whole_dollars_only():
    assert dollar_text(25) == ("25", True)
    assert dollar_text(25.0) == ("25", True)
    assert dollar_text("25") == ("25", True)
    assert dollar_text(25.5) == ("25.5", False)
    assert dollar_text(True) == ("", False)
    assert dollar_text(None) == ("", False)
    assert dollar_text(-1) == ("-1", False)


def test_price_disagreements_name_the_ma_and_do_not_edit_inputs():
    left = {"A03": "25", "S06": "25"}
    right = {"A03": "22", "S06": "25"}
    rows = price_disagreements(left, right)
    assert rows == (Example("A03", "25", "22"),)
    assert left == {"A03": "25", "S06": "25"}
    assert right == {"A03": "22", "S06": "25"}
    assert price_disagreements({"A01": "10"}, {"A01": "10"}) == ()
    assert price_disagreements({"A99": ""}, {"A99": "25"}) == (Example("A99", "", "25"),)


def test_decimal_shoe_flags_a_dropped_trailing_zero():
    clean = {
        "34.0": ["34"],
        "35.0": ["35"],
        "40.0": ["40"],
        "42.0": ["42"],
        "32.0": [],
        "34.00": [],
        "34.5": [],
        "40.00": [],
        "47.0": [],
    }
    assert decimal_shoe_misses(clean) == ()
    dropped = dict(clean)
    dropped["40.0"] = []
    rows = decimal_shoe_misses(dropped)
    assert rows[0].key == "40.0"
    assert rows[0].left == "40"
    widened = dict(clean)
    widened["34.5"] = ["34"]
    assert decimal_shoe_misses(widened)[0].key == "34.5"


def test_decimal_shoe_window_keeps_33_and_46_outside_shop():
    shop = {"33.0": [], "46.0": []}
    rows = decimal_shoe_window(shop)
    assert rows == (
        Example("33.0", "33", "dropped"),
        Example("46.0", "46", "dropped"),
    )
    assert decimal_shoe_window({"33.0": ["33"], "46.0": ["46"]}) == ()


def test_dual_cost_notes_shop_yen_preference_without_a_new_price():
    split = dual_cost_findings(
        {"dualUsdLanded": "17.5", "dualCnyLanded": "22.374"},
        {"dualShopLanded": "22.374"},
    )
    assert [item.severity for item in split] == ["boss"]
    assert split[0].code == "shop-prefers-yen"
    assert split[0].examples == (Example("Q", "17.50", "22.37"),)
    assert dual_cost_findings(
        {"dualUsdLanded": "17.5", "dualCnyLanded": "22.374"},
        {"dualShopLanded": "17.5"},
    ) == []
    broken = dual_cost_findings(
        {"dualUsdLanded": "17.5", "dualCnyLanded": "22.374"},
        {"dualShopLanded": "30"},
    )
    assert broken[0].severity == "fail"
    assert broken[0].code == "dual-cost-landed"
    missing = dual_cost_findings({}, {})
    assert missing[0].code == "dual-cost-landed"


def test_import_size_flags_a_dropped_shoe_token():
    clean = {
        "importShoe": ["40", "35", "36"],
        "importEdge": ["42"],
        "importClothing": ["S"],
        "importKindO": ["M"],
    }
    assert [item.code for item in import_size_findings(clean)] == ["import-kind-o"]
    dropped = dict(clean)
    dropped["importShoe"] = ["35", "36"]
    misses = import_size_findings(dropped)
    assert misses[0].severity == "fail"
    assert misses[0].code == "import-shoe-size"
    kept_o = dict(clean)
    kept_o["importKindO"] = ["36", "M"]
    assert import_size_findings(kept_o) == []


def test_intake_decimal_flags_a_dropped_trailing_zero():
    tokens = ("40.0", "34.0", "42.0", "40.00", "35", "S")
    shoe = ("35", "36", "37", "38", "39", "40", "41")
    assert intake_g_decimal_expected(tokens, shoe) == ("40", "35")
    clean = {"keepGDecimal": ["40", "35"], "keepADecimal": ["S"], "decimalChips": list(tokens)}
    assert intake_decimal_findings(clean, tokens, shoe) == []
    dropped = dict(clean)
    dropped["keepGDecimal"] = ["35"]
    rows = intake_decimal_findings(dropped, tokens, shoe)
    assert rows[0].severity == "fail"
    assert rows[0].code == "intake-shoe-decimal"
    assert rows[0].examples[0].key == "G"


def test_quote_examples_flag_a_planted_tier_mismatch():
    rows = quote_examples({"1.00": 4}, {"1.00": 4}, {"1.00": 5})
    assert rows == (Example("1.00", "4", "shared 4; intake 5"),)
    assert quote_examples({"30.00": 42}, {"30.00": 42}, {"30.00": 42}) == ()


def test_repo_has_no_code_fails(report):
    assert report.code_fails() == ()


def test_repo_reports_the_known_boss_splits(report):
    codes = {item.code for item in report.boss_notes()}
    missing = [code for code in BOSS_CODES if code not in codes]
    assert missing == []
    by_code = {item.code: item for item in report.findings}
    assert all(item.severity == "boss" for item in report.boss_notes())
    assert any(example.key == "A03" for example in by_code["seed-vs-live-price"].examples)
    assert any(example.key == "S06" and example.left == "26" and example.right == "25"
               for example in by_code["extras-s06-lock"].examples)
    assert any(example.key == "S06" for example in by_code["seed-missing-live"].examples)
    assert any(example.key == "K003" and example.left == "K03" and example.right == "K003"
               for example in by_code["shop-normalize-no-pad"].examples)
    assert any(example.key == "D" for example in by_code["excel-letter-gap"].examples)
    assert any(
        example.key == "33.0" and example.left == "33" and example.right == "dropped"
        for example in by_code["shoe-decimal-window"].examples
    )
    assert any(
        example.key == "40.0" and example.left == "shop keeps 40"
        for example in by_code["shop-parse-ignores-kind"].examples
    )
    assert "shoe-decimal" not in codes
    assert "dual-cost-landed" not in codes
    assert "import-shoe-size" not in codes
    assert "intake-shoe-decimal" not in codes
    assert any(
        example.key == "O" and example.left == "autolist keeps 36" and example.right == "import drops 36"
        for example in by_code["import-kind-o"].examples
    )
    yen = by_code["shop-prefers-yen"]
    assert yen.examples[0].key == "Q"
    assert yen.examples[0].left == "17.50"
    assert yen.examples[0].right == "22.37"


def test_snapshot_copies_agree(report):
    codes = {item.code for item in report.findings}
    assert "snapshot-vs-drift" not in codes
    assert "snapshot-vs-fixture" not in codes
    assert "taobao-seed-copy" not in codes
    assert "live-s06-lock" not in codes
    assert "duplicate-ma" not in codes


def test_cli_json_matches_the_report_and_writes_nothing(report, capsys):
    before = {path: path.read_bytes() for path in WATCHED}
    code = main(["--json"])
    after = {path: path.read_bytes() for path in WATCHED}
    assert code == 0
    assert after == before
    payload = json.loads(capsys.readouterr().out)
    assert payload["codeFails"] == report.to_json()["codeFails"]
    assert payload["boss"] == len(report.boss_notes())
    text = render_text(report)
    assert text.startswith("code fails: 0\n")
    assert "held.json not changed" in text


def test_strict_exits_when_boss_notes_exist():
    before = HELD.read_bytes()
    code = main(["--strict"])
    assert code == 1
    assert HELD.read_bytes() == before


def test_checker_source_has_no_write_or_network_calls():
    source = (ROOT / "scripts" / "parity_check.py").read_text(encoding="utf-8")
    for token in (
        "write_text",
        "write_bytes",
        "urlopen",
        "urllib",
        "urlretrieve",
        "mkdir",
        "unlink",
        "requests",
        "open(",
    ):
        assert token not in source
