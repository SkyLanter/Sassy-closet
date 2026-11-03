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
    disallowed_size_tokens,
    dollar_text,
    gap_alias_findings,
    gap_size_findings,
    gap_split_findings,
    dual_cost_findings,
    import_size_findings,
    intake_decimal_findings,
    intake_g_decimal_expected,
    loose_shoe_findings,
    main,
    quote_width_findings,
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
    "shop-loose-shoe",
    "quote-ma-width",
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


def test_gap_report_accepts_a_trailing_zero_inside_the_shoe_list():
    shoe = ("35", "36", "37", "38", "39", "40", "41")
    assert disallowed_size_tokens("40.0 35", shoe) == []
    assert disallowed_size_tokens("34.0", shoe) == ["34.0"]
    assert disallowed_size_tokens("42.0", shoe) == ["42.0"]
    assert disallowed_size_tokens("40.00", shoe) == ["40.00"]
    assert disallowed_size_tokens("40.0", ("S", "M")) == ["40.0"]
    assert gap_size_findings(shoe) == []
    assert gap_size_findings(())[0].code == "gap-shoe-decimal"


def test_gap_report_splits_sizes_on_the_same_separators_as_listing():
    shoe = ("35", "36", "37", "38", "39", "40", "41")
    assert disallowed_size_tokens("35;36", shoe) == []
    assert disallowed_size_tokens("40.0;35", shoe) == []
    assert disallowed_size_tokens("35;36|37/38,40.0", shoe) == []
    assert disallowed_size_tokens("35;44", shoe) == ["44"]
    assert disallowed_size_tokens("S;M", ("S", "M")) == []
    assert disallowed_size_tokens("S;99", ("S", "M")) == ["99"]
    assert gap_split_findings(shoe) == []
    assert gap_split_findings(())[0].code == "gap-size-split"


def test_gap_report_accepts_listing_size_aliases():
    clothing = ("2XS", "XS", "S", "M", "L", "XL", "2XL")
    shoe = ("35", "36", "37", "38", "39", "40", "41")
    assert disallowed_size_tokens("XXS 3XL;XXL", clothing) == []
    assert disallowed_size_tokens("xxl", clothing) == []
    assert disallowed_size_tokens("4XL", clothing) == ["4XL"]
    assert disallowed_size_tokens("XXS", ("S", "M")) == ["XXS"]
    assert disallowed_size_tokens("XXL", ("S", "M")) == ["XXL"]
    assert disallowed_size_tokens("XXS", shoe) == ["XXS"]
    assert gap_alias_findings(clothing) == []
    assert gap_alias_findings(())[0].code == "gap-size-alias"


def test_quote_width_rejects_a_canonical_three_digit_ma_and_an_overpad():
    rejected = {"ok": False, "error": "invalid"}
    rows = quote_width_findings({"A100": rejected, "K003": rejected})
    assert [item.severity for item in rows] == ["boss"]
    assert rows[0].code == "quote-ma-width"
    assert rows[0].examples == (
        Example("A100", "A100", "rejected"),
        Example("K003", "K03", "rejected"),
    )
    accepted = quote_width_findings({
        "A100": {"ok": True, "ma": "A100"},
        "K003": rejected,
    })
    assert accepted[0].severity == "fail"
    assert accepted[0].code == "quote-ma-width"
    assert accepted[0].examples == (Example("A100", "A100", "A100"),)
    assert quote_width_findings({})[0].severity == "fail"


def test_loose_shoe_notes_the_shop_and_listing_split():
    split = {
        "40.": ["40"],
        "40码": ["40"],
        "(40)": ["40"],
        "4.0": ["40"],
        "36 -37(适合平时35-36码)": [],
    }
    rows = loose_shoe_findings(split)
    assert [item.severity for item in rows] == ["boss"]
    assert rows[0].code == "shop-loose-shoe"
    assert rows[0].examples == (
        Example("40.", "dropped", "40"),
        Example("40码", "dropped", "40"),
        Example("(40)", "dropped", "40"),
        Example("4.0", "dropped", "40"),
        Example("range", "36", "dropped"),
    )
    agreed = {
        "40.": [],
        "40码": [],
        "(40)": [],
        "4.0": [],
        "36 -37(适合平时35-36码)": ["36"],
    }
    assert loose_shoe_findings(agreed) == []
    assert loose_shoe_findings({})[0].severity == "fail"
    assert loose_shoe_findings({})[0].code == "shop-loose-shoe"


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
    assert "gap-shoe-decimal" not in codes
    assert "gap-size-split" not in codes
    assert "gap-size-alias" not in codes
    assert any(
        example.key == "O" and example.left == "autolist keeps 36" and example.right == "import drops 36"
        for example in by_code["import-kind-o"].examples
    )
    yen = by_code["shop-prefers-yen"]
    assert yen.examples[0].key == "Q"
    assert yen.examples[0].left == "17.50"
    assert yen.examples[0].right == "22.37"
    loose = by_code["shop-loose-shoe"]
    assert loose.severity == "boss"
    assert loose.examples[0].key == "40."
    assert loose.examples[0].left == "dropped"
    assert loose.examples[0].right == "40"
    assert any(example.key == "4.0" and example.left == "dropped" and example.right == "40"
               for example in loose.examples)
    assert any(example.key == "range" and example.left == "36" and example.right == "dropped"
               for example in loose.examples)
    width = by_code["quote-ma-width"]
    assert width.severity == "boss"
    assert width.examples == (
        Example("A100", "A100", "rejected"),
        Example("K003", "K03", "rejected"),
    )


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
