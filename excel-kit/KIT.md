# Kit

Floor tracker for teammates on OneDrive: `Sassy_Closet_Track.xlsx` (Track / Orders / Readme). Cute Excel is retired. Boss opens the same plain book via OneDrive + Excel. Site = GF intake. Square = SoT.

```bash
python3 excel-kit/build_floor_track.py --out-dir ./out
./excel-kit/kit.sh pull    # same as: kit.sh plain | kit.sh track
```

`kit.sh pull` lands `Sassy_Closet_Track.xlsx` only. It does not delete other OneDrive files. Contract: `prompts/FLOOR_TRACK.md`. Photos: `PHOTOS.md`.
