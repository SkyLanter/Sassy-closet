# Tiny-boutique admin reliability (APPLY)

Learn note from Official PR #20, applied on this sell-test only. **Do not redesign** Kelly Ying chrome.

SKU = mã. Hub ten stay. Add assigns the next unused mã (A03+). Official alphabet (`AO001`) is rejected. Sell-facing tiles are **hold | available**. Sold / Gone retires the identity in admin and hides the tile. `qty: 1` is not a warehouse count. Dropship · Message-first.

## Silent save

- Success toast / banner only after a complete receipt: `ok`, `blobWritten`, `catalogSha`, `revalidated`.
- Read-back must match the saved facts (title, status, price) for every row in the write.
- Add / Edit / rename / Remove / Hold / settings / import wrap the action and show the error if the action throws or returns nothing.
- A **present but corrupt** live catalog (Blob / KV / local file) throws. It does **not** fall back to seed and pretend the Save landed.

## Seed drift

- Writes require the ten hub mãs. Missing A01 (etc.) is a hard fail — do not invent a replacement.
- Import keeps extras (A03+) and rejects holes / Official alphabet. P05 never $23.
- Admin Catalog banners leftover extras / missing hub mãs / duplicate mãs.
- Add Saves the next unused mã (A01+A02 → A03) to Blob / local live catalog. Receipt or error — never silent.

## Duplicate mã

- Normalize before compare (`a01` = `A01`).
- Rename onto an existing code: visible error, **không gộp**.
- Official alphabet (`AO001`) cannot parse onto this shop.
- Allowlist rows cannot be Removed. Mark Sold / Gone. Leftover extras (A04) can still be Removed.

## Not applied

Shopify IMS, Square Save, intake Lưu, Official Excel append, sharing the intake Blob, recycling a Sold mã as a new garment.
