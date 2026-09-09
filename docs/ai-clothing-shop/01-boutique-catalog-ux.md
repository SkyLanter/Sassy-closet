# Boutique catalog UX

A 10-piece unique-item closet is not a 2,000-SKU fashion site. Steal **grid discipline** from big stores; keep **one card = one mã**.

## What good catalogs do (sourced)

**Visual-first cards.** Fashion PLPs win when the photo is the card and text is secondary. Desktop 3–4 columns for comparison; mobile **2** columns as the default (1 column only when each piece needs a long caption). Source: [Suplex PLP 2026](https://suplex.design/blog/product-listing-page-best-practices).

**Filters with live counts.** Put primary filters at the top; show how many pieces sit in each bucket; update counts when the chip changes. Source: [Depict — 10 product grid practices](https://depict.ai/resources/blog/10-best-practices-for-fashion-store-product-grid-design). Sell-test already does this: All 10 / Tops 2 / Sets 1 / Accessories 5 / Jackets 1 / Hair 1.

**Tap targets ≥ 44×44.** Filter chips, Message CTA, swatches. Source: Depict + [Craftshift swatches](https://craftshift.com/shopify-product-grid-color-swatches-ux/).

**Status before price.** Unique pieces go **Available / Hold / Sold** on the card, not a fake “In stock (12)”. Art studios treat each work as one record with availability — [Art.industries](https://art.industries/), [makers inventory](https://art.industries/makers). Sell-test: Available vs **Hold · Inbox for price**.

**No cart theater.** A boutique that closes on Messenger should say so on the card (“Message to buy. No cart.”) instead of a disabled Add-to-cart. That is sell-test A01 copy today.

## Map onto sell-test (keep)

| Pattern | Already on shop | Do not “improve” into |
| --- | --- | --- |
| Featured collection + category rails | `/` + `/c/{slug}` | Shopify mega-menu, search-with-empty-index |
| mã as the hero SKU | `A01` tabular, uppercase | Pretty titles that hide the mã |
| Cover per mã | `/products/{MA}/cover.jpg` | Stock-photo placeholders |
| Editorial tiles | `/editorial/*.jpg` | Generic AI lifestyle dump |
| Hold without a dollar | P02 / P05 | `$0` or `$TBD` |
| Kelly Ying chrome | paper/ink/gold + Cormorant + motion | Intake rose / Allura |

## Apply rules (shop feature branch only)

1. **One unique piece = one mã = one PDP** (`/m/A01`). Do not explode A01 into size variants that mint A01-S / A01-M.
2. Grid card order: **photo → status → mã → kind → price or Inbox → Message**.
3. Keep filter counts honest. If a mã is removed from Blob, the chip count must drop. Lying counts are seed drift (see [07-failure-modes.md](07-failure-modes.md)).
4. Related rail = **same category, other allowlist mãs only**. A01 may show A02. Never recommend A03.
5. Fancy motion stays: announce bar, shimmer on media load, CTA shine, header view-transition. Honor `prefers-reduced-motion` (CSS already zeroes those keyframes).
6. `noindex` stays until Boss says the shop is public.

## Anti-patterns AI shops add

- Infinite scroll on 10 items (Depict: pick scroll model from **catalog size**).
- “Bestselling” sort with no sales data.
- Color names on swatches when Boss asked for **boxes only**.
- US size charts. Kit law: Asia size + cm, in the **inbox**, not a fake matrix on the PDP.
