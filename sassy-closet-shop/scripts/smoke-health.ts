const SHOP = process.env.SHOP_ORIGIN ?? "http://127.0.0.1:43147";

async function main(): Promise<void> {
  const response = await fetch(`${SHOP}/api/health`, { cache: "no-store" });
  const body = (await response.json()) as {
    ok: boolean;
    schema: string;
    backend: string;
    missingKnown: string[];
    knownMas: string[];
    blob?: { configured: boolean; prefix: string; path: string };
    dropship?: number;
    sourceLinks?: number;
    hubMessageReady?: number;
  };
  if (response.status !== 200 || !body.ok) {
    throw new Error(`health ${response.status} ok=${String(body.ok)} missing=${body.missingKnown?.join(",")}`);
  }
  if (body.schema !== "catalog.v1") {
    throw new Error(`health schema ${body.schema}`);
  }
  if (!body.knownMas?.includes("A01") || body.missingKnown?.length) {
    throw new Error("health missing known mãs");
  }
  if (!body.blob || !body.blob.path.endsWith("catalog.v1.json") || !body.blob.prefix.endsWith("/")) {
    throw new Error("health missing Blob prefix/path");
  }
  if (typeof body.dropship !== "number" || typeof body.sourceLinks !== "number") {
    throw new Error("health missing dropship counts");
  }
  if (body.hubMessageReady !== 10) {
    throw new Error(`health hub Message-ready must be 10, got ${String(body.hubMessageReady)}`);
  }
  console.log("health ok", { backend: body.backend, schema: body.schema, blob: body.blob.path });
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});
