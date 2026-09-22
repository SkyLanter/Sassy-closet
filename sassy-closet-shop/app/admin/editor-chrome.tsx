import type { ReactNode } from "react";

export function EditorCard({
  id,
  eyebrow,
  title,
  hint,
  children,
}: {
  id: string;
  eyebrow?: string;
  title: string;
  hint?: string;
  children: ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-28 rounded-2xl border border-line p-4 sm:p-6">
      {eyebrow ? (
        <p className="text-[10px] uppercase tracking-[0.16em] text-gold-deep">{eyebrow}</p>
      ) : null}
      <h3 className="text-xs uppercase tracking-[0.14em] text-muted">{title}</h3>
      {hint ? <p className="mt-1 max-w-2xl text-sm text-muted">{hint}</p> : null}
      <div className="mt-4 space-y-4">{children}</div>
    </section>
  );
}

export function EditorSectionNav({
  items,
}: {
  items: Array<{ id: string; label: string }>;
}) {
  return (
    <nav
      aria-label="Item sections"
      className="flex gap-4 overflow-x-auto border-b border-line pb-3 text-[11px] font-medium uppercase tracking-[0.16em]"
    >
      {items.map((item) => (
        <a key={item.id} href={`#${item.id}`} className="shrink-0 text-muted hover:text-ink">
          {item.label}
        </a>
      ))}
    </nav>
  );
}
