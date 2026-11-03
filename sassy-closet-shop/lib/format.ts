export function formatUsd(amount: number): string {
  if (!Number.isFinite(amount)) {
    throw new Error("Invalid USD amount");
  }
  if (Number.isInteger(amount)) {
    return `$${amount}`;
  }
  return `$${amount.toFixed(2)}`;
}
