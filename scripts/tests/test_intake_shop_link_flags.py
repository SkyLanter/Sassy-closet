"""Fixture-only intake shop-link flags. No live intake and no link writes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from held_policy import load_held_policy
from intake_shop_link_flags import (
    classify_shop_link,
    flag_intake_shop_links,
    load_rows,
    main,
    report_json,
    render_markdown,
)

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"
GAPS = FIXTURES / "intake_shop_links_gaps.json"
CLEAN = FIXTURES / "intake_shop_links_clean.json"
HELD = ROOT / "data" / "held.json"
CATALOG = ROOT / "sassy-closet-shop" / "data" / "products.json"
EXTRAS = ROOT / "sassy-closet-shop" / "data" / "intake-extras.json"
PASTE = "【淘宝】https://e.tb.cn/h.7KxYzAb  HU1234 「连衣裙」点击链接直接打开"

EXPECTED: dict[str, list[tuple[str, str, str, str, bool]]] = {
    "S06": [],
    "K06": [],
    "V05": [("blank_link", "link", "blank", "", True)],
    "K02": [("not_shop_link", "link", "not_taobao", "https://1688.com/offer/123.html", True)],
    "A26": [("not_shop_link", "link", "not_taobao", "https://detail.tmall.com/item.htm?id=123456789", True)],
    "Z81": [("blank_link", "link", "missing", "", False)],
    "Z82": [("blank_link", "link", "blank", "  \n\t", False)],
    "Z83": [("blank_link", "link", "null", "null", False)],
    "Z84": [("blank_link", "link", "blank", "n/a", False)],
    "Z85": [("not_shop_link", "link", "not_taobao", "https://example.com/shop", False)],
    "Z86": [("not_shop_link", "link", "not_taobao", "https://m.tb.cn/h.eeKwB12", False)],
    "Z87": [("not_shop_link", "link", "not_item", "https://item.taobao.com/item.htm", False)],
    "Z88": [("not_shop_link", "link", "not_item", "https://item.taobao.com/item.htm?id=12345", False)],
    "Z89": [("not_shop_link", "link", "not_item", "https://www.taobao.com/", False)],
    "Z90": [("not_shop_link", "link", "not_item", "https://s.taobao.com/search?q=dress", False)],
    "Z91": [("not_shop_link", "link", "not_share", "https://e.tb.cn/", False)],
    "Z92": [("not_shop_link", "link", "not_share", "https://e.tb.cn/h.", False)],
    "Z93": [("not_shop_link", "link", "wrapped", PASTE, False)],
    "Z94": [("not_shop_link", "link", "not_share", "https://e.tb.cn/h.7KxYzAb点击链接", False)],
    "Z95": [("not_shop_link", "link", "not_a_url", "淘宝店铺", False)],
    "Z96": [("not_shop_link", "link", "not_http", "javascript:alert(1)", False)],
    "Z97": [("not_shop_link", "link", "not_a_url", "https://user:pass@e.tb.cn/h.abc", False)],
    "Z98": [
        (
            "not_shop_link",
            "link",
            "wrapped",
            "https://e.tb.cn/h.7KxYzAb https://item.taobao.com/item.htm?id=123456789",
            False,
        )
    ],
    "Z99": [("not_shop_link", "link", "has_port", "https://e.tb.cn:443/h.abc", False)],
    "Z70": [("blank_link", "link", "blank", "", False)],
    "Z60": [("not_shop_link", "link", "not_a_string", '["nope"]', False)],
    "Z59": [("not_shop_link", "link", "not_item", "https://shop123.taobao.com/", False)],
    "Z58": [("not_shop_link", "link", "not_share", "https://e.tb.cn/h.abc.", False)],
    "Z57": [("not_shop_link", "link", "not_taobao", "https://tb.cn/h.abc", False)],
    "Z56": [
        (
            "not_shop_link",
            "link",
            "not_item",
            "https://world.taobao.com/item.htm?id=770708953593",
            False,
        )
    ],
    "Z55": [("not_shop_link", "link", "not_share", "https://e.tb.cn//h.abc", False)],
    "Z54": [("not_shop_link", "link", "not_share", "https://e.tb.cn/H.abc", False)],
    "Z53": [("not_shop_link", "link", "not_item", "https://s.click.taobao.com/abc", False)],
    "Z52": [("not_shop_link", "link", "not_http", "ftp://e.tb.cn/h.abc", False)],
}

CLEAN_SHAPES = {
    "S06": "e.tb.cn",
    "K06": "taobao-item",
    "A01": "taobao-item",
    "V05": "taobao-item",
    "Z01": "e.tb.cn",
    "Z02": "e.tb.cn",
    "Z03": "taobao-item",
    "Z04": "taobao-item",
    "Z05": "taobao-item",
    "Z06": "e.tb.cn",
    "Z07": "taobao-item",
}


def _rows(path: Path) -> list[dict[str, object]]:
    return load_rows(json.loads(path.read_text(encoding="utf-8")))


def test_gap_fixture_flags_links_and_does_not_rewrite_them() -> None:
    original = GAPS.read_text(encoding="utf-8")
    rows = _rows(GAPS)
    before = json.dumps(rows)
    report = flag_intake_shop_links(rows, load_held_policy())
    assert json.dumps(rows) == before
    assert GAPS.read_text(encoding="utf-8") == original
    found = {
        row.ma: [(flag.kind, flag.field, flag.reason, flag.stored, flag.held) for flag in row.flags]
        for row in report.rows
    }
    assert found == EXPECTED
    s06 = next(row for row in report.rows if row.ma == "S06")
    k06 = next(row for row in report.rows if row.ma == "K06")
    v05 = next(row for row in report.rows if row.ma == "V05")
    z70 = next(row for row in report.rows if row.ma == "Z70")
    z81 = next(row for row in report.rows if row.ma == "Z81")
    z93 = next(row for row in report.rows if row.ma == "Z93")
    assert s06.sell_usd == "25"
    assert s06.held is False
    assert s06.shape == "e.tb.cn"
    assert s06.stored == "https://e.tb.cn/h.8KCQeaHH3dz1iSl?tk=WeuOTTBXHOu"
    assert k06.held is True
    assert k06.shape == "taobao-item"
    assert v05.held is True
    assert z81.sell_usd == "40"
    assert z70.stored == ""
    assert z70.flags[0].stored == ""
    assert z93.stored == PASTE
    assert z93.flags[0].as_json().keys() == {"ma", "kind", "field", "stored", "reason", "held"}
    body = json.dumps(report_json(report), ensure_ascii=False)
    assert '"links": "unchanged"' in body
    assert '"fetchedTaobao": false' in body
    assert '"s06": "stays $25"' in body
    assert '"heldMas": "stay held"' in body
    assert "corrected" not in body
    assert "normalized" not in body
    assert "replacement" not in body
    assert "tesla" not in body.casefold()
    assert body.count("https://e.tb.cn/h.goodLink") == 0
    markdown = render_markdown(report)
    assert "Links stay as stored." in markdown
    assert "Taobao is not fetched." in markdown
    assert "S06 stays $25." in markdown
    assert "Held mãs stay held." in markdown
    assert "S06 | false | 25 | e.tb.cn | —" in markdown
    assert "K06 | true | — | taobao-item | —" in markdown
    assert "V05 blank_link `link` blank: stored `` stays held" in markdown
    assert "Z82 blank_link `link` blank: stored `  \\n\\t`" in markdown
    assert "K02 not_shop_link `link` not_taobao: stored `https://1688.com/offer/123.html` stays held" in markdown
    assert "A26 not_shop_link `link` not_taobao: stored `https://detail.tmall.com/item.htm?id=123456789` stays held" in markdown


def test_clean_fixture_accepts_item_and_share_links() -> None:
    rows = _rows(CLEAN)
    before = json.dumps(rows)
    report = flag_intake_shop_links(rows, load_held_policy())
    assert json.dumps(rows) == before
    assert report.flag_count == 0
    assert {row.ma: row.shape for row in report.rows} == CLEAN_SHAPES
    assert [row.ma for row in report.rows] == list(CLEAN_SHAPES)
    s06 = next(row for row in report.rows if row.ma == "S06")
    k06 = next(row for row in report.rows if row.ma == "K06")
    v05 = next(row for row in report.rows if row.ma == "V05")
    z01 = next(row for row in report.rows if row.ma == "Z01")
    z02 = next(row for row in report.rows if row.ma == "Z02")
    z04 = next(row for row in report.rows if row.ma == "Z04")
    z06 = next(row for row in report.rows if row.ma == "Z06")
    assert s06.sell_usd == "25"
    assert s06.held is False
    assert k06.held is True
    assert v05.held is True
    assert z01.stored == "  https://e.tb.cn/h.abc  "
    assert z02.stored == "HTTPS://E.TB.CN/h.AbC12"
    assert z04.field == "source_link"
    assert z06.field == "sourceLink"
    verdict = classify_shop_link(s06.stored)
    assert verdict.kind is None
    assert verdict.shape == "e.tb.cn"
    assert not hasattr(verdict, "url")


def test_cli_writes_a_report_and_leaves_shop_files(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    catalog_bytes = CATALOG.read_bytes()
    extras_bytes = EXTRAS.read_bytes()
    gaps_bytes = GAPS.read_bytes()
    clean_bytes = CLEAN.read_bytes()
    out = tmp_path / "out"
    gaps = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "intake_shop_link_flags.py"),
            "--fixture",
            str(GAPS),
            "--out",
            str(out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert gaps.returncode == 1, gaps.stderr
    assert "Intake shop link flags:" in gaps.stdout
    markdown = (out / "intake-shop-link-flags.md").read_text(encoding="utf-8")
    saved = json.loads((out / "intake-shop-link-flags.json").read_text(encoding="utf-8"))
    assert "S06 stays $25." in markdown
    assert "Taobao is not fetched." in markdown
    assert saved["flagCount"] == sum(len(flags) for flags in EXPECTED.values())
    assert saved["fetchedTaobao"] is False
    assert saved["links"] == "unchanged"
    assert saved["rows"][0]["sellUsd"] == "25"
    assert saved["rows"][0]["ma"] == "S06"
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert EXTRAS.read_bytes() == extras_bytes
    assert GAPS.read_bytes() == gaps_bytes
    held = json.loads(HELD.read_text(encoding="utf-8"))
    assert "K06" in held["heldIncomplete"]
    assert "V05" in held["heldIncomplete"]
    assert "K02" in held["heldIncomplete"]
    assert "A26" in held["heldIncomplete"]

    clean_out = tmp_path / "clean"
    clean = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "intake_shop_link_flags.py"),
            "--fixture",
            str(CLEAN),
            "--out",
            str(clean_out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert clean.returncode == 0, clean.stderr
    assert json.loads((clean_out / "intake-shop-link-flags.json").read_text(encoding="utf-8"))["flagCount"] == 0
    assert HELD.read_bytes() == held_bytes
    assert CATALOG.read_bytes() == catalog_bytes
    assert EXTRAS.read_bytes() == extras_bytes
    assert CLEAN.read_bytes() == clean_bytes


def test_cli_refuses_live_intake_and_missing_files(tmp_path: Path) -> None:
    held_bytes = HELD.read_bytes()
    out = tmp_path / "out"
    refused = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "intake_shop_link_flags.py"),
            "--fixture",
            "https://sassy-closet.vercel.app/api/submissions",
            "--out",
            str(out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert refused.returncode == 2
    assert "Live intake is not read." in refused.stderr
    assert not out.exists()
    assert HELD.read_bytes() == held_bytes

    missing = main(["--fixture", str(tmp_path / "missing.json"), "--out", str(out)])
    assert missing == 2
    broken = tmp_path / "broken.json"
    broken.write_text("{", encoding="utf-8")
    assert main(["--fixture", str(broken), "--out", str(out)]) == 2
    empty = tmp_path / "empty.json"
    empty.write_text('{"nope": []}', encoding="utf-8")
    assert main(["--fixture", str(empty), "--out", str(out)]) == 2
    assert HELD.read_bytes() == held_bytes


def test_script_has_no_live_client() -> None:
    text = (ROOT / "scripts" / "intake_shop_link_flags.py").read_text(encoding="utf-8").casefold()
    assert "urllib" not in text
    assert "requests" not in text
    assert "urlopen" not in text
    assert "vercel.app" not in text
    assert "square.com" not in text
    assert "tesla" not in text
    assert "facebook" not in text
    assert "instagram" not in text
    assert "import socket" not in text
    assert "http.client" not in text
