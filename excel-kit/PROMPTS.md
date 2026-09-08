# Cursor prompts — Boss / Mini Boss

Paste one block into a **Cursor Cloud Agent** on `https://github.com/SkyLanter/Sassy-closet`.  
Agents change kit code here. **ONE hub** is `sassycloset` (`./kit.sh save`). Lands at OneDrive `Documents/Sassy Closet/sassycloset.xlsx`.  
Bots draft only. No Square Save, no Facebook post, no Zelle. Never invent mã.

Shop law (every prompt):

- Square Free = on-hand inventory source of truth. Track stock ON.
- Official Excel (`Sassy_Closet_SoT.xlsx`) = working copy / mã index / captions — not a second inventory.
- Photos: `Documents/Sassy Closet/Photos/` as `#001.jpg` / `AO001.jpg`. `photo_link` only. No embeds.
- Mã = `AO|QU|VA|AK|GI|PK|SET` + 3 digits. Ask Stock (Dashboard `B21:B27`). Never reuse Sold.
- Wishlist ≠ stock. `#shop-decisions` is Boss yes/no.

---

## Launch (Mini Boss)

```
Open repo SkyLanter/Sassy-closet. New Cursor Cloud Agent on main.
Use excel-kit/. Do not commit live Official rows, customer names, Square tokens, or filled import CSVs.
After the PR merges, Kit copies built/cleaned workbooks to OneDrive Documents/Sassy Closet/.
```

Then paste **one** task block below. GF clothes intake contract: `prompts/GF_CLOTHES_INTAKE.md`.

---

## 1) Append Official row

```
Sassy Closet — append one Official row on the ONE desktop book Sassy_Closet_SoT.xlsx.

RUN (after you have a real mã — never invent):
  python3 excel-kit/sot/append_official_row.py -w "$SASSY_SOT" --ma AO000 \
    --name-vi "…" --size "…" --color "…" --qty 1 --status Available --photo-link "https://…"

CONTRACT
- --ma required. If missing, print ASK STOCK (Dashboard next-mã B21:B27) and stop.
- Do not invent AO/QU/VA/AK/GI/PK/SET + digits.
- If mã already exists, refuse. Update that row or ask Stock.
- Square Free still wins on-hand. qty_on_hand is a working-copy note.
- photo_link = OneDrive share URL. No embeds.
- Empty / omitted buyer fields are correct. No PII in git.

STOP if you do not have a Boss-assigned mã.
```

---

## 2) Append Wishlist row

```
Sassy Closet — append one Wishlist row. Not stock.

RUN
  python3 excel-kit/sot/append_wishlist_row.py -w "$SASSY_SOT" \
    --source "https://…" --what-vi "…" --size "M 88cm" --status candidate
  # or, only if there is truly no reopen URL:
  python3 excel-kit/sot/append_wishlist_row.py -w "$SASSY_SOT" --no-source --what-en "…"

CONTRACT
- Link/source required if available (--source / --link). Else --no-source.
- photo_link optional. photo_link is last on SoT Wishlist.
- Stay off Square until Boss confirms bought + Save yes.
- Never write a live mã on Wishlist.
```

---

## 3) Append Order row

```
Sassy Closet — append one Orders row.

RUN
  python3 excel-kit/sot/append_order_row.py -w "$SASSY_SOT" \
    --status Inquiry --ma AO000 --channel Facebook --size M --color "…"

CONTRACT
- --status must be exactly Inquiry | Reserved | Paid | Shipped | Picked up | Cancelled
- --ma only if it already exists (Stock/Boss assigned)
- Facebook inbox is the store. This is the working log.
- Omit --buyer rather than invent a name. No customer PII in git.
```

---

## 4) Bot_Activity log

```
Sassy Closet — log a draft on Bot_Activity if the sheet exists.

RUN
  python3 excel-kit/sot/append_bot_activity.py -w "$SASSY_SOT" \
    --bot Stock --action draft --summary "…" --ma AO000

If Bot_Activity is missing, the script must skip with a note and exit 0.
Never status=saved/posted/sent. Bots draft only. Times are Pacific.
```

---

## 5) Morning brief

```
Sassy Closet — morning brief from the ONE SoT book.

RUN
  python3 excel-kit/sot/dashboard_brief.py -w "$SASSY_SOT"

If cached formula values exist, print them.
If not (openpyxl cannot calculate Excel), tell Boss: open Excel → Dashboard → copy B43.
Do not invent counts. Square Free still wins on-hand.
```

---

## 6) Clean demo / Square wording

```
Sassy Closet — clean kit-seeded demo rows. Do not invent replacement stock.

RUN
  python3 excel-kit/clean_sot_demo.py path/to/Sassy_Closet_SoT.xlsx -o ./out/Sassy_Closet_SoT.xlsx
  # or report only:
  python3 excel-kit/clean_sot_demo.py path/to/Sassy_Closet_SoT.xlsx --check

Square Free = on-hand SoT. Official Excel = working copy. Strip embeds. photo_link only.
```

---

## 7) Rebuild empty SoT scaffold

```
Build empty Sassy_Closet_SoT.xlsx (headers + Dashboard!B43 formula, zero inventory).

RUN
  python3 excel-kit/sot/build_sot_desktop.py --out-dir ./out
  python3 excel-kit/tests/run_checks.py

Kit syncs ./out/Sassy_Closet_SoT.xlsx → OneDrive Documents/Sassy Closet/
Do not prefill sample Official rows. Do not embed images.
```

---

## 8) Rebuild lean desktop Official + Wishlist

See `prompts/BOUTIQUE_DESKTOP_EFFICIENT.md` (full contract). Short form:

```
python3 excel-kit/build_boutique_desktop.py --out-dir ./out
```

Phone-safe SoT edits: `prompts/BOUTIQUE_PHONE_SAFE.md`.

---

## 9) Square import draft (Track ON, mã naming)

```
Sassy Closet — Square Free import reminder. Do not Save.

Read excel-kit/square/README.md.
Template excel-kit/square/square_import_template.csv is HEADERS ONLY.
SKU = mã. Stockable = Y. Track stock ON. Token blank on create.
Replace [Default] with the live location name from a fresh Square export.
Do not commit filled rows. Do not import wishlist.
Validate a local draft with:
  python3 excel-kit/square/validate_import.py path/to/draft.csv
```

---

## 10) Kit checks before PR

```
From repo root:
  pip install -r requirements.txt
  python3 excel-kit/tests/run_checks.py

Must: py_compile every script, --help on every CLI, no fake inventory rows in git,
square template headers-only, photo_link last on Ma_List / Candidates / SoT Wishlist.
```

---

## 11) GF clothes intake

Contract: `excel-kit/prompts/GF_CLOTHES_INTAKE.md` (From GF self-upload is PRIMARY).

```
Sassy Closet — GF clothes intake (Kit code only). PRIMARY: GF uploads herself to
OneDrive Documents/Sassy Closet/From GF/ (Boss share link once). Slack #shop-intake /
Boss-paste / email are backups. Never Messenger. Never Dial Bot.

RUN
  python3 excel-kit/sot/gf_intake_apply.py --from-gf path/to/packet/ -w "$SASSY_SOT" \
    --photos-out "$SASSY_PHOTOS" --dry-run
  python3 excel-kit/sot/gf_intake_apply.py --from-gf path/to/packet/ -w "$SASSY_SOT" \
    --photos-out "$SASSY_PHOTOS"
  python3 excel-kit/tests/run_checks.py

CONTRACT
- Parse INTAKE_TEMPLATE.txt / note.txt. Exit 2 on clear errors. Never invent fields or mã.
- looking → append_wishlist_row (refuse --ma). bought without mã → Wishlist status=bought + ASK STOCK.
  bought with Stock/Boss mã → append_official_row (--ma required).
- Photos copy/rename to Photos/ as #NNN.jpg or MA.jpg. photo_link only if --photo-link (OneDrive share URL).
  Never embed. Never point SoT at From GF paths.
- --dry-run must not write xlsx. Print stay-off-Square on every success.
- Optional Bot_Activity draft if the sheet exists. Boss confirms to GF with inbox/gf_intake_reply_templates.md.
- #shop-decisions before Square Save. No Square Save, no FB post, no mint mã.

STOP if you would invent a mã or Save in Square.
```

---

## 12) From GF OneDrive link (do not hand Graph webUrl)

Docs: `excel-kit/templates/from_gf/LINKING.md` (slash after `.com`, encode `!` as `%21`). Watcher: `excel-kit/sot/FROM_GF_WATCH.md`.

```
Sassy Closet — canonicalize the From GF OneDrive browse URL. Guest Share stays manual.

RUN
  python3 excel-kit/sot/onedrive_from_gf_link.py --help
  python3 excel-kit/sot/onedrive_from_gf_link.py \
    --web-url "https://onedrive.live.com?cid=…&id=…"
  python3 excel-kit/sot/onedrive_from_gf_link.py --cid … --item-id …

CONTRACT
- Raw onedrive.live.com?cid=&id= (no /? , raw !) often 404s. Print canonical browse with /? and %21.
- Prefer Graph createLink type=edit when MSAL/Graph env is already documented. This repo has none —
  print Boss steps (Share → Can edit → copy link) and exit 0. Never invent 1drv.ms / authkey tokens.
- Do not ask for passwords in code. Do not commit live share URLs.
```

---

## 13) sassycloset hub (ONE book)

Contract: `prompts/SASSYCLOSET_HUB_2026-09-07.md`.

```
Sassy Closet — ONE hub named sassycloset.

RUN
  ./kit.sh save
  # same as: ./kit.sh run
  python3 excel-kit/tests/run_checks.py
  unzip -t out/sassycloset.xlsx

CONTRACT
- Fetch live GET https://sassy-closet.vercel.app/api/export
- Rebuild out/sassycloset.xlsx: All + A_Ao Q_Quan V_Vay K_Khoac G_Giay B_Tui
  P_PhuKien S_Set O_Khac H_Toc J_TrangSuc + Orders + Readme
- All: ma first, source_link (Taobao/e.tb.cn) col B. Never drop link columns.
- photo_folder = Documents/Sassy Closet/Photos/{ma}/
- Sync Photos to out/Photos/{ma}/ (001.jpg…). Never invent mã. No A02 folder.
- P02 and P05 are separate. A02 was renamed to P02 (not P05).
- Plain only. No cute / pink / embeds. No Square Save. No FB Post.

OneDrive land path: Documents/Sassy Closet/sassycloset.xlsx
```
