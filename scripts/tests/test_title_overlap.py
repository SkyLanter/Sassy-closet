"""Title overlap from fixtures. Rows stay separate. held.json stays put."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from title_overlap import CatalogRow, flag_title_overlap, main, normalize_title

ROOT = Path(__file__).resolve().parents[2]
HELD = ROOT / "data" / "held.json"
HELD_BYTES = HELD.read_bytes()

DRESS = "Apricot ruched lace mini dress"
DRESS_VN = "Đầm ren nhún apricot"


def test_normalize_folds_case_hyphen_and_vietnamese() -> None:
    assert normalize_title("Apricot   ruched lace mini-dress") == normalize_title(DRESS)
    assert normalize_title(DRESS_VN) == "dam ren nhun apricot"
    assert normalize_title("Áo len puppy") == "ao len puppy"


def test_d05_like_rows_share_a_dress_title_and_stay_two_codes() -> None:
    live = CatalogRow("D05", DRESS, DRESS_VN, 26)
    twin = CatalogRow("d06", "apricot   ruched lace mini-dress", DRESS_VN, 28)
    rows = [live, twin]
    flags = flag_title_overlap(rows)
    assert [row.ma for row in rows] == ["D05", "d06"]
    assert live.price_usd == 26
    assert twin.price_usd == 28
    assert len(rows) == 2
    exact = [flag for flag in flags if flag.kind == "exact"]
    assert [(flag.mas, flag.field) for flag in exact] == [
        (("D05", "D06"), "titleEn"),
        (("D05", "D06"), "titleVn"),
    ]
    assert exact[0].titles == (DRESS, "apricot   ruched lace mini-dress")
    assert all("priceUsd" not in flag.as_json() for flag in flags)


def test_near_dress_title_is_flagged_without_merging() -> None:
    rows = [
        CatalogRow("D05", DRESS, DRESS_VN, 26),
        CatalogRow("D07", "Apricot ruched lace minidress", "Đầm ren nhún apricot mini", 30),
    ]
    flags = flag_title_overlap(rows)
    assert {row.ma for row in rows} == {"D05", "D07"}
    assert [row.price_usd for row in rows] == [26, 30]
    near = [flag for flag in flags if flag.kind == "near"]
    assert len(near) == 1
    assert near[0].mas == ("D05", "D07")
    assert near[0].field == "titleEn"
    assert near[0].titles == (DRESS, "Apricot ruched lace minidress")


def test_distinct_titles_and_same_ma_are_not_title_flags() -> None:
    rows = [
        CatalogRow("S06", "Washed distressed overalls", "Yếm wash rách", 25),
        CatalogRow("D05", DRESS, DRESS_VN, 26),
        CatalogRow("D01", "Pink WITHMIN dress", "Đầm hồng WITHMIN", 46),
        CatalogRow("D02", "White WITHMIN dress", "Đầm trắng WITHMIN", 46),
        CatalogRow("D08", "Black ruched lace mini dress", "Đầm ren nhún đen", 27),
        CatalogRow("D05", DRESS, DRESS_VN, 26),
    ]
    assert flag_title_overlap(rows) == []
    assert rows[0].price_usd == 25
    assert [row.ma for row in rows].count("D05") == 2


def test_s06_near_title_keeps_25_and_held_json_stays() -> None:
    before = HELD.read_bytes()
    assert before == HELD_BYTES
    s06 = CatalogRow("S06", "Washed distressed overalls", "Yếm wash rách", 25)
    other = CatalogRow("S08", "Washed distressed overall", "Yếm wash khác", 40)
    held = CatalogRow("K06", "Sample held jacket", "Áo khoác giữ", 50)
    twin = CatalogRow("K07", "Sample held jacket", "Áo khoác giữ", 51)
    rows = [s06, other, held, twin]
    flags = flag_title_overlap(rows)
    assert s06.price_usd == 25
    assert other.price_usd == 40
    assert held.price_usd == 50
    assert [row.ma for row in rows] == ["S06", "S08", "K06", "K07"]
    found = {(flag.mas, flag.field, flag.kind) for flag in flags}
    assert (("S06", "S08"), "titleEn", "near") in found
    assert (("K06", "K07"), "titleEn", "exact") in found
    assert (("K06", "K07"), "titleVn", "exact") in found
    assert HELD.read_bytes() == HELD_BYTES


def test_cli_reports_fixture_and_does_not_write(tmp_path: Path) -> None:
    catalog = {
        "products": [
            {
                "ma": "D05",
                "titleEn": DRESS,
                "titleVn": DRESS_VN,
                "priceUsd": 26,
            },
            {
                "ma": "D06",
                "titleEn": DRESS,
                "titleVn": DRESS_VN,
                "priceUsd": 31,
            },
            {
                "ma": "S06",
                "titleEn": "Washed distressed overalls",
                "titleVn": "Yếm wash rách",
                "priceUsd": 25,
            },
        ]
    }
    path = tmp_path / "catalog.json"
    raw = json.dumps(catalog, ensure_ascii=False, indent=2)
    path.write_text(raw, encoding="utf-8")
    before_held = HELD.read_bytes()
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "title_overlap.py"), "--catalog", str(path)],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stderr == ""
    report = json.loads(result.stdout)
    assert report["readOnly"] is True
    assert report["rows"] == 3
    assert report["flags"] == [
        {
            "mas": ["D05", "D06"],
            "field": "titleEn",
            "kind": "exact",
            "titles": [DRESS, DRESS],
        },
        {
            "mas": ["D05", "D06"],
            "field": "titleVn",
            "kind": "exact",
            "titles": [DRESS_VN, DRESS_VN],
        },
    ]
    assert "priceUsd" not in result.stdout
    assert path.read_text(encoding="utf-8") == raw
    assert list(tmp_path.iterdir()) == [path]
    assert HELD.read_bytes() == before_held == HELD_BYTES


def test_cli_rejects_a_bad_catalog(tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"
    path.write_text("{", encoding="utf-8")
    assert main(["--catalog", str(path)]) == 2
    assert path.read_text(encoding="utf-8") == "{"
