# sassycloset hub — Boss 2026-09-07 ~10:33 PM PT

## Outcome

ONE hub named **sassycloset**. Build lands later on OneDrive:

```
Documents/sassycloset/
  sassycloset.xlsx
  Photos/{MA}/001.jpg…
  README.txt
```

Website https://sassy-closet.vercel.app = GF intake. Square Free = on-hand SoT. Excel is not inventory. Cute / pink / embeds are retired.

## sassycloset.xlsx — category sheets inside the main file

1. **All** — every mã from live `GET https://sassy-closet.vercel.app/api/export`  
   cols: `ma, kind, colors, sell_usd, cost, currency, square, status, flag, next_desk, photo_folder, source_link`  
   `photo_folder` = `Documents/sassycloset/Photos/{ma}/`  
   `flag` / `next_desk` empty unless the export already has them.

2–12. Category sheets (headers even if empty). Filter **All** by kind letter:

| Sheet | kind |
| --- | --- |
| A_Ao | A |
| Q_Quan | Q |
| V_Vay | V |
| K_Khoac | K |
| G_Giay | G |
| B_Tui | B |
| P_PhuKien | P |
| S_Set | S |
| O_Khac | O |
| H_Toc | H |
| J_TrangSuc | J |

13. **Orders** — blank log: `date, ma, customer, pay, amount_usd, ship_or_meetup, status, notes` (+20 empty)

14. **Readme** — hub rules (teammates; Boss opens Excel/OneDrive; site=GF intake; Square=SoT; no invent mã / no Save / no Post)

Freeze + autofilter on data sheets. Plain only — no cute / pink / embeds.

## kit.sh save (= run)

One command: fetch live export → rebuild `out/sassycloset.xlsx` (all sheets) → sync Photos to `out/Photos/{ma}/`.

Document OneDrive land path `Documents/sassycloset/`.

Alias: `kit.sh run` → same as `save`.

## Hard stops

- No invent mã.
- No Square Save.
- No FB Post.
- No passwords.
- No cute.
- A02 renamed historically — live has no A02; P02 and P05 are separate. Leftover A02 fails the build.

## Success

- `out/sassycloset.xlsx` artifact
- `kit.sh save` works + `unzip -t` + openpyxl sanity + All row count = export
- Category sheets exist
- PR + report sha256
