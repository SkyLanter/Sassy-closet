# 07 — Taobao dropship boutique

Learn track (Ultra burn) for **Sassy Closet**: a VN / Bay Area Facebook clothing boutique that **sells mainly by dropshipping through Taobao**, then ships in the US. This is **not** a large local warehouse. Square Free still wins on-hand — it just has almost nothing to win until a piece is actually bought, received, counted, and Boss-saved.

**Live apply target:** [https://sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)  
**Keep:** current design language + fancy motion. Honesty is a copy / data / admin-guard change, not a redesign.

**Date of live inspect:** 2026-09-09.  
**This repo** (`SkyLanter/Sassy-closet`) owns kit + intake. **Origin** owns the sell-site app. Do not fight Origin `main` from here.

---

## 0. How to use this note

| Reader | Use |
| --- | --- |
| Origin shop agent | §11 APPLY checklist. Change copy / guards. Do **not** restyle. |
| Intake / kit agent | §5–§7, §10. Never invent mã / $ / stock. Keep `e.tb.cn` extract. |
| Boss / Mini Boss | §3 flow + §4 scripts. Facebook inbox is the store. |
| Stock | Square only after `#shop-decisions` yes. Track ON. SKU = owned mã. |

**Hard stops (every surface):**

- Never invent mã, qty, or prices.
- Never Square Save from a bot / site / agent.
- Never Facebook Post / Send from a bot.
- Never put `source_link`, vốn / cost, customer names, or Zelle *identity* on the customer shop.
- The word **Zelle** as a method is OK. No personal name, handle, or phone on the site.
- Wishlist / staged / catalog.v1 ≠ Square on-hand.
- US sizes are never quoted to buyers. Asia size + cm only.

If a later learn doc (Messenger, PDP, admin ops, Blob catalog) disagrees with shop *chrome*, this doc wins on **dropship truth**. Chrome stays pretty.

---

## 1. Boss model — dropship boutique, not a warehouse

Sassy Closet’s public face is a cute boutique: Facebook livestream, Messenger “Message to buy,” Zelle, US ship / Bay Area meetup. The **buying engine** is Taobao (and Tmall when the share lands there).

That means most “Available” tiles are **not** a rack in California. They are a **permission to start a conversation**. The conversation is where Boss:

1. Confirms color / size against the **real Taobao SKU** (颜色 + 尺码), not the cover photo.
2. Re-opens `source_link` and checks **现货 vs 预售** *today*.
3. Quotes USD + lead time + ship path (or Hold / inbox for price).
4. Collects pay (Zelle / local cash) **after** the customer accepts the quote.
5. Orders on Taobao **after** confirm (or after a Boss-approved reserve).
6. Forwards / ships US. Square Save happens only if/when the piece is **owned and counted**.

A large local warehouse model would: receive first → count into Square → sell from on-hand → ship from the shelf.  
**This shop is inverted:** sell the conversation first, buy the garment second, own the unit last.

Owned pieces (GF bought, meetup leftovers, returns that Boss keeps) **do** go Square. They are the exception. Do not write the whole site as if every tile is that exception.

### Two mã families — do not mix

| Family | Where | Shape | Who mints |
| --- | --- | --- | --- |
| Hub / sell / intake | `sassycloset.xlsx`, intake, sell-test | `A01` letter + 2–3 digits | Boss / Stock. Shop admin “Next mã A03” is **not** assignment. |
| SoT Excel | `Sassy_Closet_SoT.xlsx` Official | `AO001` (`AO\|QU\|VA\|AK\|GI\|PK\|SET` + 3) | Stock reads Dashboard `B21:B27`. Scripts never mint. |

Intake `Lưu & lấy mã` can mint the next hub letter (`A01`, `P06`, …) into **staged**. That is not Square. That is not a sell-site allowlist add. That is not Official `AO015`.

Allowlist on sell-test **today** (do not add to this list from imagination):

`A01 S01 P01 P02 P03 P04 P05 K01 H01 A02`

Boss USD table (kit contract, live tiles match):

| Mã | Type | USD | Public status |
| --- | --- | --- | --- |
| A01 | top | 25 | available |
| S01 | set | 28 | available |
| P01 | accessory | 5 | available |
| P02 | thermos | — | **hold** |
| P03 | accessory | 18 | available |
| P04 | accessory | 13 | available |
| P05 | thermos | — | **hold** |
| K01 | jacket | 37 | available |
| H01 | hair | 8 | available |
| A02 | top | 22 | available |

P05’s hub cell may show `23`. **Do not publish it.** Empty or Hold-forced `sell_usd` → `priceUsd: null`, copy “Inbox for price.”

---

## 2. Surfaces — what is allowed to be true

Five systems. They are allowed to disagree. They are **not** allowed to pretend they are one warehouse.

```text
Facebook / Messenger     ← storefront + money talk + hold talk
        │
        ▼
Sell-test shop           ← pretty catalog + Messenger CTA
sassy-closet-shop.vercel.app
        │  (no source_link, no cost, no cart)
        ▼
OD hub sassycloset.xlsx  ← website mirror (All sheet) + Photos/{MA}/
        │
        ├─► Intake sassy-closet.vercel.app   staged rows + source_link
        ├─► SoT Sassy_Closet_SoT.xlsx        Official / Wishlist / Orders
        └─► Square Free                      ONLY owned, Track-ON on-hand
```

| Surface | URL / path | Truth it may claim | Must never claim |
| --- | --- | --- | --- |
| Facebook inbox | Page [Sassy Closet](https://www.facebook.com/profile.php?id=61594312648057) | Quote, hold, color, lead time, Zelle, ship | “In Square” unless Boss saved |
| Sell-test | https://sassy-closet-shop.vercel.app | Lookbook + listed $ or Hold + Message | On-hand warehouse, Taobao URL, vốn |
| Sell admin | `/admin` (not in main nav) | Edit titles / photos / Hold | Next-mã invent, silent price invent |
| Intake | https://sassy-closet.vercel.app | Staged fields + `source_link` + “not Square” | Stock qty, Square Save |
| OD hub | `Documents/Sassy Closet/sassycloset.xlsx` | Staff row + `source_link` + colors text | Customer JSON with cost / link |
| SoT Official | `Sassy_Closet_SoT.xlsx` | Working copy / captions / mã index | Second inventory |
| SoT Wishlist | same book | Hunt / candidate / bought-waiting-mã | On-hand, live mã |
| SoT Orders | same book | Inquiry→… Facebook thread log | Square stock |
| Square Free | Item library | Counted owned units, Track ON | Wishlist, dropship-in-flight |
| `#shop-decisions` | Slack `C0BV3GYC602` | Boss yes/no (Save, mã, price, hold extend) | Customer chat |

Intake `GET /api/ma/{code}` already encodes the split: `{ staged, on_hand, staged_only }`. Empty on-hand → **Staged only — not on Square On_Hand yet**. Sell-test has no such banner today. That is the apply gap.

---

## 3. Message-first order flow

Facebook is the store ([README](../../README.md), `#shop-decisions` 2026-09-04). The site’s job is to start the thread. There is **no cart** on sell-test — keep it that way.

### Happy path (dropship)

```text
Customer sees tile / livestream / story
        │
        ▼
Taps Message to buy  →  Messenger opens Page
        │
        ▼
CS / Boss: confirm mã + 颜色 + size(cm) + ship-to
        │
        ▼
Boss re-opens source_link on Taobao (today, this SKU)
        │
        ├─ 现货, seller qty > 0, color/size still listed
        │     → quote USD + lead-time band + ship path
        │
        └─ 预售 / 无货 / color gone / price jumped
              → Hold or new quote. Do not take “Available” tile as truth.
        │
        ▼
Customer says yes
        │
        ▼
Orders row: Inquiry → Reserved (optional hold) → Paid
        │
        ▼
Boss orders that SKU on Taobao (skuId + 颜色 + 尺码)
        │
        ▼
CN warehouse / 转运 / VN hop  →  US last mile (or Bay Area pickup)
        │
        ▼
Orders: Shipped or Picked up
        │
        ▼
Square Save?  ONLY if Boss now owns a leftover / keep piece
              and #shop-decisions said yes.
```

### Status map (do not collapse these words)

| Word | Whose mouth | Meaning |
| --- | --- | --- |
| **Available** (shop) | Customer site | “You may message about this look.” **Not** Square qty. |
| **Hold · Inbox for price** (shop) | Customer site | No published USD. Photo-check / quote pending. P02, P05 today. |
| **held / Reserved** (Excel Ma_List / Official) | Staff | Working-copy flag. Still not Square unless saved. |
| **Inquiry / Reserved / Paid / Shipped / Picked up / Cancelled** | SoT Orders | Facebook thread log. Exact enum — scripts reject others. |
| **staged / not_square** | Intake | Lưu succeeded. Not owned stock. |
| **on_hand / reserved / sold / dead** | Intake on-hand block | Only if Square-shaped rows exist. Else staged-only banner. |
| **Track ON + qty** | Square | The only number you may call “còn hàng.” |
| **现货** | Taobao seller | Promises *their* 发货 window (often 24–48h CN domestic). |
| **预售** | Taobao seller | Full-pay or deposit+tail. 发货 is the PDP clock (days–months). |
| **Hold extend?** | `#shop-decisions` | Boss yes/no to keep a *customer* hold past the usual window. |

`#shop-decisions` examples already on the wall (2026-09-04):

- `AO001 / M / đen — add to Square · on-hand 1 · cost ¥80 · price $25 — Save?`
- `Hold AO003 past 24h?`

Dropship adds a third ask shape:

- `A01 / Kem / M 88cm — TB 现货 today? quote $25 + ship 10–18d US — take Paid?`
- `P05 — still Hold, do not publish hub $23.`

### What each message must lock

Before Paid, the thread snapshot (Orders `snapshot` / `thread_note`) needs:

1. **Mã** (existing only).
2. **Taobao 颜色 string** as printed on the SKU (Chinese + the VN word you told the customer).
3. **尺码** Asia + cm from the seller chart, not a US conversion.
4. **`source_link`** (clean `https://e.tb.cn/…` or `item.taobao.com?id=`). Staff only.
5. **skuId** if the link has one (`item.htm?id=…&skuId=…`). Staff only.
6. **现货 / 预售 + the seller’s 发货 clock** (date you checked).
7. **Agreed USD** (or explicit Hold — no number).
8. **Ship path** (US address / Bay Area pickup) and that duty/line is **quoted or TBD**, not hidden.
9. **Pay method** (Zelle / cash). No name on the website; name stays in Messenger.

Kit: `excel-kit/sot/append_order_row.py` — `--ma` must already exist; `--channel` defaults to Facebook; `--buyer` omit rather than invent.

### What the site may say in that thread’s first bubble

Sell-test CTAs already deep-link the Page. Keep **Message {mã}**. Drafts (Owner pastes — Mini Boss does not Send):

**VI**

> Chào iu, mã **A01** nha 💕  
> Shop order Taobao theo đúng màu/size em chọn, rồi ship US.  
> Em gửi: màu (Kem / Xanh) + size Á châu + cm + city.  
> Em chưa chốt giá/ngày nhận cho đến khi Boss mở link check **còn đúng SKU / 现货 hay 预售**.  
> Zelle khi em yes. Mini Boss không giữ hàng hộ.

**EN**

> Hi — **A01**. We order the Taobao SKU you pick, then ship US.  
> Send: color name + Asia size + cm + city.  
> Price/ETA lock only after we reopen the link (spot vs pre-sale, that color).  
> Zelle when you yes. No cart hold on the website.

Never: “còn 1 chiếc trên Square,” “ships tomorrow,” “same as the cover photo,” “US size M.”

---

## 4. Hold / quote / lead time / 现货 vs 预售

### 4.1 Three different “holds”

| Hold | Trigger | Customer sees | Staff does |
| --- | --- | --- | --- |
| **Shop Hold** | No honest USD yet (photo-check, thermos, price jump, 预售 unknown) | Badge **Hold · Inbox for price**, `priceUsd: null` | Do not type a number into `/admin` to “look finished” |
| **Customer reserve** | They asked to hold a look | Messenger: window (default treat as **24h** unless Boss yes) | Orders `Reserved`; Slack if past 24h |
| **Taobao 预售** | Seller will make / replenish after pay | Honest ETA band, not “Available on the rack” | Do not mix with shop Hold unless USD is also unknown |

Shop Hold ≠ sold out. P02 / P05 are still messageable. Copy already says “Message to buy — photo-check, no USD yet.” **Keep that pattern.** Extend it to dropship lead-time, not only thermos photo-check.

### 4.2 Quote (what “Available $25” actually is)

A listed USD on the boutique is a **target sell**, not a landed-cost invoice.

A real quote for a Taobao dropship piece is:

```text
quoted_usd ≈
    TB SKU ¥  (this 颜色 + 尺码, today)
  + CN domestic / warehouse
  + 转运 / international
  + duty + broker/line fees   ← US: de minimis for CN/HK is gone
  + last-mile
  + Boss margin
  + buffer for 色差 / size chart miss / 预售 slip
```

Intake already converts CNY↔USD for *staff* (`1 USD = 6.71 ¥` weekly label on 2026-09-07 store default). That rate is **not** a customer promise. Do not print ¥ or the FX line on the sell-site.

If any term is unknown → **Hold · Inbox for price** or a Messenger “TBD ship/duty” line. Do not average last week’s haul and invent $23 (the P05 trap).

### 4.3 现货 vs 预售 (Taobao reality)

Taobao’s buyer-facing mind is:

- **现货** — seller set a short 发货时效. Platform C-end copy treats **24h / 48h 发货** as 现货. Default tool is often **48 hours after pay**. This is **China domestic 发货**, not a US mailbox.
- **预售** — seller used 全款预售 or 分阶段预售 (定金 + 尾款). PDP shows 预售价 / 定金 / **发货时间**. OpenAPI: `deliveryTimeType` `0` = 48h, `3` = 24h, `2` = 全款预售 with `tbDeliveryTime` in **days** (dress category examples include 3, 5, 7, 10, 15, 20, 30, 45). **SKU-level** clocks exist (`deliveryTimeSetBySku` + `skuDeliveryTime`): one color can be 现货 while the color in the cover is 预售.

Official consumer terms: 发货时间 **以宝贝详情页为准** ([淘宝预售业务协议规范](https://terms.alicdn.com/legal-agreement/terms/suit_bu1_taobao/suit_bu1_taobao202012010036_72763.html)).  
Platform 发货管理: pay + **48h or the set window**; 预售 tools for longer ([淘宝网发货管理规范](https://jianghu.taobao.com/detail/47301_58664622)); OpenAPI field list ([发货合约](https://open.alitrip.com/docs/doc.htm?articleId=121094&docType=1)).

**Ops lies you will meet (do not copy them onto Messenger as fact):**

- Title says 现货, order logistics says 全款预售 15天 — reporters have documented this bait ([读特 / 腾讯 2025-02](https://news.qq.com/rain/a/20250221A098Y800)). **Chat 旺旺 + the SKU’s 发货 clock + the order page after pay** beat the title.
- Seller 客服 says 现货, factory later says 预售. Believe the **order’s** clock; tell the customer as soon as it slips.
- 现货 + 预售 in one cart ships when the *slow* SKU is ready (common shop FAQ; Reddit dump of seller paste: 现货 3–10d, 预售 45–90d, holidays excluded).
- 预售工期 **does not include 节假日 / 工厂放假**. CNY, 618, 双11, summer factory rest — add calendar, do not add vibes.

### 4.4 Lead-time stack to *say out loud* (US / Bay Area)

Never quote “Taobao 48h” as the customer ETA. Stack:

| Leg | 现货-ish | 预售-ish | Who sees it |
| --- | --- | --- | --- |
| Seller 发货 | 24–48h typical platform 现货; some shops 3–10d | PDP days (5–45+; fashion 预售 15–90d shows up in the wild) | Boss on TB |
| CN transit → warehouse | days | same after 发货 | Agent / 转运 |
| International + US last mile | often 1–3 weeks depending on line | same | Customer |
| Duty / hold | **not optional to mention** after 2025 | same | Customer |
| Bay Area pickup | skip last-mile if Boss already has the unit | n/a | Customer |

**US customs (why quotes went stale):** CBP **CSMS #64917563** — effective **2025-05-02 00:01 EDT**, products of China and Hong Kong **do not** get the 19 U.S.C. § 1321(a)(2)(C) de minimis exemption ([CBP bulletin](https://content.govdelivery.com/accounts/USDHSCBP/bulletins/3de903b); [Federal Register 2025-04-28](https://www.govinfo.gov/content/pkg/FR-2025-04-28/html/2025-07325.htm)). Agents (e.g. Superbuy notices Feb–May 2025) pre-collect duty, add courier guarantees, or push “tax-free” lines that still slip. **Do not promise duty-free $800 parcels from CN/HK.**

Messenger band language (honest, still cute):

- 现货 SKU, known line: “Order hôm nay, thường **2–4 tuần** tới US — em giữ cửa sổ, không hứa Amazon.”
- 预售 SKU: “Món này **đặt trước** bên TQ, shop họ ghi ~**N ngày** mới gửi. Cộng ship US. Em không chốt ngày lịch.”
- Unknown: “Để Boss mở link xong báo ngày. Chưa yes thì chưa Zelle.”

### 4.5 When to flip the tile to Hold

Flip **Available → Hold** (and null the USD) when any of these is true *and* Boss has not re-quoted:

- Seller 无货 / 下架 / SKU 颜色 removed.
- 预售 clock longer than what the last caption implied.
- Hub `sell_usd` empty or disagrees with the Boss table.
- Photo-check failed (thermos P02/P05 pattern).
- Two customers want the same unique look and you will not oversell.

Do **not** flip to Hold just because Square qty is 0. On this model, Square 0 is the default.

---

## 5. Catalog truth — wishlist / staged vs owned Square on-hand

### 5.1 The honesty ladder

```text
looking / candidate / watching     Wishlist     no mã, off Square
bought (GF/Boss paid, not received) Wishlist status=bought, ASK STOCK, off Square
bought + mã, Excel Official         working copy, still off Square
Lưu on intake                       status=staged, square=not_square
catalog.v1 / sell tile              available | hold, qty always 1
#shop-decisions yes + Boss Save     Square Track ON  ← only "on hand"
sold / dead                         retire mã, never reuse
```

GF intake contract ([`excel-kit/prompts/GF_CLOTHES_INTAKE.md`](../../excel-kit/prompts/GF_CLOTHES_INTAKE.md)): Wishlist is not stock. Bought without mã → ASK STOCK. Official row ≠ Save. Reply templates **forbid** “Đã lên Square” / “hàng đang bán” while staged ([`excel-kit/inbox/gf_intake_reply_templates.md`](../../excel-kit/inbox/gf_intake_reply_templates.md)).

Intake types ([`sassy-closet/lib/types.ts`](../../sassy-closet/lib/types.ts)): every Lưu row is `status: "staged"`, `square: "not_square"`. On-hand is a **separate** bag. Tìm mã card shows the amber banner when that bag is empty.

Square import law ([`excel-kit/square/README.md`](../../excel-kit/square/README.md), Boss yes 2026-09-04): Track stock ON every item **and** variation; SKU = mã; Variation = Asia size + color; no wishlist import; no Save until Slack yes.

### 5.2 What “qty = 1” means on the sell-site

`catalog.v1` hard-codes `qty: 1` for the allowlist. On a **unique boutique piece** that Boss already owns, that can mean “one body.” On a **dropship look**, it means “we sell this conversation one customer at a time.” It is **not** a Square `New Quantity`.

If two people message A01 Kem/M:

1. First Paid + TB order placed → tell the second “đang order lô này, em check lại 现货.”
2. Do not let the site keep shouting “Available” if the SKU is now 无货.
3. Do not decrement a fake warehouse.

### 5.3 What may be published vs staff-only

| Field | Hub / intake | catalog.v1 | Customer shop | Square |
| --- | --- | --- | --- | --- |
| mã | yes | allowlist only | yes | SKU if owned |
| title / description | optional; **do not invent** | empty if hub has no columns | may stay empty or Boss-written | caption draft only |
| colors as **text** | yes | `[{id, name}]` | yes (Kem, Xanh) | Variation name |
| colors as **hex** | no invent | no invent | **no** (admin boxes stay off PDP) | n/a |
| `priceUsd` | Boss table | number or `null` | $ or Inbox for price | Price if saved |
| `qty` | not stock | always 1 | “1 piece · Message” is OK if not “on hand” | counted |
| `source_link` | **required if exists** | **omit** | **omit** | omit |
| cost / FX | staff | **omit** | **omit** | Default Unit Cost optional |
| status hub `staged` | yes | **omit** (not hold\|available) | n/a | n/a |
| Square on-hand | intake `on_hand` only if real | omit | do not print | SoT |
| photos | Photos/{MA}/ | path, `colorId` if known | Blob / `/products/{MA}/` | n/a |
| customer name | Orders only, not git | omit | omit | omit |

---

## 6. `source_link` discipline (`e.tb.cn`) — never invent mã or prices

### 6.1 What a Taobao share actually is

A phone share is a **blob**, not a URL:

```text
【淘宝】https://e.tb.cn/h.7KxYzAb  HU1234 「法式碎花连衣裙…」
点击链接直接打开 或 复制这条信息￥abc123XYZ￥后打开👉淘宝👈
```

Pieces:

| Piece | Job | Store? |
| --- | --- | --- |
| `https://e.tb.cn/h.…` | Official short hop (also `tb.cn` / `m.tb.cn`) | **Yes** — this is `source_link` |
| `https://item.taobao.com/item.htm?id=` | Stable-ish item id (`num_iid`) | Yes if you already have it |
| `&skuId=` | The **color/size row** | Yes, staff notes |
| `￥…￥` 淘口令 | Clipboard token; OpenAPI `taobao.tbk.tpwd.convert` parses it | No — expires / 淘客-tainted |
| `s.click.taobao.com` | Affiliate click | Prefer item / `e.tb.cn` |
| Chinese wrapper | Noise | Strip |

OpenAPI examples treat `https://e.tb.cn/h.…` inside the share sentence as `material_url` / 口令 input ([淘宝开放平台 tpwd APIs](https://developer.alibaba.com/docs/api.htm?apiId=32932)). Short links **rot**. 淘口令 **rot**. Down-shelf items return `10000` (下架或非淘客). **Re-open before every Paid.**

### 6.2 What this repo already does (intake)

[`sassy-closet/lib/source-link.ts`](../../sassy-closet/lib/source-link.ts) + PR [#16](https://github.com/SkyLanter/Sassy-closet/pull/16):

- Extract the first HTTP URL; prefer hosts `e.tb.cn`, `tb.cn`, `taobao.com`, `tmall.com`.
- Strip trailing punctuation and glue-on Chinese (`https://e.tb.cn/h.7KxYzAb点击链接`).
- Empty / wrapper-only paste → **empty string**. Never invent a link.
- `saveFromForm` always runs `normalizeSourceLink`. Disk stores URL only.

Tests lock the real share shape ([`sassy-closet/tests/source-link.test.ts`](../../sassy-closet/tests/source-link.test.ts)). Placeholder `https://item.taobao.com/item.htm?id=PLACEHOLDER` exists only in **kit examples**, never as live stock.

### 6.3 Kit / Wishlist

`append_wishlist_row.py` **exits 2** unless `--source URL` or `--no-source`. Silent “forget the link” is forbidden. `--ma` on Wishlist is forbidden. Keep Taobao links **forever** on staff sheets (GF HOW_TO: “Có link Taobao / shop thì giữ”).

### 6.4 Never invent

| Temptation | Correct move |
| --- | --- |
| Admin tile “Next mã **A03**” | Ignore until Boss assigns. Kit exporter hard-fails extra mãs. |
| Intake empty sell → guess $22 | Leave blank. Shop must Hold. |
| P05 hub `23` | Stay Hold. Contract says so. |
| No share paste, only a pretty photo | `source_link=""`, `--no-source`, do not Google a “similar” id. |
| 淘口令 without a URL | Do not fabricate `e.tb.cn`. Ask GF/Boss to re-share. |
| Next Official `AO016` | ASK STOCK Dashboard. Scripts print that and stop. |
| Square token from another shop | Blank token on create. |

Sell catalog contract: **never** put `source_link` in `catalog.v1` ([PR #18](https://github.com/SkyLanter/Sassy-closet/pull/18) `excel-kit/docs/SELL_CATALOG_CONTRACT.md`). Customers shop a look, not a factory.

---

## 7. Per-color SKU matching — TB 颜色

Taobao does not sell “the listing.” It sells a **SKU**: sales props `颜色` × `尺码` (and sometimes 款式). OpenAPI `Sku.properties` is `p1:v1;p2:v2`; `properties_name` is the Chinese pair; `quantity` and `price` are **per SKU**; `status` is `normal | delete` ([taobao.item.sku.get](https://open.alitrip.com/docs/api.htm?apiId=38967)).

Sassy colors are **text slugs** from the hub (`kem`, `xanh`, `cham-bi`), shown as Kem / Xanh / Chấm bi. That is a **boutique word**, not a Taobao vid.

### Matching table (staff, not customer JSON)

| Boutique | Must store with the mã | Order on Taobao |
| --- | --- | --- |
| A01 · Kem | TB 颜色 string (e.g. 杏色 / 奶油白 — **whatever the SKU says**) + skuId | That skuId, not “the beige-looking one” |
| A01 · Xanh | Second SKU | Second skuId |
| A02 · Chấm bi | Pattern name as seller wrote it | That 颜色, even if English is “polka” |
| P03 · Đen / Đỏ | Two SKUs, two qty clocks | Do not ship Đỏ when they paid Đen |
| K01 · *(no colors in catalog)* | **Gap.** Do not invent hex or “Đen.” Ask Boss / reopen TB | Refuse to order “whatever is in the cover” |

Rules:

1. **One customer color → one TB `skuId`.** If you cannot name the 颜色, you cannot take Paid.
2. **Price per SKU.** 红色 may be ¥79 and 杏色 ¥89. Shop $25 is not proof.
3. **Qty per SKU.** Listing 现货 + 杏色 0 = 无货.
4. **发货 per SKU** when `deliveryTimeSetBySku=1`.
5. Intake chips (Đen, Kem, Hoa, …) are **hints**. `color_note` / pieces[] hold the messy truth. Do not overwrite a seller string with a chip.
6. Square variation, *if* the piece becomes owned: `M / kem` (Asia size + the **same** word you sold). Not US M, not a new nickname.

### Customer-facing color UX (sell-site)

Contract: **text only**. `/admin` currently: “Boxes only — no names on the swatches. Optional note is admin-only. Add hex.” That is a **staff** widget. PDP must not become a row of unnamed pink squares that do not map to skuId.

If Origin shows colors on `/m/A01`, show **Kem** and **Xanh** as words. Tag images with `colorId` only when the file is *that* SKU (see §8). Untagged gallery ≠ all colors in stock.

---

## 8. photo ≠ link (and photo ≠ SKU)

This is the boutique’s most expensive lie.

| Mismatch | How it happens | What to do |
| --- | --- | --- |
| **Cover ≠ ordered SKU** | Model wears 杏色; tile color chips include Xanh; customer wants the cover | Message: “Ảnh bìa là Kem. Xanh là ảnh 002 / swatch. Em xác nhận.” |
| **`colorId: null` on every image** | Live `catalog.v1` export: all allowlist images `colorId: null` | Origin: do not imply the gallery is every color. Staff: tag or caption. |
| **One photo, many 颜色** | Seller uses one lookbook for 8 dyes | Order from the **SKU swatch / 尺码图**, not the model |
| **色差** | Studio light vs fabric; 直播 filter | “Ảnh shop / livestream gần hơn ảnh gốc.” Offer photo-check Hold |
| **Batch drift** | 预售 cut 2 ≠ sample | Say so on 预售 quotes |
| **Placeholder / probe** | `_placeholder.jpg`, `_probe.jpg` | Skip. Never invent Blob URLs |
| **Wrong folder** | Photo of P03 sitting in A01 | Tìm mã photo-detect can attach the wrong mã — confirm link |
| **Expired short link, live photo** | `e.tb.cn` 404, tile still pretty | Hold the tile; do not take Paid |
| **Same garment, new `id=`** | Seller relists | New `source_link`; do not assume old skuId |

Intake Tìm mã keeps **code box + photo detect** ([`FIND_MA_CARD_2026-09-08.md`](../../excel-kit/prompts/FIND_MA_CARD_2026-09-08.md)). Photo detect is “this file was saved under mã X,” not “this is the Taobao 颜色.”

Sell-test static covers live at `/products/{MA}/cover.jpg`. Editorial lifestyle (`/editorial/hero.jpg`, `/editorial/ao.jpg`, …) is **mood**, never a SKU.

---

## 9. What the sell-site should show vs what Square tracks

### 9.1 Live sell-test (2026-09-09) — keep the chrome

Inspected Production HTML/CSS:

| Keep | Evidence |
| --- | --- |
| Type ramp | **Cormorant Garamond** display + **Be Vietnam Pro** UI |
| Motion | `@keyframes announce-fade`, `shimmer-slide`, `cta-flash`; ~50 `transition`, blur, gradients |
| Livestream rail | “Facebook livestream” → Page `id=61594312648057` |
| IA | `/` featured · `/c/ao` `/c/set` `/c/phu-kien` `/c/ao-khoac` `/c/toc` · PDP `/m/{MA}` |
| Commerce | **Message to buy** / **Message {mã}** · **No cart** · footer “Zelle · Message on Messenger” |
| Hold tiles | P02, P05 “Inbox for price” |
| Admin hidden | `/admin` “Test only · not in the main nav” · Storage: Vercel Blob · Catalog (10) |

Do not flatten into a sterile inventory table. Do not add Shopify checkout. Do not put intake tabs on this host.

### 9.2 What the PDP may say (dropship-honest)

**Keep structure:** mã, type, status, price or Hold, 1-piece message line, EN + VN flavor, related rails, Messenger CTA.

**Change the warehouse idioms** currently hardcoded on live PDPs:

| Live copy (2026-09-09) | Why it is false for dropship | Honest replacement (do not invent $) |
| --- | --- | --- |
| A01: “One unique top **on hand**.” / “Áo độc bản — **một chiếc đang có**.” | Implies a counted local unit | “Listed look · message to confirm color/size. We order the Taobao SKU, then ship US.” / “Món lên site để inbox. Shop order Taobao đúng màu, rồi ship US.” |
| K01: “One jacket **on hand**.” / “**một chiếc đang có**.” | Same | Same pattern; still $37 unless Boss changes the table |
| S01 / P01 family “on hand” / “đang có” | Same | Same |
| “1 piece · Message to buy. No cart.” | The “1 piece” is OK **as conversation unit** | Keep “Message to buy. No cart.” Optional: “1 conversation at a time” — not “1 in the stockroom” |

**Available** badge stays, but its meaning is §3. Optional microcopy under the badge (small, do not redesign): “Spot vs pre-sale checked in chat.” / “现货 / 预售 chốt khi inbox.”

**Never on PDP:** Square qty, storage, `e.tb.cn`, ¥ cost, US size chart, “Buy now,” invented hex, next mã.

### 9.3 What Square tracks (only)

Square is a **tiny owned closet**, not the website.

When Boss says yes on a batch:

- Item name `A01 Áo …` or Official `AO001 Áo …` — **use the mã family Stock assigned**, do not mint a third.
- Variation `M / kem` (Asia + color word).
- `Stockable=Y`, `New Quantity [Location]` = **counted** bodies. Never `No` (that disables tracking).
- Stock alert at 0 or 1.
- Wishlist / in-flight Taobao orders / “Available” tiles **stay out**.

If Square says 0 and the site says Available, **both can be correct** (dropship look). If Square says 1 and the site says Available, you may add “ready in Bay Area” **only after** Stock confirms that unit is the same color/size. Do not auto-merge.

### 9.4 Caption vs site

Intake caption footer: `Inbox mã để lấy nha 💕 Local cash/Zelle. Ship toàn US.` Owner posts that on Facebook. Site already says Zelle + Messenger. **Do not** add a second price in the caption that is not on the tile. **Do not** put the Taobao link in the caption.

---

## 10. Failure modes

### 10.1 Overselling

**How:** Two Paid on A01 Kem/M while TB 杏色 qty is 1; or site Available after 下架; or Square 1 sold twice because Excel also “had” qty 1.

**Guard:**

- Paid is a **thread + Orders row**, not a tile click.
- Re-open `source_link` + skuId **after** yes, **before** 下单.
- Second customer gets a new check, not the old “Available.”
- Unique owned unit: Square Track ON + site Hold the moment Reserved/Paid.
- Dropship look: site may stay Available only while Boss still wants conversations; flip Hold when the SKU is gone.
- Never let catalog `qty: 1` auto-decrement from Messenger (there is no cart — do not build a shadow cart).

### 10.2 Wrong color

**How:** Customer said “cái trong ảnh.” Cover is Kem. They meant Xanh. Or Boss tapped the first 颜色 on TB. Or `/admin` hex box #F5E6C8 was labeled nothing and staff assumed 杏色.

**Guard:**

- Repeat 颜色 **string + mã + size** in the yes-message.
- Ask for a screenshot of the TB SKU panel when GF sourced it.
- Tag gallery `colorId` or say “untagged photos.”
- Refuse Paid if boutique color cannot be mapped (§7).
- Returns: photo-check Hold is cheaper than a US bounce.

### 10.3 Silent admin save

This is the dropship-specific foot-gun. Live `/admin` (2026-09-09):

- **Storage: Vercel Blob** — good (durable).
- **Add item** with a grid of **Next mã** (`A03`, `Q01`, `V01`, `K02`, `P06`, `S02`, `D01`, …). New items **start on Hold** (good) but the mã is still an invent.
- Each existing card has **Save {MA}** — one click writes Blob. No `#shop-decisions`. No “this $ is the Boss table” check. No confirm.
- Titles/descriptions are free text. Live A01 EN **already** says “on hand.” Saving again **locks the lie** into Blob SoT.
- Price USD is an open input. P05 can be typed `23`.
- **Add hex** / unnamed swatches. Easy to publish a color that is not a TB SKU.
- Image URL / upload can attach a look to the wrong mã.

**Intake twin:** `Lưu & lấy mã` mints the next letter without Dashboard. Looks like success (`Saved · Đã lưu`). Still `not_square`. On Vercel **without** Blob, `/tmp` save looks identical and **dies on redeploy** (PR [#15](https://github.com/SkyLanter/Sassy-closet/pull/15)). `/admin` on intake warns; sell-test `/admin` only says “Vercel Blob” — if that line ever says otherwise, **stop adding goods**.

**Kit twin:** exporter **hard-fails** extra mãs and price drift. Admin save **does not**. Origin must add the same allowlist / Boss-table guards, or treat `/admin` as a loaded gun.

**Rules:**

1. No Save {MA} without a visible confirm: mã, $ or Hold, status.
2. Disable **Add A03** (and every Next-mã tile) until Boss pastes an assigned code. “Next unused” is not Stock.
3. Reject `$` that is not on the Boss table unless Slack yes.
4. Reject non-empty `$` on Hold.
5. Do not persist invented hex to the customer payload.
6. Agents do not click Save. Owner does. Same spirit as Square.

### 10.4 Other ways the shop lies

| Failure | Symptom | Fix |
| --- | --- | --- |
| Short link rot | 下单 404 | Re-share; Hold tile |
| 现货 bait | Title 现货, order 预售 | Tell customer; new ETA; refund path |
| Duty surprise | Customer thought $25 landed | Quote stack §4.2; CBP 2025-05-02 |
| FX drift | ¥→$ from stale 6.71 | Staff-only; weekly; not on PDP |
| Blob /tmp confusion | Export 0 after deploy | Intake README verify: Lưu → Redeploy → still there |
| Photo detect mis-file | Wrong mã card | Confirm `source_link` + folder |
| Two mã families | A01 vs AO001 in one Slack ask | Say which book |
| Official clone pointed at intake | GF form on the shop domain | `CLONE_TO_OFFICIAL.md` — new Vercel project |

---

## 11. APPLY checklist — [sassy-closet-shop.vercel.app](https://sassy-closet-shop.vercel.app)

**Owner:** Origin shop repo (not this kit).  
**Goal:** dropship-honest catalog **without** losing the pretty shop.

### 11.0 Do not touch (design + motion lock)

Tick before any CSS/JS “cleanup”:

- [ ] **Cormorant Garamond** + **Be Vietnam Pro** stay.
- [ ] Keyframes **`announce-fade`**, **`shimmer-slide`**, **`cta-flash`** stay (and the transitions / blur / gradient wash that call them).
- [ ] Editorial tiles + hero (`/editorial/*.jpg`) stay lifestyle, not SKU evidence.
- [ ] Featured collection chips (All / Tops / Sets / Accessories / Jackets / Hair) stay.
- [ ] Livestream rail + Page link stay.
- [ ] Messenger-first CTAs stay; **no cart**, no “Buy now” checkout.
- [ ] Footer **Zelle** word stays; **no** personal name / phone.
- [ ] Hold treatment (badge + “Inbox for price” + null USD) stays for P02, P05.
- [ ] `/admin` stays **out of the main nav**.
- [ ] Intake `sassy-closet.vercel.app` stays a different project.

If a change needs a calmer layout to “look more honest,” **stop**. Honesty is type on the existing cards.

### 11.1 Copy pass (PDP + cards) — warehouse language out

Live offenders to rewrite **in place** (same hierarchy, same buttons):

- [ ] `/m/A01` — remove “on hand” / “một chiếc đang có.” Keep A01, TOP, Available, **$25**, Message A01.
- [ ] `/m/A02` — same, keep **$22**.
- [ ] `/m/S01` — “One set on hand” → dropship sentence; keep **$28**.
- [ ] `/m/P01` `/m/P03` `/m/P04` — “đang có” / “on hand” out; keep $5 / $18 / $13.
- [ ] `/m/K01` — “One jacket on hand” / “một chiếc đang có” out; keep **$37**.
- [ ] `/m/H01` — same family; keep **$8**.
- [ ] `/m/P02` `/m/P05` — **keep** Hold + Inbox for price + photo-check voice. Do **not** publish 23.
- [ ] Home + `/c/*` cards: if they inherit PDP “on hand,” fix the source string once.
- [ ] Optional one-line under status (both languages): chat confirms 现货/预售 + color. No extra sections, no shipping calculator.

Suggested EN one-liner (reuse, don’t invent prices):

> Message to buy. We confirm color/size and Taobao spot vs pre-sale, then order and ship US.

Suggested VI:

> Inbox để mua. Shop xác nhận màu/size và 现货/预售, rồi order Taobao, ship US.

### 11.2 Data / catalog truth

- [ ] Import / Blob catalog stays **exactly** the 10 allowlist mãs. No A03.
- [ ] `priceUsd` matches the Boss table; Hold ⇒ `null`.
- [ ] `source_link`, cost, FX, customer names never in client JSON.
- [ ] Customer colors = **text**. No unnamed swatch-only PDP.
- [ ] Images: if `colorId` is null, do not label the gallery as that color’s proof.
- [ ] `qty: 1` must not render as “1 in warehouse.” Prefer the existing “Message to buy. No cart.”
- [ ] Titles/descriptions: empty is legal. Do not LLM-fill.

### 11.3 Admin guards (kill silent save)

- [ ] **Save {MA}** requires confirm (mã + status + $ or Hold).
- [ ] Save rejected if `$` ∉ Boss table unless a documented override flag from Slack yes (do not invent the flag in this kit).
- [ ] Save rejected if status=Hold and `$` is non-null.
- [ ] **Add item / Next mã** disabled or requires a typed **already-assigned** mã that matches `^[AQVKGBPHJSOD]\d{2,3}$` and is not on the allowlist-by-accident. Showing A03 as a friendly default is the bug.
- [ ] Persist hex only as admin-only; customer payload strips it.
- [ ] Storage line: if not Blob, banner as loud as intake’s `/tmp` warning.
- [ ] Do not add Square Save, FB Post, or “sync stock.”

### 11.4 Messenger + Page

- [ ] CTA still opens the real Page (`profile.php?id=61594312648057` / current Boss URL).
- [ ] Prefill / first-party copy may include the **mã** (already “Message A01”).
- [ ] No bot Send. Owner types.
- [ ] `#shop-decisions` still required for Square Save / hold extend / new $.

### 11.5 Verify (Origin, after copy/guards)

Exercise like a customer, then like a dangerous intern:

1. Home → A01 PDP → Message A01 → land on Page (no cart).
2. Home → P02 / P05 still Hold, no dollar.
3. `/c/ao` still two tops, same $.
4. Motion: livestream rail fade, CTA flash, hover/shimmer still fire.
5. `/admin`: try Add A03 — **must not** publish. Try Save A01 at $1 — **must not** persist. Try Save P05 at 23 — **must not** persist.
6. View-source / network: no `e.tb.cn`, no ¥ cost, no customer names.
7. Mobile + desktop: type and motion intact.

Kit-side (this repo, already): `validate_sell_catalog.py` on `out/sell-catalog.v1.json` before any re-import.

### 11.6 Out of scope for APPLY

- New Vercel official clone — [`excel-kit/docs/CLONE_TO_OFFICIAL.md`](../../excel-kit/docs/CLONE_TO_OFFICIAL.md) (PR #18).
- Intake tabs, Ask webhook, GF From GF packets.
- Square library rows.
- Inventing titles because the hub has none.

---

## 12. Staff scripts (copy-paste, Owner sends)

Placeholders only. Do not fill with invented $ or mãs.

### 12.1 First reply (look is listed)

VI: §3. EN: §3.

### 12.2 现货 confirm

> Em ơi, Boss mở link **{ma}** màu **{tb_color}** size **{asia}+{cm}**: **现货**, họ ghi gửi trong ~{n} ngày (nội địa TQ).  
> Cộng chuyển US, cửa sổ nhận khoảng **{band}**.  
> Giá chốt **${usd}** (đã nói duty/line {included\|TBD}). Yes thì Zelle, shop mới order đúng SKU.

### 12.3 预售 confirm

> Món **{ma}** màu này đang **预售** — shop TQ hẹn ~**{n} ngày** mới gửi, chưa kể ship US / ngày lễ xưởng.  
> Không hứa ngày lịch. Vẫn muốn thì em yes + Zelle, shop đặt. Không thì thôi, không giữ giá.

### 12.4 Color mismatch

> Ảnh bìa là **{cover_color}**. Em đang hỏi **{asked}**.  
> Đó là hai SKU Taobao. Em chọn một giúp iu — Boss không order “cái đẹp nhất trong ảnh.”

### 12.5 SKU gone

> Hôm nay link **{ma} / {tb_color}** hết / gỡ.  
> Site có thể còn Available vì chưa Hold. **Chưa order được.** Em muốn đổi màu hoặc để Hold inbox giá không?

### 12.6 Hold 24h

> Giữ **{ma} {color} {size}** giúp em **24h** (tới {time PT}).  
> Quá giờ Boss hỏi lại trên Slack nếu cần extend. Website không trừ kho.

---

## 13. Sources

### This shop (primary)

| Source | What it proves |
| --- | --- |
| Live sell-test 2026-09-09 | IA, copy (“on hand”), Hold P02/P05, admin Next mã A03, Blob, motion names |
| [sassy-closet.vercel.app](https://sassy-closet.vercel.app) | Intake Lưu / staged / Taobao field |
| [README.md](../../README.md) | Facebook = store; Square Free = on-hand SoT; bots draft |
| [sassy-closet/BOSS.md](../../sassy-closet/BOSS.md) + [sassy-closet/README.md](../../sassy-closet/README.md) | Staged-only banner; no Square Save; Blob or `/tmp` wipe |
| [sassy-closet/lib/source-link.ts](../../sassy-closet/lib/source-link.ts), [tests/source-link.test.ts](../../sassy-closet/tests/source-link.test.ts), [PR #16](https://github.com/SkyLanter/Sassy-closet/pull/16) | Extract `e.tb.cn` only; never invent |
| [sassy-closet/lib/types.ts](../../sassy-closet/lib/types.ts), [on-hand.ts](../../sassy-closet/lib/on-hand.ts), [store.ts](../../sassy-closet/lib/store.ts) | `staged` / `not_square`; mint-on-Lưu; on-hand separate |
| [sassy-closet/lib/captions.ts](../../sassy-closet/lib/captions.ts) | Inbox + Zelle + US ship; no TB URL |
| [sassy-closet/lib/ask-fallback.ts](../../sassy-closet/lib/ask-fallback.ts) | “staged, not Square” |
| [excel-kit/square/README.md](../../excel-kit/square/README.md) | Track ON; SKU=mã; no wishlist import |
| [excel-kit/prompts/GF_CLOTHES_INTAKE.md](../../excel-kit/prompts/GF_CLOTHES_INTAKE.md), [inbox/gf_intake_reply_templates.md](../../excel-kit/inbox/gf_intake_reply_templates.md) | Keep source forever; never claim Square |
| [excel-kit/sot/append_wishlist_row.py](../../excel-kit/sot/append_wishlist_row.py), [append_order_row.py](../../excel-kit/sot/append_order_row.py) | `--source` or `--no-source`; Orders enums; no invent mã |
| [excel-kit/schema.py](../../excel-kit/schema.py) | Official / Wishlist / Orders columns; `source` on Wishlist |
| Slack `#shop-decisions` 2026-09-04 | yes/no Save; Track ON; Facebook stays the store; hold extend |
| PR #18 `SELL_CATALOG_CONTRACT.md` / `CLONE_TO_OFFICIAL.md` / `out/sell-catalog.v1.json` | Allowlist, Hold P02/P05, omit `source_link`, `colorId: null`, qty=1 |

Granola / Notion had **no** meeting notes on this shop (Granola MCP unauthorized; Notion search empty). If Boss later records a call that changes 24h holds or the USD table, Slack yes wins until the table is rewritten.

### Taobao / platform

| Source | What it proves |
| --- | --- |
| [淘宝预售业务协议规范（消费者侧）](https://terms.alicdn.com/legal-agreement/terms/suit_bu1_taobao/suit_bu1_taobao202012010036_72763.html) | 预售 = 预售工具; 发货时间 = PDP |
| [淘宝网发货管理规范](https://jianghu.taobao.com/detail/47301_58664622) | 48h or set window; 预售 tools for longer |
| [OpenAPI 发货合约](https://open.alitrip.com/docs/doc.htm?articleId=121094&docType=1) | `deliveryTimeType` 0/2/3; **per-SKU** 预售 days |
| [taobao.item.sku.get](https://open.alitrip.com/docs/api.htm?apiId=38967) | skuId, 颜色/尺码 props, per-SKU qty/price/status |
| [taobao.tbk.tpwd.convert](https://developer.alibaba.com/docs/api.htm?apiId=32932) | 口令 / `e.tb.cn` parse; 下架 error 10000 |
| [现货 dictionary + 电商 contrast](https://contextualchinese.com/%E7%8E%B0%E8%B4%A7) | 现货 vs 预售 as buyer language |
| [读特：现货变预售](https://news.qq.com/rain/a/20250221A098Y800) | Title/客服 现货 ≠ order 预售 |
| [r/taobao seller paste](https://www.reddit.com/r/taobao/comments/o0ghiw/does_anyone_know_what_presale_means_on_taobao/) | 现货 3–10d vs 预售 45–90d; mixed carts wait |

### US ship / duty

| Source | What it proves |
| --- | --- |
| [CBP CSMS #64917563](https://content.govdelivery.com/accounts/USDHSCBP/bulletins/3de903b) | 2025-05-02: no de minimis for CN/HK products |
| [Federal Register 2025-04-28 (90 FR 80)](https://www.govinfo.gov/content/pkg/FR-2025-04-28/html/2025-07325.htm) | EO 14256 implementation; postal duty alternatives |
| Superbuy / agent notices (2025-02–05) | Lines pre-collect duty; express guarantees; “tax-free” still slips |

Duty **rates** move. Do not bake 120% or 54% into customer copy. Bake **“duty exists; we quote it.”**

---

## 14. Sibling learn tracks

This file is **07**. Sister agents (same burst) own chrome / SEO / media / Blob / Messenger / admin. Cross-links when those PRs land:

| Likely doc | Defer to them | This doc still owns |
| --- | --- | --- |
| Messenger-first commerce | Bubble UX, Page plugin | Order of confirm → TB → ship |
| Fashion PDP color/size | Swatch UI polish | skuId / 颜色 truth, photo≠link |
| Tiny boutique admin | Form layout | Silent Save + Next-mã invent |
| Next+Blob catalog | Persistence architecture | catalog.v1 omit link/cost |
| SEO / diaspora trust | Meta, reviews | Do not claim warehouse trust |
| AI product media | Image gen | Never replace a SKU photo as proof |

Kit playbook agent (`docs/ai-clothing-shop/` index) should list this file as the **dropship law**.

---

## 15. One-screen law

> Pretty site. Messenger money. Taobao SKU. Square only when we own it.  
> `e.tb.cn` on the hub, never on the tile.  
> 现货 is their 48h, not her porch.  
> If you had to invent a mã, a dollar, or a color — you are not done; you are lying.
