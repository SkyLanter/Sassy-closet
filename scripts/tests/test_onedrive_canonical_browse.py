"""The From GF link helper must not call its own canonical output broken.

A canonical owner-browse URL is already in the fixed shape: a slash after
``.com`` and ``!`` encoded as ``%21``. ``looks_like_broken_live_browse``
decoded the query first, so the ``%21`` turned back into a bare ``!`` and
every canonical URL was reported as the failed Graph webUrl shape.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOT = ROOT / "excel-kit" / "sot"
if str(SOT) not in sys.path:
    sys.path.insert(0, str(SOT))

from onedrive_from_gf_link import build_plan, looks_like_broken_live_browse

CANONICAL = (
    "https://onedrive.live.com/?cid=7a74d53e91d4f05f"
    "&id=7A74D53E91D4F05F%21sae89effd79104c01a63f092754d1c9f9"
)
GUID_BROWSE = "https://onedrive.live.com/?id=ae89effd-7910-4c01-a63f-092754d1c9f9&cid=7a74d53e91d4f05f"
GRAPH_BROKEN = (
    "https://onedrive.live.com?cid=7a74d53e91d4f05f"
    "&id=7A74D53E91D4F05F!sae89effd79104c01a63f092754d1c9f9"
)


def test_encoded_bang_is_not_the_broken_shape() -> None:
    assert looks_like_broken_live_browse(CANONICAL) is False


def test_canonical_url_gives_no_broken_warning() -> None:
    plan = build_plan(web_url=CANONICAL)
    assert plan.canonical_browse == CANONICAL
    assert plan.input_was_broken_browse is False
    assert plan.warnings == []


def test_guid_browse_stays_quiet() -> None:
    assert looks_like_broken_live_browse(GUID_BROWSE) is False
    assert build_plan(web_url=GUID_BROWSE).warnings == []


def test_graph_weburl_is_still_broken() -> None:
    assert looks_like_broken_live_browse(GRAPH_BROKEN) is True
    plan = build_plan(web_url=GRAPH_BROKEN)
    assert plan.input_was_broken_browse is True
    assert plan.canonical_browse == CANONICAL
    assert plan.warnings
