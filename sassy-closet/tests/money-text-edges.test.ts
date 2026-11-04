import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test, { afterEach, beforeEach, describe } from "node:test";
import { convertCnyToUsd, convertUsdToCny } from "../lib/fx";
import { moneyForStore, readMoney, type MoneySide } from "../lib/money-text";
import { intakePriceView, landedUsdFromCosts } from "../lib/pricing";
import { saveSubmission } from "../lib/store";
import { resetStoreBackendForTests } from "../lib/store-backend";

const WEEKLY = 6.71;
const SIDES: readonly MoneySide[] = ["CNY", "USD"];
const STORE_ENV = [
  "SASSY_DATA_DIR",
  "VERCEL",
  "BLOB_READ_WRITE_TOKEN",
  "BLOB_STORE_ID",
  "BLOB_ACCESS",
  "INTAKE_DATASET_SYNC_WEBHOOK_URL",
  "INTAKE_DATASET_SYNC_WEBHOOK_KEY",
  "NEW_MA_WEBHOOK_URL",
  "NEW_MA_WEBHOOK_TOKEN",
] as const;

const GARBLED = [
  "127;145",
  "1e2",
  "0x10",
  "2,5",
  "0,025",
  "00,025",
  "0,250",
  "01,025",
  "80 90",
  "-5",
  "80abc",
  ".",
] as const;

test("blank money stays blank and never becomes 0", () => {
  const blanks = ["", "   ", "\uFEFF"];
  for (const raw of blanks) {
    for (const side of SIDES) {
      assert.deepEqual(readMoney(raw, side), { kind: "blank" }, JSON.stringify(raw));
      assert.equal(moneyForStore(raw, side), "");
      assert.notEqual(moneyForStore(raw, side), "0");
      assert.notEqual(moneyForStore(raw, side), "0.00");
    }
    assert.equal(convertCnyToUsd(raw, WEEKLY), "");
    assert.equal(convertUsdToCny(raw, WEEKLY), "");
    assert.notEqual(convertCnyToUsd(raw, WEEKLY), "0");
    assert.notEqual(convertCnyToUsd(raw, WEEKLY), "0.00");
  }
});

test("garbled money stays text and does not become a number", () => {
  for (const raw of GARBLED) {
    for (const side of SIDES) {
      assert.deepEqual(readMoney(raw, side), { kind: "garbled", text: raw });
      assert.equal(moneyForStore(raw, side), raw);
      assert.equal(convertCnyToUsd(raw, WEEKLY), null);
      assert.equal(convertUsdToCny(raw, WEEKLY), null);
    }
  }
  assert.equal(moneyForStore("\uFEFF  127;145  ", "CNY"), "127;145");
  assert.equal(moneyForStore("  1e2\uFEFF", "USD"), "1e2");
  assert.deepEqual(readMoney("\uFEFF127;145", "USD"), { kind: "garbled", text: "127;145" });

  assert.equal(
    landedUsdFromCosts({
      kind: "A",
      costCny: "127;145",
      costUsd: "",
      costCurrency: "CNY",
      fxRate: WEEKLY,
    }),
    null,
  );
  assert.equal(
    landedUsdFromCosts({
      kind: "A",
      costCny: "1e2",
      costUsd: "",
      costCurrency: "CNY",
      fxRate: WEEKLY,
    }),
    null,
  );
  assert.equal(
    landedUsdFromCosts({
      kind: "A",
      costCny: "",
      costUsd: "0x10",
      costCurrency: "USD",
      fxRate: WEEKLY,
    }),
    null,
  );
});

test("folded amounts store canonical digits and plain decimals stay exact", () => {
  const folded: readonly [string, MoneySide, string, number][] = [
    ["¥80", "CNY", "80", 80],
    ["￥80.5", "CNY", "80.5", 80.5],
    ["¥ 80", "CNY", "80", 80],
    ["80元", "CNY", "80", 80],
    ["８０", "CNY", "80", 80],
    ["\uFEFF80", "CNY", "80", 80],
    ["1,280", "CNY", "1280", 1280],
    ["1,280.50", "CNY", "1280.50", 1280.5],
    ["80.", "CNY", "80", 80],
    ["¥80.50", "CNY", "80.50", 80.5],
    ["$28", "USD", "28", 28],
    ["２８", "USD", "28", 28],
  ];
  for (const [raw, side, text, value] of folded) {
    const read = readMoney(raw, side);
    assert.equal(read.kind, "amount", raw);
    if (read.kind === "amount") {
      assert.equal(read.text, text, raw);
      assert.equal(read.value, value, raw);
    }
    assert.equal(moneyForStore(raw, side), text, raw);
  }
  assert.equal(moneyForStore("80.52", "CNY"), "80.52");
  assert.equal(moneyForStore("80.52", "USD"), "80.52");
  assert.equal(moneyForStore("80.5", "CNY"), "80.5");
  assert.equal(moneyForStore("80.5", "USD"), "80.5");
  assert.notEqual(moneyForStore("80.5", "USD"), "80.50");
  assert.notEqual(moneyForStore("80.52", "CNY"), "80.50");
});

test("a currency symbol only counts on its own side", () => {
  assert.deepEqual(readMoney("¥28", "USD"), { kind: "garbled", text: "¥28" });
  assert.equal(moneyForStore("¥28", "USD"), "¥28");
  assert.equal(convertUsdToCny("¥28", WEEKLY), null);

  assert.deepEqual(readMoney("$80", "CNY"), { kind: "garbled", text: "$80" });
  assert.equal(moneyForStore("$80", "CNY"), "$80");
  assert.equal(convertCnyToUsd("$80", WEEKLY), null);

  const dollars = readMoney("$28", "USD");
  assert.equal(dollars.kind, "amount");
  if (dollars.kind === "amount") assert.equal(dollars.value, 28);
  const fullwidth = readMoney("２８", "USD");
  assert.equal(fullwidth.kind, "amount");
  if (fullwidth.kind === "amount") assert.equal(fullwidth.value, 28);
});

test("weekly convert still maps 80 and 12 and rejects a dot, junk, and rate 0", () => {
  assert.equal(convertCnyToUsd("80", WEEKLY), "11.92");
  assert.equal(convertUsdToCny("12", WEEKLY), "80.52");
  assert.equal(convertCnyToUsd(".", WEEKLY), null);
  assert.equal(convertUsdToCny("abc", WEEKLY), null);
  assert.equal(convertCnyToUsd("80", 0), null);
  assert.equal(convertUsdToCny("12", 0), null);
});

test("a typed zero writes 0.00 on the other side and does not keep the old dollar", () => {
  assert.equal(convertCnyToUsd("0", WEEKLY), "0.00");
  assert.equal(convertUsdToCny("0", WEEKLY), "0.00");
  assert.equal(convertCnyToUsd("0.", WEEKLY), "0.00");
  assert.equal(convertUsdToCny("0.00", WEEKLY), "0.00");
  assert.equal(
    landedUsdFromCosts({
      kind: "A",
      costCny: "80.52",
      costUsd: "0",
      costCurrency: "USD",
      fxRate: WEEKLY,
    }),
    null,
  );
  assert.equal(
    landedUsdFromCosts({
      kind: "A",
      costCny: "0",
      costUsd: "12",
      costCurrency: "CNY",
      fxRate: WEEKLY,
    }),
    null,
  );
  const view = intakePriceView({
    ma: "A09",
    kind: "A",
    sellUsd: "0.00",
    sellCny: "0",
    sellCurrency: "USD",
    costCny: "80",
    costUsd: "12",
    costCurrency: "USD",
    fxRate: WEEKLY,
  });
  assert.equal(view.label, "$0.00");
  assert.equal(view.dollars, 0);
  assert.notEqual(view.label, "$12");
});

describe("saveSubmission money", { concurrency: 1 }, () => {
  let tmp = "";
  const prev: Record<string, string | undefined> = {};

  beforeEach(() => {
    tmp = fs.mkdtempSync(path.join(os.tmpdir(), "sassy-money-"));
    for (const key of STORE_ENV) {
      prev[key] = process.env[key];
      delete process.env[key];
    }
    process.env.SASSY_DATA_DIR = tmp;
    resetStoreBackendForTests();
  });

  afterEach(() => {
    for (const key of STORE_ENV) {
      if (prev[key] === undefined) delete process.env[key];
      else process.env[key] = prev[key];
    }
    resetStoreBackendForTests();
    fs.rmSync(tmp, { recursive: true, force: true });
  });

  test("yen and fullwidth costs store digits and a blank sell stays out of the caption", async () => {
    const yen = await saveSubmission(saveInput({ cost_cny: "¥80.50", cost_currency: "CNY" }));
    assert.equal(yen.cost_cny, "80.50");
    assert.equal(yen.sell_usd, "");
    assert.equal(yen.sell_cny, "");
    assert.match(yen.caption_vi, /Inbox giá/);
    assert.doesNotMatch(yen.caption_vi, /\$\d/);

    const fullwidth = await saveSubmission(saveInput({ cost_cny: "８０", cost_currency: "CNY" }));
    assert.equal(fullwidth.cost_cny, "80");
    assert.equal(fullwidth.sell_usd, "");
    assert.equal(fullwidth.sell_cny, "");
    assert.match(fullwidth.caption_vi, /Inbox giá/);
    assert.doesNotMatch(fullwidth.caption_vi, /\$\d/);
  });

  test("garbled cost is stored unchanged and sell stays blank", async () => {
    const saved = await saveSubmission(saveInput({ cost_cny: "127;145", cost_currency: "CNY" }));
    assert.equal(saved.cost_cny, "127;145");
    assert.equal(saved.sell_usd, "");
    assert.equal(saved.sell_cny, "");
    assert.match(saved.caption_vi, /Inbox giá/);
    assert.doesNotMatch(saved.caption_vi, /\$\d/);
  });

  test("a blank cost stays blank", async () => {
    const saved = await saveSubmission(saveInput({ cost_cny: "", cost_usd: "" }));
    assert.equal(saved.cost_cny, "");
    assert.equal(saved.cost_usd, "");
    assert.equal(saved.sell_usd, "");
    assert.equal(saved.sell_cny, "");
    assert.notEqual(saved.cost_cny, "0");
  });

  test("plain costs keep their typed decimals", async () => {
    const saved = await saveSubmission(
      saveInput({ cost_cny: "80.52", cost_usd: "80.5", cost_currency: "CNY" }),
    );
    assert.equal(saved.cost_cny, "80.52");
    assert.equal(saved.cost_usd, "80.5");
    assert.notEqual(saved.cost_usd, "80.50");
  });

  test("a typed $28 stores 28 and the caption does not double the dollar sign", async () => {
    const saved = await saveSubmission(saveInput({ sell_usd: "$28", sell_currency: "USD" }));
    assert.equal(saved.sell_usd, "28");
    assert.notEqual(saved.sell_usd, "$28");
    assert.notEqual(saved.sell_usd, "28.00");
    assert.equal(saved.price, "28");
    assert.equal(saved.caption_vi.includes("$$"), false);
    assert.match(saved.caption_vi, /\$28/);
  });
});

function saveInput(
  overrides: {
    cost_usd?: string;
    cost_cny?: string;
    cost_currency?: string;
    sell_usd?: string;
    sell_cny?: string;
    sell_currency?: string;
  } = {},
) {
  return {
    kind: "A",
    size: "",
    link: "",
    color: "",
    color_note: "",
    pieces: [],
    cost_usd: "",
    cost_cny: "",
    cost_currency: "USD",
    sell_usd: "",
    sell_cny: "",
    sell_currency: "USD",
    keep_photos: [],
    photos: [],
    needs_research: false,
    taobao_snapshot: null,
    auto_price: null,
    ...overrides,
  };
}
