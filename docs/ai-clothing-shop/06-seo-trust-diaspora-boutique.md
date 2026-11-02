# 06 — SEO, trust, and conversion for small diaspora clothing boutiques

**Track:** Ultra burn · AI clothing shop  
**Audience:** VN / Bay Area / US-ship closets that sell unique pieces over Facebook + Messenger, then take Zelle or cash.  
**Apply target:** [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app) (live crawl **2026-09-09**).  
**Voice contract:** **EN chrome** (nav, status, CTAs, announcement, titles, trust pages) + **VN product voice** (blurbs, captions, PDP soul line).  
**Hard stops (shop law):** never invent stock, sell $, or a flat ship $; never put a personal / bank-legal name on public UI unless Boss *intentionally* publishes it; Facebook inbox is the store; bots draft only.

This note is the SEO / trust / conversion playbook for that shape of shop. It is not a Shopify growth hack and not a “rank for *women’s clothing*” brief. A ten-SKU livestream closet wins by being **findable to the people who already know the livestream**, **shareable without looking like a scam**, and **clear about meetup vs ship vs pay** — without inventing a postage number Boss has not locked.

---

## 0. What this track is for

Sassy Closet is a **Messenger-first** boutique: the catalog is a lookbook, “Message to buy” is the checkout, Square is on-hand truth, Official Excel is the mã / caption working copy. Kit captions already end with:

> Inbox mã để lấy nha 💕 Local cash/Zelle. Ship toàn US.

That footer is the conversion model. SEO’s job is to make the **same** model visible on the public site, in search snippets, and in the Facebook / iMessage preview when someone pastes `/m/A01`.

Three jobs, in order:

1. **Stop hiding.** The live shop currently tells every crawler `noindex, nofollow`. Until that flips, OG tags and sitemaps do nothing in Google.
2. **Look like a real shop when shared.** Open Graph is how a mã link stops looking like a random Vercel URL in the inbox.
3. **Answer the Bay Area / US-ship questions on the page** (meetup, quote-then-ship, Zelle *after* mã confirm) so a cold click converts. Do not invent a flat ship dollar. Slack `#shop-decisions` still lists **flat ship $** as something Boss has not decided ([2026-09-04 team order](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788557030839509)).

---

## 1. Thesis (read this first)

For a diaspora closet, **trust is the ranking factor you can actually control**.

Google’s own helpful-content guidance says automated systems prioritize useful, people-first pages, and that **trust** is the most important part of E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness). E-E-A-T is not a single ranking knob; it is the conceptual bundle quality raters and ranking systems look for. Money, payments, and “will I get the dress” are closer to YMYL than a moodboard is — a buyer is about to send irreversible cash-like money. ([Creating helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content))

That means:

- A pretty hero with no how-to-buy page loses to a plainer page that says **who you are, how to pay, how you meet, how you ship**.
- Inventing “USPS $8 flat” to look more “e‑com” is both shop-law illegal *and* an FTC problem if you cannot actually ship on that basis (see §7).
- Publishing “Zelle: Jane Nguyen / 510-…” on the homepage is a **trust own-goal**: it doxxes the operator, trains scammers, and fights the official Zelle rule that people should only send money to parties they already know and have confirmed.

**EN chrome + VN product voice** is the correct bilingual strategy for this ICP. Do not fork the site into `/en` + `/vi` until you have *true* parallel pages. Google does not use `hreflang` or the HTML `lang` attribute to *detect* language; it uses the page’s own text. Localized versions are duplicates only if the **main content** stays untranslated. ([Localized versions of your pages](https://developers.google.com/search/docs/specialty/international/localized-versions); [Title links — match the writing system of the primary content](https://developers.google.com/search/docs/appearance/title-link))

| Layer | Language | Examples |
| --- | --- | --- |
| Chrome | English | Tops, Available, Hold, Message to buy, Featured collection, How to buy, Meetup & ship |
| Product soul | Vietnamese | Áo độc bản — một chiếc đang có · caption blurbs · livestream speak |
| Trust facts | English first, VN echo optional | Bay Area meetup · US ship quoted after zip/weight · Zelle after we confirm the mã |
| Titles / OG | English (primary) + mã | `A01 · Top · Sassy Closet` |
| Captions / inbox | Vietnamese | Kit `buildCaptionVi` footer |

Live PDPs already do a thin version of this (`One unique top on hand…` + `Áo độc bản — một chiếc đang có.`). Keep that split. Do not translate the nav into Vietnamese and do not strip the VN line off the PDP.

---

## 2. Shop law that governs every SEO change

From this repo’s standing rules (`README.md`, `sassy-closet/BOSS.md`, `excel-kit/DESIGN_NOTES.md`, `sassy-closet/lib/captions.ts`) and Slack `#shop-decisions`:

| Rule | SEO implication |
| --- | --- |
| Never invent mã, qty, sell $, or storage | Meta, OG, JSON-LD `Offer.price`, and announcement bars may only repeat **on-hand** facts. Hold + “Inbox for price” is correct. |
| Flat ship $ is **not** Boss-locked | Do not write `$7`, `$8.50`, “free over $50”, or `shippingRate` in schema. Say **quoted after zip + weight**. |
| Zelle name **locked** (CS reply pack) | Public UI: the word **Zelle**. Not the legal name, not the email, not the phone, not a handle, unless Boss explicitly says “publish this.” |
| Facebook inbox is the store | Primary CTA stays **Message / Inbox mã**. No fake cart for Google Shopping merchant listings. |
| Bots draft only; owner posts / takes Zelle / Square Save | Site must never claim “pay now” or auto-charge. |
| Square Free = on-hand SoT | `availability` in schema follows Square status: Available → `InStock`; Hold → `PreOrder` or omit offer; Sold → `OutOfStock` or drop the URL from the sitemap. |
| US sizes are not quoted to customers | Do not stuff “Size M US” into titles. Asia size + cm, or “message for size.” |
| Customer PII never in git / public site | No buyer names, no operator legal name, no street unless it is an intentional public meetup point. |

Slack, 2026-09-04, same message: *“Customer Service → reply pack (Zelle name locked)”* and *“Still need from Boss when free: … flat ship $”*. Treat both as **open decisions**, not blanks for an agent to fill.

---

## 3. APPLY — live audit of `sassy-closet-shop.vercel.app`

Crawled 2026-09-09: `/`, `/c/ao`, `/c/set`, `/c/phu-kien`, `/c/ao-khoac`, `/c/toc`, `/m/A01`–`/m/A02`, `/m/S01`, `/m/P01`–`/m/P05`, `/m/K01`, `/m/H01`, plus `/m/a01`, `/robots.txt`, `/sitemap.xml`, `/about`, `/shipping`, `/faq`, `/privacy`.

### 3.1 What is already right

These are **keep** behaviors. Do not “clean them up” into generic e‑com.

- **Messenger-first chrome.** Header CTA is `Messenger` → Facebook profile `id=61594312648057`. Cards say **Message to buy**. PDP: `1 piece · Message to buy. No cart.` That honesty is an E-E-A-T signal.
- **EN chrome, VN slugs, VN soul.** `html lang="en"`. Nav labels: Tops / Sets / Accessories / Jackets / Hair. Paths: `/c/ao`, `/c/phu-kien`, `/c/ao-khoac`, `/c/toc`. PDP EN description + VN line. Category titles: `Tops · Sassy Closet`.
- **Hold does not invent $.** P02 / P05: title `P02 · Thermos · Sassy Closet`, description *“No USD sell price yet — inbox for price.”* Visible: `Inbox for price`. Matches kit law.
- **Zelle naming hygiene on the public UI is currently clean.** Footer: `Sassy Closet · Zelle · Message on Messenger`. No personal name, no phone, no email. **Keep it that way.**
- **Unique-ish PDP titles.** `A01 · Top · Sassy Closet` — mã first, kind, brand. Google wants unique `<title>` text per URL and concise branding at the end. ([Title links](https://developers.google.com/search/docs/appearance/title-link))
- **Unique-enough PDP descriptions** (template, but page-specific mã). Home/category descriptions are the weak ones.
- **Favicon** exists (`/favicon.ico`, `/icon.svg`).
- **Hero 1280×720** is a usable homepage OG source once you crop to 1200×630. Product covers are **864×1152 portrait** — fine on the PDP, wrong as raw `og:image`.

### 3.2 What is broken (blocks the whole program)

| Surface | Live fact | Why it hurts |
| --- | --- | --- |
| Robots meta | **Every** HTML page: `<meta name="robots" content="noindex, nofollow"/>` | Google’s `noindex` rule: do not show the page in search. `nofollow`: do not use the links for discovery. Combined = the shop is a private lookbook that search cannot use. ([Robots meta tags](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)) |
| `robots.txt` | **404** | Missing file is not a disaster by itself (default is “may crawl”), but you also cannot declare a sitemap, and a new site with few backlinks *needs* that hint. ([robots.txt intro](https://developers.google.com/search/docs/crawling-indexing/robots/intro); [Sitemaps overview](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview)) |
| Sitemap | `/sitemap.xml` **404** (also `/sitemap`, `/sitemap-0.xml`) | New site + almost no external links = Googlebot may never find `/m/K01`. Google explicitly lists “new and has few external links” as a sitemap reason. |
| Open Graph | **Zero** `og:*` or `twitter:*` tags. `/opengraph-image` 404 | Facebook’s crawler will guess. A mã link in Messenger will preview as a generic Vercel title. The four required OG properties are `og:title`, `og:type`, `og:image`, `og:url`. ([Open Graph protocol](https://ogp.me/); [Sharing for webmasters](https://developers.facebook.com/docs/sharing/webmasters/)) |
| Canonical | None. `/m/a01` and `/m/A01` both **200** with the same content | Duplicate URLs. Sitemap + `rel=canonical` should pick **uppercase mã** (`/m/A01`). ([Canonicalization](https://developers.google.com/search/docs/crawling-indexing/canonicalization)) |
| JSON-LD | None | No `Organization`, no `Product`, no `FAQPage`. You cannot earn product snippets. Do **not** compensate by inventing shipping or ratings. ([Product structured data](https://developers.google.com/search/docs/appearance/structured-data/product)) |
| Trust routes | `/about`, `/shipping`, `/faq`, `/privacy`, `/terms` all **404** | Footer has no “How to buy” or “Meetup & ship”. Baymard: a slice of users go to the footer for shipping/returns; a banner is not a substitute. ([Footer needs return/shipping links](https://baymard.com/blog/footer-needs-return-shipping-links)) |
| Announcement bar | Single line, uppercase: **Facebook livestream** | True, but it does not answer meetup, US ship, or how to pay. No `$` (good). No Zelle name (good). Incomplete. |
| Home / category meta | Same description on `/` and every `/c/*`: `Sassy Closet — unique pieces. Facebook livestream. Zelle · Message on Messenger.` | Google: identical descriptions across pages are not helpful; write unique copy per page, especially home + popular URLs. ([Control your snippets](https://developers.google.com/search/docs/appearance/snippet)) |
| Meetup / Bay Area / ship | **Zero** occurrences of meetup, ship, Bay Area, San Jose, etc. in rendered chrome | A US-ship + local-pickup shop that never says so will lose the click *and* the inbox. Kit already promises “Ship toàn US” in captions — the site must match, **without a fake rate**. |
| Intake vs shop | This repo’s intake app (`sassy-closet/`, `sassy-closet.vercel.app`) is a **staff tool** | Do not index intake /admin. Keep `noindex` there. Only the **shop** host should go indexable. |

### 3.3 Score (live, 2026-09-09)

| Pillar | Score | Note |
| --- | --- | --- |
| Indexation | 0 / 5 | Site-wide `noindex, nofollow` |
| Titles | 3 / 5 | PDP/category unique; home too thin |
| Descriptions | 2 / 5 | PDP OK; chrome pages duplicated |
| OG / share | 0 / 5 | No tags, no 1200×630 asset |
| Sitemap + robots.txt | 0 / 5 | Both missing |
| Canonical / hreflang | 1 / 5 | Case-duplicate mã URLs; bilingual-on-one-URL (no hreflang needed yet) |
| Structured data | 0 / 5 | Absent (and must stay honest) |
| Announcement + fulfill clarity | 1 / 5 | Livestream only; no meetup/ship |
| Zelle hygiene | 5 / 5 | Public UI names the **rail**, not the person |
| EN chrome / VN voice | 4 / 5 | Pattern is live; trust pages missing |
| **Total** | **16 / 50** | Flip index + OG + how-to-buy before any “SEO content” |

---

## 4. EN chrome + VN product voice (the bilingual contract)

### 4.1 Why this split

The buyer is often **one person with two registers**:

- English for *is this a real US shop, can I Zelle, will you meet in the South Bay, do you ship to Houston?*
- Vietnamese for *cái áo này cưng không, còn mã không, inbox giúp mình giữ*.

Chrome in English reduces scam-fear for US-born / mixed-language buyers and for anyone forwarding the link to a partner who does not read VN. Product voice in Vietnamese is the brand (livestream, captions, mã speak). Swapping those — VN nav + EN product dump — reads like a translated dropship store.

Google’s title-link guidance: use the **same language and writing system as the primary content**. If the page is primarily English chrome + English trust facts, the `<title>` should be English. A Vietnamese soul line in the body is extra, not a second URL. ([Title links](https://developers.google.com/search/docs/appearance/title-link))

Do **not** add `hreflang` until `/m/A01` and `/vi/m/A01` are real alternate documents that link to each other. A single bilingual URL is not an hreflang cluster. Google: each language version must list itself and all others; return links are required. ([Localized versions](https://developers.google.com/search/docs/specialty/international/localized-versions))

`html lang="en"` on the shop is correct. (The **intake** app uses `lang="vi"` — that is a staff tool, different host, keep it `noindex`.)

### 4.2 Copy map (steal these)

**Home title (EN chrome):**  
`Sassy Closet · Unique pieces · Bay Area meetup · US ship`

**Home description (EN, ~155 characters, unique):**  
`One-of-one pieces. Message the mã on Messenger. Bay Area meetup or US ship quoted after zip and weight. Zelle or cash after we confirm — no public cart.`

**Category title:**  
`Tops · Sassy Closet` (already live — keep)

**Category description (unique, not the home string):**  
`Tops on hand at Sassy Closet. Message A01 / A02 on Messenger. Unique pieces — no cart.`

**PDP title:**  
`A01 · Top · Sassy Closet` (already live — keep)

**PDP description:**  
EN fact first, mã, no invented ship $:  
`A01 on hand — one unique top. Message to buy. Bay Area meetup or US ship (quoted). Zelle after we confirm the mã.`

**PDP soul (VN, visible, not necessarily the meta):**  
`Áo độc bản — một chiếc đang có. Inbox A01 để giữ nha.`

**Announcement (EN, one line, no $):**  
`Bay Area meetup · US ship quoted · Message the mã · Zelle after confirm`

**VN echo on How to buy (not the bar):**  
`Gặp local (Bay Area) hoặc ship toàn US — báo giá sau khi có zip + cân nặng. Zelle / cash sau khi chốt mã.`

### 4.3 What not to do

- Do not keyword-stuff `áo đẹp San Jose Vietnamese boutique cheap fashion`. Google treats stuffing in titles as spammy. ([Title links](https://developers.google.com/search/docs/appearance/title-link))
- Do not auto-translate the whole PDP with an LLM and call it a `vi` locale.
- Do not put VN-only titles on EN-primary pages (Google may rewrite the title link to match the page).
- Do not create thin `/vi` mirrors that only translate the header. Google: if you keep main content in one language and translate only the template, say so with hreflang **only if** those are actually alternate URLs — and those pages are easy to treat as duplicates. Prefer **one** bilingual URL.

---

## 5. Indexation, robots.txt, sitemap

### 5.1 Flip `noindex` on the shop only

Live: `content="noindex, nofollow"` on home, categories, and every `/m/{mã}`.

That is a **page-level** instruction Google honors when it can crawl the HTML. It is stronger than “we forgot a sitemap.” Remove it (or set `index, follow`) on public catalog URLs. Keep `noindex` on any future `/admin`, preview, or the **intake** host.

Google: `noindex` = do not show this page in results; `nofollow` = do not follow links on this page. `none` = both. ([Robots meta tags](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag))

`robots.txt` **cannot** replace `noindex`. If you `Disallow` a URL, Google may still index the URL from other links, with no snippet. To hide intake, use `noindex` *and* auth, not Disallow-only. ([robots.txt intro](https://developers.google.com/search/docs/crawling-indexing/robots/intro))

Next.js shop (App Router):

```ts
// app/layout.tsx — shop host only
export const metadata = {
  metadataBase: new URL("https://sassy-closet-shop.vercel.app"),
  title: {
    default: "Sassy Closet",
    template: "%s · Sassy Closet",
  },
  description:
    "One-of-one pieces. Message the mã on Messenger. Bay Area meetup or US ship quoted after zip and weight.",
  robots: { index: true, follow: true },
};
```

Intake (`sassy-closet/app/layout.tsx` today) should stay **non-indexable** if it is ever linked. Today its metadata is staff-facing Vietnamese and has no robots field — add `robots: { index: false, follow: false }` there so a future default-index Next version cannot leak the intake UI.

### 5.2 `robots.txt` (create)

Missing file = crawlers may fetch anything they find. Still add one so you can **point at the sitemap** and keep staff paths out.

Next.js: `app/robots.ts` → [`MetadataRoute.Robots`](https://nextjs.org/docs/app/api-reference/file-conventions/metadata/robots).

```ts
import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/api/", "/admin"],
    },
    sitemap: "https://sassy-closet-shop.vercel.app/sitemap.xml",
  };
}
```

Do **not** Disallow `/m/` or `/c/`. Do **not** use robots.txt as the way to hide a page you already `noindex`.

AI crawlers (`GPTBot`, `Google-Extended`, etc.) are a separate policy decision. For a 10-SKU lookbook, **allowing** search + answering surfaces is usually the point (AEO, §10). Blocking training crawlers does not require `noindex`.

### 5.3 Sitemap (create)

Google reads a sitemap to learn which URLs you consider important and their last update. A site this small is under the “500 pages” *you might not need one* bar — **except** it is new and has almost no inbound links, which is Google’s other “you need one” case. ([Learn about sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview); [Build and submit](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap))

Protocol rules that matter here ([sitemaps.org](https://www.sitemaps.org/protocol.html)):

- UTF-8; **absolute** `https://…` URLs only.
- 50 000 URLs / 50 MB uncompressed per file (irrelevant at 20 URLs).
- Host at the site root so it applies to the whole host.
- Include only **canonical, indexable** URLs you want in results.
- Google uses `<lastmod>` when it is consistently true; Google **ignores** `<changefreq>` and `<priority>`.

**Include**

| URL | Why |
| --- | --- |
| `/` | Home |
| `/c/ao` `/c/set` `/c/phu-kien` `/c/ao-khoac` `/c/toc` | Category hubs |
| `/m/A01` … uppercase mã only | PDPs |
| `/how-to-buy` `/meetup-ship` (once built) | Trust |

**Exclude**

- `/m/a01` (lowercase duplicate)
- Hold-only URLs **if** you do not want them shoppable in Search — or include them with honest “inbox for price” copy (P02/P05 today). Prefer include + honest availability over hiding real pieces.
- `/api/*`, intake host, preview deployments
- Sold mã (or keep the URL with `OutOfStock` and a “similar pieces” module — do not 404 a shared mã link if people still have it)

Next.js: [`app/sitemap.ts`](https://nextjs.org/docs/app/api-reference/file-conventions/metadata/sitemap) generating from the same catalog the UI uses. Add product images via the `images` field so Google can find `/products/A01/cover.jpg` as an image sitemap extension.

Submit:

1. `Sitemap: https://sassy-closet-shop.vercel.app/sitemap.xml` in robots.txt (Google finds it on the next robots crawl).
2. Google Search Console → Sitemaps report (shows fetch time + errors). Submitting is a **hint**, not a crawl guarantee. ([Build and submit](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap))

Do not add hreflang `xhtml:link` alternates until real locale URLs exist.

---

## 6. Titles, snippets, Open Graph

### 6.1 Titles

Google builds title *links* from `<title>`, visible H1, `og:title`, and other prominent text. You influence; you do not command. Best practices: unique per URL, descriptive, no stuffing, brand once at the end, same language as primary content. ([Title links](https://developers.google.com/search/docs/appearance/title-link))

Live pattern `A01 · Top · Sassy Closet` is good. Home should grow past a bare `Sassy Closet` so a SERP can say *why* to click.

### 6.2 Meta descriptions

Google often rewrites snippets from on-page text. A good meta description is still worth writing: unique, specific, a pitch. Product pages should pull **mã + availability + price-if-known + CTA**, not a site-wide slogan. ([Control your snippets](https://developers.google.com/search/docs/appearance/snippet); Shopify’s 2026 write-up agrees Google rewrites often but still uses a relevant description when it fits — [How to write a meta description](https://www.shopify.com/blog/how-to-write-meta-descriptions))

Programmatic generation is encouraged for catalog URLs **if** the strings stay human and diverse. Bad: `Sassy Closet unique pieces` × 10. Good: the P02 Hold string already live.

Use `data-nosnippet` on any element that might someday contain a Zelle handle or a private meetup pin. Google extracts snippets from visible text; `data-nosnippet` on `div`/`span`/`section` keeps that text out of SERPs and out of AI Overview *inputs*. ([Robots meta + data-nosnippet](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag))

### 6.3 Open Graph (required for this shop)

Facebook: without OG tags the crawler **guesses**. For a livestream closet, the share preview *is* the PDP. ([Sharing for webmasters](https://developers.facebook.com/docs/sharing/webmasters/); [ogp.me](https://ogp.me/))

**Every public URL needs at least:**

| Tag | Home | PDP `/m/A01` |
| --- | --- | --- |
| `og:url` | `https://sassy-closet-shop.vercel.app/` | `https://sassy-closet-shop.vercel.app/m/A01` (canonical, uppercase) |
| `og:type` | `website` | `website` (or `og:type` product if you commit to the product object; default `website` is fine) |
| `og:title` | Short, **no** extra brand pile-on — Facebook says title without extra branding | `A01 · Top` (site name goes in `og:site_name`) |
| `og:description` | Meetup + quote-ship + message + Zelle-after-confirm | Piece fact + mã + inbox; no ship $ |
| `og:image` | 1200×630 crop of `/editorial/hero.jpg` (source is 1280×720) | Generated card: cover photo + mã (do not feed raw 864×1152) |
| `og:image:width` / `height` | `1200` / `630` | same |
| `og:image:alt` | `Sassy Closet lookbook` | `A01 top — Sassy Closet` |
| `og:locale` | `en_US` | `en_US` |
| `og:site_name` | `Sassy Closet` | `Sassy Closet` |

Optional: `og:locale:alternate` = `vi_VN` **only if** you truly have a Vietnamese document. On a bilingual single URL, skip it.

Also set Twitter/X `summary_large_image` (`twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`) to the same assets so iMessage / Slack unfurls stay consistent. Next.js `generateMetadata().openGraph` + `twitter` fills both. ([Metadata and OG images](https://nextjs.org/docs/app/getting-started/metadata-and-og-images))

**Image rules that fail in production**

- Relative `/products/A01/cover.jpg` — OG requires an **absolute https** URL (`metadataBase` + path).
- Portrait cover as the only `og:image` — feed scrapers letterbox or crop faces/hems. Generate 1200×630 with `next/og` `ImageResponse`: blush ground, mã, kind, price-or-Hold, small product still.
- Reusing the same file URL after you change the photo — Facebook caches by URL. Bump `?v=` or a content hash when the cover changes. ([Sharing for webmasters — images](https://developers.facebook.com/docs/sharing/webmasters/))
- Putting the Zelle legal name or a phone number on the generated OG image. That image will be copied off-platform.

Validate with [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/) after each mã launch. The debugger also forces a rescrape.

### 6.4 Suggested `generateMetadata` for a mã

```ts
export async function generateMetadata({ params }): Promise<Metadata> {
  const { ma } = await params;
  const item = await getOnHand(ma.toUpperCase()); // Square/on-hand only
  const canonical = `https://sassy-closet-shop.vercel.app/m/${item.ma}`;
  const priceBit =
    item.status === "Hold" || !item.sellUsd
      ? "Inbox for price"
      : `$${item.sellUsd}`;
  const description =
    item.status === "Hold"
      ? `${item.ma} on Hold — photo-check. Inbox for price. Message to buy.`
      : `${item.ma} on hand — one ${item.kindEn}. Message to buy. Bay Area meetup or US ship quoted after zip and weight.`;

  return {
    title: `${item.ma} · ${item.kindEn}`,
    description,
    alternates: { canonical },
    openGraph: {
      type: "website",
      url: canonical,
      siteName: "Sassy Closet",
      locale: "en_US",
      title: `${item.ma} · ${item.kindEn}`,
      description,
      images: [{ url: `${canonical}/opengraph-image`, width: 1200, height: 630, alt: `${item.ma} ${item.kindEn}` }],
    },
    twitter: { card: "summary_large_image" },
  };
}
```

Never interpolate a `ship_fee` from Excel unless that cell is a **real quoted order**, and never put it in OG.

---

## 7. Announcement bars, meetup, and ship — without inventing $

### 7.1 What the bar is for

Live DOM (home and every inner page):

```html
<div class="… h-8 … bg-ink …">
  <p class="announce-fade … uppercase tracking-[0.22em]">Facebook livestream</p>
</div>
```

One message, eight words of tracking, no link. Fine as a *mood*. Useless as *fulfillment*.

Baymard: a large share of users **never see** a site-wide shipping banner; 32% of sites put “free shipping” only in that chrome and testers missed it. If you state a fulfill fact, **repeat it next to the buy control**, and give the footer a real **Meetup & ship** link. ([Free shipping should not only be in a banner](https://baymard.com/blog/avoid-banners-only-free-shipping); [Footer shipping/returns links](https://baymard.com/blog/footer-needs-return-shipping-links); [Banner UI](https://baymard.com/learn/banner-ui))

For this shop the “buy control” is **Message {mã}**. Put one fulfill line under that button, not only in the 32px bar.

### 7.2 What you may say (no Boss ship $ yet)

Kit already encodes fulfill as `Ship` | `Local pickup` | `Hold` | `TBD` (`excel-kit/schema.py` `SOT_FULFILL`). Captions say **Ship toàn US** with **no dollar**. Public chrome should match.

**Allowed (EN chrome)**

- Bay Area meetup / local pickup (city-level: “South Bay / East Bay — we pick a public spot in inbox”).
- Ships in the US. Rate **quoted after** ZIP + piece weight/size.
- Hold / photo-check pieces: inbox for price (already live).
- “Usually packed after payment + address confirm” — only if that is true.
- “Message the mã to reserve.”

**Forbidden until Boss locks a number in `#shop-decisions`**

- `$8 flat`, `$12 USPS`, `free over $40`, `shippingRate.value` in JSON-LD.
- “Arrives in 2 days” / “same-week guaranteed” without a **reasonable basis**.
- A made-up meetup café address.
- A Google Business pin on someone’s apartment.

### 7.3 FTC Mail / Internet Order Rule (why fake speed is worse than no speed)

If you take an order by internet / message and then mail the goods, the FTC **Mail, Internet, or Telephone Order Merchandise Rule** applies. You must have a **reasonable basis** for any ship-by claim. If you say nothing, you must have a reasonable basis to ship within **30 days** of a properly completed order (payment + the info you need to fill it). If you will miss that, you must notify and offer a refund. Silence is not a strategy if you implied speed. ([FTC business guide to the Rule](https://www.ftc.gov/business-guidance/resources/business-guide-ftcs-mail-internet-or-telephone-order-merchandise-rule))

“Properly completed” for this closet is: **mã confirmed + payment received + ship-to on file**. The clock does not start when they tap Message.

So the honest bar is:

> Bay Area meetup · US ship — we quote after ZIP · Message to buy

not:

> Free 2-day USPS — $6.99

If Boss later locks a real flat rate (the Slack open item), put **that** number in the bar, the PDP fulfill line, the `/meetup-ship` page, *and* schema, the same day. One source of truth. Until then, **quote**.

### 7.4 Recommended bar + PDP + footer

| Surface | EN chrome | VN echo (optional, not instead) |
| --- | --- | --- |
| Announcement | `Bay Area meetup · US ship quoted · Inbox the mã` | — |
| Under Message CTA | `Meetup in the Bay, or we quote US postage after ZIP + weight. No flat rate on the site.` | `Gặp local hoặc ship US — báo giá sau.` |
| Footer links | How to buy · Meetup & ship · Messenger | — |
| Footer pay line | `Zelle or cash after we confirm the mã` | `Zelle / cash sau khi chốt mã` |
| `/meetup-ship` H1 | Meetup & US shipping | — |
| `/meetup-ship` body | Public spot, no doorstep surprise; USPS/UPS quote in inbox; no published $ | Short VN restatement |

Rotate the bar only among **true** facts (livestream night, Hold on thermoses, meetup). One message at a time. Do not stack promo + ship + livestream into a 10px marquee.

### 7.5 Structured shipping (only when real)

Google can show shipping next to products if you mark up `ShippingService` / `OfferShippingDetails`. Required bits for an offer-level rate include destination country, delivery time, and a **numeric** `shippingRate`. ([Merchant shipping policy](https://developers.google.com/search/docs/appearance/structured-data/shipping-policy); [Product structured data](https://developers.google.com/search/docs/appearance/structured-data/product))

**If you do not have a real rate, omit shipping markup.** A validator-green `$0` or `$8` you invented is a lie in a rich result. Prefer a `/meetup-ship` page in plain language. Organization-level `hasShippingService` can wait until Boss locks policy.

This shop also has **no cart**. Google splits **product snippets** (pages you cannot buy on) vs **merchant listings** (pages you can purchase on). Messenger-only PDPs fit **snippets**: `Product` + `Offer` with `url` = the PDP, `price` only when USD is real, `availability` from Square. Do not pretend this is a Merchant Center checkout. ([Intro to Product structured data](https://developers.google.com/search/docs/appearance/structured-data/product))

---

## 8. Zelle naming hygiene

### 8.1 The rule

**Never put a personal name, bank-legal name, phone, or email on public UI, OG images, schema, titles, the announcement bar, or the sitemap — unless Boss explicitly decides that exact string is public.**

Slack already locked the name inside the **Customer Service reply pack** (private). The public site’s job is to name the **rail**: `Zelle`. The inbox’s job (after a real mã hold) is to send the enrolled destination.

Live footer already obeys this. The failure mode is a well-meaning “trust” PR that adds `Pay Zelle to [First Last]` under the hero.

### 8.2 Why the rule exists (cite, don’t vibe)

1. **Zelle shows the name on the bank account**, not a cute shop nickname. Recipients are told to **read the contact name before they send**. Small-business FAQ: confirm the recipient by reviewing the name displayed; tags exist for *eligible business accounts*, not as a public homepage field. ([Using Zelle with a small business account](https://www.zelle.com/faq/small-business))
2. **Zelle’s own scam guidance:** only send to people and businesses you **know and trust**; confirm the email or US mobile. Publishing a legal name + phone on a Vercel URL trains both good buyers *and* impersonators. ([How to stop scammers](https://www.zelle.com/blog/how-stop-scammers-their-tracks))
3. **FTC:** sending on Zelle / Venmo / Cash App is like sending **cash** — hard to reverse. Buyers should confirm they are talking to the real shop (the Facebook profile they already follow), not a cloned name on a random page. ([FTC consumer alert, 2023-08-14](https://consumer.ftc.gov/consumer-alerts/2023/08/do-you-use-payment-apps-venmo-cashapp-or-zelle-read))
4. **Network terms** (FI copies): Zelle is not meant as anonymous retail checkout; name on the account is a fraud-prevention display, not a marketing byline. Do not fight that by spraying the legal name onto Open Graph.
5. **Shop law:** bots never move Zelle; owner takes payment after the conversation. A public name+handle invites “I already paid Jane” disputes from people who paid a scammer.

### 8.3 Public vs inbox vs schema

| Place | Show | Never show |
| --- | --- | --- |
| Announcement, footer, OG, `<title>` | `Zelle` | Legal name, `@handle`, phone, email, last-4 |
| How to buy | “We send Zelle details **in Messenger after** we confirm the mã and the total.” | A standing QR on the homepage |
| CS reply pack (private) | Enrolled name + dest Boss locked | — |
| JSON-LD `Organization` | `name: Sassy Closet`, `sameAs: Facebook URL` | `PaymentMethod` with a person’s name; `email`/`telephone` unless they are shop-only and intentional |
| Generated OG image | Brand + mã | Any payee string |
| Snippets | `data-nosnippet` on the inbox-only payee block if it ever renders for a logged-in staff preview | Staff preview on a public host |

If Boss **intentionally** publishes a **business** Zelle tag (eligible FI + small-business enrollment), that is a different string from a personal legal name. Still: put it on `/how-to-buy` behind the “after we confirm” sentence, not in the 32px bar, and still ask the buyer to match the **name Zelle shows** to the name you sent in Messenger.

### 8.4 Suggested public sentences

**EN:** `Pay by Zelle or cash after we confirm the mã and the total in Messenger. We will send the Zelle destination in that thread — we do not publish it on the site.`

**VN:** `Zelle hoặc cash sau khi chốt mã + tổng tiền trong Messenger. Shop gửi thông tin Zelle trong inbox — không để tên/STK trên web.`

**Do not write:** `Zelle: Nguyen Thi … / 408-… / sassy@gmail.com`.

---

## 9. Trust pages and E-E-A-T for a 10-SKU closet

Google’s who / how / why questions: who made this, how was it made, why does it exist. For a boutique, “who” is **Sassy Closet** (the shop), not a dumped legal name. “How” is livestream + real photos + mã. “Why” is one-of-one pieces for the diaspora circle — not search-engine-first fashion essays. ([Helpful, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content))

Build two short EN pages (VN echo at the bottom):

### `/how-to-buy`

1. Pick a mã (`A01`).
2. Tap **Message {mã}** (Facebook).
3. Confirm size / photos (Hold = photo-check, no $ yet).
4. Choose **meetup** or **US ship** (quote).
5. Pay **Zelle or cash** after the shop sends the destination in-thread.
6. Owner packs / meets. Square Save is back-office, not your job.

FAQ pairs here are AEO gold (`FAQPage` JSON-LD). Questions to answer in **one sentence first**, then detail:

- How do I buy? Message the mã. No cart.
- Do you ship? Yes, US — we quote after ZIP and weight.
- Do you meet? Bay Area, public spot, in inbox.
- What is Zelle? A bank rail. We send details after we confirm. We do not publish a name on this site.
- Why is P02 Inbox for price? Hold / photo-check. We will not invent a USD.

### `/meetup-ship`

Fulfill only. City-level meetup. Quote algorithm in words (“USPS/UPS from our scale + your ZIP”). No dollar until Boss locks one. Return / photo-check policy in plain language (unique pieces, message first). Link from footer and from the PDP fulfill line.

**About:** a short block on home or `/how-to-buy` is enough. Real photos, Facebook `sameAs`, “unique pieces on hand.” Do not fake a street retail store. Do not add star ratings you do not have (`AggregateRating` without real reviews is spam).

**Privacy:** a 200-word EN note (what the site stores: nothing about buyers; Messenger is off-site) beats a missing `/privacy` when you turn index on.

---

## 10. Structured data (honest or absent)

Use JSON-LD. Combine with `@graph`.

**Organization / OnlineStore** on every public page:

- `name`: Sassy Closet  
- `url`: canonical host  
- `sameAs`: `[Facebook profile URL]`  
- `logo`: absolute icon  
- **No** `founder` legal name unless intentional  
- **No** `shippingRate`

**Product** on `/m/{mã}` (snippet-class, not fake merchant checkout):

- `name`: `A01 · Top`  
- `sku` / `mpn`: the mã  
- `image`: absolute cover(s)  
- `description`: EN description (plain text)  
- `offers.priceCurrency`: `USD`  
- `offers.price`: only if sell USD exists  
- `offers.availability`: `InStock` / `OutOfStock` — **not** `InStock` on Hold  
- `offers.url`: canonical PDP  
- Omit `offers` on Hold-without-price (or use a description-only Product)

**FAQPage** on `/how-to-buy` only, with questions that appear **visibly** on that page (Google’s FAQ rich-result rules have tightened; still useful for machines and AEO).

**BreadcrumbList:** `Home > Tops > A01`.

Validate: [Rich Results Test](https://search.google.com/test/rich-results), [schema.org validator](https://validator.schema.org/).

---

## 11. AEO (answer engines) without writing SEO essays

Answer engines pick **clear, extractable, current, trusted** sentences. ([AEO considerations in this skill set](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) — same helpful-content / E-E-A-T spine; structure like FAQ + first-sentence answers.)

On `/how-to-buy` and PDPs:

- First sentence = the answer.  
- Then the VN soul / livestream color.  
- Lists for steps.  
- Visible dates only if you truly update policy.

`noindex` currently blocks Google Search **and** limits how much Google can use the page as a snippet / AI Overview input. Flipping index is the AEO prerequisite. `nosnippet` would also block AI Overview use of that page’s text — do not set it site-wide. Use `data-nosnippet` only on payee / private meetup details.

Do not mass-produce “Vietnamese fashion in San Jose — a complete guide” blogs. That is search-engine-first content Google asks you to avoid.

---

## 12. Page experience (enough to not drop the share)

Core Web Vitals thresholds: **LCP < 2.5s**, **INP < 200ms**, **CLS < 0.1**. ([web.dev](https://web.dev/articles/defining-core-web-vitals-thresholds))

Live home preloads the hero + every category still + every product cover. That is aggressive for LCP on a 10-piece grid. After you add OG, do not also preload every `opengraph-image`. Keep `fetchPriority` on the hero only.

Announcement bar is a fixed `h-8` — good (less CLS than a late-loading bar). If you later add a dismissible bar, reserve the height in the layout.

---

## 13. Implementation recipe (shop host)

Do this on **sassy-closet-shop**, not on the intake app in this repo.

1. **P0 — Index.** Remove site-wide `noindex, nofollow`. Keep intake /admin noindex.  
2. **P0 — `robots.ts` + `sitemap.ts`.** Absolute shop URLs; uppercase mã; lastmod from catalog mtime.  
3. **P0 — `metadataBase` + canonical.** `/m/A01` canonical; lowercase redirects.  
4. **P0 — OG.** Default 1200×630; per-mã `opengraph-image`. Sharing Debugger.  
5. **P0 — Announcement + PDP fulfill line + footer links.** Copy from §7.4. No `$`. No name.  
6. **P1 — `/how-to-buy` + `/meetup-ship`.** EN chrome, VN echo. FAQ schema.  
7. **P1 — Unique home/category descriptions.**  
8. **P1 — JSON-LD** Organization + Product (honest Offer).  
9. **P1 — Search Console** property for the shop host; submit sitemap; inspect `/` and `/m/A01`.  
10. **P2 — GBP** only if you have a real public meetup policy you want to show.  
11. **P2 — Privacy** stub.  
12. **Never** copy Zelle legal name from the CS pack onto the site.

Caption kit (`sassy-closet/lib/captions.ts` `FOOTER`) already matches §7–8. Do not “upgrade” it to include a $ or a person’s name.

---

## 14. APPLY checklist — Sassy Closet shop

Use this as the launch punch-list. **Pass** = live HTML matches. Dated **2026-09-09**.

### P0 — can Google and Facebook even see you?

| # | Check | Live | Next action |
| --- | --- | --- | --- |
| 0.1 | Public pages send `index, follow` (or omit robots) | **FAIL** — `noindex, nofollow` on `/`, `/c/*`, `/m/*` | Flip metadata on shop host |
| 0.2 | Intake / admin stay `noindex` | Intake not this host (OK) | Add explicit noindex on `sassy-closet` layout |
| 0.3 | `https://sassy-closet-shop.vercel.app/robots.txt` 200 | **FAIL** 404 | `app/robots.ts` + Sitemap line |
| 0.4 | `https://sassy-closet-shop.vercel.app/sitemap.xml` 200, absolute URLs | **FAIL** 404 | `app/sitemap.ts` from catalog |
| 0.5 | Sitemap lists `/`, `/c/*`, uppercase `/m/{MA}` only | **FAIL** | Exclude `/m/a01` |
| 0.6 | Self-canonical on each public URL | **FAIL** | `alternates.canonical` |
| 0.7 | `/m/a01` → 308 `/m/A01` | **FAIL** — both 200 | Redirect |
| 0.8 | `og:title` `og:description` `og:image` `og:url` `og:type` present | **FAIL** | `generateMetadata` + file OG |
| 0.9 | `og:image` 1200×630 absolute HTTPS | **FAIL** — `/opengraph-image` 404; covers 864×1152 | `next/og` or cropped hero |
| 0.10 | Facebook Sharing Debugger clean for `/` and `/m/A01` | Not run (no tags) | Rescrape after 0.8 |

### P1 — trust + conversion (still no invented $)

| # | Check | Live | Next action |
| --- | --- | --- | --- |
| 1.1 | Announcement states meetup **or** US-quote-ship **or** livestream — no `$` | **PARTIAL** — livestream only | Replace/extend copy §7.4 |
| 1.2 | Same fulfill sentence sits **under Message to buy** | **FAIL** | PDP + card |
| 1.3 | Footer links: How to buy · Meetup & ship | **FAIL** — only Zelle · Messenger | Add routes |
| 1.4 | `/how-to-buy` EN steps + VN echo | **FAIL** 404 | Write page |
| 1.5 | `/meetup-ship` quote language, no flat $ | **FAIL** 404 | Write page; wait for Boss on $ |
| 1.6 | Home meta unique vs categories | **FAIL** — identical description | Per-route descriptions |
| 1.7 | Hold items stay “Inbox for price” in title, meta, OG, body | **PASS** (P02/P05) | Keep |
| 1.8 | Available items show real USD only | **PASS** | Keep; never backfill |
| 1.9 | JSON-LD Product/Offer without `shippingRate` | **FAIL** (no JSON-LD) | Add honest graph |
| 1.10 | `Organization.sameAs` = Facebook profile | **FAIL** | Add |
| 1.11 | EN chrome / VN soul still split | **PASS** | Keep; don’t hreflang-split |
| 1.12 | Search Console sitemap submitted | Unknown | After 0.4 |

### P2 — Zelle + privacy + polish

| # | Check | Live | Next action |
| --- | --- | --- | --- |
| 2.1 | Public UI contains the word Zelle **without** a personal/legal name | **PASS** | Guardrail in PR review |
| 2.2 | No Zelle dest in OG image, schema, title, bar | **PASS** | Keep |
| 2.3 | How-to-buy says dest is sent **in Messenger after confirm** | **FAIL** (no page) | §8.4 copy |
| 2.4 | CS reply pack remains the only place with the locked name | Slack: locked | Do not promote to UI |
| 2.5 | `data-nosnippet` ready if a staff-only payee block ever renders | N/A | Add when needed |
| 2.6 | Privacy stub | **FAIL** 404 | Short EN page |
| 2.7 | No fake GBP / apartment pin | **PASS** (absent) | Keep absent until intentional |
| 2.8 | Caption footer still no $ / no name | **PASS** in kit | Do not “enrich” |

### Sign-off questions (Boss, not the agent)

- [ ] Index the shop? (Today it is hidden on purpose or by leftover default — **decide**.)  
- [ ] Publish a **business** Zelle tag, or keep dest inbox-only? Default: inbox-only.  
- [ ] Lock a flat ship $ in `#shop-decisions`? Until then the site **quotes**.  
- [ ] Name a public meetup city only, or a recurring public pin?

---

## 15. Worked example — `/m/A01` after the punch-list

**`<title>`:** `A01 · Top · Sassy Closet`  
**meta description:** `A01 on hand — one unique top. Message to buy. Bay Area meetup or US ship quoted after ZIP and weight. Zelle after we confirm the mã.`  
**H1 chrome:** `A01` / `TOP` / `Available` / `$25`  
**Soul:** `Áo độc bản — một chiếc đang có.`  
**CTA:** `Message A01`  
**Fulfill (EN):** `Bay Area meetup or US ship — we quote postage after your ZIP. No flat rate published.`  
**Pay (EN):** `Zelle or cash after we confirm this mã in Messenger.`  
**OG image:** 1200×630, mã A01, hem/neck crop, **no** name, **no** `$8 ship`.  
**JSON-LD Offer:** `price: 25`, `priceCurrency: USD`, `availability: InStock`, **no** `shippingDetails`.  
**Canonical:** `https://sassy-closet-shop.vercel.app/m/A01`

That is a complete diaspora PDP: searchable, shareable, convertible, still shop-law clean.

---

## 16. Anti-patterns (do not ship)

- Flipping index on the **intake** app.  
- Merchant Center feed with invented GTIN / shipping.  
- Star ratings you did not collect.  
- “Free shipping” in the bar and a quote in the inbox.  
- Dual language homepages that only translate the header.  
- Blog spam for “Vietnamese clothes Bay Area.”  
- Putting Mini Boss / Slack / OneDrive / Square in public chrome.  
- Pasting the CS **Zelle name locked** pack into the footer “for conversion.”  
- Filling `ship_fee` in Official Excel with a guess so OG can show it.

---

## 17. Sources

Official / primary

1. Google Search Central — [Influencing title links](https://developers.google.com/search/docs/appearance/title-link)  
2. Google Search Central — [Control your snippets (meta descriptions)](https://developers.google.com/search/docs/appearance/snippet)  
3. Google Search Central — [Robots meta tags, `data-nosnippet`, `X-Robots-Tag`](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)  
4. Google Search Central — [Introduction to robots.txt](https://developers.google.com/search/docs/crawling-indexing/robots/intro)  
5. Google Search Central — [Learn about sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview)  
6. Google Search Central — [Build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)  
7. [Sitemaps protocol](https://www.sitemaps.org/protocol.html)  
8. Google Search Central — [Canonicalization](https://developers.google.com/search/docs/crawling-indexing/canonicalization)  
9. Google Search Central — [Localized versions / hreflang](https://developers.google.com/search/docs/specialty/international/localized-versions)  
10. Google Search Central — [Creating helpful, reliable, people-first content (E-E-A-T)](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)  
11. Google Search Central — [Product structured data](https://developers.google.com/search/docs/appearance/structured-data/product)  
12. Google Search Central — [Merchant shipping policy (`ShippingService`)](https://developers.google.com/search/docs/appearance/structured-data/shipping-policy)  
13. Google Search Central — [Merchant return policy](https://developers.google.com/search/docs/appearance/structured-data/return-policy)  
14. [Open Graph protocol](https://ogp.me/)  
15. Meta — [A guide to sharing for webmasters](https://developers.facebook.com/docs/sharing/webmasters/)  
16. Next.js — [Metadata and OG images](https://nextjs.org/docs/app/getting-started/metadata-and-og-images)  
17. Next.js — [`sitemap.ts`](https://nextjs.org/docs/app/api-reference/file-conventions/metadata/sitemap)  
18. Next.js — [`robots.ts`](https://nextjs.org/docs/app/api-reference/file-conventions/metadata/robots)  
19. FTC — [Business guide to the Mail, Internet, or Telephone Order Merchandise Rule](https://www.ftc.gov/business-guidance/resources/business-guide-ftcs-mail-internet-or-telephone-order-merchandise-rule)  
20. FTC — [Payment apps (Venmo, Cash App, Zelle) consumer alert](https://consumer.ftc.gov/consumer-alerts/2023/08/do-you-use-payment-apps-venmo-cashapp-or-zelle-read)  
21. Zelle — [Small business FAQ (confirm displayed name; tags)](https://www.zelle.com/faq/small-business)  
22. Zelle — [How to stop scammers (know-and-trust)](https://www.zelle.com/blog/how-stop-scammers-their-tracks)  
23. web.dev — [Core Web Vitals thresholds](https://web.dev/articles/defining-core-web-vitals-thresholds)

UX / conversion research

24. Baymard — [Free shipping should not only live in a site-wide banner](https://baymard.com/blog/avoid-banners-only-free-shipping)  
25. Baymard — [Footer needs shipping & returns links](https://baymard.com/blog/footer-needs-return-shipping-links)  
26. Baymard — [Banner UI](https://baymard.com/learn/banner-ui)  
27. Shopify — [How to write a meta description (2026)](https://www.shopify.com/blog/how-to-write-meta-descriptions)

Shop primary sources (this workspace + Slack)

28. Live HTML of [sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app) (2026-09-09 crawl: robots meta, titles, announcement bar, footer, PDP EN+VN lines, Hold pricing).  
29. `sassy-closet/lib/captions.ts` — VN caption footer: local cash/Zelle, ship toàn US, no $.  
30. `sassy-closet/app/layout.tsx` — intake metadata / `lang="vi"` (staff host).  
31. `README.md`, `sassy-closet/BOSS.md`, `excel-kit/DESIGN_NOTES.md`, `excel-kit/schema.py` — Square SoT, fulfill enums, no invented $, bots draft only.  
32. Slack `#shop-decisions`, 2026-09-04 — Zelle name locked in CS reply pack; flat ship $ still needed from Boss.

---

## 18. How this sits in the learn track

| # | Theme | This doc owns |
| --- | --- | --- |
| 01–05 | Media, PDP UX, Messenger commerce, admin ops, playbook kit | Do not contradict: no cart, no invented stock |
| **06** | **SEO, trust, conversion** | Index/OG/sitemap, EN chrome + VN voice, announcement + fulfill, Zelle hygiene |
| Later | Implementation PR on the **shop** repo/host | Execute §14 P0 first |

When you generate PR copy for the shop, say which of these sources you followed — especially Slack on **Zelle name** and **flat ship $** — so a future agent does not “helpfully” publish either.
