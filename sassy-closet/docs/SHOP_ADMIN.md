# Shop tools on intake

The customer shop (`sassy-closet-shop`, https://sassycloset.vercel.app and https://sassy-closet-shop.vercel.app) has no `/admin` page and no Shop tools button. Catalog edits live here, on the intake app, at `/admin/shop`.

Nhung’s intake tabs stay **Món mới**, **Sửa theo mã**, **Tìm mã**, **Hỏi Mini Boss**. Shop tools is the link `/admin/shop`. There is no password and no session. `/admin` CSV export stays open.

## Password

Shop tools, `/api/shop-catalog`, `/api/submissions`, `/api/export`, and `/api/ma/*` do not check `ADMIN_PASSWORD`. Anyone with the link can open and edit. Responses stay `noindex`. `ADMIN_PASSWORD` and `ADMIN_SESSION_SECRET` are not a login wall.

## Catalog

Reads and writes Vercel Blob pathname `sassy-closet-shop/catalog.v1.json` with `SHOP_BLOB_READ_WRITE_TOKEN` passed as the Blob SDK `token`. That token is the **shop** store’s read-write token. The intake store’s `BLOB_READ_WRITE_TOKEN` / `BLOB_STORE_ID` are not used for this file.

The desk lists products already in that file. It can edit titles, descriptions, existing color names, status, and USD price. It does not mint mãs, add colors, or change sizes or photos. Available USD is the catalog `priceUsd` in Blob. Hold still saves with no USD. The shop publishes that stored price on read.

After a successful write, intake POSTs the shop revalidate URL with header `x-shop-revalidate-secret`.

Incomplete Taobao mãs stay unfinished. They remain dataset and admin only, and they stay off the sell catalog: S14, A24, A25, S15, A26, K02, K03, K04, K05, V04, K06, V05, S16, S17, S18, S19, A27, A28, A29, H02, G01. That set is `HELD_INCOMPLETE_MAS`, loaded from `data/held.json`. Shop tools does not add them to Blob.

Local only: if the shop token is unset and `VERCEL` is not `1`, `SHOP_CATALOG_FILE` can point at a JSON file. Production ignores that name.

## Env names Boss adds before merge

Intake project **sassy-closet** (https://sassy-closet.vercel.app):

- `ADMIN_PASSWORD`
- `ADMIN_SESSION_SECRET`
- `SHOP_BLOB_READ_WRITE_TOKEN` (value is the shop Blob store’s `BLOB_READ_WRITE_TOKEN`; do not reuse the intake store token)
- `SHOP_REVALIDATE_SECRET`
- `SHOP_REVALIDATE_URL` (`https://sassycloset.vercel.app/api/admin/revalidate` or `https://sassy-closet-shop.vercel.app/api/admin/revalidate` — same deployment)

Shop project **sassy-closet-shop**:

- `SHOP_REVALIDATE_SECRET` (same value as on intake)

Do not put the values in git. Redeploy each project after saving the variables. This repo does not change Vercel env or production Blob.
