# Official #40 APPLY — a11y watery motion (Fast ON)

Quiet apply of [SkyLanter/Sassy-closet#40](https://github.com/SkyLanter/Sassy-closet/pull/40) `17-a11y-watery-motion.md` **§18**. Kelly Ying paper/ink/gold stays. Watery reel + 320ms Featured pour stay. Excel / OneDrive stay read-only.

Source: [17-a11y-watery-motion.md](./17-a11y-watery-motion.md). Kit QA: [qa/qa_a11y_watery_motion.py](./qa/qa_a11y_watery_motion.py) (LOOK still expects the word Hold on the live host; **this shop does not print Hold / Available to customers**).

| §18 fix | Landed |
| --- | --- |
| A. Hue-only chips | Customer chips are **text**. Admin `name` if stored; else `Color 1` / `Color 2`. Never `Color #F4F0E8`. Never invent Kem/Xanh from hex or from a bare `kem` id. |
| B. Same-src | Color tap updates the chip without moving the rail when the JPEG is unchanged (`colorId` null / shared cover). No `x:24`, no `mode="wait"`. |
| C. APG | Carousel roles only when `n > 1`. Single cover is enlarge-only. Featured stays `tablist` + `tabpanel`. |
| D. Reduce | `motion-safe:` on 1.08 zoom + card lift. Infinite shimmer / announce / CTA stay under `no-preference`. Gold + Message stay. |
| E. Frost | `backdrop-filter` on Message dock, lightbox veil, peek **chrome** strips. Never on the garment `<img>`. |

## Deliberately not applied

- Printing **Hold / Available** on the lookbook to satisfy the kit LOOK script.
- Guessing Kem from `#F4F0E8` because the hub sample used that slug.
- Flattening the watery roll when motion is OK.

Gate: `npm run smoke:motion` plus `smoke:pdp` / `smoke:bugcheck`.
