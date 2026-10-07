# DATA OK — 2026-10-01

**Overall: PASS** (0 FAIL). WARNs and NOTEs are listed with proof.
**Window:** night of 2026-09-30 → 2026-10-01 PT.
**Checked:** 2026-10-01T07:20:29Z (catalog fetch `Date` header). Visual smoke followed on the same live site.

Price source of truth for this run is the live sell Blob. Hub Official is the ops mirror. Intake Live/Held badges come from `intake-status.v1.json` when `LISTING_STATUS_URL` is set.

## Counts

| Leg | Live | Held | Proof |
| --- | --- | --- | --- |
| Sell Blob `catalog.v1` | 62 (`status=available`, qty 1, dropship 62) | 0 in the product list | `updatedAt` 2026-09-30T15:56:17.273Z · sha256 `5a61d106e697a781c3c829f2c1d9c11aeec41670b13627cfc1a72c3f99fa4ed3` · 73788 bytes · etag `"b0fa80e289c227eb2a7569bf18c8f603"` · `last-modified` Wed, 30 Sep 2026 15:56:59 GMT |
| Hub Official `sassycloset.xlsx` | 62 (`status=live`) | 0 | OneDrive `Documents/Sassy Closet/sassycloset.xlsx` · lastModified 2026-09-30T15:58:28Z · sha256 `141ab5e530ac8c7fdf68cc66b0e540e9eb1b288dd2be2f65622e111aa0a16af1` · 12823 bytes · sheet `Official` rows 2–63 |
| Intake submissions | 60 of the 62 live mãs are present | 6 held mãs present as `status=staged` | `GET https://sassy-closet.vercel.app/api/submissions` · 66 rows · `storage.durable=true` |
| Intake Live/Held file | unreadable | unreadable | WARN below |

Blob live mã set equals hub live mã set (62). Held set is in neither.

## Hard checks

### Held absent from live Blob

Boss held set: **S14, A24, A25, S15, A26, K02**.

| mã | In `catalog.v1` products | Shop `/m/{mã}` | Home HTML | Hub Official | Intake submission |
| --- | --- | --- | --- | --- | --- |
| S14 | absent | 404 | absent | absent | staged, `sell_usd` blank, updated 2026-09-29T22:19:14.984Z |
| A24 | absent | 404 | absent | absent | staged, `sell_usd` blank, updated 2026-09-29T23:09:19.428Z |
| A25 | absent | 404 | absent | absent | staged, `sell_usd` blank, updated 2026-09-30T01:16:45.694Z |
| S15 | absent | 404 | absent | absent | staged, `sell_usd` blank, updated 2026-09-30T01:20:46.892Z |
| A26 | absent | 404 | absent | absent | staged, `sell_usd` blank, updated 2026-09-30T01:29:12.390Z |
| K02 | absent | 404 | absent | absent | staged, `sell_usd` blank, updated 2026-09-30T16:38:58.545Z |

`GET https://sassycloset.vercel.app/api/health` `ok: true`, `productCount` 62, `shopVisible` 62, `catalogUpdatedAt` 2026-09-30T15:56:17.273Z. Health `blob.listed` still has staging objects for S14, A24, and A25 (see NOTE). Those pathnames are not referenced by any catalog product. S15, A26, and K02 have no `products/{mã}/cover.jpg` on that store (HEAD 404).

### S06 priceUsd == 25

| Leg | Value |
| --- | --- |
| Blob `priceUsd` | 25 |
| Hub `sell_usd` | 25 (`updated_at` 2026-09-30T07:21:35Z) |
| PDP JSON-LD `offers.price` | 25.00 |
| Visible PDP and search card | $25 |
| Intake submission `sell_usd` | blank (row updated 2026-09-17T01:32:41.866Z) |

Prior night (2026-09-30) recorded Blob and PDP at $22. Tonight both are 25. No reprice was written this run.

### Live mã price mismatches, Blob vs hub

**Empty. 62/62 `priceUsd` equals hub `sell_usd`.** Status pairs are Blob `available` and hub `live` for every live mã.

| mã | field | blob | hub | intake | result |
| --- | --- | --- | --- | --- | --- |
| A01 | priceUsd | 27 | 27 | — | PASS |
| A01 | status | available | live | — | PASS |
| A02 | priceUsd | 23 | 23 | — | PASS |
| A02 | status | available | live | — | PASS |
| A03 | priceUsd | 22 | 22 | — | PASS |
| A03 | status | available | live | — | PASS |
| A04 | priceUsd | 21 | 21 | — | PASS |
| A04 | status | available | live | — | PASS |
| A05 | priceUsd | 25 | 25 | — | PASS |
| A05 | status | available | live | — | PASS |
| A06 | priceUsd | 23 | 23 | — | PASS |
| A06 | status | available | live | — | PASS |
| A07 | priceUsd | 26 | 26 | — | PASS |
| A07 | status | available | live | — | PASS |
| A08 | priceUsd | 29 | 29 | — | PASS |
| A08 | status | available | live | — | PASS |
| A09 | priceUsd | 26 | 26 | — | PASS |
| A09 | status | available | live | — | PASS |
| A10 | priceUsd | 29 | 29 | — | PASS |
| A10 | status | available | live | — | PASS |
| A11 | priceUsd | 27 | 27 | — | PASS |
| A11 | status | available | live | — | PASS |
| A12 | priceUsd | 29 | 29 | — | PASS |
| A12 | status | available | live | — | PASS |
| A13 | priceUsd | 25 | 25 | — | PASS |
| A13 | status | available | live | — | PASS |
| A14 | priceUsd | 24 | 24 | — | PASS |
| A14 | status | available | live | — | PASS |
| A15 | priceUsd | 25 | 25 | — | PASS |
| A15 | status | available | live | — | PASS |
| A16 | priceUsd | 31 | 31 | — | PASS |
| A16 | status | available | live | — | PASS |
| A17 | priceUsd | 27 | 27 | — | PASS |
| A17 | status | available | live | — | PASS |
| A18 | priceUsd | 27 | 27 | — | PASS |
| A18 | status | available | live | — | PASS |
| A19 | priceUsd | 27 | 27 | — | PASS |
| A19 | status | available | live | — | PASS |
| A20 | priceUsd | 23 | 23 | — | PASS |
| A20 | status | available | live | — | PASS |
| A21 | priceUsd | 21 | 21 | — | PASS |
| A21 | status | available | live | — | PASS |
| A22 | priceUsd | 33 | 33 | — | PASS |
| A22 | status | available | live | — | PASS |
| A23 | priceUsd | 27 | 27 | — | PASS |
| A23 | status | available | live | — | PASS |
| B01 | priceUsd | 46 | 46 | — | PASS |
| B01 | status | available | live | — | PASS |
| B02 | priceUsd | 31 | 31 | — | PASS |
| B02 | status | available | live | — | PASS |
| B03 | priceUsd | 67 | 67 | — | PASS |
| B03 | status | available | live | — | PASS |
| D01 | priceUsd | 40 | 40 | — | PASS |
| D01 | status | available | live | — | PASS |
| D02 | priceUsd | 40 | 40 | — | PASS |
| D02 | status | available | live | — | PASS |
| D03 | priceUsd | 31 | 31 | — | PASS |
| D03 | status | available | live | — | PASS |
| D04 | priceUsd | 35 | 35 | — | PASS |
| D04 | status | available | live | — | PASS |
| D05 | priceUsd | 26 | 26 | — | PASS |
| D05 | status | available | live | — | PASS |
| H01 | priceUsd | 8 | 8 | — | PASS |
| H01 | status | available | live | — | PASS |
| J01 | priceUsd | 29 | 29 | — | PASS |
| J01 | status | available | live | — | PASS |
| J02 | priceUsd | 40 | 40 | — | PASS |
| J02 | status | available | live | — | PASS |
| K01 | priceUsd | 36 | 36 | — | PASS |
| K01 | status | available | live | — | PASS |
| O01 | priceUsd | 22 | 22 | — | PASS |
| O01 | status | available | live | — | PASS |
| O02 | priceUsd | 24 | 24 | — | PASS |
| O02 | status | available | live | — | PASS |
| O03 | priceUsd | 7 | 7 | — | PASS |
| O03 | status | available | live | — | PASS |
| O04 | priceUsd | 12 | 12 | — | PASS |
| O04 | status | available | live | — | PASS |
| O05 | priceUsd | 15 | 15 | — | PASS |
| O05 | status | available | live | — | PASS |
| P01 | priceUsd | 5 | 5 | — | PASS |
| P01 | status | available | live | — | PASS |
| P02 | priceUsd | 25 | 25 | — | PASS |
| P02 | status | available | live | — | PASS |
| P03 | priceUsd | 11 | 11 | — | PASS |
| P03 | status | available | live | — | PASS |
| P04 | priceUsd | 10 | 10 | — | PASS |
| P04 | status | available | live | — | PASS |
| P05 | priceUsd | 25 | 25 | — | PASS |
| P05 | status | available | live | — | PASS |
| Q01 | priceUsd | 28 | 28 | — | PASS |
| Q01 | status | available | live | — | PASS |
| S01 | priceUsd | 39 | 39 | — | PASS |
| S01 | status | available | live | — | PASS |
| S02 | priceUsd | 25 | 25 | — | PASS |
| S02 | status | available | live | — | PASS |
| S03 | priceUsd | 26 | 26 | — | PASS |
| S03 | status | available | live | — | PASS |
| S04 | priceUsd | 41 | 41 | — | PASS |
| S04 | status | available | live | — | PASS |
| S05 | priceUsd | 26 | 26 | — | PASS |
| S05 | status | available | live | — | PASS |
| S06 | priceUsd | 25 | 25 | — | PASS |
| S06 | status | available | live | — | PASS |
| S07 | priceUsd | 38 | 38 | — | PASS |
| S07 | status | available | live | — | PASS |
| S08 | priceUsd | 37 | 37 | — | PASS |
| S08 | status | available | live | — | PASS |
| S09 | priceUsd | 36 | 36 | — | PASS |
| S09 | status | available | live | — | PASS |
| S10 | priceUsd | 37 | 37 | — | PASS |
| S10 | status | available | live | — | PASS |
| S11 | priceUsd | 51 | 51 | — | PASS |
| S11 | status | available | live | — | PASS |
| S12 | priceUsd | 33 | 33 | — | PASS |
| S12 | status | available | live | — | PASS |
| S13 | priceUsd | 26 | 26 | — | PASS |
| S13 | status | available | live | — | PASS |
| V01 | priceUsd | 39 | 39 | — | PASS |
| V01 | status | available | live | — | PASS |
| V02 | priceUsd | 40 | 40 | — | PASS |
| V02 | status | available | live | — | PASS |
| V03 | priceUsd | 21 | 21 | — | PASS |
| V03 | status | available | live | — | PASS |

PDP check: all 62 `https://sassycloset.vercel.app/m/{mã}` returned 200 and JSON-LD `offers.price` equaled Blob `priceUsd`. Home HTML had 62 `sc-price` values and 62 unique `/m/{mã}` cards; each card dollar matched Blob. `data-shop-sort="popular"`. Per-category order matched `sassy-closet-shop/data/popular-order.json` filtered to live mãs (A, S, P, K, H, O, D, B, J, Q, V).

## WARN

| id | What | Proof | Boss ping |
| --- | --- | --- | --- |
| W1 | Intake Live/Held badges are off. `intake-status.v1.json` was not readable, so intake live/held counts cannot be stated from that file. | `GET https://sassy-closet.vercel.app/api/listing-status` → `{"enabled":false,"items":{}}` (28 bytes, no `error`). That response is the unset-`LISTING_STATUS_URL` path. Public probes 404: `…/intake-status.v1.json`, `…/sassy-closet/intake-status.v1.json`, `…/sassy-closet-shop/intake-status.v1.json`, `…/auto-list/intake-status.v1.json`, `…/auto-list/state/intake-status.v1.json`, `…/listing-status.v1.json` on host `efsi0jejsfy7j058.public.blob.vercel-storage.com`. No `auto-list/state` mirror in this repo. OneDrive search for `intake-status` returned nothing. | No. Held-off-sell is already true on Blob, hub, and the shop. Setting the public URL is an env follow-up for Mini Boss, same gap as 2026-09-30. |

## NOTE

| id | What | Proof |
| --- | --- | --- |
| N1 | Staging JPEGs for three held mãs are still public Blob objects. They are not catalog products and the shop returns 404. | HEAD 200 `image/jpeg`: `sassy-closet-shop/products/S14/cover.jpg` (322400), `…/A24/cover.jpg` (244936), `…/A25/cover.jpg` (335021), `…/A25/photo-2.jpg` (169257). Left in place. Deleting them would be a Blob write, and the catalog already keeps them off the shop. |
| N2 | Two source links differ. Prices match. | A15: Blob `sourceLink` null; hub has an `e.tb.cn` link. D05: same item id `1039727293632`; Blob host `item.taobao.com`, hub host `detail.tmall.com`. Health `sourceLinks` 61 (A15 is the missing one). |
| N3 | Intake submission `sell_usd` is the GF save-time field. It is not the live price mirror. Hub Official matches Blob, so nothing was written back. | Of 60 live mãs that have a submission: 4 already equal Blob (P01 $5, H01 $8, A05 $25, A06 $23), 13 still hold an older number (table below), 43 are blank including S06. D05 and V03 are live on Blob and hub and have no submission row. |
| N4 | Pricing formula was not applied. No mass reprice. | Formula stays a consistency note only. Cost columns on the hub mix CNY amounts labeled USD. |

Older intake `sell_usd` vs live Blob (hub matches Blob on every row):

| mã | field | intake save | blob / hub | intake | result |
| --- | --- | --- | --- | --- | --- |
| A01 | sell_usd | 25 | 27 | old save-time number | NOTE |
| S01 | sell_usd | 28 | 39 | old save-time number | NOTE |
| P05 | sell_usd | 23 | 25 | old save-time number | NOTE |
| P03 | sell_usd | 18 | 11 | old save-time number | NOTE |
| P04 | sell_usd | 13 | 10 | old save-time number | NOTE |
| K01 | sell_usd | 37 | 36 | old save-time number | NOTE |
| A02 | sell_usd | 22 | 23 | old save-time number | NOTE |
| A03 | sell_usd | 19 | 22 | old save-time number | NOTE |
| B01 | sell_usd | 41 | 46 | old save-time number | NOTE |
| B02 | sell_usd | 30 | 31 | old save-time number | NOTE |
| J01 | sell_usd | 30 | 29 | old save-time number | NOTE |
| J02 | sell_usd | 35 | 40 | old save-time number | NOTE |
| A04 | sell_usd | 20 | 21 | old save-time number | NOTE |

## Sell site

**PASS.**

| Check | Result | Proof |
| --- | --- | --- |
| Home | PASS | `https://sassycloset.vercel.app/` 200 · 532447 bytes · sha256 `b983ee5f6bcf31a512a0b12e6e4c92711a3cf76ea71f43326bbf048a22abdcb2` · 62 looks · Popular chip · prices match Blob |
| Alias | PASS | `https://sassy-closet-shop.vercel.app/` same 532447 bytes and same sha256 |
| Search | PASS | `/?q=S06` only card is S06 at $25. `/?q=ZZZNOPE` shows `Không thấy “ZZZNOPE” · No results for “ZZZNOPE”.` and zero `/m/` cards |
| PDP sample and full set | PASS | Sample includes S06 ($25), newest live S-series S13 ($26), S12 ($33), S11 ($51), S10 ($37), A23 ($27), A01 ($27), B01 ($46), D05 ($26), V03 ($21), H01 ($8), P01 ($5). Then all 62 PDPs. Held S14, A24, A25, S15, A26, K02 are 404 |
| Messenger | PASS | S06 HTML contains `https://m.me/61594312648057` and a Message S06 control. No message was sent |
| Stock copy | PASS | Home HTML has no “In stock”, “Only 1”, “left in stock”, “Add to cart”, “Buy now”, or “Sold out” |
| Images | PASS | 146 catalog image URLs returned 200 with an image body. B01 `photo-5.jpg` is 404 (9 bytes). Live B01 set is cover, photo-2, photo-3, photo-4 |
| B01 blocklist | PASS | Blocked asset is the plain-white Miss Gail tote (former photo). Live photo-4 sha256 `32f29819a2742a6b85c3ffbbd0e3dc3fd3454f36a4128c502e770ddd2e0e71b2` (same file as the 2026-09-30 QC blue denim shot). Cover / photo-2 / photo-3 are pink styled shots with “MISS GAIL” printed on the bag. Visual pass: no plain-white studio tote |
| Health | PASS | `GET /api/health` `ok: true`, reading `blob`, schema `catalog.v1` |
| Layout | PASS | Visual pass: home first screen, S06 at $25 with Message S06, S14 and K02 custom not-found, B01 gallery, and a 400px S06 view where the $25 price stays above the message bar |
| Routes that redirect home | PASS | `/how-to-buy` and `/meetup-ship` 307 to `/` from the page modules. Expected |
| Intake shell | PASS | `https://sassy-closet.vercel.app/` title Sassy Closet, tabs Món mới · Sửa theo mã · Tìm mã · Hỏi Mini Boss, Shop tools link. `/admin/shop` 307 to `/admin/shop/login`. No login was attempted |

No shop code change. Catalog meaning was left as published.

## Mini Boss handoff

Paste:

```
Midnight QC 2026-10-01 — DATA OK PASS (0 FAIL). Sell site PASS. Meta light SKIPPED.

Blob catalog.v1 62 live, updatedAt 2026-09-30T15:56:17.273Z, sha256 5a61d106e697a781c3c829f2c1d9c11aeec41670b13627cfc1a72c3f99fa4ed3.
Hub Official 62 live, file 2026-09-30T15:58:28Z, sha256 141ab5e530ac8c7fdf68cc66b0e540e9eb1b288dd2be2f65622e111aa0a16af1.
Blob ↔ hub USD mismatches: none. S06 = $25 on Blob, hub, and PDP (prior-night $22 is gone).
Held absent from Blob, hub, home, and PDP (404): S14, A24, A25, S15, A26, K02.
WARN: LISTING_STATUS_URL still unset — intake Live/Held badges off. Do not publish those mãs.
NOTE: public staging JPEGs remain for S14, A24, A25 (not in the catalog).
Luxubu: Meta mã+Giá was not re-read (FB shell / IG login wall). Prior-night Giá drift stays Luxubu’s, non-binding here. No CLEAR.
Boss ping: no.
```
