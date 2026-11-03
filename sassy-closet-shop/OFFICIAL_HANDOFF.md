# Official catalog handoff

Admin Save and the customer shop share **one** live catalog. Seed `data/products.json` is bootstrap only. Official must import the live document, not re-type seed.

Schema: **catalog.v1** (`schema`, `version: 1`, `siteId`, `products`, `settings`).

## Export from the test shop

1. Open `/admin/settings` on the test shop.
2. Click **Export catalog.v1**.
3. You get `{SITE_ID}-catalog.v1.json` (example: `sassy-closet-shop-catalog.v1.json`).
4. Keep that file offline. It is the source of truth for mãs, titles, Hold/Available/Sold, colors, photo URLs, announcement, and Messenger URL.

Export does not invent mãs or Taobao links. It dumps whatever is live (the 10 known mãs plus any mãs you added in admin), including `fulfillment` and `sourceLink` when present.

## Import on official

1. Official project env: `SITE_ID=sassy-closet-official`, `NEXT_PUBLIC_SITE_MODE=official`, `BLOB_READ_WRITE_TOKEN` set. See [CLONE_TO_OFFICIAL.md](./CLONE_TO_OFFICIAL.md).
2. Deploy official. First load may show seed until import.
3. `/admin/settings` → pick **Replace** (first official load) or **Merge** (later overlays) → **Import catalog.v1** → choose the export file → confirm.
4. Import **stamps** `siteId` to the official `SITE_ID` so the file belongs to that store. Merge overlays matching mãs and keeps extras on either side.
5. Shop home and PDPs must match the export: same mãs, same Hold (no fake USD), same color names and photos.

## Blob copy (optional, instead of JSON import)

If both projects can reach the same Blob account:

1. Copy `{test SITE_ID}/catalog.v1.json` to `{official SITE_ID}/catalog.v1.json`.
2. Copy `{test SITE_ID}/products/**` to `{official SITE_ID}/products/**` if photos are Blob URLs under the test prefix.
3. Set official `SITE_ID` and redeploy.
4. Prefer JSON Export/Import when photo URLs are already public `https://` links — no copy needed.

Do **not** write test junk to `{official SITE_ID}/catalog.v1.json`. The persist probe path is `{SITE_ID}/persist-probe.json` only.

## Checks after handoff

- Add on official → appears on official shop (not the test shop).
- Edit / rename mã → old PDP gone, new PDP live.
- Hold → Inbox for price, no buyable USD lie.
- Sold → hidden from the shop, still in admin.
- No personal names on the public UI. Messenger URL is the Page only.

## Locked mãs

Known seed mãs (do not invent extras in seed): A01, S01, P01, P02, P03, P04, P05, K01, H01, A02.

Boss prices: A01 $25, S01 $28, P01 $5, P02 Hold, P03 $18, P04 $13, P05 Hold, K01 $37, H01 $8, A02 $22.
