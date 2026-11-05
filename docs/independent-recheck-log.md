# Independent recheck log

This file is the running log for the independent recheck lane. The author of this log did not build the pull requests it records. Nothing here is a merge, a deploy, or a live write.

Window: through 2026-11-07 00:00 America/Los_Angeles.

Rules for this lane: comment on the reviewed PR only, never push to another branch, never merge, close, approve, or mark ready, and never write Blob, KV, or Meta.

A row is rechecked only at the head SHA in that row. A later push needs a new run. `INDEPENDENT RECHECK PASS` or `FAIL` is posted on the PR after `npm ci` in both apps and `scripts/hard_recheck.sh --base origin/main` with no skip flags, plus an adversarial read of the diff.

## 2026-11-02 22:20 UTC — queue opened

Open drafts from #217 up, combined #225 first. No open pull request matched a knowledge-lane docs title at this snapshot. Older learn-track drafts (#19–#41 and similar) are outside this queue unless a new knowledge-lane PR opens.

| PR | Head at queue time | Title |
| --- | --- | --- |
| #225 | `0bcfd493c420` | Draft: one branch for the safe shop fixes. Moved 2026-11-05 04:46 UTC. Verified PASS. Commented PASS `6649937807`. `8fea4bbf5290` stays the prior PASS. Moved 2026-11-04 14:00 UTC. Verified PASS. Commented PASS `6632912553` because outside FAIL `6632848598` disagrees. Outside PASS `6632716587` agrees. `7e1ef27ef773` is no longer the head. This lane’s reading of that SHA is PASS and was not commented. The script passed. `0,025` returns `0025`, the same text the parent parser at `52df79f5ca65` returned. Outside comments on that SHA are not adopted: PASS `6632291274`, withdrawn PASS `6632278826`, and FAILs `6632342594` and `6632382304`. Verified PASS at `52df79f5ca65`. Two outside cursor[bot] PASS comments on that older SHA agree, so no second comment was posted. `d79e85eeb8a9` is no longer the head. This lane’s reading of that SHA is PASS and was not commented. The script passed. The worker’s join-based FAIL is not adopted. An outside PASS agrees. An outside FAIL uses the join and disagrees. `d8a795d83902` is no longer the head. This lane’s recheck of that SHA passed and was not commented. One outside PASS still stands on it. One outside PASS was withdrawn and now says FAIL. Another outside FAIL agrees with that withdrawal. None is adopted. Verified PASS at `ec78e0836cbb`. Two outside cursor[bot] PASS comments on that older SHA agree, so no second comment was posted. Commented FAIL at `1c913dadc465`. Tree of that SHA matches the FAIL at `dea7e325b3a8`. `269fea55fc85` is FAIL and was not commented because it is not the head. Verified PASS at `39cd5cbe994c`, `4fc9fa61ee3e`, `6d1744a149ef`, `75e1d6580ed8`, `2c58e8868f4a`, `8f4f7c062442`, `0f4fcc2c255f`, `ecb7b2015773` (not commented; not the head), `77fde6ab2f3b`, `5af406779a1e`, `953e460b8f46`, `4df538a9b6eb`, `44bde2ae5e90`, and `b29c6c7ee1ef`. Commented FAIL at `d3a8fc9162c3` and `1eb4b39f124d`. FAIL at `6136247cbe57`, `e6c41e1f7656`, `dd4a4fbe2a55`, `72d792580d71`, and `ba5f60fa767d`. `f9d33ed8d8b2` was not commented. `dea7e325b3a8` is FAIL and was not commented. |
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
| #227 | `f39946047e80d9870390e6d5d6d1265d5b52648b` | FAIL | Script PASS (pytest 2114). `--proposal` matches. The log claims midnight QC, digest, and flat-summary fixes that are not in this tree. |
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
| #244 | `5a80c19474b425410b9aa8ab8f477586e3e91d65` | FAIL | Script PASS (pytest 2118). Every live S06 row is checked at $25. The log claims sold/hold filtering and other fixes that are not in this tree. Log `out/recheck/20261102-235357-184718`. |
| #254 | `a8d4be0844677a3ead83486795de6a0fcb017fbb` | PASS | pytest 2117 passed, 7 skipped. Intake 277 / 274 / 0 / 3. Shop 218 / 215 / 0 / 3. The four workflows pin checkout, setup-node, and setup-python. Findings: none. Log `out/recheck/20261102-235316-183289`. |
| #228 | `957d1d257cdfcf0eb6620e53ff4d9233e6490474` | FAIL | Script PASS (pytest 2118). One-to-four-digit caption mãs match, and S06 stays $25. The log claims midnight QC, digest, flat-summary, and `--proposal` fixes that are not in this tree. Log `out/recheck/20261103-000059-198481`. |
| #245 | `3d798dfe4560f170b945a66508e3c54de1ddc6aa` | FAIL | Script PASS (pytest 2114). Share-card catalog failure is 503. The lane A log claims image, CSV, on-hand, and intake-save fixes that are not in this tree. Log `out/recheck/20261103-000454-210086`. |
| #246 | `ce7471481dd407d038434537976e574a09c9adae` | PASS | pytest 2127 passed, 7 skipped. Intake 277 / 274 / 0 / 3. Shop 218 / 215 / 0 / 3. Merge-readiness report is read-only. Findings: none. Log `out/recheck/20261103-001628-237779`. |
| #247 | `ea06ce1ed0a9359dcda27f177aa51b60674f8925` | PASS | pytest 2128 passed, 7 skipped. Intake 278 / 275 / 0 / 3. Shop 222 / 219 / 0 / 3. In-window trailing `.0` stays. Findings: none. Log `out/recheck/20261103-002607-259720`. |
| #229 | `99121ddc2948d33b852999f2e8b4d2b7d8f91b7c` | FAIL | Script PASS (pytest 2115). Padded caption mãs match the catalog price. `Mã S06Đ` is still read as S06, and the log claims other fixes that are not in this tree. Log `out/recheck/20261103-001123-223165`. |
| #230 | `db9a5392bfdc8aadf0d1e4cc017edaf99019b5ca` | FAIL | Script PASS (pytest 2118). A bad live price no longer drops the cost-basis report. The log claims other fixes that are not in this tree. Log `out/recheck/20261103-002055-247763`. |
| #231 | `a704f452bd78a0372008c2e4754fd1313d59483d` | PASS | pytest 2114 passed, 7 skipped. Intake 277 / 274 / 0 / 3. Shop 220 / 217 / 0 / 3. A live image URL does not read a held folder. Findings: none. Log `out/recheck/20261103-002914-268425`. |
| #255 | `f22db5f7d19cf4738f0fb95aa67c42a874b81d9d` | PASS | pytest 2127 passed, 7 skipped. Intake 277 / 274 / 0 / 3. Shop 218 / 215 / 0 / 3. Unusable cost-recheck files are named and do not clear a streak. Findings: none. Log `out/recheck/20261103-000348-206996`. |
| #256 | `b23494967f843cb32f260a96192fc713ba7df335` | FAIL | Script PASS (pytest 2114). Intake 282 / 279 / 0 / 3. Shop 218 / 215 / 0 / 3. Free photo slots match. The lane A log claims hash, image, CSV, on-hand, and 503 fixes that are not in this tree. Log `out/recheck/20261103-001530-236094`. |
| #257 | `dd240888ec8d60f8b6e763b09f439f647373ecdb` | PASS | pytest 2114 passed, 7 skipped. Intake 283 / 280 / 0 / 3. Shop 229 / 226 / 0 / 3. Tests only. S06 stays $25. Findings: none. Log `out/recheck/20261103-002544-258712`. |
| #258 | `62361759122415f014de169cb3d9299877c84751` | PASS | pytest 2132 passed, 7 skipped. Intake 278 / 275 / 0 / 3. Shop 222 / 219 / 0 / 3. Gap sizes split on the listing separators. Findings: none. Log `out/recheck/20261103-003847-286375`. |
| #225 | `0bcfd493c42083cef5c388b0544abdc651b58034` | PASS | pytest 2479 passed, 7 skipped. Intake 364 / 361 / 0 / 3. Shop 263 / 260 / 0 / 3. Zero-first comma groups no longer publish S06 as $25. `$25` and `1,200` stay. Held K06 stays held. `025` still reads as 25, same as the parent. Findings: none. Log `out/recheck/20261105-043512-3658`. Comment `6649937807`. |
| #285 | `78819eaf0d049db3ecfc6049635f17781952aa63` | PASS | pytest 2121 passed, 7 skipped. Intake 277 / 274 / 0 / 3. Shop 218 / 215 / 0 / 3. S06 JSON-LD offer must be 25. A stray `$25` does not pass. `priceCurrency` is not read. Findings: none. Log `out/recheck/20261105-043512-3705`. Comment `6649939263`. |
| #288 | `9dc8050db85ba666837152f5991878d916974da9` | PASS | pytest 2131 passed, 7 skipped. Intake 277 / 274 / 0 / 3. Shop 218 / 215 / 0 / 3. A foreign hub folder does not cover a color. Prices are copied. Findings: none. Log `out/recheck/20261105-043512-3733`. Comment `6649940705`. |

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
| #259 | `0402dd50b1c6` | Count a text sell price in the price approval queue. Commented FAIL. Script PASS. |
| #260 | `900de4827176` | Add the repo knowledge base. `e9729e40ab93` script PASS, review FAIL, not commented. A cursor[bot] PASS comment at `900de4827176` appeared at 09:44 UTC. This lane did not run that recheck and does not adopt it. |
| #261 | `a0118636446d` | Treat listing size aliases as the allowed gap-report chip. Commented PASS. |
| #262 | `879db4df23d8` | Serve a product image when the URL spells the mã the short way. Commented FAIL. Script PASS. |
| #263 | `a6af62cf4814` | Reject workflows that install without the lockfile. Commented PASS. |
| #264 | `24308111f172` | Test the tiered under-$10 bump and the locked dress debox. Commented PASS. |
| #265 | `3b5fa65c67c1` | Fail the drift check when any S06 spelling leaves $25. Commented FAIL. Script PASS. |
| #266 | `384122fd106e` | Record the shop and listing split on loose shoe tokens. Commented PASS. |

## 2026-11-03 00:00 UTC

Open drafts still run through #266. #260 is the knowledge-base docs PR (`docs/knowledge/`, `AGENTS.md`, and three Cursor rules). It is checked out at `e9729e40ab93` and queued with #259 and #261–#266. #225 at `d8170670ab41`, #244, and #254 were in hard recheck. #227 is commented FAIL. No other head from #217–#258 moved. #249 is this log and is not graded.

## 2026-11-03 00:10 UTC — #225 moved, two verdicts posted

#225 head is `e88e265ef2213131c786bd70ce8de9d6d8a64756` (“Do not read a stuck suffix as S06”). The script PASS on `d8170670ab41` (pytest 2351 passed, 7 skipped; intake 315 / 312 / 0 / 3; shop 237 / 234 / 0 / 3; log `out/recheck/20261102-235649-190567`) is not a comment, because that SHA is no longer the head. The new head is in its own worktree and is not commented yet.

#244 is commented FAIL at `5a80c19474b4`. #254 is commented PASS at `a8d4be084467`. Heads from #217–#266 otherwise match the tables above. #249 is this log and is not graded.

| PR | Head | Title |
| --- | --- | --- |
| #267 | `4b073e05abe1` | Keep every spelling in the seed versus live price compare. Seen before the slow loop. Not started by this lane. A cursor[bot] FAIL comment at this SHA appeared at 09:40 UTC. This lane did not run that recheck and does not adopt it. |
| #268 | `e932dd3cd446` | Record the quote gate rejecting A100 and K003. Seen before the slow loop. Not started by this lane. A cursor[bot] PASS comment at this SHA appeared at 09:36 UTC. This lane did not run that recheck and does not adopt it. |
| #269 | `494b1909e424` | Draft: name a missing or stale Meta snapshot. Seen 2026-11-03 02:15 UTC. Not started. |
| #270 | `ae1d86fe0761` | Copy kept intake photos onto the new mã when a row is renamed. Seen 2026-11-03 02:15 UTC. Not started. |
| #271 | `239561dab0a2` | Test canonical padded new mãs and the flat $10 quote. Seen 2026-11-03 02:15 UTC. Not started. |
| #272 | `a12a3866d167` | Keep every spelling in the OneDrive mirror price compare. Seen 2026-11-03 02:15 UTC. Not started. |
| #273 | `ac1aaf5f6c36` | Record the glued clothing-letter size split. Seen 2026-11-03 02:15 UTC. Not started. |
| #274 | `204db95943ec` | Reject a short comma in order sell prices. Seen 2026-11-03 02:15 UTC. Not started. |
| #275 | `3f801da535e4` | Record the shorter shop kind names. Seen 2026-11-03 02:15 UTC. Not started. |
| #276 | `ea391e97a359` | Refuse a rename that leaves a held mã or moves S06 off $25. Seen 2026-11-03 02:15 UTC. Not started. |
| #277 | `f5995aa91eb2` | Reject install lifecycle scripts in both package.json files. Seen 2026-11-03 02:15 UTC. Not started. |
| #278 | `681bca5520bf` | Test empty catalog fallback and the sold public gate. Seen 2026-11-03 02:15 UTC. Not started. |
| #279 | `b7c009f8e71b` | Record the Official Excel mã spelling split. Seen 2026-11-03 02:15 UTC. Not started. |
| #280 | `e30f09bca797` | Show every S06 price on the desk status. Seen 2026-11-03 02:15 UTC. Not started. |
| #281 | `e7b504cde3ee` | Return 503 when the shop catalog cannot be read. Seen 2026-11-03 02:15 UTC. Not started. |
| #282 | `b101f113e76b` | Reject invalid shop-desk USD text before save. Seen 2026-11-03 04:15 UTC. Not started. |
| #283 | `754ed7e4b1f9` | Reject non-literal USD text in shop draft prices. Seen 2026-11-03 06:16 UTC. Not started. |
| #284 | `b36383c1828d` | Parse calculator and intake amounts as plain dollars. Seen 2026-11-03 08:17 UTC. Not started by this lane. A cursor[bot] PASS comment at this SHA appeared at 08:25 UTC. This lane did not run that recheck and does not adopt it. |
| #285 | `78819eaf0d04` | PASS. Read S06's own JSON-LD offer in host health. Seen 2026-11-03 10:17 UTC. Head has not moved. This lane's recheck on 2026-11-05 04:47 UTC is PASS. Comment `6649939263`. Outside PASS comments at 09:10 UTC and 19:30 UTC were not this lane's earlier reading. This run agrees with PASS. |
| #286 | `adcb7c41d760` | Reject junk dollar and comma text in parse_usd. Seen 2026-11-03 14:18 UTC. Not started. |
| #287 | `cdb6d0451758` | Reject junk dollar text in pickup whole-dollar checks. Seen 2026-11-03 20:19 UTC. Not started. |
| #288 | `9dc8050db85b` | PASS. Flag photo color ids the shop reel will not attach. Seen 2026-11-03 22:19 UTC. Head has not moved. This lane's recheck on 2026-11-05 04:47 UTC is PASS. Comment `6649940705`. |
| #289 | `40699842ba18` | Reject a dollar sign between digits in intake gap numbers. Seen 2026-11-04 02:22 UTC. Not started. |
| #290 | `03236ca0caf0` | Reject a currency mark between digits in held price proposals. Seen 2026-11-04 06:22 UTC. Not started. A cursor[bot] PASS at this SHA appeared at 06:25 UTC. This lane did not run that recheck and does not adopt it. |
| #291 | `633531e577e6` | Flag customer copy the shop treats as stock or ops voice. Seen 2026-11-04 08:23 UTC. Not started. |
| #292 | `7ea4e6c91368` | PASS. Reject spliced dollar text in blank-mã order prices. Moved 2026-11-04 13:51 UTC. Commented PASS `6632568655`. Outside PASS `6632571977` agrees, so no second comment was posted. A thousands group that starts with zero raises. S06 `$25` stays the string `25`. The first-seen SHA `7b6830ae0473` was not graded. Outside cursor[bot] PASS `6630552776` and FAIL `6632172647` on that older SHA are not adopted. |

## 2026-11-03 00:15 UTC — slower loop

From here the lane polls every 2 hours, not every 45 minutes. At most two recheck workers run at once. A pull request is rechecked only when its head SHA changes from the SHA already recorded in this log. A draft that has not moved stays as recorded, including drafts that have not had a first recheck. Already-commented SHAs are not run again.

#228 is commented FAIL at `957d1d257cdf`. #225 at `e88e265ef221` was in hard recheck when this cap landed. #229 and #245 were already inside `hard_recheck.sh`. They will be commented only if that SHA is still the head. Those workers will not be sent on to the next pull request. #249 is this log and is not graded.

## 2026-11-03 00:18 UTC — #225 and #260 moved

#225 head is now `a9580d8d70c49a5e045a01c58f06135f5b8c6b61` (“Name missing, stale, and unusable cost-recheck files”). Since `e88e265ef221` the tree also pins the four workflows and rejects an install without the lockfile. That head is checked out and not started. The run on `e88e265ef221` is still inside `hard_recheck.sh` and will not be commented.

#260 head is now `900de482717671ebc3f0e5360fd8349ce022d704`. The checkout at `e9729e40ab93` finished its script and will not be commented. Another reviewer’s PASS note on #260 is not this lane’s recheck.

Four hard rechecks are already running, so neither new head starts until a slot is free. #249 is this log and is not graded.

## 2026-11-03 00:40 UTC — #245, #246, and #247 commented

#245 is commented FAIL at `3d798dfe4560`. #246 is commented PASS at `ce7471481dd4`. #247 is commented PASS at `ea06ce1ed0a9`. Those SHAs were still the heads. #232–#244 in the same batch were already commented and were not commented again. That worker was not sent on. #225 at `a9580d8d70c4` and #260 at `900de4827176` are still waiting. #249 is this log and is not graded.

## 2026-11-03 00:42 UTC — #229, #230, and #231 commented

#229 is commented FAIL at `99121ddc2948`. #230 is commented FAIL at `db9a5392bfdc`. #231 is commented PASS at `a704f452bd78`. #217–#228 in that batch were already commented. The old #225 SHA `cda92647236a` was not commented because it is not the head. That worker was not sent on. #249 is this log and is not graded.

## 2026-11-03 00:45 UTC — #225 moved again

#225 head is now `02c2a8bbf414a2bfb09b1dd2a9e14358378e9048` (“Fail the drift check when any S06 spelling leaves $25”). Since `a9580d8d70c4` the tree also changes the price-approval queue, short mã image URLs, and kept-photo replacement. `a9580d8d70c4` was checked out and never started, so it is not commented. Four hard rechecks are still running, so `02c2a8bbf414` waits. #260 remains `900de4827176` and also waits. #249 is this log and is not graded.

## 2026-11-03 00:55 UTC — #255 through #258 commented

#255 is commented PASS at `f22db5f7d19c`. #256 is commented FAIL at `b23494967f84`. #257 is commented PASS at `dd240888ec8d`. #258 is commented PASS at `623617591224`. #250–#254 in that batch were already commented. That worker was not sent on. #225 at `02c2a8bbf414` and #260 at `900de4827176` are still waiting. #249 is this log and is not graded.

## 2026-11-03 00:57 UTC — #225 moved and one recheck started

#225 head is now `fdedb65cd548cf241a3b76c235f7b5ea539183a1` (“Copy kept intake photos onto the new mã when a row is renamed”). Since `02c2a8bbf414` it also keeps every spelling in the seed-versus-live compare. `02c2a8bbf414` was checked out and never started, so it is not commented. One recheck of `fdedb65cd548` is running. #260 stays `900de4827176` and is not started. #249 is this log and is not graded.

## 2026-11-03 01:05 UTC — #259 and #261–#266 commented

Those heads were still current. #259, #262, and #265 are FAIL because the copied quality log claims fixes the tree does not contain. The scripts passed. #261, #263, #264, and #266 are PASS. #260’s report is for `e9729e40ab93`, and the head is `900de4827176`, so it is not commented and not started while #225 is in recheck. That worker was not sent on. #249 is this log and is not graded.

## 2026-11-03 01:10 UTC — #225 moved again

#225 head is now `ed1f2ff7b5346b2194daa2fe810bad7b7b8ff22f` (“Reject a short comma in order sell prices”). Since `fdedb65cd548` it also keeps every spelling in the OneDrive mirror price compare. `fdedb65cd548` was in recheck and is not the head, so it will not be commented. One recheck of `ed1f2ff7b534` is running. #260 stays `900de4827176` and is not started. #249 is this log and is not graded.

## 2026-11-03 01:18 UTC — #225 moved to dd4a4fb

#225 head is now `dd4a4fbe2a55bdbd06d714aff31311ee041fde90` (“Refuse a rename that leaves a held mã or moves S06 off $25”). `ed1f2ff7b534` finished its script with PASS and is not the head, so it is not commented. The `fdedb65cd548` review found the soft-hyphen and left-to-right-mark S06 holes and a rename photo overwrite. That SHA is not the head, so those findings were not commented. One recheck of `dd4a4fbe2a55` is running. #260 stays `900de4827176` and is not started. #249 is this log and is not graded.

## 2026-11-03 01:36 UTC — #225 commented FAIL

`dd4a4fbe2a55` was still the head. The script passed. The review failed: a rename still overwrites a photo another row claims, a soft hyphen or left-to-right mark after S06 still trips the $25 lock, and an empty USD sell still renames S06 away. That worker was not sent on. #260 stays `900de4827176` and is not started. #249 is this log and is not graded.

## 2026-11-03 01:46 UTC — #225 moved to e6c41e1

#225 head is now `e6c41e1f76564b40f4573f3e08d65f7ac4e41a99` (“Close the rename photo claim, invisible S06 suffix, and blank S06 move”). `dd4a4fbe2a55` stays the commented FAIL. One recheck of `e6c41e1f7656` is running. #260 stays `900de4827176` and is not started. #249 is this log and is not graded.

## 2026-11-03 02:11 UTC — #225 commented FAIL at e6c41e1

`e6c41e1f7656` was still the head. The script passed. The invisible S06 suffix and the blank S06 move are closed. A same-mã add still replaces a photo another row lists, so the review is FAIL. That worker was not sent on. #260 stays `900de4827176` and is not started. #249 is this log and is not graded.

## 2026-11-03 02:15 UTC — two-hour poll, no moved head

Open drafts #217–#268 and #225 are still on the SHAs recorded above. #260 is still `900de4827176`, so the older `e9729e40ab93` report stays uncommented and no new recheck started. #269–#281 are new and are recorded at the SHAs in the table. None of them has moved since it was first seen, so none was started. No recheck worker is running. The next poll is the 2-hour timer. #249 is this log and is not graded.

## 2026-11-03 02:18 UTC — #225 moved to f9d33ed

#225 head is now `f9d33ed8d8b2cd7199cb1e28932b5ba0c31fa9bb` (“Skip a claimed photo slot when a save stays on the same mã”). `e6c41e1f7656` stays the commented FAIL. One recheck of `f9d33ed8d8b2` is running. #260 and #269–#281 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 02:41 UTC — #225 moved to b29c6c7

#225 head is now `b29c6c7ee1efe64416f189df7fb66af9bcfb85fc` (“Reject invalid shop-desk USD text before save”). Since `f9d33ed8d8b2` it also returns 503 when the shop catalog cannot be read. The worker report for `f9d33ed8d8b2` is PASS and that SHA is not the head, so it is not commented. One recheck of `b29c6c7ee1ef` is running. #260 and #269–#281 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 03:02 UTC — #225 commented PASS at b29c6c7

`b29c6c7ee1ef` was still the head. The script passed. A thrown catalog read returns 503 without writing Blob. Invalid desk USD text is rejected before the save request, and S06 stays available at $25. The same-mã photo claim skip and the invisible S06 suffix glue are still present. Findings: none. That worker was not sent on. #260 and #269–#281 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 03:10 UTC — #225 moved to 6136247

#225 head is now `6136247cbe57150c36c1e196851ef2c2d9aafb4c` (“Show every numeric S06 price on the desk status”). `b29c6c7ee1ef` stays the commented PASS. One recheck of `6136247cbe57` is running. #260 and #269–#281 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 03:33 UTC — #225 commented FAIL at 6136247

`6136247cbe57` was still the head. The script passed. The review failed: deleting every `$` turns `"2$5"` into `$25`, and a null price on one S06 spelling aborts the scan before another spelling’s numeric price is printed. That worker was not sent on. #260 and #269–#281 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 03:36 UTC — #225 moved to 44bde2a

#225 head is now `44bde2ae5e90ca0cd21d20ac244e5f22392a3bfe` (“Return 503 when a shop catalog write throws”). Since `6136247cbe57` it also keeps a bad S06 price from hiding the rest of the desk and does not read a dollar sign between digits as S06’s price. `6136247cbe57` stays the commented FAIL. One recheck of `44bde2ae5e90` is running. #260 and #269–#281 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 03:47 UTC — #225 commented PASS at 44bde2a

`44bde2ae5e90` was still the head. The script passed. A dollar sign between digits is not a price, a null S06 spelling no longer hides another spelling, and a thrown catalog write returns 503 without `blobWritten`. Findings: none. That worker was not sent on. #260 and #269–#281 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 04:15 UTC — two-hour poll, no moved head

Open drafts #217–#281 and #225 are still on the SHAs recorded above. #225 stays the PASS at `44bde2ae5e90`. #260 stays `900de4827176` and was not started. #282 is new and is recorded at `b101f113e76b`. It has not moved since it was first seen, so it was not started. No recheck worker is running. The next poll is the 2-hour timer. #249 is this log and is not graded.

## 2026-11-03 06:15 UTC — #225 moved to 4df538a

#225 head is now `4df538a9b6eb0af873ac1e7b21787ae6a26d7218` (“Reject non-literal USD text in shop draft prices”). `44bde2ae5e90` stays the commented PASS. One recheck of `4df538a9b6eb` is running. #260 and #269–#282 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 06:16 UTC — two-hour poll

The only moved head is #225 at `4df538a9b6eb`, and that recheck is already running. #217–#224 and #226–#282 are still on the recorded SHAs. #283 is new and is recorded at `754ed7e4b1f9`. It has not moved since it was first seen, so it was not started. #249 is this log and is not graded.

## 2026-11-03 06:42 UTC — #225 commented PASS at 4df538a

`4df538a9b6eb` was still the head. The script passed. Non-literal shop draft USD text stays `NaN`, and a canonical S06 save whose price is not 25 is refused. Findings: none. That worker was not sent on. #260 and #269–#283 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 07:10 UTC — #225 moved to 953e460

#225 head is now `953e460b8f465a94d0c701234f093d31c89f17c9` (“Keep the prefill amount test off the cost privacy rule”). Since `4df538a9b6eb` it also parses calculator and intake amounts as plain dollars. `4df538a9b6eb` stays the commented PASS. One recheck of `953e460b8f46` is running. #260 and #269–#283 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 07:26 UTC — #225 commented PASS at 953e460

`953e460b8f46` was still the head. The script passed. Privacy stayed CLEAN. Non-literal calculator and intake amounts stay null, and S06 still saves only at $25. Findings: none. That worker was not sent on. #260 and #269–#283 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 08:17 UTC — two-hour poll, no moved head

Open drafts #217–#283 and #225 are still on the SHAs recorded above. #225 stays the PASS at `953e460b8f46`. #260 stays `900de4827176` and was not started. #284 is new and is recorded at `b36383c1828d`. It has not moved since it was first seen, so it was not started. No recheck worker is running. The next poll is the 2-hour timer. #249 is this log and is not graded.

## 2026-11-03 08:26 UTC — #284 has an outside PASS comment

#284 head is still `b36383c1828d8c8aa298ce69563fcca5d87f4a18`. A cursor[bot] comment says INDEPENDENT RECHECK PASS at that SHA. This lane did not run that recheck and does not adopt the comment. The SHA has not moved, so this lane does not start a recheck and does not post a second comment. #249 is this log and is not graded.

## 2026-11-03 09:36 UTC — #268 has an outside PASS comment

#268 head is still `e932dd3cd446ae97fa02692f47144ce6f3cd11fd`. A cursor[bot] comment says INDEPENDENT RECHECK PASS at that SHA. This lane did not run that recheck and does not adopt the comment. The SHA has not moved, so this lane does not start a recheck and does not post a second comment. #249 is this log and is not graded.

## 2026-11-03 09:40 UTC — #267 has an outside FAIL comment

#267 head is still `4b073e05abe1f1536166637952c49424f7f0160c`. A cursor[bot] comment says INDEPENDENT RECHECK FAIL at that SHA. This lane did not run that recheck and does not adopt the comment. The SHA has not moved, so this lane does not start a recheck and does not post a second comment. #249 is this log and is not graded.

## 2026-11-03 09:44 UTC — #260 has an outside PASS comment

#260 head is still `900de482717671ebc3f0e5360fd8349ce022d704`. A cursor[bot] comment says INDEPENDENT RECHECK PASS at that SHA. This lane did not run that recheck and does not adopt the comment. The older `e9729e40ab93` report stays uncommented. The SHA has not moved, so this lane does not start a recheck and does not post a second comment. #249 is this log and is not graded.

## 2026-11-03 10:17 UTC — two-hour poll, no moved head

Open drafts #217–#284 and #225 are still on the SHAs recorded above. #225 stays the PASS at `953e460b8f46`. #285 is new and is recorded at `78819eaf0d04`. It has not moved since it was first seen, so it was not started. No recheck worker is running. The next poll is the 2-hour timer. #249 is this log and is not graded.

## 2026-11-03 10:56 UTC — #225 moved to 5af4067

#225 head is now `5af406779a1ed164b2f11492481412aa88641e59` (“Compare parsed S06 offers instead of digit substrings”). Since `953e460b8f46` it also reads S06’s own JSON-LD offer in host health. `953e460b8f46` stays the commented PASS. One recheck of `5af406779a1e` is running. #260 and #267–#285 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 11:03 UTC — outside PASS on #225 while this lane is still running

#225 head is still `5af406779a1ed164b2f11492481412aa88641e59`. A cursor[bot] comment says INDEPENDENT RECHECK PASS at that SHA. This lane did not write that comment and does not adopt it. The recheck started at 10:56 UTC is still running. This lane will not post a second comment unless that review disagrees. #249 is this log and is not graded.

## 2026-11-03 11:16 UTC — #225 verified PASS at 5af4067, no second comment

`5af406779a1e` was still the head. This lane’s script passed: pytest 2423 passed, 7 skipped; privacy CLEAN; intake npm 353 / 350 / 0 / 3; shop npm 251 / 248 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261103-110834-408980`. S06’s own Product JSON-LD offer must parse to 25, and a stray `$25` is not the gate. Findings: none. The outside PASS was already on this SHA and this review agrees, so no second comment was posted. That worker was not sent on. #260 and #267–#285 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 12:17 UTC — two-hour poll, no moved head

Open drafts #217–#285 are still on the SHAs recorded above. #225 stays the verified PASS at `5af406779a1e`. No new draft appeared. No recheck worker is running. The next poll is the 2-hour timer. #249 is this log and is not graded.

## 2026-11-03 13:50 UTC — #225 moved to 77fde6a

#225 head is now `77fde6ab2f3b6a680c5de7b3654ac66582a1961e` (“Reject junk dollar and comma text in parse_usd”). `5af406779a1e` stays the verified PASS. One recheck of `77fde6ab2f3b` is running. #260 and #267–#285 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 13:57 UTC — outside PASS on #225 while this lane is still running

#225 head is still `77fde6ab2f3b6a680c5de7b3654ac66582a1961e`. A cursor[bot] comment says INDEPENDENT RECHECK PASS at that SHA. This lane did not write that comment and does not adopt it. The recheck started at 13:50 UTC is still running. This lane will not post a second comment unless that review disagrees. #249 is this log and is not graded.

## 2026-11-03 14:00 UTC — #225 verified PASS at 77fde6a, no second comment

`77fde6ab2f3b` was still the head. This lane’s script passed: pytest 2428 passed, 7 skipped; privacy CLEAN; intake npm 353 / 350 / 0 / 3; shop npm 251 / 248 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261103-135302-417160`. `parse_usd` returns null for `2$5` and `2,5`. `$25` stays 25 and `1,200` stays 1200. A null S06 price fails the $25 guard instead of becoming 25. Findings: none. The outside PASS was already on this SHA and this review agrees, so no second comment was posted. That worker was not sent on. #260 and #267–#285 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 14:18 UTC — two-hour poll, no moved head

Open drafts #217–#285 are still on the SHAs recorded above. #225 stays the verified PASS at `77fde6ab2f3b`. #286 is new and is recorded at `adcb7c41d760`. It has not moved since it was first seen, so it was not started. No recheck worker is running. The next poll is the 2-hour timer. #249 is this log and is not graded.

## 2026-11-03 16:18 UTC — two-hour poll, no moved head

Open drafts #217–#286 are still on the SHAs recorded above. #225 stays the verified PASS at `77fde6ab2f3b`. No new draft appeared. No recheck worker is running. The next poll is the 2-hour timer. #249 is this log and is not graded.

## 2026-11-03 18:18 UTC — two-hour poll, no moved head

Open drafts #217–#286 are still on the SHAs recorded above. #225 stays the verified PASS at `77fde6ab2f3b`. No new draft appeared. No recheck worker is running. The next poll is the 2-hour timer. #249 is this log and is not graded.

## 2026-11-03 19:30 UTC — #285 has outside PASS comments

#285 head is still `78819eaf0d049db3ecfc6049635f17781952aa63`. Cursor[bot] comments say INDEPENDENT RECHECK PASS at that SHA. This lane did not run those rechecks and does not adopt them. The SHA has not moved since it was first seen, so this lane does not start a recheck and does not post another comment. #249 is this log and is not graded.

## 2026-11-03 19:52 UTC — #225 moved to ecb7b20

#225 head is now `ecb7b20157736f3b2eef8761b664c4c6e85b7c05` (“Reject junk dollar text in pickup whole-dollar checks.”). `77fde6ab2f3b` stays the verified PASS. One recheck of `ecb7b2015773` is running. #260 and #267–#286 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 19:55 UTC — #225 moved to 0f4fcc2

#225 head is now `0f4fcc2c255fbb688eae8f04213856101dcb3df3` (“Keep a photo hash when the keep path spelling differs.”). Since `ecb7b2015773` it also keeps a photo hash when the folder spelling differs. `ecb7b2015773` is still in recheck and is not the head, so it will not be commented. One recheck of `0f4fcc2c255f` is running. #260 and #267–#286 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 19:58 UTC — outside PASS on the old #225 SHA

#225 head is still `0f4fcc2c255fbb688eae8f04213856101dcb3df3`. A cursor[bot] comment says INDEPENDENT RECHECK PASS at `ecb7b2015773`. This lane did not write that comment and does not adopt it. That SHA is not the head, and the comment does not cover `0f4fcc2c255f`. This lane will not post a second comment on `ecb7b2015773`. The recheck of `0f4fcc2c255f` is still running. #249 is this log and is not graded.

## 2026-11-03 20:02 UTC — outside PASS on #225 while this lane is still running

#225 head is still `0f4fcc2c255fbb688eae8f04213856101dcb3df3`. A cursor[bot] comment says INDEPENDENT RECHECK PASS at that SHA. This lane did not write that comment and does not adopt it. The recheck started at 19:55 UTC is still running. This lane will not post a second comment unless that review disagrees. #249 is this log and is not graded.

## 2026-11-03 20:07 UTC — #225 ecb7b20 verified PASS, not commented

`ecb7b2015773` is not the head. The head is still `0f4fcc2c255f`. This lane’s script for `ecb7b2015773` passed: pytest 2434 passed, 7 skipped; privacy CLEAN; intake npm 353 / 350 / 0 / 3; shop npm 251 / 248 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261103-195936-426636`. `_whole_dollars` returns null for `2$5`, `2,5`, and `25.50`. `$25` stays 25 and `1,200` stays 1200. An S06 junk sell does not publish. Findings: none. An outside PASS was already on that older SHA, and it is not the head, so no comment was posted. That worker was not sent on. The recheck of `0f4fcc2c255f` is still running. #249 is this log and is not graded.

## 2026-11-03 20:18 UTC — #225 verified PASS at 0f4fcc2, no second comment

`0f4fcc2c255f` was still the head. This lane’s script passed: pytest 2434 passed, 7 skipped; privacy CLEAN; intake npm 358 / 355 / 0 / 3; shop npm 251 / 248 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261103-201247-434830`. `a01/001.jpg` keeps the hash stored for `A01/001.jpg`. A claimed photo is not replaced when another row spells that folder differently; the new photo takes the next free name. `001.JPG` does not share the `001.jpg` hash. Findings: none. The outside PASS was already on this SHA and this review agrees, so no second comment was posted. That worker was not sent on. #260 and #267–#286 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 20:19 UTC — two-hour poll, no moved head

Open drafts #217–#286 are still on the SHAs recorded above. #225 stays the verified PASS at `0f4fcc2c255f`. #287 is new and is recorded at `cdb6d0451758`. It has not moved since it was first seen, so it was not started. No recheck worker is running. The next poll is the 2-hour timer. #249 is this log and is not graded.

## 2026-11-03 20:28 UTC — #225 moved to 8f4f7c0

#225 head is now `8f4f7c0624429afb7828efab8fab986c54f0e163` (“Keep the hash stored beside the kept photo spelling.”). `0f4fcc2c255f` stays the verified PASS. One recheck of `8f4f7c062442` is running. #260 and #267–#287 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 20:34 UTC — outside PASS on #225 while this lane is still running

#225 head is still `8f4f7c0624429afb7828efab8fab986c54f0e163`. A cursor[bot] comment says INDEPENDENT RECHECK PASS at that SHA. This lane did not write that comment and does not adopt it. The recheck started at 20:28 UTC is still running. This lane will not post a second comment unless that review disagrees. #249 is this log and is not graded.

## 2026-11-03 20:49 UTC — #225 verified PASS at 8f4f7c0, no second comment

`8f4f7c062442` was still the head. This lane’s script passed: pytest 2434 passed, 7 skipped; privacy CLEAN; intake npm 361 / 358 / 0 / 3; shop npm 251 / 248 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261103-204039-443377`. The exact keep spelling keeps the hash stored beside it. A different spelling is reused only when every stored hash for that photo agrees. Disagreeing hashes are re-read, and another mã’s file cannot supply the hash. A directory read does not abort the save. Findings: none. The outside PASS was already on this SHA and this review agrees, so no second comment was posted. That worker was not sent on. #260 and #267–#287 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 21:47 UTC — #225 moved to 2c58e88

#225 head is now `2c58e8868f4a172223f401737ff3f300faa1b5e7` (“Restore a saved shoe size onto the intake chip.”). `8f4f7c062442` stays the verified PASS. One recheck of `2c58e8868f4a` is running. #260 and #267–#287 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 21:54 UTC — outside PASS on #225 while this lane is still running

#225 head is still `2c58e8868f4a172223f401737ff3f300faa1b5e7`. A cursor[bot] comment says INDEPENDENT RECHECK PASS at that SHA. This lane did not write that comment and does not adopt it. The recheck started at 21:47 UTC is still running. This lane will not post a second comment unless that review disagrees. #249 is this log and is not graded.

## 2026-11-03 22:06 UTC — #225 verified PASS at 2c58e88, no second comment

`2c58e8868f4a` was still the head. This lane’s script passed: pytest 2434 passed, 7 skipped; privacy CLEAN; intake npm 364 / 361 / 0 / 3; shop npm 251 / 248 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261103-215708-451856`. `restoreSizes` folds exactly `NN.0` onto a catalog chip for that kind and keeps every other token. Shoe `35.0` becomes `35`. Clothing `40.0` stays `40.0`. A kept non-chip is saved as the size string and is not written into price or `sell_usd`. Findings: none. The outside PASS was already on this SHA and this review agrees, so no second comment was posted. That worker was not sent on. #260 and #267–#287 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 22:19 UTC — two-hour poll, no moved head

Open drafts #217–#287 are still on the SHAs recorded above. #225 stays the verified PASS at `2c58e8868f4a`. #288 is new and is recorded at `9dc8050db85b`. It has not moved since it was first seen, so it was not started. No recheck worker is running. The next poll is the 2-hour timer. #249 is this log and is not graded.

## 2026-11-03 22:36 UTC — #225 moved to 75e1d65

#225 head is now `75e1d6580ed88243c2339bb479d3d67cb319d028` (“Match color-bind slides to this branch's shop reel.”). Since `2c58e8868f4a` it also adds a read-only check for photo color binds (`f068aacf654b`). `2c58e8868f4a` stays the verified PASS. One recheck of `75e1d6580ed8` is running. #260 and #267–#288 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-03 22:44 UTC — outside PASS on #225 while this lane is still running

#225 head is still `75e1d6580ed88243c2339bb479d3d67cb319d028`. A cursor[bot] comment says INDEPENDENT RECHECK PASS at that SHA. This lane did not write that comment and does not adopt it. The recheck started at 22:36 UTC is still running. This lane will not post a second comment unless that review disagrees. #249 is this log and is not graded.

## 2026-11-03 22:52 UTC — #225 verified PASS at 75e1d65, no second comment

`75e1d6580ed8` was still the head. This lane’s script passed: pytest 2456 passed, 7 skipped; privacy CLEAN; intake npm 364 / 361 / 0 / 3; shop npm 251 / 248 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261103-224515-460351`. `scripts/color_bind.py` prints JSON from a local fixture. It refuses a URL, `held.json`, and the shop catalog. A slide counts only when `colorId` equals `color.id`. Prices are copied and nothing assigns 25. Findings: none. The outside PASS was already on this SHA and this review agrees, so no second comment was posted. That worker was not sent on. #260 and #267–#288 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-04 00:20 UTC — two-hour poll, no moved head

Open drafts #217–#288 are still on the SHAs recorded above. #225 stays the verified PASS at `75e1d6580ed8`. No new draft appeared. No recheck worker is running. The next poll is the 2-hour timer. #249 is this log and is not graded.

## 2026-11-04 01:57 UTC — #225 moved to 1eb4b39

#225 head is now `1eb4b39f124dd4fb8deb9980ee8f14e9f17d0eef` (“Reject a dollar sign between digits in intake gap numbers.”). `75e1d6580ed8` stays the verified PASS. One recheck of `1eb4b39f124d` is running. #260 and #267–#288 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-04 02:03 UTC — outside PASS on #225 while this lane is still running

#225 head is still `1eb4b39f124dd4fb8deb9980ee8f14e9f17d0eef`. A cursor[bot] comment says INDEPENDENT RECHECK PASS at that SHA. This lane did not write that comment and does not adopt it. A second outside PASS on the same SHA is not recorded again. The recheck started at 01:57 UTC is still running. This lane will not post a second comment unless that review disagrees. #249 is this log and is not graded.

## 2026-11-04 02:21 UTC — #225 commented FAIL at 1eb4b39

`1eb4b39f124d` was still the head. The script passed: pytest 2457 passed, 7 skipped; privacy CLEAN; intake npm 364 / 361 / 0 / 3; shop npm 251 / 248 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261104-021238-468691`. The review is FAIL. `_num` leaves `2.5e1` and `2_5` as 25, and `load_live` stores that as the price. `1,200` is None, and the new test locks that. The outside PASS on this SHA disagrees, so this lane posted the FAIL. That worker was not sent on. #260 and #267–#288 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-04 02:22 UTC — two-hour poll, no moved head

Open drafts #217–#288 are still on the SHAs recorded above. #225 stays the commented FAIL at `1eb4b39f124d`. #289 is new and is recorded at `40699842ba18`. It has not moved since it was first seen, so it was not started. No recheck worker is running. The next poll is the 2-hour timer. #249 is this log and is not graded.

## 2026-11-04 02:28 UTC — #225 moved to d3a8fc9

#225 head is now `d3a8fc9162c3f09a38031d71f44ed7c9612f5bdf` (“Reject exponent and underscore text in intake gap numbers.”). `1eb4b39f124d` stays the commented FAIL. One recheck of `d3a8fc9162c3` is running. #260 and #267–#289 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-04 02:34 UTC — outside PASS on #225 while this lane is still running

#225 head is still `d3a8fc9162c3f09a38031d71f44ed7c9612f5bdf`. A cursor[bot] comment says INDEPENDENT RECHECK PASS at that SHA. This lane did not write that comment and does not adopt it. The recheck started at 02:28 UTC is still running. This lane will not post a second comment unless that review disagrees. #249 is this log and is not graded.

## 2026-11-04 02:42 UTC — #225 commented FAIL at d3a8fc9

`d3a8fc9162c3` was still the head. The script passed: pytest 2457 passed, 7 skipped; privacy CLEAN; intake npm 364 / 361 / 0 / 3; shop npm 251 / 248 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261104-023451-477262`. The review is FAIL. `e`, `E`, and `_` now return None, so `2.5e1` and `2_5` are not 25. `1,200` is still None, and `scripts/tests/test_intake_gaps.py:139` locks that. `load_live` stores that as the price, so a sell of `1,200` does not raise `sell_vs_live` against a live 1200. The outside PASS on this SHA disagrees, so this lane posted the FAIL. That worker was not sent on. #260 and #267–#289 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-04 02:50 UTC — #225 moved to 6d1744a

#225 head is now `6d1744a149ef9743850e79c27a7f6c42119666ea` (“Read a thousands group as a number in intake gap prices.”). `d3a8fc9162c3` stays the commented FAIL. One recheck of `6d1744a149ef` is running. #260 and #267–#289 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-04 02:56 UTC — outside PASS on #225 while this lane is still running

#225 head is still `6d1744a149ef9743850e79c27a7f6c42119666ea`. A cursor[bot] comment says INDEPENDENT RECHECK PASS at that SHA. This lane did not write that comment and does not adopt it. The recheck started at 02:50 UTC is still running. This lane will not post a second comment unless that review disagrees. #249 is this log and is not graded.

## 2026-11-04 03:07 UTC — #225 verified PASS at 6d1744a, no second comment

`6d1744a149ef` was still the head. This lane’s script passed: pytest 2457 passed, 7 skipped; privacy CLEAN; intake npm 364 / 361 / 0 / 3; shop npm 251 / 248 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261104-025926-485305`. A comma is a thousands group only when the first group is 1–999 and every later group is exactly three digits. `1,200` is 1200. `2,5`, `12,50`, and `0,025` stay None. `2.5e1` and `2_5` stay None. `$25` stays 25. An intake sell of `1,200` against a live 25 raises `sell_vs_live`. Findings: none. The outside PASS was already on this SHA and this review agrees, so no second comment was posted. That worker was not sent on. #260 and #267–#289 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-04 04:15 UTC — #225 moved to 4fc9fa6

#225 head is now `4fc9fa61ee3e5ee328e7c3b44cac8d177cb87f58` (“Keep an in-window EU shoe size written as 40.0.”). `6d1744a149ef` stays the verified PASS. One recheck of `4fc9fa61ee3e` is running. #260 and #267–#289 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-04 04:20 UTC — outside PASS on #225 while this lane is still running

#225 head is still `4fc9fa61ee3e5ee328e7c3b44cac8d177cb87f58`. A cursor[bot] comment says INDEPENDENT RECHECK PASS at that SHA. This lane did not write that comment and does not adopt it. The recheck started at 04:15 UTC is still running. This lane will not post a second comment unless that review disagrees. #249 is this log and is not graded.

## 2026-11-04 04:22 UTC — two-hour poll, no moved head

Open drafts #217–#289 are still on the SHAs recorded above. #225 stays `4fc9fa61ee3e`, and that recheck is still running. No new draft appeared. The next poll is the 2-hour timer. #249 is this log and is not graded.

## 2026-11-04 04:32 UTC — #225 verified PASS at 4fc9fa6, no second comment

`4fc9fa61ee3e` was still the head. This lane’s script passed: pytest 2457 passed, 7 skipped; privacy CLEAN; intake npm 364 / 361 / 0 / 3; shop npm 254 / 251 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261104-042627-493567`. `parseAsiaSizes` keeps an exact `NN.0` when `NN` is already in `EU_SHOE_SIZES`, which was already 34–42. `40.0` becomes `40`. `34.0` and `42.0` become those chips because they were already on that list. `4.0`, `35.00`, and `40.00` stay empty. `40.` already became `40` before this commit, because the old strip removed the dot, and the new code still does that only when there is no digit on both sides of the dot. Findings: none. The outside PASS was already on this SHA and this review agrees, so no second comment was posted. That worker was not sent on. #260 and #267–#289 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-04 06:22 UTC — two-hour poll, no moved head

Open drafts #217–#289 are still on the SHAs recorded above. #225 stays the verified PASS at `4fc9fa61ee3e`. #290 is new and is recorded at `03236ca0caf0`. It has not moved since it was first seen, so it was not started. No recheck worker is running. The next poll is the 2-hour timer. #249 is this log and is not graded.

## 2026-11-04 06:25 UTC — outside PASS on #290, not adopted

#290 head is still `03236ca0caf0728ae2e6a99aa4b00cdd83ed4a73`. A cursor[bot] comment says INDEPENDENT RECHECK PASS at that SHA. This lane did not write that comment and does not adopt it. The SHA has not moved since it was first seen, so no recheck was started. #249 is this log and is not graded.

## 2026-11-04 08:23 UTC — two-hour poll, no moved head

Open drafts #217–#290 are still on the SHAs recorded above. #225 stays the verified PASS at `4fc9fa61ee3e`. #291 is new and is recorded at `633531e577e6`. It has not moved since it was first seen, so it was not started. No recheck worker is running. The next poll is the 2-hour timer. #249 is this log and is not graded.

## 2026-11-04 08:33 UTC — #225 moved to 39cd5cb

#225 head is now `39cd5cbe994cc4839275ccb6ff9b382d9cd043b7` (“Match the shop's copy check on lead promises and spacing.”). Since `4fc9fa61ee3e` the tree also rejects a currency mark and exponent text in held price proposals and flags customer copy the shop treats as stock or ops voice. `4fc9fa61ee3e` stays the verified PASS. One recheck of `39cd5cbe994c` is running. No comment is on this SHA yet. #260 and #267–#291 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-04 08:40 UTC — outside PASS on #225, not adopted

#225 head is still `39cd5cbe994cc4839275ccb6ff9b382d9cd043b7`. A cursor[bot] comment says INDEPENDENT RECHECK PASS at that SHA. This lane did not write that comment and does not adopt it. The recheck started at 08:33 UTC is still running. This lane will not post a second comment unless that review disagrees. #249 is this log and is not graded.

## 2026-11-04 08:49 UTC — #225 verified PASS at 39cd5cb

`39cd5cbe994c` was still the head. This lane’s script passed: pytest 2478 passed, 7 skipped; privacy CLEAN; intake npm 364 / 361 / 0 / 3; shop npm 254 / 251 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261104-083533-502040`. `held_price_proposal._num` reads `1,200` as 1200 and `$25` and `¥110` as those amounts. `2$5`, `2¥5`, `2,5`, `2.5e1`, `2_5`, `0,025`, and `12,50` stay blank, and `0,025` is not 25. The copy check matches the shop lists in `public-safety.ts` and the lead pattern in `warehouse-voice.ts`. `Flat $8` flags on a description in any ASCII case. A title or a color does not carry that lead. The four copy fields are joined with a space and no trim, so `on` plus `hand` flags and `on ` plus `hand` does not. The check does not write a price. Findings: none. The outside PASS was already on this SHA and this review agrees, so no second comment was posted. That worker was not sent on. #260 and #267–#291 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-04 10:23 UTC — two-hour poll, no moved head

Open drafts #217–#291 are still on the SHAs recorded above. #225 stays the verified PASS at `39cd5cbe994c`. No new draft appeared. No recheck worker is running. The next poll is the 2-hour timer. #249 is this log and is not graded.

## 2026-11-04 10:45 UTC — #225 moved to dea7e32

#225 head is now `dea7e325b3a8b68a03bb890e630aa918b2fbee6e` (“404 a held product photo before the public file is served.”). `39cd5cbe994c` stays the verified PASS. One recheck of `dea7e325b3a8` is running. No comment is on this SHA yet. #260 and #267–#291 are unchanged and are not started. #249 is this log and is not graded.

## 2026-11-04 10:52 UTC — outside PASS on #225, not adopted

#225 head is still `dea7e325b3a8b68a03bb890e630aa918b2fbee6e`. Two cursor[bot] comments say INDEPENDENT RECHECK PASS at that SHA. This lane did not write those comments and does not adopt them. The recheck started at 10:45 UTC is still running. This lane will not post a second comment unless that review disagrees. #249 is this log and is not graded.

## 2026-11-04 10:54 UTC — outside FAIL on #225, not adopted

#225 head is still `dea7e325b3a8b68a03bb890e630aa918b2fbee6e`. A cursor[bot] comment says INDEPENDENT RECHECK FAIL at that SHA. The finding is that `/_next/image` is outside the proxy matcher and the optimizer still reads the public held file. This lane did not write that comment and does not adopt it. The recheck started at 10:45 UTC is still running. This lane will not post a comment unless that review disagrees with the comments already on the SHA. #249 is this log and is not graded.

## 2026-11-04 10:56 UTC — outside FAIL on #225 withdrawn, not adopted

#225 head is still `dea7e325b3a8b68a03bb890e630aa918b2fbee6e`. The same outside thread withdrew the FAIL. It now says the optimizer's internal read runs the proxy before the public file, and it repeats INDEPENDENT RECHECK PASS at this SHA. This lane did not write that correction and does not adopt it. The recheck started at 10:45 UTC is still running. #249 is this log and is not graded.

## 2026-11-04 11:05 UTC — #225 FAIL at dea7e32, not commented; head is 269fea5

`dea7e325b3a8` finished after the head moved, so it is not commented. This lane’s script passed: pytest 2478 passed, 7 skipped; privacy CLEAN; intake npm 364 / 361 / 0 / 3; shop npm 258 / 255 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261104-105013-510485`. The review is FAIL. `heldPublicImage` returns at `sassy-closet-shop/proxy.ts` lines 18–20 when the pathname does not literally start with `/products/`. A real `proxy()` call gets status 200 for `/products%2FS14%2Fcover.jpg`, `/products%2FS14/cover.jpg`, and `/products%2fS14%2fcover.jpg`. One `decodeURIComponent` of each is `/products/S14/cover.jpg`, which `catalogImageFolder` calls off-live. Next’s public lookup matches that decoded path and serves `public/products/S14/cover.jpg` when the file exists. The canonical `/products/S14/cover.jpg` path does 404. Outside PASS comments on `dea7e325b3a8` disagree with this review. The SHA is not the head, so no comment was posted. That worker was not sent on.

#225 head is now `269fea55fc85b0eb798a46ee4988306ceee6c2f6` (“404 a held product photo when the image optimizer asks for it.”). One recheck of `269fea55fc85` is running. #249 is this log and is not graded.

## 2026-11-04 11:10 UTC — #225 moved to 1c913da; outside PASS on 269fea5 not adopted

#225 head is now `1c913dadc46565bdb0387569d7fb1f19bc176d88` (“Revert 404 a held product photo when the image optimizer asks for it.”). Its tree is `aa41610c8f7984c765fea8013e622123c7c6c6db`, the same tree as the FAIL at `dea7e325b3a8`. One recheck of `1c913dadc465` is running. `269fea55fc85` is no longer the head. A cursor[bot] comment says INDEPENDENT RECHECK PASS at `269fea55fc85`. This lane did not write that comment and does not adopt it. The recheck of that SHA is still running and will not be commented. #249 is this log and is not graded.

## 2026-11-04 11:17 UTC — outside PASS on #225 at 1c913da, not adopted

#225 head is still `1c913dadc46565bdb0387569d7fb1f19bc176d88`. A cursor[bot] comment says INDEPENDENT RECHECK PASS at that SHA. This lane did not write that comment and does not adopt it. The tree matches the FAIL at `dea7e325b3a8`. The recheck started at 11:10 UTC is still running. This lane will not post a second comment unless that review disagrees. #249 is this log and is not graded.

## 2026-11-04 11:20 UTC — #225 commented FAIL at 1c913da

`1c913dadc465` was still the head. This lane’s script passed: pytest 2478 passed, 7 skipped; privacy CLEAN; intake npm 364 / 361 / 0 / 3; shop npm 258 / 255 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261104-111232-519532`. The tree is the same as `dea7e325b3a8`. The review is FAIL. `heldPublicImage` returns at `sassy-closet-shop/proxy.ts` lines 18–19 when the pathname does not literally start with `/products/`. A real `proxy()` call gets status 200 for `/products%2FS14%2Fcover.jpg`, `/products%2FS14/cover.jpg`, and `/products%2fS14%2fcover.jpg`. One decode of each is `/products/S14/cover.jpg`, which is off-live, and Next’s public lookup serves that file when it exists. The canonical path does 404. The outside PASS comments disagree, so this lane posted INDEPENDENT RECHECK FAIL. That worker was not sent on. `269fea55fc85` is still not the head. #249 is this log and is not graded.

## 2026-11-04 11:24 UTC — outside PASS on #225 withdrawn

#225 head is still `1c913dadc46565bdb0387569d7fb1f19bc176d88`. Two outside threads withdrew their PASS comments and now say INDEPENDENT RECHECK FAIL for the same `%2F` hole. This lane did not write those corrections. The FAIL comment already on this SHA agrees, so no second comment was posted. #249 is this log and is not graded.

## 2026-11-04 11:27 UTC — #225 FAIL at 269fea5, not commented

`269fea55fc85` is not the head. The head is `1c913dadc465`. This lane’s script on `269fea55fc85` passed: pytest 2478 passed, 7 skipped; privacy CLEAN; intake npm 364 / 361 / 0 / 3; shop npm 261 / 258 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261104-111723-527516`. The review is FAIL. `heldPublicImage` still returns before the second decode when the string does not literally start with `/products/`. Direct `/products%2FS14%2Fcover.jpg`, `/products%2FS14/cover.jpg`, `/products%2fS14%2fcover.jpg`, and `/products%2F%53%31%34%2Fcover.jpg` get status 200. An encoded optimizer `url` that is still one of those strings also gets status 200. One decode is `/products/S14/cover.jpg`, which is off-live, and Next’s public lookup serves that file when it exists. A recognized held optimizer url does 404, and a live optimizer url continues. The outside PASS on `269fea55fc85` disagrees. The SHA is not the head, so no comment was posted. That worker was not sent on. #249 is this log and is not graded.

## 2026-11-04 11:28 UTC — #225 moved to ec78e08

#225 head is now `ec78e0836cbb31d956fb83c68a9d7f9c71d05891` (“404 a held product photo when the products slash is percent-encoded.”). `1c913dadc465` stays the commented FAIL. One recheck of `ec78e0836cbb` is running. #249 is this log and is not graded.

## 2026-11-04 11:34 UTC — outside PASS on #225 ec78e08

cursor[bot] comment `6629533799` says INDEPENDENT RECHECK PASS at `ec78e0836cbb31d956fb83c68a9d7f9c71d05891`. This lane did not write it. The recheck of that SHA is still running, so the PASS is not adopted and no second comment was posted. #249 is this log and is not graded.

## 2026-11-04 11:36 UTC — second outside PASS on #225 ec78e08

cursor[bot] comment `6629574632` also says INDEPENDENT RECHECK PASS at `ec78e0836cbb31d956fb83c68a9d7f9c71d05891`. The head is still that SHA. This lane did not write it. The recheck is still running, so neither outside PASS is adopted and no comment was posted. #249 is this log and is not graded.

## 2026-11-04 11:39 UTC — #225 PASS at ec78e08, outside comments agree

#225 head is still `ec78e0836cbb31d956fb83c68a9d7f9c71d05891`. This lane’s recheck passed. pytest 2478 passed, 7 skipped; privacy CLEAN; intake npm 364 / 361 / 0 / 3; shop npm 258 / 255 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261104-113105-536396`. `heldPublicImage` now decodes the whole pathname when the first folder check is not `off-live`. `/products%2FS14%2Fcover.jpg`, `/products%2FS14/cover.jpg`, and `/products%2fS14%2fcover.jpg` return 404 `Not found` with `no-store` and no `Location`. One decode of each is `/products/S14/cover.jpg`, which Next’s public lookup would serve when the file exists. `/products/A01/cover.jpg` and `/products/S06/cover.jpg` continue. `/products/a1/cover.jpg` still 308s to `/products/A01/cover.jpg`. `/products%2FA01%2Fcover.jpg`, `/products%2FS06%2Fcover.jpg`, and `/products%2Fa1%2Fcover.jpg` are not this 404. `/products%252FS14%252Fcover.jpg` continues, and one server decode is not the held file. No CSS, price, or `held.json` change. S06 stays off the held list. Outside comments `6629533799` and `6629574632` already say PASS on this SHA and agree, so no second comment was posted. #249 is this log and is not graded.

## 2026-11-04 12:24 UTC — poll, no head moved

Open heads from #217 through #291 match the SHAs recorded above. #225 is still `ec78e0836cbb`. #292 is new: draft `7b6830ae0473df2cbe7467d4d4af88cc4ece68d3`, “Reject spliced dollar text in blank-mã order prices,” one commit, created 12:17 UTC, no comments. It has not moved since it was first seen, so no recheck was started. No worker is running. #249 is this log and is not graded.

## 2026-11-04 12:26 UTC — outside PASS on #292

#292 head is still `7b6830ae0473df2cbe7467d4d4af88cc4ece68d3`. cursor[bot] comment `6630552776` says INDEPENDENT RECHECK PASS at that SHA. This lane did not write it and does not adopt it. The draft has not moved since it was first seen, so no recheck was started and no comment was posted. #249 is this log and is not graded.

## 2026-11-04 12:28 UTC — #225 moved to d8a795d

#225 head is now `d8a795d83902c21bc0e6a09e0896bfa82c57f7fc` (“404 a held product photo when one decode resolves to that file.”). Parent is the verified PASS at `ec78e0836cbb`. One recheck of `d8a795d83902` is running. #249 is this log and is not graded.

## 2026-11-04 12:35 UTC — outside PASS on #225 d8a795d

cursor[bot] comment `6630749382` says INDEPENDENT RECHECK PASS at `d8a795d83902c21bc0e6a09e0896bfa82c57f7fc`. The head is still that SHA. This lane did not write it. The recheck is still running, so the PASS is not adopted and no second comment was posted. #249 is this log and is not graded.

## 2026-11-04 12:36 UTC — second outside PASS on #225 d8a795d

cursor[bot] comment `6630763290` also says INDEPENDENT RECHECK PASS at `d8a795d83902c21bc0e6a09e0896bfa82c57f7fc`. The head is still that SHA. This lane did not write it. The recheck is still running, so neither outside PASS is adopted and no comment was posted. #249 is this log and is not graded.

## 2026-11-04 12:38 UTC — outside FAIL on #225 d8a795d

cursor[bot] comment `6630793433` says INDEPENDENT RECHECK FAIL at `d8a795d83902c21bc0e6a09e0896bfa82c57f7fc`. The head is still that SHA. This lane did not write it. It disagrees with comments `6630749382` and `6630763290`. The claimed hole is that `pathAfterOneDecode` returns null when `..` empties the stack, so `proxy()` continues for `/foo%2F..%2F..%2Fpublic%2Fproducts%2FS14%2Fcover.jpg` and `/uploads/..%2F..%2Fpublic%2Fproducts%2FS14%2Fcover.jpg`, while one decode joined onto the shop `public` directory is `public/products/S14/cover.jpg`. The recheck is still running, so the FAIL is not adopted and no comment was posted. The running recheck could not be given this path while it was still in progress.

## 2026-11-04 12:39 UTC — one outside PASS on #225 d8a795d withdrawn

#225 head is still `d8a795d83902c21bc0e6a09e0896bfa82c57f7fc`. cursor[bot] comment `6630820068` withdraws the PASS in comment `6630763290` and now says INDEPENDENT RECHECK FAIL for the same `public` walk-back. Comment `6630763290` itself is unchanged. Comment `6630749382` still says PASS. Comment `6630793433` already said FAIL. This lane wrote none of them. The recheck is still running, so none is adopted and no comment was posted. #249 is this log and is not graded.

## 2026-11-04 12:45 UTC — #225 moved to d79e85e

#225 head is now `d79e85eeb8a9971267cd6761968f7cef86e85f26` (“404 a held product photo when a dot-dot walks back through public.”). `d8a795d83902` is no longer the head. Its recheck was still running when the head moved, so that result will not be commented. No comment is on `d79e85eeb8a9` yet. One recheck of that SHA is running. The new function starts its segment stack at `public`, so `/..%2Fpublic%2Fproducts%2FS14%2Fcover.jpg` is meant to 404. `path.posix.join` of `sassy-closet-shop/public` with `/../../sassy-closet-shop/public/products/S14/cover.jpg` is still that held file. The recheck is checking whether `proxy()` continues on that path. #249 is this log and is not graded.

## 2026-11-04 12:48 UTC — #225 PASS at d8a795d, not commented

`d8a795d83902c21bc0e6a09e0896bfa82c57f7fc` is not the head. The head is `d79e85eeb8a9`. This lane’s script on `d8a795d83902` passed: pytest 2478 passed, 7 skipped; privacy CLEAN; intake npm 364 / 361 / 0 / 3; shop npm 261 / 258 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261104-123120-545157`. The review is PASS, so no comment was posted. `pathAfterOneDecode` returns null for a `..` that leaves the URL root, including `/..%2Fpublic%2Fproducts%2FS14%2Fcover.jpg`. Dev `getItem` can join that path back onto `public/products/S14/cover.jpg` (`filesystem.js` lines 551–557). The bytes are read by `serveStatic` from the request path, not from that joined path (`router-server.js` lines 455–459). `send` normalizes `./` plus one decode and returns 403 when `..` remains (`compiled/send/index.js` `SendStream.pipe`). A direct simulation of that check blocks `/../public/products/S14/cover.jpg`, `/foo/../../public/products/S14/cover.jpg`, and `/../../sassy-closet-shop/public/products/S14/cover.jpg`. It does not block `/uploads/../products/S14/cover.jpg` or `/products%2FS14%2Fcover.jpg`, and `proxy()` 404s both of those. The outside FAIL comments on this SHA disagree. The SHA is not the head, so no comment was posted. That worker was not sent on. #249 is this log and is not graded.

## 2026-11-04 12:50 UTC — outside PASS on #225 d79e85e

cursor[bot] comment `6631036929` says INDEPENDENT RECHECK PASS at `d79e85eeb8a9971267cd6761968f7cef86e85f26`. The head is still that SHA. This lane did not write it. The recheck is still running, so the PASS is not adopted and no second comment was posted. #249 is this log and is not graded.

## 2026-11-04 12:51 UTC — outside FAIL on #225 d79e85e

cursor[bot] comment `6631062652` says INDEPENDENT RECHECK FAIL at `d79e85eeb8a9971267cd6761968f7cef86e85f26`. The head is still that SHA. This lane did not write it. It disagrees with comment `6631036929`. The claimed hole is that `proxy()` continues for `/foo%2F..%2F..%2F..%2Fsassy-closet-shop%2Fpublic%2Fproducts%2FS14%2Fcover.jpg` and the `uploads` form, while `path.posix.join` of the shop `public` directory with those paths is `public/products/S14/cover.jpg`. The recheck is still running, so the FAIL is not adopted and no comment was posted. On the previous SHA, the dev join naming that file was not the read: `send` returns 403 when `..` remains after normalizing `./` plus one decode. #249 is this log and is not graded.

## 2026-11-04 13:02 UTC — #225 PASS at d79e85e, not commented

`d79e85eeb8a9971267cd6761968f7cef86e85f26` is not the head. The head is `52df79f5ca65`. This lane’s script on `d79e85eeb8a9` passed: pytest 2478 passed, 7 skipped; privacy CLEAN; intake npm 364 / 361 / 0 / 3; shop npm 262 / 259 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261104-124846-554108`. The worker called it FAIL because `proxy()` continues for `/foo%2F..%2F..%2F..%2Fsassy-closet-shop%2Fpublic%2Fproducts%2FS14%2Fcover.jpg` and the `uploads` form while `path.posix.join` names `public/products/S14/cover.jpg`. This lane does not adopt that FAIL. A direct `send` call with a fixture held file returns 403 and an HTML error for both paths, not the file bytes. The same call returns the bytes for `/uploads/..%2Fproducts/S14/cover.jpg` and `/products%2FS14%2Fcover.jpg`, and `proxy()` 404s both. `send` normalizes `./` plus one decode and rejects a remaining `..` before the root join (`compiled/send/index.js` `SendStream.pipe`). The dev join is only the existence check (`filesystem.js` lines 551–557). The read uses the request path (`router-server.js` lines 455–459). Outside comment `6631036929` says PASS and agrees. Outside comment `6631062652` says FAIL and disagrees. The SHA is not the head, so no comment was posted. That worker was not sent on. #249 is this log and is not graded.

## 2026-11-04 13:02 UTC — #225 moved to 52df79f

#225 head is now `52df79f5ca65d4a24ddfa33cbcb23f20e93a61a8` (“404 a held product photo when a dot-dot walks back through the shop directory.”). One recheck of that SHA is running. The new function builds the dev-join stack from `process.cwd()` plus `/public`. #249 is this log and is not graded.

## 2026-11-04 13:09 UTC — outside PASS on #225 52df79f

cursor[bot] comment `6631479049` says INDEPENDENT RECHECK PASS at `52df79f5ca65d4a24ddfa33cbcb23f20e93a61a8`. The head is still that SHA. This lane did not write it. It calls `d79e85eeb8a9` a FAIL. This lane’s reading of that older SHA is PASS, because `send` returns 403 and does not return the file bytes. The recheck of `52df79f5ca65` is still running, so the PASS is not adopted and no second comment was posted. #249 is this log and is not graded.

## 2026-11-04 13:12 UTC — second outside PASS on #225 52df79f

cursor[bot] comment `6631541732` also says INDEPENDENT RECHECK PASS at `52df79f5ca65d4a24ddfa33cbcb23f20e93a61a8`. The head is still that SHA. This lane did not write it. It also calls `d79e85eeb8a9` a FAIL. This lane’s reading of that older SHA stays PASS. The recheck is still running, so neither outside PASS is adopted and no comment was posted. #249 is this log and is not graded.

## 2026-11-04 13:17 UTC — #225 PASS at 52df79f, outside comments agree

#225 head is still `52df79f5ca65d4a24ddfa33cbcb23f20e93a61a8`. This lane’s recheck passed. pytest 2478 passed, 7 skipped; privacy CLEAN; intake npm 364 / 361 / 0 / 3; shop npm 262 / 259 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261104-130532-562303`. `proxy()` returns 404 `Not found` with `no-store` and no `Location` for every probed path whose `send` normalize has no `..` and joins to `public/products/S14/cover.jpg`, including `/products%2FS14%2Fcover.jpg` and `/uploads/..%2Fproducts/S14/cover.jpg`. Those two stream the fixture bytes from `send`. The shop-directory walks, including the full cwd walk, are proxy 404s of paths `send` answers with 403 and does not stream. `/products/A01/cover.jpg` continues and `send` streams that live file. `/products/a1/cover.jpg` still 308s to `/products/A01/cover.jpg`. `/products/S06/cover.jpg` continues. S06 stays off the held list. No CSS, price, or `held.json` change in this commit. Outside comments `6631479049` and `6631541732` already say PASS on this SHA and agree, so no second comment was posted. #249 is this log and is not graded.

## 2026-11-04 13:39 UTC — #225 moved to 7e1ef27

#225 head is now `7e1ef27ef77321757e623b7a324afbde0163703e` (“404 a held product photo when the process started above the shop.”). `52df79f5ca65` stays the verified PASS. One recheck of `7e1ef27ef773` is running. The tip also contains `66d8892`, which rejects spliced dollar text in blank-mã order prices. The proxy now checks the shop directory beside `proxy.ts` as well as `process.cwd()`, so a process started in the parent directory still 404s a `..` walk through this shop name. #249 is this log and is not graded.

## 2026-11-04 13:41 UTC — outside FAIL on unmoved #292

#292 head is still `7b6830ae0473df2cbe7467d4d4af88cc4ece68d3`. cursor[bot] comment `6632172647` says INDEPENDENT RECHECK FAIL at that SHA and disagrees with the earlier outside PASS `6630552776`. This lane did not write it and does not adopt it. The draft has not moved since it was first seen, so no recheck was started and no comment was posted. The same price commit is in the #225 head `7e1ef27ef773` that is already being rechecked. The claimed hole is that `_THOUSANDS` accepts a leading zero group, so `0,025` returns `0025`, and `Decimal("0025")` is 25. #249 is this log and is not graded.

## 2026-11-04 13:47 UTC — outside PASS on #225 at 7e1ef27

#225 head is still `7e1ef27ef77321757e623b7a324afbde0163703e`. cursor[bot] comments `6632278826` and `6632291274` both say INDEPENDENT RECHECK PASS at that SHA. This lane did not write them and does not adopt them. This lane’s recheck of the same SHA is still running, so no comment was posted. Both say `0,025` still parses as `25` because the previous parser stripped the comma and `Decimal` read `0025` as 25, and both still pass the SHA. The outside FAIL `6632172647` on unmoved #292 treats that same parse as a fail. #249 is this log and is not graded.

## 2026-11-04 13:50 UTC — outside FAIL on #225 at 7e1ef27

#225 head is still `7e1ef27ef77321757e623b7a324afbde0163703e`. cursor[bot] comment `6632342594` says INDEPENDENT RECHECK FAIL at that SHA and disagrees with PASS comments `6632278826` and `6632291274`. This lane did not write it and does not adopt it. This lane’s recheck of the same SHA is still running, so no comment was posted. The held-photo part of that FAIL says the proxy 404 holds. The price claim is that `_THOUSANDS` accepts `0,025` and `_price_text` returns `0025`, which `Decimal` reads as 25. The parent parser at `52df79f5ca65` already stripped every comma and returned that same `0025` text. #249 is this log and is not graded.

## 2026-11-04 13:51 UTC — one #225 PASS withdrawn, #292 moved

#225 head is still `7e1ef27ef77321757e623b7a324afbde0163703e`. cursor[bot] comment `6632382304` withdraws the PASS whose log is `out/recheck/20261104-134224-126676`, which is comment `6632278826`, and says FAIL on this SHA. This lane did not write it and does not adopt it. PASS `6632291274` is a different log and is not named by that withdrawal. This lane’s recheck of `7e1ef27ef773` is still running, so no comment was posted.

#292 head is now `7ea4e6c9136840f063c8dd8e4d66280f1b7fa110` (“Reject a thousands group that starts with zero.”). `7b6830ae0473` was the first-seen SHA and was not graded. One recheck of `7ea4e6c91368` is running. The new pattern is `[1-9]\d{0,2}(?:,\d{3})+(?:\.\d+)?`, so a thousands group that starts with zero is supposed to raise. No comment is on this SHA yet. #249 is this log and is not graded.

## 2026-11-04 13:59 UTC — #292 PASS at 7ea4e6c

#292 head is still `7ea4e6c9136840f063c8dd8e4d66280f1b7fa110`. This lane’s recheck passed. pytest 2115 passed, 7 skipped; privacy CLEAN; intake npm 277 / 274 / 0 / 3; shop npm 218 / 215 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261104-135320-579445`. `_THOUSANDS` is `[1-9]\d{0,2}(?:,\d{3})+(?:\.\d+)?`. `0,025`, `$0,025`, `0,025$`, `00,025`, `000,025`, `0,000,025`, `0,250`, `01,200`, and `01,025` raise `price must be a number`. `1,025` returns `1025`. `$1,200.00` returns `1200.00`. S06 `$25` is a clean line at the string `25` with no flag. S06 `0,025` raises. Plain `025` returns `025`, the same string the parent returned. `flag_fixture` does not rewrite the fixture. No CSS. The diff is only `scripts/order_blank_ma.py` and `scripts/tests/test_order_blank_ma.py`. Comment `6632568655` says PASS on this SHA. No other comment is on this SHA. #249 is this log and is not graded.

## 2026-11-04 14:00 UTC — #225 moved to 8fea4bb, outside PASS agrees on #292

#225 head is now `8fea4bbf52905261ab4756b78b10653f3c4e3a3d` (“Reject a zero first group in blank-mã thousands prices.”). `7e1ef27ef773` is no longer the head. The recheck of that older SHA was still running when the head moved, so that run will not be commented. One recheck of `8fea4bbf5290` is running. No comment is on this SHA yet. The new pattern is `[1-9]\d{0,2}(?:,\d{3})+(?:\.\d+)?`. The proxy file is unchanged from `7e1ef27ef773`.

#292 head is still `7ea4e6c9136840f063c8dd8e4d66280f1b7fa110`. cursor[bot] comment `6632571977` says PASS on that SHA and agrees with this lane’s comment `6632568655`. This lane did not write `6632571977`. No second comment was posted. #249 is this log and is not graded.

## 2026-11-04 14:04 UTC — #225 PASS at 7e1ef27, not the head

#225 head is still `8fea4bbf52905261ab4756b78b10653f3c4e3a3d`. The recheck of `7e1ef27ef77321757e623b7a324afbde0163703e` finished after the head moved, so no comment was posted on that older SHA. pytest 2479 passed, 7 skipped; privacy CLEAN; intake npm 364 / 361 / 0 / 3; shop npm 263 / 260 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261104-134219-571027`. `proxy()` returns 404 for `/products%2FS14%2Fcover.jpg` and `/uploads/..%2Fproducts/S14/cover.jpg` with cwd in the shop and again with cwd in the parent. Those are the paths `send` would stream. The shop-name walks are proxy 404s of paths `send` answers with 403. `/products/A01/cover.jpg` and `/products/S06/cover.jpg` continue. `/products/a1/cover.jpg` still 308s to `/products/A01/cover.jpg`. `2$5` and `12,50` raise. S06 `$25` stays the string `25` with no flag. `0,025` returns `0025`. The parent parser at `52df79f5ca65` already returned that same text. The outside FAILs `6632342594` and `6632382304` treat that parse as a fail and are not adopted. The recheck of `8fea4bbf5290` is still running. #249 is this log and is not graded.

## 2026-11-04 14:06 UTC — outside PASS on #225 at 8fea4bb

#225 head is still `8fea4bbf52905261ab4756b78b10653f3c4e3a3d`. cursor[bot] comment `6632716587` says INDEPENDENT RECHECK PASS at that SHA. This lane did not write it and does not adopt it. This lane’s recheck of the same SHA is still running, so no comment was posted. That outside comment says `0,025`, `$0,025`, `0,025$`, `00,025`, `000,025`, `0,000,025`, `0,250`, `01,025`, and `01,200` raise, and S06 `$25` stays `25`. It calls `7e1ef27ef773` a FAIL. This lane’s reading of that older SHA is the uncommented PASS above. #249 is this log and is not graded.

## 2026-11-04 14:10 UTC — #225 PASS at 8fea4bb, outside comment agrees

#225 head is still `8fea4bbf52905261ab4756b78b10653f3c4e3a3d`. This lane’s recheck passed. pytest 2479 passed, 7 skipped; privacy CLEAN; intake npm 364 / 361 / 0 / 3; shop npm 263 / 260 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261104-140212-586216`. `_THOUSANDS` is `[1-9]\d{0,2}(?:,\d{3})+(?:\.\d+)?`. `0,025`, `$0,025`, `0,025$`, `00,025`, `01,200`, and `01,025` raise. `1,025` returns `1025`. `$1,200.00` returns `1200.00`. S06 `$25` stays the string `25` with no flag. S06 `0,025` raises. Plain `025` returns `025`. `sassy-closet-shop/proxy.ts` is unchanged from `7e1ef27ef773`. `/products%2FS14%2Fcover.jpg` is 404. `/products/A01/cover.jpg` and `/products/S06/cover.jpg` continue. `/products/a1/cover.jpg` is 308 to `/products/A01/cover.jpg`. Outside comment `6632716587` already says PASS on this SHA and agrees, so no second comment was posted. #249 is this log and is not graded.

## 2026-11-04 14:14 UTC — #225 PASS stands, outside FAIL not adopted

#225 head is still `8fea4bbf52905261ab4756b78b10653f3c4e3a3d`. cursor[bot] comment `6632848598` says FAIL at that SHA. This lane did not write it. The blank-mã parser rejects `0,025`. The order flag, packing slip, order-vs-catalog check, desk, and `plainAmount` still read a zero first group as the same number `origin/main` already produced. Order flags and the packing slip return `25` for `0,025` and `2$5`. Main's comma-and-dollar strip returned `25` for both. `plainAmount("0,025")` is `25`, and main `parseMoney` was `25`. `plainAmount("2$5")` is `null`, and main `parseMoney("2$5")` was `null`. `12,50` now raises where main returned `1250`. Comment `6632912553` says PASS on this SHA. #249 is this log and is not graded.

## 2026-11-05 04:47 UTC — #225, #285, and #288 PASS

Requested recheck of these three heads. This lane did not build them.

#225 head is now `0bcfd493c42083cef5c388b0544abdc651b58034` (“Reject a zero-first thousands group in the S06 lock.”). `8fea4bbf5290` stays the prior PASS. Since that SHA the other-parser change was added and reverted, so the net diff is the S06 lock in `publish-guard.ts` plus its tests. pytest 2479 passed, 7 skipped; privacy CLEAN; intake npm 364 / 361 / 0 / 3; shop npm 263 / 260 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261105-043512-3658`. `wholeDollars("0,025")` and the other zero-first comma spellings were 25 on `8fea4bb` and are `NaN` here, so S06, S006, and S6 publish returns `s06-lock`. `$25` stays 25. `$1,200` stays 1200. K06 stays `held`. `025` and `0025` still read as 25, the same as the parent and `origin/main`. Comment `6649937807` says PASS on this SHA.

#285 head is still `78819eaf0d049db3ecfc6049635f17781952aa63`. This lane had not started it. pytest 2121 passed, 7 skipped; privacy CLEAN; intake npm 277 / 274 / 0 / 3; shop npm 218 / 215 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261105-043512-3705`. A shop-shaped S06 offer of `25.00` passes with stray `$25` on the page. Offer `30.00` with stray `$25` fails. Null, boolean, `25.50`, `0,025`, `025`, `0025`, and `S06B` fail. `S006` and `S6` at 25 pass. `priceCurrency` is not read; the shop writer sets USD. Comment `6649939263` says PASS on this SHA. The host check was not run against the live hosts.

#288 head is still `9dc8050db85ba666837152f5991878d916974da9`. This lane had not started it. pytest 2131 passed, 7 skipped; privacy CLEAN; intake npm 277 / 274 / 0 / 3; shop npm 218 / 215 / 0 / 3; both tsc ok; `held.json` unchanged. Required skips: none. Log `out/recheck/20261105-043512-3733`. A photo in another hub folder does not count as a slide. Canonical `A02` own-folder slides match the reel. A URL, `held.json`, and the shop catalog are refused. A shared src can still look covered for the second color; the pull request states that limit. Comment `6649940705` says PASS on this SHA.

#249 is this log and is not graded.

## 2026-11-02 23:55 UTC — #225 moved again

#225 head is `d8170670ab411fe21c38630f4a38b8ecdae711e8`. The FAIL on `72d792580d71` stays the comment for that older SHA. The new head is in hard recheck and is not commented yet. #226, #243, and #253 are commented at the SHAs in the verdict table. Their log directories are `out/recheck/20261102-234222-157269`, `out/recheck/20261102-234641-168787`, and `out/recheck/20261102-234412-161336`. No knowledge-lane docs PR.

This log lives on draft PR #249 (`cursor/independent-recheck-log-cfee`). That PR is this lane's own notes, so this lane does not grade it.

PR watch subscriptions for #217–#247 expire 2026-11-05 22:28 UTC. Renew them before then so the loop still reaches 2026-11-07 00:00 America/Los_Angeles. The 45-minute timer was removed at 00:15 UTC. The replacement is a single 2-hour timer.

Early static notes, not verdicts:

- None of these diffs change `data/held.json` or a CSS file.
- #232 adds a pull-request workflow that runs the hard recheck with read-only contents permission. It does not deploy.
- #239 adds a manual workflow that GETs live shop and intake documents and aborts non-document and `/api/` requests. It does not deploy. This lane will not run that live smoke.
- #218 fails a configured Blob read closed (no seed) and drops another mã's held folder from image URLs. A primary socket error can still read the legacy blob path `sassy-closet-shop/catalog.json`; that path is an explicit tested fallback, not a seed fallback.
- #219 stops intake save from filling a blank sell with a calculated price. A typed zero still stores a zero. This is an intake field change, not an S06 catalog edit.

## 2026-11-05 06:51 UTC — #294 and #225 at 932731a PASS

Requested recheck of these two heads. This lane did not build them.

#294 head is still `21ef1cbaee64a6553fb68e401f3a9733c7c04b4f`. This lane had not started it. Comment `6651745293` says PASS. `npm ci --no-audit --no-fund` in both apps (intake 143 packages, shop 407), then `scripts/hard_recheck.sh --base origin/main --json` with `HARD_RECHECK_PYTHON=/usr/bin/python3`. An earlier 0-second pytest line (`out/recheck/20261105-063933-3751`) used a broken `/tmp/venv08/bin/python` with no pytest module. That interpreter was removed and is not the result. Log `out/recheck/20261105-064148-9065`. pytest 2185 passed, 7 skipped; privacy CLEAN; intake npm 277 / 274 / 0 / 3; shop npm 218 / 215 / 0 / 3; both tsc ok; `held.json` unchanged vs `origin/main`. Required skips: none. `shared/tiered-pricing.ts` is unchanged. Diff is 6 files, +374/−22.

A blocked `taobao_login_needed` (JSON true, int 1, or strings true/yes/y/1 with case and surrounding whitespace, including `YeS` and a newline/tab around `Yes`) drops `unreachable_mas`, `persistent_new_unreachable`, `live_price_changed`, and `new_under_or_loss` from the daily summary and from Boss decisions. Boss `compile_decisions` returns only `[('intake_mismatch', 'Z72')]`. Z72 still appears once in the summary, from the intake-mismatch line. False, 0, `""`, None, and a missing key still count. `origin/main` still lists the unreachable line and Z71 for a true doc; this tree drops them.

A middle blocked day (`" YES "`) is omitted. Z71 stays `(2, 2026-11-01)`. A blocked day that lists a different mã does not break Z71. Newest day blocked with int 1 exits 0, reports `runs_read 1 blocked_runs 1`, and the warning stays Z71 day 1. All days blocked prints the signed-out line and no mãs. Unreadable JSON `{` still counts both days. A missing summary still counts. A real unblocked middle day that is not unreachable still breaks: Z71 becomes `(1, 2026-11-03)`. Boss `streak_start` skips a blocked middle day (Z71 starts 2000-02-01) and a blocked day that omits Z71 does not move the start. A mã only on the blocked day stays unset. Unreachable rows with no flag still ask “Should Z71 go on hold?”

Notes, not a fail: `"false"` and `"no"` still count, and the else-branch also prints the sign-in line because those strings are truthy. Float `1.0`, `"1.0"`, `"yes."`, `"on"`, `"t"`, a NUL, a BOM-prefixed `true`, a zero-width space, a list, and a nested object are outside the documented acceptor and still count. Boss `streak_start` on a UTF-8 BOM summary raises `JSONDecodeError` from `load_json`. The streak file reads `utf-8-sig`, treats that same file as blocked, and ignores its CSV. S06 stays $25. Held stays held.

#225 head is still `932731ac2524c9eb1e2f582335ce1f9da1eb0065`. `0bcfd493c420` stays the prior PASS. Comment `6651746884` says PASS on this SHA. The graded claim is the tip commit against that parent: a held-mã Blob photo whose `/products/` folder is percent-encoded or tab/newline-mangled must not show on a live card. The commit touches only `catalog-image-src.ts`, `product-media.ts`, and two tests (+78/−18). It does not change `data/held.json`, a price file, CSS, layout, or copy. Same `npm ci`, then hard recheck. The broken-venv pytest line for this tree is `out/recheck/20261105-063933-3759` and is not the result. Log `out/recheck/20261105-064148-9074`. pytest 2479 passed, 7 skipped; privacy CLEAN; intake npm 364 / 361 / 0 / 3; shop npm 263 / 260 / 0 / 3; both tsc ok; `held.json` unchanged vs `origin/main`. Required skips: none.

On `0bcfd49`, `srcBelongsToMa` keeps those Blob srcs on live A03. At `932731a` the live card, the gallery reel, and admin `productFromFields` drop them, and held S14 keeps `.../products/%53%31%34/cover.jpg`. Checked: full and partial encoding, lowercase and padded `S014`, encoded `products`, a tab or newline inside `products` or a percent sequence, CR, `HTTPS://` plus a tab, a leading tab or newline, raw and encoded dot segments, backslashes, query, hash, userinfo, `./`, a second `/products/S14/` after A03, a relative path, and a protocol-relative URL. A03 with `/uploads/a03.jpg` and `/products/A04/cover.jpg` keeps only those two. `coverSrc` is `/uploads/a03.jpg`. A04, `/uploads/`, and a URL with no product folder stay. A03’s own folder stays on A03. No probed src both resolved, after one WHATWG decode, to an off-live `/products/` folder and stayed on the live card. Double-encoding, a vertical tab, and U+2028 do not become the ASCII `products/S14` key. A `%2e%2e` that pops `products` requests `.../S14/cover.jpg` with no `products` segment. S06 stays $25. No Blob or `held.json` write.

#249 is this log and is not graded.

## 2026-11-05 08:08 UTC — #225 at 6408c04 PASS

Requested recheck of this head against parent `932731a`. This lane did not build it.

#225 head is still `6408c04b505d6a37a7780ea0e6ce790397be73f2`. `932731ac2524c9eb1e2f582335ce1f9da1eb0065` stays the prior PASS. Comment `6653013783` says PASS on this SHA. The tip commit is the only delta: 7 files, +392/−12 (`scripts/s06_offer_price.py`, `scripts/midnight_qc.py`, `sassy-closet-shop/lib/intake-import.ts`, and their tests). It does not change `data/held.json`, a price file, CSS, layout, or copy. `npm ci --no-audit --no-fund` in both apps (intake 143 packages, shop 407), then `scripts/hard_recheck.sh --base origin/main` with `HARD_RECHECK_PYTHON=/tmp/recheck-python` (`/usr/bin/python3`, pytest 9.2.0 on `PYTHONPATH`; `/tmp/venv08` was absent). Log `out/recheck/20261105-080343-3608`. pytest 2491 passed, 7 skipped; privacy CLEAN; intake npm 364 / 361 / 0 / 3; shop npm 268 / 265 / 0 / 3; both tsc ok; `held.json` unchanged vs `origin/main`. Required skips: none. Working tree clean. Head was still `6408c04` after the run.

Parent reads offer strings `2$5`, `$$25`, `2.5e1`, and `2_5` as 25. This tree’s `s06_offer_dollars` is None for each, and also for `$2$5`, `2$5$`, `2$$5`, `$2.5e1`, `25e0`, `250e-1`, `2__5`, `25_0`, `0,025`, fullwidth `２５`, `2 5`, `true`, and `false`. `$25`, `25.00`, numeric 25, numeric 25.0, `$25.00`, `+$25`, and `$+25` stay 25. A neighbour `$25` does not repair `2$5`. One S06 offer of `25` beside `2$5` is not a single 25.

Parent midnight QC is sell FAIL when catalog hold A03 sits on both homes at null (`home mã set ... does not match Blob`). This tree is sell PASS, data PASS, overall PASS, and `s06Usd` 25, with A03 present in the parsed home at null (plain JSON and RSC). Sell stays PASS for a null tile on the primary host only and for status ` HOLD `. Sell still FAIL: missing live A02, extra priced A99 at 12, extra null A99, priced hold 48 / 0 / 48.00, K06 null or 40, K06 as a catalog hold at null, Q02 null or 10, and Q02 as a catalog hold at null. A null hold does not hide a missing live mã, an extra priced mã, K06, or an A02 99-vs-23 mismatch. The HTML round trip matches.

Parent kind G drops exact EU `34`–`42` and `35.0`–`41.0`. This tree keeps exact `34` through `42` and folds `35.0`–`41.0` onto those chips, including `40.0` and `41.0`. `34.0` and `42.0` drop. Also dropped: `33`, `43`, `35.00`, `35.5`, `40.`, `EU40`, `40码`, `35-36`, and `3.5e1`. Exact `34` and `42` stay when the `.0` forms are dropped beside them. Kind `g` and ` G ` keep `38`. Kind `A`, `O`, and `Giày` do not. The draft stays `hold` with `priceInput` empty for `sell_usd` `26`, `26.00`, `$26`, `0`, `2$6`, `2.5e1`, and empty, and `parseDraftPrice` is null.

Notes, not a fail: unquoted JSON `2.5e1`, `2.5E1`, `25e0`, and `250e-1` are float 25 after `json.loads`, same as the parent. Two home hits for one mã, null and 48, still collapse to null in `parse_home_prices`; one priced hit stays 48 and fails sell. A null hold with no hub row is sell PASS and data FAIL. S06 stays $25. No Blob, KV, Meta, or price write. No push to the #225 branch.

#249 is this log and is not graded.

## 2026-11-05 08:36 UTC — #294 at e0c34ba PASS

Requested recheck of this head against parent `21ef1cb`. This lane did not build it.

#294 head is still `e0c34bad44c1fd9ae891461c416f5c3cf02022e1`. `21ef1cbaee64a6553fb68e401f3a9733c7c04b4f` stays the prior PASS. Comment `6653508698` says PASS on this SHA. The tip commit is the delta under test: 6 files, +123/−17 on top of the parent, and the full diff vs `origin/main` is 6 files, +483/−25 (`scripts/cost_recheck_block.py`, `scripts/daily_summary_draft.py`, `scripts/boss_decisions.py`, `scripts/taobao_unreachable_streak.py`, and their tests). It does not change `data/held.json`, a price file, CSS, layout, or copy. `npm ci --no-audit --no-fund` in both apps (intake 143 packages, shop 407), then `scripts/hard_recheck.sh --base origin/main` with `HARD_RECHECK_PYTHON=/usr/bin/python3` (pytest 9.2.0). The worktree was detached at this SHA, so the summary's branch field is blank. Log `out/recheck/20261105-082524-3033`. pytest 2223 passed, 7 skipped; privacy CLEAN; intake npm 277 / 274 / 0 / 3; shop npm 218 / 215 / 0 / 3; both tsc ok; `held.json` unchanged vs `origin/main`. Required skips: none. Working tree clean. Head was still `e0c34ba` after the run.

One `login_blocked` is `scripts/cost_recheck_block.py` line 13. An AST walk finds that definition and no other. The daily summary, Boss decisions, and the streak watcher hold the same function object. A wrapper counted calls: daily summary 2 (blocked header and `evidence`), Boss `compile_decisions` 1, Boss `streak_start` 1, streak watcher 1. A helper forced true skips every Boss day and blocks all three watcher dates. A helper forced false keeps the middle day in both readers.

Parent `" false "` and `"\nNo\t"` are not blocked by the helper, and the summary still prints the sign-in line because the else branch treats the string as truthy. Parent JSON `1e0` and `1.0` are float 1.0, the helper returns false, and the summary prints the sign-in line and the hold question. Parent float `1.5` and the string `"1.0"` do the same. Parent float `0.0` does not print the sign-in line. Parent Boss `streak_start` and `load_json` on a UTF-8 BOM summary raise `JSONDecodeError: Unexpected UTF-8 BOM (decode using utf-8-sig)`.

This tree's strings `false` and `no`, 130 distinct values of case and surrounding whitespace (space, tab, CR, LF, CRLF, VT, FF, NBSP, em space, U+2028, U+2029, ideographic space), stay open: no sign-in line, no blocked line, the hold question stays, and Boss keeps `gone_hold` Z71 and reclassifies Z72. JSON `1`, `1.0`, and `1e0` are blocked. `1` is int 1. `1.0` and `1e0` are float 1.0. The summary prints the blocked line and the sign-in line once, drops Z71, and Boss returns only `[('intake_mismatch', 'Z72')]`. Those tokens as file bytes on a middle day that lists Z99 and omits Z71: Boss Z71 stays `2000-06-01`, Z99 does not start, the watcher blocks that day, and Z71 is `(2, 2000-06-01)`. JSON `0.0`, `1.5`, and the string `"1.0"` stay open. Z71 breaks to `2000-06-03`, the watcher keeps the middle day, and Z99 starts at `2000-06-02`. A UTF-8 BOM summary loads in Boss `streak_start`. BOM plus `1e0`, BOM plus CRLF plus `1.0`, and BOM plus `1` skip the middle day. BOM plus a leading newline plus `" false "` loads that string and breaks the streak at `2000-09-03`.

Notes, not a fail: JSON `1E0`, `1e+0`, and `1.00` parse to float 1.0 and are blocked. `0e0` and `-0.0` are not. The string `"1e0"` is not blocked. A summary whose text is `{` still counts in the watcher and still raises `JSONDecodeError` from Boss `streak_start`. S06 stays $25. Held stays held. No Blob, KV, Meta, or price write. No push to the #294 branch.

#249 is this log and is not graded.

## 2026-11-05 09:20 UTC — #225 at fe1993d PASS

Requested recheck of this head against parent `6408c04`. This lane did not build it.

Comment `6654327182` says PASS on this SHA. The comment text is the evidence below.

INDEPENDENT RECHECK PASS at `fe1993d1945e38ea44a0cecb3e79885d62df4015`.

This lane did not build this commit. The head is still `fe1993d`. The parent is `6408c04`. The tip is 12 files, +322/−27. It does not change `data/held.json`, a price file, CSS, layout, or copy.

`npm ci --no-audit --no-fund` in both apps (intake 143 packages, shop 407), then `scripts/hard_recheck.sh --base origin/main` with `HARD_RECHECK_PYTHON=/usr/bin/python3` (pytest 9.2.0, openpyxl 3.1.5 on `PYTHONPATH`). The worktree was detached at this SHA, so the summary branch field is blank. Log `out/recheck/20261105-091419-5396`. pytest 2499 passed, 7 skipped; privacy CLEAN; intake npm 365 / 362 / 0 / 3; shop npm 269 / 266 / 0 / 3; both tsc ok; `held.json` unchanged vs `origin/main` (sha256 `484dbec93976e07ce34a2acc693287b6909187834032241fe6dd95d88a83d9da`). Required skips: none. Working tree clean. The head was still `fe1993d` after the run.

An earlier invocation in this checkout stopped at pytest rc 3 in 2s because openpyxl was not installed (`freshness_check` raised `SystemExit` during collection). That log is `out/recheck/20261105-091007-2852` and is not the result.

Too-cheap. The parent `load_live` raises `TypeError: float() argument must be a string or a real number, not 'NoneType'` on a hold row with `priceUsd` null and drops every later row. This tree keeps going. K06 hold null, A01 22, S006 40, then S06 25 loads `{A01: 22, S06: 40}`. `evaluate` is lock-drift at $40 and the outcome is `LOCK_DRIFT`. S06 at 25 followed by S6 at 18 loads 18 and drifts. `true`, `false`, `"true"`, `"2.5e1"`, `"2.5E1"`, `"25e0"`, `"250e-1"`, `"2$5"`, `"0,025"`, `"12,50"`, `"$$25"`, null, and a non-row are absent and do not abort the file. `"$28"`, `"1,200"`, `"$1,200.50"`, `"25$"`, and `"  $25  "` stay 28, 1200, 1200.5, 25, and 25. A blank status and `"  Available "` stay live. `" HOLD "`, sold, hold, and a non-string status stay out. A prices map `{S06: 25, S006: 40, A01: true, K03: "$30", K06: null}` loads `{S06: 40, K03: 30}`. S06B at 10, S06Đ at 11, fullwidth `S06Ｂ` at 12, and A100 at 13 stay on their own keys beside S06 at 25. A lone S06 price of `true`, `"2.5e1"`, `"0,025"`, or null is `LOCK_DRIFT`. `main()` on K06 hold null, S06 `"$25.00"`, a sold `"2.5e1"`, and an available `true` returns 0 with outcome `QUIET_OK` and locked 1.

Boss digest and Muse pack. `S006`, `S6`, `S 06`, `S 006`, `S 6`, and `Mã S006` each open `price_approval` S06, and the three spellings together open it once. `S06B`, `S06Đ`, fullwidth `S06Ｂ`, `S06` plus a zero-width space plus B, `S06` plus a soft hyphen plus Đ, `S06` plus a left-to-right mark plus B, `S006B`, `A100`, `A1000`, and `A10000` stay out, and `A100` is not read as A10. Lowercase `s006`, `s6`, `s 06`, and `v1` stay out. `not decided, Boss price approved for S006` and `Boss price approved for S6` stay closed. `Boss price not yet approved for S006`, `Boss price not approved for S6`, `Boss price NOT approved for S 06`, and `S006 isn't approved` stay open as S06. Intake mismatch `S006` opens S06. Intake mismatch `S06B` and `A100` stay out. Blob text `S 06` with public and Boss delete is `blob_photo_delete` S06 when the public-held set is S06. `S06Đ` on that same note stays out. The morning pack `price_approval` list for that fixture is S06 and S09. The rendered section contains S06 and S09 and omits S06B, S08, and A100.

Popular rank. `canonicalMaSpelling` and `norm_ma` map `S006`, `S6`, and `s006` to S06, and `A001` to A01. `A100`, `S06B`, and `S06Đ` stay as written. `S 06` stays `S 06`. `popularScore("S006")`, `popularScore("S6")`, and `popularScore("s006")` equal `popularScore("S06")` (0.022727). `popularScore` of `S06B`, `S06Đ`, `S06Ｂ`, `A100`, and `S 06` is 0. `sortByPopular` puts `A005` and `a5` on A05's slot ahead of S05, and `S006` with `S6` on S06's slot. `S06B`, `A100`, and `Z99` stay unranked, in catalog order. `fbRankOf("A001")` and `fbRankOf("a1")` are 1. `fbRankOf("S003")` and `fbRankOf("S3")` are 3, the same as S03. `fbRankOf("S03B")`, `fbRankOf("S03Đ")`, and `fbRankOf("A100")` are absent. S06 itself is absent from the 90-day FB table, so `fbRankOf("S006")` is absent with it. The real `popular-order.json` keys and `fb-ma-rank.json` rows do not collide under the canonical key. `summary_live` of `S006 S6 X01` is `[S06, X01]`. `S006` alone is S06, not S00. `summary_live` of `S06B S06Đ A100 S06Ｂ S006 S6` is `[S06]`. `home_order` of `/m/a001`, `/m/S006`, `/m/S6`, and `/m/S06B` is `[A01, S06]`. `catalog_live` of available `S006` and `s6` is `[S06]`. Available `S06B`, `A100`, and `S06Đ` stay out. `build` of ranked `S006`, `S6`, `S06B`, `A100` against live S06 returns order `[S06]`.

Intake sync. `buildIntakeDatasetSyncPayload` splits `35;36 M/L S|M` into `["35","36","M","L","S","M"]`. `35/36`, `S|M`, `S, M`, and `S M` still split. `35-36` and fullwidth `35；36` stay one token. `;;;` omits `sizes`. The stored size string is unchanged. Those results match `kinds.ts` `sizeTokens`. The class is the same one `autolist.norm_sizes` and `intake_gaps` use: `[\s,;/|]+`.

Notes, not a fail. Unquoted JSON `2.5e1` and `25e0` are the number 25 after `json.loads`. The string forms are rejected. `"025"` and `"0025"` still become 25, the same number `float()` produced. Two off-lock S06 spellings keep the first dollar: S6 at 18 then S006 at 40 stays 18, and the outcome is still lock-drift. A later $25 does not replace that first off-lock. A hold S006 at $40 does not override an available S06 at $25. The digest flattens whitespace with `" ".join(text.split())` before the token regex, so a tab, NBSP, or a doubled space between S and 06 also opens S06. Popular `norm_ma` leaves an internal space in place, so summary text `S 06` is dropped. A too-cheap row whose mã is `S 06` at $99 stays a separate key beside S06 at $25. A trailing zero-width space, soft hyphen, or BOM with no stuck letter still reads as S06. S06 stays $25: `autolist.S06_LOCK_USD` is 25, sell-contract and admin-ops reject `priceUsd !== 25`, `data/price-drift/observed-public-sell.json` `liveUsd.S06` is 25, and `sassy-closet-shop/data/products.json` has no S06 row. `data/held.json` matches `origin/main`. No Blob, KV, Meta, or price write. No push to the #225 branch.

#249 is this log and is not graded.

## 2026-11-05 10:11 UTC — #294 at 208bd81 PASS

Requested recheck of this head against parent `e0c34ba`. This lane did not build it.

#294 head is still `208bd81d9e16bbfc7c8d9cda900a3099d87be174`. `e0c34bad44c1fd9ae891461c416f5c3cf02022e1` stays the prior PASS. Comment `6655337006` says PASS on this SHA. The comment text is the evidence below.

INDEPENDENT RECHECK PASS at `208bd81d9e16bbfc7c8d9cda900a3099d87be174`.

This lane did not build this commit. The head is still `208bd81`. The parent is `e0c34ba`. The tip is 5 files, +283/−30. The full diff vs `origin/main` is 6 files, +737/−26 (`scripts/cost_recheck_block.py`, `scripts/daily_summary_draft.py`, `scripts/boss_decisions.py`, `scripts/taobao_unreachable_streak.py`, and their tests). It does not change `data/held.json`, a price file, CSS, layout, or copy.

`npm ci --no-audit --no-fund` in both apps (intake 143 packages, shop 407), then `scripts/hard_recheck.sh --base origin/main` with `HARD_RECHECK_PYTHON=/tmp/py-recheck`. That wrapper execs `/usr/bin/python3` with pytest 9.2.0 and openpyxl 3.1.5 on `PYTHONPATH`. The system interpreter had no pytest module, and `python3-venv` is not installed. The worktree was detached at this SHA, so the summary branch field is blank. Log `out/recheck/20261105-100558-2866`. pytest 2247 passed, 7 skipped; privacy CLEAN; intake npm 277 / 274 / 0 / 3; shop npm 218 / 215 / 0 / 3; both tsc ok; `held.json` unchanged vs `origin/main` (sha256 `484dbec93976e07ce34a2acc693287b6909187834032241fe6dd95d88a83d9da`). Required skips: none. No hard-recheck step is SKIP. Working tree clean. The head was still `208bd81` after the run.

`boss_decisions.streak_start` and `taobao_unreachable_streak.partition_runs` call the same `cost_recheck_block.load_summary` object. `ENCODING` is `utf-8-sig`. `read_json` uses it. One `login_blocked` definition lives in `scripts/cost_recheck_block.py`. A wrapper that returns `("bad", None)` and a `read_json` that raises were installed together: both readers called `load_summary` and neither called `read_json`. Restored, `load_summary` on a dict calls `login_blocked`.

A summary whose text is `{` is `("bad", None)`. `streak_start` returns the earlier real day and does not raise. The watcher puts that date in `bad_dates`, leaves it out of `runs`, and leaves Z72 out of the streak. Exit is 0. The header is `latest_run 2000-08-03 runs_read 2 blocked_runs 0 unreadable_runs 1`. The same result holds for an empty file, whitespace, ` { `, a truncated object, NUL, the bytes `garbage`, every byte from 0 through 255, a UTF-16 object, a BOM-only file, a BOM plus whitespace, a BOM plus `{`, a JSON array that lists Z71 and Z72, `[]`, a BOM plus an array, `null`, whitespace around `null`, a BOM plus `null`, and whole-document `true`, `false`, `1`, and `"true"`. Extra data after a blocked object is bad, so the day is unreadable rather than signed-out. A lone `{` file makes `streak_start` return None. Two `{` days print `OK unreadable cost-recheck summary on 2 run(s); unreachable flags not used` and exit 0.

Parent `e0c34ba` on day 1 Z71, day 2 `{` with CSV Z71 and Z72, day 3 Z71: `streak_start` raises `JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)`. The watcher runs include day 2 with `{Z71, Z72}`. This tree on that fixture returns `2000-01-01` from `streak_start`. The watcher runs are `[('2000-01-01', {'Z71'})]`, blocked is empty, and bad is `['2000-01-02']`.

A missing summary stays `("missing", None)`. Three flag CSVs and no summary files, `2000-09-30`, `2000-10-01`, and `2000-10-02`, all stay in the runs, and Z71 is `(3, 2000-09-30)`. One missing day prints `latest_run 2026-11-04 runs_read 1 blocked_runs 0` and warns Z71 day 1. An empty file in the middle of that month-crossing run is bad. The runs drop that day. Z71 becomes `(2, 2000-09-30)`.

Strings `false` and `no`, 1183 values of case and surrounding whitespace (space, tab, CR, LF, CRLF, VT, FF, NBSP, em space, U+2028, U+2029, ideographic space), stay open. For `false`, `no`, `" false "`, `"\nNo\t"`, JSON false, `0`, `0.0`, `"1.0"`, `"1e0"`, `1.5`, a missing value, and `""`, the daily summary prints the unreachable line and `- Should Z71 go on hold?`, and it does not print the blocked line or the sign-in line. Boss keeps `gone_hold` Z71 and reclassifies Z72 to `intake_unreachable`.

JSON `1`, `1.0`, `1e0`, `1E0`, `1e+0`, and `1.00` are blocked. `1` is int 1. `1.0` and `1e0` are float 1.0. The summary prints the blocked line and the sign-in line once, and the hold question is absent. Boss returns only `[('intake_mismatch', 'Z72')]`. The same holds for JSON true, `" yes "`, `"Y"`, `"1"`, and `"\nYes\t"`. The string `"1.0"` stays open.

Those tokens as file bytes on `2000-06-02`, listing Z99 and omitting Z71, between Z71 days: int `1`, float `1.0`, `1e0`, a UTF-8 BOM plus `1e0`, a BOM plus CRLF plus `1.0`, and a BOM plus `1` are blocked. Boss Z71 stays `2000-06-01`. Z99 as of `2000-06-03` is unset. The watcher blocks that day, and Z71 is `(2, 2000-06-01)`. `" false "`, `"\nNo\t"`, `"1.0"`, `0.0`, `1.5`, and a BOM plus a leading newline plus `" false "` stay open. Boss Z71 breaks to `2000-06-03`. `streak_start` as of `2000-06-02` for Z99 is `2000-06-02`. As of `2000-06-03`, Z99 is unset because that day does not list Z99. With the flag CSV listing Z99 and omitting Z71, the watcher keeps the day, Z71 is `(1, 2000-06-03)`, and that day's set is `{Z99}`. A UTF-8 BOM plus `{"unreachable_mas": ["Z71"]}` loads as ok, and the streak continues from `2000-06-01`.

A readable middle summary that lists Z99 and omits Z71 still breaks Z71 at `2000-06-03`. A directory standing in for the summary file is bad, and `streak_start` does not raise. A symlink to `{` is bad, and the watcher leaves the day out.

Notes, not a fail. `daily_summary_draft.load_json` on `{` still raises `JSONDecodeError`. `boss_decisions.main` still loads the current summary through that path, so a current `{` file still raises before `streak_start`. A dangling symlink is `FileNotFoundError`, so `load_summary` reports missing and the watcher still reads that day's CSV. A second UTF-8 BOM in front of a valid object is bad. A file whose whole text is JSON `1` is bad; the login flag `1` blocks only inside a summary object. Ten thousand nested arrays raise `RecursionError` from `load_summary`. S06 stays $25: `autolist.S06_LOCK_USD` is 25, the same as `origin/main`, and `shared/live-price-snapshot.json` `liveUsd` for S06 is 25, the same as `origin/main`. `data/held.json` matches `origin/main`. No Blob, KV, Meta, or price write. No push to the #294 branch.

#249 is this log and is not graded.

## 2026-11-05 11:12 UTC — #225 at 1744f2b PASS

Requested recheck of this head against parent `fe1993d`. This lane did not build it.

#225 head is still `1744f2b7aee9539d0a86a2f3bdd592b78d658fe4`. `fe1993d1945e38ea44a0cecb3e79885d62df4015` stays the prior PASS. Comment `6656522043` says PASS on this SHA. The comment text is the evidence below.

INDEPENDENT RECHECK PASS at `1744f2b7aee9539d0a86a2f3bdd592b78d658fe4`.

This lane did not build this commit. The head is still `1744f2b`. The parent is `fe1993d`. The tip is 2 files, +246/−167 (`scripts/host_health_check.py`, `scripts/tests/test_host_health_check.py`). It does not change `data/held.json`, a price file, CSS, layout, or copy.

`npm ci --no-audit --no-fund` in both apps (intake 143 packages, shop 407), then `scripts/hard_recheck.sh --base origin/main` with `HARD_RECHECK_PYTHON=/tmp/py-recheck` (that wrapper execs `/usr/bin/python3` with pytest 9.2.0 and openpyxl 3.1.5 on `PYTHONPATH`). The worktree was detached at this SHA, so the summary branch field is blank. Log `out/recheck/20261105-110348-3403`. pytest 2503 passed, 7 skipped; privacy CLEAN; intake npm 365 / 362 / 0 / 3; shop npm 269 / 266 / 0 / 3; both tsc ok; `held.json` unchanged vs `origin/main` (sha256 `484dbec93976e07ce34a2acc693287b6909187834032241fe6dd95d88a83d9da`). Required skips: none. Every hard-recheck step is PASS, except the informational tip line. Working tree clean. The head was still `1744f2b` after the run.

`host_health_check.s06_offer_dollars` is `s06_offer_price.s06_offer_dollars`. The host file calls that function. Putting a constant 25 in its place makes a spliced page pass, so the gate follows that return value. `S06_LOCK` is 25. The hosts are `sassycloset.vercel.app` and `sassy-closet-shop.vercel.app`.

`$25`, `25.00`, and `25.000` each return 25. `s06_shows_25` is true and `s06_offer_usd` is `25.00`, including when a neighbour product is `2$5`, an `S06B` product is `$25`, and the HTML contains both. Those three strings together with numeric 25 and 25.0 still return 25. `run()` on `$25`, `25.00`, or `25.000` is PASS on both hosts with offer `25.00`.

Spliced `2$5` returns None when a neighbour says `$25`. Checked: a second product, an `@graph` neighbour, an `itemListElement` neighbour, HTML text, the description and the name, `lowPrice` 25, `priceSpecification` `$25`, a JSON `\u0024` escape, and an `@type` list. One S06 offer list that contains both `2$5` and `$25` is None. `S006`, `S6`, and `s06` at `$25` leave an S06 `2$5` as None, and an S06 `$25` leaves an `S006` `2$5` as None. A product whose URL is `/m/S006` and whose price is `2$5` stays None beside a neighbour `$25`. `2 $ 5`, `$2$5`, `$$25`, `2$$5`, `2$5$`, `2.5e1`, `25e0`, `2_5`, and `0,025` stay None beside a neighbour `$25`. `run()` on `2$5` plus a neighbour `$25` is FAIL on both hosts, `shows_25` false, and `offer_usd` null.

Parent `fe1993d` also rejects `2$5`, and it reads `25.00` and `25.000` as 25. Parent `s06_offer_usd` of `$25` is None. This tree reads `$25` as 25. Parent checks one held mã. This tree checks every `heldIncomplete` mã.

`data/held.json` `heldIncomplete` is these 21 codes: `S14 A24 A25 S15 A26 K02 K03 K04 K05 V04 K06 V05 S16 S17 S18 S19 A27 A28 A29 H02 G01`. `load_held_policy().held` equals that list. `held_codes()` is that list. `S06` is absent. `neverList` is empty and a probe policy with `neverList` `Z99` does not request `Z99`. Aliases are the lowercase letter plus a three-digit pad: `S19->s019`, `G01->g001`, `K02->k002`, `K06->k006`, `S14->s014`, `A24->a024`, `A29->a029`, `H02->h002`, `V05->v005`, and the same rule for the rest. A mocked `run()` requests 88 URLs (home, `/m/S06`, each mã, and each alias, on both hosts) and PASSes when those PDPs are 404 and the offer is `$25`. A live `/m/s019` on the primary host fails with `held S19 alias /m/s019 -> 200 (want 404)` and nothing else. A live `K06` on the shop host fails with that one line, and the other URLs are still requested.

Live host health was a read-only GET. Exit 0, overall PASS. Both hosts: DNS ok, TLS 1.3, GET `/` 200, held probe `s019` 404, S06 `$25` true. The script printed `Held mãs checked: 21 on each host, all 404.` Independent curl: every canonical `/m/{mã}` is 404 with no redirect (42/42). Every alias first response is 308. `curl -I` on `/m/s019` is `308` with `location: /m/S19`. `curl -L` follows all 42 aliases to `/m/{CANON}` and the final status is 404. urllib on `/m/s019` prints `308 -> /m/S19` and then `HTTPError 404`. `/m/g001` does the same to `/m/G01`. A local server showed that a 308 whose target is 200 is recorded as 200, which fails the check. `/m/S06` is 200 on both hosts. Each page has one Product JSON-LD, sku `S06`, price `25.00`. `s06_offer_dollars` is 25. Both homes are 200. `held.json` sha256 after those GETs is still `484dbec93976e07ce34a2acc693287b6909187834032241fe6dd95d88a83d9da`. No Blob, KV, Meta, or price write.

Notes, not a fail. An S06 `2$5` stored only under `mainEntity` is outside the walker, so a separate walked S06 `$25` still returns 25. A walked S06 `2$5` stays None when the neighbour `$25` sits under `mainEntity`. The live page is one top-level Product. A single-quoted `ld+json` script, and a script whose quotes are HTML-escaped, return None. A duplicate JSON `price` key keeps the last value: `2$5` then `$25` parses as 25, and `$25` then `2$5` is None. `025.000` is 25. `25.0001` is None. `$25.000` and `25.0000` are 25. S06 stays $25. The live offer is `25.00`. `shared/live-price-snapshot.json` `liveUsd` for S06 is 25. `sassy-closet-shop/data/products.json` has no S06 row. No push to the #225 branch.

#249 is this log and is not graded.

## 2026-11-05 11:36 UTC — #225 at 90360ef PASS

Requested recheck of this head against parent `1744f2b`. This lane did not build it. Draft #294 at `208bd81` was compared and was not modified. No code on either pull request was changed. The local merge was aborted and was not pushed.

#225 head is still `90360ef70cd5a5eae2ce5bdbcb3f8fa2c3167cc9`. `1744f2b7aee9539d0a86a2f3bdd592b78d658fe4` stays the prior PASS and is the parent. Comment `6657013975` says PASS on this SHA. The comment text is the evidence below.

INDEPENDENT RECHECK PASS at `90360ef70cd5a5eae2ce5bdbcb3f8fa2c3167cc9`.

This lane did not build this commit. The head is still `90360ef`. The parent is `1744f2b`. The tip is 8 files, +518/−43. It does not change `data/held.json`, a price file, CSS, layout, or copy. `1744f2b7aee9539d0a86a2f3bdd592b78d658fe4` is the parent and is still an ancestor. `scripts/host_health_check.py`, `scripts/s06_offer_price.py`, and `scripts/tests/test_host_health_check.py` match that commit byte for byte.

`npm ci --no-audit --no-fund` in both apps (intake added 143 packages, shop added 407), then `scripts/hard_recheck.sh --base origin/main` with `HARD_RECHECK_PYTHON=/tmp/py-recheck` (that wrapper execs `/usr/bin/python3` with pytest 9.2.0 and openpyxl 3.1.5 on `PYTHONPATH`). The worktree was detached at this SHA, so the summary branch field is blank. Log `out/recheck/20261105-113038-3905`. pytest 2539 passed, 7 skipped; privacy CLEAN; intake npm 365 / 362 / 0 / 3; shop npm 269 / 266 / 0 / 3; both tsc ok; `held.json` unchanged vs `origin/main` (sha256 `484dbec93976e07ce34a2acc693287b6909187834032241fe6dd95d88a83d9da`). Required skips: none. No hard-recheck step is SKIP. The tip line is INFO. Working tree clean. The head was still `90360ef` after the run, and the remote branch was still that SHA.

Claim checked against parent `1744f2b` with the same fixtures. A signed-out summary lists unreachable Z71, persistent-new Z71, live-price Z73, and under-price Z74, plus an intake-mismatch Z72 from the digest.

Parent JSON `true` still prints Z71, `live price change`, and `go on hold`, and Boss returns `[('gone_hold', 'Z71'), ('intake_mismatch', 'Z72')]`. `streak_start` is `2026-11-03`. The watcher run is `[('2026-11-03', ['Z71'])]`. This tree prints the signed-out line and the sign-in line, and those cost rows are absent. Boss returns `[('intake_mismatch', 'Z72')]`. `streak_start` is None. The watcher runs are empty. The same holds for JSON `1` (int), JSON `1.0` (float), JSON `1e0` (float 1.0), and the strings `true`, `yes`, `y`, and `1`.

Strings `false` and `no`, JSON `0`, and a missing key stay evidence. The brief prints Z71, `live price change`, and `go on hold`. Boss keeps `gone_hold` Z71 and `intake_mismatch` Z72. `streak_start` is `2026-11-03`. The watcher run is `[('2026-11-03', ['Z71'])]` and does not include the price-flag Z73. Parent string `false` still prints the sign-in line because that string is truthy, and it still keeps the rows. This tree keeps the rows and leaves the sign-in line out. JSON `false`, `0.0`, `" FALSE "`, `"\nNo\t"`, and the string `"1.0"` stay open on this tree. `" TRUE "`, `" YES "`, `"Y"`, and `"\nYes\t"` are blocked.

A blocked middle day, `2026-11-02`, between Z71 days stays skipped. Boss Z71 stays `2026-11-01`. Z99, listed only that day, stays unset. Watcher runs are `2026-11-01` and `2026-11-03`, the blocked date is `2026-11-02`, and Z99 is absent. Parent still reads that day's CSV as `['Z71', 'Z99']`. A blocked middle day that omits Z71 and lists Z99: parent Boss Z71 breaks to `2026-11-03`. This tree stays `2026-11-01`.

Bad JSON `{` on that middle day breaks Boss streak to `2026-11-03` and does not raise. The watcher still reads the CSV, so `2026-11-02` stays in the runs with Z99. A missing summary file breaks Boss the same way, to `2026-11-03`. The watcher still reads that day's CSV. An empty file and a whole-file `true` also break Boss and stay in the watcher runs. One `login_blocked` definition lives at `scripts/cost_recheck_block.py:10`. The morning brief, Boss decisions, and the streak watcher hold that same function object. This tree has no `load_summary`.

`1744f2b` host parser: `host_health_check.s06_offer_dollars` is `s06_offer_price.s06_offer_dollars`. `S06_LOCK` is 25. `$25` and `25.00` return 25. `s06_shows_25` is true. Spliced `2$5` beside a neighbour `$25` returns None.

Conflict with draft #294 at `208bd81d9e16bbfc7c8d9cda900a3099d87be174`. The blocked-value set matches. Twenty-two probed values, zero disagreements. Both block JSON true, int 1, float 1.0, JSON `1e0`, and strings true/yes/y/1 after strip and lower. Both leave false, strings false/no, 0, 0.0, string `"1.0"`, and a missing key open.

Malformed files disagree. On `{`, an empty file, and a whole-file `true`, #225 Boss `streak_start` returns `2026-11-03` and the watcher keeps Z99 from the CSV. #294 Boss `streak_start` returns `2026-11-01` and does not raise. #294 `load_summary` returns `("bad", None)` for `{`, empty, `[]`, and `null`, and `("missing", None)` when the path is absent. The watcher puts `2026-11-02` in `bad_dates` and leaves Z99 out of the runs. A missing summary beside a flag CSV stays in the watcher runs on both drafts. A missing Boss summary file breaks #225 (`2026-11-03`) and #294 continues to `2026-11-01`, because #294 only walks files that exist.

Helper duplication: both add `scripts/cost_recheck_block.py` with `login_blocked` and `evidence`. #294 also defines `read_json` and `load_summary`, and Boss `streak_start` and the watcher call `load_summary`. #225 opens the JSON in `_summary_lists` and `_summary_blocked` and only calls `login_blocked`.

Local test merge, not pushed. Detached worktree at `origin/main` (`04bfc35`), fast-forward to `90360ef`, then `git merge --no-commit --no-ff 208bd81`. Exit 1. Unmerged files: `scripts/boss_decisions.py` (3 hunks), `scripts/cost_recheck_block.py` (add/add, 4 hunks), `scripts/daily_summary_draft.py` (2 hunks), `scripts/taobao_unreachable_streak.py` (4 hunks), `scripts/tests/test_cost_recheck_block.py` (add/add), `scripts/tests/test_taobao_unreachable_streak.py` (2 hunks). `git merge-tree --write-tree` of the two tips also exited 1 with those six files. `daily_summary_draft.load_json` auto-merged to `cost_recheck_block.read_json` with no conflict marker. #225's helper has no `read_json`, so keeping that helper with the auto-merged loader would raise `AttributeError` on the morning brief. `pytest --collect-only` on the four overlapping test modules: rc 2, 4 collection errors, no tests collected. `boss_decisions.py` line 188 and `daily_summary_draft.py` line 524 raise `SyntaxError` on the conflict marker. `git merge --abort`, then the worktree was returned to `origin/main`. No merge commit.

Recommendation: #294 should win the shared reader and the malformed-file rule. Keep one `cost_recheck_block.py` with `login_blocked`, `evidence`, `read_json`, and `load_summary` (`utf-8-sig`). The blocked-value checks can stay as they are on either side. A summary that exists but cannot be read is skipped by Boss `streak_start` and by the watcher: it does not count and it does not break the run. #225's Boss streak ends on `{` while #225's watcher still counts that day's CSV, so those two readers disagree. A missing summary beside a flag CSV stays watcher evidence, which both drafts already do. A missing Boss summary file should still end #225's calendar run. A present unreadable file should not use that break.

Notes, not a fail. `daily_summary_draft.load_json` on a UTF-8 BOM summary raises `JSONDecodeError: Unexpected UTF-8 BOM (decode using utf-8-sig)`. Boss `streak_start` and the watcher read `utf-8-sig`, so a BOM plus JSON true is skipped and is not a streak day. #294's `load_json` loads that file. The open brief reports price changes as `1 live price change(s)` and does not print the Z73 code. The blocked brief drops that phrase. Boss decisions have no price-change line from the cost file; Z73 and Z74 are absent from the rendered text. `workflow_status._cost_parsed` is outside the four claimed surfaces. Boolean true is verdict `LOGIN` and the four counts stay 1. Int 1 and string `true` are verdict `PARSED`, the counts stay 1, and `taobao_login_needed` is false. S06 stays $25: `autolist.S06_LOCK_USD` is 25, `shared/live-price-snapshot.json` `liveUsd` for S06 is 25 and the file matches `origin/main`, and `sassy-closet-shop/data/products.json` has no S06 row. `data/held.json` matches `origin/main`. No Blob, KV, Meta, or price write. No push to the #225 branch.

#249 is this log and is not graded.

## 2026-11-05 12:30 UTC — #225 at 4e446f9 PASS

Requested recheck of this head against parent `90360ef` and against draft #294 at `208bd81`. This lane did not build either commit. No code on either pull request was changed. Both local merges were aborted and were not pushed.

#225 head is still `4e446f9c5ef19210c21ec231b69d8058f16ebfcc`. `90360ef70cd5a5eae2ce5bdbcb3f8fa2c3167cc9` stays the prior PASS and is the parent. Comment `6658019815` says PASS on this SHA. The comment text is the evidence below.

INDEPENDENT RECHECK PASS at `4e446f9c5ef19210c21ec231b69d8058f16ebfcc`.

This lane did not build this commit. The head is still `4e446f9`. The parent is `90360ef`. The tip is 8 files, +1158/−474. It does not change `data/held.json`, a price file, CSS, layout, or copy. `90360ef70cd5a5eae2ce5bdbcb3f8fa2c3167cc9` is the parent and is still an ancestor.

`npm ci --no-audit --no-fund` in both apps (intake added 143 packages, shop added 407), then `scripts/hard_recheck.sh --base origin/main` with `HARD_RECHECK_PYTHON=/usr/bin/python3` (pytest 9.2.0, openpyxl 3.1.5). The worktree was detached at this SHA, so the summary branch field is blank. Log `out/recheck/20261105-122226-3187`. pytest 2671 passed, 7 skipped; privacy CLEAN; intake npm 365 / 362 / 0 / 3; shop npm 269 / 266 / 0 / 3; both tsc ok; `held.json` unchanged vs `origin/main` (sha256 `484dbec93976e07ce34a2acc693287b6909187834032241fe6dd95d88a83d9da`). Required skips: none. No hard-recheck step is SKIP. The tip line is INFO. Working tree clean. The head was still `4e446f9` after the run, and the remote branch was still that SHA. The seven pytest skips are the six empty `neverList` gate cases and `test_workflow_is_read_only_and_scheduled`.

Helper match. `scripts/cost_recheck_block.py` and `scripts/tests/test_cost_recheck_block.py` are byte-identical to #294 at `208bd81d9e16bbfc7c8d9cda900a3099d87be174`. `git diff --exit-code 208bd81 --` those two paths is empty. Blob ids `d34b3d445df4c626aa78799dfaf8b571f8122259` and `8c2efad012ee3739d943aa74413ab4ceb991db39`. File sha256 `f305eeceb38bd349a4781545bc7169fcd5b5bb56264e93f59e6842c1a448947b` and `24ff4ee2b92da880b60dcd0885ff9cd849b799799c02a1dfe0c2b0f0fedaa093`. `scripts/tests/test_taobao_unreachable_streak.py` is also byte-identical. One `login_blocked` definition lives in the helper. Boss, the morning brief, and the watcher hold that module's `load_summary`, `login_blocked`, `evidence`, and `read_json`. `ENCODING` is `utf-8-sig`. `boss_decisions.streak_start` is `_calendar_streak_start`.

A stub `load_summary` that returns `("bad", None)` makes Boss `streak_start` return None and puts the watcher day in `bad_dates`. Both readers called the stub.

Malformed present summaries. On day 1 Z71, day 2 a bad file whose CSV lists Z71 and Z99, day 3 Z71: Boss `streak_start` as of day 3 is `2026-11-01` and Z99 is unset. The watcher runs are day 1 and day 3, `bad_dates` is day 2, and Z99 is absent. `build_report` warns `Z71 day 2 (since 2026-11-01)` and notes the unreadable day. Checked payloads: `{`, empty, whitespace, truncated object, NUL, `garbage`, every byte 0–255, UTF-16, BOM-only, BOM plus whitespace, BOM plus `{`, a JSON array, `[]`, BOM plus array, `null`, whitespace around `null`, BOM plus `null`, whole-document `true`/`false`/`1`/`"true"`, extra data after an object, a second BOM, and a directory in place of the file. A symlink to `{` is bad and is skipped the same way. None of these raised from `streak_start`, `partition_runs`, or `scan`.

Missing Boss summary. Day 2 absent between Z71 days: Boss `streak_start` as of day 3 is `2026-11-03`. An absent as-of day returns None even when day 1 lists Z71. A blocked as-of day skips to the prior present day. A blocked as-of day followed by a missing day returns None. The watcher still reads a missing day's CSV: runs include day 2 with `{Z71, Z99}`, and `bad_dates` is empty. `main` exits 0. A dangling symlink is `("missing", None)`: Boss ends at the later day, and the watcher keeps that day's CSV.

Signed-out suppression. Blocked flags: JSON true, int 1, float 1.0, and strings `true`, `yes`, `y`, `1`, including ` TRUE `, `\nYes\t`, `Y`, and ` y `. Also JSON `1e0`, `1E0`, `1e+0`, and `1.00` (each float 1.0). The brief prints the blocked line and the sign-in line once. Unreachable rows, live price changes, under-price, and the hold question are absent. Boss returns the intake mismatch Z72 and omits gone-hold Z71 and intake-unreachable Z72. The same tokens as file bytes on the middle day, including a UTF-8 BOM plus `1e0`, a BOM plus CRLF plus `1.0`, and a BOM plus `1`, are `("blocked", doc)`. Boss Z71 stays `2026-11-01`. Z99 stays unset. The watcher blocks that day.

Evidence flags: JSON false, int 0, float 0.0, strings `false`, `no`, `0`, ` FALSE `, `\nNo\t`, `"1.0"`, `"1e0"`, float 1.5, empty string, and a missing key. The brief prints the unreachable line, `live price change`, the under-price line, and `Should Z71 go on hold?`. The blocked line and the sign-in line are absent. Boss keeps gone-hold Z71 and reclassifies Z72 to intake-unreachable. Those values as file bytes on the middle day, listing Z99 and omitting Z71, break Boss Z71 to `2026-11-03` and the watcher keeps `{Z99}`. Whitespace around `false`, `no`, and `0` (space, tab, CR, LF, CRLF, VT, FF, NBSP, em space, U+2028, U+2029, ideographic space) stays open. The same pads around `true`, `yes`, `y`, and `1` are blocked.

Local merges, not pushed. Merge-base of the two tips is `origin/main` (`04bfc35`). Detached worktree at `origin/main`, fast-forward to `4e446f9`, then `git merge --no-commit --no-ff 208bd81`. Exit 0. `Automatic merge went well; stopped before committing as requested`. Unmerged paths: none. `git write-tree` is `b1cbba620faf258b4e938ab16f5b3325c33fe296`, the same tree as `4e446f9`. The index matches that HEAD, so the second merge adds no file change. The other order: fast-forward to `208bd81`, then `git merge --no-commit --no-ff 4e446f9`. Exit 0, same message, unmerged paths none, same write-tree. `git merge-tree --write-tree` both orders also exits 0 with that tree. Both merges were aborted. No merge commit. Because the merged tree is `4e446f9`, the pytest above is the pytest of the merged result: 2671 passed, 7 skipped.

Notes, not a fail. `daily_summary_draft.load_json` on `{` raises `JSONDecodeError`. `boss_decisions.main` still loads the current summary through that path and raises before it writes. Streak and the watcher skip that file. A readable dict whose `unreachable_mas` is the integer 1 raises `TypeError` from `streak_start`. Two thousand nested arrays make `json.loads` fail inside the caught decode error, and `load_summary` returns `("bad", None)`. S06 stays $25: `autolist.S06_LOCK_USD` is 25, `sassy-closet/lib/pricing.ts` has `const S06_LOCK_USD = 25`, `shared/tiered-pricing.ts` has `export const S06_LOCK_USD = 25`, and `shared/live-price-snapshot.json` `liveUsd` for S06 is 25. That snapshot, `shared/tiered-pricing.ts`, and `data/held.json` match `origin/main`. `sassy-closet-shop/data/products.json` has no S06 row. No Blob, KV, Meta, or price write. No push to the #225 branch or the #294 branch.

#249 is this log and is not graded.

## 2026-11-05 16:17 UTC — #295 at b142e7f PASS

Requested recheck of this head against parent `04bfc35`. This lane did not build it. #225 at `68f2df5` and #294 at `208bd81` were compared and not modified. No merge commit. Nothing was pushed to those branches.

#295 head is still `b142e7f1e9e14c26cfcbb768442b8d82d10f014e`. Parent is `04bfc350be2fcf47274ecf3e33f8f4eed1c0813e`. Comment `6663058055` says PASS on this SHA. The comment text is the evidence below.

INDEPENDENT RECHECK PASS at `b142e7f1e9e14c26cfcbb768442b8d82d10f014e`.

This lane did not build this commit. The head is still `b142e7f`. The parent is `04bfc35` (`origin/main`). The diff is 3 files, +1194/−1 (`scripts/boss_approval_queue.py`, `scripts/tests/test_boss_approval_queue.py`, `data/privacy-allowlist.json`). It does not change `data/held.json`, a price file, CSS, layout, or copy.

`npm ci --no-audit --no-fund` in both apps (intake added 143 packages, shop added 407), then `scripts/hard_recheck.sh --base origin/main` with `HARD_RECHECK_PYTHON=/tmp/py-recheck` (that wrapper execs `/usr/bin/python3` with pytest 9.2.0 and openpyxl 3.1.5 on `PYTHONPATH`). The worktree was detached at this SHA, so the summary branch field is blank. Log `out/recheck/20261105-142553-3435`. pytest 2142 passed, 7 skipped; privacy CLEAN; intake npm 277 / 274 / 0 / 3; shop npm 218 / 215 / 0 / 3; both tsc ok; `held.json` unchanged vs `origin/main` (sha256 `484dbec93976e07ce34a2acc693287b6909187834032241fe6dd95d88a83d9da`). Required skips: none. No hard-recheck step is SKIP. The tip line is INFO. Working tree clean. The head was still `b142e7f` after the run. The seven pytest skips are the six empty `neverList` gate cases and `scripts.tests.test_run_daily_shop_check::test_workflow_is_read_only_and_scheduled`. The new file's 28 tests passed.

Read-only. The source has one `urllib.request.Request` and it sets `method="GET"`. `GH_ARGS` is `gh pr list --state open --draft --limit 1000 --json number,title,isDraft,state,author,comments,reviews`. There is no `write_text`, `write_bytes`, `shell=True`, `git push`, `gh pr merge`, `gh pr create`, or `requests.post`. A live run's audit hook recorded one subprocess, `gh`, and no file open for write. The call was `GET https://sassy-closet.vercel.app/api/submissions` (HTTP 200, 76052 bytes) and that `gh pr list` (exit 0). `data/held.json`, `shared/live-price-snapshot.json`, `sassy-closet-shop/data/products.json`, and the script were the same sha256 after the run. Exit 0. No Blob, KV, Meta, price write, or message.

Failures print `could not read` and exit 0. Checked: `{`, empty, whitespace, `null`, a bare number, `true`, a non-row object, a UTF-8 BOM plus `{`, UTF-16, NUL, every byte 0–255, extra data after JSON, a directory in place of each fixture, a missing path, `--fx` of `0`, `-1`, `nan`, `inf`, `abc`, and empty, `file:///etc/passwd` (no socket), URLError, timeout, HTTP 500, HTML, an empty body, and bad JSON. `gh` timeout, non-zero exit, and `{` stdout do the same, and stderr is not printed. Nested arrays of depth 50, 200, 500, 1000, 2000, and 5000 on the cost summary print `Taobao cost recheck: could not read.` A broken `cost_recheck_block` that raises still prints the intake line and does not drop it. `--not-a-flag` exits 2 with no traceback.

Blocked values. This tree has no `cost_recheck_block.py`, so `defensive_login_blocked` is the reader. It matches #294 at `208bd81` `login_blocked` on 3198 values: JSON true, int 1, float 1.0, and strings `true`/`yes`/`y`/`1` after strip and case fold, including space, tab, CR, LF, CRLF, VT, FF, NBSP, em space, U+2028, U+2029, and ideographic space. JSON false, int 0, float 0.0, strings `false`/`no`/`0`/`1.0`/`1e0`, empty, a missing key, and a non-dict stay open. With #294's module installed, `summary_state` follows `load_summary` on 30 files (`{`, empty, `null`, `[]`, whole-file `true` and `1`, extra data, BOM plus `true`, BOM plus `1e0`, UTF-16, NUL, garbage, and the truth-table objects) plus a missing path and a directory. A symlink to `{` is `bad`. No disagreement.

Under-floor. `classify` calls `autolist.price`. That quote matches `shared/tiered-pricing.ts` `tieredSellUsd` and `sassy-closet/lib/pricing.ts` `tieredSellUsd` on 20011 landed values (every cent from 0.01 through 200.00, plus 16.26, 19.50, 19.51, 19.58, 3.9, 33.75, and CNY/6.723 landeds). Zero disagreements. Fixed points: 16.26→26, 19.50→30, 12→19, 5→10, 13→20, 3.9→8, 33→45. `_under` matches `pricing.ts` `underTieredMargin` (sell plus 1e-6 below the quote, or margin under 0.35) on that grid. Sell 20 on landed 13 is exactly 35% and is not under. Sell 19 is under. Sell 9 against the bumped quote 10 is under. Sell 45 on landed 33 is under the caption floor while sitting on the tier quote. V/Q/D debox is $7.50. Other letters are $0. Q02 at the $12 goods shape lands at $19.50 and quotes $30. A30 at $12 quotes $19. S06 $25 is not flagged for int 25, float 25.0, `25`, `25.00`, `25.000`, `$25`, `  $25  `, `025`, or fullwidth `２５`, including a cost of $80. Aliases `s6`, `S6`, `S006`, `s006`, and fullwidth-digit `S０６` at $25 are not flagged. `24.995` and `25.001` print `S06 stays $25.` and do not print the other amount. `S06B`, `S06Đ`, `A100`, and fullwidth `S06Ｂ` do not become S06.

Live read-only run, exit 0. Recomputing `render` from the saved GET and `gh` JSON matches stdout. 86 intake rows, no duplicate mã. 66 blank, 18 hand-edited, 1 under and hand-edited (J02), and S06 is the one row that is not waiting. Every flagged row has `auto_price` null. No under-floor row is left off the list. S20 is in the blank list; its quote is not printed. Q02 is `$30` and the tier quote is 30, so the line is hand-edited, not under. A30 is `$19` and the tier quote is 19, same. J02 is `$35` against quote 34, and the caption margin is under 35%. Live S06 `sell_usd` is blank, so it is not listed and `S06 stays $25.` is not printed. `shared/live-price-snapshot.json` `liveUsd` for S06 is 25. `sassy-closet-shop/data/products.json` has no S06 row. `autolist.S06_LOCK_USD` is 25. Held order matches `data/held.json` (21 mãs). `neverList` is empty and is not printed. `verify/cost-recheck` is absent, so the line is `No Taobao cost recheck summary was found.` 164 open drafts. 62 have a latest independent PASS and are listed. 99 whose latest independent verdict is FAIL are not, including #220, #226, #227, #229, #230, #242, #245, #259, #262, and #265. #294 and #225 are listed. #295 has no verdict comment and is not listed. A PASS whose author is the PR author does not count. Output has no email, URL, yen mark, or phone. The word Taobao appears only in the no-summary line.

```
Waiting on Boss
- No sell price on intake: A07, A08, A09, A10, A11, A12, A13, A14, A15, A16, A17, A18, A19, A20, A21, A22, A23, A24, A25, A26, A27, A28, A29, B03, D01, D02, D03, D04, D05, G01, H02, K02, K03, K04, K05, K06, O01, O02, O03, O04, O05, P02, Q01, S02, S03, S04, S05, S07, S08, S09, S10, S11, S12, S13, S14, S15, S16, S17, S18, S19, S20, V01, V02, V03, V04, V05.
- A01 is $25 on intake, hand-edited.
- A02 is $22 on intake, hand-edited.
- A03 is $19 on intake, hand-edited.
- A04 is $20 on intake, hand-edited.
- A05 is $25 on intake, hand-edited.
- A06 is $23 on intake, hand-edited.
- A30 is $19 on intake, hand-edited.
- B01 is $41 on intake, hand-edited.
- B02 is $30 on intake, hand-edited.
- H01 is $8 on intake, hand-edited.
- J01 is $30 on intake, hand-edited.
- J02 is $35 on intake, under the price floor and hand-edited.
- K01 is $37 on intake, hand-edited.
- P01 is $5 on intake, hand-edited.
- P03 is $18 on intake, hand-edited.
- P04 is $13 on intake, hand-edited.
- P05 is $23 on intake, hand-edited.
- Q02 is $30 on intake, hand-edited.
- S01 is $28 on intake, hand-edited.
- Held mãs still waiting: S14, A24, A25, S15, A26, K02, K03, K04, K05, V04, K06, V05, S16, S17, S18, S19, A27, A28, A29, H02, G01.
- Draft PR #21, Learn 07: dropship boutique law + sell-site APPLY, has an independent PASS and is still open.
- Draft PR #28, Learn 11: sell-test Origin gate + admin/Blob fix list (Kelly Ying look stays), has an independent PASS and is still open.
- Draft PR #195, Give auto-list a public mã index with no costs, has an independent PASS and is still open.
- Draft PR #208, Harden intake FX and shop health noindex after POST-207, has an independent PASS and is still open.
- Draft PR #209, Harden intake open-by-link/noindex regressions (post-#208), has an independent PASS and is still open.
- Draft PR #210, Hold a pickup with no usable landed cost even when Boss approved, has an independent PASS and is still open.
- Draft PR #211, Match the JS mã key in Python: drop a BOM, ASCII digits only, has an independent PASS and is still open.
- Draft PR #212, Live smoke: check S06's own JSON-LD offer is $25, not any $25 on the page, has an independent PASS and is still open.
- Draft PR #213, Host health: held PDP must also 404 under alternate spellings, has an independent PASS and is still open.
- Draft PR #214, Too-cheap: S06 missing from live catalog or off $25 is LOCK_DRIFT, has an independent PASS and is still open.
- Draft PR #215, hard_recheck: default base = merge-base with main (fix false FAIL on fresh clones), has an independent PASS and is still open.
- Draft PR #216, hard_recheck: parse Node spec-reporter test counts (ℹ tests N), has an independent PASS and is still open.
- Draft PR #217, Combined safe bundle #208-#216 (do not merge without Boss), has an independent PASS and is still open.
- Draft PR #218, Fail closed when Blob is down, and drop held folders from other mãs, has an independent PASS and is still open.
- Draft PR #219, Keep a blank intake sell blank and parse pasted yen safely, has an independent PASS and is still open.
- Draft PR #221, Guard shop workflows against wrong days, stale intake, and silent holds, has an independent PASS and is still open.
- Draft PR #222, Keep held-sheet landed digits aligned with the printed quote, has an independent PASS and is still open.
- Draft PR #223, Add a read-only workflow status report, has an independent PASS and is still open.
- Draft PR #224, Keep open Boss decisions the digest and streak were dropping, has an independent PASS and is still open.
- Draft PR #225, Draft: one branch for the safe shop fixes, has an independent PASS and is still open.
- Draft PR #231, Do not serve a held folder from another mã's image URL, has an independent PASS and is still open.
- Draft PR #232, Run the hard recheck on pull requests, has an independent PASS and is still open.
- Draft PR #233, Draft: read-only parity check for pricing, mã, and sizes, has an independent PASS and is still open.
- Draft PR #236, Draft: keep a trailing .0 on in-window EU shoe sizes, has an independent PASS and is still open.
- Draft PR #239, Add an on-demand read-only browser smoke, has an independent PASS and is still open.
- Draft PR #240, Draft: note that shop pricing prefers the yen cost, has an independent PASS and is still open.
- Draft PR #243, Draft: keep EU sizes when importing a G submission, has an independent PASS and is still open.
- Draft PR #246, Add a read-only draft merge-readiness report, has an independent PASS and is still open.
- Draft PR #247, Draft: keep an in-window trailing .0 on intake shoe chips, has an independent PASS and is still open.
- Draft PR #248, Keep a blank catalog status in the daily snapshot, has an independent PASS and is still open.
- Draft PR #251, Lock pull-request workflows to a read-only token, has an independent PASS and is still open.
- Draft PR #253, Draft: treat a trailing .0 as the allowed shoe chip in the gap report, has an independent PASS and is still open.
- Draft PR #254, Pin third-party actions to commit SHAs, has an independent PASS and is still open.
- Draft PR #255, Draft: name missing, stale, and unusable cost-recheck files, has an independent PASS and is still open.
- Draft PR #257, Test catalog fallback, the S06 lock, held photo spellings, and intake export, has an independent PASS and is still open.
- Draft PR #258, Split gap-report sizes on the same separators as listing, has an independent PASS and is still open.
- Draft PR #260, Add the repo knowledge base, has an independent PASS and is still open.
- Draft PR #261, Treat listing size aliases as the allowed gap-report chip, has an independent PASS and is still open.
- Draft PR #263, Reject workflows that install without the lockfile, has an independent PASS and is still open.
- Draft PR #264, Test the tiered under-$10 bump and the locked dress debox, has an independent PASS and is still open.
- Draft PR #266, Record the shop and listing split on loose shoe tokens, has an independent PASS and is still open.
- Draft PR #268, Record the quote gate rejecting A100 and K003, has an independent PASS and is still open.
- Draft PR #269, Draft: name a missing or stale Meta snapshot, has an independent PASS and is still open.
- Draft PR #271, Test canonical padded new mãs and the flat $10 quote, has an independent PASS and is still open.
- Draft PR #273, Record the glued clothing-letter size split, has an independent PASS and is still open.
- Draft PR #275, Record the shorter shop kind names, has an independent PASS and is still open.
- Draft PR #277, Reject install lifecycle scripts in both package.json files, has an independent PASS and is still open.
- Draft PR #278, Test empty catalog fallback and the sold public gate, has an independent PASS and is still open.
- Draft PR #279, Record the Official Excel mã spelling split, has an independent PASS and is still open.
- Draft PR #281, Return 503 when the shop catalog cannot be read, has an independent PASS and is still open.
- Draft PR #282, Reject invalid shop-desk USD text before save, has an independent PASS and is still open.
- Draft PR #283, Reject non-literal USD text in shop draft prices, has an independent PASS and is still open.
- Draft PR #284, Parse calculator and intake amounts as plain dollars, has an independent PASS and is still open.
- Draft PR #285, Read S06's own JSON-LD offer in host health, has an independent PASS and is still open.
- Draft PR #286, Reject junk dollar and comma text in parse_usd, has an independent PASS and is still open.
- Draft PR #287, Reject junk dollar text in pickup whole-dollar checks, has an independent PASS and is still open.
- Draft PR #288, Flag photo color ids the shop reel will not attach, has an independent PASS and is still open.
- Draft PR #289, Reject a dollar sign between digits in intake gap numbers, has an independent PASS and is still open.
- Draft PR #290, Reject a currency mark between digits in held price proposals, has an independent PASS and is still open.
- Draft PR #291, Flag customer copy the shop treats as stock or ops voice, has an independent PASS and is still open.
- Draft PR #292, Reject spliced dollar text in blank-mã order prices, has an independent PASS and is still open.
- Draft PR #294, Ignore signed-out cost rechecks as gone or price evidence, has an independent PASS and is still open.
- No Taobao cost recheck summary was found.
```

Merge. `git merge-tree --write-tree` of `b142e7f` with #225 at `68f2df5d5933b4884f081ccc314924a5b58c460b` exits 0. Tree `3ca3c5c927296070e85bb98cff5fe972c3921ad4`. The only overlapping path is `data/privacy-allowlist.json`, and it auto-merges. The merged JSON parses and contains both new rows. The same command with #294 at `208bd81d9e16bbfc7c8d9cda900a3099d87be174` exits 0. Tree `d57dd089b92f38a2709ebb1a99f8f0e26b0f8a6d`. No overlapping paths. That tree contains both `scripts/boss_approval_queue.py` and `scripts/cost_recheck_block.py`. #225 and #294 have the same `cost_recheck_block.py` blob `d34b3d445df4c626aa78799dfaf8b571f8122259`. `scripts/autolist.py` and `shared/tiered-pricing.ts` match `origin/main` on all three tips. No merge commit was made. Nothing was pushed to those branches.

Notes, not a fail. An 8-digit cost still returns, after about 68 seconds inside `autolist.price`. A 6-digit cost returns in under a second. Live sells are blank or plain integers. This tree's amount parser also accepts a leading `$` and Unicode digits, and it rejects `2.5e1`. Main's `Number()` accepts `2.5e1` and rejects `$25`. #225's `pricing.ts` `readMoney` is a different parser. `underTieredMargin` and `tieredSellUsd` are unchanged there, and `autolist.price` is unchanged, so the quote does not move on merge. Fullwidth `S０６` becomes S06 here because `norm_ma` uses Unicode `\d`. #225's `norm_ma` is ASCII-only, so that spelling would no longer be S06 after merging #225. Live mãs are ASCII. S06 stays $25. No push to the #295 branch.

#249 is this log and is not graded.

## 2026-11-05 19:54 UTC — #225 at 68f2df5 PASS

Requested recheck of this head against parent `4e446f9`. This lane did not build it. #294 at `208bd81` and #295 at `b142e7f` were compared and not modified. No merge commit. Nothing was pushed to those branches.

#225 head is still `68f2df5d5933b4884f081ccc314924a5b58c460b`. `4e446f9c5ef19210c21ec231b69d8058f16ebfcc` stays the prior PASS and is the parent. Comment `6667792988` says PASS on this SHA. The comment text is the evidence below.

INDEPENDENT RECHECK PASS at `68f2df5d5933b4884f081ccc314924a5b58c460b`.

This lane did not build this commit. The head is still `68f2df5`. The parent is `4e446f9`. The tip is 3 files, +56/−3 (`scripts/pickup.py`, `scripts/freshness_check.py`, `scripts/tests/test_workflow_guards.py`). It does not change `data/held.json`, a price file, CSS, layout, or copy. `4e446f9c5ef19210c21ec231b69d8058f16ebfcc` is the parent and is still an ancestor.

`npm ci --no-audit --no-fund` in both apps (intake added 143 packages, shop added 407), then `scripts/hard_recheck.sh --base origin/main` with `HARD_RECHECK_PYTHON=/tmp/py-recheck` (that wrapper execs `/usr/bin/python3` with pytest 9.2.0 and openpyxl 3.1.5 on `PYTHONPATH`). The worktree was detached at this SHA, so the summary branch field is blank. Log `out/recheck/20261105-192642-2951`. pytest 2684 passed, 7 skipped; privacy CLEAN; intake npm 365 / 362 / 0 / 3; shop npm 269 / 266 / 0 / 3; both tsc ok; `held.json` unchanged vs `origin/main` (sha256 `484dbec93976e07ce34a2acc693287b6909187834032241fe6dd95d88a83d9da`). Required skips: none. No hard-recheck step is SKIP. The tip line is INFO. Working tree clean. The head was still `68f2df5` after the run. The seven pytest skips are the six empty `neverList` gate cases and `scripts.tests.test_run_daily_shop_check::test_workflow_is_read_only_and_scheduled`.

Claim checked against parent `4e446f9`. Parent `plan_pickups` on boss-approved Z91 with sizes `[","]` and with `[" / | ; "]` returns `held=False`, `quoted_usd=25`, `flags=()`, `live=False`, `publish=False`. Parent `_photo_field({"gallery": [None, None]})` is 2, and `[None, "", "a.jpg"]` is 2, because `str(None)` is `"None"`. This commit holds those delimiter sizes with `flags=('missing_size',)`, `quoted_usd=None`, `held=True`, `blocks_live=True`, `live=False`, `publish=False`, and counts the null gallery as 0 and the mixed gallery as 1.

Delimiter-only sizes. Checked on Z91, G01, and O01: `,` `/` `|` `;`, repeats (`///`, `;;;`), lists of those marks, and whitespace around them (` , `, ` / | ; `, tab and newline around a comma). All are `missing_size`, held, unquoted, live false, publish false. Whitespace-only sizes (space, tab, newline, CRLF, NBSP, em space, ideographic space) take the same decision through the blank-size check.

Unicode dashes and other marks as the only size stay held and unquoted, `flags=('invalid_size',)`: ASCII hyphen, U+2010, figure dash, en dash, em dash, horizontal bar, minus, fullwidth hyphen, two-em dash, an em dash with spaces, fullwidth comma, fullwidth slash, fullwidth bar, fullwidth semicolon, ideographic comma, and U+200B. `S–M`, `S—M`, and shoe `35–36` are the same: `norm_sizes` is empty, so the dash is not read as a size and the row is not quoted.

Real sizes still quote 25 with `held=False`, `live=False`, `publish=False`: `M/L`, `S,M`, `S` plus a comma, `S|M`, `S;M`, spaced `S / M`, shoe `35/36`, `35.0`, `35///`, `/35/`, and O01 `38`. Those calls used an empty held set. G01 loaded from `data/held.json` stays held.

Null gallery. `_photo_field` skips `None` before `str`. `[None, None]` is 0. Null plus empty, space, tab, newline, NBSP, and ideographic space is 0. `[None, "a.jpg", ""]` is 1. JSON `[null, null, "", "  ", "a.jpg"]` is 1. A list under `gallery` wins over a later `photos` key, so nulls in `gallery` with a jpg in `photos` count 0. `gallery: null` falls through and a jpg in `photos` counts 1. Wiring that 0 into a boss-approved Z91 pickup is `missing_photos`, held, unquoted. `events_from_json` does not read `gallery`; a boss-approved pickup row whose only photo field is `gallery: [null, null]` has `photo_count=None` and is held unquoted. `evaluate` on an intake/Taobao fixture with sizes `S` and galleries `[null, null]` and `[null, "", "  "]` is `missing_photos`, `quoted_usd=None`, `live=False`, `publish=False`. The same fixture with one `a.jpg` among nulls is quoted 19 and held for `boss_approval` (`boss_approved` is forced false on that path). A delimiter-only size on that path is `missing_size` and unquoted.

S06 stays $25. Delimiter-only sizes with sell `25` or `$25` quote 25, flags empty, live false, publish false. Sell `30` is `s06_lock` and unquoted. `autolist.S06_LOCK_USD` is 25. Held K06 with sizes `[","]` and held G01 with `35/36` stay `flags=('held',)`, unquoted, live false, publish false. `data/held.json` bytes did not change.

Merge. `git merge-tree --write-tree` of `68f2df5` with #294 at `208bd81d9e16bbfc7c8d9cda900a3099d87be174` exits 0. Tree `5d8f72c23496c915d8b836bdde49910bbb70e117`, the same tree as this commit. No conflicted names. The same command with #295 at `b142e7f1e9e14c26cfcbb768442b8d82d10f014e` exits 0. Tree `3ca3c5c927296070e85bb98cff5fe972c3921ad4`. `data/privacy-allowlist.json` auto-merges. No merge commit was made. Each tip still has one parent. Nothing was pushed to those branches.

Notes, not a fail. A gallery slot that is `0`, `false`, `true`, `{}`, `[]`, U+200B, or U+FEFF still counts, because the check is `part is not None and str(part).strip()`. The parent counted those the same way. They are not JSON null. Copying that count onto a boss-approved pickup quotes 25 and does not hold; the pickup loader itself does not read `gallery`. Live and publish stay false. This lane does not adopt that as a fail of the null-slot fix. Dry-run galleries in this tree are URL strings.

No Blob, KV, Meta, or price write. No push to the #225 branch.

#249 is this log and is not graded.
