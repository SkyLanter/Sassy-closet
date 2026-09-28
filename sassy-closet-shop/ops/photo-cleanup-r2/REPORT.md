# Photo cleanup round 2

Draft only. Nothing here is merged or deployed. Mini Boss lands `catalog-patch.json` after Boss approves the sheets in `before-after/`.

Prices, sizes, colors, and titles are untouched. Blob was not written.

Sheets: one JPEG per mã, original on the left, result on the right, labeled `mã #n` (`cover.jpg` is #1).

## Every audited photo

| Photo | Result | Why |
| --- | --- | --- |
| A10 #1 | Cleaned | Removed the bottom `Lukira 2025` overlay. Lace hem left in place. |
| A10 #2 | Cleaned | Same Lukira overlay removed. |
| A10 #3 | Cleaned | Removed `New collection`, Lukira, `Feel your best self`, and the bottom promo (`新风潮·活动立减`, `12%`, 88VIP, sale dates). |
| A10 #4 | Cleaned | Same Lukira overlay removed. |
| A10 #5 | Cleaned | Removed the English marketing lines and the leftover `New collection` / Lukira. |
| D01 #3 | Dropped | Promo banner on a near-copy of #1. #1 stays. |
| D01 #5 | Dropped | Byte-identical to #2. |
| D02 #3 | Dropped | Promo-banner shot. Not a byte copy of #1; clean front (#1) and back (#2) stay. |
| D02 #4 | Dropped | Byte-identical to #1. Homepage hero now uses `cover.jpg` (same picture). |
| D02 #5 | Dropped | Byte-identical to #2. |
| S03 #1 | Cleaned | Removed `BOUTIQUE NIGHTDRESS`, the festival line, and `上身牛奶般的丝滑感`. Feeling mark kept. |
| S03 #2 | Skipped | `带胸垫防凸点` / `能居家可外出不尴尬` sit on the dress. Removing them smeared the fabric, so the file is unchanged. |
| A13 #1 | Cleaned | `Dreamyland` was a semi-transparent overlay, not a garment print. Removed. |
| A13 #2 | Cleaned | Same overlay removed. |
| A13 #3 | Cleaned | Same overlay removed. |
| V02 #1 | Cleaned | Removed both `©YEGU FLAGSHIP STORE` marks and `YEGU NEW FASHION`. File added at `public/products/V02/cover.jpg`. |
| J02 #1 | Cleaned | Removed the bottom `Mi Manchi` watermark. The book-page background stays. |
| J02 #2 | Cleaned | Removed the bottom `Mi Manchi` watermark. |
| J02 #3 | Dropped | Byte-identical to #2. |
| P02 #1 | Cleaned | No `shimra` / `SMNRA` on the frame. Removed the Chinese series title. Disney, ZOOTOPIA, and Nick stay. |
| P02 #2 | Cleaned | Same: no shimra; Chinese series title removed; Disney mark stays. |
| P03 #3 | Cleaned | Removed the `SMINRA` watermark. Judy Hopps lettering stays. |
| A08 #1 | Cleaned | Removed the three `FARAFEI` watermarks and saved a real JPEG, 1440×1920, 420 KB. |
| P03 #2 | Cleaned | Removed the `Random 3D sticker` and `Cleaning tool` callouts. Stitch on the bottle stays. |
| B03 #2 | Translated | `水桶包·白` on each panel is now `Bucket bag · White`. The bag is unchanged. |
| O03 #2 | Cleaned | Removed the translated marketing lines. Thumb Powder Puff / 拇指粉扑套盒 on the box stays. |
| O03 #1 | Skipped | The right side is continuous table and shadow. No separate hard-edged brown rectangle could be lifted without painting a new patch. |
| P03 #1 | Cleaned | Rebuilt the flat black rectangle in the top-right from the surrounding backdrop. Shin-chan on the bottle stays. |
| A09 #2 | Dropped | Byte-identical to #1. |
| A12 #3 | Dropped | Byte-identical to #2. |
| B03 #3 | Dropped | Byte-identical to #1. |
| D03 #3 | Dropped | Byte-identical to #1. |
| O05 #2 | Dropped | Byte-identical to #1. |
| A04 #3 | Dropped | Same frame as #2 (PNG re-encode). |
| A04 #1 | Cleaned | Was a PNG named `.jpg`. Now a real JPEG. |
| A06 #2 | Cleaned | Was a WebP named `.jpg`. Now a real JPEG. |
| S02 #1 | Compressed | JPEG q85, 1624×1624, 582 KB (was 3024×3024, 2.4 MB). |
| S02 #2 | Compressed | JPEG q85, 1624×1624, 591 KB. |
| S02 #3 | Compressed | JPEG q85, 1744×1744, 582 KB. |
| V01 #1 | Compressed | JPEG q85, 1387×1849, 580 KB (was 3097×4129, 2.8 MB). No promo text found. Saved at `public/products/V01/cover.jpg`. |

Out of scope, not touched: D05 dead photos, V03 alicdn hotlinks, A16 low-res.

## Catalog

`catalog-patch.json` is mã → new photo list (src, colorId, order only) for drops and for V01/V02 local covers. The shop also skips a `/products/…` slide when that file is missing, and points V01/V02 blob covers at the cleaned local files the same way A16, D04, and S09 already work. Mini Boss still lands the patch so Blob matches the files.
