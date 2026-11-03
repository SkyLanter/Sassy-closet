import type { ReactNode } from "react";
import { MessengerCta } from "@/components/messenger-cta";

export function ShopEmpty({
  title,
  body,
  actions,
}: {
  title: string;
  body: string;
  actions?: ReactNode;
}) {
  return (
    <div
      role="status"
      className="ky-empty-rule liquid-glass-sheet rounded-[var(--glass-radius)] py-16 text-center"
    >
      <p className="mx-auto max-w-sm break-words font-display text-[2.35rem] font-medium leading-[1.08] tracking-[0.03em] text-balance text-ink outline-none sm:text-5xl" translate="no">{title}</p>
      <p className="mx-auto mt-3 max-w-sm break-words text-[13px] leading-relaxed text-pretty text-muted" translate="no">{body}</p>
      {actions}
      <div className="mt-6 flex justify-center">
        <MessengerCta />
      </div>
    </div>
  );
}
