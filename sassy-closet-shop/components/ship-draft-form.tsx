"use client";

import { useEffect, useState } from "react";
import { MaMark } from "@/components/ma-mark";
import { useSiteSettings } from "@/components/site-settings";
import { messengerHref } from "@/lib/messenger";
import {
  composeShipDraftMessage,
  EMPTY_SHIP_DRAFT,
  parseStoredShipDraft,
  SHIP_DRAFT_STORAGE_KEY,
  type ShipDraftFields,
} from "@/lib/ship-draft";
import { HOLD_ASK_LABEL, SHIP_QUOTE } from "@/lib/dropship-copy";
import { DROPSHIP_RAIL } from "@/lib/trust-copy";
import type { ProductStatus } from "@/lib/types";

export function ShipDraftForm({
  ma,
  status,
}: {
  ma: string;
  status: ProductStatus;
}) {
  const { facebookPageUrl } = useSiteSettings();
  const [fields, setFields] = useState<ShipDraftFields>(EMPTY_SHIP_DRAFT);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setFields(parseStoredShipDraft(window.sessionStorage.getItem(SHIP_DRAFT_STORAGE_KEY)));
  }, []);

  function persist(next: ShipDraftFields) {
    setFields(next);
    window.sessionStorage.setItem(SHIP_DRAFT_STORAGE_KEY, JSON.stringify(next));
  }

  const message = composeShipDraftMessage(ma, status, fields);
  const href = messengerHref(facebookPageUrl);

  return (
    <div className="space-y-3" data-testid="shop-ship-draft">
      <p className="text-[10px] uppercase tracking-[0.16em] text-muted">
        Address + <MaMark ma={ma} className="text-[10px] tracking-[0.16em]" /> · {SHIP_QUOTE}
      </p>
      <p className="text-[12px] leading-relaxed text-muted">
        {DROPSHIP_RAIL} After Zelle we order Taobao. Dest after confirm — no ship $ on this site.
      </p>
      <div className="grid gap-2 sm:grid-cols-2">
        <label className="block text-[10px] uppercase tracking-[0.14em] text-muted">
          Name
          <input
            value={fields.name}
            onChange={(event) => persist({ ...fields, name: event.target.value })}
            className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm normal-case tracking-normal text-ink outline-none focus:border-gold"
          />
        </label>
        <label className="block text-[10px] uppercase tracking-[0.14em] text-muted">
          City
          <input
            value={fields.city}
            onChange={(event) => persist({ ...fields, city: event.target.value })}
            className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm normal-case tracking-normal text-ink outline-none focus:border-gold"
          />
        </label>
      </div>
      <label className="block text-[10px] uppercase tracking-[0.14em] text-muted">
        Address
        <input
          value={fields.address}
          onChange={(event) => persist({ ...fields, address: event.target.value })}
          className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm normal-case tracking-normal text-ink outline-none focus:border-gold"
        />
      </label>
      <label className="block text-[10px] uppercase tracking-[0.14em] text-muted">
        Note
        <input
          value={fields.note}
          onChange={(event) => persist({ ...fields, note: event.target.value })}
          placeholder={status === "hold" ? HOLD_ASK_LABEL : "Size, color…"}
          className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm normal-case tracking-normal text-ink outline-none focus:border-gold"
        />
      </label>
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          className="rounded-full border border-line px-4 py-2 text-xs uppercase tracking-[0.12em] text-ink hover:border-gold"
          onClick={async () => {
            await navigator.clipboard.writeText(message);
            setCopied(true);
            window.setTimeout(() => setCopied(false), 2000);
          }}
        >
          {copied ? "Copied" : "Copy mã + address"}
        </button>
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          referrerPolicy="no-referrer"
          data-messenger-scheme="web-newtab"
          className="rounded-full bg-ink px-4 py-2 text-xs uppercase tracking-[0.12em] text-paper"
        >
          Open Messenger
        </a>
      </div>
    </div>
  );
}
