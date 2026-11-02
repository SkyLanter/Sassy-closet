# Independent recheck log

This file is the running log for the independent recheck lane. The author of this log did not build the pull requests it records. Nothing here is a merge, a deploy, or a live write.

Window: through 2026-11-07 00:00 America/Los_Angeles.

Rules for this lane: comment on the reviewed PR only, never push to another branch, never merge, close, approve, or mark ready, and never write Blob, KV, or Meta.

A row is rechecked only at the head SHA in that row. A later push needs a new run. `INDEPENDENT RECHECK PASS` or `FAIL` is posted on the PR after `npm ci` in both apps and `scripts/hard_recheck.sh --base origin/main` with no skip flags, plus an adversarial read of the diff.

## 2026-11-02 22:20 UTC — queue opened

Open drafts from #217 up, combined #225 first. No open pull request matched a knowledge-lane docs title at this snapshot. Older learn-track drafts (#19–#41 and similar) are outside this queue unless a new knowledge-lane PR opens.

| PR | Head at queue time | Title |
| --- | --- | --- |
| #225 | `d8170670ab41` | Draft: one branch for the safe shop fixes. Moved 2026-11-02 23:55 UTC. `72d792580d71` was commented FAIL. `ba5f60fa767d` was commented FAIL. `cda92647236a` passed locally and was not commented. |
| #217 | `ee9e2a34bfb4` | Combined safe bundle #208-#216 |
| #218 | `03c23afc58a7` | Fail closed when Blob is down, and drop held folders from other mãs |
| #219 | `5b590c0f734e` | Keep a blank intake sell blank and parse pasted yen safely |
| #220 | `8119f95aa536` | Fix midnight QC home prices on RSC flight HTML |
| #221 | `c417d95e2ab2` | Guard shop workflows against wrong days, stale intake, and silent holds |
| #222 | `2fbf7070f3df` | Keep held-sheet landed digits aligned with the printed quote |
| #223 | `e78e049b47a6` | Add a read-only workflow status report |
| #224 | `9556c0f826f9` | Keep open Boss decisions the digest and streak were dropping |
| #226 | `66fd312af0b7` | Read the flat midnight QC summary in the daily draft |
| #227 | `f39946047e80` | Show the shop-draft proposal in the daily summary |
| #228 | `957d1d257cdf` | Recognize padded and short caption mãs before the price check |
| #229 | `99121ddc2948` | Compare padded caption mãs with the catalog price |
| #230 | `db9a5392bfdc` | Keep a bad live price from dropping the cost-basis report |
| #231 | `a704f452bd78` | Do not serve a held folder from another mã's image URL |
| #232 | `8b608ca5017d` | Run the hard recheck on pull requests |
| #233 | `85c24e8a24e1` | Draft: read-only parity check for pricing, mã, and sizes |
| #234 | `1a2b1e82dc88` | Read padded QC-note mãs as the shop key |
| #235 | `0e696628185d` | Prefix CSV formula starters in the intake export |
| #236 | `077a6a6de927` | Draft: keep a trailing .0 on in-window EU shoe sizes |
| #237 | `9d318d4f4253` | Compare caption Giá with a padded or lowercase price key |
| #238 | `93e2341b0008` | Read on-hand rows stored under a variant mã key |
| #239 | `7770cab00a33` | Add an on-demand read-only browser smoke |
| #240 | `e346f6c77de8` | Draft: note that shop pricing prefers the yen cost |
| #241 | `3ae952869d24` | Keep sold and hold rows out of the intake live price |
| #242 | `f0b91129a050` | Return 503 when an intake save cannot read the store |
| #243 | `9a9c2e8f9f72` | Draft: keep EU sizes when importing a G submission |
| #244 | `5a80c19474b4` | Check every live S06 row in the daily snapshot |
| #245 | `3d798dfe4560` | Return 503 when a share card cannot read the catalog |
| #246 | `ce7471481dd4` | Add a read-only draft merge-readiness report |
| #247 | `ea06ce1ed0a9` | Draft: keep an in-window trailing .0 on intake shoe chips |
| #248 | `11b0ecf35273` | Keep a blank catalog status in the daily snapshot |

## Verdicts

| PR | SHA | Result | Notes |
| --- | --- | --- | --- |
| #248 | `11b0ecf352730694738342674bc988f42df19285` | PASS | pytest 2120 passed, 7 skipped. Intake 277 / 274 / 0 / 3. Shop 218 / 215 / 0 / 3. |
| #224 | `9556c0f826f91d4d2762d7bd4d66ba201520524a` | PASS | pytest 2127 passed, 7 skipped. Intake 277 / 274 / 0 / 3. Shop 218 / 215 / 0 / 3. Negated Boss lines stay open. Findings: none. |
| #225 | `ba5f60fa767d6750ecbc18b4fa006c8967c07e60` | FAIL | Script PASS (pytest 2323). `Mã S006B` lints as S06. Log line 56 says the proposal path was not changed. Superseded by the next row. |
| #225 | `72d792580d71f6af6447043a6f981c7a646bb178` | FAIL | Script PASS (pytest 2337). ASCII `S06B` is no longer S06. `S06Đ`, fullwidth `S06Ｂ`, and a zero-width space still lock $25. Log line 56 is still uncorrected. |
| #242 | `f0b91129a050f5a796d2e343acf0c2b675fe15e5` | FAIL | Script PASS (pytest 2114). Intake save 503 matches. The lane A log claims image, CSV, and on-hand fixes that are not in this tree. |
| #226 | `66fd312af0b7f6705ec1109aaed28e5c28aab785` | FAIL | Script PASS (pytest 2119). The flat midnight QC summary matches. The log claims the home-price regex and the digest fixes, which are not in this tree. |
| #243 | `9a9c2e8f9f7278925c385ad0829d3cacb7619309` | PASS | pytest 2127 passed, 7 skipped. Intake 278 / 275 / 0 / 3. Shop 222 / 219 / 0 / 3. Kind G keeps in-window `.0` sizes. Findings: none. |
| #252 | `e66dd83417e31d046a9ddf0ac81ba8c0db092af8` | FAIL | Script PASS (pytest 2120). Bad approved Giá values are skipped. The log claims midnight QC and daily-snapshot fixes that are not in this tree. |
| #253 | `32eb7581a8dc1d4609365e4c25e3fbe43af9f30c` | PASS | pytest 2130 passed, 7 skipped. Intake 278 / 275 / 0 / 3. Shop 222 / 219 / 0 / 3. Gap report counts one trailing `.0`. Findings: none. |
| #217 | `ee9e2a34bfb45a526bb8140516372d0d89dabc09` | PASS | pytest 2164 passed, 7 skipped. Intake 281 / 278 / 0 / 3. Shop 218 / 215 / 0 / 3. Findings: none. |
| #218 | `03c23afc58a74fd6e4527742e5ff0b5ac7f98fbf` | PASS | pytest 2114 passed, 7 skipped. Intake 277 / 274 / 0 / 3. Shop 232 / 229 / 0 / 3. Findings: none. |
| #219 | `5b590c0f734e411e5eac39d78b0fae088dfa0a52` | PASS | pytest 2114 passed, 7 skipped. Intake 295 / 292 / 0 / 3. Shop 218 / 215 / 0 / 3. Findings: none. |
| #220 | `8119f95aa536d4f4b81045ec0767710c32e960ce` | FAIL | Script PASS (pytest 2121). Log lines 31–38 claim digest fixes that are not in this tree. |
| #221 | `c417d95e2ab2cf5fe990a7789939f9c68824d4ab` | PASS | pytest 2167 passed, 7 skipped. Intake 277 / 274 / 0 / 3. Shop 218 / 215 / 0 / 3. Findings: none. |
| #232 | `8b608ca5017d61060eb4732c4cd96fbc7947d04d` | PASS | pytest 2131 passed, 7 skipped. Intake 277 / 274 / 0 / 3. Shop 218 / 215 / 0 / 3. Findings: none. |
| #233 | `85c24e8a24e1d73ad36e9424436cc2a9b0d13db3` | PASS | pytest 2123 passed, 7 skipped. Intake 278 / 275 / 0 / 3. Shop 218 / 215 / 0 / 3. Findings: none. |
| #234 | `1a2b1e82dc881da37e913c27fda22879fc3bb229` | FAIL | Script PASS (pytest 2115). QC-note parser matches. The log claims other fixes that are not in this tree. |
| #235 | `0e696628185d3f52bee4530801eda27fffa20a8b` | FAIL | Script PASS (pytest 2114). CSV formula prefix matches. The log's image-route section is not in this tree. |
| #236 | `077a6a6de927553b5d5347c693e93b7ce093d9d5` | PASS | pytest 2125 passed, 7 skipped. Intake 278 / 275 / 0 / 3. Shop 220 / 217 / 0 / 3. Findings: none. |
| #237 | `9d318d4f4253095099643ad2233a019631fd2847` | FAIL | Script PASS (pytest 2115). Gap watch matches. The log claims other fixes that are not in this tree. |
| #238 | `93e2341b000829da1e0f001b7ba473b343293db8` | FAIL | Script PASS (pytest 2114). On-hand alias matches. The log's image-route and CSV-formula sections are not in this tree. |
| #222 | `2fbf7070f3df59c26733d1b089a4166fb666f238` | PASS | pytest 2126 passed, 7 skipped. Intake 277 / 274 / 0 / 3. Shop 218 / 215 / 0 / 3. Landed digits stay on the same quote. Findings: none. |
| #223 | `e78e049b47a6ab792e89f9490ae1487034c6c2aa` | PASS | pytest 2157 passed, 7 skipped. Intake 277 / 274 / 0 / 3. Shop 218 / 215 / 0 / 3. GET-only status report. Findings: none. |
| #239 | `7770cab00a332a070d57a4c520d66e739e6e52ac` | PASS | pytest 2120 passed, 7 skipped. Intake 277 / 274 / 0 / 3. Shop 218 / 215 / 0 / 3. Smoke is manual GET-only. This lane did not run the live step. Findings: none. |
| #240 | `e346f6c77de8fb6a7d513ff31fd9aab2f47f27a7` | PASS | pytest 2126 passed, 7 skipped. Intake 278 / 275 / 0 / 3. Shop 220 / 217 / 0 / 3. Yen preference is a Boss note. Findings: none. |
| #241 | `3ae952869d24f01ef6d41931ff23274ce3a461b1` | FAIL | Script PASS (pytest 2116). Sold and hold are out of the intake live price. Blank and null do not match the daily snapshot, and the log claims other fixes that are not in this tree. |
| #250 | `a381e8e66cc340f448bb1ff15f859cd27d903899` | FAIL | Script PASS (pytest 2114). Dropped-photo hashes match. The lane A log claims image, CSV, on-hand, 503, and share-card fixes that are not in this tree. |
| #251 | `afa3df612e79f1f36707640ef240b4a355703f1c` | PASS | pytest 2118 passed, 7 skipped. Intake 277 / 274 / 0 / 3. Shop 218 / 215 / 0 / 3. Workflow tokens are contents: read. Findings: none. |

#222 was still in `hard_recheck.sh` when #239 was commented. #223, #224, #226–#231, and #240–#247 stay with the earlier workers. No knowledge-lane docs PR. #250–#258 are in progress. #259 is queued. #249 is this log and is not graded.

## 2026-11-02 23:15 UTC — new drafts

| PR | Head | Title |
| --- | --- | --- |
| #250 | `a381e8e66cc3` | Drop a removed photo's hash so find-mã stops matching it |
| #251 | `afa3df612e79` | Lock pull-request workflows to a read-only token |
| #252 | `e66dd83417e3` | Skip a bad approved Giá instead of inventing $1 |
| #253 | `32eb7581a8dc` | Draft: treat a trailing .0 as the allowed shoe chip in the gap report |
| #254 | `a8d4be084467` | Pin third-party actions to commit SHAs |
| #255 | `f22db5f7d19c` | Draft: name missing, stale, and unusable cost-recheck files |
| #256 | `b23494967f84` | Keep a new intake photo from replacing a file that was kept |
| #257 | `dd240888ec8d` | Test catalog fallback, the S06 lock, held photo spellings, and intake export |
| #258 | `623617591224` | Split gap-report sizes on the same separators as listing |
| #259 | `0402dd50b1c6` | Count a text sell price in the price approval queue |

## 2026-11-02 23:55 UTC — #225 moved again

#225 head is `d8170670ab411fe21c38630f4a38b8ecdae711e8`. The FAIL on `72d792580d71` stays the comment for that older SHA. The new head is in hard recheck and is not commented yet. #226, #243, and #253 are commented at the SHAs in the verdict table. Their log directories are `out/recheck/20261102-234222-157269`, `out/recheck/20261102-234641-168787`, and `out/recheck/20261102-234412-161336`. No knowledge-lane docs PR.

This log lives on draft PR #249 (`cursor/independent-recheck-log-cfee`). That PR is this lane's own notes, so this lane does not grade it.

PR watch subscriptions for #217–#247 expire 2026-11-05 22:28 UTC. Renew them before then so the loop still reaches 2026-11-07 00:00 America/Los_Angeles. A 45-minute timer is also set.

Early static notes, not verdicts:

- None of these diffs change `data/held.json` or a CSS file.
- #232 adds a pull-request workflow that runs the hard recheck with read-only contents permission. It does not deploy.
- #239 adds a manual workflow that GETs live shop and intake documents and aborts non-document and `/api/` requests. It does not deploy. This lane will not run that live smoke.
- #218 fails a configured Blob read closed (no seed) and drops another mã's held folder from image URLs. A primary socket error can still read the legacy blob path `sassy-closet-shop/catalog.json`; that path is an explicit tested fallback, not a seed fallback.
- #219 stops intake save from filling a blank sell with a calculated price. A typed zero still stores a zero. This is an intake field change, not an S06 catalog edit.
