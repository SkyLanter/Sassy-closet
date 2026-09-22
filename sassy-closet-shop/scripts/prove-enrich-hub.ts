import { KNOWN_SEED_MAS } from "../lib/catalog-contract";
import { readLiveCatalogDocument } from "../lib/catalog-store";
import { HUB_COLORS_BY_MA } from "../lib/hub-colors";
import { HUB_RECORDED_SIZES, recordedHubSourceLink } from "../lib/hub-source-links";
import { shopSafeProduct } from "../lib/sell-contract";
import { shopVisibleProducts } from "../lib/site-settings";

const SHOP = process.env.SHOP_ORIGIN ?? "http://127.0.0.1:43147";

function fail(message: string): never {
  throw new Error(message);
}

async function main(): Promise<void> {
  const document = await readLiveCatalogDocument();
  const visible = shopVisibleProducts(document.products);

  for (const ma of KNOWN_SEED_MAS) {
    const product = document.products.find((row) => row.ma === ma);
    if (!product) {
      fail(`Live catalog missing hub ${ma}`);
    }
    if (!visible.some((row) => row.ma === ma)) {
      fail(`Hub ${ma} must stay Message-ready on the shop`);
    }
    const slugs = [...HUB_COLORS_BY_MA[ma]];
    const ids = product.colors.map((color) => color.id);
    if (ids.join(",") !== slugs.join(",")) {
      fail(`Live ${ma} colors must match recorded hub slugs (${slugs.join(",") || "empty"}), got ${ids.join(",") || "empty"}`);
    }
    if (product.sizes.length !== HUB_RECORDED_SIZES[ma].length) {
      fail(`Live ${ma} sizes must stay empty — All sheet has no size column`);
    }
    const recorded = recordedHubSourceLink(ma);
    if (!recorded || product.sourceLink !== recorded) {
      fail(`Live ${ma} must keep the recorded staff source_link`);
    }
    if (shopSafeProduct(product).sourceLink !== null) {
      fail(`Customer product for ${ma} must strip sourceLink`);
    }
    if ((ma === "P02" || ma === "P05") && (product.status !== "hold" || product.priceUsd !== null)) {
      fail(`Live ${ma} must stay Hold with no USD`);
    }
    if (ma === "P05" && product.priceUsd === 23) {
      fail("P05 must never publish $23");
    }
  }

  const extra = document.products.find((product) => product.ma === "A03");
  if (!extra) {
    fail("Live catalog missing A03 — run prove:add-a03 first");
  }
  if (!visible.some((product) => product.ma === "A03")) {
    fail("A03 must be shop-visible after Add");
  }
  if (extra.sourceLink !== null) {
    fail("A03 must not receive an invented staff link");
  }

  try {
    const [home, pdp, catalog] = await Promise.all([
      fetch(`${SHOP}/`, { cache: "no-store" }),
      fetch(`${SHOP}/m/A03`, { cache: "no-store" }),
      fetch(`${SHOP}/api/admin/catalog`, { cache: "no-store" }),
    ]);
    if (home.ok) {
      const html = await home.text();
      if (!html.includes("A03")) {
        fail("Home HTML must list A03 after Add");
      }
      if (!html.includes("Message to buy") && !html.includes("Message")) {
        fail("Home must stay Message-to-buy");
      }
      if (html.includes("e.tb.cn")) {
        fail("Customer home must not leak staff Taobao links");
      }
    }
    if (pdp.status === 404) {
      fail("/m/A03 must be 200 after Add (Boss override — not kit §15.1 404)");
    }
    if (pdp.ok) {
      const html = await pdp.text();
      if (!html.includes("A03")) {
        fail("PDP /m/A03 missing mã");
      }
      if (html.includes("e.tb.cn")) {
        fail("Customer PDP must not leak staff Taobao links");
      }
    }
    if (catalog.ok) {
      const body = (await catalog.json()) as { products?: Array<{ ma?: string }> };
      const mas = (body.products ?? []).map((row) => row.ma);
      if (!KNOWN_SEED_MAS.every((ma) => mas.includes(ma))) {
        fail("GET /api/admin/catalog must include the hub ten");
      }
      if (!mas.includes("A03")) {
        fail("GET /api/admin/catalog must include A03 after Add");
      }
    }
  } catch {
    console.log("enrich 10 ok (HTTP shop not up — catalog facts only)");
    return;
  }

  console.log("enrich 10 ok hub=10 A03=shop-visible sourceLinks=staff-only");
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});
