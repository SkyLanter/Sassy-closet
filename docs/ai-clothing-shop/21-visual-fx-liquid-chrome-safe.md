# 21 — Visual FX: liquid chrome, safe (shader-light)

**Learn track:** Ultra burn (research + live as-built + APPLY). Fast OFF.  
**Shop:** Sassy Closet — Facebook inbox is the store; Square Free is on-hand truth; sell-test lookbook is Origin-owned.  
**Live APPLY target:** [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)  
**Audience:** Mini Boss / Origin shop implementer / whoever wants “liquid chrome” without wrecking covers or melting a phone.  
**Date researched / crawled:** 2026-09-09.  
**This file does not assign stock, mint a mã, Save in Square, post to Facebook, restyle the boutique, or touch Excel / intake.**

Sister `10` is general motion law. Sister `13` is watery **tab + grid pour**. This note is the **material safety sheet**: which FX primitives are allowed, which are a fabric lie, and how to get a chrome *edge* on **chrome** without WebGL. Mini Boss pastes **§18** into the Origin agent. Do not paraphrase §18 into “add liquid glass over the photos.”

---

## 0. How to read this document

This is a **learn-track** note, not a rebuild brief and not permission to fork Origin shop code from this kit repo.

- **Cite, don’t invent.** Shop-law claims point at a file, Slack permalink, sister learn-track, or the live host. Industry claims point at NN/G, W3C Filter Effects / WCAG 2.2, MDN, Chromium filter-path notes, Lucas Bebber’s goo filter, Paper Design’s liquid-metal shader docs, or Argent’s “metal is the edge” write-up. If a fact is missing, the gap is named.
- **Never invent a mã.** Customer-facing codes this pass may name are the **first-ten allowlist** only. Admin “Next mã A03” is a prediction. Slack `AO001` / `AO003` are **decision-template examples** (`#shop-decisions`, 2026-09-04), not live lookbook stock. Kelly Ying `V984.` / `V826.` are **their** SKUs — do not copy them onto Sassy tiles.
- **Two alphabets.** Sell-site / hub = `A01`. Official / Square / SoT = `AO001`. FX never translates one into the other (`01` §9; `excel-kit/schema.py` `MA_RE`).
- **Facebook inbox is the store.** A “buy” is **Message {code}**. There is no cart. Chrome FX that implies checkout (liquid-into-bag, metallic “Shop now”) is a lie.
- **No redesign mandate.** Improve **inside** paper / ink / gold / blush, Cormorant Garamond + Be Vietnam Pro, `ma-mark`, `announce-fade`, `shimmer` / `shimmer-slide`, `cta-shine` / `cta-flash`, gold `h-px` underline, `layoutId: "featured-tab"`, `view-transition-name: site-header` / `product-{MA}`. Do not replace that language with iOS liquid glass over photography, Shopify Horizon, intake Allura/Nunito rose, or a new design system.

### 0.1 Research method (and what this pass could not see)

| Source | Result |
| --- | --- |
| Live sell-test HTML + CSS + JS of `/` and `/m/A01` (2026-09-09) | Primary **as-built** chrome vs cover map. CSS chunk `/_next/static/immutable/chunks/34vl_zddoo4ws.css`. Motion chunk `/_next/static/immutable/chunks/3_93acjqq2t4q.js`. |
| `curl -I` `/` | `x-nextjs-prerender: 1`, `x-vercel-cache: STALE` this pass — catalog still prerendered. |
| Repo `excel-kit/`, `sassy-closet/`, `README.md` | Shop law. Intake sheets are **behavior** only — do not restyle. **This PR does not edit them.** |
| Sister LEARN TRACK PRs #19–#33 (`01`–`14`) | Headings + locks. This file is `21` (FX lane; `15`–`20` may land from sibling FX agents). |
| Slack `#shop-decisions` (`C0BV3GYC602`) | Five standing messages (2026-09-04). No visual-FX thread. |
| Linear | Keyword search “liquid chrome” / “visual fx” — empty. |
| Granola meetings | MCP unauthorized (no Granola account) — **Kelly Ying meeting notes were not available this pass.** Look / cadence facts stay with `01` + `10`. |
| Notion | Workspace connected; Business-plan AI search unavailable. Keyword search returned no shop FX pages. |
| Kelly Ying Boutique public site | Cloudflare challenge this pass (`cf-mitigated: challenge`). Look facts stay with `01` / `10` (paper/ink/gold, SKU-on-card, not iOS glass). |
| Public FX / filter / mobile-perf specs | Fetched 2026-09-09. URLs in §17. |

If a later crawl disagrees with a **live** cell here, **the new crawl wins** — update the date line. Shop law still wins over industry taste.

### 0.2 Sister docs

| # | File | Job vs this note |
| --- | --- | --- |
| 01 | `01-messenger-social-commerce.md` | Kelly Ying look lock; Message-first; no cart |
| 02 | `02-pdp-color-size-ux.md` | Customer **text** colors; gallery sync |
| 09 | `09-bugcheck-sell-site-checklist.md` | Tick-box QA; MOT-01…MOT-08 |
| 10 | `10-customer-pleasing-motion-ux.md` | General motion law + five Origin reliability fixes |
| 13 | `13-watery-tab-slide-motion.md` | Watery **tab meniscus + grid pour**; optional goo on the **gold-rule wrapper only** |
| **21** | **This file** | **Liquid chrome FX; shader-light; chrome only; never wreck covers** |
| Kit | `SELL_CATALOG_CONTRACT.md` (PR #18) | Allowlist + prices + Hold null `$` |

`13` already forbade goo / displacement on photos. This note **names the primitives**, the mobile cost, the Chromium-only traps, and the **chrome-edge recipe** Origin should ship instead of a shader over `cover.jpg`.

---

## 1. Executive summary

“Liquid chrome” on a boutique lookbook is **a 1–2px metal film on UI chrome**. It is not a material poured over garments. If the buyer can see the print, the weave, or the thermos graphic **wobble**, the FX has failed — even if the GPU is happy.

Paper Design’s Liquid Metal shader is the current high-end recipe: a hard light→dark stripe ramp (faux environment), curvature along a silhouette, simplex noise for “liquid,” and per-channel sampling for prismatic fringe ([Paper Liquid Metal](https://shaders.paper.design/liquid-metal); [shader source](https://github.com/paper-design/shaders/blob/main/packages/shaders/src/shaders/liquid-metal.ts)). Argent’s production lesson is the one that matters for us: **the metal is the edge, not the background**. Full-surface chrome reads as “a website made of hubcaps.” A quiet panel with a liquid-metal **rim** is the default; fill is opt-in on hover ([Sean Geng, *Building a liquid-metal UI kit*](https://seangeng.com/writing/building-a-liquid-metal-ui-kit)).

Sassy Closet’s sell-test is already a Kelly Ying *rhythm*: paper `#fff`, ink `#111`, gold `#b08968`, blush `#f3eee8`, Cormorant wordmark, Be Vietnam UI, gold `h-px` hairlines, `cta-shine` footers. Live CSS (2026-09-09) has **zero** `goo`, `feDisplacementMap`, or WebGL. Live covers are `/products/{MA}/cover.jpg` inside `aspect-[3/4]` tiles, with a `.shimmer` overlay **on top of the photo**. PDP `/m/A01` hero is a plain `<img>` with **no** view-transition name on the hero (related rail wrongly names `product-A02` — `10` FIX 3).

So the job this pass is **not** “add a shader.” It is:

1. **Define chrome** (header, tab hairline, Message CTA rim, announce bar) vs **covers** (product photos, editorial stills, shimmer, lightbox, view-transition groups named `product-{MA}`).
2. **Pick shader-light techniques** that stay on the compositor on a mid-range phone: CSS metallic **rims** (static conic + `transform: rotate` of an oversized layer), optional Lucas Bebber **SVG goo on a dedicated gold-rule wrapper**, never `feTurbulence` + `feDisplacementMap` on an `<img>`.
3. **Refuse** Paper `LiquidMetal` with `image={cover.jpg}`, `backdrop-filter: url(#displace)`, and per-card canvases.

Reliability still beats beauty. Distorted A01, an unreadable Hold badge on P02, a Firefox-transparent header (because `backdrop-filter: url()` parsed then painted nothing), or ten WebGL contexts under a 2-column grid is a **failed** boutique.

---

## 2. Hard constraints (print these on the implementer’s wall)

1. **Never invent a mã.** Emit list is exactly `A01 S01 P01 P02 P03 P04 P05 K01 H01 A02` (PR #18). Empty `/c/quan` stays empty. No `Q01` “so the chrome demo has a tile.”
2. **Never invent qty, $, photos, hex, or color names.** Hold P02 / P05 = **Inbox for price**. Empty `colors[]` = no chips (`02`; `05`; `10` §8).
3. **Square Free = on-hand truth.** Official Excel is a working copy (`README.md`). **This kit does not edit Excel or intake in this pass.**
4. **Bots draft only.** No Square Save, no Facebook Post/Send ([`#shop-decisions` 2026-09-04](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788541753903809)).
5. **No cart, Shop now, or bag-fly.** Kelly Ying’s **$10 / $300+** and `V###` codes are **theirs** (`01` §0).
6. **Customer colors are text** (WCAG [1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)).
7. **FX never changes identity.** Same mã in, same mã out. `product-A01` morphs only to A01. Chrome FX must not drop P02/P05 or blur “Hold” into “Available.”
8. **Water / chrome never lies on the photo.** No `filter: url(#goo)` on `.shimmer`, covers, editorial stills, or heroes. No `feDisplacementMap` / `feTurbulence` over garments. Distortion is a **fabric lie**.
9. **Origin owns the pixels.** APPLY is for the Origin agent on `sassy-closet-shop`. Intake Production stays https://sassy-closet.vercel.app. This PR does not edit `excel-kit/` or `sassy-closet/`.

---

## 3. What “liquid chrome” means here (and what it is not)

### 3.1 Chrome the UI, not chromium the OS

Two words collide:

| Word | In this note | Fail if… |
| --- | --- | --- |
| **Chrome** | Browser/UI **chrome**: sticky header, tab hairline, CTA border, announce bar, category hairlines. The stuff that is **not** the garment. | Treating the product tile as “chrome” because it has a border |
| **Chrome (metal)** | A **thin** gold/ink metallic film that reads as polished metal on those UI edges | Filling a card, wordmark, or photo with hubcap chrome |

Apple “Liquid Glass” (2025–26) is refraction of **whatever sits under** a control ([LogRocket, CSS/SVG liquid glass](https://blog.logrocket.com/how-create-liquid-glass-effects-css-and-svg/); [Ekino](https://www.ekino.fr/publications/liquid-glass-in-css-and-svg/)). On a lookbook the thing under the control is **the clothes**. Frosting or displacing that is the opposite of a boutique.

Kelly Ying *look* on this shop is **paper and ink with a gold hairline** (`01` §1.3; live `:root` `--paper` / `--ink` / `--gold`). It is not iOS glass, not a dark metal dashboard, not intake rose `#D82B60`.

### 3.2 Argent’s default, mapped onto Sassy

Argent’s shipped default after the hubcap mistake ([Geng](https://seangeng.com/writing/building-a-liquid-metal-ui-kit); [github.com/seangeng/argent](https://github.com/seangeng/argent)):

> The metal is the **edge**, not the background. A quiet panel with a liquid-metal rim; `revealOnHover` may flood the surface. Calm until you touch it.

Sassy mapping:

| Argent idea | Sassy Closet |
| --- | --- |
| `variant="border"` default | Gold / metallic **rim** on header bottom, Featured hairline, Message CTA `border` |
| `variant="fill"` | **Refuse** on cards, photos, editorial mosaic |
| `revealOnHover` fill | Optional **only** on the Message CTA interior shine — live already has `.cta-shine:after` `cta-flash`. Do not replace it with a shader fill |
| Shader text | **Refuse.** Wordmark stays Cormorant ink. `background-clip: text` metal would fight `--ink` and WCAG contrast |
| Per-surface WebGL canvas | **Refuse** on the 10-tile grid. See §6 |

### 3.3 NN/G jobs, mapped onto FX

| NN/G job | Liquid-chrome meaning | Fail if… |
| --- | --- | --- |
| Feedback | CTA rim reacts within **0.1s** of hover/focus ([NN/G attention](https://www.nngroup.com/articles/animation-usability/)) | Chrome spin is the only cue that Message is tappable |
| State change | Selected tab still `aria-selected` + gold `h-px` | Goo is the only selected cue (fails 1.4.1 if it disappears in Safari) |
| Spatial metaphor | Header stays a **header** (`view-transition-name: site-header` already frozen) | Displacement on `::view-transition-old(product-A01)` |
| Signifier | Hairline is tappable chrome; phone does not need hover | Chrome only on `@media (hover:hover)` |
| Attention | One moving gold film (tab **or** CTA, not both looping) | Goo + shimmer + conic spin + stagger + VT (Hipmunk pile-on — NN/G) |

NN/G: animation must be **unobtrusive, brief, and subtle**. Use it for feedback and state — not delight, not downtime ([*The Role of Animation and Motion in UX*](https://www.nngroup.com/articles/animation-purpose-ux/)). A 6s liquid wipe or a always-on metal ocean behind the grid is downtime.

### 3.4 Technique catalog (use / refuse)

| Technique | Source | Use on sell-test? |
| --- | --- | --- |
| Live gold `h-px` + `layoutId: "featured-tab"` | Live JS `3_93acjqq2t4q.js` | **Already chrome.** Keep. `13` adds meniscus. This note does not replace it. |
| CSS metallic **rim**: padding-box fill + conic/linear on border-box, or `mask-composite: exclude` ring | [conic.style](https://www.conic.style/css-conic-gradient/); [mask-composite demos](https://codefronts.com/reference/css/mask-composite/) | **Preferred default** on header bottom + Message CTA. See §8. |
| Compositor-safe spin: oversized **static** gradient + `transform: rotate` | [DEV: animated gradient borders](https://dev.to/ericwoooo_kr/css-animated-gradient-borders-without-a-single-line-of-javascript-2k) | **Preferred motion** for the rim. Do **not** animate `@property --angle` on a large surface (repaint every frame). |
| SVG goo (`feGaussianBlur` + `feColorMatrix` alpha) | [Bebber / CSS-Tricks](https://css-tricks.com/gooey-effect/); [Codrops 2015](https://tympanus.net/codrops/2015/03/10/creative-gooey-effects/) | **Optional, gold-rule wrapper only** (`13` FIX 1). Never on photos. Safari-on-DOM caveat: degrade to hairline. |
| `feDisplacementMap` + `feTurbulence` “liquid glass” | Envato / LogRocket liquid-glass posts; [TheLinuxCode displacement guide](https://thelinuxcode.com/svg-fedisplacementmap-practical-guide-to-organic-distortion/) | **Refuse on photos and on `backdrop-filter`.** Chromium-mostly; Firefox/Safari drop `url()` in `backdrop-filter` ([BCD #24110](https://github.com/mdn/browser-compat-data/issues/24110); [Mozilla 1808785](https://bugzilla.mozilla.org/show_bug.cgi?id=1808785)). |
| Paper `@paper-design/shaders-react` `LiquidMetal` | [shaders.paper.design/liquid-metal](https://shaders.paper.design/liquid-metal) | **Refuse** with `image` = cover/editorial. **Refuse** `shape="none"` full-card fill. Not needed for a 10-SKU lookbook. |
| CSS `backdrop-filter: blur()` only | MDN `backdrop-filter` | Header already uses an **opaque-enough** paper overlay (`opacity: 0.92`). Do not add glass. Blur over a scrolling grid of photos is still a photo effect. |
| CSS `shape()` liquid ooze | [Temani Afif, CSS Tip](https://css-tip.com/sliding-liquid/) | **Refuse as a full-page veil** (`13` §3.3). |
| WebGL cloth / cursor metaballs | vendor demos | **Refuse** (`10` anti-pattern). |

---

## 4. Why displacement maps wreck product photos

This is the hard rule the prompt named. Spell it so Origin cannot “just turn the scale down.”

### 4.1 What `feDisplacementMap` actually does

`feDisplacementMap` takes two inputs: `in` (the pixels to move) and `in2` (the map). For each destination pixel it reads a channel from the map and **moves** the source sample by `scale` ([Codrops, 2019](https://tympanus.net/codrops/2019/02/12/svg-filter-effects-conforming-text-to-surface-texture-with-fedisplacementmap/)). Typical “organic / liquid / hand-drawn wobble” recipes chain `feTurbulence` (procedural noise) into that map and animate `baseFrequency` or `seed` on a timer.

On a **logo silhouette** that is the point. On a **garment photo** that is a **lie about the cloth**:

| Pixel | What the buyer needs | What displacement does |
| --- | --- | --- |
| Print / chấm bi / stripe | True pattern so they Message the right piece | Warps the print so A02’s chấm bi looks like a different fabric |
| Seam, neckline, thermos graphic | Honest still | Melts the object; Hold P02 becomes a lava lamp |
| Status badge sitting **on** the tile | “Hold · Inbox for price” readable | Filter on the card composites badge + photo into one wobble |
| `.shimmer` gold sweep | Decorative overlay, already 1.3s infinite | Displacement + shimmer = two lies, extra paint |

FTC-adjacent honesty (`05`): we already refuse invented colorways and fake reviews. **Warping the only photo of a unique piece** is the same class of lie, just in the compositor.

### 4.2 Performance: this is not a 2px CSS blur

Developers repeating `feTurbulence` + `feDisplacementMap` for “alive illustration” report **CPU cores pinned**, phones hot, battery gone — even on laptops ([coverage of SVG-filter CPU cost](https://finance.biggo.com/news/202507211315_SVG_Filter_Performance_Issues)). Chromium’s own filter-path note: many SVG-on-content filters historically ran on **CPU**; GPU path is not a given for `url(#svgFilter)` on arbitrary DOM ([Chromium *Filter Effects*](https://www.chromium.org/developers/design-documents/image-filters/)).

A 3/4 cover at 2-column phone width is already a large texture. Ten of them (home All) with an animated displacement each is a **thermal** decision, not a taste decision.

`feDisplacementMap` `scale` on a ~600×400 surface is quoted in the **6–15ms** range on a laptop for a *static* map; animated turbulence is worse ([TheLinuxCode](https://thelinuxcode.com/svg-fedisplacementmap-practical-guide-to-organic-distortion/)). Home has **ten** covers plus **six** editorial stills. Do not put that graph on any of them.

### 4.3 Engine traps (even if you swear it is “chrome”)

1. **`backdrop-filter: url(#filter)`** — Chromium may distort the backdrop; **Firefox and Safari do not** reliably. Firefox can **parse the declaration as valid** (`@supports` lies) and then paint **nothing**, punching a transparent hole ([BCD #24110](https://github.com/mdn/browser-compat-data/issues/24110); [Vaso issue: fallback ladder](https://github.com/huozhi/vaso/issues/11); [r/css fallback ladder](https://www.reddit.com/r/css/comments/1u5kwvx/liquid_glass_in_css_needs_a_fallback_ladder/)). If that declaration is on `site-header`, the sticky header **vanishes** on iPhone. Forbidden.
2. **Tainted maps** — Filter Effects treat some `feImage` / cross-origin inputs as tainted; `feDisplacementMap` then **pass-through**s with no error ([Filter Effects restrictions](https://www.w3.org/TR/filter-effects-1/#fedisplacemnentmap-restrictions); historical timing-attack CVEs around displacement ([MFSA 2014-28](https://www.mozilla.org/en-US/security/advisories/mfsa2014-28/))). Cover URLs that ever go cross-origin Blob without CORS become **silent no-ops or worse**. Do not build merchandising on that.
3. **Safari goo bulge** — even *without* displacement, `feGaussianBlur` + `feColorMatrix` goo **clips** the blur to the default filter region on Safari/iOS unless `x/y/width/height` are expanded ([SO 57742561](https://stackoverflow.com/questions/57742561/svg-bulge-on-ios-safari-with-filter-fegaussianblur-and-fecolormatrix)). Isolated circles **inflate**. Fine for a 1px gold rule with an expanded region; **fatal** on a photo (the garment grows a halo).

### 4.4 LCP / view transitions

Home covers are LCP candidates. `opacity-0` on those `<img>` is already a reliability bug (`10` FIX 2). Adding a filter that requires the image to be a filter input:

- delays first paint of the **real** pixels,
- fights `view-transition-name: product-{MA}` (the morph would transition a **warped** bitmap),
- makes Reduce Motion harder (you must remember to `filter: none` on every selector).

**Rule:** if the node’s job is “show the garment,” it does not get a filter graph. Period.

---

## 5. Shader-light ladder (mobile-first)

Goal: look expensive on a 2022 Android and an iPhone SE, **without** a WebGL context per tile.

### 5.1 Cost order (cheap → expensive)

| Tier | Primitive | Typical cost | Allowed surface |
| --- | --- | --- | --- |
| **0** | `border-line` / gold `h-px` / `cta-shine` translate | Compositor (`transform` / opacity) | **Already live.** Keep. |
| **1** | Static metallic gradient on a **2px ring** (`mask-composite: exclude` or padding-box / border-box clip) | Paint once; then idle | Header hairline, CTA ring |
| **1b** | Same ring, motion via **`transform: rotate` on an oversized pseudo** (parent `overflow: hidden`) | Compositor | **One** looping rim max (prefer CTA hover-only, not always-on) |
| **2** | Bebber goo on a **tiny** wrapper (gold rule + optional trail only) | Filter raster of a ~tab-width × 8px strip | Featured selected underline wrapper |
| **3** | `backdrop-filter: blur(8px)` (CSS functions only, **no** `url()`) | Extra backdrop copy | **Not needed** — header already `bg-paper` + 0.92 overlay |
| **4** | Animated `feTurbulence` / `feDisplacementMap` | CPU; thermal | **Never** |
| **5** | Paper `LiquidMetal` / any WebGL | GPU context + JS rAF | **Never** on grid/PDP photos. Not this APPLY. |

### 5.2 Why “animate the gradient angle” is the fake cheap path

Registering `@property --angle` and keyframing `conic-gradient(from var(--angle), …)` **repaints the box every frame**. Cost scales with area ([conic.style performance note](https://www.conic.style/css-conic-gradient/)). A 48px spinner is free. A full-card or full-header animated conic is **not**.

**Do this instead:** paint a **static** conic (or a linear gold/ink/paper ramp that *reads* as metal) on a pseudo sized ~200%, then `animation: ky-rim-spin 8s linear infinite` on **`transform`**. Parent clips. Reduce Motion: `animation: none`; ring stays as a still gold/ink gradient.

### 5.3 Metallic stops that stay Kelly Ying

Do not introduce cyan/magenta “chrome logo” palettes. Stops must be **our tokens**:

```css
/* still, gold-on-paper metal — not Apple silver, not Paper default #aaaaac */
--ky-metal: conic-gradient(
  from 0deg,
  var(--gold-deep),
  var(--paper),
  var(--gold),
  var(--ink),
  var(--gold-deep)
);
```

If the rim is 1px, the buyer sees a **glint**, not a rainbow. Keep the ring **1px** (header, tabs) or **1.5px** (CTA). `h-1` / `rounded-full` fat pills are a restyle (`13`).

### 5.4 Goo, if used at all

Bebber’s graph ([CSS-Tricks, 2015-02-04](https://css-tricks.com/gooey-effect/)):

1. `feGaussianBlur` the **container’s children** (not the photos).
2. `feColorMatrix` alpha row `18 -7` (or `19 -9` for rectangles) to threshold.
3. `feComposite operator="atop"` (or `feBlend`) so RGB of the source sits on the goo.

**Laws:**

- Apply to the **container** of the gold rule(s), not to each tab button, not to `tablist`, not to `img`.
- Expand filter region: `x="-50%" y="-50%" width="200%" height="200%"` ([Safari clip](https://stackoverflow.com/questions/57742561/svg-bulge-on-ios-safari-with-filter-fegaussianblur-and-fecolormatrix)).
- `color-interpolation-filters="sRGB"` (Safari/WebKit perf folklore: linearRGB path is neglected — [SO 53145883](https://stackoverflow.com/questions/53145883/how-to-use-a-simple-svg-filter-on-safari-with-acceptable-performance-and-without)).
- **Do not animate** `stdDeviation` or matrix values. Animate **transforms** of the hairline spans only (`13` meniscus).
- One filter id (`ky-gold-goo`). Not ten.
- Behind `prefers-reduced-motion: no-preference` **and** `!useReducedMotion()`.
- Bebber: “resource intensive if applied to large areas.” A tab underline is small. A product grid is not.

2015 comments already recorded phones turning to a “shuddering shamble” on full-page goo ([CSS-Tricks comments, Tigt](https://css-tricks.com/gooey-effect/)). Believe them.

### 5.5 Why WebGL stays off this lookbook

Paper’s React component is honest about cost: every metal surface is a **WebGL canvas**; a grid of 200 metal buttons is a bad idea; SSR shows a CSS gradient until mount ([Argent README](https://github.com/seangeng/argent)). We have **ten** covers on `/`. Even **one** full-bleed liquid-metal hero using `cover.jpg` as `image` is the exact “wreck covers” failure: the shader **encodes the photo as a mask** (`toProcessedLiquidMetal` Poisson edge in R, alpha in G) and **repaints metal over it** ([Paper docs](https://mintlify.wiki/paper-design/shaders/shaders/liquid-metal)). That is not a rim. That is a new garment.

Browser WebGL context limits are finite. Ten canvases + Next hydration + Blob images is how a sell-test becomes unusable on a GF phone.

**This APPLY: zero WebGL.**

---

## 6. Mobile performance budget (write this on the PR)

Assume: 2-column grid, mid-range Android Chrome, iOS Safari, 60Hz. Featured tabbing is **frequent** (`13`).

| Budget | Number |
| --- | --- |
| Always-on animated FX layers on `/` | **≤ 1** (prefer **0**; live shimmer already occupies that slot — `10` / WCAG 2.2.2) |
| Goo filter instances | **0 or 1** (gold-rule wrapper) |
| Displacement / turbulence graphs | **0** |
| WebGL contexts | **0** |
| Tab filter perceived time | **≤ 200ms** (`10`, `13`) — this note does not add FX that lengthens it |
| Direct-tap chrome (CTA hover shine) | Already 0.7s `cta-flash` — do not add a second loop |

**Shimmer already spends the “always-on” budget** (`.shimmer` `1.3s infinite` on **ten** tiles). WCAG [2.2.2 Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) cares because it still moves after 5s. **Do not add a second infinite metal spin on the header** while shimmer runs. Prefer:

- CTA rim: **hover / focus-visible only** (`@media (hover: hover)` + `:focus-visible`), still, otherwise;
- Header: **static** 1px gold/ink gradient, no spin;
- Tab goo: only while `layoutId` is traveling, or skip goo and keep `13` scaleX meniscus.

If Origin wants a looping rim, they must **pause or kill shimmer** first (`10` FIX 1 / MOT-08). This note does not authorize both.

---

## 7. As-built map: chrome vs covers (cite the live host)

Crawl: 2026-09-09. HTML `/`. CSS `34vl_zddoo4ws.css`. JS `3_93acjqq2t4q.js`.

### 7.1 Tokens (do not rename)

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

Fonts: Be Vietnam Pro (`font-sans`) + Cormorant Garamond (`font-display`). Keyframes to **keep names**: `announce-fade`, `shimmer-slide`, `cta-flash`. Reduced-motion block already zeros those three plus `::view-transition-*`.

Live CSS contains **no** `goo`, **no** `displac`. `backdrop-filter` hits are Tailwind’s `--tw-backdrop-*` machinery, not a shipped glass header.

### 7.2 Chrome surfaces (FX **may** touch — rims / hairlines only)

| Surface | Live hook (2026-09-09) | Allowed FX |
| --- | --- | --- |
| Livestream bar | `.announce-fade` in `h-8 bg-ink` | **Keep fade.** Do not glass this; text is 10px paper on ink |
| Sticky header | `header.sticky … border-b border-line bg-paper` + `view-transition-name: site-header` + inner `absolute inset-0 bg-paper` `opacity: 0.92` | Optional **static** 1px gold/metal along `border-b` **instead of or under** `--line`. No `backdrop-filter: url()`. Do not animate the header (VT group already `animation: none`) |
| Wordmark | `a.font-display … text-ink` → `/` | **No metal fill.** Ink on paper |
| Header Messenger | `h-px w-0 bg-gold … group-hover/cta:w-full` | Keep hairline. `13` meniscus language if shared with tabs. No goo on the `<a>` (would blur “Messenger”) |
| Category nav | `nav … border-t border-line` `aria-label="Categories"` | Optional static gold hairline on **current** `/c/*` — not this APPLY’s job; do not glass the scroller |
| Featured tabs | `role="tablist"` `aria-label="Filter featured collection"`; selected `layoutId: "featured-tab"` `h-px bg-gold` `springSoft` | **Goo wrapper optional** (`13` FIX 1). Hairline stays `h-px` |
| Footer Message CTA | `cta-shine overflow-hidden rounded-full border border-line … hover:border-gold/70` | **Best chrome-rim candidate.** Ring only. Keep `cta-flash` on `::after` |
| Admin peek button | `fixed bottom-3 right-3 … h-8 w-8` | **No FX.** 32px target; leave it boring |

`springSoft` live: `{ type: "spring", stiffness: 420, damping: 32, mass: 0.72 }`.  
`filterSlide` live: enter `x: 28*dir` / `0.32s` ease `[.22,1,.36,1]`; exit `x: -22*dir` / `0.22s`; `AnimatePresence mode="wait"` (`13` already says that blank is too long). **This FX pass must not add filter graphs to `AnimatedProductGrid`.**

### 7.3 Cover / photo surfaces (FX **must not** touch)

| Surface | Live hook | Forbidden |
| --- | --- | --- |
| Product covers | `<img src="/products/{MA}/cover.jpg" class="… object-cover … group-hover:scale-[1.08] opacity-0">` | Any `filter`, `backdrop-filter`, SVG filter, canvas, mix-blend that samples the bitmap as a displacement source |
| Shimmer overlay | `.shimmer` `absolute inset-0 z-[1]` **on the tile** (ten instances) | Goo / displacement on `.shimmer` or its parent if that parent includes the `<img>` |
| Tile VT | `view-transition-name: product-{MA}` on the `aspect-[3/4]` wrapper | Custom VT `filter` / clip that warps the snapshot |
| Editorial mosaic | `/editorial/hero.jpg` `ao.jpg` `set.jpg` `phu-kien.jpg` `ao-khoac.jpg` `toc.jpg` | Same as covers — these are **still photographs** |
| PDP hero `/m/A01` | `<img src="/products/A01/cover.jpg" class="aspect-[3/4] w-full object-cover">` — **no** `product-A01` on the hero this crawl | `10` FIX 3 still applies. Do not “fix” it with liquid glass |
| Related rail on `/m/A01` | `view-transition-name: product-A02` on the neighbor card | Do not add FX that makes the wrong-mã morph prettier |

Allowlist covers (never invent files):

`/products/A01/cover.jpg` `S01` `P01` `P02` `P03` `P04` `P05` `K01` `H01` `A02`.

### 7.4 Header HTML (trimmed)

```html
<header class="sticky top-0 z-50 border-b border-line bg-paper"
        style="view-transition-name:site-header">
  <div class="absolute inset-0 bg-paper" aria-hidden="true" style="opacity:0.92"></div>
  <!-- wordmark + Messenger hairline + category nav -->
</header>
```

The 0.92 paper veil is **already** the anti-glass choice: readable ink, no refraction of the grid scrolling underneath. **Do not replace it with Liquid Glass.**

---

## 8. Chrome-only recipes (copy-safe)

These are **patterns**, not a new design system. Class names below are suggestions; match Origin’s existing tokens.

### 8.1 Static gold-metal rim (header `border-b`)

Keep `border-b`. Tint it toward gold without a filter:

```css
header.sticky {
  border-bottom-color: color-mix(in srgb, var(--gold) 55%, var(--line));
}
```

`@supports` already used live for `color-mix` on `.shimmer`. Same gate is fine. Reduce Motion: no change (static).

### 8.2 CTA liquid-chrome **edge** (hover / focus-visible)

Keep `.cta-shine` + `cta-flash`. Add a **ring** sibling that does not wrap the icon font:

```html
<!-- footer Message — keep existing classes; add a decorative ring -->
<a class="cta-shine … relative overflow-hidden rounded-full border border-line …">
  <span class="ky-chrome-rim" aria-hidden="true"></span>
  Message on Messenger
</a>
```

```css
.ky-chrome-rim {
  pointer-events: none;
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px; /* ring thickness */
  background: var(--ky-metal, var(--gold));
  mask:
    linear-gradient(#000 0 0) content-box,
    linear-gradient(#000 0 0);
  mask-composite: exclude;
  -webkit-mask-composite: xor;
  opacity: 0.85;
}
@media (hover: hover) and (prefers-reduced-motion: no-preference) {
  .cta-shine:hover .ky-chrome-rim,
  .cta-shine:focus-visible .ky-chrome-rim {
    /* OPTIONAL: rotate an INNER oversized layer, not the mask itself */
  }
}
@media (prefers-reduced-motion: reduce) {
  .ky-chrome-rim { animation: none; opacity: 1; }
}
```

If `mask-composite` is missing, fall back to live `hover:border-gold/70` — **already shipped**. Do not invent a JS library for a 1px ring.

**Never** put `filter: url(#goo)` on this `<a>`: it would blob the 11px type and the arrow.

### 8.3 Featured gold goo wrapper (optional; same as `13`)

```html
<svg width="0" height="0" aria-hidden="true" focusable="false">
  <defs>
    <filter id="ky-gold-goo" x="-50%" y="-50%" width="200%" height="200%"
            color-interpolation-filters="sRGB">
      <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur"/>
      <feColorMatrix in="blur" type="matrix"
        values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -7"
        result="goo"/>
      <feComposite in="SourceGraphic" in2="goo" operator="atop"/>
    </filter>
  </defs>
</svg>
```

Wrapper contains **only** `layoutId="featured-tab"` (+ optional trail). `filter: url(#ky-gold-goo)` on that wrapper, gated on no-preference. If Safari skips DOM filters, `h-px bg-gold` remains.

### 8.4 What Origin must grep to prove photos are clean

```bash
rg -n "feDisplacementMap|feTurbulence|LiquidMetal|liquid-metal" app components
rg -n "filter:\\s*url\\(|backdrop-filter:.*url\\(" app components app/globals.css
rg -n "cover\\.jpg|editorial/" --glob "*.tsx"
```

Displacement / Paper / `url(#` on any file that also mounts `cover.jpg` or `editorial/` is a **fail**, even if “the filter is on the parent.” **Parent includes the photo = photo is in SourceGraphic.**

---

## 9. Failure modes (FX-specific)

| ID | Failure | Why it happens | Detect |
| --- | --- | --- | --- |
| FX-01 | Cover wobble | `filter` on `.shimmer` parent / `aspect-[3/4]` | Screenshot A01 still vs reference `/products/A01/cover.jpg` |
| FX-02 | Hold unreadable | Goo/blur on tile | P02/P05 badge + “Inbox for price” |
| FX-03 | Header hole on iPhone | `backdrop-filter: url(#…)` | Safari: header transparent, grid shows through wordmark |
| FX-04 | Thermal / jank on All tab | 10× turbulence or 10× WebGL | Chrome perf: GPU/CPU; phone heat |
| FX-05 | Firefox `@supports` lie | url() in backdrop-filter | Header or CTA invisible |
| FX-06 | Safari goo bulge | Default filter region | Gold rule becomes a sausage; or a lone tab inflates |
| FX-07 | Wrong-mã morph, prettier | FX on VT snapshots | `/` A01 → `/m/A01` still morphs A02 (`10`) |
| FX-08 | Invented SKU for demo | Empty `/c/quan` “needs a chrome tile” | `/c/quan` empty; no Q01 |
| FX-09 | Hubcap page | `LiquidMetal` `shape="none"` on cards | Entire grid is metal |
| FX-10 | Shimmer + rim both infinite | Ignored §6 | MOT-08 worse; vestibular (`10` §3.3) |

---

## 10. Accessibility

| Criterion | This FX |
| --- | --- |
| [1.4.1 Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) | Selected tab cannot be “the gooey one” only. Keep `aria-selected` + count color |
| [1.4.3 Contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) | Metal fill on Cormorant wordmark is a contrast risk. **Don’t.** CTA text stays `--ink` |
| [2.2.2 Pause, Stop, Hide](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html) | Do not add a second infinite animation while `.shimmer` loops |
| [2.3.1 Three Flashes](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html) | Do not strobe the metal rim |
| [2.3.3 Animation from Interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) (AAA) | Rim spin / goo / meniscus behind `prefers-reduced-motion` + `useReducedMotion()` |
| C39 | [WCAG Technique C39](https://www.w3.org/WAI/WCAG22/Techniques/css/C39) |

Apple HIG: frequent motion must not make people **wait** ([HIG Motion](https://developer.apple.com/design/human-interface-guidelines/motion)). Header chrome is seen on every page. **Static rim.** CTA can flash on hover like today.

---

## 11. Relationship to `10` and `13` (do not regress)

| Sister fix | This pass |
| --- | --- |
| `10` FIX 1 — reduced-motion on shimmer / announce / cta / VT | **Keep.** Add goo/rim kills in the same query |
| `10` FIX 2 — remove cover `opacity-0` | **Do not depend on opacity-0.** Do not add FX that “hides the distortion until load” |
| `10` FIX 3 — PDP `product-{THIS mã}` + lightbox | Lightbox is **more photography**. Same denylist |
| `10` FIX 4 — APG tabs ≤200ms | Goo must not slow the filter. Goo is on the **underline**, not the grid |
| `13` FIX 1 — gold meniscus | Compatible. Goo wrapper **is** that underline, not a second system |
| `13` FIX 3 — pour / clip on grid | **Clip-path on the grid wrapper is not a photo filter** if it only clips overflow of whole tiles. Still: no displacement inside the tiles |

If `10` / `13` are not on Origin `main` yet, **do not regress them** to make chrome shinier.

---

## 12. Fixtures (never invent)

| mã | Status | $ | Cover |
| --- | --- | --- | --- |
| A01 | Available | $25 | `/products/A01/cover.jpg` |
| S01 | Available | $28 | `/products/S01/cover.jpg` |
| P01 | Available | $5 | `/products/P01/cover.jpg` |
| P02 | **Hold** | Inbox for price | `/products/P02/cover.jpg` |
| P03 | Available | $18 | `/products/P03/cover.jpg` |
| P04 | Available | $13 | `/products/P04/cover.jpg` |
| P05 | **Hold** | Inbox for price | `/products/P05/cover.jpg` |
| K01 | Available | $37 | `/products/K01/cover.jpg` |
| H01 | Available | $8 | `/products/H01/cover.jpg` |
| A02 | Available | $22 | `/products/A02/cover.jpg` |

Facebook Page stay: `https://www.facebook.com/profile.php?id=61594312648057`.

---

## 13. APPLY checklist (Origin, chrome only)

Do these on sell-test / Origin feature branch. Check only when the **Preview URL** proves it.

- [ ] **No** `feDisplacementMap`, `feTurbulence`, or Paper `LiquidMetal` in shop source.
- [ ] **No** `backdrop-filter: url(` anywhere.
- [ ] **No** `filter: url(` on any ancestor of `img`, `.shimmer`, or `/editorial/`.
- [ ] Optional: `id="ky-gold-goo"` exists **once**; applied only to the Featured gold-rule wrapper.
- [ ] Optional: `.ky-chrome-rim` on footer Message CTA only; hover/focus; Kelly Ying gold/ink/paper stops; 1–1.5px.
- [ ] Optional: header `border-b` tint via `color-mix` with `--gold` — static.
- [ ] Wordmark still ink Cormorant. No `background-clip: text` metal.
- [ ] Covers at `/` and `/m/A01` match the JPEG (no wobble). Hold P02/P05 still Hold.
- [ ] Reduce Motion: no goo, no rim spin, no shimmer (existing kill), tabs + Message still work.
- [ ] Desktop + phone. Firefox + Safari + Chromium.
- [ ] No new mã. No Excel. No intake. No Production promote without Boss.

---

## 14. Out of scope

- Intake `sassy-closet/` (Allura / rose / Nunito).
- Excel / Official xlsx / Square Save.
- Origin shop **`main` restyle** / cart / SEO index.
- Implementing `10` lightbox or `13` clip-path pour **unless** they are already on the branch — do not steal those PRs’ jobs except to **not regress** the denylist.
- Kelly Ying public CSS (Cloudflare-blocked this pass).

---

## 15. Verify (live URLs)

| Check | URL |
| --- | --- |
| Grid 10, covers honest | https://sassy-closet-shop.vercel.app/ |
| Tops A01 A02 | https://sassy-closet-shop.vercel.app/c/ao |
| Hold thermos | https://sassy-closet-shop.vercel.app/m/P02 |
| Available top hero | https://sassy-closet-shop.vercel.app/m/A01 |
| Empty pants | https://sassy-closet-shop.vercel.app/c/quan |
| Invented mã dead | https://sassy-closet-shop.vercel.app/m/A03 |
| Admin untouched by FX | https://sassy-closet-shop.vercel.app/admin |

Phone + OS Reduce Motion are **required**, not optional, for this note.

---

## 16. Sources

### 16.1 First-party (this crawl)

| URL / path | Used for |
| --- | --- |
| https://sassy-closet-shop.vercel.app/ | Chrome vs cover map |
| https://sassy-closet-shop.vercel.app/m/A01 | PDP hero; wrong VT name on related |
| `/_next/static/immutable/chunks/34vl_zddoo4ws.css` | Tokens, keyframes, reduce |
| `/_next/static/immutable/chunks/3_93acjqq2t4q.js` | `featured-tab`, `springSoft`, `filterSlide`, no WebGL |
| `#shop-decisions` 2026-09-04 | Bots draft; Facebook is the store |
| `docs/ai-clothing-shop/10-…` `13-…` | Motion / watery law |
| `README.md` | Excel not a second warehouse; this PR still does not edit Excel |

### 16.2 FX / filters / metal

| URL | Used for |
| --- | --- |
| https://css-tricks.com/gooey-effect/ | Bebber goo; container not children; large-area cost; Safari DOM caveat |
| https://tympanus.net/codrops/2015/03/10/creative-gooey-effects/ | Goo on UI chrome (menus), not photos |
| https://codepen.io/lbebber/pen/LELBEo | Gooey menu filter markup |
| https://stackoverflow.com/questions/57742561/svg-bulge-on-ios-safari-with-filter-fegaussianblur-and-fecolormatrix | Expand filter region |
| https://thelinuxcode.com/svg-fedisplacementmap-practical-guide-to-organic-distortion/ | Displacement cost; keep maps small |
| https://www.w3.org/TR/filter-effects-1/#fedisplacemnentmap-restrictions | Tainted map → pass-through |
| https://www.chromium.org/developers/design-documents/image-filters/ | GPU vs CPU filter paths |
| https://github.com/mdn/browser-compat-data/issues/24110 | `backdrop-filter` + SVG `url()` not Safari/Firefox |
| https://bugzilla.mozilla.org/show_bug.cgi?id=1808785 | feTurbulence/displacement vs backdrop-filter |
| https://github.com/huozhi/vaso/issues/11 | Fallback ladder; `@supports` lie |
| https://blog.logrocket.com/how-create-liquid-glass-effects-css-and-svg/ | Liquid glass = Chromium backdrop url(); restrict to floating chrome |
| https://www.ekino.fr/publications/liquid-glass-in-css-and-svg/ | Same; shape limits |
| https://shaders.paper.design/liquid-metal | Paper LiquidMetal; `image` is a **mask** |
| https://github.com/paper-design/shaders/blob/main/packages/shaders/src/shaders/liquid-metal.ts | Stripe / contour / chroma recipe |
| https://seangeng.com/writing/building-a-liquid-metal-ui-kit | Metal = **edge**; WebGL per surface |
| https://github.com/seangeng/argent | `variant="border"` default |
| https://www.conic.style/css-conic-gradient/ | Ring + `--angle` repaint cost |
| https://dev.to/ericwoooo_kr/css-animated-gradient-borders-without-a-single-line-of-javascript-2k | Rotate static gradient, don’t animate stops |
| https://finance.biggo.com/news/202507211315_SVG_Filter_Performance_Issues | Turbulence CPU melt |

### 16.3 UX / a11y

| URL | Used for |
| --- | --- |
| https://www.nngroup.com/articles/animation-purpose-ux/ | Purpose, not delight |
| https://www.nngroup.com/articles/animation-usability/ | 0.1s cause-and-effect |
| https://www.nngroup.com/articles/response-times-3-important-limits/ | 0.1s / 1s |
| https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html | 1.4.1 |
| https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html | 2.2.2 |
| https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html | 2.3.3 |
| https://www.w3.org/WAI/WCAG22/Techniques/css/C39 | `prefers-reduced-motion` |
| https://developer.apple.com/design/human-interface-guidelines/motion | Don’t wait; Reduce Motion |

Granola: **not connected** this pass. If a later Kelly Ying meeting contradicts “no glass on photos,” shop law (honest stills, unique piece) still wins until Boss says otherwise in `#shop-decisions`.

---

## 17. What this kit PR is

Docs only: `docs/ai-clothing-shop/21-visual-fx-liquid-chrome-safe.md`.

No `excel-kit/` edits. No intake edits. No Origin git in this repo.

---

## 18. PASTE INTO ORIGIN AGENT (do not paraphrase)

Copy everything between the markers into a Cloud Agent on the **Origin `sassy-closet-shop` repo** (the git behind https://sassy-closet-shop.vercel.app). Not this kit. Not intake `sassy-closet/`. Not `excel-kit/`.

```text
===== BEGIN ORIGIN PASTE — liquid chrome SAFE (LEARN 21) =====

You are editing Origin sassy-closet-shop. Ship LIQUID CHROME on UI CHROME
ONLY. Never wreck product covers. No WebGL. No displacement maps on
photos. Do not restyle. Do not invent mã. Do not add iOS liquid glass.
Do not touch intake or Excel.

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

MEANING OF “CHROME”:
  sticky header, Featured gold h-px, footer Message CTA border, announce bar.
  NOT: /products/*/cover.jpg, /editorial/*.jpg, .shimmer, PDP hero, lightbox,
  view-transition groups named product-{MA}.

THE METAL IS THE EDGE, NOT THE FILL.
(Argent / Paper LiquidMetal lesson — do not paste Paper shaders.)

FIND FILES (rg — names may differ; match these strings, then edit those files):

  rg -n "featured-tab|cta-shine|site-header|announce-fade"
  rg -n "cover.jpg|editorial/hero|/products/"
  rg -n "feDisplacementMap|feTurbulence|LiquidMetal|backdrop-filter"
  rg -n "useReducedMotion|prefers-reduced-motion"

Expected (live 2026-09-09):
  CSS 34vl_zddoo4ws.css :root --paper --ink --gold --gold-deep --blush
  NO goo, NO displacement, NO WebGL in JS chunk 3_93acjqq2t4q.js
  header: view-transition-name:site-header; inner bg-paper opacity 0.92
  covers: img.object-cover group-hover:scale-[1.08] opacity-0  (LEARN 10
          still wants opacity-0 REMOVED — do not “fix” it with a filter)
  /m/A01 hero: /products/A01/cover.jpg — related rail names product-A02

If a file is missing, create the smallest CSS module for .ky-chrome-rim
and one hidden SVG for #ky-gold-goo. Do not invent a second design system.

────────────────────────────────────────
FIX 1 — Denylist (do this first; fail the PR if any hit remains)
────────────────────────────────────────
NEVER in app/ or components/:

  feDisplacementMap
  feTurbulence
  @paper-design/shaders / LiquidMetal
  WebGL / THREE / canvas used as a product material
  backdrop-filter: url(
  filter: url( on any node that contains or is an img / .shimmer

PARENT RULE: if SourceGraphic would include a photograph, the filter
is illegal. Moving the class to a wrapper around the tile still counts.

Editorial stills are photographs too (/editorial/hero.jpg etc.).

────────────────────────────────────────
FIX 2 — Message CTA: chrome EDGE only
────────────────────────────────────────
KEEP:
  footer a.cta-shine.overflow-hidden.rounded-full.border.border-line
  hover:border-gold/70
  ::after cta-flash (0.7s) on hover

DO:
  1. Add a 1–1.5px decorative rim (.ky-chrome-rim) using mask-composite
     exclude (with -webkit-mask-composite: xor) OR the live border tint.
     Stops: --gold-deep / --paper / --gold / --ink / --gold-deep only.
  2. Motion: if you animate, rotate an OVERSIZED STATIC gradient with
     transform (compositor). Do NOT keyframe conic-gradient angle
     (@property --angle repaints every frame).
  3. Animate ONLY on :hover / :focus-visible AND
     @media (hover: hover) and (prefers-reduced-motion: no-preference).
     Default = still rim. Phone with no hover = still gold border.
  4. Do NOT put filter:url(#goo) on the <a> (blobs 11px type).
  5. Do NOT fill the button with metal. Text stays text-ink.

────────────────────────────────────────
FIX 3 — Header: static metal hairline, not glass
────────────────────────────────────────
KEEP:
  header.sticky.border-b.border-line.bg-paper
  view-transition-name: site-header
  inner absolute inset-0 bg-paper opacity 0.92
  ::view-transition-group(site-header) { animation: none }

DO:
  Optional: border-bottom-color: color-mix(in srgb, var(--gold) 55%, var(--line))
  behind @supports (color: color-mix(in srgb, red, red)).

DO NOT:
  backdrop-filter: blur() over the product grid
  backdrop-filter: url(#anything)
  Liquid Glass refraction of covers scrolling under the header
  Animate the header (VT already frozen)
  Metal fill on the Cormorant wordmark

────────────────────────────────────────
FIX 4 — Optional Featured goo (gold-rule WRAPPER only)
────────────────────────────────────────
This is the SAME optional goo as LEARN 13 FIX 1. If 13 already
shipped it, do not add a second filter.

KEEP:
  className="absolute inset-x-0 bottom-0 h-px bg-gold"
  layoutId={!reduced && "featured-tab"}
  transition={springSoft}  /* stiffness 420, damping 32, mass 0.72 */

DO (optional):
  Wrapper that contains ONLY the rule (+ optional trail).
  SVG filter id="ky-gold-goo":
    x="-50%" y="-50%" width="200%" height="200%"
    color-interpolation-filters="sRGB"
    feGaussianBlur stdDeviation="6"
    feColorMatrix alpha row 18 -7
    feComposite operator="atop"
  Animate TRANSFORM of the hairline, never stdDeviation.
  Gated: prefers-reduced-motion: no-preference && !useReducedMotion().

NEVER: goo on tablist, tab buttons, counts, images, grid, shimmer.

If Safari skips DOM filters, hairline still works. Expand region so
iOS does not bulge a lone rule.

────────────────────────────────────────
FIX 5 — Reduce Motion + mobile budget
────────────────────────────────────────
KEEP existing reduce kills for announce-fade / shimmer / cta-shine / VT.

ADD:
  @media (prefers-reduced-motion: reduce) {
    .ky-gold-goo, [style*="ky-gold-goo"], .ky-chrome-rim {
      filter: none !important;
      animation: none !important;
    }
  }

BUDGET:
  Always-on animated FX layers on /  ≤ 1
  Live .shimmer already uses that slot (1.3s infinite × 10 tiles).
  Do NOT add an always-on header rim spin while shimmer runs.
  Goo instances: 0 or 1.
  WebGL contexts: 0.
  Displacement graphs: 0.

Do not lengthen Featured filterSlide (already 0.32+0.22 wait — LEARN 13
wants ≤200ms). Chrome FX must not wrap AnimatedProductGrid.

────────────────────────────────────────
HARD STOPS
────────────────────────────────────────
- No new mã. No Q01 / A03 / AO001 on the lookbook.
- No cart, Shop now, flying-to-cart, liquid-into-bag.
- No warehouse ticker, no fake countdown.
- Do not rewrite P02/P05 to a dollar. No e.tb.cn, no ¥, no customer names.
- Do not restyle fonts or gold “to look cleaner.”
- Do not touch https://sassy-closet.vercel.app (intake).
- Do not edit excel-kit or Official xlsx.
- Do not Production-promote without Boss. Open a Preview.
- Do not apply Paper LiquidMetal to cover.jpg (that shader uses the
  image as a MASK and repaints metal over the garment).

────────────────────────────────────────
VERIFY (you click these; do not skip)
────────────────────────────────────────
Desktop Chromium + Firefox + Safari + a real phone + OS Reduce Motion:

1. /  All ten covers look like the JPEGs (no wobble, no melt, no
   chromatic fringe on fabric). P02+P05 Hold · Inbox for price.
2. /  Optional CTA rim on footer Message; hover rim only if motion on.
   Message still opens facebook.com/profile.php?id=61594312648057
3. /  Header still opaque paper. Wordmark ink. No glass over the grid.
4. /m/A01 cover visible and undistorted. /m/P02 undistorted, no $.
5. /c/ao = A01 $25 + A02 $22. /c/quan empty.
6. Reduce Motion: no goo, no rim spin, no shimmer, no 1.08 zoom.
   Tabs + Message still work.
7. rg the branch: zero feDisplacementMap, feTurbulence, LiquidMetal,
   backdrop-filter:url. filter:url only on #ky-gold-goo wrapper
   (if present).
8. View-source / network: no e.tb.cn, no ¥, no A03, no V984.

Commit on an Origin cursor/* branch. Preview URL in the PR. Do not merge.

===== END ORIGIN PASTE =====
```

Mini Boss: copy the block above as the **entire** Origin prompt. Do not add “also make the photos more premium” or “just a little displacement.” Chrome-only *is* the liquid-chrome pass. `10` and `13` still apply if they are not on `main` yet — do not regress them.

End of 21.
