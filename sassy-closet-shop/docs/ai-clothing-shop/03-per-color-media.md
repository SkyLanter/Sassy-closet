# Per-color media

## What strong shops do

Craftshift’s Shopify gallery write-up is blunt: shoppers look at photos first, and **if the photos do not match the color they picked, trust drops** ([show images by variant](https://craftshift.com/shopify-product-gallery-variant-selection/)). Native Shopify dumps every `product.media` item into one loop; the default gallery does not filter by variant. Strong themes either:

- tag media to a color and **filter** the slideshow, or
- treat featured images as chapter markers and hide the rest.

Shopify Combined Listings exist because a colorway often needs **its own gallery and URL**, not a shared junk drawer ([combined listings](https://help.shopify.com/en/manual/products/combined-listings-app)).

Baymard still wants variations combined on the **list** card — one identity — while the **PDP** must show only the active color’s photos.

## What we already had

- Admin: hex box + **name** (required) + optional per-color photos. On the hub ten, `colorId` is a recorded slug (`kem`, `cham-bi`) or null.
- Shop: text-only names; gallery filters **this mã** to tagged ∪ untagged photos.
- Card chips switch the cover without a page reload.

## Applied here

- PDP gallery announces the selected color and “photo X of Y” in an `aria-live` region so the filter is audible, not only visual ([WAI-ARIA live regions](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html)).
- Empty color view is **—** on this mã (no blush lie, no other mã, no CSS circle).
- 3-up thumbs +N open a paper/gold lightbox (Esc / backdrop / focus).

## Deliberately not applied

- Hex swatches on the shop (this closet’s chrome is names).
- Invented fashion colors on seed mãs that only have letter-tile covers.
