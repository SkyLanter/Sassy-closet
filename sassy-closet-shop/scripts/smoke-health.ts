const SHOP = process.env.SHOP_ORIGIN ?? "http://127.0.0.1:43147";

async function main(): Promise<void> {
  const response = await fetch(`${SHOP}/api/health`, { cache: "no-store" });
  const body = (await response.json()) as {
    ok: boolean;
    schema: string;
    reading?: string;
    missingKnown: string[];
    knownMas: string[];
    blob?: { configured?: boolean; readable?: boolean; path?: string; prefix?: string; listed?: unknown };
    hubMessageReady?: number;
  };
  if (response.status !== 200 || !body.ok) {
    throw new Error(`health ${response.status} ok=${String(body.ok)} missing=${body.missingKnown?.join(",")}`);
  }
  if (body.schema !== "catalog.v1") {
    throw new Error(`health schema ${body.schema}`);
  }
  if (body.reading !== "blob" && body.reading !== "kv" && body.reading !== "local" && body.reading !== "seed") {
    throw new Error(`health reading ${String(body.reading)}`);
  }
  if (!body.knownMas?.includes("A01") || body.missingKnown?.length) {
    throw new Error("health missing known mãs");
  }
  if (!body.blob || typeof body.blob.configured !== "boolean" || typeof body.blob.readable !== "boolean") {
    throw new Error("health blob flags missing");
  }
  if ("path" in body.blob || "prefix" in body.blob || "listed" in body.blob) {
    throw new Error("health leaked blob layout");
  }
  const robots = response.headers.get("x-robots-tag") ?? "";
  if (!/noindex,\s*nofollow,\s*nosnippet/i.test(robots)) {
    throw new Error("health missing noindex");
  }
  if (body.hubMessageReady !== 10) {
    throw new Error(`health hub Message-ready must be 10, got ${String(body.hubMessageReady)}`);
  }
  console.log("health ok", { schema: body.schema, reading: body.reading, readable: body.blob.readable });
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});
