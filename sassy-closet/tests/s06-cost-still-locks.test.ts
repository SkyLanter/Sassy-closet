import assert from "node:assert/strict";
import test from "node:test";
import { intakePriceView } from "../lib/pricing";
import { lockedDeboxUsd, wouldBeLiveUsd, type IntakePriceInput } from "../../shared/tiered-pricing";

const FX = 6.723;

function digits(parts: string[]): string {
  return parts.join("");
}

const prices = {
  cny: digits(["4", "00"]),
  usd: digits(["4", "0"]),
  yen: digits(["90", ".65"]),
  buck: digits(["1"]),
  zero: digits(["0"]),
};

const bothCosts = { costCny: prices.cny, costUsd: prices.usd };
const yenOnly = { costCny: prices.cny, costUsd: null };
const usdOnly = { costCny: null, costUsd: prices.usd };
const cheapDollar = { costCny: null, costUsd: prices.buck };
const cheapYen = { costCny: prices.buck, costUsd: null };

function quote(ma: string, kind: string, costs: Pick<IntakePriceInput, "costCny" | "costUsd">) {
  return wouldBeLiveUsd({ ma, kind, liveUsd: 40, ...costs });
}

test("S06 stays $25 for every spelling and kind, including a one-unit cost", () => {
  for (const costs of [yenOnly, usdOnly, bothCosts, cheapDollar, cheapYen]) {
    const open = quote("S01", "S", costs);
    assert.equal(open.reason, "tiered");
    assert.equal(open.applied, true);
    assert.notEqual(open.wouldBeUsd, 25);

    for (const ma of ["S06", "S6", "s006", " S006 "]) {
      for (const kind of ["S", "V"]) {
        const locked = quote(ma, kind, costs);
        const label = `${ma} ${kind}`;
        assert.equal(locked.ma, "S06", label);
        assert.equal(locked.liveUsd, 40, label);
        assert.equal(locked.wouldBeUsd, 25, label);
        assert.equal(locked.applied, false, label);
        assert.equal(locked.reason, "locked", label);
        assert.notEqual(locked.wouldBeUsd, open.wouldBeUsd, label);
      }
    }
  }
});

test("a yen cost wins over a different dollar cost, and a blank cost keeps the live dollar", () => {
  const spaced = ` ${prices.yen} `;
  const fromYen = quote("A02", "a", { costCny: prices.yen, costUsd: null });
  const fromBoth = wouldBeLiveUsd({
    ma: "A03",
    kind: "A",
    liveUsd: 40,
    costCny: spaced,
    costUsd: prices.buck,
  });
  const fromDollar = wouldBeLiveUsd({
    ma: "A04",
    kind: "A",
    liveUsd: 40,
    costCny: null,
    costUsd: prices.buck,
  });
  const blank = wouldBeLiveUsd({
    ma: "A05",
    kind: "A",
    liveUsd: 18,
    costCny: prices.zero,
    costUsd: prices.zero,
  });
  assert.equal(fromYen.reason, "tiered");
  assert.equal(fromBoth.reason, "tiered");
  assert.equal(fromBoth.wouldBeUsd, fromYen.wouldBeUsd);
  assert.notEqual(fromBoth.wouldBeUsd, fromDollar.wouldBeUsd);
  assert.equal(blank.reason, "no-cost");
  assert.equal(blank.applied, false);
  assert.equal(blank.wouldBeUsd, 18);
});

test("dress letters add the locked debox and other letters do not", () => {
  for (const letter of ["V", "v", "Q", "q", "D", "d"]) {
    assert.equal(lockedDeboxUsd(letter), "7.50", letter);
  }
  assert.equal(lockedDeboxUsd("A"), "0");
  assert.equal(lockedDeboxUsd("a"), "0");

  const dress = quote("V02", "v", yenOnly);
  const puppy = quote("A02", "a", yenOnly);
  assert.equal(dress.reason, "tiered");
  assert.equal(puppy.reason, "tiered");
  assert.ok(dress.wouldBeUsd > puppy.wouldBeUsd);
});

test("a typed S06 sell stays $25 when a cost is filled, including a one-unit cost", () => {
  const filled = [
    { costCny: prices.cny, costUsd: "" },
    { costCny: "", costUsd: prices.usd },
    { costCny: prices.cny, costUsd: prices.usd },
    { costCny: "", costUsd: prices.buck },
    { costCny: prices.buck, costUsd: "" },
  ];
  for (const ma of ["S06", "s6", "s006"]) {
    for (const costs of filled) {
      const view = intakePriceView({
        ma,
        kind: "S",
        sellUsd: "80",
        sellCny: "",
        sellCurrency: "USD",
        costCurrency: "CNY",
        fxRate: FX,
        ...costs,
      });
      assert.equal(view.dollars, 25, ma);
      assert.equal(view.label, "$25", ma);
      assert.equal(view.flag, "ok", ma);
    }
  }
});

test("a dashed spelling is not the S06 lock", () => {
  assert.throws(() => quote("S-06", "S", bothCosts), /invalid/);
});
