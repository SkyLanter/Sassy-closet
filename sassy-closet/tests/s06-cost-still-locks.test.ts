import assert from "node:assert/strict";
import test from "node:test";
import { intakePriceView } from "../lib/pricing";
import { wouldBeLiveUsd } from "../../shared/tiered-pricing";

const FX = 6.723;

const COST = {
  costCny: "400",
  costUsd: "40",
} as const;

test("S06 stays $25 when a real cost is present, for every spelling", () => {
  const open = wouldBeLiveUsd({
    ma: "S01",
    kind: "S",
    liveUsd: 40,
    ...COST,
  });
  assert.equal(open.reason, "tiered");
  assert.equal(open.applied, true);
  assert.notEqual(open.wouldBeUsd, 25);

  for (const ma of ["S06", "S6", "s006", " S006 "]) {
    const locked = wouldBeLiveUsd({
      ma,
      kind: "V",
      liveUsd: 40,
      ...COST,
    });
    assert.equal(locked.ma, "S06", ma);
    assert.equal(locked.liveUsd, 40, ma);
    assert.equal(locked.wouldBeUsd, 25, ma);
    assert.equal(locked.applied, false, ma);
    assert.equal(locked.reason, "locked", ma);
    assert.notEqual(locked.wouldBeUsd, open.wouldBeUsd, ma);
  }
});

test("a yen cost wins over a different dollar cost, and a blank cost keeps the live dollar", () => {
  const fromYen = wouldBeLiveUsd({
    ma: "A02",
    kind: "a",
    liveUsd: 40,
    costCny: "90.65",
    costUsd: null,
  });
  const fromBoth = wouldBeLiveUsd({
    ma: "A03",
    kind: "A",
    liveUsd: 40,
    costCny: " 90.65 ",
    costUsd: "1",
  });
  const fromDollar = wouldBeLiveUsd({
    ma: "A04",
    kind: "A",
    liveUsd: 40,
    costCny: null,
    costUsd: "1",
  });
  const blank = wouldBeLiveUsd({
    ma: "A05",
    kind: "A",
    liveUsd: 18,
    costCny: "0",
    costUsd: "0",
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
  const dress = wouldBeLiveUsd({
    ma: "V02",
    kind: "v",
    liveUsd: 40,
    costCny: "90.65",
    costUsd: null,
  });
  const puppy = wouldBeLiveUsd({
    ma: "A02",
    kind: "a",
    liveUsd: 40,
    costCny: "90.65",
    costUsd: null,
  });
  assert.equal(dress.reason, "tiered");
  assert.equal(puppy.reason, "tiered");
  assert.ok(dress.wouldBeUsd > puppy.wouldBeUsd);
});

test("a typed S06 sell with a cost still shows $25", () => {
  const view = intakePriceView({
    ma: "s006",
    kind: "S",
    sellUsd: "80",
    sellCny: "",
    sellCurrency: "USD",
    costCny: COST.costCny,
    costUsd: COST.costUsd,
    costCurrency: "CNY",
    fxRate: FX,
  });
  assert.equal(view.dollars, 25);
  assert.equal(view.label, "$25");
  assert.equal(view.flag, "ok");
});

test("a dashed spelling is not the S06 lock", () => {
  assert.throws(
    () =>
      wouldBeLiveUsd({
        ma: "S-06",
        kind: "S",
        liveUsd: 40,
        ...COST,
      }),
    /invalid/,
  );
});
