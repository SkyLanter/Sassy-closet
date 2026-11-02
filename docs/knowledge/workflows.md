# Workflows and what runs when

The script-by-script header list is [script-index.md](script-index.md). This page is the schedule and the entry points.

## GitHub Actions

There is no `schedule:` and no `cron:` under `.github/workflows`. Nothing in CI runs the daily shop check, midnight QC, or the Muse pack.

| Workflow | When | What it runs |
| --- | --- | --- |
| `.github/workflows/dataset-checks.yml` | Pull request, and push to `main` | `pytest scripts/tests`, then three shop-link flag scripts on fixtures. No live intake and no live catalog. |
| `.github/workflows/excel-kit.yml` | Pull request, and push to `main` | `python3 excel-kit/tests/run_checks.py` |
| `.github/workflows/sassy-closet.yml` | Push or pull request that touches `sassy-closet/**`, `data/held.json`, or that workflow | In `sassy-closet/`: `npm ci`, `npm test`, `npm run typecheck`, `npm run build` |
| `.github/workflows/sassy-closet-shop.yml` | Same, for `sassy-closet-shop/**`, `data/held.json`, or that workflow | `npm ci`, `npm test`, `npm run build`. No typecheck step. The build step makes up to 3 attempts because of a next/font Turbopack flake named in the workflow. |

Neither app workflow lists `shared/**` in its paths, so a change only under `shared/` (for example `shared/tiered-pricing.ts`, which tests in both apps read) does not start the app test jobs.

`scripts/hard_recheck.sh` is not a workflow step on `main`. Open PR #232 is titled as adding it to pull requests. It was not merged on 2026-11-02.

`docs/checkpoints/START-HERE.md` describes a daily shop-check workflow at 22:15 UTC as part of unmerged draft pieces 27 and 29. That workflow file is not in `.github/workflows` now.

## Hard recheck

`scripts/hard_recheck.sh` is local. It does not use the network. Logs go under gitignored `out/recheck/<stamp>/`.

Steps, in order (`scripts/hard_recheck.sh`):

| Step | Required | What |
| --- | --- | --- |
| `git` | yes | Branch name, HEAD, and conflict markers. |
| `pytest` | yes | `scripts/run_tests.sh`, which is `pytest` plus a junit XML under `out/test-results/`. |
| guard notes | no | Looks in the pytest log for four test modules. A missing file is SKIP. |
| `privacy` | yes | `scripts/privacy_scan.py --git-diff <base>..HEAD`. PASS only when the log says CLEAN. |
| `intake-npm-test`, `intake-tsc` | yes | `npm test` and `npx tsc --noEmit` in `sassy-closet`. |
| `shop-npm-test`, `shop-tsc` | yes | Same in `sassy-closet-shop`. |
| `diff-stat` | no | `git diff --stat` against the base. |
| `working-tree` | no | Porcelain status. WARN if dirty. Does not fail the run. |
| `held-json` | yes | FAIL if `data/held.json` differs from the base. |
| `tip-status` | no | `scripts/overnight_tip_status.sh` if present. INFO only. |

If `node_modules` is missing, the npm steps are SKIP and the script can still print PASS, because SKIP is not FAIL (`Exit 0 only when every required step is PASS or SKIP`). A knowledge-lane recheck that must not skip installs dependencies first. See [how-to.md](how-to.md).

Default base: `eb8a143` if that commit exists, else the root commit. This clone does not have `eb8a143`. Pass `--base`. See [pitfalls.md](pitfalls.md).

## Package scripts

Intake `sassy-closet/package.json`: `dev` (port 3000), `build`, `start`, `test` (`node --test` on `tests/*.test.ts`), `typecheck`, `intake:sell-backfill`.

Shop `sassy-closet-shop/package.json`: `dev` and `build` write a local product manifest first. `test` runs `tests/*.test.ts`. Most `smoke:*`, `prove:*`, and `catalog:*` names map to files under `sassy-closet-shop/scripts/`. Exceptions: `smoke:origin` runs `docs/ai-clothing-shop/qa/qa_selltest_origin_gate.py`, and `smoke:fb-rank` and `catalog:fb-rank` point at `scripts/smoke-fb-rank.ts` and `scripts/stamp-fb-rank.ts`, which are not in the checkout. Many of the files that do exist have no header comment; the npm script name is the only label in git. Read the file before running it. `catalog:hub` points at `apply-hub-live.ts`, which writes the live catalog. Do not run it as a check.

## Daily and local sequences the repo documents

These commands exist. The repo does not say which clock runs them.

| Job | Command | Writes |
| --- | --- | --- |
| Desk status | `python3 scripts/desk_status.py` | README: does not write Blob, intake, Meta, or `held.json`. `--page` writes HTML from files already loaded. |
| Restock note | `python3 scripts/restock_note.py` | A markdown note. Does not change catalog, prices, or held. |
| Daily shop check | `scripts/run_daily_shop_check.sh` | `reports/daily/daily-<utc-date>.md` and `.json` by default. |
| Daily summary draft | `scripts/daily_summary_draft.py` | A local draft. Luxubu line reads `out/muse/luxubu-status-<date>.json`. |
| Midnight QC | `scripts/midnight_qc.py` | `summary.json` and `data-ok.md` under its output dir. Header says it does not fetch Taobao, does not write `data/held.json`, and does not replace the hub sheet parser. |
| Caption lint | `python3 scripts/caption_lint.py` | Prints PASS / WARN / FAIL. No network. |
| Muse pack sections | `scripts/muse_pack_sections.py` | Local files only, and only with `--write`. |
| Luxubu status | `scripts/luxubu_status_record.py` | Local JSON from flags. No network. |
| Kit checks | `python3 excel-kit/tests/run_checks.py` | Test output. |
| SoT scaffold | `python3 excel-kit/sot/build_sot_desktop.py --out-dir ./out` | A workbook under `./out`. README's live OneDrive copy is a Kit sync, not this command by itself. |
| Morning brief | `python3 excel-kit/sot/dashboard_brief.py -w <xlsx>` | Prints the brief or the formula. Does not calculate Excel. |

`scripts/live_shop_smoke.sh` and `scripts/post_blob_unblock_check.sh` GET public URLs. They are not part of `hard_recheck.sh`. The unblock checklist says not to POST.

## Intake routes

| Path | Role |
| --- | --- |
| `/` | Four-tab intake. |
| `/admin` | CSV page. Open, noindex. |
| `/admin/shop` | Shop catalog desk. Open, noindex. |
| `/admin/shop/login` | Old URL. Sent back to the desk. |
| `POST /api/submissions`, `PATCH /api/submissions/[ma]` | Save. Open. |
| `GET /api/submissions`, `GET /api/export`, `GET /api/ma/[code]` | Reads, including costs. Open and noindex on main. |
| `POST /api/ask`, `GET /api/ask/[id]`, `POST /api/ask/reply` | Ask relay. Reply needs `ASK_REPLY_SECRET`. |
| `GET /api/health` | `reading` is blob, local, or ephemeral. No costs. |
| `POST /api/find-ma`, `POST /api/taobao-lookup` | Lookups. Read the route before calling them. |
| `GET /api/photos/[...path]` | Photo bytes. |

## Sell-shop routes

| Path | Role |
| --- | --- |
| `/` | Lookbook. |
| `/m/[ma]` | Product. 404 when the mã is not in the visible catalog (held, unknown, or sold-filtered). |
| `/c/[slug]` | Category. |
| `/how-to-buy`, `/meetup-ship` | Redirect to `/` (`redirect("/")` in each page). |
| `/admin` and `/admin/*` | 404 for customers (`proxy.ts`, `app/admin/layout.tsx`). |
| `/api/health` | `reading` blob, kv, local, or seed. |
| `/api/admin/*` | 404. Route files for add, catalog, catalog import and export, hold, remove, rename, save, and settings exist, but `proxy.ts` (`customerAdminProxyDecision`) and each handler (`customerAdminApiClosed`) return 404. Only `/api/admin/revalidate` passes, and it checks the revalidate secret. Catalog edits go through intake `/admin/shop`. |
| `/share/m/[ma]`, `/share/c/[slug]` | Share cards. |
| `/products/[ma]/[file]` | Product image route. |

Env **names** only, never values: intake Blob and Ask names in `excel-kit/KIT.md` and `sassy-closet/README.md`; shop catalog token and revalidate names in `sassy-closet/docs/SHOP_ADMIN.md`.
