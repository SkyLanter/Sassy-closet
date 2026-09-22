"use client";

import { ASIA_SIZE_LETTERS, EU_SHOE_SIZES, isShopSize, type FitCm } from "@/lib/asia-size";
import type { AsiaSizeLetter, ShopSize } from "@/lib/types";

export function AdminSizeEditor({
  sizes,
  fitCm,
  onSizesChange,
  onFitChange,
}: {
  sizes: ShopSize[];
  fitCm: FitCm;
  onSizesChange: (sizes: ShopSize[]) => void;
  onFitChange: (fit: FitCm) => void;
}) {
  function toggle(letter: AsiaSizeLetter) {
    if (sizes.includes(letter)) {
      onSizesChange(sizes.filter((item) => item !== letter));
      return;
    }
    onSizesChange(ASIA_SIZE_LETTERS.filter((item) => item === letter || sizes.includes(item)));
  }

  function setCm(key: keyof FitCm, raw: string) {
    const trimmed = raw.trim();
    if (!trimmed) {
      onFitChange({ ...fitCm, [key]: null });
      return;
    }
    const value = Number(trimmed);
    if (!Number.isFinite(value) || value <= 0) {
      return;
    }
    onFitChange({ ...fitCm, [key]: value });
  }

  return (
    <section className="space-y-4" data-testid="admin-asia-size">
      <div>
        <h3 className="text-xs uppercase tracking-[0.14em] text-muted">Asia letters</h3>
        <p className="mt-1 text-sm text-muted">
          Main size system: 2XS–2XL (Asia). Never US. Leave empty when you do not have a letter — the shop will say Inbox for fit (PK / hair / thermos hide the row when empty).
        </p>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {ASIA_SIZE_LETTERS.map((letter) => {
          const selected = sizes.includes(letter);
          return (
            <button
              key={letter}
              type="button"
              data-testid="admin-size-chip"
              aria-pressed={selected}
              onClick={() => toggle(letter)}
              className={`rounded-full border px-2.5 py-1 text-[10px] font-medium uppercase tracking-[0.12em] ${
                selected
                  ? "border-ink bg-ink text-paper"
                  : "border-line bg-transparent text-ink hover:border-gold"
              }`}
            >
              {letter}
            </button>
          );
        })}
      </div>
      <div className="mt-4">
        <h3 className="text-xs uppercase tracking-[0.14em] text-muted">Footwear EU (secondary)</h3>
        <p className="mt-1 text-sm text-muted">Asia letters are main. Use 34–42 only for shoes when Taobao has no Asia letter. Never invent US maps.</p>
        <div className="mt-2 flex flex-wrap gap-1.5">
          {EU_SHOE_SIZES.map((size) => {
            const selected = sizes.includes(size);
            return (
              <button
                key={size}
                type="button"
                data-testid="admin-size-shoe-chip"
                aria-pressed={selected}
                onClick={() => {
                  if (selected) {
                    onSizesChange(sizes.filter((item) => item !== size));
                    return;
                  }
                  onSizesChange([...sizes.filter((item) => !EU_SHOE_SIZES.includes(item as typeof size)), size]);
                }}
                className={`rounded-full border px-2.5 py-1 text-[10px] font-medium uppercase tracking-[0.12em] ${
                  selected
                    ? "border-ink bg-ink text-paper"
                    : "border-line bg-transparent text-ink hover:border-gold"
                }`}
              >
                {size}
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <h3 className="text-xs uppercase tracking-[0.14em] text-muted">Fit · cm</h3>
        <p className="mt-1 text-sm text-muted">
          Stored cm only. Blank is honest. Do not type a number guessed from S / M / L.
        </p>
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        <CmField
          label="Bust / chest (cm)"
          value={fitCm.bustChestCm}
          onChange={(value) => setCm("bustChestCm", value)}
        />
        <CmField
          label="Waist (cm)"
          value={fitCm.waistCm}
          onChange={(value) => setCm("waistCm", value)}
        />
        <CmField
          label="Length (cm)"
          value={fitCm.lengthCm}
          onChange={(value) => setCm("lengthCm", value)}
        />
      </div>
    </section>
  );
}

function CmField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number | null;
  onChange: (value: string) => void;
}) {
  return (
    <label className="block text-xs uppercase tracking-[0.14em] text-muted">
      {label}
      <input
        inputMode="decimal"
        value={value === null ? "" : String(value)}
        onChange={(event) => onChange(event.target.value)}
        placeholder="—"
        className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm normal-case tabular-nums tracking-normal text-ink outline-none focus:border-gold"
      />
    </label>
  );
}
