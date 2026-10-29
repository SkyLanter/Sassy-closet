# Machine read of the intake mã list

Logged-out browsers stay locked. These routes are still **401** with no shop-admin cookie and no bearer:

- `GET /api/submissions`
- `GET /api/submissions/<mã>`
- `GET /api/ma/<mã>`
- `GET /api/export`
- `POST /api/submissions` and `PATCH /api/submissions/<mã>`

Nhung's browser uses the shop-admin session (`/admin/shop/login`, cookie `sc_admin`). That login is unchanged.

Auto-list is a machine. It has no browser cookie. It may send a bearer on **GET only**.

## Header auto-list must send

```
Authorization: Bearer <INTAKE_PIPELINE_SECRET>
```

That is the only header. The secret is not read from a query string, a cookie, or any other header name.

`POST` and `PATCH` ignore the bearer. The token cannot save a mã. `/api/shop-catalog` and `/admin/shop` ignore it too.

If `INTAKE_PIPELINE_SECRET` is unset, empty, shorter than 24 characters, longer than 256, or contains a space or other non-printable character, the bearer does nothing and the route stays 401.

## What Boss sets on Vercel before deploy

Intake project only (`sassy-closet`, https://sassy-closet.vercel.app, Root Directory `sassy-closet`). Do not set this on the sell shop.

1. Make a secret. At least 24 characters, no spaces. `openssl rand -hex 32` is a good value.
2. Use a new value. Do not copy `ADMIN_PASSWORD`, `ADMIN_SESSION_SECRET`, `ASK_REPLY_SECRET`, `NEW_MA_WEBHOOK_TOKEN`, `INTAKE_DATASET_SYNC_WEBHOOK_KEY`, or a Blob token. Those sign the browser session, answer Ask, or are sent off the server. A separate name means a leak of the auto-list machine is not a leak of Nhung's login.
3. Vercel → project **sassy-closet** → Settings → Environment Variables.
4. Name: `INTAKE_PIPELINE_SECRET`. Paste the raw value, with no quotes around it. Production, and Preview if a preview should answer auto-list.
5. Redeploy **intake only** after this change is merged. This branch is a draft. Do not merge or deploy it from the agent.
6. On the machine that runs auto-list, export the same value as `INTAKE_PIPELINE_SECRET`. Do not commit it and do not put it in the script.

Until step 4 and the redeploy, auto-list still gets 401. That is fail-closed.

## Local auto-list `run.sh`

`run.sh` is not in this repo. Add one flag to the curl that reads the mã list:

```sh
-H "Authorization: Bearer ${INTAKE_PIPELINE_SECRET}"
```

Full read, secret only from the environment:

```sh
curl -fsS \
  -H "Authorization: Bearer ${INTAKE_PIPELINE_SECRET}" \
  "${INTAKE_BASE:-https://sassy-closet.vercel.app}/api/submissions"
```

The same header works for `GET /api/submissions/<mã>`, `GET /api/ma/<mã>`, and `GET /api/export` when the script needs one mã or the CSV. The in-repo freshness check (`scripts/freshness_check.py`) sends this header when the env is set, and only on the intake submissions URL.

## Check after deploy

Logged-out, no header, must stay 401:

```sh
curl -s -o /dev/null -w '%{http_code}\n' https://sassy-closet.vercel.app/api/submissions
curl -s -o /dev/null -w '%{http_code}\n' https://sassy-closet.vercel.app/api/export
```

Machine GET must be 200. Do not paste the body into chat:

```sh
curl -s -o /dev/null -w '%{http_code}\n' \
  -H "Authorization: Bearer ${INTAKE_PIPELINE_SECRET}" \
  https://sassy-closet.vercel.app/api/submissions
```

A write with the bearer must stay 401:

```sh
curl -s -o /dev/null -w '%{http_code}\n' -X POST \
  -H "Authorization: Bearer ${INTAKE_PIPELINE_SECRET}" \
  -H 'content-type: application/json' \
  --data '{}' \
  https://sassy-closet.vercel.app/api/submissions
```

The logged-out privacy scripts (`scripts/post_deploy_privacy_check.sh`, `scripts/post_blob_unblock_check.sh`) must keep getting 401. They do not send this header.

## Not this token

The sell-shop button that pulls staged rows still calls intake with no bearer, so that button stays 401 until a later change. This token is for auto-list.
