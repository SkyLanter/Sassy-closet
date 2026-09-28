# Photo cleanup round 2 — only the photos that passed

Still a draft. Nothing is merged. Production was not deployed. Blob was not written.

The last full-size review failed five edits. Those files are the `main` bytes again. No further photo editing.

Prices, sizes, colors, and titles are untouched. Photo-list changes are only in `catalog-patch.json`.

Sheets in `before-after/` are original on the left, result on the right. `cover.jpg` is #1. A10 and A13 match `main`, so those sheets are gone.

## Every audited photo

| Photo | Final state | Why |
| --- | --- | --- |
| A10 #1 | Reverted | Two thin white `\|` bars remain, and the black skirt has a dark blotch where the bow was. Bytes match `main`. |
| A10 #2 | Reverted | The same two `\|` bars. Bytes match `main`. |
| A10 #3 | Reverted | Clearing the coupon left a blank white bar. Bytes match `main`. |
| A10 #4 | Reverted | The `\|` bars are still on the lace. Bytes match `main`. |
| A10 #5 | Reverted | `New collection` sits on the garment. Bytes match `main`. |
| D01 #3 | Dropped | Promo banner, near-copy of #1. |
| D01 #5 | Dropped | Byte-identical to #2. |
| D02 #3 | Dropped | Promo-banner shot. Front and back stay. |
| D02 #4 | Dropped | Byte-identical to #1. Hero uses `cover.jpg`. |
| D02 #5 | Dropped | Byte-identical to #2. |
| S03 #1 | Dropped | Chinese tagline sits on the shorts. Removing it left dark ghost letters. The clean flat lay (old #3) is the cover. |
| S03 #2 | Dropped | Chinese lines sit on the dress. |
| S03 #3 | Kept as cover | Now `cover.jpg`. Garment print `JUST FOR YOU` and the Feeling mark stay. |
| A13 #1 | Reverted | The cat and rose print is smeared where `Dreamyland` was, and the tail of `_` is still visible. Bytes match `main`. |
| A13 #2 | Reverted | Ghost `Dr` on the knit. Bytes match `main`. |
| A13 #3 | Reverted | Leftover `land_`. Bytes match `main`. |
| V02 #1 | Reverted | The right `©YEGU FLAGSHIP STORE` sits in the skirt highlights. The file is not in the repo. The live Blob cover is unchanged. |
| J02 #1 | Reverted | `Mi Manchi` crosses the fingers. Bytes match `main`. |
| J02 #2 | Reverted | Letter bits and a smudged finger. Bytes match `main`. |
| J02 #3 | Dropped | Byte-identical to #2. |
| P02 #1 | Reverted | The edit smeared the box and left `sminra`. Bytes match `main`. |
| P02 #2 | Reverted | Same damage. Bytes match `main`. |
| P03 #1 | Cleaned | The flat black corner patch was rebuilt. Shin-chan stays. |
| P03 #2 | Reverted | The edit blanked the English tags. Bytes match `main`. |
| P03 #3 | Reverted | The edit left `SMINRA` and smudged Judy. Bytes match `main`. |
| A08 #1 | Reverted | A faint third `FARAFEI` stayed in the bag texture. Bytes match `main`. |
| B03 #2 | Reverted | The bottom-right tile still has a black glyph fragment and a grey smear. The top-left line is dark, and the text overlaps the heart. Bytes match `main`. |
| B03 #3 | Dropped | Byte-identical to #1. |
| O03 #1 | Dropped | Hard-edged brown patches. The passed #2 is now the cover. |
| O03 #2 | Cleaned | Kept, and it is now `cover.jpg`. Thumb Powder Puff stays. |
| O03 #3 | Kept | Unedited flat lay. Still in the gallery. |
| A09 #2 | Dropped | Byte-identical to #1. |
| A12 #3 | Dropped | Byte-identical to #2. |
| D03 #3 | Dropped | Byte-identical to #1. |
| O05 #2 | Dropped | Byte-identical to #1. |
| A04 #1 | Format | PNG named `.jpg` is a real JPEG. |
| A04 #3 | Dropped | Same frame as #2. |
| A06 #2 | Format | WebP named `.jpg` is a real JPEG. |
| S02 #1–#3 | Compressed | JPEG q85, about 1624–1744 px, 582–591 KB. |
| V01 #1 | Compressed | JPEG q85, 1387×1849, 580 KB. Local file `public/products/V01/cover.jpg`. |

Out of scope, not touched: D05, V03, A16.

## Catalog

`catalog-patch.json` is mã → photo list for the drops, the S03 and O03 cover swaps, and the V01 local cover. Each listed file is on disk, and each listed mã still has at least one photo. A10 and A13 are not in the patch. B03 still lists cover, photo-2, and photo-4. V02 is not in the patch.

The shop drops a `/products/…` slide only when that file is absent from `data/local-product-files.json`. That list is written by `scripts/write-local-product-manifest.mjs` during `npm run build` and bundled into the server. Request-time `existsSync` is gone, so a serverless function that cannot see `public/` still shows the photos that shipped. Blob URLs, including V02, stay.
