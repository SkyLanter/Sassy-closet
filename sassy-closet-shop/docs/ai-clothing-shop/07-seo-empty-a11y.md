# SEO, empty states, a11y (small closets)

## What strong shops do

Google’s product structured data wants a real `Offer` and forbids inventing availability ([Product structured data](https://developers.google.com/search/docs/appearance/structured-data/product)). Schema.org `ItemList` is the collection equivalent — list the URLs that actually exist ([ItemList](https://schema.org/ItemList)).

Test-mode shops should `noindex` until `NEXT_PUBLIC_SITE_MODE=official` and a public origin exist. That is how you avoid an AI demo ranking over the real Page.

Empty lists must say so. Baymard’s filter work shows users lose trust when a grid is blank with no count ([filter UI](https://baymard.com/learn/ecommerce-filter-ui)). WCAG 2.2 status messages belong in a live region or a visible sentence, not a vanished section ([status messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html)).

## What we already had

- Root robots noindex in test (lasting TEST — see [06-seo-trust](./06-seo-trust-diaspora-boutique.md)). Official + origin can flip later.
- Product JSON-LD: Hold/dropship is PreOrder, never fake InStock, never `shippingRate`.
- Collection empty copy; skip link; `aria-current`; gallery live region.

## Applied here

- Category pages emit an `ItemList` JSON-LD of shop-visible mãs (no invented URLs if the public origin is unset — absolute URLs only when `NEXT_PUBLIC_SHOP_URL` exists).
- OG/Twitter images use the public origin when set (PDP cover, category tile, home hero). Test mode stays `noindex`.
- Empty collection / grid copy is a `role="status"` sentence. Featured and category counts are live regions.

## Deliberately not applied

- Review stars, fake stock counts, or indexing the test shop.
