/**
 * Fixture-checked blocks for save, mint, and sync.
 * This module does not write intake, Blob, or data/held.json.
 */
import type { KindCode } from "./kinds";
import { isHeldIncompleteMa, NEVER_LIST_MAS } from "./held-incomplete";
import { readMoney } from "./money-text";
import { nextMa, normalizeMa } from "./mint";

export type PublishAction = "create" | "update" | "mint" | "sync";

export type PublishIntent = {
  action: PublishAction;
  ma: string;
  sellUsd?: string | null;
  sellCurrency?: string | null;
  reused?: boolean;
  duplicate?: boolean;
};

const NEVER_LIST = new Set(NEVER_LIST_MAS.map((ma) => normalizeMa(ma)));
const S06 = "S06";

export function publishBlock(intent: PublishIntent): string | null {
  knownAction(intent.action);
  // Canonical padding too, so "S006" cannot dodge the S06 / held / never-list blocks.
  const ma = normalizeMa(intent.ma);
  if (intent.duplicate || intent.reused) {
    return intent.reused ? "reused" : "duplicate";
  }
  if (NEVER_LIST.has(ma)) return "never-list";
  if (isHeldIncompleteMa(ma)) return "held";
  if (ma === S06) {
    const currency = (intent.sellCurrency ?? "").trim().toUpperCase();
    if (currency === "CNY") return "s06-lock";
    const sell = wholeDollars(intent.sellUsd);
    if (sell !== null && sell !== 25) return "s06-lock";
  }
  return null;
}

export function wholeDollars(raw: string | null | undefined): number | null {
  if (raw == null) return null;
  // A comma is a thousands group. The first group starts at 1–999, so 0,025 is not $25.
  if (hasBadThousandsGroup(raw)) return Number.NaN;
  const parsed = readMoney(raw, "USD");
  if (parsed.kind === "blank") return null;
  if (parsed.kind !== "amount") return Number.NaN;
  if (!Number.isFinite(parsed.value) || parsed.value !== Math.trunc(parsed.value)) return Number.NaN;
  return parsed.value;
}

const REAL_THOUSANDS = /^[1-9]\d{0,2}(?:,\d{3})+(?:\.\d+)?$/;

function hasBadThousandsGroup(raw: string): boolean {
  let body = usdBody(raw);
  if (body.endsWith(".")) body = body.slice(0, -1);
  if (!body.includes(",")) return false;
  return !REAL_THOUSANDS.test(body);
}

function usdBody(raw: string): string {
  let text = raw.replaceAll("\uFEFF", "").trim();
  text = text
    .replace(/[\uFF10-\uFF19]/g, (digit) => String.fromCharCode(digit.charCodeAt(0) - 0xff10 + 0x30))
    .replace(/[\uFF0E\u3002]/g, ".")
    .replace(/\uFF0C/g, ",");
  const lead = /^(?:\$|usd)\s*/i.exec(text);
  if (lead && lead[0].length > 0) return text.slice(lead[0].length);
  const trail = /\s*(?:\$|usd)$/i.exec(text);
  if (trail && trail[0].length > 0) return text.slice(0, -trail[0].length);
  return text;
}

export function mintBlock(kind: KindCode, existing: readonly string[]): string | null {
  return publishBlock({ action: "mint", ma: nextMa(kind, [...existing]) });
}

function knownAction(action: PublishAction): void {
  switch (action) {
    case "create":
    case "update":
    case "mint":
    case "sync":
      return;
    default: {
      const neverAction: never = action;
      throw new Error(`unknown publish action ${String(neverAction)}`);
    }
  }
}
