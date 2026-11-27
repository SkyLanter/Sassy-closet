import assert from "node:assert/strict";
import { afterEach, test } from "node:test";
import { fetchTaobaoItem } from "../lib/taobao";

const LISTING = `<html><head><title>韩版针织</title></head><body>${"x".repeat(2400)}</body></html>`;
const LEAKED = `<html><head><title>secret</title></head><body>${"y".repeat(2400)}</body></html>`;

let restoreFetch: (() => void) | null = null;

afterEach(() => {
  restoreFetch?.();
  restoreFetch = null;
});

test("does not fetch an empty link, a non-shop host, or a huge paste of one", async () => {
  const seen = mockFetch(() => new Response(LEAKED, { status: 200 }));
  const empty = await fetchTaobaoItem("   \n\t  ");
  const local = await fetchTaobaoItem("http://127.0.0.1/latest/meta-data/");
  const lookalike = await fetchTaobaoItem("https://item.taobao.com.evil.test/item.htm?id=987654321098");
  const huge = await fetchTaobaoItem(`${"xem ".repeat(20_000)}http://127.0.0.1/secret`);
  assert.equal(empty.ok, false);
  assert.equal(local.ok, false);
  assert.equal(lookalike.ok, false);
  assert.equal(huge.ok, false);
  assert.deepEqual(seen.urls, []);
});

test("does not follow a Taobao redirect onto another host", async () => {
  const seen = mockFetch((url) => {
    if (url.includes("127.0.0.1")) return new Response(LEAKED, { status: 200 });
    return new Response(null, {
      status: 302,
      headers: { location: "http://127.0.0.1/secret" },
    });
  });
  const result = await fetchTaobaoItem("https://item.taobao.com/item.htm?id=987654321098");
  assert.equal(result.ok, false);
  assert.equal(seen.urls.some((url) => url.includes("127.0.0.1")), false);
  assert.ok(seen.urls.every((url) => isShopHost(url)));
});

test("still fetches a Taobao item link, including one pasted with Vietnamese around it", async () => {
  const seen = mockFetch((url) => {
    if (url.startsWith("https://e.tb.cn/")) {
      return new Response(null, {
        status: 302,
        headers: { location: "https://item.taobao.com/item.htm?id=987654321098" },
      });
    }
    return new Response(LISTING, { status: 200 });
  });
  const direct = await fetchTaobaoItem("https://item.taobao.com/item.htm?id=987654321098");
  const pasted = await fetchTaobaoItem(
    "Xem đồ https://item.taobao.com/item.htm?id=987654321098 nha",
  );
  const shortLink = await fetchTaobaoItem("https://e.tb.cn/h.short01");
  assert.equal(direct.ok, true);
  assert.equal(pasted.ok, true);
  assert.equal(shortLink.ok, true);
  if (shortLink.ok) assert.equal(shortLink.item.itemId, "987654321098");
  assert.ok(seen.urls.length > 0);
  assert.ok(seen.urls.every((url) => isShopHost(url)));
});

function isShopHost(raw: string): boolean {
  const host = new URL(raw).hostname;
  return /(^|\.)(tb\.cn|taobao\.com|tmall\.com)$/i.test(host);
}

function mockFetch(handler: (url: string, init: RequestInit | undefined) => Response) {
  const urls: string[] = [];
  const previous = globalThis.fetch;
  const wrapped: typeof fetch = async (input, init) => {
    const url = String(input);
    urls.push(url);
    const response = handler(url, init);
    if (init?.redirect === "follow" && response.status >= 300 && response.status < 400) {
      const location = response.headers.get("location");
      if (location) return wrapped(new URL(location, url).href, init);
    }
    return response;
  };
  globalThis.fetch = wrapped;
  restoreFetch = () => {
    globalThis.fetch = previous;
  };
  return { urls };
}
