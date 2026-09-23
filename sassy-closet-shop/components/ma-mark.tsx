export const MA_MARK_CLASS =
  "ma-mark font-sans font-medium uppercase tabular-nums tracking-[0.12em]";

export function MaMark({
  ma,
  className,
}: {
  ma: string;
  className?: string;
}) {
  return <span className={[MA_MARK_CLASS, className].filter(Boolean).join(" ")} translate="no">{ma}</span>;
}
