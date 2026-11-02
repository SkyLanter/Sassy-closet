# Agents

Read `docs/knowledge/README.md` before you edit this repo. That folder is the map of the shop, the scripts, the data files, and the pull request history. `sassy-closet-shop/AGENTS.md` is only the Next.js framework note.

## Stay inside these rules

- Open a draft pull request. Boss merges. Do not merge, close, or approve.
- Do not post, edit, delete, or repost Facebook or Instagram. Checkers are read-only and look at mã, Giá, size, and format.
- Do not change a live price, Blob, Square, or `data/held.json` unless the task is that change and Boss has said yes. S06 stays $25.
- Held-incomplete mãs stay off the sell catalog. Their product pages stay 404.
- Incomplete Taobao mãs are that held list. They do not get published.
- Intake stays open by link: no password and no 401. `/api` and `/admin` stay `noindex, nofollow, nosnippet`.
- Prefer a small, correct change. Do not restyle the shop in a data or script task.
- If a fact is not in the repo or the scrubbed snapshot, write UNKNOWN. Proof sentences and Excel headers are in `docs/knowledge/snapshot-proofs.md` and `docs/knowledge/snapshot-excel.md` (`INDEX.md` in the snapshot). Order_Log, Wishlist, which Taobao pull is canonical, whether `sassycloset.xlsx` is the hub, and the live SoT workbook stay unknown. See `docs/knowledge/proof-and-hub-snapshot.md`.

## Done

A separate agent that did not write the change rechecks it against the code, the data, and the tests. Use a full model, not a fast one. That agent comments PASS or FAIL, with evidence, on the draft pull request. Your own test log is not that comment.

Details and file citations: `docs/knowledge/rules.md`.
