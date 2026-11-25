import assert from "node:assert/strict";
import test from "node:test";
import { listingChip, listingItemForMa, listingStatusFromApi } from "../lib/listing-status";

function padded(ma: string): string {
  return `${ma[0]}0${ma.slice(1)}`;
}

test("bot file keyed with a padded mã still badges the canonical card", () => {
  const ma = ["A", "07"].join("");
  const { items } = listingStatusFromApi({ enabled: true, items: { [padded(ma)]: { state: "held" } } });
  const item = listingItemForMa(items, ma);
  assert.equal(item?.state, "held");
  assert.equal(listingChip(item).label, "Held");
});

test("a lowercase padded stored mã finds the canonical bot key", () => {
  const ma = ["S", "14"].join("");
  const { items } = listingStatusFromApi({ enabled: true, items: { [ma]: { state: "held" } } });
  assert.equal(listingItemForMa(items, ` ${padded(ma).toLowerCase()} `)?.state, "held");
});

test("numbers above 99 stay distinct", () => {
  const { items } = listingStatusFromApi({
    enabled: true,
    items: { A100: { state: "held" }, A10: { state: "pending" } },
  });
  assert.equal(listingItemForMa(items, "A100")?.state, "held");
  assert.equal(listingItemForMa(items, "A10")?.state, "pending");
  assert.equal(listingItemForMa(items, "A010")?.state, "pending");
});

function badge(items: Parameters<typeof listingItemForMa>[0], ma: string) {
  const item = listingItemForMa(items, ma);
  return { state: item?.state, label: listingChip(item).label };
}

test("a held badge is not overwritten when a padded alias is live", () => {
  const { items } = listingStatusFromApi({
    enabled: true,
    items: {
      A07: { state: "held", reasons: [{ code: "photo_text", vi: "giữ" }] },
      A007: { state: "live", priceUsd: 30 },
    },
  });
  const held = { state: "held", label: "Held" };
  assert.deepEqual(
    { A07: badge(items, "A07"), A007: badge(items, "A007") },
    { A07: held, A007: held },
  );
});

test("a padded live alias listed first still leaves the held badge", () => {
  const { items } = listingStatusFromApi({
    enabled: true,
    items: {
      A007: { state: "live", priceUsd: 30 },
      A07: { state: "held", reasons: [{ code: "photo_text", vi: "giữ" }] },
    },
  });
  const held = { state: "held", label: "Held" };
  assert.deepEqual(
    { A07: badge(items, "A07"), A007: badge(items, "A007") },
    { A07: held, A007: held },
  );
});
