import assert from "node:assert/strict";
import test from "node:test";
import { SHIP_QUOTE } from "../lib/dropship-copy";
import { composeShipDraftMessage } from "../lib/ship-draft";

const empty = { name: "", address: "", city: "", note: "" };

test("a customer note with a dollar amount does not crash the ship draft", () => {
  const message = composeShipDraftMessage("A01", "available", {
    ...empty,
    name: "Kelly",
    note: "budget around $40",
  });
  assert.match(message, /Mã A01/);
  assert.match(message, /budget around \$40/);
  assert.match(message, new RegExp(SHIP_QUOTE.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  const site = message.split("\n").slice(0, 2).join("\n");
  assert.equal(/\$\d/.test(site), false);
  assert.equal(/ship\s*\$/i.test(site), false);
});

test("a stored address that mentions ship $ still composes", () => {
  const message = composeShipDraftMessage("S01", "hold", {
    ...empty,
    address: "please ship $0 extra if you can",
  });
  assert.match(message, /Mã S01/);
  assert.match(message, /ship \$0 extra/);
});
