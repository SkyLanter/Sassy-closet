import { assertNever } from "./kinds";
import type { Submission } from "./types";

export const INTAKE_DATASET_SYNC_TIMEOUT_MS = 8_000;

export type IntakeDatasetSyncEvent = "create" | "update";

export type IntakeDatasetSyncPayload = {
  event: IntakeDatasetSyncEvent;
  ma: string;
  timestamp: string;
  source: "intake";
  sizes?: string[];
  colors?: string[];
  cost?: string;
  sell?: string;
  source_link?: string;
  kind?: Submission["kind"];
  photo_count?: number;
};

/**
 * Both URL and sender key are required. If either is missing the helper
 * no-ops so Authorization is never sent without a key (auth does not fail open).
 */
export function intakeDatasetSyncWebhookConfigured(): boolean {
  return Boolean(readWebhookUrl() && readWebhookKey());
}

export function buildIntakeDatasetSyncPayload(
  event: IntakeDatasetSyncEvent,
  row: Submission,
): IntakeDatasetSyncPayload {
  switch (event) {
    case "create":
    case "update":
      break;
    default:
      assertNever(event, "unknown intake dataset sync event");
  }

  const payload: IntakeDatasetSyncPayload = {
    event,
    ma: row.ma,
    timestamp: row.updated_at || new Date().toISOString(),
    source: "intake",
  };

  const sizes = splitTokens(row.size, /[\s,]+/);
  if (sizes.length) payload.sizes = sizes;

  const colors = collectColors(row);
  if (colors.length) payload.colors = colors;

  const cost = pickAmount(row.cost_currency, row.cost_usd, row.cost_cny);
  if (cost) payload.cost = cost;

  const sell =
    pickAmount(row.sell_currency, row.sell_usd, row.sell_cny) || row.price.trim();
  if (sell) payload.sell = sell;

  const sourceLink = row.link.trim();
  if (sourceLink) payload.source_link = sourceLink;

  if (row.kind) payload.kind = row.kind;

  const photoCount = row.photo_paths?.length ?? 0;
  if (photoCount > 0) payload.photo_count = photoCount;

  return payload;
}

/** POST after a successful persist. Never throws. One try, ~8s timeout, no retry. */
export async function notifyIntakeDatasetSyncWebhook(
  event: IntakeDatasetSyncEvent,
  row: Submission,
): Promise<void> {
  try {
    const url = readWebhookUrl();
    const key = readWebhookKey();
    if (!url || !key) return;

    const payload = buildIntakeDatasetSyncPayload(event, row);
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${key}`,
        "X-Automation-Key": key,
      },
      body: JSON.stringify(payload),
      signal: AbortSignal.timeout(INTAKE_DATASET_SYNC_TIMEOUT_MS),
    });
    if (!response.ok) {
      logFailure(event, row.ma, response.status);
    }
  } catch (error) {
    logFailure(event, row.ma, failureStatus(error));
  }
}

function readWebhookUrl(): string {
  return process.env.INTAKE_DATASET_SYNC_WEBHOOK_URL?.trim() ?? "";
}

function readWebhookKey(): string {
  return process.env.INTAKE_DATASET_SYNC_WEBHOOK_KEY?.trim() ?? "";
}

function splitTokens(raw: string, splitter: RegExp): string[] {
  return raw
    .split(splitter)
    .map((part) => part.trim())
    .filter(Boolean);
}

function collectColors(row: Submission): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  const add = (value: string) => {
    const trimmed = value.trim();
    if (!trimmed || seen.has(trimmed)) return;
    seen.add(trimmed);
    out.push(trimmed);
  };
  for (const part of splitTokens(row.color, /,/)) add(part);
  for (const piece of row.pieces ?? []) add(piece.color);
  return out;
}

function pickAmount(currency: string, usd: string, cny: string): string {
  const cur = currency.trim().toUpperCase();
  const usdTrim = usd.trim();
  const cnyTrim = cny.trim();
  if (cur === "CNY" && cnyTrim) return cnyTrim;
  if (cur === "USD" && usdTrim) return usdTrim;
  return usdTrim || cnyTrim;
}

function failureStatus(error: unknown): string {
  const name = error instanceof Error ? error.name : "";
  if (name === "AbortError" || name === "TimeoutError") return "timeout";
  return "network";
}

function logFailure(
  event: IntakeDatasetSyncEvent,
  ma: string,
  status: string | number,
): void {
  console.error("[intake-dataset-sync-webhook]", { event, ma, status });
}
