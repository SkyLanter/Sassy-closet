# Catalog UX (apparel lists)

## What strong shops do

Baymard’s 2025 product-list research treats the **collection grid as a decision tool**, not a poster wall ([Product List UX Best Practices 2025](https://baymard.com/blog/current-state-product-list-and-filtering)):

1. **One card per piece, colors as options on that card** — 42% of sites still split the same garment into many list rows. Shoppers compare worse. Combined listings / colorways exist so the grid stays one identity per SKU ([Shopify Combined Listings](https://help.shopify.com/en/manual/products/combined-listings-app)).
2. **Show how many items the list contains** — filter UIs that print counts (“Blue (34)”) set expectations before a click ([Baymard filter UI](https://baymard.com/learn/ecommerce-filter-ui)). A tiny closet still needs “2 pieces” vs a silent empty grid.
3. **Load the whole closet at once when the catalog is small** — Baymard’s 100–150 desktop / 15–30 mobile default is for *large* apparel catalogs ([items loaded by default](https://baymard.com/blog/number-of-items-loaded-by-default)). Ten unique mãs should never paginate.
4. **Do not invent size/brand/rating filters** — Baymard’s “five essential filters” assume multi-SKU apparel with size runs. Unique dropship pieces do not have a size matrix. Faking one is an AI-shop lie.

## What we already had

- One card per mã; text-only color names switch the card photo.
- Featured board prints a piece count when tabs change.
- Category pages printed a title only — no count, no “you are here” for assistive nav.

## Applied here

- Category heading now uses the same count line as Featured (`N pieces`).
- Category links set `aria-current="page"` ([ARIA current](https://www.w3.org/TR/wai-aria-1.2/#aria-current)).

## Deliberately not applied

- Sidebar size/price filters, “load more”, or splitting A01 into multiple cards.
- Extra thumbnails on the card (Baymard wants 3+ images on *large* PLPs). Color-name switching is the boutique equivalent without a new chrome.
