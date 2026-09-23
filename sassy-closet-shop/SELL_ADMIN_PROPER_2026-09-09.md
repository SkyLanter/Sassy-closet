# Sassy Closet — proper sell-ops admin

Date: 2026-09-09. Live shop: https://sassy-closet-shop.vercel.app. Intake (https://sassy-closet.vercel.app) is a different project — never deploy over it.

This is a **one-of-one closet**, not a multi-SKU fashion OS. Steal boutique-admin habits; drop cart, inventory counts, and checkout.

## What a good boutique admin does (adapted)

| Fashion ops habit | Here |
| --- | --- |
| Product list with thumb + SKU + status + price | Catalog: thumb · mã (sans/tabular) · title · status · price/Hold · colors · images · Edit |
| Click a row to open a deep editor | `/admin/edit/[ma]` |
| Variants = colorways with their own photos | Admin: swatch **boxes** + name + photos per color |
| Customer sees the colorway name, not a hex toy | Shop: **text-only** color labels → gallery slides for that color |
| Status is merchandising, not POS | Hold (inbox for price) · Available · Sold/Gone (hidden) |
| Preview the PDP before a livestream | Preview PDP |
| One catalog, not a CMS draft vs a storefront copy | Admin Save writes the live catalog; shop reads the same document |
| SKU uniqueness | Change mã with uniqueness + allowed letters only |

Do **not** add: cart, Square checkout, passwords on `/admin`, invented mãs, personal names, invented ship $, invented Taobao links. Dropship is the default fulfillment. Square / on-hand only after Boss received the piece.

## Routes

- `/admin` — catalog (search, type letter, status)
- `/admin/new` — add (next unused mã, default **Hold**)
- `/admin/edit/[ma]` — identity, status/price, colors+photos, copy, change mã
- `/admin/settings` — announcement + Messenger URL

## Catalog document (`catalog.v1`)

`{ version: 1, products[], settings }`. Product: `ma`, bilingual titles/descriptions, `qty: 1`, `status`, `colors[{id,hex,name,note}]`, `images[{src,colorId}]`. Writes round-trip through Blob (preferred), else KV, else local `data/live-catalog.json`.

Allowed letters: A/Q/V/K/G/B/P/H/J/S/O/D. Next áo after A01+A02 is **A03**. Qty is always 1.

## Shop chrome (do not restyle)

Kelly Ying boutique look stays: category-first grid, English chrome, mã sans/tabular, Message-first CTAs, category-switch motion, color→gallery slide. Admin may be plain.

## Must-work

1. Add item every time (clear errors; Hold default; appears on shop)
2. Edit titles/desc/price/status/images; change mã with uniqueness
3. Admin color boxes + per-color photos; shop text-only → gallery
4. Save immediately matches the customer shop (same live catalog, no stale seed)
