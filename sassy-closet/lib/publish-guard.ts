/**
 * Fixture-checked blocks for save, mint, and sync.
 * This module does not write intake, Blob, or data/held.json.
 */
import type { KindCode } from "./kinds";
import { isHeldIncompleteMa, NEVER_LIST_MAS } from "./held-incomplete";
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
  const text = wholeDollarText(raw);
  if (text == null) return null;
  if (text === "") return Number.NaN;
  const value = Number(text);
  if (!Number.isFinite(value) || value !== Math.trunc(value)) return Number.NaN;
  return value;
}

export function mintBlock(kind: KindCode, existing: readonly string[]): string | null {
  return publishBlock({ action: "mint", ma: nextMa(kind, [...existing]) });
}

const THOUSANDS = /^[1-9]\d{0,2}(?:,\d{3})+(?:\.\d+)?$/;
const PLAIN_AMOUNT = /^\d+(?:\.\d+)?$/;

/** Digits of one whole-dollar price. Blank is null. Junk is "". A thousands group starts at 1-999. */
function wholeDollarText(raw: string): string | null {
  const trimmed = raw.trim();
  if (trimmed === "") return null;
  const marks = trimmed.split("$").length - 1;
  if (marks > 1 || (marks === 1 && !trimmed.startsWith("$"))) return "";
  const body = marks === 1 ? trimmed.slice(1) : trimmed;
  if (body === "") return null;
  if (THOUSANDS.test(body)) return body.replace(/,/g, "");
  if (PLAIN_AMOUNT.test(body)) return body;
  return "";
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
