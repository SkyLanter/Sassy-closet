# GF clothes intake — design contract

Boss said **GO 2026-09-05**. Kit code only. This file is the locked contract for GF self-upload → Photos rename → Wishlist / Official staging → Boss confirms to GF.

Square Free = on-hand inventory truth. **No Square Save. No Facebook post. No mint mã. No Wishlist as on-hand.** Dial Bot is love calls — not shop intake. Messenger is not for intake.

Desktop SoT: `Documents/Sassy Closet/Sassy_Closet_SoT.xlsx` (Official / Wishlist / Orders / Dashboard). Working copy — not second inventory.

---

## A) PRIMARY: From GF self-upload

**PRIMARY.** GF uploads **herself** to the shared OneDrive folder:

`Documents/Sassy Closet/From GF/`

Boss shares that folder link **once**. She opens the link on her phone, drops photos, fills the template. Cute / soft. No one invents a mã for her.

Kit seeds the same files in-repo at `excel-kit/templates/from_gf/` (`HOW_TO_UPLOAD.md`, `INTAKE_TEMPLATE.txt`, example packets). After merge, **Kit copies the seed onto OneDrive From GF/**. Live packets stay on OneDrive — this repo never holds live Official rows.

### HOW_TO + template

| File | Job |
| --- | --- |
| `HOW_TO_UPLOAD.md` | Phone-friendly. Soft **VI first**, then EN. Looking vs bought. “chưa lên Square.” Use Boss share link. Do not invent mã. Slack is not primary. |
| `INTAKE_TEMPLATE.txt` | Kind `looking` / `bought`, `source` or `no_source`, `what_vi` / `what_en`, size (Asia + cm), color, `price_original` + `currency`, `qty_pieces`, notes, `requested_by=GF`. |

Packet = one folder (date + short name) with photos + `INTAKE_TEMPLATE.txt` **or** `note.txt` (same keys). Optional: Kit also accepts `--packet` copies of that schema.

### Backups (not primary)

1. Slack `#shop-intake` — GF or Boss drops a note when OneDrive is awkward.
2. Boss pastes the same fields into the CLI flags.
3. Email last.

**Never primary:** Messenger, Dial Bot (love calls), Facebook inbox.

If OneDrive gets messy later, a **Microsoft Form** is an optional future front-end. **Do not build the Form in this kit.**

---

## B) Field checklists

Asian sizes + cm only. Keep Taobao / shop **source links forever**. Excel stores `photo_link` only (OneDrive **Photos/** share URL). Never embed images. Never point SoT at `From GF/` paths.

### Candidate / looking (Wishlist)

| Field | Rule |
| --- | --- |
| `kind` | `looking` / `candidate` / `watching` (not bought) |
| `source` **or** `no_source` | Required. Keep the shop URL if it exists. |
| `what_vi` / `what_en` | At least one |
| `size` | Asia size + cm |
| `color` | As she says |
| `price_original` + `currency` | Maps to Wishlist `max_cost` + notes |
| `qty_pieces` | Notes on Wishlist (no qty column) |
| `requested_by` | `GF` |
| `ma` | **Forbidden.** Never put a live mã on Wishlist. |
| `status` | `candidate` / `watching` / `skip` — **not stock** |
| Square | **Off.** Stay off until Boss confirms bought/received **and** says Save. |

### Bought / received (still off Square)

Boss confirmed she bought or received it. That is **not** Square on-hand.

| Field | Rule |
| --- | --- |
| `kind` | `bought` |
| `source` | Keep forever if she still has it |
| Same descriptive fields | as candidate |
| `ma` | **Only** if Stock already assigned (Dashboard `B21:B27`). Scripts never mint. |
| Bought **without** mã | Wishlist `status=bought` + print **ASK STOCK**. Still **not** Official. Still **off Square**. |
| Bought **with** mã | `append_official_row` (`--ma` required). Official is the working copy — **not** Square Save. |
| Square | Still off until `#shop-decisions` yes + Boss taps Save. |

Wishlist `bought` ≠ on-hand. Official row ≠ Square library.

---

## C) Routing

```
From GF/  (PRIMARY self-upload)
    → parse INTAKE_TEMPLATE.txt / note.txt  (never invent)
    → copy/rename photos → Documents/Sassy Closet/Photos/
         looking: next #NNN.jpg   (and #NNN_2.jpg)
         owned mã:  MA.jpg         (AO001.jpg, AO001_2.jpg)
    → photo_link = OneDrive Photos share URL only if supplied
         else empty + Kit upload note
         never embed; never From GF path
    → candidate / looking / watching / skip
         → append_wishlist_row.py   (refuse --ma)
    → bought without mã
         → append_wishlist_row.py --status bought
         → ASK STOCK (Dashboard B21:B27)
         → do not append Official
    → bought with Stock/Boss mã
         → append_official_row.py --ma …  (required)
    → optional Bot_Activity draft if the sheet exists (never status=saved)
    → print stay-off-Square reminder
    → print Boss→GF confirm draft (cute/soft; never claim Square stock)
    → Boss confirms to GF
    → ASK STOCK if a mã is still needed
    → Slack #shop-decisions before any Square Save
```

CLI: `excel-kit/sot/gf_intake_apply.py`  
`--from-gf path/to/packet/` **and/or** `--packet` **and/or** flags mirroring `append_*`.  
`--dry-run` must not write xlsx (and must not copy photos). Exit **2** on clear validation errors.

**Kit watcher (thin — docs only, no daemon in this kit):** periodically list `Documents/Sassy Closet/From GF/` for new packet folders (skip root HOW_TO / template / `_applied/`). For each packet, run `gf_intake_apply.py --from-gf …`. Details: `excel-kit/sot/FROM_GF_WATCH.md`.

Do not wire Dial Bot. Do not post Facebook. Do not Save Square. Do not invent mã.

---

## D) This implement prompt (summary)

Build intake tooling so a GF self-upload in `From GF/` (photos + template or `note.txt`) becomes: Photos rename + Wishlist or Official **staging** row via existing `append_*` + a friendly draft reply for Boss to confirm to GF. Optional packet files with the same schema.

Delivered in-kit:

1. `excel-kit/templates/from_gf/` — HOW_TO, INTAKE_TEMPLATE, example packets (placeholder URLs only; no fake live mã as stock).
2. `excel-kit/sot/gf_intake_apply.py` — parse / validate / route / photos / dry-run / stay-off-Square / optional Bot_Activity.
3. `excel-kit/inbox/gf_intake_reply_templates.md` — VI+EN Boss→GF; never claim Square stock.
4. Tests in `excel-kit/tests/run_checks.py` + `PROMPTS.md` §11.
5. Reuse `schema.py`, `workbook.py`, `append_wishlist_row.py`, `append_official_row.py`, `append_bot_activity.py`. No Sheets / Shopify / Messenger / Dial Bot / Square Save. No filled Square CSV commits.

STOP: No Square Save. No FB post. No mint mã. No Wishlist as on-hand. Slack / Boss-paste not primary.

---

## E) Boss → GF one-pager (she uses the share link herself)

Send her the OneDrive **From GF** share link once. Soft VI first.

### VI (gửi em)

Em ơi, gửi đồ cho shop dễ thương vậy nha 💕

Boss đã share **một link OneDrive** — folder **From GF**. Em tự mở link, tự thả ảnh. Không cần Messenger, không cần gọi Dial Bot (máy đó để gọi yêu thôi).

1. Mở link Boss gửi.
2. Tạo folder nhỏ: ngày + tên đồ (vd `2026-09-05_vay-hoa`).
3. Thả ảnh em chụp / ảnh shop.
4. Copy file `INTAKE_TEMPLATE.txt` vào folder, điền những gì em biết. Không biết thì để trống. **Đừng tự đặt mã** (AO/QU/VA…) — Stock lo.
5. Ghi `kind: looking` nếu đang xem, hoặc `kind: bought` nếu em đã mua / đã nhận.
6. Có link Taobao / shop thì giữ — shop giữ link mãi.
7. Size theo **Á châu + cm**, không cần size Mỹ.

Shop **chưa lên Square** lúc em gửi. Wishlist không phải hàng đang bán. Boss đọc xong sẽ nhắn lại cho em. Cảm ơn em nhiều 💗

### EN (same page)

Hi love — clothes for the shop go here 💕

Boss shared **one OneDrive link**: folder **From GF**. You open it and upload yourself. No Messenger. Dial Bot is for love calls, not clothes.

1. Open Boss’s share link.
2. Make a small folder: date + name (e.g. `2026-09-05_vay-hoa`).
3. Drop your photos.
4. Copy `INTAKE_TEMPLATE.txt` into that folder and fill what you know. Leave blanks. **Do not invent a mã** — Stock assigns those.
5. `kind: looking` if you are hunting, `kind: bought` if you already bought / received it.
6. Keep Taobao / shop links forever when you have them.
7. Asian size + cm only.

Nothing is on Square when you upload. Wishlist is not on-hand stock. Boss will confirm back to you. Thank you 💗
