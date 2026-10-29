# Live audit — 2026-10-29

Unauthenticated read-only probe of the live intake and shop. No Blob writes, no Meta edits, no deploy, no merge. Supplier URLs and cost amounts were not saved. Evidence is status codes, redacted headers, field names, counts, and public sell prices.

Probe window: 2026-10-29 06:32–06:40 UTC.

| Host | Role |
| --- | --- |
| https://sassy-closet.vercel.app | Intake |
| https://sassy-closet-shop.vercel.app | Shop |
| https://sassycloset.vercel.app | Shop (same catalog identity as the host above) |

## Executive

**FAIL.** Blob recovery and the Sep 20 catalog check passed. Privacy failed: intake serves costs and supplier links with no session, and the public shop Blob catalog JSON includes `sourceLink`.

| Check | Result | Evidence |
| --- | --- | --- |
| Intake store recovered from Blob | PASS | `GET /api/submissions` 200, `storage.mode=durable`, `storage.durable=true`, 83 mãs, S06 present |
| `GET /api/submissions/S06` | PASS | 200, `ma=S06` |
| `GET /api/fx` | PASS | 200, `usd_cny=6.71`, `updated=2026-09-07` (same values as the code default in `emptyStore()`) |
| `GET /api/ma/S06` | PASS | 200, `staged.ma=S06`, `staged.status=staged`, `staged_only=true` |
| Shop health reads Blob | PASS | Both shops: 200, `reading=blob`, `backend=blob`, `productCount=62`, `ok=true`, `catalogUpdatedAt=2026-09-30T15:56:17.273Z` |
| `/m/S06` is $25 | PASS | Both shops: 200. Catalog `priceUsd=25`, `status=available`. Page JSON-LD price `25.00` once |
| `/m/K03` held 404 | PASS | Both shops: 404, title `Not found · Sassy Closet`. K03 is absent from the 62-mã catalog. K03 is on the held list and still in intake |
| `/m/A01` | PASS | Both shops: 200, title `A01 · Puppy cardigan · Sassy Closet` |
| Public catalog is the Sep 20 seed | PASS (it is a later catalog) | Sep 20 seed has 40 mãs. Live Blob catalog has 62 mãs, `updatedAt=2026-09-30T15:56:17.273Z`, `reading=blob` |
| Cost / supplier link exposure | FAIL | See leak map |

## Blob recovery

Headers below are the final response. `x-vercel-cache` was `MISS` on these API calls.

| Request | Status | Cache-Control | What came back |
| --- | --- | --- | --- |
| `GET /api/submissions` | 200 | `public, max-age=0, must-revalidate` | JSON. 83 submissions. Keys include `cost_cny` (79 nonempty), `cost_usd` (80 nonempty), `link` (83 nonempty, URL-shaped). `taobao_snapshot` present 25 times, nonempty 0 |
| `GET /api/submissions/S06` | 200 | `public, max-age=0, must-revalidate` | JSON. `cost_cny`, `cost_usd`, and `link` each nonempty |
| `GET /api/fx` | 200 | `public, max-age=0, must-revalidate` | JSON keys `usd_cny`, `updated`, `label`. No cost or source fields. Rate `6.71`, updated `2026-09-07` |
| `GET /api/ma/S06` | 200 | `public, max-age=0, must-revalidate` | JSON. `staged` includes nonempty `cost_cny`, `cost_usd`, and `source_link`. `on_hand` length 0 |
| `GET /api/health` on both shops | 200 | `no-store` | `reading=blob`, `blob.readable=true`, `blob.path=sassy-closet-shop/catalog.v1.json`, `blob.listed_count=70`, catalog file listed, `productCount=62`, `shopVisible=62`, `sourceLinks=61`, `schema=catalog.v1`, `siteId=sassy-closet-shop`, `mode=test`, `ok=true`, `missingKnown=0` |

S06 intake mãs observed: list contains S06. Shop catalog row: `status=available`, `priceUsd=25`, `sourceLink` key present and nonempty.

K03 is one of the 83 intake mãs. It is not one of the 62 shop mãs. Public `/m/K03` is 404 on both hosts. `data/held.json` lists K03 under `heldIncomplete`.

A01 is in intake and in the shop catalog (`status=available`, `priceUsd=27`).

The FX object matches the initial default in `sassy-closet/lib/store-backend.ts` (`usd_cny` 6.71, updated `2026-09-07`). The durable store is populated (83 submissions), so this is the rate stored in Blob. It does not show a later FX edit.

## Privacy leak map

Unauthenticated GET. A route is a leak when status is 200 and the body contains cost fields or a supplier-link field with values. Counts are nonempty values. URLs and amounts are omitted.

| Route | Status | Leak |
| --- | --- | --- |
| Intake `GET /api/export` | 200 | **FAIL.** `text/csv`, `content-disposition: attachment; filename=sassy-closet.csv`, `cache-control: public, max-age=0, must-revalidate`. 83 data rows. Columns include `cost_cny` (79), `cost_usd` (80), `source_link` (83). 83 cells are URL-shaped |
| Intake `GET /api/submissions` | 200 | **FAIL.** Every row has URL-shaped `link`. Cost fields populated on most rows. Response is cacheable at `max-age=0` and is public |
| Intake `GET /api/submissions/S06` | 200 | **FAIL.** Same cost and `link` fields for S06. The route is unauthenticated for any mã; S06 is the live sample |
| Intake `GET /api/ma/S06` | 200 | **FAIL.** `staged.source_link`, `staged.cost_cny`, `staged.cost_usd` nonempty |
| Public Blob `sassy-closet-shop/catalog.v1.json` | HEAD 200, GET 200 | **FAIL.** `content-type: application/json`, `content-disposition: inline; filename="catalog.v1.json"`, `cache-control: public, max-age=60`, `x-vercel-cache: HIT` on HEAD. 73,788 bytes. Top-level keys: `schema`, `version`, `siteId`, `updatedAt`, `settings`, `products`. Every product has a `sourceLink` key (62). 61 are nonempty. A15 is the empty one. No `cost_cny` / `cost_usd` / `source_link` keys. `https://…/sassy-closet-official/catalog.v1.json` and `https://…/catalog.v1.json` are 404 `Blob not found` |
| Shop `GET /api/health` (both hosts) | 200 | Count only. `sourceLinks` is the integer 61. The health body has no supplier URL and no cost amount. It does publish `blob.path`, `canWrite=true`, and the count |
| Shop `GET /`, `/m/S06`, `/m/A01`, `/m/K03` | 200 / 200 / 200 / 404 | No `sourceLink`, `source_link`, `cost_cny`, `cost_usd`, `taobao`, or `tb.cn` in the HTML on either host |
| Shop `GET /api/admin/catalog`, `/export`, `/import`, `/settings`, `/save`, `/hold`, `/add`, `/remove`, `/rename`, and `GET /admin` | 404 | Empty body. `cache-control: private, no-store`. `x-robots-tag: noindex, nofollow`. The proxy closes these before the handler |
| Shop `GET /api/admin/revalidate` | 405 | `Allow: POST`. Body `{ok:false}` and the error tells the caller to POST. No catalog |
| Intake `GET /api/shop-catalog` | 401 | `{ok:false, error:"Unauthorized."}` |
| Intake `GET /api/shop-catalog/login` | 405 | Sign-in is POST |
| Intake `GET /api/kinds` | 200 | No cost or source fields |
| Intake `GET /api/listing-status` | 200 | `{enabled:false, items:{}}`. No cost or source fields |
| Intake `GET /api/ask/audit-missing` | 404 | Missing id |
| Intake `GET /api/photos/not-a-real-file` | 404 | No photo bytes downloaded |
| Intake `GET /api/mini-boss`, `/api/taobao-lookup`, `/api/find-ma` | 405 | Empty body |
| Intake `GET /admin` | 200 | HTML shell. No cost fields, no `source_link`, no `tb.cn` |
| Intake `GET /` | 200 | HTML shell. One placeholder `https://e.tb.cn/...` in the link field. No stored supplier URL, no cost fields |

Customer shop HTML is clean. The supplier links are in the raw public catalog file and in the intake JSON/CSV APIs. Intake middleware only gates `/api/shop-catalog` and `/admin/shop`, which matches the live 401 on shop-catalog and the open submissions, export, and mã routes.

Submission rows also include `photo_paths` and `photo_link`. A fake photo path returned 404. Real photo bytes were not requested.

## Catalog versus the Sep 20 seed

Sep 20 baseline, counted locally from the repo (values only, no links printed):

| File | Stamp | Mãs |
| --- | --- | --- |
| `sassy-closet-shop/public/data/taobao_confirm_seed.json` | `updated_at_pt` `2026-09-20 08:32 AM PT`, `seed_kind=full` | 40 |
| `sassy-closet-shop/data/products.json` | `updatedAt` `2026-09-20T16:42:39.000Z`, `schema=catalog.v1` | 40, same mã set as the confirm seed. `sourceLink` key on 40, nonempty on 39 |

Live Blob catalog `sassy-closet-shop/catalog.v1.json`:

- `schema=catalog.v1`, `version=1`, `siteId=sassy-closet-shop`
- `updatedAt=2026-09-30T15:56:17.273Z`
- 62 mãs, no duplicate mãs, every `status` is `available`
- Health `reading=blob` on both shop hosts, so the shops are not falling back to the baked seed
- All 40 Sep 20 mãs are still in the live catalog
- 22 mãs are only in the live catalog: A16, A17, A18, A19, A20, A21, A22, A23, D04, D05, S05, S06, S07, S08, S09, S10, S11, S12, S13, V01, V02, V03

That is a later catalog. Health `knownMas` is the hub ten (A01, S01, P01, P02, P03, P04, P05, K01, H01, A02). `extras` is 52. `hubMessageReady` is 10. `dropship` is 62. `onHand` is 0.

Both shop hosts report `mode=test` and `siteId=sassy-closet-shop`. There is no public `sassy-closet-official/catalog.v1.json` (404).

Intake has 83 mãs. 62 of those are on the shop. 21 are intake-only:

- Held (`data/held.json`): S14, A24, A25, S15, A26, K02, K03, K04, K05, V04, K06, V05
- In intake and not on the held list or the shop catalog: A27, A28, A29, G01, H02, S16, S17, S18, S19

## Boss-only follow-ups

No production change was made.

1. Close unauthenticated reads of intake `GET /api/export`, `GET /api/submissions`, `GET /api/submissions/[ma]`, and `GET /api/ma/[code]`. Those four responses are the cost and supplier-link leak. Shop-catalog is already 401.
2. Stop publishing supplier URLs in the public Blob object `sassy-closet-shop/catalog.v1.json`. The file is `cache-control: public, max-age=60`. Customer HTML already omits `sourceLink`. The JSON file still has the key on all 62 rows and a nonempty value on 61 (A15 is empty).
3. Decide whether public `GET /api/health` should keep `sourceLinks` (61), `canWrite`, and `blob.path`.
4. Confirm the stored FX. Blob currently has the initial default, 6.71 dated 2026-09-07.
5. Decide the nine intake mãs that are neither held nor on the shop: A27, A28, A29, G01, H02, S16, S17, S18, S19.
6. `sassycloset.vercel.app` and `sassy-closet-shop.vercel.app` both serve the test site id `sassy-closet-shop`. Official catalog Blob path returned 404.
