# Sassy Closet knowledge base

Read this folder before changing the shop, the intake app, the Excel kit, or the scripts. It is a map of what is already in the repo. It is not a new policy.

Pinned to `main` at `04bfc35` (commit dated 2026-10-30, checked 2026-11-02). Pull request notes cover **#1–#247** as fetched on 2026-11-02. Open pull requests are drafts until Boss merges them.

## How to read it

1. [Rules](rules.md) — what agents must not do.
2. [How the shop works](shop.md) — mã, prices, held items, Taobao, intake, Meta.
3. [Workflows](workflows.md) and [script index](script-index.md) — what exists, and what actually runs.
4. [Data and Excel](data-and-excel.md) — files in git, and column names the code defines.
5. [Data flow](data-flow.md) — which copy feeds which reader.
6. [Pitfalls](pitfalls.md) — ways a correct-looking change still fails.
7. [How to do a job](how-to.md) — commands the repo already documents.
8. [PR history](pr-history.md) — every PR from #1, with state.
9. [Glossary](glossary.md).
10. [Unknowns](unknowns.md) and [proof folders and the live Excel](proof-and-hub-snapshot.md).
11. [Excel columns from the scrubbed snapshot](snapshot-excel.md) — headers from `INDEX.md`. Meanings stay header-only.
12. [What each proof folder proves](snapshot-proofs.md) — the index sentence for each of the 1089 folders.

`sassy-closet-shop/AGENTS.md` is a Next.js note about that app's framework. It does not replace this folder.

## Source rule

Use the code, tests, git history, pull request bodies, and files in this repo. If a fact is not there, write **UNKNOWN / not in repo**. Do not fill the gap from memory, a chat, or a folder that is not on disk.

Checked on 2026-11-02: `/cursor/stores/bot/knowledge-snapshot/INDEX.md` is the scrubbed read-only index. It lists 1089 proof folders and 11 exported workbooks. Schemas and the index's proof sentences are in [snapshot-excel.md](snapshot-excel.md) and [snapshot-proofs.md](snapshot-proofs.md). Example rows and proof file bodies are not in git. Order_Log, Wishlist, which Taobao pull is canonical, and whether `sassycloset.xlsx` is the hub stay UNKNOWN. See [proof-and-hub-snapshot.md](proof-and-hub-snapshot.md).

## What counts as done

A change is not done when its author says it is done. A **separate** agent, one that did not write the change, and not a fast model, rechecks it against the code, the data files, and the tests. That agent posts **PASS** or **FAIL** with evidence as a comment on the draft pull request.

This knowledge lane records that as a Boss rule for agents. It was not a string in the repo before this folder. Drafts stay drafts. Boss merges.

## Two apps, one kit

| Path | What it is | Live URL named in repo docs |
| --- | --- | --- |
| `sassy-closet/` | Nhung's intake site. Vercel root `sassy-closet`. | https://sassy-closet.vercel.app (`README.md`, `sassy-closet/README.md`) |
| `sassy-closet-shop/` | Customer sell shop. Vercel root `sassy-closet-shop`. | https://sassy-closet-shop.vercel.app (`README.md`). `sassy-closet/docs/SHOP_ADMIN.md` also names https://sassycloset.vercel.app for the same shop project. |
| `excel-kit/` | Desktop workbook builders. Kit syncs generated files to OneDrive. The live workbook is not in git. | `Documents/Sassy Closet/Sassy_Closet_SoT.xlsx` (`README.md`, `excel-kit/schema.py`) |
| `scripts/` | Read-only checks and local drafts. | No schedule in `.github/workflows`. |
