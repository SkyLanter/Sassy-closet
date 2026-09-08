# Floor tracker Excel — Boss 2026-09-07 ~10:24 PM PT

## Outcome
One plain Excel: `out/Sassy_Closet_Track.xlsx`
- Opens via OneDrive + Excel
- Primary audience = teammates (Inventory / Inbox / Caption / Buy Research / Build)
- Simple floor tracker, NOT a full Boss data-entry dump
- English headers, no pink / emoji / cute theme / merged title art
- No embeds (`photo_folder` path only)
- Autofilter + freeze header on Track / Orders

Website https://sassy-closet.vercel.app = GF intake. Square Free = on-hand SoT. Excel is not inventory truth.

## Sheets (keep thin)
1) **Track** columns only:
`ma, kind, colors, sell_usd, cost, currency, square, status, flag, next_desk, photo_folder, source_link`
- Populate from live `/api/export`
- `photo_folder` = `Documents/Sassy Closet/Photos/{ma}/`
- `flag` / `next_desk` empty by default (ops can fill). Copy a flag only if the export already has one. Do not invent stock.

2) **Orders** — blank thin log:
`date, ma, customer, pay, amount_usd, ship_or_meetup, status, notes`
Header + 20 empty. pay cash/zelle/other. status hold/paid/shipped/done/cancel.

3) **Readme** — 4–5 lines: for teammates; Boss opens via OneDrive; site=GF intake; Square=SoT; no invent mã / no Save / no Post

## Drop
Candidates sheet. 20-column Inventory dump. Cute anything.

## Hard stops
No invent mã/stock. A02 was renamed to P02 (not P05). No Square Save. No FB Post. No embeds. No passwords. No cute rebuilds. Do not delete Boss OneDrive files blindly.

## Build
1. `excel-kit/build_floor_track.py` → `out/Sassy_Closet_Track.xlsx` (fetch live export)
2. `kit.sh pull` (or `plain` / `track`) lands this book
3. KIT.md: floor tracker for teammates on OneDrive
