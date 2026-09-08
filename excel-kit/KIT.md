# Kit

ONE hub named **sassycloset** for teammates. Boss opens Excel / OneDrive. Site = GF intake. Square = SoT. Cute Excel is retired.

```bash
./kit.sh save              # same as: ./kit.sh run
# or
./excel-kit/kit.sh save
python3 excel-kit/build_sassycloset_hub.py --out-dir ./out
```

`kit.sh save` (= `run`) is the one command: fetch live `GET https://sassy-closet.vercel.app/api/export` → rebuild `out/sassycloset.xlsx` (All + category sheets + Orders + Readme) → sync Photos to `out/Photos/{ma}/`.

OneDrive land path (Build lands later):

```
Documents/sassycloset/
  sassycloset.xlsx
  Photos/{MA}/001.jpg
  README.txt
```

`kit.sh save` copies into that folder only if it already exists. It does not delete other OneDrive files. Contract: `prompts/SASSYCLOSET_HUB_2026-09-07.md`. Photos: `PHOTOS.md`.
