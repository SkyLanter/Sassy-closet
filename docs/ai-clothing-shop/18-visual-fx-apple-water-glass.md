# 18 — Visual FX: Apple color carousel, frosted-glass edge peeks, watery gallery roll

**Learn track:** Ultra burn (research + live as-built + APPLY).  
**Shop:** Sassy Closet — Facebook inbox is the store; Square Free is on-hand truth; sell-test lookbook is Origin-owned.  
**Live APPLY target:** [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)  
**Audience:** Mini Boss / Origin shop implementer.  
**Origin settings for the paste:** **Fast OFF**, **1B budget**.  
**Date researched / crawled:** 2026-09-09 (evening pass — later than `10` / `13`; **this crawl wins** on live cells).  
**This file does not assign stock, mint a mã, Save in Square, post to Facebook, restyle the boutique, copy Apple or Kelly Ying marketing, or touch Excel / intake.**

Sister `10` is the **general** motion law. Sister `13` is watery **Featured tabs + grid pour**. This note is the **PDP gallery**: how a color tap should **roll this mã’s photos** the way an Apple product page rolls finishes — with **frosted peeks at the rail edges**, not liquid glass over the garment. Kelly Ying *look* stays locked (`01` §1.3, §11; `10` §5). Fancy motion stays locked (`07` §11.0; `09` §0; `10` §2). Mini Boss pastes **§19** into Origin. Do not paraphrase §19 into “add iOS liquid glass” or “copy the iPhone page.”

---

## 0. How to read this document

This is a **learn-track** note, not a rebuild brief and not permission to fork Origin shop code from this kit repo.

- **Cite, don’t invent.** Shop-law claims point at a file, Slack permalink, sister learn-track, or the live host. Industry claims point at NN/G, W3C WCAG 2.2, WAI-ARIA APG, MDN, Chrome / WebKit scroll-driven notes, Apple HIG + WWDC25 *Meet Liquid Glass*, or named CSS specs. If a fact is missing, the gap is named.
- **Never invent a mã.** Customer-facing codes this pass may name are the **first-ten allowlist** only. Admin “Next mã A03” is a prediction. Slack `AO001` / `AO003` are **decision-template examples** (`#shop-decisions`, 2026-09-04), not live lookbook stock. Kelly Ying `V984.` / `V826.` are **their** SKUs. Apple finish names (Ultramarine, Desert Titanium, …) are **Apple’s**. Do not copy any of those onto Sassy tiles.
- **Two alphabets.** Sell-site / hub = `A01`. Official / Square / SoT = `AO001`. Motion never translates one into the other (`01` §9; `excel-kit/schema.py` `MA_RE`).
- **Facebook inbox is the store.** A “buy” is **Message {code}**. There is no cart. Watery motion that implies checkout (bag-fly, liquid pour into a cart) is a lie.
- **No stock copy.** Do not paste Apple slogans (“Pick your favorite”, “Five bold colors”), Kelly Ying livestream-day copy, or invented EN/VN product blurbs. Keep the live sentences already on `/m/A01` and `/m/P02`.
- **No redesign mandate.** Improve **inside** paper / ink / gold / blush, Cormorant Garamond + Be Vietnam Pro, `ma-mark`, `announce-fade`, `shimmer` / `shimmer-slide`, `cta-shine` / `cta-flash`, gold `h-px`, `ProductGallery`, `ColorSwatch`, `imagesForColor`, `coverSrc` / `coverSrcForColor`. Do not replace that language with iOS Liquid Glass over photography, Shopify Horizon, intake Allura/Nunito rose, or a new design system.

### 0.1 Research method (and what this pass could not see)

| Source | Result |
| --- | --- |
| Live sell-test HTML + CSS + JS of `/`, `/m/A01`, `/m/A02`, `/m/P01`, `/m/P02`, `/m/P03`, `/m/P04`, `/m/P05`, `/m/S01`, `/m/K01`, `/m/H01`, `/admin` (2026-09-09 evening) | Primary **as-built** gallery map. CSS `/_next/static/immutable/chunks/34vl_zddoo4ws.css`. Gallery chunk `/_next/static/immutable/chunks/1xr62vxitay1m.js` (exports `ProductGallery`, `ColorSwatch`, `ColorSwatchEmpty`, `ProductGrid`, `coverSrc`, `coverSrcForColor`, `imagesForColor`). Motion helpers still in `/_next/static/immutable/chunks/3_93acjqq2t4q.js`. |
| `curl -I` `/m/A03` | **404** / Next not-found. Invented mã still dead. |
| Repo `excel-kit/`, `sassy-closet/`, `README.md` | Shop law. Intake sheets are **behavior** only — do not restyle. |
| Sister LEARN TRACK PRs #19–#33 (`01`–`14`) | Headings + locks. This file is `18`. Concurrent FX notes (`13` watery tabs; iOS frosted carousel / CSS snap / springs) may land as `15`–`17` — **do not merge their jobs into this paste**. |
| Slack `#shop-decisions` (`C0BV3GYC602`) | Five standing messages (2026-09-04). No gallery-FX thread. |
| Linear | Keyword search returned no visual-FX issue. |
| Granola meetings | MCP unauthorized — no meeting notes. |
| Notion | Business-plan AI search unavailable; not used for shop law. |
| Kelly Ying Boutique public site | Cloudflare challenge this pass (`HTTP 403`, “Just a moment…”). Look / cadence facts stay with `01` + `10`. |
| Apple.com product / buy pages + WWDC25 *Meet Liquid Glass* | Fetched 2026-09-09. Used as **interaction grammar**, not copy or SKUs. |
| Public UX / a11y / CSS specs | Fetched 2026-09-09. URLs in §17. |

If a later crawl disagrees with a **live** cell here, **the new crawl wins** — update the date line. Shop law still wins over industry taste. Recorded hub color *names* in older kit samples (`kem`, `xanh`, …) do **not** override live Blob rows that store hex + empty `note`.

### 0.2 Sister docs

| # | File | Job vs this note |
| --- | --- | --- |
| 01 | `01-messenger-social-commerce.md` | Kelly Ying look lock; Message-first; no cart |
| 02 | `02-pdp-color-size-ux.md` | Customer **text** colors as *law* for patterns; gallery sync nouns |
| 04 | `04-per-color-product-media.md` | Admin **hex boxes**, no names on storefront; tag images |
| 05 | `05-ai-product-media.md` | Recorded first-ten names in an older sample — **do not chip them early** |
| 10 | `10-customer-pleasing-motion-ux.md` | General motion + lightbox + Reduce Motion |
| 13 | `13-watery-tab-slide-motion.md` | Watery **Featured tabs**, not the PDP rail |
| **18** | **This file** | **Apple-style color → gallery roll + frosted edge peeks** |
| Kit | `SELL_CATALOG_CONTRACT.md` (PR #18) | Allowlist + prices + Hold null `$` |

`02` (text chips) and `04` / live `ColorSwatch` (hex boxes, no names) **disagree**. Live 2026-09-09 evening **shipped hex boxes** on `/m/A01`. This FX pass **does not restyle chips into iOS finish dots or invent Vietnamese names**. It makes the **gallery roll honest**. A later copy pass may add stored `note` / name text; that is not this paste.

---

## 1. Executive summary

An Apple product page does not *blink* a new JPEG when you tap a finish. The **same object stays in the hand**: the gallery **rolls** to that finish, a sliver of the next shot **peeks**, and chrome at the edges **frosts** so the peek does not fight the hero. WWDC25 calls that chrome-vs-content split explicitly: Liquid Glass belongs on the **navigation / control layer**; putting it in the **content layer** muddies hierarchy ([WWDC25 — *Meet Liquid Glass*](https://developer.apple.com/videos/play/wwdc2025/219/); [HIG Materials](https://developer.apple.com/design/human-interface-guidelines/materials)).

Sassy Closet is a ten-SKU lookbook, not an iPhone buy flow. Steal the **grammar**, refuse the **catalog**:

| Apple grammar | Sassy meaning | Fail if… |
| --- | --- | --- |
| Finish picker updates the **same** product gallery | Color chip filters **this mã’s** `images[]` and **rolls** the rail to the first matching shot | `/products/A02/cover.jpg` appears on `/m/A01`; a new mã is minted “for the other color” |
| Neighbor slide **peeks** | When **this mã** has **>1 real 200 image**, the next/prev JPEG is ~8–14% visible | Fake peeks from another mã, Unsplash, or a CSS-tinted clone of the cover |
| Frosted **scroll-edge** | Paper-tinted `backdrop-filter` **strips on the rail chrome**, dissolving the peek | `backdrop-filter` / `feDisplacementMap` on the garment |
| Named finish + disc | Live chips are **hex boxes** (`04`); Apple **names** (“Ultramarine”) stay on apple.com | Inventing Kem / Xanh / Hoa from an older kit table onto empty `note:""` |

Live `/m/A01` (this crawl) already has the **nouns**: `ProductGallery`, `ColorSwatch`, `imagesForColor(product, colorId)`, `coverSrc` / `coverSrcForColor`. It does **not** yet have the **Apple job**:

1. **Color → gallery is a fake slide of the same JPEG.** A01 stores two hexes (`#F4F0E8`, `#1C2A4A`) and **one** image `{ src: "/products/A01/cover.jpg", colorId: null }`. `imagesForColor` with a selected id returns **[]**; the hero falls back to `coverSrc`, but `AnimatePresence` **remounts** because the key is `` `${colorId}-${src}` ``. The buyer watches a 280ms `x:24` wipe of the identical photo. That is downtime, not a finish change ([NN/G response times](https://www.nngroup.com/articles/response-times-3-important-limits/)).
2. **There is no rail, so there is nothing to peek.** One cover, `overflow-hidden`, click-to-cycle only if `f.length > 1` (never, today). Dots are `h-1.5 w-1.5` (6px) — not a gallery.
3. **Glass already exists on chrome, not on the hero.** Sticky Message bar: `bg-paper/95 backdrop-blur-md`. Header: opaque `bg-paper` + `opacity: 0.92` fill — **not** `backdrop-filter`. APPLY extends **edge frost** in that paper language. It does not iOS-capsule the hero.
4. **No APG carousel.** No `role="region"` / `aria-roledescription="carousel"`, no prev/next, no auto-rotate (good). Click-on-image is a hidden control.

Reliability still beats beauty. A frosted peek that shows P02 on A01, a 700ms liquid wipe that hides Hold, or a displacement filter that “wets” the cloth is a **failed** boutique.

---

## 2. Hard constraints (print these on the implementer’s wall)

1. **Never invent a mã.** Emit list is exactly `A01 S01 P01 P02 P03 P04 P05 K01 H01 A02` (PR #18). `/m/A03` stays 404. Empty `/c/quan` stays empty. No `Q01` “so the carousel has another slide.”
2. **Never invent qty, $, photos, hex, or color names.** Hold P02 / P05 = **Inbox for price**. Empty `colors[]` = **no chip row**. Empty `note` stays empty — do not print Kem / Xanh / Hoa / Cham-bi from `05` onto the live row. Do not invent `/products/A01/001.jpg` because an older OneDrive table listed it (`10`).
3. **Square Free = on-hand truth.** Official Excel is a working copy (`README.md`). This kit does not edit Excel or intake in this pass.
4. **Bots draft only.** No Square Save, no Facebook Post/Send (`#shop-decisions` 2026-09-04).
5. **No cart, Shop now, or bag-fly.** Kelly Ying’s **$10 / $300+** and `V###` codes are **theirs** (`01` §0). Apple’s “Buy” / carrier copy stays on apple.com.
6. **Customer color is not a new SKU.** Qty is 1. Colors are **how this one piece photographs**. Do not mint `A01-RED` (`04`).
7. **Motion never changes identity.** Same mã in, same mã out. `product-A01` morphs only to A01. Gallery arrows never wrap to A02.
8. **Water / glass never lies on the photo.** No `filter: url(#goo)`, no `feDisplacementMap`, no chromatic aberration on `.shimmer`, covers, or heroes. Distortion is a **fabric lie**. Frost lives on **edge chrome** only.
9. **No stock copy.** Do not replace live EN/VN sentences with Apple or boutique-template blurbs.
10. **Origin owns the pixels.** APPLY is for the Origin agent on `sassy-closet-shop`. Intake Production stays https://sassy-closet.vercel.app. This PR does not edit `excel-kit/` or `sassy-closet/`.

---

## 3. What to steal from Apple (and what this closet is not)

### 3.1 Color carousel — finish picker, not a second product

Apple’s marketing and buy pages treat **finish** as a gallery state of **one** model: tap Ultramarine → the hero / carousel shows that finish; the URL and price may change because Apple sells **inventory of that finish**. Sassy sells **one unique piece**. The picker may only change **which photos of A01** are in the rail.

Industry default (Shopify) is the failure mode we refuse: mixed gallery, theme scrolls to “the” variant image, the rest stay ([Craftshift, *Shopify variant images*](https://craftshift.com/shopify-variant-images-complete-guide/); `02` §5.5). Sell-test rule (`02` / `04` / `10` §8): selecting a color **replaces** the visible set with photos tagged to that color (or untagged shared shots). If none, keep the cover / empty paper — **never** another mã’s folder.

Apple-like **roll** (this paper’s add): when the filtered set has **more than one real file**, do not `mode="wait"` cross-fade a single `<img>`. Put the set in a **horizontal snap rail** and `scrollIntoView` the first tagged slide. Native scroll physics beat a JS `x:24` ([MDN `scroll-snap-type`](https://developer.mozilla.org/en-US/docs/Web/CSS/scroll-snap-type); [web.dev, *Well-controlled scrolling with CSS scroll snap*](https://web.dev/articles/css-scroll-snap)).

### 3.2 Frosted glass edge peeks — chrome, not cloth

WWDC25: **scroll edge effects** dissolve content as it moves under floating controls so titles stay clear; use **Regular** glass for legibility; **Clear** only over media-rich content with a dimming layer and bold foreground; **never mix** variants; **never glass-on-glass**; **never glass in the content layer** (tableviews, the photos themselves). Reduced Transparency makes glass **frostier**; Reduced Motion kills elastic lensing ([WWDC25](https://developer.apple.com/videos/play/wwdc2025/219/); [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)).

Web approximation (not an OS port):

| Layer | CSS | Role |
| --- | --- | --- |
| Peek | Slide `flex-basis` ~86–92% + `scroll-snap-align: center` | Neighbor JPEG is partially on-screen ([CodeFronts snap carousel](https://codefronts.com/components/css-image-slider/scroll-snap-touch-image-carousel/); [W3Tweaks peeking carousel](https://www.w3tweaks.com/css/css-scroll-snap-explained/)) |
| Edge fade | `mask-image: linear-gradient(90deg, transparent, #000 var(--fade), #000 calc(100% - var(--fade)), transparent)` on the **rail** or on **edge overlays** | Soft cut instead of a hard crop ([MDN `mask-image`](https://developer.mozilla.org/en-US/docs/Web/CSS/mask-image); [Pqina overflow fade](https://pqina.nl/blog/fade-out-overflow-using-css-mask-image/)) |
| Frost | `backdrop-filter: blur(10–16px) saturate(140%)` + `background: color-mix(in srgb, var(--paper) 50–70%, transparent)` on **left/right strips only** | Regular-ish paper glass. Live sticky bar already uses `backdrop-blur-md` + `bg-paper/95` ([MDN `backdrop-filter`](https://developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter)) |

**Refuse** SVG `feDisplacementMap` as `backdrop-filter: url(#liquid)` on the hero. That is Chromium-only “true refraction,” expensive, and it **warps the garment** ([kube.io](https://kube.io/blog/liquid-glass-css-svg/); [WebTricks](https://webtricks.dev/blog/liquid-glass-css); [rizroze/liquid-glass](https://github.com/rizroze/liquid-glass)). Sister `13` already banned goo on photos. This note bans it on the **gallery content layer** too.

MDN: a parent with `opacity < 1`, `filter`, `mask`, or `clip-path` becomes a **backdrop root** and the blur only samples inside that parent. Do not put `opacity: 0.92` (header trick) on the rail wrapper or the edge frost will sample nothing useful.

### 3.3 Liquid / watery transitions — viscosity on the rail, not a 6s veil

Watery *for this gallery* is three physical metaphors, all gold-on-paper:

| Metaphor | Buyer should feel | Fail if… |
| --- | --- | --- |
| **Roll** | Color tap **scrolls** the existing rail to that finish’s first shot | `mode="wait"` blanks the hero; same JPEG wipes itself |
| **Meniscus at the chip** | Selected `ColorSwatch` keeps `outline-ink` (live) + optional gold `h-px` under the row — not a fat iOS capsule | New pill language; glass blob under 11px type |
| **Viscosity** | Snap + `scroll-behavior: smooth` only when motion is allowed; springy settle from the UA | 540ms wait (`13`’s Featured bug) copied onto the PDP |

NN/G: animation is for **feedback, state-change, spatial metaphor, signifier** — not delight ([*The Role of Animation and Motion in UX*](https://www.nngroup.com/articles/animation-purpose-ux/)). Cause and effect within **0.1s** ([*Animation for Attention*](https://www.nngroup.com/articles/animation-usability/)). **0.1 / 1 / 10s** clocks ([Nielsen](https://www.nngroup.com/articles/response-times-3-important-limits/)). A color tap is frequent: budget **≤200ms perceived** (`10`), same as Featured.

Apple HIG Motion: do not make people wait for frequent animation; Reduce Motion replaces large spatial moves with a **crossfade or instant** ([HIG — Motion](https://developer.apple.com/design/human-interface-guidelines/motion); [Reduced Motion criteria](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria/)). WWDC23: sustained oscillation is a comfort risk ([WWDC23 10078](https://developer.apple.com/videos/play/wwdc2023/10078/)).

CSS `shape()` liquid wipes and 6s full-page reveals ([Temani Afif / CSS Tip](https://css-tip.com/sliding-liquid/)) stay **refused** as a gallery clock (`13` §3.3). Optional: a **≤8px** clip-path wave on the **leading edge of a slide enter**, `@supports`, Reduce Motion off, ≤180ms — never on the JPEG pixels.

### 3.4 Technique catalog (use / refuse)

| Technique | Source | Use on sell-test PDP? |
| --- | --- | --- |
| Native `overflow-x` + `scroll-snap-type: x mandatory` + peek width | MDN; web.dev; CodeFronts; W3Tweaks | **Yes**, when `imagesForColor` length > 1 |
| `scroll-behavior: smooth` + `scrollIntoView({ inline: "center" })` on color tap | MDN; APG (real scrolling brings slides on-screen) | **Yes** if `!useReducedMotion()`; else `auto` / `instant` |
| `mask-image` edge fade | MDN; Pqina; CodeFronts | **Yes** on rail or edge overlays |
| Paper `backdrop-filter` edge strips | MDN; live sticky bar; WWDC Regular glass | **Yes**, chrome only; gate with `prefers-reduced-transparency` |
| Keep `ColorSwatch` hex boxes | Live; `04` | **Yes**. Do not invent names. Do not switch to Apple circular finishes. |
| `imagesForColor` / `coverSrcForColor` | Live chunk `12573` | **Keep names.** Fix empty-filter remount. |
| `AnimatePresence mode="wait"` + `x:24` | Live `ProductGallery` | **Refuse as the color clock.** Keep opacity crossfade only when **src actually changes** and length === 1 |
| SVG goo / displacement on photos | Bebber; kube.io; WebTricks | **Refuse** |
| WebGL cloth / cursor metaballs / canvas image-sequence Apple hero | CSS-Tricks 2020 canvas scrub; Geyer 2024 | **Refuse** (`10` anti-pattern). We do not have 120 finish frames. |
| Auto-rotating carousel | APG | **Refuse.** No auto-play. |
| Full-viewport Liquid Glass / glass-on-glass | WWDC25 | **Refuse** |
| Featured `filterSlide` / `featured-tab` goo | `13` | **Out of scope.** Do not retune tabs in this paste. |

---

## 4. As-built hook map (cite the live host)

Crawl: 2026-09-09 evening. HTML on `/m/A01`. CSS `34vl_zddoo4ws.css`. JS `1xr62vxitay1m.js` (modules `8883` ProductGallery, `9040` ColorSwatch, `12573` media helpers, `46072` ProductGrid).

### 4.1 CSS tokens (do not rename)

```css
:root {
  --canvas: #fff;
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

`--canvas` is **new vs `10`/`13`** (same `#fff` as `--paper`). Fonts on `<html>`: `be_vietnam_pro_…__variable` + `cormorant_garamond_…__variable`.

Existing keyframes — **keep names** (`10` FIX 1):

```css
@keyframes announce-fade { 0%,12%{opacity:0} 20%,80%{opacity:1} 92%,to{opacity:0} }
@keyframes shimmer-slide { 0%{background-position:120% 0} to{background-position:-20% 0} }
@keyframes cta-flash { to{transform:translate(120%)} }
```

Reduced-motion query still kills announce / shimmer / cta / `::view-transition-*`. It still does **not** kill card `scale-[1.08]` (`10` MOT-03). **No** `prefers-reduced-transparency` rule in the chunk. **No** `mask-image`, **no** `scroll-snap`.

View transitions (unchanged):

```css
::view-transition { pointer-events: none }
::view-transition-group(site-header) { z-index: 100; animation: none }
::view-transition-old(site-header) { display: none }
::view-transition-new(site-header) { animation: none }
```

`--duration-enter` / `--duration-exit` / `--duration-move` are declared; `ProductGallery` **ignores them** (hard-coded `0.28s`). APPLY may bind rail CSS to `--duration-enter` (≤210ms). Do not invent `--liquid-500ms`. Do not use `--duration-move: .4s` as the color clock (`13` §12).

### 4.2 Header vs sticky Message (glass already in chrome)

| Surface | Live classes | Glass? |
| --- | --- | --- |
| Announcement bar | `h-8 bg-ink text-paper` + `.announce-fade` | No |
| Header | `sticky top-0 z-50 border-b border-line bg-paper` + inner `bg-paper` `opacity: 0.92` | **Fake frost** (alpha fill). Not `backdrop-filter`. `view-transition-name: site-header` |
| Category nav | `h-10 overflow-x-auto` gold `h-px` on hover | Hairline, not glass |
| PDP sticky footer (`md:hidden`) | `border-t-2 border-gold/45 bg-paper/95 backdrop-blur-md` | **Yes — Regular-ish paper glass.** Keep. |
| Shop-tools FAB | `h-8 w-8` gold dot | Untouched |

Edge peeks should **rhyme** with the sticky footer (`paper/95` + `blur-md`), not with iOS capsules. Do not add a second glass sheet **on top of** the sticky bar (WWDC: no glass-on-glass).

### 4.3 `ProductGallery` (reconstructed from `1xr62vxitay1m.js`)

```js
function ProductGallery({ product }) {
  const reduced = useReducedMotion();
  const [colorId, setColorId] = useState(null); // null = all
  const [index, setIndex] = useState(0);
  const shots = imagesForColor(product, colorId);
  const cover = coverSrc(product);
  const i = shots.length === 0 ? 0 : Math.min(index, shots.length - 1);
  const src = shots[i]?.src ?? cover;

  // hero: AnimatePresence mode="wait"
  // motion: enter { opacity: 0, x: 24 } unless reduced
  //         exit  { opacity: 0, x: -18 } (reduced: opacity only)
  //         duration: 0.28 * !reduced, ease [.22, 1, .36, 1]
  // key: `${colorId ?? "all"}-${src ?? "none"}`
  // img onClick: if shots.length > 1 → setIndex((n) => (n + 1) % length)
  // dots if length > 1: h-1.5 w-1.5, aria-label={`Image ${n+1}`}
  // chips if product.colors.length > 0: ColorSwatch; click toggles id, resets index to 0
}
```

Helpers (module `12573`) — **keep export names**:

```js
function coverSrc(product) {
  return product.images.find((img) => img.src.trim())?.src;
}
function imagesForColor(product, colorId) {
  const n = product.images.filter((img) => img.src.trim());
  return colorId === null ? n : n.filter((img) => img.colorId === colorId);
}
function coverSrcForColor(product, colorId) {
  const n = imagesForColor(product, colorId);
  return n[0] ? n[0].src : coverSrc(product);
}
```

**Honesty bug:** when `colorId` is set and no image has that `colorId`, `imagesForColor` returns `[]`, `src` falls back to `coverSrc`, but the **key still changes**, so `wait` plays a directional slide of the **same file**.

`ColorSwatch` (`9040`):

- `h-6 w-6` (`md`) `rounded-sm border border-black/20`
- Selected: `outline outline-2 outline-offset-2 outline-ink`
- `aria-pressed`, `aria-label={title ?? `Color ${hex}`}`, `title={title ?? hex}`
- `ColorSwatchEmpty`: dashed “No color” + diagonal mute rule (admin-ish; **not** on live A01)

WCAG [1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html): selected is **outline + aria-pressed**, not hue alone — live already does this. WCAG [2.5.8 Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html): `h-6 w-6` is **exactly 24px**. Dots at `h-1.5` **fail**. This pass: if a rail ships, dots become ≥24px **or** are replaced by APG prev/next (preferred). Do not “fix” chips into 44px Apple discs in this paste unless you also keep the hex fill and the 11px tracking row — chip restyle is **out of scope**.

### 4.4 Live color / image matrix (this crawl — do not invent)

PDP `ProductGallery` `colors[]` / `images[]` from RSC:

| mã | Status | `$` | `colors[]` on **this** PDP | `images[]` | Article chip row |
| --- | --- | --- | --- | --- | --- |
| **A01** | Available | $25 | Two: `cb3d45c1231ab` `#F4F0E8` `note:""` · `c4b0be6de43a3` `#1C2A4A` `note:""` | `cover.jpg` `colorId: null` | **Yes** — two hex boxes, both `aria-pressed="false"` (selected starts `null`) |
| A02 | Available | $22 | `[]` | `cover.jpg` `colorId: null` | No |
| S01 | Available | $28 | `[]` (no chips in article) | `cover.jpg` | No |
| P01 | Available | $5 | `[]` | `cover.jpg` | No |
| **P02** | **Hold** | Inbox for price | `[]` | `cover.jpg` | No |
| P03 P04 | Available | $18 / $13 | `[]` | `cover.jpg` | No |
| **P05** | **Hold** | Inbox for price | `[]` on this PDP article | `cover.jpg` | No |
| K01 | Available | $37 | `[]` | `cover.jpg` | No |
| H01 | Available | $8 | `[]` | `cover.jpg` | No |

Hex buttons **elsewhere** on accessory PDPs / home are **related-card / grid** `ColorSwatch` previews for rows that have colors (A01 on home + `/m/A02` related). Do not treat those as “P01 has four finishes.” P01’s own gallery `colors: []`.

A01 hero still has **no** `view-transition-name: product-A01` (related rail names `product-A02`). That is `10` FIX 3 — **do not regress**; this paste may add the name on the **rail’s current slide wrapper**, not on a neighbor tile.

Lightbox: still **no** `role="dialog"` on A01. Click-cycle is not a lightbox. `10` owns the enlarge dialog. This paste must not invent a second overlay. If `10` already shipped a lightbox on Origin `main`, **reuse it**; gallery set = current color filter.

### 4.5 A01 copy (do not rewrite)

Live `/m/A01`:

- Title `A01 · Top · Sassy Closet`; `robots: noindex, nofollow`
- `1 piece · Message to buy. No cart.`
- EN: “One unique top on hand. Message A01 for real photos and size.”
- VN: “Áo độc bản — một chiếc đang có.”
- CTA: Message A01 → `https://www.facebook.com/profile.php?id=61594312648057`

P02 stays Hold / inbox-for-price copy. No USD. No Apple “From $799”. No Kelly Ying shipping sentence.

---

## 5. Kelly Ying look — steal the rhythm, refuse the glass OS

`01` / `10` already locked the steal list. Cloudflare blocked a fresh fetch this pass. For this FX note:

| Cue | Steal? |
| --- | --- |
| Paper / ink / gold hairline / 11px tracking / SKU-on-card | **Yes** |
| Hex finish chips under the photo (`04` + live A01) | **Yes — keep.** Apple circular named finishes are **not** the look. |
| Editorial crop | **Yes** — clip the **frame**; do not displace JPEG pixels |
| Cart · Checkout · $10 / $300+ · `V###` | **No** |
| iOS-26 Liquid Glass over the hero | **No.** Paper stays paper. Frost = **edge strips** + existing sticky bar |
| Apple “Five bold colors” / Photographic Styles copy | **No** |

---

## 6. Reliability law (water and glass must not lie)

Same ten laws as `10` §6 / `13` §6, plus gallery-specific:

1. **Hold remains a word** while the rail rolls. Frost must not recolor Hold → Available (`09` MOT-08; WCAG 1.4.1).
2. **Color tap never changes mã, $, or route.** A01 stays A01 at $25.
3. **Empty filter ≠ borrowed folder.** `imagesForColor` empty → keep `coverSrc` **without** a wait-slide remount. Do not pull A02.
4. **No second shimmer** during a color roll. `.shimmer` is cover-load sheen (`10` §12).
5. **Peeks require a second real 200.** If only `cover.jpg` exists, there is **no peek**. Do not CSS-scale a ghost duplicate.
6. **Arrows never wrap across mãs.** A01’s last slide does not become A02.
7. **`::view-transition { pointer-events: none }` stays.** Edge overlays are `pointer-events: none` so Message taps work (`10` MOT-05).
8. **Same data, every surface.** Home A01 card swatches = `/m/A01` chips = admin row (`09` NAV-09). Do not show chips on A02’s gallery while A02 `colors: []`.

---

## 7. Color carousel (the finish picker)

### 7.1 What is already correct

- `colors.length === 0` → **no row**. A02 / P02 / … are honest.
- Toggle-off (click selected id → `null`) returns to the full unfiltered list.
- `aria-pressed` + ink outline on the selected hex.
- Light hex `#F4F0E8` has `border-black/20` so it does not vanish on `--paper` (`04`).
- `useReducedMotion()` already zeros the **x** offset (exit becomes opacity-only).

### 7.2 What is not Apple, and not boutique

1. **Remount of the same `src`.** Fix the key: key from **src + index**, not from color id when src is unchanged. Skip `AnimatePresence` when `prevSrc === nextSrc`.
2. **No roll.** Apple’s picker **moves the gallery**, it does not play a 280ms page-slide of one frame. When length > 1, native snap + `scrollIntoView`.
3. **Selected starts `null`.** Both A01 chips render `aria-pressed="false"`. Optional APPLY: if every image is untagged, **do not imply** a finish is “on” — `null` is honest. Do not auto-select the first hex just to look like Apple’s default finish.
4. **No name.** Live `note:""`. Do not invent Kem. If admin later stores a note, `ColorSwatch` already accepts `title` — pass `note` only when non-empty (`04`: names still not required on the box).

### 7.3 APPLY recipe (keep `ColorSwatch`)

Keep the live button chrome. On color activate:

```js
onClick={() => {
  setColorId((cur) => (cur === id ? null : id));
  setIndex(0);
  // after paint: if rail exists, slide[0].scrollIntoView({
  //   inline: "center", block: "nearest",
  //   behavior: reduced ? "instant" : "smooth",
  // })
}}
```

Bind `imagesForColor` as today. If you add a fallback for untagged images, **document it**: e.g. `colorId == null` shots stay visible for every finish (shared flats). Live helper does **not** include shared shots when a color is selected (`filter colorId === t` only). Changing that is a **data policy** change: prefer **admin tagging** over silently showing the cover as if it were `#1C2A4A`. Visible empty: keep cover, **no motion**, optional muted line that already exists (“Message A01 for real photos”) — do not add new stock copy.

---

## 8. Frosted glass edge peeks

### 8.1 When peeks are legal

| Images in the **current filter** | Peek + frost | Motion |
| --- | --- | --- |
| 0 | Paper empty / blush box (live) | None |
| 1 | **No peek.** Full-bleed hero as today | Color change: **no** wait-slide if src unchanged; 150–250ms opacity only if src changed (`10`) |
| ≥2 (all 200 on **this** host, **this** mã) | Peek + edge frost | Native snap roll |

Do not pad the rail with a second copy of `cover.jpg` to “force a peek.”

### 8.2 Rail (smallest Apple-like structure)

```css
.ky-gallery-rail {
  display: flex;
  gap: 0.75rem;
  overflow-x: auto;
  overscroll-behavior-inline: contain;
  scroll-snap-type: x mandatory;
  scroll-padding-inline: 7%;
  scrollbar-width: none;
}
.ky-gallery-rail::-webkit-scrollbar { display: none; }
.ky-gallery-slide {
  flex: 0 0 86%;
  scroll-snap-align: center;
}
@media (prefers-reduced-motion: reduce) {
  .ky-gallery-rail {
    scroll-snap-type: none;
    scroll-behavior: auto;
  }
}
```

86% column ≈ **7% peek** per side when centered (W3Tweaks / CodeFronts). Phone: 88–90% if 86% feels sparse. `scroll-padding-inline` keeps the snap out from under frost strips.

Markup: `role="region"` `aria-roledescription="carousel"` `aria-label="A01 photos"` (label **without** the word “carousel” — APG). Each slide `role="group"` `aria-roledescription="slide"` `aria-label="1 of N"` if no unique caption. **No auto-rotate.** Prev/next **buttons** (not image-click-only). ([APG Carousel](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/))

### 8.3 Edge frost (Regular paper, not Clear iOS)

Two `pointer-events: none` strips, 8–12% wide, left and right of the rail viewport (not inside each JPEG):

```css
.ky-gallery-edge {
  position: absolute;
  inset-block: 0;
  width: 10%;
  z-index: 2;
  pointer-events: none;
  background: color-mix(in srgb, var(--paper) 58%, transparent);
  backdrop-filter: blur(12px) saturate(140%);
  -webkit-backdrop-filter: blur(12px) saturate(140%);
}
.ky-gallery-edge[data-side="left"] {
  left: 0;
  mask-image: linear-gradient(to right, #000 40%, transparent);
}
.ky-gallery-edge[data-side="right"] {
  right: 0;
  mask-image: linear-gradient(to left, #000 40%, transparent);
}
@media (prefers-reduced-transparency: reduce) {
  .ky-gallery-edge {
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
    background: var(--paper);
    opacity: 0.92;
  }
}
```

Rhyme with live sticky `backdrop-blur-md` + `bg-paper/95`. Optional 1px `inset` highlight in `rgb(255 255 255 / 0.35)` on the **inner** edge of the strip (WebTricks rim) — **not** a chromatic fringe.

**Do not** put `backdrop-filter` on the `<img>`. **Do not** wrap the rail in `opacity: 0.92` (backdrop root trap). **Do not** frost the sticky Message bar a second time.

First/last slide: hide or fade the outer edge so the first JPEG is not eaten ([Shadcnblocks masked carousel note](https://www.shadcnblocks.com/block/case-studies10) — pattern only, not a component install).

### 8.4 Header sticky vs rail

Header is already a paper lid. Do not add a WWDC **hard** scroll-edge on the PDP header in this paste. Optional later: when the gallery is **not** the thing scrolling under the header (page scroll is vertical), a header blur is a **different surface** — out of scope (`10` header VT already locked).

---

## 9. Liquid / watery gallery roll

### 9.1 Color tap (the Apple moment)

| Motion on | Reduce Motion |
| --- | --- |
| `scroll-behavior: smooth` to first shot of that color; UA snap settle | Instant `scrollTo` / `behavior: "instant"`; no offset animation |
| Chip outline updates in ≤100ms (live CSS outline is instant) | Same |
| If src set is **identical** | **Zero** motion |

If length === 1 and src **changes** (admin tagged a different cover): 150–250ms **opacity** crossfade only (`10` §8.3). No `x:24`. No clip-path page-turn.

### 9.2 Slide-to-slide (swipe / arrows)

Native overflow scrolling is the watery material — momentum, rubber-band, trackpad. Do **not** overlay Framer `x: 24` on every snap (double motion). Optional `animation-timeline: view(inline)` scale 0.96 → 1 on the centered slide ([css-scroll-driven.com horizontal gallery](https://www.css-scroll-driven.com/scroll-driven-view-transition-implementation-patterns/scroll-driven-media-and-gallery-effects/horizontal-scroll-gallery-with-scroll-timeline/); WebKit [scroll-driven animations](https://webkit.org/blog/17101/a-guide-to-scroll-driven-animations-with-just-css/)) **only** behind `@supports` and `prefers-reduced-motion: no-preference`. Peek slides may sit at 0.96; the centered slide is 1. **Never** scale the Message CTA.

### 9.3 What to delete from live `ProductGallery`

- `AnimatePresence mode="wait"` around a **single** hero as the default color/index clock.
- `initial: { x: 24 }` / `exit: { x: -18 }` / `duration: 0.28` as the **only** transition.
- `onClick` on the `<img>` that secretly advances index **without** a visible next control (hidden carousel). Keep click → lightbox **if** `10` shipped one; otherwise click does nothing extra until arrows exist.

Keep the ease token `[.22, 1, .36, 1]` if you still fade a **src change**. Keep `useReducedMotion()`.

### 9.4 Optional clip pour (only if you refuse a rail)

If Origin **cannot** ship a rail this pass (length always 1 until admin tags): **do not fake peeks**. Only ship FIX 1 (no remount of same src) + FIX 5 (hero VT name). That is still a valid boutique. A clip-path wipe of one JPEG is `13`’s Featured mistake copied onto the PDP — **refuse**.

---

## 10. Color → gallery honesty (no stock photos)

Admin path (`04` / APPLY list E): add hex → tag image → Save {mã}. Until `colorId` is set on a second file:

- A01 color tap **must not** look like a second photo arrived.
- Do not fetch `/products/A01/001.jpg` speculatively (`10`: that URL 404’d in an earlier pass).
- Do not tint `#F4F0E8` over the JPEG with `mix-blend-mode` to fake a finish (invented hue; fails 1.4.1 for Hoa-class names later).
- Grid `coverSrcForColor` may preview a tagged cover on the **card** when the buyer is not on the PDP; it must still be **this mã**.

Shared untagged shots: current helper **hides** them when a color is selected. APPLY: either **tag** them in admin or treat untagged as shared (`colorId == null` **included** in every filter). Pick one; document in code. Default for this paste: **keep live filter** (strict `colorId === t`) + no remount when the fallback cover is used — so a tap that cannot show a tagged shot is visually a **chip state change only**.

---

## 11. Reduced-motion + reduced-transparency + vestibular

Do not collapse these clocks (`10` §3.3; [Motion Spec](https://motionspec.dev/blog/wcag-2-3-3-animation-from-interactions)):

| Criterion | Gallery impact |
| --- | --- |
| [2.2.2](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) A | No auto-rotate. Do not add a looping edge shimmer. `.shimmer` still infinite — `10` FIX 1, not this paste’s new loop |
| [2.3.1](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html) A | Do not strobe frost |
| [2.3.3](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) AAA | Snap, smooth scroll, view() scale, src fade. Sufficient: [C39](https://www.w3.org/WAI/WCAG22/Techniques/css/C39) + `useReducedMotion` |
| [1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) | Chip outline + `aria-pressed`; Hold as text |
| [2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) | Prev/next ≥24×24 (prefer 44). Dots 6px illegal if they are the only control |
| [`prefers-reduced-transparency`](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-transparency) | Edge frost → opaque paper (WWDC Reduced Transparency → frostier / more opaque). Also apply to sticky bar if you touch it — prefer **not** retuning the sticky bar this pass |

MDN: Reduce Motion means **remove, reduce, or replace**; large pans/zooms are vestibular triggers ([`prefers-reduced-motion`](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)). A full-bleed `translateX(24px)` on the hero is that class — live already gates it; the rail’s **smooth scroll** must gate too.

---

## 12. Timing budget

| Interaction | Budget | Live 2026-09-09 evening | APPLY |
| --- | --- | --- | --- |
| Chip selected style | ≤100ms | Outline instant — OK | Keep |
| Same-src color tap | **0ms** extra | **~280ms wait wipe** | Kill remount |
| Src-changing color tap, 1 image | 150–250ms opacity | n/a (no tagged second file) | Fade only |
| Color tap, ≥2 images | Smooth scroll ≤ ~200–300ms UA | n/a | Native snap; no extra Framer |
| Peek frost | Static paint | n/a | No animation loop |
| Featured tab pour | ≤200ms (`13`) | ~540ms wait | **Out of scope** |
| Home → PDP VT | ≤300ms | Names mismatch (`10`) | Put `product-{MA}` on current slide |
| Image dots | — | 6px | Replace or enlarge if rail ships |

---

## 13. Performance

Tokopedia: scroll JS at 50% CPU vs ~2% after CSS scroll-driven timelines ([Chrome SDA / e-commerce](https://developer.chrome.com/blog/css-ui-ecommerce-sda)). Lessons:

- The rail is **real overflow**, not per-frame `transform` on touchmove.
- Frost strips are **~10% × hero height**, not a full-viewport `backdrop-filter` (expensive; Bebber/Tigt warning in `13` §13).
- Animate `transform` / `opacity` / `clip-path` only if you add a src fade. Do not animate `width` / `filter` on the JPEG.
- Do not run `.shimmer` **and** a view() scale **and** a wait-slide together.
- Preload **current** cover (`rel=preload` already on A01 + A02). Lazy-load slide 2+ (`loading="lazy"`). Do not preload every mã’s folder (`06` LCP).
- ISR `x-nextjs-stale-time: 300` is a cache clock. Filter from the **payload already on the page**.

Apple marketing pages that scrub **canvas image sequences** on scroll ([CSS-Tricks 2020](https://css-tricks.com/lets-make-one-of-those-fancy-scrolling-animations-used-on-apple-product-pages/); [Geyer 2024](https://geyer.dev/blog/css-image-sequence-animations/)) need dozens of frames. This closet has **one JPEG per mã** today. Do not build a 120-frame finish spinner.

---

## 14. APPLY — [sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)

**Owner:** Origin `sassy-closet-shop` (not this kit).  
**Look:** Kelly Ying paper / ink / gold.  
**Job:** Apple-grammar **color → gallery roll** + **frosted edge peeks** when this mã has >1 real photo.  
**Origin agent:** Fast **OFF**, budget **1B**.  
**Mã:** allowlist only. **No** Square Save. **No** FB Send. **No** cart. **No** stock copy.  
**Do not edit** `excel-kit/` or intake `sassy-closet/`.  
**Do not** retune Featured `filterSlide` (that is `13`).

Human-readable ticks. **Paste block is §19.**

### 14.0 Do not touch (lock — tick first)

- [ ] Cormorant Garamond + Be Vietnam Pro.
- [ ] Paper / ink / gold / blush; `ma-mark`; 11px tracking; gold **hairline** language.
- [ ] Keyframes `announce-fade`, `shimmer-slide`, `cta-flash` and classes `announce-fade`, `shimmer`, `cta-shine`.
- [ ] Exports `ProductGallery`, `ColorSwatch`, `imagesForColor`, `coverSrc`, `coverSrcForColor` **remain** (bodies may change).
- [ ] Allowlist ten; Hold **P02, P05** without `$`.
- [ ] Message-first; Page `61594312648057`; footer **Zelle** word; `noindex`.
- [ ] Sticky `md:hidden` bar: `bg-paper/95 backdrop-blur-md` **remains** (do not stack a second glass).
- [ ] A01 live copy sentences **unchanged**.

### 14.1 Color → roll (A01 is the fixture)

- [ ] `/m/A01` still shows two hex chips `#F4F0E8` / `#1C2A4A`. No invented names.
- [ ] Tap a chip: `aria-pressed` moves; **same** `cover.jpg` does **not** wait-slide.
- [ ] Tap again: color id `null`; still A01 $25.
- [ ] `/m/A02` still has **no** chip row (`colors: []`).
- [ ] `/m/P02` still Hold · Inbox for price; no chips unless Blob actually has `colors[]` on **P02**.

### 14.2 Rail + peeks (only if ≥2 **200** images on that mã)

- [ ] Horizontal snap rail; neighbor peeks; edge frost paper blur + mask.
- [ ] APG: region+slides, prev/next ≥24px, **no auto-rotate**.
- [ ] Reduce Motion: no smooth scroll, no view() scale, frost may stay static.
- [ ] Reduce Transparency: edge strips opaque paper.
- [ ] Never peek another mã.

### 14.3 Hero VT name (`10` still required)

- [ ] Current A01 slide wrapper: `view-transition-name: product-A01`.
- [ ] Related A02 tile keeps `product-A02`.

---

## 15. Forbidden (reject in review)

1. Minting `A03` / `Q01` / `AO001` / `A01-RED`.
2. Unsplash / dummy JPEGs / CSS-tinted fake finishes.
3. `feDisplacementMap` / goo / chromatic aberration on photos.
4. iOS capsule tab bar / glass over the 3/4 hero.
5. Auto-advancing carousel.
6. Apple or Kelly Ying **copy** (finishes named, $10 ship, “Pick your favorite”).
7. Cart / Shop now / bag-fly.
8. Rewriting P02/P05 to a dollar.
9. Editing intake or Excel from this Origin job.
10. Fighting Origin shop `main` with a kit-repo code change (this file is kit **notes** only).
11. Restyling Featured tabs “while you’re here” (`13`’s paste).
12. `opacity-0` cover left stuck (`10` FIX 2).

---

## 16. Verify (Origin clicks these; kit does not ship UI)

Desktop + phone + OS Reduce Motion + Reduce Transparency + keyboard:

1. `/m/A01` — two hex chips; cover visible; Message A01 still opens Page `61594312648057`. Color tap does **not** wipe the same JPEG. Copy unchanged.
2. `/m/A02` — no chip row; $22; related may show A01’s chips on the **card** only.
3. `/m/P02` — Hold, no `$`. `/c/quan` empty. `/m/A03` 404.
4. If a mã has **two 200 photos** tagged: rail peeks; frost on edges; arrows; no wrap to another mã.
5. Reduce Motion: instant src swap / instant scroll; chips and Message still work.
6. Reduce Transparency: edge strips go opaque paper; garment not warped.
7. View-source / network: no `e.tb.cn`, no `¥`, no `A03`, no `V984`, no Unsplash.

---

## 17. Sources

### 17.1 Shop law / live

- `README.md`, `sassy-closet/BOSS.md`, `excel-kit/schema.py` `MA_RE` / `ASK_STOCK_MA`
- Slack `#shop-decisions` 2026-09-04 — <https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788541753903809> (channel law); Track ON <https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788553474026779>
- Live host — <https://sassy-closet-shop.vercel.app/m/A01>
- Sisters `02`, `04`, `10`, `13` (PRs #19, playbook `04`, #31, #33)

### 17.2 Apple (grammar, not copy)

- WWDC25, *Meet Liquid Glass* — <https://developer.apple.com/videos/play/wwdc2025/219/>
- Apple HIG, *Materials* — <https://developer.apple.com/design/human-interface-guidelines/materials>
- Apple, *Adopting Liquid Glass* — <https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass>
- Apple HIG, *Motion* — <https://developer.apple.com/design/human-interface-guidelines/motion>
- Apple, Reduced Motion evaluation — <https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria/>
- WWDC23, *Design considerations for vision and motion* — <https://developer.apple.com/videos/play/wwdc2023/10078/>
- Apple, iPhone (finish names as **their** catalog) — <https://www.apple.com/iphone/>
- Apple Newsroom, iPhone 16 colors (do not copy onto Sassy) — <https://www.apple.com/newsroom/2024/09/apple-introduces-iphone-16-and-iphone-16-plus/>

### 17.3 Motion / scroll / mask / frost (web)

- Nielsen Norman Group, animation purpose / attention / microinteractions / PDP — <https://www.nngroup.com/articles/animation-purpose-ux/>, <https://www.nngroup.com/articles/animation-usability/>, <https://www.nngroup.com/articles/microinteractions/>, <https://www.nngroup.com/articles/ecommerce-product-pages/>
- Jakob Nielsen, response-time limits — <https://www.nngroup.com/articles/response-times-3-important-limits/>
- MDN, `scroll-snap-type` — <https://developer.mozilla.org/en-US/docs/Web/CSS/scroll-snap-type>
- MDN, `mask-image` — <https://developer.mozilla.org/en-US/docs/Web/CSS/mask-image>
- MDN, `backdrop-filter` — <https://developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter>
- MDN, `prefers-reduced-motion` — <https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion>
- MDN, `prefers-reduced-transparency` — <https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-transparency>
- web.dev, CSS scroll snap — <https://web.dev/articles/css-scroll-snap>
- WebKit, scroll-driven animations — <https://webkit.org/blog/17101/a-guide-to-scroll-driven-animations-with-just-css/>
- Chrome, e-commerce scroll-driven animations — <https://developer.chrome.com/blog/css-ui-ecommerce-sda>
- Chrome, View Transitions — <https://developer.chrome.com/docs/web-platform/view-transitions/>
- CSS-Tricks, Apple-style canvas scrub (refuse as architecture) — <https://css-tricks.com/lets-make-one-of-those-fancy-scrolling-animations-used-on-apple-product-pages/>
- Geyer, CSS image-sequence (refuse — we lack frames) — <https://geyer.dev/blog/css-image-sequence-animations/>
- CodeFronts, scroll-snap + mask peek — <https://codefronts.com/components/css-image-slider/scroll-snap-touch-image-carousel/>
- W3Tweaks, peeking carousel — <https://www.w3tweaks.com/css/css-scroll-snap-explained/>
- Pqina, mask overflow fade — <https://pqina.nl/blog/fade-out-overflow-using-css-mask-image/>
- css-scroll-driven.com, horizontal gallery + `view(inline)` — <https://www.css-scroll-driven.com/scroll-driven-view-transition-implementation-patterns/scroll-driven-media-and-gallery-effects/horizontal-scroll-gallery-with-scroll-timeline/>
- WebTricks, liquid glass CSS (rim/sheen; displacement Chromium-only) — <https://webtricks.dev/blog/liquid-glass-css>
- kube.io, liquid glass SVG (Chrome-only backdrop url()) — <https://kube.io/blog/liquid-glass-css-svg/>
- HTML-in-Canvas, liquid glass CSS vs WebGL — <https://html-in-canvas.dev/liquid-glass-effect/>

### 17.4 Accessibility

- WAI-ARIA APG, Carousel — <https://www.w3.org/WAI/ARIA/apg/patterns/carousel/>
- WAI-ARIA APG, Tabs — <https://www.w3.org/WAI/ARIA/apg/patterns/tabs/>
- W3C WCAG 2.2 Understanding 1.4.1 / 2.2.2 / 2.3.1 / 2.3.3 / 2.5.8 — linked in §11
- W3C technique C39 — <https://www.w3.org/WAI/WCAG22/Techniques/css/C39>

### 17.5 Catalog / gallery platforms (learn, don’t install)

- Craftshift, Shopify variant images / mixed gallery — <https://craftshift.com/shopify-variant-images-complete-guide/>
- Shopify help, variant images — <https://help.shopify.com/en/manual/products/product-media/add-images-variants>

### 17.6 Weaker / vendor (directional only)

Theme posts that claim conversion lifts without a method are **not** shop law. Framer “Feature Explorer” finish ellipses are a **named-disc** pattern — steal the *update the image* job, not the component or Apple-like ellipses. Canvas Apple-hero clones (21st.dev MacBook Neo, etc.) are **out**.

---

## 18. Open questions (do not answer by inventing)

1. Will admin tag A01’s two hexes onto **separate** Blob files, or stay on one untagged `cover.jpg`? Peek rail is blocked until ≥2 **200s**.
2. Shared vs strict `imagesForColor` (include `colorId == null` in every filter)? Live is strict. Changing it is a merchandising decision, not an FX flourish.
3. `02` text chips vs live / `04` hex boxes — which wins for storefront? This pass does not restyle.
4. After Granola access: did a call already forbid `backdrop-filter` on mobile for battery? Until then, match the **existing** sticky `backdrop-blur-md`.
5. Concurrent `15`–`17` FX notes: if an iOS-frosted-carousel paste ships, **merge jobs** — this file owns **color → roll + edge peeks**; do not double-wrap the hero in two rails.

---

## 19. PASTE INTO ORIGIN AGENT (do not paraphrase)

Copy everything between the markers into a Cloud Agent on the **Origin `sassy-closet-shop` repo** (the git behind https://sassy-closet-shop.vercel.app). Not this kit. Not intake `sassy-closet/`. Not `excel-kit/`.

**Origin UI before you run it:** Fast = **OFF**. Budget = **1B**.

```text
===== BEGIN ORIGIN PASTE — Apple water / glass gallery (LEARN 18) =====

ORIGIN SETTINGS (do not skip): Fast OFF. Budget 1B.

You are editing Origin sassy-closet-shop. Ship APPLE-GRAMMAR visual FX on the
EXISTING PDP gallery: color → gallery ROLL + frosted EDGE PEEKS + watery
(native snap) transitions. Do not restyle the boutique. Do not invent mã.
Do not add iOS Liquid Glass over photos. Do not copy Apple or Kelly Ying
marketing. Do not touch intake or Excel.

HOST: https://sassy-closet-shop.vercel.app
LAW: Facebook inbox is the store. No cart. No Square Save. No FB Post/Send.
ALLOWLIST ONLY: A01 S01 P01 P02 P03 P04 P05 K01 H01 A02
HOLD (no $): P02 P05
PRICES: A01 $25 · S01 $28 · P01 $5 · P03 $18 · P04 $13 · K01 $37 · H01 $8 · A02 $22
LOOK LOCK: Cormorant Garamond + Be Vietnam Pro; paper / ink / gold / blush;
ma-mark; 11px uppercase tracking; gold HAIRLINE; announce-fade; shimmer +
shimmer-slide; cta-shine + cta-flash.
Do NOT switch to intake rose / Allura / Nunito. Do NOT add Shopify cart.
Do NOT copy Kelly Ying V984 or “$10 shipping on $300+”.
Do NOT copy Apple finish names (Ultramarine, Desert Titanium, …) or
“Pick your favorite” / “Five bold colors”.
Do NOT apply SVG goo / feDisplacementMap / chromatic aberration to photos.

FIND FILES (rg — names may differ; match these strings, then edit those files):

  rg -n "ProductGallery|ColorSwatch|imagesForColor|coverSrcForColor"
  rg -n "AnimatePresence|useReducedMotion"
  rg -n "announce-fade|shimmer-slide|--gold:|backdrop-blur-md"
  rg -n "view-transition-name:product-|product-\$\{"

Expected (live 2026-09-09 evening, chunk 1xr62vxitay1m.js + 34vl_zddoo4ws.css):
  ProductGallery:
    colorId state starts null
    imagesForColor(product, colorId)
    coverSrc fallback
    AnimatePresence mode="wait"
    motion enter x:24 / exit x:-18 / duration 0.28 ease [.22,1,.36,1]
    key = `${colorId ?? "all"}-${src}`
    img onClick cycles index if length>1
    ColorSwatch row if colors.length>0
  imagesForColor:
    null → all src.trim() images
    else → filter img.colorId === colorId   // empty if untagged
  ColorSwatch: h-6 w-6 rounded-sm, outline-ink when selected,
    aria-label={`Color ${hex}`}
  :root --canvas --paper --ink --gold --gold-deep --blush
        --duration-enter:.21s --duration-exit:.15s --duration-move:.4s
  Sticky md:hidden bar: bg-paper/95 backdrop-blur-md  (KEEP)
  A01 payload: colors #F4F0E8 + #1C2A4A notes empty;
    images [{ src: "/products/A01/cover.jpg", colorId: null }]
  A02 / P02 galleries: colors []
  /m/A01 hero has NO view-transition-name product-A01 (related has product-A02)

If a file is missing, create the smallest new file next to ProductGallery —
do not invent a second design system.

────────────────────────────────────────
FIX 1 — Same JPEG must not wait-slide (A01 fixture)
────────────────────────────────────────
BUG: selecting a hex remounts AnimatePresence because the key includes
colorId even when imagesForColor is [] and src falls back to cover.jpg.
Buyer sees a 280ms x-wipe of the identical photo.

DO:
  1. Key the hero/rail by actual src (+ index), not by colorId when src
     is unchanged.
  2. If prevSrc === nextSrc, do not run mode="wait" / x:24.
     Chip state (aria-pressed + outline) is enough.
  3. Keep imagesForColor / coverSrc / coverSrcForColor NAMES.
     Do not invent a parallel helper.
  4. Do not invent /products/A01/001.jpg. Do not borrow A02’s cover.
  5. Do not auto-select the first hex on load (null = honest).

────────────────────────────────────────
FIX 2 — Color → ROLL when this mã has ≥2 real 200 images
────────────────────────────────────────
WHEN product.images filtered by imagesForColor has length ≥ 2 AND each
src 200s on THIS host (do not pad with duplicates):

  Replace the single wait-slide <img> with a native rail:

    .ky-gallery-rail {
      display: flex; gap: .75rem;
      overflow-x: auto;
      overscroll-behavior-inline: contain;
      scroll-snap-type: x mandatory;
      scroll-padding-inline: 7%;
      scrollbar-width: none;
    }
    .ky-gallery-slide { flex: 0 0 86%; scroll-snap-align: center; }

  Color tap: setIndex(0) then slide[0].scrollIntoView({
    inline: "center", block: "nearest",
    behavior: reduced ? "instant" : "smooth"
  })

  Reduced: scroll-snap-type none; scroll-behavior auto; no view() scale.

WHEN length < 2: do NOT fake a peek. Keep one hero. Opacity fade 150–250ms
ONLY if src actually changed.

Do NOT also run Framer x:24 on the rail (double motion).
Do NOT auto-rotate.

────────────────────────────────────────
FIX 3 — Frosted EDGE PEEKS (chrome, not cloth)
────────────────────────────────────────
Only if FIX 2 rail exists.

  Absolute left/right strips ~10% width, pointer-events: none,
  z-index above photos, below Message CTA:

    background: color-mix(in srgb, var(--paper) 58%, transparent);
    backdrop-filter: blur(12px) saturate(140%);
    -webkit-backdrop-filter: blur(12px) saturate(140%);
    mask-image: linear-gradient toward the center to transparent

  Rhyme with existing sticky bar (paper/95 + blur-md).
  Optional 1px inner white highlight. NO rainbow fringe.

  @media (prefers-reduced-transparency: reduce) {
    strips: backdrop-filter none; background var(--paper); opacity .92;
  }

NEVER:
  backdrop-filter / filter:url() / feDisplacementMap on the <img>
  wrapping the rail in opacity < 1 (backdrop-root trap)
  a second glass sheet on the sticky Message bar (glass-on-glass)
  Clear iOS capsules / glass in the content layer (WWDC25)

First/last slide: don’t eat the JPEG with the outer frost
(soften/hide the unused outer strip).

────────────────────────────────────────
FIX 4 — APG carousel (no hidden click-cycle)
────────────────────────────────────────
If rail ships:
  1. role="region" aria-roledescription="carousel"
     aria-label="{MA} photos"  (label does NOT include the word carousel)
  2. Each slide role="group" aria-roledescription="slide"
     aria-label="1 of N" if no unique caption
  3. Visible prev/next BUTTONS, min 24×24 (prefer min-h-11 like Message)
  4. REMOVE img onClick secret cycle (or keep click only as lightbox
     opener IF LEARN 10 lightbox already exists — do not build a second)
  5. Dots if kept: ≥24px hit; aria-label "Image N"; not 6px.
  6. No auto-play. No wrap from A01 last slide to A02.
  7. aria-live polite ONLY if not auto-rotating (it isn’t).

If rail does NOT ship (still 1 image): skip APG carousel; keep one hero.
Do not add decorative dots for a single cover.

────────────────────────────────────────
FIX 5 — product-{THIS mã} on the current hero/slide
────────────────────────────────────────
Put view-transition-name: product-{ma} on the A01 (etc.) hero / current
slide wrapper. Related-rail tiles keep THEIR mã names.
Do not add a liquid root wipe on ::view-transition-old(root).
Keep ::view-transition { pointer-events: none }

Optional @view-transition { navigation: auto } AFTER names match (LEARN 10).

────────────────────────────────────────
FIX 6 — CSS reduce gates (add, don’t delete existing)
────────────────────────────────────────
KEEP existing reduce kills for announce-fade / shimmer / cta / VT.

ADD:

  @media (prefers-reduced-motion: reduce) {
    .ky-gallery-rail {
      scroll-snap-type: none !important;
      scroll-behavior: auto !important;
    }
    .ky-gallery-slide { transform: none !important; }
  }

  @media (prefers-reduced-transparency: reduce) {
    .ky-gallery-edge {
      backdrop-filter: none !important;
      -webkit-backdrop-filter: none !important;
      background: var(--paper) !important;
    }
  }

Do not use --duration-move:.4s as the color clock.
Chip restyle (text names, 44px Apple discs) is OUT OF SCOPE.
Featured tab meniscus / filterSlide is OUT OF SCOPE (LEARN 13).

────────────────────────────────────────
HARD STOPS
────────────────────────────────────────
- No new mã. No Q01 / A03 / AO001 / A01-RED on the lookbook.
- No cart, Shop now, flying-to-cart.
- No warehouse ticker, no fake countdown.
- Do not rewrite P02/P05 to a dollar. No e.tb.cn, no ¥, no customer names.
- Do not rewrite A01 EN/VN sentences. No Apple slogans. No V984.
- Do not restyle fonts or gold “to look cleaner.”
- Do not invent a second photo so the peek has something to show.
- Do not touch https://sassy-closet.vercel.app (intake).
- Do not edit excel-kit or Official xlsx.
- Do not Production-promote without Boss. Open a Preview.

────────────────────────────────────────
VERIFY (you click these; do not skip)
────────────────────────────────────────
Desktop + phone + OS Reduce Motion + Reduce Transparency + keyboard:

1. /m/A01  two hex chips #F4F0E8 #1C2A4A. Cover VISIBLE.
   Tap each chip: outline/aria-pressed moves; SAME jpeg does not wipe.
   Copy still “One unique top on hand…” / “Áo độc bản…”.
   Message A01 → facebook.com/profile.php?id=61594312648057
2. /m/A02  no gallery chip row. $22.
3. /m/P02  Hold · Inbox for price. No dollar.
   /c/quan empty. /m/A03 404.
4. If any allowlist mã has ≥2 200 images: rail peeks, edge frost,
   arrows, no wrap to another mã. Else: no fake peek.
5. Reduce Motion: no smooth roll, no x-wipe, no shimmer, no 1.08 zoom.
   Chips + Message still work.
6. Reduce Transparency: edge strips opaque paper; photo not displaced.
7. View-source / network: no e.tb.cn, no ¥, no A03, no V984, no Unsplash.

Commit on an Origin cursor/* branch. Preview URL in the PR. Do not merge.

===== END ORIGIN PASTE =====
```

Mini Boss: copy the block above as the **entire** Origin prompt. Set Fast **OFF** and budget **1B** in the Origin UI. Do not add “also make it more premium” or “add liquid glass.” The roll + edge frost *are* the Apple-water pass. `10`’s lightbox / Reduce-hover fixes and `13`’s tab meniscus still apply if they are not on Origin `main` yet — do not regress them, and do not re-paste those jobs into this run unless they are missing.

End of 18.
