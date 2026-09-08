# Plain data Excel rebuild — Boss 2026-09-07 ~10:15 PM PT

> **Superseded ~10:24 PM PT.** Do not rebuild the 20-column Inventory dump or Candidates sheet. Current book is the teammate floor tracker: `Sassy_Closet_Track.xlsx` via `build_floor_track.py`. See `FLOOR_TRACK.md`.

## Outcome Boss sees
One plain Excel: `out/Sassy_Closet_Data.xlsx`
- English headers only
- No pink / emoji / cute theme / merged title art
- No embedded images (photo_link path only)
- Autofilter + freeze header row
- Thin default fonts; opens fast
- Populated from live site export

Website https://sassy-closet.vercel.app stays GF input. Excel = Boss simple mirror / edit buffer.

## Context
- Live export: GET https://sassy-closet.vercel.app/api/export (CSV)
- Photos path: Documents/Sassy Closet/Photos/{MA}/
- Mã: letter + growing digits A01…A99 then A100+. Letters: A áo Q quần V váy K áo khoác G giày B túi P phụ kiện S set O khác H tóc J trang sức
- Square Free = on-hand SoT; Excel is NOT inventory truth
- A02 was renamed to P02 (not P05). No leftover A02 rows. Never invent mã.
- Kit home: excel-kit/

## Sheets
1) Inventory — columns exactly:
ma, kind, kind_vi, size, color, color_note, color_pieces, blurb, cost_cny, cost_usd, cost_currency, sell_cny, sell_usd, sell_currency, source_link, status, square, created_at, updated_at, photo_link
Pull every row from /api/export. photo_link = Documents/Sassy Closet/Photos/{ma}/

2) Candidates — blank template:
title_note, source_link, size_note, color_note, cost_note, status, photo_note
Header + 20 empty rows. status looking/skip/bought if easy.

3) Orders — blank log:
date, ma, customer_note, pay_method, amount_usd, ship_or_meetup, status, notes
Header + 20 empty. pay cash/zelle/other. status hold/paid/shipped/done/cancel.

No Dashboard. No Bot_Activity. Skip square_import unless trivial headers-only.

## Hard stops
No invent mã/stock. No Square Save. No FB Post. No embeds. No passwords. No cute rebuilds. Do not delete Boss OneDrive files blindly.

## Build
1. excel-kit/build_plain_data.py → out/Sassy_Closet_Data.xlsx (fetch live export)
2. Update kit.sh pull (or kit.sh plain) to land this plain book instead of cute Wishlist
3. Short KIT.md / PHOTOS.md note: cute Excel retired
4. Bug check: unzip -t; openpyxl sanity; Inventory count == export; no mã cell A02; photo_link ends Photos/{ma}/; no embeds
5. Leave artifact out/Sassy_Closet_Data.xlsx

## Success
- Plain openable xlsx
- Inventory matches live export (P02 yes, A02 no)
- Kit docs/pull updated
- Report artifact path + checksum

Model already set: grok-4.6 xhigh Fast ON.
