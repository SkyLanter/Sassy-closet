import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import daily_summary_draft as d  # noqa: E402

QC = {"overall": "WARN", "fails": [], "warns": ["X99_CODE placeholder free text"],
      "counts": {"live": 3, "held": 1, "intake": 4, "new_since_oct21": 0},
      "s06": {"blob": 25}, "pass2": {"agrees": True}}
COST = {"counts": {"unreachable": 1}, "unreachable_mas": ["Z01"],
        "persistent_new_unreachable": ["Z01"], "live_price_changed": [],
        "new_under_or_loss": [], "wake_reason": "Z01 FREE_TEXT_MUST_NOT_COPY"}
DIG = "- [hold_call] Z01  first_seen=2000-01-01  source=x\nTOTAL 1"
GAPS = {"snapshot_posts": 2, "no_ma": [{"id": "1"}], "no_gia": []}
PROP = {"verdicts": {"Z02": "$30", "Z03": "NEEDS_INPUT"}}


def _b(ig="pass", fb="pass", gaps=GAPS):
    return d.build(QC, COST, d.parse_digest(DIG), gaps, PROP, ig, fb, "2000-01-01")


def test_clear_only_when_both_pass():
    assert "CLEAR" in _b()
    for ig, fb in [("pass", "unchecked"), ("fail", "pass"), ("unchecked", "unchecked")]:
        assert "CLEAR" not in _b(ig, fb).upper().replace("NOT CLEAR", "")


def test_no_free_text_leak():
    t = _b()
    assert "FREE_TEXT" not in t and "placeholder" not in t
    assert "Z02 $30" in t and "Z03" in t and "Hold call: Z01" in t


def test_no_report_not_counted():
    assert "not counted" in _b(gaps=None)


def test_notes_fallback_without_snapshot():
    g = {"snapshot_posts": 0, "no_ma": [["fb", "reel", "1000000001"]],
         "no_gia": [["fb", "post", "ma:Z05"], ["fb", "reel", "1000000001"], ["ig", "post", "ma:Z06"]]}
    t = _b(gaps=g)
    assert "from QC notes" in t and "1 post(s) with no mã, 3 with no Giá" in t
    assert "FB reel 1000000001" in t and "FB post Z05" in t and "IG post Z06" in t


def test_newly_gone_is_hold_question():
    t = _b()
    assert "- Should Z01 go on hold?" in t


def test_under_price_warn_to_intake_mismatch():
    qc = dict(QC, warns=["INTAKE_COST_VS_LIVE Z07 (placeholder) and Z08 under-price", "OTHER_CODE Z09 note"])
    t = d.build(qc, COST, d.parse_digest(DIG), GAPS, PROP, "pass", "pass", "2000-01-01")
    assert "Under-priced at intake cost (midnight QC): Z07, Z08" in t and "Z09" not in t and "placeholder" not in t


def test_mismatch_split_by_reason():
    qc = dict(QC, warns=["INTAKE_COST_VS_LIVE Z07 under-price"])
    cost = dict(COST, unreachable_mas=["Z01", "Z10", "Z11"], persistent_new_unreachable=["Z01"])
    dig = ("- [intake_mismatch] Z01  first_seen=2000-01-01  source=x\n"
           "- [intake_mismatch] Z10  first_seen=2000-01-01  source=x\n"
           "- [intake_mismatch] Z12  first_seen=2000-01-01  source=x\nTOTAL 3")
    t = d.build(qc, cost, d.parse_digest(dig), GAPS, PROP, "pass", "pass", "2000-01-01")
    assert "Under-priced at intake cost (midnight QC): Z07\n" in t
    assert "Taobao listing unreachable or gone: Z10\n" in t
    assert "Intake cost doesn't match public Taobao price: Z12\n" in t
    assert "Intake vs live mismatch" not in t and "Z11" not in t.split("Waiting on you:")[1]
    assert "Should Z01 go on hold?" in t and t.split("Waiting on you:")[1].count("Z01") == 1


def test_main_writes_file_only(tmp_path):
    for n, o in [("qc.json", QC), ("c.json", COST), ("g.json", GAPS), ("p.json", PROP)]:
        (tmp_path / n).write_text(json.dumps(o))
    (tmp_path / "d.txt").write_text(DIG)
    out = tmp_path / "out"
    d.main(["--date", "2000-01-01", "--qc", str(tmp_path / "qc.json"), "--cost", str(tmp_path / "c.json"),
            "--digest", str(tmp_path / "d.txt"), "--gaps", str(tmp_path / "g.json"),
            "--proposal", str(tmp_path / "p.json"), "--out-dir", str(out)])
    assert [p.name for p in out.iterdir()] == ["daily-summary-2000-01-01.md"]


def test_legacy_qc_midnight_and_shop_lines():
    lines = d.midnight_lines(QC)
    assert lines[0] == "Midnight QC: WARN, 0 fail(s), 1 warning(s); second pass agreed."
    assert lines[1] == "Shop: 3 items live, 1 held, intake 4 rows, 0 new, S06 $25."
    text = _b()
    assert lines[0] in text and lines[1] in text


def test_flat_summary_shop_line_hides_notes():
    qc = {"overall": "PASS", "dataOk": "PASS", "sellSite": "PASS",
          "freshnessGuards": "PASS", "freshnessHub": "skip",
          "blobCount": 62, "heldCount": 22, "intakeCount": 40, "s06Usd": 25,
          "notes": "SECRET_NOTE", "a02TitleEn": "SECRET_TITLE",
          "blobHubUsdMismatches": ["A02 23->25"]}
    text = d.build(qc, None, {}, None, None, "pass", "pass", "2000-01-01")
    assert "Midnight QC: PASS. Data PASS. Sell site PASS. Freshness guards PASS. Hub SKIP." in text
    assert "62 items live, 22 held, intake 40 rows, S06 $25." in text
    for hidden in ("second pass", "SECRET_NOTE", "SECRET_TITLE", "23->25"):
        assert hidden not in text


def test_flat_script_bools_and_hub_ok():
    text = "\n".join(d.midnight_lines({
        "dataOk": "<script>", "freshnessHub": "ok", "s06Usd": True, "blobCount": True}))
    assert "Data UNKNOWN" in text and "<script>" not in text
    assert "Shop:" not in text and "Hub OK" in text


def test_flat_s06_nan_inf_omitted():
    for bad in (float("nan"), float("inf")):
        text = "\n".join(d.midnight_lines({"overall": "PASS", "blobCount": 62, "s06Usd": bad}))
        assert "S06" not in text and "62 items live" in text


def test_qc_none_not_found():
    assert d.midnight_lines(None) == ["Midnight QC: not found for today."]
    assert "Midnight QC: not found for today." in d.build(
        None, None, {}, None, None, "pass", "pass", "2000-01-01")


BLOCKED_LINE = ("Taobao cost recheck: blocked on a signed-out read. "
                "Unreachable rows and price deltas in this file are not used.")
SIGNIN_LINE = "Taobao still needs your sign-in."


def _blocked_cost(flag=True):
    return {
        "taobao_login_needed": flag,
        "counts": {"unreachable": 4},
        "unreachable_mas": ["Z01", "Z10"],
        "persistent_new_unreachable": ["Z01"],
        "live_price_changed": ["Z10"],
        "new_under_or_loss": ["Z11"],
        "wake_reason": "SECRET_WAKE",
    }


def test_signed_out_cost_block_is_not_price_or_gone_evidence():
    dig = "- [intake_mismatch] Z10  first_seen=2000-01-01  source=x\nTOTAL 1"
    text = d.build(QC, _blocked_cost(True), d.parse_digest(dig), GAPS, None,
                   "pass", "pass", "2000-01-01")
    lines = text.splitlines()
    start = lines.index(BLOCKED_LINE)
    assert lines[start + 1] == SIGNIN_LINE
    assert lines[start + 2] == ""
    assert "listings unreachable" not in text
    assert "live price change" not in text
    assert "under-price/loss" not in text
    assert "Newly gone" not in text
    assert "Should Z01 go on hold?" not in text
    assert "Taobao listing unreachable" not in text
    assert "Intake cost doesn't match public Taobao price: Z10" in text
    assert "SECRET_WAKE" not in text
    assert "Midnight QC: WARN, 0 fail(s), 1 warning(s); second pass agreed." in text


def test_flat_midnight_lines_stay_when_cost_is_blocked():
    qc = {"overall": "PASS", "dataOk": "PASS", "sellSite": "PASS",
          "freshnessGuards": "PASS", "freshnessHub": "skip",
          "blobCount": 62, "heldCount": 22, "intakeCount": 40, "s06Usd": 25}
    text = d.build(qc, _blocked_cost(), {}, None, None, "pass", "pass", "2000-01-01")
    assert "Midnight QC: PASS. Data PASS. Sell site PASS. Freshness guards PASS. Hub SKIP." in text
    assert "62 items live, 22 held, intake 40 rows, S06 $25." in text
    assert BLOCKED_LINE in text
    assert "listings unreachable" not in text


def test_negative_login_flag_keeps_evidence_and_hold_question():
    for flag in ("false", "no", False, 0, "1.0"):
        text = d.build(QC, _blocked_cost(flag), d.parse_digest(DIG), GAPS, None,
                       "pass", "pass", "2000-01-01")
        assert "listings unreachable" in text
        assert "1 live price change(s)" in text
        assert "1 new under-price/loss." in text
        assert "Newly gone on Taobao and still live: Z01." in text
        assert "Should Z01 go on hold?" in text
        assert SIGNIN_LINE not in text
        assert "blocked on a signed-out read" not in text
        assert "SECRET_WAKE" not in text


def test_login_block_accepts_one_and_yes():
    for flag in (1, 1.0, "yes", " y ", "1"):
        text = d.build(QC, _blocked_cost(flag), {}, GAPS, None, "pass", "pass", "2000-01-01")
        assert BLOCKED_LINE in text and SIGNIN_LINE in text
        assert "Should Z01 go on hold?" not in text


UNREADABLE = "Taobao cost recheck: unreadable, so not used."


def _brief(tmp_path, *, cost, qc="null", gaps="{}", proposal="null"):
    day = "2000-01-05"
    root = tmp_path / "root"
    (root / "verify" / "cost-recheck").mkdir(parents=True)
    (root / "verify" / "cost-recheck" / f"summary.{day}.json").write_text(cost, encoding="utf-8")
    paths = {}
    for name, body in (("qc.json", qc), ("gaps.json", gaps), ("proposal.json", proposal), ("digest.txt", DIG)):
        path = tmp_path / name
        path.write_text(body, encoding="utf-8")
        paths[name] = path
    out = tmp_path / "out"
    code = d.main([
        "--date", day,
        "--root", str(root),
        "--qc", str(paths["qc.json"]),
        "--cost", str(root / "verify" / "cost-recheck" / f"summary.{day}.json"),
        "--digest", str(paths["digest.txt"]),
        "--gaps", str(paths["gaps.json"]),
        "--proposal", str(paths["proposal.json"]),
        "--out-dir", str(out),
    ])
    text = (out / f"daily-summary-{day}.md").read_text(encoding="utf-8")
    return code, text


def test_main_bad_shapes_do_not_raise(tmp_path):
    code, text = _brief(tmp_path, cost="true", qc="true", gaps="[]", proposal="[1]")
    assert code == 0
    assert UNREADABLE in text
    assert "Midnight QC: unreadable, so not used." in text
    assert "listings unreachable" not in text
    assert "Should " not in text
    assert "Caption gaps: gap report unavailable" in text
    assert "Hold call: Z01" in text


def test_main_true_counts_do_not_abort(tmp_path):
    cost = json.dumps({
        "counts": True,
        "unreachable_mas": ["Z01"],
        "persistent_new_unreachable": ["Z01"],
    })
    code, text = _brief(tmp_path, cost=cost)
    assert code == 0
    assert UNREADABLE not in text
    assert "unreadable listings unreachable (Z01)" in text
    assert "? listings unreachable" not in text
    assert "1 listings unreachable" not in text
    assert "True listings" not in text
    assert "Should Z01 go on hold?" in text


def test_non_dict_counts_are_unreadable_and_do_not_raise():
    shapes = (True, 1, 1.0, ["Z01"], "many", " ", "\u200b", False, 0, [], "", None)
    for counts in shapes:
        text = d.build(
            None,
            {
                "counts": counts,
                "unreachable_mas": ["Z01"],
                "persistent_new_unreachable": ["Z01"],
            },
            {},
            {},
            None,
            "pass",
            "pass",
            "2000-01-01",
        )
        assert "unreadable listings unreachable (Z01)" in text
        assert "True listings" not in text
        assert "many listings" not in text
        assert "Should Z01 go on hold?" in text
    missing = d.build(
        None,
        {"unreachable_mas": ["Z01"]},
        {},
        {},
        None,
        "pass",
        "pass",
        "2000-01-01",
    )
    assert "? listings unreachable (Z01)" in missing
    assert "unreadable listings unreachable" not in missing
    blocked = d.build(
        None,
        {
            "taobao_login_needed": True,
            "counts": True,
            "unreachable_mas": ["Z01"],
            "persistent_new_unreachable": ["Z01"],
        },
        {},
        {},
        None,
        "pass",
        "pass",
        "2000-01-01",
    )
    assert BLOCKED_LINE in blocked
    assert "listings unreachable" not in blocked
    assert "Should Z01 go on hold?" not in blocked


def test_main_non_dict_counts_are_unreadable(tmp_path):
    shapes = (True, 1, ["Z01"], "many", False, 0, [], "")
    for index, counts in enumerate(shapes):
        code, text = _brief(tmp_path / str(index), cost=json.dumps({
            "counts": counts,
            "unreachable_mas": ["Z01"],
            "persistent_new_unreachable": ["Z01"],
        }))
        assert code == 0
        assert "unreadable listings unreachable (Z01)" in text
        assert "? listings unreachable" not in text
        assert "True listings" not in text
        assert "Should Z01 go on hold?" in text


def test_main_signed_out_cost_stays_blocked(tmp_path):
    code, text = _brief(tmp_path, cost=json.dumps(_blocked_cost(1)))
    assert code == 0
    assert BLOCKED_LINE in text and SIGNIN_LINE in text
    assert UNREADABLE not in text
    assert "listings unreachable" not in text
    assert "Should Z01 go on hold?" not in text


def test_legacy_bool_shop_fields_print_unreadable():
    text = "\n".join(d.midnight_lines({
        "s06": {"blob": True},
        "counts": {"live": True, "held": True, "intake": True},
        "fails": [],
        "warns": [],
    }))
    assert "True" not in text
    assert "$1" not in text and "$0" not in text
    assert "unreadable items live" in text
    assert "unreadable held" in text
    assert "intake unreadable rows, 0 new" in text
    assert "S06 unreadable" in text
    false_s06 = "\n".join(d.midnight_lines({
        "s06": {"blob": False}, "counts": {}, "fails": [], "warns": [],
    }))
    assert "S06 $0" not in false_s06 and "$0" not in false_s06
    assert "S06 unreadable" in false_s06
    assert "S06 $25." in "\n".join(d.midnight_lines(QC))


def test_legacy_non_numeric_shop_fields_print_unreadable():
    text = "\n".join(d.midnight_lines({
        "counts": {"live": "six", "held": None, "intake": {}},
        "s06": {"blob": "25"},
        "fails": [],
        "warns": [],
    }))
    assert "six" not in text and "$" not in text
    assert text.count("unreadable") >= 4


def test_bool_and_non_numeric_unreachable_count_is_unreadable():
    text = d.build(
        None,
        {"counts": {"unreachable": True}, "unreachable_mas": ["Z01"]},
        {}, {}, None, "pass", "pass", "2000-01-01",
    )
    assert "True listings" not in text
    assert "unreadable listings unreachable (Z01)" in text
    text_s = d.build(
        None,
        {"counts": {"unreachable": "many"}, "unreachable_mas": ["Z01"]},
        {}, {}, None, "pass", "pass", "2000-01-01",
    )
    assert "many listings" not in text_s
    assert "unreadable listings unreachable (Z01)" in text_s
    kept = d.build(
        None,
        {"counts": {"unreachable": 4}, "unreachable_mas": ["Z01"]},
        {}, {}, None, "pass", "pass", "2000-01-01",
    )
    assert "4 listings unreachable (Z01)" in kept
    assert "unreadable listings unreachable" not in kept


def test_present_bad_meta_qc_is_not_freshness_ok(tmp_path):
    day = "2000-01-05"
    root = tmp_path / "root"
    (root / "verify" / "cost-recheck").mkdir(parents=True)
    (root / "verify" / "cost-recheck" / f"summary.{day}.json").write_text("{", encoding="utf-8")
    muse = root / "out" / "muse"
    muse.mkdir(parents=True)
    (muse / f"meta-qc-{day}.json").write_text("{", encoding="utf-8")
    digest = tmp_path / "digest.txt"
    digest.write_text(DIG, encoding="utf-8")
    gaps = tmp_path / "gaps.json"
    gaps.write_text("{}", encoding="utf-8")
    out = tmp_path / "out"
    code = d.main([
        "--date", day, "--root", str(root),
        "--digest", str(digest), "--gaps", str(gaps), "--out-dir", str(out),
    ])
    text = (out / f"daily-summary-{day}.md").read_text(encoding="utf-8")
    assert code == 0
    assert "Meta QC json: OK" not in text
    assert "Meta QC json: unreadable (meta-qc-2000-01-05.json)" in text
    assert "Taobao cost recheck: unreadable, so not used." in text
    assert "(unreadable)" in text
    assert "meta-qc-2000-01-05.json (missing)" not in text


def test_bad_muse_file_still_reads_passing_snapshot(tmp_path):
    day = "2000-01-05"
    muse = tmp_path / "out" / "muse"
    muse.mkdir(parents=True)
    (muse / f"meta-qc-{day}.json").write_text("{", encoding="utf-8")
    snap = tmp_path / "out" / "meta-snapshot"
    snap.mkdir(parents=True)
    side = {"luxubu": {"status": "pass"}, "miniboss": {"status": "pass"}}
    (snap / "meta-snapshot-20000105T010000.json").write_text(
        json.dumps({"qc": {"ig": side, "fb": side}}), encoding="utf-8")
    st, src = d.read_meta_status(tmp_path, day)
    assert st["ig"] == st["fb"] == ("pass", "Luxubu + Mini Boss agree")
    assert src.startswith("Meta snapshot meta-snapshot-20000105T010000.json")


def test_legacy_bool_pass_and_bare_s06_do_not_raise():
    lines = d.midnight_lines({"pass2": True, "fails": True, "s06": 25, "counts": []})
    assert lines[0].startswith("Midnight QC:")
    assert "S06" not in "\n".join(lines)
    text = d.build(
        {"pass2": True, "fails": True, "warns": True, "s06": 25, "counts": []},
        None,
        {},
        {},
        {"verdicts": True},
        "pass",
        "pass",
        "2000-01-01",
    )
    assert "Midnight QC:" in text
    assert "S06" not in text
    assert "Suggested sell prices" not in text
    assert d.under_price_mas("Z01 under-priced vs live $") == ["Z01"]


def test_bool_lists_are_not_ma_evidence():
    assert d.mas(True) == []
    assert d.mas("Z01") == []
    assert d.mas(["Z01", True, "nope"]) == ["Z01"]
    text = d.build(
        None,
        {"unreachable_mas": True, "persistent_new_unreachable": True, "counts": {}},
        {},
        {"no_ma": True, "no_gia": True},
        None,
        "pass",
        "pass",
        "2000-01-01",
    )
    assert "Should " not in text
    assert "No mã:" not in text


def test_main_lone_brace_cost_is_unreadable(tmp_path):
    day = "2000-01-05"
    root = tmp_path / "root"
    cost_dir = root / "verify" / "cost-recheck"
    cost_dir.mkdir(parents=True)
    (cost_dir / f"summary.{day}.json").write_text("{", encoding="utf-8")
    (cost_dir / "summary.2000-01-04.json").write_text(
        json.dumps({"unreachable_mas": ["Z71"], "persistent_new_unreachable": ["Z71"]}),
        encoding="utf-8",
    )
    qc = tmp_path / "qc.json"
    qc.write_text("{", encoding="utf-8")
    digest = tmp_path / "digest.txt"
    digest.write_text(DIG, encoding="utf-8")
    gaps = tmp_path / "gaps.json"
    gaps.write_text("{}", encoding="utf-8")
    out = tmp_path / "out"
    code = d.main([
        "--date", day,
        "--root", str(root),
        "--qc", str(qc),
        "--cost", str(cost_dir / f"summary.{day}.json"),
        "--digest", str(digest),
        "--gaps", str(gaps),
        "--out-dir", str(out),
        "--stdout",
    ])
    assert code == 0
    text = (out / f"daily-summary-{day}.md").read_text(encoding="utf-8")
    assert UNREADABLE in text
    assert "Midnight QC: unreadable, so not used." in text
    assert "listings unreachable" not in text
    assert "Should Z71 go on hold?" not in text
    assert "Hold call: Z01" in text
