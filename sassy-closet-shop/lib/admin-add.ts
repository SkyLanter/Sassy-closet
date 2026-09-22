import type { ProductFieldsInput } from "@/lib/admin-ops";
import { emptyFitCm } from "@/lib/asia-size";
import { TYPE_LABELS } from "@/lib/catalog";
import { MA_LETTERS, type MaLetter } from "@/lib/ma";

export function isAddLetter(value: string): value is MaLetter {
  return (MA_LETTERS as readonly string[]).includes(value);
}

/** Hold + Message-first starter. Assigned mã comes from Add Save — never a trap tile. */
export function messageReadyAddFields(letter: MaLetter): ProductFieldsInput {
  const labels = TYPE_LABELS[letter];
  return {
    titleEn: labels.en,
    titleVn: labels.vn,
    descriptionEn: "",
    descriptionVn: "",
    status: "hold" as const,
    priceUsd: null,
    colors: [],
    images: [],
    sizes: [],
    fitCm: emptyFitCm(),
    fulfillment: "dropship",
    sourceLink: null,
  };
}

export function mergeAddFields(
  letter: MaLetter,
  patch: Partial<ProductFieldsInput>,
): ProductFieldsInput {
  const starter = messageReadyAddFields(letter);
  return {
    ...starter,
    ...patch,
    titleEn: (patch.titleEn ?? starter.titleEn).trim() || starter.titleEn,
    titleVn: (patch.titleVn ?? starter.titleVn).trim() || starter.titleVn,
    descriptionEn: (patch.descriptionEn ?? starter.descriptionEn).trim() || starter.descriptionEn,
    descriptionVn: (patch.descriptionVn ?? starter.descriptionVn).trim() || starter.descriptionVn,
    status: patch.status ?? starter.status,
    priceUsd: patch.priceUsd === undefined ? starter.priceUsd : patch.priceUsd,
    colors: patch.colors ?? starter.colors,
    images: patch.images ?? starter.images,
    sizes: patch.sizes ?? starter.sizes,
    fitCm: patch.fitCm ?? starter.fitCm,
    fulfillment: patch.fulfillment ?? starter.fulfillment,
    sourceLink: patch.sourceLink === undefined ? starter.sourceLink : patch.sourceLink,
  };
}
