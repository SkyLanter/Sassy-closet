import assert from "node:assert/strict";
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { emptyFitCm } from "../lib/asia-size";
import { catalogImageSrcBlocked } from "../lib/catalog-image-src";
import { invalidateLiveCatalogMemo } from "../lib/catalog-store";
import { HELD_INCOMPLETE_MAS, isOffLiveSell } from "../lib/held-incomplete";
import { maLetter } from "../lib/ma";

const HELD = HELD_INCOMPLETE_MAS[0]!;
const PADDED = `${HELD[0]}0${HELD.slice(1)}`;

/** Keep percent-encoding in the URL path. encodeURIComponent("S14") is a no-op. */
function percentFolder(folder: string): string {
  return [...folder]
    .map((char) => `%${char.charCodeAt(0).toString(16).padStart(2, "0").toUpperCase()}`)
    .join("");
}

function product(ma: string, srcs: string[]) {
  return {
    ma,
    type: maLetter(ma),
    titleVn: ma,
    titleEn: ma,
    priceUsd: 20,
    qty: 1,
    status: "available",
    colors: [],
    images: srcs.map((src) => ({ src, alt: ma })),
    sizes: [],
    fitCm: emptyFitCm(),
    descriptionVn: "",
    descriptionEn: "",
    fulfillment: "dropship",
    sourceLink: null,
  };
}

function folderFromRequest(url: string): string | null {
  const pathOnly = url.split("?")[0] ?? url;
  let decoded = pathOnly;
  try {
    decoded = decodeURIComponent(pathOnly);
  } catch {
    return null;
  }
  const match = decoded.match(/\/products\/([^/]+)(?:\/|$)/i);
  return match?.[1] ?? null;
}

test("catalog image src blocks held folders, including Blob URLs and padded spellings", () => {
  const heldUrl = `https://blob.example/products/${HELD}/cover.jpg?v=1`;
  const paddedUrl = `https://blob.example/products/${PADDED}/cover.jpg`;
  const lowerUrl = `https://blob.example/products/${HELD.toLowerCase()}/cover.jpg`;
  const encoded = `https://blob.example/products/${percentFolder(HELD)}/cover.jpg`;
  assert.equal(catalogImageSrcBlocked(heldUrl), true, heldUrl);
  assert.equal(catalogImageSrcBlocked(paddedUrl), true, paddedUrl);
  assert.equal(catalogImageSrcBlocked(lowerUrl), true, lowerUrl);
  assert.equal(catalogImageSrcBlocked(encoded), true, encoded);
  assert.equal(
    catalogImageSrcBlocked(
      `HTTPS://blob.example/sassy-closet-shop/pro\tducts/${HELD}/cover.jpg`,
    ),
    true,
  );
  assert.equal(catalogImageSrcBlocked(`/products/${HELD}/cover.jpg`), true);
  assert.equal(catalogImageSrcBlocked("https://blob.example/products/A03/cover.jpg"), false);
  assert.equal(catalogImageSrcBlocked("https://blob.example/products/A99/cover.jpg"), false);
  assert.equal(catalogImageSrcBlocked("/uploads/cover.jpg"), false);
  assert.equal(catalogImageSrcBlocked("/products/../cover.jpg"), false);
  assert.equal(catalogImageSrcBlocked(`/products/A03/../../products/${HELD}/cover.jpg`), true);
  assert.equal(catalogImageSrcBlocked(`https://blob.example/products/${HELD}`), true);
  assert.equal(catalogImageSrcBlocked("https://blob.example/products/A99/../A99/cover.jpg"), false);
  assert.equal(
    catalogImageSrcBlocked(`/products/A03/%2e%2e/%2e%2e/products/${percentFolder(HELD)}/cover.jpg`),
    true,
  );
});

test("public image route does not serve a held folder under a live mã URL", async () => {
  const hits: string[] = [];
  const bodies = new Map<string, string>([
    [`/products/${HELD}/cover.jpg`, "HELD-SECRET-BYTES"],
    [`/products/${PADDED}/cover.jpg`, "PADDED-HELD-BYTES"],
    [`/products/${HELD.toLowerCase()}/cover.jpg`, "LOWER-HELD-BYTES"],
    [`/products/${percentFolder(HELD)}/cover.jpg`, "ENCODED-HELD-BYTES"],
    ["/products/A03/cover.jpg", "OWN-HTTP-BYTES"],
    ["/products/A99/cover.jpg", "OTHER-FOLDER-BYTES"],
    ["/products/A07/cover.jpg", "SECOND-SAFE-BYTES"],
    [`/products/${HELD}/photo-1.jpg`, "HELD-PHOTO-BYTES"],
    ["/products/A09/photo-1.jpg", "PHOTO-SAFE-BYTES"],
  ]);
  const server = createServer((req: IncomingMessage, res: ServerResponse) => {
    const url = req.url ?? "/";
    hits.push(url);
    const pathOnly = url.split("?")[0] ?? url;
    if (pathOnly === "/go-held") {
      res.writeHead(302, { location: `/products/${HELD}/cover.jpg` });
      res.end();
      return;
    }
    if (pathOnly === "/go-own") {
      res.writeHead(302, { location: "/products/A03/cover.jpg" });
      res.end();
      return;
    }
    const body = bodies.get(pathOnly) ?? "UNEXPECTED";
    res.writeHead(200, { "content-type": "image/jpeg" });
    res.end(body);
  });
  await new Promise<void>((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => resolve());
  });
  const address = server.address();
  if (!address || typeof address === "string") {
    server.close();
    throw new Error("test server did not bind a port");
  }
  const origin = `http://127.0.0.1:${address.port}`;
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "shop-held-cross-"));
  const cwd = process.cwd();
  const saved: Record<string, string | undefined> = {};
  for (const key of Object.keys(process.env)) {
    if (/BLOB|KV_|VERCEL/.test(key)) {
      saved[key] = process.env[key];
      delete process.env[key];
    }
  }
  try {
    fs.mkdirSync(path.join(tmp, "data"), { recursive: true });
    fs.mkdirSync(path.join(tmp, "public", "products", "A05"), { recursive: true });
    fs.mkdirSync(path.join(tmp, "public", "products", HELD), { recursive: true });
    fs.writeFileSync(path.join(tmp, "public", "products", "A05", "cover.jpg"), "LOCAL-OWN-BYTES");
    fs.writeFileSync(path.join(tmp, "public", "products", HELD, "cover.jpg"), "HELD-DISK-BYTES");
    const heldUrl = `${origin}/products/${HELD}/cover.jpg`;
    const products = [
      product("Q02", [heldUrl]),
      product("A03", [`${origin}/products/A03/cover.jpg`]),
      product("A04", [`${origin}/products/A99/cover.jpg`]),
      product("D02", [`${origin}/products/${PADDED}/cover.jpg`]),
      product("V02", [`${origin}/products/${HELD.toLowerCase()}/cover.jpg`]),
      product("B02", [`${origin}/products/${percentFolder(HELD)}/cover.jpg`]),
      product("A07", [heldUrl, `${origin}/products/A07/cover.jpg`]),
      product("A05", [`/products/A05/cover.jpg`]),
      product("J02", [`/products/A03/../../products/${HELD}/cover.jpg`]),
      product("G02", [`${origin}/products/${HELD}`]),
      product("P06", [`${origin}/go-held`]),
      product("A06", [`${origin}/go-own`]),
      product("A08", [`${origin}/products/${HELD}/photo-1.jpg`]),
      product("A09", [`${origin}/products/${HELD}/photo-1.jpg`, `${origin}/products/A09/photo-1.jpg`]),
    ];
    fs.writeFileSync(path.join(tmp, "data", "live-catalog.json"), JSON.stringify(products));
    process.chdir(tmp);
    invalidateLiveCatalogMemo();
    const { GET } = await import("../app/products/[ma]/[file]/route");
    const callFile = (ma: string, file: string) =>
      GET(new Request(`https://example.invalid/products/${ma}/${file}`), {
        params: Promise.resolve({ ma, file }),
      });
    const call = (ma: string) => callFile(ma, "cover.jpg");

    const heldDirect = await call(HELD);
    assert.equal(heldDirect.status, 404, "held mã URL stays 404");
    assert.match(heldDirect.headers.get("cache-control") ?? "", /no-store/);

    const leaked = await call("Q02");
    assert.equal(leaked.status, 404, "live mã must not serve a held folder");
    assert.equal(await leaked.text(), "Not found");
    assert.match(leaked.headers.get("cache-control") ?? "", /no-store/);

    const padded = await call("D02");
    assert.equal(padded.status, 404, "padded held folder stays unserved");
    const lower = await call("V02");
    assert.equal(lower.status, 404, "lowercase held folder stays unserved");
    const encoded = await call("B02");
    assert.equal(encoded.status, 404, "encoded held folder stays unserved");

    const own = await call("A03");
    assert.equal(own.status, 200, "own folder URL still serves");
    assert.equal(Buffer.from(await own.arrayBuffer()).toString("utf8"), "OWN-HTTP-BYTES");

    const other = await call("A04");
    assert.equal(other.status, 200, "a non-held extra folder still serves");
    assert.equal(Buffer.from(await other.arrayBuffer()).toString("utf8"), "OTHER-FOLDER-BYTES");

    const second = await call("A07");
    assert.equal(second.status, 200, "a later safe src still serves when a held src is first");
    assert.equal(Buffer.from(await second.arrayBuffer()).toString("utf8"), "SECOND-SAFE-BYTES");

    const local = await call("A05");
    assert.equal(local.status, 200, "a local cover for the same mã still serves");
    assert.equal(Buffer.from(await local.arrayBuffer()).toString("utf8"), "LOCAL-OWN-BYTES");

    const traversed = await call("J02");
    assert.equal(traversed.status, 404, "a .. path must not read a held folder");
    assert.equal(await traversed.text(), "Not found");

    const noslash = await call("G02");
    assert.equal(noslash.status, 404, "a held folder with no trailing slash must not be fetched");

    const redirected = await call("P06");
    assert.equal(redirected.status, 404, "a redirect into a held folder must not be served");

    const redirectOwn = await call("A06");
    assert.equal(redirectOwn.status, 200, "a redirect to this shop's own folder still serves");
    assert.equal(Buffer.from(await redirectOwn.arrayBuffer()).toString("utf8"), "OWN-HTTP-BYTES");

    const heldPhoto = await callFile("A08", "photo-1.jpg");
    assert.equal(heldPhoto.status, 404, "a held photo URL must not be served");
    const safePhoto = await callFile("A09", "photo-1.jpg");
    assert.equal(safePhoto.status, 200, "a later safe photo still serves");
    assert.equal(Buffer.from(await safePhoto.arrayBuffer()).toString("utf8"), "PHOTO-SAFE-BYTES");

    const heldFetches = hits.filter((url) => {
      const folder = folderFromRequest(url);
      return folder !== null && isOffLiveSell(folder);
    });
    assert.deepEqual(heldFetches, [], `held folders were fetched: ${heldFetches.join(", ")}`);
  } finally {
    process.chdir(cwd);
    invalidateLiveCatalogMemo();
    for (const [key, value] of Object.entries(saved)) {
      if (value === undefined) {
        delete process.env[key];
      } else {
        process.env[key] = value;
      }
    }
    await new Promise<void>((resolve) => server.close(() => resolve()));
    fs.rmSync(tmp, { recursive: true, force: true });
  }
});
