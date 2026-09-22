# 04 — Next + Blob catalog architecture (APPLY on sell-test)

Learn note from Official [PR #24](https://github.com/SkyLanter/Sassy-closet/pull/24). Applied on this Origin shop only. **Do not write Excel, OneDrive, or intake `store.json`.**

## Surfaces (never mix)

| Surface | Blob key | Mã |
| --- | --- | --- |
| This shop | `{SITE_ID}/catalog.v1.json` | Hub ten + Boss-added extras |
| Intake GF | `store.json` | Intake-local mint — not this catalog |
| Official clone | its own `SITE_ID` | Same schema, different project |

## catalog.v1

Envelope: `schema`, `version`, `siteId`, `products`, `settings`, optional `updatedAt`. Handoff export also writes `allowlist` (the ten). Kit files may send `source` / `exportedAt` / word types (`top`, `thermos`) — parse accepts them; shop storage stays letter types (`A`, `P`).

Hub ten: A01 $25 · S01 $28 · P01 $5 · P02 Hold · P03 $18 · P04 $13 · P05 Hold · K01 $37 · H01 $8 · A02 $22.

P02/P05 stay `priceUsd` null. Pretty import does not publish $23.

Boss Add (A03+) is a separate path. Kit replace **keeps** live extras.

## Import / export

- Admin settings: Export / Import catalog.v1 (replace or merge)
- `GET /api/admin/catalog/export`
- `POST /api/admin/catalog/import` (body = catalog.v1, or `{ catalog, mode }`)
- Empty kit titles keep shop copy
- OneDrive `Documents/Sassy Closet/Photos/…` paths are dropped (shop `src` stays `/products/{MA}/cover.jpg` or a Blob URL)
- No public `GET /api/catalog`

## Cache after Save

Blob `put` uses `cacheControlMaxAge: 0`. Reads use `get({ useCache: false })`. Save stamps `updatedAt`, then `revalidatePath` (`/`, `/m/[ma]` page, `/c/[slug]` page) and **two** public warms. Shop + admin HTML send `private, no-store`.

## Not applied

Writing the hub xlsx, sharing intake Blob, minting A03 from kit JSON, Square Save, Facebook Send.
