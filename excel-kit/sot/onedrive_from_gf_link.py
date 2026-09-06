#!/usr/bin/env python3
"""Canonicalize personal OneDrive From GF browse URLs for Kit / Mini Boss.

Microsoft Graph often returns personal-folder webUrl like:

  https://onedrive.live.com?cid=7a74d53e91d4f05f&id=7A74D53E91D4F05F!sae89effd79104c01a63f092754d1c9f9

That shape 404s for Boss: no slash after `.com`, and `!` in `id` is not
encoded. This helper prints a canonical owner-browse URL. It does **not**
mint guest share tokens (`1drv.ms` / `authkey`).

Prefer Graph createLink type=edit when the shop already has MSAL/Graph
credentials. This repo documents none — print Boss Share steps and exit 0.

Usage:
  python3 excel-kit/sot/onedrive_from_gf_link.py --cid CID --item-id ID
  python3 excel-kit/sot/onedrive_from_gf_link.py --web-url 'https://onedrive.live.com?cid=...&id=...'
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from urllib.parse import parse_qs, unquote, urlparse

# Keep in sync with schema.ONEDRIVE_FROM_GF. Do not import schema — that
# pulls openpyxl, and this helper must --help with stdlib only.
ONEDRIVE_FROM_GF = "Documents/Sassy Closet/From GF"

LIVE_HOSTS = {"onedrive.live.com", "www.onedrive.live.com"}
SHARE_HOST_MARKERS = ("1drv.ms", "1drv.com")
GUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
HEX32_RE = re.compile(r"^[0-9a-fA-F]{32}$")
CID_HEX_RE = re.compile(r"^[0-9a-fA-F]{8,}$")
PERSONAL_S_ID_RE = re.compile(
    r"^(?P<cid>[0-9a-fA-F]{8,})!(?P<rest>s[0-9a-fA-F]{32})$",
    re.IGNORECASE,
)
BANG_ID_RE = re.compile(
    r"^(?P<cid>[0-9a-fA-F]{8,})!(?P<rest>.+)$",
    re.IGNORECASE,
)

# Graph item.webUrl for this shop's From GF folder (owner browse — often 404s as-is).
EXAMPLE_BROKEN_WEB_URL = (
    "https://onedrive.live.com?cid=7a74d53e91d4f05f"
    "&id=7A74D53E91D4F05F!sae89effd79104c01a63f092754d1c9f9"
)

GRAPH_STEPS = """\
Graph createLink: this repo has no MSAL / Graph credentials.
Do not invent client secrets, passwords, or 1drv.ms / authkey tokens.

If Kit later documents Graph auth, call (type=edit so GF can upload):
  POST https://graph.microsoft.com/v1.0/me/drive/items/{item-id}/createLink
  body: {"type": "edit", "scope": "anonymous"}
  use the JSON field link.webUrl — never mint the token by hand.

Until then, guest share stays manual (Boss):
  1. Open From GF in OneDrive while signed in (canonical browse URL above).
  2. Share → Can edit (not view-only).
  3. Copy the link Microsoft generates (usually 1drv.ms) and send THAT to GF.
  4. Do not paste raw Graph item.webUrl (`onedrive.live.com?cid=&id=`).

Docs: excel-kit/templates/from_gf/LINKING.md
"""


class LinkError(ValueError):
    """Bad --cid / --item-id / --web-url; not a Graph failure."""


@dataclass
class LinkPlan:
    cid: str | None = None
    item_id: str | None = None
    guid: str | None = None
    canonical_browse: str | None = None
    guid_browse: str | None = None
    redir: str | None = None
    path_browse: str | None = None
    guest_share: str | None = None
    input_was_broken_browse: bool = False
    warnings: list[str] = field(default_factory=list)


def encode_bang(value: str) -> str:
    """Encode `!` as %21 once (unquote first so %21 is not double-encoded)."""
    return unquote(value or "").replace("!", "%21")


def normalize_cid(cid: str | None) -> str | None:
    if cid is None:
        return None
    text = unquote(str(cid)).strip().strip("{}").replace("-", "").lower()
    if text.startswith("cid="):
        text = text[4:]
    if not text:
        return None
    if not CID_HEX_RE.match(text):
        raise LinkError(f"cid looks wrong (want hex, got {cid!r}).")
    return text


def hyphenate_guid(hex32: str) -> str:
    h = hex32.lower()
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def guid_from_item_id(item_id: str | None) -> str | None:
    """Personal Graph ids look like CID!s<32hex>. Search webUrl uses the GUID form."""
    if not item_id:
        return None
    raw = unquote(item_id).strip()
    if GUID_RE.match(raw):
        return raw.lower()
    compact = raw.replace("-", "")
    if HEX32_RE.match(compact):
        return hyphenate_guid(compact)
    match = PERSONAL_S_ID_RE.match(raw)
    if match:
        rest = match.group("rest")
        return hyphenate_guid(rest[1:])
    if raw.lower().startswith("s") and HEX32_RE.match(raw[1:]):
        return hyphenate_guid(raw[1:])
    return None


def normalize_item_id(item_id: str | None, cid: str | None = None) -> str | None:
    if item_id is None:
        return None
    raw = unquote(str(item_id)).strip()
    if not raw:
        return None
    match = BANG_ID_RE.match(raw)
    if match:
        left = match.group("cid").upper()
        rest = match.group("rest")
        return f"{left}!{rest}"
    if cid:
        cid_norm = normalize_cid(cid)
        if cid_norm is None:
            return None
        prefix = cid_norm.upper()
        if GUID_RE.match(raw) or HEX32_RE.match(raw.replace("-", "")):
            hex32 = raw.replace("-", "").lower()
            return f"{prefix}!s{hex32}"
        if raw.lower().startswith("s") and HEX32_RE.match(raw[1:]):
            return f"{prefix}!{raw}"
        return f"{prefix}!{raw}"
    if GUID_RE.match(raw):
        return raw.lower()
    return raw


def is_guest_share_url(url: str) -> bool:
    text = (url or "").strip().lower()
    if not text:
        return False
    if any(marker in text for marker in SHARE_HOST_MARKERS):
        return True
    if "authkey=" in text:
        return True
    if "sharepoint.com" in text and (
        "/:f:/" in text or "/:u:/" in text or "/:x:/" in text or "shareid=" in text
    ):
        return True
    return False


def looks_like_broken_live_browse(url: str) -> bool:
    """True for the Graph webUrl shape Boss hit (no /? and/or raw ! in id)."""
    raw = (url or "").strip()
    if not raw:
        return False
    lowered = raw.lower()
    if "onedrive.live.com?" in lowered and "onedrive.live.com/?" not in lowered:
        return True
    parsed = urlparse(_ensure_scheme(raw))
    host = (parsed.hostname or "").lower()
    if host not in LIVE_HOSTS:
        return False
    query = parse_qs(parsed.query, keep_blank_values=True)
    item = (query.get("id") or query.get("resid") or [""])[0]
    if "!" in unquote(item) and "%21" not in item:
        return True
    if parsed.path in ("", None) and parsed.query:
        return True
    return False


def _ensure_scheme(url: str) -> str:
    text = url.strip()
    if text.startswith("//"):
        return "https:" + text
    if "://" not in text:
        return "https://" + text
    if text.lower().startswith("http://"):
        return "https://" + text[7:]
    return text


def parse_web_url(url: str) -> dict[str, str | None]:
    """Pull cid / id / resid / guid out of an owner-browse or share URL."""
    raw = _ensure_scheme(url.strip())
    parsed = urlparse(raw)
    query = parse_qs(parsed.query, keep_blank_values=True)

    def first(*keys: str) -> str | None:
        for key in keys:
            values = query.get(key) or query.get(key.lower())
            if values and str(values[0]).strip():
                return unquote(str(values[0]).strip())
        return None

    cid = first("cid")
    item = first("id", "resid")
    guid = None
    if item and GUID_RE.match(item):
        guid = item.lower()
        item_id = None
    else:
        item_id = item

    if not cid and item_id:
        match = BANG_ID_RE.match(item_id)
        if match:
            cid = match.group("cid")

    path = parsed.path or ""
    if not item_id and path.startswith("/redir"):
        item_id = first("resid", "id")

    return {"cid": cid, "item_id": item_id, "guid": guid, "url": raw}


def canonical_browse_url(cid: str, item_id: str) -> str:
    return (
        f"https://onedrive.live.com/?cid={cid.lower()}"
        f"&id={encode_bang(item_id)}"
    )


def guid_browse_url(cid: str, guid: str) -> str:
    return f"https://onedrive.live.com/?id={guid.lower()}&cid={cid.lower()}"


def redir_url(item_id: str) -> str:
    return f"https://onedrive.live.com/redir?resid={encode_bang(item_id)}"


def path_browse_url(cid: str, folder: str = ONEDRIVE_FROM_GF) -> str:
    encoded = "/".join(
        part.replace(" ", "%20") for part in folder.strip("/").split("/")
    )
    return f"https://d.docs.live.net/{cid.lower()}/{encoded}"


def _graph_auth_in_repo() -> bool:
    """Only call createLink when the kit already documents Graph/MSAL env.

    Do not invent secret names. Today: none in this repo.
    """
    return False


def build_plan(
    *,
    cid: str | None = None,
    item_id: str | None = None,
    web_url: str | None = None,
    folder_path: str = ONEDRIVE_FROM_GF,
) -> LinkPlan:
    warnings: list[str] = []
    guest_share: str | None = None
    parsed_cid = cid
    parsed_item = item_id
    parsed_guid: str | None = None
    broken = False

    if web_url:
        stripped = web_url.strip()
        if is_guest_share_url(stripped):
            guest_share = stripped
        broken = looks_like_broken_live_browse(stripped)
        extracted = parse_web_url(stripped)
        parsed_cid = parsed_cid or extracted["cid"]
        parsed_item = parsed_item or extracted["item_id"]
        parsed_guid = extracted["guid"]
        if broken:
            warnings.append(
                "Input matches the failed Graph webUrl shape "
                "(onedrive.live.com?cid=&id= without /? and/or raw !). "
                "That often 404s. Use the canonical browse URL below, or "
                "Share → Can edit for GF."
            )

    cid_norm = normalize_cid(parsed_cid) if parsed_cid else None
    item_norm = normalize_item_id(parsed_item, cid_norm)
    if item_norm and "!" in item_norm and cid_norm is None:
        cid_norm = normalize_cid(item_norm.split("!", 1)[0])
        item_norm = normalize_item_id(item_norm, cid_norm)

    guid = parsed_guid or guid_from_item_id(item_norm) or guid_from_item_id(parsed_item)
    if guid and cid_norm and (item_norm is None or "!" not in item_norm):
        item_norm = normalize_item_id(guid, cid_norm)

    if guest_share is None and not cid_norm and not item_norm and not guid:
        raise LinkError(
            "Need --cid and --item-id, or --web-url with those query params. "
            "A 1drv.ms Share link can be passed as --web-url by itself."
        )

    plan = LinkPlan(
        cid=cid_norm,
        item_id=item_norm,
        guid=guid,
        guest_share=guest_share,
        input_was_broken_browse=broken,
        warnings=warnings,
    )
    if cid_norm and item_norm and "!" in item_norm:
        plan.canonical_browse = canonical_browse_url(cid_norm, item_norm)
        plan.redir = redir_url(item_norm)
    if cid_norm and guid:
        plan.guid_browse = guid_browse_url(cid_norm, guid)
        if plan.canonical_browse is None:
            plan.canonical_browse = plan.guid_browse
    if cid_norm:
        plan.path_browse = path_browse_url(cid_norm, folder_path)
    if plan.canonical_browse is None and plan.path_browse:
        warnings.append(
            "No item id — printed the path-style From GF URL only. "
            "Pass --item-id (Graph drive item id) for the cid+id browse URL."
        )
        plan.canonical_browse = plan.path_browse
    return plan


def format_plan(plan: LinkPlan) -> str:
    lines: list[str] = []
    if plan.input_was_broken_browse or plan.warnings:
        lines.append("WARN")
        for note in plan.warnings:
            lines.append(f"  {note}")
        lines.append("")
    if plan.guest_share:
        lines.append("guest / Share link (send this to GF — already a share URL):")
        lines.append(plan.guest_share)
        lines.append("")
    lines.append("canonical browse (signed-in owner; slash after .com, ! as %21):")
    lines.append(plan.canonical_browse or "(unavailable)")
    if plan.guid_browse and plan.guid_browse != plan.canonical_browse:
        lines.append("")
        lines.append("GUID browse (Graph search webUrl shape — also has /?):")
        lines.append(plan.guid_browse)
    if plan.redir:
        lines.append("")
        lines.append("redir:")
        lines.append(plan.redir)
    if plan.path_browse:
        lines.append("")
        lines.append(f"path-style (signed-in owner, {ONEDRIVE_FROM_GF}/):")
        lines.append(plan.path_browse)
    lines.append("")
    lines.append("---")
    if _graph_auth_in_repo():
        lines.append("Graph credentials documented — would POST createLink type=edit.")
    else:
        lines.append(GRAPH_STEPS.rstrip())
    return "\n".join(lines) + "\n"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Canonicalize a personal OneDrive From GF browse URL. "
            "Fixes the Graph webUrl 404 shape (missing /? after .com, raw ! in id). "
            "Does not invent share tokens. Guest Share is still manual: "
            "Share → Can edit → copy link. Graph createLink type=edit only if "
            "MSAL/Graph env is already documented in this repo (it is not)."
        ),
        epilog=(
            "Example (the Graph webUrl that 404'd for Boss):\n"
            f"  python3 excel-kit/sot/onedrive_from_gf_link.py --web-url '{EXAMPLE_BROKEN_WEB_URL}'\n"
            "Docs: excel-kit/templates/from_gf/LINKING.md"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--cid",
        default=None,
        help="personal OneDrive cid (hex), e.g. 7a74d53e91d4f05f",
    )
    parser.add_argument(
        "--item-id",
        dest="item_id",
        default=None,
        help="Graph drive item id / resid, e.g. 7A74D53E91D4F05F!sae89…",
    )
    parser.add_argument(
        "--web-url",
        dest="web_url",
        default=None,
        help="known Graph webUrl or browse URL (canonicalized; 1drv.ms passed through)",
    )
    parser.add_argument(
        "--folder-path",
        dest="folder_path",
        default=ONEDRIVE_FROM_GF,
        help=f"path-style folder (default: {ONEDRIVE_FROM_GF})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if not args.cid and not args.item_id and not args.web_url:
        _parser().print_help(sys.stderr)
        print(
            "\nerror: pass --cid and --item-id, or --web-url.",
            file=sys.stderr,
        )
        return 2
    try:
        plan = build_plan(
            cid=args.cid,
            item_id=args.item_id,
            web_url=args.web_url,
            folder_path=args.folder_path,
        )
    except LinkError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    sys.stdout.write(format_plan(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
