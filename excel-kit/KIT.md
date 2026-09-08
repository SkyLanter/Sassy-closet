# Kit

Bought / on-hand + tax books (Boss 2026-09-07 ~11:30 PM PT).

```bash
python3 excel-kit/build_square_finance.py --out-dir ./out
./excel-kit/kit.sh square    # same as: kit.sh finance | kit.sh books
```

`kit.sh square` rebuilds `out/Square.xlsx` + `out/Finance.xlsx` and copies them into the shop folder only if it already exists. It does not delete other OneDrive files.

OneDrive land path:

```
Documents/Sassy Closet/Square.xlsx
Documents/Sassy Closet/Finance.xlsx
```

On_Hand starts empty. Staged site mãs are not bought. Finance starts empty — no invented sales. Square Free = SoT. No Square Save.

Contract: `prompts/SQUARE_AND_FINANCE_EXCEL_2026-09-07.md`.
