"""Piece 32: privacy_scan tests. All data below is synthetic (Z99 mã, 555 numbers, example links)."""
import io
import json
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import privacy_scan as ps  # noqa: E402

SCRIPT = Path(__file__).resolve().parents[1] / "privacy_scan.py"


def rules(text, rel="x.md", allow=()):
    ps.ACTIVE.clear(); ps.ACTIVE.update(ps.RULES)
    return sorted({h.rule for h in ps.scan_text(rel, text, list(allow))})


@pytest.mark.parametrize("line,rule", [
    ("Cost ¥12 for Z99", "yen"),
    ("price 42 CNY", "cny"),
    ('{"intake_cny": 77.5}', "intake_cny"),
    ("see https://item.taobao.com/item.htm?id=12345", "taobao"),
    ("link e.tb.cn/h.abc", "tb_cn"),
    ("https://detail.1688.com/offer/1.html", "1688"),
    ('"supplier": "shop zzz"', "supplier"),
    ("call +84 912 345 678", "phone"),
    ("call (555) 010-0199", "phone"),
    ("mail zz.buyer@example.com", "email"),
    ("Z99 $ cost 1.23 labeled CNY", "cost"),
])
def test_each_rule_fires(line, rule):
    assert rule in rules(line)


@pytest.mark.parametrize("line", [
    "the intake_cny field is read here",           # bare field name in code
    "Taobao sign-in is Boss-only",                  # prose
    "@pytest.mark.parametrize('a', [1])",           # decorator, not an email
    "no_usd_cost: 3 mã: Z97, Z98, Z99",             # counts, not costs
    "save refuses an S12 CNY sell",                 # mã code next to CNY
    "commit d70c01d at 2026-10-21T09:06Z, 178 tests",
    "Giá $25",
])
def test_no_false_positive(line):
    assert rules(line) == []


def test_strict_flags_bare_words():
    ps.ACTIVE.clear(); ps.ACTIVE.update(ps.RULES); ps.ACTIVE.update(ps.STRICT_RULES)
    got = {h.rule for h in ps.scan_text("x", "Taobao intake_cny ¥", [])}
    assert {"taobao_word", "intake_cny_word", "yen_any"} <= got


def test_cost_table_rule_and_redaction():
    md = "| mã | ¥ | kg | landed | sell |\n|---|---|---|---|---|\n| Z99 | 88 | 0.3 | 15.5 | $25 |\n"
    assert "cost_table" in rules(md)
    out = ps.redact_text(md)
    assert "88" not in out and "15.5" not in out and "$25" in out and "0.3" in out
    assert rules(out) == []


def test_redact_json_stays_valid_and_clean():
    src = json.dumps({"rows": [{"ma": "Z99", "intake_cny": 88.0, "cost_usd": "12.5", "landed_usd": 15.1,
                                 "sourceLink": "https://item.taobao.com/item.htm?id=999", "live": 25}],
                      "info": ["cny: 5 mã: Z1, Z2"]}, indent=1)
    out = ps.redact_text(src)
    data = json.loads(out)
    row = data["rows"][0]
    assert row["intake_cny"] == row["cost_usd"] == row["landed_usd"] == "[redacted]"
    assert row["sourceLink"] == "[redacted-link]" and row["live"] == 25
    assert data["info"] == ["cny: 5 mã: Z1, Z2"]
    assert rules(out) == []


def test_redact_prose_pairs_and_formula():
    out = ps.redact_text("Z99: Cost ¥13 / $1.94. Z98 (¥14 / $2.08). note ceil((¥12 / 6.7 + $1 × 0.8) / 0.75) = ceil(4.56) = $31")
    for v in ("13 /", "1.94", "14 /", "2.08", "4.56", "¥12"):
        assert v not in out
    assert "$31" in out


def test_allowlist_scopes_by_path_and_rule(tmp_path):
    allow = [{"path": "scripts/tests/test_x.py", "rules": ["yen"], "reason": "synthetic"}]
    assert rules("¥5 a@b.co", "scripts/tests/test_x.py", allow) == ["email"]
    assert rules("¥5", "pkg/scripts/tests/test_x.py", allow) == []
    assert rules("¥5", "scripts/other.py", allow) == ["yen"]
    bad = tmp_path / "a.json"; bad.write_text(json.dumps([{"path": "x"}]))
    with pytest.raises(ValueError):
        ps.load_allowlist(str(bad))


def test_patch_files_scan_only_added_lines_with_inner_path():
    diff = ("--- a/scripts/tests/t.py\n+++ b/scripts/tests/t.py\n@@ -1,1 +1,2 @@\n-old ¥9\n+new ¥7\n"
            "--- a/data/real.json\n+++ b/data/real.json\n@@ -0,0 +1 @@\n+{\"intake_cny\": 50}\n")
    allow = [{"path": "scripts/tests/t.py", "reason": "synthetic"}]
    ps.ACTIVE.clear(); ps.ACTIVE.update(ps.RULES)
    hits = ps.scan_file_text("pieces/x/changes.patch", diff, allow)
    assert [(h.path, h.rule) for h in hits] == [("pieces/x/changes.patch::data/real.json", "intake_cny")]


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def test_cli_exit_codes_dir_and_tgz(tmp_path):
    clean = tmp_path / "clean"; clean.mkdir(); (clean / "a.md").write_text("Giá $25 for Z99\n")
    dirty = tmp_path / "dirty"; dirty.mkdir(); (dirty / "p.json").write_text('{"intake_cny": 64}\n')
    (dirty / "bin.dat").write_bytes(b"\x00\x01" + "¥12".encode())
    assert run("--no-allowlist", str(clean)).returncode == 0
    r = run("--no-allowlist", str(dirty))
    assert r.returncode == 1 and "p.json" in r.stdout and "64" not in r.stdout  # value never echoed
    tgz = tmp_path / "b.tgz"
    with tarfile.open(tgz, "w:gz") as tf:
        tf.add(dirty, arcname="dirty")
    r = run("--no-allowlist", "--json", str(tgz))
    assert r.returncode == 1 and json.loads(r.stdout)["count"] == 1
    bak = tmp_path / "b.tgz.bak-20261021"; bak.write_bytes(tgz.read_bytes())
    assert run("--no-allowlist", str(bak)).returncode == 1  # archive detected by content, not name
    assert run().returncode == 2
    assert run(str(tmp_path / "missing")).returncode == 2
    assert run("--bogus").returncode == 2
    assert run("--git-diff", "nodots").returncode == 2


def test_cli_git_diff_added_lines(tmp_path):
    g = lambda *a: subprocess.run(["git", "-C", str(tmp_path), *a], check=True, capture_output=True)
    g("init", "-q"); g("config", "user.email", "t@t.t"); g("config", "user.name", "t")
    (tmp_path / "f.md").write_text("old line ¥10\n"); g("add", "."); g("commit", "-qm", "a")
    (tmp_path / "f.md").write_text("old line ¥10\nnew ok line\n"); g("commit", "-qam", "b")
    assert run("--no-allowlist", "--repo", str(tmp_path), "--git-diff", "HEAD~1..HEAD").returncode == 0
    (tmp_path / "f.md").write_text("old line ¥10\nnew ok line\nZ99 cost 12\n"); g("commit", "-qam", "c")
    assert run("--no-allowlist", "--repo", str(tmp_path), "--git-diff", "HEAD~1..HEAD").returncode == 1


def test_redact_cli_roundtrip(tmp_path):
    src = tmp_path / "s.md"; src.write_text("Z99 cost ¥88\n")
    dst = tmp_path / "o" / "s.md"
    assert run("--redact", str(src), str(dst)).returncode == 0
    assert "88" not in dst.read_text() and run("--no-allowlist", str(dst)).returncode == 0


def test_repo_allowlist_entries_have_reasons():
    entries = ps.load_allowlist(str(Path(__file__).resolve().parents[2] / "data" / "privacy-allowlist.json"))
    assert entries and all(e["reason"].strip() for e in entries)
