import { HOLD_PRICE_LABEL } from "@/lib/dropship-copy";
import { formatUsd } from "@/lib/format";
import type { ProductStatus } from "@/lib/types";

/** Visible Save confirm: mã + status + $ or Hold. Not a next-mã trap tile. */
export function saveConfirmLine(
  ma: string,
  status: ProductStatus,
  priceUsd: number | null,
): string {
  switch (status) {
    case "hold":
      return `Save ${ma} · Hold · ${HOLD_PRICE_LABEL}`;
    case "available":
      return `Save ${ma} · Available · ${priceUsd === null ? HOLD_PRICE_LABEL : formatUsd(priceUsd)}`;
    case "sold":
      return `Save ${ma} · Sold / Gone · ${priceUsd === null ? "—" : formatUsd(priceUsd)}`;
    default: {
      const _exhaustive: never = status;
      return _exhaustive;
    }
  }
}

export function saveConfirmPrompt(line: string): string {
  return `${line}. Blob write + revalidate — not a silent Save.`;
}
