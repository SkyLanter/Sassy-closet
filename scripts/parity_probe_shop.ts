/**
 * Read-only shop facts for scripts/parity_check.py.
 * Reads stdin JSON, writes one JSON object to stdout. No catalog writes.
 */
import { readFileSync } from "node:fs";

import {
  ASIA_SIZE_LETTERS,
  EU_SHOE_SIZES,
  parseAsiaSizes,
} from "../sassy-closet-shop/lib/asia-size";
import { MA_LETTERS, canonicalMaSpelling, normalizeMa } from "../sassy-closet-shop/lib/ma";
import { intakeToPrefill, type IntakeSubmission } from "../sassy-closet-shop/lib/intake-import";
import { calcPricing, deboxForLetter, sellUsdFromLanded } from "../sassy-closet-shop/lib/pricing";

type ProbeRequest = {
  mas: (string | null)[];
  landed: string[];
  aliasTokens: string[];
  shoeTokens: string[];
  letters: string[];
  dualCost: {
    kind: string;
    costCny: string;
    costUsd: string;
    fx: string;
  };
  importSizes: {
    shoe: string;
    clothing: string;
    edge: string;
    kindO: string;
  };
};

function sizedSubmission(kind: string, size: string): IntakeSubmission {
  return {
    id: 0,
    ma: `${kind}01`,
    kind,
    size,
    color: "",
    color_note: "",
    pieces: [],
    link: "",
    price: "",
    cost_cny: "",
    cost_usd: "",
    cost_currency: "",
    sell_cny: "",
    sell_usd: "",
    sell_currency: "",
    blurb: "",
    photo_paths: [],
    photo_hashes: [],
    status: "staged",
    square: "",
    created_at: "",
    updated_at: "",
    caption_vi: "",
    caption_en: "",
    blurb_suggested: "",
    photo_link: "",
  };
}

function readRequest(): ProbeRequest {
  const payload: unknown = JSON.parse(readFileSync(0, "utf8"));
  if (typeof payload !== "object" || payload === null) {
    throw new Error("probe request must be an object");
  }
  return payload as ProbeRequest;
}

function spell(mas: (string | null)[], fn: (value: string) => string): Record<string, string> {
  const out: Record<string, string> = {};
  mas.forEach((raw, index) => {
    out[String(index)] = fn(raw ?? "");
  });
  return out;
}

function main(): void {
  const request = readRequest();
  const flat: Record<string, number | null> = {};
  for (const text of request.landed) {
    const landed = Number(text);
    flat[text] = Number.isFinite(landed) && landed > 0 ? sellUsdFromLanded(landed) : null;
  }
  const shoeParsed: Record<string, string[]> = {};
  for (const token of request.shoeTokens) {
    shoeParsed[token] = parseAsiaSizes([token]);
  }
  const debox: Record<string, number | null> = {};
  for (const letter of request.letters) {
    debox[letter] = deboxForLetter(letter);
  }
  const dual = request.dualCost;
  const priced = calcPricing({
    costCny: Number(dual.costCny),
    costUsd: Number(dual.costUsd),
    fx: Number(dual.fx),
    deboxUsd: deboxForLetter(dual.kind),
  });
  const body = {
    kindLetters: [...MA_LETTERS],
    clothing: [...ASIA_SIZE_LETTERS],
    shoe: [...EU_SHOE_SIZES],
    canonicalMaSpelling: spell(request.mas, canonicalMaSpelling),
    normalizeMa: spell(request.mas, normalizeMa),
    aliasParsed: parseAsiaSizes(request.aliasTokens),
    shoeParsed,
    flat,
    debox,
    dualShopLanded: priced.landedUsd,
    importShoe: intakeToPrefill(sizedSubmission("G", request.importSizes.shoe)).sizes,
    importClothing: intakeToPrefill(sizedSubmission("A", request.importSizes.clothing)).sizes,
    importEdge: intakeToPrefill(sizedSubmission("G", request.importSizes.edge)).sizes,
    importKindO: intakeToPrefill(sizedSubmission("O", request.importSizes.kindO)).sizes,
  };
  process.stdout.write(`${JSON.stringify(body)}\n`);
}

main();
