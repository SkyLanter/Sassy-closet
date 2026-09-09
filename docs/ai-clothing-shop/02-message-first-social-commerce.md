# Message-first / social-commerce

Facebook inbox is the store. The website is a **lookbook that starts a thread**. The app never Sends.

## What the platforms actually give you

**`m.me` links** open (or reopen) a Messenger conversation with a Page. Optional `ref` is copied into a `messaging_referrals` webhook so the Page knows *which tile* was clicked. The link can also carry a suggested `text`. Sources:

- [m.me Links (Messenger Platform)](https://developers.facebook.com/docs/messenger-platform/discovery/m-me-links/)
- [m.me Links (Business Messaging)](https://developers.facebook.com/documentation/business-messaging/messenger-platform/discovery/m-me-links)
- [messaging_referrals](https://developers.facebook.com/docs/messenger-platform/reference/webhook-events/messaging_referrals/)

Shape:

```text
https://m.me/<PAGE>?ref=A01
```

`ref` must be URL-encoded; alphanumeric plus `-` `_` `=` is the documented safe set. Clicking an `m.me` link on an existing thread **reopens the 24-hour window** — still a *customer-started* message, not a bot blast.

**Product templates / Send API** ([product template](https://developers.facebook.com/docs/messenger-platform/send-messages/template/product/)) let an *app* push catalog cards into chat. **Hard stop: no FB Send.** Do not add a Page token, do not POST `/me/messages`. Owner types in inbox.

**Meta catalogs** ([FBE catalog](https://developers.facebook.com/docs/facebook-business-extension/fbe/guides/catalog/), [Feed API](https://developers.facebook.com/docs/commerce-platform/catalog/feed/)) are for ads / Page shops. Optional later. A full-replace feed that drops rows Meta cannot find is the same class of bug as **seed drift**.

**Industry pattern:** fashion brands already close in IG/WA/Messenger DMs ([TailorTalk](https://tailortalk.ai/), [SellThread](https://sellthread.com/)). Those products automate the inbox. Sassy does **not** — humans + Zelle. Use them only as proof that “Message to buy” is a real storefront, not a missing checkout.

## What sell-test does today

- Copy: “Message to buy. No cart.”
- Footer: “Zelle · Message on Messenger.”
- Livestream chip → Facebook Page.
- Every CTA currently uses the **profile URL**, not `m.me?ref=`:
  `https://www.facebook.com/profile.php?id=61594312648057`

Shoppers land on the Page, not a prefilled “A01” thread. That is the gap.

## Apply (sell-test / shop feature branch)

1. **Keep Message-first.** No cart, no Stripe, no Square checkout widget, no “Buy now” that charges.
2. **CTA opens Messenger** (or the Page if `m.me` is not ready). Site does not Send.
3. Prefer `https://m.me/<page>?ref=<MA>` with `MA` in the allowlist only. Suggested composer text may include the mã; the **user** still hits send.
4. Hold pieces (P02, P05): CTA label stays **Message to buy** / **Inbox for price**, never “Pay $0”.
5. Zelle stays a **footer fact**, not a form. No Zelle API.
6. Do not embed the Messenger customer-chat plugin that auto-messages.
7. Caption starters belong in **intake Saved card** (already). Shop PDP can show “Message {mã} →” only.

## Hard stop reminder

Copy-only drafts in kit. Owner posts, owner sends, owner takes Zelle. Any PR that adds `pages_messaging` send scope or a “Send to buyer” button is out of scope.
