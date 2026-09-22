# Official #38 APPLY — CSS snap / mask / VT gallery (Fast OFF)

Quiet apply of [SkyLanter/Sassy-closet#38](https://github.com/SkyLanter/Sassy-closet/pull/38) `19-visual-fx-css-snap-mask-vt.md` **§22**. Kelly Ying paper/ink/gold stays. Featured watery pour stays **320ms**. Excel / OneDrive stay read-only. No Swiper. No invented `001.jpg`.

Source playbook: [19-visual-fx-css-snap-mask-vt.md](./19-visual-fx-css-snap-mask-vt.md).

| §22 fix | Landed |
| --- | --- |
| 1. Frame name | `view-transition-name: product-{THIS mã}` on `.ky-gallery-frame` — the stable `aspect-[3/4] overflow-hidden bg-[#f3f1ee]` box. Not on `<img>`, not on the color `AnimatePresence` layer. Related A02 tile is `product-A02` only. |
| 2. Snap rail | Native `scroll-snap-type: x mandatory` on `.pdp-rail` / `.ky-gallery-port` **inside** that named frame. Fast OFF keeps **78% / 12px center-snap** so a real neighbor JPEG peeks. `n=1` is full-bleed, no dots, no mask, no clone. |
| 3. Paper-edge mask | `mask-image` on the **rail**, never the JPEG. `--fade: 1.25rem`. `data-edge="start\|end\|both"` from the snapped index. `n=1` or Reduce → `mask-image: none`. No animated mask bloom. |
| 4. Backdrop chrome | `backdrop-filter` on sticky Message bar + `.pdp-lightbox-veil` + `.liquid-glass` prev/next only. **No** `.ky-frost-*` on peek cloth. `--blur-md: 12px`. Header opacity sheet untouched. |
| 5. Lightbox | Portal, Đóng 44×44, `setTimeout(0)` close. Veil `bg-ink/70` + blur behind no-preference. Same-mã snap rail inside; **no wrap**. |
| 6. Colors | `imagesForColor` tagged ∪ `null` on this mã. No minting files from hex. A02 never lists `/products/A01/`. |
| 7. Reduce | Instant scroll. Mask off. Veil blur off. Enlarge + Message still work. |

## Deliberately not applied

- LEARN 19’s `flex: 0 0 100%` / `snap-align: start` on the **PDP** rail (would hide the neighbor photo; peek would be a fake paper fade). Lightbox overlay uses 100% start-snap.
- Inventing `/products/{MA}/001.jpg` because HQ folders listed it.
- Customer Hold / Available / on-hand copy (VERIFY still says “Hold · Inbox for price”; the shop prints Inbox without that word).
- SVG goo / displacement / `backdrop-filter` on photography.

Gate: `npm run smoke:motion` plus `smoke:pdp` / `smoke:media` / `smoke:bugcheck`.
