"""HTTP shop-link flags from fixtures. Stored links, prices, and held.json stay put."""

from __future__ import annotations

import copy
import io
import json
import subprocess
import sys
from contextlib import redirect_stderr
from pathlib import Path

from http_shop_link_flags import (
    LinkFlag,
    flag_http_shop_links,
    load_rows,
    main,
)

ROOT = Path(__file__).resolve().parents[2]
HELD = ROOT / "data" / "held.json"
PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"
EXTRAS = ROOT / "sassy-closet-shop" / "data" / "intake-extras.json"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
CLEAN = FIXTURES / "shop_link_https_clean.json"
HTTP = FIXTURES / "shop_link_https_http.json"
HELD_BYTES = HELD.read_bytes()
PRODUCTS_BYTES = PRODUCTS.read_bytes()
EXTRAS_BYTES = EXTRAS.read_bytes()
CLEAN_BYTES = CLEAN.read_bytes()
HTTP_BYTES = HTTP.read_bytes()
HTTP_LINK = "http://e.tb.cn/h.httpShopLink"
HTTP_UPPER = "HTTP://item.taobao.com/item.htm?id=123456789012"
S06_HTTPS = "https://e.tb.cn/h.8sN0OlfvL4eWjAz?tk=P0HOTjnnu3L"


def test_http_link_is_flagged_and_not_rewritten() -> None:
    row = {"ma": "z81", "link": HTTP_LINK}
    flags = flag_http_shop_links([row]).flags
    assert row == {"ma": "z81", "link": HTTP_LINK}
    assert flags == (LinkFlag("Z81", "http_link", "link", HTTP_LINK),)
    assert set(flags[0].as_json()) == {"ma", "kind", "field", "stored"}
    assert "https://e.tb.cn/h.httpShopLink" not in flags[0].stored


def test_blank_link_stays_blank() -> None:
    blank = {"ma": "V05", "link": ""}
    spaces = {"ma": "Z83", "link": "  \n\t"}
    missing = {"ma": "Z80"}
    null_row = {"ma": "Z84", "link": None}
    other_field = {"ma": "Z70", "link": "", "source_link": HTTP_LINK}
    rows = [blank, spaces, missing, null_row, other_field]
    before = copy.deepcopy(rows)
    report = flag_http_shop_links(rows)
    assert rows == before
    assert report.flags == ()
    assert [row.scheme for row in report.rows] == ["blank", "blank", "blank", "blank", "blank"]
    assert [row.stored for row in report.rows] == ["", "  \n\t", "", "", ""]
    assert "link" not in missing


def test_https_and_lookalikes_are_not_http() -> None:
    rows = [
        {"ma": "S06", "sell_usd": "25", "link": S06_HTTPS},
        {"ma": "Z85", "link": "https://example.com/shop?next=http://insecure.example/item"},
        {"ma": "Z88", "link": "HTTPS://e.tb.cn/h.Upper"},
        {"ma": "Z89", "link": "https://http.example/item"},
        {"ma": "A01", "sourceLink": "https://e.tb.cn/h.8KCQeaHH3dz1iSl?tk=WeuOTTBXHOu"},
    ]
    before = copy.deepcopy(rows)
    report = flag_http_shop_links(rows)
    assert rows == before
    assert report.flags == ()
    assert report.rows[0].sell_usd == "25"
    assert report.rows[0].scheme == "https"
    assert [row.scheme for row in report.rows] == ["https", "https", "https", "https", "https"]


def test_s06_http_link_keeps_25_and_the_stored_text() -> None:
    row = {"ma": "S06", "sell_usd": "25", "priceUsd": 25, "link": "http://shop.example/s06"}
    before = copy.deepcopy(row)
    report = flag_http_shop_links([row])
    assert row == before
    assert row["sell_usd"] == "25"
    assert row["priceUsd"] == 25
    assert row["link"] == "http://shop.example/s06"
    assert report.rows[0].sell_usd == "25"
    assert report.flags == (LinkFlag("S06", "http_link", "link", "http://shop.example/s06"),)
    assert "https://shop.example/s06" not in report.flags[0].stored


def test_catalog_price_stays_on_the_row(tmp_path: Path) -> None:
    raw = {
        "products": [
            {"ma": "S06", "priceUsd": 25, "sourceLink": "http://shop.example/s06"},
        ]
    }
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = load_rows(payload)
    report = flag_http_shop_links(rows)
    assert rows[0]["priceUsd"] == 25
    assert rows[0]["sourceLink"] == "http://shop.example/s06"
    assert report.rows[0].sell_usd == "25"
    assert report.flags == (LinkFlag("S06", "http_link", "sourceLink", "http://shop.example/s06"),)
    assert path.read_text(encoding="utf-8") == json.dumps(raw)


def test_gap_fixture_flags_http_and_leaves_s06_and_blanks() -> None:
    payload = json.loads(HTTP.read_text(encoding="utf-8"))
    before = copy.deepcopy(payload)
    rows = load_rows(payload)
    report = flag_http_shop_links(rows)
    by_ma = {row.ma: row for row in report.rows}
    assert payload == before
    assert [flag.ma for flag in report.flags] == ["Z81", "Z82", "Z86"]
    assert report.flags[0].stored == HTTP_LINK
    assert report.flags[1].stored == HTTP_UPPER
    assert report.flags[2] == LinkFlag("Z86", "http_link", "sourceLink", "http://shop.example/item")
    assert by_ma["S06"].sell_usd == "25"
    assert by_ma["S06"].stored == S06_HTTPS
    assert by_ma["S06"].scheme == "https"
    assert by_ma["V05"].stored == ""
    assert by_ma["Z83"].stored == "   "
    assert by_ma["Z84"].stored == ""
    assert by_ma["Z70"].stored == ""
    assert by_ma["Z70"].flags == ()
    assert payload["submissions"][7]["link"] == ""
    assert payload["submissions"][7]["source_link"] == "http://e.tb.cn/h.hidden"
    assert by_ma["Z85"].scheme == "https"
    assert by_ma["A01"].sell_usd == "27"
    assert HTTP.read_bytes() == HTTP_BYTES
    assert HELD.read_bytes() == HELD_BYTES
    assert PRODUCTS.read_bytes() == PRODUCTS_BYTES
    assert EXTRAS.read_bytes() == EXTRAS_BYTES


def test_clean_fixture_accepts_https_and_blank_links() -> None:
    payload = json.loads(CLEAN.read_text(encoding="utf-8"))
    before = copy.deepcopy(payload)
    report = flag_http_shop_links(load_rows(payload))
    assert payload == before
    assert report.flag_count == 0
    assert report.rows[0].ma == "S06"
    assert report.rows[0].sell_usd == "25"
    assert report.rows[0].stored == S06_HTTPS
    blank = {row.ma: row.stored for row in report.rows if row.scheme == "blank"}
    assert blank == {"V05": "", "Z83": "   ", "Z84": ""}
    assert CLEAN.read_bytes() == CLEAN_BYTES
    assert HELD.read_bytes() == HELD_BYTES


def test_cli_writes_a_report_and_leaves_shop_files(tmp_path: Path) -> None:
    gap_out = tmp_path / "gap"
    gap = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "http_shop_link_flags.py"),
            "--fixture",
            str(HTTP),
            "--out",
            str(gap_out),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert gap.returncode == 1, gap.stderr
    assert gap.stderr == ""
    assert "HTTP shop link flags: 3" in gap.stdout
    report = json.loads((gap_out / "http-shop-link-flags.json").read_text(encoding="utf-8"))
    markdown = (gap_out / "http-shop-link-flags.md").read_text(encoding="utf-8")
    assert report["readOnly"] is True
    assert report["rewritten"] is False
    assert report["links"] == "unchanged"
    assert report["s06SellUsd"] == "25"
    assert report["flagCount"] == 3
    assert [flag["stored"] for flag in report["flags"]] == [
        HTTP_LINK,
        HTTP_UPPER,
        "http://shop.example/item",
    ]
    assert "https://e.tb.cn/h.httpShopLink" not in markdown
    assert "https://shop.example/item" not in markdown
    assert HTTP_LINK in markdown
    assert HTTP_UPPER in markdown
    s06 = next(row for row in report["rows"] if row["ma"] == "S06")
    assert s06["sellUsd"] == "25"
    assert s06["stored"] == S06_HTTPS
    blanks = [row for row in report["rows"] if row["scheme"] == "blank"]
    assert [row["stored"] for row in blanks] == ["", "   ", "", ""]
    assert HTTP.read_bytes() == HTTP_BYTES
    assert CLEAN.read_bytes() == CLEAN_BYTES
    assert HELD.read_bytes() == HELD_BYTES
    assert PRODUCTS.read_bytes() == PRODUCTS_BYTES
    assert EXTRAS.read_bytes() == EXTRAS_BYTES

    clean_out = tmp_path / "clean"
    clean = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "http_shop_link_flags.py"),
            "--fixture",
            str(CLEAN),
            "--out",
            str(clean_out),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert clean.returncode == 0, clean.stderr
    clean_report = json.loads((clean_out / "http-shop-link-flags.json").read_text(encoding="utf-8"))
    assert clean_report["flagCount"] == 0
    assert clean_report["s06SellUsd"] == "25"
    assert clean_report["rewritten"] is False
    assert CLEAN.read_bytes() == CLEAN_BYTES
    assert HELD.read_bytes() == HELD_BYTES


def test_cli_refuses_live_catalog_held_and_urls(tmp_path: Path) -> None:
    out = tmp_path / "out"
    products_before = PRODUCTS.read_bytes()
    held_before = HELD.read_bytes()
    extras_before = EXTRAS.read_bytes()
    for target in (
        str(PRODUCTS),
        str(HELD),
        str(EXTRAS),
        str(ROOT / "data"),
        "https://sassy-closet-shop.vercel.app/m/S06",
    ):
        code, err = _run_main(["--fixture", target, "--out", str(out)])
        assert code == 2
        assert "fixtures only" in err
        assert not out.exists()
    code, err = _run_main(["--fixture", str(CLEAN), "--out", str(ROOT / "data")])
    assert code == 2
    assert "fixtures only" in err
    code, err = _run_main(["--fixture", str(CLEAN), "--out", str(HELD)])
    assert code == 2
    assert "fixtures only" in err
    assert PRODUCTS.read_bytes() == products_before == PRODUCTS_BYTES
    assert HELD.read_bytes() == held_before == HELD_BYTES
    assert EXTRAS.read_bytes() == extras_before == EXTRAS_BYTES
    assert CLEAN.read_bytes() == CLEAN_BYTES


def test_cli_rejects_bad_and_missing_files(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("{", encoding="utf-8")
    code, err = _run_main(["--fixture", str(path), "--out", str(tmp_path / "out")])
    assert code == 2
    assert err
    assert path.read_text(encoding="utf-8") == "{"
    missing = tmp_path / "missing.json"
    code, err = _run_main(["--fixture", str(missing), "--out", str(tmp_path / "missing-out")])
    assert code == 2
    assert "Fixture not found" in err
    assert not missing.exists()
    bad = tmp_path / "shape.json"
    bad.write_text(json.dumps([{"link": HTTP_LINK}]), encoding="utf-8")
    code, err = _run_main(["--fixture", str(bad), "--out", str(tmp_path / "shape-out")])
    assert code == 2
    assert "mã" in err
    assert bad.read_text(encoding="utf-8") == json.dumps([{"link": HTTP_LINK}])
    assert HELD.read_bytes() == HELD_BYTES


def test_script_is_fixture_only() -> None:
    text = (ROOT / "scripts" / "http_shop_link_flags.py").read_text(encoding="utf-8")
    lowered = text.lower()
    for banned in (
        "urllib",
        "requests",
        "http.client",
        "held_policy",
        "intake_shop_link_flags",
        "open(",
    ):
        assert banned not in lowered
    assert "held.json" in text
    assert "replace(\"http" not in lowered
    assert "https://" not in text.replace("rather than https", "")


def _run_main(argv: list[str]) -> tuple[int, str]:
    err = io.StringIO()
    with redirect_stderr(err):
        code = main(argv)
    return code, err.getvalue()
