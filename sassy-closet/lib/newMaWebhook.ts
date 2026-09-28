import { after } from "next/server";
import { assertNever } from "./kinds";

export const NEW_MA_WEBHOOK_TIMEOUT_MS = 3_000;

export type NewMaWebhookEvent = "create" | "update";

export type NewMaWebhookInput = {
  event: NewMaWebhookEvent;
  ma: string;
  updated_at: string;
  photo_count: number;
  /** Set only when this save renamed the mã. Omitted otherwise. */
  previous_ma?: string;
};

export type NewMaWebhookPayload = {
  event: NewMaWebhookEvent;
  ma: string;
  updated_at: string;
  source: "intake";
  photo_count: number;
  previous_ma?: string;
};

/** True only when both URL and token are set. The page receives this boolean, never the values. */
export function newMaWebhookConfigured(): boolean {
  return Boolean(readEnv("NEW_MA_WEBHOOK_URL") && readEnv("NEW_MA_WEBHOOK_TOKEN"));
}

export function buildNewMaWebhookPayload(input: NewMaWebhookInput): NewMaWebhookPayload {
  switch (input.event) {
    case "create":
    case "update":
      break;
    default:
      assertNever(input.event, "unknown new-mã webhook event");
  }
  const payload: NewMaWebhookPayload = {
    event: input.event,
    ma: input.ma,
    updated_at: input.updated_at,
    source: "intake",
    photo_count: input.photo_count,
  };
  const previous = input.previous_ma?.trim() ?? "";
  if (previous && previous !== input.ma) payload.previous_ma = previous;
  return payload;
}

/** One POST. Never throws. One try, 3s timeout, no retry. */
export async function notifyNewMaWebhook(input: NewMaWebhookInput): Promise<void> {
  const event = input.event;
  const ma = input.ma;
  try {
    switch (event) {
      case "create":
      case "update":
        break;
      default:
        assertNever(event, "unknown new-mã webhook event");
    }
    const url = readEnv("NEW_MA_WEBHOOK_URL");
    const token = readEnv("NEW_MA_WEBHOOK_TOKEN");
    if (!url || !token || !ma.trim()) return;
    if (!url.startsWith("https://")) {
      logFailure(event, ma, "skip");
      return;
    }

    const payload = buildNewMaWebhookPayload(input);
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
        "X-Automation-Key": token,
      },
      body: JSON.stringify(payload),
      redirect: "manual",
      signal: AbortSignal.timeout(NEW_MA_WEBHOOK_TIMEOUT_MS),
    });
    if (!response.ok) logFailure(event, ma, response.status);
  } catch (error) {
    logFailure(event, ma, failureStatus(error));
  }
}

/**
 * Run after a successful persist, without holding the save response.
 * `after()` schedules work once the response is flushed (Vercel waitUntil).
 * It throws outside a request (node:test calling the route directly); that
 * path falls back to a detached promise so the save still returns.
 */
export function scheduleNewMaWebhook(input: NewMaWebhookInput): void {
  try {
    after(() => notifyNewMaWebhook(input));
  } catch (error) {
    if (!isOutsideRequestScope(error)) return;
    void notifyNewMaWebhook(input).catch(() => {});
  }
}

export function scheduleNewMaWebhookFromRow(
  event: NewMaWebhookEvent,
  row: { ma: string; updated_at: string; photo_paths?: readonly string[] },
  previousMa?: string,
): void {
  scheduleNewMaWebhook({
    event,
    ma: row.ma,
    updated_at: row.updated_at,
    photo_count: row.photo_paths?.length ?? 0,
    previous_ma: previousMa,
  });
}

function readEnv(name: "NEW_MA_WEBHOOK_URL" | "NEW_MA_WEBHOOK_TOKEN"): string {
  return process.env[name]?.trim() ?? "";
}

function isOutsideRequestScope(error: unknown): boolean {
  return error instanceof Error && error.message.includes("outside a request scope");
}

function failureStatus(error: unknown): "timeout" | "network" {
  const name = error instanceof Error ? error.name : "";
  if (name === "AbortError" || name === "TimeoutError") return "timeout";
  return "network";
}

function logFailure(
  event: NewMaWebhookEvent,
  ma: string,
  status: number | "timeout" | "network" | "skip",
): void {
  console.error("[new-ma-webhook]", { event, ma, status });
}
