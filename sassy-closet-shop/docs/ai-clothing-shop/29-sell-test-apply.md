# Official #29 APPLY — sell-test (kit-lane)

Quiet apply of [SkyLanter/Sassy-closet#29](https://github.com/SkyLanter/Sassy-closet/pull/29) `AI_CLOTHING_SHOP_APPLY_TO_SELL_TEST.md` on this sell-test shop. Kelly Ying paper / ink / gold + Be Vietnam / Cormorant stay. Intake (`sassy-closet.vercel.app`) is untouched.

Observed trap (Official crawl of stale Vercel): admin **next-mã tiles** A03, Q01, V01, K02, G01, B01, P06, H02, J01, S02, O01, D01. Those codes are not stock.

## Mini Boss override (do not collapse)

Official §A wants Add tiles gone, Save outside the hub ten → 4xx, `/m/A03` 404, featured count 10.

**Boss Add stays open.** A03+ must Save and appear on the shop after the receipt. Official “do not mint A03” is about **media/kit not inventing stock** and about **next-mã trap tiles**, not about closing Add.

| Official #29 | Landed here |
| --- | --- |
| Kill Add A03 / Add Q01 / Pants → Q01 tiles | Add heading is **Add mã**. Letter picker is `A · Tops` only. Submit is **Save new mã**. Prediction is “Assigned on Save — not a shop tile.” `data-next-ma-trap="off"` |
| Save outside allowlist → 4xx | Official `AO001` / invalid letters 400. Save of a code **not in the catalog yet** 400. After Boss Add, that mã Saves (A03+) |
| `/m/A03` 404 / grid 10 | Until Add. After Add, A03 is a real piece. Seed stays the hub ten. Do not invent Q01/D01 for empty categories |
| Blob + `revalidatePath` after Save | Receipt `{ ok, blobWritten, catalogSha, revalidated }`. No `/tmp` silent save |
| Uploads > 4.5 MB | Client + Server Action refuse with a loud 4.5 MB error (not a silent drop). `@vercel/blob` stays server-only |
| Export JSON | `/admin` settings **Export catalog.v1** + `data-catalog-export="json"` |
| `m.me?ref=A01` + mã in context | Product CTAs and cards use `?ref={ma}&text=`. Header/footer stay generic `?text=` |
| Hold P02/P05, no cart | Unchanged. No Shop now / Add to cart |
| Per-color hex admin; shop swatches | Admin hex boxes. Shop stays **text-only names** (PR #19 / WCAG — Official “no names on discs” is admin discs, not deleting readable chips) |
| Fancy motion + chrome | `announce-fade` / `shimmer` / `cta-shine` / `site-header` view-transition stay |

## Out of scope (rejected)

- Intake tabs, Square Save, Facebook Send, passwords
- Inventing Q01 / D01 so Pants / Dresses look stocked
- Flipping test `noindex`
- Writing Excel / OneDrive / intake

Gate: `npm run smoke:kit-apply` plus the existing admin / dropship / bugcheck / origin LOOK smokes.
