# 19 — Visual FX: CSS scroll-snap, mask-image, backdrop-filter, view transitions (PDP gallery)

**Learn track:** Ultra burn (Fast **OFF**). Research + live as-built + Origin APPLY.  
**Shop:** Sassy Closet — Facebook inbox is the store; Square Free is on-hand truth; sell-test lookbook is Origin-owned.  
**Live APPLY target:** [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)  
**Audience:** Mini Boss / Origin shop implementer / whoever ships **watery rolling slides** on the fashion PDP gallery without lying about the garment.  
**Date researched / crawled:** 2026-09-09.  
**This file does not assign stock, mint a mã, Save in Square, post to Facebook, restyle the boutique, or touch Excel / intake.**

Sister `10` is the **general** motion law (purpose, reduced-motion, lightbox contract, PDP hero **names**). Sister `13` is watery **Featured tabs + grid pour**. This note is the **PDP rail**: how `/m/{MA}` photos **roll**, fade at the paper edge, frost **chrome** (not cloth), and **morph** from the home tile. Kelly Ying *look* stays locked (`01` §1.3, §11; `10` §5; `13` §5). Mini Boss pastes **§22** into the Origin agent. Do not paraphrase §22 into “add liquid glass” or “install Swiper.”

---

## 0. How to read this document

This is a **learn-track** note, not a rebuild brief and not permission to fork Origin shop code from this kit repo.

- **Cite, don’t invent.** Shop-law claims point at a file, Slack permalink, sister learn-track, or the live host. Industry claims point at NN/G, W3C WCAG 2.2, WAI-ARIA APG, MDN, CSS Scroll Snap L1, CSS Masking L1, Filter Effects / `backdrop-filter`, CSS View Transitions L1, Chrome View Transitions / CSS carousels. If a fact is missing, the gap is named.
- **Never invent a mã.** Customer-facing codes this pass may name are the **first-ten allowlist** only. Admin “Next mã A03” is a prediction. Slack `AO001` / `AO003` are **decision-template examples** (`#shop-decisions`, 2026-09-04), not live lookbook stock. Kelly Ying `V984.` / `V826.` are **their** SKUs — do not copy them onto Sassy tiles or into a fake extra slide.
- **Two alphabets.** Sell-site / hub = `A01`. Official / Square / SoT = `AO001`. A gallery path is `/products/A01/cover.jpg`, never `/products/AO001/…` (`01` §9; `excel-kit/schema.py` `MA_RE`).
- **Facebook inbox is the store.** A “buy” is **Message {code}**. There is no cart. Rolling slides that fly into a bag are a lie.
- **No redesign mandate.** Improve **inside** paper / ink / gold / blush, Cormorant Garamond + Be Vietnam Pro, `ma-mark`, `announce-fade`, `shimmer` / `shimmer-slide`, `cta-shine` / `cta-flash`, gold `h-px`, `view-transition-name: site-header` / `product-{MA}`. Do not replace that language with iOS liquid glass over photography, Shopify Horizon, Swiper/Slick, intake Allura/Nunito rose, or a new design system.

### 0.1 Research method (and what this pass could not see)

| Source | Result |
| --- | --- |
| Live sell-test HTML + headers of `/`, `/m/A01`, `/m/P02`, `/c/ao`, `/c/quan`, `/m/A03` (2026-09-09) | Primary **as-built** PDP gallery map. A01 `x-nextjs-prerender: 1`, `x-nextjs-stale-time: 300`, `x-vercel-cache: STALE`. |
| Live CSS `/_next/static/immutable/chunks/34vl_zddoo4ws.css` | Tokens, keyframes, reduced-motion, `::view-transition-*`, Tailwind `backdrop-blur-md`. **Zero** `scroll-snap-*`. **Zero** `mask-image`. |
| Image HEAD | `/products/A01/cover.jpg` **200** (JPEG). `/products/A01/001.jpg` and `002.jpg` **404**. Same pattern assumed until a later crawl proves extra files. |
| Repo `excel-kit/` (read-only), `sassy-closet/` (read-only), `README.md` | Shop law. Intake `PhotoLightbox` / `PhotoThumbs` are **behavior** only — do not import rose. |
| Sister LEARN TRACK PRs #19–#33 (`01`–`14`) | Headings + locks. This file is `19`. Parallel FX agents (liquid chrome, springs, Apple glass, frosted carousel, a11y watery) may land `15`–`18` / `20+` — this file owns **snap + mask + backdrop + VT on the PDP rail** only. |
| Slack `#shop-decisions` (`C0BV3GYC602`) | Five standing messages (2026-09-04). No gallery-FX thread. `AO001` / `AO003` remain templates. |
| Linear | Keyword search returned onboarding `TIE-3` only. |
| Granola meetings | MCP unauthorized — no meeting notes. |
| Notion | Business-plan AI search unavailable. |
| Kelly Ying Boutique public site | Home + Dresses indexed 2026-09-09 (WebSearch). Steal **rhythm** only. Do not copy `V###` or **$10 / $300+**. |
| Public CSS / a11y / VT specs | Fetched 2026-09-09. URLs in §20. |

If a later crawl disagrees with a **live** cell here, **the new crawl wins** — update the date line. Shop law still wins over industry taste. A 200 on a new `/products/A01/001.jpg` is permission to add a snap child. A 404 is not.

### 0.2 Sister docs

| # | File | Job vs this note |
| --- | --- | --- |
| 01 | `01-messenger-social-commerce.md` | Kelly Ying look lock; Message-first; no cart |
| 02 | `02-pdp-color-size-ux.md` | Customer **text** colors; gallery sync nouns |
| 03 | `03-tiny-boutique-admin.md` | Admin brains; do not mint from “Next mã” |
| 04 | `04-next-blob-catalog-arch.md` | ISR / Blob; `/m/A03` must 404 |
| 05 | `05-ai-product-media.md` | Recorded first-ten colors; no invented hex *names* |
| 06 | `06-seo-trust-diaspora-boutique.md` | Soft-launch `noindex`; LCP vs extra slides |
| 07 | `07-taobao-dropship-boutique.md` | Motion lock list; dropship-honest copy |
| 08 | `08-dropship-ops-runbook.md` | Staff clock; does not restyle |
| 09 | `09-bugcheck-sell-site-checklist.md` | Tick-box QA; MOT-01…MOT-08; PDP-04 enlarge |
| 10 | `10-customer-pleasing-motion-ux.md` | General motion law; lightbox contract; **hero VT names** |
| 11 | `11-vercel-blob-admin-qa.md` | Admin / Blob gate; look stays |
| 12 | `12-fb-messenger-dropship-copy.md` | VN+EN phrase bank; no motion |
| 13 | `13-watery-tab-slide-motion.md` | Watery **tabs + grid pour** — not the PDP rail |
| 14 | `14-complete-admin-feature-matrix.md` | Admin matrix; this note does not Add items |
| **19** | **This file** | **Snap + mask + backdrop + VT on PDP rolling slides** |
| Kit | `SELL_CATALOG_CONTRACT.md` (PR #18) | Allowlist + prices + Hold null `$` |

`10` FIX 3 already asked for `product-{THIS mã}` on the hero and a lookbook lightbox. Live (this crawl) **still** has neither on the hero box. This note **does not replace** that fix. It names the four CSS primitives that make the gallery feel like **water rolling** once the name and the files exist.

---

## 1. Executive summary

A fashion PDP gallery is not a slideshow toy. It is **the garment, closer**, one honest frame at a time.

Nielsen Norman Group: animation must be **unobtrusive, brief, and subtle**. Use it for **feedback**, **state-change**, **navigation metaphors**, and **stronger signifiers** — not delight, not downtime ([NN/G, *The Role of Animation and Motion in UX*](https://www.nngroup.com/articles/animation-purpose-ux/)). Chrome’s View Transitions docs use **exactly** this shop’s metaphor: a listing thumbnail that continues into the PDP image; a fixed header that stays put ([Chrome View Transitions](https://developer.chrome.com/docs/web-platform/view-transitions/)). Baymard still wants an **enlarged view** of product photos ([Baymard, sufficient image resolution and zoom](https://baymard.com/blog/ensure-sufficient-image-resolution-and-zoom)). Live A01 copy already says “Message A01 for real photos and size” because the site has **one** public JPEG.

Sassy Closet’s sell-test already shipped a Kelly Ying *rhythm*: serif wordmark, gold hairline, blush/paper/ink, 11px tracking, livestream rail, SKU-on-card — **without** Kelly Ying’s cart (`01` §1.3). Live PDP **gallery** (2026-09-09) is still a **single cover**:

| Hook | Live fact |
| --- | --- |
| Hero | `<div class="relative overflow-hidden bg-[#f3f1ee]"><div style="opacity:1;transform:none"><img src="/products/{MA}/cover.jpg" class="aspect-[3/4] w-full object-cover"></div></div>` |
| `view-transition-name` on that box | **Absent** on `/m/A01` and `/m/P02` |
| Related-rail names | `/m/A01` → `product-A02` only. `/m/P02` → `product-P01` `P03` `P04` `P05`. **Wrong morph target.** |
| Extra files | `001.jpg` / `002.jpg` **404** |
| `scroll-snap-*` / `mask-image` | **0** in CSS chunk |
| `backdrop-filter` | Utility `.backdrop-blur-md` (`--blur-md: 12px`). **Used** on the phone sticky Message bar (`bg-paper/95 … backdrop-blur-md`). **Not** on the hero. Header frosts with `bg-paper` + inner `opacity:0.92`, **not** blur. |
| Customer color UI | `/m/A01` now paints two **hex squares** (`#F4F0E8`, `#1C2A4A`, `aria-label="Color #…"`). Shop law (`02`, `10`) still says **text** on the customer PDP. Treat the hex row as an **as-built gap**, not permission to invent Kem/Xanh chips or extra JPEGs. |
| Lightbox | No `role="dialog"` on crawled PDPs (`10` §4.5). |
| Reduce Motion | Zeros `.announce-fade`, `.shimmer`, `.cta-shine:hover:after`, `::view-transition-*` animations. Does **not** zero card `scale-[1.08]` (`10` MOT-03). |

“Watery rolling slides” for **this** closet is four primitives, all gold-on-paper:

| Primitive | Buyer should feel | Fail if… |
| --- | --- | --- |
| **Scroll-snap** | A flick **settles** on one photo, flush in the 3/4 frame | Half a sleeve; Swiper JS; a second mã in the rail |
| **mask-image** | The **paper edge** dissolves so the next photo *peeks* | The JPEG is goo’d / displaced; first/last slide looks cut-off with no neighbor |
| **backdrop-filter** | Chrome (sticky CTA, lightbox veil, optional dots) sits on **frosted paper** | The garment is frosted; blur is trapped by a mask/opacity parent |
| **View Transitions** | Home tile **is** this hero; Back is the reverse | `product-A02` morphs on A01; liquid root wipe; duplicate names on every slide |

Reliability still beats beauty. A snap rail that borrows A02’s cover, a mask that hides Hold type, a blur that lies about fabric tooth, or a VT name shared by two mãs is a **failed** boutique.

---

## 2. Hard constraints (print these on the implementer’s wall)

1. **Never invent a mã.** Emit list is exactly `A01 S01 P01 P02 P03 P04 P05 K01 H01 A02` (PR #18). Empty `/c/quan` stays empty. No `Q01` “so the rail has a fourth slide.” `/m/A03` stays 404 (`04`; this crawl).
2. **Never invent qty, $, photos, hex *names*, or files.** Hold P02 / P05 = **Inbox for price**. Snap children = URLs that **already 200**. Today that is `/products/{MA}/cover.jpg` only. Do **not** add `/products/A01/001.jpg` because OneDrive or intake once had `001.jpg` (`10` FIX 3).
3. **Square Free = on-hand truth.** Official Excel is a working copy (`README.md`). This kit does not edit Excel or intake in this pass.
4. **Bots draft only.** No Square Save, no Facebook Post/Send (`#shop-decisions` 2026-09-04).
5. **No cart, Shop now, or bag-fly.** Kelly Ying’s **$10 / $300+** and `V###` codes are **theirs** (`01` §0).
6. **Customer colors are text** (WCAG [1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)). Live hex squares on A01 are a **gap** (`02` §7). This APPLY does not “fix” them by inventing Kem/Xanh labels unless admin already stored those **words**. It also does not spawn a slide per hex when only `cover.jpg` 200s.
7. **Motion never changes identity.** Same mã in, same mã out. `product-A01` morphs only to A01. The rail never wraps to A02.
8. **Water never lies on the photo.** No `filter: url(#goo)`, no `feDisplacementMap`, no `backdrop-filter` on `<img>` or `.shimmer`. Distortion is a **fabric lie** (`13` §2.8).
9. **Origin owns the pixels.** APPLY is for the Origin agent on `sassy-closet-shop`. Intake Production stays https://sassy-closet.vercel.app. This PR does not edit `excel-kit/` or `sassy-closet/`.

---

## 3. What “watery rolling slides” means here (and what it is not)

### 3.1 Fashion liquid, not OS chrome, not Featured pour

`13` already defined watery for **tabs**: meniscus, viscosity, pour. **Do not reuse `filterSlide` / `layoutId: "featured-tab"` on the PDP hero.** Different document region, different metaphor.

PDP watery is **a photo rolling in a wet frame**:

| Metaphor | Buyer should feel | Technique |
| --- | --- | --- |
| **Settle** | Momentum dies on a whole garment, not a seam | `scroll-snap-type: x mandatory` + `scroll-snap-stop: always` |
| **Meniscus at the paper** | Next photo *bleeds* in at the edge, then the frame is opaque again | `mask-image: linear-gradient(...)` on the **scroller**, not the JPEG |
| **Frosted chrome** | Sticky Message / lightbox veil sit on paper air | `backdrop-filter: blur(var(--blur-md))` + `bg-paper/95` — **already live** on the phone bar |
| **Same piece, closer** | Home card continues | `view-transition-name: product-{THIS mã}` on the **frame** |

Apple HIG: do not make people **wait** for frequent motion; Reduce Motion replaces large spatial moves with a **crossfade or instant** ([HIG — Motion](https://developer.apple.com/design/human-interface-guidelines/motion)). Swiping photos is frequent. Watery is **short viscosity** (native snap physics), not a 700ms luxury wipe.

Refuse:

- iOS “liquid glass” over the hero ([FreeFrontend liquid-glass roundup](https://freefrontend.com/css-liquid-glass/) — OS chrome).
- Swiper / Slick / Flickity / Embla as a default (`13` already refused WebGL cloth). Native overflow + snap is the boutique.
- `13`’s gold goo on this rail.
- Auto-play, Ken Burns, parallax (WCAG 2.3.3 names large zooms / parallax).

### 3.2 NN/G jobs, mapped onto the rail

| NN/G job | Watery meaning | Fail if… |
| --- | --- | --- |
| Feedback | Snap completes; index “1 / n” (when n>1) updates within **0.1s** of settle ([NN/G attention](https://www.nngroup.com/articles/animation-usability/)) | Finger up, photo still drifting 400ms with no cue |
| State change | `aria-current` / pressed on the matching thumb or marker; color filter (when real) changes **this** set | Animation is the only cue (fails 1.4.1) |
| Spatial metaphor | Horizontal roll = more photos of **this** piece; VT = “the same piece, closer” | Related-rail A02 inside A01’s scroller |
| Signifier | Cut-off next photo + gold hairline dots (when n>1); phone does not need hover | Rail looks like a static poster when extra 200s exist |
| Attention | One moving thing: the photo | Snap + shimmer + VT + backdrop bloom all at once (Hipmunk pile-on — NN/G) |

### 3.3 Technique catalog (use / refuse)

| Technique | Source | Use on sell-test PDP? |
| --- | --- | --- |
| CSS Scroll Snap L1 (`x mandatory`, `align: start`, `stop: always`) | [MDN scroll-snap-type](https://developer.mozilla.org/en-US/docs/Web/CSS/scroll-snap-type); [CSS Scroll Snap](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_scroll_snap); [web.dev well-controlled scrolling](https://web.dev/articles/css-scroll-snap) | **Yes. Core.** Even when n=1 (one snap point; no fake extras). |
| `mask-image: linear-gradient(...)` edge fade | [MDN mask-image](https://developer.mozilla.org/en-US/docs/Web/CSS/mask-image); [CSS Masking L1](https://drafts.csswg.org/css-masking-1/) | **Yes, on the scroller chrome.** Off when n=1 (nothing to peek). Off under Reduce Motion if it feels like a pan. |
| Scroll-driven mask (`animation-timeline: scroll(self inline)`) | [css-scroll-driven.com horizontal gallery](https://www.css-scroll-driven.com/scroll-driven-view-transition-implementation-patterns/scroll-driven-media-and-gallery-effects/horizontal-scroll-gallery-with-scroll-timeline/) | **Optional, later.** Static edge mask first. Do not pair with `mandatory` if the fade must stay continuous (`proximity` note in that article). |
| `backdrop-filter` / `-webkit-backdrop-filter` | [MDN backdrop-filter](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/backdrop-filter) | **Yes, chrome only.** Keep the live phone bar. Lightbox veil may use it. **Never** on the `<img>`. |
| Cross-document VT + named `product-{MA}` | [Chrome VT](https://developer.chrome.com/docs/web-platform/view-transitions/); [MDN view-transition-name](https://developer.mozilla.org/en-US/docs/Web/CSS/view-transition-name) | **Yes, on the frame.** Prerequisite: `10` FIX 3. |
| Same-document `startViewTransition` for color / slide | [Chrome same-document](https://developer.chrome.com/docs/web-platform/view-transitions/same-document) | **Color:** 150–250ms **opacity** (`10` §8), not a named wipe. **Slide:** prefer **native snap**; do not VT every flick. |
| CSS Overflow 5 `::scroll-button()` / `::scroll-marker` | [Chrome, Carousels with CSS](https://developer.chrome.com/blog/carousels-with-css); [Chrome, accessible carousels](https://developer.chrome.com/blog/accessible-carousel) | **Progressive enhancement** behind `@supports`. Real prev/next buttons + `aria-` first (Firefox/Safari gaps). |
| Swiper / Keen / CSS-only radio hacks | vendor | **Refuse** as the default. |
| `shape()` liquid ooze / Bebber goo | `13` §3.3 | **Refuse on photos.** Optional only on Featured gold rule (`13`), not here. |

---

## 4. Spec deep-dive (Fast OFF — implementers need the traps)

### 4.1 CSS scroll-snap

Set **on the scroll container**: `scroll-snap-type`. Strictness:

- **`mandatory`** — after scroll ends, the UA **must** snap if a snap position exists ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/scroll-snap-type)). Fashion PDP: **use this**. A sleeve stuck at 40% is a lie about the cut.
- **`proximity`** — UA *may* snap. Better for long editorial strips; worse for “one look, one frame.”

Axis: **`x`** or **`inline`**. Prefer `x` on this LTR lookbook (VN copy does not flip the rail). Do not snap `both`.

Set **on each slide**:

```css
.pdp-rail {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scroll-padding-inline: 0;
  overscroll-behavior-x: contain;
  -webkit-overflow-scrolling: touch;
}
.pdp-slide {
  flex: 0 0 100%;
  scroll-snap-align: start;
  scroll-snap-stop: always;
}
```

`scroll-snap-stop: always` forces a stop at **each** photo even on a fast flick ([CSS-Tricks / common gallery recipe](https://css-tricks.com/almanac/properties/s/scroll-snap-type/); [Chrome carousel note](https://developer.chrome.com/blog/carousels-with-css)). Boutique: the buyer must not skip the only other 200 of this mã.

`scroll-padding` keeps the snapped edge off a sticky header if you inset the rail. Live header is `h-14` / `sm:h-16` sticky; the hero is **below** it, so padding 0 is correct **unless** you put a floating control on the frame.

**Keyboard:** a scrollport that is not a native `<input>` often cannot receive arrows. Put `tabindex="0"` on the rail, `role="region"` `aria-roledescription="carousel"` **or** (when n=1) skip carousel semantics and keep a plain figure ([Chrome accessible carousel](https://developer.chrome.com/blog/accessible-carousel); Adrian Roselli, keyboard-only scrolling areas). APG Carousel is heavy; with n=1, **do not** announce a carousel.

**n=1 (today):** still use the same DOM (one `li`). Mandatory snap with one child is a no-op visually. That is honest. Do not duplicate `cover.jpg` to fake a roll.

**JS:** `element.scrollTo({ left: i * width, behavior })` for buttons. `behavior: "smooth"` **only** when `prefers-reduced-motion: no-preference`. Otherwise `behavior: "instant"` (or `"auto"`).

**Re-snap:** MDN: if content is added/removed, the container **re-snaps** to the previously snapped item if it still exists. Color filter that **removes** slides must then snap to index 0 of the **filtered** set — still this mã.

### 4.2 mask-image gradients

`mask-image` hides parts of an element using the alpha (and optionally luminance) of a mask ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/mask-image); [CSS Masking L1](https://drafts.csswg.org/css-masking-1/#the-mask-image)). A CSS `linear-gradient` is a valid `<image>`.

Boutique recipe (scroller, not img):

```css
.pdp-rail {
  --fade: 1.25rem;
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
  mask-mode: alpha;
}
```

Black / opaque = visible; transparent = paper shows through. That **peek** is the watery edge. Prefix `-webkit-mask-image` for Safari.

**Traps:**

1. **n=1 / first / last.** A symmetric fade **eats** the garment’s left/right crop on a single cover. APPLY: `--fade: 0` when `n === 1` or at the start/end (scroll-driven or `data-edge="start|mid|end"`). Prefer mid-only fades.
2. **`mask-mode`.** Default `match-source` is usually alpha for CSS gradients. Set `alpha` explicitly so a gold-tinted gradient does not luminance-clip.
3. **Failed mask = transparent black = nothing visible** (MDN). Never `url()` a local `file://` mask. Gradients do not CORS-fail.
4. **Animation type is discrete** for `mask-image` (MDN formal definition). You cannot smoothly tween two gradient strings as one property in all engines. Change `--fade` (if registered) or toggle a class; do not expect a 200ms interpolation of the image list.
5. **Backdrop root.** An element with `mask` / `mask-image` ≠ `none` **is a backdrop root** ([MDN backdrop-filter](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/backdrop-filter)). A child `backdrop-filter` will only frost **inside** the masked scroller, not the page. Therefore: **do not put lightbox-veil blur inside the masked rail.** Veil is a portal to `document.body` (`10` FIX 3).
6. **Do not mask the JPEG** with a radial “luxury vignette” that crops the garment. Editorial crop lives in the **file** / `object-cover` frame (`13` §5).

### 4.3 backdrop-filter

`backdrop-filter` filters **pixels already painted behind** the element, up to the nearest **backdrop root**. The element (or its background) must be **partly transparent** or you will see nothing ([MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/backdrop-filter)).

Backdrop roots include: the document root; `filter` ≠ none; **`opacity` < 1**; **`mask` / `mask-image` / `clip-path` ≠ none**; another `backdrop-filter`; `mix-blend-mode` ≠ normal; `will-change` of the above.

Live lookbook already chose two frost strategies:

| Surface | How it frosts | Implication |
| --- | --- | --- |
| Sticky header | Inner `div.absolute.inset-0.bg-paper` **`opacity: 0.92`** | That inner div **is** a backdrop root. A blur **inside** the header will not sample the hero. Do not “upgrade” the header to `backdrop-blur` **and** keep 0.92 on a wrapper without checking. |
| Phone Message bar | `bg-paper/95 … backdrop-blur-md` | **Keep.** `--blur-md: 12px` is already the token. This is paper air, not iOS glass. |

APPLY for lightbox:

```css
.pdp-lightbox-veil {
  background: color-mix(in srgb, var(--ink) 70%, transparent);
  -webkit-backdrop-filter: blur(var(--blur-md));
  backdrop-filter: blur(var(--blur-md));
}
@media (prefers-reduced-motion: reduce) {
  .pdp-lightbox-veil {
    -webkit-backdrop-filter: none;
    backdrop-filter: none;
  }
}
```

Reduce Motion: blur is not always “motion,” but a live blur as the dialog opens can feel like a zoom. Instant opaque `bg-ink/70` is the fallback (`10` §9.5). Do not animate `backdrop-filter` from 0→12px on open (filter animation is expensive; WWDC23 oscillation/comfort).

**Never:**

- `backdrop-filter` on the hero `<img>` or the snap child (frosted silk = fake fabric).
- Combining `opacity: 0.92` parent + child blur and expecting the **page** to frost.
- Chromatic aberration / `url(#displacement)` “glass” over covers (`13` refuse list).

Safari: keep the `-webkit-` prefix. If blur is unsupported, `bg-paper/95` / `bg-ink/70` must still read.

### 4.4 View Transitions

Two trigger models, same snapshots ([Chrome](https://developer.chrome.com/docs/web-platform/view-transitions/)):

| Kind | Trigger | This shop |
| --- | --- | --- |
| Cross-document (MPA) | Same-origin navigation if **both** pages opt in | Home `/` → `/m/A01`. Opt-in: `@view-transition { navigation: auto; }` — **still missing** from the downloaded CSS chunk (`10` §4.4; this crawl). |
| Same-document (SPA) | `document.startViewTransition(() => update())` | Featured filter (`13` — Framer already owns it). Color swap (`10` — skip VT; use opacity). **Not** every snap flick. |

Names:

- Unique per participating element in a document. **Two nodes with `product-A01` is a bug.**
- Put `product-{THIS mã}` on the **frame** (the `aspect-[3/4]` / `bg-[#f3f1ee]` box that is the snap viewport), **not** on every slide.
- Slides inside may use **no** name, or `match-element` only if you never also name the frame the same way.
- Related-rail tiles keep `product-{neighbor}` (`10` FIX 3).

Live CSS already:

```css
::view-transition { pointer-events: none }
::view-transition-group(site-header) { z-index: 100; animation: none }
::view-transition-old(site-header) { display: none }
::view-transition-new(site-header) { animation: none }
@media (prefers-reduced-motion: reduce) {
  ::view-transition-group(*),
  ::view-transition-old(*),
  ::view-transition-new(*) { animation: none !important }
}
```

Keep all of that. Do **not** add a watery `clip-path` on `::view-transition-old(root)` (`13` §9). Optional custom animation **only** on `::view-transition-new(product-A01)` after names match, ≤280ms, skipped when reduced.

`startViewTransition` must be skipped when `matchMedia('(prefers-reduced-motion: reduce)').matches` ([Chrome same-document reduced motion](https://developer.chrome.com/docs/web-platform/view-transitions/same-document#handling_reduced_motion_preferences); [C39](https://www.w3.org/WAI/WCAG22/Techniques/css/C39); [SCR40](https://www.w3.org/WAI/WCAG22/Techniques/client-side-script/SCR40)).

### 4.5 How the four compose (legal stack)

```
document.body
  header          VT: site-header (instant)
  main
    .pdp-frame    VT: product-{MA}     ← morph target; aspect 3/4; bg #f3f1ee
      .pdp-rail   overflow-x + snap    ← mask-image HERE (optional peek)
        .pdp-slide × n                 ← 200s only; stop:always
          img                         ← NO filter, NO backdrop-filter, NO VT name
    color row     text pills when stored names exist; hex squares are a gap
    copy + Message
  related rail    VT: product-{neighbor} only
  phone bar       backdrop-blur-md + paper/95   ← KEEP; not inside .pdp-rail
  lightbox portal backdrop-filter on VEIL only
```

Illegal stacks:

- `mask-image` + child `backdrop-filter` expecting to frost the **page**.
- VT name on **each** slide `product-A01` (duplicate).
- Snap rail that includes related-rail mãs.
- Goo / displacement on `img`.

---

## 5. As-built hook map (cite the live host)

Crawl: 2026-09-09. CSS `34vl_zddoo4ws.css`.

### 5.1 CSS tokens (do not rename)

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
  --blur-md: 12px;
}
```

Fonts (HTML classes on `<html>`): `be_vietnam_pro_…__variable` + `cormorant_garamond_…__variable`.

Existing keyframes — keep names (`10` FIX 1): `announce-fade`, `shimmer-slide`, `cta-flash`. Reduced-motion query as quoted in `10` §4.7 / `13` §4.1.

`--duration-move: .4s` is **longer** than a PDP snap settle should *feel*. Native snap uses UA physics; do not bind `scroll-behavior: smooth` to `.4s` as a CSS animation on `scrollLeft`. Button `scrollTo` smooth is OK under no-preference only.

### 5.2 Surfaces

| Surface | URL | Gallery job today | Customer PDP? |
| --- | --- | --- | --- |
| Lookbook home | `/` | `product-{MA}` on every allowlist tile + `site-header` | Grid |
| Category | `/c/ao` … `/c/quan` | Same cards when the set is non-empty; `/c/quan` header only | Grid |
| PDP | `/m/{MA}` | **One** `cover.jpg`; no snap; no mask; **no** hero VT name | Yes |
| Admin | `/admin` | Not a customer gallery | No |
| Intake | https://sassy-closet.vercel.app | Rose `PhotoLightbox` + 3-up thumbs | **No** |

### 5.3 `/m/A01` (Available top, $25)

- Hero: `/products/A01/cover.jpg` alt `A01. TOP` — **visible** (no `opacity-0` on this img). Inner wrapper `style="opacity:1;transform:none"` (motion-lib residue; `13` saw the same on the grid).
- **No** `view-transition-name: product-A01` on the `overflow-hidden bg-[#f3f1ee]` box.
- Color row under hero: two **hex** buttons `aria-label="Color #F4F0E8"` / `Color #1C2A4A"`, `aria-pressed="false"`, `h-6 w-6 rounded-sm`. Hub recorded ids for A01 are `kem`, `xanh` (`05` / `10` §4.5) — **do not relabel these hexes in this pass** unless admin stored those words. Do not add slides for them while only `cover.jpg` 200s.
- Copy, Message, related A02 with `product-A02` + `opacity-0` on the related img until JS (`10` FIX 2 — still a related-rail bug).
- Phone sticky: `fixed inset-x-0 bottom-0 z-40 md:hidden` → inner `backdrop-blur-md bg-paper/95 border-gold/45`.
- Staff `aria-label="Shop tools"` gold dot — not a cart (`09`).

### 5.4 `/m/P02` (Hold thermos, Inbox for price)

- Hero: `/products/P02/cover.jpg` alt `P02. THERMOS`. **No** `product-P02` name.
- **No** hex row under **this** hero this crawl. Related P01/P03/P04/P05 cards show tiny hex chips (`h-4 w-4`) — still not text (`02`).
- Related VT names: neighbors only.
- Hold badge gold; no dollar.

### 5.5 What already honors Reduce Motion

| Motion | Reduced today |
| --- | --- |
| shimmer / announce / cta-flash / VT animations | `none !important` |
| Header VT | Already `animation: none` |
| Hero snap / mask | n/a (not shipped) |
| Card hover 1.08 | **Still runs** (`10` MOT-03) |
| Phone `backdrop-blur-md` | Still on — static frost; OK to keep |

### 5.6 Intake behavior library (do not import chrome)

| Pattern | File | Steal |
| --- | --- | --- |
| Lightbox | `sassy-closet/components/PhotoLightbox.tsx` (PR #14) | Portal; `aria-modal`; Esc; focus close; restore; body lock; `setTimeout(0)` close |
| 3-up + `+N` | `PhotoThumbs.tsx` | Zero photos = text-only; `FIND_CARD_THUMB_LIMIT = 3` |
| Kind exhaustive switch | `kinds.ts` `assertNever` | If Origin adds a `layout` union, same `never` default |

---

## 6. Kelly Ying look — steal the rhythm, refuse the cart and the glass

| Kelly Ying / fashion cue | Steal? |
| --- | --- |
| Editorial 3/4 crop, SKU visible | **Yes** — keep `aspect-[3/4]` `object-cover` `ma-mark` |
| Collection hairline, uppercase tracking | **Yes** — dots / arrows in **gold hairline**, not pills |
| Livestream cadence (their Sunday/Monday print) | **No** — Boss has not locked days (`01`) |
| Cart · Checkout · $10 / $300+ | **No** |
| `V826.` / `V984.` | **No** — do not invent slides or mãs |
| iOS glass over the dress photo | **No** |
| Peek of the next look in a boutique window | **Yes** — that is the mask fade when n>1 |

---

## 7. Reliability law (the rail must not lie)

1. **Hold remains a word** while photos roll. Frosted veil must not recolor Hold into Available (`09` MOT-08).
2. **One mã per rail.** A01’s scroller never contains A02’s file. Related rail is a **separate** list.
3. **200s only.** Build slides from HEAD/GET success, not from an OD table or “typical boutique has 5 angles.”
4. **n=1 is a pass.** No cloned cover, no looping `scroll-snap` that teleports.
5. **Color filter ⊆ this mã.** When stored names exist, filtered set may be 0 extra files — keep cover + “Message {MA} for real photos” (`10` FIX 5). Never borrow A02.
6. **Duplicate VT names are identity bugs.** One `product-A01` per document.
7. **Pointer events.** `::view-transition { pointer-events: none }` stays. Lightbox portal above the sticky Message (`z-[80]` vs bar `z-40`).
8. **No Excel, no intake edit, no Square Save.**

---

## 8. PDP rail recipe (scroll-snap)

### 8.1 Markup (smallest)

```html
<div class="pdp-frame relative overflow-hidden bg-[#f3f1ee]"
     style="view-transition-name: product-A01">
  <ul class="pdp-rail" tabindex="0" aria-label="Photos of A01">
    <li class="pdp-slide">
      <button type="button" aria-label="Xem ảnh lớn · View larger">
        <img src="/products/A01/cover.jpg" alt="A01. TOP" class="aspect-[3/4] w-full object-cover" />
      </button>
    </li>
    <!-- more <li> only if that src 200s -->
  </ul>
</div>
```

`/m/P02` → `product-P02` and `Photos of P02`. Never `product-A02` on this box.

When n=1: omit `tabindex="0"` if you want; the enlarge button is the control. Do not set `aria-roledescription="carousel"`.

When n>1: `aria-label` can include “slide k of n” live region **polite** on snap settle. Prev/next `aria-controls` the rail id.

### 8.2 CSS (keep boutique frame)

Reuse `bg-[#f3f1ee]` (live placeholder, not `--blush`). Do not switch to `--blush` without Boss — it is a different cream.

Hide scrollbar **or** keep thin gold — live Featured uses `.tab-scroll { scrollbar-width: none }`. A photo rail may keep a **thin** scrollbar as an affordance ([CodeFronts shop-the-look recipe](https://codefronts.com/snippets/css-image-carousel/shop-the-look-card-slider/) argues not to hide it). APPLY: `scrollbar-width: thin; scrollbar-color: var(--gold) transparent` on desktop; hide on the phone bar overlap if it fights the CTA. Do not invent a second design system.

### 8.3 Controls

**Must (n>1):**

- Prev / Next buttons, 44×44 (`2.5.8`), ink/paper, gold hairline, disabled (not missing) at ends.
- Keyboard: Left/Right when the rail or a control is focused; do not steal page Up/Down.

**May:**

- `@supports (scroll-marker-group: after)` gold `h-px` / 6px squares as `::scroll-marker`. Selected = `--gold`. Unselected = `--line`.
- Thumbs under the rail (intake 3-up **behavior**, lookbook chrome). Thumb click `scrollTo` that index.

**Must not:**

- Autoplay.
- Infinite loop wrapping last→first (feels like a second piece).
- Dots when n=1.

### 8.4 Lightbox (same set)

`10` FIX 3 contract, restated for a **rail**:

- Portal to `body`; veil `bg-ink/70` + optional `backdrop-blur-md`; **not** `bg-rose-950/70`.
- Overlay rail: **same** snap recipe, same src list, start at the index that was open.
- Esc / backdrop / ✕; focus trap or tiny control set; restore focus to the slide button.
- `setTimeout(0)` close so the sticky Message does not eat the click.
- Reduced: no scale pop; veil instant; snap `behavior: auto`.

---

## 9. mask-image (watery paper edge)

### 9.1 When to paint a fade

| State | `--fade` |
| --- | --- |
| n = 1 | `0` |
| n > 1, snapped at 0 | right edge only |
| n > 1, snapped at last | left edge only |
| n > 1, middle | both edges, `1–1.5rem` |

Do not fade more than ~8% of the frame — Baymard zoom research is about **seeing the garment**, not hiding it.

### 9.2 Reduce Motion

If the fade **moves** with scroll (scroll-driven), kill it under `prefers-reduced-motion: reduce` (`mask-image: none`). A **static** mid-rail fade is optional to keep (it is not animation). Prefer kill for vestibular users if QA says the peek “swims.”

### 9.3 Do not

- Mask `.shimmer` with a second gradient (double-eat).
- Use SVG luminance masks over photos.
- Animate `mask-image` URL swaps.

---

## 10. backdrop-filter (chrome, not cloth)

### 10.1 Keep what is live

Phone sticky Message: `backdrop-blur-md` + `bg-paper/95` + `border-gold/45`. That **is** the boutique frost. Do not replace with a heavier 40px “glass” or saturate/invert.

Header: leave the 0.92 paper sheet unless a dedicated header APPLY (not this file) restacks it. Do not add blur under that opacity wrapper and call it a bugfix.

### 10.2 Lightbox / floating dots

Veil may frost. Dots sitting **on** the photo may use `bg-paper/80` **without** blur (blur on a 6px dot is noise). If you frost a control **over** the hero, put it **outside** the masked rail (sibling overlay), or accept that mask is a backdrop root.

### 10.3 Reduce Motion / performance

Do not animate blur. Tokopedia moved scroll work to CSS to cut main-thread cost ([Chrome SDA](https://developer.chrome.com/blog/css-ui-ecommerce-sda)). A per-frame `backdrop-filter` under a snapping hero is a jank trap — keep blur on **static** chrome.

---

## 11. View Transitions (frame morph, not per-flick)

### 11.1 Cross-document (home → PDP)

Order of operations:

1. Put `product-{MA}` on `.pdp-frame`.
2. Add `@view-transition { navigation: auto; }` on layout CSS (`10` FIX 1 PATCH C).
3. Keep header rules.
4. Only then consider a custom `::view-transition-new(product-A01)` pour (`13` §9). Default crossfade is enough.

### 11.2 Same-document

| Event | VT? |
| --- | --- |
| Finger snap to next photo | **No** — native scroll |
| Button `scrollTo` | **No** |
| Color chip (stored names, real files) | **No VT wipe** — opacity 150–250ms (`10`) |
| Open lightbox | **No** full-page VT — overlay |
| Featured tabs | Out of scope (`13`) |

### 11.3 Reduced

Skip `startViewTransition`. CSS already zeros `::view-transition-*` animations. Names may stay (they are not motion).

---

## 12. Color → gallery (do not watery-invent chips or files)

Live A01 hex squares (`#F4F0E8`, `#1C2A4A`) are **not** the `02` text-pill UI. APPLY this file:

1. **Do not** turn those hexes into extra snap children without tagged images that 200.
2. **Do not** invent labels Kem / Xanh / Đỏ from the hex or from `05`’s recorded table unless that **row** stores the word.
3. When admin later has `colors[].id` **and** `images[].colorId` **and** those srcs 200: filter the **rail** to matching + shared (`colorId == null`). Re-snap to 0. Opacity crossfade on the `<img>` if the element is reused; if you remount slides, native snap from 0 is enough.
4. Empty filter: keep cover, keep Message line. Never A02.

`aria-pressed` on A01’s hexes is currently **false, false** — neither selected. If Origin keeps hexes this pass (out of `02` law), at least one must be pressed **or** they must be non-toggle decorations. Prefer `02` text pills in a later APPLY; this FX pass must not make the rail depend on them.

---

## 13. Reduced-motion + vestibular

| Criterion | Rail impact |
| --- | --- |
| [2.2.2](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) A | Do not auto-play the rail. `.shimmer` is still the loop (`10`). |
| [2.3.1](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html) A | Do not strobe dots. |
| [2.3.3](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) AAA | Snap *physics* are UA scrolling (usually allowed). Custom `scroll-behavior: smooth`, VT zooms, mask swim, blur bloom = interaction animation → C39. |
| [1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) | Index must not be gold-dot-only; include text “1 / 3” or `aria-current`. Hex-only color remains a gap. |
| [2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) | Prev/next/enlarge ≥ 24×24 CSS px (shop already uses 44 on intake close). |

Apple: fade, don’t zoom. Reduced fallback = **instant** `scrollTo`, **no** smooth, **no** VT animation, **no** moving mask, enlarge still works.

---

## 14. Timing budget

| Interaction | Budget | Live 2026-09-09 | APPLY |
| --- | --- | --- | --- |
| Enlarge control visible | 0 (paint) | Missing | Add button |
| Snap settle (finger) | UA | n/a | `mandatory` + `stop: always` |
| Prev/next `scrollTo` | ≤200ms perceived | n/a | `smooth` only if no-preference; else instant |
| Color img swap | 150–250ms | hex chips, no swap | opacity, not wipe |
| Home → PDP VT | ≤300ms | names mismatch | `10` FIX 3 first, then `@view-transition` |
| Lightbox open | ≤200ms | missing | instant veil if reduced |
| Shimmer | 1.3s infinite | on related cards | `10` FIX 1; **not** on PDP hero img this crawl (no `.shimmer` on A01 hero) |
| `--duration-move` .4s | — | unused on PDP | do not bind the rail to it |

NN/G 0.1 / 1 / 10s still apply ([Response Time Limits](https://www.nngroup.com/articles/response-times-3-important-limits/)). A 540ms `filterSlide` wait is a Featured bug (`13`); do not copy it here.

---

## 15. Performance

- Decode **this mã’s** 200s. Preload hero `cover.jpg` is already in `<head>`. Do **not** preload A02 on A01 except the related tile (live already preloads A02 — LCP cost `06` already flagged). Extra slides: `loading="lazy"` after the first.
- Animate `transform` / `opacity` / native scroll. Do not animate `width`, `filter`, or `backdrop-filter` on the hero ([Lewis FLIP](https://aerotwist.com/blog/flip-your-animations/)).
- `content-visibility` on offscreen slides is optional; snap + `flex-basis: 100%` already limits paint.
- ISR `stale-time: 300` — the rail reads the **payload**, not a public `/api/catalog` (404).

---

## 16. APPLY — [sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)

Human-readable ticks. **Paste block is §22.** Origin shop `main` is off-limits. Feature branch + Preview only.

### 16.0 Do not touch (lock — tick first)

- [ ] Allowlist only: `A01 S01 P01 P02 P03 P04 P05 K01 H01 A02`.
- [ ] Hold P02 / P05 stay **Inbox for price**.
- [ ] No Excel. No intake. No Square Save. No FB Send.
- [ ] No cart. No `V984`. No `$10 / $300+`.
- [ ] No `/products/{MA}/001.jpg` unless it **200s**.
- [ ] Do not restyle fonts / gold / Message CTAs “to look cleaner.”
- [ ] Do not fight `13`’s Featured pour in this PR unless colliding by accident — PDP files only.

### 16.1 View-transition frame (prerequisite)

- [ ] `.pdp-frame` (today’s `relative overflow-hidden bg-[#f3f1ee]`) has `view-transition-name: product-{THIS mã}`.
- [ ] Related rail keeps **neighbor** names only.
- [ ] `@view-transition { navigation: auto; }` after names match.
- [ ] Keep `::view-transition { pointer-events: none }` and header freeze.

### 16.2 Scroll-snap rail

- [ ] Scroller `scroll-snap-type: x mandatory`; children `scroll-snap-align: start; scroll-snap-stop: always; flex: 0 0 100%`.
- [ ] Slide list = 200s for **this** mã (today: one `cover.jpg`).
- [ ] n=1: no carousel announcement, no dots, no cloned slide.
- [ ] n>1: prev/next 44×44; arrows; no wrap.
- [ ] `overscroll-behavior-x: contain` so the page does not hijack a horizontal flick.

### 16.3 mask-image

- [ ] Gradient on the **rail**, `-webkit-` prefix, `mask-mode: alpha`.
- [ ] `--fade: 0` when n=1 and at ends.
- [ ] No mask on `<img>`. No mask+backdrop-filter on the same node as the lightbox veil.

### 16.4 backdrop-filter

- [ ] Keep phone `backdrop-blur-md` bar.
- [ ] Lightbox veil may frost; Reduce Motion → solid `ink/70`.
- [ ] No blur on photography.

### 16.5 Lightbox + enlarge

- [ ] Hero (and each slide) is a `<button>` enlarge, not a bare img onclick.
- [ ] Intake **behavior**, lookbook **chrome** (`10` §9).
- [ ] Overlay uses the **same** src set and snap recipe.

### 16.6 Color

- [ ] Do not invent chips or files.
- [ ] If hex row stays, it must not spawn fake slides.
- [ ] When real named colors + tagged 200s exist: filter rail; text pills per `02`/`10`.

### 16.7 Reduce Motion

- [ ] Instant scroll; no VT animation; no moving mask; enlarge still works.
- [ ] Related-rail `opacity-0` still a `10` FIX 2 — do not copy that onto the hero.

### 16.8 Verify (Origin, after FX work)

1. `/m/A01` cover visible. Chrome: home A01 tile morphs into A01 **frame** (not A02).  
2. `/m/A01` enlarge → lightbox `cover.jpg` only; Esc / ✕ / backdrop; Message still works.  
3. `/m/P02` Hold, no `$`, `product-P02` on **its** frame.  
4. `/m/A03` 404. `/c/quan` empty.  
5. Reduce Motion: no shimmer, no 1.08 if `10` landed, no VT zoom, rail still swipeable.  
6. Network: no `e.tb.cn`, no ¥, no A03, no V984, no invented `001.jpg` 404s as `<img>`.  
7. Phone: sticky Message + `backdrop-blur-md` still there; rail does not trap it.  
8. If a second file 200s later: snap settle, fade on the peek edge, no wrap to another mã.

---

## 17. Anti-patterns (quick refuse list)

1. Swiper / Slick / “just npm i embla” as the first move.  
2. Duplicate `cover.jpg` so the rail “has something to roll.”  
3. `product-A01` on every slide.  
4. `product-A02` left as the only name on `/m/A01`.  
5. `backdrop-filter` on the garment.  
6. `mask-image` on the JPEG vignette.  
7. Goo / displacement / `shape()` ooze on photos (`13`).  
8. Hex chips inventing Kem slides.  
9. Infinite loop carousel.  
10. Autoplay.  
11. Liquid root VT wipe.  
12. Intake rose lightbox.  
13. Excel / Official xlsx / Square Save / FB Send.  
14. `Q01` / `A03` / `AO001` on the lookbook.

---

## 18. Acceptance (sell-test PDP FX)

- [ ] Allowlist unchanged. Holds honest.  
- [ ] Hero VT name matches **its** mã.  
- [ ] Snap rail exists; n=1 is honest; n>1 rolls with `stop: always`.  
- [ ] Mask peek only when there is a neighbor; never hides a single cover.  
- [ ] Backdrop frost on chrome only.  
- [ ] Lightbox uses 200s only.  
- [ ] Reduce Motion still buys.  
- [ ] Sources in §20 still explain every shop-law sentence.  
- [ ] §22 paste was not paraphrased into “make it premium.”

---

## 19. Open questions (do not answer by inventing)

1. When will `/products/{MA}/001.jpg` (or Blob URLs) actually **200**? Lightbox/rail must follow 200s, not this sentence.  
2. Will customer color UI drop hex squares for **text** (`02`) in the same Origin PR as this rail, or later? This file must not block on renaming `#F4F0E8`.  
3. Featured `filterSlide` vs PDP snap — keep separate. If a future agent unifies “watery” into one Motion helper, refuse on photography.  
4. `@view-transition { navigation: auto }` — confirm in a Chrome trace after names match; this CSS chunk still lacks it.  
5. Granola was unauthorized — if a meeting already banned `backdrop-filter` on the phone bar, update this file; until then, **keep the live bar**.  
6. Parallel FX LEARN (`15`–`18` / `20+`) — if they ship a frosted carousel, **merge**: one rail, this stack, no second library.

---

## 20. Sources

### 20.1 Shop law and as-built

- `README.md` — Square SoT; bots draft; Facebook inbox.  
- `excel-kit/DESIGN_NOTES.md`, `excel-kit/schema.py` — mã law; ASK STOCK (**read only**; this PR does not edit kit).  
- `excel-kit/docs/SELL_CATALOG_CONTRACT.md` + sample (PR #18) — allowlist, prices, Hold P02/P05.  
- Sisters `01`–`14` (PRs #19–#33) — look lock, PDP nouns, MOT checklist, motion (`10`), watery tabs (`13`).  
- Slack `#shop-decisions` (2026-09-04):  
  - [Channel law](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788541753903809)  
  - [Track stock ON proposal](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788553328521899)  
  - [Boss yes](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788553474026779)  
  - [Square LIVE](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788556083454949)  
  - [Soft-launch prep, draft only](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788557030839509)  
- Live host 2026-09-09: https://sassy-closet-shop.vercel.app — CSS `34vl_zddoo4ws.css`.  
- Intake `sassy-closet/components/PhotoLightbox.tsx`, `PhotoThumbs.tsx` (PR #14).  
- Kelly Ying Boutique — <https://www.kellyyingboutique.net/> (look / cadence only).

### 20.2 CSS scroll-snap / carousels

- MDN, *CSS scroll snap* — <https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_scroll_snap>  
- MDN, `scroll-snap-type` — <https://developer.mozilla.org/en-US/docs/Web/CSS/scroll-snap-type>  
- CSS Scroll Snap Module Level 1 — <https://drafts.csswg.org/css-scroll-snap-1/>  
- web.dev, *Well-controlled scrolling with CSS scroll snap* — <https://web.dev/articles/css-scroll-snap>  
- CSS-Tricks, `scroll-snap-type` — <https://css-tricks.com/almanac/properties/s/scroll-snap-type/>  
- Chrome, *Carousels with CSS* — <https://developer.chrome.com/blog/carousels-with-css>  
- Chrome, *Make accessible carousels* — <https://developer.chrome.com/blog/accessible-carousel>  
- CodeFronts, shop-the-look card slider (directional) — <https://codefronts.com/snippets/css-image-carousel/shop-the-look-card-slider/>

### 20.3 mask-image / backdrop-filter

- MDN, `mask-image` — <https://developer.mozilla.org/en-US/docs/Web/CSS/mask-image>  
- CSS Masking Module Level 1 — <https://drafts.csswg.org/css-masking-1/#the-mask-image>  
- MDN, `backdrop-filter` (backdrop **roots**, including mask / opacity) — <https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/backdrop-filter>  
- Filter Effects Module Level 1 — <https://drafts.fxtf.org/filter-effects-1/>  
- Horizontal gallery + `mask-image` + scroll timeline (optional later) — <https://www.css-scroll-driven.com/scroll-driven-view-transition-implementation-patterns/scroll-driven-media-and-gallery-effects/horizontal-scroll-gallery-with-scroll-timeline/>

### 20.4 View Transitions

- Chrome, *Smooth transitions with the View Transition API* — <https://developer.chrome.com/docs/web-platform/view-transitions/>  
- Chrome, same-document + reduced motion — <https://developer.chrome.com/docs/web-platform/view-transitions/same-document#handling_reduced_motion_preferences>  
- MDN, View Transition API — <https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API>  
- MDN, `view-transition-name` — <https://developer.mozilla.org/en-US/docs/Web/CSS/view-transition-name>  
- CSS View Transitions Module Level 1 — <https://drafts.csswg.org/css-view-transitions-1/>

### 20.5 Motion / a11y / gallery UX

- Nielsen Norman Group, *The Role of Animation and Motion in UX* — <https://www.nngroup.com/articles/animation-purpose-ux/>  
- Nielsen Norman Group, *Animation for Attention and Comprehension* — <https://www.nngroup.com/articles/animation-usability/>  
- Jakob Nielsen, *Response Time Limits* — <https://www.nngroup.com/articles/response-times-3-important-limits/>  
- Apple HIG, *Motion* — <https://developer.apple.com/design/human-interface-guidelines/motion>  
- WWDC23, *Design considerations for vision and motion* — <https://developer.apple.com/videos/play/wwdc2023/10078/>  
- W3C, WCAG 2.2 SC 2.2.2 / 2.3.1 / 2.3.3 / 1.4.1 / 2.5.8 Understanding pages.  
- W3C technique C39 — <https://www.w3.org/WAI/WCAG22/Techniques/css/C39>  
- WAI-ARIA APG, Dialog (Modal) — <https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/>  
- Baymard, *Ensure Sufficient Image Resolution and Zoom* — <https://baymard.com/blog/ensure-sufficient-image-resolution-and-zoom>  
- A11yFix, lightbox keyboard/focus — <https://blog.a11yfix.dev/blog/product-image-zoom-lightbox-accessibility/>  
- Motion Spec, *2.3.3 is AAA; 2.2.2 is the Level A loop* — <https://motionspec.dev/blog/wcag-2-3-3-animation-from-interactions>

### 20.6 Weaker / vendor (directional only)

- FreeFrontend liquid-glass — OS chrome, not this look.  
- Theme posts that claim “+% conversion from microinteractions” without a method are **not** shop law.  
- CSS Overflow 5 scroll markers — Chrome-first; progressive enhancement only.

---

## 21. One-page APPLY card (tear-off)

PDP watery rolling = **snap settle** + **paper-edge mask** + **frosted chrome** + **named frame morph**.  
Files: `cover.jpg` that **200**. Names: `product-{THIS mã}` on the frame.  
Blur the **veil**, not the silk. Fade the **rail**, not the JPEG.  
n=1 is honest. n>1 does not wrap to another mã.  
Paste **§22**. Do not add “also make it liquid glass.”

---

## 22. PASTE INTO ORIGIN AGENT (do not paraphrase)

Copy everything between the markers into a Cloud Agent on the **Origin `sassy-closet-shop` repo** (the git behind https://sassy-closet-shop.vercel.app). Not this kit. Not intake `sassy-closet/`. Not `excel-kit/`. Not Origin `main`.

```text
===== BEGIN ORIGIN PASTE — watery rolling PDP slides (LEARN 19) =====

You are editing Origin sassy-closet-shop. Ship WATERY ROLLING SLIDES on the
EXISTING fashion PDP gallery using CSS scroll-snap, mask-image edge fades,
backdrop-filter on chrome, and view transitions on the FRAME. Do not restyle.
Do not invent mã. Do not add iOS liquid glass. Do not npm i Swiper.
Do not touch intake or Excel.

HOST: https://sassy-closet-shop.vercel.app
LAW: Facebook inbox is the store. No cart. No Square Save. No FB Post/Send.
ALLOWLIST ONLY: A01 S01 P01 P02 P03 P04 P05 K01 H01 A02
HOLD (no $): P02 P05
PRICES: A01 $25 · S01 $28 · P01 $5 · P03 $18 · P04 $13 · K01 $37 · H01 $8 · A02 $22
LOOK LOCK: Cormorant Garamond + Be Vietnam Pro; paper / ink / gold / blush;
ma-mark; 11px uppercase tracking; gold HAIRLINE; announce-fade; shimmer;
cta-shine + cta-flash; aspect-[3/4] bg-[#f3f1ee].
Do NOT switch to intake rose / Allura / Nunito. Do NOT add Shopify cart.
Do NOT copy Kelly Ying V984 or “$10 shipping on $300+”.
Do NOT apply SVG goo / displacement / shape() ooze / backdrop-filter
to product photos.

FIND FILES (rg — names may differ; match these strings, then edit those files):

  rg -n "bg-\\[\\#f3f1ee\\]|products/.*/cover.jpg|view-transition-name:product-"
  rg -n "Message A01 for real photos|Inbox for price|backdrop-blur-md"
  rg -n "announce-fade|shimmer-slide|--duration-enter|--gold:"
  rg -n "@view-transition|::view-transition"

Expected (live 2026-09-09 HTML + 34vl_zddoo4ws.css):
  PDP hero:
    <div class="relative overflow-hidden bg-[#f3f1ee]">
      <div style="opacity:1;transform:none">
        <img src="/products/A01/cover.jpg" alt="A01. TOP"
             class="aspect-[3/4] w-full object-cover "/>
      </div>
    </div>
  NO view-transition-name on that box.
  /m/A01 related rail: view-transition-name:product-A02  (WRONG morph target)
  /m/P02 related: product-P01 P03 P04 P05 — NOT product-P02 on hero.
  /products/A01/cover.jpg 200; /products/A01/001.jpg 404; 002.jpg 404.
  Phone bar: bg-paper/95 backdrop-blur-md border-gold/45  (KEEP)
  Header: view-transition-name:site-header + inner bg-paper opacity 0.92
  :root --paper:#fff --ink:#111 --gold:#b08968 --blush:#f3eee8
        --duration-enter:.21s --duration-exit:.15s --duration-move:.4s
        --blur-md:12px
  ZERO scroll-snap / mask-image in the CSS chunk.
  A01 customer row: hex buttons #F4F0E8 and #1C2A4A (aria-label Color #…).
        Do NOT invent Kem/Xanh slides from those hexes. Do NOT mint files.

If a file is missing, create the smallest new file next to the PDP —
do not invent a second design system.

────────────────────────────────────────
FIX 1 — Frame name (View Transition morph)
────────────────────────────────────────
Put view-transition-name: product-{THIS mã} on the hero FRAME
(the overflow-hidden bg-[#f3f1ee] aspect box), not on <img>, not on <a>,
not on related tiles of a different mã.

  /m/A01 frame → product-A01
  /m/P02 frame → product-P02
  Related A02 tile → product-A02 (only)

ADD to layout/global CSS (keep existing header VT rules):

  @view-transition { navigation: auto; }

KEEP:
  ::view-transition { pointer-events: none }
  ::view-transition-group(site-header) { z-index: 100; animation: none }
  ::view-transition-old(site-header) { display: none }
  ::view-transition-new(site-header) { animation: none }
  reduced-motion: animation:none on ::view-transition-*

Do NOT watery-clip ::view-transition-old(root).
Do NOT put product-A01 on every slide (duplicate names).

────────────────────────────────────────
FIX 2 — CSS scroll-snap rail (watery ROLL)
────────────────────────────────────────
Turn the single img into a scroller INSIDE the named frame.

  .pdp-rail {
    display: flex;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    overscroll-behavior-x: contain;
    -webkit-overflow-scrolling: touch;
  }
  .pdp-slide {
    flex: 0 0 100%;
    scroll-snap-align: start;
    scroll-snap-stop: always;
  }

SLIDE LIST = srcs that already 200 for THIS mã.
Today: exactly one — /products/{MA}/cover.jpg
Do NOT add 001.jpg / 002.jpg while they 404.
Do NOT clone cover.jpg to fake a second slide.
Do NOT put A02 in A01’s rail.

n = 1: no dots, no aria-roledescription="carousel", no wrap.
n > 1: Prev/Next 44×44 ink/paper + gold hairline; disabled at ends;
       Left/Right when rail focused; polite "k / n".
       Do not infinite-loop.

Buttons: scrollTo({ left: i * width, behavior:
  matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'
})

Optional progressive enhancement ONLY behind
  @supports (scroll-marker-group: after)
gold hairline markers. Real buttons still exist.

Do NOT npm install a carousel library.

────────────────────────────────────────
FIX 3 — mask-image paper edge (watery PEEK)
────────────────────────────────────────
On the RAIL (not the img), when n > 1 AND not reduced:

  --fade: 1.25rem;
  mask-mode: alpha;
  -webkit-mask-image / mask-image:
    linear-gradient(to right,
      transparent 0, #000 var(--fade),
      #000 calc(100% - var(--fade)), transparent 100%);

At start snap: fade RIGHT only. At end: LEFT only. Middle: both.
n = 1 OR reduced: mask-image: none; --fade: 0.

NEVER mask the JPEG. NEVER url() a file mask.
Remember: mask-image makes a BACKDROP ROOT — do not put
lightbox backdrop-filter inside this node.

────────────────────────────────────────
FIX 4 — backdrop-filter chrome only
────────────────────────────────────────
KEEP the live phone Message bar:
  bg-paper/95 backdrop-blur-md border-gold/45
  --blur-md: 12px

Lightbox veil (portal to document.body):
  bg-ink/70 (NOT bg-rose-950/70)
  optional backdrop-filter: blur(var(--blur-md))
  Reduce Motion: blur NONE; solid ink/70
Do NOT animate blur 0→12px.

NEVER backdrop-filter / -webkit-backdrop-filter on <img>, .shimmer,
.pdp-slide, or the hero photograph.
Do not “upgrade” the header’s opacity:0.92 sheet in this PR.

────────────────────────────────────────
FIX 5 — Enlarge + lookbook lightbox (same set)
────────────────────────────────────────
Wrap each slide img in <button type="button"
  aria-label="Xem ảnh lớn · View larger">.

New file e.g. components/PhotoLightbox.tsx — do NOT import intake rose.

Contract (steal behavior from kit PhotoLightbox, restyle):
  - createPortal to document.body, z above sticky bar (z-40)
  - role="dialog" aria-modal="true" aria-labelledby=…
  - veil as FIX 4
  - image object-contain max-h-[88dvh] ring paper/gold, not rose
  - close 44×44, ink/paper, aria-label="Đóng"
  - Esc + backdrop + ✕
  - focus close on open; restore document.activeElement
  - lock body overflow
  - close via setTimeout(0) so click does not hit Message CTA
  - reduced: no scale pop; instant veil
  - gallery set = current mã + current color filter only
  - src list = 200s only (today cover.jpg)
  - INSIDE overlay: same snap recipe as FIX 2; start at opened index
  - arrows/swipe never wrap to another mã

Sticky footer Message {MA} (cta-shine, Page id 61594312648057)
must work after close.

────────────────────────────────────────
FIX 6 — Color row must not invent slides
────────────────────────────────────────
Live A01 hex squares #F4F0E8 / #1C2A4A are NOT text pills (LEARN 02/10).
This PR:
  - does not mint files or mãs from hex
  - does not add snap children for colors without tagged 200s
  - does not relabel hex as Kem/Xanh unless admin stored those WORDS
If you also ship text pills (preferred, not required here):
  recorded ids IF present on that row only:
    A01 kem,xanh · S01 kem · P01 hoa · P02 do · P03 den,do · P04 kem
    P05 hong,do,xanh · A02 cham-bi · K01 none · H01 none
  filter rail to colorId match OR null; opacity 150–250ms;
  missing photos → cover + Message line; NEVER /products/A02 on /m/A01.

JS if you call startViewTransition (you probably should NOT for snap):
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !document.startViewTransition) update();
  else document.startViewTransition(update);
NEVER startViewTransition on every scrollsnapchange.

────────────────────────────────────────
FIX 7 — Reduce Motion
────────────────────────────────────────
KEEP existing kills for announce-fade / shimmer / cta / VT animations.

ADD:
  @media (prefers-reduced-motion: reduce) {
    .pdp-rail { scroll-behavior: auto; mask-image: none; -webkit-mask-image: none; }
    .pdp-lightbox-veil { backdrop-filter: none; -webkit-backdrop-filter: none; }
  }

Finger scrolling may still snap (UA). Buttons use behavior instant.
No custom VT animation. Enlarge still works.

────────────────────────────────────────
HARD STOPS
────────────────────────────────────────
- No new mã. No Q01 / A03 / AO001 / V984 on the lookbook.
- No cart, Shop now, flying-to-cart, Swiper.
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

1. /  card A01 → /m/A01. Chrome motion ON: tile morphs into A01 FRAME
   (product-A01 → product-A01). A02 related is NOT the morph.
2. /m/A01 cover VISIBLE. Tap enlarge. Lightbox src =
   /products/A01/cover.jpg only. Esc / ✕ / backdrop. Focus returns.
   Message A01 still opens facebook.com/profile.php?id=61594312648057
3. /m/P02: Hold · Inbox for price. Frame name product-P02. No dollar.
4. /c/ao = A01 $25 + A02 $22. /c/quan empty. /m/A03 404.
5. Rail: n=1 no dots. If a second file 200s (do not invent): snap
   flush, stop:always, peek fade only on the neighbor edge, no wrap.
6. Reduce Motion: no shimmer, no VT zoom, no moving mask, no blur bloom;
   swipe + Message + lightbox still work.
7. Phone sticky bar still backdrop-blur-md + paper/95.
8. View-source / network: no e.tb.cn, no ¥, no A03, no V984,
   no <img> to 404 001.jpg.

Commit on an Origin cursor/* branch. Preview URL in the PR. Do not merge.

===== END ORIGIN PASTE =====
```

Mini Boss: copy the block above as the **entire** Origin prompt. Do not add “also make it more premium” or “add liquid glass.” The snap + mask + chrome frost + named frame *are* the watery rolling-slides pass. `10`’s lightbox/hero-name fixes and `13`’s Featured pour still apply if they are not on `main` yet — do not regress them; do not reimplement Featured inside this PDP PR.

End of 19.
