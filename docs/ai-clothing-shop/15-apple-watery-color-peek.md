# 15 — Apple watery see-through color + carousel peek (PDP)

**Learn track:** Ultra burn / Fast OFF (research + live as-built + paste-ready Origin APPLY).  
**Shop:** Sassy Closet — Facebook inbox is the store; Square Free is on-hand truth; sell-test lookbook is Origin-owned.  
**Live APPLY target:** [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)  
**Audience:** Mini Boss / Origin shop implementer / whoever ships **PDP color chips + gallery roll** without breaking reliability or the Kelly Ying look.  
**Date researched / crawled:** 2026-09-09.  
**This file does not assign stock, mint a mã, Save in Square, post to Facebook, restyle the boutique, or touch Excel / intake.**

Sister `13` is **Featured tab + grid pour** (home). Sister `10` is **general motion law**. Sister `02` / `05` own **color nouns**. This note is the **PDP material**: Apple-grade **watery see-through color chips**, a **peeking photo carousel**, and a **rolling tab/slide** when the buyer changes color — wired **only** through stored `colorId`. Mini Boss pastes **§19** into the Origin agent. Do not paraphrase §19 into “add iOS Liquid Glass to the garment.”

---

## 0. How to read this document

This is a **learn-track** note, not a rebuild brief and not permission to fork Origin shop code from this kit repo.

- **Cite, don’t invent.** Shop-law claims point at a file, Slack permalink, sister learn-track, or the live host. Industry claims point at Apple HIG / product pages / WWDC, W3C WCAG 2.2, WAI-ARIA, MDN, CSS Scroll Snap, Motion, or Chrome carousel notes. If a fact is missing, the gap is named.
- **Never invent a mã.** Customer-facing codes this pass may name are the **first-ten allowlist** only: `A01 S01 P01 P02 P03 P04 P05 K01 H01 A02`. Admin “Next mã A03” is a prediction. Slack `AO001` / `AO003` are **decision-template examples** (`#shop-decisions`, 2026-09-04), not live lookbook stock. Kelly Ying `V984.` / `V826.` are **their** SKUs — do not copy them onto Sassy tiles.
- **Two alphabets.** Sell-site / hub = `A01`. Official / Square / SoT = `AO001`. Motion never translates one into the other (`01` §9; `excel-kit/schema.py` `MA_RE`).
- **Facebook inbox is the store.** A “buy” is **Message {code}**. There is no cart. Color motion that implies checkout (bag-fly, finish pouring into a cart) is a lie.
- **No stock copy.** Do not write Shopify filler, fake reviews, “free shipping,” US-size charts, or invented color names (Kem, Navy, Burgundy, Lavender) from a hex. Keep the live bilingual sentences already on each mã.
- **No redesign mandate.** Improve **inside** paper / ink / gold / blush, Cormorant Garamond + Be Vietnam Pro, `ma-mark`, `announce-fade`, `shimmer` / `shimmer-slide`, `cta-shine` / `cta-flash`, gold `h-px` underline, `springSoft`, `filterSlide` ease `[.22, 1, .36, 1]`. Do not replace that language with iOS Liquid Glass over photography, Shopify Horizon, intake Allura/Nunito rose, or a new design system.

### 0.1 Research method (and what this pass could not see)

| Source | Result |
| --- | --- |
| Live sell-test HTML + JS of `/m/A01`, `/m/P04`, `/m/P05`, `/m/S01`, `/m/P02`, `/`, `/admin` (2026-09-09) | Primary **as-built** PDP color + gallery map. CSS chunk `/_next/static/immutable/chunks/34vl_zddoo4ws.css`. Home motion chunk `/_next/static/immutable/chunks/3_93acjqq2t4q.js`. PDP chunk `/_next/static/immutable/chunks/1xr62vxitay1m.js` (exports `ProductGallery`, `ColorSwatch`, `imagesForColor`, `coverSrcForColor`). |
| Repo `excel-kit/`, `sassy-closet/`, `README.md` | Shop law. Intake sheets are **behavior** only — do not restyle. |
| Sister LEARN TRACK PRs #19–#33 (`01`–`14`) | Headings + locks. This file is `15`. |
| Playbook APPLY list (PR #29) | Sell-test lock: **hex boxes, no names on storefront swatches**. |
| Slack `#shop-decisions` (`C0BV3GYC602`) | Five standing messages (2026-09-04). No watery-color-peek thread. |
| Linear | Keyword search returned onboarding `TIE-2` only — no PDP motion issue. |
| Granola meetings | MCP unauthorized — no meeting notes. |
| Notion | Keyword search returned the default Welcome page only. |
| Apple HIG (Materials / Motion / Color) | Official pages are JS apps; this pass used the Apple docs mirror plus WWDC25 transcripts and *Adopting Liquid Glass*. URLs in §17. |
| Apple iPhone 17 product pages | Marketing page lists five **named** finishes + Product viewer prev/next. Direct fetch of `apple.com/iphone-17/` timed out this pass; UK/US page extracts and Newsroom still used. Do not steal Apple finish **names**. |
| Public CSS / Motion / WCAG specs | Fetched 2026-09-09. URLs in §17. |

If a later crawl disagrees with a **live** cell here, **the new crawl wins** — update the date line. Shop law still wins over industry taste.

### 0.2 Sister docs

| # | File | Job vs this note |
| --- | --- | --- |
| 01 | `01-messenger-social-commerce.md` | Kelly Ying look lock; Message-first; no cart |
| 02 | `02-pdp-color-size-ux.md` | Color **nouns**; WCAG 1.4.1; gallery sync law |
| 03 | `03-tiny-boutique-admin.md` | Admin brains; do not mint from “Next mã” |
| 04 | `04-next-blob-catalog-arch.md` | ISR / Blob; `/m/A03` must 404 |
| 05 | `05-ai-product-media.md` | Recorded first-ten colors; `colorId` bind; no invented hex |
| 06 | `06-seo-trust-diaspora-boutique.md` | Soft-launch `noindex`; unique `/c/*` titles |
| 07 | `07-taobao-dropship-boutique.md` | Motion lock list; dropship-honest copy |
| 08 | `08-dropship-ops-runbook.md` | Staff clock; does not restyle |
| 09 | `09-bugcheck-sell-site-checklist.md` | Tick-box QA |
| 10 | `10-customer-pleasing-motion-ux.md` | General motion law + PDP hero VT / lightbox |
| 11 | `11-vercel-blob-admin-qa.md` | Admin / Blob gate; look stays |
| 12 | `12-fb-messenger-dropship-copy.md` | VN+EN phrase bank; no motion |
| 13 | `13-watery-tab-slide-motion.md` | **Home** Featured gold meniscus + grid pour |
| 14 | `14-complete-admin-feature-matrix.md` | Admin matrix; hex tag UI already exists |
| **15** | **This file** | **PDP watery color peek + carousel roll via `colorId`** |
| Kit | Playbook README + `AI_CLOTHING_SHOP_APPLY_TO_SELL_TEST.md` (PR #29) | Hex boxes on storefront; no names on shopper swatches |

`02` and `10` asked for **customer text-only** colors (WCAG + non-hue words like Hoa / Caro). **Live sell-test + playbook already shipped hex boxes** (`ColorSwatch`, admin copy “Boxes only — no names on the swatches”). This note **does not rewind that lock**. It makes the **boxes watery and honest**, adds a **non-color selected cue**, and **rolls the gallery by `colorId`**. It does **not** invent Vietnamese names from hex.

`13` already owns Featured `layoutId: "featured-tab"` + `filterSlide`. Do **not** retune the home grid in this APPLY. PDP gallery is a **second** roll.

---

## 1. Executive summary

Apple’s iPhone product pages do three things a boutique PDP should steal **as behavior**, not as chrome:

1. **Finish chips that look like the material** — a small, glossy, slightly see-through disc you can *read as enamel*, with a ring when selected ([iPhone 17](https://www.apple.com/iphone-17/) / [UK](https://www.apple.com/uk/iphone-17/): named finishes + Product viewer).
2. **A product viewer that peeks the next frame** — “Previous / Next feature item in Product viewer” so the buyer knows there is more without a mystery hamburger.
3. **Color change = the object rolls**, not a hard cut. The same piece, next finish.

Sassy Closet’s sell-test already has the **data sockets** for that, and they are **not wired through**:

| Hook (live 2026-09-09, chunk `1xr62vxitay1m.js`) | Live fact | Gap |
| --- | --- | --- |
| `ColorSwatch` | `h-6 w-6 rounded-sm` opaque `background-color: hex`; `border-black/20`; selected `outline-2 outline-offset-2 outline-ink` | Flat paint chip. No glass, no photo peek, not circular, no meniscus. |
| `ProductGallery` | `useState(null)` color + `useState(0)` index; `imagesForColor(product, colorId)` | Filter **drops** untagged photos when a color is selected. |
| `imagesForColor` | `t === null ? all : images.filter(img => img.colorId === t)` | Sister `02`/`10` want tagged **OR** shared (`colorId == null`). Live drops shared. |
| Gallery motion | `AnimatePresence mode="wait"`; enter `x:24` / exit `x:-18` / `0.28s` ease `[.22,1,.36,1]` | Hard slide, **no peek**, ~280ms serial. No `scroll-snap`. |
| Dots | `h-1.5 w-1.5 rounded-full` only if `images.length > 1` | A01 has **one** image → no dots, no swipe track. |
| `aria-pressed` | SSR HTML: **both** A01 chips `aria-pressed="false"` | Selected state is client-only; crawlers / first paint lie. |
| `images[].colorId` | A01 / P04 / P05 covers are **`null`** | Color tap cannot honestly change pixels until admin tags. |

That is already a **hex chip + directional slide**. It is **not** yet watery, and it is **not** yet a color→gallery roll:

1. The chip is a **6×6 rectangle of paint**. Apple’s finish picker is a **tiny piece of the object** (glass / enamel / specular). Watery here means **the chip is a window**, not a CSS `background-color` brick.
2. The gallery is a **single `<img>`** that remounts. Fashion photography wants a **peeking track** (next photo visible at the edge) so the hand knows it can roll ([CSS Scroll Snap L1 “peek”](https://www.w3.org/TR/css-scroll-snap-1/); [Chrome, *Make accessible carousels*](https://developer.chrome.com/blog/accessible-carousel)).
3. `imagesForColor` **hides** shared covers the moment a `colorId` is selected. With every live `colorId: null`, a tap **cannot** change the hero — and if Origin later tags only *some* photos, shared flats/labels would **vanish**. That is a data bug, not a motion taste.
4. Color chips have **no names on storefront** (playbook lock). WCAG [1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) and Apple HIG *Inclusive color* still require a **non-color** cue: selected ring, `aria-pressed`, optional `sr-only` “Color 1 of 2”. **Do not invent “Kem” / “Navy” to “fix” 1.4.1.**
5. SVG goo, `feDisplacementMap`, and full-viewport Liquid Glass on the **garment** are **lies about cloth** (`13` §3). Glass belongs on **chips, sticky bar, selected ring** — the control layer. HIG: **don’t put Liquid Glass in the content layer** ([Materials](https://developer.apple.com/design/human-interface-guidelines/materials)).

Reliability still beats beauty. A chip that tints A01’s cover toward `#1C2A4A` without a tagged photo, a 700ms luxury wipe that hides P02 Hold, or a peek that shows **A02’s** cover beside A01, is a **failed** boutique.

---

## 2. Hard constraints (print these on the implementer’s wall)

1. **Never invent a mã.** Emit list is exactly `A01 S01 P01 P02 P03 P04 P05 K01 H01 A02`. Empty `/c/quan` stays empty. No `Q01` “so the carousel has a second slide.”
2. **Never invent qty, $, photos, hex, or color names.** Hold P02 / P05 = **Inbox for price**. Empty `colors[]` = **no chip row**. Do not CSS-circle a missing color (`02` §8.2; `05` §3.2; `10` §8).
3. **Never invent which photo is which color.** Tag only in `/admin`. Until `images[].colorId` is a stored id, the hero stays the cover. Do not hue-rotate the cover to “preview” a hex.
4. **Square Free = on-hand truth.** Official Excel is a working copy (`README.md`). This kit does not edit Excel or intake in this pass.
5. **Bots draft only.** No Square Save, no Facebook Post/Send (`#shop-decisions` 2026-09-04).
6. **No cart, Shop now, or bag-fly.** Kelly Ying’s **$10 / $300+** and `V###` codes are **theirs**.
7. **Customer storefront still has no color *names*.** Playbook: “Boxes only — no names on the swatches. Optional note is admin-only.” Hex + selected ring + `aria-label="Color #RRGGBB"` is the public contract. Admin `note` may become `title` **only if it is already saved** — do not write a note.
8. **Motion never changes identity.** Same mã in, same mã out. Gallery pixels after a color tap are **this mã**, `colorId === selected.id` **or** `colorId == null` (shared). Never another folder.
9. **Water never lies on the photo.** No `filter: url(#goo)` on `.shimmer`, covers, or heroes. No `feDisplacementMap` over garments. Distortion is a **fabric lie**.
10. **Origin owns the pixels.** APPLY is for the Origin agent on `sassy-closet-shop`. Intake Production stays https://sassy-closet.vercel.app. This PR does not edit `excel-kit/` or `sassy-closet/`.

---

## 3. What “Apple watery peek” means here (and what it is not)

### 3.1 Steal the iPhone *product page*, not the OS chrome

Apple in 2025–26 uses **Liquid Glass** as a **functional layer** for controls and navigation: translucent, tinted by what sits behind it, morphing like a droplet ([Newsroom, 2025-06](https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/); [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass); WWDC25 *Meet Liquid Glass* session 219). HIG Materials:

- Liquid Glass **floats above content**. **Don’t use it in the content layer.**
- Use it **sparingly**, on the **most important functional elements**.
- **Clear** glass only over **visually rich media**; **regular** glass when text must stay legible.
- Clear glass over a bright photo may need a **~35% dark dim**.
- Reduce Transparency / Increase Contrast / Reduce Motion **must** change the effect (frostier, higher contrast, less elastic).

The **iPhone marketing page** is a different object: a **finish row** (Lavender / Sage / Mist Blue / White / Black on iPhone 17) plus a **Product viewer** with previous/next. The chips are **little windows onto the finish**. The viewer **peeks** adjacent frames. That is the steal.

**Refuse** on sell-test:

| Refuse | Why |
| --- | --- |
| Full-viewport Liquid Glass, chromatic aberration on covers | Frosts the garment; fights `--paper` / `--ink` (`13` §3.1) |
| Apple finish **names** (Lavender, Sage, …) or Kelly Ying `V984` | Stock copy / their SKU |
| Cursor-follow blobs, WebGL cloth, 3D iPhone mockups | `10` anti-pattern; not a boutique photo |
| Fat iOS capsules / `rounded-full` **pills** under 11px labels | `13` gold hairline lock |
| Auto-advancing carousel | App Store Connect Reduced Motion: auto-advance is a trigger ([criteria](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria/)) |

**Watery *for this closet*** is three physical metaphors, all gold-on-paper, **on the PDP**:

| Metaphor | Buyer should feel | Fail if… |
| --- | --- | --- |
| **Enamel window** | The color chip is a **see-through tile** of the recorded hex (and, if tagged, a **tiny crop of that color’s photo**) | Opaque 6×6 brick, or a guessed hue on an untagged mã |
| **Meniscus ring** | Selected chip grows a **gold/ink ring** that stretches like `featured-tab`, then sits flush | Outline that only appears on hover; no `aria-pressed` |
| **Peek + roll** | Next photo is **visible at the edge**; changing color **rolls** the track to the first image with that `colorId` | Hard cut; mixed gallery; another mã’s cover in the peek |

Apple HIG Motion: do not make people **wait** for frequent motion; Reduce Motion replaces large spatial moves with a **crossfade or instant** ([HIG Motion](https://developer.apple.com/design/human-interface-guidelines/motion); [Reduced Motion criteria](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria/)). Color tapping is frequent. Watery is **short viscosity**, not a show. WWDC25: Reduce Motion **decreases intensity and disables elastic properties** of Liquid Glass — map that to **no spring overshoot on the chip**, no goo.

### 3.2 Playbook hex vs LEARN `02` text-only

This is an explicit **lock collision**. Resolve it in Origin’s favor **as live + playbook**, not by inventing names:

| Layer | Color UI | This APPLY |
| --- | --- | --- |
| Intake (`sassy-closet.vercel.app`) | Vietnamese **text** pills (`COLORS[].vi`) | **Untouched** |
| LEARN `02` / `10` | Customer **text-only** (Hoa, Caro, Ánh kim cannot be hex) | Still true for **pattern words**. If a future row stores a non-hue **word**, do **not** paint a guessed circle. |
| Sell-test live + playbook PR #29 | **Hex boxes**, no names on shopper swatches; admin note admin-only | **Keep.** Make boxes watery. |
| This file | Apple peek **behavior** on those boxes | Glass + ring + gallery roll via `colorId` |

WCAG [1.4.1 Use of Color (A)](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html): color must not be the **only** visual means. Sufficient technique **G14** is text. Apple HIG Color: “Avoid relying solely on color… use text labels or glyph shapes.” Origin satisfies this **without names** by:

1. **Selected ring** (shape) + `outline-ink` / gold hairline.
2. **`aria-pressed="true"`** on the selected chip (live SSR currently lies — both `false`).
3. **`aria-label="Color #F4F0E8"`** (already) plus **`sr-only`** `Selected · 1 of 2` (index, not a name).
4. Gallery change is a **second** cue (the photo). If there is no tagged photo, **do not fake the second cue**.

HIG Color also: **don’t use the same color to mean different things**; **apply color sparingly to glass** (tint the **selected** chip, not every chip). Light hex keeps a **border on paper** (playbook E).

### 3.3 NN/G jobs, mapped onto color + gallery

| NN/G job | Watery meaning | Fail if… |
| --- | --- | --- |
| Feedback | Ring starts moving within **0.1s** of tap ([NN/G animation usability](https://www.nngroup.com/articles/animation-usability/)) | Click, then 300ms of nothing |
| State change | `aria-pressed` + gallery set change; motion is extra | Animation is the only cue (fails 1.4.1) |
| Spatial metaphor | Later color in the row → gallery rolls **forward**; earlier color rolls **back** | Random direction; wait-mode blank page |
| Signifier | Peek of the next photo = “there is more”; chip is tappable on phone | Watery only on `@media (hover:hover)` |
| Attention | One moving ring + one rolling track | Goo + shimmer + stagger + VT all at once (Hipmunk pile-on — NN/G) |

NN/G PDP must-haves still include **recognizable images + enlarge** ([*UX Guidelines for Ecommerce Product Pages*](https://www.nngroup.com/articles/ecommerce-product-pages/)). This APPLY does not replace `10`’s lightbox fix. It **does** require that whatever lightbox exists **filters to the current `colorId` set**.

---

## 4. Apple sources (HIG + product pages + WWDC)

### 4.1 Materials — glass is a *layer*, not a filter on cloth

Quoted / paraphrased from HIG Materials (Apple Developer; this pass read via the docs mirror) and *Adopting Liquid Glass*:

- A material lets **color pass through** so people keep a sense of place.
- Liquid Glass is for **controls and navigation** that **float above** content. Content (the garment) stays in the **content layer** with **standard** materials.
- **Exception:** a transient control *in* the content layer (slider / toggle) may take on glass **when activated**. A color chip is exactly that class of control: small, interactive, over paper or over a thumbnail.
- **Clear** glass: highly translucent, for components **over photos/video**. **Regular**: blurs and adjusts luminosity so **text stays readable**.
- Overuse “provides a subpar user experience by distracting from that content.”
- Test Reduce Transparency, Increase Contrast, Reduce Motion. Custom glass **must** be tested; system components adapt automatically.

**Origin mapping:** watery glass on **`ColorSwatch` + selected ring + optional peek-edge veil**. **Not** on `.shimmer`, hero `<img>`, or Message CTA. Sticky bar already uses `bg-paper/95 backdrop-blur-md` — keep; that **is** a control layer over the page (HIG-legal). Do not add a second full-width glass sheet.

### 4.2 Color — tint glass like stained glass, not a rainbow toolbar

HIG Color + Liquid Glass color:

- Glass has **no inherent color**; it takes color from **what is behind it**.
- You **may** tint some glass (stained glass) to emphasize a **primary** control. System does this for prominent buttons.
- **Apply color sparingly.** Do not tint every control.
- Inclusive color: **never color alone**.
- Even a single-appearance shop should consider light/dark variants if glass must adapt; sell-test is **paper/ink only** — do not invent a Dark Mode. Just keep **Increase Contrast**: thicker ring, more opaque fill.

WWDC25 *Build a UIKit app with the new design* (284): glass elements can **merge like water droplets** when they overlap; prefer animating the **effect** (materialize / dematerialize) over fading `alpha`. **Origin:** if two chips are adjacent, **do not** goo-merge them into one blob (that would look like a dual-color lie). Keep a **2px paper gutter**. Optional: selected chip **materializes** a ring (`layoutId`) rather than popping `outline`.

### 4.3 Motion — frequent taps stay short; Reduce Motion is a dissolve

HIG Motion:

- Add motion **purposefully**. Gratuitous animation distracts or makes people unwell.
- **Make motion optional.** Never the only channel.
- Feedback should **follow the gesture** (slide down → dismiss down, not sideways). Color row is **horizontal** → gallery roll is **horizontal**.
- **Aim for brevity.** Avoid extra motion on **frequent** UI.
- **Let people cancel** — do not block Message until the tween ends (`10` already).
- Avoid **sustained oscillation ~0.2 Hz**. One overshoot max (`13` / WWDC23).

App Store Connect Reduced Motion evaluation:

- Depth simulation (**parallax, animated blur, depth-of-field**) should **disable or change** when Reduce Motion is on.
- Auto-advancing carousels should **stop**.
- Decorative motion: **off**. Meaningful motion (state change): replace with **dissolve / highlight fade / color shift**, not a void.

WCAG [2.3.3 Animation from Interactions (AAA)](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html): interaction-triggered motion can be disabled unless essential. `prefers-reduced-motion` is the sufficient technique (C39). Vestibular risk is **nausea / migraine**. Origin: Reduce Motion → **instant chip**, **instant gallery** (opacity crossfade ≤150ms or duration 0), **no peek parallax**, **no animated blur** on photos.

### 4.4 iPhone product page — named finishes we will **not** copy

Live extracts (2026-09-09):

- [iPhone 17](https://www.apple.com/iphone-17/) / [UK](https://www.apple.com/uk/iphone-17/): finishes **Lavender, Sage, Mist Blue, White, Black**; copy “Choose from five gorgeous finishes”; Product viewer **Previous / Next feature item**.
- [Newsroom, 2025-09](https://www.apple.com/uk/newsroom/2025/09/apple-introduces-iphone-17/): same five colours, storage SKUs. **Not our catalog.**

**Steal:** chip row + viewer peek + color drives the viewer.  
**Do not steal:** the words Lavender/Sage/…, the 3D WebGL phone, Buy/cart, storage picker, `$829`.

If Origin needs a visual reference, **open those URLs** — do not screenshot Apple assets into `/public`.

---

## 5. CSS + Motion technique catalog (use / refuse)

| Technique | Source | Use on sell-test PDP? |
| --- | --- | --- |
| `backdrop-filter: blur()` | [MDN `backdrop-filter`](https://developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter); Filter Effects L2 | **Chip glass rim** + keep sticky `backdrop-blur-md`. Needs a **semi-transparent** background or the blur is invisible. **Backdrop root trap:** parent `opacity < 1`, `filter`, `mask`, `clip-path`, or another `backdrop-filter` **clips** the blur to that ancestor — do not wrap the chip row in `opacity: 0.9`. |
| `filter: blur()` on the **element** | [MDN `filter`](https://developer.mozilla.org/en-US/docs/Web/CSS/filter) | **Peek neighbors only** (slides not snapped). **Never** on the active garment. Reduce Motion / Reduce Transparency → `filter: none`. |
| `mask-image` / `mask-image: linear-gradient(...)` | [MDN `mask-image`](https://developer.mozilla.org/en-US/docs/Web/CSS/mask-image); CSS Masking L1 | **Track edges** (fade peek into paper). **Chip specular**: `radial-gradient(circle at 30% 25%, #fff, transparent 55%)` as a **highlight layer**, not a mask that eats the hex. CORS: mask URLs must be HTTP(S), not `file://`. |
| `scroll-snap-type: x mandatory` + `scroll-snap-align` | [MDN `scroll-snap-type`](https://developer.mozilla.org/en-US/docs/Web/CSS/scroll-snap-type); [CSS Scroll Snap L1](https://www.w3.org/TR/css-scroll-snap-1/) | **Preferred gallery.** L1 explicitly allows a **peek** of the previous page so people know they are not at the start. |
| `scroll-padding-inline` | [MDN `scroll-padding`](https://developer.mozilla.org/en-US/docs/Web/CSS/scroll-padding) | **Required** with container padding so snap points account for the peek inset. |
| Peek layout | Slide `flex: 0 0 ~88–92%`; gap 8–12px; padding-inline = peek | Adjacent photo **visible**. Not 100% slides. |
| Chrome accessible carousel | [Chrome, 2025-09-29](https://developer.chrome.com/blog/accessible-carousel) | `role="region"` + `aria-label` + `aria-live="polite"` on the gallery. Peek is an expected single-item pattern. `::scroll-marker` / `interactivity: inert` are **Chrome 135+** — **progressive**; do not require them. Fallback: only the active slide’s img is in tab order. |
| Motion `layout` / `layoutId` | [Motion layout animations](https://motion.dev/docs/react-layout-animations) | **Selected ring** `layoutId="pdp-color-ring"` (undefined when reduced). Keep `springSoft`. Do not share `featured-tab`. |
| `AnimatePresence` | [Motion AnimatePresence](https://www.framer.com/motion/animate-presence/) (also [motion.dev](https://motion.dev/docs/react-animate-presence)) | Live already `mode="wait"` on the **hero swap**. Prefer **native snap** for swipe; keep Presence for **color-driven** roll if the track remounts. Prefer `mode="sync"` / overlapping so the gallery **never blanks**. `custom={direction}` for roll direction. Unique `key` = `src` or `colorId-src`. |
| `clip-path: inset()` wipe | [MDN `clip-path`](https://developer.mozilla.org/en-US/docs/Web/CSS/clip-path); `13` FIX 3 | **Optional** if Origin **keeps** a remounting hero instead of a snap track. Same budget as `13`: perceived **≤200ms**. |
| SVG goo (Bebber) | `13` §3.3 | **Not this APPLY** on chips (too close to photos). Featured hairline only, per `13`. |
| CSS `shape()` liquid ooze | CSS Tip 2026-04-02 (`13`) | **Refuse** as a veil. |
| View Transitions `product-{MA}` | `10` FIX 3 | Home → PDP only. **Do not** VT the color filter. Color is same-document Framer/snap. |
| `prefers-reduced-transparency` | [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-transparency) (experimental) | **Progressive:** if `reduce`, chip fill `opacity: 1`, `backdrop-filter: none`. Safari/iOS Reduce Transparency is the real user setting. |
| WebGL / Three.js phone | vendor mockups | **Refuse.** |

---

## 6. As-built hook map (cite the live host)

Crawl: 2026-09-09. HTML on `/m/{MA}`. CSS `34vl_zddoo4ws.css`. PDP JS `1xr62vxitay1m.js`. Shared helpers also inlined in home chunk `3_93acjqq2t4q.js` (`ColorSwatch`, `coverSrcForColor`, `imagesForColor`).

### 6.1 CSS tokens (do not rename)

Same `:root` as `13` §4.1 — **do not retune for this pass:**

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

Fonts: Be Vietnam Pro (`font-sans`) + Cormorant Garamond (`font-display`). Keep `announce-fade` / `shimmer-slide` / `cta-flash` / `tab-scroll` / view-transition header rules from `13`. `--duration-move:.4s` is **not** the color-tap clock.

### 6.2 `ColorSwatch` (live)

Reconstructed from chunk `1xr62vxitay1m.js` / `3_93acjqq2t4q.js` module `9040`:

```js
function sizeClass(size) {
  switch (size) {
    case "sm": return "h-4 w-4";
    case "md": return "h-6 w-6";
    case "lg": return "h-8 w-8";
    default: return size; // exhaustive fallback: treat unknown as class string
  }
}

// ColorSwatch({ hex, selected = false, onClick, size = "md", title })
<button
  type="button"
  aria-label={title ?? `Color ${hex}`}
  aria-pressed={selected}
  title={title ?? hex}
  onClick={onClick}
  className={`${sizeClass(size)} shrink-0 rounded-sm border border-black/20 ${
    selected ? "outline outline-2 outline-offset-2 outline-ink" : ""
  }`}
  style={{ backgroundColor: hex }}
/>
```

`ColorSwatchEmpty` exists (`aria-label="No color"`, dashed, 45° mute rule) — **admin untagged control**, not a customer “invent a color” chip. Do not show Empty on the PDP to “complete a row of five.”

**Keep:** `rounded-sm` **boxes** (playbook). Do **not** switch to iOS `rounded-full` capsules. Watery is **inside** the box. Optional: `rounded-[3px]` max — not a circle unless Boss yes.

### 6.3 `imagesForColor` / `coverSrcForColor` (live — bug)

```js
function imagesForColor(product, colorId) {
  const n = product.images.filter((img) => img.src.trim());
  return colorId === null ? n : n.filter((img) => img.colorId === colorId);
}

function coverSrc(product) {
  return product.images.find((img) => img.src.trim())?.src;
}

function coverSrcForColor(product, colorId) {
  const n = imagesForColor(product, colorId);
  return n[0] ? n[0].src : coverSrc(product);
}
```

**Law for APPLY** (sisters `02` §8 / `05` §7 / `10` §8 — live **violates** this):

```
view(ma, colorId) =
  images of THIS mã where src is non-empty AND
    (colorId is null  → all)
    (colorId is set   → colorId === selected  OR  colorId == null)
  never another mã’s folder
  never a CSS-tinted stand-in
```

When a color is selected and **no** image has that id, **keep the shared cover visible** (coverSrc fallback already does this in `ProductGallery` via `g = f[x]?.src ?? h`). After the filter is fixed to **include** shared, selecting a color with no tagged shots still shows shared — **honest**. Tagging is how the roll **gains** extra slides, not how the cover **disappears**.

### 6.4 `ProductGallery` (live)

Reconstructed from `1xr62vxitay1m.js`:

```js
function ProductGallery({ product }) {
  const reduced = useReducedMotion();
  const [colorId, setColorId] = useState(null);
  const [index, setIndex] = useState(0);
  const images = imagesForColor(product, colorId);
  const cover = coverSrc(product);
  const idx = images.length === 0 ? 0 : Math.min(index, images.length - 1);
  const src = images[idx]?.src ?? cover;

  return (
    <>
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
                alt={displayTitle(product)}
                className={`aspect-[3/4] w-full object-cover ${images.length > 1 ? "cursor-pointer" : ""}`}
                onClick={() => {
                  if (images.length > 1) setIndex((i) => (i + 1) % images.length);
                }}
              />
            ) : (
              <div className="aspect-[3/4] bg-blush" />
            )}
          </motion.div>
        </AnimatePresence>
        {images.length > 1 ? (
          <div className="absolute inset-x-0 bottom-3 z-[2] flex justify-center gap-1.5">
            {images.map((img, n) => (
              <button
                type="button"
                aria-label={`Image ${n + 1}`}
                onClick={() => setIndex(n)}
                className={`h-1.5 w-1.5 rounded-full ${n === idx ? "bg-paper" : "bg-paper/40"}`}
              />
            ))}
          </div>
        ) : null}
      </div>
      {product.colors.length > 0 ? (
        <div className="mt-4 flex flex-wrap items-center gap-2">
          {product.colors.map((c) => (
            <ColorSwatch
              key={c.id}
              hex={c.hex}
              selected={colorId === c.id}
              size="md"
              onClick={() => {
                setColorId((cur) => (cur === c.id ? null : c.id));
                setIndex(0);
              }}
            />
          ))}
        </div>
      ) : null}
    </>
  );
}
```

**Keep the names** `ProductGallery`, `ColorSwatch`, `imagesForColor`, `coverSrcForColor`. Keep toggle-off (`same id → null`) so buyers can return to the unfiltered set. Keep `useReducedMotion()`. Keep aspect `[3/4]`.

**Gaps vs Apple peek / roll:**

| Gap | Live | APPLY |
| --- | --- | --- |
| Peek | Single full-bleed img; overflow hidden | Snap track, ~90% slide, neighbor visible |
| Direction | Always enter from `x:24` (right), never uses color **index** | Direction = `index(nextColor) >= index(current) ? 1 : -1` like Featured `b()` |
| `mode="wait"` | Serial ~280ms | Overlap or native scroll; perceived ≤200ms (`10` / `13`) |
| `scroll-snap` | **0** matches in A01 HTML | Add |
| `mask-image` | **0** | Optional edge fade |
| VT on hero | **Missing** `product-A01` on A01 hero (`10`) | Still `10`’s job; do not regress |
| Lightbox | Click cycles index if `length > 1`; no dialog | `10` lightbox; this pass may keep click-to-advance **and** swipe |
| Related rail | A01 page VT name is **`product-A02`** (neighbor tile) | Do not put A01’s ring on A02 |

### 6.5 Sticky Message bar (already watery-legal)

`/m/A01` mobile:

```
fixed inset-x-0 bottom-0 z-40 md:hidden
  border-t-2 border-gold/45 bg-paper/95
  shadow-[0_-18px_44px_-16px_rgba(17,17,17,0.38)]
  backdrop-blur-md
  padding-bottom: max(0.9rem, env(safe-area-inset-bottom))
```

CTA: `cta-shine` ink pill, `aria-label="Message A01 on Messenger"`, href `https://www.facebook.com/profile.php?id=61594312648057`. **Keep.** Do not glass this into an iOS tab bar. Do not put color chips **inside** the sticky bar (too easy to mis-tap Message).

### 6.6 Recorded first-ten colors (do not add rows)

Crawled JSON, 2026-09-09. **These ids/hexes are stored. Do not invent more. Do not name them.**

| Mã | Status / $ | `colors[]` | `images[]` |
| --- | --- | --- | --- |
| A01 | Available · $25 | `cb3d45c1231ab` `#F4F0E8`; `c4b0be6de43a3` `#1C2A4A` | `/products/A01/cover.jpg` `colorId: null` |
| S01 | Available · $28 | `[]` | cover `null` |
| P01 | Available · $5 | `[]` | cover `null` |
| P02 | **Hold · Inbox for price** | `[]` | cover `null` |
| P03 | Available · $18 | `[]` | cover `null` |
| P04 | Available · $13 | `c27b990776c31` `#F4F0E8` | cover `null` |
| P05 | **Hold · Inbox for price** | `cf8dbca819819` `#E8D5C4`; `cee9b65b6a45b` `#8B3A3A`; `cffd8b024e8d1` `#1C2A4A` | cover `null` |
| K01 | Available · $37 | `[]` | cover `null` |
| H01 | Available · $8 | `[]` | cover `null` |
| A02 | Available · $22 | `[]` | cover `null` |

SSR on `/m/A01`: both chips `aria-pressed="false"`. Related-rail on `/m/P04` shows **other mãs’** `h-4` chips (P05’s three, etc.) via `ProductGrid` — that is **not** P04 growing extra colors. Do not copy related-rail hexes onto P04’s PDP row.

Empty `colors[]` (S01, P01, P02, P03, K01, H01, A02): **no chip row**. Do not backfill from `05`’s recorded table until admin Save on **that** row.

### 6.7 Admin (already has tag UI)

`/admin` copy, live: **“Boxes only — no names on the swatches. Optional note is admin-only.”** **Add hex** · **Add a color above to tag this image.** Per-row **Save {mã}**. Catalog count **10**. Next-mã tiles include A03 / Q01 / … — **do not use them** (`14`, playbook A).

APPLY **data** job (not this kit): on Preview, **tag** real photos to existing ids **only when the photo is of that finish**. If A01’s cover is the only file, leave `colorId: null` (shared). Do not duplicate the JPEG to fake a second color.

---

## 7. colorId roll — the only honest gallery change

### 7.1 State machine

```
selectedColorId = null | colors[i].id     // never a made-up string
index            = 0 … view.length-1

on color chip activate (same id → toggle null):
  direction = index(next) >= index(prev) ? 1 : -1   // 0 if toggle off
  selectedColorId = next
  view = imagesForColor(product, selectedColorId)      // FIXED helper
  index = first index in view whose colorId === selected
          else 0
  ROLL the track to that slide (scrollTo / scrollIntoView)
  ring layoutId moves

on swipe / snap / dot / hero click:
  index changes inside current view only
  does not change selectedColorId unless the snapped slide
  has a non-null colorId different from selected — optional
  (default: swipe does NOT steal the chip; color is an explicit tap)

on size change (if/when sizes exist):
  gallery does not change unless a photo is tagged to that size
  (02 / 10: photos are color-keyed)
```

### 7.2 What “roll” looks like

**Preferred (Apple viewer):** the track is **already** a row of this mã’s view. Color tap = **`element.scrollTo({ left, behavior })`** with `scroll-behavior: smooth` when motion is on, `auto` when reduced. Neighbor peeks stay. No remount.

**Fallback (keep `AnimatePresence`):** keep `filterSlide`-class motion but **drive `x` by `direction`**, overlap enter/exit, **≤200ms**. Do not keep `mode="wait"` at 0.28s.

**Forbidden:** `filter: hue-rotate()` / `brightness()` toward the hex. That **invents** a garment.

### 7.3 PLP cards (`ProductGrid`)

Live already: `useState(null)` + `coverSrcForColor` + `ColorSwatch size="sm"` under the tile; hover still `scale-[1.08]` (`10` wants this **off** under Reduce Motion). APPLY: **same watery chip recipe at `sm`**, same `imagesForColor` fix. Tapping a chip **must not** navigate; it only swaps the card cover (`onClick` already stops on the button). Do not add a peeking carousel on the grid (too noisy; Hipmunk). One photo + chips is enough on PLP.

---

## 8. Color chip recipe (enamel window)

Layers, back → front, **inside** the existing `h-6 w-6` (`md`) / `h-4 w-4` (`sm`) box:

1. **Photo peek (only if** this `color.id` has a tagged image):** `background-image: url(tagged.src)` `background-size: cover`; `background-position: center`. This is the Apple “window onto the finish.” If none tagged, **skip this layer** (do not use another mã, do not use the untagged cover as if it were this color).
2. **Hex glaze:** `linear-gradient(180deg, color-mix(in srgb, var(--hex) 72%, white), var(--hex))` at **opacity ~0.78** if a photo peek exists, **opacity 1** if not. `color-mix` is the watery see-through. Unsupported browsers: solid `background-color: hex` (already live).
3. **Speculum:** `::after` `inset-0` `background: radial-gradient(120% 80% at 30% 20%, rgba(255,255,255,.55), transparent 55%)`; `pointer-events: none`; `mix-blend-mode: soft-light`. Reduce Transparency → hide.
4. **Glass rim:** `box-shadow: inset 0 1px 0 rgba(255,255,255,.55), inset 0 -1px 0 rgba(17,17,17,.12)` + `border-black/20`. Light hex (`relative luminance` high — `#F4F0E8` **is** light): keep/strengthen the border (playbook). Dark hex (`#1C2A4A`): border can stay; ring is the selected cue.
5. **Selected meniscus:** `motion.span layoutId={!reduced && "pdp-color-ring"}` `absolute -inset-1` `border border-gold` **or** keep `outline-ink` and add a **gold** hairline (`h-px` language). One ring. Spring = `springSoft`. Scale 1 → 1.06 → 1 while travelling (one overshoot).
6. **Hit target:** visual 24×24 (`md`) is small for thumbs. Expand the **button** with `p-1` / `::before` 44×44 invisible hitbox ([Apple HIG hit targets](https://developer.apple.com/design/human-interface-guidelines/buttons) — 44pt). Do not grow the **visible** enamel to 44px (would look like a kids’ craft).

`backdrop-filter: blur(6px)` on the glaze **only** when layer 1 (photo) exists and the glaze is translucent. If the parent is a backdrop root, skip blur rather than inventing a broken frost.

**Reduce Motion:** no scale, no spring; ring **jumps**.  
**Reduce Transparency:** glaze opacity 1, no blur, no speculum.  
**Forced colors / `prefers-contrast: more`:** 2px `outline-ink`, drop soft-light.

---

## 9. Gallery peek + roll recipe

### 9.1 Track

```css
.pdp-peek {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  overscroll-behavior-x: contain;
  scroll-snap-type: x mandatory;
  scroll-padding-inline: 8%;
  padding-inline: 8%;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
}
.pdp-peek::-webkit-scrollbar { display: none; }
.pdp-peek-slide {
  flex: 0 0 86%;
  scroll-snap-align: center;
  aspect-ratio: 3 / 4;
  object-fit: cover;
}
@media (prefers-reduced-motion: reduce) {
  .pdp-peek { scroll-behavior: auto; }
  .pdp-peek-slide { filter: none; }
}
```

Optional watery edge (not on the photo bytes — on the **track**):

```css
.pdp-peek {
  mask-image: linear-gradient(
    90deg,
    transparent 0,
    #000 8%,
    #000 92%,
    transparent 100%
  );
}
```

Neighbors **may** `filter: blur(0.4px) saturate(0.92)` **only** when they are not the snapped slide. App Store Connect lists **animated blur** as a Reduce Motion trigger — so this neighbor blur is **static** (no animation) and **off** when reduced. If it reads as a fabric lie in QA, **delete it**; peek width alone is enough.

### 9.2 A11y (Chrome carousel + APG)

- Wrapper: `role="region"` `aria-label="Photos {MA}"` `aria-live="polite"` (polite = color/snap changes announce without yelling).
- Each slide img `alt` stays `displayTitle` (`A01. TOP`) — do not invent “front, navy.” If later admin stores a real caption, use that.
- Dots: keep `aria-label="Image {n}"`; selected `aria-current="true"`.
- Keyboard: Left/Right when focus is in the region (do not steal page Up/Down). Home/End first/last.
- Do not `touch-action: none` the whole PDP (`10` / Baymard pinch).
- **No autoplay.**

Chrome Overflow 5 (`::scroll-marker`, `interactivity: inert`) is **nice** on Chromium 135+. Safari/Firefox: snap track + dots + buttons is enough. Do not ship a carousel that **only** works with `::scroll-button`.

### 9.3 Color → `scrollTo`

On color tap, after `view` is computed:

```js
const i = Math.max(0, view.findIndex((img) => img.colorId === selectedId));
track.scrollTo({
  left: slides[i].offsetLeft - track.clientWidth * 0.07,
  behavior: reduced ? "auto" : "smooth",
});
```

If Origin keeps AnimatePresence instead of a track, pass `custom={direction}` and variants `x: 28 * direction` enter / `-22 * direction` exit, ease `[.22, 1, .36, 1]`, **sum ≤200ms**, prefer `mode="sync"` with `position: absolute` overlap so paper never flashes.

### 9.4 Empty / single image

A01 today: **one** cover, two chips, both untagged. Correct UX:

- Track has **one** slide (the cover). **No fake peek** of a duplicated cover (that looks like two pieces).
- Chips still select (ring + `aria-pressed`).
- Gallery **does not** animate a fake second JPEG.
- Copy stays the live sentence: “Message A01 for real photos and size.” / “Áo độc bản — một chiếc đang có.” **No stock “swipe to see more colors.”**

When admin later tags a second file to `c4b0be6de43a3`, the track **gains** a slide and peek **appears** because `length > 1`. Until then, honesty > theater.

---

## 10. Rolling tab/slide on the PDP (vs LEARN 13)

| Surface | Owner | Motion |
| --- | --- | --- |
| Featured chips on `/` | `13` | Gold `h-px` `layoutId="featured-tab"` + grid pour |
| PDP color chips | **This file** | Gold/ink **ring** `layoutId="pdp-color-ring"` |
| PDP photos | **This file** | Peek track + color `scrollTo` (or directional Presence) |
| Home → PDP hero | `10` | `view-transition-name: product-{THIS mã}` |

Do **not** reuse `layoutId="featured-tab"` on a color chip (Motion will FLIP the home hairline into the PDP — a bug). Do **not** run `filterSlide` on `AnimatedProductGrid` from a PDP color tap.

If Origin wants one shared spring, **keep `springSoft`** `{ stiffness: 420, damping: 32, mass: 0.72 }` as the boutique viscosity token (`13`).

---

## 11. Accessibility (non-negotiable)

| Rule | Source | Origin |
| --- | --- | --- |
| Color not the only cue | WCAG 1.4.1; HIG Inclusive color | Ring + pressed + sr-only index; **no invented names** |
| Motion off | WCAG 2.3.3; HIG Motion; C39 | `useReducedMotion` already; extend to snap `behavior: auto`, no neighbor blur, no spring |
| Transparency off | HIG Materials; `prefers-reduced-transparency` | Solid hex, no backdrop-filter on chips |
| No autoplay | App Store Connect RM | No timer |
| Name, Role, Value | WCAG 4.1.2 | `aria-pressed` must match selection **on first paint** (fix SSR false/false) |
| Hit target | HIG Buttons | 44px hit, 24px enamel |
| Contrast of ring vs paper | WCAG 1.4.11 (UI components, 3:1) | `outline-ink` `#111` on `--paper` passes; gold `#b08968` on white is **soft** — use gold as **inner** hairline, ink as the 3:1 ring |
| Sticky bar | Live `backdrop-blur-md` | Keep safe-area; don’t trap focus |

Pattern words (if they ever appear on sell-test): **no hex**. That remains `02`. Current live ids are **hex-only**.

---

## 12. APPLY checklist (Origin, sell-test only)

Do these on https://sassy-closet-shop.vercel.app / the Origin shop **feature branch**. Check each box only when the live Preview proves it.

### A. Data honesty (`colorId`)

- [ ] `imagesForColor` includes **shared** (`colorId == null`) when a color is selected.
- [ ] Never reads another mã’s `/products/{OTHER}/`.
- [ ] Empty `colors[]` → no chip row (S01, P01, P02, P03, K01, H01, A02 this crawl).
- [ ] A01 chips stay the two stored ids. P04 one id. P05 three ids. No fourth chip.
- [ ] Admin tag + Save is the only way a cover gains a `colorId`. No auto-tag from hex distance.

### B. Watery chips (look lock)

- [ ] Still **boxes** (`rounded-sm`), not iOS capsules.
- [ ] Light hex (`#F4F0E8`, `#E8D5C4`) keep a visible border on paper.
- [ ] Selected = ink ring + optional gold hairline `layoutId="pdp-color-ring"` (off when reduced).
- [ ] `aria-pressed` true on the selected chip **in HTML after hydrate and on SSR if selected is default**. Default selected may stay **none** (`null`) — then all `false` is OK; today’s bug is **cannot** become true in SSR because selection is client-only. Fine. After tap, pressed must flip.
- [ ] No color **names** on shopper UI. No “Kem” / “Navy” / “Lavender”.
- [ ] No goo / displacement on chips or photos.

### C. Peek carousel

- [ ] When `view.length > 1`: snap track, neighbor peek, dots, Left/Right.
- [ ] When `view.length === 1`: one photo, **no cloned peek**.
- [ ] Color tap rolls to the first tagged slide for that id (or stays on shared cover).
- [ ] Perceived motion ≤200ms; Reduce Motion instant.
- [ ] `aria-label="Photos A01"` (mã from the page, allowlist only).

### D. Kelly Ying + Message-first

- [ ] Cormorant / Be Vietnam / paper / ink / gold / blush unchanged.
- [ ] Message {MA} still opens `facebook.com/profile.php?id=61594312648057`.
- [ ] P02 / P05 still **Hold · Inbox for price** (no `$`).
- [ ] No cart, no Shop now, no Apple Buy.
- [ ] Sticky `backdrop-blur-md` bar still Message, not a color dock.

### E. Out of scope (reject)

- Intake, Excel, Square Save, FB Send.
- Featured grid pour (`13`) unless already shipped — do not regress.
- Invented mã A03 / Q01 / D01.
- Stock copy, US sizes, fake reviews.

---

## 13. Anti-patterns (failed boutique)

1. Tinting `/products/A01/cover.jpg` toward `#1C2A4A` because the navy chip was tapped and `colorId` is still `null`.
2. Peeking **A02** beside A01 (related-rail leak / wrong `view-transition-name`).
3. Cloning the same cover twice so the track “has a peek.”
4. Naming chips Kem / Ivory / Navy from the hex.
5. `rounded-full` 44px iOS settings discs on a Cormorant page.
6. `filter: url(#goo)` on the hero.
7. Autoplay.
8. `mode="wait"` 280ms white flash on every color tap.
9. Putting Liquid Glass on the **garment**.
10. Writing “Free shipping on $300+” or Kelly Ying `V984`.

---

## 14. Verify (Origin clicks these; do not skip)

Desktop + phone + OS Reduce Motion + (if available) Reduce Transparency + keyboard:

1. `/m/A01` — two boxes `#F4F0E8` / `#1C2A4A`. Tap each: ring moves; Message A01 still Facebook Page `61594312648057`; $25 Available. **Until tagged:** hero stays `cover.jpg` (honest). After a real tag on Preview: gallery **rolls** to that file only.
2. `/m/P05` — three boxes; Hold · Inbox for price; **no** dollar on card or sticky.
3. `/m/P04` — one PDP box `#F4F0E8`. Related rail may show **other** mãs’ chips; those taps must not rewrite **P04’s** gallery.
4. `/m/S01` `/m/P02` — **no** chip row. P02 Hold.
5. `/` — A01 card `sm` chips if `colors.length > 0`; grid still 10; All/Tops counts unchanged. Featured hairline still `13`’s job.
6. `/m/A03` — not found. No new SKU in network.
7. Reduce Motion: no ring stretch, no peek blur, no 1.08 zoom, Message still works.
8. View-source / network: no `e.tb.cn`, no `¥`, no `A03`, no `V984`, no Apple asset hotlink.

---

## 15. Fixtures (never invent mã)

Allowlist: **A01 S01 P01 P02 P03 P04 P05 K01 H01 A02**.  
Hold: **P02 P05**.  
Prices: A01 $25 · S01 $28 · P01 $5 · P03 $18 · P04 $13 · K01 $37 · H01 $8 · A02 $22.  
Facebook: `https://www.facebook.com/profile.php?id=61594312648057`.

---

## 16. Open questions (do not answer by inventing)

1. Will Boss tag A01’s two hexes to real second/third photos, or stay one shared cover? Until Save, peek **cannot** appear honestly.
2. Should a snapped slide with a non-null `colorId` **move** the chip selection? Default **no** (chip is explicit). Revisit if admin tags every photo.
3. After Granola access: did a meeting already ban hex on storefront in favor of `02` text pills? Until then, **live + playbook hex boxes** stay.
4. `prefers-reduced-transparency` support in the shop’s browser matrix — progressive enhancement only.
5. iPhone 17 US page fetch timed out this pass — if a later crawl shows a different Product-viewer DOM, steal **behavior**, still not Apple assets.

---

## 17. Sources

### Apple

- HIG Motion — https://developer.apple.com/design/human-interface-guidelines/motion  
- HIG Materials — https://developer.apple.com/design/human-interface-guidelines/materials  
- HIG Color — https://developer.apple.com/design/human-interface-guidelines/color  
- Adopting Liquid Glass — https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass  
- Newsroom: new software design / Liquid Glass (2025-06) — https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/  
- WWDC25 session 219 *Meet Liquid Glass* — https://developer.apple.com/videos/play/wwdc2025/219/  
- WWDC25 session 284 *Build a UIKit app with the new design* — https://developer.apple.com/videos/play/wwdc2025/284/  
- App Store Connect Reduced Motion criteria — https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria/  
- iPhone 17 — https://www.apple.com/iphone-17/  
- iPhone 17 (UK) — https://www.apple.com/uk/iphone-17/  
- iPhone 17 Newsroom (UK, 2025-09) — https://www.apple.com/uk/newsroom/2025/09/apple-introduces-iphone-17/  

### CSS / Motion / a11y

- MDN `backdrop-filter` — https://developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter  
- MDN `filter` — https://developer.mozilla.org/en-US/docs/Web/CSS/filter  
- MDN `mask-image` — https://developer.mozilla.org/en-US/docs/Web/CSS/mask-image  
- MDN `scroll-snap-type` — https://developer.mozilla.org/en-US/docs/Web/CSS/scroll-snap-type  
- MDN `scroll-padding` — https://developer.mozilla.org/en-US/docs/Web/CSS/scroll-padding  
- MDN `prefers-reduced-transparency` — https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-transparency  
- CSS Scroll Snap Module L1 — https://www.w3.org/TR/css-scroll-snap-1/  
- Chrome: Make accessible carousels (2025-09-29) — https://developer.chrome.com/blog/accessible-carousel  
- Motion layout animations — https://motion.dev/docs/react-layout-animations  
- Motion / Framer `AnimatePresence` — https://www.framer.com/motion/animate-presence/  
- WCAG 2.2 SC 1.4.1 Use of Color — https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html  
- WCAG 2.2 SC 2.3.3 Animation from Interactions — https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html  
- NN/G animation purpose / response times / ecommerce PDPs — https://www.nngroup.com/articles/animation-purpose-ux/ · https://www.nngroup.com/articles/response-times-3-important-limits/ · https://www.nngroup.com/articles/ecommerce-product-pages/  

### Shop law

- This repo `README.md`, `sassy-closet/BOSS.md`, Slack `#shop-decisions` 2026-09-04  
- Playbook APPLY (PR #29) `excel-kit/prompts/AI_CLOTHING_SHOP_APPLY_TO_SELL_TEST.md`  
- Sisters `02`, `05`, `10`, `13`, `14`

---

## 18. What this pass could not see

- Granola (unauthorized).  
- Official Apple HIG pages (JS shell); used mirror + WWDC + Adopting Liquid Glass.  
- `apple.com/iphone-17/` full HTML (timeout); used UK extract + Newsroom.  
- Kelly Ying public site (Cloudflare on sister `13` this day). Look stays with `01` / `10`.  
- Tagged Blob images beyond `cover.jpg` — admin UI exists; live JSON still `colorId: null`.

---

## 19. PASTE INTO ORIGIN AGENT (do not paraphrase)

Copy everything between the markers into a Cloud Agent on the **Origin `sassy-closet-shop` repo** (the git behind https://sassy-closet-shop.vercel.app). Not this kit. Not intake `sassy-closet/`. Not `excel-kit/`.

```text
===== BEGIN ORIGIN PASTE — Apple watery color peek (LEARN 15) =====

You are editing Origin sassy-closet-shop. Ship APPLE-GRADE watery
see-through COLOR CHIPS + peeking GALLERY ROLL on the EXISTING PDP.
Do not restyle the boutique. Do not invent mã. Do not add iOS Liquid
Glass over photography. Do not touch intake or Excel. No stock copy.

HOST: https://sassy-closet-shop.vercel.app
LAW: Facebook inbox is the store. No cart. No Square Save. No FB Post/Send.
ALLOWLIST ONLY: A01 S01 P01 P02 P03 P04 P05 K01 H01 A02
HOLD (no $): P02 P05
PRICES: A01 $25 · S01 $28 · P01 $5 · P03 $18 · P04 $13 · K01 $37 · H01 $8 · A02 $22
LOOK LOCK: Cormorant Garamond + Be Vietnam Pro; paper / ink / gold / blush;
ma-mark; 11px uppercase tracking; ColorSwatch is a BOX (rounded-sm),
NOT an iOS capsule; announce-fade; shimmer; cta-shine + cta-flash.
Do NOT switch to intake rose / Allura / Nunito.
Do NOT copy Kelly Ying V984 or “$10 shipping on $300+”.
Do NOT copy Apple finish names (Lavender, Sage, Mist Blue).
Do NOT apply SVG goo / displacement / hue-rotate to product photos.
Do NOT write color NAMES on shopper swatches (playbook). Admin note stays admin-only.

FIND FILES (rg — names may differ; match these strings, then edit those files):

  rg -n "ProductGallery|ColorSwatch|imagesForColor|coverSrcForColor"
  rg -n "colorId|Add hex|Boxes only"
  rg -n "springSoft|filterSlide|useReducedMotion"
  rg -n "announce-fade|shimmer-slide|--gold:|backdrop-blur-md"

Expected (live 2026-09-09 chunk 1xr62vxitay1m.js + 3_93acjqq2t4q.js
+ 34vl_zddoo4ws.css):

  ColorSwatch: h-6 w-6 (md) / h-4 w-4 (sm), rounded-sm, border-black/20,
    selected outline-2 outline-offset-2 outline-ink, aria-label `Color ${hex}`
  ProductGallery:
    colorId state default null; index 0
    imagesForColor(product, colorId)
    AnimatePresence mode="wait"
    enter {opacity:0,x:24} → {opacity:1,x:0}
    exit  {opacity:0,x:-18}  duration 0.28s ease [.22,1,.36,1]
    key `${colorId??"all"}-${src??"none"}`
    dots only if images.length>1
    chip onClick toggles id and setIndex(0)
  imagesForColor LIVE (BUG — you must fix):
    colorId===null ? all : filter img.colorId===colorId
    ← this DROPS shared photos. Wrong.
  coverSrcForColor: first of imagesForColor, else coverSrc
  springSoft = { type:"spring", stiffness:420, damping:32, mass:0.72 }
  :root --paper --ink --gold --gold-deep --blush --duration-enter:.21s

Recorded colors (DO NOT invent more; DO NOT name them):
  A01  cb3d45c1231ab #F4F0E8 · c4b0be6de43a3 #1C2A4A
       images: /products/A01/cover.jpg colorId null
  P04  c27b990776c31 #F4F0E8
  P05  cf8dbca819819 #E8D5C4 · cee9b65b6a45b #8B3A3A · cffd8b024e8d1 #1C2A4A
  S01 P01 P02 P03 K01 H01 A02: colors [] → NO chip row

If a file is missing, create the smallest new file next to ProductGallery —
do not invent a second design system.

────────────────────────────────────────
FIX 1 — imagesForColor (honesty, then motion)
────────────────────────────────────────
REPLACE the filter with:

  function imagesForColor(product, colorId) {
    const n = product.images.filter((img) => img.src.trim());
    if (colorId == null) return n;
    const tagged = n.filter((img) => img.colorId === colorId);
    const shared = n.filter((img) => img.colorId == null);
    // tagged first, then shared flats/labels. NEVER another mã.
    return tagged.length ? [...tagged, ...shared] : shared;
  }

coverSrcForColor stays: imagesForColor[0] ?? coverSrc.

NEVER hue-rotate / brightness the cover toward a hex.
NEVER duplicate cover.jpg to fake a peek.

Admin: tagging UI already exists (“Add a color above to tag this image”).
On Preview, tag ONLY if the file is actually that finish. Do not auto-tag.

────────────────────────────────────────
FIX 2 — Watery enamel chip (keep the box)
────────────────────────────────────────
KEEP:
  rounded-sm (BOX, not capsule)
  sizes sm/md
  border-black/20  (required on light hex #F4F0E8 #E8D5C4)
  aria-label={`Color ${hex}`}
  title = hex (or saved admin note IF present — do not write a note)
  toggle-off on second tap

DO (motion on only):
  1. Inner layers:
       a) If this color.id has a tagged image: thumbnail peek
          (background-size:cover of THAT src only).
       b) Hex glaze: color-mix / linear-gradient of the stored hex
          at ~0.78 opacity when (a) exists, else solid hex.
       c) Speculum ::after radial-gradient white highlight,
          pointer-events:none. Hide when reduced-transparency
          or prefers-reduced-motion.
       d) Inset highlight + existing border.
  2. Selected meniscus:
       motion.span layoutId={!reduced && "pdp-color-ring"}
       absolute -inset-1 rounded-[inherit]
       box-shadow/outline INK (3:1 vs paper) + optional gold hairline
       transition={springSoft}
       while travelling: scaleX/Y 1 → 1.06 → 1 (ONE overshoot).
       Do NOT reuse layoutId "featured-tab".
  3. Hit target ≥44px via padding / ::before. Visible enamel stays 16/24px.
  4. backdrop-filter: blur(6px) ONLY on the glaze when a photo peek
     exists. If a parent is a backdrop-root (opacity<1, filter, mask),
     skip blur. NEVER backdrop-filter the hero img.
  5. Do NOT rounded-full. Do NOT h-11 fat discs.
  6. PLP ProductGrid sm chips: same recipe, scaled.

Reduce Motion: ring jumps, no scale, no speculum animation.
prefers-reduced-transparency: solid hex, no blur, no speculum.

────────────────────────────────────────
FIX 3 — Peeking gallery + color ROLL
────────────────────────────────────────
WHEN view.length > 1:
  Replace the single remounting <img> with a horizontal track:

    display:flex; gap:8px; overflow-x:auto;
    scroll-snap-type: x mandatory;
    scroll-padding-inline: 8%; padding-inline: 8%;
    slides: flex: 0 0 86%; scroll-snap-align: center; aspect-[3/4];

  Optional track mask-image linear-gradient fade at the edges
  (paper peek), NOT a mask that clips the garment oddly.

  role="region" aria-label={`Photos ${ma}`} aria-live="polite"
  Dots stay. Left/Right when region focused. No autoplay.
  Do not touch-action:none the whole PDP.

  Color tap:
    direction = index(nextColor) >= index(prev) ? 1 : -1
    set colorId, then scrollTo the first slide whose
    colorId === selected (else 0), behavior smooth unless reduced.

WHEN view.length <= 1:
  One photo. NO cloned peek. Chips still work (ring only).

OPTIONAL neighbor filter: blur(0.4px) on NON-snapped slides only.
Static, not animated. OFF under Reduce Motion. Delete if it
looks like a fabric lie.

If you KEEP AnimatePresence instead of a snap track:
  STOP using mode="wait" at 0.28s.
  Drive x by direction (Featured filterSlide numbers:
    enter 28*dir, exit -22*dir, ease [.22,1,.36,1]).
  Overlap (mode="sync" + absolute) OR cut so perceived ≤200ms.
  reduced: duration 0.
  Do not also run a snap track (pick one).

────────────────────────────────────────
FIX 4 — a11y + reduce CSS
────────────────────────────────────────
KEEP existing reduce kills for announce-fade / shimmer / cta-shine / VT.

ADD:
  @media (prefers-reduced-motion: reduce) {
    .pdp-peek { scroll-behavior: auto !important; }
    .pdp-peek-slide { filter: none !important; }
    .pdp-color-ring { transform: none !important; }
  }
  @media (prefers-reduced-transparency: reduce) {
    .pdp-color-glaze { opacity: 1 !important; backdrop-filter: none !important; }
  }

aria-pressed must follow selection after tap.
sr-only on selected chip: "Selected color {i} of {n}" — INDEX, no name.

────────────────────────────────────────
HARD STOPS
────────────────────────────────────────
- No new mã. No Q01 / A03 / AO001 on the lookbook.
- No cart, Shop now, Buy, Apple-style storage picker.
- Do not rewrite P02/P05 to a dollar. No e.tb.cn, no ¥, no customer names.
- Do not restyle fonts or gold “to look cleaner.”
- Do not touch https://sassy-closet.vercel.app (intake).
- Do not edit excel-kit or Official xlsx.
- Do not Production-promote without Boss. Open a Preview.
- Do not retune FeaturedBoard (LEARN 13) in this pass unless you
  regress it — leave featured-tab / filterSlide names alone.

────────────────────────────────────────
VERIFY (you click these; do not skip)
────────────────────────────────────────
Desktop + phone + OS Reduce Motion + keyboard:

1. /m/A01  two boxes. Tap each: ring moves. $25 Available.
   Message A01 → facebook.com/profile.php?id=61594312648057
   Until a photo is tagged: cover stays cover.jpg (honest).
   After you tag a real file to c4b0be6de43a3 on Preview:
   tap navy box → track ROLLS to that file. No hue-rotate.
2. /m/P05  three boxes. Hold · Inbox for price. No $.
3. /m/P04  one box. Related-rail chips belong to OTHER mãs;
   tapping them must not replace P04’s hero with P05.
4. /m/S01 /m/P02  no chip row. P02 Hold.
5. /  grid still 10. A01 sm chips if present. No A03.
6. Reduce Motion: no stretch, no neighbor blur, no 1.08 zoom.
7. View-source / network: no e.tb.cn, no ¥, no A03, no V984,
   no apple.com image hotlinks.
8. Photos never go through #goo / feDisplacementMap.

Commit on an Origin cursor/* branch. Preview URL in the PR. Do not merge.

===== END ORIGIN PASTE =====
```

Mini Boss: copy the block above as the **entire** Origin prompt. Do not add “also make it more premium” or “add liquid glass.” The enamel chip + peek + `colorId` roll *are* the watery pass. `10`’s hero VT + lightbox and `13`’s Featured pour still apply if they are not on `main` yet — do not regress them.

End of 15.
