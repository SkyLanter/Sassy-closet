import { isKnownSeedMa, type KnownSeedMa } from "@/lib/catalog-contract";
import { normalizeMa } from "@/lib/ma";
import { parseSourceLink } from "@/lib/source-link";
import type { Product } from "@/lib/types";

/**
 * Staff Taobao URLs copied read-only from the hub All sheet.
 * Do not invent a link. Do not write Excel / OneDrive / intake.
 * Customer surfaces must strip `sourceLink` (see `shopSafeProduct`).
 */
export const HUB_SOURCE_LINKS = {
  A01: "https://e.tb.cn/h.8KCQeaHH3dz1iSl?tk=WeuOTTBXHOu",
  S01: "https://e.tb.cn/h.8KBBS0G8a3NQqtg?tk=YcEnTTALzCr",
  P01: "https://e.tb.cn/h.8LUkbrVGhE4Yurr?tk=RYgXTTzkt8b",
  P02: "https://e.tb.cn/h.8KU3zzXBR4OB9me?tk=kcDJT6G7z4p",
  P03: "https://e.tb.cn/h.8KKzBinMRDOZhNO?tk=nf9vThVDZ31",
  P04: "https://e.tb.cn/h.8LYfu0T52xNPoOD?tk=sfeoT6uLsAa",
  P05: "https://e.tb.cn/h.8pbIxrTW0mbK1Wk?tk=oDgIT6GKXrw",
  K01: "https://e.tb.cn/h.8LLjHT2R8bUOvIz?tk=cgigThRIuvf",
  H01: "https://e.tb.cn/h.8KE7trcDe92yo2O?tk=fkqzThRw8Yn",
  A02: "https://e.tb.cn/h.8JSyU68ajHWyf52?tk=rSynThj54Ks",
} as const satisfies Record<KnownSeedMa, string>;

/** Hub All sheet has no size column — do not invent Asia letters. */
export const HUB_RECORDED_SIZES: Readonly<Record<KnownSeedMa, readonly string[]>> = {
  A01: [],
  S01: [],
  P01: [],
  P02: [],
  P03: [],
  P04: [],
  P05: [],
  K01: [],
  H01: [],
  A02: [],
};

export function recordedHubSourceLink(ma: string): string | null {
  const key = normalizeMa(ma);
  if (!isKnownSeedMa(key)) {
    return null;
  }
  return parseSourceLink(HUB_SOURCE_LINKS[key], key);
}

/** Fill a missing staff link from the recorded hub copy. Never mint A03+. */
export function applyRecordedHubSourceLink(product: Product): Product {
  if (product.sourceLink) {
    return product;
  }
  const recorded = recordedHubSourceLink(product.ma);
  if (!recorded) {
    return product;
  }
  return { ...product, sourceLink: recorded };
}
