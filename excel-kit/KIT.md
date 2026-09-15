# Kit

ONE hub named **sassycloset** for teammates. Excel on OneDrive is the **offline backup if the website dies**. Always keep `ma` + `source_link` (Taobao / e.tb.cn) plus `photo_folder`, colors, sell/cost, status — never drop link columns. Site = GF intake. Square = SoT. Cute Excel is retired.

```bash
./kit.sh save              # same as: ./kit.sh run
# or
./excel-kit/kit.sh save
python3 excel-kit/build_sassycloset_hub.py --out-dir ./out
```

`kit.sh save` (= `run`) is the one command: fetch live `GET https://sassy-closet.vercel.app/api/export` → rebuild `out/sassycloset.xlsx` (All + category sheets + Orders + Readme) → sync Photos to `out/Photos/{ma}/`.

OneDrive land path:

```
Documents/Sassy Closet/sassycloset.xlsx
Documents/Sassy Closet/Photos/{MA}/001.jpg
Documents/Sassy Closet/README.txt
```

`kit.sh save` copies into that folder only if it already exists. It does not delete other OneDrive files. Contract: `prompts/SASSYCLOSET_HUB_2026-09-07.md`. Photos: `PHOTOS.md`.

## Square.xlsx + Finance.xlsx

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

## Site env names

Intake app lives in repo `sassy-closet/` (Vercel Root Directory). Excel kit stays here.

Document **names only**. Never paste secret values into git, PRs, or chat logs.

| Env | Used by |
| --- | --- |
| `MINIBOSS_ASK_WEBHOOK_URL` | `POST /api/ask` relays `{id, question}` |
| `MINIBOSS_ASK_WEBHOOK_KEY` | Bearer / `x-miniboss-ask-key` on that webhook POST |
| `ASK_REPLY_SECRET` | Gates `POST /api/ask/reply` |
| `SASSY_DATA_DIR` | Optional local data root |
| `BLOB_READ_WRITE_TOKEN` | Vercel Blob (auto). Durable mã JSON + photo bytes |
| `BLOB_STORE_ID` | Vercel Blob store id (auto when connected; OIDC on Vercel) |
| `BLOB_ACCESS` | Optional `private` (default) or `public`; must match the Blob store |

If `MINIBOSS_ASK_WEBHOOK_URL` or `MINIBOSS_ASK_WEBHOOK_KEY` is missing, Ask uses the on-site rules draft and shows **Mini Boss offline — local draft**.

Full contracts:

- `prompts/SAVED_CARD_AND_REAL_MINIBOSS_ASK_2026-09-07.md`
- `prompts/FIND_MA_CARD_2026-09-08.md` — Tìm mã code box + full info card. Keep find-by-photo / color detect. `GET /api/ma/{code}` is read-only staged + `on_hand` (empty = staged-only, never fake Square Free).
