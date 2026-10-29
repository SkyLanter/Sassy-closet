# Auto-list mã index

Logged-out browsers stay **401** on the routes that carry costs and supplier links:

- `GET /api/submissions`
- `GET /api/submissions/<mã>`
- `GET /api/ma/<mã>`
- `GET /api/export`
- `POST /api/submissions` and `PATCH /api/submissions/<mã>`

Nhung still opens those in the browser after `/admin/shop/login`. There is no service login and no new secret for the pipeline.

Auto-list reads a separate public list. It has no money fields and no supplier links.

## What auto-list calls

```
GET https://sassy-closet.vercel.app/api/ma-index
```

No header. No cookie. No new environment variable.

```json
{
  "items": [
    {
      "ma": "A01",
      "kind": "A",
      "size": "M",
      "color": "Kem",
      "status": "staged",
      "photo_count": 1,
      "created_at": "2026-01-02T00:00:00.000Z",
      "updated_at": "2026-01-03T00:00:00.000Z"
    }
  ]
}
```

Those eight fields are the whole item. Costs, sell amounts, captions, notes, and source links are not in this JSON. A landed-cost quote still needs a logged-in export; this list only tells the runner which mãs exist and their size, color, and photo count.

`run.sh` is not in this repo. Point its intake curl at `/api/ma-index` and read `.items[]`. Drop any header that sent a pipeline secret. Example:

```sh
curl -fsS "${INTAKE_BASE:-https://sassy-closet.vercel.app}/api/ma-index"
```

`INTAKE_BASE` is the host the box already uses. Do not add `INTAKE_PIPELINE_SECRET`.

## Deploy checklist (Boss, after this draft is merged)

No new Vercel variable. No new password.

1. Redeploy **intake only** (`sassy-closet`, https://sassy-closet.vercel.app). Do not deploy the sell shop for this change.
2. On the auto-list machine, change the intake URL in `run.sh` from `/api/submissions` to `/api/ma-index`. No new login.
3. Logged-out cost routes must stay 401:

```sh
curl -s -o /dev/null -w '%{http_code}\n' https://sassy-closet.vercel.app/api/submissions
curl -s -o /dev/null -w '%{http_code}\n' https://sassy-closet.vercel.app/api/export
curl -s -o /dev/null -w '%{http_code}\n' https://sassy-closet.vercel.app/api/ma/S06
```

4. The index must be 200. The body must not contain `cost_`, `source_link`, or `taobao`:

```sh
curl -fsS https://sassy-closet.vercel.app/api/ma-index | python3 -c 'import json,sys; d=json.load(sys.stdin); assert "items" in d; text=json.dumps(d).lower(); assert "cost_" not in text and "source_link" not in text and "taobao" not in text; print(len(d["items"]), "mã")'
```
