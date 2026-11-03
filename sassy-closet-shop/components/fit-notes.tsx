import { formatCm } from "@/lib/asia-size";
import type { ShopMeasurements } from "@/lib/shop-look";

const ROWS = [
  { key: "bustChestCm", label: "Ngực / Bust" },
  { key: "waistCm", label: "Eo / Waist" },
  { key: "lengthCm", label: "Dài / Length" },
] as const;

/** Stored centimeters only. Hidden when the catalog row has none. */
export function FitNotes({ measurements }: { measurements: ShopMeasurements | null }) {
  if (!measurements) {
    return null;
  }

  const rows = ROWS.flatMap((row) => {
    const value = measurements[row.key];
    if (value === null) {
      return [];
    }
    return [{ label: row.label, value }];
  });

  if (rows.length === 0) {
    return null;
  }

  return (
    <div className="mt-6" data-testid="fit-notes">
      <p className="mb-2 text-[11px] uppercase tracking-[0.16em] text-muted" translate="no">
        Số đo · cm
      </p>
      <dl className="max-w-sm">
        {rows.map((row) => (
          <div key={row.label} className="flex min-h-11 items-center justify-between gap-4 border-b border-gold/35">
            <dt className="text-[13px] text-muted" translate="no">
              {row.label}
            </dt>
            <dd className="text-[13px] font-medium tabular-nums text-ink">{formatCm(row.value)}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
