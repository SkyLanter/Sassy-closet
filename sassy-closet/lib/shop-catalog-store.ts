import { readFile, writeFile } from "node:fs/promises";
import { get, put } from "@vercel/blob";
import {
  SHOP_CATALOG_BLOB_PATH,
  listShopCatalog,
  type ShopCatalogList,
  type ShopCatalogPort,
} from "@/lib/shop-catalog";

function isMissingFile(error: unknown): boolean {
  return typeof error === "object" && error !== null && "code" in error && error.code === "ENOENT";
}

export function createFileShopCatalogPort(filePath: string): ShopCatalogPort {
  return {
    async read() {
      try {
        const text = await readFile(filePath, "utf8");
        return JSON.parse(text) as unknown;
      } catch (error) {
        if (isMissingFile(error)) {
          return null;
        }
        throw error;
      }
    },
    async write(body) {
      await writeFile(filePath, body, "utf8");
      return { url: `file://${filePath}` };
    },
  };
}

/**
 * Uses SHOP_BLOB_READ_WRITE_TOKEN only. The SDK `token` option wins over the
 * intake project's BLOB_READ_WRITE_TOKEN / BLOB_STORE_ID, so this writes the
 * shop store at sassy-closet-shop/catalog.v1.json.
 */
export function createVercelShopCatalogPort(token: string): ShopCatalogPort {
  return {
    async read() {
      try {
        const result = await get(SHOP_CATALOG_BLOB_PATH, {
          access: "public",
          token,
          useCache: false,
        });
        if (!result || result.statusCode !== 200 || !result.stream) {
          return null;
        }
        const text = await new Response(result.stream).text();
        return JSON.parse(text) as unknown;
      } catch (error) {
        const status =
          typeof error === "object" && error !== null && "statusCode" in error
            ? Number(error.statusCode)
            : 0;
        if (status === 404) {
          return null;
        }
        throw error;
      }
    },
    async write(body) {
      const blob = await put(SHOP_CATALOG_BLOB_PATH, body, {
        access: "public",
        token,
        addRandomSuffix: false,
        allowOverwrite: true,
        contentType: "application/json",
        cacheControlMaxAge: 0,
      });
      if (!blob.url) {
        throw new Error("Blob put returned no URL");
      }
      return { url: blob.url };
    },
  };
}

export function shopCatalogPortFromEnv(): { ok: true; port: ShopCatalogPort } | { ok: false; error: string } {
  const token = process.env.SHOP_BLOB_READ_WRITE_TOKEN?.trim() ?? "";
  if (token) {
    return { ok: true, port: createVercelShopCatalogPort(token) };
  }
  if (process.env.VERCEL === "1") {
    return { ok: false, error: "Shop catalog storage is not configured." };
  }
  const file = process.env.SHOP_CATALOG_FILE?.trim() ?? "";
  if (file) {
    return { ok: true, port: createFileShopCatalogPort(file) };
  }
  return { ok: false, error: "Shop catalog storage is not configured." };
}

export async function loadShopCatalogForAdmin(): Promise<ShopCatalogList> {
  const selected = shopCatalogPortFromEnv();
  if (!selected.ok) {
    return selected;
  }
  const document = await selected.port.read();
  if (document === null) {
    return { ok: false, error: "Shop catalog is missing." };
  }
  return listShopCatalog(document);
}
