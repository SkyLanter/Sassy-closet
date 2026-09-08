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
