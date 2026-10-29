import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_shop_drafts as r  # noqa: E402


def _tool(d: Path, name: str, body: str):
    (d / f"{name}.py").write_text(body)


def test_failure_does_not_stop_others(tmp_path):
    s = tmp_path / "scripts"; s.mkdir()
    _tool(s, "good_a", "print('OK placeholder X01')\n")
    _tool(s, "bad_b", "import sys; print('boom'); sys.exit(3)\n")
    _tool(s, "good_c", "print('OK placeholder X02')\n")
    rep = tmp_path / "out" / "2099-01-01"
    rows = r.run_all([("good_a", []), ("bad_b", []), ("missing_d", []), ("good_c", [])], rep, scripts=s)
    assert [x[2] for x in rows] == ["OK", "FAILED", "FAILED", "OK"]
    assert rows[1][1] == 3 and rows[2][1] == 127
    idx = r.write_index(rows, rep, "2099-01-01").read_text()
    assert "| 2 | bad_b | 3 | FAILED | 02-bad_b.txt |" in idx
    assert "Overall: FAILED (bad_b, missing_d)" in idx
    assert (rep / "04-good_c.txt").read_text().startswith("OK placeholder X02")


def test_all_ok_index(tmp_path):
    s = tmp_path / "scripts"; s.mkdir()
    _tool(s, "t1", "print('fine')\n")
    rep = tmp_path / "r"
    rows = r.run_all([("t1", [])], rep, scripts=s)
    assert "Overall: OK" in r.write_index(rows, rep, "2099-01-01").read_text()


def test_steps_order_and_proposal_dir(tmp_path):
    steps = r.build_steps(tmp_path, tmp_path / "rep", "2099-01-01")
    assert [t for t, _ in steps] == ["taobao_unreachable_streak", "boss_decisions_digest", "meta_caption_gap_report",
                                    "intake_code_reuse_check", "held_price_proposal", "daily_summary_draft"]
    hp = dict(steps)["held_price_proposal"]
    assert hp[hp.index("--proposal-dir") + 1] == str(tmp_path / "rep" / "proposals")


def test_gap_exit1_is_gaps_not_failed(tmp_path):
    s = tmp_path / "scripts"; s.mkdir()
    _tool(s, "meta_caption_gap_report", "import sys; print('GAP placeholder X03'); sys.exit(1)\n")
    _tool(s, "plain", "import sys; sys.exit(1)\n")
    rep = tmp_path / "r"
    rows = r.run_all([("meta_caption_gap_report", []), ("plain", [])], rep, scripts=s)
    assert [x[2] for x in rows] == ["GAPS", "FAILED"]
    assert "Overall: FAILED (plain)" in r.write_index(rows, rep, "2099-01-01").read_text()


def test_gaps_only_overall(tmp_path):
    s = tmp_path / "scripts"; s.mkdir()
    _tool(s, "meta_caption_gap_report", "import sys; sys.exit(1)\n")
    _tool(s, "ok1", "print('fine')\n")
    rep = tmp_path / "r"
    rows = r.run_all([("ok1", []), ("meta_caption_gap_report", [])], rep, scripts=s)
    idx = r.write_index(rows, rep, "2099-01-01").read_text()
    assert "| 2 | meta_caption_gap_report | 1 | GAPS |" in idx
    assert "Overall: GAPS (meta_caption_gap_report)" in idx


def test_real_errors_stay_failed_for_gap_tool():
    for code in (2, 3, 124, 127):
        assert r.status_for("meta_caption_gap_report", code) == "FAILED"
    assert r.status_for("meta_caption_gap_report", 0) == "OK"
    assert r.status_for("other", 1) == "FAILED"
    assert r.overall([("a", 1, "GAPS", None), ("b", 2, "FAILED", None)]) == "FAILED (b)"


def test_runner_passes_order_and_held_to_digest(tmp_path):
    steps = dict(r.build_steps(tmp_path, tmp_path / "rep", "2099-01-01"))
    a = steps["boss_decisions_digest"]
    assert a[a.index("--order") + 1] == str(r.REPO / "sassy-closet-shop" / "data" / "popular-order.json")
    assert a[a.index("--held") + 1] == str(r.REPO / "data" / "held.json")


def test_index_lists_popular_order_held_item(tmp_path):
    s = tmp_path / "scripts"; s.mkdir()
    _tool(s, "boss_decisions_digest", "print('- [popular_order_held] Remove held X99 from popular order? (placeholder)')\n")
    rep = tmp_path / "r"
    rows = r.run_all([("boss_decisions_digest", [])], rep, scripts=s)
    assert "Digest items: popular_order_held" in r.write_index(rows, rep, "2099-01-01").read_text()
