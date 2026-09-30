import assert from "node:assert/strict";
import { describe, test } from "node:test";
import {
  buildIntakeDataset,
  datasetEntryForMa,
  datasetLaneLabel,
  isAllowedShopOrigin,
  formatMaList,
  publicCatalogUrlFromSitemap,
  rowsFromShopCatalog,
  type ShopDatasetRow,
} from "../lib/intake-dataset";
import { shopDatasetFromPublicShop } from "../lib/shop-dataset-read";

const shop: ShopDatasetRow[] = [
  { ma: "A01", status: "available", priceUsd: 27 },
  { ma: "D05", status: "available", priceUsd: 32 },
  { ma: "V03", status: "available", priceUsd: 28 },
  { ma: "P02", status: "hold", priceUsd: null },
  { ma: "Q09", status: "sold", priceUsd: 10 },
];

describe("intake dataset vs shop catalog", () => {
  test("live is available catalog rows; incomplete intake mãs stay held", () => {
    const view = buildIntakeDataset(["A01", "S14", "A24", "p02", "A25", "S15", "A26"], shop);
    assert.equal(view.ready, true);
    assert.equal(view.liveCount, 3);
    assert.deepEqual(view.liveCount, view.entries.filter((entry) => entry.lane === "live").length);
    assert.deepEqual(
      view.entries.filter((entry) => entry.lane === "live").map((entry) => entry.ma),
      ["A01", "D05", "V03"],
    );
    assert.deepEqual(view.heldMas, ["S14", "A24", "P02", "A25", "S15", "A26"]);
    assert.deepEqual(
      view.shopOnlyLive.map((entry) => entry.ma),
      ["D05", "V03"],
    );
    assert.equal(datasetEntryForMa(view, "s14")?.lane, "held");
    assert.equal(datasetEntryForMa(view, "A01")?.lane, "live");
    assert.equal(datasetEntryForMa(view, "Q09")?.lane, "sold");
    assert.equal(datasetLaneLabel("held"), "Held · chưa xong");
    assert.equal(datasetLaneLabel("live"), "Live");
    assert.equal(formatMaList(["D05", "V03"]), "D05, V03");
    assert.equal(formatMaList(["A01", "A02", "A03"], 2), "A01, A02 +1");
    assert.equal(view.entries.some((entry) => entry.ma === "B99"), false);
  });

  test("unread shop catalog does not mark anyone live", () => {
    const view = buildIntakeDataset(["A01", "S14"], null);
    assert.equal(view.ready, false);
    assert.equal(view.liveCount, 0);
    assert.deepEqual(view.heldMas, []);
    assert.equal(datasetEntryForMa(view, "A01"), null);
  });

  test("catalog list drops a broken read and keeps prices that are already stored", () => {
    assert.equal(rowsFromShopCatalog({ ok: false, error: "missing" }), null);
    const rows = rowsFromShopCatalog({
      ok: true,
      updatedAt: null,
      siteId: "sassy-closet-shop",
      products: [
        {
          ma: "d05",
          titleVn: "",
          titleEn: "",
          descriptionVn: "",
          descriptionEn: "",
          priceUsd: 32,
          status: "available",
          locked: false,
          shopPriceUsd: 32,
          colors: [],
        },
      ],
    });
    assert.deepEqual(rows, [{ ma: "D05", status: "available", priceUsd: 32 }]);
  });

  test("public catalog URL comes from the shop sitemap blob host", () => {
    const xml =
      '<url><loc>https://sassycloset.vercel.app/m/A15</loc><image:loc>https://efsi0jejsfy7j058.public.blob.vercel-storage.com/sassy-closet-shop/products/A15/photo-gray.jpg</image:loc></url>';
    assert.equal(
      publicCatalogUrlFromSitemap(xml),
      "https://efsi0jejsfy7j058.public.blob.vercel-storage.com/sassy-closet-shop/catalog.v1.json",
    );
    assert.equal(publicCatalogUrlFromSitemap("<urlset></urlset>"), null);
    assert.equal(isAllowedShopOrigin("https://sassycloset.vercel.app"), true);
    assert.equal(isAllowedShopOrigin("https://evil.example/sassycloset.vercel.app"), false);
    assert.equal(isAllowedShopOrigin("http://sassycloset.vercel.app"), false);
  });

  test("public shop read uses only the allowlisted origin", async () => {
    let calls = 0;
    const fetchImpl: typeof fetch = async (input) => {
      calls += 1;
      const url = String(input);
      if (url.endsWith("/sitemap.xml")) {
        return new Response(
          "https://store1.public.blob.vercel-storage.com/sassy-closet-shop/products/A01/cover.jpg",
        );
      }
      assert.equal(
        url,
        "https://store1.public.blob.vercel-storage.com/sassy-closet-shop/catalog.v1.json",
      );
      return new Response(
        JSON.stringify({
          schema: "catalog.v1",
          version: 1,
          siteId: "sassy-closet-shop",
          products: [
            {
              ma: "A01",
              titleVn: "Áo",
              titleEn: "Top",
              priceUsd: 27,
              status: "available",
              colors: [],
              sizes: ["S"],
              images: [],
            },
          ],
        }),
      );
    };
    const blocked = await shopDatasetFromPublicShop(fetchImpl, "https://evil.example");
    assert.equal(blocked, null);
    assert.equal(calls, 0);
    const rows = await shopDatasetFromPublicShop(fetchImpl, "https://sassycloset.vercel.app");
    assert.deepEqual(rows, [{ ma: "A01", status: "available", priceUsd: 27 }]);
    assert.equal(calls, 2);
  });
});
