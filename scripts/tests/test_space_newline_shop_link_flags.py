"""Space and newline shop-link flags from fixtures. Stored links, prices, and held.json stay put."""

from __future__ import annotations

import copy
import io
import json
import subprocess
import sys
from contextlib import redirect_stderr
from pathlib import Path

from space_newline_shop_link_flags import (
    LinkFlag,
    flag_space_newline_shop_links,
    load_rows,
    main,
)

ROOT = Path(__file__).resolve().parents[2]
HELD = ROOT / "data" / "held.json"
PRODUCTS = ROOT / "sassy-closet-shop" / "data" / "products.json"
EXTRAS = ROOT / "sassy-closet-shop" / "data" / "intake-extras.json"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
CLEAN = FIXTURES / "shop_link_space_clean.json"
GAPS = FIXTURES / "shop_link_space_newline.json"
HELD_BYTES = HELD.read_bytes()
PRODUCTS_BYTES = PRODUCTS.read_bytes()
EXTRAS_BYTES = EXTRAS.read_bytes()
CLEAN_BYTES = CLEAN.read_bytes()
GAPS_BYTES = GAPS.read_bytes()
S06_HTTPS = "https://e.tb.cn/h.8sN0OlfvL4eWjAz?tk=P0HOTjnnu3L"
SPACE_LINK = "https://e.tb.cn/h.space Link"
NEWLINE_LINK = "https://item.taobao.com/item.htm?id=123456789012\n"
BOTH_LINK = "https://shop.example/item with space\nand newline"
CR_LINK = "https://e.tb.cn/h.cr\rLink"
HIDDEN_SPACE = "https://e.tb.cn/h.hidden space"


def test_space_link_is_flagged_and_not_rewritten() -> None:
    rows = [
        {"ma": "z81", "link": SPACE_LINK},
        {"ma": "Z91", "link": " https://e.tb.cn/h.lead"},
        {"ma": "Z92", "link": "https://e.tb.cn/h.trail "},
    ]
    before = copy.deepcopy(rows)
    flags = flag_space_newline_shop_links(rows).flags
    assert rows == before
    assert flags == (
        LinkFlag("Z81", "space", "link", SPACE_LINK),
        LinkFlag("Z91", "space", "link", " https://e.tb.cn/h.lead"),
        LinkFlag("Z92", "space", "link", "https://e.tb.cn/h.trail "),
    )
    assert flags[1].stored.startswith(" ")
    assert flags[2].stored.endswith(" ")
    for flag in flags:
        assert set(flag.as_json()) == {"ma", "kind", "field", "stored"}
        assert "%20" not in flag.stored
        assert " " in flag.stored


def test_newline_link_is_flagged_and_not_rewritten() -> None:
    wrapped = "https://item.taobao.com/item.htm?id=123\r\n456"
    leading = "\nhttps://e.tb.cn/h.lead"
    rows = [
        {"ma": "Z82", "link": NEWLINE_LINK},
        {"ma": "Z87", "link": CR_LINK},
        {"ma": "Z93", "link": wrapped},
        {"ma": "Z94", "link": leading},
    ]
    before = copy.deepcopy(rows)
    flags = flag_space_newline_shop_links(rows).flags
    assert rows == before
    assert flags == (
        LinkFlag("Z82", "newline", "link", NEWLINE_LINK),
        LinkFlag("Z87", "newline", "link", CR_LINK),
        LinkFlag("Z93", "newline", "link", wrapped),
        LinkFlag("Z94", "newline", "link", leading),
    )
    assert flags[0].stored.endswith("\n")
    assert "\r" in flags[1].stored
    assert "\r\n" in flags[2].stored
    assert flags[3].stored.startswith("\n")
    for flag in flags:
        assert "%0a" not in flag.stored.lower()


def test_space_and_newline_together_keep_both_characters() -> None:
    row = {"ma": "Z86", "sourceLink": BOTH_LINK}
    before = copy.deepcopy(row)
    report = flag_space_newline_shop_links([row])
    assert row == before
    assert report.flags == (LinkFlag("Z86", "space_and_newline", "sourceLink", BOTH_LINK),)
    assert " " in report.flags[0].stored
    assert "\n" in report.flags[0].stored
    assert report.flags[0].stored == BOTH_LINK
    assert "https://shop.example/item%20with%20space" not in report.flags[0].stored


def test_blank_link_stays_blank() -> None:
    blank = {"ma": "V05", "link": ""}
    spaces = {"ma": "Z83", "link": "  \n\t"}
    only_newline = {"ma": "Z88", "link": "\n"}
    missing = {"ma": "Z80"}
    null_row = {"ma": "Z84", "link": None}
    other_field = {"ma": "Z70", "link": "", "source_link": HIDDEN_SPACE}
    later_field = {"ma": "Z71", "source_link": " \r ", "sourceLink": SPACE_LINK}
    rows = [blank, spaces, only_newline, missing, null_row, other_field, later_field]
    before = copy.deepcopy(rows)
    report = flag_space_newline_shop_links(rows)
    assert rows == before
    assert report.flags == ()
    assert [row.mark for row in report.rows] == ["blank"] * len(rows)
    assert [row.stored for row in report.rows] == ["", "  \n\t", "\n", "", "", "", " \r "]
    assert "link" not in missing
    assert other_field["source_link"] == HIDDEN_SPACE
    assert later_field["sourceLink"] == SPACE_LINK


def test_encoded_and_plain_links_are_not_flagged() -> None:
    tabbed = "https://e.tb.cn/h.tab\tLink"
    rows = [
        {"ma": "S06", "sell_usd": "25", "link": S06_HTTPS},
        {"ma": "Z89", "link": "https://e.tb.cn/h.encoded%20space"},
        {"ma": "Z95", "link": "https://e.tb.cn/h.encoded%0Aline"},
        {"ma": "Z96", "link": "https://example.com/space-and-newline"},
        {"ma": "Z97", "link": tabbed},
        {"ma": "A01", "sourceLink": "https://e.tb.cn/h.8KCQeaHH3dz1iSl?tk=WeuOTTBXHOu"},
    ]
    before = copy.deepcopy(rows)
    report = flag_space_newline_shop_links(rows)
    assert rows == before
    assert report.flags == ()
    assert report.rows[0].sell_usd == "25"
    assert report.rows[0].mark == "clean"
    assert report.rows[4].stored == tabbed
    assert [row.mark for row in report.rows] == ["clean"] * len(rows)


def test_s06_spaced_link_keeps_25_and_the_stored_text() -> None:
    link = "https://shop.example/s06 item"
    row = {"ma": "S06", "sell_usd": "25", "priceUsd": 25, "link": link}
    before = copy.deepcopy(row)
    report = flag_space_newline_shop_links([row])
    assert row == before
    assert row["sell_usd"] == "25"
    assert row["priceUsd"] == 25
    assert row["link"] == link
    assert report.rows[0].sell_usd == "25"
    assert report.flags == (LinkFlag("S06", "space", "link", link),)
    assert "https://shop.example/s06%20item" not in report.flags[0].stored
    assert "https://shop.example/s06item" not in report.flags[0].stored


def test_catalog_price_stays_on_the_row(tmp_path: Path) -> None:
    link = "https://shop.example/s06\nitem"
    raw = {
        "products": [
            {"ma": "S06", "priceUsd": 25, "sourceLink": link},
        ]
    }
    path = tmp_path / "catalog.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = load_rows(payload)
    report = flag_space_newline_shop_links(rows)
    assert rows[0]["priceUsd"] == 25
    assert rows[0]["sourceLink"] == link
    assert report.rows[0].sell_usd == "25"
    assert report.flags == (LinkFlag("S06", "newline", "sourceLink", link),)
    assert path.read_text(encoding="utf-8") == json.dumps(raw)
    assert HELD.read_bytes() == HELD_BYTES
    assert PRODUCTS.read_bytes() == PRODUCTS_BYTES
    assert EXTRAS.read_bytes() == EXTRAS_BYTES


def test_gap_fixture_flags_space_or_newline_and_leaves_s06_and_blanks() -> None:
    payload = json.loads(GAPS.read_text(encoding="utf-8"))
    before = copy.deepcopy(payload)
    rows = load_rows(payload)
    report = flag_space_newline_shop_links(rows)
    by_ma = {row.ma: row for row in report.rows}
    assert payload == before
    assert [(flag.ma, flag.kind, flag.stored) for flag in report.flags] == [
        ("Z81", "space", SPACE_LINK),
        ("Z82", "newline", NEWLINE_LINK),
        ("Z86", "space_and_newline", BOTH_LINK),
        ("Z87", "newline", CR_LINK),
    ]
    assert by_ma["S06"].sell_usd == "25"
    assert by_ma["S06"].stored == S06_HTTPS
    assert by_ma["S06"].mark == "clean"
    assert by_ma["S06"].flags == ()
    assert by_ma["V05"].stored == ""
    assert by_ma["Z83"].stored == "   "
    assert by_ma["Z84"].stored == ""
    assert by_ma["Z88"].stored == "\n"
    assert by_ma["Z88"].mark == "blank"
    assert by_ma["Z70"].stored == ""
    assert by_ma["Z70"].flags == ()
    assert payload["submissions"][6]["link"] == ""
    assert payload["submissions"][6]["source_link"] == HIDDEN_SPACE
    assert by_ma["Z89"].mark == "clean"
    assert by_ma["A01"].sell_usd == "27"
    assert GAPS.read_bytes() == GAPS_BYTES
    assert HELD.read_bytes() == HELD_BYTES
    assert PRODUCTS.read_bytes() == PRODUCTS_BYTES
    assert EXTRAS.read_bytes() == EXTRAS_BYTES


def test_clean_fixture_accepts_plain_and_blank_links() -> None:
    payload = json.loads(CLEAN.read_text(encoding="utf-8"))
    before = copy.deepcopy(payload)
    report = flag_space_newline_shop_links(load_rows(payload))
    assert payload == before
    assert report.flag_count == 0
    assert report.rows[0].ma == "S06"
    assert report.rows[0].sell_usd == "25"
    assert report.rows[0].stored == S06_HTTPS
    blank = {row.ma: row.stored for row in report.rows if row.mark == "blank"}
    assert blank == {"V05": "", "Z83": "   ", "Z84": ""}
    assert CLEAN.read_bytes() == CLEAN_BYTES
    assert HELD.read_bytes() == HELD_BYTES


def test_cli_writes_a_report_and_leaves_shop_files(tmp_path: Path) -> None:
    gap_out = tmp_path / "gap"
    gap = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "space_newline_shop_link_flags.py"),
            "--fixture",
            str(GAPS),
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
    assert "Shop link space or newline flags: 4" in gap.stdout
    report = json.loads((gap_out / "space-newline-shop-link-flags.json").read_text(encoding="utf-8"))
    markdown = (gap_out / "space-newline-shop-link-flags.md").read_text(encoding="utf-8")
    assert report["readOnly"] is True
    assert report["rewritten"] is False
    assert report["links"] == "unchanged"
    assert report["s06SellUsd"] == "25"
    assert report["flagCount"] == 4
    assert [flag["stored"] for flag in report["flags"]] == [
        SPACE_LINK,
        NEWLINE_LINK,
        BOTH_LINK,
        CR_LINK,
    ]
    assert "https://e.tb.cn/h.space%20Link" not in markdown
    assert "https://e.tb.cn/h.spaceLink" not in markdown
    assert SPACE_LINK in markdown
    assert "https://item.taobao.com/item.htm?id=123456789012\\n" in markdown
    s06 = next(row for row in report["rows"] if row["ma"] == "S06")
    assert s06["sellUsd"] == "25"
    assert s06["stored"] == S06_HTTPS
    blanks = [row for row in report["rows"] if row["mark"] == "blank"]
    assert [row["stored"] for row in blanks] == ["", "   ", "", "", "\n"]
    assert GAPS.read_bytes() == GAPS_BYTES
    assert CLEAN.read_bytes() == CLEAN_BYTES
    assert HELD.read_bytes() == HELD_BYTES
    assert PRODUCTS.read_bytes() == PRODUCTS_BYTES
    assert EXTRAS.read_bytes() == EXTRAS_BYTES

    clean_out = tmp_path / "clean"
    clean = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "space_newline_shop_link_flags.py"),
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
    assert "Shop link space or newline flags: 0" in clean.stdout
    clean_report = json.loads((clean_out / "space-newline-shop-link-flags.json").read_text(encoding="utf-8"))
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
        str(ROOT / "sassy-closet-shop" / "public" / "data"),
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
    code, err = _run_main(["--fixture", str(CLEAN), "--out", str(CLEAN.parent)])
    assert code == 2
    assert "overwrite" in err
    assert PRODUCTS.read_bytes() == products_before == PRODUCTS_BYTES
    assert HELD.read_bytes() == held_before == HELD_BYTES
    assert EXTRAS.read_bytes() == extras_before == EXTRAS_BYTES
    assert CLEAN.read_bytes() == CLEAN_BYTES
    assert GAPS.read_bytes() == GAPS_BYTES


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
    bad.write_text(json.dumps([{"link": SPACE_LINK}]), encoding="utf-8")
    code, err = _run_main(["--fixture", str(bad), "--out", str(tmp_path / "shape-out")])
    assert code == 2
    assert "mã" in err
    assert bad.read_text(encoding="utf-8") == json.dumps([{"link": SPACE_LINK}])
    empty_ma = tmp_path / "empty.json"
    empty_ma.write_text(json.dumps([{"ma": "  ", "link": SPACE_LINK}]), encoding="utf-8")
    code, err = _run_main(["--fixture", str(empty_ma), "--out", str(tmp_path / "empty-out")])
    assert code == 2
    assert "mã" in err
    assert HELD.read_bytes() == HELD_BYTES


def test_non_string_link_is_left_alone() -> None:
    row = {"ma": "Z90", "link": 12345}
    before = copy.deepcopy(row)
    report = flag_space_newline_shop_links([row])
    assert row == before
    assert report.flags == ()
    assert report.rows[0].mark == "other"
    assert report.rows[0].stored == "12345"


def test_script_is_fixture_only() -> None:
    text = (ROOT / "scripts" / "space_newline_shop_link_flags.py").read_text(encoding="utf-8")
    lowered = text.lower()
    for banned in (
        "urllib",
        "requests",
        "http.client",
        "held_policy",
        "http_shop_link_flags",
        "intake_shop_link_flags",
        "open(",
        "urlparse",
        "splitlines",
        "%20",
        "%0a",
    ):
        assert banned not in lowered
    assert "held.json" in text
    assert 'replace(" "' not in text
    assert ".replace(' '" not in text
    assert HELD.read_bytes() == HELD_BYTES


def _run_main(argv: list[str]) -> tuple[int, str]:
    err = io.StringIO()
    with redirect_stderr(err):
        code = main(argv)
    return code, err.getvalue()
