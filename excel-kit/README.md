# excel-kit

Builders, SoT CLIs, and prompts for Sassy Closet Excel books. **This GitHub repo is where Cursor Cloud Agents change the kit.** Kit syncs generated `.xlsx` files to OneDrive `Documents/Sassy Closet/`.

Square Free is the on-hand inventory source of truth. Official Excel (`Sassy_Closet_SoT.xlsx`) is the ONE desktop working copy / mã index / captions — not a second inventory.

## Layout

```
excel-kit/
  README.md
  PROMPTS.md                 ← Boss / Mini Boss paste these into Cloud Agents
  EFFICIENCY.md
  DESIGN_NOTES.md
  schema.py
  clean_sot_demo.py
  build_boutique_desktop.py
  sot/                       ← ONE workbook: Sassy_Closet_SoT.xlsx
  square/                    ← headers-only Square import + Track ON rules
  prompts/BOUTIQUE_DESKTOP_EFFICIENT.md
  prompts/BOUTIQUE_PHONE_SAFE.md
  prompts/GF_CLOTHES_INTAKE.md   ← GF self-upload contract (not live inventory)
  prompts/SAVED_CARD_AND_REAL_MINIBOSS_ASK_2026-09-07.md
  KIT.md                         ← site env names (no secret values)
  templates/from_gf/             ← HOW_TO + INTAKE_TEMPLATE + example packets
  inbox/gf_intake_reply_templates.md
  tests/run_checks.py
```

## Shop rules

- **Square Free** = on-hand inventory source of truth. Track stock ON for every item and variation. Wishlist / candidates stay off Square until Boss confirms bought and says Save.
- **Official Excel** lives on OneDrive: `Documents/Sassy Closet/Sassy_Closet_SoT.xlsx` (working copy / mã index / captions — **not** second inventory).
- **Photos** live in `Documents/Sassy Closet/Photos/` named `#001.jpg` / `AO001.jpg`. Excel stores `photo_link` only — **never embed images**. `photo_link` is last on Ma_List, Candidates, and SoT Wishlist.
- **Mã** = `AO` / `QU` / `VA` / `AK` / `GI` / `PK` / `SET` + 3 digits. Never invent stock. Never reuse a Sold mã. Ask Stock (Dashboard `B21:B27`).
- **Bots draft only.** Owner posts, sends, takes Zelle, taps Square Save.
- **Cursor Cloud Agents** build here. **Kit** syncs files to OneDrive. Mini Boss launch steps: repo root `README.md` + `PROMPTS.md`.

## Scripts

Needs Python 3.10+ and `openpyxl` (`pip install -r requirements.txt` from the repo root).

```bash
# Empty SoT scaffold (Dashboard!B43 morning brief formula)
python3 excel-kit/sot/build_sot_desktop.py --out-dir ./out

# Lean desktop Official + Wishlist
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
| `Documents/Sassy Closet/Sassy_Closet_SoT.xlsx` | ONE desktop book (Official / Wishlist / Orders / Dashboard) |
| `Documents/Sassy Closet/Sassy_Closet_Official_desktop.xlsx` | Lean desktop Ma_List / Orders / Bot_Activity |
| `Documents/Sassy Closet/Sassy_Closet_Wishlist_desktop.xlsx` | Lean desktop Candidates |
| `Documents/Sassy Closet/Photos/` | `#001.jpg` / `AO001.jpg` — links only in Excel |
| `Documents/Sassy Closet/From GF/` | PRIMARY GF self-upload inbox (Kit copies HOW_TO + template) |
