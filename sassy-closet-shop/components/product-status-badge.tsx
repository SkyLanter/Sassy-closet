import type { Product } from "@/lib/types";

export function ProductStatusBadge({
  product,
  tone = "plain",
  audience = "customer",
}: {
  product: Product;
  tone?: "plain" | "overlay";
  audience?: "customer" | "admin";
}) {
  const overlay = tone === "overlay";

  switch (product.status) {
    case "hold":
      if (audience !== "admin") {
        return null;
      }
      return (
        <span
          className={
            overlay
              ? "inline-flex items-center gap-1 rounded-full bg-gold px-2 py-0.5 text-[9px] font-semibold uppercase tracking-[0.16em] text-ink shadow-sm"
              : "inline-flex items-center gap-1 rounded-full bg-gold px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.16em] text-ink"
          }
        >
          {overlay ? "Hold" : "Tạm giữ · Hold"}
        </span>
      );
    case "available":
      if (audience !== "admin") {
        return null;
      }
      return (
        <span
          className={
            overlay
              ? "inline-flex items-center rounded-full bg-ink px-2 py-0.5 text-[9px] font-semibold uppercase tracking-[0.16em] text-paper shadow-sm"
              : "inline-flex items-center rounded-full bg-ink px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.16em] text-paper"
          }
        >
          Available
        </span>
      );
    case "sold":
      return (
        <span
          className={
            overlay
              ? "inline-flex items-center rounded-full bg-paper/90 px-2 py-0.5 text-[9px] font-semibold uppercase tracking-[0.16em] text-muted shadow-sm"
              : "inline-flex items-center rounded-full border border-line px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.16em] text-muted"
          }
        >
          Sold
        </span>
      );
    default: {
      const _exhaustive: never = product.status;
      return _exhaustive;
    }
  }
}
