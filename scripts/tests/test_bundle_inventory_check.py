import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import bundle_inventory_check as b


def mk(tmp, name, patch=True, proof=True):
    d = tmp / name
    (d / "patches").mkdir(parents=True)
    (d / "proof").mkdir()
    if patch:
        (d / "patches" / "0001-x.patch").write_text("x")
    if proof:
        (d / "proof" / "pytest.txt").write_text("ok")


def inv(tmp, names):
    (tmp / "INVENTORY.tsv").write_text("".join(f"{n}\tabc\tdraft/{n}\tbase\t1\n" for n in names))


def test_clean(tmp_path):
    mk(tmp_path, "17-a"); mk(tmp_path, "18-b"); inv(tmp_path, ["17-a", "18-b"])
    r = b.check(str(tmp_path))
    assert r["issues"] == [] and r["folders"] == 2 and r["rows"] == 2


def test_non_pr_folders_info(tmp_path):
    mk(tmp_path, "01-15-combined"); (tmp_path / "08-stack-check").mkdir()
    mk(tmp_path, "17-a"); inv(tmp_path, ["17-a"])
    r = b.check(str(tmp_path))
    assert r["folders"] == 3 and r["rows"] == 1 and r["issues"] == []
    assert {f for f, _ in r["info"]} == {"01-15-combined", "08-stack-check"}


def test_missing_row_and_folder(tmp_path):
    mk(tmp_path, "17-a"); inv(tmp_path, ["18-b"])
    r = b.check(str(tmp_path))
    assert ("17-a", "missing_row") in r["issues"]
    assert ("18-b", "missing_folder") in r["issues"]


def test_no_patch_no_proof(tmp_path):
    mk(tmp_path, "17-a", patch=False, proof=False); inv(tmp_path, ["17-a"])
    r = b.check(str(tmp_path))
    assert ("17-a", "no_patches") in r["issues"] and ("17-a", "no_proof") in r["issues"]


def test_dup_row(tmp_path):
    mk(tmp_path, "17-a"); inv(tmp_path, ["17-a", "17-a"])
    assert ("17-a", "dup_row") in b.check(str(tmp_path))["issues"]


def test_ignores_files_and_odd_dirs(tmp_path):
    mk(tmp_path, "17-a"); inv(tmp_path, ["17-a"]); (tmp_path / "tmp").mkdir()
    assert b.check(str(tmp_path))["folders"] == 1


def test_main_output(tmp_path, capsys):
    mk(tmp_path, "17-a"); inv(tmp_path, ["17-a"])
    assert b.main([str(tmp_path)]) == 0
    assert "OK bundle matches inventory" in capsys.readouterr().out


# Piece 87: strict gap listing (placeholder data only)
def test_gaps_listed_by_name_allowlisted_ok(tmp_path, capsys):
    mk(tmp_path, "01-15-combined"); (tmp_path / "08-stack-check").mkdir()
    mk(tmp_path, "17-a"); inv(tmp_path, ["17-a"])
    assert b.main([str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "GAP folder_without_row 01-15-combined allowlisted" in out
    assert "GAP folder_without_row 08-stack-check allowlisted" in out
    assert "OK bundle matches inventory" in out


def test_unallowed_missing_row_exits_1(tmp_path, capsys):
    mk(tmp_path, "17-a"); mk(tmp_path, "18-b"); inv(tmp_path, ["17-a"])
    assert b.main([str(tmp_path)]) == 1
    out = capsys.readouterr().out
    assert "GAP folder_without_row 18-b NOT_ALLOWLISTED" in out
    assert "OK bundle" not in out and "FAIL" in out


def test_row_without_folder_listed(tmp_path, capsys):
    mk(tmp_path, "17-a"); inv(tmp_path, ["17-a", "19-c"])
    r = b.check(str(tmp_path))
    assert r["rows_without_folder"] == ["19-c"] and r["unallowed_missing_rows"] == []
    b.main([str(tmp_path)])
    assert "GAP row_without_folder 19-c" in capsys.readouterr().out
