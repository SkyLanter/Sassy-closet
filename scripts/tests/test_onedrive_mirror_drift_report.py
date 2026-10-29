import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("r", Path(__file__).resolve().parents[1] / "onedrive_mirror_drift_report.py")
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)


def test_fixture_drift():
    assert r.main([]) == 0
    assert r.main(["--strict"]) == 1


def test_norm_ma_compare():
    rows = r.compare({"d005": 28, " v3 ": 24, "S06": 25}, {"D05": 26, "V03": 24})
    assert rows == [("D05", 28, 26, "DRIFT"), ("S06", 25, None, "NO_LIVE"), ("V03", 24, 24, "MATCH")]
