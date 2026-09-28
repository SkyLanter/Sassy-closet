import { SHOW_TRUST_STRIP, TRUST_PAY_LINE, TRUST_SHIP_LINE } from "@/lib/trust-strip";

/** Rendered only when SHOW_TRUST_STRIP is on. Default is off. */
export function TrustStrip() {
  if (!SHOW_TRUST_STRIP) {
    return null;
  }

  return (
    <div
      data-testid="shop-trust-strip"
      className="mx-auto max-w-7xl pb-2 pl-[max(1.25rem,env(safe-area-inset-left,0px))] pr-[max(1.25rem,env(safe-area-inset-right,0px))] text-center sm:pl-[max(2rem,env(safe-area-inset-left,0px))] sm:pr-[max(2rem,env(safe-area-inset-right,0px))]"
    >
      <p className="text-[11px] uppercase leading-relaxed tracking-[0.14em] text-muted" translate="no">
        {TRUST_PAY_LINE}
      </p>
      <p className="mt-1 text-[11px] uppercase leading-relaxed tracking-[0.14em] text-muted" translate="no">
        {TRUST_SHIP_LINE}
      </p>
    </div>
  );
}
