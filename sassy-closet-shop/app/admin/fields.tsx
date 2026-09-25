"use client";

export function Field({
  label,
  value,
  onChange,
  disabled,
  placeholder,
  hint,
  testId,
  required,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  placeholder?: string;
  hint?: string;
  testId?: string;
  /** Shows a small "Required" chip next to the label. */
  required?: boolean;
}) {
  return (
    <label className="block text-xs uppercase tracking-[0.14em] text-muted">
      <span className="inline-flex items-center gap-2">
        {label}
        {required ? (
          <span className="rounded-full border border-gold-deep/40 bg-blush px-2 py-0.5 text-[10px] font-medium normal-case tracking-normal text-gold-deep">
            Required
          </span>
        ) : null}
      </span>
      <input
        value={value}
        disabled={disabled}
        placeholder={placeholder}
        data-testid={testId}
        onChange={(event) => onChange(event.target.value)}
        className="mt-1 min-h-11 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm normal-case tracking-normal text-ink outline-none focus:border-gold disabled:bg-blush"
      />
      {hint ? (
        <span className="mt-1 block text-[11px] font-normal normal-case tracking-normal text-muted">
          {hint}
        </span>
      ) : null}
    </label>
  );
}

export function Area({
  label,
  value,
  onChange,
  hint,
  placeholder,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  hint?: string;
  placeholder?: string;
}) {
  return (
    <label className="block text-xs uppercase tracking-[0.14em] text-muted">
      {label}
      <textarea
        value={value}
        rows={5}
        placeholder={placeholder}
        onChange={(event) => onChange(event.target.value)}
        className="mt-1 w-full min-h-11 rounded-lg border border-line bg-paper px-3 py-2 text-sm normal-case tracking-normal text-ink outline-none focus:border-gold"
      />
      {hint ? (
        <span className="mt-1 block text-[11px] font-normal normal-case tracking-normal text-muted">
          {hint}
        </span>
      ) : null}
    </label>
  );
}

export function FormAlert({
  tone,
  text,
}: {
  tone: "ok" | "error";
  text: string;
}) {
  return (
    <p
      role={tone === "error" ? "alert" : "status"}
      className={`rounded-xl border px-4 py-3 text-sm ${
        tone === "error"
          ? "border-gold-deep/40 bg-blush text-gold-deep"
          : "border-ink/10 bg-ink text-paper"
      }`}
    >
      {text}
    </p>
  );
}
