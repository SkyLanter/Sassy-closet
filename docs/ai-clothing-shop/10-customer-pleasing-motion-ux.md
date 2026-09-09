# 10 — Customer-pleasing motion UX

**Learn track:** Ultra burn (research + live as-built + APPLY).  
**Shop:** Sassy Closet — Facebook inbox is the store; Square Free is on-hand truth; sell-test lookbook is Origin-owned.  
**Live APPLY target:** [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)  
**Audience:** Mini Boss / Origin shop implementer / whoever polishes motion without breaking reliability.  
**Date researched / crawled:** 2026-09-09.  
**This file does not assign stock, mint a mã, Save in Square, post to Facebook, or redesign the boutique.**

Kelly Ying *look* is locked (`01` §1.3, §11). Fancy motion is locked (`07` §11.0; `09` §0). This note is the **motion reliability** book: boutique micro-interactions that feel premium **because they tell the truth**, not because they add more movement.

---

## 0. How to read this document

This is a **learn-track** note, not a rebuild brief and not permission to fork Origin shop code from this kit repo.

- **Cite, don’t invent.** Shop-law claims point at a file, Slack permalink, sister learn-track, or the live host. Industry claims point at NN/G, W3C WCAG 2.2, WAI-ARIA APG, MDN / Chrome View Transitions, Baymard, Apple HIG, or Jakob Nielsen’s response-time limits. If a fact is missing, the gap is named.
- **Never invent a mã.** The only customer-facing codes this pass may name are the **first-ten allowlist**. Admin “Next mã A03” is a prediction, not a product. Slack’s `AO001` / `AO003` lines are **decision-template examples** from `#shop-decisions` (2026-09-04), not proof those pieces exist in Square or on the lookbook. Kelly Ying’s `V984.` / `V826.` card codes are **their** SKUs — do not copy them onto Sassy tiles.
- **Two alphabets.** Sell-site / hub display = letter + 2–3 digits (`A01`). Official / Square / SoT = `AO` / `QU` / `VA` / `AK` / `GI` / `PK` / `SET` + three digits (`AO001`). Motion must never “helpfully” translate one into the other (`01` §9; `excel-kit/schema.py` `MA_RE`; `sassy-closet/lib/mint.ts`).
- **Facebook inbox is still the store** until Boss changes that in `#shop-decisions`. A “buy” on this site is **Message {code}**. There is no cart. Motion that implies checkout (bag bounce, flying-to-cart) is a lie.
- **No redesign mandate.** Improve **inside** paper / ink / gold / blush, Cormorant Garamond + Be Vietnam Pro, `ma-mark`, `announce-fade`, `shimmer` / `shimmer-slide`, `cta-shine` / `cta-flash`, gold underline, hover lift, `view-transition-name: site-header` / `product-{MA}`. Do not replace that language with Shopify Horizon, intake Allura/Nunito rose, or a new design system (`01` §11; `07` §11.0; `09` §0).

### 0.1 Research method (and what this pass could not see)

| Source | Result |
| --- | --- |
| Live sell-test HTML + CSS + `curl -I` of `/`, `/c/ao`, `/c/set`, `/c/phu-kien`, `/c/ao-khoac`, `/c/toc`, `/c/quan`, `/m/A01`, `/m/A02`, `/m/S01`, `/m/P02`, `/admin` | Read 2026-09-09. Primary **as-built** motion map. |
| Live CSS chunk `/_next/static/immutable/chunks/34vl_zddoo4ws.css` | Keyframes, reduced-motion query, hover MQ, view-transition rules. Quoted below. |
| Repo `excel-kit/`, `sassy-closet/`, `README.md` | Shop law. Intake lightbox / sheets are the **behavior** library, not the sell-site skin. |
| Sister LEARN TRACK PRs #19–#27 (`01`–`09`) | Headings + APPLY locks. This file is `10`. |
| Slack `#shop-decisions` (`C0BV3GYC602`) | Five standing messages (2026-09-04). |
| PR #18 `excel-kit/docs/SELL_CATALOG_CONTRACT.md` + sample `sell-catalog.v1.json` | Allowlist, prices, Hold pair, **recorded** color ids (not live customer chips). |
| Linear | No motion-UX issue this pass. |
| Granola meetings | MCP unauthorized — no meeting notes. |
| Notion | Keyword search returned no Sassy Closet motion pages. |
| Kelly Ying Boutique public site | Home + Dresses collection fetched 2026-09-09. **Look / cadence / SKU-on-card** only. Cloudflare later blocked a repeat product fetch — collection facts below come from the successful home + collection read and from `01`. |
| Public UX / a11y / motion specs | Fetched 2026-09-09. URLs in §16. |

If a later crawl disagrees with a **live** cell here, **the new crawl wins** — update the date line. Shop law still wins over industry taste. Recorded hub colors in the catalog contract win over a model that “sees” a new shade.

### 0.2 Sister docs

| # | File | Job vs this note |
| --- | --- | --- |
| 01 | `01-messenger-social-commerce.md` | Kelly Ying look lock; Message-first; no cart; no invented ship `$` |
| 02 | `02-pdp-color-size-ux.md` | Customer **text** colors; gallery sync nouns; intake lightbox as pattern |
| 03 | `03-tiny-boutique-admin.md` | Admin brains; do not mint from “Next mã” |
| 04 | `04-next-blob-catalog-arch.md` | ISR / Blob; `/m/A03` must 404 |
| 05 | `05-ai-product-media.md` | Recorded first-ten colors; `colorId` bind; no invented hex |
| 06 | `06-seo-trust-diaspora-boutique.md` | Soft-launch `noindex`; unique `/c/*` titles |
| 07 | `07-taobao-dropship-boutique.md` | Motion lock list; dropship-honest copy |
| 08 | `08-dropship-ops-runbook.md` | Staff clock; does not restyle |
| 09 | `09-bugcheck-sell-site-checklist.md` | Tick-box QA; MOT-01…MOT-08 |
| **10** | **This file** | **How motion should behave; APPLY for Origin** |
| Kit | `SELL_CATALOG_CONTRACT.md` (PR #18) | Allowlist + prices + Hold null `$` |

---

## 1. Executive summary

Premium boutique motion is **feedback that keeps the buyer oriented**. It is not a second brand, not a loading show, and not a reason to hide Hold, invent a color, or mint `A03`.

Nielsen Norman Group’s motion research is blunt: animation must be **unobtrusive, brief, and subtle**. Use it for **feedback**, **state-change**, **navigation metaphors**, and **stronger signifiers**. Do not use it to fill downtime or to “delight.” Peripheral vision is wired to treat motion as important; irrelevant motion degrades the task ([NN/G, *The Role of Animation and Motion in UX*](https://www.nngroup.com/articles/animation-purpose-ux/); [NN/G, *Animation for Attention and Comprehension*](https://www.nngroup.com/articles/animation-usability/)). Microinteractions are trigger → rule → feedback, one job each ([NN/G, *Microinteractions in User Experience*](https://www.nngroup.com/articles/microinteractions/); Saffer 2014, cited there).

Sassy Closet’s sell-test already shipped a Kelly Ying *rhythm*: serif wordmark, gold underline, blush/paper/ink, uppercase 11px tracking, livestream rail, SKU-on-card, collection chips — **without** Kelly Ying’s cart ([kellyyingboutique.net](https://www.kellyyingboutique.net/); `01` §1.3). Live CSS (2026-09-09) already has the boutique motion language:

| Token | Live fact |
| --- | --- |
| `@keyframes announce-fade` | `4.2s ease-in-out` on the livestream line |
| `@keyframes shimmer-slide` | `1.3s ease-in-out infinite` on `.shimmer` (ten home cards) |
| `@keyframes cta-flash` | `0.7s` shine on `.cta-shine:hover:after` |
| Card hover (`@media (hover:hover)`) | `-translate-y-1.5`, image `scale-[1.08]` / `800ms`, gold underline `scale-x` |
| View Transitions | `view-transition-name: site-header` + `product-{MA}` on **home cards** |
| Reduced motion | `@media (prefers-reduced-motion: reduce)` zeros `.announce-fade`, `.shimmer`, `.cta-shine:hover:after`, and `::view-transition-*` animations |

That is enough “fancy.” The gaps that still break **customer-pleasing** (and reliability) are not missing particles. They are:

1. **Category switch** — home Featured is a `tablist` that filters the ten; `/c/*` is a second IA. Motion must keep counts honest and never spawn a tile to fill an empty category (`/c/quan` is empty on purpose).
2. **Color → gallery** — live customer `colors: []` is honest. When admin later stores **recorded** names from the hub contract, text chips must filter **this mã’s** hero / thumbs / lightbox. No hue-only dots. No borrowed folder.
3. **Lightbox** — sell-test PDPs have a single `cover.jpg` and **no** enlarge dialog this crawl. Intake `PhotoLightbox` already has the reliable close/focus contract (PR #14). APPLY: steal **behavior**, dress it in Kelly Ying chrome.
4. **Reduced-motion fallbacks** — looping animation is already killed. **Hover scale / lift is not.** View-transition **names on PDP heroes are missing**, so the Chrome “thumbnail → PDP” morph ([Chrome View Transitions](https://developer.chrome.com/docs/web-platform/view-transitions/)) cannot keep the same mã in the handoff.

Reliability beat beauty when they conflict. A gold shimmer that hides a Hold badge, a 700ms wipe that feels like navigation to another mã, or a color fade that shows `A02`’s cover on `A01` is a **failed** boutique — not a premium one.

---

## 2. Hard constraints (print these on the implementer’s wall)

1. **Never invent a mã.** Stock / Boss assigns. Scripts require `--ma` or print ASK STOCK (`excel-kit/schema.py` `ASK_STOCK_MA`). Sold Official mã stays retired. Unique piece = unique mã (`excel-kit/DESIGN_NOTES.md`; `excel-kit/square/README.md`). Sell-test emit list is **exactly** `A01 S01 P01 P02 P03 P04 P05 K01 H01 A02` (PR #18).
2. **Never invent qty, $, storage, photos, hex, or color names.** Empty = hide the chip row, or `—`, or **Inbox for price** on Hold. Do not CSS-circle a missing color (`02` §8.2; `05` §3.2).
3. **Square Free = on-hand source of truth.** Official Excel is a working copy / mã index / captions — not a second warehouse (`README.md`). Sell-site `qty: 1` must not animate as “1 in warehouse” (`07` §11.2).
4. **Bots draft only.** No Square Save, no Facebook Post/Send, no Zelle from the app (`README.md`; Slack `#shop-decisions` 2026-09-04).
5. **No cart, Shop now, or bag-fly.** Kelly Ying’s public site has Cart + Checkout and **Flat rate $10 shipping on order $300+**. Those dollars are **theirs**. Sassy’s `#shop-decisions` still lists flat ship `$` as unlocked (`01` §0, §11).
6. **Customer colors are text.** WCAG 2.2 SC [1.4.1 Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html). Pattern names (Hoa, Chấm bi, Caro, Ánh kim) cannot be a hue disc (`kinds.ts`; `05` §3.2 `cham-bi`).
7. **Motion never changes identity.** Same mã in, same mã out. View-transition name `product-A01` must morph **only** to A01’s hero. Category filter must not drop P02/P05 or invent Q01.
8. **Origin owns the pixels.** This kit does not modify `sassy-closet-shop` git (`CLONE_TO_OFFICIAL.md`; PR #18). APPLY is for the Origin agent. Intake Production stays https://sassy-closet.vercel.app.

---

## 3. What “premium” motion means here

### 3.1 NN/G: purpose first, chrome second

NN/G’s usable animation jobs, mapped onto this closet:

| NN/G job | Sassy Closet meaning | Fail if… |
| --- | --- | --- |
| Feedback | Tab gold underline; `aria-selected`; color pill `aria-pressed`; lightbox open | Click does nothing visible for >100ms with no state change ([NN/G response times](https://www.nngroup.com/articles/response-times-3-important-limits/)) |
| State change | Available ↔ Hold stays **text**; color filter changes **this** gallery | Animation is the only cue (fails 1.4.1) |
| Spatial metaphor | Card → PDP is “the same piece, closer”; overlay is “on top of this page” | Instant full-screen swap that feels like a new site; Back leaves a trap |
| Signifier | Gold underline grows on hover (`@media (hover:hover)`); card lifts | Phone requires hover to know the tile is tappable (`09` MOB-09) |
| Attention | Livestream `announce-fade` | Infinite shimmer competes with Hold gold (`09` MOT-08) |

NN/G’s attention paper: for a cause-and-effect link, the effect should start within **0.1 seconds** of the action ([*Animation for Attention and Comprehension*](https://www.nngroup.com/articles/animation-usability/)). Jakob Nielsen’s classic limits: **0.1s** feels instantaneous; **1s** keeps flow; **10s** needs a progress story ([*Response Time Limits*](https://www.nngroup.com/articles/response-times-3-important-limits/)). Boutique motion that lasts longer than ~300–400ms on a **direct tap** (color, category chip, lightbox) starts to feel like navigation — which on a 10-SKU lookbook is how buyers lose the mã.

NN/G also warns that **time-filling** transition animation is what testers hate. A 700ms page-flip between All and Tops is downtime, not luxury.

### 3.2 Apple HIG / Chrome: reduce, don’t amputate meaning

Apple’s motion guidance: do not make people **wait** for an animation to finish, especially one they will see often; let them cancel motion ([Apple HIG — Motion](https://developer.apple.com/design/human-interface-guidelines/motion)). Reduce Motion should replace large spatial moves (zoom, slide, scale) with a **crossfade or instant**, not a dead UI ([App Store Connect Reduced Motion criteria](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria/)). Apple’s vision/motion session further flags **sustained oscillation** as a comfort risk ([WWDC23 — Design considerations for vision and motion](https://developer.apple.com/videos/play/wwdc2023/10078/)). A 1.3s **infinite** shimmer is a small-amplitude loop — decorative, but it never stops.

Chrome’s View Transitions docs use **exactly** this shop’s metaphor: a listing thumbnail that continues into the PDP image; a fixed header that stays put; a grid that **reorders when filtered** ([Smooth transitions with the View Transition API](https://developer.chrome.com/docs/web-platform/view-transitions/)). They also say reduced-motion users can get `animation: none` on `::view-transition-*`, **or** a subtler animation that still shows relationship ([same-document guide, “React to the reduced motion preference”](https://developer.chrome.com/docs/web-platform/view-transitions/same-document#handling_reduced_motion_preferences)). Live CSS already takes the hard-off path for VT animations. That is allowed. The remaining job is to keep **state** visible when motion is off.

### 3.3 WCAG: two different clocks

Do not collapse these (common error; see [Motion Spec on 2.3.3 vs 2.2.2](https://motionspec.dev/blog/wcag-2-3-3-animation-from-interactions)):

| Criterion | Level | What it covers here |
| --- | --- | --- |
| [2.2.2 Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) | **A** | Moving / blinking / scrolling that **starts automatically**, lasts **>5s**, and runs **in parallel** with other content. `.shimmer` is `infinite` at 1.3s — it is still moving at 6s, 60s, and after the buyer started reading price. OS Reduce Motion is *a* mechanism; an on-page pause is the strict reading. `announce-fade` is 4.2s (under 5s) if it does not loop. |
| [2.3.1 Three Flashes](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html) | **A** | Nothing on the live CSS flashes ≥3 times/second. Do not “improve” `cta-flash` into a strobe. |
| [2.3.3 Animation from Interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) | **AAA** | Hover lift, scale, view transitions, color crossfade. Sufficient technique: [C39 `prefers-reduced-motion`](https://www.w3.org/WAI/WCAG22/Techniques/css/C39). Live query **does not** yet disable hover `scale-[1.08]` / `-translate-y-1.5` (`09` MOT-03). |
| [2.2.2 / 2.3.3 both] | — | Auto-playing *and* interaction-triggered motion can fail both if they loop and cannot be disabled. |

Vestibular impact is not theoretical. W3C’s 2.3.3 Understanding page: extra motion can mean dizziness, migraine, bed rest. Parallax and large zooms are named risks. A boutique 1.08 hover zoom on a full card is the kind of **scale** Reduce Motion is meant to replace with a fade.

---

## 4. As-built map (cite the live host, don’t redesign it)

### 4.1 Surfaces

| Surface | URL | Motion job today | Customer PDP? |
| --- | --- | --- | --- |
| Lookbook home | `/` | Announce fade; featured `tablist`; 10 shimmer cards; VT names on every allowlist tile + header | Grid |
| Category pages | `/c/ao` `/c/set` `/c/phu-kien` `/c/ao-khoac` `/c/toc` `/c/quan` … | Same card chrome; header VT; per-tile `product-{MA}` when that mã is in the set | Grid |
| PDP | `/m/{MA}` | `ma-mark`; related-rail cards; **no lightbox string** on A01 this crawl | Yes — Message, not cart |
| Admin | `/admin` | Hidden from nav; no customer VT names in the 2026-09-09 HTML | No |
| Intake | https://sassy-closet.vercel.app | Rose sheets, Allura/Nunito, `PhotoLightbox` Esc/focus/portal | **No** — `INTAKE • NHẬN ĐỒ` |
| Facebook inbox | Page `61594312648057` | The store | Chat |

### 4.2 Featured collection vs `/c/*` (two IAs)

Home Featured is **not** a link row. Live markup (2026-09-09):

```html
<div role="tablist" aria-label="Filter featured collection">
  <button type="button" role="tab" aria-selected="true">All<span>10</span>…gold rule</button>
  <button …>Tops<span>2</span></button>
  … Sets 1 · Accessories 5 · Jackets 1 · Hair 1
</div>
<p>10 pieces</p>
```

Tabs are **client filters**. Counts sum to 10. Gold `h-px` underline is the selected signifier (`transition-colors duration-300`). Separate routes exist for the same kinds (`/c/ao` title “Tops · Sassy Closet”, `/c/quan` title “Pants · Sassy Closet” with **no** `product-*` VT names — empty set).

APPLY must treat these as **one catalog, two URLs**, not two inventories. Filtering “Tops” must show **A01 + A02** only — the same two `/c/ao` shows. It must not hide Hold accessories from **Accessories** / `/c/phu-kien`.

### 4.3 Card / hover / shine (Kelly Ying lift)

Home cards (all ten allowlist mãs) share:

- `view-transition-name: product-{MA}`
- `.shimmer` overlay (`background-size: 200%`; `animation: 1.3s ease-in-out infinite shimmer-slide`)
- `transition-[transform,box-shadow] duration-500` + `group-hover:-translate-y-1.5` + shadow
- Image `duration-[800ms] ease-out group-hover:scale-[1.08]`
- Gold hairline `origin-left scale-x-0` → `group-hover:scale-x-100` (`duration-500`)
- Badge text **Available** (ink) or **Hold** (gold) + `sr-only` “Status: ” (`09` A11Y-02)

Hover utilities live under `@media (hover:hover)` in the same CSS chunk — phones should still open `/m/A01` with no lift (`09` MOB-09).

One `.cta-shine` lives on home (header/footer Message). Hover runs `cta-flash` (translate shine 0.7s).

### 4.4 View Transitions — what actually morphs

**Home** names (complete allowlist + header):

`site-header`, `product-A01`, `product-S01`, `product-P01`, `product-P02`, `product-P03`, `product-P04`, `product-P05`, `product-K01`, `product-H01`, `product-A02`.

**PDP `/m/A01`** this crawl: `site-header` and **`product-A02` only** (related-rail tile). The A01 hero `<img src="/products/A01/cover.jpg" alt="A01. TOP">` has **no** `view-transition-name: product-A01`.

**`/m/P02`:** related-rail `product-P01` / `P03` / `P04` / `P05` + header — **not** `product-P02` on the hero.

**`/m/S01`:** `site-header` only (no other Set to relate).

Chrome’s canonical example is thumbnail → full image **sharing a name**. Today the name lives on the listing card and on the **neighbor** card of the PDP, not on the hero the buyer just opened. The morph the look paid for is therefore **easy to lose** (fallback: whole-page fade). That is an as-built gap, not a taste note (`09` MOT-04).

Header rules already in CSS:

```css
::view-transition { pointer-events: none }
::view-transition-group(site-header) { z-index: 100; animation: none }
::view-transition-old(site-header) { display: none }
::view-transition-new(site-header) { animation: none }
```

`pointer-events: none` on the overlay is the right reliability move (clicks during the snapshot must not freeze Messenger — `09` MOT-05). Header is intentionally **instant** so the rail does not swim.

No `@view-transition { navigation: auto }` appeared in the downloaded CSS chunk. Cross-document VT still requires **both** documents to opt in ([Chrome MPA section](https://developer.chrome.com/docs/web-platform/view-transitions/)). If home→PDP morphs in Chrome today, the opt-in lives in another chunk or inline; if it does not, adding the at-rule is APPLY — **after** heroes share `product-{MA}`.

### 4.5 Color / gallery / lightbox today

| Check | Live 2026-09-09 |
| --- | --- |
| Customer color row on `/m/A01` | Absent (`09` + this crawl) |
| Hero | One `/products/A01/cover.jpg`; `rel=preload` |
| Thumbs / `+N` | None on A01 |
| `role="dialog"` / “lightbox” string | None on crawled PDPs |
| Enlarge control | None (NN/G “enlarged view” is unmet; copy already says “Message A01 for real photos”) |
| Related rail | A02 cover, hover scale, `opacity-0` until hydrated |

Hub **recorded** colors (kit sample / `05` §3.2 — **do not add ids**):

| Mã | Recorded `colors[].id` | Live customer chips |
| --- | --- | --- |
| A01 | `kem`, `xanh` | empty |
| S01 | `kem` | empty |
| P01 | `hoa` | empty |
| P02 | `do` (Hold) | empty |
| P03 | `den`, `do` | empty |
| P04 | `kem` | empty |
| P05 | `hong`, `do`, `xanh` (Hold) | empty |
| K01 | *(none)* | empty |
| H01 | *(none)* | empty |
| A02 | `cham-bi` | empty |

Until admin binds `colorId`, a color tap has **nothing honest to show**. Empty is the pass. Inventing Kem chips from this table onto the live PDP without a stored row is still inventing UI.

### 4.6 Intake motion library (behavior only)

Do **not** restyle the lookbook to Allura / `#D82B60`. Do steal contracts already in this repo:

| Pattern | File | Steal |
| --- | --- | --- |
| Bottom / center sheet | `SavedCard.tsx`, `FindMaCard.tsx` | Backdrop click, Done, `role="dialog"`, stopPropagation on the sheet |
| Lightbox | `PhotoLightbox.tsx` (PR #14) | Portal; `aria-modal="true"`; Esc; focus close; restore focus; `body` scroll lock; backdrop + ✕; `setTimeout(0)` close so the click does not fall through to the card (`FindMaCard` stay-open — PR #14 / `6d1071e`) |
| 3-up + `+N` | `PhotoThumbs.tsx`, `FIND_CARD_THUMB_LIMIT = 3` | Zero photos = text-only |
| Kind / color pills | `IntakeApp.tsx` | `rounded-full`, `aria-pressed`, words not circles |

### 4.7 Reduced-motion as shipped

Exact live query:

```css
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto }
  .announce-fade, .shimmer, .cta-shine:hover:after { animation: none !important }
  ::view-transition-group(*),
  ::view-transition-old(*),
  ::view-transition-new(*) { animation: none !important }
}
```

**Killed:** looping shimmer, announce fade, CTA shine sweep, VT CSS animations.  
**Not killed:** `duration-500` lift, `duration-[800ms] scale-[1.08]`, gold underline scale, `transition-colors duration-300` on tabs. Those are still **motion animation from interaction** under 2.3.3.

---

## 5. Kelly Ying look — steal the rhythm, refuse the cart

Kelly Ying Boutique (Garden Grove) is the **look + livestream cadence** reference, not the commerce engine (`01` §1.3).

What their **public site** actually does ([kellyyingboutique.net](https://www.kellyyingboutique.net/), home + Dresses collection read 2026-09-09):

| Their pattern | Steal for Sassy? |
| --- | --- |
| Livestream banner with **days** (Chủ Nhật và Thứ 2) | Steal the *idea* of a named cadence. Sassy currently prints only “Facebook livestream” — `01` APPLY #5: name a day or take the bar down. Do not invent days. |
| Flat rate **$10 / $300+** | **Refuse.** Not Sassy’s number. |
| Cart + Checkout | **Refuse.** Message-first is locked. |
| SKU on the card (`V984. LACE BLACK DRESS`) | Steal the *job* (comment and DM name the same piece). Sassy’s printed code is **A01**, not `V984`. |
| Collection chips (Dresses / Tops / Bottoms / Two-Pieces / Sleepwear) | Steal the *rhythm* (short uppercase kinds + count). Sassy’s chips are All / Tops / Sets / Accessories / Jackets / Hair — do not add Sleepwear or Kids to invent stock. |
| Dense product grid, price on card | Already shipped. Keep 2-up phone (`09` MOB). |

Third-party listings describe weekly Facebook lives and staff who chat (`01` cites Loc8NearMe / Locality). That is **inbox speed**, not a JS confetti. Meta’s click-to-message best practices are greet / look available / answer ([Meta](https://www.facebook.com/business/help/269324800441478)) — a 14-hour read receipt is the abandoned cart (`01` §7.6). Motion on the lookbook cannot fix that.

**Look lock (do not restyle away):**

- Cormorant Garamond display + Be Vietnam Pro UI (`07` §9.1 / §11.0).
- Paper / ink / gold / blush; `ma-mark` tabular nums; 11px uppercase tracking.
- Gold underline on selected Featured tab and hover hairline.
- Editorial lifestyle (`/editorial/*`) is **mood**, never SKU proof (`07` §11.0).
- No Inter takeover, no dark luxury theme, no Horizon clone (`02` §13.4; `09` §0).

---

## 6. Reliability law (motion must not lie)

Write these as code-review questions. If a PR answers “the animation looked expensive,” it is not ready.

1. **Identity.** After the animation, the visible mã is the mã the buyer selected. `product-A01` never finishes on S01’s pixels.
2. **Status.** Hold vs Available is readable **mid-shimmer** and with Reduce Motion on. Gold vs ink is a hint; **words** are the fact (WCAG 1.4.1; `09` MOT-08).
3. **Price.** P02 / P05 never flash `$23` or `$` during a crossfade (PR #18; `01` §11).
4. **Catalog bounds.** Category motion only rearranges **allowlist** tiles. Empty `/c/quan` stays empty. No skeleton that looks like a sixth accessory.
5. **Color honesty.** Gallery pixels after a color tap are tagged `colorId` for **that** name on **that** mã, or untagged shared shots — never another folder (`02` §8; `05` §7).
6. **CTA.** Message / Messenger stays clickable. VT overlay `pointer-events: none` stays. Do not `await` 800ms before navigation.
7. **Interrupt.** Apple: user can proceed before the tween ends ([HIG Motion](https://developer.apple.com/design/human-interface-guidelines/motion)). Color tap #2 cancels tap #1’s fade. Lightbox Esc works on frame 1.
8. **No checkout metaphor.** No bag, no flying thumbnail to a cart icon, no “Added!” toast that implies Square decremented.
9. **No dark-pattern motion.** NN/G names flashing countdown clocks as attention hijacking ([animation-purpose-ux](https://www.nngroup.com/articles/animation-purpose-ux/)). No fake 24h Hold timer (`02` §15).
10. **Same data, every surface.** Home card = Featured filter = `/c/*` = PDP = admin header (`09` NAV-09). Motion cannot paper over a $25 / $22 split.

---

## 7. Category switch

### 7.1 Two switches, one truth

| Switch | Mechanism | Motion that belongs |
| --- | --- | --- |
| Home Featured tabs | Same-document filter (`role="tablist"`) | Gold underline move **or** fade; grid reorder with optional `startViewTransition`; counts update |
| Kind routes | `/c/ao` etc. (MPA) | Shared `site-header`; cards that exist on both sides keep `product-{MA}` |

Do not implement a third filter (search chips, “New arrivals” that invents a season) without a Boss row.

### 7.2 Desired behavior (home tabs)

```text
on Featured tab activate
  → aria-selected moves; gold rule sits under the new word
  → "N pieces" matches the visible allowlist count
  → tiles that leave fade/shrink ≤200ms (or instant if reduce)
  → tiles that stay keep their mã, price, Hold/Available
  → Hold accessories stay when Accessories is selected (P02, P05)
  → URL strategy is explicit: either stay on `/` (today) or push `/c/…`
     — do not do both and show different sets
  → do not fetch or mint a tile to avoid an empty grid
```

WAI-ARIA Tabs: `role="tablist"` / `tab` / `tabpanel`, arrow keys, `aria-selected`, one selected ([APG Tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/)). Live buttons already have `role="tab"` and `aria-selected`. APPLY: wire a `tabpanel` (the `<ul>` grid) with `aria-labelledby` / `aria-controls` if not already in the hydrated tree, and keyboard arrows if they are mouse-only today.

Chrome’s cards demo is the right **filter** metaphor ([View Transitions](https://developer.chrome.com/docs/web-platform/view-transitions/)): items that remain **move**, items that leave **fade**, items that enter **fade**. They do not clone.

### 7.3 Empty categories

`/c/quan` (Pants) returned 200 with only `site-header` VT this crawl. That is **honest**. APPLY empty copy: “Chưa có quần trên lookbook” / “No pants listed” — not a fake Q01, not a Taobao screenshot, not a Kelly Ying bottoms scrape.

Kind letters that exist in intake (`Q V D G B J O` … in `kinds.ts`) are **not** permission to show those `/c/*` as stocked. Soft-launch has ten pieces. Counts on home (Tops 2, Accessories 5, …) must stay math on that ten.

### 7.4 Timing

| Path | Default | `prefers-reduced-motion: reduce` |
| --- | --- | --- |
| Underline / color of tab | 150–300ms (live `duration-300` is fine) | Instant selected styles |
| Grid filter | ≤200ms opacity + small translate **or** VT group | Instant swap; no scale |
| Route `/` → `/c/ao` | Header static; matching A01/A02 morph if names exist on both | Instant navigation; names still help **scroll restoration**, not zoom |

If filter JS is slower than **1s**, show the existing “N pieces” as stale only if you also show a quiet busy state — do not shimmer a second catalog (`NN/G` 1s / 10s limits). ISR (`x-nextjs-stale-time: 300` on home) is a cache clock, not a motion clock (`04`; `09`).

### 7.5 Reliability tests (category)

- All → 10 tiles, same mãs as the contract allowlist.
- Tops → A01 ($25 Available) + A02 ($22 Available) only.
- Accessories → P01–P05; P02 and P05 still **Hold · Inbox for price**.
- Hair → H01 $8; Jackets → K01 $37; Sets → S01 $28.
- Rapid tabbing does not duplicate A01 or drop P04.
- Reduce Motion: filter still works; no leftover opacity:0 ghost tiles.

---

## 8. Color → gallery

Sister `02` owns the noun model. This section is the **motion** of that model on the Kelly Ying PDP.

### 8.1 When `colors` is empty (today)

No chip row. No four mystery dots. Hero stays the stored cover. CTA stays “Message {MA} for real photos” where that sentence already exists (`09` PDP-01…04). **Do not** animate a swatch into existence from `05`’s recorded table until admin has saved those colors on **that** row.

### 8.2 When a row later has recorded names

Use **only** ids already on that mã (`05` §3.2). Customer control = **text pills** in lookbook chrome (ink ring, gold or ink selected rule — not intake rose unless you are on intake).

```text
on customer color activate
  → selectedColor = that recorded name (Kem, Xanh, Hoa, Đỏ, …)
  → visible text: Đang xem: {name}
  → hero + thumbs + lightbox set = images where colorId matches
       OR colorId is null (shared), per 02 §8 / 05 §7
  → short opacity crossfade on the image only (150–250ms)
  → do not change mã, price, Hold, or route
  → do not fetch /products/A02/ when the page is A01
  → missing set → honest empty / Message {MA}, never a CSS circle

on customer size activate (if exposed)
  → availability line updates
  → gallery does not change unless a photo is tagged to that size
    (default: photos are color-keyed)
```

### 8.3 Motion that belongs vs motion that lies

| Keep | Refuse |
| --- | --- |
| 150–250ms opacity on **hero img** | Full-page wipe, blur-up that never resolves |
| Thumb `aria-current` + hairline | Bouncing dots, auto-advancing carousel |
| Instant swap on Reduce Motion | 800ms scale “to feel premium” |
| Prefetch next color’s first HQ **after** idle | Preload every mã’s folder (hurts LCP — `06`) |

Shopify’s default (scroll to one variant image, leave a mixed strip) is the industry failure mode `02` already refused ([Craftshift](https://craftshift.com/shopify-variant-images-complete-guide/); Horizon thread). Do not reintroduce it as a “smooth scroll.”

Baymard: users expect **zoom** and enough resolution to see detail ([*Ensure Sufficient Image Resolution and Zoom*](https://baymard.com/blog/ensure-sufficient-image-resolution-and-zoom) — 93% of desktop sites offer some zoom; 25% fail resolution/zoom). Color change without enlarge still leaves the NN/G “enlarged view” hole. That is §9.

### 8.4 Pattern colors

`hoa`, `cham-bi`, and intake `caro` / `anhkim` / `pastel` / `khac` are **words**. A crossfade that tints the hero toward a guessed hex invents a hue (`05` §3.2: do not rename `cham-bi` to Trắng because a model sees dots).

### 8.5 Performance so the fade is pretty

Hero: `fetchpriority="high"` / existing `rel=preload` on the **current** cover only. Secondary thumbs `loading="lazy"`. When the buyer selects Xanh, swap `src` to the bound file (or show empty). Do not keep A01 Kem on screen at 30% opacity on top of A02’s preload — `/m/A01` already preloads A02’s cover for the rail; that is related-rail LCP, not a color bind.

---

## 9. Lightbox

### 9.1 Why it exists

NN/G’s PDP must-haves include **recognizable images + enlarge** ([*UX Guidelines for Ecommerce Product Pages*](https://www.nngroup.com/articles/ecommerce-product-pages/)). Baymard: zoom is a convention; low-res zoom looks cheap and users leave. Apparel buyers need seam / fabric / print (Hoa, Chấm bi) more than a 1.08 hover crop.

Live A01 has **no** enlarge control. Honest interim copy (“Message A01 for real photos”) is better than a dead magnifier (`09` PDP-04). APPLY is to add a lightbox **when there is a real file**, using intake’s close contract and lookbook chrome.

### 9.2 Steal intake reliability (PR #14)

`PhotoLightbox.tsx` already:

- Portals to `document.body` (escape stacking / `z` wars).
- `role="dialog"` + `aria-modal="true"` + labelled title (“Ảnh lớn”).
- Focuses close; restores `document.activeElement` on unmount.
- Locks `document.body.style.overflow`.
- Esc (capture) + backdrop + ✕.
- Defers `onClose` with `setTimeout(0)` so the same pointer does not click the find card closed.

WAI-ARIA APG Dialog (Modal): focus in; Tab cycles; Escape closes; focus returns to invoker; visible close button; `aria-modal="true"` only if the page is truly inert ([APG](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)). Intake is **close** to this; it does not implement a full Tab **trap**. APPLY: add trap **or** keep the control set so small (close + image) that Tab cannot escape — do not ship a half-modal that tabs into Messenger under the veil (a11y lightbox writeups call this the common store trap — [A11yFix](https://blog.a11yfix.dev/blog/product-image-zoom-lightbox-accessibility/)).

Trigger must be a **`<button>`** (or `<a>`), not a bare `<img onclick>`. Intake thumbs already are buttons (`PhotoThumbs.tsx`).

### 9.3 Kelly Ying chrome (do not import intake rose)

| Piece | Lookbook treatment |
| --- | --- |
| Veil | Ink / paper dim (live cards already use `from-ink/25`–`/55`), not `bg-rose-950/70` |
| Image | Existing radius language; `object-contain`; max ~`88dvh` is fine to steal |
| Close | 44×44 minimum (WCAG 2.5.8 target-size **AA** is 24px; this shop already uses 40–44 on intake close). Gold or ink, not a new icon font |
| Caption | Printed mã + selected color **name** if any — `A01 · Kem` — never a guessed English SEO title |

### 9.4 Gallery rules inside the overlay

- Set = **current color filter**, not the mixed catalog (`02` §8.1 `on lightbox open`).
- Swipe / arrows only among that set. Do not wrap into A02.
- `+N` on a 3-up row opens the **same** mã’s remaining files (`photos.ts` `visiblePhotoPaths`), not another folder.
- Zero extra files: enlarge the one cover, or keep Message-for-photos — do not invent `002.jpg` because OD HQ listed two files in the contract. Live `/products/A01/001.jpg` 404’d in `09`; only `cover.jpg` is proven on the CDN this pass.
- Pinch-zoom: do not `touch-action: none` the whole PDP just to own the gesture (Baymard users try native pinch first).

### 9.5 Motion

| Default | Reduced motion |
| --- | --- |
| Veil opacity 150–200ms; image opacity (no 1.08 pop) | Instant appear / disappear |
| Optional tiny scale 1.0→1.02 **only** if Reduce Motion is off | No scale |
| Close is immediate on Esc (do not wait for tween) | Same |

NN/G: overlay without a slide metaphor is how people hit **Back** and leave the site ([animation-purpose-ux](https://www.nngroup.com/articles/animation-purpose-ux/) WebMD accordion example). A **short** fade plus a visible ✕ beats a full-screen un-animated swap that feels like a new route. If you animate, keep the PDP visible (dimmed) so Back is not the close button.

### 9.6 Close vs find-card lesson

PR #14 / `sassy-closet/README.md`: closing the lightbox must **not** close the parent sheet. On the lookbook there is no find sheet — but a related-rail hover or a sticky Message footer must not eat the same click. Keep the deferred close.

---

## 10. Reduced-motion fallbacks

### 10.1 What “fallback” means

Not a second ugly theme. Same Kelly Ying type and gold rules. **Spatial** motion (translate, scale, VT snapshot zoom, infinite slide) becomes **opacity or instant**. State (selected tab, selected color, dialog open, Hold text) stays.

W3C C39: either disable motion in `@media (prefers-reduced-motion: reduce)` or **only enable** motion in `no-preference` ([C39](https://www.w3.org/WAI/WCAG22/Techniques/css/C39)). Chrome: you may keep a **subtle** VT that still shows relationship. Apple: fade instead of zoom.

JavaScript: `matchMedia('(prefers-reduced-motion: reduce)')` before `document.startViewTransition`. Chrome documents `skipTransition` for a site-level preference ([same-document guide](https://developer.chrome.com/docs/web-platform/view-transitions/same-document)). If Reduce Motion is on, call the DOM update **without** a transition (their `if (!document.startViewTransition)` fallback path).

### 10.2 APPLY matrix

| Effect | Default (live) | Reduce Motion target |
| --- | --- | --- |
| `announce-fade` 4.2s | Keep if Boss keeps an unnamed livestream bar | Already `animation: none` — bar stays **visible** (do not `display:none` the announcement) |
| `.shimmer` infinite 1.3s | Boutique sheen | Already none. **Also** wrap the infinite animation in `no-preference` so a forgotten class cannot loop. For 2.2.2 Level A, treat OS Reduce Motion as the pause **or** stop auto-play (prefer `no-preference` so the default can be still) |
| `cta-shine` / `cta-flash` | Hover sheen | Already none on `:hover:after` |
| Card lift + 1.08 zoom | `@media (hover:hover)` 500–800ms | **Gap:** add `translate: none; scale: 1; box-shadow: none` (or 120ms opacity only) |
| Gold underline width | 300–500ms | Instant `scale-x-100` on selected / focus-visible |
| Featured filter / color fade | 150–250ms opacity | Instant |
| View Transitions | Morph when names match | Already `animation: none` on groups — keep names for **identity**, not zoom |
| Lightbox | 150–200ms veil | Instant |
| `scroll-behavior` | — | Already `auto` |

### 10.3 Do not hide content in the fallback

- Hold badge, price or Inbox for price, Message CTA, mã — all visible with animations disabled.
- `opacity-0` hydration on related-rail images (live A02 thumb) must resolve without waiting for a hover animation.
- `aria-selected` / `aria-pressed` remain the source of truth if gold hairlines are the bits you skip.

### 10.4 Manual site toggle (optional, not a mã)

2.3.3 Understanding lists an **on-page** control as one way to meet the SC. A 10-SKU soft-launch does not need a settings cog if OS Reduce Motion is honored **including hover scale**. Do not invent a customer account to store the pref.

---

## 11. Timing budget (one table)

| Interaction | Feels direct (NN/G 0.1s) | Still in flow (≤1s) | Too long |
| --- | --- | --- | --- |
| Tab / color selected style | Ink/gold swap ≤100ms | 300ms live tab color is OK | 700ms+ “luxury” ease |
| Hero color crossfade | Start by 100ms | 150–250ms total | 800ms image scale |
| Category grid filter | Feedback at tap | ≤200ms settle | Waiting on ISR |
| Lightbox open | Veil starts immediately | 200ms | Entrance bounce |
| Card hover | — | 500ms lift is hover-only | 800ms zoom **and** Reduce Motion still on |
| Home → PDP | Navigation starts on click | VT ≤300ms if used | Block Message until tween ends |
| Announce | Ambient | 4.2s one-shot | Infinite loop |
| Shimmer | — | — | `infinite` (2.2.2 / attention) |

Apple: frequent UI should not make people sit through custom motion every time ([HIG](https://developer.apple.com/design/human-interface-guidelines/motion)). Featured tabbing is frequent. Color tapping will be frequent once chips exist. Those two stay **short**.

---

## 12. Performance (so the boutique does not jank)

Janky 1.08 scale is worse than no scale. `06` already flags home preloading the hero + every category still + every cover as aggressive for LCP.

Motion-specific:

- Animate `transform` and `opacity` only (compositor). Do not animate `top` / `width` / `blur` on the full grid.
- `::view-transition { pointer-events: none }` stays.
- Do not run `shimmer-slide` on `prefers-reduced-motion` **or** `prefers-reduced-data` if you add the latter later — not required this pass.
- Related-rail `opacity-0` until JS is a reliability bug if JS is late — the cover must paint.
- ISR stale (300s) + a 500ms filter animation can show **old** counts. Filter from the **payload already on the page**, not from a refetch, unless the refetch is required for truth.

---

## 13. APPLY — [sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)

**Owner:** Origin `sassy-closet-shop` (not this kit).  
**Look:** Kelly Ying rhythm. **Motion:** keep the named keyframes; make them **tell the truth**.  
**Mã:** allowlist only. **No** Square Save. **No** FB Send. **No** cart.

### 13.0 Do not touch (lock — tick first)

- [ ] Cormorant Garamond + Be Vietnam Pro.
- [ ] Paper / ink / gold / blush; `ma-mark`; 11px tracking; gold underline language.
- [ ] Keyframes `announce-fade`, `shimmer-slide`, `cta-flash` and classes `announce-fade`, `shimmer`, `cta-shine` **remain in the CSS file** (you may stop **auto-playing** them — do not “clean up” the brand).
- [ ] Featured chips All / Tops / Sets / Accessories / Jackets / Hair + counts that sum to **10**.
- [ ] Livestream rail + Page `61594312648057`.
- [ ] Message-first CTAs; footer **Zelle** word; no personal name.
- [ ] Hold treatment on **P02, P05** (no published `$`).
- [ ] `/admin` out of the main nav.
- [ ] Intake host unchanged.

### 13.1 Category switch

- [ ] Featured `tablist` filters the **same** ten as `/` and `/c/*`. Tops = A01+A02; Accessories = P01–P05 including both Holds.
- [ ] Empty kinds (`/c/quan` and any other zero-count letter) stay empty — copy, not a minted tile.
- [ ] Selected tab: gold rule + `aria-selected="true"`; keyboard per [APG Tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/).
- [ ] Filter motion ≤200ms; Reduce Motion = instant. No second shimmer while filtering.
- [ ] Do not sync Kelly Ying collection names (Sleepwear, Kids, Cosmetics) onto this grid.
- [ ] Home “N pieces” matches the selected tab’s allowlist count.

### 13.2 Color → gallery (only after admin has real `colors[]`)

- [ ] Customer chips = **recorded names** on that mã (`05` §3.2). No chips while live arrays are empty.
- [ ] Text only. `cham-bi` stays “Chấm bi”. `hoa` stays “Hoa”. No invented hex.
- [ ] Activating a name filters hero + thumbs + lightbox **for this mã**.
- [ ] Crossfade 150–250ms on the image; Reduce Motion instant.
- [ ] Size (if shown) does not swap folders.
- [ ] Missing bind → Message {MA} / empty, never `/products/A02/cover.jpg` on A01.
- [ ] Do not mint `A03` “for the other color.”

### 13.3 Lightbox

- [ ] Trigger is a button; `aria-label` in VI+EN (“Xem ảnh lớn” / enlarge).
- [ ] Dialog: `role="dialog"`, `aria-modal="true"`, labelled; Esc; ✕; backdrop; focus in; focus restore; body scroll lock; deferred close (PR #14 contract).
- [ ] Chrome is ink/gold/paper, not intake rose.
- [ ] Set is the current color filter; arrows do not leave the mã.
- [ ] Only files that already 200 on this host (today: `/products/{MA}/cover.jpg`). Do not invent `001.jpg` on the CDN because OD HQ listed it.
- [ ] Reduce Motion: no scale pop. Esc closes without waiting.
- [ ] Sticky Message CTA is not under an inert veil without a way out (close first).

### 13.4 Reduced-motion + hover gap

- [ ] Keep the live `prefers-reduced-motion` kills for announce / shimmer / cta-shine / VT animations.
- [ ] **Add** Reduce Motion kills (or `no-preference` wrappers) for card `-translate-y-1.5` and `scale-[1.08]`.
- [ ] Put **infinite** `shimmer-slide` behind `prefers-reduced-motion: no-preference` (2.2.2 / attention). Selected gold rule does not depend on shimmer.
- [ ] `startViewTransition` skipped when `matchMedia('(prefers-reduced-motion: reduce)')` matches.
- [ ] Put `view-transition-name: product-{MA}` on the **PDP hero** of that mã (A01 hero → `product-A01`, P02 hero → `product-P02`, …). Related-rail keeps **its** mã’s name, not the page’s.
- [ ] `@view-transition { navigation: auto }` on lookbook documents if you want MPA morph — both sides, same-origin only ([Chrome](https://developer.chrome.com/docs/web-platform/view-transitions/)).
- [ ] Header overlay `pointer-events: none` stays.

### 13.5 Reliability / commerce (motion-adjacent)

- [ ] Mid-animation, Hold is still the word Hold; P02/P05 have no `$`.
- [ ] Message {MA} works during and after VT.
- [ ] No cart, bag, Shop now, or flying-thumbnail-to-cart.
- [ ] No countdown, no fake stock pulse, no “1 in warehouse” ticker (`07` §11.1–11.2).
- [ ] Do not print Kelly Ying’s **$10 / $300+** or their `V###` codes.

### 13.6 Verify (Origin, after motion work)

Exercise like a customer, then with Reduce Motion on (OS), then keyboard-only:

1. Home Featured: All → Tops → Accessories → All. Counts 10 / 2 / 5 / 10. P02 still Hold.
2. Home A01 card → `/m/A01`. In Chrome with motion on: tile should morph **into A01’s hero** once names match. Neighbor A02 must not be the morph target.
3. `/c/ao` still two tops, $25 / $22. `/c/quan` still empty.
4. `/m/P02` / `/m/P05`: no dollar; Message still opens the Page.
5. If any mã has customer colors in admin (do not invent them): tap each **word**; gallery follows; Reduce Motion instant.
6. If lightbox shipped: open from A01 cover; Esc / ✕ / backdrop; focus returns; Message still there after close.
7. Reduce Motion: no shimmer slide, no announce loop, no 1.08 zoom, no VT zoom; tabs and Message still work.
8. Hover-less phone: tiles open without requiring lift.
9. View-source: no `e.tb.cn`, no ¥, no customer names, no `A03`.

Kit-side: `validate_sell_catalog.py` on a real export before re-import. This PR does not run Origin.

### 13.7 Out of scope

- New official Vercel clone (`CLONE_TO_OFFICIAL.md`).
- Intake tab motion / fifth tab (`BOSS.md`).
- Square Online theme, Horizon, AR, 360, auto-play lookbook video.
- Inventing titles, hex, ship `$`, or livestream days.

---

## 14. Anti-patterns (quick refuse list)

1. Minting `A03` / `Q01` / `AO001` so a category or color “has something to animate.”  
2. Copying Kelly Ying `V984` or `$10 / $300+` onto a tile.  
3. Hue-only dots as the color control.  
4. Color tap that leaves a mixed gallery or another mã’s cover.  
5. Lightbox that cannot Esc, or that closes the whole PDP / find sheet.  
6. Infinite shimmer as the only Hold/Available cue.  
7. Hover zoom that still runs with Reduce Motion.  
8. `product-A01` view-transition name on A02’s hero.  
9. Waiting for 800ms scale before `Message A01` is clickable.  
10. Cart-bag microinteraction “to feel like a real shop.”  
11. Parallax hero, cursor-follow zoom, WebGL cloth, auto-play video.  
12. Restyling to intake rose / Allura to “match the kit.”  
13. Skeleton tiles that look like stock on `/c/quan`.  
14. Countdown Hold clocks (NN/G dark pattern; `02` §15).  
15. Translating `A01` → `AO001` in a caption that rides the animation.

---

## 15. Acceptance (sell-test motion)

A reviewer can fail the page against this list without a redesign argument:

- [ ] Every mã that moves on screen is on the allowlist and was **already assigned**.  
- [ ] Featured filter and `/c/*` show the same sets; empty stays empty.  
- [ ] P02 / P05 never display a dollar, including mid-tween.  
- [ ] Customer colors, if any, are **words** and filter **this** gallery.  
- [ ] Lightbox (if present) matches §13.3; if absent, no dead zoom control.  
- [ ] Reduce Motion: no infinite animation, no VT zoom, no 1.08 hover zoom; tasks still complete.  
- [ ] PDP hero `view-transition-name` matches **its** mã.  
- [ ] Message CTA never blocked by a transition overlay.  
- [ ] Fonts, gold, chips, no-cart CTA still match `01` / `07` locks.  
- [ ] Sources in §16 still explain every shop-law sentence.

---

## 16. Sources

### 16.1 Shop law and as-built

- `README.md` — Square SoT; Official working copy; bots draft; Facebook inbox; Cloud Agents.  
- `excel-kit/DESIGN_NOTES.md` — layers; `MA_RE`; refuse fake inventory / Shopify / US sizes.  
- `excel-kit/schema.py` — `ASK_STOCK_MA`; Dashboard next-mã; photo_link text only.  
- `excel-kit/square/README.md` — Track ON (Boss yes 2026-09-04); SKU = mã.  
- `excel-kit/prompts/FIND_MA_CARD_2026-09-08.md` — big mã; staged-only sentence; never invent qty/$.  
- `excel-kit/docs/SELL_CATALOG_CONTRACT.md` + `excel-kit/samples/sell-catalog.v1.json` (PR #18) — allowlist, prices, Hold P02/P05, recorded color ids.  
- `sassy-closet/BOSS.md`, `sassy-closet/README.md` — four tabs; Blob; lightbox; staged-only.  
- `sassy-closet/lib/kinds.ts` — `COLORS` including Hoa, Caro, Ánh kim, Khác.  
- `sassy-closet/lib/photos.ts` — `FIND_CARD_THUMB_LIMIT = 3`.  
- `sassy-closet/components/PhotoLightbox.tsx`, `PhotoThumbs.tsx`, `FindMaCard.tsx`, `SavedCard.tsx`, `IntakeApp.tsx`.  
- Sisters `01`–`09` (PRs #19–#27) — look lock, PDP nouns, recorded colors, MOT checklist.  
- Slack `#shop-decisions` (2026-09-04):  
  - [Channel law + Hold-past-24h **example**](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788541753903809)  
  - [Track stock ON proposal](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788553328521899)  
  - [Boss yes](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788553474026779)  
  - [Square LIVE](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788556083454949)  
  - [Soft-launch prep, draft only](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788557030839509)  
- Live host 2026-09-09: https://sassy-closet-shop.vercel.app , `/c/ao`, `/c/set`, `/c/phu-kien`, `/c/ao-khoac`, `/c/toc`, `/c/quan`, `/m/A01`, `/m/A02`, `/m/S01`, `/m/P02`, `/admin`, CSS `34vl_zddoo4ws.css`.  
- Kelly Ying Boutique — <https://www.kellyyingboutique.net/> (home + Dresses collection, 2026-09-09).  
- `01` also cites [Loc8NearMe](https://www.loc8nearme.com/california/garden-grove/kelly-ying-boutique/6384948/) and [Locality](https://localitybiz.com/32074742/kelly-ying-boutique-garden-grove) for the live+inbox pattern.

### 16.2 Motion / microinteraction research

- Nielsen Norman Group, *The Role of Animation and Motion in UX* — <https://www.nngroup.com/articles/animation-purpose-ux/>  
- Nielsen Norman Group, *Animation for Attention and Comprehension* — <https://www.nngroup.com/articles/animation-usability/>  
- Nielsen Norman Group, *Microinteractions in User Experience* — <https://www.nngroup.com/articles/microinteractions/>  
- Nielsen Norman Group, *UX Guidelines for Ecommerce Product Pages* — <https://www.nngroup.com/articles/ecommerce-product-pages/>  
- Jakob Nielsen, *Response Time Limits* (0.1 / 1 / 10s) — <https://www.nngroup.com/articles/response-times-3-important-limits/>  
- Apple HIG, *Motion* — <https://developer.apple.com/design/human-interface-guidelines/motion>  
- Apple, Reduced Motion evaluation criteria — <https://developer.apple.com/help/app-store-connect/manage-app-accessibility/reduced-motion-evaluation-criteria/>  
- WWDC23, *Design considerations for vision and motion* — <https://developer.apple.com/videos/play/wwdc2023/10078/>  
- Chrome, *Smooth transitions with the View Transition API* — <https://developer.chrome.com/docs/web-platform/view-transitions/>  
- Chrome, same-document VT + reduced motion — <https://developer.chrome.com/docs/web-platform/view-transitions/same-document#handling_reduced_motion_preferences>  
- MDN, View Transition API — <https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API>

### 16.3 Accessibility

- W3C, WCAG 2.2 Understanding SC 2.2.2 Pause, Stop, Hide — <https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html>  
- W3C, WCAG 2.2 Understanding SC 2.3.1 Three Flashes — <https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html>  
- W3C, WCAG 2.2 Understanding SC 2.3.3 Animation from Interactions (AAA) — <https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html>  
- W3C technique C39 (`prefers-reduced-motion`) — <https://www.w3.org/WAI/WCAG22/Techniques/css/C39>  
- W3C, WCAG 2.2 Understanding SC 1.4.1 Use of Color — <https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html>  
- W3C, WCAG 2.2 Understanding SC 2.5.8 Target Size (Minimum) — <https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html>  
- WAI-ARIA APG, Dialog (Modal) — <https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/>  
- WAI-ARIA APG, Tabs — <https://www.w3.org/WAI/ARIA/apg/patterns/tabs/>  
- MDN, `prefers-reduced-motion` — <https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion>  
- Motion Spec, *WCAG 2.3.3 is AAA; 2.2.2 is the Level A loop* — <https://motionspec.dev/blog/wcag-2-3-3-animation-from-interactions>

### 16.4 Gallery / zoom (industry)

- Baymard, *Ensure Sufficient Image Resolution and Zoom* — <https://baymard.com/blog/ensure-sufficient-image-resolution-and-zoom>  
- Craftshift, Shopify variant images / mixed gallery — <https://craftshift.com/shopify-variant-images-complete-guide/>  
- Shopify Community, Horizon hide-unselected-media limits — <https://community.shopify.com/t/horizon/659928>  
- A11yFix, lightbox keyboard/focus traps — <https://blog.a11yfix.dev/blog/product-image-zoom-lightbox-accessibility/>

### 16.5 Weaker / vendor sources (directional only)

Theme posts that claim “+X% conversion from microinteractions” without a public method are **not** shop law. Prefer NN/G, WCAG, Baymard, Chrome, Apple, this repo, and the live CSS.

---

## 17. Open questions (do not answer by inventing)

1. Will Featured tabs stay on `/` (client filter) or should they push `/c/*` for shareable URLs (`06` wants unique category descriptions either way)?  
2. When do first-ten `colors[]` get **saved** on sell-test admin (recorded hub names in `05` §3.2 vs live empty)? Do not chip them early.  
3. Is `/products/{MA}/001.jpg` going to be wired, or is `cover.jpg` the only public file? Lightbox must follow **200s**, not the OD table.  
4. After Granola/Notion access: did a meeting already pick hover-zoom-off vs fade-on-reduce? This file treats C39 + Apple “fade not zoom” as the standing instruction.  
5. Livestream **days**: Boss still has not locked a cadence (`01`). Motion cannot invent Sunday/Monday just because Kelly Ying printed them.

---

## 18. One-page APPLY card (tear-off)

```text
SELL-TEST MOTION — Sassy Closet lookbook
Look: Kelly Ying rhythm (Cormorant / Be Vietnam / ink-gold-paper). NO cart.
Keep: announce-fade · shimmer-slide · cta-flash · gold rule · VT names
Category: Featured tabs filter the TEN. Empty /c/quan stays empty. No Q01.
Color: TEXT chips only when stored. Filter THIS mã. 150–250ms fade.
Lightbox: PR #14 behavior, lookbook chrome. Esc / focus / no other folder.
Reduce: kill loops + VT zoom + 1.08 hover. Instant state. Header clickable.
Hero VT name = this mã (A01→product-A01). Never morph into the neighbor.
Hold P02/P05: word Hold, no $. Message stays the CTA.
Never invent mã / hex / $ / V984 / $10-over-$300.
Store: Facebook inbox. Bots draft. No Save. No Post.
```

End of 10.
