# 11 — Vercel Blob admin QA (Add / Edit / rename / persist / cache / Hold / per-color)

**LEARN TRACK (Ultra burn)** · learn → **run** · Next.js App Router + Vercel Blob.

This chapter is the **QA pack** for boutique admin: concrete curl / Node / browser scripts and print-and-tick checklists. It does **not** change Origin shop code, intake Production, or Square. Sibling architecture lives in [`04-next-blob-catalog-arch.md`](./04-next-blob-catalog-arch.md) (ISR + Blob clocks). Sibling ops live in [`03-tiny-boutique-admin.md`](./03-tiny-boutique-admin.md) (add / edit / rename law). Sibling media lives in [`05-ai-product-media.md`](./05-ai-product-media.md) (per-color bind). This file is the **pass/fail harness** those notes assume.

**Never invent mã.** The only sell-site codes this lane may name are the Boss allowlist of ten. Admin “Next mã A03” is a suggestion, not a test fixture. Do not POST a new live row to Production to “have something to QA.” [[S1]](#s1-sell-catalog-contract)

Written 2026-09-09 against `main` @ `ba33024` plus the open kit handoff on [PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18). Live headers below were fetched the same day (sell-test + intake). Granola MCP was not signed in; Slack / Linear / Notion had no extra QA script. Shop law is taken from repo contracts + live HTML, not from a recalled conversation.

---

## 0. How to use this pack

| If you need… | Jump to |
| --- | --- |
| What you may mutate vs read-only | [§1 Surfaces](#1-surfaces--what-qa-may-touch) |
| App Router + Blob map | [§3 System under test](#3-system-under-test--app-router--blob) |
| Preflight before any Save | [§4 QA-00](#4-qa-00--preflight) |
| Add mã | [§5 QA-A](#5-qa-a--add-mã) |
| Edit (same identity) | [§6 QA-B](#6-qa-b--edit-same-mã) |
| Rename | [§7 QA-C](#7-qa-c--rename-mã) |
| Blob persist / redeploy | [§8 QA-D](#8-qa-d--blob-persist) |
| Cache bust after Save | [§9 QA-E](#9-qa-e--cache-bust-after-save) |
| Hold display | [§10 QA-F](#10-qa-f--hold-display) |
| Per-color photos | [§11 QA-G](#11-qa-g--per-color-photos) |
| One golden path | [§12](#12-golden-path--90-minutes-sell-test--local-intake) |
| Printable ticks | [§15](#15-printable-checklists) |

**Default stance:** live sell-test and intake Production are **read-only** until Boss says yes in `#shop-decisions`. Mutation scripts run against **local** `SASSY_DATA_DIR` (intake) or a **Preview** shop — never invent a Production mã to fill a hole.

A screenshot of `/admin` is **not** a pass. Headers, bytes, and a second GET after Save are.

---

## 1. Surfaces — what QA may touch

```
 Square Free        on-hand SoT (later). Boss Save only.  QA: never Save.
 Official Excel     working copy / AO001 mã index.        QA: no invented --ma.
 OD hub + Photos/   sassycloset.xlsx All + Photos/{MA}/   QA: source of files.
 Intake Next+Blob   sassy-closet.vercel.app               QA: local mutate; Production = read + redeploy proof.
 Sell Next+Blob     sassy-closet-shop.vercel.app          QA: read-only scripts; Save is Origin / Boss.
 catalog.v1 JSON    PR #18 export / validate              QA: hard-fail extras.
```

| Surface | URL / path | Admin | Persist | QA mutate? |
| --- | --- | --- | --- | --- |
| **Intake** | https://sassy-closet.vercel.app · repo `sassy-closet/` | `/admin` = CSV + Kho. Tabs: Món mới / Sửa / Tìm mã / Ask | Blob `sassy-closet/store.json` + `sassy-closet/photos/` | **Local / Preview only.** Production Lưu only with a Boss-owned draft mã |
| **Sell-test** | https://sassy-closet-shop.vercel.app · `/admin` | Per-mã editor. Storage: Vercel Blob. Catalog (10) | Origin shop Blob (not this repo) | **Read scripts always.** Save {MA} only if Boss wants a cache drill — then **restore** |
| **Official** | *new* project (never intake DNS) | Same family as sell-test | Own Blob | Same as sell-test after clone |
| **Kit JSON** | `out/sell-catalog.v1.json` on [PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) | n/a | File | Validate only. Do not hand-mint products |

[[S2]](#s2-clone-to-official) [[S3]](#s3-intake-readme) [[S4]](#s4-live-2026-09-09)

Hard stops on every script:

- Never invent mã, $, qty, hex, titles, or photo bytes.
- Never Square Save / Facebook Post-Send from QA.
- Never commit `BLOB_*` **values**, Square tokens, or customer names.
- Never treat intake `nextMa()` or admin **Next mã A03** as an assigned sell-site code.

---

## 2. Allowlist (cite, do not extend)

Boss table. Scripts **must** hard-fail on any other code. [[S1]](#s1-sell-catalog-contract)

| Mã | Type | USD | Sell status | Recorded colors (hub) | Real HQ files |
| --- | --- | --- | --- | --- | --- |
| A01 | top | 25 | available | `kem`, `xanh` | `001.jpg`, `002.jpg` |
| S01 | set | 28 | available | `kem` | `001.jpg` |
| P01 | accessory | 5 | available | `hoa` | `001.jpg`, `002.jpg` |
| **P02** | thermos | — | **hold** | `do` | `001.jpg`, `002.jpg` |
| P03 | accessory | 18 | available | `den`, `do` | `001.jpg`, `002.jpg`, `003.jpg` |
| P04 | accessory | 13 | available | `kem` | `001.jpg`, `002.jpg` |
| **P05** | thermos | — | **hold** | `hong`, `do`, `xanh` | `001.jpg`, `002.jpg`, `003.jpg` |
| K01 | jacket | 37 | available | *(none)* | `001.jpeg`, `002.jpeg` |
| H01 | hair | 8 | available | *(none)* | `001.jpeg`, `002.jpeg`, `003.jpeg` |
| A02 | top | 22 | available | `cham-bi` | `001.jpeg`, `002.jpeg` |

`P05` may show `23` on hub All. **Do not publish $23.** Hold ⇔ `priceUsd` is JSON `null`. [[S1]](#s1-sell-catalog-contract)

Live sell-test tiles (2026-09-09) match this table: A01 $25, S01 $28, P01 $5, P02 Hold · Inbox for price, P03 $18, P04 $13, P05 Hold · Inbox for price, K01 $37, H01 $8, A02 $22. `/m/A03` is **404**. `/admin` still prints **Next mã A03** — ignore it. [[S4]](#s4-live-2026-09-09)

Two alphabets (do not coerce in a script):

| Alphabet | Shape | Where |
| --- | --- | --- |
| Hub / sell | `A01` (letter + 2–3 digits) | Intake `parseHubMa`, sell `SELL_MA_RE`, this QA pack |
| SoT / Square | `AO001` | Official Excel, Square SKU until the A01 handoff |

`A01` ≠ `A001` ≠ `AO001`. A test that “normalizes” across alphabets is a fail. [[S5]](#s5-schema-py) [[S6]](#s6-intake-mint)

---

## 3. System under test — App Router + Blob

QA is testing **two clocks** that lie independently: Next.js route cache and Vercel Blob CDN. A Save that writes Blob but does not bust HTML, or that busts HTML but `get()`s a 60-second-old JSON, both look like “Save is broken.”

### 3.1 Intake (this repo) — mutation store, already uncached

| Piece | Path | App Router | Blob |
| --- | --- | --- | --- |
| Home (four tabs) | `sassy-closet/app/page.tsx` | `export const dynamic = "force-dynamic"` | Reads `store.json` via `getFx()` → `get(..., { useCache: false })` |
| CSV admin | `sassy-closet/app/admin/page.tsx` | `force-dynamic` | `storeHealth()` only (env), no catalog list |
| Create | `POST /api/submissions` | Route Handler | `put(STORE_BLOB_PATH, …, { allowOverwrite, addRandomSuffix: false, cacheControlMaxAge: 0 })` + `writePhoto` |
| Edit / rename | `PATCH /api/submissions/{ma}` | Route Handler | Same write; new photos under **new** `{ma}/00n.ext` |
| Photo proxy | `GET /api/photos/[...path]` | Route Handler | `get(PHOTO_BLOB_PREFIX+rel, { useCache: true })` — **cached** |
| Find card | `GET /api/ma/{code}` | Route Handler | Store read (no-cache) |
| Export | `GET /api/export` | Route Handler | CSV from store |
| List + health | `GET /api/submissions` | Route Handler | `{ submissions, storage }` |

Live intake (2026-09-09): `/admin` → `cache-control: private, no-cache, no-store, max-age=0, must-revalidate`, `x-vercel-cache: MISS`, Kho **durable (Vercel Blob)**. `/api/submissions` and `/api/export` → `x-vercel-cache: MISS`. That is the correct default for a **mutation store**. [[S4]](#s4-live-2026-09-09) [[S7]](#s7-store-backend) [[S8]](#s8-intake-admin)

```129:147:sassy-closet/lib/store-backend.ts
    async readStore() {
      const result = await getBlobOrNull(STORE_BLOB_PATH, { access, useCache: false });
      // ...
    },
    async writeStore(store) {
      await put(STORE_BLOB_PATH, JSON.stringify(store, null, 2), {
        access,
        addRandomSuffix: false,
        allowOverwrite: true,
        contentType: "application/json",
        cacheControlMaxAge: 0,
      });
    },
    async readPhoto(rel) {
      const result = await getBlobOrNull(`${PHOTO_BLOB_PREFIX}${safe}`, { access, useCache: true });
```

`cacheControlMaxAge: 0` **may not be honored** — Blob docs: minimum overwrite propagation is **60 seconds**; `cacheControlMaxAge` cannot go below 60s. Anyone who `get()`s `store.json` **without** `useCache: false` can see a minute-old closet. Photos that **overwrite** `A01/001.jpg` can show the old JPEG for up to 60s (or a month if the default TTL stuck). Safer: new `002.jpg` + update the pointer (intake already increments on new uploads). [[S9]](#s9-vercel-blob) [[S10]](#s10-blob-consistent-reads)

### 3.2 Sell-test (Origin) — ISR customer pages + dynamic admin

Observed 2026-09-09 (not in this git; do not fork):

| URL | `x-vercel-cache` | `age` (sample) | `cache-control` |
| --- | --- | --- | --- |
| `/` | **STALE** | 188 | `public, max-age=0, must-revalidate` |
| `/c/ao` | **STALE** | 250 | same |
| `/m/A01` | **STALE** | 113 | same |
| `/m/P02` | **STALE** | 113 | same |
| `/m/P05` | **STALE** | 311 | same |
| `/m/A03` | **STALE 404** | 1789 | same |
| `/products/A01/cover.jpg` | **HIT** | 1749 | same · `image/jpeg` · `etag: "ff42d884…"` · `last-modified: Wed, 09 Sep 2026 18:56:32 GMT` |
| `/admin` | **MISS** | 0 | `private, no-cache, no-store, max-age=0, must-revalidate` |

`STALE` = served **old HTML** while a background regenerate runs. `max-age=0, must-revalidate` only forces the **browser / CDN to revalidate**. If Full Route Cache still has a stale RSC payload, the operator can Save Hold and still see $23. [[S11]](#s11-next-isr) [[S12]](#s12-vercel-cache-status)

App Router bust after Save (what Origin **should** do; kit does not own this code):

1. Write catalog JSON with `put(..., { allowOverwrite: true, addRandomSuffix: false })`.
2. Next read of that JSON: `get(..., { useCache: false })`.
3. `revalidatePath('/')`, `revalidatePath('/c/[slug]', 'page')`, `revalidatePath('/m/[ma]', 'page')` — **literal** `/m/P05` or the token form **plus** `'page'`. `revalidatePath('/m/[ma]')` without the type is a common miss. [[S13]](#s13-revalidate-path)
4. `revalidatePath` **marks**; regeneration happens on the **next visit**. Route Handlers do not refresh an open tab’s Router Cache. Server Actions can; a bare `POST /api/revalidate` will not update the tab you are staring at. [[S11]](#s11-next-isr)
5. Operator: `router.refresh()` or hard-refresh, then **GET the public URL twice** (first may still be STALE).
6. If regenerate **throws**, ISR **keeps the last good page**. Admin Hold + public $23 is this failure. [[S11]](#s11-next-isr)

Recommended shop admin contract (from 04; not implemented in this repo):

| Method | Path | After success |
| --- | --- | --- |
| PATCH / POST | Origin Save {MA} (Server Action or gated route) | Blob write + `revalidatePath` of `/`, `/c/*`, `/m/{ma}` |
| POST | `/api/admin/revalidate` (if landed) | Same marks; still warm the URL |
| POST | `/api/admin/catalog/import` | Reject extras; then revalidate **all** public paths |

No public `GET /api/catalog` on sell-test (404, and that 404 is itself cached). After adding a route later, a **cached 404** can keep serving until that exact path is revalidated. [[S4]](#s4-live-2026-09-09) [[S11]](#s11-next-isr)

### 3.3 Four Next.js caches + two Blob layers (cheat sheet)

| Layer | Cross-request? | Bust |
| --- | --- | --- |
| Request memoization | No | n/a |
| Data Cache (`fetch` / `unstable_cache`) | Yes | `revalidateTag` / `cache: 'no-store'` |
| Full Route Cache (HTML + RSC) | Yes | `revalidatePath`, `dynamic = 'force-dynamic'` |
| Router Cache (client) | Tab session | `router.refresh()`, Server Action revalidate |
| Vercel CDN (`x-vercel-cache`) | Yes | Cache-Control + path revalidate |
| Blob CDN (`get()`) | Yes · default ≤ 1 month · overwrite ≤ **60s** stale | `useCache: false` on **private** `get()`; **new pathname** |

Next.js 15: `fetch` is **uncached by default**. Wrapping Blob `get()` **and** `fetch(blobUrl, { next: { revalidate: 3600 } })` creates **two clocks**. Prefer SDK `useCache: false` for the mutable catalog document. [[S14]](#s14-next-caching)

---

## 4. QA-00 — Preflight

Run first. If this fails, every later script is noise.

### 4.1 Constants (copy into the shell)

```bash
# Read-only live hosts. Do not invent a third shop URL.
export INTAKE="https://sassy-closet.vercel.app"
export SHOP="https://sassy-closet-shop.vercel.app"
export ALLOWLIST="A01 S01 P01 P02 P03 P04 P05 K01 H01 A02"
export HOLD_MAS="P02 P05"
# Boss USD (available only). Hold must not appear here.
# A01=25 S01=28 P01=5 P03=18 P04=13 K01=37 H01=8 A02=22
```

### 4.2 Header dump (read-only)

```bash
dump() {
  local name="$1" url="$2"
  printf '\n===== %s %s =====\n' "$name" "$url"
  curl -sS -D - -o /tmp/qa-"$name".body -A "SassyCloset-LearnQA/1.0" --max-time 25 "$url" \
    | tr -d '\r' \
    | grep -iE '^(HTTP/|cache-control:|age:|x-vercel-cache:|x-nextjs-cache:|content-type:|etag:|last-modified:)'
}
dump intake_admin "$INTAKE/admin"
dump intake_subs  "$INTAKE/api/submissions"
dump shop_home    "$SHOP/"
dump shop_admin   "$SHOP/admin"
dump shop_a01     "$SHOP/m/A01"
dump shop_p02     "$SHOP/m/P02"
dump shop_p05     "$SHOP/m/P05"
dump shop_a03     "$SHOP/m/A03"
dump shop_cover   "$SHOP/products/A01/cover.jpg"
```

**Pass (intake Production, 2026-09-09 shape):**

- `/admin` HTML contains `Kho: durable (Vercel Blob)` and `Không Post, không Square Save.`
- `/admin` + `/api/submissions` → `x-vercel-cache: MISS` (or BYPASS). **Fail** if HIT/STALE on the mutation APIs.
- `/api/submissions` JSON: `storage.durable === true`. **Fail** if `mode` is `ephemeral` — that is the `/tmp` shredder ([PR #15](https://github.com/SkyLanter/Sassy-closet/pull/15)).

**Pass (sell-test):**

- `/admin` → `Storage: Vercel Blob`, `Catalog ( 10 )` (spacing may vary), `Test only · not in the main nav`.
- `/admin` → `private, no-store` + `x-vercel-cache: MISS`.
- Public `/`, `/c/ao`, `/m/{allowlist}` → 200 HTML. `/m/A03` → **404**.
- Public pages may be HIT or STALE. That is expected ISR. Record `etag` + `age` for QA-E.

### 4.3 Public catalog assertion (Python, read-only)

No extra deps. Uses only stdlib. **Does not invent rows** — it only asserts the ten.

```python
#!/usr/bin/env python3
"""qa_public_catalog.py — read-only sell-test. Never POST. Never mint."""
from __future__ import annotations

import re
import sys
import urllib.request

SHOP = "https://sassy-closet-shop.vercel.app"
ALLOW = ["A01", "S01", "P01", "P02", "P03", "P04", "P05", "K01", "H01", "A02"]
PRICE = {
    "A01": "25",
    "S01": "28",
    "P01": "5",
    "P03": "18",
    "P04": "13",
    "K01": "37",
    "H01": "8",
    "A02": "22",
}
HOLD = {"P02", "P05"}
UA = "SassyCloset-LearnQA/1.0"


def get(url: str) -> tuple[int, str, dict[str, str]]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=25) as res:
            headers = {k.lower(): v for k, v in res.headers.items()}
            return res.status, res.read().decode("utf-8", "replace"), headers
    except urllib.error.HTTPError as err:
        headers = {k.lower(): v for k, v in err.headers.items()}
        return err.code, err.read().decode("utf-8", "replace"), headers


def visible(html: str) -> str:
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html)


def main() -> int:
    failed = 0

    status, html, hdr = get(f"{SHOP}/")
    text = visible(html)
    print("GET /", status, "x-vercel-cache=", hdr.get("x-vercel-cache"), "age=", hdr.get("age"))
    if status != 200:
        print("FAIL home not 200")
        return 2
    for ma in ALLOW:
        if ma not in text:
            print(f"FAIL home missing {ma}")
            failed += 1
    if "A03" in text:
        print("FAIL home invented A03")
        failed += 1
    if "$23" in text:
        print("FAIL home published $23 (P05 leak)")
        failed += 1
    for ma, usd in PRICE.items():
        if f"${usd}" not in text:
            print(f"FAIL home missing ${usd} (expected for {ma})")
            failed += 1
    for ma in HOLD:
        # Live copy 2026-09-09: "Status: Hold {MA} THERMOS Inbox for price"
        window = text
        if "Inbox for price" not in window or "Hold" not in window:
            print("FAIL home missing Hold / Inbox for price")
            failed += 1
            break

    for ma in HOLD:
        st, body, _ = get(f"{SHOP}/m/{ma}")
        vis = visible(body)
        print(f"GET /m/{ma}", st)
        if st != 200:
            print(f"FAIL /m/{ma} not 200")
            failed += 1
            continue
        if "Hold" not in vis or "Inbox for price" not in vis:
            print(f"FAIL /m/{ma} missing Hold / Inbox copy")
            failed += 1
        if "$23" in vis or re.search(r"\$\s*23\b", vis):
            print(f"FAIL /m/{ma} published $23")
            failed += 1
        if re.search(r"Status:\s*Available", vis) and ma in vis[:80]:
            # Title line is "Status: Hold" on live PDP (2026-09-09).
            if "Status: Hold" not in vis:
                print(f"FAIL /m/{ma} not Status: Hold")
                failed += 1

    st, _, _ = get(f"{SHOP}/m/A03")
    print("GET /m/A03", st)
    if st != 404:
        print("FAIL /m/A03 must 404 (admin Next is unused)")
        failed += 1

    st, body, hdr = get(f"{SHOP}/admin")
    vis = visible(body)
    print("GET /admin", st, "x-vercel-cache=", hdr.get("x-vercel-cache"))
    if "Vercel Blob" not in vis:
        print("FAIL admin Storage is not Vercel Blob")
        failed += 1
    if "Catalog" not in vis or "10" not in vis:
        print("FAIL admin Catalog (10) missing")
        failed += 1
    # Next A03 may appear. That is OK. Public must not.

    print("failed=", failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
```

**Pass:** exit 0. **Fail:** home missing a allowlisted mã, `$23` anywhere public, Hold PDPs without Inbox copy, `/m/A03` not 404, admin not Blob.

Run:

```bash
python3 qa_public_catalog.py
```

(Paste into a scratch file outside git, or keep it in notes. Do **not** commit a fake catalog next to it.)

### 4.4 Kit validate (when PR #18 is checked out)

```bash
python3 excel-kit/scripts/validate_sell_catalog.py ./out/sell-catalog.v1.json
# or the kit-local twin:
python3 excel-kit/scripts/validate_sell_catalog.py excel-kit/samples/sell-catalog.v1.json
```

**Pass:** schema `catalog.v1`, exactly those ten in that order, P02/P05 `status=hold` + `priceUsd` null, every `colorId` is null or in that product’s `colors[].id`, no `cost` / `source_link` / `blob:` URLs. **Fail:** extra `A03`, P05 priced 23, invented hex, kind-tab merge. [[S1]](#s1-sell-catalog-contract) [[S15]](#s15-sell-catalog-py)

### 4.5 Intake unit preflight (laptop)

```bash
cd sassy-closet
npm test
npm run typecheck
```

Locked today: `storageMode` local / ephemeral / durable; save does not invent *extra* mãs beyond `nextMa`; `parseStore` refuses garbage overwrite; `realPhotoPaths` never invents files; find-card does not invent on-hand from staged colors. [[S16]](#s16-intake-tests)

---

## 5. QA-A — Add mã

Three gates (from 03). QA tests the **gate**, not “can I type A03.”

1. **Identity** — Boss/Stock assigned, **or** intake-only draft that will **not** be exported.
2. **Facts** — real photos / colors / empty-better-than-invented.
3. **Publication** — sell / Square / Facebook are separate yeses.

### 5.1 Intake create — local only (Node)

Do **not** run this against Production. Empty `new_ma` mints `nextMa(kind)` **inside that store** (`A01` on an empty closet). That is hub-draft behavior, not a sell-site assignment. [[S17]](#s17-store-save)

```bash
cd sassy-closet
# Isolated closet. Gitignored. Not Production.
export SASSY_DATA_DIR="$(mktemp -d /tmp/sassy-qa-XXXX)"
unset BLOB_READ_WRITE_TOKEN BLOB_STORE_ID VERCEL
npm test -- tests/store.test.ts
```

Manual API (same dir, `npm run dev` in another terminal **without** Blob env):

```bash
# 1x1 jpeg prefix is enough for hash tests; do not invent a garment photo for Production.
python3 - <<'PY'
open("/tmp/qa-dot.jpg","wb").write(
    bytes.fromhex("ffd8ffe000104a46494600010100000100010000ffd9")
)
print("wrote /tmp/qa-dot.jpg")
PY

curl -sS -F "kind=A" -F "prefix=A" -F "size=M" -F "color=Kem" \
  -F "color_note=" -F "link=" -F "pieces=[]" -F "keep_photos=[]" \
  -F "cost_usd=" -F "cost_cny=" -F "sell_usd=" -F "sell_cny=" \
  -F "photos=@/tmp/qa-dot.jpg;type=image/jpeg" \
  http://127.0.0.1:3000/api/submissions | python3 -m json.tool
```

**Pass:**

| Check | Expected |
| --- | --- |
| HTTP | 200, `submission.ma` is `A01` on an **empty** local store (first Áo) |
| Status | `staged`, `square: not_square` |
| Photos | `photo_paths: ["A01/001.jpg"]` · `GET /api/photos/A01/001.jpg` 200 |
| Saved card (UI) | **Saved · Đã lưu**, big mã, Copy mã / `?ma=` / caption starter, **no** Post / Send / Square Save |
| Kho | `/admin` still “máy local (data/)” when Blob unset |
| CSV | `GET /api/export` lists that mã · **no qty column** |
| Second POST same kind | `A02` — and **only** those two rows. Test name in repo: “does not invent extra mãs” |

**Fail:**

| Symptom | Meaning |
| --- | --- |
| 200 with `A03` on an empty store | Invented / wrong counter |
| `status` not `staged` | Publication leak |
| CSV has `qty` | Pretending to be Square |
| Production URL used | Stop. Restore nothing you did not own |

### 5.2 Intake create — explicit mã (still local)

```bash
curl -sS -F "kind=P" -F "new_ma=P10" -F "color=Đen" -F "pieces=[]" -F "keep_photos=[]" \
  http://127.0.0.1:3000/api/submissions
# Second time:
curl -sS -o /tmp/qa-dup.json -w "%{http_code}\n" -F "kind=P" -F "new_ma=P10" \
  -F "pieces=[]" -F "keep_photos=[]" \
  http://127.0.0.1:3000/api/submissions
```

**Pass:** first save `P10`. Second → **409** `Mã P10 đã có rồi — không gộp nha`. Letter-only `new_ma=P` → next unused **in this store**. Garbage → **400** “Mã mới: chữ P (ra P kế) hoặc đủ số kiểu P10”. [[S17]](#s17-store-save)

`P10` here is a **local fixture**, not a live sell-site code. Do not export it. Do not upload it to sell-test.

### 5.3 Sell-test Add — refuse invented publication

Live `/admin` (2026-09-09): “New items start on Hold. Type comes from the letter. Qty is always 1.” Grid shows **Next mã A03** / Q01 / V01 / …. [[S4]](#s4-live-2026-09-09)

**Do not click Add A03** unless Boss assigned A03 **and** the kit allowlist was revised. QA the **negative**:

```bash
# Public must not grow a tile.
curl -sS "$SHOP/" | grep -oE '\bA03\b' && echo FAIL invented A03 on home || echo PASS no public A03
curl -sS -o /dev/null -w "%{http_code}\n" "$SHOP/m/A03"   # expect 404
```

Browser checklist (no Save required):

- [ ] Add panel copy says new items start **Hold**
- [ ] Qty cannot be typed to 3 because H01 has three jpegs
- [ ] Type for letter P is accessory — **except** existing P02/P05 stay **thermos**
- [ ] There is **no** import of intake CSV into this admin
- [ ] After a mistaken Add (if someone did it): public count still 10, or Boss deleted the extra **before** `#shop-decisions` official

### 5.4 Official / Square add (not this site)

```bash
# Missing --ma must ASK STOCK. Do not invent AO001.
python3 excel-kit/sot/append_official_row.py -w "$SASSY_SOT" --name-vi "x"
# expect exit 2 + ASK_STOCK / Dashboard B21:B27
```

**Pass:** no row written. **Fail:** script minted a code. [[S18]](#s18-append-official)

---

## 6. QA-B — Edit (same mã)

Edit = facts. Rename = §7. Do not mix.

### 6.1 Intake Sửa — local / Preview

UI: **Sửa theo mã** → type a **known** local mã → **Mở** → change color note / keep photos → **Lưu thay đổi · Keep same mã**. Deep link `/?ma=A01`. [[S19]](#s19-intake-app)

```bash
# Load
curl -sS "http://127.0.0.1:3000/api/submissions/A01" | python3 -m json.tool

# PATCH: keep the existing photo, change color_note only
curl -sS -X PATCH -F "kind=A" -F "size=M" -F "color=Kem, Xanh" \
  -F "color_note=pastel nhẹ" -F "link=" -F "pieces=[]" \
  -F "keep_photos=[\"A01/001.jpg\"]" \
  -F "cost_usd=12" -F "cost_cny=" -F "sell_usd=28" -F "sell_cny=" \
  "http://127.0.0.1:3000/api/submissions/A01"
```

**Pass:**

| Check | Expected |
| --- | --- |
| Identity | `ma` still `A01` (or whichever **existing** local mã you loaded) |
| Photos | `photo_paths` still includes `A01/001.jpg` · bytes unchanged |
| Note | `color_note` updated |
| Missing mã | `GET` / `PATCH` unknown → **404** `Không tìm thấy mã này` |
| Tìm mã | `GET /api/ma/A01` → staged fields + `staged_only: true` if `on_hand` empty — **no invented qty** |
| Saved card | Opens with the **same** mã |

Repo lock: `tests/source-link.test.ts` “PATCH / Sửa extracts URL and does not wipe other fields or photos.” [[S16]](#s16-intake-tests)

**Fail (silent save):**

| Check | Expected fail mode |
| --- | --- |
| `keep_photos` invalid JSON | Parsed as `[]` — **photos vanish** ([`form-save.ts`](../../sassy-closet/lib/form-save.ts)). QA: send valid JSON array |
| `pieces` invalid JSON | Same silent `[]`. Live UI already sends `[]` — do not “fix” by inventing Piece rows |
| Empty keep + no new files | Hashes cleared on purpose. Confirm you meant wipe |

### 6.2 Sell-test Edit — Save {MA} (Boss / Origin)

`/admin` per tile (2026-09-09): Hold / Available, Price USD, bilingual titles + descriptions, **Boxes only — no names on the swatches**, Add URL / Upload image, **Save {MA}**. [[S4]](#s4-live-2026-09-09)

Read-only QA (no Save):

```bash
# Admin HTML should list each allowlisted mã once.
python3 - <<'PY'
import re, urllib.request
html = urllib.request.urlopen(urllib.request.Request(
    "https://sassy-closet-shop.vercel.app/admin",
    headers={"User-Agent":"SassyCloset-LearnQA/1.0"},
)).read().decode("utf-8","replace")
for ma in "A01 S01 P01 P02 P03 P04 P05 K01 H01 A02".split():
    n = len(re.findall(rf"\b{ma}\b", html))
    print(ma, n)
    if n < 1:
        raise SystemExit(f"FAIL admin missing {ma}")
print("PASS admin mentions all ten")
PY
```

If Boss authorizes a **reversible** edit (e.g. tweak `titleEn` on A01 then put it back):

1. Note current public sentence on `/m/A01` (“One unique top on hand. Message A01…” on 2026-09-09).
2. Save {A01} on `/admin`.
3. Immediately run **§9 QA-E** on `/m/A01`, `/`, `/c/ao`.
4. Restore the old title. Save again. Warm again.
5. **Do not** change P05 to $23 “to see if Hold works.” Hold QA is §10.

**Pass:** public HTML matches admin after warm (two GETs). **Fail:** admin new, public old, `x-vercel-cache: HIT` with pre-Save `etag`.

### 6.3 Sell JSON edit (kit)

Re-export from **All** after Boss changes price/Hold. `xlsx` disagreeing with Boss USD → exporter **hard-fail**. Do not hand-edit `out/sell-catalog.v1.json` to invent `titleEn`. [[S15]](#s15-sell-catalog-py)

---

## 7. QA-C — Rename mã

Most dangerous admin op. Photo paths, captions, Square SKU, Messenger threads, and JSON keys all follow the code.

### 7.1 Intake rename — local

UI: Sửa → **Đổi mã · Change code** (`data-testid="rename-ma"`). Placeholder `P` or `P10`. Changing **kind** while editing **suggests** `nextMa(nextKind, knownMas)` into the box — treat as a **draft suggestion**, not Stock. [[S19]](#s19-intake-app)

```bash
# Rename local A01 → A10 (fixture, not live stock)
curl -sS -X PATCH -F "kind=A" -F "new_ma=A10" -F "color=Kem" \
  -F "pieces=[]" -F "keep_photos=[\"A01/001.jpg\"]" \
  "http://127.0.0.1:3000/api/submissions/A01"
```

**Pass:**

| Check | Expected |
| --- | --- |
| Response `ma` | `A10` |
| Saved card | Big **A10** |
| `GET /api/submissions/A01` | **404** |
| `GET /api/submissions/A10` | 200, same id / created_at |
| Collision | Rename onto an existing local mã → **409** không gộp |
| Kind letter only | `new_ma=Q` → next Q in **this** store |

**Photo caveat (must run, do not skip):** `saveSubmission` writes **new** bytes under `{newMa}/00n`. `keep_photos` still lists `{oldMa}/001.jpg` unless rewritten. [[S17]](#s17-store-save)

```bash
curl -sS -o /dev/null -w "old:%{http_code}\n" "http://127.0.0.1:3000/api/photos/A01/001.jpg"
curl -sS -o /dev/null -w "new:%{http_code}\n" "http://127.0.0.1:3000/api/photos/A10/001.jpg"
curl -sS "http://127.0.0.1:3000/api/ma/A10" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['staged']['photo_paths'])"
```

**Pass:** at least one URL **200** for the **current** `photo_paths`. **Fail:** thumbs 404 and someone “fills” with a random image — that is inventing photos. Re-upload the **same** bytes or copy Blob objects. Never invent a replacement garment.

Tìm mã + `/api/photos` for **both** codes after rename. Leftover old folder is OK; leftover **Available** public tile under the old code is not (sell-test).

### 7.2 Sell-test / official rename

Allowlist is the product id. A rename is “remove old slot + add new assigned slot” — **today the allowlist is closed**. QA the negative:

```bash
# Must stay 404 / absent. Do not create A01b.
curl -sS -o /dev/null -w "%{http_code}\n" "$SHOP/m/A01b"
```

Do not mint a parallel tile. Official Excel + Square SKU + `Photos/{MA}/` must move together **when Stock says** — not from this pack. [[S2]](#s2-clone-to-official)

---

## 8. QA-D — Blob persist

The Saved card does **not** prove durability. Production already wiped `/tmp` once. [[S3]](#s3-intake-readme)

### 8.1 Mode matrix

| Env | `storageMode()` | `/admin` Kho | Persist across Production Redeploy? |
| --- | --- | --- | --- |
| `BLOB_READ_WRITE_TOKEN` or `BLOB_STORE_ID` | `durable` | durable (Vercel Blob) | **Yes** (this is the pass) |
| laptop, no Vercel, no Blob | `local` | máy local (`data/`) | Local yes · Production **no** |
| `VERCEL=1`, no Blob | `ephemeral` | tạm `/tmp` | **No** — export 0, photos 404 |

```bash
cd sassy-closet
node --import tsx --test --test-concurrency=1 tests/store.test.ts
# assertion: "storageMode is local without Blob, ephemeral on Vercel, durable with Blob env"
```

### 8.2 Intake Production redeploy proof (Boss / Mini Boss)

Only after a **real** Lưu of a Boss-owned mã (do not mint one for the test):

1. Note the mã from Saved card.
2. `GET $INTAKE/api/submissions` → that mã present · `storage.durable === true`.
3. `GET $INTAKE/api/photos/{ma}/001.jpg` → 200, record `content-type` + byte length.
4. `GET $INTAKE/api/export` → CSV contains that mã.
5. Vercel → intake project → Deployments → Production → **Redeploy** (no env change).
6. Repeat 2–4. Same mã, same photo bytes (or 200 with same length/hash).

**Pass:** rows + photo survive. **Fail:** export 0 / photo 404 → Blob not connected to **Production**, or `BLOB_ACCESS` mismatches store access (Private vs Public is immutable at create). [[S3]](#s3-intake-readme) [[S20]](#s20-blob-private)

```bash
# After redeploy — read-only. Replace MA with the Boss-owned code you saved. Never A03.
MA=A01   # example only if that mã already exists on intake
curl -sS "$INTAKE/api/submissions" | python3 -c "import sys,json,os
d=json.load(sys.stdin)
print('durable', d.get('storage',{}).get('durable'), 'mode', d.get('storage',{}).get('mode'))
mas=[r.get('ma') for r in d.get('submissions',[])]
print('count', len(mas))
print('has', os.environ.get('MA'), os.environ['MA'] in mas)
"
curl -sS -D - -o /tmp/qa-photo.bin "$INTAKE/api/photos/${MA}/001.jpg" | tr -d '\r' | grep -iE '^(HTTP/|content-type:)'
wc -c /tmp/qa-photo.bin
```

### 8.3 Sell-test persist

`/admin` already says **Storage: Vercel Blob** + Catalog (10). Redeploy sell-test Production once:

1. Home still lists the ten · Hold P02/P05 · no $23.
2. `/products/A01/cover.jpg` still 200 `image/jpeg`.
3. `/admin` still Catalog (10).

**Fail:** empty grid after redeploy → official/test pointed at `/tmp` or a **different** Blob. Do not “restore” by inventing ten tiles. Import `catalog.v1` + real OD files. [[S2]](#s2-clone-to-official)

### 8.4 Corrupt JSON must not become an empty closet

```bash
cd sassy-closet && node --import tsx --test --test-concurrency=1 tests/store.test.ts
# "parseStore refuses to treat garbage as an empty closet"
```

**Pass:** `{not-json` and `{}` throw `không ghi đè`. **Fail:** a 500 “fixed itself” by PUTting `{ submissions: [] }`. That is how a durable store still loses the closet. [[S7]](#s7-store-backend)

Missing Blob **404** is `null` (`isMissingBlobError`) → `emptyStore()` on first write. Different from corrupt. QA: empty durable + migrate-from-laptop only when dest is empty and source is a **known** leftover. Never invent rows to fill. [[S3]](#s3-intake-readme)

### 8.5 Three Blobs, three identities

```
intake Blob     sassy-closet/store.json + photos/     GF
sell-test Blob  Origin catalog + /products covers     experiment
official Blob   own catalog + photos                  customers
```

QA isolation (after official exists): flip Hold on official **must not** change sell-test `/m/P05`. Hit both hosts. [[S2]](#s2-clone-to-official)

Hobby caps (intake README): 1 GB, 10k simple reads / 2k writes / month. A QA loop that `get()`s the full catalog every second will burn the month. Sleep between header dumps. [[S3]](#s3-intake-readme)

---

## 9. QA-E — Cache bust after Save

This is the section that burns shops: **you saved Hold on P05 and the tile still says $23.**

### 9.1 What “busted” means (pass bar)

After Save {MA} (or import):

| Surface | Must show new facts by |
| --- | --- |
| `/admin` | Immediate (already `no-store` / MISS) |
| Blob catalog JSON (private `get`) | Immediate **if** `useCache: false`; else ≤ 60s |
| Public `/`, `/c/{slug}`, `/m/{MA}` | Next **warm** GET after `revalidatePath` — often the **second** GET if the first is STALE |
| Open admin tab | `router.refresh()` or hard-refresh (Router Cache) |
| `/products/{MA}/cover.jpg` after **overwrite** of the same pathname | New `etag` / `last-modified` · may need `?v=updatedAt` because browsers ignore your 60s CDN hope [[S21]](#s21-blob-kb) |

### 9.2 Header + body script (run before and after Save)

```bash
# qa-cache-pair.sh
# Usage: SHOP=... MA=A01 ./qa-cache-pair.sh
# Read-only. Pair with a human Save in another window.
set -euo pipefail
MA="${MA:?set MA to an allowlisted code}"
SHOP="${SHOP:-https://sassy-closet-shop.vercel.app}"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
dir="/tmp/qa-cache-$MA-$stamp"
mkdir -p "$dir"

fetch() {
  local tag="$1" url="$2"
  curl -sS -D "$dir/$tag.hdr" -o "$dir/$tag.body" -A "SassyCloset-LearnQA/1.0" "$url"
  python3 - "$dir/$tag.hdr" "$dir/$tag.body" <<'PY'
import sys, hashlib, pathlib
hdr = pathlib.Path(sys.argv[1]).read_text(errors="replace")
body = pathlib.Path(sys.argv[2]).read_bytes()
fields = {}
for line in hdr.splitlines():
    if ":" in line:
        k,v = line.split(":",1)
        fields[k.strip().lower()] = v.strip()
print("status", hdr.splitlines()[0] if hdr else "?")
for k in ("x-vercel-cache","age","etag","cache-control","last-modified","content-type"):
    if k in fields:
        print(f"{k}: {fields[k]}")
print("sha256", hashlib.sha256(body).hexdigest()[:16], "bytes", len(body))
PY
}

echo "== first GET =="
fetch 1a "$SHOP/m/$MA"
fetch 1b "$SHOP/"
echo "== second GET (warm / after Save) =="
sleep 2
fetch 2a "$SHOP/m/$MA"
fetch 2b "$SHOP/"
echo "bodies: $dir"
```

**How to read it:**

| First GET | Second GET | Verdict |
| --- | --- | --- |
| STALE, old Hold/price | HIT/MISS, **new** sha256 | Pass — SWR did its job; you looked twice |
| HIT, **old** sha256, age climbing | same etag | **Fail** — `revalidatePath` missed this path (or regenerate threw and last-good stuck) |
| MISS, new sha256 | HIT, same new sha256 | Pass |
| STALE 404 on a path you **just added** | still 404 | Cached 404 — revalidate the **exact** path [[S11]](#s11-next-isr) |

On 2026-09-09, `/m/A01` was already **STALE** with `age: 113` before any QA Save. That is the baseline, not a regression by itself. Regression = **content** disagrees with `/admin` after a documented Save + two warms.

### 9.3 Browser checklist after Save {MA}

Do this as a real user, not only curl. Intake and sell-test both apply.

1. `/admin` (or Sửa) → change one **allowed** field → Save.
2. **Do not** trust the Saved card / admin form alone.
3. New tab (or disable cache in DevTools) → open `/m/{MA}` (shop) or Tìm mã (intake).
4. Hard-refresh. If still old: wait 60s (Blob overwrite) and refresh **twice**.
5. Category page that lists that mã (`/c/ao` for A01, `/c/phu-kien` for P0x).
6. Home grid tile.
7. Compare `etag` from §9.2. If HTML sha256 unchanged and admin changed → file a cache bug, not a “GF typed wrong” bug.

Mobile + desktop: Router Cache is **per tab**. Phone Safari can keep the old RSC after desktop Save.

### 9.4 Intake-specific bust

Intake pages are `force-dynamic` + store `useCache: false`. After local Lưu:

```bash
curl -sS http://127.0.0.1:3000/api/submissions | python3 -c "import sys,json; print([r['ma'] for r in json.load(sys.stdin)['submissions']])"
curl -sS http://127.0.0.1:3000/api/ma/A01 | python3 -m json.tool
```

**Pass:** GET immediately shows the PATCH. **Fail:** only if someone later wraps `getFx` / `listSubmissions` in `unstable_cache` or `fetch(..., { next: { revalidate: 3600 } })` without tags. Add that as a review check on any intake PR that touches `app/page.tsx` or `lib/store.ts`.

Photo replace **same** `A01/001.jpg`:

```bash
# Before / after overwrite — lengths or hashes must change within 60s on a useCache:true read.
curl -sS -o /tmp/p1.bin http://127.0.0.1:3000/api/photos/A01/001.jpg
# ... PATCH new file that overwrites 001.jpg ...
sleep 5
curl -sS -o /tmp/p2.bin http://127.0.0.1:3000/api/photos/A01/001.jpg
cmp /tmp/p1.bin /tmp/p2.bin && echo "STILL OLD — wait up to 60s or write 002.jpg" || echo "bytes changed"
```

**Preferred pass:** upload became `002.jpg` and JSON pointer moved. Overwrite pass is allowed only if bytes change and the UI `img` is not browser-cached without a query string. Intake `PhotoThumbs` uses `/api/photos/{rel}` with **no** cache-buster query today — after overwrite, hard-refresh or add `?v={updated_at}` in a future PR (do not invent that change in this note).

### 9.5 Shop photo CDN

`/products/A01/cover.jpg` on 2026-09-09: `x-vercel-cache: HIT`, `age: 1749`, etag `ff42d88433b351134d6ab6693f6ce336`. After replacing the cover **in place**, QA:

```bash
curl -sS -D - -o /tmp/cover.jpg "$SHOP/products/A01/cover.jpg" \
  | tr -d '\r' | grep -iE '^(HTTP/|etag:|last-modified:|x-vercel-cache:|age:)'
# Then:
curl -sS -D - -o /tmp/cover2.jpg "$SHOP/products/A01/cover.jpg?v=$(date +%s)" \
  | tr -d '\r' | grep -iE '^(HTTP/|etag:|x-vercel-cache:)'
```

**Pass:** new etag within 60s **or** new pathname (`cover-2.jpg` / content-hash). **Fail:** tile still old after 2 minutes with the same etag and no query-bust. [[S9]](#s9-vercel-blob) [[S21]](#s21-blob-kb)

### 9.6 `generateStaticParams` must not invent mã

If Origin prerenders PDPs, the param list = **Blob products ∩ allowlist**. QA:

```bash
for ma in A03 Q01 V01 P06 AO001 A001; do
  code=$(curl -sS -o /dev/null -w "%{http_code}" "$SHOP/m/$ma")
  echo "$ma $code"
  test "$code" = "404" || echo "FAIL $ma must not be a live PDP"
done
```

Empty-state “letter placeholder” PDPs for unused next-codes are a **fail**. [[S1]](#s1-sell-catalog-contract) [[S11]](#s11-next-isr)

### 9.7 Tag vs path review (for Origin PRs)

When reviewing shop code (not in this repo):

- [ ] Save {MA} calls `revalidatePath` with `'page'` on dynamic segments
- [ ] Import revalidates `/` and every `/c/*` and every `/m/{allowlist}`
- [ ] Catalog `get` uses `useCache: false`
- [ ] Photos use immutable pathnames **or** documented 60s + `?v=`
- [ ] No `revalidate: 3600` as the **only** freshness story for Hold/price
- [ ] Failed generate does not leave last-good Available on a Hold mã — validate **before** write, assert HTML **after**

---

## 10. QA-F — Hold display

Hold is **not** one bit. A PDP that prints a single “Held” badge will lie. [[S22]](#s22-pdp-hold)

### 10.1 Dialect map (assert the **right** words on the **right** surface)

| Dialect | Values | Customer / admin copy | QA |
| --- | --- | --- | --- |
| Sell `catalog.v1` | `hold` \| `available` | Hold · Inbox for price · **no USD** | Public HTML + JSON |
| Official SoT | Available, Reserved, **Hold**, Sold, Damaged, Donated | Staff Excel. Reserved ≠ Hold | Do not scrape Excel into shop badges |
| Ma_List | in_stock, **held**, sold, archived | Lean desktop. Maps **both** Reserved and Hold → `held` | **Do not** show `held` on the shop |
| Intake submission | always `staged` | Not Hold | Saved card must not say Available |
| Intake on_hand | on_hand, reserved, sold, dead | Tìm mã block | Empty → **Staged only — not on Square On_Hand yet** |
| Orders `fulfill` | Ship, Local pickup, **Hold**, TBD | How they get it | Not Official Hold |
| Slack | “Hold {ma} past 24h?” | Boss yes/no | **No public countdown** unless a real `hold_until` exists |

[[S5]](#s5-schema-py) [[S22]](#s22-pdp-hold) [[S23]](#s23-on-hand)

### 10.2 Live sell-test copy (2026-09-09) — gold strings

Home tile:

```text
Status: Hold P02 THERMOS Inbox for price
Status: Hold P05 THERMOS Inbox for price
```

PDP `/m/P02` and `/m/P05`:

```text
Status: Hold
Inbox for price
Hold · Inbox for price. Message to buy — photo-check, no USD yet.
Thermos on Hold (photo-check). No USD sell price yet — inbox for price.
Bình giữ nhiệt đang Hold — kiểm tra ảnh.
```

**Must not appear** on those PDPs or on home: `$23`, `Status: Available` as the **hero** status for P02/P05, a ticking `23:59:12`, a personal name, a cart decrement.

Admin tile for Hold mãs: **Hold · Inbox for price** selected (not Available + Price 23).

### 10.3 Read-only Hold script

```bash
python3 - <<'PY'
import re, urllib.request

SHOP = "https://sassy-closet-shop.vercel.app"
UA = {"User-Agent": "SassyCloset-LearnQA/1.0"}

def vis(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
        html = r.read().decode("utf-8", "replace")
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html)

failed = 0
home = vis(f"{SHOP}/")
for ma in ("P02", "P05"):
    pdp = vis(f"{SHOP}/m/{ma}")
    print("====", ma)
    for needle in ("Hold", "Inbox for price", "no USD"):
        ok = needle.lower() in pdp.lower()
        print(" ", needle, "OK" if ok else "MISSING")
        failed += not ok
    if "$23" in pdp or "$23" in home:
        print(" FAIL $23")
        failed += 1
    if re.search(r"23:59|countdown|hold_until", pdp, re.I):
        print(" FAIL invented timer")
        failed += 1
print("exit", 1 if failed else 0)
raise SystemExit(1 if failed else 0)
PY
```

### 10.4 Hold ↔ Available flip (only with Boss + restore)

If `#shop-decisions` says “prove cache on Hold,” use **sell-test** (not official, not intake):

1. Snapshot `/m/P05` sha256 + admin status (should already be Hold).
2. **Do not** type 23. If you must flip to Available for a drill, use a **non-Hold** mã’s title, not P05’s price.
3. Preferred drill: change A01 `titleEn` by one word → Save → §9 → restore.
4. If Boss explicitly wants a P05 Available drill: set a **temporary** Boss USD **in the allowlist first**, Save, warm `/`, `/c/phu-kien`, `/m/P05`, then set Hold + `priceUsd` null again. Never leave $23 public.

**Pass:** Hold HTML has no dollar amount in the hero price slot (“Inbox for price”). Available HTML has **exactly** the Boss USD from §2. **Fail:** Available badge + blank price, or Hold badge + `$23`.

### 10.5 Intake Hold is not a dropdown

Intake `Submission.status` is **always** `staged`. QA:

```bash
curl -sS "$INTAKE/api/submissions" | python3 -c "import sys,json
rows=json.load(sys.stdin).get('submissions',[])
bad=[r['ma'] for r in rows if r.get('status')!='staged' or r.get('square')!='not_square']
print('non-staged', bad)
"
```

Tìm mã on-hand: if `on_hand` is missing, card must show **Staged only — not on Square On_Hand yet** (`data-testid="find-card-staged-only"`). Status string `Available` on a raw on-hand object is **dropped** (not in `on_hand|reserved|sold|dead`). Do not treat Excel Official Hold as intake on-hand. [[S23]](#s23-on-hand) [[S24]](#s24-find-ma)

### 10.6 Cross-surface Hold lies (fail these)

| Lie | Why it fails |
| --- | --- |
| Shop badge `held` | Ma_List dialect on a customer page |
| Same badge for Official Reserved and Official Hold | Dashboard already splits those COUNTIFs |
| Hold tile with Messenger “$25” | Price leaked |
| Pretty gallery on P05 + Available | Media does not release Hold [[S25]](#s25-product-media) |
| Public 24h timer from the Slack **example** “Hold AO003 past 24h?” | That mã is an **example**, not stock; no `hold_until` field |

---

## 11. QA-G — Per-color photos

A color is **not** a new mã. Per-color storage is `images[].colorId`, not `A01-KEM`. [[S25]](#s25-product-media)

### 11.1 Data shapes (assert, do not invent binds)

**Intake** (live UI 2026-09-09): one `ma`, `color` comma-joined chips, `photo_paths[]` in save order. `Piece.photos` exists on the type but **Món mới saves `pieces: []`**. CSV `color_pieces` stays empty until someone wires it. [[S19]](#s19-intake-app) [[S26]](#s26-types)

**Sell `catalog.v1`:** `colors: [{id, name}]` text-only (no invented hex). `images: [{src, colorId, order}]`. Today every exported image is `colorId: null` — **honest**, because HQ folders are flat (`001.jpg`, not `kem/001.jpg`). [[S1]](#s1-sell-catalog-contract) [[S27]](#s27-catalog-json)

Binding rule (pass bar):

> A file may join a color only when (a) the mã is allowlisted, (b) the `colorId` already exists on **that** mã, and (c) a human saw the pixels.

Otherwise `colorId` stays `null`. Shared / unassigned images are valid.

### 11.2 Recorded colors — do not add to this list

| Mã | `colors[].id` allowed | Files | Auto-map? |
| --- | --- | --- | --- |
| A01 | `kem`, `xanh` | 001–002 `.jpg` | **No** |
| S01 | `kem` | 001 `.jpg` | Optional `kem` after visual check |
| P01 | `hoa` | 001–002 `.jpg` | No `hong` |
| P02 | `do` | 001–002 `.jpg` | Hold still |
| P03 | `den`, `do` | 001–003 `.jpg` | **Do not** 001→đen, 002→đỏ, 003→invented third color |
| P04 | `kem` | 001–002 `.jpg` | Same as S01 |
| P05 | `hong`, `do`, `xanh` | 001–003 `.jpg` | Coincidence of counts ≠ mapping. Hold |
| K01 | **∅** | 001–002 `.jpeg` | `colorId` **null only**. Do not add `den` |
| H01 | **∅** | 001–003 `.jpeg` | `colorId` **null only** |
| A02 | `cham-bi` | 001–002 `.jpeg` | Do not rename to `trang` |

Chip list in intake (`kinds.ts`) has `kem` / `xanh` / `hoa` / … . `cham-bi` is a **hub slug** — keep it. [[S28]](#s28-kinds)

### 11.3 Validate colorId (kit JSON)

```python
#!/usr/bin/env python3
"""qa_color_binds.py — fail invented colorIds. Does not mint mãs."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ALLOWED = ["A01", "S01", "P01", "P02", "P03", "P04", "P05", "K01", "H01", "A02"]
# Hub export 2026-09-09 (PR #18 sample). Empty = no bind except null.
HUB_COLORS = {
    "A01": {"kem", "xanh"},
    "S01": {"kem"},
    "P01": {"hoa"},
    "P02": {"do"},
    "P03": {"den", "do"},
    "P04": {"kem"},
    "P05": {"hong", "do", "xanh"},
    "K01": set(),
    "H01": set(),
    "A02": {"cham-bi"},
}


def main(path: str) -> int:
    data = json.loads(Path(path).read_text())
    if data.get("schema") != "catalog.v1":
        print("FAIL schema")
        return 2
    failed = 0
    products = data.get("products") or []
    mas = [p.get("ma") for p in products]
    if mas != ALLOWED:
        print("FAIL allowlist order", mas)
        failed += 1
    for p in products:
        ma = p["ma"]
        ids = {c.get("id") for c in p.get("colors") or []}
        if ids != HUB_COLORS[ma]:
            print(f"FAIL {ma} colors {ids} != hub {HUB_COLORS[ma]}")
            failed += 1
        if any("hex" in (c or {}) and c.get("hex") for c in p.get("colors") or []):
            print(f"FAIL {ma} invented hex")
            failed += 1
        for im in p.get("images") or []:
            cid = im.get("colorId")
            src = im.get("src") or im.get("url") or ""
            if src.startswith("blob:"):
                print(f"FAIL {ma} blob: URL persisted")
                failed += 1
            if cid not in (None, "") and cid not in ids:
                print(f"FAIL {ma} colorId {cid} not on product")
                failed += 1
            if ma in {"K01", "H01"} and cid not in (None, ""):
                print(f"FAIL {ma} must not have a color bind yet")
                failed += 1
            for junk in ("_placeholder", "_probe", "/.keep"):
                if junk in src:
                    print(f"FAIL {ma} junk src {src}")
                    failed += 1
    print("failed", failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
```

```bash
# When PR #18 files are present:
python3 qa_color_binds.py excel-kit/samples/sell-catalog.v1.json
```

Sample on that branch (2026-09-09): all `colorId` are `null`. That **passes**.

### 11.4 Sell-test admin — per-color UX (browser)

Origin `/admin` (2026-09-09): “Colors Boxes only — no names on the swatches.” Customer PLP/PDP must stay **text** (`Kem`, `Xanh`, `Chấm bi`). [[S2]](#s2-clone-to-official) [[S4]](#s4-live-2026-09-09)

Checklist:

- [ ] Mã picker = the ten. No free-text upload mã
- [ ] Color picker = that mã’s `colors[]` + **Unassigned**. K01/H01 = Unassigned only
- [ ] **Add color** is not a staff mint (colors enter via hub → export)
- [ ] Upload appends `{ url, colorId, order: max+1 }` on an **existing** mã
- [ ] Selecting a customer color **filters** the gallery to that `colorId` ∪ `null` (APPLY in 02/05). Empty color → `—`, never another mã’s photos, never a stock placeholder
- [ ] Hold badge still visible on P02/P05 media panel
- [ ] AI upload (if any) requires `parentSrc` on the same mã; does not overwrite `Photos/{MA}/001.jpg`
- [ ] `qty` still `1` after uploading three files

### 11.5 Intake photos (local)

```bash
# After local create with 2 files:
curl -sS http://127.0.0.1:3000/api/submissions/A01 \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['submission']['photo_paths'])"
# expect ['A01/001.jpg','A01/002.jpg'] — never invent 003
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3000/api/photos/A01/001.jpg
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:3000/api/photos/A01/003.jpg  # 404 honest
```

Tìm mã thumbs: ≤3 in one row, `+N` if more, tap lightbox. Zero photos → text-only (`find-card-photos-empty`). [[S29]](#s29-photos) [[S24]](#s24-find-ma)

Find-by-photo matches **hash**, not “looks like Kem.” Wrong-file match is a fail only if hashes collide; do not invent a color from the detector.

### 11.6 Worked refusals (QA must reproduce the *no*)

| Attempt | Expected |
| --- | --- |
| Bind `A01` image to `do` | Reject — `do` not on A01 |
| Bind `K01` to `den` | Reject — empty `colors[]` |
| Map P05 001/002/003 → hồng/đỏ/xanh automatically | Reject — human only |
| Upload as mã `A03` | Reject — not allowlisted |
| Persist `blob:http://localhost/…` | `validate_catalog` fail |
| Generate Xanh twin for A01 without a Xanh photo | Leave chip, `colorId` null |
| Excel `AO001` folder merged into sell `A01` | Two alphabets — do not merge |

---

## 12. Golden path — 90 minutes (sell-test + local intake)

Print. Soft-launch stays sell-test until green.

**A. Read-only live (20 min)**

1. QA-00 header dump.
2. `qa_public_catalog.py` exit 0.
3. Hold script §10.3 exit 0.
4. `/m/A03` 404. Home has no A03. No `$23`.
5. Intake `/admin` Kho durable. `storage.durable` true.
6. Kit `validate_sell_catalog.py` PASS if PR #18 is on disk.

**B. Local intake mutate (25 min)** — `SASSY_DATA_DIR` temp, **no** Production

1. QA-A create → A01 on empty store + photo 200 + Saved card.
2. QA-A duplicate `P10` → 409.
3. QA-B PATCH color_note + keep_photos.
4. QA-C rename A01→A10 → photos checked both paths.
5. `npm test` still green.
6. **Delete the temp dir.** Do not export those mãs.

**C. Sell-test Save drill (25 min)** — Boss yes, then restore

1. Change A01 title by one word (or Origin-approved field).
2. QA-E pair script + two browser warms on `/m/A01`, `/`, `/c/ao`.
3. Restore title. Warm again.
4. Confirm P02/P05 still Hold.

**D. Persist (20 min)** — only if a **real** intake mã was saved earlier this week

1. QA-D redeploy proof on intake **or** sell-test Redeploy + ten tiles remain.
2. Do not invent a mã to have something to redeploy.

---

## 13. Automated checks already in this repo

Run these on every intake PR that touches store / photos / admin. They are **not** a substitute for live Hold/cache.

```bash
cd sassy-closet && npm test && npm run typecheck
python3 excel-kit/tests/run_checks.py
```

| Test | Guards |
| --- | --- |
| `tests/store.test.ts` | mode matrix; first save `A01` on empty; D→`D01`; second `A02`; migrate copies real bytes only; empty source copies 0; `parseStore` không ghi đè; path traversal |
| `tests/photos.test.ts` | no invented paths; `/api/photos` prefix; 3-up `+N` |
| `tests/find-ma-card.test.ts` | no invented on-hand; photo_paths stay as stored |
| `tests/source-link.test.ts` | PATCH keep photos; empty link stays empty |
| `tests/ask-and-saved.test.ts` | kind/color line; D label |
| Kit `run_checks.py` | no `ma=next`; Square template headers-only; no fake inventory in git |

Sell-catalog tests live on [PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) (`validate_catalog`, allowlist, Hold pairing). Not on `main` @ `ba33024`.

---

## 14. Failure matrix (QA → cause)

| Symptom | Likely clock | What to run |
| --- | --- | --- |
| Saved card shows mã, Redeploy export 0 | Ephemeral `/tmp` | QA-D · `/admin` Kho |
| Admin Hold, tile $23 | ISR last-good or missed `revalidatePath` | QA-E + QA-F |
| Admin new photo, tile old JPEG | Blob 60s + browser cache | QA-E §9.5 · new pathname |
| Tìm mã 404 after rename | keep_photos still old `{ma}/` | QA-C photo pair |
| Photos gone after Lưu | `keep_photos` JSON → `[]` | QA-B |
| Home shows A03 | Someone clicked Next mã | QA-A §5.3 · delete + allowlist |
| P05 $23 | Hub cell leaked | QA-F · contract Hold |
| K01 swatch named Đen | Invented color | QA-G |
| `/m/A03` 200 placeholder | `generateStaticParams` invented | QA-E §9.6 |
| Official empty after clone | Wrong Blob / intake DNS | QA-D §8.5 |
| GET `/api/catalog` 404 HIT age 1900s | Cached 404 | Revalidate exact path after adding route |
| Two tabs disagree | Router Cache | Hard-refresh each |

---

## 15. Printable checklists

### 15.1 Before any session

- [ ] I know the surface (intake local / intake Production / sell-test / official / kit JSON)
- [ ] I will not invent mã / $ / qty / hex / titles / photos
- [ ] Square Save and FB Post/Send are off
- [ ] Secret **values** stay out of git / PR / chat
- [ ] QA-00 preflight recorded (headers + `qa_public_catalog.py`)

### 15.2 Add

- [ ] Intake local: empty store → first letter-code only; 409 on collision
- [ ] Saved card: Copy mã / link / caption; no Post
- [ ] Sell-test: did **not** publish A03 / Next-grid
- [ ] Official append (if any): `--ma` required; ASK STOCK otherwise

### 15.3 Edit

- [ ] Loaded the **same** mã (Mở / Tìm / `/?ma=`)
- [ ] `keep_photos` valid JSON
- [ ] Sell Save {MA} → QA-E warm of `/`, `/c/*`, `/m/{MA}`
- [ ] P05 still not $23

### 15.4 Rename

- [ ] New mã assigned and free (409)
- [ ] Photo 200 under **current** `photo_paths`
- [ ] Old public PDP not left Available
- [ ] Did not gộp two pieces

### 15.5 Blob persist

- [ ] Intake Production: Kho durable
- [ ] Redeploy proof: mã + photo 200
- [ ] Sell-test Redeploy: Catalog (10)
- [ ] Official (if up): **own** Blob
- [ ] `parseStore` still refuses garbage

### 15.6 Cache bust after Save

- [ ] Admin MISS / no-store
- [ ] Public pair script: sha256 changed or proven STALE→HIT
- [ ] Second GET done (SWR)
- [ ] Cover image etag or `?v=` after overwrite
- [ ] `/m/A03` still 404
- [ ] Phone tab refreshed

### 15.7 Hold display

- [ ] P02 / P05: Hold · Inbox for price · no USD
- [ ] Eight priced mãs match §2
- [ ] No `held` badge, no countdown, no personal name
- [ ] Intake rows still `staged` / `not_square`
- [ ] Tìm mã empty on-hand → staged-only sentence

### 15.8 Per-color photos

- [ ] `colorId` null or ∈ that product’s ids
- [ ] K01 / H01 unbound
- [ ] P03 / P05 not auto-mapped
- [ ] Customer colors are text
- [ ] No `blob:` src, no `_placeholder`
- [ ] HQ originals not overwritten by AI
- [ ] Qty still 1

---

## 16. Related LEARN TRACK / kit

| Doc | Job |
| --- | --- |
| This file | **QA scripts** for Add / Edit / rename / Blob / cache / Hold / per-color |
| [`03-tiny-boutique-admin.md`](./03-tiny-boutique-admin.md) | Law + failure modes (silent save, seed drift, duplicate codes) |
| [`04-next-blob-catalog-arch.md`](./04-next-blob-catalog-arch.md) | ISR + Blob clocks + clone |
| [`05-ai-product-media.md`](./05-ai-product-media.md) | Lighting + bind rule + AI refusals |
| [`02-pdp-color-size-ux.md`](./02-pdp-color-size-ux.md) | Hold dialects + customer text colors |
| `excel-kit/docs/SELL_CATALOG_CONTRACT.md` (PR #18) | Schema + allowlist |
| `excel-kit/docs/CLONE_TO_OFFICIAL.md` (PR #18) | New project + own Blob |
| `sassy-closet/README.md` · `BOSS.md` | Intake Blob / four tabs |

---

## Sources

<a id="s1-sell-catalog-contract"></a>

**S1.** `excel-kit/docs/SELL_CATALOG_CONTRACT.md` on [PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) (`cursor/catalog-export-clone-official-5ad2`). `catalog.v1`, allowlist, Hold P02/P05, photo list, no invented hex/mã. Not on `main` at `ba33024`.

<a id="s2-clone-to-official"></a>

**S2.** `excel-kit/docs/CLONE_TO_OFFICIAL.md` on the same PR. New Vercel project, own Blob, “do not mint A03”, Messenger / Zelle, go-live ticks.

<a id="s3-intake-readme"></a>

**S3.** [`sassy-closet/README.md`](../../sassy-closet/README.md) + [`sassy-closet/BOSS.md`](../../sassy-closet/BOSS.md) — durable Blob, Hobby caps, restore, Tìm mã, never invent, Redeploy proof.

<a id="s4-live-2026-09-09"></a>

**S4.** Live GET 2026-09-09 this run: https://sassy-closet-shop.vercel.app `/` `/admin` `/c/ao` `/m/A01` `/m/P02` `/m/P05` `/m/A03` `/products/A01/cover.jpg`; https://sassy-closet.vercel.app `/admin` `/api/submissions` `/api/export`. Cache headers and Hold/price copy as quoted in §3.2, §10.2.

<a id="s5-schema-py"></a>

**S5.** [`excel-kit/schema.py`](../../excel-kit/schema.py) — `MA_RE` AO001, `SOT_OFFICIAL_STATUS`, `OFFICIAL_TO_MA_LIST_STATUS`, `ASK_STOCK_MA`, A01 cutover comment.

<a id="s6-intake-mint"></a>

**S6.** [`sassy-closet/lib/mint.ts`](../../sassy-closet/lib/mint.ts) — `parseHubMa`, `nextMa`, `formatMa`.

<a id="s7-store-backend"></a>

**S7.** [`sassy-closet/lib/store-backend.ts`](../../sassy-closet/lib/store-backend.ts) — `STORE_BLOB_PATH`, `PHOTO_BLOB_PREFIX`, `useCache`, `cacheControlMaxAge: 0`, `parseStore`, `isMissingBlobError`, migrate-once.

<a id="s8-intake-admin"></a>

**S8.** [`sassy-closet/app/admin/page.tsx`](../../sassy-closet/app/admin/page.tsx) — `force-dynamic`; CSV + Kho; no Post / Square Save. [`sassy-closet/app/page.tsx`](../../sassy-closet/app/page.tsx) — `force-dynamic`.

<a id="s9-vercel-blob"></a>

**S9.** [Vercel Blob](https://vercel.com/docs/vercel-blob) — CDN cache up to 1 month; overwrite / delete may take **60s**; `cacheControlMaxAge` minimum 60s; `allowOverwrite` / `addRandomSuffix`.

<a id="s10-blob-consistent-reads"></a>

**S10.** [Vercel Blob consistent reads (2026-07-14)](https://vercel.com/changelog/vercel-blob-now-supports-consistent-reads-on-private-storage) — `get({ useCache: false })`; new pathname is immediately consistent.

<a id="s11-next-isr"></a>

**S11.** [Incremental Static Regeneration (App Router)](https://nextjs.org/docs/app/guides/incremental-static-regeneration) — stale-while-revalidate; `revalidatePath` marks, next visit regenerates; failed regenerate keeps last good page; `generateStaticParams`; Proxy not applied on on-demand ISR.

<a id="s12-vercel-cache-status"></a>

**S12.** [Vercel cache status](https://vercel.com/docs/caching/cache-status) — `HIT` / `MISS` / `STALE` / `REVALIDATED`. STALE = serve old, refresh in background.

<a id="s13-revalidate-path"></a>

**S13.** [`revalidatePath`](https://nextjs.org/docs/app/api-reference/functions/revalidatePath) — literal path vs `/m/[ma]` + `'page'`; Route Handler vs Server Action.

<a id="s14-next-caching"></a>

**S14.** [Next.js 15 caching](https://nextjs.org/docs/15/app/guides/caching) — four caches; Next 15 `fetch` uncached by default; Data Cache vs memoization; `revalidatePath` vs `router.refresh`.

<a id="s15-sell-catalog-py"></a>

**S15.** `excel-kit/sell_catalog.py` + `excel-kit/scripts/validate_sell_catalog.py` on PR #18 — `SCHEMA_ID`, `SELL_ALLOWLIST`, `SELL_ALLOWLIST_PRICE_USD`, `validate_catalog`, Hold ⇔ `priceUsd` null.

<a id="s16-intake-tests"></a>

**S16.** `sassy-closet/tests/store.test.ts`, `photos.test.ts`, `find-ma-card.test.ts`, `source-link.test.ts`, `ask-and-saved.test.ts`.

<a id="s17-store-save"></a>

**S17.** [`sassy-closet/lib/store.ts`](../../sassy-closet/lib/store.ts) `saveSubmission` / `resolveSaveMa`; [`sassy-closet/lib/form-save.ts`](../../sassy-closet/lib/form-save.ts) silent `[]` on bad JSON.

<a id="s18-append-official"></a>

**S18.** [`excel-kit/sot/append_official_row.py`](../../excel-kit/sot/append_official_row.py) — `--ma` required; duplicate refuse; ASK STOCK.

<a id="s19-intake-app"></a>

**S19.** [`sassy-closet/components/IntakeApp.tsx`](../../sassy-closet/components/IntakeApp.tsx) — Món mới / Sửa / rename / `pieces: []` / Saved card. [`SavedCard.tsx`](../../sassy-closet/components/SavedCard.tsx).

<a id="s20-blob-private"></a>

**S20.** [Private Blob storage](https://vercel.com/docs/vercel-blob/private-storage) + [Blob + Next.js](https://vercel.com/kb/guide/vercel-blob) — proxy through a Route Handler; store access mode fixed at create.

<a id="s21-blob-kb"></a>

**S21.** [Vercel Blob troubleshooting](https://vercel.com/kb/guide/vercel-blob) — overwrite visible in ~60s; browsers need `?v=` (or new pathname) to drop their copy.

<a id="s22-pdp-hold"></a>

**S22.** [`docs/ai-clothing-shop/02-pdp-color-size-ux.md`](./02-pdp-color-size-ux.md) §10 — Hold ≠ Reserved ≠ Orders fulfill Hold; no invented countdown. [`excel-kit/DESIGN_NOTES.md`](../../excel-kit/DESIGN_NOTES.md) — do not mix status dialects on one sheet.

<a id="s23-on-hand"></a>

**S23.** [`sassy-closet/lib/on-hand.ts`](../../sassy-closet/lib/on-hand.ts) — `STAGED_ONLY_MESSAGE`; `ON_HAND_STATUSES`; empty bag stays empty.

<a id="s24-find-ma"></a>

**S24.** [`excel-kit/prompts/FIND_MA_CARD_2026-09-08.md`](../../excel-kit/prompts/FIND_MA_CARD_2026-09-08.md) + [`sassy-closet/components/FindMaCard.tsx`](../../sassy-closet/components/FindMaCard.tsx) + [`sassy-closet/app/api/ma/[code]/route.ts`](../../sassy-closet/app/api/ma/[code]/route.ts).

<a id="s25-product-media"></a>

**S25.** [`docs/ai-clothing-shop/05-ai-product-media.md`](./05-ai-product-media.md) — bind rule; K01/H01 null; P03/P05 no auto-map; AI is a labeled child.

<a id="s26-types"></a>

**S26.** [`sassy-closet/lib/types.ts`](../../sassy-closet/lib/types.ts) — `Piece`, `Submission`, `MaLookup`.

<a id="s27-catalog-json"></a>

**S27.** `excel-kit/samples/sell-catalog.v1.json` / `out/sell-catalog.v1.json` on PR #18 (`exportedAt` `2026-09-09T01:42:55Z`). All `colorId` null.

<a id="s28-kinds"></a>

**S28.** [`sassy-closet/lib/kinds.ts`](../../sassy-closet/lib/kinds.ts) — letters + color chips. Hub slug `cham-bi` is not a chip rename.

<a id="s29-photos"></a>

**S29.** [`sassy-closet/lib/photos.ts`](../../sassy-closet/lib/photos.ts) + [`components/PhotoThumbs.tsx`](../../sassy-closet/components/PhotoThumbs.tsx) — 3-up row; never invent paths. [PR #14](https://github.com/SkyLanter/Sassy-closet/pull/14).

<a id="s30-pr15"></a>

**S30.** [PR #15](https://github.com/SkyLanter/Sassy-closet/pull/15) — Durable Vercel Blob store; missing Blob ≠ crash.

<a id="s31-kit-md"></a>

**S31.** [`excel-kit/KIT.md`](../../excel-kit/KIT.md) — env **names** only (`BLOB_READ_WRITE_TOKEN`, `BLOB_STORE_ID`, `BLOB_ACCESS`).

<a id="s32-repo-readme"></a>

**S32.** [`README.md`](../../README.md) — Square Free = on-hand SoT; bots draft only; never invent mã.

---

*End of 11. If `SELL_CATALOG_CONTRACT.md` merges with a different allowlist or Hold table, update §2 and the Python asserts from that file — do not keep a shadow price list in this note.*
