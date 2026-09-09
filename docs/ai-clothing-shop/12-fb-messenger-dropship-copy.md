# LEARN 12 — FB Messenger dropship copy (VN+EN phrase bank)

Message-first clipboard for a Taobao dropship boutique that **discovers on Facebook / the lookbook** and **closes in Messenger**. Written for Sassy Closet. Sourced. Phrase-bank style.

**This file does not Send.** Inbox Desk / Mini Boss **draft**. Owner pastes into the Page inbox and taps Send. Agents do not hit Meta Send API, do not take Zelle, do not Save Square, do not mint mã, do not invent ship `$` or stock.

**Live APPLY target:** [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)  
Kelly Ying *look* is locked (Cormorant + Be Vietnam Pro, paper / blush / gold, `announce-fade`, no cart). Honesty is **type on existing chrome**, not a redesign.

**Sister files (do not collapse jobs):**

| Doc | Job | This file |
| --- | --- | --- |
| [LEARN 01](https://github.com/SkyLanter/Sassy-closet/pull/22) | Messenger storefront law (funnel, no-cart CTA, Zelle ritual) | We **fill the bubbles** |
| [LEARN 07](https://github.com/SkyLanter/Sassy-closet/pull/21) | Dropship *truth* (现货/预售, catalog ladder, APPLY warehouse out) | We **say that truth out loud** |
| [LEARN 08](https://github.com/SkyLanter/Sassy-closet/pull/26) | Hands (Inbox Desk + Buy Research hops) | We **expand the desk pack** into variants + address + clocks |
| [LEARN 02](https://github.com/SkyLanter/Sassy-closet/pull/19) | PDP color / size / Hold *words* | We keep Hold ≠ Reserved |
| Kit `excel-kit/inbox/gf_intake_reply_templates.md` | Boss → GF intake (OneDrive) | **Never** reuse as customer sales copy |

Facebook inbox is the store. Slack `#shop-decisions` is Boss yes/no. Messenger is **not** GF intake ([`excel-kit/prompts/GF_CLOTHES_INTAKE.md`](../../excel-kit/prompts/GF_CLOTHES_INTAKE.md)).

---

## 0. How to use this bank

### 0.1 Hard stops (print these first)

1. **Never invent mã.** Public lookbook codes today are exactly ten: `A01 S01 P01 P02 P03 P04 P05 K01 H01 A02` (live audit 2026-09-09, [sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)). Official Excel codes are `AO|QU|VA|AK|GI|PK|SET` + three digits — Stock reads Dashboard `B21:B27`; scripts refuse to mint ([`excel-kit/DESIGN_NOTES.md`](../../excel-kit/DESIGN_NOTES.md)). `/admin` “Next mã A03” is **not** assignment ([LEARN 07](https://github.com/SkyLanter/Sassy-closet/pull/21) §10.3). Do not add an 11th code in a customer bubble.
2. **Never invent ship `$`.** `#shop-decisions` (2026-09-04) still lists **flat ship $** as unlocked. Kelly Ying’s public “Flat rate $10 shipping on order $300+” is *their* number ([kellyyingboutique.net](https://www.kellyyingboutique.net/)) — do not copy the dollars. Intake footer already: `Ship toàn US.` with **no** `$` ([`sassy-closet/lib/captions.ts`](../../sassy-closet/lib/captions.ts)).
3. **Never invent stock / qty / “on hand.”** Square Free is on-hand SoT. Lookbook `qty: 1` is a **conversation unit**, not a counted warehouse body ([LEARN 07](https://github.com/SkyLanter/Sassy-closet/pull/21) §5.2). Live A01 still says “on hand” / “một chiếc đang có” — **do not repeat that lie** in Messenger (07 APPLY debt).
4. **Never invent USD.** Boss table only. `P02` / `P05` stay **Inbox for price**. Do not publish P05 hub `23`.
5. **Never invent a Zelle handle, tag, or phone.** Slack already: *Customer Service → reply pack (Zelle name locked)*. Slot `{zelle}` resolves from that pack — **not from git**.
6. **No Facebook Send / Post from a bot.** [Messenger Send API exists](https://developers.facebook.com/docs/messenger-platform/send-messages/); shop law forbids agent Send. Intake Ask already: `Mini Boss không gửi hộ` ([`sassy-closet/lib/ask-fallback.ts`](../../sassy-closet/lib/ask-fallback.ts)).
7. **Cite.** If a number, clock, or duty rate is not on a cited page or in the CS / Buy Research note *today*, leave the slot empty or say TBD.

Granola was not signed in (`granola.ai/mcp-signup`). Slack `#shop-decisions`, the live shop, kit law, and public FTC / Zelle / CBP / Meta / Taobao / USPS pages were read instead.

### 0.2 Slot dictionary (fill from truth, never guess)

| Slot | Filled from | Forbidden fill |
| --- | --- | --- |
| `{code}` | Printed lookbook code the buyer tapped, **or** Stock-assigned Official | `A03`, “similar to A01”, invented `AO015` |
| `{tb_color}` | Taobao 颜色 string *this check* (Buy Research) | “cái trong ảnh”, cover guess |
| `{asked}` | Buyer’s words | Staff synonym |
| `{cover_color}` | What the cover actually is | — |
| `{asia}` | Asia chip they said: `2XS XS S M L XL 2XL` ([`sassy-closet/lib/kinds.ts`](../../sassy-closet/lib/kinds.ts)) | US 0–12 / S=4 |
| `{cm}` | Bust / waist / hip they typed | Chart conversion |
| `{usd}` | Boss quote after R1 | P05 `23`, last week’s haul |
| `{n}` | Seller PDP / order 发货 **days** on the date checked | Vibes |
| `{band}` | Lead-time **band** you had a reasonable basis for | “2-day”, “tomorrow” |
| `{time_pt}` | Clock ≤24h from **now**, Pacific | “vài ngày” |
| `{zelle}` | Locked CS pack **display name** | Git, Page About, lookbook |
| `{old_band}` / `{new_date_with_basis}` | Prior promise / new date you can defend | Invented calendar |
| `{carrier}` | Real last-mile / international **carrier** number | Taobao order id, “generating…” |
| `{city}` | City / metro they typed (inquiry) | Full street at hello |
| `{attn}` `{street}` `{unit}` `{st}` `{zip}` `{phone}` | USPS block **after** Paid + ship path | Meetup home, git commit |
| `{public_spot}` | Owner-chosen public meetup | Invented neighborhood |
| `{included\|TBD}` | Duty / line as quoted or explicit TBD | “duty-free”, a % |

Empty slot → leave the placeholder or skip the sentence. Do not “helpfully” invent.

### 0.3 Three clocks named “24h” (never mix)

| Clock | Whose | What it is | Customer sentence |
| --- | --- | --- | --- |
| **Meta standard messaging window** | Platform | 24 hours from the person’s last qualifying action; API sends outside it fail ([Send a Message](https://developers.facebook.com/docs/messenger-platform/send-messages/)) | Do **not** tell the buyer “we only have 24h to chat.” Owner is a **human** in Page Inbox. Speed still matters: first reply in the same waking block PT ([Meta messaging best practices](https://www.facebook.com/business/help/269324800441478)). |
| **Shop customer reserve** | Sassy | Named buyer hold. Default **≤24h PT**. Past 24h = Slack `Hold {code} past 24h?` (`#shop-decisions` 2026-09-04) | “Giữ giúp 24h tới {time_pt}.” |
| **Taobao 现货 发货** | Seller | Platform C-end mind often **24h / 48h 发货 after pay** — **China domestic warehouse**, not a US porch ([淘宝网发货管理规范](https://jianghu.taobao.com/detail/47301_58664622); [发货合约](https://open.alitrip.com/docs/doc.htm?articleId=121094&docType=1)) | “Họ ghi gửi trong ~{n} ngày **nội địa TQ**.” |

A fourth word that is **not** 24h: **预售** = PDP 发货 clock in **days** ([淘宝预售业务协议规范](https://terms.alicdn.com/legal-agreement/terms/suit_bu1_taobao/suit_bu1_taobao202012010036_72763.html)). Do not rename 预售 “Hold” unless USD is also unknown.

### 0.4 Voice split (site ≠ thread)

| Surface | Voice | Why |
| --- | --- | --- |
| Lookbook / announcement / PDP | Kelly Ying *editorial*: short, uppercase tracking, bilingual crumb, almost no 💕 | Locked look ([LEARN 01](https://github.com/SkyLanter/Sassy-closet/pull/22) §1.3). Do not cute-ify the hero. |
| Messenger | Soft diaspora boutique: `iu`, `em`, one 💕 max per bubble, VN first if they wrote VN | Matches intake caption + Ask drafts. Still honest. |
| Slack `#shop-decisions` | One-line yes/no ask | Not customer chat |

Reply in the language they used. Mixed thread: **VI full, then one EN sentence**. Do not machine-translate size into US.

### 0.5 Allowlist (cite, do not grow)

Live tiles 2026-09-09:

| `{code}` | Kind | Public | USD on card |
| --- | --- | --- | --- |
| `A01` | TOP | Available | $25 |
| `A02` | TOP | Available | $22 |
| `S01` | SET | Available | $28 |
| `P01` | ACCESSORY | Available | $5 |
| `P02` | THERMOS | **Hold** | Inbox for price |
| `P03` | ACCESSORY | Available | $18 |
| `P04` | ACCESSORY | Available | $13 |
| `P05` | THERMOS | **Hold** | Inbox for price |
| `K01` | JACKET | Available | $37 |
| `H01` | HAIR | Available | $8 |

Worked examples in this bank use **those ten only**. `AO001` / `AO003` appear only as Slack *format* examples from `#shop-decisions` — **do not mint them**.

### 0.6 Phrase card format

Every card below:

- **ID** — stable handle for Inbox Desk / later Origin clipboard.
- **When / Never** — hop + veto.
- **Orders** — SoT hop if any (`Inquiry|Reserved|Paid|Shipped|Picked up|Cancelled` — exact, [`excel-kit/schema.py`](../../excel-kit/schema.py)).
- **Cite** — primary URL or shop law.
- **VI** then **EN** — paste-ready. Owner Sends.

---

## 1. Thread spine (which card, in order)

```text
Buyer taps Message {code} / types hello
        │
        ▼
[INQ-*] first reply + lock color / Asia+cm / city-or-pickup
        │
        ├─ tile is Hold (P02/P05) ──► [HOLD-SHOP-*]  no Zelle, no $
        ├─ missing code / photo-only ──► [INQ-ASK-CODE]
        └─ listed Available ──► Buy Research R1 (08 §10)
                │
                ├─ Pass 现货 ──► [LEAD-SPOT] + [INQ-QUOTE]
                ├─ Pass 预售 ──► [LEAD-PRE] + [INQ-QUOTE]
                ├─ color ≠ cover ──► [INQ-COLOR]
                └─ 无货 / 下架 ──► [INQ-GONE]  (consider tile Hold)
        │
Buyer asks “giữ giúp”
        ▼
[HOLD-24-*]  ≤24h PT · Slack if longer
        │
Buyer yes on quote
        ▼
[ZELLE-*]  locked name · no screenshot Paid
        │
Bank shows money ──► Orders Paid
        ▼
[ADDR-*]  only if fulfill=Ship · USPS block · confirm-back
   or [ADDR-PICKUP] / meetup
        │
Buy Research R2 → Boss 下单
        ▼
[LEAD-ORDERED] → [LEAD-TRACK-*] → Shipped / Picked up
        │
Slip past {band} ──► [LEAD-FTC]  same day you know
```

Do not skip R1 before `{usd}` or a customer reserve. Do not collect a **street** at hello. Do not 下单 on a JPEG.

---

## 2. Inquiry bank

Facebook hello → Orders **Inquiry** (`append_order_row.py --status Inquiry --channel Facebook`). Omit `--buyer` rather than invent a name. `--ma` only if it already exists ([`excel-kit/PROMPTS.md`](../../excel-kit/PROMPTS.md) task 3).

Cite: Facebook = store ([`README.md`](../../README.md)); first reply speed ([Meta messaging best practices](https://www.facebook.com/business/help/269324800441478)); no “on hand” ([LEARN 07](https://github.com/SkyLanter/Sassy-closet/pull/21) §9.2).

### INQ-01 — First reply, listed Available tile

**When:** Buyer named a **live Available** code, or tapped Message on one.  
**Never:** P02/P05; Wishlist; “còn hàng Square”; ship `$`.  
**Orders:** Inquiry.

**VI**

> Chào iu, mã **{code}** nha 💕  
> Shop **order Taobao** đúng màu / size em chọn, rồi ship US — không phải kho sẵn trong tủ.  
> Em gửi giúp:  
> 1) **tên màu** (không phải “cái trong ảnh”)  
> 2) size Á châu (**2XS–2XL**) + cm ngực / eo  
> 3) **city** hoặc muốn **pickup**  
> Giá / ngày nhận chốt sau khi Boss mở link check **đúng SKU · 现货 hay 预售**.  
> Zelle khi em yes. Mini Boss không giữ hàng hộ.

**EN**

> Hi — **{code}**. We order the Taobao SKU you pick, then ship US. This is not a back-room unit.  
> Send: **color name** (not “the one in the photo”) + Asia size (**2XS–2XL**) + bust/waist cm + city or pickup.  
> Price / ETA lock after we reopen the link (that color, spot vs pre-sale).  
> Zelle when you yes. No cart hold on the website.

**Why:** Repeats 07/08 first bubble, kills live PDP “on hand,” asks **city not street**, names Asia chips from [`kinds.ts`](../../sassy-closet/lib/kinds.ts).

### INQ-02 — First reply, shop Hold / Inbox for price (`P02` / `P05` shape)

**When:** Tile is Hold · Inbox for price.  
**Never:** Draft `$23` for P05. Do not read this Hold as “someone else reserved it.”  
**Orders:** Inquiry. Do **not** Reserved.

**VI**

> **{code}** đang **Hold** — shop đang kiểm tra ảnh / giá, **chưa có USD trên web**.  
> Em gửi thêm ảnh thật em cần + số đo giúp.  
> **Chưa Zelle.** Chưa giữ chỗ. Hold trên site ≠ đã giữ cho bạn khác.

**EN**

> **{code}** is on **Hold** — photo-check, **no USD on the card**.  
> Send the photos / measurements you need.  
> **No Zelle yet.** Site Hold is not “reserved for someone else.”

Cite: live [`/m/P02`](https://sassy-closet-shop.vercel.app/m/P02) (“Hold · photo-check, no USD yet”); [LEARN 01](https://github.com/SkyLanter/Sassy-closet/pull/22) §3.1.

### INQ-03 — No code / photo-only hello

**When:** “Còn cái váy live không?” / screenshot without a mã.  
**Never:** Guess `A01`. Never invent a hunt mã.

**VI**

> Iu gửi **mã trên web** giúp (ví dụ **A01**, **K01** — đúng chữ trên card).  
> Shop không đoán món từ ảnh live. Không tự đặt mã mới.

**EN**

> Send the **code on the card** (example: **A01**, **K01** — the letters you see).  
> We do not guess the piece from a live screenshot. We do not invent a new code.

Cite: lookbook codes are the join key ([LEARN 01](https://github.com/SkyLanter/Sassy-closet/pull/22) §9). Examples are **on the allowlist**, not new SKUs.

### INQ-04 — Code not on the allowlist / not on site

**When:** They typed `A03`, `AO001`, `V984`, or a Kelly Ying SKU.  
**Never:** “Để em lấy mã AO…” / Next mã.

**VI**

> Shop **không thấy mã đó** trên lookbook hôm nay.  
> Lookbook đang có: **A01 A02 S01 P01 P02 P03 P04 P05 K01 H01**.  
> Em gửi đúng mã trên card, hoặc ảnh card. Mini Boss **không invent mã**.

**EN**

> That code is **not on today’s lookbook**.  
> Live codes: **A01 A02 S01 P01 P02 P03 P04 P05 K01 H01**.  
> Send a card code or a photo of the card. We do not invent codes.

Cite: Ask fallback “Không thấy {ma} trên site. Hỏi Stock / Boss — Mini Boss không invent mã.” ([`ask-fallback.ts`](../../sassy-closet/lib/ask-fallback.ts)).

### INQ-05 — Size: Asia + cm only

**When:** They ask “US 4 / M Mỹ?”  
**Never:** Convert. [DESIGN_NOTES](../../excel-kit/DESIGN_NOTES.md) refuse list: no US sizes to customers.

**VI**

> Size shop dùng **Á châu: 2XS XS S M L XL 2XL** + **cm** (ngực / eo / mông).  
> Không đổi sang size Mỹ. Em đo giúp 1 lần — Boss đối chiếu chart shop TQ, không đoán.

**EN**

> We use **Asia sizes (2XS–2XL)** plus **cm** (bust / waist / hip).  
> We do not convert to US sizes. Measure once — we match the seller chart, we do not guess.

Cite: [`kinds.ts`](../../sassy-closet/lib/kinds.ts) `SIZES`; Ask fallback size line.

### INQ-06 — Color name vs cover (two SKUs)

**When:** Cover ≠ asked color, or “order giúp cái đẹp nhất.”  
**Never:** Order the pretty photo.

**VI**

> Ảnh bìa là **{cover_color}**. Em đang hỏi **{asked}**.  
> Đó là **hai SKU Taobao**. Em chọn **một** giúp — shop không order “cái đẹp nhất trong ảnh.”

**EN**

> Cover is **{cover_color}**. You asked **{asked}**.  
> Those are **two Taobao SKUs**. Pick **one** — we will not order “whichever looks best in the photo.”

Cite: [LEARN 07](https://github.com/SkyLanter/Sassy-closet/pull/21) §7–§8; [taobao.item.sku.get](https://open.alitrip.com/docs/api.htm?apiId=38967) (per-SKU 颜色).

### INQ-07 — Quote after Buy Research Pass (do not Send before R1)

**When:** R1 Pass or Pass-预售; Boss locked `{usd}` and `{band}` and `{included|TBD}`.  
**Never:** Before R1; if any slot empty.

**VI**

> Boss mở link **{code}** · màu **{tb_color}** · size **{asia}** + **{cm}**.  
> **{现货|预售}** — cửa sổ nhận khoảng **{band}** (xem tin lead time). Duty / line: **{included|TBD}**.  
> Giá chốt **${usd}**. Web **chưa in phí ship** — ship báo **số** trong chat khi em yes ship.  
> Local pickup / cash thì không ship. Yes thì mình gửi tên Zelle.

**EN**

> We reopened **{code}** · **{tb_color}** · **{asia}** + **{cm}**.  
> **{spot|pre-sale}** — receive window about **{band}** (see lead-time bubble). Duty / line: **{included|TBD}**.  
> Locked **${usd}**. Site has **no printed ship fee** — we quote ship **in chat** if you want ship.  
> Local pickup / cash = no ship. Yes → we send the Zelle name.

Cite: unlocked flat ship $ (Slack 2026-09-04); [NN/g hidden fees](https://www.nngroup.com/articles/ecommerce-taxes-fees/) — admit unknown extras; CBP no de minimis for CN/HK from 2025-05-02 ([CSMS #64917563](https://content.govdelivery.com/accounts/USDHSCBP/bulletins/3de903b)).

### INQ-08 — SKU gone / 下架 / 无货

**When:** R1 or R2: that 颜色×尺码 qty 0 or link 404.  
**Never:** “Similar A03”; invent `source_link`.

**VI**

> Hôm nay link **{code} / {tb_color}** hết hoặc gỡ.  
> Site có thể còn **Available** vì chưa Hold. **Chưa order được.**  
> Em muốn Boss check **màu khác trên cùng món** (SKU mới) — hoặc để Hold inbox giá?

**EN**

> Today **{code} / {tb_color}** is gone or the link is down.  
> The site may still say Available if we have not flipped Hold. **We cannot order it.**  
> Want another **color on the same look** (new SKU check) — or Hold / inbox for price?

Cite: [LEARN 08](https://github.com/SkyLanter/Sassy-closet/pull/26) §8.3 / §9.6; [`source-link.ts`](../../sassy-closet/lib/source-link.ts) extract-only (PR #16).

### INQ-09 — Hunt / Wishlist (not a lookbook tile)

**When:** They want a piece that is **not** one of the ten.  
**Never:** “Hàng đang bán.” Never mint.

**VI**

> Món này **chưa lên lookbook** — đang xem / ứng viên, **chưa lên Square**, chưa bán.  
> Em giữ link Taobao nếu có. **Đừng tự đặt mã.** Khi Boss chốt, mình inbox lại.

**EN**

> This look is **not on the lookbook** — hunt / candidate, **not on Square**, not for sale.  
> Keep the Taobao link if you have one. **Do not invent a code.** We will write when Boss decides.

Cite: GF templates ([`gf_intake_reply_templates.md`](../../excel-kit/inbox/gf_intake_reply_templates.md)); Messenger is not the intake inbox.

### INQ-10 — Icebreaker landing (they tapped a prompt)

**When:** Ad / icebreaker `Còn A01 không?` — **only if A01 is still Available**.  
**Never:** Prompt for a sold / gone code.

**VI**

> Có, **A01** đang trên lookbook 💕 Inbox đúng mã rồi.  
> Gửi màu + size Á châu + cm + city / pickup. Shop check SKU rồi báo giá / 现货-预售.

**EN**

> Yes — **A01** is on the lookbook. You already sent the code.  
> Send color + Asia size + cm + city / pickup. We check that SKU, then quote + spot vs pre-sale.

Cite: [click-to-Messenger ads](https://www.facebook.com/business/help/212519562595207); 01 §2.4 — prompts only for codes that are live *right now*. Swap `{code}` from allowlist; do not keep A01 if the tile flipped.

---

## 3. Hold 24h bank

Three Holds ([LEARN 07](https://github.com/SkyLanter/Sassy-closet/pull/21) §4.1). This section is the **customer reserve clock** plus the two clarifiers.

Cite: Slack example `Hold AO003 past 24h?` (format only — do not mint `AO003`); apparel 24h escalate ([TopSource holds playbook](https://topsource.global/blog/order-holds-playbook/), [Uphance](https://www.uphance.com/blog/order-holds-when-to-use-which-type/)).

### HOLD-SHOP-01 — Merchandising Hold (not a reserve)

Same as **INQ-02**. Repeat if they say “ai giữ rồi?”

**VI**

> Hold trên **{code}** là **chưa có giá / đang check ảnh** — không phải đã giữ cho khách khác.

**EN**

> Hold on **{code}** means **no price yet / photo-check** — not “already reserved for someone else.”

### HOLD-24-01 — Start customer reserve (≤24h PT)

**When:** Available (or honest quoted SKU) + they asked to hold + R1 has not failed.  
**Never:** P02/P05 before Boss prices; past 24h without Slack yes; bot extend.  
**Orders:** `Reserved` only if Official / staff agree this is a **named** reserve (01 §3.4). Lookbook tile stays Available unless Boss flips it.

**VI**

> Giữ **{code} · {tb_color} · {asia}** giúp em **24 giờ** — tới **{time_pt} PT**.  
> Inbox trước giờ đó để **Zelle** hoặc hẹn mặt.  
> Sau giờ đó món về Available trên site — trừ khi Boss **yes** thêm giờ trên Slack.  
> Giữ chỗ **không** trừ kho Square (dropship). Không giữ quá 24h tự ý.

**EN**

> Holding **{code} · {tb_color} · {asia}** for **24 hours** — until **{time_pt} PT**.  
> Write before then to **Zelle** or set meetup.  
> After that it returns to Available on the site — unless Boss **yes** on Slack for more time.  
> A hold is **not** a Square decrement (dropship). We do not self-extend past 24h.

`{time_pt}` = now + ≤24h, Pacific (Bot_Activity times are PT — [`append_bot_activity.py`](../../excel-kit/sot/append_bot_activity.py)).

### HOLD-24-02 — They ask for 2–3 days / “giữ tới cuối tuần”

**When:** Requested clock **>24h**.  
**Never:** Say yes in Messenger first.

**VI**

> Giữ **quá 24 giờ** thì Boss phải yes trên Slack.  
> Mình hỏi giúp. Chưa yes thì mình **chưa hứa** giữ. Em Zelle trong 24h thì chắc hơn.

**EN**

> Holds **past 24 hours** need a Boss yes on Slack.  
> Asking now. Until yes, we **have not promised** the extra time. Zelle inside 24h is the sure path.

**Slack draft (not customer):**

> Hold {code} {tb_color} {asia} past 24h?

Cite: `#shop-decisions` purpose (Save / mã / price / **hold extend**).

### HOLD-24-03 — Screenshot stall (clock still running)

**When:** They sent a JPEG “paid” during a reserve.  
**Never:** Flip Paid.

**VI**

> Mình cần thấy tiền trong **app ngân hàng**. Screenshot chưa tính.  
> Giữ **{code}** tới **{time_pt} PT** (còn trong 24h). Giờ đó tới mà chưa thấy Zelle thì hết giữ.

**EN**

> We need the money on the **bank / Zelle activity** screen. A screenshot does not count.  
> Hold on **{code}** until **{time_pt} PT** (still inside 24h). If we do not see Zelle by then, the hold ends.

Cite: Zelle cannot reverse + completed ≠ JPEG ([Zelle FAQ](https://www.zelle.com/faq/im-unsure-about-using-zelle-pay-someone-i-dont-know-what-should-i-do)); 08 §9.10.

### HOLD-24-04 — Clock expired, no Slack yes

**When:** `{time_pt}` passed; Boss did not extend.

**VI**

> Hết giờ giữ **{code}** rồi iu 💕 Món về Available.  
> Vẫn muốn thì inbox lại — Boss check SKU **hôm nay** (có thể hết màu).

**EN**

> The hold on **{code}** ended. It is Available again.  
> Still want it — write again. We re-check that SKU **today** (the color may be gone).

### HOLD-24-05 — Already reserved for someone else

**When:** Another named reserve is live (≤24h or Slack-extended).  
**Never:** Oversell the same 颜色×尺码 as if unique-owned unless Square says so.

**VI**

> **{code}** đang giữ cho bạn khác (≤24h trừ khi Boss yes).  
> Em muốn mình **báo khi về Available** không? Không giữ hàng hộ ngoài clock đó.

**EN**

> **{code}** is held for someone else (≤24h unless Boss yes).  
> Want a ping when it is Available again? We do not hold a second secret queue.

Cite: 01 §10; 08 §9.15.

### HOLD-24-06 — Slack yes to extend (Owner then Sends)

**When:** `#shop-decisions` replied **yes**.  
**Never:** Before the yes.

**VI**

> Boss yes — giữ **{code}** thêm tới **{time_pt} PT**.  
> Inbox Zelle / hẹn mặt trước giờ mới. Sau đó hết giữ.

**EN**

> Boss yes — holding **{code}** until **{time_pt} PT**.  
> Zelle / meetup before the new time. Then the hold ends.

### HOLD-24-07 — Do not confuse with Meta’s window

**When:** Staff wants to “nudge before 24h API.”  
**Never:** Customer-facing “chat hết hạn.”

Staff only (not a buyer paste):

> Meta 24h window is an **API** rule. Owner replies as a human in Inbox. Customer reserve 24h is **shop law**. Do not threaten “thread dies at 24h.”

Cite: [standard messaging window](https://developers.facebook.com/docs/messenger-platform/send-messages/).

---

## 4. Zelle bank

No-card on purpose ([LEARN 01](https://github.com/SkyLanter/Sassy-closet/pull/22) §4). Footer may say the **word** Zelle. **No** name / handle / phone on the site ([LEARN 07](https://github.com/SkyLanter/Sassy-closet/pull/21) hard stop; PR #18).

Zelle’s own words: use with people you **know and trust**; if unsure you will get what you paid for (online sales), they recommend you **do not** use Zelle; **no purchase protection**; payments to an enrolled recipient **cannot be reversed** ([Zelle FAQ](https://www.zelle.com/faq/im-unsure-about-using-zelle-pay-someone-i-dont-know-what-should-i-do)).

FTC: sending money through a payment app is **like sending cash** ([FTC payment-app alert](https://consumer.ftc.gov/consumer-alerts/2023/08/do-you-use-payment-apps-venmo-cashapp-or-zelle-read); [ftc.gov/paymentapps](https://www.ftc.gov/paymentapps)).

Venmo is on the SoT pay list. **Do not publish a Venmo CTA** until Boss writes a handle in the CS pack (01 §4.4).

### ZELLE-01 — Ask (name locked, protection said out loud)

**When:** Quote accepted (or cash meetup declined) and `{zelle}` is in the CS pack.  
**Never:** Before `{usd}` exists (except cash-meetup path). Never paste a handle from memory if the pack is not open.  
**Orders:** still Unpaid until bank.

**VI**

> Zelle giúp shop nhận nhanh.  
> Zelle **không có bảo vệ mua hàng** — gửi là như gửi tiền mặt, **không hoàn chiều** ([FAQ Zelle](https://www.zelle.com/faq/im-unsure-about-using-zelle-pay-someone-i-dont-know-what-should-i-do)).  
> Em chỉ Zelle **đúng tên: {zelle}** — tên hiện trên app phải khớp.  
> Không bấm **link lạ**, không “upgrade Zelle business,” không QR từ người lạ.  
> Memo: **{code} {tb_color} {asia}**.  
> Mình xác nhận khi thấy tiền trong **app ngân hàng**. Screenshot chưa tính.

**EN**

> Zelle is how we take payment.  
> Zelle **does not offer purchase protection** — it is like cash and **cannot be reversed** ([Zelle FAQ](https://www.zelle.com/faq/im-unsure-about-using-zelle-pay-someone-i-dont-know-what-should-i-do)).  
> Send only to **this exact name: {zelle}**. The name on your screen must match.  
> No mystery links, no “upgrade to business Zelle,” no stranger QR.  
> Memo: **{code} {tb_color} {asia}**.  
> We confirm on the **bank / Zelle activity** screen. Screenshots do not count.

QR is OK **only** if it is the shop’s own bank QR and the **displayed name** matches `{zelle}` ([same FAQ — Zelle QR](https://www.zelle.com/faq/im-unsure-about-using-zelle-pay-someone-i-dont-know-what-should-i-do)).

### ZELLE-02 — Refuse to draft pay (desk veto)

**When:** Any of: no R1; P02/P05 unpriced; 无货; `{usd}` empty; they want “pay a different name.”  
**Never:** Soft-yes.

**VI**

> Chưa gửi tên Zelle được.  
> Thiếu: **{SKU check / giá Boss / còn hàng màu này}**.  
> Shop không nhận Zelle “trước, tính sau.”

**EN**

> We cannot send a Zelle name yet.  
> Missing: **{SKU check / Boss price / that color still orderable}**.  
> We do not take Zelle “now, figure it out later.”

Cite: 08 §5.3.

### ZELLE-03 — Screenshot / email “receipt”

**VI**

> Cảm ơn ảnh. Shop **chưa** ghi Paid.  
> Mình mở app ngân hàng. Khi thấy Zelle **{zelle}** đúng số **${usd}**, mình nhắn lại.  
> Giữ **{code}** tới **{time_pt} PT** nếu đang trong clock 24h.

**EN**

> Thanks for the image. We have **not** marked Paid.  
> Checking the bank app. When Zelle to **{zelle}** shows **${usd}**, we will write.  
> Hold on **{code}** until **{time_pt} PT** if a 24h reserve is running.

### ZELLE-04 — Wrong name / overpay / “refund the extra”

**When:** Classic P2P fraud shapes (01 §5.4).  
**Never:** Send money back from a bot. Zelle **cannot reverse**; Owner sends a **new** payment only if Boss says so.

**VI**

> Tên trên Zelle **không khớp {zelle}** — em **đừng** gửi thêm, đừng “refund giúp.”  
> Shop không bảo em upgrade account. Nếu đã gửi nhầm, em báo **ngân hàng em**.  
> Đơn mình **chưa** Paid.

**EN**

> The Zelle name **does not match {zelle}** — do **not** send more, do not “refund the extra.”  
> We never ask you to upgrade an account. If you sent to the wrong person, call **your** bank.  
> This order is **not** Paid.

Cite: FTC like-cash; Zelle no reverse; FTC [what to do if you were scammed](https://consumer.ftc.gov/articles/what-do-if-you-were-scammed).

### ZELLE-05 — Bank confirmed → Paid

**When:** Owner sees the ledger.  
**Orders:** `Paid`, `pay_method=Zelle`. Then R2 **before** 下单.

**VI**

> Thấy Zelle rồi 💕 Đúng **${usd}**.  
> Shop đặt **đúng SKU {tb_color} / {asia}** trên Taobao sau khi check link lần nữa.  
> Nếu **ship**: gửi địa chỉ theo tin address (tên + street + APT + city + state + ZIP + phone).  
> Nếu **pickup / meetup**: không cần street nhà.  
> Tracking US khi có **mã carrier** — 现货 48h là kho TQ, không phải porch em.

**EN**

> Zelle is in the bank 💕 **${usd}** matches.  
> We order the **exact SKU {tb_color} / {asia}** after one more link check.  
> **Ship:** send the address block in the next bubble (name + street + APT + city + state + ZIP + phone).  
> **Pickup / meetup:** no home street.  
> US tracking when we have a **carrier** number — a 48h 现货 clock is their China warehouse, not your porch.

### ZELLE-06 — Cash meetup alternative (no street)

**When:** They do not want Zelle. Owner picks the spot.  
**Never:** Publish a home address. Never invent a city.

**VI**

> Cash **chỗ công cộng** Owner chọn — không đổi chỗ sau khi chốt, không đưa địa chỉ nhà lên chat rộng.  
> Xem món, đếm tiền, xong. **Không** “về nhà rồi Zelle.”  
> Facebook khuyên giữ địa chỉ nhà riêng, báo người tin cậy, điện thoại đủ pin ([Marketplace in-person](https://www.facebook.com/help/2329750133711372)).

**EN**

> Cash at a **public spot the Owner picks** — do not change the spot after we agree; do not put a home address in a wide thread.  
> Inspect the piece, count cash, done. **No** “I’ll Zelle when I get home.”  
> Facebook: keep the home address private; tell a trusted person; charged phone ([in-person tips](https://www.facebook.com/help/2329750133711372)).

`{public_spot}` only after Owner names it. Caption ceiling until then: `Local cash/Zelle` ([`captions.ts`](../../sassy-closet/lib/captions.ts)).

### ZELLE-07 — Refund path (Owner, new send)

**When:** FTC cancel / 无货 after Paid.  
**Never:** “Zelle reverse.”

**VI**

> Shop hoàn **${usd}** bằng Zelle **mới** về đúng tên em đã gửi — Zelle **không đảo** giao dịch cũ ([FAQ](https://www.zelle.com/faq/im-unsure-about-using-zelle-pay-someone-i-dont-know-what-should-i-do)).  
> Owner bấm trên app ngân hàng. Bot không chuyển tiền.

**EN**

> We refund **${usd}** as a **new** Zelle to the name you paid from — Zelle **does not reverse** the old payment ([FAQ](https://www.zelle.com/faq/im-unsure-about-using-zelle-pay-someone-i-dont-know-what-should-i-do)).  
> Owner taps the bank app. Bots do not move money.

Prompt refund timing: FTC **prompt refund** for cash-like / non-enumerated methods is **seven working days** after the refund right vests ([16 CFR 435.1](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-435); [FTC business guide](https://www.ftc.gov/business-guidance/resources/business-guide-ftcs-mail-internet-or-telephone-order-merchandise-rule)). Do not promise “instant” unless Owner is at the app.

---

## 5. Address collect bank

Collect **coarse** location at Inquiry (`{city}` / pickup). Collect the **USPS delivery block** only after **Paid** and `fulfill=Ship`.

Why wait:

- A Messenger “ship it to Texas” **is** a mail / internet / telephone order **regardless of how advertised or paid** ([16 CFR 435.1](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-435); [FTC business guide](https://www.ftc.gov/business-guidance/resources/business-guide-ftcs-mail-internet-or-telephone-order-merchandise-rule)). “Receipt of a properly completed order” includes **payment + all information needed to ship**. Asking for the street **before** they have accepted `{usd}` + `{band}` + duty TBD invites a half-order and a 30-day clock you cannot defend.
- PII: SoT Orders may store `buyer` / `fb_handle` on the **working copy**; **never commit** names, streets, or phones to git ([`PROMPTS.md`](../../excel-kit/PROMPTS.md)). `thread_note` is staff, not customer JSON (PR #18).
- Meetup: **no home street** ([Facebook in-person](https://www.facebook.com/help/2329750133711372)).

USPS wants a **complete** delivery address: attention, delivery line (street + APT/STE on the **same** line or the line **above** the street, never below), last line city + state + ZIP ([Postal Explorer — Delivery Address](https://pe.usps.com/businessmail101?ViewName=DeliveryAddress); [Publication 28 ch. 2](https://pe.usps.com/text/pub28/28c2_001.htm)). ~25% of pieces are missing an apartment or have a bad ZIP — ask `{unit}` on purpose.

Shop ships **US** (`Ship toàn US.`). Do not collect a non-US block unless Boss opens that lane.

**Never invent ship `$` in these bubbles.**

### ADDR-01 — Inquiry: city / pickup only

**When:** INQ-01 follow-up if they skipped item 3.  
**Never:** “Gửi full address.”

**VI**

> Em ở **city / metro** nào, hoặc muốn **pickup**?  
> Chưa cần số nhà. Street gửi **sau khi Zelle xong** nếu em chọn ship.

**EN**

> Which **city / metro**, or do you want **pickup**?  
> No street yet. We ask the delivery block **after Zelle** if you choose ship.

### ADDR-02 — After Paid: request the USPS block

**When:** `Paid` + they chose ship.  
**Never:** Before bank; for meetup.

**VI**

> Gửi địa chỉ **giao hàng US** giúp, **một block**, đủ dòng:  
> 1) Tên người nhận `{attn}`  
> 2) Số + tên đường `{street}` + **APT/STE/UNIT `{unit}`** (nếu có — thiếu APT hay bị trả về)  
> 3) City `{city}` + state `{st}` + ZIP `{zip}`  
> 4) SĐT `{phone}` (carrier gọi)  
> USPS đọc dưới lên: city / state / ZIP rồi mới tới street ([Postal Explorer](https://pe.usps.com/businessmail101?ViewName=DeliveryAddress)).  
> **Chưa** báo phí ship `$` trên web — mình báo **số** trong chat khi Boss chốt line. Duty / thuế nhập: **{included|TBD}** (CN/HK **không** de minimis từ 2025-05-02 — [CBP CSMS #64917563](https://content.govdelivery.com/accounts/USDHSCBP/bulletins/3de903b)).  
> Không gửi địa chỉ nhà nếu em **meetup**.

**EN**

> Send one **US delivery block**:  
> 1) Recipient `{attn}`  
> 2) Street `{street}` + **APT/STE/UNIT `{unit}`** (missing APT is a common fail)  
> 3) City `{city}` + state `{st}` + ZIP `{zip}`  
> 4) Phone `{phone}` (carrier)  
> USPS reads bottom-up: city / state / ZIP, then street ([Postal Explorer](https://pe.usps.com/businessmail101?ViewName=DeliveryAddress)).  
> **No** printed ship `$` on the site — we quote a **number in chat** when Boss locks the line. Duty: **{included|TBD}** (CN/HK **not** de minimis as of 2025-05-02 — [CBP CSMS #64917563](https://content.govdelivery.com/accounts/USDHSCBP/bulletins/3de903b)).  
> Skip this if you **meetup**.

### ADDR-03 — Confirm-back (read it to them)

**When:** They pasted a block. Owner / Desk reads it back.  
**Never:** Silently copy into 下单.

**VI**

> Mình đọc lại — em reply **YES** nếu đúng:  
> `{attn}`  
> `{street} {unit}`  
> `{city} {st} {zip}`  
> `{phone}`  
> Sai một ký tự em sửa. Chưa YES thì chưa ghi lên đơn.

**EN**

> Reading back — reply **YES** if this is exact:  
> `{attn}`  
> `{street} {unit}`  
> `{city} {st} {zip}`  
> `{phone}`  
> Fix any character. No YES → we do not write it on the order.

Cite: USPS: missing directional / apartment misroutes ([Postal Explorer tips](https://pe.usps.com/businessmail101?ViewName=DeliveryAddress)). Confirm-back is the cheap check.

### ADDR-04 — Missing APT / ZIP / phone

**VI**

> Thiếu **{APT hoặc ZIP 5 số hoặc SĐT}**.  
> USPS hay kẹt vì thiếu apartment / ZIP sai. Em bổ sung giúp — shop không đoán số nhà.

**EN**

> Missing **{APT or 5-digit ZIP or phone}**.  
> USPS often stalls on a missing apartment or a bad ZIP. Add it — we will not guess a unit number.

ZIP lookup: [USPS ZIP Code Lookup](https://tools.usps.com/zip-code-lookup.htm) (Owner may verify; do not invent a ZIP+4 to look finished). Publication 28: last line city, state, ZIP ([ch. 2](https://pe.usps.com/text/pub28/28c2_001.htm)).

### ADDR-05 — PO Box / locker / “leave with neighbor”

**When:** They offered a Box or a workaround.  
**Never:** Promise a carrier that rejects Box / signature.

**VI**

> PO Box / locker: Boss check **line ship** có nhận không.  
> Chưa yes thì chưa hứa. Không để “gửi hộ hàng xóm” nếu carrier cần chữ ký.

**EN**

> PO Box / locker: Boss checks whether **this** ship line accepts it.  
> No promise until that check. We will not “leave with a neighbor” if the carrier needs a signature.

Do not name a carrier you have not booked.

### ADDR-06 — Pickup / meetup instead (refuse street)

**VI**

> Pickup / meetup thì **đừng** gửi số nhà.  
> Owner chọn chỗ công cộng `{public_spot}` — hoặc “TBD chỗ public, mình báo.”  
> Cash đủ, xem món, xong.

**EN**

> Pickup / meetup: **do not** send a home street.  
> Owner picks a public spot `{public_spot}` — or “TBD public, we will name it.”  
> Cash in full, inspect, done.

### ADDR-07 — Duty / line honesty (no rate theater)

**When:** They ask “free duty? $8 ship?”  
**Never:** Bake 54% / 120% / Kelly `$10` / `$6.95 USPS`.

**VI**

> Ship **toàn US** — **số phí** báo trong chat, web chưa in vì Boss chưa chốt flat $.  
> Hàng TQ/HK **không** còn cửa de minimis (từ **2025-05-02**) — duty **có thể** có; shop nói **included hoặc TBD**, không nói “duty-free.”  
> Tổng = giá món **${usd}** + ship (khi có số) + duty (nếu TBD thì nói trước khi Zelle).

**EN**

> We ship **US-wide** — the **fee number** is in chat; the site does not print it because Boss has not locked a flat ship $.  
> CN/HK goods **lost** de minimis (2025-05-02) — duty **may** apply; we say **included or TBD**, never “duty-free.”  
> Total = piece **${usd}** + ship (once numbered) + duty (if TBD, say so **before** Zelle).

Cite: [CSMS #64917563](https://content.govdelivery.com/accounts/USDHSCBP/bulletins/3de903b); later broader suspension notice ([90 FR / EO 14324](https://www.federalregister.gov/documents/2025/08/29/2025-16802/notice-of-implementation-of-the-president-s-executive-order-14324-suspending-duty-free-de-minimis)) — **rates still not for customer copy**; [NN/g](https://www.nngroup.com/articles/ecommerce-taxes-fees/).

### ADDR-08 — Change-of-address after 下单

**VI**

> Đơn đã đặt — đổi địa chỉ **không chắc**.  
> Em gửi block mới; Boss hỏi line. Chưa yes thì giữ block cũ. Không hứa intercept.

**EN**

> The Taobao order is already placed — an address change is **not guaranteed**.  
> Send the new block; Boss asks the line. Until yes, the old block stands. We do not promise an intercept.

### ADDR-09 — Staff hygiene (not a buyer paste)

> Paste the YES block into OneDrive / SoT Orders `thread_note` on the **shop machine**.  
> **Never** git, never Bot_Activity summary, never sell-catalog JSON, never a screenshot in `#shop-decisions`.

Cite: [`PROMPTS.md`](../../excel-kit/PROMPTS.md) “Omit --buyer rather than invent”; PR #18 omit customer PII from client catalog.

---

## 6. Lead time bank

Stack to say out loud ([LEARN 07](https://github.com/SkyLanter/Sassy-closet/pull/21) §4.4):

| Leg | 现货-ish | 预售-ish |
| --- | --- | --- |
| Seller 发货 | Often 24–48h **China** after pay; some shops 3–10d | PDP days (fashion 15–90d shows up in the wild) |
| CN line → US | Days–weeks; holidays / 工厂放假 **not** in the PDP day count | Same, **after** 发货 |
| US last mile | After a **carrier** number exists | Same |

Consumer terms: 发货时间 **以宝贝详情页为准** ([淘宝预售业务协议规范](https://terms.alicdn.com/legal-agreement/terms/suit_bu1_taobao/suit_bu1_taobao202012010036_72763.html)).

Title 现货 can become order 预售 — documented bait ([读特 / 腾讯 2025-02](https://news.qq.com/rain/a/20250221A098Y800)). Believe **order + SKU clock**, not the title.

FTC 30-day Rule: if you state a time, you need a **reasonable basis**; if you state **nothing**, you still need a basis to ship within **30 days** of a properly completed order; if you will miss, offer **delay-or-refund** clearly, without them asking ([FTC business guide](https://www.ftc.gov/business-guidance/resources/business-guide-ftcs-mail-internet-or-telephone-order-merchandise-rule); [16 CFR 435](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-435)). A dropship 预售 band **is** a stated time. If the factory slips, run **LEAD-FTC** the day you know.

**Never quote “48h” as the porch date.**

### LEAD-WAIT — Unknown until R1

**VI**

> Để Boss mở link xong báo ngày. **Chưa yes thì chưa Zelle.**  
> Chưa có cửa sổ thì shop **không** nói “2 tuần” cho có.

**EN**

> We open the link, then we name a window. **No Zelle until you yes.**  
> If we do not have a window yet, we will **not** invent “2 weeks.”

### LEAD-SPOT — 现货 confirm

**VI**

> Màu **{tb_color}** đang **现货** — shop TQ ghi gửi trong ~**{n} ngày** (**nội địa TQ**, thường 24–48h kho họ).  
> Cộng chuyển US. Cửa sổ nhận khoảng **{band}**.  
> **Không** chốt ngày lịch trên porch. 48h ≠ tới tay em.

**EN**

> **{tb_color}** is **现货 / spot** — they list ship-out in ~**{n} days** (**China domestic**, often 24–48h from *their* warehouse).  
> Plus US transit. Receive window about **{band}**.  
> **No** porch calendar date. 48h is not your doorstep.

Cite: [发货管理规范](https://jianghu.taobao.com/detail/47301_58664622); OpenAPI `deliveryTimeType` 0 = 48h, 3 = 24h ([发货合约](https://open.alitrip.com/docs/doc.htm?articleId=121094&docType=1)).

### LEAD-PRE — 预售 confirm

**VI**

> Món **{code}** màu **{tb_color}** đang **预售 / đặt trước**.  
> Shop họ ghi ~**{n} ngày** mới **gửi** (theo trang PDP, **chưa kể** ngày lễ xưởng / ship US).  
> Không hứa ngày lịch. Vẫn muốn thì em yes + Zelle **{zelle}**, shop đặt. Không thì thôi — **không** giữ giá.

**EN**

> **{code}** in **{tb_color}** is **预售 / pre-sale**.  
> They list ~**{n} days** to **ship-out** (PDP clock, **excluding** factory holidays / US transit).  
> No porch date. Still want it → yes + Zelle **{zelle}**, we place. Otherwise we **do not** hold the price.

Cite: [预售协议](https://terms.alicdn.com/legal-agreement/terms/suit_bu1_taobao/suit_bu1_taobao202012010036_72763.html); mixed-cart wait / 45–90d paste ([r/taobao](https://www.reddit.com/r/taobao/comments/o0ghiw/does_anyone_know_what_presale_means_on_taobao/)) as **color**, not shop law.

### LEAD-BAIT — Title said 现货, order says 预售

**VI**

> Title / 客服 ghi 现货, **đơn** ghi 预售 ~**{n} ngày**. Shop tin **đơn**.  
> Cửa sổ mới: **{band}**. Em chọn **đợi** hoặc **hoàn** (tin FTC).

**EN**

> Title / chat said spot; the **order** says pre-sale ~**{n} days**. We believe the **order**.  
> New window: **{band}**. You choose **wait** or **refund** (FTC bubble).

Cite: [读特](https://news.qq.com/rain/a/20250221A098Y800).

### LEAD-ORDERED — After R2 + 下单

**VI**

> Đã đặt **{code} {tb_color} {asia}** trên Taobao.  
> Đang chờ **gửi kho TQ**. Có **mã carrier** mình gửi trong thread này.  
> Cửa sổ vẫn **{band}**. Chặng TQ có thể **không** hiện trên 17TRACK.

**EN**

> Placed **{code} {tb_color} {asia}** on Taobao.  
> Waiting on **China ship-out**. We will send a **carrier** number in this thread.  
> Window still **{band}**. The China leg may **not** show on 17TRACK.

Cite: [17TRACK Taobao](https://www.17track.net/en/brands/taobao) — carrier ≠ marketplace order id; [Cainiao help](https://help.17track.net/hc/en-us/articles/115002402551-Why-can-t-Cainiao-AliExpress-shipping-method-be-tracked).

### LEAD-TRACK-NONE — No carrier yet

**VI**

> Chưa có mã carrier. Shop theo dõi trên **đơn Taobao / kho chuyến**.  
> Cửa sổ vẫn **{band}**. Không spam 6 lần scan tiếng Trung.

**EN**

> No carrier number yet. We are watching the **Taobao order / transfer warehouse**.  
> Window still **{band}**. We will not spam six Chinese scan events.

### LEAD-TRACK-HAS — Carrier exists

**VI**

> Mã theo dõi: **{carrier}**.  
> Dán vào trang **hãng** hoặc [17TRACK](https://www.17track.net/).  
> Đây là chặng US / international. **Không** phải mã đơn Taobao.

**EN**

> Tracking: **{carrier}**.  
> Paste on the **carrier** site or [17TRACK](https://www.17track.net/).  
> This is the US / international leg. It is **not** the Taobao order id.

**Orders:** `Shipped` only when this is true enough for Boss — not when the seller clicked 发货 in China.

### LEAD-FTC — Delay-or-refund (same day you know)

**When:** You will miss `{old_band}` / the 30-day default / the stated 预售 band.  
**Never:** Invent `{new_date_with_basis}`. Never wait for them to chase.  
**Orders:** stay Paid until they pick; then Shipped or Cancelled + refund.

**VI**

> Không gửi đúng cửa sổ đã nói (**{old_band}**).  
> Em chọn:  
> 1) đợi tới **{new_date_with_basis}** (shop có cơ sở cho ngày này), **hoặc**  
> 2) **huỷ + hoàn**  
> Shop **không** tự giữ tiền im. ([FTC 30-day Rule](https://www.ftc.gov/business-guidance/resources/business-guide-ftcs-mail-internet-or-telephone-order-merchandise-rule))

**EN**

> We will miss the window we stated (**{old_band}**).  
> You choose:  
> 1) wait until **{new_date_with_basis}** (we have a basis for that date), **or**  
> 2) **cancel + refund**  
> We will **not** sit on the money. ([FTC 30-day Rule](https://www.ftc.gov/business-guidance/resources/business-guide-ftcs-mail-internet-or-telephone-order-merchandise-rule))

If you will **never** ship: cancel + refund **without being asked** (same guide). If you cannot name a revised date with a basis: option 2 only.

### LEAD-HOLIDAY — Factory rest / 618 / 双11 / CNY

**VI**

> Ngày lễ xưởng **không** nằm trong số **{n} ngày** trên PDP.  
> Cửa sổ **{band}** đã cộng lịch đó / hoặc TBD — em đọc lại giúp. Không cộng “cảm giác.”

**EN**

> Factory holidays are **not** inside the PDP **{n} days**.  
> **{band}** already includes that calendar — or it is TBD. We do not add vibes.

### LEAD-OWNED — Exception: truly on-hand Square unit

**When:** Stock confirms Square Track-ON qty ≥ 1 for **this** color/size **and** Slack said this is the owned path.  
**Never:** Default dropship tiles (A01 live copy is **not** this).

**VI**

> Món **{code}** size/màu này **đang trên Square** (Boss đã Save).  
> Hẹn pickup / ship **trong nước** — không đợi kho TQ.  
> Vẫn không invent ngày nếu chưa pack.

**EN**

> **{code}** in this size/color **is on Square** (Boss already Saved).  
> Local pickup / domestic ship — no China warehouse wait.  
> Still no invented porch date until it is packed.

Cite: Square Free = on-hand SoT ([`README.md`](../../README.md)); TOMORROW “Paid? Owner Zelle + Square Save” is the **owned** path — dropship inserts TB between Paid and any Square thought ([LEARN 08](https://github.com/SkyLanter/Sassy-closet/pull/26) §2).

---

## 7. Never-say lexicon

| Do not draft | Why | Say instead |
| --- | --- | --- |
| “On hand” / “một chiếc đang có” / “còn 1 trong kho” | Live PDP lie for dropship | INQ-01 |
| “Ships tomorrow” / “2-day” / “48h tới tay” | No basis; 48h is CN 发货 | LEAD-SPOT |
| `$6.95` / `free ship` / Kelly `$10 / $300+` | Flat ship $ unlocked | ADDR-07 / INQ-07 |
| “Duty-free” / “không thuế” | [CSMS #64917563](https://content.govdelivery.com/accounts/USDHSCBP/bulletins/3de903b) | `{included\|TBD}` |
| `$23` on P05 / decorative `$0` | Hold · Inbox for price | INQ-02 |
| `A03` / `AO001` as live stock / “em lấy mã” | Invent | INQ-04 |
| US size “M = 8” | DESIGN_NOTES | INQ-05 |
| “Đã lên Square” on a lookbook tile | Wishlist / staged / dropship | INQ-09 / LEAD-OWNED only if true |
| “Zelle có buyer protection” | Zelle FAQ opposite | ZELLE-01 |
| “Paid” from a screenshot | Cash-like | ZELLE-03 |
| “Upgrade Zelle” link | Hostile | ZELLE-04 |
| Home address on the lookbook / at Inquiry | Meetup + PII | ADDR-01 / ADDR-06 |
| Taobao URL / ¥ vốn in the bubble | Staff only | — |
| “Similar item I Googled” | Invent `source_link` | INQ-08 |
| Venmo handle | Not in CS pack | Wordless until Boss writes it |
| “Chat hết hạn 24h” | Meta API ≠ shop reserve | HOLD-24-07 |
| Agent Send / ManyChat checkout | Shop law; 01 §2.5 | Draft only |

---

## 8. Page greeting + icebreakers (Owner in Meta, not agent Send)

Owner configures these in Meta Business Suite → Inbox → Automations ([Create a Messenger greeting](https://www.facebook.com/help/1698046970464236); [Messenger Profile — greeting / ice_breakers](https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/)). Cloud Agents do **not** POST the Profile API.

### GREET-01 — Instant reply / greeting (no ship `$`)

**VI**

> Chào em 💕 Sassy Closet — món độc bản.  
> Gửi **mã trên web** (ví dụ A01) + size Á châu + cm ngực/eo.  
> Zelle / cash meetup. Ship: **hỏi trong inbox** — web chưa in phí ship.

**EN**

> Hi — Sassy Closet, unique looks.  
> Send the **code on the site** (example A01) + Asia size + bust/waist cm.  
> Zelle / cash meetup. Ship: **ask in inbox** — no printed ship fee on the site.

`A01` here is an **example of a live allowlist code**, same as 01 §2.3. If A01 ever leaves the lookbook, Owner edits the greeting to another **live** code.

### ICE-01 — Tappable prompts (Ads Manager / ice breakers)

Only enable rows that are true **today**:

| Prompt | Live only if |
| --- | --- |
| `Còn A01 không?` | A01 Available |
| `Còn K01 không?` | K01 Available |
| `Hold / inbox giá (P02)` | P02 still Hold |
| `Size + cm` | Always (Asia) |
| `Meetup hay ship?` | Always — **no** `$` |

Do not add `Shop now`. Message destinations use **Send message** ([CTA by objective](https://www.facebook.com/business/help/410873986524407)). Meta Shops checkout moved to **website** checkout ([Shops change](https://www.facebook.com/business/help/1314349509894768)) — Sassy’s website is a **lookbook**, not a cart.

---

## 9. APPLY — sell-test strings + where they go

Origin shop git is **not** this repo. This section is the **clipboard for the Origin agent**. Keep motion (`announce-fade`, `cta-flash`, `shimmer-slide`), fonts, hero, no cart, footer word **Zelle**, Hold treatment on P02/P05. **Replace warehouse idioms only.**

Inspected 2026-09-09:

| Slot on site | Live text | Class / place |
| --- | --- | --- |
| Announcement | `Facebook livestream` | Top `h-8` ink bar, `p.announce-fade`, uppercase 10px tracking |
| Header CTA | `Messenger` | Links Page `61594312648057` |
| Card CTA | `Message to buy` | Under price / Inbox for price |
| Hold price | `Inbox for price` | P02, P05 |
| PDP Available rail | `1 piece · Message to buy. No cart.` | `/m/A01` `/m/K01` … |
| PDP Available body | `One unique top on hand.` / `một chiếc đang có.` | **Replace** |
| PDP Hold rail | `Hold · Inbox for price. Message to buy — photo-check, no USD yet.` | `/m/P02` — **keep shape** |
| Footer | `Zelle · Message on Messenger` | Keep word Zelle; no handle |
| Meta description | `unique pieces. Facebook livestream. Zelle · Message on Messenger.` | Keep |

There is **no** `/how-to-buy` route today. Do **not** add a new page (redesign). Put how-to-buy on **announcement + PDP one-liner + optional footer crumb**.

### 9.1 Announcement (`AnnouncementBar` / `announce-fade`)

Keep the bar. Swap the string. Stay uppercase-ish, short, **no `$`**, no 11th mã.

**Preferred (bilingual crumb, one line):**

> Inbox mã · Zelle · ship US quote in chat

If the bar must stay a *livestream* pointer (Kelly rail), use a **rotating** second slide — same class, do not add a second bar:

1. `Facebook livestream` (keep)
2. `Message to buy · no cart · no printed ship $`

**Do not** put `{zelle}` name here. **Do not** put `A03`.

### 9.2 How-to-buy (no new IA)

**PDP Available one-liner** (replaces “on hand” / “một chiếc đang có”) — same hierarchy, both languages:

**EN**

> Message to buy. We confirm color, Asia size, and Taobao spot vs pre-sale, then order and ship US.

**VI**

> Inbox để mua. Shop xác nhận màu, size Á châu, và 现货/预售, rồi order Taobao, ship US.

**Optional footer crumb** (append after existing Zelle · Messenger, still 11px uppercase):

> Ship quote in chat · cash meetup

**Optional microcopy under Available badge** (small, no new section):

> 现货 / 预售 chốt khi inbox

**Do not** add a shipping calculator, Shop now, or a cart.

Worked PDP replacements (keep printed USD from the Boss table):

| Route | Keep | Replace body with |
| --- | --- | --- |
| `/m/A01` | A01 · TOP · Available · **$25** · Message to buy | How-to-buy EN/VI above. Drop “on hand.” |
| `/m/A02` | **$22** | Same |
| `/m/S01` | **$28** | Same; “set” in the type line stays |
| `/m/P01` `/m/P03` `/m/P04` | $5 / $18 / $13 | Same |
| `/m/K01` | **$37** | Same. Drop “One jacket on hand.” |
| `/m/H01` | **$8** | Same |

### 9.3 Hold CTAs (P02 / P05)

**Keep:** badge `Hold`, price slot `Inbox for price`, button `Message to buy`, photo-check sentence.

**Keep rail:**

> Hold · Inbox for price. Message to buy — photo-check, no USD yet.

**Tighten body (optional, same voice):**

**EN**

> Thermos on Hold (photo-check). No USD yet — inbox for price. Not reserved for another buyer.

**VI**

> Bình giữ nhiệt đang Hold — kiểm tra ảnh, chưa có USD. Không phải đã giữ cho bạn khác.

**Card under-price line** stays `Inbox for price` + `Message to buy`.  
**Do not** publish `23`. **Do not** reuse Hold to mean Reserved until Official + Square + Slack agree ([LEARN 01](https://github.com/SkyLanter/Sassy-closet/pull/22) §3.4).

**Icebreaker / Message {code} prefill** for Hold tiles:

> Hi Sassy — P02 inbox giá + ảnh thật.

(Only `P02` / `P05` while those two are the Hold set.)

### 9.4 Sticky / header CTA

Keep `Messenger` / `Message on Messenger` → Page `https://www.facebook.com/profile.php?id=61594312648057`.  
Prefill may include the **printed** mã (`Message A01`) — [m.me `text=`](https://developers.facebook.com/docs/messenger-platform/discovery/m-me-links/) is Owner-side. Do not prefill a ship `$`.

### 9.5 Verify (Origin, after type lands)

1. Home announcement still `announce-fade`; no handle; no `$10`.
2. `/m/A01` `/m/K01` have **no** “on hand” / “đang có”; **$25** / **$37** unchanged.
3. `/m/P02` `/m/P05` still Hold + Inbox for price; no `23`.
4. Footer still says **Zelle** the word; Message to buy; **no cart**.
5. Allowlist still ten codes. No A03.

---

## 10. Source list

### 10.1 This shop

| Source | Proves |
| --- | --- |
| Live sell-test 2026-09-09 `/` `/m/A01` `/m/P02` `/m/K01` | Ten tiles; announcement `Facebook livestream`; warehouse PDP; Hold P02/P05; footer Zelle |
| Slack `#shop-decisions` 2026-09-04 | Facebook = store; Hold >24h yes/no; Zelle name locked; flat ship $ unlocked; Track ON; no Save until yes |
| [`README.md`](../../README.md) | Bots draft; Owner sends / Zelle / Square Save |
| [`sassy-closet/lib/captions.ts`](../../sassy-closet/lib/captions.ts) | Inbox + cash/Zelle + Ship toàn US; no `$` |
| [`sassy-closet/lib/ask-fallback.ts`](../../sassy-closet/lib/ask-fallback.ts) | Copy inbox; không gửi hộ; không invent mã |
| [`sassy-closet/lib/kinds.ts`](../../sassy-closet/lib/kinds.ts) | Asia `2XS–2XL` |
| [`excel-kit/schema.py`](../../excel-kit/schema.py) | Orders / pay / fulfill enums |
| [`excel-kit/DESIGN_NOTES.md`](../../excel-kit/DESIGN_NOTES.md) | No US sizes; no bot Zelle; no mint mã |
| [`excel-kit/inbox/gf_intake_reply_templates.md`](../../excel-kit/inbox/gf_intake_reply_templates.md) | Never claim Square; Messenger ≠ intake |
| Sibling PRs [19](https://github.com/SkyLanter/Sassy-closet/pull/19) [21](https://github.com/SkyLanter/Sassy-closet/pull/21) [22](https://github.com/SkyLanter/Sassy-closet/pull/22) [26](https://github.com/SkyLanter/Sassy-closet/pull/26) | PDP / dropship law / Messenger law / ops desk |

### 10.2 Meta / Messenger

| URL | Proves |
| --- | --- |
| [Send a Message — 24h window](https://developers.facebook.com/docs/messenger-platform/send-messages/) | Standard messaging window; API ≠ Owner Inbox |
| [Messaging best practices](https://www.facebook.com/business/help/269324800441478) | Greet, look available, answer |
| [Page greeting](https://www.facebook.com/help/1698046970464236) | Instant reply; Owner-configured |
| [Messenger Profile API](https://developers.facebook.com/docs/messenger-platform/reference/messenger-profile-api/) | greeting / ice_breakers properties |
| [m.me links](https://developers.facebook.com/docs/messenger-platform/discovery/m-me-links/) | Prefill `text=` |
| [Click to Messenger ads](https://www.facebook.com/business/help/212519562595207) | Message destinations |
| [Shops / checkout change](https://www.facebook.com/business/help/1314349509894768) | In-app checkout gone |
| [Marketplace in-person](https://www.facebook.com/help/2329750133711372) | Home address private |
| Page [`61594312648057`](https://www.facebook.com/profile.php?id=61594312648057) | The store |

### 10.3 Pay / delay / duty / address / Taobao

| URL | Proves |
| --- | --- |
| [Zelle FAQ — unknown payee / no reverse](https://www.zelle.com/faq/im-unsure-about-using-zelle-pay-someone-i-dont-know-what-should-i-do) | No protection; cannot reverse; QR name check |
| [FTC payment apps](https://consumer.ftc.gov/consumer-alerts/2023/08/do-you-use-payment-apps-venmo-cashapp-or-zelle-read) | Like cash |
| [FTC 30-day Rule — business guide](https://www.ftc.gov/business-guidance/resources/business-guide-ftcs-mail-internet-or-telephone-order-merchandise-rule) | Reasonable basis; delay-or-refund; prompt refund |
| [16 CFR 435](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-435) | Internet/phone orders; completed order = pay + ship info |
| [CBP CSMS #64917563](https://content.govdelivery.com/accounts/USDHSCBP/bulletins/3de903b) | 2025-05-02 no de minimis CN/HK |
| [NN/G taxes & fees](https://www.nngroup.com/articles/ecommerce-taxes-fees/) | Admit extras |
| [USPS Delivery Address](https://pe.usps.com/businessmail101?ViewName=DeliveryAddress) | Attn / street+APT / city state ZIP |
| [USPS Pub 28 ch. 2](https://pe.usps.com/text/pub28/28c2_001.htm) | Complete standardized last line |
| [USPS ZIP Lookup](https://tools.usps.com/zip-code-lookup.htm) | Verify, do not invent |
| [淘宝预售协议](https://terms.alicdn.com/legal-agreement/terms/suit_bu1_taobao/suit_bu1_taobao202012010036_72763.html) | 发货 = PDP |
| [淘宝发货管理](https://jianghu.taobao.com/detail/47301_58664622) | 48h or set window |
| [OpenAPI 发货合约](https://open.alitrip.com/docs/doc.htm?articleId=121094&docType=1) | 24h/48h vs 预售 days |
| [读特 现货→预售](https://news.qq.com/rain/a/20250221A098Y800) | Title ≠ order |
| [17TRACK Taobao](https://www.17track.net/en/brands/taobao) | Carrier ≠ order id |
| [Kelly Ying](https://www.kellyyingboutique.net/) | Look reference; **do not copy $10 / $300+** |

---

## 11. Tear-off

> **Draft. Owner Sends.** Mini Boss không gửi hộ.  
> Inquiry → R1 → quote or shop-Hold → 24h reserve (Slack if longer) → Zelle **in the bank** → address **if ship** → R2 → 下单 → carrier.  
> Three 24hs: Meta API · shop reserve · CN 发货. Do not mix.  
> VN first in-thread. Site stays Kelly (announcement / how-to / Hold CTAs — §9).  
> Allowlist ten. No A03. No P05 `$23`. No ship `$` until Slack writes one. No duty-free.  
> If you had to invent a mã, a dollar, a stock count, a street, or a porch date — stop; you are lying.

*Learn track. Agents draft. Owner posts, sends, takes Zelle, Saves Square.*
