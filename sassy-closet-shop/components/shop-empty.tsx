import { MessengerCta } from "@/components/messenger-cta";

export function ShopEmpty({
  title,
  body,
}: {
  title: string;
  body: string;
}) {
  return (
    <div
      role="status"
      className="ky-empty-rule bg-paper py-16 text-center"
    >
      <p className="font-display text-[2.35rem] font-medium leading-[1.08] tracking-[0.03em] text-balance text-ink sm:text-5xl" translate="no">{title}</p>
      <p className="mx-auto mt-3 max-w-sm text-[13px] leading-relaxed text-pretty text-muted" translate="no">{body}</p>
      <div className="mt-6 flex justify-center">
        <MessengerCta />
      </div>
    </div>
  );
}
