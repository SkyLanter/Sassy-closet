import { assertNever } from "./kinds";
import { normalizeMa } from "./mint";
import { ON_HAND_STATUSES, type OnHandRow, type OnHandStatus } from "./types";

export const STAGED_ONLY_MESSAGE = "Staged only — not on Square On_Hand yet";

export function normalizeFindCode(raw: string): string {
  return normalizeMa(raw.trim());
}

export function photoFolder(ma: string): string {
  const code = normalizeFindCode(ma);
  return code ? `Documents/Sassy Closet/Photos/${code}/` : "";
}

export function dashIfEmpty(value: string | number | null | undefined): string {
  if (value === null || value === undefined) return "—";
  const text = String(value).trim();
  return text === "" ? "—" : text;
}

export function moneyLine(usd: string, cny: string): string {
  const u = usd.trim();
  const c = cny.trim();
  if (u && c) return `$${u} · ¥${c}`;
  if (u) return `$${u}`;
  if (c) return `¥${c}`;
  return "—";
}

export function onHandStatusLabel(status: OnHandStatus | ""): string {
  switch (status) {
    case "on_hand":
      return "on_hand";
    case "reserved":
      return "reserved";
    case "sold":
      return "sold";
    case "dead":
      return "dead";
    case "":
      return "—";
    default: {
      const _never: never = status;
      return assertNever(_never, "Unknown on-hand status");
    }
  }
}

export function sanitizeOnHandRows(raw: unknown, ma: string): OnHandRow[] {
  if (!Array.isArray(raw)) return [];
  const where = photoFolder(ma);
  const rows: OnHandRow[] = [];
  for (const item of raw) {
    if (!item || typeof item !== "object") continue;
    const rec = item as Record<string, unknown>;
    rows.push({
      size: readTrimmed(rec.size),
      color: readTrimmed(rec.color),
      qty_on_hand: parseQty(rec.qty_on_hand ?? rec.qty),
      status: parseStatus(rec.status),
      storage_location: readTrimmed(rec.storage_location ?? rec.storage),
      notes: readTrimmed(rec.notes),
      where_stored: where,
    });
  }
  return rows;
}

function readTrimmed(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

function parseQty(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim() !== "") {
    const n = Number(value);
    if (Number.isFinite(n)) return n;
  }
  return null;
}

function parseStatus(value: unknown): OnHandStatus | "" {
  if (typeof value !== "string") return "";
  const status = value.trim().toLowerCase();
  return (ON_HAND_STATUSES as readonly string[]).includes(status)
    ? (status as OnHandStatus)
    : "";
}
