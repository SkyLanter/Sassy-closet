# AI clothing-shop playbook (kit lane)

How AI-built clothing shops are actually assembled — sourced patterns, mapped onto **Sassy Closet sell-test**, without fighting Origin shop main and without touching intake.

| Lane | What it is | This playbook |
| --- | --- | --- |
| **Kit** | This repo: [SkyLanter/Sassy-closet](https://github.com/SkyLanter/Sassy-closet). Excel SoT + intake at `sassy-closet.vercel.app`. | Home. Docs + apply list + export validator. |
| **Sell-test** | [sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app) | Observe + write apply notes. Do not invent mã. |
| **Origin shop** | Separate sell-site app / `main`. | **Do not fight Origin shop main.** Apply on sell-test / a shop feature branch only. |
| **Intake** | `sassy-closet/` in this repo (Món mới · Sửa · Tìm mã · Ask). | **Untouched.** Different chrome (Allura / Nunito / rose). |

## Hard stops

- **Never invent mã.** Only `A01 S01 P01 P02 P03 P04 P05 K01 H01 A02`.
- **Intake untouched.**
- **No Square Save.**
- **No Facebook Send / Post.** Facebook inbox is the store; the site only *opens* a message.
- **No passwords** in code, git, admin, or prompts.

## Read in this order

1. [08-sell-test-observed.md](08-sell-test-observed.md) — what the live shop actually is (2026-09-09).
2. [01-boutique-catalog-ux.md](01-boutique-catalog-ux.md)
3. [02-message-first-social-commerce.md](02-message-first-social-commerce.md)
4. [03-tiny-admin-ops.md](03-tiny-admin-ops.md)
5. [04-per-color-product-media.md](04-per-color-product-media.md)
6. [05-nextjs-blob-catalog.md](05-nextjs-blob-catalog.md)
7. [06-clone-to-official.md](06-clone-to-official.md) — merge with catalog-export work; do not abandon.
8. [07-failure-modes.md](07-failure-modes.md) — silent save, seed drift, mã collision.
9. [MERGE.md](MERGE.md) — sibling agent + file ownership.
10. [SOURCES.md](SOURCES.md) — every URL.

**Apply list (Boss / Mini Boss paste):** [`excel-kit/prompts/AI_CLOTHING_SHOP_APPLY_TO_SELL_TEST.md`](../../excel-kit/prompts/AI_CLOTHING_SHOP_APPLY_TO_SELL_TEST.md)

**Allowlist + export gate:** `excel-kit/sell_test_allowlist.py` and `excel-kit/sot/validate_sell_catalog_export.py`.

## What “Kelly Ying design + fancy motion” means here

Boss name for the **sell-test** visual system (not intake). Live CSS tokens, 2026-09-09:

| Token | Value |
| --- | --- |
| Paper / ink | `--paper:#fff` · `--ink:#111` |
| Blush / gold | `--blush:#f3eee8` · `--gold:#b08968` · `--gold-deep:#8c6a4e` |
| Line / muted | `--line:#ececec` · `--muted:#6b6b6b` |
| Body | Be Vietnam Pro (`font-sans`) |
| Display | Cormorant Garamond (`font-display`) |
| Motion | `announce-fade` 4.2s · `shimmer-slide` 1.3s · `cta-flash` 0.7s hover · view-transition on `site-header` · `--duration-enter:.21s` `--duration-exit:.15s` `--duration-move:.4s` |

Preserve that system. Do not restyle the shop to match intake rose / Allura.

## Admin ↔ shop link (keep)

- Shop is the public catalog (`/`, `/c/…`, `/m/{mã}`).
- Admin is `/admin` — labeled **Test only · not in the main nav**.
- Admin already has **Back to shop** / **Open sell-test editor**.
- Keep that two-way link. Do not add a password wall. Do not hide admin so editors cannot return to the grid.

## Catalog export / CLONE_TO_OFFICIAL

Sibling branch `cursor/catalog-export-clone-official-5ad2` already has `excel-kit/docs/CLONE_TO_OFFICIAL.md` + `catalog.v1` export scripts. This playbook **does not replace them**. It adds sourced shop-building notes + a sell-test apply list + a second allowlist gate that accepts catalog.v1.

See [MERGE.md](MERGE.md) and [06-clone-to-official.md](06-clone-to-official.md).
