import { randomUUID } from "node:crypto";
import { localAskAnswer } from "./ask-fallback";
import type { AskRecord } from "./types";

const ASK_TIMEOUT_MS = 45_000;

const globalAsk = globalThis as typeof globalThis & {
  __sassyAsks?: Map<string, AskRecord>;
};

function asks(): Map<string, AskRecord> {
  if (!globalAsk.__sassyAsks) globalAsk.__sassyAsks = new Map();
  return globalAsk.__sassyAsks;
}

export function webhookConfigured(): boolean {
  return Boolean(
    process.env.MINIBOSS_ASK_WEBHOOK_URL?.trim() &&
      process.env.MINIBOSS_ASK_WEBHOOK_KEY?.trim(),
  );
}

export function createAsk(question: string): AskRecord {
  const now = new Date().toISOString();
  const trimmed = question.trim();
  if (!trimmed) {
    throw Object.assign(new Error("Gõ câu hỏi nha."), { status: 400 });
  }
  const record: AskRecord = {
    id: randomUUID(),
    question: trimmed,
    status: "waiting",
    answer: "",
    copies: [],
    source: "relay",
    offline: false,
    created_at: now,
    updated_at: now,
  };
  asks().set(record.id, record);
  return record;
}

export function getAsk(id: string): AskRecord | null {
  const record = asks().get(id);
  if (!record) return null;
  if (record.status === "waiting" && isTimedOut(record)) {
    applyLocalFallback(record);
  }
  return record;
}

export function applyLocalFallback(record: AskRecord): AskRecord {
  const local = localAskAnswer(record.question);
  record.status = "ready";
  record.answer = local.reply;
  record.copies = local.copies;
  record.source = "local";
  record.offline = true;
  record.updated_at = new Date().toISOString();
  asks().set(record.id, record);
  return record;
}

export function replyAsk(id: string, answer: string): AskRecord {
  const record = asks().get(id);
  if (!record) {
    throw Object.assign(new Error("Ask id không có."), { status: 404 });
  }
  const text = answer.trim();
  if (!text) {
    throw Object.assign(new Error("answer trống."), { status: 400 });
  }
  record.status = "ready";
  record.answer = text;
  record.copies = [];
  record.source = "relay";
  record.offline = false;
  record.updated_at = new Date().toISOString();
  asks().set(record.id, record);
  return record;
}

export function publicAsk(record: AskRecord): {
  id: string;
  status: AskRecord["status"];
  question: string;
  answer?: string;
  copies?: AskRecord["copies"];
  source?: AskRecord["source"];
  offline?: boolean;
} {
  const body: ReturnType<typeof publicAsk> = {
    id: record.id,
    status: record.status,
    question: record.question,
  };
  if (record.status === "ready") {
    body.answer = record.answer;
    body.copies = record.copies;
    body.source = record.source;
    body.offline = record.offline;
  }
  return body;
}

export async function notifyWebhook(record: AskRecord): Promise<boolean> {
  const url = process.env.MINIBOSS_ASK_WEBHOOK_URL?.trim();
  const key = process.env.MINIBOSS_ASK_WEBHOOK_KEY?.trim();
  if (!url || !key) return false;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      authorization: `Bearer ${key}`,
      "x-miniboss-ask-key": key,
    },
    body: JSON.stringify({ id: record.id, question: record.question }),
  });
  return response.ok;
}

export function readReplySecret(request: Request, body: { secret?: string }): string {
  const header =
    request.headers.get("x-ask-reply-secret") ||
    request.headers.get("authorization")?.replace(/^Bearer\s+/i, "") ||
    "";
  return (body.secret || header).trim();
}

export function replySecretOk(provided: string): boolean {
  const expected = process.env.ASK_REPLY_SECRET?.trim();
  if (!expected) return false;
  return provided === expected;
}

function isTimedOut(record: AskRecord): boolean {
  const started = Date.parse(record.created_at);
  if (!Number.isFinite(started)) return false;
  return Date.now() - started >= ASK_TIMEOUT_MS;
}
