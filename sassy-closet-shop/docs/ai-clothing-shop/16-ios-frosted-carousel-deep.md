# 16 — iOS / Apple frosted color carousel + scroll-snap gallery (fashion)

**Learn track:** Ultra burn, Fast OFF (research + live as-built + recipes + APPLY).  
**Shop:** Sassy Closet — Facebook inbox is the store; Square Free is on-hand truth; sell-test lookbook is Origin-owned.  
**Live APPLY target:** [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)  
**Audience:** Mini Boss / Origin shop implementer / whoever ships the **PDP watery roll** without breaking reliability.  
**Date researched / crawled:** 2026-09-09 (evening pass; live HTML/CSS/JS re-fetched).  
**This file does not assign stock, mint a mã, Save in Square, post to Facebook, restyle the boutique, or touch Excel / intake.**

Sister `10` is general motion law (lightbox, VT names, color → gallery *motion*). Sister `13` is watery **Featured tab + grid pour**. This note is the **PDP gallery**: Apple’s product-color *peek* translated into a fashion rail that **snaps**, **frosts only the edges**, and **filters by `colorId`**. Kelly Ying *look* stays locked (`01` §1.3; `10` §5; `13` §5). Mini Boss pastes **§21** into the Origin agent. Do not paraphrase §21 into “add iOS liquid glass” or “copy Apple marketing.”

---

## 0. How to read this document

This is a **learn-track** note, not a rebuild brief and not permission to fork Origin shop code from this kit repo.

- **Cite, don’t invent.** Shop-law claims point at a file, Slack permalink, sister learn-track, or the live host. Industry claims point at Apple HIG, NN/G, Baymard, W3C WCAG 2.2, WAI-ARIA APG, MDN (`mask-image`, `backdrop-filter`, `scroll-snap-*`), Chrome CSS Overflow 5, Motion `useScroll`, or WebKit bugs. If a fact is missing, the gap is named.
- **Never invent a mã.** Customer-facing codes this pass may name are the **first-ten allowlist** only. Admin “Next mã A03” is a prediction. Slack `AO001` / `AO003` are **decision-template examples** (`#shop-decisions`, 2026-09-04), not live lookbook stock. Kelly Ying `V984.` / `V826.` are **their** SKUs — do not copy them onto Sassy tiles or into gallery `alt`.
- **No stock copy.** Do not paste Apple product-page sentences, Kelly Ying dress titles, Taobao titles, or Unsplash alt text onto A01–A02. Keep the live bilingual lines that already exist (“One unique top on hand. Message A01 for real photos and size.” / “Áo độc bản — một chiếc đang có.”). Gallery `alt` stays `{MA}. {KIND}` as `displayTitle` already formats.
- **Two alphabets.** Sell-site / hub = `A01`. Official / Square / SoT = `AO001`. The carousel never translates one into the other (`01` §9; `excel-kit/schema.py` `MA_RE`).
- **Facebook inbox is the store.** A “buy” is **Message {code}**. There is no cart. A carousel that peeks the *next SKU* as if it were a colorway is a lie.
- **No redesign mandate.** Improve **inside** paper / ink / gold / blush, Cormorant Garamond + Be Vietnam Pro, `ma-mark`, `announce-fade`, `shimmer` / `shimmer-slide`, `cta-shine` / `cta-flash`, gold `h-px`, `springSoft`, `filterSlide` *ease*, `view-transition-name: site-header` / `product-{MA}`. Do not replace that language with iOS Liquid Glass over photography, Shopify Horizon, intake Allura/Nunito rose, or a new design system.

### 0.1 Research method (and what this pass could not see)

| Source | Result |
| --- | --- |
| Live sell-test HTML of `/`, `/m/A01`, `/m/A02`, `/m/S01`, `/m/P01`, `/m/P02`, `/m/P03`, `/m/P04`, `/m/P05`, `/m/K01`, `/m/H01`, `/admin` (2026-09-09 evening) | Primary **as-built** gallery map. **Delta vs `10` / `13` morning crawls:** customer hex chips and `ProductGallery` are now in the HTML/JS. |
| CSS chunk `/_next/static/immutable/chunks/34vl_zddoo4ws.css` | Same tokens as `13` §4.1. **No** `scroll-snap-*`, **no** `mask-image`. Tailwind `backdrop-blur-md` utility exists; **not used on the hero**. |
| PDP JS `/_next/static/immutable/chunks/1xr62vxitay1m.js` | Exports `ProductGallery`, `ColorSwatch`, `ColorSwatchEmpty`. Motion: `AnimatePresence mode="wait"`, `x: 24 / -18`, `duration: 0.28`. |
| Shared helpers (module `12573`) | `coverSrc`, `coverSrcForColor`, `imagesForColor` — reconstructed in §4.3. |
| Home motion chunk `3_93acjqq2t4q.js` | Same `springSoft` / `filterSlide` as `13`. Grid also renders `ColorSwatch` when `product.colors.length > 0`. |
| Photo HEAD | `/products/{MA}/cover.jpg` **200** for the ten. `/products/A01/001.jpg` and `/products/A01/002.jpg` **404**. Do not invent extra files because OneDrive HQ listed them (`10` FIX 3). |
| Repo `excel-kit/`, `sassy-closet/`, `README.md` | Shop law. Intake lightbox is **behavior** only. |
| Sister LEARN TRACK PRs #19–#33 (`01`–`14`) | Headings + locks. This file is `16` (15 may land in parallel; do not wait). |
| Slack `#shop-decisions` (`C0BV3GYC602`) | Standing Square Track ON + bots draft only (2026-09-04). No carousel thread. |
| Linear | Onboarding `TIE-*` only — no gallery issue. |
| Granola meetings | MCP unauthorized — no meeting notes. |
| Notion | No Sassy Closet carousel pages. |
| Kelly Ying Boutique public site | Cloudflare-blocked on sister `13` this day; look facts stay with `01` / `10`. **Do not scrape their product copy.** |
| Apple.com iPhone 17 / iPhone Air public pages (2026-09-09) | Color *names* on the marketing page (Lavender / Sage / …). Implementation recipes below are **web-platform** (HIG + CSS), not a dump of Apple’s minified CSS. |
| Public CSS / a11y / motion specs | Fetched 2026-09-09. URLs in §19. |

If a later crawl disagrees with a **live** cell here, **the new crawl wins** — update the date line. Shop law still wins over industry taste. Recorded hub `colors[].id` (`05` §3.2) wins over a hex the page painted.

### 0.2 Sister docs

| # | File | Job vs this note |
| --- | --- | --- |
| 01 | `01-messenger-social-commerce.md` | Kelly Ying look lock; Message-first; no cart; no invented ship `$` |
| 02 | `02-pdp-color-size-ux.md` | Customer **text** colors; gallery sync nouns; mixed-gallery refuse |
| 03 | `03-tiny-boutique-admin.md` | Admin brains; do not mint from “Next mã” |
| 04 | `04-next-blob-catalog-arch.md` | ISR / Blob; `/m/A03` must 404 |
| 05 | `05-ai-product-media.md` | Recorded first-ten colors; `colorId` bind; no invented hex |
| 06 | `06-seo-trust-diaspora-boutique.md` | Soft-launch `noindex`; unique `/c/*` titles |
| 07 | `07-taobao-dropship-boutique.md` | Motion lock list; dropship-honest copy |
| 08 | `08-dropship-ops-runbook.md` | Staff clock; does not restyle |
| 09 | `09-bugcheck-sell-site-checklist.md` | Tick-box QA; PDP-01…04; MOT-* |
| 10 | `10-customer-pleasing-motion-ux.md` | General motion + lightbox + FIX 5 color fade |
| 11 | `11-vercel-blob-admin-qa.md` | Admin / Blob gate; look stays |
| 12 | `12-fb-messenger-dropship-copy.md` | VN+EN phrase bank; **no stock copy** |
| 13 | `13-watery-tab-slide-motion.md` | Watery **tabs + grid**. This file does **not** redo `featured-tab`. |
| 14 | `14-complete-admin-feature-matrix.md` | Admin must store `colors[]` + `images[{src,colorId}]` |
| **16** | **This file** | **Frosted peek gallery + scroll-snap watery roll; Origin APPLY** |
| Kit | `SELL_CATALOG_CONTRACT.md` (PR #18) | Allowlist + prices + Hold null `$` |

`10` already asked for text pills, 150–250ms image fade, and a lightbox. Live JS (this crawl) **already** has `ProductGallery` + `imagesForColor`. This note names those hooks and tells Origin **how to make the rail feel like Apple paging without becoming Apple chrome or a mixed-SKU strip**.

---

## 1. Executive summary

Apple’s product pages teach one physical idea: **the object stays; the finish changes; you can see that another finish exists without leaving the object.** Adjacent colorways *peek*. The active device *snaps* to center. The chrome around the peek may frost. The copy names the finish in **words**.

A fashion boutique of **unique pieces** (qty 1, Message to buy) must steal the *peek + snap*, and refuse the *next-product-as-color* trick. On Sassy Closet the “finish” is a **recorded color on this mã**, proven by files tagged `colorId`. The peek is the **next honest photo of this mã** (front → back → detail), not A02 leaking into A01’s hero.

Nielsen Norman Group: animation is for **feedback, state-change, navigation metaphors, stronger signifiers** — not delight, not downtime ([NN/G, *The Role of Animation and Motion in UX*](https://www.nngroup.com/articles/animation-purpose-ux/)). Baymard: apparel PDPs need **enough images + zoom**; a mixed gallery (đen + hồng in one unfiltered strip) is the industry failure mode Shopify themes still ship (`02` §5.5; [Craftshift, variant images](https://craftshift.com/shopify-variant-images-complete-guide/)). Apple HIG Collections: image-first, easy to choose, don’t invent a layout that draws attention to itself ([HIG Collections](https://developer.apple.com/design/human-interface-guidelines/collections)). HIG Page Controls: paging + dots; **hide the same-axis scroll indicator**; don’t ship more than about **ten** dots ([HIG Page Controls](https://developer.apple.com/design/human-interface-guidelines/page-controls)).

Live sell-test (2026-09-09 evening), reconstructed from `ProductGallery` in `1xr62vxitay1m.js`:

| Hook | Live fact |
| --- | --- |
| `ProductGallery` | One hero `<img class="aspect-[3/4] w-full object-cover">` in `bg-[#f3f1ee]`. |
| `AnimatePresence mode="wait"` | Color / index change: enter `opacity 0, x: 24` → `1, 0`; exit `x: -18`; **0.28s** ease `[.22,1,.36,1]` (`filterSlide` family). Reduce: opacity only. |
| Image click | If `imagesForColor.length > 1`, `index = (i+1) % n`. **No** swipe, **no** `scroll-snap`, **no** lightbox. |
| Dots | `h-1.5 w-1.5 rounded-full bg-paper` — only if `f.length > 1`. A01 has one cover → **no dots**. |
| `ColorSwatch` | `h-6 w-6 rounded-sm` **hex fill**. `aria-label="Color #F4F0E8"`. Selected = `outline-ink`. |
| `imagesForColor(product, colorId)` | All `images` with `src.trim()` when `colorId == null`; else **strict** `image.colorId === colorId` (**drops shared `null`** — fights `02` / `10` / `05`). |
| Fallback | `g = f[i]?.src ?? coverSrc(product)` — empty filter still shows the **cover**. Every hex can look like it “worked.” |
| VT | Hero still has **no** `view-transition-name: product-A01`. Related rail names the **neighbor** (`product-A02` on `/m/A01`) — `10` FIX 3 still open. |
| Photos that 200 | `/products/{MA}/cover.jpg` only on this host. |

That is already a **colorId-aware gallery**. It is **not** yet an Apple-class roll:

1. **Hex discs on the customer** violate WCAG 1.4.1 and the shop’s text-only lock (`02` §7). Pattern ids (`hoa`, `cham-bi`) cannot be a square of `#F4F0E8`.
2. **The same two hexes appear on A01 and A02** (`#F4F0E8`, `#1C2A4A`). Hub recorded A02 as **`cham-bi` only** (`05` §3.2). Peeking “another color” that is really A01’s Kem/Xanh is a **catalog lie**.
3. **Accessories share a four-hex strip** (`#F4F0E8 #E8D5C4 #8B3A3A #1C2A4A` on P01, P02, P03, P04, P05). Hub recorded P01 `hoa`, P02 `do`, P04 `kem`. A shared palette is not a per-mã color list.
4. Click-to-cycle + 6px dots is not paging. There is nothing to *peek*. Apple’s affordance is the **neighbor in the frame**.
5. `mode="wait"` + 280ms x-slide is the same family `13` already called too long for a frequent tap. Color change should be **150–250ms opacity** (`10` §8.3), not a second page sliding over the first. **Shot-to-shot** inside one color is the watery *roll* (native snap).
6. Frost/mask/snap are **absent**. Tailwind `backdrop-filter` is unused on the hero — good (don’t frost the garment). APPLY puts frost on **edge chrome** only.

Reliability still beats beauty. A frosted peek that shows A02’s cover, a snap that wraps to P01 from A01, or a hex that invents Hồng on K01 is a **failed** boutique.

---

## 2. Hard constraints (print these on the implementer’s wall)

1. **Never invent a mã.** Emit list is exactly `A01 S01 P01 P02 P03 P04 P05 K01 H01 A02` (PR #18). Empty `/c/quan` stays empty. No `Q01` “so the carousel has a pants slide.”
2. **Never invent qty, $, photos, hex, or color names.** Hold P02 / P05 = **Inbox for price**. Empty `colors[]` = no chips (`02`; `05`; `10` §8). K01 / H01 / S01 live chips this crawl: **empty — keep them empty** until admin stores names on **that** row.
3. **Square Free = on-hand truth.** Official Excel is a working copy (`README.md`). This kit does not edit Excel or intake in this pass.
4. **Bots draft only.** No Square Save, no Facebook Post/Send (`#shop-decisions` 2026-09-04).
5. **No cart, Shop now, or bag-fly.** Kelly Ying’s **$10 / $300+** and `V###` codes are **theirs** (`01` §0). Do not put them in `alt`, captions, or dots.
6. **Customer colors are text** (WCAG [1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)). Admin may keep hex **boxes**. The lookbook must not.
7. **Gallery identity.** After any snap, fade, or frost, the visible mã is the mã in the URL. `product-A01` never finishes on S01’s pixels. Related-rail tiles are **other mãs**, not gallery slides.
8. **`colorId` is the only honest link.** A file may join a color only when (a) the mã is allowlisted, (b) the color id already exists on **that** mã, (c) a human agreed the pixels are that color (`05` §3.5). Otherwise `colorId` stays `null` (shared).
9. **Water / frost never lies on the photo.** No `backdrop-filter` / SVG goo / `feDisplacementMap` on `.shimmer`, covers, or heroes (`13` §2.8). Distortion is a fabric lie. Frost lives on **peek overlays** (paper-tinted strips at the rail edges).
10. **Origin owns the pixels.** APPLY is for the Origin agent on `sassy-closet-shop`. Intake Production stays https://sassy-closet.vercel.app. This PR does not edit `excel-kit/` or `sassy-closet/`.

---

## 3. What Apple’s color carousel actually is (fashion translation)

### 3.1 The iOS / Apple product pattern (jobs, not pixels)

On Apple marketing and in iOS system galleries, four jobs repeat:

| Job | System analog | Web CSS analog |
| --- | --- | --- |
| **Paging** | `UIScrollView` paging / SwiftUI `.scrollTargetBehavior(.paging)` or `.viewAligned` ([HIG Scroll Views](https://developer.apple.com/design/human-interface-guidelines/scroll-views); iOS 17 `scrollTargetLayout`) | `overflow-x: auto; scroll-snap-type: x mandatory; scroll-snap-align: center` ([MDN `scroll-snap-type`](https://developer.mozilla.org/en-US/docs/Web/CSS/scroll-snap-type)) |
| **Peek** | Neighbor card visible in the same scroll port (not a mystery fade) | Slide width **< 100%** of the port + `scroll-padding-inline` matching the peek gutter ([MDN scroll padding](https://developer.mozilla.org/en-US/docs/Web/CSS/scroll-padding)) |
| **Frosted edge** | Liquid Glass / vibrancy on **chrome** (tab bars, sidebars), not on the product render ([Apple Newsroom, Liquid Glass, 2025-06](https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/)) | `mask-image` so the neighbor **dissolves into paper**; optional `backdrop-filter` on a **strip**, not on `<img>` ([MDN `mask-image`](https://developer.mozilla.org/en-US/docs/Web/CSS/mask-image); [MDN `backdrop-filter`](https://developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter)) |
| **Finish name** | Color word under the device (Sage, Black, …) | **Text pill** + `Đang xem: {name}` (`02` §7). Not a hue-only dot. |

HIG Motion: frequent interactions must not make people **wait**; Reduce Motion replaces large spatial moves with a **crossfade or instant** ([HIG Motion](https://developer.apple.com/design/human-interface-guidelines/motion); [App Store Connect Reduced Motion criteria](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria/)). Color taps on a 10-SKU lookbook are frequent. The **roll** (finger-driven snap) can be spatial; the **color tap** should not be a 540ms luxury wipe (`13` already timed Featured at ~540ms and rejected it).

HIG Collections: prefer standard row/grid; make items easy to choose; don’t change layout while people are looking unless they asked ([HIG Collections](https://developer.apple.com/design/human-interface-guidelines/collections)). Filtering the rail to one `colorId` **is** an explicit action. Silently mixing A02 into A01 is not.

### 3.2 Steal vs refuse

| Apple / iOS cue | Steal for Sassy? |
| --- | --- |
| Neighbor peek (11–20% of the port) | **Yes** — when this mã has **≥2 honest files** in the current filter. |
| Mandatory snap to center | **Yes** — one shot in focus. `scroll-snap-stop: always` so a fast flick does not skip a seam shot ([MDN `scroll-snap-stop`](https://developer.mozilla.org/en-US/docs/Web/CSS/scroll-snap-stop)). |
| Page-control dots, ≤10, hide scrollbar on that axis | **Yes** — gold/ink, not iOS gray. Live 6px paper dots are too small (WCAG 2.5.8 24px target is AAA; shop already uses **min-h-10** on pills — keep 44×44 hit on buttons, dots can stay visual if each slide is also a snap target). |
| Color *name* next to the object | **Yes** — Kem, Xanh, Hoa, Đỏ, Hồng, Đen, Chấm bi. |
| Liquid Glass over the whole UI | **Refuse.** Fights `--paper` / `--ink`. `13` §3.1 already banned full-viewport glass. |
| Next *product* in the same carousel (You might also like) | **Refuse inside ProductGallery.** Related rail already exists under the fold. |
| Auto-advance | **Refuse.** WCAG 2.2.2 Pause, Stop, Hide ([SC 2.2.2](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html)). Live `.shimmer` is already the shop’s one infinite loop (`10` FIX 1). |
| Apple marketing sentences / iPhone color names | **Refuse.** No stock copy. |
| Peek when there is only one file | **Refuse.** A fake gutter with a duplicated cover is a ghost SKU. Single-slide = full-bleed hero, no mask. |

### 3.3 Fashion-specific: peek shots, not SKUs

Apple sells **N finishes of one model**. Sassy sells **one physical piece**. The gallery is:

```text
/m/{MA}  →  images[] belonging to that MA
             ├─ colorId === selected id   (this finish)
             └─ colorId === null          (shared: label, flaw, flat)

Related rail → other allowlist mãs (A02 on A01). NEVER slides in ProductGallery.
```

Baymard’s list-item research (expose all colors; don’t hide them in a menu) applies to **options of this piece**, not to exploding the catalog ([*Make All Color Swatches Available in Mobile List Items*](https://baymard.com/blog/mobile-interactive-color-swatches)). Text pills all visible satisfy “exposed options.” Hex discs fail pattern colors and CVD (`02` §5.4).

---

## 4. As-built hook map (cite the live host)

Crawl: 2026-09-09 evening. HTML on `/m/A01`. CSS `34vl_zddoo4ws.css`. PDP chunk `1xr62vxitay1m.js`. Helpers module **`12573`**.

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

Hero placeholder: `bg-[#f3f1ee]` (not `--blush`, close). Keep it. Do not invent `--frost: blur(40px)` as a brand token; if you need a length, bind **`--duration-enter`** for fades and a **local** `--peek: 12%` on the gallery wrapper.

Existing reduce query (unchanged from `10` / `13`):

```css
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto }
  .announce-fade, .shimmer, .cta-shine:hover:after { animation: none !important }
  ::view-transition-group(*), ::view-transition-old(*), ::view-transition-new(*) { animation: none !important }
}
```

`--duration-move: .4s` is **longer** than the color-tap budget. Do not use it as the gallery clock (`13` §12).

### 4.2 `ProductGallery` (reconstructed from the minified chunk)

```js
function ProductGallery({ product }) {
  const reduced = useReducedMotion();
  const [colorId, setColorId] = useState(null); // null = "all"
  const [index, setIndex] = useState(0);
  const shots = imagesForColor(product, colorId);
  const fallback = coverSrc(product);
  const i = shots.length === 0 ? 0 : Math.min(index, shots.length - 1);
  const src = shots[i]?.src ?? fallback;

  return (
    <div>
      <div className="relative overflow-hidden bg-[#f3f1ee]">
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={`${colorId ?? "all"}-${src ?? "none"}`}
            initial={!reduced && { opacity: 0, x: 24 }}
            animate={{ opacity: 1, x: 0 }}
            exit={reduced ? { opacity: 0 } : { opacity: 0, x: -18 }}
            transition={{ duration: 0.28 * !reduced, ease: [0.22, 1, 0.36, 1] }}
          >
            {src ? (
              <img
                src={src}
                alt={displayTitle(product)} // "A01. TOP"
                className={`aspect-[3/4] w-full object-cover ${shots.length > 1 ? "cursor-pointer" : ""}`}
                onClick={() => { if (shots.length > 1) setIndex((n) => (n + 1) % shots.length); }}
              />
            ) : (
              <div className="aspect-[3/4] bg-blush" />
            )}
          </motion.div>
        </AnimatePresence>
        {shots.length > 1 && (
          <div className="absolute inset-x-0 bottom-3 z-[2] flex justify-center gap-1.5">
            {shots.map((img, n) => (
              <button type="button" aria-label={`Image ${n + 1}`} onClick={() => setIndex(n)}
                className={`h-1.5 w-1.5 rounded-full ${n === i ? "bg-paper" : "bg-paper/40"}`} />
            ))}
          </div>
        )}
      </div>
      {product.colors.length > 0 && (
        <div className="mt-4 flex flex-wrap items-center gap-2">
          {product.colors.map((c) => (
            <ColorSwatch
              hex={c.hex}
              selected={colorId === c.id}
              size="md"
              onClick={() => { setColorId((cur) => (cur === c.id ? null : c.id)); setIndex(0); }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
```

`ColorSwatch` (module `9040`): `h-6 w-6 rounded-sm border-black/20`, `style.backgroundColor = hex`, `aria-label={title ?? "Color "+hex}`. Selected: `outline outline-2 outline-offset-2 outline-ink`. **`ColorSwatchEmpty`** exists (`aria-label="No color"`, dashed + diagonal) — **not used** on crawled PDPs.

Live `/m/A01` hero wrapper (no VT name):

```html
<div class="relative overflow-hidden bg-[#f3f1ee]">
  <div style="opacity:1;transform:none">
    <img src="/products/A01/cover.jpg" alt="A01. TOP" class="aspect-[3/4] w-full object-cover "/>
  </div>
</div>
<div class="mt-4 flex flex-wrap items-center gap-2">
  <button type="button" aria-label="Color #F4F0E8" aria-pressed="false" title="#F4F0E8"
    class="h-6 w-6 shrink-0 rounded-sm border border-black/20" style="background-color:#F4F0E8"></button>
  <button type="button" aria-label="Color #1C2A4A" aria-pressed="false" title="#1C2A4A"
    class="h-6 w-6 shrink-0 rounded-sm border border-black/20" style="background-color:#1C2A4A"></button>
</div>
```

### 4.3 `coverSrc` / `imagesForColor` / `coverSrcForColor` (module `12573`)

Exact bodies from the chunk:

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

**Law vs live:**

| Rule (`02` §8 / `05` §7 / `10` FIX 5) | Live `imagesForColor` |
| --- | --- |
| Selected color → `colorId === id` **OR** `colorId == null` (shared) | **Drops** shared `null` when a color is selected |
| Missing tagged set → honest empty / Message {MA} | Falls back to **cover** (`?? coverSrc`) — every chip “works” |
| Grid must not borrow another mã’s folder | `coverSrcForColor` only looks at `product.images` — **good**, *if* admin didn’t copy A01 files onto A02 |

`ProductGrid` already calls `coverSrcForColor(product, selected)` when a tile swatch is selected. Same fallback lie.

### 4.4 Live customer chips vs hub recorded ids

Hub sample (`05` §3.2 — **do not add ids**). Live HTML this evening:

| Mã | Hub `colors[].id` | Live customer chips (hex in `aria-label`) | Honest? |
| --- | --- | --- | --- |
| A01 | `kem`, `xanh` | `#F4F0E8`, `#1C2A4A` | Hex, not words. Hexes *might* be Kem/Xanh — **names missing** |
| A02 | `cham-bi` | **same two hexes as A01** | **No.** Chấm bi is not two navy/cream discs |
| S01 | `kem` | *(none)* | Empty = pass until admin stores the name |
| P01 | `hoa` | four-hex accessory strip | Pattern cannot be four discs |
| P02 | `do` (Hold) | four-hex strip | Hold still Hold; **extra finishes invented** |
| P03 | `den`, `do` | four-hex strip | Extra chips vs two ids |
| P04 | `kem` | four-hex strip | Extra chips |
| P05 | `hong`, `do`, `xanh` (Hold) | four-hex strip | Count mismatch; still Hold / no `$` (good) |
| K01 | *(none)* | none | Pass |
| H01 | *(none)* | none | Pass |

**APPLY does not “fix” this by inventing Vietnamese labels for those hexes.** Origin: show **text ids/names already on that row**; if the row is a leaked palette, **remove chips that are not in `05` §3.2 for that mã**. Admin hex boxes stay on `/admin` (`14` §8).

### 4.5 Two IAs (do not snap them into one strip)

| Surface | Mechanism | Carousel? |
| --- | --- | --- |
| PDP `ProductGallery` | This mã’s `images[]` | **Yes** — watery roll |
| Related rail | Other allowlist mãs | **No** — keep cards + `product-{neighbor}` |
| Home Featured | `FeaturedBoard` + `filterSlide` | **No** — owned by `13` |
| `/c/*` | Kind routes | **No** |

Routes still exist: `/c/ao` (A01+A02), `/c/set` (S01), `/c/phu-kien` (P01–P05), `/c/ao-khoac` (K01), `/c/toc` (H01), `/c/quan` (**empty**). Messenger still: `https://www.facebook.com/profile.php?id=61594312648057`.

### 4.6 What already honors Reduce Motion

`useReducedMotion()` zeros the gallery `x` offset and duration (`0.28 * !reduced`). CSS still does **not** kill card `scale-[1.08]` / `translate-y-1.5` (`10` FIX 1). APPLY: gallery snap `scroll-behavior: auto` under reduce; no mask animation; frost overlays `display: none` or opacity 0.

---

## 5. Kelly Ying look — steal the rhythm, refuse the glass

Kelly Ying Boutique is the **look + livestream cadence** reference, not the commerce engine and **not a copy deck** (`01` §1.3; `10` §5).

| Their pattern | Steal for the gallery? |
| --- | --- |
| SKU on the card (`V984. …`) | Steal the *job*: mã visible. Print **A01**, never `V984`. |
| Collection chips + counts | Already on Featured. Do not add Sleepwear slides. |
| Cart / `$10 over $300` | **Refuse.** |
| Dense 2-up phone grid | Keep. Gallery is PDP, not PLP. |
| Dress product descriptions | **Refuse.** No stock copy. |

**Look lock (do not restyle away):**

- Cormorant Garamond display + Be Vietnam Pro UI.
- Paper / ink / gold / blush; `ma-mark` tabular nums; 11px uppercase tracking.
- Gold **hairline** selected rule (`h-px bg-gold`) on **text** color pills — same language as `featured-tab`, not a fat iOS capsule.
- Editorial `/editorial/*` is mood, never a gallery slide for a mã (`07` §11.0).
- No Inter takeover, no dark luxury theme, no Horizon clone.

Frosted peeks must read as **paper fog**, not iOS gray glass: `color-mix(in oklab, var(--paper) 72%, transparent)` over `--blush` / `#f3f1ee`. Gold is the hairline and the Message CTA, not a blur tint.

---

## 6. Reliability law (frost must not lie)

Write these as code-review questions. If a PR answers “the peek looked expensive,” it is not ready.

1. **Identity.** After snap / fade / frost, the URL mã, the `ma-mark`, the Message CTA, and the hero folder agree. `/m/A01` never shows `/products/A02/cover.jpg` as a gallery slide.
2. **Status.** Hold vs Available stays **text** mid-roll. P02 / P05 never flash a dollar (`09` MOT-08).
3. **Color honesty.** Visible shots after a color activate are `colorId === selected.id || colorId == null`. Never another mã. Never a CSS-tinted cover pretending to be Xanh (`05` §3.2: do not rename `cham-bi`).
4. **Empty is a pass.** One file → no peek, no dots, no mask. Zero files → blush box + existing “Message {MA} for real photos” — not Unsplash, not Kelly Ying, not A02.
5. **CTA.** Sticky Message stays clickable. Do not `await` snap. `::view-transition { pointer-events: none }` stays (`10`).
6. **Interrupt.** Second color tap cancels the first fade. Esc closes lightbox on frame 1 (`10` §6.7). Finger on the rail must beat a leftover `scroll-behavior: smooth` from a previous `scrollTo`.
7. **No checkout metaphor.** No bag, no flying thumbnail, no “Added.”
8. **No wrap to another product.** `index % n` is **this filter’s** length, not the related rail.
9. **Same data, every surface.** Home swatch (if any) = PDP pills = admin row (`09` NAV-09). A leaked four-hex accessory palette fails this.

---

## 7. Recipe A — CSS `mask-image` (edge peeks)

**Job:** show that another shot exists by **dissolving** the neighbor into paper, without a pointer-blocking overlay.

Google Chrome’s modern-web-guidance: a gradient mask is better than a semi-opaque overlay because the **page background shows through** and hits/selection still work ([soft-edge content fade](https://github.com/GoogleChrome/modern-web-guidance/blob/main/skills/modern-web-guidance/guides/visual-design/soft-edge-content-fade.md)). Pqina: mask the **scroll container**; reserve a scrollbar shield if a scrollbar is visible ([fade-out overflow](https://pqina.nl/blog/fade-out-overflow-using-css-mask-image/)). On iOS, overlay scrollbars usually paint **above** the mask (tw-fade notes) — good.

### 7.1 Default (single shot) — no mask

```css
.ky-gallery-port[data-count="1"] {
  -webkit-mask-image: none;
  mask-image: none;
}
```

### 7.2 Peek rail (≥2 shots)

Apply the mask to the **port**, not to each `<img>` (masking each image independently creates a hole in the garment).

```css
.ky-gallery-port {
  --peek: 12%;               /* neighbor visible */
  --fade: 28px;              /* dissolve width */
  overflow-x: auto;
  overflow-y: hidden;
  overscroll-behavior-x: contain;
  scrollbar-width: none;
}
.ky-gallery-port::-webkit-scrollbar { display: none; }

.ky-gallery-port[data-count="n"] { /* n >= 2 */
  -webkit-mask-image: linear-gradient(
    to right,
    transparent 0,
    #000 var(--fade),
    #000 calc(100% - var(--fade)),
    transparent 100%
  );
  mask-image: linear-gradient(
    to right,
    transparent 0,
    #000 var(--fade),
    #000 calc(100% - var(--fade)),
    transparent 100%
  );
}
```

Alpha masks: **opaque** mask pixels keep the element; transparent hide it ([MDN `mask-image`](https://developer.mozilla.org/en-US/docs/Web/CSS/mask-image)). Prefix `-webkit-mask-image` remains required for older Safari.

### 7.3 Scroll-aware fade (progressive)

If `@supports (animation-timeline: scroll(self inline))`, thicken the start fade only when `scrollLeft > 0`, end fade only when not at max ([tw-fade](https://github.com/petekp/tw-fade); Stack Overflow `animation-timeline: scroll(self)`). Safari 17–18 without SDA: **static dual fade is OK**. Do not require JS to compute mask stops on every `scroll` event (that is the CPU tax Chrome’s SDA case studies left).

### 7.4 Fallback

```css
@supports not ((mask-image: linear-gradient(black, transparent)) or (-webkit-mask-image: linear-gradient(black, transparent))) {
  .ky-gallery-port[data-count="n"] { mask-image: none; }
  .ky-gallery-port[data-count="n"]::before,
  .ky-gallery-port[data-count="n"]::after {
    content: "";
    position: absolute; top: 0; bottom: 0; width: var(--fade);
    pointer-events: none;
    background: linear-gradient(to right, var(--paper), transparent);
  }
  .ky-gallery-port[data-count="n"]::after {
    right: 0;
    background: linear-gradient(to left, var(--paper), transparent);
  }
}
```

`pointer-events: none` is mandatory on overlay fallbacks so swipe still hits the rail.

### 7.5 Do not

- Mask the **Message** sticky footer.
- Animate `mask-size` as a color wipe (`10` §8.3: wipes feel like a different piece).
- Use a PNG sprite mask (`steps()` carousel tutorials). Wrong metaphor; extra asset; fails Reduce Motion.

---

## 8. Recipe B — `backdrop-filter` (frosted chrome, not the garment)

**Job:** the peek reads as **fogged paper**, like a vitrine edge — not iOS Liquid Glass on the cloth.

MDN: `backdrop-filter` blurs **pixels behind** the element, up to the nearest **backdrop root**. Parents with `opacity < 1`, `filter`, `mask`, `clip-path`, or another `backdrop-filter` **clip the blur to that parent** ([MDN `backdrop-filter`](https://developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter)). This is why frosting an overlay **inside** `overflow: hidden` + `border-radius` + `transform` often **paints nothing** (WebKit [bug 205019](https://bugs.webkit.org/show_bug.cgi?id=205019); Firefox [1860175](https://bugzilla.mozilla.org/show_bug.cgi?id=1860175)).

### 8.1 Legal structure

```text
.ky-gallery-shell          /* position:relative; NO overflow:hidden if frost is a child */
  .ky-gallery-port          /* overflow-x:auto; scroll-snap; mask-image (Recipe A) */
     .ky-slide * n
  .ky-frost-start           /* pointer-events:none; left strip */
  .ky-frost-end             /* pointer-events:none; right strip */
```

Frost strips are **siblings** of the port (or a non-clipped overlay), not descendants of a `transform`ed `motion.div`. Live `AnimatePresence` wrapping the **img** is exactly the stacking-context trap — **do not** put `backdrop-filter` on that `motion.div`.

```css
.ky-frost-start,
.ky-frost-end {
  position: absolute;
  top: 0; bottom: 0;
  width: max(12px, var(--fade, 28px));
  pointer-events: none;
  z-index: 2;
  background: color-mix(in oklab, var(--paper) 55%, transparent);
  -webkit-backdrop-filter: blur(10px) saturate(120%);
  backdrop-filter: blur(10px) saturate(120%);
}
.ky-frost-start { left: 0; }
.ky-frost-end { right: 0; }

@media (prefers-reduced-motion: reduce) {
  .ky-frost-start, .ky-frost-end {
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
    background: color-mix(in oklab, var(--paper) 78%, transparent);
  }
}
```

Blur **10px**, not 40px. Large blurs on a 58vh hero are the “shuddering shamble” Bebber’s commenters already documented (`13` §13). Saturate ≤120% — this is paper, not candy glass.

Always duplicate `-webkit-backdrop-filter` ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter)). Baseline 2024: fine for current iOS; still prefix.

### 8.2 When frost is off

- `data-count="1"`
- `prefers-reduced-motion: reduce`
- `@media (hover: none)` **does not** turn frost off — phones are the primary peek device
- Forced-colors / `prefers-contrast: more`: drop blur; keep a 1px `--line` edge so the port is still a box

### 8.3 Forbidden

| Technique | Why |
| --- | --- |
| `backdrop-filter` on `<img>` or `.shimmer` | Frosts the garment; LCP; Safari overflow bugs |
| SVG `feDisplacementMap` over covers | Fabric lie (`13` §2.8) |
| `filter: url(#goo)` on the rail | Goo fuses two SKUs into one blob |
| Chromatic aberration / specular “Liquid Glass” shaders | OS chrome; fights gold hairline |
| Frost on Featured grid (`13`) | Wrong surface |

Live CSS already generates `.backdrop-blur-md`. **Do not** slap it on the hero to “use the utility.”

---

## 9. Recipe C — CSS `scroll-snap` (the watery roll’s physics)

**Job:** finger-driven paging that feels like iOS `viewAligned` / paging, **without** a JS carousel library and **without** Motion `drag` on the same node.

Native scroll keeps momentum, rubber-banding, trackpad, keyboard, and screen-reader scroll. JS carousels fake this badly ([CodeFronts scroll-snap slider](https://codefronts.com/layouts/css-grid-layouts/scroll-snap-slider/)).

### 9.1 Port + slides

```css
.ky-gallery-port {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: 78%;          /* 11% peek each side when padded */
  gap: 12px;
  overflow-x: auto;
  overscroll-behavior-x: contain;
  scroll-snap-type: x mandatory;
  scroll-padding-inline: 11%;
  padding-inline: 11%;
  -webkit-overflow-scrolling: touch; /* legacy iOS momentum; harmless if ignored */
}
.ky-gallery-port[data-count="1"] {
  grid-auto-columns: 100%;
  padding-inline: 0;
  scroll-padding-inline: 0;
  scroll-snap-type: none;
}
.ky-slide {
  scroll-snap-align: center;
  scroll-snap-stop: always;
  width: 100%;
  min-width: 0;
}
.ky-slide img {
  display: block;
  width: 100%;
  aspect-ratio: 3 / 4;
  object-fit: cover;
}
```

**Why 78% / 11%:** the peek *is* the leftover. `scroll-padding-inline` **must** match padding or the snap point ignores the gutter ([MDN / cssShowcase](https://www.cssshowcase.com/articles/layout/scroll-snap)). Older iOS Safari: prefer **explicit** slide widths (px from `ResizeObserver` or `cqw`) if `%` columns collapse ([W3Tweaks iOS note](https://www.w3tweaks.com/css/css-scroll-snap-explained/)).

`mandatory` vs `proximity`: carousels use **mandatory** so a shot never rests half-cut ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/scroll-snap-type)). `proximity` is for long editorial pages.

`scroll-snap-stop: always`: a fast flick **stops on the next shot**, not three later — important when the next shot is the seam / print (Hoa, Chấm bi). Safari: works for **touch**; can ignore stop on some `scrollBy` paths ([caniuse `scroll-snap-stop`](https://caniuse.com/mdn-css_properties_scroll-snap-stop)). Color-tap `scrollTo` should target the **element**, not `scrollLeft += clientWidth`.

### 9.2 Programmatic scroll (color tap / dots)

```js
slideEl.scrollIntoView({ inline: "center", block: "nearest", behavior: reduced ? "instant" : "smooth" });
```

Prefer `scrollIntoView` on the **slide node** over `port.scrollBy({ left: port.clientWidth })`. WebKit has historically kept a **stale snap point** after programmatic scroll until a later drag ([WebKit PR 64111](https://github.com/WebKit/WebKit/pull/64111)). If a color tap lands on the wrong shot on iPhone, re-call `scrollTo` on `scrollend` (or a 100ms timeout fallback where `scrollend` is missing).

Do **not** set `scroll-behavior: smooth` on `html` for this port — the shop’s reduce query already sets `html { scroll-behavior: auto }`. Scope smooth to the port, gated by `useReducedMotion`.

### 9.3 Keyboard + APG

WAI-ARIA APG Carousel: previous/next, don’t auto-rotate, don’t trap focus, name the region ([APG Carousel](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/)).

Minimum:

- `aria-roledescription="carousel"` on the shell (or a labelled `region`).
- Each slide: `role="group"` + `aria-roledescription="slide"` + `aria-label="{n} of {n} · {MA}"`.
- Prev/next **buttons** (44×44), visually gold hairline, **in addition to** swipe. Live click-on-image-to-advance is an undocumented control — keep swipe + buttons; image click should open **lightbox** (`10` FIX 3), not skip.
- Dots: `aria-current="true"` on the snapped slide’s control; don’t rely on 6px alone (1.4.1).
- Do not steal vertical page scroll (no `preventDefault` on vertical touch).

Chrome 135+ `::scroll-marker` / `scroll-marker-group` can generate dots from CSS ([Chrome, *Carousels with CSS*](https://developer.chrome.com/blog/carousels-with-css); [MDN CSS carousels](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Overflow/Carousels)). **Safari/Firefox: not supported** (caniuse scroll-marker, 2026-09-09). APPLY: **real buttons** as the baseline; `::scroll-marker` as progressive enhancement behind `@supports`. Empty `content: " "` fails WCAG 4.1.2 — MDN requires a name (`attr(data-accname)`).

### 9.4 RTL

Shop UI is EN+VN; layout is LTR today. If `dir="rtl"` ever lands, snap axis is **inline**. Test `scroll-padding-inline` (not `padding-left` only).

---

## 10. Recipe D — Framer Motion (listen; don’t fight the scroller)

Live gallery already uses `motion/react`: `useReducedMotion`, `AnimatePresence mode="wait"`, `x` slide, `springSoft` on **tiles**. `13` owns `filterSlide` on Featured. This recipe is **PDP only**.

Motion docs: `useScroll({ container })` tracks `scrollX` / `scrollXProgress` and can ride `ScrollTimeline` ([Motion `useScroll`](https://motion.dev/docs/react-use-scroll)).

### 10.1 Do this

| Use | How |
| --- | --- |
| Native snap rail | CSS Recipe C. Motion does **not** `drag` the same node ([SO drag vs width bugs](https://stackoverflow.com/questions/77751989/framer-motion-drag-carousel-not-working-properly)). |
| Center scale / opacity | `useScroll({ container: portRef })` + `useTransform` on **non-image** chrome (dot scale, gold hairline). Optional slide `scale: 0.97 → 1` on the **wrapper**, not a blur. |
| Color pill underline | `layoutId="pdp-color"` + `h-px bg-gold` + `springSoft` — **same meniscus rules as `13` FIX 1**. Reduce → `layoutId` undefined. |
| Color change on the **set** | When `colorId` changes, **replace** the slide list, `scrollTo(0)`, **opacity 150–250ms** on the port (`10` §8.3). Do **not** reuse `x: 24` wait-mode for color. |
| Lightbox | `10` FIX 3. Motion for veil opacity only. |

### 10.2 Do not do this

| Anti-pattern | Why |
| --- | --- |
| `drag="x"` + `scroll-snap` on one track | Two physics systems; iOS rubber-band fights `dragConstraints` |
| `AnimatePresence mode="wait"` for **shot-to-shot** | Native scroll already interpolates. Wait-mode blanks the hero (`13` §8.2). |
| `filterSlide` x on the gallery | That’s Featured’s metaphor. A gallery that translates like a new page feels like a new mã. |
| `staggerChildren` on slides | 70ms × n is a mosaic job (`13` §8.2). |
| `layoutId` reused as `"featured-tab"` | Collision with home. Use `"pdp-color"` / `"pdp-dot"`. |
| Parallax on the garment (`useTransform` x on `<img>`) | WCAG 2.3.3 names large spatial moves; also a fabric lie if crop shifts |

### 10.3 Color-change snippet (keep names)

```tsx
const reduced = useReducedMotion();
const shots = imagesForColor(product, selectedId); // APPLY: include shared nulls

<motion.div
  key={selectedId ?? "all"}
  initial={reduced ? false : { opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: reduced ? 0 : 0.2, ease: [0.22, 1, 0.36, 1] }}
>
  <div ref={portRef} className="ky-gallery-port tab-scroll" data-count={shots.length}>
    {shots.map((img) => (
      <div className="ky-slide" key={img.src} data-colorid={img.colorId ?? "shared"}>
        <img src={img.src} alt={displayTitle(product)} />
      </div>
    ))}
  </div>
</motion.div>
```

Ease `[.22,1,.36,1]` is already live. Duration **0.20s** (color) vs **0.28s x-slide** (delete the x-slide).

If `shots.length === 0`: blush box + Message line. **Do not** `?? coverSrc`.

### 10.4 Observing the snap (dots / `aria-current`)

Prefer `onScroll` + `scrollend`, or `IntersectionObserver` with `root: port`, `threshold: 0.6`. Do not run `setState` every pixel. `useScroll().scrollX` may drive a motion value for a gold progress hairline under the dots without React render.

---

## 11. `colorId` gallery link (the whole lesson in one contract)

Sister `05` already wrote the bind rule. This section is the **runtime** contract `ProductGallery` must obey. Catalog.v1 shape (kit / `05`):

```json
{
  "ma": "A01",
  "colors": [{ "id": "kem", "name": "Kem" }],
  "images": [
    { "src": "/products/A01/cover.jpg", "colorId": "kem", "order": 1 }
  ]
}
```

Live admin still speaks hex boxes (`08-sell-test-observed`; `14` §8). **Customer** `name` (or id pretty-printed) is what the lookbook prints. Do not mint `A01-KEM`. Do not invent `/products/A01/001.jpg` because HQ had it — **HEAD 404 this crawl**.

### 11.1 Filter (replace live `imagesForColor`)

```js
function imagesForColor(product, colorId) {
  const n = product.images.filter((img) => img.src && img.src.trim());
  if (colorId == null) return n; // "all" / no selection: shared + tagged (honest mixed only when no chip selected)
  return n.filter((img) => img.colorId === colorId || img.colorId == null);
}
```

When a chip **is** selected, `02` §8 wants **tagged + shared**, not the full mixed set of other colors. Live code is the opposite of Shopify-default mixed (good direction) but **too strict** (drops shared) and then **too loose** (cover fallback).

**Selected chip:**

1. `tagged = images where colorId === id`
2. `shared = images where colorId == null`
3. `view = tagged.concat(shared)` (or tagged-only if you must — **document the pick**; `10` FIX 5 uses OR null)
4. If `tagged.length === 0` and `shared.length === 0` → empty state, **not** coverSrc
5. If `tagged.length === 0` and shared exists → show shared + line `Chưa có ảnh màu này · Message {MA}` — do not tint shared toward a guessed hex

### 11.2 Chip row (customer)

Only if `product.colors.length > 0` **and** each item has an `id` that is on **that** mã’s allowlisted vocabulary (`05` §3.2). **No hex circles.**

```text
rounded-full px-3 min-h-10 text-[11px] uppercase tracking-[0.14em]
selected: text-ink + gold h-px (layoutId="pdp-color")
idle: text-muted hover:text-ink
aria-pressed
visible name: Kem, Xanh, Hoa, Đỏ, Hồng, Đen, Chấm bi
echo: Đang xem: {name}
```

Toggle-to-null (live) is OK if “all” is a real mode **and** `aria-pressed` reflects it. Prefer **radio** semantics (`02` §7) so two colors cannot look selected. `ColorSwatch` hex component stays **admin-only** (`14`).

Grid `ColorSwatch` on home cards: same law. If you keep a preview, use **photo** chips later — not discs (`02` §5.2). Tonight’s home cards should not paint A02 as cream+navy discs.

### 11.3 Ids you may show IF present on that row (do not add missing)

`A01 kem,xanh · S01 kem · P01 hoa · P02 do · P03 den,do · P04 kem · P05 hong,do,xanh · A02 cham-bi · K01 none · H01 none`

`cham-bi` stays `cham-bi` / “Chấm bi”. Do not rename to Trắng.

### 11.4 Scroll + color

```text
on color activate
  → set selected id
  → rebuild shots via imagesForColor (shared OR tagged)
  → set index 0
  → scroll slide[0] into center (instant if reduced)
  → do not change mã, $, Hold, route
  → do not fetch /products/A02/ from /m/A01
  → prefetch the first tagged file of the *next* idle color after idle (optional)
```

Size chips, if any, do **not** swap photos unless a file is size-tagged (`10` §8.2). Default: color-keyed only.

### 11.5 Lightbox set

`10` FIX 3: lightbox `src` list = **current filter only**. Arrows never wrap to A02. Today the only 200 on A01 is `/products/A01/cover.jpg`. Extra slides appear when admin uploads files that **200** on this host.

---

## 12. Watery roll (how this file uses `13`)

`13` = **tabs + grid pour**. This file = **gallery roll**. Do not stack both metaphors on one tap.

| Gesture | Watery meaning | Technique |
| --- | --- | --- |
| Finger on PDP shots (same color) | **Roll** — neighbor peeks, snaps, edge fogs | Recipes A+C (+ B optional) |
| Color text pill | **Finish change** — short opacity; gold hairline meniscus | Recipe D opacity + `13` meniscus on `pdp-color` |
| Featured All → Tops | **Pour** the grid | `13` only |
| Home card → PDP | **Morph** `product-{MA}` | `10` FIX 3; no gallery clip on `::view-transition-old(root)` (`13` §9) |

**Timing:** roll is user-driven (no budget except snap settle). Color opacity **150–250ms**. Meniscus ≤300ms (`13` §12). Do not run gallery x-slide **and** Featured `filterSlide` **and** `shimmer` as one “premium” stack.

Goo: still **gold-rule wrapper only**, never on slides (`13` FIX 1).

---

## 13. Reduced-motion + vestibular

| Criterion | Gallery impact |
| --- | --- |
| [2.2.2](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) A | No autoplay. Do not add a second infinite frost pulse. `.shimmer` remains the known loop (`10` FIX 1). |
| [2.3.1](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html) A | No strobing dots. |
| [2.3.3](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) AAA | Color fade + meniscus + optional scale. Sufficient: C39 + `useReducedMotion`. Native snap may remain (user-driven scroll is not “animation from interaction” in the same way; still disable **smooth** programmatic scroll). |
| [1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) A | Words + `aria-pressed` + `Đang xem`. Hex discs fail. |
| [2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) AA (24px) / boutique 44px | Pills `min-h-10`. Prev/next 44×44. Dots are indicators; slides are the targets. |

Apple: fade, don’t zoom. Reduced gallery = **instant src / instant scrollLeft** + no frost blur + no mask animation + no `x: 24`.

MDN: `prefers-reduced-motion: reduce` means remove, reduce, or replace; scaling/panning large objects are vestibular triggers ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)). A 78% peek rail that **the user** scrolls is OK; a Motion `scale: 1.08` on the hero is the same family as the card hover `10` already asked to `motion-safe:`.

---

## 14. Timing budget

| Interaction | Budget | Live 2026-09-09 evening | APPLY |
| --- | --- | --- | --- |
| Color pill feedback (`aria-pressed` + hairline start) | ≤100ms ([NN/G attention](https://www.nngroup.com/articles/animation-usability/)) | Outline on hex — OK speed, wrong control | Text + `layoutId` |
| Color image swap | 150–250ms opacity (`10`) | **280ms + x-translate + wait** | Opacity only; no wait blank |
| Shot-to-shot | Native snap settle (UA) | Click modulo + 280ms x | Native snap; no Motion x |
| Frost / mask | Static or SDA | n/a | No extra clock |
| Lightbox open | ≤200ms veil | n/a | `10` FIX 3 |
| Home → PDP VT | ≤300ms | Names mismatch | `10` FIX 3 first |
| `--duration-move` | 400ms | Unused on gallery | Do not bind |

Jakob Nielsen: 0.1s instantaneous; 1s flow ([*Response Time Limits*](https://www.nngroup.com/articles/response-times-3-important-limits/)). Color tap is a **direct tap**.

---

## 15. Performance + Safari traps

- LCP: keep `rel=preload` on **this** cover only. Live `/m/A01` also preloads **A02** for the related rail — don’t add every color’s HQ. Secondary slides `loading="lazy"` + `fetchpriority="low"`.
- Animate `transform` / `opacity` / simple `clip-path`. Do not animate `width`, `filter`, or `box-shadow` on the hero ([Lewis FLIP](https://aerotwist.com/blog/flip-your-animations/)).
- `backdrop-filter` on two 28px strips, not the 3/4 hero.
- `mask-image` on the port is cheap; don’t also `filter: blur()` the slides.
- ISR `x-nextjs-stale-time: 300` is a cache clock. Filter from images **already in the payload**.
- iOS: `overscroll-behavior-x: contain` so the gallery doesn’t steal back-swipe navigation.
- Don’t combine `overflow: hidden` parent + `border-radius` + `transform` + child `backdrop-filter` (WebKit 205019).
- Chrome `::scroll-marker` is enhancement only (no Safari).

---

## 16. APPLY — [sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)

**Owner:** Origin `sassy-closet-shop` (not this kit).  
**Look:** Kelly Ying paper / ink / gold. **Job:** watery **gallery roll** + honest **`colorId`**.  
**Mã:** allowlist only. **No** Square Save. **No** FB Send. **No** cart. **No** Excel. **No** intake.  
**No stock copy.**

Human-readable ticks. **Paste block is §21.**

### 16.0 Do not touch (lock — tick first)

- [ ] Cormorant Garamond + Be Vietnam Pro.
- [ ] Paper / ink / gold / blush; `ma-mark`; 11px tracking; gold **`h-px`** (not a fat pill).
- [ ] Keyframes `announce-fade`, `shimmer-slide`, `cta-flash` remain.
- [ ] `FeaturedBoard` / `featured-tab` / `filterSlide` / `springSoft` remain (owned by `13` — change bodies there, not here).
- [ ] Exports `ProductGallery`, `imagesForColor`, `coverSrc`, `coverSrcForColor`, `ColorSwatch` **remain as names** (bodies change).
- [ ] Livestream rail + Page `61594312648057`.
- [ ] Message-first CTAs; footer **Zelle** word; no personal name.
- [ ] Hold on **P02, P05** (no published `$`).
- [ ] `/admin` out of the main nav; hex boxes **may stay on admin**.
- [ ] Intake host unchanged. Excel untouched.

### 16.1 Customer chips (kill hex on the lookbook)

`rg -n "ColorSwatch|ProductGallery|imagesForColor|coverSrcForColor"`

- [ ] PDP + home grid: **no** `ColorSwatch` hex discs for shoppers.
- [ ] Text pills only, ids from **that** row (`05` §3.2). A02 = Chấm bi only (or empty until stored). A01 = Kem / Xanh **words** if those ids are on the row — not `#F4F0E8`.
- [ ] Strip leaked four-hex accessory palettes from P01–P05 unless each hex maps to a **stored id on that mã**. Do not invent names to justify the discs.
- [ ] S01 / K01 / H01 stay chip-less until admin stores colors.
- [ ] `Đang xem: {name}` when a chip is selected.
- [ ] Selected rule: `layoutId="pdp-color"` + `h-px bg-gold` + `springSoft`; reduce → instant.

### 16.2 `imagesForColor` body

- [ ] Include `colorId == null` shared shots when a color is selected (`10` FIX 5).
- [ ] **Delete** `src ?? coverSrc` as a success path for a selected color with no tagged files.
- [ ] Empty tagged+shared → blush + existing Message photos line.
- [ ] Never load `/products/A02/` on `/m/A01`.
- [ ] Do not invent `001.jpg` URLs that 404.

### 16.3 Watery roll (snap + mask + optional frost)

- [ ] If `shots.length === 1`: full-bleed hero, **no** mask, **no** frost, **no** dots, no peek gutter.
- [ ] If `shots.length >= 2`: Recipe C snap rail (78/11 or 86/11 — pick one), Recipe A mask, optional Recipe B frost **siblings**.
- [ ] `scroll-snap-stop: always`; hide scrollbar (`tab-scroll` already exists — reuse).
- [ ] Prev/next 44×44 + dots with `aria-current`. Image click → **lightbox**, not modulo skip.
- [ ] `mode="wait"` + `x: 24` **removed** from shot-to-shot. Color change = opacity 150–250ms.
- [ ] Reduce Motion: instant swap, `scroll-behavior: auto`, no frost blur, no mask animation.

### 16.4 Hooks still required from `10` / `13` (do not regress)

- [ ] `view-transition-name: product-{THIS mã}` on the **hero shell** (`10` FIX 3). Related rail keeps neighbor names.
- [ ] Lightbox ink/paper (`10` FIX 3). Set = current color filter.
- [ ] Featured watery (`13`) does not freeze Message or invent Q01.
- [ ] `::view-transition { pointer-events: none }`.

### 16.5 Reliability / commerce

- [ ] Message A01 still opens Page `61594312648057` (or `m.me?ref=A01` when ready — site never Sends).
- [ ] P02/P05 Inbox for price.
- [ ] `/m/A03` 404.
- [ ] View-source: no `e.tb.cn`, no `¥`, no `V984`, no `A03`.

### 16.6 Verify (Origin, after watery roll)

Desktop + phone + OS Reduce Motion + keyboard:

1. `/m/A01` — cover visible; chips are **words** (or none if row emptied). Message A01. Hero VT name `product-A01`.
2. If ≥2 real 200 files: swipe snaps; neighbor peeks; frost/mask on edges only; photos sharp in the center.
3. Color Kem → only A01 Kem+shared. Color Xanh → not A02. Reduce = instant.
4. `/m/A02` — **not** A01’s two discs. Chấm bi text or empty.
5. `/m/P02` `/m/P05` — Hold, no `$`. No four mystery discs unless those ids are stored.
6. `/m/K01` `/m/H01` `/m/S01` — no invented chips. Single cover, no fake peek.
7. Lightbox: Esc / ✕ / backdrop; focus return; Message still works.
8. `/` Featured still 10; `13` pour not broken. `/c/quan` empty.

---

## 17. Anti-patterns (quick refuse list)

1. iOS Liquid Glass over the hero.  
2. Hex customer discs (`ColorSwatch` on PDP).  
3. Peeking A02 inside A01’s port.  
4. Duplicating the cover to fake a second slide.  
5. Autoplay / Ken Burns on the garment.  
6. Motion `drag` + CSS snap on one node.  
7. `imagesForColor` fallback to cover for a missing color.  
8. Inventing `Q01` / `A03` / `AO001` / `V984`.  
9. Kelly Ying or Apple **copy** in titles, alts, or captions.  
10. `feDisplacementMap` / goo on photos.  
11. `scroll-snap` on the Featured grid.  
12. Embla / Swiper / Keen — not needed; native snap is the product.  
13. Excel edits, intake restyle, Square Save, FB Send.  
14. `::scroll-marker` **without** real named buttons (Safari).  
15. Stock Unsplash / “similar item” filler when tagged photos are empty.

---

## 18. Acceptance (sell-test watery roll)

- [ ] Kelly Ying tokens + fonts unchanged.  
- [ ] Customer colors are **words** tied to stored ids; hex only in admin.  
- [ ] Gallery filter is `colorId` OR shared; never another mã.  
- [ ] Peek + snap only when ≥2 honest 200 files.  
- [ ] Frost/mask are edge chrome; center garment is unfiltered.  
- [ ] Reduce Motion: no spatial gallery tween; chips still work.  
- [ ] Hold P02/P05; allowlist ten; no Excel; no intake.  
- [ ] No Apple/Kelly Ying/Taobao stock copy.  
- [ ] Preview URL, not Production, until Boss yes.

---

## 19. Sources

### 19.1 Shop law and as-built

- Live host 2026-09-09: https://sassy-closet-shop.vercel.app — CSS `34vl_zddoo4ws.css`; PDP JS `1xr62vxitay1m.js`; helpers module `12573`; home motion `3_93acjqq2t4q.js`.  
- This repo: `README.md`, `sassy-closet/BOSS.md`, `sassy-closet/README.md`.  
- PR #18 `SELL_CATALOG_CONTRACT.md`.  
- Slack `#shop-decisions` 2026-09-04 — Track ON; bots draft only.  
- Sisters `02`, `05`, `10`, `13`, `14`.  
- Kelly Ying Boutique — <https://www.kellyyingboutique.net/> (look only; no copy).  
- Apple marketing pages (color *names* only): <https://www.apple.com/iphone-17/>, <https://www.apple.com/iphone-air/>.

### 19.2 Apple / iOS

- HIG Collections — <https://developer.apple.com/design/human-interface-guidelines/collections>  
- HIG Scroll Views — <https://developer.apple.com/design/human-interface-guidelines/scroll-views>  
- HIG Page Controls — <https://developer.apple.com/design/human-interface-guidelines/page-controls>  
- HIG Motion — <https://developer.apple.com/design/human-interface-guidelines/motion>  
- Reduced Motion evaluation — <https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria/>  
- Liquid Glass (chrome, not product renders) — <https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/>  
- SwiftUI `scrollTargetBehavior` / `viewAligned` (paging analog) — community writeups of iOS 17 APIs.

### 19.3 CSS recipes

- MDN `scroll-snap-type` — <https://developer.mozilla.org/en-US/docs/Web/CSS/scroll-snap-type>  
- MDN `scroll-snap-stop` — <https://developer.mozilla.org/en-US/docs/Web/CSS/scroll-snap-stop>  
- MDN `scroll-padding` — <https://developer.mozilla.org/en-US/docs/Web/CSS/scroll-padding>  
- MDN `mask-image` — <https://developer.mozilla.org/en-US/docs/Web/CSS/mask-image>  
- MDN `backdrop-filter` (backdrop root) — <https://developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter>  
- MDN CSS carousels / Overflow 5 — <https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Overflow/Carousels>  
- Chrome, *Carousels with CSS* (`::scroll-marker`, Chrome 135+) — <https://developer.chrome.com/blog/carousels-with-css>  
- Chrome SDA ecommerce (clip-path; CPU) — <https://developer.chrome.com/blog/css-ui-ecommerce-sda>  
- GoogleChrome modern-web-guidance, soft-edge fade — <https://github.com/GoogleChrome/modern-web-guidance/blob/main/skills/modern-web-guidance/guides/visual-design/soft-edge-content-fade.md>  
- Pqina, mask overflow fade — <https://pqina.nl/blog/fade-out-overflow-using-css-mask-image/>  
- WebKit `backdrop-filter` + overflow — <https://bugs.webkit.org/show_bug.cgi?id=205019>  
- WebKit stale snap after programmatic scroll — <https://github.com/WebKit/WebKit/pull/64111>

### 19.4 Motion

- Motion `useScroll` — <https://motion.dev/docs/react-use-scroll>  
- Motion layout / `layoutId` — <https://www.framer.com/motion/layout-animations/>  
- Paul Lewis, FLIP — <https://aerotwist.com/blog/flip-your-animations/>  
- Do not combine drag + snap — <https://stackoverflow.com/questions/77751989/framer-motion-drag-carousel-not-working-properly>

### 19.5 UX / a11y / fashion PDP

- NN/G animation purpose / attention / microinteractions / response times — see `10` §16 / `13` §17.  
- NN/G ecommerce PDPs — <https://www.nngroup.com/articles/ecommerce-product-pages/>  
- Baymard zoom — <https://baymard.com/blog/ensure-sufficient-image-resolution-and-zoom>  
- Baymard mobile color swatches — <https://baymard.com/blog/mobile-interactive-color-swatches>  
- Craftshift variant images / mixed gallery — <https://craftshift.com/shopify-variant-images-complete-guide/>  
- WAI-ARIA APG Carousel — <https://www.w3.org/WAI/ARIA/apg/patterns/carousel/>  
- WCAG 2.2.2 / 2.3.3 / 1.4.1 / C39 — W3C Understanding docs.  
- A11yFix lightbox — <https://blog.a11yfix.dev/blog/product-image-zoom-lightbox-accessibility/>

### 19.6 Weaker / vendor (directional only)

- CodeFronts liquid-glass cards / peek sliders — OS toys; steal **snap math**, refuse glass on photos.  
- AirPods Max clone sliders (GitHub/Letstartdesign) — gradient body bg; **refuse** as a look.  
- Theme posts claiming “+% conversion from carousels” without method are **not** shop law.

---

## 20. Open questions (do not answer by inventing)

1. Who stored A02’s two hexes and the accessory four-strip — Blob drift vs a shared palette component? Origin inspects admin JSON; this kit does not invent the names.  
2. Will admin keep `colors[].hex` forever? Customer still must see **text**. Mapping hex→id without a stored id is invention.  
3. Recipe B frost on or off by default? Mask-only is enough if Safari backdrop+overflow remains flaky.  
4. `::scroll-marker` as enhancement once Safari ships — not a 2026-09-09 requirement.  
5. After Granola access: did a meeting already ban peek gutters on PDP? Until then, ≥2 files ⇒ peek.  
6. Livestream **days** still unlocked (`01`). Gallery cannot invent Sunday/Monday.

---

## 21. PASTE INTO ORIGIN AGENT (do not paraphrase)

Copy everything between the markers into a Cloud Agent on the **Origin `sassy-closet-shop` repo** (the git behind https://sassy-closet-shop.vercel.app). Not this kit. Not intake `sassy-closet/`. Not `excel-kit/`. Not Official Excel.

```text
===== BEGIN ORIGIN PASTE — iOS frosted carousel / watery roll (LEARN 16) =====

You are editing Origin sassy-closet-shop. Ship a WATERY GALLERY ROLL on the
EXISTING ProductGallery: CSS scroll-snap + edge mask + optional frosted
peek CHROME + colorId-linked shots. Do not restyle the boutique. Do not
invent mã. Do not add iOS Liquid Glass over photos. Do not copy Apple,
Kelly Ying, or Taobao product copy. Do not touch intake or Excel.

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
Do NOT apply backdrop-filter / SVG goo / displacement to product photos.

FIND FILES (rg — names may differ; match these strings, then edit those files):

  rg -n "ProductGallery|ColorSwatch|imagesForColor|coverSrcForColor|coverSrc"
  rg -n "Color #F4F0E8|aria-label={\`Color"
  rg -n "featured-tab|filterSlide|springSoft"
  rg -n "announce-fade|shimmer-slide|--duration-enter|--gold:"
  rg -n "useReducedMotion|AnimatePresence"

Expected (live 2026-09-09 evening, chunk 1xr62vxitay1m.js + module 12573):
  ProductGallery:
    colorId state default null; index state 0
    shots = imagesForColor(product, colorId)
    src = shots[i]?.src ?? coverSrc(product)   // DELETE this cover fallback
    AnimatePresence mode="wait"  initial x:24 / exit x:-18 / 0.28s
      ease [.22,1,.36,1]
    img onClick cycles index if shots.length > 1
    ColorSwatch hex discs when product.colors.length > 0
  imagesForColor(product, colorId):
    all trimmed srcs if colorId === null
    else filter image.colorId === colorId   // TOO STRICT (drops shared)
  coverSrc = first image with src.trim()
  coverSrcForColor = first imagesForColor or coverSrc
  ColorSwatch: h-6 w-6 rounded-sm, backgroundColor hex, aria-label Color {hex}
  Hero /m/A01: NO view-transition-name on this mã (related rail names product-A02)
  Photos that 200: /products/{MA}/cover.jpg only. 001.jpg 404 — do not invent.

:root --paper --ink --gold --gold-deep --blush --duration-enter:.21s
      --duration-exit:.15s --duration-move:.4s
  springSoft = { type: "spring", stiffness: 420, damping: 32, mass: 0.72 }

If a file is missing, create the smallest new file next to ProductGallery —
do not invent a second design system.

────────────────────────────────────────
FIX 1 — Customer colors are TEXT + this mã’s ids only
────────────────────────────────────────
STOP rendering ColorSwatch hex discs on PDP and on home ProductGrid.
Keep ColorSwatch for /admin if that screen already uses boxes.

WHEN product.colors.length > 0 AND ids are stored on THAT row:
  Text pills (lookbook chrome):
    rounded-full px-3 min-h-10 text-[11px] uppercase tracking-[0.14em]
    selected: text-ink + absolute inset-x-0 bottom-0 h-px bg-gold
              layoutId={!reduced && "pdp-color"} transition={springSoft}
    idle: text-muted hover:text-ink
    aria-pressed + visible name
  Recorded ids you may show IF present (do not add missing ones):
    A01 kem,xanh · S01 kem · P01 hoa · P02 do · P03 den,do · P04 kem
    P05 hong,do,xanh · A02 cham-bi · K01 none · H01 none
  Echo: Đang xem: {name}
  hoa / cham-bi stay words. No invented hex. No A01 discs on A02.
  LIVE BUG: A02 HTML currently shows the SAME two hexes as A01
  (#F4F0E8 #1C2A4A). P01–P05 show a shared four-hex strip. Remove any
  chip whose id is not on that mã. Do not invent Vietnamese labels to
  justify leaked hex.

WHEN colors[] is empty (live S01 K01 H01): NO chip row. Pass.

────────────────────────────────────────
FIX 2 — imagesForColor is the gallery link (honest empty)
────────────────────────────────────────
Replace imagesForColor with:

  function imagesForColor(product, colorId) {
    const n = product.images.filter((img) => img.src?.trim());
    if (colorId == null) return n;
    return n.filter((img) => img.colorId === colorId || img.colorId == null);
  }

coverSrcForColor: first of that list, or undefined (NOT coverSrc).
ProductGallery src: shots[i]?.src only.
If shots.length === 0: blush box + existing
  “Message {MA} for real photos” line.
NEVER ?? coverSrc to make a hex “work”.
NEVER fetch /products/A02/ from /m/A01.
NEVER invent /products/A01/001.jpg (404 today).
Only files that 200 on this host.

On color activate: reset index 0; scroll slide 0 to center
(behavior instant if useReducedMotion()). Do not change mã, $, Hold, route.

────────────────────────────────────────
FIX 3 — Watery roll: native scroll-snap + mask (+ optional frost)
────────────────────────────────────────
Replace click-cycle + AnimatePresence x-slide as the shot-to-shot mechanic.

IF shots.length === 1:
  Full-bleed aspect-[3/4] object-cover in bg-[#f3f1ee].
  No mask, no frost, no dots, no peek gutter.
  view-transition-name: product-{THIS mã} on this shell.

IF shots.length >= 2:
  Port (reuse tab-scroll to hide scrollbar):
    display: grid; grid-auto-flow: column; grid-auto-columns: 78%;
    gap: 12px; overflow-x: auto; overscroll-behavior-x: contain;
    scroll-snap-type: x mandatory;
    scroll-padding-inline: 11%; padding-inline: 11%;
  Slides: scroll-snap-align: center; scroll-snap-stop: always;
  Mask on the PORT (not on img):
    mask-image / -webkit-mask-image:
      linear-gradient(to right, transparent 0, #000 28px, #000 calc(100% - 28px), transparent 100%)
  OPTIONAL frost: sibling strips .ky-frost-start / .ky-frost-end
    pointer-events: none; width ~28px;
    background: color-mix(in oklab, var(--paper) 55%, transparent);
    backdrop-filter: blur(10px) saturate(120%);
    -webkit-backdrop-filter: same;
    NOT inside a transformed motion.div; NOT on <img>; NOT on .shimmer.
  Dots: aria-current on snapped slide; gold/paper, not 6px-only affordance.
  Prev/next buttons 44×44 (aria-label Ảnh trước / Ảnh sau).
  img click opens lightbox (LEARN 10) — do not modulo-advance.
  Do NOT Motion drag the port. Native scroll only.
  useScroll(container) may drive dot/hairline chrome only.

Color change (new shot list):
  AnimatePresence OK for the SET, but opacity 150–250ms ONLY
  (ease [.22,1,.36,1]). No x:24. No mode="wait" blank. Reduced = duration 0.

Do NOT:
  filter:url(#goo) on img, .shimmer, hero, Message CTA
  feDisplacementMap on covers
  fake second slide by duplicating cover
  wrap gallery to related-rail mãs
  autoplay
  Swiper/Embla/Keen
  --duration-move:.4s as the gallery clock

────────────────────────────────────────
FIX 4 — Lightbox + VT name (do not regress LEARN 10)
────────────────────────────────────────
Hero shell: view-transition-name: product-{THIS mã}
  /m/A01 → product-A01. Never product-A02 on A01’s hero.
Related rail keeps product-{neighbor}.

Lightbox (if not already shipped):
  portal, role="dialog" aria-modal="true"
  veil bg-ink/70 (NOT rose)
  Esc + backdrop + 44×44 Đóng
  set = current mã + current color filter only
  src list = shots that 200
  setTimeout(0) close so Message CTA is not clicked
  reduced: no scale pop

Sticky Message {MA} class cta-shine, Page id 61594312648057, after close.

────────────────────────────────────────
FIX 5 — CSS reduce
────────────────────────────────────────
KEEP existing reduce kills for announce-fade / shimmer / cta-shine / VT.

ADD:
  @media (prefers-reduced-motion: reduce) {
    .ky-gallery-port { scroll-behavior: auto !important; }
    .ky-frost-start, .ky-frost-end {
      backdrop-filter: none !important;
      -webkit-backdrop-filter: none !important;
    }
    .ky-gallery-port {
      -webkit-mask-image: none;
      mask-image: none;
    }
  }

Optional ::scroll-marker only behind @supports, WITH named buttons
as the real control (Safari has no scroll-marker yet).

────────────────────────────────────────
HARD STOPS
────────────────────────────────────────
- No new mã. No Q01 / A03 / AO001 on the lookbook.
- No cart, Shop now, flying-to-cart.
- No warehouse ticker, no fake countdown.
- Do not rewrite P02/P05 to a dollar. No e.tbcdn, no ¥, no customer names.
- Do not restyle fonts or gold “to look cleaner.”
- Do not paste Apple / Kelly Ying / Taobao sentences onto tiles.
- Do not touch https://sassy-closet.vercel.app (intake).
- Do not edit excel-kit or Official xlsx.
- Do not Production-promote without Boss. Open a Preview.

────────────────────────────────────────
VERIFY (you click these; do not skip)
────────────────────────────────────────
Desktop + phone + OS Reduce Motion + keyboard:

1. /m/A01 cover VISIBLE. Chips are words (Kem/Xanh) or none —
   never unlabeled hex discs. Message A01 →
   facebook.com/profile.php?id=61594312648057
   Hero view-transition-name is product-A01.
2. If only cover.jpg 200s: no peek gutter, no fake second slide.
   If ≥2 files 200: swipe snaps; neighbor peeks through paper fog;
   center photo is sharp (no backdrop-filter on img).
3. Color tap filters THIS mã via colorId OR shared. A02 cover never
   appears. Reduce Motion instant. Đang xem: {name}.
4. /m/A02 does NOT show A01’s two hexes. Cham-bi text or empty.
5. /m/P02 and /m/P05: Hold · Inbox for price. No leaked 4-disc
   palette unless those ids are stored on that row.
6. /m/S01 /m/K01 /m/H01: no invented chips. /c/quan empty. /m/A03 404.
7. Lightbox if shipped: Esc / ✕ / backdrop; Message still works.
8. / Featured All 10; Tops A01+A02; Accessories keeps Hold P02/P05.
9. View-source / network: no e.tbcdn, no ¥, no A03, no V984.
10. Photos never go through backdrop-filter or #goo.

Commit on an Origin cursor/* branch. Preview URL in the PR. Do not merge.

===== END ORIGIN PASTE =====
```

Mini Boss: copy the block above as the **entire** Origin prompt. Do not add “also make it more premium” or “add liquid glass.” The snap + paper-edge peek + `colorId` filter *are* the watery roll. `10`’s lightbox / VT names and `13`’s Featured meniscus still apply if they are not on `main` yet — do not regress them.

End of 16.
