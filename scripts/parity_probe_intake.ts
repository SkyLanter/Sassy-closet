/**
 * Read-only facts for scripts/parity_check.py.
 * Reads stdin JSON, writes one JSON object to stdout. No catalog writes.
 */
import { readFileSync } from "node:fs";

import { canonicalHeldKey } from "../sassy-closet/lib/held-incomplete";
import {
  CLOTHING_SIZES,
  KIND_CODES,
  SHOE_SIZES,
  isKindCode,
  keepSizesForKind,
  sizesForKind,
} from "../sassy-closet/lib/kinds";
import { normalizeMa } from "../sassy-closet/lib/mint";
import {
  captionPriceLine,
  deboxFor,
  intakePriceView,
  landedUsdFromCosts,
  sellPriceFlag,
  sellUsdFromLanded,
  tieredMarginForSell,
  tieredSellUsd,
} from "../sassy-closet/lib/pricing";
import {
  canonicalQuoteMa,
  lockedDeboxUsd,
  marginForSell,
  tieredSellUsd as sharedTieredSellUsd,
  wouldBeLiveUsd,
} from "../shared/tiered-pricing";

type ProbeRequest = {
  mas: (string | null)[];
  landed: string[];
  sells: number[];
  aliasTokens: string[];
  shoeTokens: string[];
  currencyCase: {
    ma: string;
    kind: string;
    liveUsd: number;
    costCny: string;
    costUsd: string;
    fx: string;
  };
  captionCase: {
    ma: string;
    kind: string;
    sellUsd: string;
    costCny: string;
    costUsd: string;
    fx: string;
  };
  deboxCase: {
    ma: string;
    kind: string;
    liveUsd: number;
    costCny: string;
    costUsd: string;
  };
  dualCost: {
    kind: string;
    costCny: string;
    costUsd: string;
    fx: string;
  };
};

type SellInput = {
  ma: string;
  kind: string;
  sellUsd: string;
  sellCny: string;
  sellCurrency: string;
  costCny: string;
  costUsd: string;
  costCurrency: string;
  fxRate: number;
};

function readRequest(): ProbeRequest {
  const payload: unknown = JSON.parse(readFileSync(0, "utf8"));
  if (typeof payload !== "object" || payload === null) {
    throw new Error("probe request must be an object");
  }
  return payload as ProbeRequest;
}

function quoteNumber(text: string, quote: (landed: number) => number | null): number | null {
  const landed = Number(text);
  if (!Number.isFinite(landed) || landed <= 0) return null;
  return quote(landed);
}

function quoteShared(text: string): number | { error: string } {
  try {
    return sharedTieredSellUsd(text);
  } catch (error) {
    return { error: error instanceof Error ? error.message : "quote failed" };
  }
}

function spellings(mas: (string | null)[]): Record<string, string> {
  const out: Record<string, string> = {};
  mas.forEach((raw, index) => {
    out[String(index)] = normalizeMa(raw ?? "");
  });
  return out;
}

function heldSpellings(mas: (string | null)[]): Record<string, string> {
  const out: Record<string, string> = {};
  mas.forEach((raw, index) => {
    out[String(index)] = canonicalHeldKey(raw ?? "");
  });
  return out;
}

function quoteSpellings(mas: (string | null)[]): Record<string, string> {
  const out: Record<string, string> = {};
  mas.forEach((raw, index) => {
    out[String(index)] = canonicalQuoteMa(raw ?? "");
  });
  return out;
}

function captionInput(request: ProbeRequest): SellInput {
  return {
    ma: request.captionCase.ma,
    kind: request.captionCase.kind,
    sellUsd: request.captionCase.sellUsd,
    sellCny: "",
    sellCurrency: "USD",
    costCny: request.captionCase.costCny,
    costUsd: request.captionCase.costUsd,
    costCurrency: "USD",
    fxRate: Number(request.captionCase.fx),
  };
}

function sellInput(request: ProbeRequest, costCurrency: string, sellUsd: string): SellInput {
  return {
    ma: request.currencyCase.ma,
    kind: request.currencyCase.kind,
    sellUsd,
    sellCny: "",
    sellCurrency: "USD",
    costCny: request.currencyCase.costCny,
    costUsd: request.currencyCase.costUsd,
    costCurrency,
    fxRate: Number(request.currencyCase.fx),
  };
}

function wouldBe(request: ProbeRequest, costCurrency: string | null) {
  const base = {
    ma: request.currencyCase.ma,
    kind: request.currencyCase.kind,
    liveUsd: request.currencyCase.liveUsd,
    costCny: request.currencyCase.costCny,
    costUsd: request.currencyCase.costUsd,
  };
  if (costCurrency === null) return wouldBeLiveUsd(base);
  return wouldBeLiveUsd({ ...base, costCurrency });
}

function shortMa(ma: string): { ok: true; ma: string; wouldBeUsd: number } | { ok: false; error: string } {
  try {
    const row = wouldBeLiveUsd({
      ma,
      kind: ma.trim().charAt(0) || "A",
      liveUsd: 27,
      costCny: null,
      costUsd: null,
    });
    return { ok: true, ma: row.ma, wouldBeUsd: row.wouldBeUsd };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "invalid" };
  }
}

function scales(): Record<string, string[]> {
  const out: Record<string, string[]> = {};
  for (const letter of KIND_CODES) {
    out[letter] = [...sizesForKind(letter)];
  }
  return out;
}

function dualLanded(request: ProbeRequest, costCurrency: string): number | null {
  return landedUsdFromCosts({
    kind: request.dualCost.kind,
    costCny: request.dualCost.costCny,
    costUsd: request.dualCost.costUsd,
    costCurrency,
    fxRate: Number(request.dualCost.fx),
  });
}

function kept(kind: string, tokens: string[]): string[] {
  if (!isKindCode(kind)) return [];
  return keepSizesForKind(tokens, kind);
}

function main(): void {
  const request = readRequest();
  const sharedTier: Record<string, number | { error: string }> = {};
  const intakeTier: Record<string, number | null> = {};
  const flat: Record<string, number | null> = {};
  for (const text of request.landed) {
    sharedTier[text] = quoteShared(text);
    intakeTier[text] = quoteNumber(text, tieredSellUsd);
    flat[text] = quoteNumber(text, sellUsdFromLanded);
  }
  const sharedMargin: Record<string, string> = {};
  const intakeMargin: Record<string, number> = {};
  for (const sell of request.sells) {
    sharedMargin[String(sell)] = marginForSell(sell);
    intakeMargin[String(sell)] = tieredMarginForSell(sell);
  }
  const typed = captionInput(request);
  const deboxQuote = wouldBeLiveUsd({
    ma: request.deboxCase.ma,
    kind: request.deboxCase.kind,
    liveUsd: request.deboxCase.liveUsd,
    costCny: request.deboxCase.costCny,
    costUsd: request.deboxCase.costUsd,
    costCurrency: "USD",
  });
  const blankUsd = intakePriceView(sellInput(request, "USD", ""));
  const blankCny = intakePriceView(sellInput(request, "CNY", ""));
  const blankEmpty = intakePriceView(sellInput(request, "", ""));
  const deboxBlank = intakePriceView({
    ma: request.deboxCase.ma,
    kind: request.deboxCase.kind,
    sellUsd: "",
    sellCny: "",
    sellCurrency: "USD",
    costCny: request.deboxCase.costCny,
    costUsd: request.deboxCase.costUsd,
    costCurrency: "USD",
    fxRate: Number(request.currencyCase.fx),
  });
  const locked: Record<string, string> = {};
  const intakeDebox: Record<string, number> = {};
  for (const letter of KIND_CODES) {
    locked[letter] = lockedDeboxUsd(letter);
    intakeDebox[letter] = deboxFor(letter);
  }
  const body = {
    kindLetters: [...KIND_CODES],
    clothing: [...CLOTHING_SIZES],
    shoe: [...SHOE_SIZES],
    scales: scales(),
    keepG: kept("G", request.shoeTokens),
    keepO: kept("O", request.shoeTokens),
    keepOLetters: kept("O", ["M"]),
    keepGLetters: kept("G", ["M"]),
    normalizeMa: spellings(request.mas),
    canonicalHeldKey: heldSpellings(request.mas),
    canonicalQuoteMa: quoteSpellings(request.mas),
    sharedTier,
    intakeTier,
    flat,
    sharedMargin,
    intakeMargin,
    wouldBeUsd: wouldBe(request, "USD").wouldBeUsd,
    wouldBeCny: wouldBe(request, "CNY").wouldBeUsd,
    wouldBeOmitted: wouldBe(request, null).wouldBeUsd,
    wouldBeEmpty: wouldBe(request, "").wouldBeUsd,
    blankUsd: blankUsd.dollars,
    blankCny: blankCny.dollars,
    blankEmpty: blankEmpty.dollars,
    viewFlag: intakePriceView(typed).flag,
    sellFlag: sellPriceFlag(typed),
    caption: captionPriceLine(typed),
    shortA1: shortMa("A1"),
    shortS6: shortMa("s6"),
    deboxWouldBe: deboxQuote.wouldBeUsd,
    deboxBlank: deboxBlank.dollars,
    lockedDebox: locked,
    intakeDebox,
    dualUsdLanded: dualLanded(request, "USD"),
    dualCnyLanded: dualLanded(request, "CNY"),
  };
  process.stdout.write(`${JSON.stringify(body)}\n`);
}

main();
