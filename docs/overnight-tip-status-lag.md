# Why overnight_tip_status "lags" one piece

Observed overnight: piece N's in-piece re-run named piece N-3 (e.g. 364's run named 358, not 361).

Root cause (read-only diagnosis, piece 367): the script only counts a branch as PASS when
`PROOF_ROOT/proof-NNN/SUMMARY.md` exists, carries a hard_recheck PASS verdict, AND mentions the
branch tip SHA. Inside piece N, the run happens before piece N's SUMMARY.md is written, so N is
`no-summary`. If the previous code piece's proof dir is also absent from PROOF_ROOT or still mid-write
when the run happens, the stack head falls back one more step. This is not a parser bug.

Fix (process, no code change): re-run AFTER SUMMARY.md is written:

    scripts/overnight_tip_status.sh --repo . --proof-root /workspace

Verified piece 367: post-proof re-run → `piece-364-tip-status-361-head @ 3b967a5`.
Verified piece 370: post-proof re-run after 367 SUMMARY.md → `piece-367-tip-status-lag-doc @ 04d737e`.
Verified piece 373: post-proof re-run after 370 SUMMARY.md → `piece-370-tip-status-367-head @ 523dd93`.
Verified piece 376: post-proof re-run after 373 SUMMARY.md → `piece-373-tip-status-370-head @ 73a3abf`. Header comment now guarded by a test.
Verified piece 379: post-proof re-run after 376 SUMMARY.md → `piece-376-tip-status-comment-test @ befb57a`.
Verified piece 382: post-proof re-run after 379 SUMMARY.md → `piece-379-tip-status-376-head @ bac81b7`.
Verified piece 385: post-proof re-run after 382 SUMMARY.md → `piece-382-tip-status-379-head @ 88e254d`.
Verified piece 388: post-proof re-run after 385 SUMMARY.md → `piece-385-tip-status-382-head @ 8f1da21`.
Verified piece 391: post-proof re-run after 388 SUMMARY.md → `piece-388-tip-status-385-head @ cc4129c`.
Verified piece 394: post-proof re-run after 391 SUMMARY.md → `piece-391-tip-status-388-head @ 29bc525`.
Verified piece 397: post-proof re-run after 394 SUMMARY.md → `piece-394-tip-status-391-head @ cbc9a0a`.
Verified piece 400: post-proof re-run after 397 SUMMARY.md → `piece-397-tip-status-394-head @ 65d8e4b`.
Verified piece 403: post-proof re-run after 400 SUMMARY.md → `piece-400-tip-status-397-head @ f89001c`.
Verified piece 406: post-proof re-run after 403 SUMMARY.md → `piece-403-tip-status-400-head @ f123e1e`.
Verified piece 409: post-proof re-run after 406 SUMMARY.md → `piece-406-tip-status-403-head @ a122518`.
Verified piece 412: post-proof re-run after 409 SUMMARY.md → `piece-409-tip-status-406-head @ 4dad6f9`.
Verified piece 415: post-proof re-run after 412 SUMMARY.md → `piece-412-tip-status-409-head @ 03d5049`.
Verified piece 418: post-proof re-run after 415 SUMMARY.md → `piece-415-tip-status-412-head @ 249263e`.
Verified piece 421: post-proof re-run after 418 SUMMARY.md → `piece-418-tip-status-415-head @ a15683a`.
Verified piece 424: post-proof re-run after 421 SUMMARY.md → `piece-421-tip-status-418-head @ b011311`.
Verified piece 427: post-proof re-run after 424 SUMMARY.md → `piece-424-tip-status-421-head @ 93b04e4`.
Verified piece 430: post-proof re-run after 427 SUMMARY.md → `piece-427-tip-status-424-head @ 478f2fe`.
Verified piece 433: post-proof re-run after 430 SUMMARY.md → `piece-430-tip-status-427-head @ cfbd7a4`.
Verified piece 436: post-proof re-run after 433 SUMMARY.md → `piece-433-tip-status-430-head @ 98d7347`.
Verified piece 439: post-proof re-run after 436 SUMMARY.md → `piece-436-tip-status-433-head @ abdd10c`.
Verified piece 442: post-proof re-run after 439 SUMMARY.md → `piece-439-tip-status-436-head @ fcb2ae3`.
Verified piece 445: post-proof re-run after 442 SUMMARY.md → `piece-442-tip-status-439-head @ 074831f`.
Verified piece 448: post-proof re-run after 445 SUMMARY.md → `piece-445-tip-status-442-head @ 74dc93f`.
Verified piece 451: post-proof re-run after 448 SUMMARY.md → `piece-448-tip-status-445-head @ 3abc5d2`.
Verified piece 454: post-proof re-run after 451 SUMMARY.md → `piece-451-tip-status-448-head @ 94f8edd`.
Verified piece 457: post-proof re-run after 454 SUMMARY.md → `piece-454-tip-status-451-head @ 2f22826`.
Verified piece 460: post-proof re-run after 457 SUMMARY.md → `piece-457-tip-status-454-head @ eda0872`.
Verified piece 463: post-proof re-run after 460 SUMMARY.md → `piece-460-tip-status-457-head @ e357e72`.
Verified piece 466: post-proof re-run after 463 SUMMARY.md → `piece-463-tip-status-460-head @ 8738937`.
Verified piece 469: post-proof re-run after 466 SUMMARY.md → `piece-466-tip-status-463-head @ a3646e8`.
Verified piece 472: post-proof re-run after 469 SUMMARY.md → `piece-469-tip-status-466-head @ 5c17c81`.
Verified piece 475: post-proof re-run after 472 SUMMARY.md → `piece-472-tip-status-469-head @ b9da541`.
Verified piece 478: post-proof re-run after 475 SUMMARY.md → `piece-475-tip-status-472-head @ b282fb3`.
Verified piece 481: post-proof re-run after 478 SUMMARY.md → `piece-478-tip-status-475-head @ e40f235`.
Verified piece 484: post-proof re-run after 481 SUMMARY.md → `piece-481-tip-status-478-head @ 7c9a307`.
Verified piece 487: post-proof re-run after 484 SUMMARY.md → `piece-484-tip-status-481-head @ 3fd298b`.
Verified piece 490: post-proof re-run after 487 SUMMARY.md → `piece-487-tip-status-484-head @ f6d5c17`.
Verified piece 493: post-proof re-run after 490 SUMMARY.md → `piece-490-tip-status-487-head @ ed86b6e`.
Verified piece 496: post-proof re-run after 493 SUMMARY.md → `piece-493-tip-status-490-head @ c86dd33`.
Verified piece 499: post-proof re-run after 496 SUMMARY.md → `piece-496-tip-status-493-head @ 0104e55`.
Verified piece 502: post-proof re-run after 499 SUMMARY.md → `piece-499-tip-status-496-head @ 3b83066`.
Verified piece 505: post-proof re-run after 502 SUMMARY.md → `piece-502-tip-status-499-head @ d5a5339`.
- Verified piece 508 (2026-10-29): post-SUMMARY re-run of overnight_tip_status.sh names piece-505-tip-status-502-head @ 5840143.
- Verified piece 511 (2026-10-29): post-SUMMARY re-run of overnight_tip_status.sh names piece-508-tip-status-505-head @ b78c46d.
- Verified piece 514 (2026-10-29): post-SUMMARY re-run of overnight_tip_status.sh names piece-511-tip-status-508-head @ 82b22e2.
- Verified piece 517 (2026-10-29): post-SUMMARY re-run of overnight_tip_status.sh names piece-514-tip-status-511-head @ dc900a3.
- Verified piece 520 (2026-10-29): post-SUMMARY re-run of overnight_tip_status.sh names piece-517-tip-status-514-head @ bfa6d24.
- Verified piece 523 (2026-10-29): post-SUMMARY re-run of overnight_tip_status.sh names piece-520-tip-status-517-head @ 8fe24e8.
- Verified piece 529 (2026-10-29): post-SUMMARY re-run of overnight_tip_status.sh names piece-526-privacy-check-brokenpipe @ ecdc540 (stacked on 523 @ 3e576fb).
- Verified piece 532 (2026-10-29): post-SUMMARY re-run of overnight_tip_status.sh names piece-529-tip-status-526-head @ 08740a8.
- Verified piece 535 (2026-10-29): post-SUMMARY re-run of overnight_tip_status.sh names piece-532-tip-status-529-head @ c3842be.
- Verified piece 538 (2026-10-29): post-SUMMARY re-run of overnight_tip_status.sh names piece-535-tip-status-532-head @ bbe535a.
- Verified piece 541 (2026-10-29): post-SUMMARY re-run of overnight_tip_status.sh names piece-538-tip-status-535-head @ 55fb69d.
- Verified piece 544 (2026-10-29): post-SUMMARY re-run of overnight_tip_status.sh names piece-541-tip-status-538-head @ 2b18d1b.
- Verified piece 547 (2026-10-29): post-SUMMARY re-run of overnight_tip_status.sh names piece-544-tip-status-541-head @ bd9cbd5.
- Verified piece 550 (2026-10-29): post-SUMMARY re-run of overnight_tip_status.sh names piece-547-tip-status-544-head @ 20f7862.
- Verified piece 553 (2026-10-29): post-SUMMARY re-run of overnight_tip_status.sh names piece-550-tip-status-547-head @ e8b4f72.
- Verified piece 556 (2026-10-29): post-SUMMARY re-run of overnight_tip_status.sh names piece-553-tip-status-550-head @ ef7e3f4.
- Verified piece 559 (2026-10-29): post-SUMMARY re-run of overnight_tip_status.sh names piece-556-tip-status-553-head @ ee3a99c.
- Verified piece 562 (2026-10-29): post-SUMMARY re-run of overnight_tip_status.sh names piece-559-tip-status-556-head @ cde49f3.
- Verified piece 565 (2026-10-29): post-SUMMARY re-run of overnight_tip_status.sh names piece-562-tip-status-559-head @ 3fd509a.
- Piece 568 (2026-10-29): re-ran `overnight_tip_status.sh` after 565 landed; recommended tip names `piece-565-tip-status-562-head` @ `93a0034`. Docs-only confirm.
- Piece 571 (2026-10-29): re-ran `overnight_tip_status.sh` after 568 landed; stack head names `piece-568-tip-status-565-head` @ `404f9f7` (PASS). Docs-only confirm.
- Piece 574 (2026-10-29): re-ran `overnight_tip_status.sh` after 571 landed; stack head names `piece-571-tip-status-568-head` @ `480c27d` (PASS). Docs-only confirm.
- Piece 577 (2026-10-29): re-ran `overnight_tip_status.sh` after 574 landed; stack head names `piece-574-tip-status-571-head` @ `da1f771` (PASS). Docs-only confirm.
- Piece 580 (2026-10-29): re-ran `overnight_tip_status.sh` after 577 landed; stack head names `piece-577-tip-status-574-head` @ `86a4c19` (PASS). Docs-only confirm.
- Piece 583 (2026-10-29): re-ran `overnight_tip_status.sh` after 580 landed; stack head names `piece-580-tip-status-577-head` @ `dfd9e35` (PASS). Docs-only confirm.
- Piece 586 (2026-10-29): re-ran `overnight_tip_status.sh` after 583 landed; stack head names `piece-583-tip-status-580-head` @ `1fc24a3` (PASS). Docs-only confirm.
- Piece 589 (2026-10-29): re-ran `overnight_tip_status.sh` after 586 landed; stack head names `piece-586-tip-status-583-head` @ `ebbd693` (PASS). Docs-only confirm.
- Piece 592 (2026-10-29): re-ran `overnight_tip_status.sh` after 589 landed; stack head names `piece-589-tip-status-586-head` @ `b690b29` (PASS). Docs-only confirm.
- Piece 595 (2026-10-29): re-ran `overnight_tip_status.sh` after 592 landed; stack head names `piece-592-tip-status-589-head` @ `d152556` (PASS). Docs-only confirm.
- Piece 598 (2026-10-29): re-ran `overnight_tip_status.sh` after 595 landed; stack head names `piece-595-tip-status-592-head` @ `c498c97` (PASS). Docs-only confirm.
- Piece 601 (2026-10-29): re-ran `overnight_tip_status.sh` after 598 landed; stack head names `piece-598-tip-status-595-head` @ `79d6cf4` (PASS). Docs-only confirm.
- Piece 604 (2026-10-29): re-ran `overnight_tip_status.sh` after 601 landed; stack head names `piece-601-tip-status-598-head` @ `d57ee46` (PASS). Docs-only confirm.
- Piece 607 (2026-10-29): re-ran `overnight_tip_status.sh` after 604 landed; stack head names `piece-604-tip-status-601-head` @ `02817b4` (PASS). Docs-only confirm.
- Piece 610 (2026-10-29): re-ran `overnight_tip_status.sh` after 607 landed; stack head names `piece-607-tip-status-604-head` @ `363b9f2` (PASS). Docs-only confirm.
- Piece 613 (2026-10-29): re-ran `overnight_tip_status.sh` after 610 landed; stack head names `piece-610-tip-status-607-head` @ `c97cae0` (PASS). Docs-only confirm.
- Piece 616 (2026-10-29): re-ran `overnight_tip_status.sh` after 613 landed; stack head names `piece-613-tip-status-610-head` @ `f4f61c0` (PASS). Docs-only confirm.
- Piece 619: re-ran overnight_tip_status.sh after 616 landed; stack head = piece-616-tip-status-613-head @ b4664fa (PASS). PRIMARY tip text unchanged.
- Piece 622 (2026-10-29): re-ran `overnight_tip_status.sh` after 619 landed; stack head names `piece-619-tip-status-616-head` @ `eded58e` (PASS). Docs-only confirm; PRIMARY tip text unchanged.
- Piece 625 (2026-10-29): re-ran `overnight_tip_status.sh` after 622 landed; stack head names `piece-622-tip-status-619-head` @ `72c88cf` (PASS). Docs-only confirm; PRIMARY tip text unchanged.
- Piece 628 (2026-10-29): re-ran `overnight_tip_status.sh` after 625 landed; stack head names `piece-625-tip-status-622-head` @ `bbeaa42` (PASS). Docs-only confirm; PRIMARY tip text unchanged.
- Piece 631 (2026-10-29): re-ran `overnight_tip_status.sh` after 628 landed; stack head names `piece-628-tip-status-625-head` @ `6125119` (PASS). Docs-only confirm; PRIMARY tip text unchanged.
- Piece 634 (2026-10-29): re-ran `overnight_tip_status.sh` after 631 landed; stack head names `piece-631-tip-status-628-head` @ `534a1c5` (PASS). Docs-only confirm; PRIMARY tip text unchanged.
- Piece 637 (2026-10-29): re-ran `overnight_tip_status.sh` after 634 landed; stack head names `piece-634-tip-status-631-head` @ `ef15ba7` (PASS). Docs-only confirm; PRIMARY tip text unchanged.
- Piece 640 (2026-10-29): re-ran `overnight_tip_status.sh` after 637 landed; stack head names `piece-637-tip-status-634-head` @ `30637bd` (PASS). Docs-only confirm; PRIMARY tip text unchanged.
- Piece 643 (2026-10-29): re-ran `overnight_tip_status.sh` after 640 landed; stack head names `piece-640-tip-status-637-head` @ `da78ed5` (PASS). Docs-only confirm; PRIMARY tip text unchanged.
- Piece 646 (2026-10-29): re-ran `overnight_tip_status.sh` after 643 landed; stack head names `piece-643-tip-status-640-head` @ `027d166` (PASS). Docs-only confirm; PRIMARY tip text unchanged.
- Piece 649 (2026-10-29): re-ran `overnight_tip_status.sh` after 646 landed; stack head names `piece-646-tip-status-643-head` @ `a08a859` (PASS). Docs-only confirm; PRIMARY tip text unchanged.
- Piece 652 (2026-10-29): re-ran `overnight_tip_status.sh` after 649 landed; stack head names `piece-649-tip-status-646-head` @ `1b378ed` (PASS). Docs-only confirm; PRIMARY tip text unchanged.
- Piece 655 (2026-10-29): re-ran `overnight_tip_status.sh` after 652 landed; stack head names `piece-652-tip-status-649-head` @ `c541ecc` (PASS). Docs-only confirm; PRIMARY tip text unchanged.
- Piece 658 (2026-10-29): re-ran `overnight_tip_status.sh` after 655 landed; stack head names `piece-655-tip-status-652-head` @ `934c8f4` (PASS). Docs-only confirm; PRIMARY tip text unchanged.
- Piece 661 (2026-10-29): re-ran `overnight_tip_status.sh` after 658 SUMMARY landed; recommended tip names **658** @ `2d78072`. PRIMARY tip text unchanged.
- Piece 664 (2026-10-29): re-ran `overnight_tip_status.sh` after 661 SUMMARY landed; recommended tip names **661** @ `1803f10`. PRIMARY tip text unchanged.
- Piece 667 (2026-10-29): re-ran `overnight_tip_status.sh` after 664 SUMMARY landed; recommended tip names **664** @ `108e8ef`. PRIMARY tip text unchanged.
- Piece 670 (2026-10-29): re-ran `overnight_tip_status.sh` after 667 SUMMARY landed; recommended tip names **667** @ `dedc56d`. PRIMARY tip text unchanged.
- Piece 673 (2026-10-29): re-ran `overnight_tip_status.sh` after 670 SUMMARY landed; recommended tip names **670** @ `cdbd3ed`. PRIMARY tip text unchanged.
- Piece 676 (2026-10-29): re-ran `overnight_tip_status.sh` after 673 SUMMARY landed; recommended tip names **673** @ `d13a44a`. PRIMARY tip text unchanged.
- Piece 679 (2026-10-29): re-ran `overnight_tip_status.sh` after 676 SUMMARY landed; recommended tip names **676** @ `8290300`. PRIMARY tip text unchanged.
- Piece 682 (2026-10-29): re-ran `overnight_tip_status.sh` after 679 SUMMARY landed; recommended tip names **679** @ `43efc1f`. PRIMARY tip text unchanged.
- Piece 685 (2026-10-29): re-ran `overnight_tip_status.sh` after 682 SUMMARY landed; recommended tip names **682** @ `b8b0f38`. PRIMARY tip text unchanged.
- Piece 688 (2026-10-29): re-ran `overnight_tip_status.sh` after 685 SUMMARY landed; recommended tip names **685** @ `c56a204`. PRIMARY tip text unchanged.
- Piece 691 (2026-10-29): re-ran `overnight_tip_status.sh` after 688 SUMMARY landed; recommended tip names **688** @ `cbc7bc7`. PRIMARY tip text unchanged.
- Piece 694 (2026-10-29): re-ran `overnight_tip_status.sh` after 691 SUMMARY landed; recommended tip names **691** @ `3c3929e`. PRIMARY tip text unchanged.
- Piece 697 (2026-10-29): re-ran `overnight_tip_status.sh` after 694 SUMMARY landed; recommended tip names **694** @ `cca6268`. PRIMARY tip text unchanged.
- Piece 700 (2026-10-29): re-ran `overnight_tip_status.sh` after 697 SUMMARY landed; recommended tip names **697** @ `d33746e`. PRIMARY tip text unchanged.
- Piece 703 (2026-10-29): re-ran `overnight_tip_status.sh` after 700 SUMMARY landed; recommended tip names **700** @ `c144284`. PRIMARY tip text unchanged.
- Piece 706 (2026-10-29): re-ran `overnight_tip_status.sh` after 703 SUMMARY landed; recommended tip names **703** @ `372f1a3`. PRIMARY tip text unchanged.
- Piece 709 (2026-10-29): re-ran `overnight_tip_status.sh` after 706 SUMMARY landed; recommended tip names **706** @ `3709df9`. PRIMARY tip text unchanged.
- Piece 712 (2026-10-29): re-ran `overnight_tip_status.sh` after 709 SUMMARY landed; recommended tip names **709** @ `f1a3a70`. PRIMARY tip text unchanged.
- Piece 715 (2026-10-29): re-ran `overnight_tip_status.sh` after 712 SUMMARY landed; recommended tip names **712** @ `9b0bf0b`. PRIMARY tip text unchanged.
- Piece 718 (2026-10-29): re-ran `overnight_tip_status.sh` after 715 SUMMARY landed; recommended tip names **715** @ `28f534f`. PRIMARY tip text unchanged.
- Piece 721 (2026-10-29): re-ran `overnight_tip_status.sh` after 718 SUMMARY landed; recommended tip names **718** @ `6471298`. PRIMARY tip text unchanged.
- Piece 724 (2026-10-29): re-ran `overnight_tip_status.sh` after 721 SUMMARY landed; recommended tip names **721** @ `eb494b8`. PRIMARY tip text unchanged.
- Piece 727 (2026-10-29): re-ran `overnight_tip_status.sh` after 724 SUMMARY landed; recommended tip names **724** @ `c97e06f`. PRIMARY tip text unchanged.
- Piece 730 (2026-10-29): re-ran `overnight_tip_status.sh` after 727 SUMMARY landed; recommended tip names **727** @ `93c7715`. PRIMARY tip text unchanged.
- Piece 733 (2026-10-29): re-ran `overnight_tip_status.sh` after 730 SUMMARY landed; recommended tip names **730** @ `9267e06`. PRIMARY tip text unchanged.
- Piece 736 (2026-10-29): re-ran `overnight_tip_status.sh` after 733 SUMMARY landed; recommended tip names **733** @ `cd80015`. PRIMARY tip text unchanged.
- Piece 739 (2026-10-29): re-ran `overnight_tip_status.sh` after 736 SUMMARY landed; recommended tip names **736** @ `d665ed0`. PRIMARY tip text unchanged.
- Piece 742 (2026-10-29): re-ran `overnight_tip_status.sh` after 739 SUMMARY landed; recommended tip names **739** @ `a7d24df`. PRIMARY tip text unchanged.
- Piece 745 (2026-10-29): re-ran `overnight_tip_status.sh` after 742 SUMMARY landed; recommended tip names **742** @ `97eaab7`. PRIMARY tip text unchanged.
- Piece 748 (2026-10-29): re-ran `overnight_tip_status.sh` after 745 SUMMARY landed; recommended tip names **745** @ `7166c1e`. PRIMARY tip text unchanged.
- Piece 751 (2026-10-29): re-ran `overnight_tip_status.sh` after 748 SUMMARY landed; recommended tip names **748** @ `16147fb`. PRIMARY tip text unchanged.
- Piece 754 (2026-10-29): re-ran `overnight_tip_status.sh` after 751 SUMMARY landed; recommended tip names **751** @ `8ee92b9`. PRIMARY tip text unchanged.
- Piece 757 (2026-10-29): re-ran `overnight_tip_status.sh` after 754 SUMMARY landed; recommended tip names **754** @ `b9e623c`. PRIMARY tip text unchanged.
- Piece 760 (2026-10-29): re-ran `overnight_tip_status.sh` after 757 SUMMARY landed; recommended tip names **757** @ `a665051`. PRIMARY tip text unchanged.
- Piece 763 (2026-10-29): re-ran `overnight_tip_status.sh` after 760 SUMMARY landed; recommended tip names **760** @ `1b64c0a`. PRIMARY tip text unchanged.
- Piece 766 (2026-10-29): re-ran `overnight_tip_status.sh` after 763 SUMMARY landed; recommended tip names **763** @ `fc02608`. PRIMARY tip text unchanged.
- Piece 769 (2026-10-29): re-ran `overnight_tip_status.sh` after 766 SUMMARY landed; recommended tip names **766** @ `2d1bf2f`. PRIMARY tip text unchanged.
- Piece 772 (2026-10-29): re-ran `overnight_tip_status.sh` after 769 SUMMARY landed; recommended tip names **769** @ `ae5258b`. PRIMARY tip text unchanged.
- Piece 775 (2026-10-29): re-ran `overnight_tip_status.sh` after 772 SUMMARY landed; stack head names **772** @ `bc4ae7a` (PASS). PRIMARY tip text unchanged.
- Piece 778 (2026-10-29): re-ran `overnight_tip_status.sh` after 775 SUMMARY landed; stack head names **775** @ `3935f94` (PASS). PRIMARY tip text unchanged.
- Piece 781 (2026-10-29): re-ran `overnight_tip_status.sh` after 778 SUMMARY landed; stack head names **778** @ `c2eca60` (PASS). PRIMARY tip text unchanged.
- Piece 784 (2026-10-29): re-ran `overnight_tip_status.sh` after 781 SUMMARY landed; stack head names **781** @ `23c085c` (PASS). PRIMARY tip text unchanged.
- Piece 787 (2026-10-29): re-ran `overnight_tip_status.sh` after 784 SUMMARY landed; stack head names **784** @ `2b214a6` (PASS). PRIMARY tip text unchanged.
- Piece 790 (2026-10-29): re-ran `overnight_tip_status.sh` after 787 SUMMARY landed; stack head names **787** @ `8a0b17f` (PASS). PRIMARY tip text unchanged.
- Piece 793 (2026-10-29): re-ran `overnight_tip_status.sh` after 790 SUMMARY landed; stack head names **790** @ `5b90b95` (PASS). PRIMARY tip text unchanged.
- Piece 796 (2026-10-29): re-ran `overnight_tip_status.sh` after 793 SUMMARY landed; stack head names **793** @ `d68aab5` (PASS). PRIMARY tip text unchanged.
