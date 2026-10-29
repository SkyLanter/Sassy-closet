import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import intake_code_reuse_check as m  # noqa: E402

LINK1 = "https://example.invalid/item?id=111"
LINK2 = "https://example.invalid/item?id=222"


def _json(tmp_path, subs):
    p = tmp_path / "intake.json"
    p.write_text(json.dumps({"submissions": subs}))
    return p


def test_same_code_different_item_flagged(tmp_path):
    p = _json(tmp_path, [
        {"ma": "Z01", "created_at": "2000-01-01T00:00:00Z", "title": "dress", "link": LINK1},
        {"ma": "Z01", "created_at": "2000-02-01T00:00:00Z", "title": "skirt", "link": LINK2},
        {"ma": "Z02", "created_at": "2000-01-01", "title": "top"},
    ])
    assert m.find_reuse(m.load_rows(p)) == [{"ma": "Z01", "rows": 2, "dates": ["2000-01-01", "2000-02-01"]}]


def test_identical_duplicates_not_flagged(tmp_path):
    r = {"ma": "Z01", "created_at": "2000-01-01", "title": "dress", "link": LINK1}
    assert m.find_reuse(m.load_rows(_json(tmp_path, [r, dict(r)]))) == []


def test_item_id_alone_flags(tmp_path):
    p = _json(tmp_path, [{"ma": "Z03", "created_at": "2000-01-01", "title": "x", "link": LINK1},
                         {"ma": "Z03", "created_at": "2000-01-01", "title": "x", "link": LINK2}])
    assert m.find_reuse(m.load_rows(p))[0]["ma"] == "Z03"


def test_md_and_csv_cross_source(tmp_path):
    md = tmp_path / "intake-Z05-2000-03-01.md"
    md.write_text("| Mã | Title | source_link |\n| --- | --- | --- |\n| Z05 | dress | %s |\n" % LINK1)
    c = tmp_path / "x.csv"
    c.write_text("ma,title,source_link,created_at\nZ05,pants,%s,2000-04-01\n" % LINK2)
    rows = m.load_rows(md) + m.load_rows(c)
    assert m.find_reuse(rows) == [{"ma": "Z05", "rows": 2, "dates": ["2000-03-01", "2000-04-01"]}]


def test_output_never_prints_cost_link_or_title(tmp_path, capsys):
    p = _json(tmp_path, [
        {"ma": "Z01", "created_at": "2000-01-01", "title": "secretdress", "link": LINK1},
        {"ma": "Z01", "created_at": "2000-02-01", "title": "secretskirt", "link": LINK2},
    ])
    m.main([str(p)])
    m.main([str(p), "--json"])
    out = capsys.readouterr().out
    for bad in ("example.invalid", "111", "222", "secret"):
        assert bad not in out
    assert "REUSED Z01 rows=2" in out


def test_ok_line(tmp_path, capsys):
    m.main([str(_json(tmp_path, [{"ma": "Z01", "created_at": "2000-01-01"}]))])
    assert capsys.readouterr().out.startswith("OK no reused codes")
