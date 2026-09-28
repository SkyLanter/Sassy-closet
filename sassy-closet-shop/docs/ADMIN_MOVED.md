# Admin moved to intake

Customers do not get a shop desk.

- `GET /admin` and every `/admin/*` path return **404**. There is no Shop tools button and no logo long-press.
- `POST /api/admin/revalidate` stays. It requires header `x-shop-revalidate-secret` equal to `SHOP_REVALIDATE_SECRET`. Missing, wrong, or unset secret is **401**. `GET` is **405**.
- Every other `/api/admin/*` route returns **404**.

Catalog edits are on the intake app (`/admin/shop`), which writes Blob `sassy-closet-shop/catalog.v1.json` and then calls this revalidate endpoint. See `sassy-closet/docs/SHOP_ADMIN.md`.

`presentLockedBossPrices` / `BOSS_PRICE_LIST` are unchanged. The shop still shows those USD prices on read.
