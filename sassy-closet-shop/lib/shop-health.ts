import { PRIVATE_ROBOTS_TAG } from "@/lib/private-robots";
import type { CatalogBackend } from "@/lib/storage-info";

export const SHOP_HEALTH_HEADERS = {
  "Cache-Control": "private, no-store, no-cache, max-age=0, must-revalidate",
  "X-Robots-Tag": PRIVATE_ROBOTS_TAG,
} as const;

export type PublicShopHealth = {
  ok: boolean;
  schema: string;
  reading: CatalogBackend;
  blob: {
    configured: boolean;
    readable: boolean;
  };
  productCount: number;
  shopVisible: number;
  hubMessageReady: number;
  missingKnown: string[];
  knownMas: string[];
};

export type ShopHealthErrorBody = {
  ok: false;
  error: "Catalog read failed";
  corrupt: boolean;
};

/**
 * Public health JSON. `reading` is blob, kv, local, or seed.
 * Blob object paths, tokens, costs, and shop links stay off this body.
 */
export function publicShopHealth(input: {
  ok: boolean;
  schema: string;
  reading: CatalogBackend;
  blobConfigured: boolean;
  blobReadable: boolean;
  productCount: number;
  shopVisible: number;
  hubMessageReady: number;
  missingKnown: readonly string[];
  knownMas: readonly string[];
}): PublicShopHealth {
  return {
    ok: input.ok,
    schema: input.schema,
    reading: input.reading,
    blob: {
      configured: input.blobConfigured,
      readable: input.blobReadable,
    },
    productCount: input.productCount,
    shopVisible: input.shopVisible,
    hubMessageReady: input.hubMessageReady,
    missingKnown: [...input.missingKnown],
    knownMas: [...input.knownMas],
  };
}

/** Fixed text. Caller errors can carry tokens and are not copied here. */
export function shopHealthError(corrupt: boolean): ShopHealthErrorBody {
  return { ok: false, error: "Catalog read failed", corrupt };
}
