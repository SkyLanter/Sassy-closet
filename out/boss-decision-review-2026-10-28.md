# Boss decision review: pieces 192–206 (Oct 28, 2026)

**Summary.** Everything from tonight is on one combined branch, `piece-206-combined-check` @ `0f3f177`, local only (no push, no merge, no PR). The recheck passed: pytest 1317 pass / 6 skip, privacy CLEAN, shop 198/198, intake 216/216 (3 never-list fixtures skipped in each), tsc OK in both apps (source: proof-206/recheck.txt, ts-tests.txt). Tonight's work made mã spelling (S006, s6, " K03 ") match the same way everywhere, so the S06 $25 lock and the held checks only got stricter. Nine items below need your call.

---

## 1. The never-list is empty
- **Now:** `data/held.json` `neverList` = `[]` (21 held mãs). Every never-list check runs but blocks nothing. The 3 never-list fixtures in each of the 3 test suites (6 in pytest) are skipped for that reason (proof-202 drift-report; proof-206).
- **Why it matters:** if a mã should never be listed, nothing stops it today except the held list.
- **Options:** (a) keep it empty (b) add specific mãs.
- **Default:** (a) keep empty, unless you have codes in mind.

## 2. held_photo_exposure reads the wrong held file by default
- **Now:** `scripts/held_photo_exposure.py:52` defaults to `auto-list/state/held.json` (a runtime state file), not `data/held.json`. It only matches the real held list when given `held=data/held.json` (proof-202).
- **Why it matters:** a held-photo exposure check could use an old list.
- **Options:** (a) point the default at `data/held.json` (b) leave it.
- **Default:** (a), a small draft change.

## 3. Trap list includes held mãs K02, H02, G01
- **Now:** shop `lib/next-ma-trap.ts:2` `INVENTED_NEXT_MAS` lists K02, G01, H02, which are also held. They're "invented mã" trap labels, not a status list, so this isn't drift (proof-202).
- **Options:** (a) leave it (b) remove the held ones from the trap list.
- **Default:** (a) leave it.

## 4. Pricing math differs between scripts and shop
- **Now:** Python `autolist.price()` uses tiered margins. Shop `pricing.ts` `sellUsdFromLanded` uses a flat 25% margin (ceil(landed / 0.75), +$2 if under $10), and `marginVerdict` shows "Inbox giá" under a 35% margin floor (proof-204 gate-matrix).

| Landed cost | Python autolist | Shop app |
|---|---|---|
| $5 | $10 | $9 |
| $12 | $19 | $16 |
| $20 | $30 | $27 |
| $50 | $67 | $67 |

- **Why it matters:** the same item can get a lower suggested price in the shop admin than in the auto-list scripts.
- **Options:** (a) Python tiers are right, so the shop should match (b) the shop's flat 25% is right (c) keep both (different uses).
- **Default:** (a), since the scripts never undercut. Nothing changes until you say so.

## 5. S06 with no price
- **Now:** intake `publishBlock` (`sassy-closet/lib/publish-guard.ts:36`) only checks S06 when a price is given, so a blank price passes. Shop admin save refuses S06 without $25 (`admin-ops.ts:210`). Python autolist always quotes $25 (`autolist.py:165`) (proof-204).
- **Why it matters:** an intake draft for S06 can be saved without a price. Any price given must be $25.
- **Options:** (a) keep it (drafts may lack a price) (b) intake also requires $25 for S06.
- **Default:** (a) keep.

## 6. Daily check uses the snapshot's held flag
- **Now:** `scripts/daily_shop_check.py:186` flags "held mã live" using the held flag recorded in the snapshot when it was taken. The apps use today's `data/held.json` (proof-204).
- **Options:** (a) keep point-in-time (b) also check today's held list.
- **Default:** (a) keep, since it's right for old snapshots.

## 7. Padded product URLs
- **Now:** `sassy-closet-shop/lib/ma-url.ts:32` redirects `/m/a001` to `/m/A001`, not `/m/A01`. A padded URL doesn't open the product page (lookup finds nothing). This is a lookup issue, not a safety bypass (proof-201 call-sites).
- **Options:** (a) leave it (b) redirect padded URLs to the canonical page (/m/A01).
- **Default:** (b) as a draft, low risk. Or (a) if no one shares padded links.

## 8. Duplicate check in product-parse (FYI only)
- `product-parse.ts:208` now catches duplicate mãs by canonical spelling (piece 196), so K03 and K003 can't both exist. Nothing to decide.

## 9. Bundle rebuild and draft PRs
- The bundle rebuild is still stopped pending your decision. GitHub (`gh`) isn't signed in, so no draft PR can be opened. All pieces are local branches.
- **Options:** (a) restart the bundle rebuild (b) keep it stopped. Separately: sign in `gh` to allow draft PRs.

## Already waiting on Boss (no new detail)
- Blob storage outage / intake HTTP 500 (auto-list fails at its first step)
- Meta items pending your approval
- Taobao login on the box for the intake ¥ audit

---

## Boss answers
- [ ] 1. Never-list: (a) keep empty  (b) add: ____
- [ ] 2. held_photo_exposure default: (a) use data/held.json  (b) leave
- [ ] 3. Trap list K02/H02/G01: (a) leave  (b) remove held ones
- [ ] 4. Pricing: (a) Python tiers  (b) shop flat 25%  (c) keep both
- [ ] 5. S06 no price in intake: (a) allow drafts  (b) require $25
- [ ] 6. Daily check held flag: (a) point-in-time  (b) add today's list
- [ ] 7. Padded URLs: (a) leave  (b) redirect to canonical
- [ ] 8. product-parse duplicates: FYI, no answer needed
- [ ] 9. Bundle rebuild: (a) restart  (b) keep stopped;  gh sign-in: yes / no
