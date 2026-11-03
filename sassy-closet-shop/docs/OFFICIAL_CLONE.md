# Official clone (one-shot)

This folder (`sassy-closet-shop/` in GitHub `SkyLanter/Sassy-closet`) is the **sell-test shop**. Copy it into a **new** official website. Do not deploy over GF intake. Origin temp `tiensidequests/tmp-87ea3acf7683fefe` is deprecated for new commits.

| Site | URL | Blob / `SITE_ID` | Indexing |
| --- | --- | --- | --- |
| **Intake (READ ONLY)** | https://sassy-closet.vercel.app | intake project — never write from this repo | n/a |
| **This TEST shop** | https://sassy-closet-shop.vercel.app | `sassy-closet-shop` | `NEXT_PUBLIC_SITE_MODE=test` → HTML **noindex** |
| **Official (new)** | your domain | `sassy-closet-official` (new Blob prefix) | `NEXT_PUBLIC_SITE_MODE=official` → index |

Same git. New Vercel project. New Blob prefix (or new Blob store). Do not reuse the test domain unless you intend to replace the test site.

## 1. Clone GitHub

1. Clone [SkyLanter/Sassy-closet](https://github.com/SkyLanter/Sassy-closet) and use folder `sassy-closet-shop/`, not the intake app (`sassy-closet/`).
2. Keep branch `main` as the template.
3. Do not copy `data/live-catalog.json` from a laptop into git (it is gitignored). Export JSON from admin instead.

## 2. New Vercel project

1. Import this git repo as a **new** Vercel project (suggested name: `sassy-closet-official`).
2. Framework: Next.js. **Root Directory:** `sassy-closet-shop`.
3. Do **not** attach `sassy-closet.vercel.app` (intake).
4. Do **not** attach `sassy-closet-shop.vercel.app` unless you are replacing TEST.

## 3. Environment (Production + Preview)

Copy names from [`.env.example`](../.env.example). Set real values in Vercel — never commit secrets.

| Name | Official | Test (this deploy) |
| --- | --- | --- |
| `SITE_ID` | `sassy-closet-official` | `sassy-closet-shop` |
| `NEXT_PUBLIC_SITE_ID` | same as `SITE_ID` | `sassy-closet-shop` |
| `NEXT_PUBLIC_SITE_MODE` | `official` | `test` |
| `NEXT_PUBLIC_SHOP_URL` | `https://YOUR-OFFICIAL-DOMAIN` (no trailing slash) | test URL or empty locally |
| `NEXT_PUBLIC_MESSENGER_URL` | Public Facebook Page URL | same Page is fine |
| `BLOB_READ_WRITE_TOKEN` | Token for a **new** Blob store (preferred) | existing test store |

Optional KV (`KV_REST_API_URL` + `KV_REST_API_TOKEN`) only if Blob is unset. Blob wins when both are set.

There is **no** `ADMIN_PASSWORD`. `/admin` is open for sell-ops. Do not add Square checkout, Facebook Send, or personal Zelle names on the public UI.

## 4. Blob prefix

Writes:

- Catalog: `{SITE_ID}/catalog.v1.json`
- Images: `{SITE_ID}/products/{mã}/…`

Test and official may share one Blob **account** only if `SITE_ID` differs. Prefer a dedicated official store.

This shop still **reads** legacy `{SITE_ID}/catalog.json` if `catalog.v1.json` is missing. Writes always use `catalog.v1.json`.

## 5. Catalog import

Admin Save and the customer shop share **one** live catalog. Seed `data/products.json` is bootstrap only.

1. On TEST: `/admin/settings` → **Export catalog.v1**  
   or `npm run catalog:backup` locally (writes `data/backups/`, gitignored).
   Export is validated as **catalog.v1 JSON** (not HTML, not a kit xlsx path) before download.
2. Deploy official with env above (first load may show seed).
3. Official `/admin/settings` → **Replace** (first load) or **Merge** (later) → **Import catalog.v1**.
   Import rejects non-catalog files in the browser, then stamps `siteId` to the official `SITE_ID`. Hub ten must stay. Extra mãs (A03+) copy as data — A03 Kit stub is **data**, not a code path. Do not overwrite A03 with GF intake until Boss says yes.
4. Import receipt must include shop `/` and `/m/A01` after Blob write + revalidate.
5. Open official `/` and `/m/A01`. Confirm photos, prices, Inbox-for-price looks (P02/P05), plain Messenger.

HTTP: `GET /api/admin/catalog/export` · `POST /api/admin/catalog/import`. Never intake `/api/export`. Excel / OneDrive / https://sassy-closet.vercel.app stay read-only.

## 6. Go-live checklist

- [ ] `NEXT_PUBLIC_SITE_MODE=official` (flips HTML index; test stays noindex)
- [ ] `NEXT_PUBLIC_SHOP_URL` is the public origin (canonical + OG)
- [ ] `NEXT_PUBLIC_MESSENGER_URL` is the Page (plain `m.me/{id}`, no `?text=`)
- [ ] Blob token set; Add/Save shows a receipt (`ok`, `blobWritten`, `catalogSha`, `revalidated`)
- [ ] Export → import round-trip: hub ten present, P02/P05 no fake $23
- [ ] Customer UI: name / price / description / colors / Message only — no Hold / Available / on-hand
- [ ] `/admin` not in the main nav (logo long-press / gold dot)
- [ ] Intake site untouched
- [ ] No Square Save, no Facebook Send, no invented mãs

## 7. What stays Boss-only (do not invent on clone)

- Overwriting **A03** Kit stub with GF intake photos/copy
- Flat ship `$` and meetup spots
- New mãs beyond Add’s next unused letter
- Indexing the **test** URL

Sister notes: [OFFICIAL_HANDOFF.md](../OFFICIAL_HANDOFF.md) (export/import detail), [CLONE_TO_OFFICIAL.md](../CLONE_TO_OFFICIAL.md) (short pointer).
