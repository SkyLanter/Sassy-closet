import { assertNever } from "./kinds";

export const LISTING_TEXT_CAP = 300;
export const LISTING_STATUS_TIMEOUT_MS = 2_000;
/** Badge refresh while the intake tab is visible. Hidden tabs do not poll. */
export const LISTING_STATUS_POLL_MS = 45_000;
const LISTING_NOTE_CAP = 20;
const LISTING_MA_CAP = 40;

export const LISTING_STATES = ["live", "held", "pending", "excluded", "unknown"] as const;

export type ListingState = (typeof LISTING_STATES)[number];

export type ListingNote = {
  code: string;
  vi: string;
};

export type ListingItem = {
  state: ListingState;
  priceUsd?: number;
  url?: string;
  since_run?: string;
  reasons: ListingNote[];
  todo: ListingNote[];
};

export type ListingChipTone = "ok" | "warn" | "muted";

export type ListingChip = {
  label: string;
  tone: ListingChipTone;
};

export type ListingWebView = {
  summary: string;
  href?: string;
  notes: string[];
};

export type ListingStatusClient = {
  enabled: boolean;
  items: Record<string, ListingItem>;
};

export function parseListingFile(value: unknown): Record<string, ListingItem> | null {
  if (!isRecord(value) || value.version !== 1) return null;
  return parseListingItems(value.items);
}

export function parseListingItems(value: unknown): Record<string, ListingItem> | null {
  if (!isRecord(value)) return null;
  const items: Record<string, ListingItem> = {};
  for (const [rawKey, rawItem] of Object.entries(value)) {
    const key = rawKey.trim().toUpperCase();
    if (!key || key.length > LISTING_MA_CAP) continue;
    const item = parseListingItem(rawItem);
    if (!item) continue;
    items[key] = item;
  }
  return items;
}

/** Client read of GET /api/listing-status. `enabled: false` or `error: true` means no badges. */
export function listingStatusFromApi(payload: unknown): ListingStatusClient {
  if (!isRecord(payload) || payload.enabled === false || payload.error === true) {
    return { enabled: false, items: {} };
  }
  const items = parseListingItems(payload.items);
  return { enabled: true, items: items ?? {} };
}

/** Interval while the tab is visible. Any other visibility stops the poll. */
export function listingPollIntervalMs(visibility: string): number | null {
  if (visibility === "visible") return LISTING_STATUS_POLL_MS;
  return null;
}

export function listingItemForMa(
  items: Record<string, ListingItem>,
  ma: string,
): ListingItem | undefined {
  const direct = items[ma];
  if (direct) return direct;
  const key = ma.trim().toUpperCase();
  if (!key || key === ma) return undefined;
  return items[key];
}

export function listingChip(item: ListingItem | undefined): ListingChip {
  if (!item) return { label: "Đang chờ bot", tone: "muted" };
  switch (item.state) {
    case "live": {
      const price = formatUsd(item.priceUsd);
      return { label: price ? `Live ${price}` : "Live", tone: "ok" };
    }
    case "held":
      return { label: "Held", tone: "warn" };
    case "pending":
      return { label: "Đang chờ bot", tone: "muted" };
    case "excluded":
      return { label: "Excluded", tone: "muted" };
    case "unknown":
      return { label: "Unknown", tone: "muted" };
    default:
      return assertNever(item.state, "unknown listing state");
  }
}

export function listingWebView(item: ListingItem | undefined): ListingWebView {
  if (!item) return { summary: "Đang chờ bot", notes: [] };
  switch (item.state) {
    case "live": {
      const price = formatUsd(item.priceUsd);
      return {
        summary: price ? `Live · ${price}` : "Live",
        href: item.url,
        notes: [...noteLines(item.reasons), ...noteLines(item.todo)],
      };
    }
    case "held":
      return { summary: "Held", notes: noteLines(item.reasons) };
    case "pending":
      return { summary: "Đang chờ bot", notes: noteLines(item.reasons) };
    case "excluded":
      return { summary: "Excluded", notes: noteLines(item.reasons) };
    case "unknown":
      return { summary: "Unknown", notes: noteLines(item.reasons) };
    default:
      return assertNever(item.state, "unknown listing state");
  }
}

export function formatUsd(priceUsd: number | undefined): string | null {
  if (typeof priceUsd !== "number" || !Number.isFinite(priceUsd) || priceUsd < 0) return null;
  if (Number.isInteger(priceUsd)) return `$${String(priceUsd)}`;
  return `$${priceUsd.toFixed(2)}`;
}

function parseListingItem(value: unknown): ListingItem | null {
  if (!isRecord(value)) return null;
  const state = parseState(value.state);
  if (!state) return null;
  const item: ListingItem = {
    state,
    reasons: parseNotes(value.reasons),
    todo: parseNotes(value.todo),
  };
  const price = parsePrice(value.priceUsd);
  if (price !== undefined) item.priceUsd = price;
  const url = parseHttpUrl(value.url);
  if (url) item.url = url;
  const since = capString(value.since_run);
  if (since) item.since_run = since;
  return item;
}

function parseState(value: unknown): ListingState | null {
  if (typeof value !== "string") return null;
  const normalized = value.trim().toLowerCase();
  if (!normalized) return null;
  switch (normalized) {
    case "live":
    case "held":
    case "pending":
    case "excluded":
      return normalized;
    default:
      return "unknown";
  }
}

function parsePrice(value: unknown): number | undefined {
  if (typeof value !== "number" || !Number.isFinite(value) || value < 0) return undefined;
  return value;
}

function parseHttpUrl(value: unknown): string | undefined {
  const text = capString(value);
  if (!text || !/^https?:\/\//i.test(text)) return undefined;
  return text;
}

function parseNotes(value: unknown): ListingNote[] {
  if (!Array.isArray(value)) return [];
  const notes: ListingNote[] = [];
  for (const entry of value) {
    if (!isRecord(entry)) continue;
    const vi = capString(entry.vi);
    if (!vi) continue;
    notes.push({ code: capString(entry.code) ?? "", vi });
    if (notes.length >= LISTING_NOTE_CAP) break;
  }
  return notes;
}

function noteLines(notes: ListingNote[]): string[] {
  return notes.map((note) => note.vi);
}

function capString(value: unknown): string | undefined {
  if (typeof value !== "string") return undefined;
  const trimmed = value.trim();
  if (!trimmed) return undefined;
  return trimmed.length > LISTING_TEXT_CAP ? trimmed.slice(0, LISTING_TEXT_CAP) : trimmed;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
