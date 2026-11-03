# Official #36 APPLY — iOS frosted carousel (Fast OFF)

Quiet apply of [SkyLanter/Sassy-closet#36](https://github.com/SkyLanter/Sassy-closet/pull/36) `16-ios-frosted-carousel-deep.md` **§21**. Kelly Ying paper/ink/gold stays. Featured watery pour stays **320ms**. No WebGL. No Excel. No stock copy on the shop.

Source playbook: [16-ios-frosted-carousel-deep.md](./16-ios-frosted-carousel-deep.md).

| §21 fix | Landed |
| --- | --- |
| 1. Native snap | PDP roll is CSS `scroll-snap-type: x mandatory` on `.ky-gallery-port`. No Framer `drag` on the same node. `n === 1` is full-bleed, no peek/mask/frost/dots. |
| 2. Edge mask | `mask-image` on the **port**, not `<img>`. Neighbors dissolve into paper over 28px. |
| 3. Frost chrome | Sibling strips in this pass. **#38 removed them** — `backdrop-filter` is chrome / lightbox veil only, never peek cloth. |
| 4. Chrome motion | Framer `useScroll({ container })` drives the gold hairline. Color SET fade is `COLOR_FADE_SECONDS` (0.2) opacity only — no `x:24`, no `mode="wait"`. |
| 5. Honest colorId | `imagesForColor` = tagged ∪ shared `null` on **this** mã. Unknown ids stay empty. `/products/{other hub mã}/` never renders. A02 is Chấm bi, never A01 Kem/Xanh hexes. |

## Deliberately not applied

- iOS Liquid Glass / goo / displacement on photography.
- Inventing chips on K01 / H01.
- Customer Hold / Available / on-hand copy (VERIFY line 5 in the kit still says Hold; this shop keeps Inbox for price without that word).
- Closing Boss Add / minting A03 on the lookbook.

Gate: `npm run smoke:motion` plus `smoke:pdp` / `smoke:media` / `smoke:bugcheck`.
