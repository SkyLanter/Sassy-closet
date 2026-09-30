# 20 — Visual FX: layoutId, shared element, spring pours

**Learn track:** Ultra burn (Fast OFF). Physics + Motion APIs + live as-built + Origin APPLY.  
**Shop:** Sassy Closet — Facebook inbox is the store; Square Free is on-hand truth; sell-test lookbook is Origin-owned.  
**Live APPLY target:** [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)  
**Audience:** Mini Boss / Origin shop implementer who will edit **`FeaturedBoard` watery tabs + gallery**.  
**Date researched / crawled:** 2026-09-09 (same host, same chunks as `13`).  
**This file does not assign stock, mint a mã, Save in Square, post to Facebook, restyle the boutique, or touch Excel / intake.**

Sister `10` is **general** motion law. Sister `13` is the **watery material** (meniscus + pour metaphor, goo/clip catalog). This note is the **engine**: Framer Motion / Motion One `layoutId`, shared-element matching, spring constants, `AnimatePresence` modes, and why the live Featured path still feels like a page flip. Mini Boss pastes **§19** into the Origin agent. Do not paraphrase §19 into “add liquid glass” or “rewrite it in Motion One.”

---

## 0. How to read this document

This is a **learn-track** note, not a rebuild brief and not permission to fork Origin shop code from this kit repo.

- **Cite, don’t invent.** Shop-law claims point at a file, Slack permalink, sister learn-track, or the live host. Industry claims point at Motion docs (`motion.dev`), Paul Lewis FLIP, NN/G, W3C WCAG 2.2, WAI-ARIA APG, MDN, Chrome View Transitions, Apple HIG. If a fact is missing, the gap is named.
- **Never invent a mã.** Customer-facing codes this pass may name are the **first-ten allowlist** only. Admin “Next mã A03” is a prediction. Slack `AO001` / `AO003` are **decision-template examples** (`#shop-decisions`, 2026-09-04), not live lookbook stock. Kelly Ying `V984.` / `V826.` are **their** SKUs — do not copy them onto Sassy tiles.
- **Two alphabets.** Sell-site / hub = `A01`. Official / Square / SoT = `AO001`. Motion never translates one into the other (`01` §9; `excel-kit/schema.py` `MA_RE`).
- **Facebook inbox is the store.** A “buy” is **Message {code}**. There is no cart. Shared-element motion that flies a tile into a bag is a lie.
- **No redesign mandate.** Improve **inside** paper / ink / gold / blush, Cormorant Garamond + Be Vietnam Pro, `ma-mark`, `announce-fade`, `shimmer` / `shimmer-slide`, `cta-shine` / `cta-flash`, gold `h-px` underline, `layoutId: "featured-tab"`, `filterSlide`, `springSoft`, `view-transition-name: site-header` / `product-{MA}`. Do not replace that language with iOS liquid glass, Shopify Horizon, intake Allura/Nunito rose, or a second animation library.

### 0.1 Research method (and what this pass could not see)

| Source | Result |
| --- | --- |
| Live sell-test HTML + CSS + JS of `/` (2026-09-09, this crawl) | Primary as-built. CSS `/_next/static/immutable/chunks/34vl_zddoo4ws.css`. Motion chunk `/_next/static/immutable/chunks/3_93acjqq2t4q.js` (module `42295` = `springSoft` / `filterSlide` / `fadeUp` / `staggerContainer`; `FeaturedBoard` + `AnimatedProductGrid` + `ProductGrid` in the same chunk family). |
| `curl` of `/c/ao`, `/c/quan`, `/m/A01` | Category vs home IA; PDP VT names (same gaps as `10`). |
| Repo `excel-kit/`, `sassy-closet/`, `README.md` | Shop law. Intake sheets are **behavior** only — do not restyle. |
| Sisters `01`–`14` (PRs #19–#33) | Headings + locks. This file is `20`. `13` is the watery APPLY sibling; this file does not replace it. |
| Slack `#shop-decisions` (`C0BV3GYC602`) | Five standing messages (2026-09-04). No springs / layoutId thread. |
| Linear | Keyword search returned no motion issue. |
| Granola meetings | MCP unauthorized — no meeting notes. |
| Notion | Business-plan AI search unavailable. Keyword search empty for FeaturedBoard. |
| Kelly Ying Boutique public site | Fetch timed out this pass. Look / cadence facts stay with `01` + `10`. |
| Motion docs (`motion.dev`) 2026-09-09 | React layout animations, transitions/springs, AnimatePresence modes, LayoutGroup, vanilla `animateLayout` (Motion+). URLs in §17. |

If a later crawl disagrees with a **live** cell here, **the new crawl wins** — update the date line. Shop law still wins over industry taste.

### 0.2 Sister docs

| # | File | Job vs this note |
| --- | --- | --- |
| 01 | `01-messenger-social-commerce.md` | Kelly Ying look lock; Message-first; no cart |
| 02 | `02-pdp-color-size-ux.md` | Customer **text** colors; gallery sync |
| 09 | `09-bugcheck-sell-site-checklist.md` | MOT-01…MOT-08 |
| **10** | `10-customer-pleasing-motion-ux.md` | General motion law + five Origin reliability fixes |
| **13** | `13-watery-tab-slide-motion.md` | Watery **metaphor** (meniscus / viscosity / pour); clip vs FLIP recipes; goo catalog |
| 14 | `14-complete-admin-feature-matrix.md` | Admin brains; do not mint from Next-grid |
| **20** | **This file** | **Motion / Motion One APIs, spring math, shared-element IDs, FeaturedBoard APPLY** |
| Kit | `SELL_CATALOG_CONTRACT.md` (PR #18) | Allowlist + prices + Hold null `$` |

`13` already asked for gold stretch, ≤200ms pour, APG tabs, pick A **or** B. Live JS (this crawl) **still** matches `13`’s chunk names. This note names **why** `wait` + remount + `staggerContainer` fights the spring, and which Motion knobs Origin must turn.

---

## 1. Executive summary

A boutique tab is a **shared-element spring**. A boutique gallery filter is either a **short directional pour** or an **in-place FLIP of the same ten tiles**. Those are two different Motion jobs. Live Featured does **both poorly at once**.

Nielsen Norman Group: animation must be **unobtrusive, brief, and subtle**. Use it for **feedback**, **state-change**, **navigation metaphors**, and **stronger signifiers** — not delight, not downtime ([NN/G, *The Role of Animation and Motion in UX*](https://www.nngroup.com/articles/animation-purpose-ux/)). 0.1s feels instantaneous; 1s keeps flow ([*Response Time Limits*](https://www.nngroup.com/articles/response-times-3-important-limits/)). `10` budgeted **≤200ms** for Featured filter. Live is already over that before watery is added.

Live motion on the **tab + gallery** path (2026-09-09, chunk `3_93acjqq2t4q.js`):

| Hook | Live fact |
| --- | --- |
| Package | `motion/react` (Framer Motion successor). **Not** vanilla Motion One. **Not** Motion+ `animateLayout`. |
| `FeaturedBoard` | Client filter. State `"all"` + `types[]`. Counts from the ten. |
| Tab button `f()` | `role="tab"` · `aria-selected` · gold `h-px` · `layoutId: "featured-tab"` unless `useReducedMotion()` |
| `springSoft` | `{ type: "spring", stiffness: 420, damping: 32, mass: 0.72 }` — **ζ ≈ 0.92**, settle ≈ **180ms** (§4) |
| Click `b(next)` | `direction = index(next) >= index(current) ? 1 : -1` then `setState` |
| `AnimatedProductGrid` | Outer `AnimatePresence mode="wait"` + `filterSlide` + **`motionKey={selected}` remount** + `ProductGrid replay={true}` |
| `filterSlide` | Enter `x: 28*dir` / **0.32s** ease `[.22,1,.36,1]`; exit `x: -22*dir` / **0.22s**. Reduced = duration `0`. |
| `ProductGrid` | Inner `AnimatePresence mode="popLayout"`; each tile `layout: true` + `fadeUp` + `springSoft` |
| `staggerContainer` | `{ staggerChildren: 0.07, delayChildren: 0.04 }` — **fires on every Featured remount** because `replay: true` |
| `.tab-scroll` | `overflow-x-auto` — **no `layoutScroll`** (Motion: scrollable FLIP parents must opt in) |
| Count line | Outer `AnimatePresence mode="wait"` + `motion.span` `duration: 0.18` |

That is already a **shared-element gold rule** (Motion `layoutId` = FLIP-class travel — [Motion layout animations](https://motion.dev/docs/react-layout-animations); [Paul Lewis, *FLIP Your Animations*](https://aerotwist.com/blog/flip-your-animations/)) plus a **directional slide**. It is **not** yet a spring pour:

1. The gold rule is a 1px rectangle that translates on a **straight path** (Motion default). Stretch is missing (`13` §7). `layoutScroll` is missing, so phone tab-scroll can FLIP from the wrong origin.
2. Outer `mode="wait"` **serializes** 0.22 + 0.32 = **~540ms blank**. Inner `popLayout` + `layout` never get a chance to FLIP remaining tiles because the whole grid **unmounts**.
3. `replay: true` restaggers children (`0.04 + n×0.07`). Ten tiles ≈ **740ms of leftover bounce** stacked on the wait. That is the opposite of viscosity.
4. `filterSlide` is a **tween**, not a spring — correct for `x`/`clip-path`. Do not “upgrade” clip-path to `springSoft` (§9).
5. Tabs are still mouse-first: no `tabpanel`, no `aria-controls`, no arrow keys (`10` §7; [APG Tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/)).

Reliability still beats beauty. A spring that overshoots three times, a `layoutId` that morphs A01’s cover into A02, or a 700ms wait that hides P02 is a **failed** boutique.

---

## 2. Hard constraints (print these on the implementer’s wall)

1. **Never invent a mã.** Emit list is exactly `A01 S01 P01 P02 P03 P04 P05 K01 H01 A02` (PR #18). Empty `/c/quan` stays empty. No `Q01` “so the FLIP has somewhere to go.”
2. **Never invent qty, $, photos, hex, or color names.** Hold P02 / P05 = **Inbox for price**. Empty `colors[]` = no chips (`02`; `05`; `10` §8).
3. **Square Free = on-hand truth.** Official Excel is a working copy (`README.md`). This kit does not edit Excel or intake in this pass.
4. **Bots draft only.** No Square Save, no Facebook Post/Send (`#shop-decisions` 2026-09-04).
5. **No cart, Shop now, or bag-fly.** Kelly Ying’s **$10 / $300+** and `V###` codes are **theirs** (`01` §0).
6. **Customer colors are text** (WCAG [1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)).
7. **Motion never changes identity.** Same mã in, same mã out. `layoutId={`tile-${ma}`}` and `view-transition-name: product-{MA}` morph **only** that mã. Filter must not drop P02/P05.
8. **Water / springs never lie on the photo.** No `filter: url(#goo)` on `.shimmer`, covers, or heroes. No `feDisplacementMap`. No `layout` scale that stretches a 3:4 JPEG into a different crop without `layout="position"` on the image.
9. **Stay on `motion/react`.** Do not add Motion+ `animateLayout`, GSAP Flip, or a second `layoutId` runtime. Origin already paid the React bundle.
10. **Origin owns the pixels.** APPLY is for the Origin agent on `sassy-closet-shop`. Intake Production stays https://sassy-closet.vercel.app. This PR does not edit `excel-kit/` or `sassy-closet/`.

---

## 3. Two Motion stacks (pick the one already on the host)

“Framer Motion / Motion One” in the Boss brief is **one family**, two public APIs. Origin already shipped the React one.

| Stack | Import | Shared-element knob | Layout knob | On sell-test? |
| --- | --- | --- | --- | --- |
| **Motion for React** (was Framer Motion) | `motion/react` | `layoutId="…"` on `<motion.*>` | `layout` / `layout="position"` | **Yes.** `useReducedMotion`, `AnimatePresence`, `springSoft`. |
| **Motion (vanilla / Motion One lineage)** | `motion` `animate()` | n/a in the free layout API | WAAPI / JS springs on transforms | Not the Featured path. |
| **Motion+ `animateLayout` (early access)** | `motion-plus/animate-layout` | `data-layout-id` | `data-layout` + wrap DOM update | **Refuse.** Paid, alpha, requires `motion@12.29.2+`. Duplicate of what `layoutId` already does. ([Motion layout animations — vanilla](https://motion.dev/docs/layout-animations)) |

Mapping if someone pastes a vanilla snippet into Origin:

| Vanilla / Motion+ | React (live) |
| --- | --- |
| `data-layout-id="featured-tab"` | `layoutId="featured-tab"` |
| `data-layout` | `layout` |
| `data-layout="preserve-aspect"` | `layout="preserve-aspect"` (or `"position"` on photos) |
| `animateLayout(update, { type: "spring", stiffness: 420, damping: 32, mass: 0.72 })` | `transition={springSoft}` on the destination node |

**Do not migrate.** The live underline recipe is already the Motion docs’ tab example: `isSelected && <motion.span layoutId="underline" />` ([React layout animations — shared](https://motion.dev/docs/react-layout-animations)).

View Transitions stay the **navigation** tool (home card → `/m/{MA}`). Motion `layoutId` stays the **same-document** tool (Featured tabs + optional in-place tiles). Mixing both on the same element is how IDs collide (`10` FIX 3; §6).

---

## 4. Spring physics (the live token, named)

Motion springs are either **physics** (`stiffness`, `damping`, `mass`) or **duration** (`duration` + `bounce`). Physics springs keep **velocity across interruptions** — that is why a frantic tabber still feels wet. Duration springs do not inherit velocity, but they can compile to CSS ([Motion transitions](https://motion.dev/docs/react-transitions)).

`bounce` + `duration` are **ignored** when `stiffness` / `damping` / `mass` are set. Live `springSoft` is physics. Keep it physics.

### 4.1 Live `springSoft` — compute, don’t guess

Hook (module `42295`):

```js
const springSoft = { type: "spring", stiffness: 420, damping: 32, mass: 0.72 };
```

Second-order model (same as Android `SpringForce` / Figma springs):

| Symbol | Formula | Live value |
| --- | --- | --- |
| k | stiffness | 420 |
| c | damping | 32 |
| m | mass | 0.72 |
| ωₙ | `sqrt(k / m)` | `sqrt(420 / 0.72) ≈ 24.15 rad/s` |
| ζ | `c / (2 * sqrt(k * m))` | `32 / (2 * sqrt(302.4)) ≈ 0.920` |
| Settle (~2%) | `4 / (ζ * ωₙ)` | `4 / 22.2 ≈ 0.18 s` |

ζ **< 1** = underdamped = **one small overshoot**. ζ **= 1** = critical = fastest with no bounce. ζ **> 1** = overdamped = sluggish ([Figma, *How we built spring animations*](https://www.figma.com/blog/how-we-built-spring-animations/); [Android spring damping](https://developer.android.com/develop/ui/views/animations/spring-animation); [Mayhew, *Atmospheric Animations*](https://alexmayhew.dev/blog/atmospheric-animations-framer-motion)).

**0.92 is already the boutique number.** One overshoot is silk. Do not raise mass to “feel more liquid” — mass 1.2 at this k drops ωₙ and stretches settle past 250ms. Do not drop damping to 12 — ζ ≈ 0.34 is a toy. WWDC23 flags **sustained oscillation** as a comfort risk ([vision and motion](https://developer.apple.com/videos/play/wwdc2023/10078/)).

Optional duration-based alias **only if** Origin later needs a CSS-only fallback:

```js
// equivalent *feel*, loses interrupt velocity
{ type: "spring", visualDuration: 0.18, bounce: 0.12 }
```

`visualDuration` is the time until the motion *looks* settled; bounce happens after ([Motion `visualDuration`](https://motion.dev/docs/react-transitions)). Do not ship both physics and bounce on the same object.

### 4.2 Named springs (do not invent a fifth)

Keep the **export name** `springSoft`. If Origin needs a second token, add it next to module `42295` — do not scatter magic numbers.

| Token | Suggested body | Use | Refuse |
| --- | --- | --- | --- |
| `springSoft` (live) | `k420 / c32 / m0.72` | Gold `featured-tab`; tile `layout` on recipe **B** | Clip-path, opacity, goo blur |
| `springMeniscus` (optional) | **same as `springSoft`** + child `scaleX` keyframes | Stretch film on the rule | A second, bouncier spring |
| `kyEase` (live bezier) | `[0.22, 1, 0.36, 1]` | `filterSlide` tween (pour) | Gold rule travel |
| `tweenCount` | `{ duration: 0.12, ease: kyEase }` | “N pieces” swap | Spring on 11px type (goo-adjacent blur) |

Opacity should stay a **linear or ease tween**. Springing opacity feels like a fade that overshoots 1.05 — browsers clip it, and it reads as a flash ([Motion value-specific transitions](https://motion.dev/docs/react-transitions)):

```js
transition={{
  layout: springSoft,
  opacity: { duration: 0.12, ease: "linear" },
}}
```

### 4.3 Interruptibility

Motion layout animations are **interruptible**. View Transitions are **not** ([Motion vs VT](https://motion.dev/docs/react-layout-animations)). Featured tabbing is frequent — the buyer will tap Tops then Accessories before settle. That is why the gold rule is `layoutId` + physics spring, not a CSS `left` tween and not a View Transition.

If Origin wraps the filter in `document.startViewTransition`, a second tap **snaps** the first animation to the end. `10` already said: skip `startViewTransition` when Reduce Motion; this file adds: **do not VT the Featured filter at all**. Framer already owns it.

---

## 5. `layout` vs `layoutId` vs `layout="position"`

FLIP (First, Last, Invert, Play): measure before, mutate DOM, invert with `transform`, play to identity ([Lewis](https://aerotwist.com/blog/flip-your-animations/); [CSS-Tricks FLIP](https://css-tricks.com/animating-layouts-with-the-flip-technique/)). Motion’s projection layer is FLIP that also **scale-corrects** children.

| Prop | What it does | Featured use |
| --- | --- | --- |
| `layout` | Animate **this** node’s size+position when React layout changes | Tile `motion.li` (already `layout: true`) |
| `layout="position"` | Translate only; **size snaps** | Cover `<img>` / `aspect-[3/4]` wrapper so 3:4 photos do not squash |
| `layout="size"` | Scale only | Rare. Not the hairline. |
| `layout="preserve-aspect"` | Motion+ / vanilla `data-layout` enum | Photos if Origin ever uses `animateLayout` — we are not |
| `layoutId="id"` | Match **two** nodes; new node FLIPs out of the old | Gold rule `"featured-tab"`; recipe B `"tile-${ma}"` |

Warnings from Motion docs, mapped:

| Doc warning | Sell-test meaning |
| --- | --- |
| Change layout via `className` / `style`, **not** `animate` width | Do not `animate={{ width }}` the gold rule. Let `layoutId` FLIP. |
| `display: inline` cannot transform | Gold rule is `span` with `absolute` — already a blockified box. Keep `absolute inset-x-0 bottom-0`. |
| Two live nodes with the **same** `layoutId` **crossfade** | Never put `"featured-tab"` on the trail. Trail = `"featured-tab-trail"`. |
| Destination `transition` wins | Stretch / spring config lives on the **entering** rule (the selected tab’s span). |
| Default path is a **straight line**; `arc()` curves it | **Refuse `arc()` on the hairline** — it would lift gold off the 11px baseline. |
| Scale distorts children | Hairline has no children. Tiles: put `layout` (or `layout="position"`) on the photo, not only the `li`. |
| `border` cannot render `< 1px` | `h-px` is already 1px — **do not scaleY** the rule. Stretch **scaleX only**. |
| SVG layout is broken | Goo SVG stays `width="0" height="0"`; do not `layoutId` the `<filter>`. |
| Horizontal window resize kills layout animations | Do not QA springs by dragging DevTools; reload at a width. |

`layoutId` is **global** across the page unless namespaced with `LayoutGroup id` ([LayoutGroup](https://motion.dev/docs/react-layout-group)). One Featured row is fine. If Origin later duplicates chips on `/c/*`, wrap each row:

```tsx
<LayoutGroup id="featured-home">
  {/* tabs with layoutId="featured-tab" → actually featured-home-featured-tab */}
</LayoutGroup>
```

Do not wrap the **whole page** in one group “for safety” — CollectionList accordions / mosaics would then FLIP when tabs change.

---

## 6. Shared-element map (three layers, three ID systems)

Do not collapse these. They look similar in screenshots and fight in code.

| Layer | ID system | Document | Live 2026-09-09 | APPLY |
| --- | --- | --- | --- | --- |
| **A. Tab meniscus** | Motion `layoutId="featured-tab"` | Same page | Present; reduced → `undefined` | Keep. Add stretch. `layoutScroll` on `.tab-scroll`. |
| **B. Gallery tiles** | Motion `layoutId={`tile-${ma}`}` **or** remount pour | Same page | `layout: true` **without** `layoutId`; remounted by `motionKey` so FLIP never sees All→Tops | Recipe **A** or **B**, not both (`13` §8.3) |
| **C. Card → PDP** | CSS `view-transition-name: product-{MA}` | Navigation | Names on **home cards**; `/m/A01` hero **unnamed** (`10` FIX 3) | Not this watery pass except: do not steal `product-A01` as a Motion `layoutId` |

### 6.1 Registry (print next to the allowlist)

| ID | Kind | Owner | Collision if… |
| --- | --- | --- | --- |
| `featured-tab` | Motion layoutId | Selected gold `h-px` | Trail / second tablist / admin preview |
| `featured-tab-trail` | Motion layoutId (optional) | 30% gold film | Reusing `featured-tab` |
| `tile-A01` … `tile-A02` | Motion layoutId (recipe B only) | Featured `motion.li` | Using `product-A01` here **and** as VT name |
| `product-A01` … `product-A02` | VT name | Card cover + **PDP hero** | Motion `layoutId="product-A01"` |
| `site-header` | VT name | Header | Motion layoutId of the same string |

Allowlist only. There is no `tile-A03`, no `product-Q01`.

### 6.2 Crossfade vs teleport

Motion: if the **old** node is still mounted when the new `layoutId` enters, the two **crossfade**. The live tab recipe unmounts the idle rule (`e ? motion.span : null` on the selected button only) — that is the **underline pattern**, not a crossfade. Keep it. If both All and Tops rendered a gold span, the line would ghost.

`AnimatePresence` around a `layoutId` modal is for **return trips**. The tab rule does not need Presence; it hops between selected buttons. The **grid** does.

---

## 7. `layoutScroll`, `layoutRoot`, `LayoutGroup` — live gaps

### 7.1 `layoutScroll` (phone)

Motion: *“To correctly animate layout within a scrollable container, you must add the `layoutScroll` prop”* ([layout animations](https://motion.dev/docs/react-layout-animations)).

Live markup:

```html
<div class="-mx-3 mt-6 overflow-x-auto px-3 tab-scroll sm:mx-0 sm:overflow-visible">
  <div role="tablist" aria-label="Filter featured collection">…gold rule…</div>
</div>
```

The scroller is a **plain `div`**. On `sm+` it is `overflow-visible` (no scroll). On phone it is `overflow-x-auto` with scrollbar hidden (`13` §4.1). The gold `layoutId` FLIP measures in viewport space unless the scroll parent is a `motion` node with `layoutScroll`. Symptom: tap a chip that was off-screen, `scrollIntoView` runs, the hairline **jumps from the old scroll origin**.

APPLY:

```tsx
<motion.div layoutScroll className="-mx-3 mt-6 overflow-x-auto px-3 tab-scroll sm:mx-0 sm:overflow-visible">
```

Do **not** put `layout` on that scroller (it would FLIP the whole chip row). `layoutScroll` only teaches projection about `scrollLeft`.

### 7.2 `layoutRoot`

Needed for `position: fixed` ancestors. Featured is in document flow. Header VT is `site-header`. Do not mark the page `layoutRoot` unless a future sticky tab bar is `fixed`.

### 7.3 `LayoutGroup`

The Motion **library** ships `LayoutGroup` (chunk references the context). FeaturedBoard does **not** wrap the tablist. One row + one `featured-tab` id = OK. Recipe B (tiles FLIP while the gold rule FLIPs) **should** group **tabs and grid separately**, not together — otherwise the rule’s spring and the tiles’ spring share a dirty flag and hitch.

```tsx
<LayoutGroup id="featured-tabs">{/* tablist */}</LayoutGroup>
<LayoutGroup id="featured-grid">{/* ProductGrid recipe B */}</LayoutGroup>
```

`13` did not require this. This file does, **if** recipe B ships.

---

## 8. `AnimatePresence` modes — the 540ms blank is a mode bug

[AnimatePresence `mode`](https://motion.dev/docs/react-animate-presence) (default **`sync`**):

| Mode | Behavior | Motion’s own example use | Featured? |
| --- | --- | --- | --- |
| `sync` | Enter and exit **overlap** | Overlays; needs `position: absolute` if boxes collide | Legal for recipe **A** if both grids are stacked + `overflow-hidden` |
| `wait` | Enter waits for exit. **One child only.** | Wizards, **tab content** in their tutorial | Live outer grid. Honest for a *new page*. Too slow for a **filter**. |
| `popLayout` | Exit is `position: absolute`; siblings reflow now | Lists + `layout` | **Already inner** on `ProductGrid` |

Motion’s tutorial says tab *content* → `wait`. That is for **unrelated panels** (settings vs profile). Featured is a **filter of the same ten SKUs**. Chrome’s VT filter demo: remainers **move**, leavers **fade**, enterers **fade** — they do not blank ([Chrome View Transitions](https://developer.chrome.com/docs/web-platform/view-transitions/)).

### 8.1 Double wrap (the live architecture)

```text
AnimatedProductGrid
  AnimatePresence mode="wait"          ← OUTER: remounts on motionKey=selected
    motion.div  filterSlide            ← tween x 28 / -22
      ProductGrid replay={true}        ← restagger every time
        AnimatePresence mode="popLayout"  ← INNER: never sees a partial list
          motion.li layout + fadeUp + springSoft  × n
```

Because `wait` unmounts the whole `ProductGrid`, the inner `popLayout` only ever animates **first paint of a new list**, not All→Tops remaining A01/A02. `replay: true` forces `animate="show"` so `staggerContainer` runs on every tab.

**Recipe A (keep remount / pour):** outer Presence stays; **cut durations**; prefer `mode="sync"` with both panels `absolute inset-0` inside `overflow-hidden`; set **`replay={false}`** on Featured so stagger does not run; inner `popLayout` is redundant on a full remount — leave it for `/c/*` pages that share `ProductGrid`.

**Recipe B (in-place FLIP):** **delete the outer wait + `motionKey` remount.** Pass the filtered array into one `ProductGrid`. Inner `popLayout` + `layout` + `layoutId={`tile-${ma}`}` finally do their job. Gold meniscus is the only watery. **Do not also `filterSlide` x/clip.**

`forwardRef` is required on custom children of `popLayout` ([docs warning](https://motion.dev/docs/react-animate-presence)). Live `v({product})` is a function component used as `<v product={e} />` — if recipe B mis-positions exits, wrap `v` in `forwardRef` to the `li`.

Parent performing `layout` must be `position: relative` or `popLayout` measures the wrong offset parent ([motion#3026](https://github.com/motiondivision/motion/issues/3026)). APPLY: `motion.ul` already a grid — add `className="… relative"` (or `style={{ position: "relative" }}`).

`initial={false}` is already set (no enter-on-first-paint). Keep it.

`custom={direction}` + variants that read `usePresenceData()` is how to keep directional exit **after** the node is removed from the tree ([Presence `custom`](https://motion.dev/docs/react-animate-presence)). Recipe A can pass `direction` this way instead of closing over stale `filterSlide(dir)`.

---

## 9. Spring pours — what may spring, what must tween

“Pour” is a **clip uncover**, not a springy `x`. Springs overshoot. `clip-path: inset()` that overshoots `inset(-10%)` flashes neighboring pixels. `x` that overshoots 28px shows a gap of `--paper` (reads as a blank shop).

| Property | Spring? | Why |
| --- | --- | --- |
| Gold rule **position** (`layoutId`) | **Yes** `springSoft` | Interruptible; ζ 0.92 = one wet tick |
| Gold rule **scaleX** stretch | **Yes**, or a 2–3 keyframe tween 1 → 1.15 → 1 on the same spring | Meniscus (`13` §7.3) |
| Grid **clip-path** | **No — tween** `kyEase` 80–180ms | Overshoot = invalid inset / photo lie |
| Grid **x** | **Tween only**, and **small** (`8px`) if clip is the hero; or **0** on recipe B | Live 28px is a second page |
| Tile **layout** (recipe B) | **Yes** `springSoft` | Remaining SKUs slide in-grid |
| Tile **opacity** enter/exit | **Tween** 80–120ms linear | Spring opacity flashes |
| Count text | **Tween** 120ms | 11px type |
| Goo `stdDeviation` | **Do not animate** | Filter thrash; optional static 6 |

Recipe A body (keep export name `filterSlide`; ease token kept):

```js
function filterSlide(reduced, dir) {
  if (reduced) {
    return {
      initial: { opacity: 1, x: 0, clipPath: "inset(0)" },
      animate: { opacity: 1, x: 0, clipPath: "inset(0)", transition: { duration: 0 } },
      exit: { opacity: 1, x: 0, clipPath: "inset(0)", transition: { duration: 0 } },
    };
  }
  const from = dir > 0 ? "inset(0 0 0 28%)" : "inset(0 28% 0 0)";
  const exitTo = dir > 0 ? "inset(0 28% 0 0)" : "inset(0 0 0 28%)";
  return {
    initial: { opacity: 0.96, clipPath: from, x: 8 * dir },
    animate: {
      opacity: 1,
      clipPath: "inset(0)",
      x: 0,
      transition: { duration: 0.18, ease: [0.22, 1, 0.36, 1] },
    },
    exit: {
      opacity: 0.96,
      clipPath: exitTo,
      x: -6 * dir,
      transition: { duration: 0.12, ease: [0.22, 1, 0.36, 1] },
    },
  };
}
```

If Origin keeps `mode="wait"`, those two durations **must sum to ≤200ms** (e.g. 80ms exit + 120ms enter). Prefer `sync` + overlapping abs panels so perceived time ≈ **max(enter, exit) ≈ 180ms**.

`--duration-enter: .21s` / `--duration-exit: .15s` already exist and are **unused** by Featured (`13` §4.1). Binding clip CSS to them is legal. **`--duration-move: .4s` is too slow** for tabs.

Optional `shape()` wave on the leading edge: `13` §8.4. Not required. Never spring the shape.

---

## 10. Distortion — 3:4 covers must not become cloth

Motion animates layout with **scale**. A `li` that FLIPs from a 2-col slot to a 5-col slot will **squash the JPEG** unless the image is scale-corrected (`layout` on the child) or the `li` uses `layout="position"` ([content stretches FAQ](https://motion.dev/docs/react-layout-animations)).

Live tile: `aspect-[3/4]` wrapper + `object-cover` img. Hover already `scale-[1.08]` via CSS (`10`). Stacking Motion scale + CSS hover scale is how garments look drunk.

APPLY for recipe B:

```tsx
<motion.li
  layout
  layoutId={`tile-${product.ma}`}
  transition={{ layout: springSoft, opacity: { duration: 0.12 } }}
>
  <motion.div layout="position" className="relative aspect-[3/4] overflow-hidden">
    {/* cover; view-transition-name stays product-{ma} on this box when namedTransition */}
  </motion.div>
</motion.li>
```

`borderRadius` / `boxShadow` must be set on `style={{}}` if Origin ever rounds the card during FLIP — Motion only corrects those when they are **motion styles**, not Tailwind classes that never enter projection.

Do **not** `layout` the `.shimmer` overlay (it would FLIP a loading sheen across SKUs). Shimmer is cover-load only (`10` §12).

---

## 11. As-built hook map (cite the live host)

Crawl: 2026-09-09. Same chunks as `13`: CSS `34vl_zddoo4ws.css`, JS `3_93acjqq2t4q.js`.

### 11.1 CSS tokens (do not rename)

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

Fonts: Be Vietnam Pro (`font-sans`) + Cormorant Garamond (`font-display`). Keyframes `announce-fade` / `shimmer-slide` / `cta-flash` stay (`10` FIX 1). `::view-transition { pointer-events: none }` stays.

### 11.2 `FeaturedBoard` (reconstructed)

```js
function FeaturedBoard({ products, types }) {
  const [selected, setSelected] = useState("all");
  const [dir, setDir] = useState(1);
  const reduced = useReducedMotion();
  const tabs = ["all", ...types];
  const filtered = selected === "all" ? products : products.filter((p) => p.type === selected);
  function b(next) {
    setDir(tabs.indexOf(next) >= tabs.indexOf(selected) ? 1 : -1);
    setSelected(next);
  }
  // tab: layoutId={reduced ? undefined : "featured-tab"} + transition={springSoft}
  // count: AnimatePresence wait + duration 0.18
  return <AnimatedProductGrid products={filtered} motionKey={selected} direction={dir} />;
}
```

Labels + counts (sum = 10): `All 10 · Tops 2 · Sets 1 · Accessories 5 · Jackets 1 · Hair 1`.

Routes still exist: `/c/ao` (A01+A02), `/c/set` (S01), `/c/phu-kien` (P01–P05), `/c/ao-khoac` (K01), `/c/toc` (H01), `/c/quan` (**empty**). APPLY: Tops filter = A01+A02; Accessories keeps Hold P02/P05.

### 11.3 Strings to `rg`

| String | Role |
| --- | --- |
| `FeaturedBoard` | Home Featured section |
| `Filter featured collection` | `aria-label` on `tablist` |
| `featured-tab` | Motion `layoutId` |
| `springSoft` | Shared physics spring |
| `filterSlide` | Grid enter/exit variants |
| `AnimatedProductGrid` | `products` · `motionKey` · `direction` |
| `ProductGrid` | `replay` · inner `popLayout` |
| `fadeUp` / `staggerContainer` | Tile / mosaic variants |
| `tab-scroll` | Horizontal scroller |
| `useReducedMotion` | Framer hook |
| `coverSrc` / `coverSrcForColor` | Cover helpers |
| `viewTransitionName: product-${ma}` | On `aspect-[3/4]` when `namedTransition` |

**Not present:** `layoutScroll`, `layoutId={`tile-`, `aria-controls`, `tabpanel`, `clipPath`, `goo`, `startViewTransition`.

### 11.4 What already honors Reduce Motion

| Motion | Reduced today |
| --- | --- |
| `layoutId: "featured-tab"` | **Off** (`undefined`) — rule teleports. Correct. |
| `filterSlide` | Duration 0. Correct. |
| Count span | Duration 0. Correct. |
| `fadeUp` / `staggerContainer` | Offsets/stagger 0. Correct. |
| CSS shimmer / announce / cta / VT | `animation: none`. Correct. |
| Card `scale-[1.08]` / `-translate-y-1.5` | **Still runs** (`10` MOT-03). Watery must not add a second hover zoom. |

---

## 12. Reduced-motion + vestibular

WCAG clocks (do not collapse — [Motion Spec](https://motionspec.dev/blog/wcag-2-3-3-animation-from-interactions); `10` §3.3):

| Criterion | Springs / layoutId impact |
| --- | --- |
| [2.2.2](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) A | Infinite `.shimmer` is still the loop. Do not spring-loop the gold rule (`repeat: Infinity`). |
| [2.3.1](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html) A | Do not strobe `scaleX`. |
| [2.3.3](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) AAA | Tab FLIP, clip pour, tile layout = interaction animation. Sufficient: [C39](https://www.w3.org/WAI/WCAG22/Techniques/css/C39) + `useReducedMotion` (already). |
| [1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) | Selected tab is ink + rule + `aria-selected`, not gold alone. |

MDN: `prefers-reduced-motion: reduce` means **remove, reduce, or replace**; scaling/panning large objects are vestibular triggers ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)). A grid `translateX(28px)` plus clip is that class — already zeroed. `layoutId` already off. Keep both.

Apple: fade, don’t zoom. Reduced fallback = **instant selected rule** + **instant grid** + count text swap. Springs are non-essential.

`MotionConfig reducedMotion="user"` is an alternative to per-hook `useReducedMotion` ([MotionConfig](https://motion.dev/docs/react-motion-component)). Live uses the hook. Do not wrap the app in a config that **also** changes `springSoft` globally (admin would inherit).

---

## 13. Timing budget (physics + live)

| Interaction | Budget | Live 2026-09-09 | APPLY |
| --- | --- | --- | --- |
| Gold rule starts moving | ≤100ms | Spring starts on render — OK | Keep `layoutId`; add `layoutScroll` |
| Gold rule settles | ≤300ms | ζ 0.92 → **~180ms** | Keep `springSoft`; one overshoot |
| Count “N pieces” | ≤120–180ms | 180ms | Keep or cut to 120ms tween |
| Grid pour perceived | ≤200ms (`10`) | **~540ms wait** + stagger up to **~740ms** | Recipe A: cut/overlap; `replay={false}`. Recipe B: drop outer wait |
| Tile layout (B only) | ≤180ms | n/a (remounted) | `springSoft` |
| Home → PDP VT | ≤300ms | Names mismatch | `10` FIX 3; not a spring pour |
| Shimmer | — | 1.3s infinite | `10` FIX 1; not a tab tool |

Do not use `--duration-move: .4s` as the tab clock.

---

## 14. APPLY — [sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app) FeaturedBoard watery tabs

**Owner:** Origin `sassy-closet-shop` (not this kit).  
**Look:** Kelly Ying hairline + paper. **Job:** shared-element **spring** on the gold rule + **pour or in-place FLIP** on the gallery.  
**Mã:** allowlist only. **No** Square Save. **No** FB Send. **No** cart.  
**Do not edit** `excel-kit/` or intake `sassy-closet/`.  
**Do not migrate to Motion One / Motion+.**

Human-readable ticks. **Paste block is §19.** Compatible with `13` §14 — this file adds physics + `layoutScroll` + the double-Presence diagnosis.

### 14.0 Do not touch (lock — tick first)

- [ ] Cormorant Garamond + Be Vietnam Pro.
- [ ] Paper / ink / gold / blush; `ma-mark`; 11px tracking; gold **`h-px`** (not a fat pill).
- [ ] Keyframes `announce-fade`, `shimmer-slide`, `cta-flash` and classes `announce-fade`, `shimmer`, `cta-shine` **remain**.
- [ ] Exports / strings `FeaturedBoard`, `featured-tab`, `filterSlide`, `springSoft`, `AnimatedProductGrid`, `ProductGrid` **remain** (you may change **bodies**).
- [ ] `springSoft` stays `{ type: "spring", stiffness: 420, damping: 32, mass: 0.72 }` unless a comment cites §4 and ζ stays **0.85–0.98**.
- [ ] Featured chips All / Tops / Sets / Accessories / Jackets / Hair + counts that sum to **10**.
- [ ] Livestream rail + Page `61594312648057`.
- [ ] Message-first CTAs; footer **Zelle** word; no personal name.
- [ ] Hold on **P02, P05** (no published `$`).
- [ ] `/admin` out of the main nav.
- [ ] Intake host unchanged.
- [ ] No `motion-plus`, no GSAP Flip, no new `layoutId` runtime.

### 14.1 JS hooks — tab (`FeaturedBoard`)

`rg -n "featured-tab|Filter featured collection|springSoft|tab-scroll|layoutScroll"`

- [ ] Keep `layoutId={!reduced && "featured-tab"}` on the gold `h-px`.
- [ ] Keep `transition={springSoft}` (destination wins).
- [ ] Stretch: `scaleX` 1 → ~1.15 → 1 on the **rule only** (scaleX, never scaleY / `h-1`). One overshoot max.
- [ ] Optional trail: `layoutId="featured-tab-trail"` — **different id**.
- [ ] Wrap `.tab-scroll` in `<motion.div layoutScroll>` (no `layout` on the scroller).
- [ ] Optional: `LayoutGroup id="featured-tabs"` around the tablist only.
- [ ] Click `b()` still sets `direction` from index compare.
- [ ] APG: `aria-controls` → grid id; grid `role="tabpanel"` + `aria-labelledby`; Left/Right (+ Home/End); do not steal Up/Down.
- [ ] `scrollIntoView({ inline: "nearest", block: "nearest" })` for the selected chip.
- [ ] Counts stay math: Tops = A01+A02; Accessories = P01–P05 including Holds.

### 14.2 JS hooks — gallery (pick A **or** B)

`rg -n "filterSlide|AnimatedProductGrid|motionKey|mode:\\\"wait\\\"|popLayout|replay"`

**A — Pour the wrapper (smallest diff)**

- [ ] Keep `filterSlide(reduced, direction)` **name** + ease `[0.22, 1, 0.36, 1]`.
- [ ] Tween **clip-path** + tiny `x` (§9). Do **not** assign `springSoft` to clip-path.
- [ ] Perceived ≤200ms: `mode="sync"` + overlapping abs children **or** keep `wait` with exit+enter **sum ≤200ms**.
- [ ] `ProductGrid replay={false}` on the Featured path (stagger stays on home `CollectionList` / first paint of `/c/*` only).
- [ ] Reduced: duration 0, `x: 0`, `clipPath: "inset(0)"`.

**B — Filter in place (more honest)**

- [ ] Remove outer `wait` remount (`motionKey` / `filterSlide` x). Inner `popLayout` + `layout` stay.
- [ ] Add `layoutId={`tile-${ma}`}` on each Featured `motion.li` (allowlist mãs only).
- [ ] Cover wrapper `layout="position"` so JPEGs do not squash.
- [ ] `forwardRef` the tile to the `li` if popLayout mis-measures.
- [ ] `motion.ul` `position: relative`.
- [ ] Optional `LayoutGroup id="featured-grid"`.
- [ ] Leavers/enterers: opacity tween 80–120ms. Remainers: `springSoft` layout.
- [ ] Do not also run wrapper `filterSlide` clip/x.

**Both**

- [ ] Empty filter / `/c/quan`: copy only (`Nothing in this collection yet.` may stay or become the bilingual pair from `13`). No shimmer skeletons. No Q01.
- [ ] No second `.shimmer` while filtering.
- [ ] Message {MA} clickable during pour (`pointer-events` not trapped).

### 14.3 Do not spring / watery these

- [ ] Product covers / `.shimmer` / PDP hero — no goo, no displacement, no `layoutId="product-{MA}"`.
- [ ] `cta-shine` / `cta-flash` — stay a shine.
- [ ] Shop-tools dialog — not a liquid sheet.
- [ ] Intake `PhotoLightbox` / rose sheets — do not import.
- [ ] `arc()` on the hairline.
- [ ] `startViewTransition` around Featured filter.

### 14.4 Reliability / commerce

- [ ] Mid-pour, Hold is still the word Hold; P02/P05 have no `$`.
- [ ] No cart, bag, Shop now, flying-to-cart, liquid-into-bag.
- [ ] No countdown, no fake stock pulse (`07` §11).
- [ ] Do not print Kelly Ying **$10 / $300+** or `V###`.
- [ ] Do not alias `A01` ↔ `AO001` in a caption that rides the pour.

### 14.5 Verify (Origin, after springs work)

Desktop (hover) + phone (no hover, **tab-scroll**) + OS Reduce Motion + keyboard:

1. Home Featured: All → Tops → Accessories → All. Counts 10 / 2 / 5 / 10. Gold hairline **stretches then settles ~180ms** (motion on) or **jumps** (reduced). P02 still Hold.
2. Phone: scroll chips, select Hair off-screen — rule FLIPs from the **chip**, not from x=0 of the scroller (`layoutScroll`).
3. Direction: All → Hair pours/FLIPs one way; Hair → All the other. Rapid Tops→Accessories **interrupts** the spring (no snap-to-end like VT).
4. Perceived filter ≤200ms. No empty-white flash. No 10-tile stagger on tab change.
5. Keyboard: Tab into the list, arrows move + activate (or Space/Enter if manual). Up/Down still scroll the page.
6. `/c/ao` still two tops, $25 / $22. `/c/quan` still empty.
7. `/m/A01` cover visible; Message works. Do not regress `10` hero-name gap if you also ship that PR.
8. Reduce Motion: no stretch, no pour, no goo, no shimmer slide, no 1.08 zoom (`10`). Tabs + Message still work.
9. View-source: no `e.tb.cn`, no ¥, no `A03`, no `V984`.

---

## 15. Anti-patterns (quick refuse list)

1. Minting `A03` / `Q01` so a FLIP “has somewhere to go.”
2. Installing `motion-plus` / GSAP Flip / a second `layoutId` runtime.
3. Putting `springSoft` on `clip-path` or opacity.
4. Raising `mass` above ~0.9 or dropping `damping` below ~24 on the hairline.
5. `arc()` on `featured-tab`.
6. Two visible nodes with `layoutId="featured-tab"`.
7. `layoutId="product-A01"` on a tile (collides with VT).
8. Keeping outer `wait` **and** `replay={true}` stagger.
9. Shipping recipe A **and** B.
10. `filter: url(#goo)` on `tablist`, cards, or covers.
11. `feDisplacementMap` / chromatic aberration on product photos.
12. Full-page `shape()` ooze; CSS Anchor glass pointer.
13. VT around Featured filter; cart-bag shared-element.
14. Restyling to intake rose / Allura.
15. Copying Kelly Ying `V984` or `$10 / $300+`.
16. Translating `A01` → `AO001` in a caption that rides the pour.
17. Using `--duration-move: .4s` as the tab clock.

---

## 16. Acceptance (sell-test springs)

A reviewer can fail the page against this list without a redesign argument:

- [ ] Every mã that moves is on the allowlist and was **already assigned**.
- [ ] Featured filter and `/c/*` show the same sets; empty stays empty.
- [ ] P02 / P05 never display a dollar, including mid-pour.
- [ ] Gold rule is still `h-px bg-gold` + `layoutId="featured-tab"` + `springSoft` (ζ ~0.92).
- [ ] `filterSlide` / `FeaturedBoard` / `springSoft` still exist as names.
- [ ] Perceived filter ≤200ms with motion on; instant with Reduce Motion.
- [ ] Phone scrolled tabs: hairline still tracks the selected chip.
- [ ] No goo/displacement on photography; no JPEG squash on recipe B.
- [ ] APG tablist keyboard works.
- [ ] Message CTA never blocked by a clip overlay.
- [ ] Fonts, gold, chips, no-cart CTA still match `01` / `07` / `10` / `13` locks.

---

## 17. Sources

### 17.1 Shop law and as-built

- `README.md` — Square SoT; bots draft; Facebook inbox.
- `excel-kit/DESIGN_NOTES.md`, `excel-kit/schema.py` — mã law; ASK STOCK.
- `excel-kit/docs/SELL_CATALOG_CONTRACT.md` + sample (PR #18) — allowlist, prices, Hold P02/P05.
- Sisters `01`–`14` (PRs #19–#33) — look lock, PDP nouns, MOT checklist, watery (`13`), admin matrix (`14`).
- Slack `#shop-decisions` (2026-09-04):
  - [Channel law](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788541753903809)
  - [Track stock ON proposal](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788553328521899)
  - [Boss yes](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788553474026779)
  - [Square LIVE](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788556083454949)
- Live host 2026-09-09: https://sassy-closet-shop.vercel.app — CSS `34vl_zddoo4ws.css`; JS `3_93acjqq2t4q.js` (module `42295`).
- Kelly Ying Boutique — <https://www.kellyyingboutique.net/> (timed out this pass; prior read in `01` / `10`).

### 17.2 Motion APIs (Framer Motion / Motion One family)

- Motion for React, *Layout animations* (`layout`, `layoutId`, FLIP vs VT, `layoutScroll`, distortion) — <https://motion.dev/docs/react-layout-animations>
- Legacy Framer URL (same family) — <https://www.framer.com/motion/layout-animations/>
- Motion, *Transitions* (tween / spring physics / `visualDuration` / value-specific) — <https://motion.dev/docs/react-transitions>
- Motion, *AnimatePresence* (`sync` / `wait` / `popLayout`, `custom`, `initial={false}`) — <https://motion.dev/docs/react-animate-presence>
- Motion, *LayoutGroup* (`id` namespaces `layoutId`) — <https://motion.dev/docs/react-layout-group>
- Motion vanilla / Motion+, *Layout animations* (`animateLayout`, `data-layout-id`, early access) — <https://motion.dev/docs/layout-animations>
- Motion example, shared layout (vanilla `data-layout-id`) — <https://motion.dev/examples/js-shared-layout-animation>
- Motion example, AnimatePresence modes — <https://motion.dev/examples/react-animate-presence-modes>
- `popLayout` + parent `layout` offset-parent bug — <https://github.com/motiondivision/motion/issues/3026>
- Paul Lewis, *FLIP Your Animations* — <https://aerotwist.com/blog/flip-your-animations/>
- CSS-Tricks, *Animating Layouts with the FLIP Technique* — <https://css-tricks.com/animating-layouts-with-the-flip-technique/>
- Figma, *How we built spring animations* (ζ, stiffness) — <https://www.figma.com/blog/how-we-built-spring-animations/>
- Android developers, *Spring animation* (under/critical/over damped) — <https://developer.android.com/develop/ui/views/animations/spring-animation>
- Alex Mayhew, *Atmospheric Animations: The Physics of Framer Motion* — <https://alexmayhew.dev/blog/atmospheric-animations-framer-motion>

### 17.3 UX / a11y / watery (shared with `10` / `13`)

- Nielsen Norman Group, *The Role of Animation and Motion in UX* — <https://www.nngroup.com/articles/animation-purpose-ux/>
- Nielsen Norman Group, *Animation for Attention and Comprehension* — <https://www.nngroup.com/articles/animation-usability/>
- Jakob Nielsen, *Response Time Limits* — <https://www.nngroup.com/articles/response-times-3-important-limits/>
- Apple HIG, *Motion* — <https://developer.apple.com/design/human-interface-guidelines/motion>
- WWDC23, *Design considerations for vision and motion* — <https://developer.apple.com/videos/play/wwdc2023/10078/>
- MDN, `clip-path` — <https://developer.mozilla.org/en-US/docs/Web/CSS/clip-path>
- MDN, `prefers-reduced-motion` — <https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion>
- Chrome, *Smooth transitions with the View Transition API* — <https://developer.chrome.com/docs/web-platform/view-transitions/>
- WAI-ARIA APG, Tabs — <https://www.w3.org/WAI/ARIA/apg/patterns/tabs/>
- W3C, WCAG 2.2 SC 2.3.3 / 2.2.2 / 1.4.1; technique C39
- Lucas Bebber, *The Gooey Effect* — <https://css-tricks.com/gooey-effect/>
- Temani Afif, *A Sliding “Liquid Oozing” Reveal* — <https://css-tip.com/sliding-liquid/>

---

## 18. Open questions (do not answer by inventing)

1. Recipe A vs B — Origin picks one. This file prefers **B** if they can drop the outer remount (inner `popLayout` already exists); **A** if they must ship a pour this week. `13` left it open; still open.
2. After Granola access: did a meeting already ban springs on the hairline? Until then, live `springSoft` stays the token.
3. Will Featured stay a client filter on `/`, or should chips push `/c/*`? Pour is same-document; a route change needs VT names, not `filterSlide`.
4. Livestream **days** still unlocked (`01`). Motion cannot invent Sunday/Monday.
5. Kelly Ying home timed out this pass — do not invent new steal cues.
6. `ProductGrid` empty string is English-only (`Nothing in this collection yet.`). Copy bank is `12`; do not invent VN from memory unless `13`’s pair is used as-is.

---

## 19. PASTE INTO ORIGIN AGENT (do not paraphrase)

Copy everything between the markers into a Cloud Agent on the **Origin `sassy-closet-shop` repo** (the git behind https://sassy-closet-shop.vercel.app). Not this kit. Not intake `sassy-closet/`. Not `excel-kit/`. Not Origin shop `main` — sell-test / a shop feature branch only.

This paste **refines** LEARN 13’s watery brief with spring math, `layoutScroll`, and the double-`AnimatePresence` diagnosis. Do not ship 13 and 20 as two restyles. One FeaturedBoard pass.

```text
===== BEGIN ORIGIN PASTE — FeaturedBoard springs + watery tabs (LEARN 20) =====

You are editing Origin sassy-closet-shop. Ship SHARED-ELEMENT SPRINGS + WATERY
TAB / GALLERY POUR on the EXISTING FeaturedBoard. Do not restyle. Do not invent
mã. Do not add iOS liquid glass. Do not install Motion+ / GSAP Flip / Motion One
as a second runtime. Stay on motion/react. Do not touch intake or Excel.

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
Do NOT layoutId="product-{MA}" (that string is a View Transition name).

FIND FILES (rg — names may differ; match these strings, then edit those files):

  rg -n "featured-tab|Filter featured collection|springSoft|filterSlide"
  rg -n "AnimatedProductGrid|FeaturedBoard|ProductGrid|tab-scroll|replay"
  rg -n "useReducedMotion|layoutId|mode:\\\"wait\\\"|popLayout"
  rg -n "announce-fade|shimmer-slide|--duration-enter|--gold:"

Expected (live 2026-09-09 chunk 3_93acjqq2t4q.js + 34vl_zddoo4ws.css):
  import from motion/react (NOT motion-plus)
  springSoft = { type: "spring", stiffness: 420, damping: 32, mass: 0.72 }
    physics: ζ ≈ 0.92, ωn ≈ 24 rad/s, settle ≈ 180ms — KEEP
  filterSlide(reduced, dir):
    motion on:  enter x:28*dir 0.32s ease [.22,1,.36,1]
                exit  x:-22*dir 0.22s
    reduced:    duration 0
  FeaturedBoard click b(next): dir = index(next) >= index(cur) ? 1 : -1
  Gold rule: layoutId="featured-tab" (undefined when reduced)
  AnimatedProductGrid: AnimatePresence mode="wait" + motionKey=selected
                       + ProductGrid replay={true}   ← THIS IS THE 540ms+stagger bug
  ProductGrid: inner AnimatePresence mode="popLayout"; li layout + fadeUp + springSoft
  tab-scroll: overflow-x-auto, NO layoutScroll
  :root --paper --ink --gold --gold-deep --blush --duration-enter:.21s
        --duration-exit:.15s --duration-move:.4s

If a file is missing, create the smallest new file next to FeaturedBoard —
do not invent a second design system.

────────────────────────────────────────
FIX 1 — Gold meniscus (shared layoutId + springSoft)
────────────────────────────────────────
KEEP:
  className="absolute inset-x-0 bottom-0 h-px bg-gold"
  layoutId={!reduced && "featured-tab"}
  transition={springSoft}   // destination transition wins

DO:
  1. While the rule travels (motion on only), stretch scaleX ~1 → 1.15 → 1
     so it reads as a pulled gold film, then flush under the new label.
     NEVER scaleY / h-1 / rounded-full / glass. One overshoot max
     (ζ 0.92 already provides it — do not drop damping).
  2. Phone: wrap .tab-scroll in <motion.div layoutScroll> so FLIP accounts
     for scrollLeft. Do not put layout on the scroller.
  3. OPTIONAL trail: layoutId="featured-tab-trail" (DIFFERENT id)
     class "absolute inset-x-0 bottom-0 h-px bg-gold/30"
     same spring + delay 0.04; opacity 0 after settle.
  4. OPTIONAL goo on a WRAPPER THAT CONTAINS ONLY the rule (+ trail):
     SVG filter id="ky-gold-goo" (Bebber): stdDeviation 6, alpha 18 -7.
     NEVER on tablist, buttons, or images. Reduce Motion → filter:none.
  5. OPTIONAL LayoutGroup id="featured-tabs" around THIS tablist only.
  6. Do NOT use transition.layout.path = arc() (lifts the hairline).
  7. Do NOT put springSoft on opacity of the 11px labels.

────────────────────────────────────────
FIX 2 — APG tabs (springs do not replace a11y)
────────────────────────────────────────
Live: role="tablist" aria-label="Filter featured collection"
      buttons role="tab" aria-selected — NO aria-controls, NO tabpanel.

DO:
  1. id on the grid wrapper; each tab aria-controls that id.
  2. Grid wrapper: role="tabpanel" aria-labelledby=active tab.
  3. Left/Right (+ Home/End) move focus; auto-activate (ten SKUs in memory)
     OR Space/Enter if you cannot keep pour ≤200ms.
  4. Do not steal Up/Down (page scroll).
  5. scrollIntoView({ inline: "nearest", block: "nearest" })
  6. Counts stay: All 10, Tops 2 (A01+A02), Sets 1, Accessories 5
     (P01–P05, P02+P05 Hold), Jackets 1, Hair 1. No new chips.

────────────────────────────────────────
FIX 3 — Gallery: pick A or B (not both)
────────────────────────────────────────
DIAGNOSIS: outer wait remounts ProductGrid (motionKey) so inner popLayout
never FLIPs remainers. replay={true} re-runs staggerChildren 0.07 × n
(~740ms) on every tab. That is why it feels like a new page.

PICK ONE:

  A) POUR (keep AnimatedProductGrid remount).
     Keep name filterSlide + ease [.22,1,.36,1] + dir from b().
     Tween clipPath inset from the incoming side (28%) + x: 8*dir
       → inset(0) + x:0 in ~180ms (tween, NOT springSoft).
     Exit clip toward outgoing side + x: -6*dir in ~80–120ms.
     Prefer mode="sync" with both panels position:absolute; inset:0
       inside overflow-hidden so enter/exit overlap.
     If you keep mode="wait", exit+enter MUST sum ≤200ms.
     Pass replay={false} on Featured ProductGrid (no stagger on filter).
     Reduced: clipPath inset(0), x:0, duration 0.

  B) IN-PLACE FLIP (preferred if you can delete the outer remount).
     Drop motionKey wait + filterSlide x/clip.
     One ProductGrid; filter the array.
     Each li: layout + layoutId={`tile-${ma}`} + springSoft on layout
       + opacity tween 80–120ms enter/exit.
     Cover box: layout="position" (do not squash 3:4 JPEGs).
     ul: position relative (popLayout offset parent).
     forwardRef the tile component to the li if exits jump.
     Optional LayoutGroup id="featured-grid".
     Do NOT also run wrapper translateX / clip pour.

FORBIDDEN: A+B together.
FORBIDDEN: staggerContainer on Featured tab changes.
FORBIDDEN: springSoft on clip-path.
CollectionList stagger (0.07) stays on the home mosaic / first /c/* paint.

Empty /c/quan and any 0-count tab: copy only — keep
"Nothing in this collection yet." or 13’s pair
"Chưa có quần trên lookbook" / "No pants listed".
No shimmer skeletons. No Q01.

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
  html:after full-page shape() liquid
  --duration-move:.4s as the tab clock
  cart / bag-fly / liquid-into-bag
  document.startViewTransition around Featured filter
  layoutId strings that match view-transition-name (product-A01 etc.)

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
- Do not add motion-plus / GSAP.

────────────────────────────────────────
VERIFY (you click these; do not skip)
────────────────────────────────────────
Desktop + phone (scroll the chips) + OS Reduce Motion + keyboard:

1. /  All→Tops→Accessories→All. Counts 10 / 2 / 5 / 10.
   Gold hairline stretches then settles ~180ms (motion) or jumps (reduced).
   P02+P05 Hold · Inbox for price. Arrows move tabs.
2. /  Phone: select a chip that was off-screen. Hairline comes FROM that
   chip (layoutScroll), not from the left edge of the scroller.
3. /  All→Hair vs Hair→All opposite directions.
   Rapid Tops→Accessories interrupts the spring (no VT snap).
   Perceived filter ≤200ms. No long white blank. No 10-tile stagger.
4. /c/ao = A01 $25 + A02 $22. /c/quan empty.
5. /m/A01 cover visible. Message A01 still opens
   facebook.com/profile.php?id=61594312648057
6. Reduce Motion: no stretch, no pour, no goo, no shimmer,
   no 1.08 zoom. Tabs + Message still work.
7. View-source / network: no e.tb.cn, no ¥, no A03, no V984.
8. Photos never go through #ky-gold-goo. Recipe B photos never squash.

Commit on an Origin cursor/* branch. Preview URL in the PR. Do not merge.

===== END ORIGIN PASTE =====
```

Mini Boss: copy the block above as the **entire** Origin prompt. Do not add “also make it more premium” or “add liquid glass.” The `layoutId` spring + one pour **or** in-place FLIP *are* the visual-FX pass. `10`’s five reliability fixes and `13`’s watery locks still apply if they are not on `main` yet — do not regress them.

End of 20.
