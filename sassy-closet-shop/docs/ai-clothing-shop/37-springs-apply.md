# Official #37 APPLY — FeaturedBoard springs (Fast OFF)

Quiet apply of [SkyLanter/Sassy-closet#37](https://github.com/SkyLanter/Sassy-closet/pull/37) `20-visual-fx-motion-springs.md` **§19**. Kelly Ying paper/ink/gold stays. PDP native snap gallery from #36 stays. No WebGL. No Excel. No stock copy on the shop.

Source playbook: [20-visual-fx-motion-springs.md](./20-visual-fx-motion-springs.md). Watery metaphor: [13-watery-tab-slide-motion.md](./13-watery-tab-slide-motion.md).

| §19 fix | Landed |
| --- | --- |
| 1. Gold meniscus | `layoutId="featured-tab"` + `springSoft` (ζ ≈ 0.92). `scaleX` 1 → 1.15 → 1 over 320ms. Trail `featured-tab-trail`. Goo on `.featured-tab-film` only. `LayoutGroup id="featured-tabs"`. |
| 2. `layoutScroll` | Phone tab scroller is `motion.div layoutScroll` — no `layout` on the row. |
| 3. Recipe A only | Overlapping `mode="sync"` pour. `replay={false}`. No `tile-${ma}`. No 540ms `wait` blank. |
| 4. Wet, not flippy | Clip-path tween (28% rounded uncover, **not** `springSoft`). Tiny `x` (8 / −6). Fast OFF pour stays **320ms**. |
| 5. Reduce | Hairline jumps. Pour clip/transform killed. No goo on photos. |

## Deliberately not applied

- Recipe B in-place `layoutId={`tile-${ma}`}` (would squash 3:4 covers next to the pour).
- Cutting the pour to a 180ms Fast fade.
- Motion+ / GSAP / a second animation runtime.

Gate: `npm run smoke:motion`.
