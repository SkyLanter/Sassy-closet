"use client";

type SwatchSize = "sm" | "md" | "lg";

function swatchSizeClass(size: SwatchSize): string {
  switch (size) {
    case "sm":
      return "h-4 w-4";
    case "md":
      return "h-6 w-6";
    case "lg":
      return "h-8 w-8";
    default: {
      const _exhaustive: never = size;
      return _exhaustive;
    }
  }
}

export function ColorSwatch({
  hex,
  selected = false,
  onClick,
  size = "md",
  title,
}: {
  hex: string;
  selected?: boolean;
  onClick?: () => void;
  size?: SwatchSize;
  title?: string;
}) {
  return (
    <button
      type="button"
      aria-label={title ?? `Color ${hex}`}
      aria-pressed={selected}
      title={title ?? hex}
      onClick={onClick}
      className={`${swatchSizeClass(size)} shrink-0 rounded-sm border border-black/20 ${
        selected ? "outline outline-2 outline-offset-2 outline-ink" : ""
      }`}
      style={{ backgroundColor: hex }}
    />
  );
}

export function ColorSwatchEmpty({
  selected = false,
  onClick,
  size = "md",
}: {
  selected?: boolean;
  onClick?: () => void;
  size?: SwatchSize;
}) {
  return (
    <button
      type="button"
      aria-label="No color"
      aria-pressed={selected}
      onClick={onClick}
      className={`${swatchSizeClass(size)} relative shrink-0 rounded-sm border border-dashed border-muted ${
        selected ? "outline outline-2 outline-offset-2 outline-ink" : ""
      }`}
    >
      <span className="absolute inset-x-1 top-1/2 h-px -rotate-45 bg-muted" />
    </button>
  );
}
