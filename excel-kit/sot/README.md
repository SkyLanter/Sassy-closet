# SoT package — one desktop workbook

Scripts that read and append `Documents/Sassy Closet/Sassy_Closet_SoT.xlsx`.

Square Free = on-hand inventory source of truth.  
Official Excel = working copy / mã index / captions.  
Never invent mã. Never embed images. `photo_link` last on Wishlist.

```
excel-kit/sot/
  workbook.py              shared locate / header map / append
  append_official_row.py   Official ( --ma required or ask Stock )
  append_wishlist_row.py   Wishlist ( Link/source if available )
  append_order_row.py      Inquiry|Reserved|Paid|Shipped|Picked up|Cancelled
  append_bot_activity.py   append if Bot_Activity exists, else skip + note
  gf_intake_apply.py       GF From GF packet → photos + Wishlist/Official staging
  dashboard_brief.py       print cached Dashboard values; else copy B43
  build_sot_desktop.py     empty SoT scaffold (no fake stock)
  FROM_GF_WATCH.md         how Kit scans From GF (no daemon in this repo)
```

## Locate the book

1. `--workbook path/to/Sassy_Closet_SoT.xlsx`
2. `$SASSY_SOT`
3. OneDrive `Documents/Sassy Closet/Sassy_Closet_SoT.xlsx`

Lean desktop books (`Ma_List` / `Candidates`) work as a fallback for Official / Wishlist appends.

## Examples

```bash
# Official — mã is mandatory
python3 excel-kit/sot/append_official_row.py -w ./out/Sassy_Closet_SoT.xlsx \
  --ma AO001 --name-vi "Áo hồng" --size M --color đen --qty 1 --status Available

# Wishlist — must pass a reopen link or admit there is none
python3 excel-kit/sot/append_wishlist_row.py -w ./out/Sassy_Closet_SoT.xlsx \
  --source "https://item.taobao.com/..." --what-vi "Váy hoa" --size "M 88cm"

# Orders
python3 excel-kit/sot/append_order_row.py -w ./out/Sassy_Closet_SoT.xlsx \
  --status Inquiry --ma AO001 --channel Facebook --size M

# Bot log (skips cleanly if the sheet is missing)
python3 excel-kit/sot/append_bot_activity.py -w ./out/Sassy_Closet_SoT.xlsx \
  --bot Stock --action draft --summary "Save proposal AO001" --ma AO001

# Morning brief (needs Excel-cached values, or Boss copies Dashboard!B43)
python3 excel-kit/sot/dashboard_brief.py -w ./out/Sassy_Closet_SoT.xlsx

# GF clothes intake (PRIMARY: From GF packet; still off Square)
python3 excel-kit/sot/gf_intake_apply.py --from-gf ./excel-kit/templates/from_gf/examples/candidate_looking_vay \
  -w ./out/Sassy_Closet_SoT.xlsx --photos-out ./out/Photos --dry-run
```
