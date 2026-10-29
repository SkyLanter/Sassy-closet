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
