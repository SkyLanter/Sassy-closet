import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { emptyFitCm } from "../lib/asia-size";
import { HELD_INCOMPLETE_MAS } from "../lib/held-incomplete";
import { filterLooksByQuery } from "../lib/look-search";
import { canonicalMaSpelling, maLetter } from "../lib/ma";
import { coverSrc, ownMaImages, srcBelongsToMa } from "../lib/product-media";
import { findShopProduct } from "../lib/products";
import { productJsonLd } from "../lib/seo";
import { shopVisibleLooks, shopVisibleProducts } from "../lib/site-settings";
import type { Product, ProductImageAsset } from "../lib/types";

const held = HELD_INCOMPLETE_MAS[0]!;

function image(src: string, order: number): ProductImageAsset {
  return { src, colorId: null, order };
}

function product(ma: string, priceUsd: number, images: ProductImageAsset[] = []): Product {
  const type = maLetter(ma);
  if (type === null) {
    throw new Error(`Invalid mã ${ma}`);
  }
  return {
    ma,
    type,
    titleVn: canonicalMaSpelling(ma),
    titleEn: canonicalMaSpelling(ma),
    priceUsd,
    qty: 1,
    status: "available",
    colors: [],
    images,
    sizes: [],
    fitCm: emptyFitCm(),
    descriptionVn: "",
    descriptionEn: "",
    fulfillment: "dropship",
    sourceLink: null,
  };
}

function paddedSpelling(ma: string): string {
  const code = canonicalMaSpelling(ma);
  return `${code.slice(0, 1)}0${code.slice(1)}`;
}

function shortSpelling(ma: string): string {
  const code = canonicalMaSpelling(ma);
  return `${code.slice(0, 1)}${String(Number(code.slice(1)))}`;
}

/** Spellings canonicalMaSpelling treats as the same mã (lower, padded, short). */
function equivalentSpellings(ma: string): string[] {
  const code = canonicalMaSpelling(ma);
  const letter = code.slice(0, 1);
  const rest = code.slice(1);
  const unpadded = String(Number(rest));
  const candidates = [
    ma,
    code,
    code.toLowerCase(),
    `${letter}${unpadded}`,
    `${letter.toLowerCase()}${unpadded}`,
    paddedSpelling(code),
    `${letter.toLowerCase()}0${rest}`,
    `${letter}${unpadded.padStart(rest.length + 2, "0")}`,
  ];
  return [...new Set(candidates)].filter((spelling) => canonicalMaSpelling(spelling) === code);
}

function queriesForHeld(ma: string): string[] {
  const code = canonicalMaSpelling(ma);
  const queries = [ma, code, paddedSpelling(code)];
  if (code.endsWith("0")) {
    queries.push(shortSpelling(code));
  }
  return [...new Set(queries)];
}

function jsonLdImages(jsonLd: Record<string, unknown>): string[] {
  const imageValue = jsonLd.image;
  if (typeof imageValue === "string") {
    return [imageValue];
  }
  assert.ok(Array.isArray(imageValue));
  return imageValue.map((item) => {
    assert.equal(typeof item, "string");
    return item;
  });
}

function mentionsFolder(src: string, folder: string): boolean {
  return src.toLowerCase().includes(`/products/${folder.toLowerCase()}/`);
}

const a03Images = [
  image(`/products/${held}/cover.jpg`, 1),
  image("/uploads/a03.jpg", 2),
  image("/products/A04/cover.jpg", 3),
];

const fixtures: Product[] = [
  ...HELD_INCOMPLETE_MAS.flatMap((ma) => [
    product(ma, 40),
    product(ma.toLowerCase(), 41),
    product(paddedSpelling(ma), 42),
  ]),
  product("S06", 25, [image("/products/S06/cover.jpg", 1)]),
  product("A03", 30, a03Images),
  product("A02", 22, [image("/products/A01/cover.jpg", 1), image("/products/a01/extra.jpg", 2)]),
];

test("shopVisibleProducts drops held mãs in every spelling and keeps S06 at 25", () => {
  for (const ma of HELD_INCOMPLETE_MAS) {
    assert.equal(fixtures.some((row) => row.ma === ma), true, ma);
    assert.equal(fixtures.some((row) => row.ma === ma.toLowerCase()), true, ma.toLowerCase());
    assert.equal(fixtures.some((row) => row.ma === paddedSpelling(ma)), true, paddedSpelling(ma));
  }

  const visible = shopVisibleProducts(fixtures);
  assert.deepEqual(
    visible.map((row) => row.ma),
    ["S06", "A03", "A02"],
  );
  const s06 = visible.find((row) => row.ma === "S06");
  assert.ok(s06);
  assert.equal(s06.priceUsd, 25);

  for (const row of visible) {
    const leaked = HELD_INCOMPLETE_MAS.some(
      (ma) => canonicalMaSpelling(ma) === canonicalMaSpelling(row.ma),
    );
    assert.equal(leaked, false, row.ma);
  }

  assert.equal(canonicalMaSpelling("S6"), "S06");
  assert.equal(canonicalMaSpelling("s006"), "S06");
  const byShort = findShopProduct(visible, "S6");
  assert.ok(byShort);
  assert.equal(byShort.ma, "S06");
  assert.equal(byShort.priceUsd, 25);
  assert.equal(findShopProduct(visible, "s006"), byShort);
  assert.equal(findShopProduct(visible, "S06"), byShort);
  assert.equal(findShopProduct(visible, held), undefined);
  assert.equal(findShopProduct(visible, held.toLowerCase()), undefined);
  assert.equal(findShopProduct(visible, paddedSpelling(held)), undefined);

  const paths = visible.map((row) => `/m/${canonicalMaSpelling(row.ma)}`);
  assert.equal(paths.includes("/m/S06"), true);
  assert.equal(paths.includes("/m/A03"), true);
  assert.equal(paths.includes("/m/A02"), true);
  for (const ma of HELD_INCOMPLETE_MAS) {
    assert.equal(paths.includes(`/m/${canonicalMaSpelling(ma)}`), false, ma);
  }

  const sitemap = readFileSync(new URL("../app/sitemap.ts", import.meta.url), "utf8");
  assert.match(sitemap, /shopVisibleProducts/);
});

test("srcBelongsToMa keeps a held mã's own folder and rejects it on other mãs", () => {
  const spellings = equivalentSpellings(held);
  const code = canonicalMaSpelling(held);
  assert.ok(spellings.includes(code));
  assert.ok(spellings.includes(code.toLowerCase()));
  assert.ok(spellings.includes(paddedSpelling(held)));
  assert.equal(canonicalMaSpelling(shortSpelling(held)), code);
  assert.ok(spellings.includes(shortSpelling(held)));

  for (const folder of spellings) {
    for (const productMa of spellings) {
      assert.equal(
        srcBelongsToMa(`/products/${folder}/cover.jpg`, productMa),
        true,
        `${folder} on ${productMa}`,
      );
    }
    assert.equal(srcBelongsToMa(`/products/${folder}/cover.jpg`, "A03"), false, folder);
    assert.equal(
      srcBelongsToMa(
        `https://example.public.blob.vercel-storage.com/sassy-closet-shop/products/${folder}/cover.jpg`,
        "A03",
      ),
      false,
      folder,
    );
  }

  const blobUrl = `https://example.public.blob.vercel-storage.com/sassy-closet-shop/products/${held}/cover.jpg`;
  assert.equal(blobUrl.includes(`/products/${held}/`), true);
  assert.equal(srcBelongsToMa(blobUrl, "A03"), false);
  assert.equal(srcBelongsToMa(blobUrl, held), true);

  assert.equal(srcBelongsToMa("/products/A01/cover.jpg", "A02"), false);
  assert.equal(srcBelongsToMa("/products/a01/extra.jpg", "A02"), false);
  assert.equal(srcBelongsToMa("/products/a01/extra.jpg", "A01"), true);
  assert.equal(srcBelongsToMa("/products/A001/cover.jpg", "A02"), false);
  assert.equal(srcBelongsToMa("/products/A04/cover.jpg", "A03"), true);
  assert.equal(srcBelongsToMa("/uploads/a03.jpg", "A03"), true);
  assert.equal(srcBelongsToMa("https://cdn.example.com/looks/a03.jpg", "A03"), true);
  assert.equal(srcBelongsToMa("", "A03"), false);
});

test("public A03 images drop the held folder and S06 JSON-LD keeps 25.00", () => {
  const a03 = fixtures.find((row) => row.ma === "A03");
  assert.ok(a03);
  const kept = ["/uploads/a03.jpg", "/products/A04/cover.jpg"];
  assert.deepEqual(
    ownMaImages(a03).map((item) => item.src),
    kept,
  );
  assert.equal(coverSrc(a03), "/uploads/a03.jpg");

  const looks = shopVisibleLooks(fixtures);
  const a03Look = looks.find((look) => look.ma === "A03");
  assert.ok(a03Look);
  assert.deepEqual(
    a03Look.images.map((item) => item.src),
    kept,
  );
  assert.equal(coverSrc(a03Look), "/uploads/a03.jpg");

  const a03Ld = productJsonLd(a03Look);
  const published = jsonLdImages(a03Ld);
  assert.equal(published.length, kept.length);
  for (const [index, src] of kept.entries()) {
    assert.equal(published[index]?.endsWith(src), true, src);
  }
  for (const folder of equivalentSpellings(held)) {
    assert.equal(
      published.some((src) => mentionsFolder(src, folder)),
      false,
      folder,
    );
    assert.equal(
      a03Look.images.some((item) => mentionsFolder(item.src, folder)),
      false,
      folder,
    );
  }

  const s06Look = looks.find((look) => look.ma === "S06");
  assert.ok(s06Look);
  assert.equal(s06Look.priceUsd, 25);
  const offers = productJsonLd(s06Look).offers;
  assert.ok(offers !== null && typeof offers === "object");
  assert.equal(Array.isArray(offers), false);
  assert.equal((offers as { price?: unknown }).price, "25.00");
});

test("search queries built from held mãs match nothing on the visible list", () => {
  const visible = shopVisibleLooks(fixtures);
  assert.equal(visible.some((look) => look.ma === "S06"), true);
  for (const ma of HELD_INCOMPLETE_MAS) {
    const queries = queriesForHeld(ma);
    assert.ok(queries.includes(ma), ma);
    assert.ok(queries.includes(paddedSpelling(ma)), ma);
    for (const query of queries) {
      assert.deepEqual(
        filterLooksByQuery(visible, query).map((look) => look.ma),
        [],
        query,
      );
    }
  }
});
