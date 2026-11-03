# Official #34 APPLY — liquid chrome SAFE (Fast OFF)

Quiet apply of [SkyLanter/Sassy-closet#34](https://github.com/SkyLanter/Sassy-closet/pull/34) `21-visual-fx-liquid-chrome-safe.md` **§18**. Kelly Ying paper/ink/gold stays. Watery tab pour + Apple peek/roll stay. No WebGL. No Excel. No stock copy on the shop.

Source playbook in this repo: [18-visual-fx-liquid-chrome-safe.md](./18-visual-fx-liquid-chrome-safe.md) (kit filename was `21-…`; `21-dropship-apply.md` already occupies 21 here).

| §18 fix | Landed |
| --- | --- |
| 1. Denylist | No `feDisplacementMap` / `feTurbulence` / Paper `LiquidMetal` / `backdrop-filter: url()`. Goo is not on `<img>`, `.shimmer`, or PDP hero. |
| 2. Message CTA edge | `.ky-chrome-rim` 1.5px mask ring; `--ky-metal` gold/paper/ink stops; compositor `ky-rim-spin` on hover/focus only (`hover` + no-preference). Keep `cta-shine` / `cta-flash`. No goo on the `<a>`. |
| 3. Header hairline | `.ky-header-film` static `color-mix` gold on `border-b`. Paper 0.92 veil stays. No glass over scrolling covers. Wordmark stays ink. |
| 4. Featured goo | Existing `#ky-gold-goo` on `.featured-tab-film` only. Region `x/y -50%` / `200%`, `colorInterpolationFilters="sRGB"`. Meniscus `h-px` + trail. Fast OFF pour stays 320ms. |
| 5. Reduce Motion | Goo + rim spin killed. Shimmer / announce / cta-flash already gated. |

## Deliberately not applied

- Paper shaders, WebGL, displacement on covers or editorial stills.
- Always-on header rim spin (`.shimmer` already spends the infinite slot).
- Restyling fonts, fat pills, iOS liquid glass over photography.
- Inventory / Hold / Available language on customer tiles (Boss sell-test).

Gate: `npm run smoke:motion`.
