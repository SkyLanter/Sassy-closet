# Photo cleanup round 2 — after review

Still a draft. Nothing is merged or deployed. Blob was not written.

Prices, sizes, colors, and titles are untouched. Photo-list changes are only in `catalog-patch.json`.

Sheets in `before-after/` are original on the left, result on the right. `cover.jpg` is #1.

Zoom check used the installed files: RapidOCR, near-white pixel counts in the Lukira bow box, and the pixel box that actually changed. A blank or smeared edit was reverted to the `main` bytes.

## Every audited photo

| Photo | Final state | Why |
| --- | --- | --- |
| A10 #1 | Cleaned | Lukira letters were already gone. The leftover white bow in the hem (x 602–640) is gone: 1 near-white pixel in that box, against 0 on the passed #4. OCR finds no Lukira. The extra change is 489 pixels inside y 1668–1764. |
| A10 #2 | Cleaned | Same bow only. Changed pixels sit in (602, 1704)–(639, 1730). Near-white count in that box is 0. OCR finds no Lukira. |
| A10 #3 | Reverted | The promo strip is an opaque coupon. Clearing the type left a blank white bar. Putting legs back would invent the photo. Bytes match `main`. |
| A10 #4 | Cleaned | Kept. Review passed this one. Lace hem, no Lukira. |
| A10 #5 | Reverted | `New collection` sits on the garment, and the bow was still there. Bytes match `main`. |
| D01 #3 | Dropped | Promo banner, near-copy of #1. |
| D01 #5 | Dropped | Byte-identical to #2. |
| D02 #3 | Dropped | Promo-banner shot. Front and back stay. |
| D02 #4 | Dropped | Byte-identical to #1. Hero uses `cover.jpg`. |
| D02 #5 | Dropped | Byte-identical to #2. |
| S03 #1 | Dropped | Chinese tagline sits on the shorts. Removing it left dark ghost letters in the hem. The clean flat-lay (old #3) is the cover. |
| S03 #2 | Dropped | `带胸垫防凸点` / `能居家可外出不尴尬` are on the dress. |
| S03 #3 | Cleaned | Now `cover.jpg`. Garment print `JUST FOR YOU` and the Feeling mark stay. |
| A13 #1 | Cleaned | Kept. `Dreamyland` overlay removed. Review passed this one. |
| A13 #2 | Reverted | Ghost `Dr` was an incomplete wipe of text on the knit. A mask large enough to finish it covers the cardigan. Bytes match `main`. |
| A13 #3 | Reverted | Same for the leftover `land_`. Bytes match `main`. |
| V02 #1 | Reverted | The right `©YEGU FLAGSHIP STORE` is light type in the skirt highlights. A mask that catches it also takes the folds. The half-cleaned file is not in the repo, so it cannot ship. The live Blob cover is unchanged. |
| J02 #1 | Reverted | `Mi Manchi` crosses the fingers. The edit left the name and smudged a fingertip. Bytes match `main`. |
| J02 #2 | Reverted | Letter bits and a smudged finger. Bytes match `main`. |
| J02 #3 | Dropped | Byte-identical to #2. |
| P02 #1 | Reverted | The edit smeared the box, ate part of the art, erased `800ML`, and left `sminra`. `sminra` is on the packaging; lifting it hits the cup. Disney, ZOOTOPIA, Nick, and `800ML` are back. Bytes match `main`. |
| P02 #2 | Reverted | Same damage. Bytes match `main`. |
| P03 #1 | Cleaned | Kept. The flat black corner patch was rebuilt. Shin-chan stays. Review passed this one. |
| P03 #2 | Reverted | The edit blanked the English tags and left the inset pictures. Bytes match `main`. |
| P03 #3 | Reverted | A tight mask left `SMINRA`. The wider mask is what smudged Judy. Bytes match `main`. |
| A08 #1 | Reverted | A faint third `FARAFEI` and a dotted mark stayed in the bag texture. Bytes match `main` (PNG data in a `.jpg` name, as before). |
| B03 #2 | Translated | `水桶包·白` is `Bucket bag · White` on all four tiles. The bottom-right line is the same light lettering as the other three, starting to the right of the heart. Heart pixels left of x 808 are the previous frame. OCR reads the phrase on every tile. |
| B03 #3 | Dropped | Byte-identical to #1. |
| O03 #1 | Dropped | Hard-edged brown patches are still on that frame. The passed #2 is now the cover. |
| O03 #2 | Cleaned | Kept, and it is now `cover.jpg`. Marketing lines are gone. Thumb Powder Puff / 拇指粉扑套盒 stays. |
| O03 #3 | Kept | Unedited flat lay. Still in the gallery. |
| A09 #2 | Dropped | Byte-identical to #1. |
| A12 #3 | Dropped | Byte-identical to #2. |
| D03 #3 | Dropped | Byte-identical to #1. |
| O05 #2 | Dropped | Byte-identical to #1. |
| A04 #1 | Cleaned | PNG named `.jpg` is a real JPEG. |
| A04 #3 | Dropped | Same frame as #2. |
| A06 #2 | Cleaned | WebP named `.jpg` is a real JPEG. |
| S02 #1–#3 | Compressed | JPEG q85, about 1624–1744 px, 582–591 KB. |
| V01 #1 | Compressed | JPEG q85, 1387×1849, 580 KB. No promo text. Local file `public/products/V01/cover.jpg`. |

Out of scope, not touched: D05, V03, A16.

## Catalog

`catalog-patch.json` is mã → photo list (src, colorId, order) for the drops, the S03 and O03 cover swaps, and the V01 local cover. V02 is not in the patch. The shop still omits a missing `/products/…` slide, and still points the V01 blob cover at the local file.
