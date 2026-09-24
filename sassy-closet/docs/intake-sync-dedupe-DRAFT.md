# Intake → Hub Sync Dedupe — DRAFT (do NOT enable)

**Status:** Draft only. Requires Boss's exact yes before the poll is resumed
or the webhook is trusted in production. (Mini Boss reviewed the plan
2026-09-23 and confirmed 1–3 plus the additions below.)

## Problem
The intake poll (paused since ~2026-09-14 23:00 PT) and the intake webhook
(`notifyIntakeDatasetSyncWebhook`, never fired — Vercel lacks
`INTAKE_DATASET_SYNC_WEBHOOK_URL` / `INTAKE_DATASET_SYNC_WEBHOOK_KEY`)
can double-process the same submission. There is no lock today.

## Plan (Mini Boss-confirmed)

1. **Refresh the poll snapshot after every sync finishes.** Webhook runs must
   update the same snapshot the poll reads, or the next poll redoes the work.
2. **Idempotency key = mã + last-edited timestamp.** Skip submissions already
   processed at the same timestamp. ("Seen once forever" is wrong — an edit
   must re-sync.)
3. **Webhook primary, poll backup only for misses.** One sync routine body;
   only the wake differs. Never two slightly different sync scripts.

## Additions (Mini Boss, same review)

- **Wire the webhook env first.** Without URL/key/auth on the intake site,
  the poll becomes the real primary by accident.
- **Same sync path for both triggers.** One function/routine body.
- **needs_research rows:** pick up into the hub Excel only — row hold /
  needs_research, flag Buy Research. No invented fields, no margin apply,
  no sell land, no Square.
- **Path A vs Path B:** this poll/webhook is Excel/Photos (Path A).
  Sell-site land stays deliberate Admin/PR + photo re-host — do NOT auto-PR
  from the sync.
- **Quiet poll:** no chat spam on "nothing new"; alert only on real changes
  or failures.
- **Enable gate:** Boss exact-yes before Resume poll or trusting the webhook
  in prod.

## Truth order (Mini Boss, 2026-09-23)
Live sell-site PDP is the price SoT. The hub Excel is an ops mirror and is
significantly behind on sell_$ (blank for ~20 mãs as of 2026-09-23) — any
automation reading hub sell_$ will underprice/misprice. Do not let the sync
overwrite live prices from the hub.
