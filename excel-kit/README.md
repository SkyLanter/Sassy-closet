# excel-kit

Builders, SoT CLIs, and prompts for Sassy Closet Excel books. **This GitHub repo is where Cursor Cloud Agents change the kit.** Kit syncs generated `.xlsx` files to OneDrive `Documents/Sassy Closet/`.

**Cute / pink / emoji / phone Excel is retired** (Boss 2026-09-07). Boss opens one plain book: `Sassy_Closet_Data.xlsx`. Website `https://sassy-closet.vercel.app` stays GF input. Excel is a simple mirror / edit buffer — **not** inventory truth. Square Free remains on-hand SoT.

See `KIT.md`, `PHOTOS.md`, and `prompts/PLAIN_DATA_EXCEL.md`.

## Layout

```
excel-kit/
  README.md
  KIT.md                     ← cute Excel retired; Boss plain book
  PHOTOS.md                  ← Photos/{MA}/ folder links only
  kit.sh                     ← pull | plain → Sassy_Closet_Data.xlsx
  PROMPTS.md                 ← Boss / Mini Boss paste these into Cloud Agents
  EFFICIENCY.md
  DESIGN_NOTES.md
  schema.py
  build_plain_data.py        ← live /api/export → plain data book
  clean_sot_demo.py
  build_boutique_desktop.py  ← retired cute builders (kept for old SoT CLIs)
  sot/                       ← legacy SoT CLIs (AO001-style until that handoff)
  square/                    ← headers-only Square import + Track ON rules
  prompts/PLAIN_DATA_EXCEL.md
  prompts/BOUTIQUE_DESKTOP_EFFICIENT.md   ← retired cute prompt
  prompts/BOUTIQUE_PHONE_SAFE.md          ← retired cute prompt
  prompts/GF_CLOTHES_INTAKE.md   ← GF self-upload contract (not live inventory)
  templates/from_gf/             ← HOW_TO + INTAKE_TEMPLATE + example packets
  inbox/gf_intake_reply_templates.md
  tests/run_checks.py
```

## Shop rules

- **Square Free** = on-hand inventory source of truth. Track stock ON for every item and variation. Wishlist / candidates stay off Square until Boss confirms bought and says Save.
- **Boss Excel** lives on OneDrive: `Documents/Sassy Closet/Sassy_Closet_Data.xlsx` (plain Inventory / Candidates / Orders). Not a second inventory.
- **Photos** live in `Documents/Sassy Closet/Photos/{MA}/`. Excel stores `photo_link` only — **never embed images**.
- **Live mã** = letter + growing digits (`A01`…`A99` then `A100+`). Letters: A áo Q quần V váy K áo khoác G giày B túi P phụ kiện S set O khác H tóc J trang sức. Never invent. A02 was renamed to P02 (not P05).
- **Bots draft only.** Owner posts, sends, takes Zelle, taps Square Save.
- **Cursor Cloud Agents** build here. **Kit** syncs files to OneDrive. Mini Boss launch steps: repo root `README.md` + `PROMPTS.md`.

## Scripts

Needs Python 3.10+ and `openpyxl` (`pip install -r requirements.txt` from the repo root).

```bash
# Boss plain data book from the live site export
python3 excel-kit/build_plain_data.py --out-dir ./out
./excel-kit/kit.sh pull

# Empty SoT scaffold (legacy; Dashboard!B43 morning brief formula)
python3 excel-kit/sot/build_sot_desktop.py --out-dir ./out

# Retired cute desktop Official + Wishlist (do not use for Boss daily)
python3 excel-kit/build_boutique_desktop.py --out-dir ./out

# Append / brief (need a local or OneDrive SoT path)
python3 excel-kit/sot/append_official_row.py -w ./out/Sassy_Closet_SoT.xlsx --ma AO001 --name-vi "Áo"
python3 excel-kit/sot/append_wishlist_row.py -w ./out/Sassy_Closet_SoT.xlsx --source https://example.com --what-vi "Váy"
python3 excel-kit/sot/append_order_row.py -w ./out/Sassy_Closet_SoT.xlsx --status Inquiry --ma AO001
python3 excel-kit/sot/append_bot_activity.py -w ./out/Sassy_Closet_SoT.xlsx --bot Stock --action draft --summary "note"
python3 excel-kit/sot/dashboard_brief.py -w ./out/Sassy_Closet_SoT.xlsx

# GF clothes intake (From GF packet → Photos rename + Wishlist/Official staging)
python3 excel-kit/sot/gf_intake_apply.py --help
python3 excel-kit/sot/gf_intake_apply.py --from-gf excel-kit/templates/from_gf/examples/candidate_looking_vay \
  -w ./out/Sassy_Closet_SoT.xlsx --photos-out ./out/Photos --dry-run
python3 excel-kit/sot/onedrive_from_gf_link.py --help

# Strip demo rows + Square wording
python3 excel-kit/clean_sot_demo.py path/to/Sassy_Closet_SoT.xlsx -o ./out/Sassy_Closet_SoT_cleaned.xlsx

# Square headers-only check
python3 excel-kit/square/validate_import.py excel-kit/square/square_import_template.csv

# Kit CI
python3 excel-kit/tests/run_checks.py
```

Do not commit live inventory, customer names, secrets, or a filled Square CSV. Empty data sheets are intentional.

## OneDrive sync targets

| File | Role |
| --- | --- |
| `Documents/Sassy Closet/Sassy_Closet_Data.xlsx` | ONE plain Boss book (Inventory / Candidates / Orders) |
| `Documents/Sassy Closet/Photos/{MA}/` | Folder per mã — `photo_link` only, no embeds |
| `Documents/Sassy Closet/From GF/` | PRIMARY GF self-upload inbox (Kit copies HOW_TO + template) |
| `Documents/Sassy Closet/Sassy_Closet_SoT.xlsx` | Legacy SoT (cute theme retired — do not rebuild for daily use) |
