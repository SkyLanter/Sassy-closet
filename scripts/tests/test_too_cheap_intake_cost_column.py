"""The cost CSV the intake app writes must be readable, and never silently empty.

`sassy-closet/lib/store.ts` `exportCsv()` (served by `GET /api/export`) writes the
cost column as `cost_cny`. `too_cheap_check.load_costs()` only looked for
`intake_cny`, then `baseline_cny`, so every row of a real intake export came back
with a blank intake ¥ and the mã was reported `skip-missing`.

Nothing crashed: the check printed `QUIET_OK` with `skipped` equal to the live
count. A live mã that is under target stayed invisible, which is the one outcome
this check exists to catch.

A cost file that carries a mã but no ¥ at all is now reported as unreadable
instead of quietly turning every row into a skip.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

import too_cheap_check as tc

# sassy-closet/lib/store.ts exportCsv() header, in order.
EXPORT_HEADER = [
    "ma", "kind", "kind_vi", "size", "color", "color_note", "color_pieces", "blurb",
    "cost_cny", "cost_usd", "cost_currency", "sell_cny", "sell_usd", "sell_currency",
    "source_link", "status", "square", "created_at", "updated_at", "photo_link",
    "size_options",
]

LIVE = {"products": [{"ma": "A01", "priceUsd": 20, "status": "available"},
                     {"ma": "S06", "priceUsd": 25, "status": "available"}]}


def write_export(path: Path, rows: list[dict[str, str]]) -> Path:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=EXPORT_HEADER)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in EXPORT_HEADER})
    return path


def write_kg(path: Path, kg: dict[str, str]) -> Path:
    path.write_text("ma,kg\n" + "".join(f"{ma},{value}\n" for ma, value in kg.items()), encoding="utf-8")
    return path


def run(tmp_path: Path, costs: Path, weights: Path | None = None):
    (tmp_path / "live.json").write_text(json.dumps(LIVE), encoding="utf-8")
    out = tmp_path / "r.json"
    argv = ["--live", str(tmp_path / "live.json"), "--costs", str(costs),
            "--out-json", str(out), "--out-md", str(tmp_path / "r.md")]
    if weights is not None:
        argv += ["--weights", str(weights)]
    rc = tc.main(argv)
    return rc, json.loads(out.read_text(encoding="utf-8"))


def test_load_costs_reads_the_export_cost_column(tmp_path):
    costs = write_export(tmp_path / "export.csv", [{"ma": "A01", "cost_cny": "100"}])
    assert tc.load_costs(costs)["A01"]["intake_cny"] == "100"


def test_under_target_is_found_in_a_real_export(tmp_path):
    # ¥100 / 6.723 + 10.52 * 0.3 = $18.03 landed -> target above the $20 live price.
    costs = write_export(
        tmp_path / "export.csv",
        [{"ma": "A01", "cost_cny": "100"}, {"ma": "S06", "cost_cny": "60"}],
    )
    weights = write_kg(tmp_path / "kg.csv", {"A01": "0.3", "S06": "0.5"})
    rc, summary = run(tmp_path, costs, weights)
    assert rc == 0
    assert summary["outcome"] == "UNDER_FOUND"
    assert [row["ma"] for row in summary["under_target"]] == ["A01"]
    assert summary["counts"]["skip-missing"] == 0


def test_exported_sell_usd_is_never_used_as_the_cost(tmp_path):
    # The export also carries sell_usd; a cost must not be read from it.
    costs = write_export(
        tmp_path / "export.csv",
        [{"ma": "A01", "cost_cny": "", "sell_usd": "900"}],
    )
    assert tc.load_costs(costs)["A01"]["intake_cny"] == ""


def test_intake_cny_still_wins_for_existing_cost_files(tmp_path):
    path = tmp_path / "costs.csv"
    path.write_text("ma,intake_cny,cost_cny,kg\nA01,100,999,0.3\n", encoding="utf-8")
    assert tc.load_costs(path)["A01"]["intake_cny"] == "100"


def test_a_cost_file_without_a_yen_column_is_refused(tmp_path):
    (tmp_path / "live.json").write_text(json.dumps(LIVE), encoding="utf-8")
    costs = tmp_path / "nosuchcolumn.csv"
    costs.write_text("ma,kg\nA01,0.3\n", encoding="utf-8")
    out = tmp_path / "r.json"
    with pytest.raises(SystemExit) as exit_info:
        tc.main(["--live", str(tmp_path / "live.json"), "--costs", str(costs),
                 "--out-json", str(out), "--out-md", str(tmp_path / "r.md")])
    assert exit_info.value.code == 2
    assert not out.exists()
