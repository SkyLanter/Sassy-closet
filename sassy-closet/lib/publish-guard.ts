/**
 * Fixture-checked blocks for save, mint, and sync.
 * This module does not write intake, Blob, or data/held.json.
 */
import type { KindCode } from "./kinds";
import { isHeldIncompleteMa, NEVER_LIST_MAS } from "./held-incomplete";
import { nextMa } from "./mint";

export type PublishAction = "create" | "update" | "mint" | "sync";

export type PublishIntent = {
  action: PublishAction;
  ma: string;
  sellUsd?: string | null;
  reused?: boolean;
  duplicate?: boolean;
};

const NEVER_LIST = new Set(NEVER_LIST_MAS.map((ma) => ma.toUpperCase()));
const S06 = "S06";

export function publishBlock(intent: PublishIntent): string | null {
  knownAction(intent.action);
  const ma = intent.ma.trim().toUpperCase();
  if (intent.duplicate || intent.reused) {
    return intent.reused ? "reused" : "duplicate";
  }
  if (NEVER_LIST.has(ma)) return "never-list";
  if (isHeldIncompleteMa(ma)) return "held";
  if (ma === S06) {
    const sell = wholeDollars(intent.sellUsd);
    if (sell !== null && sell !== 25) return "s06-lock";
  }
  return null;
}

export function wholeDollars(raw: string | null | undefined): number | null {
  if (raw == null) return null;
  const text = raw.trim().replace(/^\$/, "").replace(/,/g, "");
  if (text === "") return null;
  if (!/^\d+(?:\.\d+)?$/.test(text)) return Number.NaN;
  const value = Number(text);
  if (!Number.isFinite(value) || value !== Math.trunc(value)) return Number.NaN;
  return value;
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
