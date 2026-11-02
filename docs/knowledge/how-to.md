# How to do a job

Commands below are the ones the repo already prints. They do not deploy, post, or change a live price. A step that is not in the repo is omitted on purpose.

## Read the shop before editing

1. Read [README.md](README.md) in this folder, then [rules.md](rules.md).
2. Confirm you are on a branch, not committing to `main`.
3. If the task touches `data/held.json`, S06's dollar, or a public page, stop and treat it as a Boss decision.

## Run the full local recheck without skipped app tests

From the repo root, after `node_modules` exists in both apps:

```bash
npm ci --prefix sassy-closet
npm ci --prefix sassy-closet-shop
scripts/hard_recheck.sh --base origin/main
```

Pass `--base origin/main`. Without `--base`, a clone that does not contain `eb8a143` (this one does not) diffs against the root commit, and the privacy and `held.json` steps fail on old history. See [pitfalls.md](pitfalls.md). The script prints `HARD RECHECK: PASS` or `FAIL`. Logs are under `out/recheck/`.

`npm ci` needs a network install. The recheck script itself does not fetch the shop.

Excel kit and dataset CI, separately:

```bash
pip install -r requirements.txt
python3 excel-kit/tests/run_checks.py
python -m pytest scripts/tests -q
```

## See what is waiting, without writing live data

```bash
python3 scripts/desk_status.py --fixture ./desk.json
python3 scripts/restock_note.py --fixture ./catalog.json --note ./out/restock-note.md
```

The README says `--read-prs` asks `gh` for open pull request numbers and does not write the HTML page. A fixture path is required by those examples. Do not point them at production.

## Check captions offline

`scripts/caption_lint.py` reads a local `.json` or `.csv` with `url`, `platform`, and `text`. It does not log into Meta. Exit 0 is all PASS, 1 is any WARN, 2 is any FAIL or a usage error. `--warn-ok` lets WARN exit 0. The header in that file is the rule list.

`scripts/caption_gia_check.py` is a shim onto the linter. Prefer `caption_lint.py`.

## Check held mãs

The list is `data/held.json`. `scripts/held_policy.py` loads it. It is a library, not a command. A report between two fixtures:

```bash
python3 scripts/held_diff.py --help
```

Use that `--help` text. Do not pass a path that writes `data/held.json`.

A public 404 for a held mã is what `getProduct` does after `isOffLiveSell`. Confirm with the unit tests `sassy-closet-shop/tests/held-incomplete.test.ts` rather than by editing the list.

## Price questions

Read `sassy-closet/lib/pricing.ts` and `scripts/autolist.py` before quoting a formula. The flat 25% path and the tiered path are both in the intake file. S06's displayed dollar is the lock, not a fresh quote.

`python3 scripts/price_drift_report.py` regenerates the comparison described in `docs/price-drift-boss-decision.md`. The doc says it applies no dollars.

`python3 scripts/seed_vs_live_report.py` prints and writes nothing (`docs/seed-vs-live-mismatch.md`).

Do not run these without Boss's yes:

- `sassy-closet-shop/scripts/apply-hub-live.ts` (`npm run catalog:hub`) and `unlock-p02-p05-28.ts` write the live catalog as soon as they run. They have no dry-run flag and no phrase check.
- `apply-price-bump-20.ts` writes Blob prices when `--apply` is passed. It has no phrase check.
- `intake:sell-backfill` writes only with `--apply-sell` or `--apply-d05` and the exact `BOSS_CONFIRM` phrase in its header.

## Build a desktop workbook locally

```bash
pip install -r requirements.txt
python3 excel-kit/sot/build_sot_desktop.py --out-dir ./out
python3 excel-kit/build_boutique_desktop.py --out-dir ./out
python3 excel-kit/sot/dashboard_brief.py -w ./out/Sassy_Closet_SoT.xlsx
```

`/out/` is gitignored (a few older files under `out/` are tracked anyway; see [script-index.md](script-index.md)). Copying into OneDrive is Kit's job after merge (`README.md`). This command does not do that copy.

## Intake health and the open link

`sassy-closet/tests/open-link-health-guards.test.ts` is the regression for "no password, no 401, noindex on `/api` and `/admin`". Run it with the intake test script:

```bash
npm test --prefix sassy-closet
```

`docs/post-blob-unblock-checklist.md` is the GET list for after Boss unblocks Blob. It includes `/api/ma/S06` on intake and `/m/S06` plus `/m/K03` on the shop. Run `scripts/post_blob_unblock_check.sh` only as that doc describes. It does not POST.

## Add a script check

Put it under `scripts/`, with a module docstring that says whether it writes. Add a test under `scripts/tests/`. `dataset-checks.yml` runs that whole directory on pull requests. Keep `data/held.json` unchanged unless the task is the held list and Boss has said yes.

## Open a pull request

Branch from current `main`. Open a draft. Do not merge, close, or approve it. The separate-agent PASS or FAIL comment is required before the work counts as done ([rules.md](rules.md)). Boss merges.
