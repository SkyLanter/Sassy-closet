# 17 — Accessibility + reduced-motion for watery / frosted carousels

**Learn track:** Ultra burn (research + live as-built + Origin APPLY). Fast OFF — this is not a restyle memo.  
**Shop:** Sassy Closet — Facebook inbox is the store; Square Free is on-hand truth; sell-test lookbook is Origin-owned.  
**Live APPLY target:** [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)  
**Audience:** Mini Boss / Origin shop implementer / whoever ships watery or frosted **gallery** motion without making people sick or flattening the boutique.  
**Date researched / crawled:** 2026-09-09 (evening pass; CSS `34vl_zddoo4ws.css`, motion `3_93acjqq2t4q.js`, gallery `1xr62vxitay1m.js`).  
**This file does not assign stock, mint a mã, Save in Square, post to Facebook, restyle the boutique, write Excel, or touch intake Production.**

Sister `10` is **general** motion law. Sister `13` is watery **tab + grid pour**. This note is the **a11y lock** on watery / frosted **carousels** (PDP `ProductGallery`, future lightbox set, any auto-rotator) so Origin can keep the premium paper/ink/gold feel when `prefers-reduced-motion: reduce`. Mini Boss pastes **§18** into the Origin agent. Do not paraphrase §18 into “add iOS liquid glass” or “turn motion off everywhere.”

---

## 0. How to read this document

This is a **learn-track** note, not a rebuild brief and not permission to fork Origin shop code from this kit repo.

- **Cite, don’t invent.** Shop-law claims point at a file, Slack permalink, sister learn-track, or the live host. Industry claims point at WAI-ARIA APG Carousel, WCAG 2.2 (2.2.2 / 2.3.1 / 2.3.3 / 1.4.1 / 2.1.1 / 2.4.7 / 2.5.8), W3C C39 / SCR40, MDN `prefers-reduced-motion`, Apple HIG Motion, NN/G animation-purpose. If a fact is missing, the gap is named.
- **Never invent a mã.** Customer-facing codes this pass may name are the **first-ten allowlist** only. Admin “Next mã A03” is a prediction. Slack `AO001` / `AO003` are **decision-template examples** (`#shop-decisions`, 2026-09-04), not live lookbook stock. Kelly Ying `V984.` / `V826.` are **their** SKUs — do not copy them onto Sassy tiles.
- **Two alphabets.** Sell-site / hub = `A01`. Official / Square / SoT = `AO001`. Motion never translates one into the other (`01` §9; `excel-kit/schema.py` `MA_RE`).
- **Facebook inbox is the store.** A “buy” is **Message {code}**. There is no cart. A carousel that auto-plays “Shop now” or pours into a bag is a lie.
- **No redesign mandate.** Improve **inside** paper / ink / gold / blush, Cormorant Garamond + Be Vietnam Pro, `ma-mark`, `announce-fade`, `shimmer` / `shimmer-slide`, `cta-shine` / `cta-flash`, gold `h-px`, `layoutId: "featured-tab"`, `filterSlide`, `springSoft`, `ProductGallery`. Do not replace that language with iOS liquid glass over photography, Shopify Horizon, intake Allura/Nunito rose, or a gray “a11y theme.”

**Reduced-motion here does not mean ugly.** Same Kelly Ying type, same gold hairline, same Message CTA. Spatial travel (translate, scale, infinite slide, goo, parallax) becomes **opacity or instant**. State (selected color, Hold word, price or Inbox for price, dialog open) stays.

### 0.1 Research method (and what this pass could not see)

| Source | Result |
| --- | --- |
| Live sell-test HTML + CSS + JS of `/`, `/m/A01`, `/m/P02` (2026-09-09 evening) | Primary **as-built** gallery map. CSS `/_next/static/immutable/chunks/34vl_zddoo4ws.css`. Motion `/_next/static/immutable/chunks/3_93acjqq2t4q.js`. Gallery `/_next/static/immutable/chunks/1xr62vxitay1m.js` (exports `ProductGallery`, `ColorSwatch`). |
| RSC payload on those pages | `colors[]` is **no longer empty** on A01 / P04 / P05 (hex + empty `note`, random `id` hashes). `images[].colorId` is still `null`. |
| Repo `excel-kit/`, `sassy-closet/`, `README.md` | Shop law. Intake `PhotoLightbox.tsx` is **behavior** only — do not import rose. |
| Sister LEARN TRACK PRs #19–#33 (`01`–`14`) | Headings + locks. This file is `17`. `15`/`16` were unused at branch time; in-flight sisters “iOS frosted carousel” / “Apple watery color peek” must **obey this a11y lock**, not the other way around. |
| Slack `#shop-decisions` (`C0BV3GYC602`) | Five standing messages (2026-09-04). No carousel / reduced-motion thread. |
| Linear / Notion / Granola | No shop motion issue. Granola MCP unauthorized. Notion AI search unavailable. |
| Kelly Ying Boutique public site | Prior reads in `01` / `10`. This pass did not re-scrape; look lock unchanged. |
| Public a11y / carousel specs | Fetched 2026-09-09. URLs in §18. |

If a later crawl disagrees with a **live** cell here, **the new crawl wins** — update the date line. Shop law still wins over industry taste.

### 0.2 Sister docs

| # | File | Job vs this note |
| --- | --- | --- |
| 01 | `01-messenger-social-commerce.md` | Kelly Ying look lock; Message-first; no cart |
| 02 | `02-pdp-color-size-ux.md` | Customer **text** colors; gallery sync |
| 09 | `09-bugcheck-sell-site-checklist.md` | MOT-01…MOT-08, A11Y-01…12, QC-A11Y |
| 10 | `10-customer-pleasing-motion-ux.md` | General motion + five Origin fixes; assumed `colors: []` |
| 13 | `13-watery-tab-slide-motion.md` | Watery **tab + grid pour**; not PDP gallery |
| **17** | **This file** | **A11y + reduced-motion for watery/frosted carousels; Origin APPLY** |
| Kit | `SELL_CATALOG_CONTRACT.md` (PR #18) | Allowlist + prices + Hold null `$` |

`10` said live customer `colors: []`. **This crawl is later the same day:** A01, P04, and P05 now emit hex `ColorSwatch` rows. Treat `10` §8.1 as **stale on those three SKUs**. The noun law in `02` (text names, not hue-only) still wins.

---

## 1. Executive summary

A boutique gallery is allowed to feel **wet**. It is not allowed to **lie**, **strobe**, **auto-advance unpaid**, or **frost the garment**. Reduced-motion users still get the Closet — paper, gold hairline, Hold words, Message {mã} — not a stripped wireframe.

Live 2026-09-09 evening, the watery carousel **already exists**. It is not a named `<Carousel>`. It is **`ProductGallery`** on `/m/{MA}`:

| Hook | Live fact |
| --- | --- |
| Export `ProductGallery` | RSC module on PDP (`$L14` on `/m/A01`) |
| `useReducedMotion()` | Gates gallery **x-slide** duration (`duration: .28 * !reduced`) |
| Slide | `AnimatePresence mode="wait"`; enter `x:24` / opacity 0→1; exit `x:-18` / opacity 0; ease `[.22,1,.36,1]` |
| Click-on-`<img>` | If `imagesForColor.length > 1`, cycles index `(i+1) % n` — **not** a lightbox |
| Dots | Only when `f.length > 1`: `h-1.5 w-1.5` (6px) `aria-label="Image {n}"` |
| `ColorSwatch` | Customer hex buttons `h-6 w-6`, `aria-label="Color #HEX"`, `aria-pressed` |
| A01 `colors[]` | `{id:"cb3d45c1231ab", hex:"#F4F0E8", note:""}`, `{id:"c4b0be6de43a3", hex:"#1C2A4A", note:""}` |
| P04 `colors[]` | one `{hex:"#F4F0E8", note:""}` |
| P05 `colors[]` | three hexes `#E8D5C4` / `#8B3A3A` / `#1C2A4A`, `note:""` — **Hold**, no `$` |
| `images[]` | still one `/products/{MA}/cover.jpg` with `colorId: null` on every allowlist SKU this crawl |
| Frost | Phone sticky Message dock: `bg-paper/95 backdrop-blur-md` — **chrome**, not the JPEG |
| APG carousel | **Absent** (`aria-roledescription` count 0 in gallery + motion chunks) |
| Lightbox | **Absent** on crawled PDPs (intake `PhotoLightbox` is the behavior donor only) |

That gallery is already a **carousel-shaped widget** (sequential slides + optional dots + color as a second axis). It fails boutique a11y in five specific ways — not because motion exists, but because motion is doing the wrong job:

1. **Hue-only chips** (WCAG [1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)). `aria-label="Color #F4F0E8"` is a hex, not Kem / Xanh. `02` / `10` FIX 5 required **text pills**. Empty `note` is not permission to guess a Vietnamese name from the hex.
2. **Motion that lies.** Color tap remounts `motion.div` keyed `${colorId??"all"}-${src}`. `src` stays `cover.jpg`. The buyer watches a watery **x-slide of the same JPEG**. That is vestibular cost with zero information (`10` §6 identity law).
3. **Click-to-cycle on the photo** with no keyboard equivalent (WCAG [2.1.1](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html)) and no enlarge. `10` §9 wanted a lightbox; live click **steals** that gesture for wrap-around.
4. **6px dots** when a second file exists (WCAG [2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) 24×24). Paper-on-photo contrast is luck, not a spec.
5. **Hover 1.08 / card lift** still run under Reduce Motion (`10` MOT-03; `09` MOT-03). Gallery slide **does** honor `useReducedMotion`. The premium feel gap is the **ungated CSS**, not Framer.

Reduced-motion **must not kill** the look: keep Cormorant / Be Vietnam, `--gold` hairline, Available/Hold **words**, `$25` / Inbox for price, Message A01, paper dock. Kill translate/scale/infinite loops. Apple: **fade, don’t zoom** ([HIG Motion](https://developer.apple.com/design/human-interface-guidelines/motion)). W3C C39: prefer enabling motion only under `prefers-reduced-motion: no-preference` so a forgotten class cannot loop ([C39](https://www.w3.org/WAI/WCAG22/Techniques/css/C39)).

---

## 2. Hard constraints (print these on the implementer’s wall)

1. **Never invent a mã.** Emit list is exactly `A01 S01 P01 P02 P03 P04 P05 K01 H01 A02` (PR #18). Empty `/c/quan` stays empty. No `Q01` “so the carousel has a fourth slide.”
2. **Never invent qty, $, photos, hex, or color names.** Hold P02 / P05 = **Inbox for price**. Empty `note` + hash `id` ≠ Kem. Do not relabel `#F4F0E8` as Kem because `05` recorded `kem` on a hub sample.
3. **Square Free = on-hand truth.** Official Excel is a working copy (`README.md`). This kit does not edit Excel or intake in this pass.
4. **Bots draft only.** No Square Save, no Facebook Post/Send (`#shop-decisions` 2026-09-04).
5. **No cart, Shop now, or bag-fly.** Kelly Ying’s **$10 / $300+** and `V###` codes are **theirs** (`01` §0).
6. **Customer colors are text** (WCAG 1.4.1; `02` §7). Hex squares are staff chrome or they are a fail.
7. **Motion never changes identity.** Same mã in, same mã out. Color tap must not borrow `/products/A02/cover.jpg` on A01.
8. **Water / frost never lies on the photo.** No `filter: url(#goo)`, no `feDisplacementMap`, no `backdrop-blur` on the hero JPEG. Distortion is a **fabric lie** (`13` §2.8).
9. **Origin owns the pixels.** APPLY is for the Origin agent on `sassy-closet-shop`. Intake Production stays https://sassy-closet.vercel.app.

---

## 3. What “watery / frosted carousel” means here

### 3.1 Three surfaces, only one is live

| Surface | Live 2026-09-09 evening | Watery? | Frosted? | Carousel? |
| --- | --- | --- | --- | --- |
| Featured tabs + `filterSlide` | Yes (`13`) | Gold meniscus + grid pour | No | **No** — APG **tabs**, not carousel. Do not stamp `aria-roledescription="carousel"` on `FeaturedBoard`. |
| PDP `ProductGallery` | Yes | `x:24` / `x:-18` / 280ms | No on the JPEG | **Yes, de facto** — sequential slides + dots + color axis |
| Phone Message dock | Yes | No | `backdrop-blur-md` on `bg-paper/95` | No |
| Lightbox set | **No** | `10` §9 would fade | Veil `bg-ink/70` is dim, not glass-on-garment | Carousel-like when `files.length > 1` |
| Auto-rotating lookbook | **No** | — | — | **Refuse** as default (`10` §8.3; APG: reduced-motion starts paused) |

### 3.2 Fashion liquid vs OS chrome (repeat from `13`, scoped to gallery)

“Liquid glass” vendor posts mean `backdrop-filter` + displacement over **the whole chrome**. On a lookbook that **frosts the garment** and fights `--paper` / `--ink`. **Refuse** full-viewport glass, chromatic aberration on covers, cursor-follow blobs.

Legal frost on this Closet:

| Frost | Why it is legal | Fail if… |
| --- | --- | --- |
| Sticky Message dock `bg-paper/95 backdrop-blur-md` | Sits **below** the article; gold border; mã + Hold/Available **words** + `$` / Inbox still readable | Blur applied to the hero `<img>` or ColorSwatch |
| Lightbox veil `bg-ink/70` (not intake `bg-rose-950/70`) | Dims the **page**, not the pixels inside `object-contain` | Veil uses `backdrop-blur` **on** the enlarged JPEG |
| Optional gold-rule goo (`13` FIX 1) | Hairline wrapper only | Filter on `ProductGallery` / `.shimmer` / covers |

Blur itself is **not** WCAG 2.3.3 motion. Do not rip the dock frost “for a11y.” Reduced-motion users still get paper/95; they do **not** get the x-slide.

### 3.3 NN/G jobs, mapped onto gallery

| NN/G job | Gallery meaning | Fail if… |
| --- | --- | --- |
| Feedback | Color / slide change starts within **0.1s** ([NN/G](https://www.nngroup.com/articles/animation-usability/)) | Click, then 300ms of blank `wait` |
| State change | Visible **name** + `aria-pressed` + image set; motion extra | Hex circle is the only cue (1.4.1) |
| Spatial metaphor | Next photo from the right if you pressed Next — **not** a new mã | Wrap to A02; color tap slides the **same** JPEG |
| Signifier | Prev/Next are buttons ≥24px; phone does not need hover | 6px dots only; `img onclick` |
| Attention | One moving layer | Shimmer + x-slide + 1.08 zoom + goo (Hipmunk pile-on) |

### 3.4 Technique catalog (gallery only)

| Technique | Use on sell-test gallery? |
| --- | --- |
| Opacity crossfade 150–250ms (`10` §8.2) | **Preferred** image change when `src` actually changes |
| `x:24` watery slide (`ProductGallery` live) | **Only** when `src` changes **and** Reduce Motion is off. Cut to ≤200ms. Never for same-src color taps. |
| `clip-path` wipe (`13` recipe A) | Optional on Featured **grid**, not on the garment JPEG |
| Click-wrap on `<img>` | **Refuse.** Enlarge (lightbox) or do nothing. Advance via buttons. |
| Autoplay rotator | **Refuse as default.** If Boss later asks, APG pause + Reduce Motion starts paused ([APG carousel example](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/examples/carousel-1-prev-next/)). |
| `backdrop-blur` on hero | **Refuse.** |
| SVG goo / displacement | **Refuse** on gallery. Optional on Featured gold rule only (`13`). |

---

## 4. As-built hook map (cite the live host)

Crawl: 2026-09-09 evening. Host `x-nextjs-stale-time: 300`. Fonts on `<html>`: `be_vietnam_pro_…__variable` + `cormorant_garamond_…__variable`.

### 4.1 CSS tokens (do not rename)

Same `:root` as `13` §4.1: `--paper #fff` / `--ink #111` / `--muted #6b6b6b` / `--line #ececec` / `--gold #b08968` / `--gold-deep #8c6a4e` / `--blush #f3eee8` / `--duration-exit:.15s` / `--duration-enter:.21s` / `--duration-move:.4s`.

Exact live reduce query (unchanged from `10` §4.7):

```css
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto }
  .announce-fade, .shimmer, .cta-shine:hover:after { animation: none !important }
  ::view-transition-group(*),
  ::view-transition-old(*),
  ::view-transition-new(*) { animation: none !important }
}
```

**Killed:** looping shimmer, announce fade, CTA shine, VT CSS animations.  
**Not killed:** `group-hover:-translate-y-1.5`, `group-hover:scale-[1.08]`, editorial `scale-105`, gold `scale-x-100` hairline, `ProductGallery` x-slide (that one is JS `useReducedMotion`, not this query).

`::view-transition { pointer-events: none }` stays. Header VT groups stay frozen.

### 4.2 `ProductGallery` (reconstructed from `1xr62vxitay1m.js`)

```text
ProductGallery({ product })
  reduced = useReducedMotion()
  selectedColorId = useState(null)          // u
  imageIndex     = useState(0)              // p
  set = imagesForColor(product, selectedColorId)
  cover = coverSrc(product)
  src = set[clampedIndex]?.src ?? cover

  AnimatePresence mode="wait"
    motion.div key={`${selectedColorId ?? "all"}-${src ?? "none"}`}
      initial: reduced ? false : { opacity: 0, x: 24 }
      animate: { opacity: 1, x: 0 }
      exit:    reduced ? { opacity: 0 } : { opacity: 0, x: -18 }
      transition: { duration: 0.28 * !reduced, ease: [.22, 1, .36, 1] }
      <img src=src alt=displayTitle(product)
           onClick: if set.length > 1 → index = (i+1) % n
           class: cursor-pointer if set.length > 1 >

  if set.length > 1:
    dots: button aria-label="Image {n+1}" · h-1.5 w-1.5
          selected bg-paper else bg-paper/40

  if product.colors.length > 0:
    ColorSwatch hex=color.hex selected={selectedColorId===color.id}
      onClick: toggle id (same id → null), reset index to 0
```

`ColorSwatch` sizes: `sm` = `h-4 w-4` (home cards), `md` = `h-6 w-6` (PDP), `lg` = `h-8 w-8`. Default `aria-label={`Color ${hex}`}` unless `title` passed — live PDP does **not** pass a name.

No `role="region"`, no `aria-roledescription`, no prev/next, no lightbox, no `view-transition-name: product-{THIS mã}` on the PDP hero wrapper (`/m/A01` still names **`product-A02`** on the related rail only — `10` FIX 3 still open).

### 4.3 Live `colors[]` (this crawl — do not freeze as a mã)

| Mã | `colors[]` this crawl | `images[]` | Customer UI |
| --- | --- | --- | --- |
| A01 | 2× `{id: hash, hex, note:""}` `#F4F0E8` `#1C2A4A` | cover.jpg `colorId: null` | Two hue squares under hero |
| P04 | 1× `#F4F0E8` | cover.jpg null | One hue square (home + PDP if opened) |
| P05 | 3× `#E8D5C4` `#8B3A3A` `#1C2A4A` | cover.jpg null | Three hue squares; **Hold · Inbox for price** |
| S01 P01 P02 P03 K01 H01 A02 | `[]` | cover.jpg null | No row (honest) |

Hub sample names in `05` §3.2 (`kem`, `xanh`, `hoa`, …) are **not** on these rows. APPLY must not print them until admin stores a **name** field (or non-empty `note` that is already a customer word — do not translate hex).

### 4.4 Featured path (not a carousel; still reduced-motion)

Unchanged from `13`: `FeaturedBoard` + `filterSlide(reduced, dir)` + `springSoft` `{stiffness:420,damping:32,mass:0.72}` + `layoutId: "featured-tab"`. Reduced already zeros `filterSlide` x. APG `tabpanel` / `aria-controls` still missing. Do **not** watery-carousel this into `aria-roledescription="carousel"`.

### 4.5 Intake behavior to steal (not chrome)

`sassy-closet/components/PhotoLightbox.tsx`: portal, `role="dialog"` `aria-modal="true"`, Esc, focus close, restore focus, body scroll lock, deferred close. Veil is **rose** — lookbook must use ink/paper (`10` §9.3).

---

## 5. Kelly Ying look — steal the rhythm, refuse the glass

Unchanged lock (`01` §1.3, `10` §5, `13` §5):

- Cormorant Garamond display + Be Vietnam Pro UI.
- Paper / ink / gold / blush; `ma-mark`; 11px uppercase tracking.
- Gold **hairline**, not a fat iOS pill.
- SKU-on-card job = **A01**, not `V984`.
- Livestream rail idea; do not invent Chủ Nhật / Thứ 2.
- **Refuse** cart, Checkout, **$10 / $300+**.

Reduced-motion **must still look like that page**. The anti-pattern is a “safe mode” that swaps Cormorant for system UI, kills gold, or hides Message “until motion is back.”

---

## 6. Reliability law (water must not lie)

Write these as code-review questions (`10` §6 + gallery):

1. **Identity.** After the animation, the visible mã is the mã on the URL. Color tap never finishes on another folder.
2. **Status.** Hold vs Available is readable **mid-slide**. P05 chips must not flash Available or a `$`.
3. **Price.** P02 / P05 never display `$` during a crossfade.
4. **Catalog bounds.** Gallery set = this mã’s files. Dots do not wrap to A02.
5. **Color honesty.** Pixels after a color tap are tagged `colorId` for **that** id, or shared `colorId == null`. If the set is unchanged, **do not animate**.
6. **CTA.** Sticky Message / header Messenger stay clickable. VT overlay `pointer-events: none` stays. Gallery click must not swallow the dock.
7. **Interrupt.** Second color tap cancels the first tween. Esc closes lightbox on frame 1 (`10` §9).
8. **No checkout metaphor.**
9. **No dark-pattern motion.** No fake countdown inside a rotator (`09` / `07`).
10. **Same data, every surface.** Home hex row = PDP hex row = admin. Do not show chips on home and hide them on PDP (or the reverse) for the same payload.

---

## 7. WCAG clocks (do not collapse them)

| Criterion | Level | Gallery impact |
| --- | --- | --- |
| [2.2.2 Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) | **A** | Infinite `.shimmer` is the live loop (`13` §11). A future autoplay carousel **must** have pause/stop/hide. Click-manual advance is not 2.2.2. Prefer wrapping shimmer in `no-preference` (`10` FIX 1). |
| [2.3.1 Three flashes](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html) | **A** | Do not strobe gold dots or rapid wrap on click. |
| [2.3.3 Animation from interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) | **AAA** | Color tap x-slide, hover 1.08, Featured pour = interaction animation. Sufficient: [C39](https://www.w3.org/WAI/WCAG22/Techniques/css/C39) + [SCR40](https://www.w3.org/WAI/WCAG22/Techniques/client-side-script/SCR40) / `useReducedMotion`. This shop still **aims** at it (`09` MOT-02). |
| [1.4.1 Use of color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) | **A** | Hex-only `ColorSwatch` **fails** today on A01/P04/P05. |
| [2.1.1 Keyboard](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html) | **A** | `img onClick` cycle is mouse-only. |
| [2.4.7 Focus visible](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html) | **AA** | Dots / swatches need a gold or ink ring, not `outline-none` with no replacement. `ColorSwatch` already outlines selected with `outline-ink` — keep that, add focus-visible. |
| [2.5.8 Target size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) | **AA** | `h-1.5` dots fail; `h-4` home swatches fail; `h-6` PDP swatches are 24px **if** the hit box is the button (border-box). Prefer `min-h-11` text pills (`10` FIX 5). |
| [4.1.2 Name, Role, Value](https://www.w3.org/WAI/WCAG22/Understanding/name-role-value.html) | **A** | If you call it a carousel, APG names it. Featured stays **tabs**. |

Shop bar: **A + AA** on the lookbook (`09` §12). 2.3.3 is AAA; still honor OS Reduce Motion because vestibular cost is real ([Understanding 2.3.3](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html)).

---

## 8. APG carousel (when `files.length > 1`)

WAI-ARIA APG [Carousel](https://www.w3.org/WAI/ARIA/apg/patterns/carousel/):

- Container: landmark / `role="region"` + `aria-roledescription="carousel"` + accessible name (`A01 photos` / `Ảnh A01`). Localize the roledescription if the page is Vietnamese; live `<html lang="en">` — keep English roledescription **or** set `lang` honestly. Do not invent a bilingual rotator.
- Each slide: `role="group"` + `aria-roledescription="slide"` + `aria-label="1 of N"`. Off-screen slides `aria-hidden="true"` (not `display:none` if you need width for FLIP — `visibility` / `aria-hidden` is enough).
- Prev / Next: real `<button>`s, first in reading order after optional pause. Labels “Previous photo” / “Next photo” (or VN if the page language is VN).
- **No auto-rotate on load.** APG example: if OS reduced-motion, auto-rotation **starts paused**; this shop goes further — **do not ship auto-rotate** unless Boss asks.
- If auto-rotate ever ships: pause control is first; label toggles “Stop slide rotation” / “Start slide rotation” (not `aria-pressed` with a static name); stop on focus and hover; do not restart until explicit.
- Live region `aria-live="polite"` announces **manual** changes only. Silent during any auto-rotate.
- Keyboard: Left/Right when focus is inside the carousel; do not steal page Up/Down.
- Do not move focus to the new slide unless the user activated Next/Prev (not on auto-advance).

**FeaturedBoard is not this pattern.** Tabs: [APG Tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/) (`13` FIX 2).

**Single-image PDP** (today: every allowlist cover is one file): do **not** add carousel roles. A region with one slide and dots is noise. Enlarge via lightbox (`10` FIX 3). Color row, if named, is a **toolbar / radiogroup of text pills**, not a carousel.

---

## 9. Reduced-motion without killing premium

### 9.1 What “fallback” means (`10` §10.1, gallery-specific)

Not a second theme. Same type and gold. **Spatial** motion becomes **opacity or instant**.

| Effect | Motion on (premium) | Reduce Motion (still premium) |
| --- | --- | --- |
| Color / photo change when `src` **changes** | 150–250ms opacity **or** ≤200ms watery x (not both) | Instant `src` swap; no `x` |
| Color tap when `src` **unchanged** | **No animation** (law §6) | Same |
| Lightbox veil | 150–200ms opacity | Instant |
| Hero 1.08 / card lift | `motion-safe:` only | None — photo still sharp, gold hairline still there |
| Infinite shimmer | `no-preference` only | Static gradient (paint stays) |
| Gold Featured meniscus (`13`) | stretch / optional goo | Instant `h-px` under selected tab |
| Sticky dock frost | `backdrop-blur-md` OK | Keep paper/95; blur may stay (not 2.3.3) |
| `announce-fade` | 4.2s | `animation: none` — **bar stays visible** |
| View Transitions | morph when names match | `animation: none`; **keep names** for identity |

### 9.2 Inverse C39 (preferred)

```css
@media (prefers-reduced-motion: no-preference) {
  .shimmer { animation: 1.3s ease-in-out infinite shimmer-slide; }
  /* watery gallery slide classes live here too, if CSS-driven */
}
```

JS already:

```js
const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
// ProductGallery: duration: 0.28 * !reduced  — keep
// startViewTransition: skip when reduced     — 10 FIX 4
```

### 9.3 Do not hide content in the fallback

- Hold badge, Inbox for price, Message CTA, mã — visible with animations disabled.
- `opacity-0` hydration on related-rail covers (`10` FIX 2) must resolve without hover.
- Do not `display:none` the livestream bar when reduce is on.
- Do not remove gold hairline because “motion is off.” Instant gold is still the selected signifier.

### 9.4 Manual site toggle

`09` / `10` §10.4: a 10-SKU soft-launch does **not** need a settings cog if OS Reduce Motion is honored **including hover scale and gallery x**. Do not invent a customer account to store the pref.

---

## 10. Vestibular / performance

MDN: `prefers-reduced-motion: reduce` means remove, reduce, or replace; **scaling and panning large objects** are vestibular triggers ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)). A full-bleed `x:24` on a 3/4 hero is exactly that class.

Apple Reduced Motion criteria: fade instead of zoom; do not make people wait for frequent motion ([App Store Connect](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria/)). Color tapping is frequent. 280ms + `mode="wait"` is already a **blank** if exit and enter serialize (`13` Featured math). Gallery should **overlap opacity** or cut to ≤200ms; reduced = 0.

Do not add parallax on CollectionList (`13` already refused `animation-timeline: view()` for this APPLY). `whileInView` + `staggerContainer` already zeros duration when reduced — keep that.

Performance: animate `opacity` / `transform` only. No `filter` on the JPEG. `::view-transition { pointer-events: none }` stays. Do not run shimmer **and** gallery x **and** 1.08 together.

---

## 11. APPLY — [sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)

**Owner:** Origin `sassy-closet-shop` (not this kit).  
**Look:** Kelly Ying paper / ink / gold. **Job:** make `ProductGallery` (and any later lightbox set) accessible and reduce-safe **without** flattening the boutique.  
**Mã:** allowlist only. **No** Square Save. **No** FB Send. **No** cart. **No Excel.**  
**Do not edit** `excel-kit/` or intake `sassy-closet/` Production.

Human-readable ticks. **Paste block is §18.**

### 11.0 Do not touch (lock — tick first)

- [ ] Cormorant Garamond + Be Vietnam Pro.
- [ ] Paper / ink / gold / blush; `ma-mark`; 11px tracking; gold **`h-px`**.
- [ ] Keyframes `announce-fade`, `shimmer-slide`, `cta-flash` and classes `announce-fade`, `shimmer`, `cta-shine` **remain**.
- [ ] Exports `ProductGallery`, `ColorSwatch`, `FeaturedBoard`, `filterSlide`, `springSoft`, `featured-tab` **remain** (you may change **bodies**).
- [ ] Featured chips All / Tops / Sets / Accessories / Jackets / Hair + counts that sum to **10**.
- [ ] Livestream rail + Page `61594312648057`.
- [ ] Message-first CTAs; footer **Zelle** word; no personal name.
- [ ] Hold on **P02, P05** (no published `$`).
- [ ] `/admin` out of the main nav.
- [ ] Intake host unchanged.
- [ ] Phone dock may keep `bg-paper/95 backdrop-blur-md` — do not “fix a11y” by deleting it.

### 11.1 FIX A — Hue-only chips (1.4.1)

`rg -n "ColorSwatch|aria-label={\`Color|imagesForColor"`

- [ ] Customer-facing chips **require a name**. If `note` (or a future `name` / `id` that is a known word like `kem`) is empty, **do not render `ColorSwatch`** on home or PDP. Staff hex belongs in `/admin`.
- [ ] Do **not** invent Kem / Xanh / Hồng from `#F4F0E8` / `#1C2A4A` / `#8B3A3A` / `#E8D5C4`.
- [ ] When a name exists: **text pills** per `10` FIX 5 (`aria-pressed` + visible word + gold `h-px`). Hex may be a **left swatch beside the word**, never the only cue.
- [ ] P05 remains Hold · Inbox for price while chips exist.
- [ ] Home `h-4 w-4` hex under A01 / P04 / P05 cards: same rule — hide or name; do not leave 16px hue-only.

### 11.2 FIX B — Stop lying watery slides

`rg -n "ProductGallery|imagesForColor|x:24|duration:.28"`

- [ ] If `imagesForColor(product, nextId)` yields the **same `src`** as now, setState **without** `AnimatePresence` remount (keep the key stable; no `x:24`).
- [ ] If `src` changes: **pick one** — opacity 150–250ms **or** watery `x` ≤200ms overlapping (not `wait` blank). Ease `[.22,1,.36,1]` may stay.
- [ ] Reduced: `x: 0`, duration `0`, instant src. Keep `useReducedMotion`.
- [ ] Never bind A02’s cover on A01.

### 11.3 FIX C — Carousel APG only when there are real files

- [ ] `images` that **200** on this host. Live proven: `/products/{MA}/cover.jpg`. Do not invent `001.jpg` because OneDrive listed it (`09` 404).
- [ ] `files.length === 1`: no dots, no `aria-roledescription`, no click-cycle. Hero is a **button** “Xem ảnh lớn · View larger” → lightbox (`10` FIX 3).
- [ ] `files.length > 1`: region + carousel + slide roles; Prev/Next ≥24px (prefer 44px); dots optional **in addition** at ≥24px hit; `img` is not the Next control.
- [ ] Off-screen slides `aria-hidden`. No wrap to another mã.
- [ ] No autoplay.

### 11.4 FIX D — Reduced CSS (premium stays)

Same as `10` FIX 1 patches A–B: shimmer / announce / cta behind `no-preference`; `motion-safe:` on `translate-y-1.5` + `scale-[1.08]` + editorial `scale-105`. Keep reduce query kills. Keep `::view-transition { pointer-events: none }`.

### 11.5 FIX E — Frost stays on chrome

- [ ] Do not add `backdrop-blur` / liquid glass to `ProductGallery`, covers, `.shimmer`, Featured grid, or ColorSwatch.
- [ ] Dock frost may stay. Lightbox veil = `bg-ink/70`, image `object-contain` unfrosted.
- [ ] Optional `13` gold goo never touches this gallery.

### 11.6 Reliability / commerce

- [ ] Mid-slide, Hold is still Hold; P02/P05 have no `$`.
- [ ] Message {MA} works during and after.
- [ ] No cart, bag-fly, Shop now.
- [ ] No Kelly Ying `$10 / $300+` or `V###`.

### 11.7 Verify (Origin, after APPLY)

Desktop (hover) + phone (no hover) + OS Reduce Motion + keyboard:

1. `/m/A01` — if names still empty: **no hex row**. Cover visible. Message A01 works. Reduce Motion: no x-slide, no 1.08 on related A02.
2. `/m/P05` — Hold · Inbox for price; no `$`; no hue-only row (or named pills if admin stored words).
3. `/m/P02` — no `$`. No invented chips.
4. `/` Featured All→Tops→Accessories→All. Counts 10 / 2 / 5 / 10. P02 Hold. (`13` watery tab may still be open — do not regress.)
5. Keyboard: Tab to Message; no dead `img onclick` trap. If multi-file gallery ships, arrows move slides.
6. View-source: no `e.tb.cn`, no ¥, no `A03`, no `V984`, no `aria-roledescription="carousel"` on Featured tabs.
7. Reduce Motion: livestream **text** still there; gold hairline still there; dock still paper; photos unfrosted.

---

## 12. Anti-patterns (quick refuse list)

1. Minting `A03` / `Q01` so a carousel “has four slides.”  
2. Guessing Kem from `#F4F0E8`.  
3. `aria-roledescription="carousel"` on `FeaturedBoard`.  
4. Autoplay lookbook / color rotator.  
5. `backdrop-blur` or goo on the hero JPEG.  
6. iOS liquid-glass capsule under Featured or gallery.  
7. Click-wrap on `<img>` instead of lightbox.  
8. 6px dots as the only Next control.  
9. Keeping same-src color taps as `x:24` remounts.  
10. Grayscale / Inter / “a11y theme” under Reduce Motion.  
11. Hiding Hold, price, or Message in the fallback.  
12. Importing intake rose lightbox.  
13. Cart-bag pour.  
14. Copying Kelly Ying `V984` or `$10 / $300+`.  
15. Translating `A01` → `AO001` in an `aria-label`.  
16. Fighting `13` by deleting `filterSlide` / `featured-tab`.  
17. Excel / intake writes from this pass.

---

## 13. Acceptance (sell-test a11y watery)

A reviewer can fail the page against this list without a redesign argument:

- [ ] Every mã that moves is on the allowlist and was **already assigned**.  
- [ ] P02 / P05 never display a dollar, including mid-slide.  
- [ ] Customer color controls are **named** or **absent** — never hue-only.  
- [ ] Same-src color taps do not watery-slide.  
- [ ] No autoplay carousel. No carousel role on Featured tabs.  
- [ ] Reduce Motion: no x-slide, no 1.08 zoom, no shimmer loop, no goo on photos; gold + Message + Hold still present.  
- [ ] Frost, if any, is dock/veil chrome — not the garment.  
- [ ] Keyboard can reach Message and any real Prev/Next.  
- [ ] Fonts, gold, chips, no-cart CTA still match `01` / `07` / `10` / `13` locks.

---

## 14. Timing budget

| Interaction | Budget | Live evening 2026-09-09 | APPLY |
| --- | --- | --- | --- |
| Color tap, same src | 0ms | ~280ms x-slide of same JPEG | **0ms** |
| Color / photo, src changes | 150–250ms opacity or ≤200ms x | 280ms + `wait` | Cut; pick one motion |
| Lightbox veil | 150–200ms | n/a | Instant if reduced |
| Featured pour | ≤200ms (`10`/`13`) | ~540ms wait | `13` FIX 3 |
| Gold meniscus | ≤300ms settle | `springSoft` | `13` FIX 1 |
| Hover 1.08 | motion-safe only | always | `10` FIX 1 |
| Shimmer loop | no-preference only | always infinite | `10` FIX 1 |

`--duration-move:.4s` is **not** the gallery clock.

---

## 15. QA gate in this kit

Run (read-only HTTP GET against the live host or `SHOP=`):

```bash
python3 docs/ai-clothing-shop/qa/qa_a11y_watery_motion.py
python3 docs/ai-clothing-shop/qa/qa_a11y_watery_motion.py --look
python3 docs/ai-clothing-shop/qa/qa_a11y_watery_motion.py --gate
```

- **LOOK** must stay green (Kelly Ying chrome, allowlist, Hold, no cart, no invented mã).  
- **GATE** is expected **red** until Origin lands §11 / §18 (hue-only chips gone or named; reduce query covers hover scale; gate checks hue-only `Color #` labels and missing `motion-safe` / `tabpanel`).  
Never POST. Never mint mã.

---

## 16. Open questions (do not answer by inventing)

1. Will admin add a **name** field, reuse `note`, or map hash ids to `05` words? Until one of those is stored on the row, chips stay **off**.  
2. Is `/products/{MA}/001.jpg` going to 200, or is `cover.jpg` the only public file? Carousel roles wait on **200s**.  
3. In-flight LEARN “iOS frosted carousel” / “Apple watery color peek”: they must **not** put glass on the JPEG or autoplay. This file is the a11y lock.  
4. Featured stay-on-`/` vs push `/c/*` (`13` Q1) — irrelevant to gallery APG.  
5. After Granola access: did a meeting already ban PDP x-slides? Until then, live `ProductGallery` x is the thing to **gate**, not celebrate.

---

## 17. Sources

### 17.1 Shop law and as-built

- `README.md` — Square SoT; bots draft; Facebook inbox.  
- `excel-kit/DESIGN_NOTES.md`, `excel-kit/schema.py` — mã law.  
- Sisters `01`–`14` (PRs #19–#33) — look lock, PDP nouns, MOT/A11Y checklists, motion (`10`), watery tabs (`13`).  
- Slack `#shop-decisions` (2026-09-04):  
  - [Channel law](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788541753903809)  
  - [Track stock ON proposal](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788553328521899)  
  - [Boss yes](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788553474026779)  
  - [Square LIVE](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788556083454949)  
  - [Soft-launch prep, draft only](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788557030839509)  
- Live host 2026-09-09 evening: https://sassy-closet-shop.vercel.app — CSS `34vl_zddoo4ws.css`; JS `3_93acjqq2t4q.js`; gallery `1xr62vxitay1m.js`.  
- Intake `sassy-closet/components/PhotoLightbox.tsx` — close contract only.

### 17.2 Accessibility / reduced-motion

- WAI-ARIA APG, Carousel — <https://www.w3.org/WAI/ARIA/apg/patterns/carousel/>  
- WAI-ARIA APG, Carousel example (reduced-motion starts paused) — <https://www.w3.org/WAI/ARIA/apg/patterns/carousel/examples/carousel-1-prev-next/>  
- WAI-ARIA APG, Tabs — <https://www.w3.org/WAI/ARIA/apg/patterns/tabs/>  
- WAI-ARIA APG, Dialog (Modal) — <https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/>  
- WCAG 2.2 SC 2.2.2 Pause, Stop, Hide — <https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html>  
- WCAG 2.2 SC 2.3.1 Three Flashes — <https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html>  
- WCAG 2.2 SC 2.3.3 Animation from Interactions — <https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html>  
- WCAG technique C39 — <https://www.w3.org/WAI/WCAG22/Techniques/css/C39>  
- WCAG technique SCR40 — <https://www.w3.org/WAI/WCAG22/Techniques/client-side-script/SCR40>  
- WCAG 2.2 SC 1.4.1 Use of Color — <https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html>  
- WCAG 2.2 SC 2.1.1 Keyboard — <https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html>  
- WCAG 2.2 SC 2.4.7 Focus Visible — <https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html>  
- WCAG 2.2 SC 2.5.8 Target Size (Minimum) — <https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html>  
- MDN `prefers-reduced-motion` — <https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion>  
- Apple HIG, Motion — <https://developer.apple.com/design/human-interface-guidelines/motion>  
- Apple, Reduced Motion evaluation criteria — <https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria/>  
- Motion Spec on 2.3.3 vs 2.2.2 — <https://motionspec.dev/blog/wcag-2-3-3-animation-from-interactions>  
- Chrome, same-document VT + reduced motion — <https://developer.chrome.com/docs/web-platform/view-transitions/same-document#handling_reduced_motion_preferences>

### 17.3 Motion / UX (directional)

- Nielsen Norman Group, *The Role of Animation and Motion in UX* — <https://www.nngroup.com/articles/animation-purpose-ux/>  
- Nielsen Norman Group, *Animation for Attention and Comprehension* — <https://www.nngroup.com/articles/animation-usability/>  
- Nielsen Norman Group, *UX Guidelines for Ecommerce Product Pages* — <https://www.nngroup.com/articles/ecommerce-product-pages/>  
- Baymard, image resolution and zoom — <https://baymard.com/blog/ensure-sufficient-image-resolution-and-zoom>  

### 17.4 Weaker / vendor (directional only)

- FreeFrontend liquid-glass roundups — OS chrome, not this look.  
- “Accessible carousel” blog posts that add autoplay + pause as the default — pause is required **if** you autoplay; this shop should **not** autoplay.

---

## 18. PASTE INTO ORIGIN AGENT (do not paraphrase)

Copy everything between the markers into a Cloud Agent on the **Origin `sassy-closet-shop` repo** (the git behind https://sassy-closet-shop.vercel.app). Not this kit. Not intake `sassy-closet/`. Not `excel-kit/`. Not Official xlsx.

```text
===== BEGIN ORIGIN PASTE — a11y watery / frosted carousel (LEARN 17) =====

You are editing Origin sassy-closet-shop. Make ProductGallery (and any
lightbox set) accessible and reduce-motion safe WITHOUT flattening the
Kelly Ying look. Do not restyle. Do not invent mã. Do not add iOS
liquid glass on photos. Do not touch intake or Excel.

HOST: https://sassy-closet-shop.vercel.app
LAW: Facebook inbox is the store. No cart. No Square Save. No FB Post/Send.
ALLOWLIST ONLY: A01 S01 P01 P02 P03 P04 P05 K01 H01 A02
HOLD (no $): P02 P05
PRICES: A01 $25 · S01 $28 · P01 $5 · P03 $18 · P04 $13 · K01 $37 · H01 $8 · A02 $22
LOOK LOCK: Cormorant Garamond + Be Vietnam Pro; paper / ink / gold / blush;
ma-mark; 11px uppercase tracking; gold HAIRLINE (h-px bg-gold);
announce-fade; shimmer + shimmer-slide; cta-shine + cta-flash.
Phone Message dock MAY keep: bg-paper/95 backdrop-blur-md border-gold.
Do NOT switch to intake rose / Allura / Nunito. Do NOT add Shopify cart.
Do NOT copy Kelly Ying V984 or “$10 shipping on $300+”.
Do NOT apply SVG goo / displacement / backdrop-blur to product photos.
Do NOT ship a gray “a11y theme.” Reduce Motion still looks like this boutique:
same type, gold, Hold words, Message {MA}.

FIND FILES (rg — names may differ; match these strings, then edit those files):

  rg -n "ProductGallery|ColorSwatch|imagesForColor|coverSrcForColor"
  rg -n "x:24|duration:.28|Image \$\{"
  rg -n "announce-fade|shimmer-slide|prefers-reduced-motion|group-hover:scale-\\[1\\.08\\]"
  rg -n "Filter featured collection|featured-tab|filterSlide|useReducedMotion"
  rg -n "backdrop-blur-md"

Expected (live 2026-09-09 evening, chunk 1xr62vxitay1m.js + 34vl_zddoo4ws.css):
  ProductGallery:
    useReducedMotion()
    AnimatePresence mode="wait"
    motion.div initial={!reduced && {opacity:0,x:24}}
               animate={{opacity:1,x:0}}
               exit={reduced ? {opacity:0} : {opacity:0,x:-18}}
               transition={{duration:.28*!reduced, ease:[.22,1,.36,1]}}
    img onClick cycles index if imagesForColor.length>1
    dots h-1.5 w-1.5 aria-label="Image N" if length>1
    ColorSwatch when colors.length>0 (hex, aria-label="Color #HEX")
  A01 colors: two hex #F4F0E8 #1C2A4A, note "", random ids, images colorId null
  P04: one hex #F4F0E8
  P05: three hexes, Hold, no $
  Other seven: colors []
  CSS reduce query does NOT kill hover 1.08 / translate-y-1.5
  FeaturedBoard is TABS — never aria-roledescription="carousel"

If a file is missing, create the smallest new file next to ProductGallery —
do not invent a second design system.

────────────────────────────────────────
FIX A — Hue-only chips (WCAG 1.4.1)
────────────────────────────────────────
PROBLEM: Customer ColorSwatch is a 16–24px square whose only name is
"Color #F4F0E8". note is "". That is color-as-the-only-cue.
05's kem/xanh words are NOT on these rows — do not print them.

DO:
  1. If a color has no customer-facing NAME (empty note AND id is not
     a known stored word), do NOT render ColorSwatch on home or PDP.
     Hex can stay in /admin.
  2. When a name EXISTS on that row (admin stored it — do not invent):
     text pills as LEARN 10 FIX 5:
       rounded-full min-h-10 text-[11px] uppercase tracking-[0.14em]
       aria-pressed + visible name
       selected: text-ink + gold h-px
     Optional tiny hex swatch BESIDE the word, never instead of it.
  3. Home cards: remove h-4 w-4 hue-only rows under A01/P04/P05 until named.
  4. P05 stays Hold · Inbox for price. No $ while chips exist.

────────────────────────────────────────
FIX B — Stop same-src watery slides
────────────────────────────────────────
PROBLEM: Color tap remounts motion.div even when src stays
/products/A01/cover.jpg (colorId null). Buyer sees x:24 of the SAME JPEG.

DO:
  1. If imagesForColor(product, nextId) has the same src as current,
     update selected id WITHOUT changing the motion key / WITHOUT x.
  2. If src actually changes: ONE of
       (i) opacity 150–250ms on the <img>
       (ii) watery x ≤200ms overlapping (not mode="wait" blank)
     Not both. Keep ease [.22,1,.36,1] if you keep x.
  3. Reduced (useReducedMotion or matchMedia reduce): x:0, duration 0,
     instant src. No scale.
  4. NEVER load /products/A02/cover.jpg on /m/A01.

────────────────────────────────────────
FIX C — Gallery controls + lightbox (not img-click wrap)
────────────────────────────────────────
Live: one cover.jpg per mã (200). 001.jpg is NOT proven.

DO:
  1. files.length===1 (today): NO dots, NO carousel roles, NO onClick cycle.
     Wrap hero in <button type="button" aria-label="Xem ảnh lớn · View larger">
     opening LEARN 10 lightbox (ink veil, not rose; Esc/backdrop/✕;
     portal; focus restore; setTimeout(0) close).
     src = files that 200. Today: /products/{MA}/cover.jpg only.
  2. files.length>1 (only after extra files 200):
     role="region" aria-roledescription="carousel" aria-label="{MA} photos"
     slides: role="group" aria-roledescription="slide" aria-label="k of n"
     offscreen: aria-hidden="true"
     Prev/Next <button> min 24×24 (prefer 44×44). Dots optional extra.
     Keyboard Left/Right inside the region. Do not steal page Up/Down.
     NO autoplay. NO wrap to another mã.
  3. FeaturedBoard stays role="tablist". Do not mark it a carousel.
     (LEARN 13 still wants aria-controls + tabpanel + arrows.)

────────────────────────────────────────
FIX D — Reduce CSS without killing gold
────────────────────────────────────────
KEEP keyframes announce-fade / shimmer-slide / cta-flash.

PATCH — infinite motion only if OS wants it:

  @media (prefers-reduced-motion: no-preference) {
    .shimmer { background-size:200% 100%; animation:1.3s ease-in-out infinite shimmer-slide; }
    .announce-fade { animation:4.2s ease-in-out announce-fade; }
    .cta-shine:hover:after { animation:.7s cta-flash; }
  }

KEEP existing reduce { animation:none on those + VT groups }.

ADD motion-safe: on card
  group-hover:-translate-y-1.5  → motion-safe:group-hover:-translate-y-1.5
  group-hover:scale-[1.08]      → motion-safe:group-hover:scale-[1.08]
  editorial scale-105 / duration-700 similarly.

Do NOT remove gold hairline, Cormorant, Hold badges, or Message CTAs
when reduce is on. Do NOT grayscale the shop.

KEEP:
  ::view-transition { pointer-events: none }
  site-header VT frozen
  dock bg-paper/95 backdrop-blur-md  (chrome frost is allowed)

NEVER:
  backdrop-blur / goo / feDisplacementMap on img, .shimmer, hero
  html:after liquid glass
  autoplay carousel
  cart / bag-fly

────────────────────────────────────────
HARD STOPS
────────────────────────────────────────
- No new mã. No Q01 / A03 / AO001 on the lookbook.
- No inventing Kem/Xanh from hex.
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

1. /m/A01  No hue-only squares if still unnamed.
   Cover visible (not opacity-0). Lightbox OR static hero —
   not click-wrap. Message A01 → Page 61594312648057.
   Reduce: no x-slide, no 1.08 on related A02, gold+type stay.
2. /m/P05  Hold · Inbox for price. No $. Same chip rule.
3. /m/P02  No $. No invented chips.
4. /  All→Tops→Accessories→All = 10 / 2 / 5 / 10. P02 Hold.
   Featured is still tabs, not a carousel.
5. /c/ao = A01 $25 + A02 $22. /c/quan empty.
6. Keyboard reaches Message. If multi-file gallery exists,
   arrows move slides; dots are not the only control.
7. View-source / network: no e.tb.cn, no ¥, no A03, no V984.
   No goo filter on photos. Dock may still backdrop-blur.

Commit on an Origin cursor/* branch. Preview URL in the PR. Do not merge.

===== END ORIGIN PASTE =====
```

Mini Boss: copy the block above as the **entire** Origin prompt. Do not add “also make it more premium” or “add liquid glass.” Named chips + honest slides + reduce-safe hover **are** the premium. `10` FIX 2–3 (cover opacity / PDP `product-{MA}` / lightbox) and `13` watery tab still apply if they are not on Origin `main` yet — do not regress them.

---

## 19. Kit vs Origin (this PR)

| Lane | This PR does |
| --- | --- |
| Kit `docs/ai-clothing-shop/17-a11y-watery-motion.md` | LEARN + paste brief |
| Kit `docs/ai-clothing-shop/qa/qa_a11y_watery_motion.py` | Read-only live LOOK / GATE |
| Origin `sassy-closet-shop` | Mini Boss pastes §18 — **pixels live there** |
| `excel-kit/`, Official xlsx, intake Production | **Untouched** |

End of 17.
