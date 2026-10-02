# Shop tools on intake

The customer shop (`sassy-closet-shop`, https://sassycloset.vercel.app and https://sassy-closet-shop.vercel.app) has no `/admin` page and no Shop tools button. Catalog edits live here, on the intake app, at `/admin/shop`.

Nhung’s intake tabs stay **Món mới**, **Sửa theo mã**, **Tìm mã**, **Hỏi Mini Boss**. Shop tools is a separate password page at `/admin/shop`, linked from the CSV export page, not from the intake form. `/admin` CSV export stays open.

The intake saved list and this desk read the shop catalog to label **Live** (status `available`) and **Held · chưa xong** (status `hold`, or an intake mã that is not in the catalog). The never-publish set `HELD_INCOMPLETE_MAS` (S14, A24, A25, S15, A26, K02, K03, K04, K05, V04) is never Live, including when a catalog row says available. That read does not write prices, photos, or mãs.

## Password

Sign-in checks `ADMIN_PASSWORD` on the server. A matching password sets cookie `sc_admin`: HttpOnly, Secure, SameSite=Lax, path `/`, 30 days, no Domain. The cookie value is a MAC, not the password. The MAC key is `HMAC-SHA256(ADMIN_SESSION_SECRET, ADMIN_PASSWORD)`. If either variable is missing, shop tools stay locked. There is no default password.

Five failures from the same IP in 10 minutes return 429. A wrong password waits briefly.

## Catalog

Reads and writes Vercel Blob pathname `sassy-closet-shop/catalog.v1.json` with `SHOP_BLOB_READ_WRITE_TOKEN` passed as the Blob SDK `token`. That token is the **shop** store’s read-write token. The intake store’s `BLOB_READ_WRITE_TOKEN` / `BLOB_STORE_ID` are not used for this file.

The desk lists products already in that file. It can edit titles, descriptions, existing color names, status, and USD price. It does not mint mãs, add colors, or change sizes or photos. Available USD is the catalog `priceUsd` in Blob. Hold still saves with no USD. The shop publishes that stored price on read.

After a successful write, intake POSTs the shop revalidate URL with header `x-shop-revalidate-secret`.

Incomplete Taobao mãs stay unfinished. They remain dataset and admin only, and they stay off the sell catalog: S14, A24, A25, S15, A26, K02, K03, K04, K05, V04. The same set is `HELD_INCOMPLETE_MAS` in `lib/held-incomplete.ts`. Shop tools does not add them to Blob.

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
