# 08 — Dropship ops runbook (day-to-day)

**Learn track:** Ultra burn.  
**Shop:** Sassy Closet — VN / Bay Area Facebook boutique; **Taobao is the buying engine**; Facebook inbox is the store.  
**Audience:** Customer Service (Inbox Desk), Scout (Buy Research), Mini Boss, Stock, Boss, a later Origin agent who might ship staff pages.  
**Date researched:** 2026-09-09.  
**This file does not assign stock, mint a mã, take Zelle, Send on Facebook, or Save in Square.**

Sister **07** is the *law* (dropship-honest catalog + sell-site APPLY). Sister **02** is the *PDP* (color / size / Hold words). Sister **01** is the *storefront* (Messenger, Zelle ritual, no cart). **This file is the hands:** inquiry → Hold → Zelle → order on Taobao → tracking → exceptions.

---

## 0. How to read this document

This is a **runbook**, not a rebuild brief and not a warehouse SOP.

- **Cite, don’t invent.** Shop-law claims point at this repo, Slack `#shop-decisions`, or a sibling learn-track file. Industry claims point at Taobao consumer terms / OpenAPI, FTC 16 CFR 435, Zelle’s own FAQ, CBP CSMS, Meta messaging docs, or a named aggregator’s own help page. If a fact is missing, the gap is named.
- **Never invent a mã.** Hub / sell allowlist today is exactly ten codes (`A01 S01 P01 P02 P03 P04 P05 K01 H01 A02`). Official / Square shape is `AO|QU|VA|AK|GI|PK|SET` + 3 digits — Stock reads Dashboard `B21:B27`. Slack’s `AO001` / `AO003` lines are **decision-template examples** from 2026-09-04, not proof those pieces exist. Kit CLI `--help` examples that type `AO001` are **usage shape**, not live stock.
- **Never invent $ , qty, tracking numbers, skuId, 颜色 strings, or a Zelle handle.** Empty = leave empty, or say Inbox / TBD.
- **Bots draft only.** Owner posts, **sends**, takes Zelle, taps Square Save ([`README.md`](../../README.md); `excel-kit/schema.py` `BOTS_DRAFT_ONLY`).
- **07 wins on dropship truth.** If this runbook and a later chrome / SEO / media note disagree about “on hand,” 现货, or `source_link`, **07 + this file win**. Chrome stays pretty.

### 0.1 Hard stops (print these first)

1. Never invent mã / qty / $ / storage / photos / skuId / `e.tb.cn`.
2. Never Square Save from a bot / site / agent. Track ON is a *standing rule*, not a Save ([`excel-kit/square/README.md`](../../excel-kit/square/README.md); Slack 2026-09-04).
3. Never Facebook **Send** or **Post** from a bot. Inbox Desk **drafts**. Owner taps Send.
4. Never move Zelle from a script. Confirm in the **bank / Zelle activity**, not a JPEG ([LEARN 01](https://github.com/SkyLanter/Sassy-closet/pull/22) §5).
5. Never quote US sizes to buyers. Asia size + cm only ([`excel-kit/DESIGN_NOTES.md`](../../excel-kit/DESIGN_NOTES.md)).
6. Never put `source_link`, vốn / cost, customer names, or Zelle *identity* on the customer shop ([PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) `SELL_CATALOG_CONTRACT.md`).
7. Never treat Wishlist / staged / `catalog.v1` `qty: 1` as Square on-hand ([`sassy-closet/BOSS.md`](../../sassy-closet/BOSS.md)).
8. Never promise “ships tomorrow,” “duty-free $800,” or “Taobao 48h = her porch.”
9. Never reuse a Sold Official mã.
10. Never collapse shop Hold, customer reserve, and Taobao 预售 into one word.

### 0.2 Sister docs

| File | Owns | This file still owns |
| --- | --- | --- |
| [01 Messenger](https://github.com/SkyLanter/Sassy-closet/pull/22) | Page / m.me / 24h window / no-cart CTA | When the thread becomes an Orders row |
| [02 PDP color/size](https://github.com/SkyLanter/Sassy-closet/pull/19) | Text colors, cm sheet, gallery sync | skuId match before Paid |
| [03 Tiny admin](https://github.com/SkyLanter/Sassy-closet/pull/20) | Add / edit / rename / silent Save | Status after a real TB exception |
| [04 Blob catalog](https://github.com/SkyLanter/Sassy-closet/pull/24) | ISR / Blob / import | Do not publish `source_link` |
| [05 AI media](https://github.com/SkyLanter/Sassy-closet/pull/23) | Per-color attach | Photo ≠ SKU proof |
| [07 Dropship law](https://github.com/SkyLanter/Sassy-closet/pull/21) | Quote stack, honesty ladder, APPLY copy | **Daily hops + drafts + TB checks** |

`01`–`07` paths are sibling PRs as of 2026-09-09 (not all on `main`). Cite the PR until merge. Do not copy their APPLY chrome work into this kit.

### 0.3 What “Inbox Desk” and “Buy Research” are (and are not)

**Live Origin sell-test (2026-09-09)** has `/`, `/c/*`, `/m/{MA}`, hidden `/admin`. It does **not** have staff ops pages:

| Tried | Result |
| --- | --- |
| `https://sassy-closet-shop.vercel.app/inbox` | HTTP 404 |
| `/inbox-desk` `/desk` `/ops` `/staff` `/buy` `/research` `/buy-research` | HTTP 404 |

So these names are **desks**, not URLs.

| Desk | Who | Job | Live home today |
| --- | --- | --- | --- |
| **Inbox Desk** | Customer Service + Owner | Draft every customer line. **Never Send.** | Facebook / Messenger Inbox + SoT **Orders** + this §9 pack. Intake Ask already returns a **Copy inbox** card and says Mini Boss does not Send ([`sassy-closet/lib/ask-fallback.ts`](../../sassy-closet/lib/ask-fallback.ts)). |
| **Buy Research** | Scout + Boss | Re-open the Taobao page **today** and pass / Hold / Skip **before** quote, **again** before 下单. | Slack soft-launch: **Scout → Buy/Skip checklist** (2026-09-04 14:23 PT) + hub `source_link` + this §10 page. |

If Origin later ships `/inbox-desk` or `/buy-research`, those pages must implement **this** contract. They must not invent a Send button, a Square Save, or a Next-mã tile.

### 0.4 Research method (and what this pass could not see)

| Source | Result |
| --- | --- |
| Repo `excel-kit/`, `sassy-closet/`, `README.md` | Read. Primary shop law. |
| Slack `#shop-decisions` (`C0BV3GYC602`) | Six standing messages, 2026-09-04. Cited below. |
| Live sell-test + intake + `/admin` | Fetched 2026-09-09. |
| Sibling PRs #19 / #21 / #22 / #18 | Read. |
| Linear | No dropship ops issue (workspace only had onboarding). |
| Granola meetings | MCP unauthorized — no meeting notes this pass. |
| Notion | Keyword search empty for Inbox Desk / Buy Research / dropship. |
| Public FTC / Zelle / CBP / Taobao / 17TRACK / Cainiao | Fetched 2026-09-09. URLs in §16. |

If a later Granola call changes the 24h Hold or the USD table, **`#shop-decisions` yes wins** until the table is rewritten.

---

## 1. Who moves which piece

Slack *Team order: soft-launch prep* (2026-09-04 14:23 PT) already named the lane, even without the words “Inbox Desk” / “Buy Research”:

| Lane (Slack) | Desk in this file | Allowed | Forbidden |
| --- | --- | --- | --- |
| Customer Service → reply pack (Zelle name **locked**) | **Inbox Desk** | Draft VI/EN; lock the *name* in the CS pack, not in git | Send; publish the handle on the lookbook |
| Scout → Buy/Skip checklist | **Buy Research** | Reopen `source_link`; 现货/预售; 颜色 × 尺码 qty | Invent a similar `id=`; Skip-without-`--no-source` on Wishlist |
| Stock → first-mã Save proposal | Stock | ASK STOCK; Track-ON draft CSV **off git** | Save before Slack yes; mint `A03` / `AO016` |
| Quill → caption skeleton | Quill | Caption starter (mã line 1) | Post |
| Ledger | Ledger | Optional margin note | Invent landed $ on the PDP |
| Mini Boss / Cloud Agents | Kit | Draft Orders / Bot_Activity; change kit **code** | Send / Zelle / Square Save / live PII in git |

Facebook stays the store. `#shop-decisions` stays Boss **yes / no** only — Save, mã, price, hold extend. Not customer chat ([channel purpose](https://tien-ota6716.slack.com/archives/C0BV3GYC602/p1788541753903809)).

GF clothes intake is a **different inbox**: OneDrive `From GF/`. **Never Messenger. Never Dial Bot** ([`excel-kit/PROMPTS.md`](../../excel-kit/PROMPTS.md) task 11). Do not file a customer “còn A01 không?” packet in From GF.

---

## 2. The spine: inquiry → Hold → Zelle → TB → tracking

The shop is **inverted** ([07](https://github.com/SkyLanter/Sassy-closet/pull/21) §1): conversation first, Taobao SKU second, owned Square unit last.

```text
Facebook hello / lookbook Message {mã}
        │
        ▼
[Inbox Desk] draft first reply     →  Owner Sends
        │
        ▼
Orders: Inquiry
        │
        ▼
[Buy Research] reopen source_link   →  Pass / Hold / Skip
        │
        ├─ shop Hold (no honest $ / photo-check / 预售 unknown)
        ├─ customer reserve (named, ≤24h unless Slack yes)
        └─ quote (USD + band + duty/line TBD-or-included)
        │
        ▼
Customer yes
        │
        ▼
[Inbox Desk] Zelle draft (locked name from CS pack)
        │
        ▼
Owner: money in bank app (not JPEG)  →  Orders: Paid
        │
        ▼
[Buy Research] SECOND check (same skuId, today)
        │
        ▼
Boss 下单 on Taobao (颜色 + 尺码 + skuId)
        │
        ▼
CN 发货 → 转运 / agent → US last mile  (or Bay Area pickup)
        │
        ▼
Orders: Shipped  or  Picked up
        │
        ▼
Square Save?  ONLY leftover / keep piece + Slack yes
```

SoT already prints the non-dropship version on the **TOMORROW** sheet: “New Facebook hello → Orders Inquiry” then “Paid? Owner Zelle + Square Save” ([`excel-kit/sot/build_sot_desktop.py`](../../excel-kit/sot/build_sot_desktop.py)). Dropship **inserts Buy Research + 下单 between Paid and any Square thought**. Most Paid rows will **never** become Square.

### 2.1 Status machines (do not collapse)

| Word | Whose mouth | Meaning |
| --- | --- | --- |
| **Available** (lookbook) | Customer site | “You may message this look.” **Not** Square qty. Live 2026-09-09: A01 $25, S01 $28, P01 $5, P03 $18, P04 $13, K01 $37, H01 $8, A02 $22. |
| **Hold · Inbox for price** | Customer site | No published USD. Live: **P02, P05** only. Photo-check voice. **Not** “someone reserved it.” |
| **Inquiry** | SoT Orders | Facebook hello logged. Exact enum. |
| **Reserved** | SoT Orders | Named customer reserve (clock). Still not Square. |
| **Paid** | SoT Orders | Bank-confirmed Zelle / cash. **Permission to 下单**, not proof the SKU shipped. |
| **Shipped** / **Picked up** | SoT Orders | US last-mile handed off, or meetup done. |
| **Cancelled** | SoT Orders | Thread died, SKU gone, customer refused delay, or refund path. |
| **held / Reserved / Hold** | Official / Ma_List | Working-copy flags. Official `Hold` and Official `Reserved` both map to Ma_List `held` ([`excel-kit/schema.py`](../../excel-kit/schema.py) `OFFICIAL_TO_MA_LIST_STATUS`). |
| **现货** | Taobao seller | *Their* 24–48h (typical) **CN domestic 发货**, not a US porch. |
| **预售** | Taobao seller | PDP 发货 clock in days. Full-pay or 定金+尾款. |
| **Hold {ma} past 24h?** | Slack | Boss yes/no to *extend a customer reserve*. |

Orders accept **only** `Inquiry | Reserved | Paid | Shipped | Picked up | Cancelled` ([`excel-kit/sot/append_order_row.py`](../../excel-kit/sot/append_order_row.py)). Scripts reject other strings. Do not invent `Dropship` / `TB ordered` / `In transit` as an order_status. Put those facts in `thread_note`.

Pay list: `Zelle | Cash | Venmo | Other | Unpaid`. Fulfill: `Ship | Local pickup | Hold | TBD`. Venmo is on the list; **do not publish a Venmo CTA** until Boss writes a handle in the CS pack (01 §4.4).

### 2.2 What must be locked before each hop

| Hop | Must already be true | May still be TBD |
| --- | --- | --- |
| Inquiry row | Channel (default Facebook). Display code **if** they named a published one. | Size, color, $ , ship, buyer name (omit rather than invent) |
| Shop Hold tile | No honest USD, or photo-check, or SKU/clock broken | Customer name |
| Customer Reserved | Published mã **or** Stock-assigned Official mã; color + Asia size + cm; clock ≤24h PT | Ship fee |
| Quote | Buy Research **Pass** (or Pass-with-预售 said out loud); agreed USD **or** explicit Hold | Duty/line if you said TBD |
| Paid | Quote accepted; **bank** Zelle or cash in hand | Tracking |
| 下单 | Second Buy Research Pass; skuId + 颜色 + 尺码; `source_link` still opens | US tracking |
| Shipped | A **carrier** number (or honest “economic line, no scan yet”) | Square |
| Square Save | Owned, counted, Slack **yes**, Track ON | — |

Thread snapshot fields 07 already requires (staff `thread_note`, never customer JSON): mã, TB 颜色 string + VN word you told them, 尺码 + cm, clean `source_link`, skuId if present, 现货/预售 + clock + **date checked**, agreed USD or Hold, ship path, pay method.

---

## 3. Inquiry (Facebook hello)

Facebook inbox is the store ([`README.md`](../../README.md)). The lookbook’s job is to start the thread. Live CTAs are **Message to buy** / **Message {mã}** — no cart ([https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app), `/m/A01` 2026-09-09).

### 3.1 First ten minutes (Inbox Desk)

1. Read the first bubble. Prefer a **published** display code (`A01`…) over “cái áo kem.”
2. If they send a photo only: do **not** assign a mã from photo-detect. Intake Tìm mã photo-detect means “this file was saved under mã X,” not “this is the Taobao 颜色” ([`excel-kit/prompts/FIND_MA_CARD_2026-09-08.md`](../../excel-kit/prompts/FIND_MA_CARD_2026-09-08.md)). Draft: ask them to send the **web code**.
3. Draft the first reply (§9.1). **Do not Send.**
4. Append Orders **Inquiry** on the OneDrive SoT book. `--ma` only if the code already exists in that book’s Official / assigned set. For a lookbook-only hello on `A01`, you may log the display code in `snapshot` / `thread_note` and leave Official `--ma` empty rather than invent `AO001`.
5. Log Bot_Activity `action=draft` if the sheet exists. Status must stay `draft` — the CLI **exits 2** on `saved|posted|sent|zelle` ([`excel-kit/sot/append_bot_activity.py`](../../excel-kit/sot/append_bot_activity.py)).

Intake Ask already drafts a cute line and stamps **Mini Boss không gửi hộ** ([`ask-fallback.ts`](../../sassy-closet/lib/ask-fallback.ts)). That is the Inbox Desk spirit on the *intake* host. Customer chat still happens on the **Page**, not on `sassy-closet.vercel.app`.

### 3.2 What to ask in the first back-and-forth

Need these before Buy Research can Pass a *sell* quote:

1. **Mã** they mean (published lookbook code, or Stock-assigned Official).
2. **Color word they want** (Kem / Xanh / …) — text, not “cái trong ảnh.”
3. **Asia size + cm** (ngực / eo / dài as relevant). Chips on intake: `2XS XS S M L XL 2XL` ([`sassy-closet/lib/kinds.ts`](../../sassy-closet/lib/kinds.ts)). Never convert to US.
4. **City / ship vs Bay Area pickup.**
5. Whether they are asking **this** look or a hunt (Wishlist / no `source_link`).

Do **not** ask them to paste `e.tb.cn` in Messenger. Staff reopen the hub link. Customers shop a look, not a factory (PR #18: omit `source_link` from `catalog.v1`).

### 3.3 What not to promise at Inquiry

Live PDP A01 still says “One unique top **on hand**” / “một chiếc đang có” (2026-09-09). That sentence is a **warehouse idiom 07 already flagged**. Inbox Desk must **not** repeat it as Square truth. Honest first line: listed look, we confirm color/size and 现货/预售, then order Taobao, then ship US.

Forbidden at Inquiry:

- “Còn 1 trên Square.”
- “Ships tomorrow” / “2-day” without a reasonable basis ([FTC 30-day Rule](https://www.ftc.gov/business-guidance/resources/business-guide-ftcs-mail-internet-or-telephone-order-merchandise-rule)).
- A ship **dollar** (`#shop-decisions` still lists **flat ship $** as unlocked, 2026-09-04 14:23 PT).
- US size.
- “Same as the cover” when colors exist (A01 is Kem / Xanh on the hub; cover ≠ every SKU — 07 §8).
- Inventing `A03` because `/admin` showed **Next mã A03**.

### 3.4 Inquiry CLI (shape only)

```text
python3 excel-kit/sot/append_order_row.py -w "$SASSY_SOT" \
  --status Inquiry --channel Facebook \
  --snapshot "A01 / color TBD / size TBD" \
  --thread-note "FB hello; Buy Research not run"
```

`--ma` only for a **real assigned** Official mã. Kit `--help` types `AO001` as a dummy; **do not mint it**. `--buyer` omit rather than invent. No PII in git ([`excel-kit/PROMPTS.md`](../../excel-kit/PROMPTS.md) task 3).

---

## 4. Hold

Three different holds. Mixing them is the most expensive CS lie (01 §3, 07 §4.1, 02 §10).

| Hold | Trigger | Customer sees | Staff does |
| --- | --- | --- | --- |
| **Shop Hold** | No honest USD, photo-check, price jump, 预售 unknown, SKU broken | Badge **Hold · Inbox for price**, `priceUsd: null` | Do not type P05’s hub `23` into `/admin` |
| **Customer reserve** | They asked to hold a **quoted** look | Messenger clock (default **24h PT**) | Orders `Reserved`; Slack if past 24h |
| **Taobao 预售** | Seller will make / replenish after pay | Honest ETA **band**, not “on the rack” | Buy Research records PDP days; do not rename it “Hold” unless USD is also unknown |

P02 / P05 are **merchandising** Holds today (“photo-check, no USD yet”). A buyer must not read that as “reserved for someone else.” Keep that sentence (01 §3.6).

### 4.1 When to flip the *tile* to Hold

Flip Available → Hold and **null the USD** when any of these is true and Boss has not re-quoted (07 §4.5):

- Seller 无货 / 下架 / that 颜色 removed.
- 预售 clock longer than the last caption implied.
- Hub `sell_usd` empty or disagrees with the Boss table.
- Photo-check failed (P02 / P05 pattern).
- Two customers want the same **unique owned** unit (Square Track ON + site Hold the moment Reserved/Paid).

Do **not** flip to Hold just because Square qty is 0. On this model, Square 0 is the default.

Do **not** flip to Hold just because one person is chatting. That is a **customer reserve** in Messenger + Orders, not a lookbook badge — unless you are refusing a second conversation on a unique owned piece.

### 4.2 24-hour clock

`#shop-decisions` example format (not live stock): `Hold AO003 past 24h?`  
Apparel ops writing treats undifferentiated holds as rot; 24h is the common escalate line (01 cites [TopSource](https://topsource.global/blog/order-holds-playbook/) and [Uphance](https://www.uphance.com/blog/order-holds-when-to-use-which-type/)).

Sassy rule: **past 24h = Slack yes/no.** Inbox Desk does not extend. Mini Boss does not extend.

Clock language is **Pacific**. Bot_Activity times are Pacific ([`append_bot_activity.py`](../../excel-kit/sot/append_bot_activity.py)).

### 4.3 Hold vs oversell

`catalog.v1` hard-codes `qty: 1` for the allowlist (PR #18). On a **dropship look**, that means “one conversation at a time,” not “one body in California.”

If two people message **A01 Kem / M**:

1. First **Paid** + TB order placed → second customer gets a **new** Buy Research, not the old “Available.”
2. If that skuId is now 0 → Inbox Desk uses §9.6 (SKU gone). Consider flipping the tile if *all* sellable SKUs are gone.
3. Never decrement a fake warehouse. Never build a shadow cart.

Unique **owned** unit (Square 1): Hold the tile the moment Reserved/Paid.

---

## 5. Zelle (and cash meetup)

No-card on purpose (01 §4). SoT pay list includes Zelle / Cash / Venmo. Footer on the lookbook may say the **word** Zelle. **No personal name, handle, or phone on the site** (07 hard stop; PR #18).

### 5.1 Shop-side ritual (Owner — Inbox Desk only drafts)

1. Buyer named a **live display code** or a Stock-assigned Official mã.
2. Buy Research **Pass** (or Hold-price path for P02/P05). If Official / Square disagree on an *owned* unit, stop and ask Stock. Never invent qty.
3. Inbox Desk drafts the pay line with `{zelle}` = **locked CS pack name**. This repo does not contain that name. Slack already said the pack is locked (2026-09-04).
4. Owner Sends the name **in the thread**, after the piece is confirmed — not as a public website dump.
5. Buyer pays. Owner opens the **bank / Zelle activity**.
6. Only then: Orders → `Paid`, `pay_method=Zelle` (or Cash). Fulfill `Ship` / `Local pickup` / `TBD`.
7. **Then** second Buy Research + 下单. Not before.

Zelle’s own FAQ: use it with people you know and trust; **no purchase protection**; payments to an enrolled recipient **cannot be reversed** ([Zelle: unsure about paying someone you don’t know](https://www.zelle.com/faq/im-unsure-about-using-zelle-pay-someone-i-dont-know-what-should-i-do)).

FTC: sending money through a payment app is **like sending cash** ([FTC payment-app alert](https://consumer.ftc.gov/consumer-alerts/2023/08/do-you-use-payment-apps-venmo-cashapp-or-zelle-read); [ftc.gov/paymentapps](https://www.ftc.gov/paymentapps)).

**Never ship on a screenshot.** Fake “upgrade to business Zelle” links are hostile. Overpay + “refund the extra” is classic P2P fraud (01 §5.4).

### 5.2 Cash meetup

Facebook Marketplace in-person tips: keep the home address private; share the plan; do not change the spot; charged phone ([Facebook help](https://www.facebook.com/help/2329750133711372)). Bay Area PD **Safe Exchange Zones** exist as a pattern (01 cites Oakland PD, etc.). **Owner picks the public spot.** Do not invent a neighborhood in this runbook. Caption ceiling today: `Local cash/Zelle` ([`sassy-closet/lib/captions.ts`](../../sassy-closet/lib/captions.ts)).

Cash at handoff: inspect piece, count cash, done. No “I’ll Zelle when I get home.”

### 5.3 When Zelle is *illegal* for the desk (process, not criminal-code advice)

Inbox Desk refuses to draft a pay line when:

- Buy Research is **Skip** / SKU 无货 and no alternate color agreed.
- Shop Hold still has **no** Boss USD (P02 / P05 until photo-check + Slack/Boss price).
- They asked for a **Venmo handle** that is not in the CS pack.
- They want Owner to Send first from a bot.
- They sent only a screenshot and the bank app is empty — stay Inquiry/Reserved, do not mark Paid.

---

## 6. Order on Taobao (after Paid)

Boss (or a human Scout under Boss) places the order. **Agents do not 下单.** This section is the pre-flight and the after-pay notes.

### 6.1 Two Buy Research passes (non-negotiable)

| Pass | When | Why |
| --- | --- | --- |
| **R1** | After Inquiry, before quote / customer reserve | Short links rot; title 现货 can be order 预售 ([读特 / 腾讯 2025-02](https://news.qq.com/rain/a/20250221A098Y800)); 颜色 qty is per SKU ([taobao.item.sku.get](https://open.alitrip.com/docs/api.htm?apiId=38967)). |
| **R2** | After Paid, **before** 下单 | Someone else bought the last 杏色 / M; seller flipped 预售; `e.tb.cn` 404. |

Same checklist (§10). New **date checked**. If R2 fails, **do not 下单**. Inbox Desk drafts the exception (§9.6–§9.8). Refund / new quote / Cancelled — Owner decides; Slack if $ / hold / Save is involved.

### 6.2 What you click on Taobao

Taobao sells a **SKU**, not “the listing.” Sales props are typically `颜色` × `尺码` (sometimes 款式). OpenAPI: `Sku.properties`, `properties_name`, per-SKU `quantity` / `price` / `status` `normal|delete`.

Rules (07 §7, repeated because this is where money leaves):

1. One customer color → one `skuId`. If you cannot name the 颜色, you cannot 下单.
2. Price per SKU. Shop $25 is not proof 杏色 = 红色.
3. Qty per SKU. Listing 现货 + that 颜色 0 = 无货.
4. 发货 per SKU when `deliveryTimeSetBySku=1` ([OpenAPI 发货合约](https://open.alitrip.com/docs/doc.htm?articleId=121094&docType=1)).
5. Intake chips (Đen, Kem, Hoa, …) are **hints**. Do not overwrite the seller string with a chip.
6. Cover photo is not the SKU. A01’s cover may be Kem while they paid Xanh.

`source_link` must be a **URL**, not a 淘口令. Intake already extracts the first preferred host (`e.tb.cn` / `tb.cn` / `taobao.com` / `tmall.com`) and stores URL only ([`sassy-closet/lib/source-link.ts`](../../sassy-closet/lib/source-link.ts); [PR #16](https://github.com/SkyLanter/Sassy-closet/pull/16)). 口令 expires. Short links rot. Re-open; do not Google a “similar” item id.

### 6.3 After 下单 (staff notes)

Write into `thread_note` (SoT, not git, not catalog.v1):

- TB order id (marketplace id — **not** a carrier number).
- skuId + 颜色 + 尺码 as actually purchased.
- 现货 / 预售 as shown on the **order**, not the title.
- Seller 发货 clock + date.
- Agent / 转运 shipment id if any (second id).
- CN domestic tracking if any (third id).
- International / last-mile tracking when it exists (the only number you usually give the customer).

Keep these **four identifiers separate**. 17TRACK itself says: a Taobao **order** number is not a **carrier** tracking number; they will not open private order pages for you ([17TRACK Taobao brand page](https://www.17track.net/en/brands/taobao)).

Orders status stays **Paid** until there is a real handoff to the customer (US label or pickup). Do not mark **Shipped** because 圆通 scanned in Guangzhou.

### 6.4 Square after 下单?

Almost never.

Square is a **tiny owned closet** (07 §9.3). In-flight Taobao, Wishlist, and “Available” tiles stay out. Save only if Boss now owns a leftover / keep piece, counted, Track ON, Slack yes. SKU = assigned mã. Variation = Asia size + the **same color word you sold**.

TOMORROW’s line “Paid? Owner Zelle + Square Save” is the **owned-piece** path. Dropship Paid ≠ Save.

---

## 7. Tracking

### 7.1 Legs (say the stack; never quote “48h” as the porch date)

| Leg | 现货-ish | 预售-ish | Who sees it |
| --- | --- | --- | --- |
| Seller 发货 | Platform 现货 mind is often **24h / 48h 发货** after pay ([淘宝发货时效 tool copy](https://www.imeie.com/archives/6536.html); [发货管理规范](https://jianghu.taobao.com/detail/47301_58664622)) | PDP days (OpenAPI `tbDeliveryTime`; fashion 预售 15–90d shows up in the wild) | Boss on TB |
| CN transit → warehouse / agent | days | same after 发货 | Agent dashboard |
| International + US last mile | often 1–3 weeks depending on line | same | Customer |
| Duty / exam | **not optional to mention** | same | Customer |
| Bay Area pickup | skip last mile if Boss already has the unit | n/a | Customer |

Consumer 预售 terms: 发货时间 **以宝贝详情页为准** ([淘宝预售业务协议规范](https://terms.alicdn.com/legal-agreement/terms/suit_bu1_taobao/suit_bu1_taobao202012010036_72763.html)).

**US customs.** CBP **CSMS #64917563**: effective **2025-05-02 00:01 EDT**, products of China and Hong Kong **do not** get 19 U.S.C. § 1321(a)(2)(C) de minimis ([bulletin](https://content.govdelivery.com/accounts/USDHSCBP/bulletins/3de903b); [90 FR 80 / 2025-04-28](https://www.govinfo.gov/content/pkg/FR-2025-04-28/html/2025-07325.htm)). Later **EO 14324** suspended duty-free de minimis more broadly (Federal Register implementation notice [90 FR 42418](https://www.federalregister.gov/documents/2025/08/29/2025-16802/notice-of-implementation-of-the-presidents-executive-order-14324-suspending-duty-free-de-minimis)). **Rates move. Do not bake a % into customer copy.** Bake “duty exists; we quote it.”

Messenger bands (07 §4.4 — reuse, don’t invent days per mã):

- 现货 SKU, known line: “Order hôm nay, thường **2–4 tuần** tới US — em giữ cửa sổ, không hứa Amazon.”
- 预售: “Món này **đặt trước** bên TQ, shop họ ghi ~**N ngày** mới gửi. Cộng ship US. Em không chốt ngày lịch.”
- Unknown: “Để Boss mở link xong báo ngày. Chưa yes thì chưa Zelle.”

### 7.2 Which window to open

| Number you have | Open | Do not |
| --- | --- | --- |
| Taobao order id | Taobao / 千牛 order → 物流 | Paste into 17TRACK as if it were UPS |
| Cainiao / 菜鸟 number | [track.cainiao.com](https://track.cainiao.com/orderTrack) (their box asks for **Cainiao** numbers) | Assume every TB parcel is Cainiao-queryable |
| Agent parcel id (e.g. Superbuy “My Parcels”) | That agent dashboard (China leg + QC photos) | Give the customer the agent login |
| Real carrier (USPS / Yanwen / 4PX / …) | Carrier site **and/or** [17TRACK](https://www.17track.net/en/brands/taobao) | Promise 17TRACK will show the CN domestic silent week |
| Nothing yet | Order page + 旺旺 | Invent a tracking string |

17TRACK help: they are **not** connected to every Cainiao / marketplace reference; they want the **original carrier** number ([17TRACK help: Cainiao](https://help.17track.net/hc/en-us/articles/115002402551-Why-can-t-Cainiao-AliExpress-shipping-method-be-tracked)). Economic lines may have **no** scan. Honest Inbox Desk line: “Chưa có mã carrier — shop theo dõi trên đơn Taobao.”

### 7.3 When the customer hears a number

Give a tracking number when it identifies **their** US-bound (or local-pickup) parcel — not when 中通 accepted a bag of twenty SKUs.

Until then, Inbox Desk drafts **status in words** + the band you already sold. Do not spam six Chinese scan events.

Orders → **Shipped** when the US-facing label exists **or** Boss has handed a real last-mile number. **Picked up** when cash/meetup is done. `meetup_or_ship` / `fulfill` hold the path.

### 7.4 FTC clock (internet / phone orders)

A Messenger “ship it to Texas” **is** a mail / internet / telephone order (16 CFR 435 — *regardless of how advertised or paid*). If you state a ship-by time, you need a **reasonable basis**. If you state **nothing**, you still need a reasonable basis to ship within **30 days** of a properly completed order. If you will miss that, you must offer **delay-or-refund**, clearly, without them having to demand it ([FTC business guide](https://www.ftc.gov/business-guidance/resources/business-guide-ftcs-mail-internet-or-telephone-order-merchandise-rule); [eCFR Part 435](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-435)).

Face-to-face cash meetup is the carve-out the 2014 amendments discuss. Do not write “ships tomorrow” unless the piece is in hand and Boss has a carrier ritual.

**Dropship implication:** if you sold a 预售 “~20 ngày + US ship,” you stated a **band**. If the factory slips past the band you had a reasonable basis for, **Inbox Desk runs §9.7 the day you know** — not after the customer chases.

---

## 8. Exceptions

Stop. Re-run Buy Research if the page might have changed. Draft; Owner Sends. Slack if $ / hold extend / Square is involved.

### 8.1 Wrong color

**How it happens**

- Customer: “cái trong ảnh.” Cover is Kem; they meant Xanh (A01 has both names on the hub; live `catalog.v1` images are `colorId: null` — gallery is **not** proof).
- Boss tapped the first 颜色 on TB.
- `/admin` hex box with no name (staff widget; PDP must stay **text** — 02 / 07).
- 色差: studio vs fabric vs livestream filter.
- 预售 cut 2 ≠ sample.

**Ops**

1. Do not 下单 “the pretty one.”
2. Repeat **mã + TB 颜色 string + VN word + size + cm** in the yes-message before Paid.
3. If already Paid / already 下单: photo the SKU panel + order page. If wrong SKU shipped in CN, **旺旺 / agent intercept** is cheaper than a US bounce.
4. If already on her porch: Inbox Desk drafts the mismatch; Owner offers photo-check / return path Boss names. **Do not invent a restock mã.**
5. Flip to shop Hold only if you can no longer honestly sell that color.

**Inbox Desk:** §9.5. **Buy Research:** checks 4, 8, 9, 14.

### 8.2 预售 delay

**How it happens**

- Title / 客服 said 现货; order says 全款预售 N 天 (documented bait: [读特](https://news.qq.com/rain/a/20250221A098Y800)).
- SKU-level clock: cover 现货, paid color 预售 (`deliveryTimeSetBySku`).
- Mixed cart waits for the slow SKU (common seller paste: 现货 3–10d vs 预售 45–90d; holidays excluded — 07 cites [r/taobao](https://www.reddit.com/r/taobao/comments/o0ghiw/does_anyone_know_what_presale_means_on_taobao/)).
- 节假日 / 工厂放假 (CNY, 618, 双11, summer rest) **not** in the PDP day count.
- Tmall 延迟发货 / 缺货 rules on the *seller* side (赔付红包, 72h still not shipped → 缺货 mind — [天猫物流时效公示 excerpts](https://diantuoyi.com/article/13816.html)) do **not** automatically become a Sassy customer promise. They are a **signal** to tell her *today*.

**Ops**

1. Believe the **order’s** clock, not the title.
2. Same day: Inbox Desk §9.7 (FTC option notice shape: new date you have a basis for, **or** cancel + refund).
3. Do not invent the new date. If you cannot ship and cannot name a revised date with a basis, **cancel and refund** (FTC: if you will never ship, refund without being asked).
4. Prompt refund on Zelle is **Owner in the bank app**. Agents do not reverse Zelle (Zelle: you generally **cannot** reverse; Owner sends a **new** payment).
5. Update `thread_note`. Status stays Paid until refunded → **Cancelled**, or until actually Shipped.
6. If the *tile* still implies a short clock, flip to Hold or rewrite the band (Origin copy — 07 APPLY). Do not silently keep “2–4 tuần” on a 45-day 预售.

### 8.3 Out of stock / 下架 / 无货

**How it happens**

- skuId `quantity` 0 or `status=delete`.
- Item 下架 — OpenAPI 口令 convert error `10000` (下架或非淘客) on stale 淘客 links ([tpwd.convert](https://developer.alibaba.com/docs/api.htm?apiId=32932)).
- `e.tb.cn` 404; tile still pretty.
- Seller relists under a **new** `id=` — old skuId is dead.
- Second customer after you just bought the last unit.

**Ops**

1. R2 failed → **do not 下单**.
2. If not yet Paid: §9.6; offer another **mapped** color (second skuId) or shop Hold. Do not invent a cousin listing.
3. If Paid: refund or agreed alternate SKU (new Buy Research Pass on *that* skuId). Slack if the $ changes.
4. Wishlist finds without a link: `--no-source`, never a guessed URL ([`append_wishlist_row.py`](../../excel-kit/sot/append_wishlist_row.py) exits 2 unless `--source` or `--no-source`).
5. Site may stay Available only while Boss still wants conversations **and** some SKU on that item still Passes. If the look is dead, Hold the tile. Do not mint `A03` as a replacement.

Seller-side 缺货 (Tmall: delay + 72h still not shipped, or seller admits 缺货) is **their** penalty ladder. For Sassy it is an **exception day**: tell the customer; do not wait for a 红包 to appear in 千牛.

### 8.4 Other exception table

| Failure | Symptom | Desk move |
| --- | --- | --- |
| Short link rot | 下单 404 | New share from GF/Boss; Hold tile; no Paid |
| Duty surprise | “I thought $25 landed” | Quote stack 07 §4.2; CBP cites; do not invent a duty $ |
| FX drift | Staff used stale 6.71 | Staff-only weekly label on intake; never print ¥ on the shop |
| Screenshot Paid | JPEG, empty bank | Stay Reserved; §9.4 |
| Size miss | Asia M ≠ her 88cm | cm sheet (02); do not “US M” |
| Photo detect mis-file | Wrong mã card | Confirm `source_link` + folder |
| Two alphabets | A01 vs AO001 in one Slack ask | Say which book |
| Silent `/admin` Save | Title “on hand” locked into Blob | 07 §10.3; agents do not click Save |
| 色差 after unbox | “Không giống ảnh” | Photo-check Hold is cheaper next time; this time Boss path |
| Agent QC fail | Photo / wrong item in warehouse | Intercept; do not mark Shipped |

---

## 9. Inbox Desk — draft patterns (never Send)

### 9.0 Contract

**Inbox Desk produces clipboard text.** Owner pastes into Messenger and taps Send.

Hard rules (if Origin later builds a page, implement these as UI):

| Control | Rule |
| --- | --- |
| **Copy draft** | Allowed |
| **Send** | **Must not exist.** No Meta Send API from this repo or from Origin staff tools ([Messenger Send API exists](https://developers.facebook.com/docs/messenger-platform/send-messages/); shop law forbids agent Send). |
| **Post** | Must not exist |
| **Square Save** | Must not exist |
| **Zelle request** | Must not exist |
| **Mã picker** | Published allowlist + Stock-assigned Official only. **No Next mã A03.** |
| **$ field** | Boss table or blank. Reject P05 `23`. |
| **Customer name** | Optional on the draft; **never** commit to git |
| **Zelle identity** | Placeholder `{zelle}` resolved from the **CS pack**, not from the page source |
| **Tracking field** | Paste a real carrier number or leave blank — no “generate” |

Intake already: `HARD_STOP = "Copy thôi — Mini Boss không Post, không Send, không Square Save, không tự đặt mã."` and inbox draft *“Mini Boss không gửi hộ.”*

Bot_Activity: `--action draft|propose|log|skip`, `--status` default `draft`, refuse `saved|save|posted|sent|zelle`.

Meta **icebreakers / Page greeting** are Owner-configured automations, not Cloud Agent Send (01 §2.3; [Page greeting help](https://www.facebook.com/help/1698046970464236)). The 24-hour messaging window still starts when the **buyer** messages ([Meta messaging best practices](https://www.facebook.com/business/help/269324800441478)). Speed is the abandoned cart. Drafts must be ready the same waking block PT.

Placeholders below: `{code}` = published lookbook code **or** Stock-assigned Official. `{zelle}` = locked CS name. `{tb_color}` / `{asia}` / `{cm}` / `{usd}` / `{n}` / `{band}` / `{carrier}` = **filled from Buy Research or the bank**, never guessed. Do not replace them with a made-up mã.

### 9.1 First reply — look is listed (Available tile)

**VI**

> Chào iu, mã **{code}** nha 💕  
> Shop order Taobao theo đúng màu/size em chọn, rồi ship US.  
> Em gửi: màu (tên, không phải “cái trong ảnh”) + size Á châu + cm + city / pickup.  
> Em chưa chốt giá/ngày nhận cho đến khi Boss mở link check **đúng SKU / 现货 hay 预售**.  
> Zelle khi em yes. Mini Boss không giữ hàng hộ.

**EN**

> Hi — **{code}**. We order the Taobao SKU you pick, then ship US.  
> Send: color **name** + Asia size + cm + city.  
> Price/ETA lock only after we reopen the link (spot vs pre-sale, that color).  
> Zelle when you yes. No cart hold on the website.

Do not use “on hand” / “một chiếc đang có” even if `/m/A01` still says it (07 APPLY debt).

### 9.2 First reply — shop Hold / Inbox for price (P02 / P05 shape)

> **{code}** đang Hold — kiểm tra ảnh, **chưa có giá USD**.  
> Em gửi thêm ảnh / số đo. Không Zelle cho đến khi Boss chốt giá.  
> (Không đọc Hold này là “đã giữ cho bạn khác.”)

EN: “Hold · photo-check, no USD yet — inbox for price.” Do **not** draft `$23` for P05.

### 9.3 现货 confirm (after Buy Research Pass)

> Em ơi, Boss mở link **{code}** màu **{tb_color}** size **{asia}+{cm}**: **现货**, họ ghi gửi trong ~{n} ngày (**nội địa TQ**).  
> Cộng chuyển US, cửa sổ nhận khoảng **{band}**. Duty/line: **{included\|TBD}**.  
> Giá chốt **${usd}**. Yes thì Zelle **{zelle}**, shop mới order đúng SKU.

### 9.4 预售 confirm

> Món **{code}** màu **{tb_color}** đang **预售** — shop TQ hẹn ~**{n} ngày** mới gửi, chưa kể ship US / ngày lễ xưởng.  
> Không hứa ngày lịch. Vẫn muốn thì em yes + Zelle **{zelle}**, shop đặt. Không thì thôi, không giữ giá.

### 9.5 Color mismatch / cover ≠ SKU

> Ảnh bìa là **{cover_color}**. Em đang hỏi **{asked}**.  
> Đó là hai SKU Taobao. Em chọn một giúp iu — Boss không order “cái đẹp nhất trong ảnh.”

### 9.6 SKU gone / 下架 / 无货

> Hôm nay link **{code} / {tb_color}** hết hoặc gỡ.  
> Site có thể còn Available vì chưa Hold. **Chưa order được.**  
> Em muốn đổi màu (Boss check SKU mới) hoặc để Hold inbox giá không?

### 9.7 预售 / factory slip (FTC option)

> Không gửi đúng cửa sổ đã nói (**{old_band}**).  
> Em chọn: đợi đến **{new_date_with_basis}** **hoặc** hoàn.  
> Shop không tự giữ tiền im. ([FTC 30-day Rule](https://www.ftc.gov/business-guidance/resources/business-guide-ftcs-mail-internet-or-telephone-order-merchandise-rule))

Do not send until there is a real paid internet order. Do not invent `{new_date_with_basis}`.

### 9.8 Customer reserve 24h

> Giữ **{code} {tb_color} {asia}** giúp em **24h** (tới {time PT}).  
> Inbox trước giờ đó để Zelle / hẹn mặt. Sau giờ đó món về Available trên site — trừ khi Boss yes thêm giờ trên Slack.

Past 24h draft **to Slack**, not to the customer, until Boss answers:

> Hold {code} {tb_color} {asia} past 24h?

### 9.9 Zelle ask (name locked)

> Zelle giúp mình nhận nhanh. Zelle **không có bảo vệ mua hàng** ([FAQ](https://www.zelle.com/faq/im-unsure-about-using-zelle-pay-someone-i-dont-know-what-should-i-do)).  
> Em chỉ Zelle **đúng tên {zelle}** mình gửi trong chat — không link lạ, không “upgrade account.”  
> Mình cần thấy tiền trong app ngân hàng. Screenshot chưa tính.

### 9.10 Screenshot only

> Mình cần thấy tiền trong app ngân hàng. Screenshot chưa tính.  
> Giữ **{code}** thêm [≤24h] giúp.

### 9.11 Paid → we are ordering

> Thấy Zelle rồi 💕 Shop đặt đúng SKU **{tb_color} / {asia}** trên Taobao.  
> Tracking US gửi khi có **mã carrier**. 现货 48h là kho TQ, không phải porch em.

### 9.12 Tracking — have a carrier number

> Mã theo dõi: **{carrier}**. Dán vào trang hãng hoặc [17TRACK](https://www.17track.net/).  
> Đây là chặng US / international. Chặng TQ có thể không hiện trên app này.

### 9.13 Tracking — no carrier yet

> Chưa có mã carrier. Shop theo dõi trên đơn Taobao / kho chuyến.  
> Cửa sổ vẫn **{band}**. Có số sẽ nhắn trong thread này.

### 9.14 Shipped / Picked up

> Hàng ra last-mile rồi 💕 Tracking **{carrier}**.  
> hoặc: Hẹn **{public_spot_owner_chose}** — cash đủ, xem món, xong. Không Zelle ở lề đường.

### 9.15 Already reserved for someone else

> **{code}** đang giữ cho bạn khác (≤24h trừ khi Boss yes). Em muốn mình báo khi về Available không?

### 9.16 Gone / Sold (owned mã retired)

> **{code}** sold / không còn. Không giữ chỗ trên món đã bán. Không tái sử dụng mã Official đã Sold.

### 9.17 Hunt / no source (Wishlist, not a lookbook tile)

Reuse GF intake voice only when the packet is actually From GF ([`excel-kit/inbox/gf_intake_reply_templates.md`](../../excel-kit/inbox/gf_intake_reply_templates.md)):

> Đây là đang xem / ứng viên — **chưa lên Square**, chưa phải hàng shop đang bán.

Never: “Đã lên Square” / “Em tự lấy mã AO…” / “Hàng đang bán” while Wishlist or staged.

### 9.18 Ship quote (no dollar on the site)

> Ship toàn US — mình báo **số** trong chat. Web chưa in phí ship vì Boss chưa chốt flat $.  
> Tổng = giá món + ship. Local cash meetup thì không ship.

Forbidden until Slack writes a number: `$6.95`, `free ship`, copying another boutique’s `$10 / $300+` (01 §6).

### 9.19 Refuse list (do not draft)

| Ask | Why |
| --- | --- |
| “Send her a message from the API” | Shop law |
| “Just pick A03” | `/admin` Next mã is an invent |
| “Quote US M” | DESIGN_NOTES refuse list |
| “Put $8 ship on the card” | Unlocked flat ship $; FTC + NN/G fee honesty |
| “Mark Paid from this screenshot” | Zelle + FTC cash-like |
| “Tell her duty-free” | CBP 2025-05-02+ |
| “Ships tomorrow” | No basis unless in-hand + ritual |
| “Here’s a similar Taobao I Googled” | Never invent `source_link` |
| Customer PII into git / Bot_Activity | `PROMPTS.md` |

---

## 10. Buy Research — TB page checks

### 10.0 Contract

**Buy Research is a page audit.** Scout / Boss opens `source_link` *today*. The output is **Pass / Pass-预售 / Hold / Skip** plus a staff note. It is not a customer page. It is not a 下单 bot.

Live Origin has **no** `/buy-research` (404). Until it does, the checklist lives here + Slack “Buy/Skip.” If Origin builds the page:

- Input: existing mã **or** Wishlist row + `source_link`.
- No “find similar.”
- No mint mã.
- No publish to catalog.v1.
- Show extracted URL only (same rules as [`source-link.ts`](../../sassy-closet/lib/source-link.ts)).
- Persist staff fields on hub / SoT / Orders `thread_note`, **never** in customer JSON.

Wishlist: `--source URL` or `--no-source`. Silent “forget the link” is forbidden. `--ma` on Wishlist is forbidden.

### 10.1 When to run

| Moment | Required |
| --- | --- |
| New Inquiry on a listed look | R1 before any $ / reserve |
| P02 / P05 inbox | R1 — still no $ until Boss |
| Customer changes color or size | R1 again (new skuId) |
| After Paid | **R2** before 下单 |
| Exception day (delay, 无货 rumor, 色差) | R3 |
| Weekly soft-launch | Optional sweep of the **ten** allowlist links — do not add an 11th |

### 10.2 Paste hygiene (before the page)

A phone share is a **blob**:

```text
【淘宝】https://e.tb.cn/h.7KxYzAb  HU1234 「…」
点击链接直接打开 或 复制这条信息￥abc123XYZ￥后打开淘宝
```

| Piece | Store? |
| --- | --- |
| `https://e.tb.cn/h.…` / `item.taobao.com?id=` | **Yes** — `source_link` |
| `&skuId=` | Yes — staff notes |
| `￥…￥` 淘口令 | **No** — expires / 淘客-tainted |
| `s.click.taobao.com` | Prefer item / `e.tb.cn` |
| Chinese wrapper | Strip |

Intake `normalizeSourceLink`: first HTTP URL; prefer those hosts; strip trailing punct and glue-on 中文; empty paste → empty string — **never invent**. Tests lock the real share shape ([`sassy-closet/tests/source-link.test.ts`](../../sassy-closet/tests/source-link.test.ts)). Placeholder `item.htm?id=PLACEHOLDER` exists only in **kit examples**.

### 10.3 The page (18 checks)

Open the extracted URL on a logged-in Taobao / 千牛 / agent preview. Tick in order. **Fail-closed:** any ❌ that is not explicitly “Hold-and-ask-Boss” → **Skip** (do not quote, do not 下单).

| # | Check | Pass looks like | Fail |
| --- | --- | --- | --- |
| 1 | URL opens | Same item you stored | 404 / 下架 / “similar items” wall |
| 2 | `id=` stable | Matches hub note if you already saved one | New id after relist (treat as **new** link) |
| 3 | Title vs tool | 现货 / 预售 **tool** + 发货时效, not title adjective alone | Title 现货, tool 预售 — record **预售**, tell CS |
| 4 | 颜色 list | The VN word maps to a **printed** 颜色 | Cannot map; hex-only guess |
| 5 | 尺码 list | Asia letter or seller chart in **cm** | US chart only; no cm |
| 6 | skuId | Selected 颜色 × 尺码 shows a skuId | “Default” SKU / first row |
| 7 | qty **that** SKU | > 0 (or 预售 that still accepts pay) | 0 / delete |
| 8 | ¥ **that** SKU | Written down for the quote stack | Assumed = shop $ |
| 9 | Cover vs SKU | You know which photo is which 颜色 | Ordering from the model |
| 10 | 发货 clock | 24h / 48h / N 天 + **date you checked** | “Soon” |
| 11 | Per-SKU clock | If `deliveryTimeSetBySku`, read **this** SKU | Borrowed the cover’s 现货 |
| 12 | 节假日 banner | Added to the band if present | Ignored 工厂放假 |
| 13 | Shop / 旺旺 | Optional: ask 现货 for **that** skuId; still believe the **order** later | 客服 vibe > PDP |
| 14 | 色差 / batch notes | Seller 尺码图 / 色差 disclaimer read | “Looks like the livestream” |
| 15 | Freight to *your* 仓库 / 转运 | Known or TBD | Hidden in the $25 |
| 16 | Duty / line to US | Known or TBD (post-2025-05-02: not “free”) | “Under $800 de minimis” |
| 17 | Photo rights / live tile | Hub photos are **this** item | Editorial `/editorial/*.jpg` used as SKU proof |
| 18 | Mã honesty | You are auditing a **listed** code or a Wishlist row | Temptation to mint A03 / AO016 |

OpenAPI field reminders: `deliveryTimeType` `0` ≈ 48h, `3` ≈ 24h, `2` = 全款预售 with `tbDeliveryTime` in **days** (dress-category examples include 3, 5, 7, 10, 15, 20, 30, 45 — those are **platform examples**, not Sassy lead times).

### 10.4 Outcomes

| Outcome | Quote? | Tile | Orders | Slack |
| --- | --- | --- | --- | --- |
| **Pass 现货** | Yes, with CN clock + US band + duty/line | Stay Available if Boss still wants chats | Inquiry → (Reserved) → Paid after Zelle | Only if $ leaves the Boss table |
| **Pass 预售** | Yes, with PDP days said out loud | Stay Available **or** Hold if the last caption implied 现货 | Same | If clock blows the old band |
| **Hold** | No $ , or TBD ship/duty only | **Hold · Inbox for price** | Stay Inquiry until Boss | If you need a price yes |
| **Skip** | No | Hold if it was a live look | Inquiry → Cancelled or leave Inquiry + note | If Paid already (refund) |

P05 hub cell may show `23`. **Do not publish it.** Empty or Hold-forced `sell_usd` → `priceUsd: null` (PR #18).

K01 live catalog has **no** recorded colors. Buy Research **must not invent Đen**. Ask Boss / reopen TB; refuse 下单 “whatever is in the cover” (07 §7).

### 10.5 What to write down (staff)

```text
date_checked_pt:
ma:                 # published or Stock-assigned — never minted here
source_link:        # extracted URL only
item_id:
skuId:
颜色:               # seller string
尺码:               # seller string + cm
boutique_word:      # Kem / Xanh / … text chip, if mapped
现货_or_预售:
发货_clock:
qty_this_sku:
¥_this_sku:
duty_line:          # included / TBD — not a guessed %
outcome:            # Pass | Pass-预售 | Hold | Skip
notes:
```

Never put this block in `catalog.v1`, captions, or the PDP.

### 10.6 Worked *shape* (A01 — do not fill fake SKU facts)

A01 is **published**: Available, $25, TOP, Message A01. Hub colors include Kem / Xanh. Photos `001.jpg`, `002.jpg` exist; export `colorId` is **null** (PR #18 sample).

Buy Research does **not** invent that Kem = 杏色 or that skuId = `123`. Scout opens the stored `source_link`, selects the 颜色 the customer named, reads **that** row. If the link is missing: `--no-source` / Hold / ask GF — **not** a Google lookalike.

Admin “Next mã **A03**” is not a research target.

### 10.7 Quote stack (math lives in 07; desk only fills known terms)

```text
quoted_usd ≈
    TB SKU ¥  (this 颜色 + 尺码, today)
  + CN domestic / warehouse
  + 转运 / international
  + duty + broker/line
  + last-mile
  + Boss margin
  + buffer for 色差 / size miss / 预售 slip
```

Intake FX (`1 USD = 6.71 ¥` weekly label, 2026-09-07 store default) is **staff**, not a customer promise. If any term is unknown → Hold or Messenger TBD. Do not average last week’s haul.

NN/G: unexpected fees feel like a trick; if you cannot calculate yet, **admit the extra charge exists** ([NN/G taxes & fees](https://www.nngroup.com/articles/ecommerce-taxes-fees/)).

---

## 11. Logging: Orders, Slack, Bot_Activity

### 11.1 Orders columns (SoT)

From [`schema.py`](../../excel-kit/schema.py) `SOT_ORDERS`: `order_id`, `date`, `channel`, `buyer`, `fb_handle`, `ma`, `snapshot`, `qty`, `agreed_price`, `ship_fee`, `net`, `order_status`, `pay_method`, `fulfill`, `meetup_or_ship`, `thread_note`, `last_touch`.

Rules:

- `order_id` default `ORD###` if the column exists — **not** a mã.
- `ship_fee` empty rather than guess.
- `buyer` / `fb_handle` omit in any file that might be committed. Live OneDrive may have them; **git must not**.
- Dropship facts (skuId, 现货, TB order id, carrier) → `thread_note` / `snapshot`, not a new unofficial status.

### 11.2 Slack ask shapes (yes / no only)

Already on the wall (templates — **not** live inventory):

- `AO001 / M / đen — add to Square · on-hand 1 · cost ¥80 · price $25 — Save?`
- `Hold AO003 past 24h?`

Dropship adds (use a **real** published or assigned code):

- `{code} / {tb_color} / {asia} {cm} — TB 现货 today? quote $25 + ship 10–18d US — take Paid?`  
  (dollar only if it is the Boss table or Slack already yes’d a change)
- `P05 — still Hold, do not publish hub $23.`
- `{code} Paid but R2 无货 — refund Zelle?`
- `{code} 预售 slipped to {n} days — extend band or refund?`

Until Boss answers, bots stay read-only on that item.

### 11.3 Bot_Activity

`--bot Stock | Scout | Guide | Quill | Ledger | Mini Boss`  
`--action draft | propose | log | skip`  
`--summary` one line, **no customer secrets**.

Example shape (no minted mã):

```text
python3 excel-kit/sot/append_bot_activity.py -w "$SASSY_SOT" \
  --bot Scout --action draft \
  --summary "Buy Research R1 A01 — outcome in thread_note, not this cell"
```

If `--ma` is passed, it must pass `require_ma` or the script prints `ASK_STOCK_MA` and exits 2.

---

## 12. Daily / weekly cadence (dropship overlay on TOMORROW)

SoT **TOMORROW** is “not inventory. Check Square first if a count disagrees.” Overlay:

**Morning (PT)**

1. Dashboard `B43` morning brief — do not invent counts if Excel has not calculated ([`dashboard_brief.py`](../../excel-kit/sot/dashboard_brief.py)).
2. Inbox Desk: unread Page threads. First reply same waking block.
3. Filter Orders: Inquiry without R1; Reserved clocks; Paid without R2 / 下单; Paid with 预售 clock in the window.
4. Square: only for **owned** reserved units. Square 0 + site Available can both be correct.

**Inbox**

5. New hello → Inquiry + §9.1/§9.2 draft.
6. Yes + bank Zelle → Paid → R2 → Boss 下单.
7. Exception day → §8 the **day you know**.

**Scout**

8. R1/R2 queue. Weekly optional sweep of the **ten** allowlist links.
9. Wishlist candidates: source or `--no-source`. Bought without mã → ASK STOCK, still off Square ([GF intake](../../excel-kit/prompts/GF_CLOTHES_INTAKE.md)).

**Night**

10. If Agents changed `excel-kit`, rebuild / append, Kit syncs OneDrive. Still no Save / Send / Zelle.

Soft-launch still needs from Boss (Slack 2026-09-04): Square login on Stock’s box · **flat ship $** · OneDrive sign-in card. Until those exist, desks TBD the ship dollar and do not pretend Stock’s browser is verified.

---

## 13. APPLY (ops — not a redesign)

**Keep** Cormorant / Be Vietnam Pro / motion / no cart / Zelle **word** / Hold P02·P05 / hidden `/admin` (07 §11.0). This file does not restyle the boutique.

### 13.1 Inbox Desk (today, no new URL)

- [ ] CS pack has the locked Zelle **name** off-repo.
- [ ] Drafts in §9 are the pack; Owner Sends.
- [ ] Ask / Mini Boss copy buttons stay **Copy**, never Send.
- [ ] Every new hello has an Orders Inquiry (or an explicit Skip note).
- [ ] No customer PII in git.
- [ ] Prefill `m.me` + `text=` is Origin APPLY (01 §11) — Desk still types the code if the Page opens bare.

### 13.2 Buy Research (today, no new URL)

- [ ] Every Paid has R1 + R2 dates in `thread_note`.
- [ ] `source_link` is extracted URL or `--no-source`.
- [ ] No Google-similar id.
- [ ] K01: no invented color.
- [ ] P02 / P05: no published $23.
- [ ] Allowlist stays ten codes.

### 13.3 If Origin builds `/inbox-desk` or `/buy-research`

- [ ] No Send / Post / Save / Zelle / Next-mã.
- [ ] Mã picker = allowlist + assigned Official.
- [ ] Buy Research writes staff notes only.
- [ ] Inbox Desk fills `{zelle}` from a **server-side** CS pack, not from client HTML.
- [ ] Same rose / boutique chrome if the pages are in the sell-test app — **do not** ship a sterile “ops dashboard” that replaces the lookbook.

### 13.4 Stock / Square

- [ ] Track ON still standing (Boss **yes** 2026-09-04 13:24 PT).
- [ ] No wishlist / in-flight TB import.
- [ ] Save ask in Slack per batch.

### 13.5 Verify this document (kit)

```text
# file exists; relative kit links resolve from this path
test -f docs/ai-clothing-shop/08-dropship-ops-runbook.md
```

Grep check: extra codes (`A03`, `Q01`, `AO016`, …) appear only as **refusals** or Slack/kit **templates**. No live tracking numbers. No Zelle handle. No invented skuId.

---

## 14. Anti-patterns (quick refuse)

- Treating **Available** as Square qty.
- Treating **Hold** (P02) as Reserved.
- Treating **预售** as shop Hold (unless $ is also unknown).
- Marking Orders `Shipped` on a Guangzhou scan.
- Pasting a Taobao **order** id into 17TRACK as UPS.
- Sending Taobao 48h as the US ETA.
- “Duty-free under $800” after 2025-05-02 (and later broader suspensions).
- Screenshot = Paid.
- Cover photo = 颜色.
- `/admin` Next mã = assignment.
- Caption with `e.tb.cn`.
- US size “helpful” conversion.
- Agent Send “to be faster.”
- Inventing a 11th lookbook code in a draft.
- Filing customer chat in From GF.
- Silent `/admin` Save that locks “on hand” into Blob.

---

## 15. Open questions (do not answer by inventing)

1. **Flat ship $** — unlocked on Slack. Until yes, inbox-only.
2. **Zelle display name** — locked in CS pack; not in this repo. Do not guess.
3. **Meetup neighborhood** — Owner picks; not published here.
4. **Venmo** — on SoT list; no public CTA yet.
5. **A01 Kem/Xanh ↔ actual 颜色 / skuId** — live TB page only; not in git.
6. **K01 colors** — none recorded; do not invent.
7. **Whether Origin will ship Inbox Desk / Buy Research URLs** — 404 today; this file is the contract.
8. **Official mãs for the ten lookbook codes** — do not bridge `A01` → `AO001` without Stock.
9. **Current duty %** — do not bake; quote per shipment.
10. **Granola / Notion** — empty this pass; Slack yes still wins.

---

## 16. Sources

### 16.1 This shop (primary)

| Source | What it proves |
| --- | --- |
| Live sell-test 2026-09-09 (`/`, `/m/A01`, `/admin`) | 10 tiles; A01 “on hand”; P02/P05 Hold; Next mã A03; no `/inbox-desk` |
| [sassy-closet.vercel.app](https://sassy-closet.vercel.app) | Intake Lưu / staged / Taobao field / FX label |
| [README.md](../../README.md) | Facebook = store; Square Free = on-hand; bots draft; Cloud Agents |
| [sassy-closet/BOSS.md](../../sassy-closet/BOSS.md) | Staged-only; no Square Save; Blob or wipe |
| [sassy-closet/lib/ask-fallback.ts](../../sassy-closet/lib/ask-fallback.ts) | Copy inbox; Mini Boss không gửi hộ; staged ≠ Square |
| [sassy-closet/lib/captions.ts](../../sassy-closet/lib/captions.ts) | Inbox + Zelle + Ship toàn US; no $ ship; no TB URL |
| [sassy-closet/lib/source-link.ts](../../sassy-closet/lib/source-link.ts) + [PR #16](https://github.com/SkyLanter/Sassy-closet/pull/16) | Extract URL; never invent |
| [sassy-closet/lib/kinds.ts](../../sassy-closet/lib/kinds.ts) | Asia sizes; text color chips including non-hues |
| [excel-kit/schema.py](../../excel-kit/schema.py) | Orders enums; pay/fulfill; ASK_STOCK_MA; BOTS_DRAFT_ONLY |
| [excel-kit/sot/append_order_row.py](../../excel-kit/sot/append_order_row.py) | Exact statuses; omit buyer; existing mã only |
| [excel-kit/sot/append_bot_activity.py](../../excel-kit/sot/append_bot_activity.py) | Refuse sent/posted/zelle; Pacific |
| [excel-kit/sot/append_wishlist_row.py](../../excel-kit/sot/append_wishlist_row.py) | `--source` or `--no-source` |
| [excel-kit/sot/build_sot_desktop.py](../../excel-kit/sot/build_sot_desktop.py) | START HERE + TOMORROW inbox steps |
| [excel-kit/square/README.md](../../excel-kit/square/README.md) | Track ON; SKU=mã; no wishlist import |
| [excel-kit/DESIGN_NOTES.md](../../excel-kit/DESIGN_NOTES.md) | No US sizes; no bot Zelle |
| [excel-kit/inbox/gf_intake_reply_templates.md](../../excel-kit/inbox/gf_intake_reply_templates.md) | Never claim Square; never mint |
| [excel-kit/PROMPTS.md](../../excel-kit/PROMPTS.md) | Task 3 Orders; task 11 never Messenger intake |
| Slack `#shop-decisions` 2026-09-04 | yes/no; Track ON yes; Square LIVE; CS pack; Scout Buy/Skip; flat ship $ unlocked; Facebook stays the store |
| PR #18 `SELL_CATALOG_CONTRACT.md` | Allowlist + USD table; omit `source_link`; Hold P02/P05; qty=1 |
| Sibling PRs [19](https://github.com/SkyLanter/Sassy-closet/pull/19) [21](https://github.com/SkyLanter/Sassy-closet/pull/21) [22](https://github.com/SkyLanter/Sassy-closet/pull/22) | PDP / dropship law / Messenger |

### 16.2 Taobao / platform

| Source | What it proves |
| --- | --- |
| [淘宝预售业务协议规范（消费者侧）](https://terms.alicdn.com/legal-agreement/terms/suit_bu1_taobao/suit_bu1_taobao202012010036_72763.html) | 预售 = 预售工具; 发货时间 = PDP |
| [淘宝网发货管理规范](https://jianghu.taobao.com/detail/47301_58664622) | 48h or set window; 预售 tools for longer |
| [发货时效工具升级 copy](https://www.imeie.com/archives/6536.html) | C-end 现货 = 24h/48h 发货 mind; longer = 预售 |
| [OpenAPI 发货合约](https://open.alitrip.com/docs/doc.htm?articleId=121094&docType=1) | `deliveryTimeType` 0/2/3; per-SKU days |
| [taobao.item.sku.get](https://open.alitrip.com/docs/api.htm?apiId=38967) | skuId, 颜色/尺码, per-SKU qty/price/status |
| [taobao.tbk.tpwd.convert](https://developer.alibaba.com/docs/api.htm?apiId=32932) | 口令 / `e.tb.cn`; 下架 10000 |
| [读特：现货变预售](https://news.qq.com/rain/a/20250221A098Y800) | Title/客服 ≠ order clock |
| [r/taobao 预售 paste](https://www.reddit.com/r/taobao/comments/o0ghiw/does_anyone_know_what_presale_means_on_taobao/) | Mixed carts wait; holiday exclude |

### 16.3 Tracking

| Source | What it proves |
| --- | --- |
| [17TRACK Taobao](https://www.17track.net/en/brands/taobao) | Carrier number ≠ TB order id; no private order access |
| [17TRACK Cainiao help](https://help.17track.net/hc/en-us/articles/115002402551-Why-can-t-Cainiao-AliExpress-shipping-method-be-tracked) | Marketplace refs often untrackable; need original carrier |
| [Cainiao track](https://track.cainiao.com/orderTrack) | Cainiao-number box, not “any TB id” |

### 16.4 US ship / duty / delay / pay

| Source | What it proves |
| --- | --- |
| [CBP CSMS #64917563](https://content.govdelivery.com/accounts/USDHSCBP/bulletins/3de903b) | 2025-05-02: no de minimis for CN/HK products |
| [Federal Register 2025-04-28](https://www.govinfo.gov/content/pkg/FR-2025-04-28/html/2025-07325.htm) | EO 14256 implementation |
| [90 FR 42418 / EO 14324 notice](https://www.federalregister.gov/documents/2025/08/29/2025-16802/notice-of-implementation-of-the-presidents-executive-order-14324-suspending-duty-free-de-minimis) ([mirror](https://thefederalregister.org/documents/2025-16802/notice-of-implementation-of-the-president-s-executive-order-14324-suspending-duty-free-de-minimis-treatment-for-all-coun)) | Later broader de minimis suspension — rates still not for customer copy |
| [FTC 30-day Rule — business guide](https://www.ftc.gov/business-guidance/resources/business-guide-ftcs-mail-internet-or-telephone-order-merchandise-rule) | Reasonable basis; delay-or-refund |
| [16 CFR 435](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-435) | Internet/phone orders; prompt refund definition |
| [Zelle FAQ — unknown payee / no reverse](https://www.zelle.com/faq/im-unsure-about-using-zelle-pay-someone-i-dont-know-what-should-i-do) | No purchase protection; cannot reverse |
| [FTC payment apps](https://consumer.ftc.gov/consumer-alerts/2023/08/do-you-use-payment-apps-venmo-cashapp-or-zelle-read) | Like cash |
| [NN/G fees](https://www.nngroup.com/articles/ecommerce-taxes-fees/) | Admit unknown extras |
| [Facebook in-person](https://www.facebook.com/help/2329750133711372) | Meetup safety pattern |
| [Meta messaging best practices](https://www.facebook.com/business/help/269324800441478) | Greet, look available, answer |
| [Messenger Send API](https://developers.facebook.com/docs/messenger-platform/send-messages/) | Exists — shop still forbids agent Send |

### 16.5 Weaker / vendor (do not treat as shop law)

Seller blogs on “2025 发货 48h,” Superbuy notices, Fishgoo tracking explainers. Use them as **color** only. PDP / order clock / CBP / FTC / Zelle / Slack win.

---

## 17. One-page tear-off

> Facebook hello → Orders **Inquiry** → **Buy Research R1** → quote or Hold → yes → **Zelle in the bank** → Orders **Paid** → **Buy Research R2** → Boss 下单 → track **carrier** (not order id) → **Shipped / Picked up**.  
> Square only if we **own** it and Slack said yes.  
> **Inbox Desk drafts. Owner Sends.** Mini Boss không gửi hộ.  
> **Buy Research** is the Taobao page *today*: skuId × 颜色 × 尺码 × 现货/预售 × qty × ¥.  
> 现货 48h is their warehouse. 预售 is the PDP. Delay → FTC choice the day you know.  
> P02 / P05 stay Inbox for price. P05 is not $23. A03 is not a mã.  
> If you had to invent a mã, a dollar, a color, or a tracking number — stop; you are lying.

*Learn track. Agents draft. Owner posts, sends, takes Zelle, Saves Square.*
