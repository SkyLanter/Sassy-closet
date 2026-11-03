export type SaveReceiptView = {
  ok: true;
  blobWritten: true;
  catalogSha: string;
  updatedAt: string;
  revalidated: string[];
  ma?: string;
  renamedTo?: string;
};

export function isCompleteSaveReceipt(result: unknown): result is SaveReceiptView {
  if (typeof result !== "object" || result === null) {
    return false;
  }
  const row = result as Record<string, unknown>;
  return (
    row.ok === true &&
    row.blobWritten === true &&
    typeof row.catalogSha === "string" &&
    row.catalogSha.length >= 8 &&
    typeof row.updatedAt === "string" &&
    row.updatedAt.length >= 8 &&
    Array.isArray(row.revalidated) &&
    row.revalidated.length > 0
  );
}

export function silentSaveError(): string {
  return "Save did not return a Blob + revalidate receipt. The shop may still be stale.";
}

export function saveReceiptLine(result: SaveReceiptView): string {
  return `sha ${result.catalogSha.slice(0, 12)}`;
}

/** Import / settings Save must drop shop home and hub A01, not only an admin path. */
export function receiptRevalidatedShop(result: SaveReceiptView): boolean {
  return result.revalidated.includes("/") && result.revalidated.includes("/m/A01");
}
