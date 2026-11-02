# 13 — Watery / liquid tab + slide motion

**Learn track:** Ultra burn (research + live as-built + APPLY).  
**Shop:** Sassy Closet — Facebook inbox is the store; Square Free is on-hand truth; sell-test lookbook is Origin-owned.  
**Live APPLY target:** [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)  
**Audience:** Mini Boss / Origin shop implementer / whoever polishes **tab + grid** motion without breaking reliability.  
**Date researched / crawled:** 2026-09-09.  
**This file does not assign stock, mint a mã, Save in Square, post to Facebook, restyle the boutique, or touch Excel / intake.**

Sister `10` is the **general** motion law (purpose, reduced-motion, lightbox, PDP hero names). This note is the **material**: how Featured tabs and the grid **pour**, not flip. Kelly Ying *look* stays locked (`01` §1.3, §11). Fancy motion stays locked (`07` §11.0; `09` §0; `10` §2). Mini Boss pastes **§19** into the Origin agent. Do not paraphrase §19 into “add liquid glass.”

---

## 0. How to read this document

This is a **learn-track** note, not a rebuild brief and not permission to fork Origin shop code from this kit repo.

- **Cite, don’t invent.** Shop-law claims point at a file, Slack permalink, sister learn-track, or the live host. Industry claims point at NN/G, W3C WCAG 2.2, WAI-ARIA APG, MDN, Chrome View Transitions / scroll-driven case studies, Lucas Bebber’s goo filter, Paul Lewis FLIP, Motion `layoutId`, or Apple HIG. If a fact is missing, the gap is named.
- **Never invent a mã.** Customer-facing codes this pass may name are the **first-ten allowlist** only. Admin “Next mã A03” is a prediction. Slack `AO001` / `AO003` are **decision-template examples** (`#shop-decisions`, 2026-09-04), not live lookbook stock. Kelly Ying `V984.` / `V826.` are **their** SKUs — do not copy them onto Sassy tiles.
- **Two alphabets.** Sell-site / hub = `A01`. Official / Square / SoT = `AO001`. Motion never translates one into the other (`01` §9; `excel-kit/schema.py` `MA_RE`).
- **Facebook inbox is the store.** A “buy” is **Message {code}**. There is no cart. Watery motion that implies checkout (bag-fly, liquid pour into a cart) is a lie.
- **No redesign mandate.** Improve **inside** paper / ink / gold / blush, Cormorant Garamond + Be Vietnam Pro, `ma-mark`, `announce-fade`, `shimmer` / `shimmer-slide`, `cta-shine` / `cta-flash`, gold `h-px` underline, `layoutId: "featured-tab"`, `filterSlide`, `springSoft`, `view-transition-name: site-header` / `product-{MA}`. Do not replace that language with iOS liquid glass over photography, Shopify Horizon, intake Allura/Nunito rose, or a new design system.

### 0.1 Research method (and what this pass could not see)

| Source | Result |
| --- | --- |
| Live sell-test HTML + CSS + JS of `/` (2026-09-09) | Primary **as-built** tab + slide map. CSS chunk `/_next/static/immutable/chunks/34vl_zddoo4ws.css`. Motion chunk `/_next/static/immutable/chunks/3_93acjqq2t4q.js` (exports `FeaturedBoard`, `AnimatedProductGrid`, `filterSlide`, `springSoft`, `fadeUp`, `staggerContainer`). |
| `curl -I` / HTML of `/c/ao`, `/c/quan`, `/m/A01`, `/m/P02` | Category vs home IA; PDP VT names (same gaps as `10`). |
| Repo `excel-kit/`, `sassy-closet/`, `README.md` | Shop law. Intake sheets are **behavior** only — do not restyle. |
| Sister LEARN TRACK PRs #19–#31 (`01`–`12`) | Headings + locks. This file is `13`. |
| Slack `#shop-decisions` (`C0BV3GYC602`) | Five standing messages (2026-09-04). No watery-motion thread. |
| Linear | Keyword search returned onboarding `TIE-3` only — no motion issue. |
| Granola meetings | MCP unauthorized — no meeting notes. |
| Notion | Business-plan AI search unavailable; keyword search not used for shop law. |
| Kelly Ying Boutique public site | Cloudflare challenge this pass (`Ray ID: a388e425bc1c018b`). Look / cadence facts stay with `01` + `10` (home + Dresses, earlier 2026-09-09 read). |
| Public UX / a11y / liquid-motion specs | Fetched 2026-09-09. URLs in §17. |

If a later crawl disagrees with a **live** cell here, **the new crawl wins** — update the date line. Shop law still wins over industry taste.

### 0.2 Sister docs

| # | File | Job vs this note |
| --- | --- | --- |
| 01 | `01-messenger-social-commerce.md` | Kelly Ying look lock; Message-first; no cart |
| 02 | `02-pdp-color-size-ux.md` | Customer **text** colors; gallery sync |
| 03 | `03-tiny-boutique-admin.md` | Admin brains; do not mint from “Next mã” |
| 04 | `04-next-blob-catalog-arch.md` | ISR / Blob; `/m/A03` must 404 |
| 05 | `05-ai-product-media.md` | Recorded first-ten colors; no invented hex |
| 06 | `06-seo-trust-diaspora-boutique.md` | Soft-launch `noindex`; unique `/c/*` titles |
| 07 | `07-taobao-dropship-boutique.md` | Motion lock list; dropship-honest copy |
| 08 | `08-dropship-ops-runbook.md` | Staff clock; does not restyle |
| 09 | `09-bugcheck-sell-site-checklist.md` | Tick-box QA; MOT-01…MOT-08 |
| 10 | `10-customer-pleasing-motion-ux.md` | General motion law + five Origin fixes |
| 11 | `11-vercel-blob-admin-qa.md` | Admin / Blob gate; look stays |
| 12 | `12-fb-messenger-dropship-copy.md` | VN+EN phrase bank; no motion |
| **13** | **This file** | **Watery tab + slide; APPLY for Origin** |
| Kit | `SELL_CATALOG_CONTRACT.md` (PR #18) | Allowlist + prices + Hold null `$` |

`10` already asked for APG tabs, ≤200ms filter, and `startViewTransition` skipped on Reduce Motion. Live JS (this crawl) **already** has a spring gold rule and a directional `filterSlide`. This note names those hooks and tells Origin **how to make them feel liquid without changing the look**.

---

## 1. Executive summary

A premium boutique tab does not *jump*. It **wets** the next label. A premium boutique grid does not *pop*. It **pours** in the direction the buyer just pointed. That is the whole job.

Nielsen Norman Group: animation must be **unobtrusive, brief, and subtle**. Use it for **feedback**, **state-change**, **navigation metaphors**, and **stronger signifiers** — not delight, not downtime ([NN/G, *The Role of Animation and Motion in UX*](https://www.nngroup.com/articles/animation-purpose-ux/)). Peripheral vision treats motion as important; irrelevant motion degrades the task. Microinteractions are trigger → rule → feedback, one job each ([NN/G, *Microinteractions in User Experience*](https://www.nngroup.com/articles/microinteractions/); Saffer 2014).

Sassy Closet’s sell-test already shipped a Kelly Ying *rhythm*: serif wordmark, gold hairline, blush/paper/ink, 11px tracking, livestream rail, SKU-on-card, Featured chips — **without** Kelly Ying’s cart (`01` §1.3). Live motion on the **tab + slide** path (2026-09-09, JS chunk `3_93acjqq2t4q.js`) is already more specific than `10` could see from HTML alone:

| Hook | Live fact |
| --- | --- |
| `FeaturedBoard` | Client filter. State `"all"` + `types[]`. Counts from the ten. |
| Tab button `f()` | `role="tab"` · `aria-selected` · gold `h-px` · `layoutId: "featured-tab"` unless reduced |
| `springSoft` | `{ type: "spring", stiffness: 420, damping: 32, mass: 0.72 }` |
| Click `b(next)` | `direction = index(next) >= index(current) ? 1 : -1` then `setState` |
| `AnimatedProductGrid` | `AnimatePresence mode="wait"` + `filterSlide(reduced, direction)` |
| `filterSlide` | Enter `x: 28*dir` / `0.32s` ease `[.22,1,.36,1]`; exit `x: -22*dir` / `0.22s`. Reduced = duration `0`. |
| Count line | `AnimatePresence` + `motion.span` `duration: 0.18` (0 if reduced) |
| `ProductGrid` tiles | `layout` + `fadeUp` + `springSoft` on each `motion.li` |

That is already a **shared-element gold rule** (Motion `layoutId` = FLIP-class travel — [Motion layout animations](https://www.framer.com/motion/layout-animations/); [Paul Lewis, *FLIP Your Animations*](https://aerotwist.com/blog/flip-your-animations/)) plus a **directional slide**. It is **not** yet watery:

1. The gold rule is a **1px rectangle** that translates. No stretch, no meniscus, no trailing film. It reads as a UI slider, not silk.
2. `AnimatePresence mode="wait"` **serializes** exit then enter (`0.22 + 0.32 = 0.54s`). NN/G’s 0.1s / 1s limits say a frequent tab should feel instantaneous at the tap and stay in flow under 1s ([*Response Time Limits*](https://www.nngroup.com/articles/response-times-3-important-limits/)). `10` budgeted **≤200ms** for the filter. Live is already long. Watery must **overlap and soften**, not add a 700ms luxury wipe.
3. The slide is a hard `translateX`. Fashion photography wants a **clip** (curtain / pour), not a second page sliding over the first ([Chrome e-commerce SDA: redBus `clip-path` reveal](https://developer.chrome.com/blog/css-ui-ecommerce-sda); [MDN `clip-path`](https://developer.mozilla.org/en-US/docs/Web/CSS/clip-path)).
4. Tabs are still mouse-first: no `tabpanel`, no `aria-controls`, no arrow keys (`10` §7; [APG Tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/)).
5. SVG **goo** (Bebber) and CSS `shape()` liquid wipes are **tools**, not a new brand. Applied to product photos they **lie about the garment**. Applied to a dedicated gold-rule layer they can feel wet.

Reliability still beats beauty. A goo filter that blurs “Hold” into “Available”, a 700ms ooze that hides P02, or a clip-path that flashes A02’s cover on A01 is a **failed** boutique.

---

## 2. Hard constraints (print these on the implementer’s wall)

1. **Never invent a mã.** Emit list is exactly `A01 S01 P01 P02 P03 P04 P05 K01 H01 A02` (PR #18). Empty `/c/quan` stays empty. No `Q01` “so the wipe has something to pour.”
2. **Never invent qty, $, photos, hex, or color names.** Hold P02 / P05 = **Inbox for price**. Empty `colors[]` = no chips (`02`; `05`; `10` §8).
3. **Square Free = on-hand truth.** Official Excel is a working copy (`README.md`). This kit does not edit Excel or intake in this pass.
4. **Bots draft only.** No Square Save, no Facebook Post/Send (`#shop-decisions` 2026-09-04).
5. **No cart, Shop now, or bag-fly.** Kelly Ying’s **$10 / $300+** and `V###` codes are **theirs** (`01` §0).
6. **Customer colors are text** (WCAG [1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)).
7. **Motion never changes identity.** Same mã in, same mã out. `product-A01` morphs only to A01. Filter must not drop P02/P05.
8. **Water never lies on the photo.** No `filter: url(#goo)` on `.shimmer`, covers, or heroes. No `feDisplacementMap` over garments. Distortion is a **fabric lie**.
9. **Origin owns the pixels.** APPLY is for the Origin agent on `sassy-closet-shop`. Intake Production stays https://sassy-closet.vercel.app. This PR does not edit `excel-kit/` or `sassy-closet/`.

---

## 3. What “watery” means here (and what it is not)

### 3.1 Fashion liquid, not OS chrome

“Liquid glass” in 2025–26 vendor posts usually means `backdrop-filter` + SVG displacement over **the whole chrome** ([FreeFrontend liquid-glass roundup](https://freefrontend.com/css-liquid-glass/)). That is a phone OS trick. On a lookbook it **frosts the garment** and fights `--paper` / `--ink`. **Refuse** full-viewport glass, chromatic aberration on covers, and cursor-follow blobs.

Watery *for this closet* is three physical metaphors, all gold-on-paper:

| Metaphor | Buyer should feel | Fail if… |
| --- | --- | --- |
| **Meniscus** | The gold hairline **stretches** toward the next tab, then snaps flush | Fat pill / iOS capsule under the 11px label |
| **Viscosity** | Travel is springy (`springSoft`), not linear | Instant teleport, or a 700ms “luxury” ease |
| **Pour** | The grid **uncovers** in the tab’s direction (clip), same ten SKUs | A second catalog slides in; empty kinds spawn tiles |

Apple HIG: do not make people **wait** for frequent motion; Reduce Motion replaces large spatial moves with a **crossfade or instant** ([HIG — Motion](https://developer.apple.com/design/human-interface-guidelines/motion); [App Store Connect Reduced Motion criteria](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria/)). Featured tabbing is frequent. Watery is **short viscosity**, not a show.

### 3.2 NN/G jobs, mapped onto tab + slide

| NN/G job | Watery meaning | Fail if… |
| --- | --- | --- |
| Feedback | Gold rule starts moving within **0.1s** of tap ([NN/G attention](https://www.nngroup.com/articles/animation-usability/)) | Click, then 300ms of nothing |
| State change | `aria-selected` + count text + visible set change; motion is extra | Animation is the only cue (fails 1.4.1) |
| Spatial metaphor | Right-hand tab → grid pours from the right; Back feels like the reverse | Random direction; wait-mode “new page” |
| Signifier | Hairline is tappable chrome; phone does not need hover | Watery only on `@media (hover:hover)` |
| Attention | One moving gold film | Goo + shimmer + stagger + VT all at once (Hipmunk pile-on — NN/G) |

### 3.3 Technique catalog (use / refuse)

| Technique | Source | Use on sell-test? |
| --- | --- | --- |
| Shared `layoutId` FLIP | [Motion layout](https://www.framer.com/motion/layout-animations/); [Lewis FLIP](https://aerotwist.com/blog/flip-your-animations/); [CSS-Tricks FLIP](https://css-tricks.com/animating-layouts-with-the-flip-technique/) | **Already live** on `featured-tab`. Keep. Tune spring / add stretch. |
| SVG goo (`feGaussianBlur` + `feColorMatrix` alpha) | [Bebber / CSS-Tricks](https://css-tricks.com/gooey-effect/); [Animata Gooey Tabs](https://animata.design/docs/tabs/gooey-tabs) | **Optional, gold-rule layer only.** Never on photos or 11px type. Safari-on-DOM caveat: Bebber — degrade to the hairline. |
| `clip-path: inset()` wipe | [MDN clip-path](https://developer.mozilla.org/en-US/docs/Web/CSS/clip-path); [Chrome SDA / redBus](https://developer.chrome.com/blog/css-ui-ecommerce-sda) | **Preferred watery slide** on `AnimatedProductGrid` wrapper. Compositor-friendlier than animating `width`. |
| CSS `shape()` liquid ooze | [Temani Afif, CSS Tip, 2026-04-02](https://css-tip.com/sliding-liquid/) | **Refuse as a full-page veil.** Optional 1-axis wave on the **clip edge** if `@supports` and reduced = off. 6s demos are **not** a tab budget. |
| View Transitions custom `clip-path` | [CSS VT L1](https://drafts.csswg.org/css-view-transitions-1/); Chrome same-document | Home → PDP only, **after** `product-{MA}` names match (`10` FIX 3). Do not VT the Featured filter (same-document Framer already owns it). |
| CSS Anchor + glass pointer | [FreeFrontend anchored tab, 2026-03](https://freefrontend.com/code/anchored-glassmorphic-tab-indicator-2026-03-03/) | **Refuse.** Firefox/Safari gaps; glass fights paper. `layoutId` already tracks the tab. |
| WebGL cloth / cursor metaballs | vendor demos | **Refuse** (`10` anti-pattern 11). |
| Scroll-driven `animation-timeline: view()` | [Chrome SDA](https://developer.chrome.com/blog/css-ui-ecommerce-sda) | **Not this APPLY.** CollectionList already has `whileInView` + `staggerContainer`. Do not add parallax (WCAG 2.3.3 names it). |

---

## 4. As-built hook map (cite the live host)

Crawl: 2026-09-09. HTML on `/`. CSS `34vl_zddoo4ws.css`. JS `3_93acjqq2t4q.js` (Turbopack module `42295` = motion helpers; `FeaturedBoard` + `AnimatedProductGrid` in the same chunk).

### 4.1 CSS tokens (do not rename)

```css
:root {
  --paper: #fff;
  --ink: #111;
  --muted: #6b6b6b;
  --line: #ececec;
  --gold: #b08968;
  --gold-deep: #8c6a4e;
  --blush: #f3eee8;
  --duration-exit: .15s;
  --duration-enter: .21s;
  --duration-move: .4s;
}
```

Fonts (HTML classes on `<html>`): `be_vietnam_pro_…__variable` + `cormorant_garamond_…__variable`. Utilities: `font-sans` → `--font-be-vietnam`; `font-display` → `--font-cormorant`.

Existing keyframes (keep names — `10` FIX 1):

```css
@keyframes announce-fade { 0%,12%{opacity:0} 20%,80%{opacity:1} 92%,to{opacity:0} }
@keyframes shimmer-slide { 0%{background-position:120% 0} to{background-position:-20% 0} }
@keyframes cta-flash { to{transform:translate(120%)} }
.announce-fade { animation: 4.2s ease-in-out announce-fade }
.shimmer { background-size: 200% 100%; animation: 1.3s ease-in-out infinite shimmer-slide }
.cta-shine:after { transform: translate(-120%) }
.cta-shine:hover:after { animation: .7s cta-flash }
.tab-scroll { scrollbar-width: none }
.tab-scroll::-webkit-scrollbar { display: none }
::view-transition { pointer-events: none }
::view-transition-group(site-header) { z-index: 100; animation: none }
::view-transition-old(site-header) { display: none }
::view-transition-new(site-header) { animation: none }
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto }
  .announce-fade, .shimmer, .cta-shine:hover:after { animation: none !important }
  ::view-transition-group(*), ::view-transition-old(*), ::view-transition-new(*) { animation: none !important }
}
```

`--duration-enter` / `--duration-exit` / `--duration-move` are **declared and unused** by the Featured path (Framer owns timing). APPLY may bind clip-path CSS to these tokens so watery stays on-brand. Do not invent `--liquid-500ms`.

### 4.2 JS exports to `rg` (names may be file-split; strings are stable)

| Export / string | Role |
| --- | --- |
| `FeaturedBoard` | Home Featured section |
| `Filter featured collection` | `aria-label` on `role="tablist"` |
| `featured-tab` | Motion `layoutId` on the gold rule |
| `springSoft` | Shared spring (tabs + tile `layout`) |
| `filterSlide` | Grid enter/exit variants |
| `AnimatedProductGrid` | `products` · `motionKey` · `direction` |
| `AnimatePresence` | `mode="wait"` around the grid; `mode="wait"` around “N pieces” |
| `useReducedMotion` | Framer hook (`motion/react`) |
| `fadeUp` | Tile / CollectionList item variants |
| `staggerContainer` | CollectionList only (`staggerChildren: 0.07`) |
| `tab-scroll` | Horizontal tab scroller, scrollbar hidden |
| `ProductGrid` | `<ul class="grid grid-cols-2 …">` |
| `coverSrc` / `coverSrcForColor` | Cover path helpers |
| `ColorSwatch` | Exists in chunk — **customer chips still empty** on live PDPs |
| `MaMark` | Tabular mã |
| `viewTransitionName: product-${ma}` | On `aspect-[3/4]` wrapper when `namedTransition` |

**Not present** in this chunk: `startViewTransition`, `aria-controls`, `tabpanel`, `goo`, `clip-path` on the grid.

### 4.3 FeaturedBoard (reconstructed from the minified chunk)

```js
// direction: +1 when moving right / later index, -1 when moving left
function b(next) {
  const cur = tabs.indexOf(selected);
  setDirection(tabs.indexOf(next) >= cur ? 1 : -1);
  setSelected(next);
}

// tab chrome
<motion.span
  layoutId={reduced ? undefined : "featured-tab"}
  className="absolute inset-x-0 bottom-0 h-px bg-gold"
  transition={springSoft}
/>

// grid
<AnimatedProductGrid products={filtered} motionKey={selected} direction={dir} />
```

`springSoft` and `filterSlide` live in module `42295`:

```js
const springSoft = { type: "spring", stiffness: 420, damping: 32, mass: 0.72 };
const easeOutExpoish = [0.22, 1, 0.36, 1]; // cubic-bezier

function filterSlide(reduced, dir /* +1 | -1 */) {
  if (reduced) {
    return {
      initial: { opacity: 1, x: 0 },
      animate: { opacity: 1, x: 0, transition: { duration: 0 } },
      exit: { opacity: 0, transition: { duration: 0 } },
    };
  }
  return {
    initial: { opacity: 0, x: 28 * dir },
    animate: { opacity: 1, x: 0, transition: { duration: 0.32, ease: easeOutExpoish } },
    exit: { opacity: 0, x: -22 * dir, transition: { duration: 0.22, ease: easeOutExpoish } },
  };
}
```

`fadeUp(reduced)`: hidden `{ opacity: 0, y: 20 }` → show via `springSoft`; exit `{ opacity: 0, y: 8, duration: 0.18 }`. Reduced: no offset.

`staggerContainer(reduced)`: `{ staggerChildren: 0.07, delayChildren: 0.04 }` or duration 0.

### 4.4 Two IAs (do not watery them into two inventories)

Home Featured is a **client filter**. Live labels + counts (sum = 10):

`All 10 · Tops 2 · Sets 1 · Accessories 5 · Jackets 1 · Hair 1`

Routes still exist: `/c/ao` (A01+A02), `/c/set` (S01), `/c/phu-kien` (P01–P05), `/c/ao-khoac` (K01), `/c/toc` (H01), `/c/quan` (**empty**, `site-header` only). APPLY: Tops filter = A01+A02; Accessories keeps Hold P02/P05; `/c/quan` does not gain a liquid splash of fake pants.

### 4.5 What already honors Reduce Motion

| Motion | Reduced behavior today |
| --- | --- |
| `layoutId: "featured-tab"` | **Off** (`undefined`) — rule teleports. Correct. |
| `filterSlide` | Duration 0. Correct. |
| Count `motion.span` | Duration 0. Correct. |
| `fadeUp` / `staggerContainer` | Offsets/stagger 0. Correct. |
| CSS shimmer / announce / cta / VT | `animation: none`. Correct. |
| Card `scale-[1.08]` / `-translate-y-1.5` | **Still runs** (`10` MOT-03). Out of this file’s *new* scope except: watery must not add a second hover zoom. |

---

## 5. Kelly Ying look — steal the rhythm, refuse the glass

`01` / `10` already locked the steal list. For watery, add:

| Kelly Ying / fashion cue | Steal? |
| --- | --- |
| Gold hairline under the active collection | **Yes** — it is already `h-px bg-gold`. Watery = that line **melts**, not a new pill. |
| Uppercase 11px tracking | **Yes** — do not goo-blur the type (Bebber: filter the **container** of blobs, not the labels). |
| Editorial crop, SKU on card | **Yes** — clip the **frame**, not the pixels of the JPEG (no displacement). |
| Cart · Checkout · $10 / $300+ | **No.** |
| Sleepwear / Kids / Cosmetics collections | **No.** Do not invent tabs so a wipe has more stops. |
| iOS-26 liquid glass over hero | **No.** Paper stays paper. |

Cloudflare blocked a fresh Kelly Ying fetch this pass. Do not invent collection names from memory. If a later agent can read the site, update `01` — do not scrape SKUs onto Sassy.

---

## 6. Reliability law (water must not lie)

Same ten laws as `10` §6, plus watery-specific:

1. **Hold remains a word** while the grid pours. Gold goo must not recolor the Hold badge into ink Available (`09` MOT-08; WCAG 1.4.1).
2. **Counts are math on the allowlist**, not a fade that “feels like more arrived.” All=10, Tops=2, Accessories=5 including both Holds.
3. **No second shimmer** during `filterSlide`. `.shimmer` is a **cover-load** sheen, not a filter spinner (`10` §12).
4. **`mode="wait"` is a reliability risk.** The buyer sees an empty gap between catalogs. Prefer overlapping pour (exit + enter together) so the set never blanks. If you keep `wait`, cut durations so **exit+enter ≤ 200ms** combined.
5. **Goo on type is a contrast failure.** 11px gold-deep counts (`text-gold-deep`) must stay crisp (WCAG 1.4.3 is the contrast clock; goo lowers effective contrast).
6. **Pointer events.** `::view-transition { pointer-events: none }` stays (`10` MOT-05). A clip-path overlay on the grid must not trap Message taps after the tween.
7. **Same data, every surface.** Home filter = `/c/*` = PDP = admin header (`09` NAV-09).

---

## 7. Watery tab (the gold meniscus)

### 7.1 What is already correct

Motion’s shared `layoutId="featured-tab"` **is** the right architecture: one gold rule, FLIP’d between tabs, spring `420 / 32 / 0.72`, skipped when `useReducedMotion()` ([Motion: *when a new component is added with a matching layoutId, it animates out from the old*](https://www.framer.com/motion/layout-animations/)). Do **not** replace it with `getBoundingClientRect` + `left` animation (layout thrash — Lewis). Do **not** replace it with CSS Anchor glass.

### 7.2 Why it does not feel wet yet

A 1px `scale-x` / position FLIP travels in a **straight line** (Motion default). Water has:

- **Stretch** on the travel axis (meniscus pulled toward the next label).
- **Overshoot** (spring mass already 0.72 — slightly wet; do not raise mass so far the rule wobbles three times).
- **A film**, not a bar: optional 30% gold trail that dies in ≤150ms.

WWDC23 flags **sustained oscillation** as a comfort risk ([vision and motion](https://developer.apple.com/videos/play/wwdc2023/10078/)). One overshoot is boutique. A bouncing blob is a toy.

### 7.3 APPLY recipe (keep `h-px bg-gold`)

Keep the live class string:

`absolute inset-x-0 bottom-0 h-px bg-gold`

Then, **only** when `prefers-reduced-motion: no-preference` / `!useReducedMotion()`:

1. **Stretch (preferred, no new assets).** On the `motion.span` with `layoutId="featured-tab"`, add a layout-aware scale: during travel, `scaleX` 1 → ~1.15 → 1 (or Motion `layout` distortion + a child `layout` counter-scale — [Motion “content stretches” FAQ](https://www.framer.com/motion/layout-animations/)). The rule should look **pulled**, then flush under the new label. Do not thicken to `h-1` / `h-2` (that is a pill; look lock is a hairline).
2. **Trail (optional).** A second span, `bg-gold/30`, `layoutId="featured-tab-trail"`, `transition: { ...springSoft, delay: 0.04 }`, opacity 0 after settle. Must not steal `featured-tab` (Motion: two live elements with the same id crossfade — we want **one** selected rule).
3. **Goo (optional, last).** Hidden SVG:

```svg
<svg aria-hidden="true" width="0" height="0" class="absolute">
  <filter id="ky-gold-goo" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur" />
    <feColorMatrix in="blur" type="matrix"
      values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -7" result="goo" />
    <feComposite in="SourceGraphic" in2="goo" operator="atop" />
  </filter>
</svg>
```

Matrix `18 -7` is Bebber’s published goo ([CSS-Tricks](https://css-tricks.com/gooey-effect/)). Apply `filter: url(#ky-gold-goo)` to a **wrapper that contains only the gold rule + optional trail**, not the `tablist`. `stdDeviation` 6 is boutique; 10+ will bloom into the labels. `@supports` + Reduce Motion = `filter: none`. If Safari-on-DOM fails (Bebber), the hairline remains.

4. **Do not** put `filter: url(#ky-gold-goo)` on `.tab-scroll` or the buttons. Bebber: *the filter should be applied to the container of the blobs*; bleeding area required or edges artifact.

### 7.4 APG (still required — watery does not replace it)

Live buttons have `role="tab"` and `aria-selected`. Missing: `aria-controls`, `role="tabpanel"` on the grid, arrow keys, Home/End ([APG Tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/)).

Automatic activation is OK **because the ten are already in memory** (APG: auto-activate when panels have no noticeable latency). Manual activation (Space/Enter) if you cannot keep the pour ≤200ms.

Keyboard: Left/Right in this horizontal list; do **not** steal Up/Down (APG: leave those for page scroll).

`tab-scroll` hides the scrollbar. On phone, selected tab must still **scroll into view** (`scrollIntoView({ inline: "nearest" })`) when arrows or tap land off-screen. That is orientation, not decoration.

### 7.5 Selected style (non-motion)

Keep: selected `text-ink` + count `text-gold-deep`; idle `text-muted hover:text-ink` + count `text-muted/80`; `transition-colors duration-300`; `text-[11px] uppercase tracking-[0.18em]`. Watery is the **rule**, not a weight/color party.

---

## 8. Watery slide (the grid pour)

### 8.1 What is already correct

- Direction is **honest**: later tab → `dir = +1` → enter from `x: 28`, exit to `x: -22` (and the reverse). That is NN/G’s spatial metaphor (Amtrak-style process slide — [NN/G](https://www.nngroup.com/articles/animation-purpose-ux/)).
- `useReducedMotion()` already zeros `filterSlide`.
- Wrapper `overflow-hidden` (`mt-8 overflow-hidden`) is the right clip parent.
- `motionKey: selected` remounts the grid per tab — necessary for `AnimatePresence`.

### 8.2 What feels dry / slow

1. **`mode="wait"`** empties the grid, then fills it. On a 10-SKU lookbook that reads as “the shop disappeared.” Chrome’s VT filter demo: items that remain **move**, items that leave **fade**, items that enter **fade** — they do not blank ([Chrome View Transitions](https://developer.chrome.com/docs/web-platform/view-transitions/)). Featured is a **filter**, not a new route. Prefer `mode="sync"` / `popLayout` (Motion) so exit and enter overlap, **or** keep `wait` but cut to **80ms exit + 120ms enter**.
2. **`x: 28` / `-22` without clip** looks like a second page. Fashion wants a **wipe**: `clip-path: inset(0 100% 0 0)` → `inset(0)` in the travel direction ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/clip-path); redBus used `inset(45% 20% 45% 20%)` → open for **gallery reveal**, not tabbing — steal the *clip*, not the 45% letterbox).
3. **Tile `fadeUp` + `staggerChildren: 0.07` on CollectionList** is a **home mosaic** job. Do **not** stagger Featured tiles on every tab (10 × 70ms = 700ms of leftover motion). `ProductGrid` already `layout` + `fadeUp` each `li` — on filter change that is a second animation stacked on `filterSlide`. APPLY: Featured filter path should **not** stagger; keep `layout` so remaining tiles (All → Tops leaves A01/A02 in place) can FLIP if you switch off `wait` and filter in-place.

### 8.3 Two legal implementations (pick one; do not ship both)

**A — Pour the wrapper (smallest diff).** Keep `AnimatedProductGrid` + `filterSlide`. Change variants:

```js
function filterSlide(reduced, dir) {
  if (reduced) return /* duration 0, x:0, clip inset(0) */;
  const from = dir > 0 ? "inset(0 0 0 28%)" : "inset(0 28% 0 0)";
  const exitTo = dir > 0 ? "inset(0 28% 0 0)" : "inset(0 0 0 28%)";
  return {
    initial: { opacity: 0.96, clipPath: from, x: 8 * dir },
    animate: {
      opacity: 1, clipPath: "inset(0)", x: 0,
      transition: { duration: 0.18, ease: [0.22, 1, 0.36, 1] },
    },
    exit: {
      opacity: 0.96, clipPath: exitTo, x: -6 * dir,
      transition: { duration: 0.12, ease: [0.22, 1, 0.36, 1] },
    },
  };
}
```

Keep the **export name** `filterSlide`. Keep the ease token `[.22,1,.36,1]`. Bind CSS fallback to `--duration-enter` / `--duration-exit` if you also drive clip from a class. Reduced: `clipPath: inset(0)`, no x.

**B — Filter in place (more honest, more work).** Drop `motionKey` remount. Filter the array; let each `motion.li layout` + `layoutId={`tile-${ma}`}` FLIP. Leavers fade (`fadeUp.exit`). Enterers fade. No wholesale x-slide. This matches Chrome’s “cards reorder when filtered.” Watery here is **only** the gold meniscus. Prefer B if `wait` cannot be cut.

Do **not** do A **and** B (double motion).

### 8.4 Optional wave on the clip edge

Afif’s `clip-path: shape()` ooze ([CSS Tip](https://css-tip.com/sliding-liquid/)) needs **matching granularity + shape id** at 0% and 100% or the interpolation breaks. If used, one shallow wave on the **leading edge** of the inset, amplitude ≤ 8px, duration ≤ 180ms, `@supports (clip-path: shape(…))`, Reduce Motion off. Full-viewport `html:after` 6s reveal = **refuse**.

### 8.5 Empty kinds

`/c/quan` and any zero-count tab: copy only (“Chưa có quần trên lookbook” / “No pants listed”). No liquid splash, no shimmer tiles, no Kelly Ying bottoms scrape (`10` §7).

---

## 9. Home → PDP (slide vs morph)

Watery tabs are **same-document**. Home → `/m/A01` is **navigation**. `10` FIX 3 still stands: put `view-transition-name: product-A01` on the **A01 hero** (live crawl: hero has **no** name; related rail names `product-A02`). 

Do **not** add a watery clip-path to `::view-transition-old(root)` as a page-turn. Chrome’s default crossfade + a **named** product morph is the boutique metaphor (thumbnail continues). A liquid root wipe feels like a new site (NN/G overlay-vs-page warning).

If you customize VT:

```css
@keyframes ky-pour-in {
  from { clip-path: inset(0 0 0 12%); opacity: 0.9; }
  to   { clip-path: inset(0); opacity: 1; }
}
@media (prefers-reduced-motion: no-preference) {
  ::view-transition-new(product-A01) { animation: 0.28s ky-pour-in both; }
}
```

Only after names match. Keep `::view-transition { pointer-events: none }`. Skip when `matchMedia('(prefers-reduced-motion: reduce)')` — do not call `startViewTransition` (`10`; [Chrome same-document + reduced motion](https://developer.chrome.com/docs/web-platform/view-transitions/same-document#handling_reduced_motion_preferences); [SCR40](https://www.w3.org/WAI/WCAG22/Techniques/client-side-script/SCR40) / [C39](https://www.w3.org/WAI/WCAG22/Techniques/css/C39)).

No `@view-transition { navigation: auto }` in the downloaded CSS chunk this crawl (`10` already noted). Add it **after** heroes share names.

---

## 10. Color → gallery (do not watery-invent chips)

Live customer `colors: []`. Empty = **no row** (`10` §8). When admin later stores recorded ids (`05` §3.2), chips are **text**; image change is a **150–250ms opacity** crossfade, not a liquid wipe (wipes feel like a **different piece**). Never borrow `/products/A02/cover.jpg` on A01. `coverSrcForColor` already exists in the chunk — bind it; do not add a second helper.

---

## 11. Reduced-motion + vestibular

WCAG clocks (do not collapse — [Motion Spec](https://motionspec.dev/blog/wcag-2-3-3-animation-from-interactions); `10` §3.3):

| Criterion | Watery impact |
| --- | --- |
| [2.2.2](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) Level A | Infinite `.shimmer` is still the loop. Watery must not add a second infinite wave. |
| [2.3.1](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html) Level A | Do not strobe the gold rule. |
| [2.3.3](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) Level AAA | Tab stretch, clip pour, goo bloom = interaction animation. Sufficient: C39 + JS `useReducedMotion` (already). |
| [1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) | Selected tab is ink + rule + `aria-selected`, not gold alone. |

MDN: `prefers-reduced-motion: reduce` means **remove, reduce, or replace** motion; scaling/panning large objects are vestibular triggers ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)). A grid `translateX(28px)` plus clip is exactly that class — already zeroed. A goo bloom on the hairline must zero too.

Apple: fade, don’t zoom. Watery reduced fallback = **instant selected rule** + **instant grid** + count text swap. The meniscus and pour are non-essential.

---

## 12. Timing budget

| Interaction | Budget | Live 2026-09-09 | APPLY |
| --- | --- | --- | --- |
| Gold rule starts moving | ≤100ms | Spring starts on render — OK | Keep `layoutId` |
| Gold rule settles | ≤300ms | `stiffness 420` — typically in budget | One overshoot max |
| Count “N pieces” | 180ms | `duration: 0.18` | Keep or cut to 120ms |
| Grid pour (total perceived) | ≤200ms (`10`) | **~540ms** (`wait` 220+320) | Overlap or cut to 120+80 |
| Clip-path wave (optional) | ≤180ms | n/a | Same clock as pour |
| Goo bloom | ≤200ms | n/a | No loop |
| Home → PDP VT | ≤300ms | Names mismatch | `10` FIX 3 first |
| Shimmer | — | 1.3s **infinite** | `10` FIX 1; not a tab tool |
| CollectionList stagger | 70ms × n | Home mosaic only | Do not reuse on Featured filter |

`--duration-move: .4s` is **longer** than the Featured budget. Do not blindly apply it to `filterSlide`.

---

## 13. Performance

Bebber: goo is “light in size” and **expensive on large areas**. Tigt’s 2015 comment on that article: a phone became a “shuddering shamble.” Tokopedia measured scroll JS at 50% CPU vs 2% after moving to CSS scroll-driven timelines ([Chrome SDA](https://developer.chrome.com/blog/css-ui-ecommerce-sda)). Lessons:

- Goo wrapper = **hairline height** (a few px + blur padding), not the 58vh hero, not the 10-card grid.
- Animate `transform`, `opacity`, `clip-path` (simple `inset()`). Do not animate `width` / `top` / `filter` on the grid ([Lewis](https://aerotwist.com/blog/flip-your-animations/); CSS-Tricks FLIP).
- Complex `shape()` paths can fall off the compositor (treat as progressive enhancement).
- `::view-transition { pointer-events: none }` stays.
- Do not run `shimmer-slide` **and** a pour **and** tile `fadeUp` together.
- ISR `x-nextjs-stale-time: 300` is a cache clock. Filter from the **payload already on the page**.

---

## 14. APPLY — [sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)

**Owner:** Origin `sassy-closet-shop` (not this kit).  
**Look:** Kelly Ying hairline + paper. **Job:** watery **tab + slide** on the hooks below.  
**Mã:** allowlist only. **No** Square Save. **No** FB Send. **No** cart.  
**Do not edit** `excel-kit/` or intake `sassy-closet/`.

Human-readable ticks. **Paste block is §19.**

### 14.0 Do not touch (lock — tick first)

- [ ] Cormorant Garamond + Be Vietnam Pro.
- [ ] Paper / ink / gold / blush; `ma-mark`; 11px tracking; gold **`h-px`** language (not a fat pill).
- [ ] Keyframes `announce-fade`, `shimmer-slide`, `cta-flash` and classes `announce-fade`, `shimmer`, `cta-shine` **remain**.
- [ ] Exports / strings `FeaturedBoard`, `featured-tab`, `filterSlide`, `springSoft`, `AnimatedProductGrid` **remain** (you may change **bodies**).
- [ ] Featured chips All / Tops / Sets / Accessories / Jackets / Hair + counts that sum to **10**.
- [ ] Livestream rail + Page `61594312648057`.
- [ ] Message-first CTAs; footer **Zelle** word; no personal name.
- [ ] Hold on **P02, P05** (no published `$`).
- [ ] `/admin` out of the main nav.
- [ ] Intake host unchanged.

### 14.1 CSS hooks (globals / motion stylesheet)

`rg -n "announce-fade|shimmer-slide|cta-flash|--duration-enter|--gold|tab-scroll|prefers-reduced-motion"`

- [ ] Keep `:root` tokens in §4.1. Do not invent a second palette.
- [ ] Optional: `--duration-enter` / `--duration-exit` drive **clip** only if you add a CSS class; do not set them to 0.7s.
- [ ] New keyframes, if any, namespaced `ky-pour-in` / `ky-meniscus` — do not reuse `shimmer-slide` for tabs.
- [ ] `#ky-gold-goo` (if shipped) is `aria-hidden` SVG; `filter` only on the gold-rule wrapper.
- [ ] `@media (prefers-reduced-motion: reduce)` also sets `filter: none` on that wrapper and `clip-path: none` on the grid.
- [ ] Keep `::view-transition { pointer-events: none }` and frozen `site-header` rules.

### 14.2 JS hooks — tab (`FeaturedBoard`)

`rg -n "featured-tab|Filter featured collection|springSoft|tab-scroll"`

- [ ] Keep `layoutId={!reduced && "featured-tab"}` on the gold `h-px`.
- [ ] Keep `transition={springSoft}` (`stiffness: 420`, `damping: 32`, `mass: 0.72`) unless you **only** add a `scaleX` stretch; do not switch to `duration: 0.7`.
- [ ] Optional trail uses a **different** `layoutId` (`featured-tab-trail`).
- [ ] Click `b()` still sets `direction` from index compare, then selected type (`"all"` or a `types[]` key).
- [ ] APG: `aria-controls` → grid id; grid `role="tabpanel"` + `aria-labelledby`; Left/Right (+ Home/End); one selected.
- [ ] `tab-scroll`: `scrollIntoView({ inline: "nearest" })` for the selected tab on activate.
- [ ] Counts stay math: Tops = A01+A02; Accessories = P01–P05 including Holds.

### 14.3 JS hooks — slide (`filterSlide` / `AnimatedProductGrid`)

`rg -n "filterSlide|AnimatedProductGrid|motionKey|mode:\\\"wait\\\""`

- [ ] Keep the function name `filterSlide(reduced, direction)`.
- [ ] Keep ease `[0.22, 1, 0.36, 1]` or map it to a named `kyEase`.
- [ ] Cut perceived time to **≤200ms**. Either leave `mode="wait"` and use ~120ms enter / ~80ms exit, **or** overlap (`sync` / `popLayout`) and keep ~180ms enter.
- [ ] Add directional `clipPath: inset(...)` (recipe A) **or** in-place `layoutId={`tile-${ma}`}` (recipe B). Not both.
- [ ] Reduced: duration 0, `x: 0`, `clipPath: inset(0)`.
- [ ] Do not stagger Featured tiles (`staggerContainer` stays on `CollectionList` only).
- [ ] No second `.shimmer` while filtering.
- [ ] Empty filter / `/c/quan`: copy, not a minted tile.

### 14.4 Do not watery these

- [ ] Product covers / `.shimmer` / PDP hero — no goo, no displacement, no `shape()` ooze on JPEGs.
- [ ] `cta-shine` / `cta-flash` — stay a shine, not a blob button ([Framer Bubble Blob](https://www.framer.com/marketplace/components/bubble-blob-button/) is a toy CTA; refuse).
- [ ] Shop-tools dialog (`role="dialog"` in `25mb9l6f4ual1.js`) — not a liquid sheet.
- [ ] Intake `PhotoLightbox` / rose sheets — do not import.

### 14.5 Reliability / commerce

- [ ] Mid-pour, Hold is still the word Hold; P02/P05 have no `$`.
- [ ] Message {MA} works during and after the pour.
- [ ] No cart, bag, Shop now, flying-to-cart, liquid-into-bag.
- [ ] No countdown, no fake stock pulse (`07` §11).
- [ ] Do not print Kelly Ying **$10 / $300+** or `V###`.

### 14.6 Verify (Origin, after watery work)

Desktop (hover) + phone (no hover) + OS Reduce Motion + keyboard:

1. Home Featured: All → Tops → Accessories → All. Counts 10 / 2 / 5 / 10. Gold hairline **stretches** (motion on) or **jumps** (reduced). P02 still Hold.
2. Direction: All → Hair pours one way; Hair → All the other. No random axis.
3. Perceived filter time ≤200ms (phone + mid-tier). No empty-white flash if you left `wait` without cutting durations.
4. Keyboard: Tab into the list, arrows move + activate (or Space/Enter if manual). Focus visible. Up/Down still scroll the page.
5. `/c/ao` still two tops, $25 / $22. `/c/quan` still empty.
6. `/m/A01` cover visible; Message works. Do not regress `10` hero-name gap if you also ship that PR.
7. Reduce Motion: no stretch, no pour, no goo, no shimmer slide, no 1.08 zoom (`10`). Tabs + Message still work.
8. View-source: no `e.tb.cn`, no ¥, no `A03`, no `V984`.

---

## 15. Anti-patterns (quick refuse list)

1. Minting `A03` / `Q01` so a wipe “has somewhere to go.”  
2. Fat glass pill / iOS liquid-glass under Featured labels.  
3. `filter: url(#goo)` on `tablist`, cards, or covers.  
4. `feDisplacementMap` / chromatic aberration on product photos.  
5. Full-page `html:after` 6s `shape()` ooze (Afif demo is a **tip**, not a shop).  
6. Keeping `mode="wait"` at 0.32 + 0.22 (540ms blank).  
7. Staggering 10 Featured tiles on every tab.  
8. CSS Anchor glass pointer (support + look).  
9. WebGL cloth, cursor metaballs, auto-play lookbook video.  
10. Cart-bag pour “to feel like a real shop.”  
11. Restyling to intake rose / Allura.  
12. Copying Kelly Ying `V984` or `$10 / $300+`.  
13. Using `--duration-move: .4s` as the tab clock.  
14. Translating `A01` → `AO001` in a caption that rides the pour.  
15. Shipping A **and** B (wrapper pour + in-place FLIP).

---

## 16. Acceptance (sell-test watery)

A reviewer can fail the page against this list without a redesign argument:

- [ ] Every mã that moves is on the allowlist and was **already assigned**.  
- [ ] Featured filter and `/c/*` show the same sets; empty stays empty.  
- [ ] P02 / P05 never display a dollar, including mid-pour.  
- [ ] Gold rule is still `h-px bg-gold` (stretch/trail/goo optional); not a new pill system.  
- [ ] `featured-tab`, `filterSlide`, `springSoft`, `FeaturedBoard` still exist as names.  
- [ ] Perceived filter ≤200ms with motion on; instant with Reduce Motion.  
- [ ] No goo/displacement on photography.  
- [ ] APG tablist keyboard works.  
- [ ] Message CTA never blocked by a clip overlay.  
- [ ] Fonts, gold, chips, no-cart CTA still match `01` / `07` / `10` locks.

---

## 17. Sources

### 17.1 Shop law and as-built

- `README.md` — Square SoT; bots draft; Facebook inbox.  
- `excel-kit/DESIGN_NOTES.md`, `excel-kit/schema.py` — mã law; ASK STOCK.  
- `excel-kit/docs/SELL_CATALOG_CONTRACT.md` + sample (PR #18) — allowlist, prices, Hold P02/P05.  
- Sisters `01`–`12` (PRs #19–#31) — look lock, PDP nouns, MOT checklist, general motion (`10`).  
- Slack `#shop-decisions` (2026-09-04):  
  - [Channel law](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788541753903809)  
  - [Track stock ON proposal](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788553328521899)  
  - [Boss yes](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788553474026779)  
  - [Square LIVE](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788556083454949)  
  - [Soft-launch prep, draft only](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788557030839509)  
- Live host 2026-09-09: https://sassy-closet-shop.vercel.app — CSS `34vl_zddoo4ws.css`; JS `3_93acjqq2t4q.js` (module `42295`).  
- Kelly Ying Boutique — <https://www.kellyyingboutique.net/> (Cloudflare-blocked this pass; prior read in `01` / `10`).

### 17.2 Motion / liquid technique

- Nielsen Norman Group, *The Role of Animation and Motion in UX* — <https://www.nngroup.com/articles/animation-purpose-ux/>  
- Nielsen Norman Group, *Animation for Attention and Comprehension* — <https://www.nngroup.com/articles/animation-usability/>  
- Nielsen Norman Group, *Microinteractions in User Experience* — <https://www.nngroup.com/articles/microinteractions/>  
- Jakob Nielsen, *Response Time Limits* — <https://www.nngroup.com/articles/response-times-3-important-limits/>  
- Apple HIG, *Motion* — <https://developer.apple.com/design/human-interface-guidelines/motion>  
- Apple, Reduced Motion evaluation criteria — <https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria/>  
- WWDC23, *Design considerations for vision and motion* — <https://developer.apple.com/videos/play/wwdc2023/10078/>  
- Paul Lewis, *FLIP Your Animations* — <https://aerotwist.com/blog/flip-your-animations/>  
- Josh Comeau / CSS-Tricks, *Animating Layouts with the FLIP Technique* — <https://css-tricks.com/animating-layouts-with-the-flip-technique/>  
- Motion (Framer), *Layout animations* / `layoutId` — <https://www.framer.com/motion/layout-animations/>  
- Lucas Bebber, *The Gooey Effect* (CSS-Tricks) — <https://css-tricks.com/gooey-effect/>  
- Animata, *Gooey Tabs* (filter on tab **blobs**, not copy) — <https://animata.design/docs/tabs/gooey-tabs>  
- Temani Afif, *A Sliding “Liquid Oozing” Reveal* (`shape()`, 2026-04-02) — <https://css-tip.com/sliding-liquid/>  
- MDN, `clip-path` — <https://developer.mozilla.org/en-US/docs/Web/CSS/clip-path>  
- MDN, `prefers-reduced-motion` — <https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion>  
- Chrome, *Smooth transitions with the View Transition API* — <https://developer.chrome.com/docs/web-platform/view-transitions/>  
- Chrome, same-document VT + reduced motion — <https://developer.chrome.com/docs/web-platform/view-transitions/same-document#handling_reduced_motion_preferences>  
- Chrome, *Scroll-driven animations case studies* (Tokopedia / redBus `clip-path`) — <https://developer.chrome.com/blog/css-ui-ecommerce-sda>  
- CSS View Transitions Module Level 1 — <https://drafts.csswg.org/css-view-transitions-1/>  

### 17.3 Accessibility

- WAI-ARIA APG, Tabs — <https://www.w3.org/WAI/ARIA/apg/patterns/tabs/>  
- W3C, WCAG 2.2 SC 2.2.2 Pause, Stop, Hide — <https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html>  
- W3C, WCAG 2.2 SC 2.3.1 Three Flashes — <https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html>  
- W3C, WCAG 2.2 SC 2.3.3 Animation from Interactions — <https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html>  
- W3C technique C39 — <https://www.w3.org/WAI/WCAG22/Techniques/css/C39>  
- W3C, WCAG 2.2 SC 1.4.1 Use of Color — <https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html>  
- Motion Spec, *2.3.3 is AAA; 2.2.2 is the Level A loop* — <https://motionspec.dev/blog/wcag-2-3-3-animation-from-interactions>

### 17.4 Weaker / vendor (directional only)

- FreeFrontend liquid-glass / anchored glass tab — OS chrome, not this look.  
- Framer Marketplace “Bubble Blob Button” — toy CTA; refuse on Message.  
- DEV.to liquid nav (dive/travel/resurface) — fun; too much travel for 11px chips.  
- Theme posts that claim “+% conversion from microinteractions” without a method are **not** shop law.

---

## 18. Open questions (do not answer by inventing)

1. Will Featured stay a client filter on `/`, or should chips push `/c/*` (`06` wants unique titles either way)? Watery pour is same-document either way; a route change needs VT names, not `filterSlide`.  
2. Recipe A (wrapper clip) vs B (in-place tile FLIP) — Origin picks one. This file does not require goo.  
3. After Granola access: did a meeting already ban springs on the hairline? Until then, live `springSoft` stays the token.  
4. Livestream **days** still unlocked (`01`). Motion cannot invent Sunday/Monday.  
5. Kelly Ying home was Cloudflare-blocked this pass — do not invent new steal cues.

---

## 19. PASTE INTO ORIGIN AGENT (do not paraphrase)

Copy everything between the markers into a Cloud Agent on the **Origin `sassy-closet-shop` repo** (the git behind https://sassy-closet-shop.vercel.app). Not this kit. Not intake `sassy-closet/`. Not `excel-kit/`.

```text
===== BEGIN ORIGIN PASTE — watery tab + slide (LEARN 13) =====

You are editing Origin sassy-closet-shop. Ship WATERY / LIQUID motion on the
EXISTING Featured tab + grid slide. Do not restyle. Do not invent mã.
Do not add iOS liquid glass. Do not touch intake or Excel.

HOST: https://sassy-closet-shop.vercel.app
LAW: Facebook inbox is the store. No cart. No Square Save. No FB Post/Send.
ALLOWLIST ONLY: A01 S01 P01 P02 P03 P04 P05 K01 H01 A02
HOLD (no $): P02 P05
PRICES: A01 $25 · S01 $28 · P01 $5 · P03 $18 · P04 $13 · K01 $37 · H01 $8 · A02 $22
LOOK LOCK: Cormorant Garamond + Be Vietnam Pro; paper / ink / gold / blush;
ma-mark; 11px uppercase tracking; gold HAIRLINE (h-px bg-gold) — not a fat pill;
announce-fade; shimmer + shimmer-slide; cta-shine + cta-flash.
Do NOT switch to intake rose / Allura / Nunito. Do NOT add Shopify cart.
Do NOT copy Kelly Ying V984 or “$10 shipping on $300+”.
Do NOT apply SVG goo / displacement / shape() ooze to product photos.

FIND FILES (rg — names may differ; match these strings, then edit those files):

  rg -n "featured-tab|Filter featured collection|springSoft|filterSlide"
  rg -n "AnimatedProductGrid|FeaturedBoard|tab-scroll"
  rg -n "announce-fade|shimmer-slide|--duration-enter|--gold:"
  rg -n "useReducedMotion|layoutId"

Expected (live 2026-09-09 chunk 3_93acjqq2t4q.js + 34vl_zddoo4ws.css):
  springSoft = { type: "spring", stiffness: 420, damping: 32, mass: 0.72 }
  filterSlide(reduced, dir):
    motion on:  enter x:28*dir 0.32s ease [.22,1,.36,1]
                exit  x:-22*dir 0.22s
    reduced:    duration 0
  FeaturedBoard click b(next): dir = index(next) >= index(cur) ? 1 : -1
  Gold rule: layoutId="featured-tab" (undefined when reduced)
  AnimatedProductGrid: AnimatePresence mode="wait" + motionKey=selected
  :root --paper --ink --gold --gold-deep --blush --duration-enter:.21s
        --duration-exit:.15s --duration-move:.4s

If a file is missing, create the smallest new file next to FeaturedBoard —
do not invent a second design system.

────────────────────────────────────────
FIX 1 — Gold meniscus (keep h-px, make it wet)
────────────────────────────────────────
KEEP:
  className="absolute inset-x-0 bottom-0 h-px bg-gold"
  layoutId={!reduced && "featured-tab"}
  transition={springSoft}

DO:
  1. While the rule travels (motion on only), stretch it: scaleX ~1 → 1.15 → 1
     so it reads as a pulled gold film, then flush under the new label.
     One overshoot max. No looping bounce (WWDC23 oscillation).
  2. OPTIONAL trail: second span layoutId="featured-tab-trail"
     class "absolute inset-x-0 bottom-0 h-px bg-gold/30"
     same spring + delay 0.04; opacity 0 after settle.
     NEVER reuse layoutId "featured-tab" on two visible nodes.
  3. OPTIONAL goo on a WRAPPER THAT CONTAINS ONLY the rule (+ trail):
     SVG filter id="ky-gold-goo" (Bebber):
       feGaussianBlur stdDeviation="6"
       feColorMatrix alpha row 18 -7
       feComposite operator="atop"
     filter: url(#ky-gold-goo) behind @media (prefers-reduced-motion: no-preference)
     and !useReducedMotion(). NEVER put the filter on tablist, buttons, or images.
     If Safari skips DOM filters, hairline still works.
  4. Do NOT change the rule to h-1 / rounded-full / backdrop-blur / glass.

────────────────────────────────────────
FIX 2 — APG tabs (watery does not replace a11y)
────────────────────────────────────────
Live: role="tablist" aria-label="Filter featured collection"
      buttons role="tab" aria-selected — NO aria-controls, NO tabpanel.

DO:
  1. id on the grid wrapper; each tab aria-controls that id.
  2. Grid / AnimatedProductGrid wrapper: role="tabpanel" aria-labelledby=active tab.
  3. Left/Right (+ Home/End) move focus; auto-activate (ten SKUs are in memory)
     OR Space/Enter if you cannot keep pour ≤200ms.
  4. Do not steal Up/Down (page scroll).
  5. tab-scroll: scrollIntoView({ inline: "nearest", block: "nearest" })
     when the selected chip is off-screen.
  6. Counts stay: All 10, Tops 2 (A01+A02), Sets 1, Accessories 5
     (P01–P05, P02+P05 Hold), Jackets 1, Hair 1. No new chips.

────────────────────────────────────────
FIX 3 — Grid pour (filterSlide body; keep the name)
────────────────────────────────────────
PROBLEM: mode="wait" + 0.22 exit + 0.32 enter = ~540ms blank. Too long
(NN/G 0.1 / 1s; LEARN 10 budget ≤200ms).

PICK ONE:

  A) Keep AnimatedProductGrid remount (motionKey=selected).
     Change filterSlide (keep name + ease [.22,1,.36,1] + dir from b()):
       motion on, total perceived ≤200ms:
         enter: clipPath inset from the incoming side (28%) + x: 8*dir
                → inset(0) + x:0 in ~180ms (or 120ms if you keep wait)
         exit:  clipPath toward the outgoing side + x: -6*dir in ~80–120ms
       reduced: clipPath inset(0), x:0, duration 0
     Prefer overlapping (mode="sync" or popLayout) so the grid never blanks.
     If you keep mode="wait", you MUST cut the two durations so sum ≤200ms.

  B) Stop remounting. Filter the array in place. Each tile:
       layout + layoutId={`tile-${ma}`}
       leavers fade (fadeUp.exit); enterers fade.
     No wrapper translateX. Watery is then ONLY the gold meniscus.
     Do not also run filterSlide x/clip.

FORBIDDEN: A+B together. Forbidden: staggerContainer on Featured tiles.
CollectionList stagger (0.07) stays on the home mosaic only.

Empty /c/quan and any 0-count tab: copy only — "Chưa có quần trên lookbook"
/ "No pants listed". No shimmer skeletons. No Q01.

────────────────────────────────────────
FIX 4 — CSS reduce + no photo distortion
────────────────────────────────────────
KEEP existing reduce kills for announce-fade / shimmer / cta-shine / VT.

ADD:
  @media (prefers-reduced-motion: reduce) {
    .ky-gold-goo, [style*="ky-gold-goo"], .featured-tab-film {
      filter: none !important;
    }
    .featured-pour, [data-filter-slide] {
      clip-path: none !important;
      transform: none !important;
    }
  }

NEVER:
  filter:url(#goo) on img, .shimmer, hero, or Message CTA
  feDisplacementMap on covers
  html:after full-page shape() liquid (CSS Tip 6s demo)
  --duration-move:.4s as the tab clock
  cart / bag-fly / liquid-into-bag

Optional VT: only AFTER product-{THIS mã} is on the PDP hero (LEARN 10).
Do not add a watery root wipe on ::view-transition-old(root).
Keep ::view-transition { pointer-events: none }

────────────────────────────────────────
HARD STOPS
────────────────────────────────────────
- No new mã. No Q01 / A03 / AO001 on the lookbook.
- No cart, Shop now, flying-to-cart.
- No warehouse ticker, no fake countdown.
- Do not rewrite P02/P05 to a dollar. No e.tb.cn, no ¥, no customer names.
- Do not restyle fonts or gold “to look cleaner.”
- Do not touch https://sassy-closet.vercel.app (intake).
- Do not edit excel-kit or Official xlsx.
- Do not Production-promote without Boss. Open a Preview.

────────────────────────────────────────
VERIFY (you click these; do not skip)
────────────────────────────────────────
Desktop + phone + OS Reduce Motion + keyboard:

1. /  All→Tops→Accessories→All. Counts 10 / 2 / 5 / 10.
   Gold hairline stretches (motion) or jumps (reduced).
   P02+P05 Hold · Inbox for price. Arrows move tabs.
2. /  All→Hair vs Hair→All pour opposite directions.
   Perceived filter ≤200ms. No long white blank.
3. /c/ao = A01 $25 + A02 $22. /c/quan empty.
4. /m/A01 cover visible. Message A01 still opens
   facebook.com/profile.php?id=61594312648057
5. Reduce Motion: no stretch, no pour, no goo, no shimmer,
   no 1.08 zoom. Tabs + Message still work.
6. View-source / network: no e.tb.cn, no ¥, no A03, no V984.
7. Photos never go through #ky-gold-goo.

Commit on an Origin cursor/* branch. Preview URL in the PR. Do not merge.

===== END ORIGIN PASTE =====
```

Mini Boss: copy the block above as the **entire** Origin prompt. Do not add “also make it more premium” or “add liquid glass.” The meniscus + pour *are* the watery pass. `10`’s five reliability fixes still apply if they are not on `main` yet — do not regress them.

End of 13.
