# How Taobao functions — Buy Research LEARN playbook

**Access / write date:** 2026-09-15 · **DRAFT ONLY** · Browse / GET research · **Never 旺旺 / cart / checkout / buy** · **Never invent ¥ or mã**

**Job:** teach Buy Research how a pasted short link becomes a readable item page, what is public vs login-gated, and which flags must fire **before** any buy brief. This file is not an order script.

**SoT for URL extract:** `sassy-closet/lib/source-link.ts` (`normalizeSourceLink`). Form-save already runs it on mint / Sửa. Buy Research does the same by hand on every paste.

**Mã source:** `uploads/live-export-latest.csv` (export dated through 2026-09-15). Live pass opened clothing **A01 / A03 / A12**, bags **B01 / B02**, jewelry **J01 / J02**, and thermos **P02** (plus **P03** only as the photo≠link / 保温杯 control). Stored `source_link` values are cited as-is.

**Prior pass (do not mix dates):** 2026-09-08 PT notes in the attached draft. Where today’s number differs, **both** dates stay in the table.

---

## Hard stops

- Never 旺旺. Never open chat. Never add to cart. Never checkout. Never buy.
- Never invent ¥. Every yen in this file is either (a) read on a cited URL this pass, (b) the export `cost_*` field, or (c) explicitly **unknown**.
- Never invent mã. Never treat export cost as “the” Taobao ask.
- Cite the **stored short URL** (`source_link`) in Excel / intake — not a reconstructed 淘口令 wrapper.
- **Flag before buy brief:** 保温杯 (or 水杯/杯子) sitting on letter **P**, and **photo≠link** (mint photos / color chips vs 主图 / review SKU).

---

## 1) Redirect chain (live 2026-09-15)

These `e.tb.cn` shares did **not** HTTP-302. They returned **200 HTML** (share / call-app page) that **embeds** the desktop item URL + numeric id.

```
Boss/GF paste  【淘宝】… https://e.tb.cn/h.…?tk=… …
        │
        ▼
normalizeSourceLink   →  URL only (see §2)
        │
        ▼
GET https://e.tb.cn/h.{code}?tk=…     HTTP 200  (not 3xx)
        │  same HTML shape on https://m.tb.cn/h.{code}
        │  apex https://tb.cn  did not resolve from this research host (NXDOMAIN)
        ▼
Embedded target:
  https://item.taobao.com/item.htm?id={itemId}&price={n}&short_name=h.{code}&…
        │
        ├─ desktop item.taobao.com?id=   → JS login wall → login.taobao.com
        ├─ h5.m.taobao.com/awp/core/detail.htm?id=  → 302 → m.intl.taobao.com/detail/detail.html?id=
        └─ research PDP (logged-out):  https://world.taobao.com/item/{itemId}.htm
```

| Hop | What happened 2026-09-15 | Use |
| --- | --- | --- |
| `e.tb.cn/h.…?tk=…` | HTTP **200** share HTML. Empty `<title>`. Embeds `item.taobao.com/item.htm?…&id=…&price=…&short_name=h.…`. Fallback mention of `http://m.tb.cn/scanError.htm`. | Resolve **item id**. Treat embedded `price=` as **share-page ask**, not automatically the world PDP ¥. |
| `m.tb.cn/h.{same code}` | Same 200 share HTML as `e.tb.cn` (probed with A01 code `h.8KCQeaHH3dz1iSl`). | `tb.cn` family still in the prefer list. |
| Apex `tb.cn` | DNS **NXDOMAIN** from this host. | Do not claim a live apex hop today. |
| `item.taobao.com/item.htm?id=` | ~5 KB JS. Sets `login.taobao.com/member/login.jhtml?redirectURL=` (desktop) or `login.m.taobao.com` (mobile UA). **No public title / ¥ / 主图.** | **Login wall.** Do not scrape CN desktop as the research PDP. |
| `h5.m.taobao.com/awp/core/detail.htm?id=` | **302** → `m.intl.taobao.com/detail/detail.html?id=`. Thin overseas shell this pass (no item ¥ in the 8 KB HTML). | Not the research PDP today. |
| `world.taobao.com/item/{id}.htm` | HTTP **200**. Truncated CN title, public **¥**, shop, og 主图, review-text SKU. Header **請登入 / 登入查看更多優惠**. Quantity stepper visible. **No selectable SKU chips.** | **Public research PDP.** |

**Short-link behavior (this pass):**

- Logged-out GET of `e.tb.cn` does **not** require a Taobao login to reveal `id=` + embedded `price=`.
- Logged-out **desktop CN item URL** does require login (wall).
- Logged-out **world.taobao** shows a public ¥ and 主图, plus **登入查看更多優惠** — so the public ¥ may still not be the logged-in / coupon ask.
- World often **hides** 现货·预售, item 包邮/运费, and 销量 totals. Mark those **unknown** unless Boss App / logged-in shot shows them.
- Share-page `price=` and world ¥ **sometimes disagree** (see A03, B01, B02, P02, P03). Cite both. Do not average. Do not invent a third number.

---

## 2) Normalize rules (code-aligned)

Mirror `sassy-closet/lib/source-link.ts`. Never store the Chinese wrapper.

1. **NBSP → space** — replace `\u00a0` then trim.
2. **Extract `http(s)`** — first match each `https?://…` token.
3. **Strip trailing punct** — drop a trailing run of `.,;:!?)\]}>` from each token (stops the URL before `。` / `点击`).
4. **Prefer shop hosts** in this order of *acceptability*: **`e.tb.cn` → `tb.cn` → `taobao.com` → `tmall.com`**. Implementation: keep URLs whose host matches that set, then take the **first remaining URL in paste order** (not a second sort among shop hosts). If none match, take the first URL. If none, **empty** — never invent a link.
5. Tests in `sassy-closet/tests/source-link.test.ts` cover `【淘宝】…点击链接…￥…淘宝` pastes, `m.tb.cn` over a snack 淘口令, and `detail.tmall.com` over `example.com`.

```
【淘宝】https://e.tb.cn/h.7KxYzAb  HU1234 「法式碎花连衣裙夏季新款」点击链接直接打开…
        →  https://e.tb.cn/h.7KxYzAb
```

---

## 3) Item page anatomy (what Buy Research reads)

| Block | CN cues (world / share) | Shop use | Public on world 2026-09-15? |
| --- | --- | --- | --- |
| Title | `<title>` / og:title, often **truncated** (`…`) | Kind guess (針織衫 / 保溫杯 / 女包 / 銀飾) | Yes, truncated |
| Breadcrumb | `首頁 > …` | Kind vs letter | Often yes (P02/P03: 廚房 → 杯子/水杯/水壺 → **保溫杯**) |
| 主图 | `og:image` (alicdn / gw.alicdn) | **photo≠link** vs `Photos/{ma}/` | Yes |
| Live ¥ | `¥ 109.00` next to title; also **登入查看更多優惠** | vs export `cost_cny` / `cost_usd` | Yes — **and** share HTML `price=` may differ |
| SKU | 顏色分類 / 主要顏色 / 尺碼 / 容量 ml / 均碼 / 商品規格 | Match chips + photo | **Review text only.** No selectable chips logged-out |
| 现货 · 预售 | 现货 / 預售 | Lead time before any brief | **Not shown** on these nine world pages → **unknown** |
| 包邮 / 运费 | 包邮 / 運費 | Landed inbound later | Header **運費立減** only. Item 包邮 **not shown** → **unknown** |
| Shop · 销量 | 店舖資訊 + 物流/服務/描述 scores; 用戶購後 / 好評率 | Thin-sample if few reviews | Shop **yes**. **销量 total not shown** — use review count, not invented 销量 |

**均碼:** none of the opened clothing PDPs printed 均碼 in public review SKU lines this pass (A01/A03/A12 showed **尺碼:S/M**). Still look for it on every clothing paste. Jewelry used **商品規格**, not 均碼. Drinkware put **ml** inside **顏色分類**.

---

## 4) Per-mã live pass (2026-09-15)

Export fields are **intake/Excel**, not Taobao. World ¥ = public PDP ask. Share `price=` = query param on the embedded `item.taobao.com` URL inside `e.tb.cn` HTML. **Do not blend.**

| mã | kind letter | short → id | Title (CN trunc, world) | Shop (logistics / 服務 / 描述) | Cat / 主图 | World ¥ | Share `price=` | Export cost | Photo vs link | Kind vs letter | Flag |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |
| **A01** | A Áo | e.tb.cn `h.8KCQeaHH3dz1iSl` → `770708953593` | 日系奶呼呼小狗針織衫… | MOGi 4.7 / 4.7 / 4.6 · 1 用戶購後 · 100% 好評 | 針織衫. 主图: lilac puppy cardigan | **109.00** | **109** | ¥90.65 / $13.51 | Match — lilac puppy knit | A = áo · OK | Hold / research only |
| **A03** | A Áo | `h.8p9N3n8BxBY4aEN` → `1055474873165` | 專櫃撤回洋派超好看白… | pakchoi品牌設計女裝 4.6 / 4.6 / 4.4 · 3 reviews | 品牌女裝 / 上衣. 主图: white lace-collar blouse | **100.00** | **72** | ¥59 / $8.79 | Match — white blouse vs 白/象牙 export | A = áo · OK | **¥ split** share 72 vs world 100 |
| **A12** | A Áo | `h.8s7QqCSbdBca1Ss` → `1019149471031` | 半芝桃 原創白色波點… | 半芝桃 4.7 / 4.7 / 4.6 · 26 reviews | 服裝內衣. 主图: white 波點 + black two-tone blouse | **128.00** | **128** | ¥103 / $15.35 | Match — 波點 blouse | A = áo · OK | — |
| **B01** | B Túi | `h.8r5CGrlgQBNFyPl` → `911830646247` | Carit Koty… | CARIT KOTY 專櫃正品女包 4.9 / 4.9 / 4.9 · reviews thin on world | 箱包皮具 → 時尚女包 → 單肩包. 主图: pink lace tote “MISS GAIL” | **899.00** | **198** | ¥174.46 / $26 | 主图 is a **pink** tote (export also lists 綠/藍) — confirm SKU vs Photos/B01/ | B = túi · OK | **¥ split** 899 vs 198; SKU chips **unknown** logged-out |
| **B02** | B Túi | `h.8quCap2qAP6bcyt` → `1058381538227` | Caidre韓系波點… | CAIDRE箱包 4.9 / 4.9 / 4.8 · 100+ reviews | 包包. 主图: blue/pink 波點 tote + charm | **179.90** | **79.9** | ¥67.10 / $10 | Match — 波點 tote | B = túi · OK | **¥ split** 179.90 vs 79.9 |
| **J01** | J Trang sức | `h.8qF251J3MmOaNhJ` → `1019720838228` | 「月光貝爾」S925… | ABAO輕珠寶 4.8 / 4.7 / 4.7 · 85 reviews | 珠寶 → 銀飾. 主图: pearl drop necklace in pink box | **150.00** | **150** | ¥114.07 / $17 | Match — S925 pearl necklace | J = trang sức · OK | — |
| **J02** | J | `h.8qFnJs3yfEE6ff8` → `1051234002002` | 一貝子白月光 純銀貝… | Mi Manchi 輕珠寶 4.8 / 4.8 / 4.8 · 25 reviews | 首飾 → 項鏈/吊墜. 主图: silver shell necklace | **188.00** | **188** | ¥154.33 / $23 | Match — 貝/shell necklace | J = trang sức · OK | — |
| **P02** | P 配件 | `h.8KU3zzXBR4OB9me` → `971820172739` | 瘋狂動物城保溫杯朱迪… | 杯比無奈 4.8 / 4.8 / 4.8 · 100+ · **99%** 好評 | **保溫杯** / 水杯. 主图: Nick 800ml 冰霸杯 + box 「800ML」 | **112.50** | **101.2** | ¥63 (CNY) | 主图 = Nick tumbler (matches this link). Export letter is still **P** | **保温杯 vs P** | Hold. Do not write a P-accessory buy brief |
| **P03** | P | `h.8KKzBinMRDOZhNO` → `979636368813` | 迪士尼聯名保溫杯高顏… | 杯比無奈 4.8 / 4.8 / 4.8 · 100+ | **保溫杯**. 主图: **Judy + Nick pair** slim bottles | **49.90** | **39.9** | ¥31 / $4.62 | **photo≠link risk** — live 主图 is Judy/Nick, not a mint Shin-chan; export chips Đen/Đỏ | **保温杯 vs P** + **photo≠link** | **Stop** before buy brief |

2026-09-08 world ¥ on P02 (**112.50**) and P03 (**49.90**) **still match** today’s world PDP. Share `price=` today is **lower** (101.2 / 39.9). A01 world ¥ **109.00** unchanged vs 2026-09-08.

### SKU evidence (review / chip text on world — not a logged-in picker)

- **A01:** `顏色分類:紫色;尺碼:M`
- **A03:** `顏色分類:白色;尺碼:S`
- **A12:** `主要顏色:白色;尺碼:M` (no 均碼 on page)
- **B01:** no review SKU line on world this pass → **unknown**
- **B02:** `顏色分類:藍色帶掛件`
- **J01:** `商品規格:S925銀 「月光貝爾」一物一證 一年售後質保`
- **J02:** no SKU line in the first review → **unknown** beyond title 純銀貝
- **P02:** `顏色分類:尼克800ml-冰霸杯-茶倉+隨機3d貼+清潔杯刷[【正版授權】]`
- **P03:** `顏色分類:尼克500ml-雙飲+贈3d貼+清潔杯刷`

现货 · 预售 · 包邮 · 销量 totals: **unknown** on all nine world pages.

---

## 5) Flag before buy brief — 保温杯 vs P, photo≠link

### 保温杯 vs letter P

`kinds.ts` letter **P** = **Phụ kiện** (accessories). Drinkware breadcrumbs on P02/P03 are **淘寶國際 → 廚房/餐飲用具 → 杯子/水杯/水壺 → 保溫杯**. That is **not** hair / 髮飾 / small accessory.

- **P02** live 主图 + SKU = **800ml** Nick ice tumbler. Letter **P** is the wrong bucket until Boss picks drinkware (**O Khác** or a new letter). Do not fold this into a soft-clothes P haul without that call.
- **P03** same shop **杯比無奈**, same **保溫杯** crumb, **500ml** Nick SKU in reviews, **Judy+Nick** 主图.

Hair control from the 2026-09-08 pass (not re-opened today): **P01** was 髮箍 / 髮飾 — letter P can be correct for **hair**. The flag is **保温杯 vs P**, not “every P is wrong.”

### photo≠link (P03)

Live 2026-09-15:

- World 主图 = Judy Hopps (pink) + Nick Wilde (cream) pair.
- Review SKU = **尼克500ml**.
- Export row: colors **Đen, Đỏ**; `photo_link` = `Documents/Sassy Closet/Photos/P03/`.

This research host **cannot open OneDrive Photos/P03/**. The 2026-09-08 pass recorded mint **Shin-chan** photos against this same id `979636368813`. **Do not invent** that those files are still Shin-chan. **Do** block a buy brief until Boss diffs `Photos/P03/` against today’s 主图 + 尼克500ml chip.

Other opened mãs: 主图 matches the live title (A01 puppy knit, A03 white blouse, A12 波點 blouse, B02 波點 tote, J01 pearl, J02 shell, P02 Nick 800ml). **B01** 主图 is the pink lace tote — confirm against `Photos/B01/` and the 綠/藍 export chips before a brief.

---

## 6) URLs + access date 2026-09-15

Always keep the **stored short link** next to the world PDP.

| mã | Stored `source_link` | World PDP |
| --- | --- | --- |
| A01 | https://e.tb.cn/h.8KCQeaHH3dz1iSl?tk=WeuOTTBXHOu | https://world.taobao.com/item/770708953593.htm |
| A03 | https://e.tb.cn/h.8p9N3n8BxBY4aEN?tk=OurQTSg7ai8 | https://world.taobao.com/item/1055474873165.htm |
| A12 | https://e.tb.cn/h.8s7QqCSbdBca1Ss?tk=2rsaT8cFgzO | https://world.taobao.com/item/1019149471031.htm |
| B01 | https://e.tb.cn/h.8r5CGrlgQBNFyPl?tk=GwTkTSie0IM | https://world.taobao.com/item/911830646247.htm |
| B02 | https://e.tb.cn/h.8quCap2qAP6bcyt?tk=SoaeTSRQbkc | https://world.taobao.com/item/1058381538227.htm |
| J01 | https://e.tb.cn/h.8qF251J3MmOaNhJ?tk=tkdtTSRpBU6 | https://world.taobao.com/item/1019720838228.htm |
| J02 | https://e.tb.cn/h.8qFnJs3yfEE6ff8?tk=mzU2TS82aJh | https://world.taobao.com/item/1051234002002.htm |
| P02 | https://e.tb.cn/h.8KU3zzXBR4OB9me?tk=kcDJT6G7z4p | https://world.taobao.com/item/971820172739.htm |
| P03 | https://e.tb.cn/h.8KKzBinMRDOZhNO?tk=nf9vThVDZ31 | https://world.taobao.com/item/979636368813.htm |

**主图 (og:image, fetched 2026-09-15):**

- A01: `https://img.alicdn.com/imgextra/O1CN01w9us091dVt0aVYofc_!!6000000003742-2-yinhe.png` (lilac puppy cardigan — filename looks generic; bytes are the knit)
- A03: `https://img.alicdn.com/imgextra/i3/3238738379/O1CN01PRacAH2BldmLpL4F2_!!3238738379.jpg`
- A12: `https://img.alicdn.com/imgextra/i3/2212735207665/O1CN01f0Fubi26UcxyLq2am~crop,0,125,750,750~_!!2212735207665.jpg`
- B01: `https://img.alicdn.com/imgextra/i4/2759324356/O1CN01K8Llru1i36JMmR0lP_!!2759324356.jpg`
- B02: `https://img.alicdn.com/imgextra/i2/645209687/O1CN01MQOPmw2LQhpuXF7eu_!!645209687.jpg`
- J01: `https://img.alicdn.com/imgextra/i4/3402360924/O1CN01qfGvgQ1IhF5SFmNMR_!!3402360924.jpg`
- J02: `https://img.alicdn.com/imgextra/i3/1726870227/O1CN012UAfrA1DY132C6BOL~crop,0,340,1500,1500~_!!1726870227.jpg`
- P02: `https://img.alicdn.com/imgextra/i3/2992346532/O1CN01piXkXV1y7iBkPVCKN_!!2992346532.jpg`
- P03: `https://img.alicdn.com/imgextra/i1/2992346532/O1CN01ERMcMh1y7iC1sOWfn_!!2992346532.jpg`

Desktop wall (A01 id, same pattern for the others): https://item.taobao.com/item.htm?id=770708953593 → login.taobao.com (fetched 2026-09-15).

---

## 7) Findings vs open questions

**Findings**

- `e.tb.cn` → item id is reliable on these nine shares. Research PDP = **world.taobao.com/item/{id}.htm**.
- Public world ¥ is real and dated. It is **not** always the share `price=` and **not** the export cost.
- Drinkware listings stay under **保溫杯**. Letter **P** is wrong for P02/P03 until Boss assigns a drinkware bucket.
- P03 still needs a photo vs 主图 check before any brief.
- 包邮 / 现货 / 销量 totals stay **unknown** on world without a Boss/app shot.

**Open (Boss — not invented here)**

1. P03 `Photos/P03/` vs live Judy/Nick 主图 + 尼克500ml (photo≠link).
2. P02/P05 letter: keep P, move to **O**, or new drinkware letter.
3. A03 / B01 / B02 / P02 / P03: which ask is the one GF paid or will pay — share `price=`, world ¥, or a logged-in coupon? **Do not pick.**
4. B01 world **¥899** vs share **198** vs export **¥174.46** — confirm SKU + 主图 color vs Photos/B01/.
5. Item-level 包邮 / 现货 / 销量 — need App or logged-in shot. Not on world today.

---

## 8) What this file is not

No 下单 steps. No cart path. No 旺旺 script. No customer ship $. No invented SKU picker. Inbound China→US ¥ lives in [`cainiao-weight-scale.md`](cainiao-weight-scale.md).

Sibling LEARN 08 (PR #26, not on `main` as of this write) is Inbox Desk + Buy Research **ops** wording. This file is the **PDP / short-link** map only.

No 旺旺 · no cart · no buy.
