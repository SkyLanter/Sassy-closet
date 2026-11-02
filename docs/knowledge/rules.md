# Hard rules

These are the rules the repo enforces or states. Each one names a file. A pull request that is still open does not override them.

## Drafts and Boss

- Bots draft only. The owner posts, sends, takes Zelle, and taps Square Save (`README.md`, `excel-kit/schema.py` `BOTS_DRAFT_ONLY`).
- Boss yes/no is Slack `#shop-decisions` (`README.md`). This repo does not contain that Slack history.
- Merged PR #203's body says "Boss decides. Do not merge without Boss yes."
- Cloud agents open pull requests. Kit syncs workbooks after merge (`README.md`). A pull request does not deploy production (`README.md`).
- Do not commit live Official rows, customer names, Square tokens, or a filled import CSV (`README.md`).

## No live writes from a check

The root README's desk status and restock note say those commands do not write Blob, intake, Meta, or `data/held.json`. The same sentence is on many script headers in [script-index.md](script-index.md). A script that writes live data is a write tool. Examples: `sassy-closet-shop/scripts/apply-price-bump-20.ts` (writes Blob with `--apply`), `migrate-covers-to-blob.ts` (`--live`), `apply-hub-live.ts` and `unlock-p02-p05-28.ts` (call `writeLiveCatalogDocument` when run, with no dry-run flag and no phrase check), and `intake-sell-backfill.ts`. Do not run a write tool against production without Boss's yes, plus the exact phrase where the tool requires one.

`sassy-closet/scripts/intake-sell-backfill.ts` is dry-run unless `--apply-sell` or `--apply-d05` is set and `BOSS_CONFIRM` is the exact phrase in that file's header.

## Prices

- Do not invent a sell price. New prices are a Boss decision (`docs/price-drift-boss-decision.md`: "No dollars applied. Boss picks which column wins.").
- S06 stays $25 (`sassy-closet/lib/publish-guard.ts`, `sassy-closet/lib/pricing.ts`, `scripts/caption_lint.py`).
- Do not change `data/held.json` in a drive-by edit. `scripts/hard_recheck.sh` fails the run when `data/held.json` differs from the base.

## Held and Taobao

- Held-incomplete mãs stay off the public sell catalog and their product pages 404. See [shop.md](shop.md).
- `neverList` is empty. Do not invent never-list rows.
- Incomplete Taobao mãs are the `heldIncomplete` list. They are not published (`README.md`, `publishBlock`).

## Intake access

- Intake data routes stay open by link. No session wall (`sassy-closet/lib/shop-admin-gate.ts`, `sassy-closet/docs/SHOP_ADMIN.md`).
- Those routes send `noindex, nofollow, nosnippet` (`sassy-closet/lib/intake-direct-link-headers.ts`).
- Do not add a password to hide `/api/ma/<mã>`. The doc says the link is the access (`SHOP_ADMIN.md`).
- Open PRs #188 and #189 would add a login on cost reads. They are not merged. Do not implement them as if they were current law.

## Meta

- Do not delete or repost a Meta post. `scripts/meta_inventory.py` sets every flag's action to `edit original only / Boss decides`. `scripts/caption_gap_watch.py` says fixes are edits of the original post, and Boss decides. `scripts/tests/test_meta_inventory.py` and `scripts/tests/test_caption_gap_watch.py` assert the report text does not suggest delete or repost.
- `scripts/meta_inventory.py` reads a saved Facebook/Instagram export, `data/held.json`, and a cost-free daily-inputs snapshot. Its flags are `no_ma`, `held_promoted`, `duplicate`, `live_no_post`, `missing_gia`, and `caption_lint`.
- `scripts/caption_gap_watch.py` reads a saved caption export. Its flags are `missing_caption`, `missing_ma`, `missing_gia`, and `gia_differs`.
- `scripts/caption_lint.py` checks caption shape: line 1 `Mã X00`, a `Giá $NN` amount anywhere in the caption, S06 at $25, and Giá against the approved or live dollar. It does not edit the post. Size checks are the separate scripts named in [shop.md](shop.md).
- Tool output stays free of supplier cost and supplier links. `scripts/caption_lint.py` refuses to print a report that matches `PRIVATE` (¥, taobao, tmall, 1688, cost, giá vốn). `scripts/luxubu_status_record.py` rejects a title that matches `BANNED` (¥, $, a URL, an email). `scripts/muse_pack_sections.py` writes mãs, post IDs, and counts only.

## Quality and visuals

Merged PR #203 limited itself to scripts and tests: no shop or intake UI, no prices, no `held.json`. The learn-track visual docs are research notes under `sassy-closet-shop/docs/ai-clothing-shop/`. They are not a license to restyle the live shop. Customer copy must not say a dropship look is "on hand" (`sassy-closet-shop/lib/warehouse-voice.ts`).

## What "done" means for an agent

A separate agent that did not build the change rechecks it against the code, the data, and the tests, with Fast off (not a `-fast` model). It posts PASS or FAIL with evidence on the draft pull request. The author's own test run is not that comment. This sentence is the knowledge-lane Boss rule. It was not in the repo before `docs/knowledge/`.

## Privacy

`scripts/privacy_scan.py` runs inside `scripts/hard_recheck.sh` against the diff from the base to `HEAD`. `shared/live-price-snapshot.json` keeps sell dollars and nulls `costCny`, `costUsd`, `costSource`, and `landedUsd` (merged PR #207). Do not put those costs back.
