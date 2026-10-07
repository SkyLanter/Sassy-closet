# Sassy Closet LEARN — Taobao deep dive (DRAFT ONLY)

**Live evidence date:** 2026-09-15  
**Mode:** LEARN / Buy Research draft · browse-only · **Never 旺旺 / cart / buy / checkout** · **No invent ¥**  
**SoT:** upload `live-export-latest.csv` (38 staged mã) · method `taobao-how-it-works.md` + `sassy-closet/lib/source-link.ts` (`normalizeSourceLink`)

Every mã below was opened the same way: stored short `source_link` → GET `e.tb.cn` share HTML (HTTP 200, JS `var url`) → numeric `id` + share `price=` → GET `https://world.taobao.com/item/{id}.htm` (HTTP 200, `__ICE_APP_CONTEXT__` / `normalItemResponse`). Desktop `item.taobao.com` login-wall and H5 `m.intl.taobao.com/detail/detail.html` shell were **not** used as buy paths. No 旺旺. No cart.

World titles stay **truncated** (`…`). SKU chips are **not selectable** logged-out (`simplifiedType: MOST_SIMPLIFIED`). Colors / sizes / 均码 below come only from public review `skuInfo` when present. 现货/预售 and domestic 运费 are **unknown** unless a review SKU literally says 現貨. `freeShipping` was **false** on all 38; the only 运费 UI on world is the login teaser **註冊運費立減**.

**Price lanes (do not invent a single true ¥):**
- Share embed `price=` — ask/promo hint at share-copy time
- World `itemPrice.promotionPrice` + `originalPrice` + remark `價格可能因優惠活動發生變化`
- Intake `cost_cny` / `cost_usd` / `cost_currency` from the export (O04 both costs blank)

**Photos:** OneDrive hub `Documents/Sassy Closet/Photos/` listed 2026-09-15 has folders only for **A01 A02 A03 B01 H01 K01 P01–P05 S01**. Later mãs have a `photo_link` path in the export but **no folder on that hub listing** — pixel photo≠link for those is **unknown**, not “mismatch.” Listing heroes were opened for A01 / B01 / K01 / P01–P05 / S01 / O04 only.

**Call default:** Hold · draft only. Never buy without Boss exact yes.

---

## Index (38) — 2026-09-15

| mã | kind | id | share ¥ | world promo ¥ | intake cost_cny / usd | shop | flags |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| **A01** | A Áo | `770708953593` | 109 | 109.00 | 90.65 / 13.51 | MOGi | ¥ vs intake, thin/unknown |
| **P01** | P Phụ kiện | `777722622771` | 5.8 | 6.00 | 7.18 / 1.07 | MichuGo飾品 | share≠world, ¥ vs intake |
| **S01** | S Set đồ | `1064756450416` | 148 | 399.00 | 114.07 / 17 | LUNAVIBE | share≠world, ¥ vs intake, thin/unknown, S vs 洋裝 |
| **P02** | P Phụ kiện | `971820172739` | 101.2 | 112.50 | 63 / 9.39 | 杯比無奈 | share≠world, ¥ vs intake, 保温杯 vs P |
| **P05** | P Phụ kiện | `979479898479` | 98.9 | 109.90 | 75 / 11.18 | 杯比無奈 | share≠world, ¥ vs intake, 保温杯 vs P |
| **P03** | P Phụ kiện | `979636368813` | 39.9 | 49.90 | 31 / 4.62 | 杯比無奈 | share≠world, ¥ vs intake, 保温杯 vs P, photo≠link |
| **P04** | P Phụ kiện | `806694443822` | 23.8 | 50.00 | 15.90 / 2.37 | 問香坊 | share≠world, ¥ vs intake |
| **K01** | K Áo khoác | `1072275004755` | 125 | 125.00 | — / 15.32 | Urcoly 饅饅家 | thin/unknown |
| **H01** | H Tóc | `682702361411` | 17.9 | 17.90 | — / 2 | 芭拉小屋 | — |
| **A02** | A Áo | `1048030091519` | 85.9 | 85.90 | 71 / — | 醬爆家 | ¥ vs intake |
| **A03** | A Áo | `1055474873165` | 72 | 100.00 | 59 / 8.79 | pakchoi品牌設計女裝 | share≠world, ¥ vs intake, thin/unknown |
| **B01** | B Túi | `911830646247` | 198 | 899.00 | 174.46 / 26 | CARIT KOTY 專櫃正品女包 | share≠world, ¥ vs intake, thin/unknown |
| **B02** | B Túi | `1058381538227` | 79.9 | 179.90 | 67.10 / 10 | CAIDRE箱包 | share≠world, ¥ vs intake |
| **J01** | J Trang sức | `1019720838228` | 150 | 150.00 | 114.07 / 17 | ABAO輕珠寶 | ¥ vs intake |
| **J02** | J Trang sức | `1051234002002` | 188 | 188.00 | 154.33 / 23 | Mi Manchi 輕珠寶 | ¥ vs intake, thin/unknown |
| **A04** | A Áo | `1043650520057` | 76 | 76.00 | 62 / 9.24 | 黑色薔薇 Costume | ¥ vs intake |
| **A05** | A Áo | `1054893415097` | 99.98 | 99.98 | 87.23 / 13 | UNCUSTOMARY旗艦店 | ¥ vs intake |
| **A06** | A Áo | `1032055577336` | 89 | 139.00 | 73.81 / 11 | 陳佳真CHENJIAZHEN | share≠world, ¥ vs intake |
| **A07** | A Áo | `1040724590755` | 49.99 | 49.99 | 87.23 / 13 | Frequency山雞 | ¥ vs intake |
| **S02** | S Set đồ | `1073269081509` | 69.8 | 69.80 | 51 / 7.60 | 蘿拉仙女生活館 | ¥ vs intake |
| **S03** | S Set đồ | `965483321452` | 78 | 608.00 | 60.39 / 9 | 覓思妍睡衣店 | share≠world, ¥ vs intake |
| **A08** | A Áo | `1067602875649` | 119.8 | 184.31 | 90 / 13.41 | 法芭菲旗艦店 | share≠world, ¥ vs intake |
| **A09** | A Áo | `1039283288293` | 98 | 98.00 | 84 / 12.52 | PinkSiren | ¥ vs intake |
| **O01** | O Khác / Other | `1050846794665` | 73.8 | 105.00 | 60 / 8.94 | 港蘊旗艦店 | share≠world, ¥ vs intake |
| **O02** | O Khác / Other | `1036949523897` | 69.8 | 99.00 | 80.52 / 12 | 港蘊旗艦店 | share≠world, ¥ vs intake |
| **D01** | D Đầm / Dress | `1046519667783` | 166 | 166.00 | 134.20 / 20 | withmin涼皮 | ¥ vs intake |
| **D02** | D Đầm / Dress | `1046521459484` | 166 | 166.00 | 131 / 19.52 | withmin涼皮 | ¥ vs intake |
| **B03** | B Túi | `1007708184718` | 279 | 279.00 | 204 / 30.40 | 迪士尼品牌正品專櫃店 | ¥ vs intake |
| **Q01** | Q Quần | `1042320874853` | 105 | 105.00 | 74.55 / 11.11 | Wuu2Sweet吳太甜 | ¥ vs intake |
| **O03** | O Khác / Other | `1028539989739` | 1.6 | 1.60 | 0.69 / 0.10 | 淼淼淼小哥 | ¥ vs intake |
| **S04** | S Set đồ | `1047301043121` | 165 | 246.00 | 140 / 20.86 | 賣衣服養你啊 | share≠world, ¥ vs intake |
| **A10** | A Áo | `989709595663` | 119 | 119.00 | 100.65 / 15 | Lukira | ¥ vs intake |
| **O05** | O Khác / Other | `1078272019049` | 39.9 | 118.00 | 42 / 6.26 | 俏繪旗艦店 | share≠world, ¥ vs intake |
| **O04** | O Khác / Other | `1077516969221` | 29.9 | 99.00 | — / — | 俏繪旗艦店 | blank cost, share≠world |
| **A11** | A Áo | `841848039676` | 109 | 129.00 | 93 / 13.86 | 表演時刻旗艦店 | share≠world, ¥ vs intake |
| **A12** | A Áo | `1019149471031` | 128 | 128.00 | 103 / 15.35 | 半芝桃 | ¥ vs intake |
| **A13** | A Áo | `988176960813` | 99 | 99.00 | 81 / 12.07 | Dreamyland | ¥ vs intake, thin/unknown |
| **D03** | D Đầm / Dress | `1060137201822` | 108 | 108.00 | 92 / 13.71 | 大霓Dani | ¥ vs intake |

---

## A01 · A Áo

**Short:** https://e.tb.cn/h.8KCQeaHH3dz1iSl?tk=WeuOTTBXHOu  
**Resolved id:** `770708953593`  
**World:** https://world.taobao.com/item/770708953593.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 日系奶呼呼小狗針織衫... |
| Meta 選購 hint | 選購日系奶呼呼小狗皮帶 |
| Breadcrumb | 首頁 |
| Share `price=` | **¥109** (embed; cite as share lane) |
| World `promotionPrice` | **¥109.00** (aligned with share this pass) |
| World `originalPrice` | ¥109.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `90.65` · cost_usd `13.51` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `S M L` · color `Kem, Xanh` · note `Tím, vàng chanh` |
| Colors / sizes / 均码 (live) | `顏色分類:紫色;尺碼:M` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **MOGi** · 廣東深圳 · 1150 items · scores 4.7/4.7/4.6 (4.7 物流服務; 4.7 服務; 4.6 商品描述) · 好評 1 · latest public review 2026.04.26 13:13: sku `顏色分類:紫色;尺碼:M` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/O1CN01w9us091dVt0aVYofc_!!6000000003742-2-yinhe.png` |
| Export photo_link | `Documents/Sassy Closet/Photos/A01/` · OneDrive Photos hub folder: yes |

**Flags**

- ¥ **drift**: share 109 ≠ intake 90.65 · world 109.00 ≠ intake 90.65 (intake cost_cny **90.65**; cost_usd **13.51** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- meta 選購 hint says **小狗皮帶** while title/hero is a **針織衫 / lilac puppy cardigan**. Treat as world SEO noise, not a new photo≠link (hero matches archive).
- photo≠link: **not newly detected** from listing hero this pass — listing hero = lilac puppy-embroidered cardigan (matches 2026-09-08 archive Y lilac knit)
- 保温杯 vs P: n/a (not a P thermos listing).
- **thin stock / unknown:** thin public 好評 (1) · item-level qty **unknown** logged-out.

**Call:** Hold · draft only · no buy.

---

## P01 · P Phụ kiện

**Short:** https://e.tb.cn/h.8LUkbrVGhE4Yurr?tk=RYgXTTzkt8b  
**Resolved id:** `777722622771`  
**World:** https://world.taobao.com/item/777722622771.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 法式復古碎花髮箍女高... |
| Meta 選購 hint | 選購法式復古碎花髮箍 |
| Breadcrumb | 首頁 › 阿裏B2C商城 › 配飾 › 首飾/飾品 › 髮飾 › 梳子 |
| Share `price=` | **¥5.8** (embed; cite as share lane) |
| World `promotionPrice` | **¥6.00** (differs from share — cite both) |
| World `originalPrice` | ¥6.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `7.18` · cost_usd `1.07` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `∅` · color `Hoa` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:咖色髮箍` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **MichuGo飾品** · 浙江金華 · 2384 items · scores 4.8/4.8/4.8 (4.8 物流服務; 4.8 服務; 4.8 商品描述) · 好評 500+ · latest public review 2026.08.03 21:10: sku `顏色分類:咖色髮箍` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i3/800470442/O1CN016AJpyl1F8U08jiMLJ_!!800470442.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/P01/` · OneDrive Photos hub folder: yes |

**Flags**

- ¥ **drift**: share 5.8 ≠ intake 7.18 · world 6.00 ≠ intake 7.18 · share 5.8 ≠ world 6.00 (intake cost_cny **7.18**; cost_usd **1.07** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **not newly detected** from listing hero this pass — listing hero = stacked floral 髮箍 (cream/pink/brown/ivory) — matches 髮箍 title + archive Y floral
- 保温杯 vs P: **no** — this P listing is not drinkware (法式復古碎花髮箍女高...).
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).

**Call:** Hold · draft only · no buy.

---

## S01 · S Set đồ

**Short:** https://e.tb.cn/h.8KBBS0G8a3NQqtg?tk=YcEnTTALzCr  
**Resolved id:** `1064756450416`  
**World:** https://world.taobao.com/item/1064756450416.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 韓系時尚設計感針織拼... |
| Meta 選購 hint | 選購韓系時尚設計感針織拼... |
| Breadcrumb | 首頁 › Hitao地圖模板 › 服飾鞋包 › 下裝pant › 牛仔褲 |
| Share `price=` | **¥148** (embed; cite as share lane) |
| World `promotionPrice` | **¥399.00** (differs from share — cite both) |
| World `originalPrice` | ¥399.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `114.07` · cost_usd `17` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `S M L XL` · color `Kem` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:洋裝;尺碼:S` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **LUNAVIBE** · 廣東深圳 · 1853 items · scores 4.8/4.8/4.7 (4.8 物流服務; 4.8 服務; 4.7 商品描述) · 好評 3 · latest public review 2026.07.26 17:41: sku `顏色分類:洋裝;尺碼:S` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i3/2216595262753/O1CN01TODkEl1WCvWO1hXR9_!!2216595262753.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/S01/` · OneDrive Photos hub folder: yes |

**Flags**

- ¥ **drift**: share 148 ≠ intake 114.07 · world 399.00 ≠ intake 114.07 · share 148 ≠ world 399.00 (intake cost_cny **114.07**; cost_usd **17** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **not newly detected** from listing hero this pass — listing hero = cream polo knit 洋裝 (bag+shoes are props). Review SKU 洋裝;S. Intake is S Set — kind vs one-piece dress, not a proven photo swap
- 保温杯 vs P: n/a (not a P thermos listing).
- **thin stock / unknown:** thin public 好評 (3) · item-level qty **unknown** logged-out.
- **kind vs listing:** intake **S Set đồ** · live title/SKU/hero read as **one 洋裝** (cream polo dress). Breadcrumb `牛仔褲` looks like world SEO noise — do not treat as pants.

**Call:** Hold · draft only · no buy.

---

## P02 · P Phụ kiện

**Short:** https://e.tb.cn/h.8KU3zzXBR4OB9me?tk=kcDJT6G7z4p  
**Resolved id:** `971820172739`  
**World:** https://world.taobao.com/item/971820172739.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 瘋狂動物城保溫杯朱迪... |
| Meta 選購 hint | 選購瘋狂動物城保溫杯朱迪... |
| Breadcrumb | 首頁 › 淘寶國際 › 廚房/餐飲用具 › 杯子/水杯/水壺 › 保溫杯 |
| Share `price=` | **¥101.2** (embed; cite as share lane) |
| World `promotionPrice` | **¥112.50** (differs from share — cite both) |
| World `originalPrice` | ¥112.50 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `63` · cost_usd `9.39` · cost_currency `CNY` |
| Intake size / color (export, not live chips) | size `∅` · color `Đỏ` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:尼克800ml-冰霸杯-茶倉+隨機3d貼+清潔杯刷[【正版授權】]` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **杯比無奈** · 浙江金華 · 169 items · scores 4.8/4.8/4.8 (4.8 物流服務; 4.8 服務; 4.8 商品描述) · 好評 100+ · latest public review 2026.08.12 14:52: sku `顏色分類:尼克800ml-冰霸杯-茶倉+隨機3d貼+清潔杯刷[【正版授權】]` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i3/2992346532/O1CN01piXkXV1y7iBkPVCKN_!!2992346532.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/P02/` · OneDrive Photos hub folder: yes |

**Flags**

- ¥ **drift**: share 101.2 ≠ intake 63 · world 112.50 ≠ intake 63 · share 101.2 ≠ world 112.50 (intake cost_cny **63**; cost_usd **9.39** CNY). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **not newly detected** from listing hero this pass — listing hero = Nick Wilde 800ml 冰霸杯 + box 8000ML/800ml Zootopia — matches archive Y Nick 800ml
- **保温杯 vs P:** title/breadcrumb is drinkware (`瘋狂動物城保溫杯朱迪...` · `首頁 › 淘寶國際 › 廚房/餐飲用具 › 杯子/水杯/水壺 › 保溫杯`). Kind letter is **P Phụ kiện**. Same 杯比無奈 shop family as P02/P03/P05 if shop matches.
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).

**Call:** Hold · draft only · no buy.

---

## P05 · P Phụ kiện

**Short:** https://e.tb.cn/h.8pbIxrTW0mbK1Wk?tk=oDgIT6GKXrw  
**Resolved id:** `979479898479`  
**World:** https://world.taobao.com/item/979479898479.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 必AINUO保溫杯可愛大容... |
| Meta 選購 hint | 選購必AINUO保溫杯可愛大容... |
| Breadcrumb | 首頁 › 淘寶國際 › 廚房/餐飲用具 › 杯子/水杯/水壺 › 保溫杯 |
| Share `price=` | **¥98.9** (embed; cite as share lane) |
| World `promotionPrice` | **¥109.90** (differs from share — cite both) |
| World `originalPrice` | ¥109.90 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `75` · cost_usd `11.18` · cost_currency `CNY` |
| Intake size / color (export, not live chips) | size `∅` · color `Hồng, Đỏ, Xanh` · note `∅` |
| Colors / sizes / 均码 (live) | SKU chips **not on world** (no review `skuInfo`) · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **杯比無奈** · 浙江金華 · 169 items · scores 4.8/4.8/4.8 (4.8 物流服務; 4.8 服務; 4.8 商品描述) · 好評 17 · latest public review 2026.05.19 08:44: sku `—` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i2/2992346532/O1CN01joQ3RW1y7iC6CdGTe_!!2992346532.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/P05/` · OneDrive Photos hub folder: yes |

**Flags**

- ¥ **drift**: share 98.9 ≠ intake 75 · world 109.90 ≠ intake 75 · share 98.9 ≠ world 109.90 (intake cost_cny **75**; cost_usd **11.18** CNY). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **not newly detected** from listing hero this pass — listing hero = My Melody / Piano 大容量 tumbler — matches archive Y Melody
- **保温杯 vs P:** title/breadcrumb is drinkware (`必AINUO保溫杯可愛大容...` · `首頁 › 淘寶國際 › 廚房/餐飲用具 › 杯子/水杯/水壺 › 保溫杯`). Kind letter is **P Phụ kiện**. Same 杯比無奈 shop family as P02/P03/P05 if shop matches.
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).

**Call:** Hold · draft only · no buy.

---

## P03 · P Phụ kiện

**Short:** https://e.tb.cn/h.8KKzBinMRDOZhNO?tk=nf9vThVDZ31  
**Resolved id:** `979636368813`  
**World:** https://world.taobao.com/item/979636368813.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 迪士尼聯名保溫杯高顏... |
| Meta 選購 hint | 選購迪士尼聯名保溫杯高顏... |
| Breadcrumb | 首頁 › 淘寶國際 › 廚房/餐飲用具 › 杯子/水杯/水壺 › 保溫杯 |
| Share `price=` | **¥39.9** (embed; cite as share lane) |
| World `promotionPrice` | **¥49.90** (differs from share — cite both) |
| World `originalPrice` | ¥49.90 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `31` · cost_usd `4.62` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `∅` · color `Đen, Đỏ` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:尼克500ml-雙飲+贈3d貼+清潔杯刷` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **杯比無奈** · 浙江金華 · 169 items · scores 4.8/4.8/4.8 (4.8 物流服務; 4.8 服務; 4.8 商品描述) · 好評 100+ · latest public review 2026.07.20 07:46: sku `顏色分類:尼克500ml-雙飲+贈3d貼+清潔杯刷` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i1/2992346532/O1CN01ERMcMh1y7iC1sOWfn_!!2992346532.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/P03/` · OneDrive Photos hub folder: yes |

**Flags**

- ¥ **drift**: share 39.9 ≠ intake 31 · world 49.90 ≠ intake 31 · share 39.9 ≠ world 49.90 (intake cost_cny **31**; cost_usd **4.62** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- **photo≠link (detectable):** live listing hero is Judy/Nick 保温杯; 2026-09-08 playbook archive flagged Photos/P03 as Shin-chan vs Nick 500ml. Photos/P03 still has `001.jpg` `002.jpg` `003.jpg` on OneDrive (binaries not re-opened this pass). Treat as **still flagged** until Boss eyes the three Photos against this Judy/Nick PDP.
- **保温杯 vs P:** title/breadcrumb is drinkware (`迪士尼聯名保溫杯高顏...` · `首頁 › 淘寶國際 › 廚房/餐飲用具 › 杯子/水杯/水壺 › 保溫杯`). Kind letter is **P Phụ kiện**. Shop **杯比無奈** — same as P02/P05.
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).

**Call:** Hold · draft only · no buy.

---

## P04 · P Phụ kiện

**Short:** https://e.tb.cn/h.8LYfu0T52xNPoOD?tk=sfeoT6uLsAa  
**Resolved id:** `806694443822`  
**World:** https://world.taobao.com/item/806694443822.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 甜美蝴蝶結草莓八角貝... |
| Meta 選購 hint | 選購甜美蝴蝶結草莓八角貝... |
| Breadcrumb | 首頁 › 淘寶國際 › 服飾配件/皮帶/帽子/圍巾 › 所有女士帽子 |
| Share `price=` | **¥23.8** (embed; cite as share lane) |
| World `promotionPrice` | **¥50.00** (differs from share — cite both) |
| World `originalPrice` | ¥50.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `15.90` · cost_usd `2.37` · cost_currency `CNY` |
| Intake size / color (export, not live chips) | size `∅` · color `Kem` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:米白色;尺碼:M（56-58cm）` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **問香坊** · 浙江杭州 · 9283 items · scores 4.8/4.8/4.7 (4.8 物流服務; 4.8 服務; 4.7 商品描述) · 好評 200+ · latest public review 2026.09.11 17:46: sku `顏色分類:米白色;尺碼:M（56-58cm）` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i1/172619986/O1CN010KSlqk2Nde4wrX3Kq_!!0-item_pic.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/P04/` · OneDrive Photos hub folder: yes |

**Flags**

- ¥ **drift**: share 23.8 ≠ intake 15.90 · world 50.00 ≠ intake 15.90 · share 23.8 ≠ world 50.00 (intake cost_cny **15.90**; cost_usd **2.37** CNY). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **not newly detected** from listing hero this pass — listing hero = cream strawberry/bow bucket hat — matches intake Kem + 帽子 breadcrumb
- 保温杯 vs P: **no** — this P listing is not drinkware (甜美蝴蝶結草莓八角貝...).
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).

**Call:** Hold · draft only · no buy.

---

## K01 · K Áo khoác

**Short:** https://e.tb.cn/h.8LLjHT2R8bUOvIz?tk=cgigThRIuvf  
**Resolved id:** `1072275004755`  
**World:** https://world.taobao.com/item/1072275004755.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 黃色小狗刺繡卡通毛衣... |
| Meta 選購 hint | 選購黃色小狗刺繡卡通毛衣... |
| Breadcrumb | 首頁 › 儷人購 › 天貓奢品直營 › 女裝 › 毛衣 |
| Share `price=` | **¥125** (embed; cite as share lane) |
| World `promotionPrice` | **¥125.00** (aligned with share this pass) |
| World `originalPrice` | ¥125.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `∅` · cost_usd `15.32` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `S M L` · color `∅` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:黃色;尺碼:S` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **Urcoly 饅饅家** · 廣東廣州 · 1179 items · scores 4.8/4.8/4.8 (4.8 物流服務; 4.8 服務; 4.8 商品描述) · 好評 5 · latest public review 2026.08.06 18:12: sku `顏色分類:黃色;尺碼:S` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i1/1951029552/O1CN01vHH6lYKuUrB2vH2e_!!1951029552.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/K01/` · OneDrive Photos hub folder: yes |

**Flags**

- intake `cost_cny` **blank** · `cost_usd`=15.32 USD — CNY drift **unknown** (no invented FX)
- photo≠link: **not newly detected** from listing hero this pass — listing hero = yellow zip puppy cardigan (毛衣/外套). K Áo khoác is plausible; title/breadcrumb = 毛衣 not heavy coat
- 保温杯 vs P: n/a (not a P thermos listing).
- **thin stock / unknown:** thin public 好評 (5) · item-level qty **unknown** logged-out.
- kind vs listing: intake **K Áo khoác** · live **黃色小狗…毛衣** zip cardigan. Plausible as light jacket; not a coat. `cost_cny` blank.

**Call:** Hold · draft only · no buy.

---

## H01 · H Tóc

**Short:** https://e.tb.cn/h.8KE7trcDe92yo2O?tk=fkqzThRw8Yn  
**Resolved id:** `682702361411`  
**World:** https://world.taobao.com/item/682702361411.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 韓國兒童布藝雙色蝴蝶... |
| Meta 選購 hint | 選購韓國兒童布藝雙色蝴蝶... |
| Breadcrumb | 首頁 › 儷人購 › TIMEI › 嬰孩 › 兒童配飾 |
| Share `price=` | **¥17.9** (embed; cite as share lane) |
| World `promotionPrice` | **¥17.90** (aligned with share this pass) |
| World `originalPrice` | ¥17.90 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `∅` · cost_usd `2` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `∅` · color `∅` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:酒紅色[蝴蝶結髮夾]` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** at item level. The word 現貨 appears only in a related-article title (`12 歲女孩韓系穿搭尺碼對照表與現貨挑選攻略…`) — **not** this SKU. No 预售 on the PDP. |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **芭拉小屋** · 江蘇徐州 · 735 items · scores 4.9/4.9/4.9 (4.9 物流服務; 4.9 服務; 4.9 商品描述) · 好評 600+ · latest public review 2026.06.30 16:08: sku `顏色分類:酒紅色[蝴蝶結髮夾]` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i2/1816813907/O1CN01NZTeKr1ejSCoSUhzQ_!!1816813907.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/H01/` · OneDrive Photos hub folder: yes |

**Flags**

- intake `cost_cny` **blank** · `cost_usd`=2 USD — CNY drift **unknown** (no invented FX)
- photo≠link: **unknown / not pixel-compared** this pass (folder exists on OneDrive hub; listing hero not opened).
- 保温杯 vs P: n/a (not a P thermos listing).
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).

**Call:** Hold · draft only · no buy.

---

## A02 · A Áo

**Short:** https://e.tb.cn/h.8JSyU68ajHWyf52?tk=rSynThj54Ks  
**Resolved id:** `1048030091519`  
**World:** https://world.taobao.com/item/1048030091519.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 高級感復古波點撞色娃... |
| Meta 選購 hint | 選購高級感復古波點撞色娃... |
| Breadcrumb | 首頁 › 導航平臺 › 拍賣會（舊前臺） › 奢侈品 › 男裝 |
| Share `price=` | **¥85.9** (embed; cite as share lane) |
| World `promotionPrice` | **¥85.90** (aligned with share this pass) |
| World `originalPrice` | ¥85.90 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `71` · cost_usd `∅` · cost_currency `CNY` |
| Intake size / color (export, not live chips) | size `S M L XL` · color `∅` · note `Chấm bi` |
| Colors / sizes / 均码 (live) | `顏色:米白色;尺碼:L` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **醬爆家** · 廣東深圳 · 3849 items · scores 4.8/4.8/4.8 (4.8 物流服務; 4.8 服務; 4.8 商品描述) · 好評 13 · latest public review 2026.05.21 23:53: sku `顏色:米白色;尺碼:L` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i2/2438225909/O1CN01Abt5DP1tWNUWszkN0_!!2438225909.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/A02/` · OneDrive Photos hub folder: yes |

**Flags**

- ¥ **drift**: share 85.9 ≠ intake 71 · world 85.90 ≠ intake 71 (intake cost_cny **71**; cost_usd blank · cost_currency CNY). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown / not pixel-compared** this pass (folder exists on OneDrive hub; listing hero not opened).
- 保温杯 vs P: n/a (not a P thermos listing).
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).
- breadcrumb ends **男裝** — treat as world SEO noise unless Boss sees menswear on the PDP gallery (hero not opened).

**Call:** Hold · draft only · no buy.

---

## A03 · A Áo

**Short:** https://e.tb.cn/h.8p9N3n8BxBY4aEN?tk=OurQTSg7ai8  
**Resolved id:** `1055474873165`  
**World:** https://world.taobao.com/item/1055474873165.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 專櫃撤回洋派超好看白... |
| Meta 選購 hint | 選購專櫃撤回洋派超好看白... |
| Breadcrumb | 首頁 › 品牌女裝 › 2016當季新品 › 天貓獨家首發 |
| Share `price=` | **¥72** (embed; cite as share lane) |
| World `promotionPrice` | **¥100.00** (differs from share — cite both) |
| World `originalPrice` | ¥100.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `59` · cost_usd `8.79` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `L S M XL` · color `Trắng ngà` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:白色;尺碼:S` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **pakchoi品牌設計女裝** · 北京 · 1455 items · scores 4.6/4.6/4.4 (4.6 物流服務; 4.6 服務; 4.4 商品描述) · 好評 3 · latest public review 2026.06.02 14:55: sku `顏色分類:白色;尺碼:S` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i3/3238738379/O1CN01PRacAH2BldmLpL4F2_!!3238738379.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/A03/` · OneDrive Photos hub folder: yes |

**Flags**

- ¥ **drift**: share 72 ≠ intake 59 · world 100.00 ≠ intake 59 · share 72 ≠ world 100.00 (intake cost_cny **59**; cost_usd **8.79** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown / not pixel-compared** this pass (folder exists on OneDrive hub; listing hero not opened).
- 保温杯 vs P: n/a (not a P thermos listing).
- **thin stock / unknown:** thin public 好評 (3) · item-level qty **unknown** logged-out.

**Call:** Hold · draft only · no buy.

---

## B01 · B Túi

**Short:** https://e.tb.cn/h.8r5CGrlgQBNFyPl?tk=GwTkTSie0IM  
**Resolved id:** `911830646247`  
**World:** https://world.taobao.com/item/911830646247.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | Carit Koty... |
| Meta 選購 hint | 選購高級感牛仔帆布單肩包 |
| Breadcrumb | 首頁 › 阿裏B2C商城 › 箱包皮具 › 時尚女包 › 單肩包 |
| Share `price=` | **¥198** (embed; cite as share lane) |
| World `promotionPrice` | **¥899.00** (differs from share — cite both) |
| World `originalPrice` | ¥899.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `174.46` · cost_usd `26` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `∅` · color `Hồng, Xanh` · note `∅` |
| Colors / sizes / 均码 (live) | SKU chips **not on world** (no review `skuInfo`) · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **CARIT KOTY 專櫃正品女包** · 廣東廣州 · 1523 items · scores 4.9/4.9/4.9 (4.9 物流服務; 4.9 服務; 4.9 商品描述) · 好評 unknown (ICE `goodCount` empty) |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i4/2759324356/O1CN01K8Llru1i36JMmR0lP_!!2759324356.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/B01/` · OneDrive Photos hub folder: yes |

**Flags**

- ¥ **drift**: share 198 ≠ intake 174.46 · world 899.00 ≠ intake 174.46 · share 198 ≠ world 899.00 (intake cost_cny **174.46**; cost_usd **26** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **not newly detected** from listing hero this pass — listing hero = pink lace-rim MISS GIRL tote, watermark CARITKOTY — matches archive ≈ lace tote
- 保温杯 vs P: n/a (not a P thermos listing).
- **thin stock / unknown:** 好評 count hidden on world · no public reviews/SKU on world · rateList empty · meta omits 好評率 · item-level qty **unknown** logged-out.

**Call:** Hold · draft only · no buy.

---

## B02 · B Túi

**Short:** https://e.tb.cn/h.8quCap2qAP6bcyt?tk=SoaeTSRQbkc  
**Resolved id:** `1058381538227`  
**World:** https://world.taobao.com/item/1058381538227.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | Caidre韓系波點... |
| Meta 選購 hint | 選購Caidre韓系波點... |
| Breadcrumb | 首頁 › 導航平臺 › 拍賣會（舊前臺） › 奢侈品 › 包包 |
| Share `price=` | **¥79.9** (embed; cite as share lane) |
| World `promotionPrice` | **¥179.90** (differs from share — cite both) |
| World `originalPrice` | ¥179.90 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `67.10` · cost_usd `10` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `∅` · color `Xanh, Đen, Tím, Vàng chanh` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:藍色帶掛件` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **CAIDRE箱包** · 河北保定 · 762 items · scores 4.9/4.9/4.8 (4.9 物流服務; 4.9 服務; 4.8 商品描述) · 好評 100+ · latest public review 2026.07.28 21:43: sku `顏色分類:藍色帶掛件` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i2/645209687/O1CN01MQOPmw2LQhpuXF7eu_!!645209687.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/B02/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 79.9 ≠ intake 67.10 · world 179.90 ≠ intake 67.10 · share 79.9 ≠ world 179.90 (intake cost_cny **67.10**; cost_usd **10** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).

**Call:** Hold · draft only · no buy.

---

## J01 · J Trang sức

**Short:** https://e.tb.cn/h.8qF251J3MmOaNhJ?tk=tkdtTSRpBU6  
**Resolved id:** `1019720838228`  
**World:** https://world.taobao.com/item/1019720838228.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 「月光貝爾」S925... |
| Meta 選購 hint | 選購「月光貝爾」S925... |
| Breadcrumb | 首頁 › 喵街 › 喵街類目管理 › 珠寶/鑽石/翡翠/黃金 › 銀飾 |
| Share `price=` | **¥150** (embed; cite as share lane) |
| World `promotionPrice` | **¥150.00** (aligned with share this pass) |
| World `originalPrice` | ¥150.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `114.07` · cost_usd `17` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `∅` · color `∅` · note `∅` |
| Colors / sizes / 均码 (live) | `商品規格:S925銀 「月光貝爾」一物一證 一年售後質保` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **ABAO輕珠寶** · 廣東廣州 · 376 items · scores 4.8/4.7/4.7 (4.8 物流服務; 4.7 服務; 4.7 商品描述) · 好評 85 · latest public review 2026.05.16 09:55: sku `商品規格:S925銀 「月光貝爾」一物一證 一年售後質保` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i4/3402360924/O1CN01qfGvgQ1IhF5SFmNMR_!!3402360924.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/J01/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 150 ≠ intake 114.07 · world 150.00 ≠ intake 114.07 (intake cost_cny **114.07**; cost_usd **17** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).

**Call:** Hold · draft only · no buy.

---

## J02 · J Trang sức

**Short:** https://e.tb.cn/h.8qFnJs3yfEE6ff8?tk=mzU2TS82aJh  
**Resolved id:** `1051234002002`  
**World:** https://world.taobao.com/item/1051234002002.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 一貝子白月光 純銀貝... |
| Meta 選購 hint | 選購一貝子白月光 純銀貝... |
| Breadcrumb | 首頁 › 阿裏B2C商城 › 配飾 › 首飾/飾品 › 項鏈/吊墜 › 長項鏈 |
| Share `price=` | **¥188** (embed; cite as share lane) |
| World `promotionPrice` | **¥188.00** (aligned with share this pass) |
| World `originalPrice` | ¥188.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `154.33` · cost_usd `23` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `∅` · color `∅` · note `∅` |
| Colors / sizes / 均码 (live) | SKU chips **not on world** (no review `skuInfo`) · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **Mi Manchi 輕珠寶** · 廣東廣州 · 45 items · scores 4.8/4.8/4.8 (4.8 物流服務; 4.8 服務; 4.8 商品描述) · 好評 25 · latest public review 2026.05.22 14:44: sku `—` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i3/1726870227/O1CN012UAfrA1DY132C6BOL~crop,0,340,1500,1500~_!!1726870227.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/J02/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 188 ≠ intake 154.33 · world 188.00 ≠ intake 154.33 (intake cost_cny **154.33**; cost_usd **23** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- **thin stock / unknown:** shop only 45 items · item-level qty **unknown** logged-out.

**Call:** Hold · draft only · no buy.

---

## A04 · A Áo

**Short:** https://e.tb.cn/h.8pMgHxYEOig5Xdo?tk=jEbnTS8lCK7  
**Resolved id:** `1043650520057`  
**World:** https://world.taobao.com/item/1043650520057.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 法式蕾絲拼接鏤空高級... |
| Meta 選購 hint | 選購法式蕾絲拼接鏤空高級... |
| Breadcrumb | 首頁 › 品牌女裝 › 設計師原創品牌 › 原創針織衫 |
| Share `price=` | **¥76** (embed; cite as share lane) |
| World `promotionPrice` | **¥76.00** (aligned with share this pass) |
| World `originalPrice` | ¥76.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `62` · cost_usd `9.24` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `S M L` · color `Xanh mint` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:綠色;尺碼:S` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **黑色薔薇 Costume** · 廣東廣州 · 664 items · scores 4.7/4.7/4.7 (4.7 物流服務; 4.7 服務; 4.7 商品描述) · 好評 400+ · latest public review 2026.05.21 16:19: sku `顏色分類:綠色;尺碼:S` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i1/2200807684655/O1CN01xIneRT1kG2ouPjgWh~crop,0,166,900,900~_!!2200807684655.png` |
| Export photo_link | `Documents/Sassy Closet/Photos/A04/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 76 ≠ intake 62 · world 76.00 ≠ intake 62 (intake cost_cny **62**; cost_usd **9.24** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).

**Call:** Hold · draft only · no buy.

---

## A05 · A Áo

**Short:** https://e.tb.cn/h.8JXt41uotVLo8QE?tk=TH75TSI5UeF  
**Resolved id:** `1054893415097`  
**World:** https://world.taobao.com/item/1054893415097.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `tmall`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 辣妹風絕美蕾絲一字肩... |
| Meta 選購 hint | 選購辣妹風絕美蕾絲一字肩... |
| Breadcrumb | 首頁 › 儷人購 › 特賣匯 › 女款背心 |
| Share `price=` | **¥99.98** (embed; cite as share lane) |
| World `promotionPrice` | **¥99.98** (aligned with share this pass) |
| World `originalPrice` | ¥99.98 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `87.23` · cost_usd `13` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `S M L` · color `∅` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:杏色[帶胸墊];尺碼:S` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **UNCUSTOMARY旗艦店** · 廣東廣州 · 1363 items · scores 4.9/4.9/4.8 (4.9 物流服務; 4.9 服務; 4.8 商品描述) · 好評 unknown (ICE `goodCount` empty) · latest public review 2026.06.24 16:14: sku `顏色分類:杏色[帶胸墊];尺碼:S` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i3/2218664159104/O1CN01aFp1n32H7gvZFh6Ub_!!4611686018427381632-2-item_pic.png` |
| Export photo_link | `Documents/Sassy Closet/Photos/A05/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 99.98 ≠ intake 87.23 · world 99.98 ≠ intake 87.23 (intake cost_cny **87.23**; cost_usd **13** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- **thin stock / unknown:** 好評 count hidden on world · item-level qty **unknown** logged-out.

**Call:** Hold · draft only · no buy.

---

## A06 · A Áo

**Short:** https://e.tb.cn/h.8pDrLlO8XQcAbFi?tk=xJw9TSIv3GK  
**Resolved id:** `1032055577336`  
**World:** https://world.taobao.com/item/1032055577336.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 法式純欲掛頸蕾絲上衣... |
| Meta 選購 hint | 選購法式純欲掛頸蕾絲上衣... |
| Breadcrumb | 首頁 › 儷人購 › 特賣匯 › 女款背心 |
| Share `price=` | **¥89** (embed; cite as share lane) |
| World `promotionPrice` | **¥139.00** (differs from share — cite both) |
| World `originalPrice` | ¥139.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `73.81` · cost_usd `11` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `L S M` · color `∅` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:第一批;尺碼:S` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **陳佳真CHENJIAZHEN** · 廣東廣州 · 4043 items · scores 4.6/4.5/4.4 (4.6 物流服務; 4.5 服務; 4.4 商品描述) · 好評 39 · latest public review 2026.03.20 16:46: sku `顏色分類:第一批;尺碼:S` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i1/2358108080/O1CN01G8DuhY29YhL6Q0Pn4_!!2358108080.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/A06/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 89 ≠ intake 73.81 · world 139.00 ≠ intake 73.81 · share 89 ≠ world 139.00 (intake cost_cny **73.81**; cost_usd **11** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).

**Call:** Hold · draft only · no buy.

---

## A07 · A Áo

**Short:** https://e.tb.cn/h.8JV8U1dMsYoj38U?tk=4Y4JTSFY9yE  
**Resolved id:** `1040724590755`  
**World:** https://world.taobao.com/item/1040724590755.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | Frequency山... |
| Meta 選購 hint | 選購Frequency山... |
| Breadcrumb | 首頁 › 儷人購 › 特賣匯 › 女款背心 |
| Share `price=` | **¥49.99** (embed; cite as share lane) |
| World `promotionPrice` | **¥49.99** (aligned with share this pass) |
| World `originalPrice` | ¥49.99 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `87.23` · cost_usd `13` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `S M L` · color `∅` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:圖片色【常規版】;尺碼:S` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **Frequency山雞** · 北京 · 1462 items · scores 4.6/4.5/4.4 (4.6 物流服務; 4.5 服務; 4.4 商品描述) · 好評 8 · latest public review 2026.04.13 15:08: sku `顏色分類:圖片色【常規版】;尺碼:S` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i3/3916866234/O1CN01XSHI4A1vvECtjMcOi~crop,0,125,750,750~_!!3916866234.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/A07/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift (reverse):** intake cost_cny **87.23** is **above** live share=world **49.99** (cost_usd **13** USD). Still not a payable ¥ — just note the inversion vs usual share/world ≥ intake.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- **thin stock / unknown:** thin public 好評 (8) · item-level qty **unknown** logged-out.

**Call:** Hold · draft only · no buy.

---

## S02 · S Set đồ

**Short:** https://e.tb.cn/h.8pA8S04XNP5rz4Z?tk=g9gdTSFBZA5  
**Resolved id:** `1073269081509`  
**World:** https://world.taobao.com/item/1073269081509.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 卡通貓咪印花長袖睡衣... |
| Meta 選購 hint | 選購卡通貓咪印花長袖睡衣... |
| Breadcrumb | 首頁 › 淘寶國際 › 女士內衣/男士內衣/家居服 › 珊瑚絨睡衣 |
| Share `price=` | **¥69.8** (embed; cite as share lane) |
| World `promotionPrice` | **¥69.80** (aligned with share this pass) |
| World `originalPrice` | ¥69.80 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `51` · cost_usd `7.60` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `M L XL 2XL` · color `∅` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:QKM-T0061-1#[帶胸墊];尺碼:M【建議80-100斤】` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **蘿拉仙女生活館** · 廣東揭陽 · 1940 items · scores 4.8/4.8/4.8 (4.8 物流服務; 4.8 服務; 4.8 商品描述) · 好評 9 · latest public review 2026.08.17 21:09: sku `顏色分類:QKM-T0061-1#[帶胸墊];尺碼:M【建議80-100斤】` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i2/2260173746/O1CN01UXcpC8HiDfE68fzM_!!2260173746.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/S02/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 69.8 ≠ intake 51 · world 69.80 ≠ intake 51 (intake cost_cny **51**; cost_usd **7.60** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- **thin stock / unknown:** thin public 好評 (9) · item-level qty **unknown** logged-out.

**Call:** Hold · draft only · no buy.

---

## S03 · S Set đồ

**Short:** https://e.tb.cn/h.8rIIIbpFLPkqdC1?tk=UeV1TSvJnCl  
**Resolved id:** `965483321452`  
**World:** https://world.taobao.com/item/965483321452.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 【萌寵樂園】可愛卡通... |
| Meta 選購 hint | 選購【萌寵樂園】可愛卡通... |
| Breadcrumb | 首頁 › 淘寶國際 › 女士內衣/男士內衣/家居服 › 珊瑚絨睡衣 |
| Share `price=` | **¥78** (embed; cite as share lane) |
| World `promotionPrice` | **¥608.00** (differs from share — cite both) |
| World `originalPrice` | ¥608.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `60.39` · cost_usd `9` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `M L XL` · color `∅` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:萌寵樂園【帶胸墊】;尺碼:M女【推薦80-100斤】` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **覓思妍睡衣店** · 北京 · 3804 items · scores 4.8/4.8/4.8 (4.8 物流服務; 4.8 服務; 4.8 商品描述) · 好評 800+ · latest public review 2026.08.26 21:23: sku `顏色分類:萌寵樂園【帶胸墊】;尺碼:M女【推薦80-100斤】` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i4/2208176878869/O1CN01OOs8el2FO3n45e3uk_!!2208176878869.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/S03/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 78 ≠ intake 60.39 · world 608.00 ≠ intake 60.39 · share 78 ≠ world 608.00 (intake cost_cny **60.39**; cost_usd **9** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).

**Call:** Hold · draft only · no buy.

---

## A08 · A Áo

**Short:** https://e.tb.cn/h.8qA0Ix8x9kQ7yz2?tk=B96LT7EXFAn  
**Resolved id:** `1067602875649`  
**World:** https://world.taobao.com/item/1067602875649.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `tmall`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 浪漫柔系蕾絲拼接緞面... |
| Meta 選購 hint | 選購浪漫柔系蕾絲拼接緞面... |
| Breadcrumb | 首頁 › 天貓國際 › 女裝 › 蕾絲衫/雪紡衫 |
| Share `price=` | **¥119.8** (embed; cite as share lane) |
| World `promotionPrice` | **¥184.31** (differs from share — cite both) |
| World `originalPrice` | ¥184.31 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `90` · cost_usd `13.41` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `S M L` · color `∅` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:米白色上衣;尺碼:S` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **法芭菲旗艦店** · 廣東廣州 · 13684 items · scores 4.7/4.6/4.6 (4.7 物流服務; 4.6 服務; 4.6 商品描述) · 好評 unknown (ICE `goodCount` empty) · latest public review 2026.08.22 14:37: sku `顏色分類:米白色上衣;尺碼:S` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i3/2207389132035/O1CN01SzOVmD8D1JI1chua_!!4611686018427380995-2-item_pic.png` |
| Export photo_link | `Documents/Sassy Closet/Photos/A08/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 119.8 ≠ intake 90 · world 184.31 ≠ intake 90 · share 119.8 ≠ world 184.31 (intake cost_cny **90**; cost_usd **13.41** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- **thin stock / unknown:** 好評 count hidden on world · item-level qty **unknown** logged-out.

**Call:** Hold · draft only · no buy.

---

## A09 · A Áo

**Short:** https://e.tb.cn/h.8qANGt2F2USMG7z?tk=3CgqT7EpBk4  
**Resolved id:** `1039283288293`  
**World:** https://world.taobao.com/item/1039283288293.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 歐美辣妹風V領蕾絲花... |
| Meta 選購 hint | 選購歐美辣妹風V領蕾絲花... |
| Breadcrumb | 首頁 › 喵街前臺類目 › 女裝 › 上衣 › 真絲上衣 |
| Share `price=` | **¥98** (embed; cite as share lane) |
| World `promotionPrice` | **¥98.00** (aligned with share this pass) |
| World `originalPrice` | ¥98.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `84` · cost_usd `12.52` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `S M L` · color `∅` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:白色;尺碼:S` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **PinkSiren** · 廣東惠州 · 1072 items · scores 4.7/4.7/4.6 (4.7 物流服務; 4.7 服務; 4.6 商品描述) · 好評 64 · latest public review 2026.04.09 07:39: sku `顏色分類:白色;尺碼:S` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i4/2610050383/O1CN012g9Vbn1EhSp4rBgif~crop,0,450,1350,1350~_!!2610050383.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/A09/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 98 ≠ intake 84 · world 98.00 ≠ intake 84 (intake cost_cny **84**; cost_usd **12.52** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).

**Call:** Hold · draft only · no buy.

---

## O01 · O Khác / Other

**Short:** https://e.tb.cn/h.8IGMPH4b1AOyk5s?tk=IBGbT7ywLKI  
**Resolved id:** `1050846794665`  
**World:** https://world.taobao.com/item/1050846794665.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `tmall`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 法式仙女風蝴蝶結波點... |
| Meta 選購 hint | 選購法式波點高跟一字拖 |
| Breadcrumb | 首頁 › 儷人購 › 天貓奢品直營 › 女鞋 › 拖鞋 |
| Share `price=` | **¥73.8** (embed; cite as share lane) |
| World `promotionPrice` | **¥105.00** (differs from share — cite both) |
| World `originalPrice` | ¥105.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `60` · cost_usd `8.94` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `∅` · color `Trắng, Hồng` · note `Bi trắng và hòng Size 36-39` |
| Colors / sizes / 均码 (live) | `顏色分類:波點;尺碼:36` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **港蘊旗艦店** · 浙江臺州 · 515 items · scores 4.8/4.8/4.8 (4.8 物流服務; 4.8 服務; 4.8 商品描述) · 好評 unknown (ICE `goodCount` empty) · latest public review 2026.05.31 13:27: sku `顏色分類:波點;尺碼:36` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i4/3440340243/O1CN01o89Ave1DfLNthgg6k_!!4611686018427383059-2-item_pic.png` |
| Export photo_link | `Documents/Sassy Closet/Photos/O01/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 73.8 ≠ intake 60 · world 105.00 ≠ intake 60 · share 73.8 ≠ world 105.00 (intake cost_cny **60**; cost_usd **8.94** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- **thin stock / unknown:** 好評 count hidden on world · item-level qty **unknown** logged-out.
- kind **O Khác** vs breadcrumb **女鞋/拖鞋** (G Giày exists in the kit). Letter kept as export; not a photo≠link by itself.

**Call:** Hold · draft only · no buy.

---

## O02 · O Khác / Other

**Short:** https://e.tb.cn/h.8JYtG1MFPlnSWdR?tk=BifhT7B2DyU  
**Resolved id:** `1036949523897`  
**World:** https://world.taobao.com/item/1036949523897.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `tmall`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 少女風碎花蝴蝶結一字... |
| Meta 選購 hint | 選購少女風碎花蝴蝶結一字... |
| Breadcrumb | 首頁 › 儷人購 › 天貓奢品直營 › 女鞋 › 拖鞋 |
| Share `price=` | **¥69.8** (embed; cite as share lane) |
| World `promotionPrice` | **¥99.00** (differs from share — cite both) |
| World `originalPrice` | ¥99.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `80.52` · cost_usd `12` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `∅` · color `Đen, Trắng` · note `Size 35 to 40` |
| Colors / sizes / 均码 (live) | `顏色分類:白色;尺碼:35` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **港蘊旗艦店** · 浙江臺州 · 515 items · scores 4.8/4.8/4.8 (4.8 物流服務; 4.8 服務; 4.8 商品描述) · 好評 unknown (ICE `goodCount` empty) · latest public review 2026.06.15 22:08: sku `顏色分類:白色;尺碼:35` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i1/3440340243/O1CN01kWtMxD1DfLNJaR4j3_!!4611686018427383059-2-item_pic.png` |
| Export photo_link | `Documents/Sassy Closet/Photos/O02/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 69.8 ≠ intake 80.52 · world 99.00 ≠ intake 80.52 · share 69.8 ≠ world 99.00 (intake cost_cny **80.52**; cost_usd **12** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- **thin stock / unknown:** 好評 count hidden on world · item-level qty **unknown** logged-out.
- kind **O Khác** vs breadcrumb **女鞋/拖鞋** (G Giày exists in the kit). Letter kept as export; not a photo≠link by itself.

**Call:** Hold · draft only · no buy.

---

## D01 · D Đầm / Dress

**Short:** https://e.tb.cn/h.8IuehN5oDQq0mKu?tk=TSJWT7BlgWI  
**Resolved id:** `1046519667783`  
**World:** https://world.taobao.com/item/1046519667783.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | WITHMIN 粉色... |
| Meta 選購 hint | 選購WITHMIN 粉色... |
| Breadcrumb | 首頁 › 品牌女裝 › 洋裝 › 氣質洋裝 |
| Share `price=` | **¥166** (embed; cite as share lane) |
| World `promotionPrice` | **¥166.00** (aligned with share this pass) |
| World `originalPrice` | ¥166.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `134.20` · cost_usd `20` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `S M L` · color `Hồng` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:粉色;尺碼:S` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **withmin涼皮** · 廣東廣州 · 1388 items · scores 4.8/4.7/4.7 (4.8 物流服務; 4.7 服務; 4.7 商品描述) · 好評 500+ · latest public review 2026.08.21 14:26: sku `顏色分類:粉色;尺碼:S` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i1/2570551622/O1CN01MAVaPq1NqvYXAw3Vc_!!2570551622.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/D01/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 166 ≠ intake 134.20 · world 166.00 ≠ intake 134.20 (intake cost_cny **134.20**; cost_usd **20** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).

**Call:** Hold · draft only · no buy.

---

## D02 · D Đầm / Dress

**Short:** https://e.tb.cn/h.8J19U7AXarFp5si?tk=laULT7BwQ6T  
**Resolved id:** `1046521459484`  
**World:** https://world.taobao.com/item/1046521459484.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | WITHMIN 白色... |
| Meta 選購 hint | 選購WITHMIN 白色... |
| Breadcrumb | 首頁 › 品牌女裝 › 洋裝 › 氣質洋裝 |
| Share `price=` | **¥166** (embed; cite as share lane) |
| World `promotionPrice` | **¥166.00** (aligned with share this pass) |
| World `originalPrice` | ¥166.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `131` · cost_usd `19.52` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `S M L` · color `Trắng` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:白色;尺碼:S` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **withmin涼皮** · 廣東廣州 · 1388 items · scores 4.8/4.7/4.7 (4.8 物流服務; 4.7 服務; 4.7 商品描述) · 好評 64 · latest public review 2026.05.12 13:18: sku `顏色分類:白色;尺碼:S` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i4/2570551622/O1CN01Yozzhk1NqvYXx0MNp_!!2570551622.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/D02/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 166 ≠ intake 131 · world 166.00 ≠ intake 131 (intake cost_cny **131**; cost_usd **19.52** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).

**Call:** Hold · draft only · no buy.

---

## B03 · B Túi

**Short:** https://e.tb.cn/h.8rTGQO7OItONbkA?tk=c2oET7zWqBJ  
**Resolved id:** `1007708184718`  
**World:** https://world.taobao.com/item/1007708184718.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 迪士尼包包生日禮物女... |
| Meta 選購 hint | 選購迪士尼包包生日禮物女... |
| Breadcrumb | 首頁 › 導航平臺 › 拍賣會（舊前臺） › 奢侈品 › 包包 |
| Share `price=` | **¥279** (embed; cite as share lane) |
| World `promotionPrice` | **¥279.00** (aligned with share this pass) |
| World `originalPrice` | ¥279.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `204` · cost_usd `30.40` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `∅` · color `∅` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:迪士尼聯名-櫻花粉【雪莉玫+限定禮袋】` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **迪士尼品牌正品專櫃店** · 廣東廣州 · 582 items · scores 4.9/4.9/4.9 (4.9 物流服務; 4.9 服務; 4.9 商品描述) · 好評 75 · latest public review 2026.07.27 16:23: sku `顏色分類:迪士尼聯名-櫻花粉【雪莉玫+限定禮袋】` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i4/765113186/O1CN016StwIf1ZPEz2w72tB_!!765113186.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/B03/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 279 ≠ intake 204 · world 279.00 ≠ intake 204 (intake cost_cny **204**; cost_usd **30.40** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).

**Call:** Hold · draft only · no buy.

---

## Q01 · Q Quần

**Short:** https://e.tb.cn/h.8rhr0aiQK5LTZp6?tk=Z8qYTiacYLD  
**Resolved id:** `1042320874853`  
**World:** https://world.taobao.com/item/1042320874853.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 吳太甜 百搭capr... |
| Meta 選購 hint | 選購吳太甜 百搭capr... |
| Breadcrumb | 首頁 › 品牌女裝 › 休閒褲 › 商場同款 |
| Share `price=` | **¥105** (embed; cite as share lane) |
| World `promotionPrice` | **¥105.00** (aligned with share this pass) |
| World `originalPrice` | ¥105.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `74.55` · cost_usd `11.11` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `L S M XL` · color `Trắng, Đen` · note `∅` |
| Colors / sizes / 均码 (live) | `尺寸:M;顏色分類:黑色五分褲` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **Wuu2Sweet吳太甜** · 廣東廣州 · 595 items · scores 4.8/4.8/4.7 (4.8 物流服務; 4.8 服務; 4.7 商品描述) · 好評 200+ · latest public review 2026.08.29 19:20: sku `尺寸:M;顏色分類:黑色五分褲` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i1/2217644131820/O1CN01ZwWAW51PJbyQmn3Ap_!!2217644131820.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/Q01/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 105 ≠ intake 74.55 · world 105.00 ≠ intake 74.55 (intake cost_cny **74.55**; cost_usd **11.11** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).

**Call:** Hold · draft only · no buy.

---

## O03 · O Khác / Other

**Short:** https://e.tb.cn/h.8s4JLqv5j0g8Z7e?tk=ApjRTiiwi69  
**Resolved id:** `1028539989739`  
**World:** https://world.taobao.com/item/1028539989739.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 五枚裝~可愛小貓貓拇... |
| Meta 選購 hint | 選購五枚裝~可愛小貓貓拇... |
| Breadcrumb | 首頁 › 阿裏B2C商城 › 日化/清潔/護理 › 個人洗浴/清潔/護理 › 洗浴用具/浴球/鏡梳 › 粉撲 |
| Share `price=` | **¥1.6** (embed; cite as share lane) |
| World `promotionPrice` | **¥1.60** (aligned with share this pass) |
| World `originalPrice` | ¥1.60 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `0.69` · cost_usd `0.10` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `∅` · color `∅` · note `∅` |
| Colors / sizes / 均码 (live) | `商品規格:5枚裝#貓咪禮盒裝` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **淼淼淼小哥** · 廣東廣州 · 47 items · scores 4.6/4.6/4.5 (4.6 物流服務; 4.6 服務; 4.5 商品描述) · 好評 1000+ · latest public review 2026.08.21 07:56: sku `商品規格:5枚裝#貓咪禮盒裝` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i2/1088949910/O1CN01x0V2W22N4q8YijsK6_!!1088949910.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/O03/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 1.6 ≠ intake 0.69 · world 1.60 ≠ intake 0.69 (intake cost_cny **0.69**; cost_usd **0.10** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- **thin stock / unknown:** shop only 47 items · item-level qty **unknown** logged-out.

**Call:** Hold · draft only · no buy.

---

## S04 · S Set đồ

**Short:** https://e.tb.cn/h.8s4B4htXZ4FDIHD?tk=UYNRTiR2TUD  
**Resolved id:** `1047301043121`  
**World:** https://world.taobao.com/item/1047301043121.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 重工蕾絲魚骨抹胸上衣... |
| Meta 選購 hint | 選購重工蕾絲魚骨抹胸上衣... |
| Breadcrumb | 首頁 › 品牌女裝 › 2016當季新品 › 天貓獨家首發 |
| Share `price=` | **¥165** (embed; cite as share lane) |
| World `promotionPrice` | **¥246.00** (differs from share — cite both) |
| World `originalPrice` | ¥246.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `140` · cost_usd `20.86` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `XS L S M` · color `Trắng, Đỏ` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:紅色（抹胸上衣+半身裙）;尺碼:XS` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **賣衣服養你啊** · 北京 · 366 items · scores 4.9/4.9/4.9 (4.9 物流服務; 4.9 服務; 4.9 商品描述) · 好評 62 · latest public review 2026.05.19 22:37: sku `顏色分類:紅色（抹胸上衣+半身裙）;尺碼:XS` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i2/2925704495/O1CN01C37nxX1j4lSCV8kFE_!!2925704495.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/S04/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 165 ≠ intake 140 · world 246.00 ≠ intake 140 · share 165 ≠ world 246.00 (intake cost_cny **140**; cost_usd **20.86** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).

**Call:** Hold · draft only · no buy.

---

## A10 · A Áo

**Short:** https://e.tb.cn/h.8rlnYG67PkBUJy2?tk=A3e2TRQPEGG  
**Resolved id:** `989709595663`  
**World:** https://world.taobao.com/item/989709595663.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | Lukira 奧黛小... |
| Meta 選購 hint | 選購Lukira 奧黛小... |
| Breadcrumb | 首頁 › 導航平臺 › 淘寶創意 › 服裝內衣 |
| Share `price=` | **¥119** (embed; cite as share lane) |
| World `promotionPrice` | **¥119.00** (aligned with share this pass) |
| World `originalPrice` | ¥119.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `100.65` · cost_usd `15` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `S M L` · color `∅` · note `∅` |
| Colors / sizes / 均码 (live) | `主要顏色:糯米杏（第一批）現貨;尺碼:M` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货 **named in review SKU** (`主要顏色:糯米杏（第一批）現貨;尺碼:M`) · item-level 预售 **not seen** · selectable stock chips **absent** |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **Lukira** · 廣東廣州 · 423 items · scores 4.7/4.7/4.6 (4.7 物流服務; 4.7 服務; 4.6 商品描述) · 好評 300+ · latest public review 2026.08.16 19:00: sku `主要顏色:糯米杏（第一批）現貨;尺碼:M` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i2/2218650496114/O1CN013QuH051v2GeFI0zlT_!!2218650496114.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/A10/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 119 ≠ intake 100.65 · world 119.00 ≠ intake 100.65 (intake cost_cny **100.65**; cost_usd **15** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).

**Call:** Hold · draft only · no buy.

---

## O05 · O Khác / Other

**Short:** https://e.tb.cn/h.8rOfGnCaJlwRSVZ?tk=yxteTR9f1yt  
**Resolved id:** `1078272019049`  
**World:** https://world.taobao.com/item/1078272019049.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `tmall`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 可愛蝴蝶結小羊棉拖鞋... |
| Meta 選購 hint | 選購可愛蝴蝶結小羊棉拖鞋... |
| Breadcrumb | 首頁 › 喵街 › 喵街類目管理 › 女鞋 › 拖鞋 |
| Share `price=` | **¥39.9** (embed; cite as share lane) |
| World `promotionPrice` | **¥118.00** (differs from share — cite both) |
| World `originalPrice` | ¥118.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `42` · cost_usd `6.26` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `∅` · color `∅` · note `Size 36-41` |
| Colors / sizes / 均码 (live) | `顏色分類:粉色7333小羊棉拖鞋;尺碼:38[-39(偏小一碼)]` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **俏繪旗艦店** · 浙江寧波 · 5979 items · scores 4.7/4.6/4.5 (4.7 物流服務; 4.6 服務; 4.5 商品描述) · 好評 unknown (ICE `goodCount` empty) · latest public review 2026.09.12 16:30: sku `顏色分類:粉色7333小羊棉拖鞋;尺碼:38[-39(偏小一碼)]` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i4/3421240519/O1CN01gohoahYAcNE2vH2e_!!4611686018427387079-0-item_pic.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/O05/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 39.9 ≠ intake 42 · world 118.00 ≠ intake 42 · share 39.9 ≠ world 118.00 (intake cost_cny **42**; cost_usd **6.26** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- **thin stock / unknown:** 好評 count hidden on world · item-level qty **unknown** logged-out.
- kind **O Khác** vs breadcrumb **女鞋/拖鞋** (G Giày exists in the kit). Letter kept as export; not a photo≠link by itself.

**Call:** Hold · draft only · no buy.

---

## O04 · O Khác / Other

**Short:** https://e.tb.cn/h.8IHGsvkidFuxFpK?tk=S4tATR9JWnV  
**Resolved id:** `1077516969221`  
**World:** https://world.taobao.com/item/1077516969221.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `tmall`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 卡通可愛兔子毛毛鞋女... |
| Meta 選購 hint | 選購卡通可愛兔子毛毛鞋女... |
| Breadcrumb | 首頁 › 喵街 › 喵街類目管理 › 女鞋 › 拖鞋 |
| Share `price=` | **¥29.9** (embed; cite as share lane) |
| World `promotionPrice` | **¥99.00** (differs from share — cite both) |
| World `originalPrice` | ¥99.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | **BLANK** — `cost_cny` empty · `cost_usd` empty · `cost_currency` USD. Note: no cost to drift against. |
| Intake size / color (export, not live chips) | size `∅` · color `∅` · note `Size 36-41` |
| Colors / sizes / 均码 (live) | `顏色分類:白色6623兔子棉拖鞋;尺碼:38[-39(適合平時37-38碼)]` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **俏繪旗艦店** · 浙江寧波 · 5983 items · scores 4.7/4.6/4.5 (4.7 物流服務; 4.6 服務; 4.5 商品描述) · 好評 unknown (ICE `goodCount` empty) · latest public review 2026.09.04 21:18: sku `顏色分類:白色6623兔子棉拖鞋;尺碼:38[-39(適合平時37-38碼)]` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i3/3421240519/O1CN01o0Auw3CfZ2H2vH2e_!!4611686018427387079-0-item_pic.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/O04/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- **O04 intake cost blank** (`cost_cny` empty · `cost_usd` empty) — **cannot compute ¥ drift vs intake**. Do not invent cost.
- photo≠link: **not newly detected** from listing hero this pass — listing hero = white bunny 棉拖鞋 — matches title 兔子毛毛鞋. No Photos/O04 on OneDrive hub this pass
- 保温杯 vs P: n/a (not a P thermos listing).
- **thin stock / unknown:** 好評 count hidden on world · item-level qty **unknown** logged-out.
- kind **O Khác** vs breadcrumb **女鞋/拖鞋** (G Giày exists in the kit). Letter kept as export; not a photo≠link by itself.

**Call:** Hold · draft only · no buy.

---

## A11 · A Áo

**Short:** https://e.tb.cn/h.8H5CQoPgwjl36Nw?tk=YgB1TRkrlfk  
**Resolved id:** `841848039676`  
**World:** https://world.taobao.com/item/841848039676.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `tmall`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 奶黃色趣味小狗毛衣外... |
| Meta 選購 hint | 選購奶黃色趣味小狗毛衣外... |
| Breadcrumb | 首頁 › 儷人購 › 天貓奢品直營 › 女裝 › 毛衣 |
| Share `price=` | **¥109** (embed; cite as share lane) |
| World `promotionPrice` | **¥129.00** (differs from share — cite both) |
| World `originalPrice` | ¥129.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `93` · cost_usd `13.86` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `S M L` · color `∅` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:黃色;尺碼:L` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **表演時刻旗艦店** · 廣東東莞 · 1123 items · scores 4.8/4.8/4.8 (4.8 物流服務; 4.8 服務; 4.8 商品描述) · 好評 unknown (ICE `goodCount` empty) · latest public review 2024.10.19 20:36: sku `顏色分類:黃色;尺碼:L` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i4/2934924135/O1CN01YrvNP31gPsjJ7fMiR_!!2-item_pic.png` |
| Export photo_link | `Documents/Sassy Closet/Photos/A11/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 109 ≠ intake 93 · world 129.00 ≠ intake 93 · share 109 ≠ world 129.00 (intake cost_cny **93**; cost_usd **13.86** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- **thin stock / unknown:** 好評 count hidden on world · item-level qty **unknown** logged-out.

**Call:** Hold · draft only · no buy.

---

## A12 · A Áo

**Short:** https://e.tb.cn/h.8s7QqCSbdBca1Ss?tk=2rsaT8cFgzO  
**Resolved id:** `1019149471031`  
**World:** https://world.taobao.com/item/1019149471031.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 半芝桃 原創白色波點... |
| Meta 選購 hint | 選購半芝桃 原創白色波點... |
| Breadcrumb | 首頁 › 導航平臺 › 淘寶創意 › 服裝內衣 |
| Share `price=` | **¥128** (embed; cite as share lane) |
| World `promotionPrice` | **¥128.00** (aligned with share this pass) |
| World `originalPrice` | ¥128.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `103` · cost_usd `15.35` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `S M L XL` · color `∅` · note `∅` |
| Colors / sizes / 均码 (live) | `主要顏色:白色;尺碼:M` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **半芝桃** · 廣東東莞 · 1614 items · scores 4.7/4.7/4.6 (4.7 物流服務; 4.7 服務; 4.6 商品描述) · 好評 26 · latest public review 2026.08.22 21:34: sku `主要顏色:白色;尺碼:M` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i3/2212735207665/O1CN01f0Fubi26UcxyLq2am~crop,0,125,750,750~_!!2212735207665.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/A12/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 128 ≠ intake 103 · world 128.00 ≠ intake 103 (intake cost_cny **103**; cost_usd **15.35** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- thin stock / unknown: public 好評 not tiny · **item qty still unknown** (no stock chip).

**Call:** Hold · draft only · no buy.

---

## A13 · A Áo

**Short:** https://e.tb.cn/h.8IdUQLLRMS18xaT?tk=Xz02T8Xca81  
**Resolved id:** `988176960813`  
**World:** https://world.taobao.com/item/988176960813.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 春夏粉色碎花貓咪針織... |
| Meta 選購 hint | 選購春夏粉色碎花貓咪針織... |
| Breadcrumb | 首頁 › 導航平臺 › 淘寶創意 › 服裝內衣 |
| Share `price=` | **¥99** (embed; cite as share lane) |
| World `promotionPrice` | **¥99.00** (aligned with share this pass) |
| World `originalPrice` | ¥99.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `81` · cost_usd `12.07` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `S M L` · color `∅` · note `∅` |
| Colors / sizes / 均码 (live) | `主要顏色:碎花貓咪T恤;尺碼:L` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **Dreamyland** · 北京 · 88 items · scores 4.9/4.9/4.8 (4.9 物流服務; 4.9 服務; 4.8 商品描述) · 好評 10 · latest public review 2026.09.02 10:46: sku `主要顏色:碎花貓咪T恤;尺碼:L` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i1/2206892696490/O1CN01tyCgJw1xoTZDC94ae_!!2206892696490.heic` |
| Export photo_link | `Documents/Sassy Closet/Photos/A13/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 99 ≠ intake 81 · world 99.00 ≠ intake 81 (intake cost_cny **81**; cost_usd **12.07** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- **thin stock / unknown:** shop only 88 items · thin public 好評 (10) · item-level qty **unknown** logged-out.

**Call:** Hold · draft only · no buy.

---

## D03 · D Đầm / Dress

**Short:** https://e.tb.cn/h.8HDJ57ubctdLHOr?tk=3bMrT8XswiP  
**Resolved id:** `1060137201822`  
**World:** https://world.taobao.com/item/1060137201822.htm  
**Fetched:** 2026-09-15 GET share HTTP 200 · world HTTP 200 · ICE `True` · `itemExist` `True` · `seoItemType` `taobao`

| Field | Sourced value |
| --- | --- |
| Title CN (world trunc) | 微胖mm法式甜辣風蕾... |
| Meta 選購 hint | 選購微胖mm法式甜辣風蕾... |
| Breadcrumb | 首頁 › Hitao地圖模板 › 服飾鞋包 › 下裝pant › 牛仔褲 |
| Share `price=` | **¥108** (embed; cite as share lane) |
| World `promotionPrice` | **¥108.00** (aligned with share this pass) |
| World `originalPrice` | ¥108.00 (same as promotionPrice · `hasRangePrice` `False`) |
| World price remark | 價格可能因優惠活動發生變化 |
| Intake cost | cost_cny `92` · cost_usd `13.71` · cost_currency `USD` |
| Intake size / color (export, not live chips) | size `S M L XL` · color `∅` · note `∅` |
| Colors / sizes / 均码 (live) | `顏色分類:新品試銷;尺碼:M[建議90-100斤]` · 均码 **not seen** on world title / ICE / review chips |
| 现货 / 预售 | 现货/预售 **unknown** (no item-level chip logged-out; no 预售 string on this PDP) |
| 运费 | `freeShipping`: **False** · world UI **註冊運費立減** (login teaser only) · domestic 包邮/运费金额 **unknown** |
| Shop | **大霓Dani** · 廣東廣州 · 681 items · scores 4.9/4.8/4.8 (4.9 物流服務; 4.8 服務; 4.8 商品描述) · 好評 7 · latest public review 2026.06.25 10:43: sku `顏色分類:新品試銷;尺碼:M[建議90-100斤]` |
| Listing image (world `images[0]`) | `//img.alicdn.com/imgextra/i3/2622222234/O1CN01FbljSv1SNDxVAR0fu~crop,0,225,750,750~_!!2622222234.jpg` |
| Export photo_link | `Documents/Sassy Closet/Photos/D03/` · OneDrive Photos hub folder: **not listed** this pass |

**Flags**

- ¥ **drift**: share 108 ≠ intake 92 · world 108.00 ≠ intake 92 (intake cost_cny **92**; cost_usd **13.71** USD). Do not collapse to one payable ¥ — Boss login/coupon.
- photo≠link: **unknown** — `Photos/{mã}/` **not in** OneDrive hub listing (A01–A03/B01/H01/K01/P01–P05/S01 only). Export still points at that path. Do not invent a match.
- 保温杯 vs P: n/a (not a P thermos listing).
- **thin stock / unknown:** thin public 好評 (7) · item-level qty **unknown** logged-out.
- breadcrumb `牛仔褲` vs D Đầm — world SEO noise; title is 蕾絲 dress language.

**Call:** Hold · draft only · no buy.

---

## Findings (2026-09-15)

1. All **38** shorts returned HTTP 200 HTML with JS `var url` → item id + `price=`. All 38 world PDPs returned HTTP 200 + ICE `itemExist: true`. No mã failed resolve. No purchase path used.
2. World remains login-light and **MOST_SIMPLIFIED**: no selectable SKU matrix, no payable freight number, almost no 现货/预售 chip. A10 is the exception: review SKU `糯米杏（第一批）現貨`.
3. Share ¥ **≠** world `promotionPrice` on 18 mã this pass (largest: **B01** 198 vs 899 · **S03** 78 vs 608 · **S01** 148 vs 399 · **O04** 29.9 vs 99 · **O05** 39.9 vs 118 · **B02** 79.9 vs 179.9 · **P04** 23.8 vs 50). Aligned examples: A01 109 · A12 128 · J01 150 · J02 188 · D01/D02 166.
4. **O04 intake cost is blank.** Live lanes still exist (share ¥29.9 · world ¥99.00) but drift vs cost cannot be scored. Boss needs a cost before any buy talk.
5. **保温杯 vs P** still live on **P02 / P03 / P05** (杯比無奈 · breadcrumb 杯子/水杯/水壺 › 保溫杯). P01 髮箍 and P04 帽子 are P without thermos.
6. **photo≠link:** only **P03** stays flagged (listing Judy/Nick vs archive Shin-chan Photos). A01/B01/P01/P02/P04/P05 listing heroes match prior notes. Other mãs: either hub folder not listed or hero not opened — **unknown**, not invented.
7. **S01** is a Set letter on a **one-piece 洋裝** listing (cream polo dress). **K01** is K on a yellow zip **毛衣**. **O01/O02/O04/O05** are 拖鞋 under O.
8. Thin/unknown public surface: **B01** (no world reviews) · **A01** 1 好評 · **S01/A03** 3 · **K01** 5 · **J02** shop 45 items / 25 好評 · **A13** shop 88 / 10 好評 · **A05** 好評 count hidden.
9. **A07** reverse ¥: intake cost_cny 87.23 **above** live share=world **49.99** — still not a license to invent payable; just note the inversion.
10. Granola meeting lookup was **not available** this run (account not signed up). Decisions here follow the uploaded playbook only.

## Open Qs (Boss)

1. Payable ¥ after login/coupon on the three-way / two-way drifts — especially B01 **174.46 / 198 / 899**, S03 **60.39 / 78 / 608**, S01 **114.07 / 148 / 399**, O04 **∅ / 29.9 / 99**, O05 **42 / 39.9 / 118**, A03 **59 / 72 / 100**, B02 **67.10 / 79.9 / 179.9**, P04 **15.90 / 23.8 / 50**, A08 **90 / 119.8 / 184.31**.
2. O04: fill `cost_cny` / `cost_usd` or confirm skip.
3. P03: Boss eye Photos/P03 `001–003.jpg` vs this Judy/Nick PDP — keep or clear photo≠link.
4. Drinkware letter: keep P02/P03/P05 as P or split out of Phụ kiện.
5. S01 letter S vs 洋裝; K01 K vs 毛衣; O-slippers vs G.
6. Full size/color matrices (export lists many; world only showed one review chip each).
7. Freight payable (world hides it).

## Hard stops

Never 旺旺. Never cart / checkout / buy. Never invent mã / ¥ / stock. Draft notes only.

No 旺旺 · no cart · no buy.
