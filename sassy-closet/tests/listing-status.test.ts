import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";
import { GET } from "../app/api/listing-status/route";
import {
  LISTING_STATUS_POLL_MS,
  LISTING_TEXT_CAP,
  formatUsd,
  listingChip,
  listingItemForMa,
  listingPollIntervalMs,
  listingStatusFromApi,
  listingWebView,
  parseListingFile,
} from "../lib/listing-status";

const ENV_KEYS = ["LISTING_STATUS_URL", "SHOP_BLOB_READ_WRITE_TOKEN"] as const;
const STATUS_URL = "https://example.invalid/intake-status.v1.json";
const BLOB_TOKEN = "shop-blob-token-should-not-leak";

const PHOTO_VI =
  "Không có ảnh nào dùng được: ảnh có chữ Trung / watermark ... → chị gửi giúp ảnh sạch nha.";
const SIZE_VI = "thiếu size";
const COLOR_VI = "Màu trên form “Hồng, Trắng” khác màu seller ...";

describe("listing status parse", () => {
  test("keeps live, held, and pending text exactly and drops junk", () => {
    const long = `  ${"ả".repeat(LISTING_TEXT_CAP + 5)}  `;
    const parsed = parseListingFile({
      version: 1,
      generatedAt: "2026-09-28T08:12:10Z",
      run: "20260928T081201Z",
      items: {
        " a17 ": {
          state: "live",
          priceUsd: 25,
          url: "https://sassycloset.vercel.app/m/A17",
          todo: [{ code: "color_mismatch", vi: `  ${COLOR_VI}  ` }],
        },
        A22: {
          state: "held",
          since_run: "20260928T081046Z",
          reasons: [
            { code: "photo_text", vi: PHOTO_VI },
            { code: "size_missing", vi: SIZE_VI },
          ],
          todo: [{ code: "ignore", vi: "not on a held card" }],
        },
        S13: { state: "pending" },
        Z01: { state: "nope", reasons: [{ code: "internal", vi: "nội bộ" }] },
        Z02: { state: "excluded" },
        bad: { state: "" },
        "javascript:alert(1)": { state: "live", url: "javascript:alert(1)", priceUsd: "25" },
      },
    });
    assert.ok(parsed);
    assert.equal(parsed.A17.state, "live");
    assert.equal(parsed.A17.priceUsd, 25);
    assert.equal(parsed.A17.url, "https://sassycloset.vercel.app/m/A17");
    assert.deepEqual(parsed.A17.todo, [{ code: "color_mismatch", vi: COLOR_VI }]);
    assert.deepEqual(parsed.A22.reasons.map((note) => note.vi), [PHOTO_VI, SIZE_VI]);
    assert.equal(parsed.A22.since_run, "20260928T081046Z");
    assert.equal(parsed.S13.state, "pending");
    assert.equal(parsed.Z01.state, "unknown");
    assert.equal(parsed.Z01.reasons[0].vi, "nội bộ");
    assert.equal(parsed.Z02.state, "excluded");
    assert.equal("bad" in parsed, false);
    assert.equal(parsed["JAVASCRIPT:ALERT(1)"].url, undefined);
    assert.equal(parsed["JAVASCRIPT:ALERT(1)"].priceUsd, undefined);

    const capped = parseListingFile({
      version: 1,
      items: { A01: { state: "held", reasons: [{ code: "photo_text", vi: long }] } },
    });
    assert.equal(capped?.A01.reasons[0].vi.length, LISTING_TEXT_CAP);
    assert.equal(capped?.A01.reasons[0].vi.startsWith("ả"), true);
  });

  test("wrong version or a non-object items bag is an error", () => {
    assert.equal(parseListingFile({ version: 2, items: {} }), null);
    assert.equal(parseListingFile({ version: "1", items: {} }), null);
    assert.equal(parseListingFile({ version: 1, items: [] }), null);
    assert.equal(parseListingFile(null), null);
  });

  test("chips and the Web field use the file text", () => {
    const items = parseListingFile({
      version: 1,
      items: {
        A17: {
          state: "live",
          priceUsd: 25,
          url: "https://sassycloset.vercel.app/m/A17",
          reasons: [{ code: "color_mismatch", vi: COLOR_VI }],
          todo: [{ code: "color_mismatch", vi: COLOR_VI }],
        },
        A22: {
          state: "held",
          reasons: [
            { code: "photo_text", vi: PHOTO_VI },
            { code: "size_missing", vi: SIZE_VI },
          ],
        },
      },
    });
    assert.ok(items);
    assert.deepEqual(listingChip(items.A17), { label: "Live $25", tone: "ok" });
    assert.deepEqual(listingChip(items.A22), { label: "Held", tone: "warn" });
    assert.deepEqual(listingChip(undefined), { label: "Đang chờ bot", tone: "muted" });
    assert.deepEqual(listingChip({ state: "pending", reasons: [], todo: [] }), {
      label: "Đang chờ bot",
      tone: "muted",
    });
    assert.equal(listingChip({ state: "live", reasons: [], todo: [] }).label, "Live");
    assert.equal(listingChip({ state: "excluded", reasons: [], todo: [] }).label, "Excluded");
    assert.equal(listingChip({ state: "unknown", reasons: [], todo: [] }).label, "Unknown");

    const live = listingWebView(items.A17);
    assert.equal(live.summary, "Live · $25");
    assert.equal(live.href, "https://sassycloset.vercel.app/m/A17");
    assert.deepEqual(live.notes, [COLOR_VI, COLOR_VI]);
    const held = listingWebView(items.A22);
    assert.equal(held.summary, "Held");
    assert.equal(held.href, undefined);
    assert.deepEqual(held.notes, [PHOTO_VI, SIZE_VI]);
    assert.equal(listingWebView(undefined).summary, "Đang chờ bot");
    assert.equal(listingItemForMa(items, "a17")?.state, "live");
    assert.equal(formatUsd(25), "$25");
    assert.equal(formatUsd(24.5), "$24.50");
    assert.equal(formatUsd(10.1), "$10.10");
    assert.equal(
      listingChip({ state: "live", priceUsd: 24.5, reasons: [], todo: [] }).label,
      "Live $24.50",
    );
    assert.equal(listingWebView({ state: "live", priceUsd: 24.5, reasons: [], todo: [] }).summary, "Live · $24.50");
  });

  test("enabled false hides items; a bare items bag still shows badges", () => {
    const off = listingStatusFromApi({ enabled: false, items: { A17: { state: "live", priceUsd: 25 } } });
    assert.equal(off.enabled, false);
    assert.deepEqual(off.items, {});
    const on = listingStatusFromApi({
      items: { A17: { state: "live", priceUsd: 24, reasons: [], todo: [] } },
    });
    assert.equal(on.enabled, true);
    assert.equal(on.items.A17.priceUsd, 24);
    assert.deepEqual(listingStatusFromApi(null), { enabled: false, items: {} });
    const failed = listingStatusFromApi({
      enabled: false,
      error: true,
      items: { A17: { state: "live", priceUsd: 25 } },
    });
    assert.equal(failed.enabled, false);
    assert.deepEqual(failed.items, {});
  });

  test("badges poll every 45s only while the tab is visible", () => {
    assert.equal(LISTING_STATUS_POLL_MS, 45_000);
    assert.equal(listingPollIntervalMs("visible"), 45_000);
    assert.equal(listingPollIntervalMs("hidden"), null);
    assert.equal(listingPollIntervalMs("prerender"), null);
    const intake = fs.readFileSync(path.join(process.cwd(), "components/IntakeApp.tsx"), "utf8");
    assert.match(intake, /visibilitychange/);
    assert.match(intake, /listingPollIntervalMs/);
    assert.match(intake, /scheduleListingRefresh/);
  });
});

describe("GET /api/listing-status", () => {
  const prev: Record<string, string | undefined> = {};
  let fetchCalls: { url: string; init: RequestInit }[] = [];
  let originalFetch: typeof fetch | undefined;

  beforeEach(() => {
    for (const key of ENV_KEYS) {
      prev[key] = process.env[key];
      delete process.env[key];
    }
    fetchCalls = [];
    originalFetch = globalThis.fetch;
    globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
      fetchCalls.push({ url: String(input), init: init ?? {} });
      return new Response(JSON.stringify(sampleFile()), {
        status: 200,
        headers: { "content-type": "application/json" },
      });
    }) as typeof fetch;
  });

  afterEach(() => {
    for (const key of ENV_KEYS) {
      if (prev[key] === undefined) delete process.env[key];
      else process.env[key] = prev[key];
    }
    if (originalFetch) globalThis.fetch = originalFetch;
  });

  test("unset URL does not fetch and disables badges", async () => {
    process.env.SHOP_BLOB_READ_WRITE_TOKEN = BLOB_TOKEN;
    const response = await GET();
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), { enabled: false, items: {} });
    assert.equal(fetchCalls.length, 0);
    assert.equal(response.headers.get("cache-control"), "no-store");
  });

  test("reads the public URL with no-store and no token", async () => {
    process.env.LISTING_STATUS_URL = `  ${STATUS_URL}  `;
    process.env.SHOP_BLOB_READ_WRITE_TOKEN = BLOB_TOKEN;
    const response = await GET();
    assert.equal(response.status, 200);
    const body = (await response.json()) as {
      enabled: boolean;
      items: { A17: { priceUsd: number }; A22: { reasons: { vi: string }[] } };
    };
    assert.equal(body.enabled, true);
    assert.equal(body.items.A17.priceUsd, 25);
    assert.equal(body.items.A22.reasons[0].vi, PHOTO_VI);
    assert.equal(fetchCalls.length, 1);
    assert.equal(fetchCalls[0].url, STATUS_URL);
    assert.equal(fetchCalls[0].init.cache, "no-store");
    assert.ok(fetchCalls[0].init.signal instanceof AbortSignal);
    const headers = new Headers(fetchCalls[0].init.headers);
    assert.equal(headers.get("authorization"), null);
    assert.equal(JSON.stringify(body).includes(BLOB_TOKEN), false);
  });

  test("500, timeout, and bad JSON hide badges with a distinct error", async () => {
    process.env.LISTING_STATUS_URL = STATUS_URL;
    const hidden = { enabled: false, error: true, items: {} };
    globalThis.fetch = (async () => new Response("nope", { status: 500 })) as typeof fetch;
    const failed = await GET();
    assert.equal(failed.status, 200);
    assert.deepEqual(await failed.json(), hidden);

    globalThis.fetch = (async () => {
      throw new DOMException("The operation was aborted.", "TimeoutError");
    }) as typeof fetch;
    const timedOut = await GET();
    assert.equal(timedOut.status, 200);
    assert.deepEqual(await timedOut.json(), hidden);

    globalThis.fetch = (async () => new Response("not-json", { status: 200 })) as typeof fetch;
    const bad = await GET();
    assert.equal(bad.status, 200);
    assert.deepEqual(await bad.json(), hidden);
    assert.equal(listingStatusFromApi(hidden).enabled, false);
  });
});

test("listing status route and client UI do not touch the shop blob token or webhook secrets", () => {
  const route = fs.readFileSync(path.join(process.cwd(), "app/api/listing-status/route.ts"), "utf8");
  assert.equal(route.includes("SHOP_BLOB"), false);
  assert.equal(route.includes("put("), false);
  const clientFiles = [
    "components/IntakeApp.tsx",
    "components/SavedCard.tsx",
    "components/FindMaCard.tsx",
    "app/page.tsx",
  ];
  for (const file of clientFiles) {
    const source = fs.readFileSync(path.join(process.cwd(), file), "utf8");
    assert.equal(source.includes("NEW_MA_WEBHOOK_URL"), false, file);
    assert.equal(source.includes("NEW_MA_WEBHOOK_TOKEN"), false, file);
    assert.equal(source.includes("LISTING_STATUS_URL"), false, file);
    assert.equal(source.includes("SHOP_BLOB_READ_WRITE_TOKEN"), false, file);
  }
});

function sampleFile() {
  return {
    version: 1,
    generatedAt: "2026-09-28T08:12:10Z",
    run: "20260928T081201Z",
    items: {
      A17: { state: "live", priceUsd: 25, url: "https://sassycloset.vercel.app/m/A17" },
      A22: {
        state: "held",
        since_run: "20260928T081046Z",
        reasons: [{ code: "photo_text", vi: PHOTO_VI }],
      },
    },
  };
}
