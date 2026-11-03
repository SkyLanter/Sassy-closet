export function FulfillLine({
  className,
}: {
  className?: string;
}) {
  return (
    <div className={className} data-testid="shop-fulfill-line">
      <p className="text-sm text-muted">Message on Messenger.</p>
    </div>
  );
}
