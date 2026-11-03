# START HERE — draft pieces 17-99 (for Boss)

Plain-English map of the waiting drafts. Every line comes from the 17-99 review guide
and the patch file lists. Nothing here is merged, pushed or live.

## Where it stands
- 82 draft pieces. Test-applied onto live main d13ec40: 76 clean, 0 conflicts, 0 missing.
- 6 are already in main and need nothing: 18, 20, 21, 23, 54, 56.
- The review guide flags 0 pieces for live writes.
- All tests pass on the full stack (688).

## Groups by purpose
| Group | Pieces |
|---|---|
| Price checks (too-cheap, headroom, held price sheets, price approval queue, cost-basis report) | 17-20, 47, 55, 70 |
| Daily shop check and its sections (gaps, runner, snapshot, not-found, hung runs, held photos) | 22-24, 27, 29, 30, 37, 38, 41, 42, 44-46, 49 |
| Held list | 26 |
| Captions and Meta post checks (Giá, lint, post inventory, caption gaps, Reels, Meta snapshot) | 21, 31, 33, 35, 48, 53, 60 |
| Popular order (Meta carry-over, live-set check, gaps, held-in-order report) | 72-76 |
| Meta dual-confirm (Luxubu + Mini Boss must both pass) | 78-80 |
| 3:30 PM daily summary | 57-59, 77, 84-86, 91, 98 |
| Boss decisions list | 40, 51, 52, 89, 90, 92-95, 99 |
| Intake / Muse pack | 23, 54, 56 |
| Privacy and host health | 32, 34 |
| Bundle and review tooling (guide, dry run, inventory/sync checks) | 50, 61-69, 71, 82, 83, 87, 97 |
| Stack notes / checkpoints (proof only) | 28, 36, 39, 43, 81, 88, 96, 100 |

## Read-only vs changes the shop
The review guide labels all 82 pieces read-only (no live-write code). Pieces 30, 34, 36, 73
and 95 read the live site over the network (GET/HEAD only). Every other piece is local only.

These pieces change shop files or shop behaviour if merged — read before merging:
- **28** — carries the earlier open shop PRs (01-15 combined) into the stack: live site code
  under sassy-closet-shop/ (product pages, photos, sitemap, SEO, cache, catalog store) and
  the intake sell-price backfill + D05 seed under sassy-closet/. **Touches the live site,
  Blob catalog code and prices.** Merging this is the same decision as merging 01-15.
- **26** (also inside 28) — changes data/held.json: holds S16-S19, A27-A29, H02, G01.
  Changes which mãs are held.
- **74** — adds A15, S09, P04, P05, H01, D04 to sassy-closet-shop/data/popular-order.json.
  **Changes the Popular order on the live site.**
- **27, 29** — add a GitHub workflow that runs the daily shop check on a schedule
  (22:15 UTC daily). Read-only check, but it starts running by itself once merged.
- **21, 22** — add data/approved-held-gia.json (a reference list the checks read).
- No piece touches Meta posts, Square, Vercel or domains.

## Suggested merge order (batches)
1. **Batch A — read-only price and daily checks:** 17, 19, 22, 24, 27, 29 (27/29 turn on the schedule).
2. **Batch B — shop changes, Boss's call:** 26, then 28 (live site + prices), then 74 (Popular order).
   Hold these if any answer is not yes; batches C-E do not need them to be live,
   but they apply on top of 28 in this stack order.
3. **Batch C — QC tooling:** 30-49 in number order (rebased copies of 38, 39, 42-48 are in piece 68).
4. **Batch D — summary, decisions, popular-order reports, Meta dual-confirm:** 50-80.
5. **Batch E — bundle tooling and checkpoints:** 81-100.
Exact order: "Suggested merge order" in the 17-99 REVIEW-GUIDE.md.

## Rerun the dry run (read-only)
    python scripts/stack_apply_dryrun.py --repo . --bundle out/pending-draft-prs --main d13ec40 --guide out/pending-draft-prs/100-checkpoint-start-here/proof/REVIEW-GUIDE.md
