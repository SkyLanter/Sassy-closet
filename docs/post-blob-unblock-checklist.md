# After the Blob store is unblocked: recovery checklist
Read-only. Run only AFTER Boss unblocks the Vercel Blob store. One command does all of it:

    scripts/post_blob_unblock_check.sh      # GET only, no tokens, no writes; ends with POST-UNBLOCK CHECK: PASS|FAIL

| # | URL | PASS looks like |
|---|-----|-----------------|
| 1 | https://sassy-closet.vercel.app/ | 200, form shows. The FX label is the real one, not "Tỷ giá mặc định … kho đang không đọc được" |
| 2 | https://sassy-closet.vercel.app/api/submissions | **401** logged out (240b: rows have costs). Logged in at /admin/shop/login: 200 with a real mã list, no `"storeUnavailable":true` |
| 3 | https://sassy-closet.vercel.app/api/fx | 200 with `usd_cny` |
| 4 | https://sassy-closet.vercel.app/api/submissions/S06 and /api/ma/S06 | **401** logged out. Logged in: 200 with mã S06 |
| 5 | https://sassy-closet.vercel.app/api/export | **401** without login (piece 240 locks the costs CSV). If you're logged in at /admin/shop/login, it's a 200 CSV. The script only checks the logged-out status |
| 5b | https://sassy-closet.vercel.app/api/ma-index | **200** with `items` (mã, kind, size, color, status, photo count, timestamps). Body must not contain `cost_`, `source_link`, or `taobao`. No login. See `sassy-closet/docs/MA_INDEX.md` |
| 6 | https://sassy-closet.vercel.app/api/photos/<photo path> | Manual: 200 image (needs a path from the logged-in list) |
| 7 | Find-mã (POST photo) | Manual: on the intake page, use "find mã" with a known photo. It should return a match, not the store-down message. The script skips it because it's a POST |
| 8 | https://sassy-closet-shop.vercel.app/api/health | `"reading":"blob"`, `"blob":{"readable":true}` (not `"seed"`) |
| 9 | https://sassy-closet-shop.vercel.app/m/S06 | 200 and shows **$25** (S06 lock) |
| 10 | https://sassy-closet-shop.vercel.app/m/K03 | **404** (held mã stays hidden). A 200 here means tell Boss immediately |
| 11 | /m/A01 /m/A02 /m/S01 /m/P01 on the shop | 200 |

## Still 500 / seed after the unblock?
1. Wait a few minutes and rerun (CDN/cache). Then check the Vercel dashboard → Storage → Blob store status shows active.
2. Vercel → each project (sassy-closet, sassy-closet-shop) → Settings → Environment Variables. Confirm `BLOB_READ_WRITE_TOKEN` (or the store link) is still present for Production. Never paste the token anywhere.
3. If env changed: redeploy the current production deployment (Vercel → Deployments → Redeploy). **Boss only.**
4. Last resort, **Boss yes required**: create a new Blob store, connect it, and copy the data. Never do this silently, because it risks data loss.
5. The intake page now shows a clear Vietnamese message (503) instead of a blank 500 while the store is down. Saves still refuse, so no data is overwritten.

## Not in this checklist (never without Boss)
No Blob writes, price/FX saves, Meta, Square, domain changes, merges or deploys.
