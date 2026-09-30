# Per-color product media

Shoppers decide color on the photo. If the swatch does not change the image, the swatch is decoration.

## Platform lesson (Shopify, used as a spec — we are not moving to Shopify)

Shopify’s own help: **one assigned image per variant**; more shots live on the product gallery, grouped next to that color. Source: [Add images to product variants](https://help.shopify.com/en/manual/products/product-media/add-images-variants). Variants themselves are option combinations with **unique SKUs** ([Add variants](https://help.shopify.com/en/manual/products/variants/add-variants)). Extra color galleries need mapping (metafield / filter) — [multiple variant images](https://shopifytheme.blog/multiple-variant-images-in-shopify/).

Craftshift’s boutique-grid rule: swatches **under** the image (not on it), left-aligned, **4–6** visible, 44px hit, 1px border on light colors, accessible **name** even if the shop hides the name visually. Source: [Product grid color swatches](https://craftshift.com/shopify-product-grid-color-swatches-ux/).

## Sassy difference (unique piece)

Sell-test qty is **1**. Colors are **how this one piece photographs** (hex boxes), not a warehouse of sizes. Do **not** mint `A01-RED` / `A01-KEM` as new mãs. The mã stays `A01`.

Intake already has per-piece color chips (`sassy-closet/lib/kinds.ts` + `pieces[]`) — **do not copy that UI onto the shop**. Shop admin said: **boxes only, no names on the swatches; optional note is admin-only.**

## Data shape (export / Blob)

```json
{
  "ma": "A01",
  "colors": [
    { "hex": "#1a1a1a", "note": "admin only" }
  ],
  "images": [
    { "src": "blob-or-/products/A01/cover.jpg", "color_hex": "#1a1a1a", "role": "cover" }
  ]
}
```

Rules:

1. Every image that is not a detail/flat-lay should have a `color_hex` if any colors exist.
2. Cover is the first tagged image of the first color, or the dedicated `cover.jpg`.
3. PDP: tap swatch → swap the gallery to images with that hex. No swatch → no invented second photo.
4. Grid: optional first-swatch preview; do not wrap 15 dots (Craftshift).
5. Light hex (`#fff`, `#f3eee8` blush) needs a ring or they vanish on `--paper`.
6. Screen readers get the hex or the admin note; customers still see a box.

## Apply

- Keep admin: Add hex → tag image → Save {mã}.
- Refuse Save that adds a swatch and leaves every image untagged (warn, don’t invent a tag).
- Do not print color *names* on the storefront swatches.
- Do not pull intake’s 27 named chips (`den`, `trang`, …) onto the shop unless Boss asks.
- Clone-to-Official: `color` column can hold hex list or the admin note — **photo_link** still points at the folder / share URL, never an embed.
