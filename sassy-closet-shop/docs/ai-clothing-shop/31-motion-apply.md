# Official #31 APPLY — customer-pleasing motion

Quiet apply of [SkyLanter/Sassy-closet#31](https://github.com/SkyLanter/Sassy-closet/pull/31) `10-customer-pleasing-motion-ux.md` **§18**. Kelly Ying chrome stays. No new mã. No cart. No redesign.

Source playbook: [10-customer-pleasing-motion-ux.md](./10-customer-pleasing-motion-ux.md).

| §18 fix | Landed |
| --- | --- |
| 1. Looped motion only under `prefers-reduced-motion: no-preference` | `announce-fade` / `shimmer-slide` infinite / `cta-flash` gated. Card lift + 1.08 zoom use `motion-safe:`. Reduce query still kills animations + VT zoom. `@view-transition { navigation: auto }` |
| 2. Covers paint without JS | `fadeUp` hidden is opacity 1. Cover `<img>` has no `opacity-0`. Shimmer sits behind the photo. `view-transition-name: product-{THIS mã}` on the aspect wrapper |
| 3. PDP hero VT + ink/gold lightbox | Hero wrapper is `product-{ma}`. Related rail keeps neighbor names. Trigger is a button (“Xem ảnh lớn · View larger”). `PhotoLightbox` portals, ink/70 veil, gold ring, 44×44 **Đóng**, Esc / backdrop / ✕, deferred close, this-mã set only |
| 4. Featured tabs | APG keyboard stays. Filter is ≤180ms opacity. Holds stay in their type (P02/P05 in Accessories). Empty `/c/quan` does not mint Q01 |
| 5. Color → gallery | Text chips only when `colors[]` exist. Fade this mã’s tagged ∪ untagged images (150–200ms). Reduce = instant. Never swap in another mã’s cover |

## Deliberately not applied

- Closing Boss Add / hiding live A03. Official “All 10” is the hub-ten seed. After Add, counts are honest math on shop-visible rows.
- Inventing Kem/Xanh chips on rows whose `colors[]` is empty.
- Intake rose lightbox, `001.jpg`, cart motion, Kelly Ying `$10 / $300+`.

Gate: `npm run smoke:motion` plus pdp / bugcheck / kit-apply.
