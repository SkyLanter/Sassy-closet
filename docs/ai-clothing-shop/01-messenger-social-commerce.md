# LEARN 01 — Messenger-first / social-commerce clothing boutiques

Playbook for unique-piece clothing shops that sell on Facebook / Instagram and close in Messenger — not a cart. Written for Sassy Closet. Sourced. No invented mã. No Square Save. No Facebook Send.

**Live APPLY target:** [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)  
Kelly Ying *look* is locked. Message-first is already on. This file is the commerce law, not a redesign brief.

**Sister systems (do not confuse them):**

| Surface | URL / path | Job |
| --- | --- | --- |
| Public lookbook | [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app) | Browse + Message to buy. No cart. |
| GF intake | [https://sassy-closet.vercel.app](https://sassy-closet.vercel.app) | Món mới / Sửa / Tìm mã / Ask. Never Posts. |
| Facebook inbox | [Page `61594312648057`](https://www.facebook.com/profile.php?id=61594312648057) | The store. Owner replies. |
| Slack `#shop-decisions` | Boss yes/no | Square Save, mã, price, Hold extend. |
| Square Free | Owner only | On-hand SoT. Agent never Saves. |
| Official Excel | OneDrive `Sassy_Closet_SoT.xlsx` | Working copy / mã index / captions. Not a second warehouse. |

---

## 0. Hard stops (print these first)

1. **Never invent mã.** Official stock codes are `AO` / `QU` / `VA` / `AK` / `GI` / `PK` / `SET` + three digits (`AO001`). Scripts refuse to mint. Sold mã stays retired. Ask Stock (Dashboard `B21:B27`). The public lookbook already shows **display codes** (`A01`, `S01`, `P01`…). Those are live catalog IDs already on the site — cite them, do not invent new ones, and do not treat them as Official Excel mã.
2. **No Square Save.** Bots and agents draft / propose only. Track stock ON is the standing rule. Wishlist stays off Square until Boss confirms bought and says yes in `#shop-decisions`.
3. **No Facebook Send / Post.** Owner posts the caption, sends the message, takes Zelle, taps Square Save. Agents may draft copy. They do not hit Send.
4. **Never invent a ship price.** `#shop-decisions` still lists **flat ship $** as something Boss has not locked. Kelly Ying’s published “Flat rate $10 shipping on order $300+” is *their* number ([kellyyingboutique.net](https://www.kellyyingboutique.net/)). It is not Sassy’s. Say “ask in inbox for ship / meetup” until Boss writes a number.
5. **Cite URLs.** Every pattern below points at a primary page. If a number is not on a cited page, it is not a shop fact.

Granola was not signed in for this run (`granola.ai/mcp-signup`). Slack `#shop-decisions` and the live shop were read instead.

---

## 1. Why this model exists (2025–2026)

### 1.1 Meta killed in-app checkout. Discovery stayed.

As of September 2025, Facebook and Instagram Shops use **website checkout**. Meta’s own help page: if a shop used checkout on Facebook or Instagram, the method was updated or the shop is invisible. Purchases, refunds, shipping, and branding now live off-platform.

- [About Changes to Shops and Checkout on Facebook and Instagram](https://www.facebook.com/business/help/1314349509894768)

Shopify’s 2026 social-commerce note says the same thing in merchant language: Instagram and Facebook remain discovery galleries; native checkout is gone; shoppers are sent to the brand’s own site.

- [Social Commerce Trends for 2026 — Shopify](https://www.shopify.com/enterprise/blog/social-commerce-trends)

For a **no-card, unique-piece boutique**, “your own website” does **not** have to mean Shopify checkout. It can mean a lookbook whose only conversion is a Messenger thread. That is what Sassy already shipped: `1 piece · Message to buy. No cart.`

### 1.2 Messenger is still Meta’s commerce primitive

Meta still documents Messenger as the channel that combines in-store concierge with online convenience: catalog cards, receipts, back-in-stock alerts, **ads that click to Messenger**, **m.me links**, Page “Send Message,” Chat Plugin, QR codes.

- [Messenger for Commerce](https://developers.facebook.com/products/messenger/commerce/)
- [Create ads that click to Messenger](https://www.facebook.com/business/help/212519562595207)
- [Best practices for ads that click to message](https://www.facebook.com/business/help/269324800441478)
- [m.me links](https://developers.facebook.com/docs/messenger-platform/discovery/m-me-links/)
- [ig.me links (Instagram)](https://developers.facebook.com/docs/messenger-platform/instagram/features/ig-me-links)
- [Add an action button to your Facebook Page](https://www.facebook.com/help/977869848936797)
- [Add an action button to your Instagram business account](https://www.facebook.com/help/instagram/1419650861499317)

Happy Socks and Kiehl’s case notes on the commerce page (personalized guided shopping + click-to-Messenger ads) are brand-scale. The *shape* is what a boutique copies: **one question, one piece, one human reply** — not a 12-field checkout.

### 1.3 The diaspora / Little Saigon pattern Kelly Ying already runs

Kelly Ying Boutique (Garden Grove) is the look reference, not the checkout reference.

What their **public site** actually does ([kellyyingboutique.net](https://www.kellyyingboutique.net/)):

- Cart + Checkout (Shopify-style).
- Banner: **Livestream Facebook Chủ Nhật và Thứ 2 hằng tuần**.
- Banner: **Flat rate $10 shipping on order $300+** — *their* published rate. Do not copy the dollar amount onto Sassy.
- SKUs on the card (`V984. LACE BLACK DRESS`) so a live comment and a later DM can name the same piece.
- Collections: Dresses / Tops / Bottoms / Two-Pieces / Sleepwear.

Reviews on third-party listings describe weekly Facebook lives, staff who chat and follow up, and a “friendly checking out system” — i.e. **live + inbox + a cart for people who want it**.

- [Kelly Ying Boutique — Loc8NearMe](https://www.loc8nearme.com/california/garden-grove/kelly-ying-boutique/6384948/)
- [Kelly Ying Boutique — Locality](https://localitybiz.com/32074742/kelly-ying-boutique-garden-grove)

Sassy’s locked decision is the **look** (editorial hero, paper/blush/gold, Cormorant + Be Vietnam Pro, bilingual crumbs) **without** the cart. That is a harder conversion problem. This playbook is how no-cart shops still close.

### 1.4 Live selling is a different conversion engine

Comment-sold livestreams (Facebook Live + “sold” in comments + invoice in Messenger) are how many US boutiques scaled. West Raspberry’s owner told Business Insider she spent five hours invoicing after one live when she did PayPal by hand.

- [How 2 Clothing Boutique Owners Used Facebook Live — Business Insider](https://www.businessinsider.com/clothing-boutique-owners-facebook-live-commentsold-grow-sales-2021-7)

Vendor writeups (treat as vendor, not census) claim live viewers convert several times higher than cold PDPs. Use them as *motivation to keep the livestream banner honest*, not as a Sassy KPI.

- [Live selling start guide — LiveShopFront](https://liveshopfront.com/how-to-start-live-selling-instagram-facebook)

Sassy’s announce bar already says **Facebook livestream**. The inbox must be staffed when that is true. An empty live promise is worse than no banner.

---

## 2. The funnel: Facebook / Instagram → Messenger (not cart)

Think of four hops. Each hop has an official Meta tool. Agents implement **links and drafts**. Owner clicks Send.

```
Post / Reel / Live / Lookbook card
        ↓  (m.me / ig.me / Page Message / Click-to-Messenger ad)
Messenger thread  (buyer names the display code)
        ↓  (Owner confirms Available | Hold | gone)
Hold / Reserved on SoT + Square  (Boss yes if Save or Hold-extend)
        ↓
Zelle name locked  ·  or cash meetup  ·  then ship / pickup
        ↓
Orders: Inquiry → Reserved → Paid → Shipped | Picked up
```

### 2.1 Entry objects Meta already gives you

| Entry | Official job | Sassy use |
| --- | --- | --- |
| **Page action button** “Send Message” | [Facebook Help: add an action button](https://www.facebook.com/help/977869848936797) | Page is the storefront door. |
| **Instagram action button** | [Instagram Help: action buttons](https://www.facebook.com/help/instagram/1419650861499317) | Same door on IG. Partner list is limited; Message / email may be what you get. |
| **m.me/{Page}** | [m.me links](https://developers.facebook.com/docs/messenger-platform/discovery/m-me-links/) | Website, captions, email, Stories. Optional `ref` (attribution) and `text` (prefill). Clicking an existing thread **resets the 24-hour messaging window**. |
| **ig.me** | [ig.me links](https://developers.facebook.com/docs/messenger-platform/instagram/features/ig-me-links) | Same idea on Instagram. Instagram Web does not support ig.me. |
| **Ads that click to Messenger** | [Setup](https://www.facebook.com/business/help/212519562595207) · [Best practices](https://www.facebook.com/business/help/269324800441478) | Traffic / Engagement / Leads / Sales → conversion location **Message destinations**. Greet. Suggest first-tap prompts. |
| **Story / comment replies** | [Messenger for Commerce](https://developers.facebook.com/products/messenger/commerce/) | Product questions from IG comments become DMs. Owner replies. Agent does not Send. |
| **Lookbook “Message to buy”** | Live site | Every card and PDP already points at the Page. |

### 2.2 Prefill is the no-cart “SKU line”

Meta’s m.me `text` parameter is “the customized message sent by you when a person clicks your m.me link to enter a conversation.”

- [m.me reference](https://developers.facebook.com/docs/messenger-platform/discovery/m-me-links/)

That is how a lookbook without a cart still arrives as a **named inquiry**. The buyer should not have to invent a sentence.

**Pattern (draft for Owner to wire — do not invent a new mã):**

`https://m.me/<PAGE_USERNAME>?text=Hi%20Sassy%20—%20A01%20còn%20không%3F`

Until a username vanity URL exists, the live site uses the profile id:

[https://www.facebook.com/profile.php?id=61594312648057](https://www.facebook.com/profile.php?id=61594312648057)

That URL opens the **profile**, not a prefilled composer. It is why a buyer can land on the Page and still not start a thread. APPLY item 1 is to prefer `m.me` + `text=` with the **already published** display code (`A01`, not a minted `AO014`).

`ref` is for *your* analytics (lookbook vs Story vs live pin). It is not a customer-facing mã.

### 2.3 The 24-hour window (why the first buyer message matters)

The standard messaging window opens when a person messages the Page, taps a CTA, clicks a click-to-Messenger ad and then messages, clicks m.me / ig.me into an existing thread, reacts, or comments.

- [Send a Message — standard messaging window](https://developers.facebook.com/docs/messenger-platform/send-messages/)

For a human-owned boutique this is still the rule of the room: **the buyer speaks first**, then Owner can follow up for 24 hours. Icebreakers and greetings (Page Inbox → Automations) are allowed; they are not “FB Send” from an agent.

- [Create an automated Messenger greeting](https://www.facebook.com/help/1698046970464236)

Greeting that matches shop law (Owner pastes in Meta, not from this repo):

> Chào em 💕 Sassy Closet — món độc bản. Gửi **mã trên web** (ví dụ A01) + size ngực/eo (cm) hoặc ảnh. Zelle / cash meetup. Ship: inbox hỏi — chưa có giá ship cố định trên web.

Do not put a dollar ship rate in that greeting until Boss locks it.

### 2.4 Click-to-Messenger ads (when Boss buys traffic)

Meta: pick the objective that matches the goal; set conversion location to **Message destinations**; write a greeting; offer tappable prompts (“Start conversations”).

- [How to set up click to Messenger ads](https://www.facebook.com/business/help/212519562595207)
- [CTA buttons by objective](https://www.facebook.com/business/help/410873986524407) — for Messenger destinations the honest buttons are **Send message**, not Shop now.

Prompts that convert without a cart (Owner configures in Ads Manager):

1. `Còn A01 không?` — only if `A01` is still Available on the lookbook.
2. `Hold / inbox giá` — for Hold cards (`P02`, `P05` today).
3. `Size + cm` — Asia size + cm only (shop law: never quote US sizes to buyers).
4. `Meetup hay ship?` — no dollar.

Never run a Shop-now ad that implies website checkout. Meta’s Shops ads now assume a **website** conversion location ([Shops checkout change](https://www.facebook.com/business/help/1314349509894768)). Sassy’s “website” is a lookbook. Message destinations are the honest objective.

### 2.5 What “no cart” is *not*

It is not ManyChat / SellThread / DM Canvas / DMCart / Queek / Selmo auto-checkout. Those products exist and will pitch “pay in the chat.”

- [Messenger for Commerce](https://developers.facebook.com/products/messenger/commerce/) (platform)
- Vendor examples (do not adopt): [SellThread](https://sellthread.com/), [DM Canvas](https://massively.ai/dm-canvas/), [DMCart](https://dmcartapp.com/), [Queek](https://usequeek.com/business/shop), [Selmo](https://www.selmo.io/en-us/partner/whizbang)

They want a bot that Sends and a payment link. Shop law forbids agent Send and Square Save. If Boss later wants a **draft** icebreaker only, that is a `#shop-decisions` yes — still no Save, still no invented mã.

---

## 3. Hold vs Available (three vocabularies — do not mix)

This is the most common oversell. Sassy already uses **two words on the lookbook** and **more words in Excel**. They are not synonyms.

### 3.1 Public lookbook (what the buyer sees)

Live audit, 2026-09-09, [sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app):

| Display code | Kind | Public status | Price on card | PDP promise |
| --- | --- | --- | --- | --- |
| `A01` | TOP | Available | $25 | “One unique top on hand. Message A01…” |
| `A02` | TOP | Available | $22 | same shape |
| `S01` | SET | Available | $28 | “One set on hand.” |
| `P01` | ACCESSORY | Available | $5 | “Inbox P01 to buy.” |
| `P02` | THERMOS | **Hold** | **Inbox for price** | “Hold · photo-check, no USD yet.” |
| `P03` | ACCESSORY | Available | $18 | Inbox P03 |
| `P04` | ACCESSORY | Available | $13 | Inbox P04 |
| `P05` | THERMOS | **Hold** | **Inbox for price** | same as P02 |
| `K01` | JACKET | Available | $37 | “Message K01 for size and photos.” |
| `H01` | HAIR | Available | $8 | Inbox H01 |

That is the entire published catalog (10 pieces). Do not add an 11th code in copy.

**Available** on the lookbook = “we will talk about selling this unique piece.”  
**Hold** on the lookbook (as implemented) = “not priced in USD yet / photo-check.” It is *not* automatically “reserved for a named buyer.”

That second meaning is the trap. A buyer reading “Hold” on `P02` might think someone else already claimed it. The PDP copy currently explains: *photo-check, no USD sell price yet*. Keep that sentence. Do not silently reuse Hold to mean Reserved.

### 3.2 Official Excel / Ma_List (working copy)

From kit schema and design notes (`excel-kit/schema.py`, `excel-kit/DESIGN_NOTES.md`):

| Layer | Words | Meaning |
| --- | --- | --- |
| Official status | `Available` → `Reserved` → `Sold` plus `Hold` / `Damaged` / `Donated` | Working-copy life of a mã. |
| Ma_List | `in_stock` / `held` / `sold` / `archived` | Lean desktop. `Reserved` and Official `Hold` both map to `held`. |
| Orders | `Inquiry` → `Reserved` → `Paid` → `Shipped` \| `Picked up` \| `Cancelled` | Facebook hello → money → handoff. |
| Fulfill | `Ship` / `Local pickup` / `Hold` / `TBD` | How the paid order leaves. |
| Pay | `Zelle` / `Cash` / `Venmo` / `Other` / `Unpaid` | How money arrives. |

Square Free still wins on-hand. Official `qty_on_hand` is a note.

### 3.3 Slack law for Hold *time*

`#shop-decisions` (2026-09-04) examples of asks Boss answers with yes/no:

- `AO001 / M / đen — add to Square · on-hand 1 · cost ¥80 · price $25 — Save?` (example format only — **do not mint `AO001` if Stock has not assigned it**)
- `Hold AO003 past 24h?`

So: **a customer Hold that lasts past 24 hours is a Boss decision.** Apparel ops writing agrees: undifferentiated holds rot; 24h is the common escalate line.

- [Order holds playbook — TopSource](https://topsource.global/blog/order-holds-playbook/)
- [Order holds in apparel — Uphance](https://www.uphance.com/blog/order-holds-when-to-use-which-type/)

### 3.4 Recommended public words (so the three layers stay honest)

| Buyer-facing | Use when | Never use when |
| --- | --- | --- |
| **Available** | Square on-hand ≥ 1 (or Boss has said the lookbook row is live) and no named reserve | Wishlist / staged-only / photo-check |
| **Hold · inbox for price** | Price or photo not Boss-approved (current `P02` / `P05` pattern) | A named buyer is waiting on Zelle |
| **Reserved** (optional later) | Named buyer + clock + `#shop-decisions` if >24h | As a pretty synonym for Available |
| **Sold** | Paid or handed off; mã retired | “Almost sold” as urgency theater |

Do **not** flip a lookbook card to Reserved in code unless the same row is Reserved on Official and held on Square. Agents do not Save Square to make that true.

### 3.5 Hold clock (Owner paste, draft only)

When a buyer asks to hold an **Available** piece:

> Em giữ **[display code already on the site]** đến [time PT, ≤24h] giúp. Inbox trước giờ đó để Zelle / hẹn mặt. Sau giờ đó món về Available — trừ khi Boss yes thêm giờ.

If they ask past 24h: post in `#shop-decisions` (`Hold {ma} past 24h?`) and wait. Do not invent the mã if Stock has not assigned one.

### 3.6 Photo-check Hold (already on `P02` / `P05`)

This is a **merchandising** Hold, not a customer reserve:

> Thermos on Hold (photo-check). No USD sell price yet — inbox for price.

Correct. Do not put a guessed `$` on those cards. Do not invent a Square Save to “make it real.”

---

## 4. No-card shops (why Sassy is allowed to skip Stripe)

### 4.1 Definition

A no-card shop takes **Zelle, cash, maybe Venmo** and refuses card-not-present. The lookbook has no Pay button. The SoT pay list is already `Zelle | Cash | Venmo | Other | Unpaid`.

This is common in Facebook-live boutiques and Marketplace-adjacent closets. It is also the **risk the shop chooses on purpose**: no chargebacks, no Shopify, no Meta checkout, no Square Online. Square Free here is **inventory**, not a card terminal, unless Boss later says otherwise.

### 4.2 What you gain

- Unique pieces: one inbox thread = one allocation. No cart race.
- Diaspora buyers already live in Messenger + Zelle.
- No “Shop now” lie after Meta’s checkout sunset.
- Owner sees the person before the piece leaves.

### 4.3 What you give up (say this in trust copy, do not hide it)

Zelle’s own FAQ: use it with people you **know and trust**. If you are not sure you will get what you paid for (online bidding / sales sites), they recommend you **do not** use Zelle. **Zelle does not offer purchase protection.** Payments to an enrolled recipient **cannot be reversed**.

- [I’m unsure about using Zelle to pay someone I don’t know](https://www.zelle.com/faq/im-unsure-about-using-zelle-pay-someone-i-dont-know-what-should-i-do)
- Same page: “Can I reverse a Zelle payment?” → **No.**

FTC, in plain language: sending money through a payment app is **like sending cash** — very hard to get back. They tell consumers not to pay someone who *insists* the only method is a payment app / gift card / crypto / wire.

- [Do you use payment apps like Venmo, CashApp, or Zelle? — FTC](https://consumer.ftc.gov/consumer-alerts/2023/08/do-you-use-payment-apps-venmo-cashapp-or-zelle-read)
- [What to do if you were scammed — Zelle and bank transfers](https://consumer.ftc.gov/articles/what-do-if-you-were-scammed)
- [ftc.gov/paymentapps](https://www.ftc.gov/paymentapps)

CFPB: P2P transfers can be Regulation E EFTs; stored balances in *nonbank* apps are often **not** FDIC/NCUA insured unless extra products are on.

- [Electronic Fund Transfers FAQs](https://www.consumerfinance.gov/compliance/compliance-resources/deposit-accounts-resources/electronic-fund-transfers/electronic-fund-transfers-faqs/)
- [Is the money I keep in my payment app safe?](https://www.consumerfinance.gov/ask-cfpb/is-the-money-i-keep-in-my-payment-app-safe-en-2135/)

**Trust move for a no-card boutique:** do not pretend Zelle is “buyer protected.” Do pretend (because it is true) that the shop is a **named Page**, unique pieces, livestream, and a human who will meet or ship after money is **in the bank app**, not after a screenshot.

### 4.4 Venmo is on the SoT list. Treat it as second.

Venmo Friends-and-Family is the same “cash-like” bucket. Goods & Services is a different product. Until Boss writes a Venmo handle in the CS pack, **do not publish a Venmo CTA** on the lookbook. Footer today is honest: `Zelle · Message on Messenger`.

---

## 5. Zelle and cash-meetup patterns (safe, sourced)

`#shop-decisions` already: **Customer Service → reply pack (Zelle name locked).** This section is the *pattern*, not the name. Do not invent a Zelle handle, tag, or phone.

### 5.1 Shop-side Zelle ritual (Owner)

1. Buyer names a **live display code** (`A01`) or a Stock-assigned Official mã.
2. Owner confirms **Available** (or Hold-price if `P02`/`P05`) in the thread. If Official/Square disagree, stop and ask Stock. Never invent qty.
3. Owner sends **the locked Zelle name** (from the CS pack — not from this repo).
4. Buyer pays. Owner opens **the bank / Zelle activity**, not a JPEG.
5. Only then: Orders → `Reserved`/`Paid`, fulfill `Ship` or `Local pickup`. Square on-hand change = Boss Save.

Zelle: money to an enrolled recipient is typically available in minutes and **cannot be canceled**. Fake “upgrade to business Zelle” links are always scams (vendor writeups collect this; the *principle* matches Zelle’s own “we don’t reverse” + FTC’s “like cash”).

- [Zelle FAQ — reverse / cancel](https://www.zelle.com/faq/im-unsure-about-using-zelle-pay-someone-i-dont-know-what-should-i-do)
- [FTC payment-app alert](https://consumer.ftc.gov/consumer-alerts/2023/08/do-you-use-payment-apps-venmo-cashapp-or-zelle-read)

**Never ship on a screenshot.** Confirm in the official banking activity.

Zelle QR: Zelle documents a QR so the sender does not mistype email/phone. Not every bank offers it. When sending to someone new, confirm the **displayed name**.

- Same Zelle FAQ, “How do I use a Zelle QR code?”

Optional later (Owner): show the QR *in the thread after* the piece is confirmed — not as a public website dump of the handle.

### 5.2 What to tell the buyer (honest, not scary)

Draft (Owner sends):

> Zelle giúp mình nhận nhanh. Zelle **không có bảo vệ mua hàng** ([zelle.com FAQ](https://www.zelle.com/faq/im-unsure-about-using-zelle-pay-someone-i-dont-know-what-should-i-do)). Em chỉ Zelle **đúng tên shop** mình gửi trong chat — không link lạ, không “upgrade account.” Muốn xem món trước thì hẹn **cash meetup** chỗ công cộng.

That paragraph *cites the network’s own warning* instead of promising “safe checkout.”

### 5.3 Cash meetup (Facebook + police pattern)

Facebook’s own Marketplace in-person tips: keep the home address private; share the plan with a trusted person; do not change the spot after you agree; charged phone; save local emergency numbers.

- [Facebook Marketplace tips for meeting in person](https://www.facebook.com/help/2329750133711372)

US police departments independently advertise **Safe Exchange Zones** (camera-covered lots / lobbies). Examples, not Sassy venues:

- [Oakland PD Safe Exchange Zones](https://www.facebook.com/oaklandpoliceca/videos/opd-safe-exchange-zone/1272130354053634/)
- [Brooklyn Park PD internet safe zone](https://www.facebook.com/BPPDMN/posts/we-encourage-you-to-be-safe-when-buying-and-selling-items-of-value-off-of-social/855488453289088/)
- [Monroe PD meetup stalls](https://www.facebook.com/MonroeWAPolice/posts/safe-exchange-meetup-spots-available-at-the-monroe-police-departmentif-you-are-p/1193291967546571/)

**Sassy rule:** Owner picks the public spot. Never publish a home address on the lookbook. Never invent a city if Boss has not named one. “Local cash/Zelle” is already the intake caption footer — that is the ceiling until Boss writes a meetup neighborhood.

Cash at handoff: inspect piece, count cash, done. No Zelle-at-the-curb “I’ll send when I get home.”

### 5.4 Scam shapes a boutique must refuse

| Pattern | Why it fails shop law | Source |
| --- | --- | --- |
| Screenshot / email “payment received” | Not the bank ledger | Zelle FAQ + FTC “like cash” |
| Overpay + “refund the extra” | Classic P2P fraud | FTC scam recovery page |
| “Upgrade Zelle to business” link | Zelle does not charge a fee to receive | Zelle + industry writeups; treat link as hostile |
| Gift card / crypto / wire only | FTC: insistence on those rails is a red flag | [FTC payment-app alert](https://consumer.ftc.gov/consumer-alerts/2023/08/do-you-use-payment-apps-venmo-cashapp-or-zelle-read) |
| Off-platform to a personal profile | Facebook stays the store | Repo README + `#shop-decisions` |
| Buyer asks Owner to Send first from a bot | Agents do not Send | Shop law |

If money already moved the wrong way: bank first, then [ReportFraud.ftc.gov](https://reportfraud.ftc.gov/).

---

## 6. Trust copy without inventing ship prices

### 6.1 Why “just put $8 ship” is illegal *and* bad UX

**Legal.** The FTC Mail, Internet, or Telephone Order Merchandise Rule (16 CFR 435) applies to goods ordered by mail, phone, fax, or Internet — **regardless of how the order was advertised, how the customer pays, or who started the chat**. If you state or imply a ship-by time, you need a **reasonable basis**. If you state **nothing**, you still need a reasonable basis to ship within **30 days** of a properly completed order. If you will miss that, you must offer delay-or-refund.

- [Rule summary](https://www.ftc.gov/legal-library/browse/rules/mail-internet-or-telephone-order-merchandise-rule)
- [Business guide (30-day Rule)](https://www.ftc.gov/business-guidance/resources/business-guide-ftcs-mail-internet-or-telephone-order-merchandise-rule)
- [Selling on the Internet: prompt delivery](https://www.ftc.gov/business-guidance/resources/selling-internet-prompt-delivery-rules)
- eCFR text: [16 CFR Part 435](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-435)

Face-to-face cash meetup is the carve-out the 2014 amendments discuss (buyer does not order via the internet). A Messenger “ship it to Texas” **is** an internet/phone order. Do not write “ships tomorrow” unless the piece is in hand and Boss has a carrier ritual.

**UX.** Nielsen Norman: unexpected fees at the end feel like a trick; nonstandard or high shipping should be acknowledged **on the product page**. If you cannot calculate yet, **admit the extra charge exists**. Inventing a low number to look cheap is the failure mode they document (Disney / Macy’s furniture).

- [How to display taxes, fees, and shipping — NN/g](https://www.nngroup.com/articles/ecommerce-taxes-fees/)

Baymard’s checkout research (cart world): extra charges are the leading stated reason people abandon. Sassy has **no cart**, so the equivalent sin is **bait price on the card + surprise ship in the 12th message**.

- [Reduce cart abandonment — Baymard](https://baymard.com/learn/reduce-cart-abandonment)

### 6.2 What Sassy may say *today* (no dollar)

Allowed because they do not invent a rate:

- `Ship: inbox for quote` / `Ship toàn US — hỏi trong chat`
- `Local cash / Zelle meetup`
- `No USD ship price on the site yet`
- Intake caption footer already in code: `Inbox mã để lấy nha 💕 Local cash/Zelle. Ship toàn US.` (`sassy-closet/lib/captions.ts`) — **no `$`**. Keep it that way until Boss locks flat ship.

Forbidden until `#shop-decisions` writes a number:

- `$6.95 USPS` / `$10 over $50` / copying Kelly Ying’s **$10 / $300+**
- `Free ship` as a vibe
- `2-day` / `ships today` without a reasonable basis (FTC)

Kelly Ying *can* print `$10` because they published it on their own site. Different shop, different basis.

### 6.3 Trust stack that does not need a ship table

Put these near the CTA, not in a fake FAQ page (the lookbook has no `/shipping` — 404 — and that is fine):

1. **Unique piece / 1 on hand** — already on PDPs (`1 piece · Message to buy. No cart.`).
2. **Status word** — Available vs Hold, with Hold explained.
3. **Named Page** — header Messenger → official profile id.
4. **Livestream** — only if Owner is actually live on a cadence (Kelly Ying publishes Sun/Mon; Sassy only says the word today).
5. **Pay rails named without protection theater** — `Zelle · cash meetup`.
6. **Size truth** — Asia size + cm. Never US size to the buyer (`excel-kit/DESIGN_NOTES.md`).
7. **Price honesty** — USD on Available; `Inbox for price` on photo-check Hold. Never a decorative `$0`.
8. **`noindex, nofollow`** is currently on the lookbook. Soft-launch: do not promise Google traffic. Trust is the Page + the thread.

### 6.4 After Boss locks a flat ship $

Then — and only then — NN/g says put the **number next to the price**, not in a footer poem. Until that Slack yes, the honest line is:

> Tổng = giá món + ship (inbox báo số). Chưa in giá ship trên web vì Boss chưa chốt.

Orders already have a `ship_fee` column. Leave it empty rather than guess (`excel-kit/schema.py`).

---

## 7. CTAs that convert without a cart

### 7.1 What the lookbook already does (do not restyle)

Live patterns that are correct:

- Header: `Messenger` → official Page.
- Card: `Message to buy`.
- Available PDP: `Message A01 →` / `Message S01 →` (code in the button).
- Hold PDP: `Message to buy →` (no fake `$`).
- Sticky footer: `Zelle · Message on Messenger`.
- Announce: `Facebook livestream`.
- Meta description: `unique pieces. Facebook livestream. Zelle · Message on Messenger.`

This is already the anti-cart kit. Kelly Ying look (serif wordmark, gold underline, blush hero, uppercase 11px tracking) stays. Do not add Add to cart, Shop now, or a bag icon.

### 7.2 Why the verb is Message, not Buy now

Meta’s own ad CTAs for a Messenger conversion location are **Send message**, not Shop now ([CTA catalog](https://www.facebook.com/business/help/410873986524407)). Shop now promises a checkout Meta no longer runs for Shops ([checkout change](https://www.facebook.com/business/help/1314349509894768)).

NN/g’s fee research is about **not surprising people**. A button that says Buy now on a site with no pay form *is* a surprise.

Best boutique verbs (keep):

| Verb | Job |
| --- | --- |
| **Message to buy** | Card / Hold |
| **Message A01** | Available PDP — code travels with the tap |
| **Inbox for price** | Unpriced Hold |
| **Message on Messenger** | Footer / header |

Avoid: `Add to cart`, `Checkout`, `Buy with card`, `Shop now`, `Send` (agent), `Save` (Square).

### 7.3 One job per tap

A no-cart CTA must do **one** of these:

1. Open Messenger with the **display code already typed** (`m.me` + `text=`).
2. Or open the official Page if vanity / m.me is not ready (current behavior).

It must not:

- Mint a mã.
- Start a Square invoice.
- Fire a Send API message from this repo.
- Deep-link to a checkout URL Meta now expects for Shops ads.

### 7.4 First buyer line (icebreaker / prefill)

Owner-facing drafts. Codes below are **only** ones already on the lookbook.

- Available: `Hi Sassy — A01 còn không? Size [Asia] / ngực [cm] / eo [cm].`
- Hold price: `Hi Sassy — P02 inbox giá + ảnh thật.`
- Meetup: `A01 · cash meetup · [day] · chỗ công cộng.`
- Ship ask: `A01 · ship [state]. Inbox báo phí — web chưa in giá ship.`

Quill can draft captions; Owner posts. Caption starter is mã on line 1 (`sassy-closet` Saved card). Intake footer already teaches the close: inbox + cash/Zelle + ship-US-without-`$`.

### 7.5 Live comments → inbox (no bot)

When the announce bar is true:

1. Pin the lookbook URL + “comment mã / display code.”
2. Buyer comments the **published** code.
3. Owner replies in comments *or* asks them to Message — Owner’s hands, not an agent Send.
4. Same Hold clock as §3.5.
5. After the live: do not leave “Facebook livestream” up if the next date is unknown. Kelly Ying prints **days**. Sassy should too, once Boss names them — not before.

Comment-sold tooling (CommentSold, Selmo) exists because invoicing by hand melts owners ([Business Insider](https://www.businessinsider.com/clothing-boutique-owners-facebook-live-commentsold-grow-sales-2021-7)). Sassy’s answer at this volume (10 pieces) is **Orders rows**, not a new vendor.

### 7.6 Speed that feels like a cart

Meta’s click-to-message best practices: greet, look available, answer.

- [Best practices](https://www.facebook.com/business/help/269324800441478)

Human SLA that matches a 10-SKU closet:

- First reply: same waking block (PT).
- Availability: only after Square / Official agree.
- Hold >24h: Slack yes/no.
- Paid: Zelle visible in bank, then pack or meetup.

A 14-hour read receipt is the actual abandoned cart.

---

## 8. Channel map (Facebook inbox is the store)

From repo README and `#shop-decisions`:

| Channel | Allowed | Forbidden |
| --- | --- | --- |
| Facebook / Messenger | Customer chat, lives, posts (Owner) | Agent Send / Post |
| Instagram DM | Same if Page is linked | Agent Send |
| Lookbook | Status, price-or-inbox, Message CTA | Cart, invented ship $, new mã |
| Slack `#shop-decisions` | Save / mã / price / Hold extend | Customer chat |
| From GF / OneDrive | Intake photos | Messenger as intake inbox |
| Square | Owner Save, Track ON | Agent Save, wishlist as stock |
| Dial Bot | Not the store | — |

GF intake contract: **Never Messenger. Never Dial Bot** (`excel-kit/PROMPTS.md` task 11). Customers buy in Messenger; GF uploads in OneDrive. Do not cross the streams.

---

## 9. Display codes vs Official mã (read twice)

Two number systems are already in production. Mixing them is how agents invent mã by accident.

| System | Examples already in the world | Who mints |
| --- | --- | --- |
| **Lookbook display code** | `A01` `A02` `S01` `P01`–`P05` `K01` `H01` | Already published on the Vercel lookbook. Do not add `A03` in a playbook or PR. |
| **Official Excel / Square SKU** | `AO` `QU` `VA` `AK` `GI` `PK` `SET` + 3 digits | Stock / Boss only. Dashboard next-mã. |
| **Intake kind letter** | `A` áo, `S` set, `P` phụ kiện, `K` khoác, `H` tóc, plus `D` đầm, etc. | Saved card after Lưu — still not a Square Save. |

`A01` on the lookbook is **not** proof that Official `AO001` exists. Soft-launch Slack still asked for **first-mã Save proposal** after Square login. Until Stock assigns, the public code is a **lookbook id** only.

When writing customer copy: use the code **printed on the card the buyer tapped**. When writing Square / Official: use the Boss-assigned mã only.

---

## 10. Owner reply pack (drafts — Owner sends)

Placeholders: `{code}` = a code **already on the lookbook or assigned by Stock**. `{zelle}` = locked CS name. Never invent either.

**Still Available**

> Còn `{code}` 💕 Một món. Giá trên web. Size gửi Asia + cm (ngực/eo). Zelle `{zelle}` hoặc cash chỗ công cộng. Ship: mình báo số trong chat — web chưa in phí ship.

**Hold · inbox for price** (`P02` / `P05` shape)

> `{code}` đang Hold — kiểm tra ảnh, **chưa có giá USD**. Em gửi thêm ảnh / số đo. Không Zelle cho đến khi Boss chốt giá.

**Already Reserved**

> `{code}` đang giữ cho bạn khác (≤24h trừ khi Boss yes). Em muốn mình báo khi về Available không?

**Gone / Sold**

> `{code}` sold / không còn. Không giữ chỗ trên món đã bán. (Không tái sử dụng mã Official đã Sold.)

**Zelle received (bank confirmed)**

> Thấy Zelle rồi 💕 Mình pack / hẹn meetup. Tracking hoặc chỗ hẹn gửi trong thread này.

**Screenshot only**

> Mình cần thấy tiền trong app ngân hàng. Screenshot chưa tính. Giữ `{code}` thêm [≤24h] giúp.

**Ship delay (FTC)**

> Không ship đúng hẹn. Em chọn: đợi đến [date mình có cơ sở] **hoặc** hoàn. ([FTC 30-day Rule](https://www.ftc.gov/business-guidance/resources/business-guide-ftcs-mail-internet-or-telephone-order-merchandise-rule))

Do not send the delay template until there is a real paid internet order. Do not invent the date.

---

## 11. APPLY — [sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)

Short list. Look stays Kelly Ying. Message-first stays. No new mã. No Square Save. No FB Send. No invented ship `$`.

1. **Prefill the already-printed code.** Header/card/PDP should prefer `m.me` + `text=` with `A01` / `S01` / … ([m.me links](https://developers.facebook.com/docs/messenger-platform/discovery/m-me-links/)). Today every CTA is the bare profile [id `61594312648057`](https://www.facebook.com/profile.php?id=61594312648057). That is a Page view, not a started thread.
2. **Keep Available vs Hold as two different sentences.** Available = priced unique piece + `Message {code}`. Hold = `Inbox for price` + photo-check + no USD ([`/m/P02`](https://sassy-closet-shop.vercel.app/m/P02)). Do not reuse Hold to mean Reserved until Official + Square + Slack agree.
3. **Do not add a cart, Shop now, or Square checkout** to match Kelly Ying’s site. Their cart and **$10 / $300+** ([kellyyingboutique.net](https://www.kellyyingboutique.net/)) are not Sassy’s. Steal layout rhythm only.
4. **One how-to line, no ship number.** Footer already has `Zelle · Message on Messenger`. Add at most: `Inbox for ship quote or cash meetup` — not `$x`. `#shop-decisions` still needs Boss’s flat ship $.
5. **Livestream banner must name a day or come down.** Kelly Ying prints Sun/Mon. Sassy currently prints the channel only. Empty cadence trains people to ignore the bar.
6. **Do not index-invent catalog.** Ten published pieces. No `A03` in marketing. Soft-launch `noindex` stays until Boss says otherwise.
7. **Icebreaker / greeting in Meta Inbox** (Owner): ask for the **web code** + cm; name Zelle/cash; refuse a ship `$`. [Greeting help](https://www.facebook.com/help/1698046970464236).
8. **Ads, if any:** Message destinations + Send message ([setup](https://www.facebook.com/business/help/212519562595207)). Prompts only for codes that are Available or Hold-for-price *right now*.
9. **Ops stay in the kit:** Inquiry on Facebook → Orders row (no PII in git) → Hold-extend in Slack → Owner Zelle / meetup → Owner Square Save. Agents draft.

---

## 12. Source list (URLs cited above)

### Meta / Facebook / Instagram

- https://www.facebook.com/business/help/1314349509894768
- https://developers.facebook.com/products/messenger/commerce/
- https://www.facebook.com/business/help/212519562595207
- https://www.facebook.com/business/help/269324800441478
- https://www.facebook.com/business/help/410873986524407
- https://developers.facebook.com/docs/messenger-platform/discovery/m-me-links/
- https://developers.facebook.com/docs/messenger-platform/instagram/features/ig-me-links
- https://developers.facebook.com/docs/messenger-platform/send-messages/
- https://www.facebook.com/help/977869848936797
- https://www.facebook.com/help/instagram/1419650861499317
- https://www.facebook.com/help/1698046970464236
- https://www.facebook.com/help/2329750133711372
- https://www.facebook.com/profile.php?id=61594312648057

### Shopify / industry context

- https://www.shopify.com/enterprise/blog/social-commerce-trends
- https://www.businessinsider.com/clothing-boutique-owners-facebook-live-commentsold-grow-sales-2021-7
- https://liveshopfront.com/how-to-start-live-selling-instagram-facebook

### Zelle / FTC / CFPB / police meetup

- https://www.zelle.com/faq/im-unsure-about-using-zelle-pay-someone-i-dont-know-what-should-i-do
- https://consumer.ftc.gov/consumer-alerts/2023/08/do-you-use-payment-apps-venmo-cashapp-or-zelle-read
- https://consumer.ftc.gov/articles/what-do-if-you-were-scammed
- https://www.ftc.gov/paymentapps
- https://reportfraud.ftc.gov/
- https://www.consumerfinance.gov/compliance/compliance-resources/deposit-accounts-resources/electronic-fund-transfers/electronic-fund-transfers-faqs/
- https://www.consumerfinance.gov/ask-cfpb/is-the-money-i-keep-in-my-payment-app-safe-en-2135/
- https://www.facebook.com/oaklandpoliceca/videos/opd-safe-exchange-zone/1272130354053634/
- https://www.facebook.com/BPPDMN/posts/we-encourage-you-to-be-safe-when-buying-and-selling-items-of-value-off-of-social/855488453289088/
- https://www.facebook.com/MonroeWAPolice/posts/safe-exchange-meetup-spots-available-at-the-monroe-police-departmentif-you-are-p/1193291967546571/

### Shipping promises / fee UX

- https://www.ftc.gov/legal-library/browse/rules/mail-internet-or-telephone-order-merchandise-rule
- https://www.ftc.gov/business-guidance/resources/business-guide-ftcs-mail-internet-or-telephone-order-merchandise-rule
- https://www.ftc.gov/business-guidance/resources/selling-internet-prompt-delivery-rules
- https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-435
- https://www.nngroup.com/articles/ecommerce-taxes-fees/
- https://baymard.com/learn/reduce-cart-abandonment

### Hold ops (industry, not shop law)

- https://topsource.global/blog/order-holds-playbook/
- https://www.uphance.com/blog/order-holds-when-to-use-which-type/

### Look reference (not Sassy prices)

- https://www.kellyyingboutique.net/
- https://www.loc8nearme.com/california/garden-grove/kelly-ying-boutique/6384948/
- https://localitybiz.com/32074742/kelly-ying-boutique-garden-grove

### This shop

- https://sassy-closet-shop.vercel.app
- https://sassy-closet-shop.vercel.app/m/A01
- https://sassy-closet-shop.vercel.app/m/P02
- https://sassy-closet.vercel.app
- Slack `#shop-decisions` (2026-09-04): Facebook is the store; Hold >24h is a yes/no; Zelle name locked; flat ship $ still needed from Boss; no Square Save until yes.

---

*Learn track. Agents draft. Owner posts, sends, takes Zelle, Saves Square.*
