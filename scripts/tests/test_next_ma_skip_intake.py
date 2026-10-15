"""Next free mã per letter, skipping catalog, held, and unpublished intake. No writes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from next_ma_skip_intake import count_fixture, count_next_free, main, next_code

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "scripts" / "tests" / "fixtures" / "next-ma-skip-intake.json"
SCRIPT = ROOT / "scripts" / "next_ma_skip_intake.py"
HELD_PATH = ROOT / "data" / "held.json"
PRODUCTS_PATH = ROOT / "sassy-closet-shop" / "data" / "products.json"
INTAKE_EXTRAS_PATH = ROOT / "sassy-closet-shop" / "data" / "intake-extras.json"
MINT_PATH = ROOT / "sassy-closet" / "lib" / "mint.ts"
INTAKE_APP_PATH = ROOT / "sassy-closet" / "components" / "IntakeApp.tsx"
HELD_BYTES = HELD_PATH.read_bytes()
PRODUCTS_BYTES = PRODUCTS_PATH.read_bytes()
INTAKE_EXTRAS_BYTES = INTAKE_EXTRAS_PATH.read_bytes()
MINT_BYTES = MINT_PATH.read_bytes()
INTAKE_APP_BYTES = INTAKE_APP_PATH.read_bytes()

CATALOG = ["Q01", "S06", "S13", "D05", "K01", "A23", "V03", "P01", "P02", "P05"]
HELD = ["S14", "S15", "S16", "K02", "K03", "K04", "K05", "K06", "A24", "A25", "A26", "V04", "V05"]


def test_fixture_skips_unpublished_intake_and_keeps_q02() -> None:
    before = FIXTURE.read_bytes()
    report = count_fixture(FIXTURE)
    assert report["next"] == {
        "A": "A29",
        "D": "D06",
        "K": "K07",
        "P": "P06",
        "Q": "Q02",
        "S": "S20",
        "V": "V06",
    }
    assert "A27" not in report["next"].values()
    assert "A28" not in report["next"].values()
    assert report["intakeNotInCatalog"] == ["A27", "A28", "S17", "S18", "S19"]
    assert "A27" in report["intakeNotInCatalog"]
    assert "Q01" in report["intake"]
    assert "Q01" not in report["intakeNotInCatalog"]
    assert "Q02" not in report["catalog"]
    assert "Q02" not in report["held"]
    assert "Q02" not in report["intake"]
    assert set(report["next"].values()).isdisjoint(report["catalog"])
    assert set(report["next"].values()).isdisjoint(report["held"])
    assert set(report["next"].values()).isdisjoint(report["intakeNotInCatalog"])
    assert report["prices"]["S06"] == "25"
    assert FIXTURE.read_bytes() == before
    _unchanged()


def test_intake_a27_is_not_the_next_a_and_q02_stays_next() -> None:
    without_intake = count_next_free(CATALOG, HELD, [])
    assert without_intake.next_by_letter["A"] == "A27"
    assert without_intake.next_by_letter["Q"] == "Q02"
    assert without_intake.intake_not_in_catalog == ()

    only_a27 = count_next_free(CATALOG, HELD, ["a27"])
    assert only_a27.next_by_letter["A"] == "A28"
    assert only_a27.next_by_letter["Q"] == "Q02"
    assert only_a27.intake_not_in_catalog == ("A27",)
    assert "A27" not in only_a27.next_by_letter.values()

    queen_already_catalogued = count_next_free(["q01"], [], ["Q01"])
    assert queen_already_catalogued.next_by_letter["Q"] == "Q02"
    assert queen_already_catalogued.intake_not_in_catalog == ()

    quoted = count_next_free(["Q01"], [], ["Q02"])
    assert quoted.next_by_letter["Q"] == "Q03"
    assert quoted.intake_not_in_catalog == ("Q02",)
    assert count_fixture(FIXTURE)["next"]["Q"] == "Q02"
    _unchanged()


def test_walk_matches_catalog_max_then_skips_held_and_intake() -> None:
    assert next_code("Q", ["Q01"], [], []) == "Q02"
    assert next_code("q", ["q01"], ["s14"], ["a27"]) == "Q02"
    assert next_code("P", ["P01"], ["P02"], []) == "P03"
    assert next_code("P", ["P01"], [], ["P02"]) == "P03"
    assert next_code("P", ["P01"], ["P02", "P03"], []) == "P04"
    assert next_code("P", ["P01", "P04"], ["P02", "P03"], ["P06"]) == "P05"
    assert next_code("P", ["P01", "P02", "P05"], [], []) == "P06"
    assert next_code("D", [], [], []) == "D01"
    assert next_code("D", ["D01", "V01"], [], []) == "D02"
    assert next_code("A", ["A23"], ["A24", "A25", "A26"], ["A27"]) == "A28"
    assert next_code("A", ["A23"], ["A24", "A25", "A26"], ["A27", "A28"]) == "A29"
    assert next_code("A", ["A23"], ["A24", "A25", "A26"], ["A27", "A29"]) == "A28"
    assert next_code("A", ["A99"], [], []) == "A100"
    assert next_code("A", [], [], ["A27"]) == "A01"


def test_lists_are_not_mutated_and_s06_other_dollar_is_refused(tmp_path: Path) -> None:
    catalog = ["q01", "S06", "A23"]
    held = ["s14", "A24", "A25", "A26"]
    intake = ["A27", "q01"]
    prices = {"S06": "25"}
    report = count_next_free(catalog, held, intake, prices)
    assert report.next_by_letter["Q"] == "Q02"
    assert report.next_by_letter["A"] == "A28"
    assert report.intake_not_in_catalog == ("A27",)
    assert report.prices["S06"] == "25"
    assert catalog == ["q01", "S06", "A23"]
    assert held == ["s14", "A24", "A25", "A26"]
    assert intake == ["A27", "q01"]
    assert prices == {"S06": "25"}

    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["prices"]["S06"] = "26"
    bad = tmp_path / "s06-26.json"
    bad.write_text(json.dumps(payload), encoding="utf-8")
    before = bad.read_bytes()
    with pytest.raises(ValueError, match="^S06 stays \\$25$"):
        count_fixture(bad)
    assert bad.read_bytes() == before

    payload["prices"]["S06"] = "24"
    with pytest.raises(ValueError, match="^S06 stays \\$25$"):
        count_next_free(payload["catalog"], payload["held"], payload["intake"], payload["prices"])
    assert payload["prices"]["S06"] == "24"
    _unchanged()


def test_cli_prints_q02_skips_a27_and_writes_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    ran = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(FIXTURE)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stderr
    payload = json.loads(ran.stdout)
    assert payload["next"]["Q"] == "Q02"
    assert payload["next"]["A"] == "A29"
    assert "A27" not in payload["next"].values()
    assert payload["intakeNotInCatalog"][0] == "A27"
    assert payload["prices"]["S06"] == "25"

    source = SCRIPT.read_text(encoding="utf-8")
    assert "write_text" not in source
    assert "write_bytes" not in source
    assert "urlopen" not in source
    assert "requests" not in source
    assert "IntakeApp" not in source
    assert "mint.ts" not in source

    def fail_read(self: Path, *args: object, **kwargs: object) -> str:
        raise AssertionError(f"read {self}")

    monkeypatch.setattr(Path, "read_text", fail_read)
    with pytest.raises(ValueError, match="^live reads are refused$"):
        count_fixture(HELD_PATH)
    with pytest.raises(ValueError, match="^live reads are refused$"):
        count_fixture(PRODUCTS_PATH)
    with pytest.raises(ValueError, match="^Live intake is not read\\. Pass a fixture file\\.$"):
        count_fixture(Path("https://sassy-closet.vercel.app/api/submissions"))
    _unchanged()


def test_cli_refuses_a_url_and_the_held_file() -> None:
    for fixture in (
        str(HELD_PATH),
        "scripts/tests/fixtures/../../../data/held.json",
    ):
        ran = subprocess.run(
            [sys.executable, str(SCRIPT), "--fixture", fixture],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        assert ran.returncode == 2, ran.stdout
        assert ran.stdout == ""
        assert "live reads are refused" in ran.stderr
    missing = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(FIXTURE.parent / "missing.json")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert missing.returncode == 2
    assert missing.stdout == ""
    _unchanged()


def test_live_intake_url_exits_nonzero_and_is_not_read(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    url = "https://sassy-closet.vercel.app/api/submissions"
    reads: list[str] = []
    original = Path.read_text

    def record_read(self: Path, *args: object, **kwargs: object) -> str:
        reads.append(str(self))
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", record_read)
    assert main(["--fixture", url]) != 0
    assert main(["--fixture", "//sassy-closet.vercel.app/api/submissions"]) == 2
    captured = capsys.readouterr()
    assert "Live intake is not read. Pass a fixture file." in captured.err
    assert url not in reads
    assert all("api/submissions" not in item for item in reads)

    ran = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", url],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert ran.returncode != 0
    assert ran.returncode == 2
    assert ran.stdout == ""
    assert "Live intake is not read. Pass a fixture file." in ran.stderr

    pointer = tmp_path / "intake-url.json"
    pointer.write_text(
        json.dumps(
            {
                "catalog": ["Q01"],
                "held": [],
                "intake": url,
            }
        ),
        encoding="utf-8",
    )
    before = pointer.read_bytes()
    pointed = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(pointer)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert pointed.returncode == 2
    assert pointed.stdout == ""
    assert "Live intake is not read. Pass a fixture file." in pointed.stderr
    assert pointer.read_bytes() == before
    source = SCRIPT.read_text(encoding="utf-8")
    assert "urllib" not in source
    assert "urlopen" not in source
    assert "requests" not in source
    assert count_fixture(FIXTURE)["next"]["Q"] == "Q02"
    assert "A27" not in count_fixture(FIXTURE)["next"].values()
    _unchanged()


def test_real_held_file_stays_held_and_s06_lock_stays_25() -> None:
    payload = json.loads(HELD_BYTES)
    assert payload["heldIncomplete"] == [
        "S14",
        "A24",
        "A25",
        "S15",
        "A26",
        "K02",
        "K03",
        "K04",
        "K05",
        "V04",
        "K06",
        "V05",
    ]
    assert payload["neverList"] == []
    assert "Q02" not in payload["heldIncomplete"]
    assert "A27" not in payload["heldIncomplete"]
    assert "S06" not in payload["heldIncomplete"]
    lock = (ROOT / "sassy-closet-shop" / "lib" / "admin-ops.ts").read_text(encoding="utf-8")
    assert 'ma === "S06" && input.priceUsd !== 25' in lock
    assert "S06 stays $25." in lock
    assert not (ROOT / "scripts" / "next_free_ma.py").exists()
    _unchanged()


def _unchanged() -> None:
    assert HELD_PATH.read_bytes() == HELD_BYTES
    assert PRODUCTS_PATH.read_bytes() == PRODUCTS_BYTES
    assert INTAKE_EXTRAS_PATH.read_bytes() == INTAKE_EXTRAS_BYTES
    assert MINT_PATH.read_bytes() == MINT_BYTES
    assert INTAKE_APP_PATH.read_bytes() == INTAKE_APP_BYTES
