import assert from "node:assert/strict";
import test from "node:test";
import { NextRequest } from "next/server";
import { HELD_INCOMPLETE_MAS } from "../lib/held-incomplete";
import { proxy } from "../proxy";

const held = HELD_INCOMPLETE_MAS[0]!;

/** Each folder character as %HH. encodeURIComponent leaves ASCII letters and digits alone. */
function percentFolder(folder: string): string {
  return [...folder]
    .map((char) => `%${char.charCodeAt(0).toString(16).padStart(2, "0").toUpperCase()}`)
    .join("");
}

function get(pathname: string): Response {
  return proxy(new NextRequest(`http://127.0.0.1${pathname}`, { method: "GET" }));
}

async function assertOffLiveImage(pathname: string): Promise<void> {
  const response = get(pathname);
  assert.equal(response.status, 404, pathname);
  assert.equal(await response.text(), "Not found", pathname);
  assert.match(response.headers.get("cache-control") ?? "", /no-store/, pathname);
  assert.equal(response.headers.get("location"), null, pathname);
}

test("proxy 404s a held product image before any redirect", async () => {
  await assertOffLiveImage(`/products/${held}/cover.jpg`);
  await assertOffLiveImage(`/products/${held.toLowerCase()}/cover.jpg`);
  await assertOffLiveImage(`/products/${held[0] + "0" + held.slice(1)}/cover.jpg`);
  await assertOffLiveImage(`/products/${percentFolder(held)}/cover.jpg`);
  await assertOffLiveImage(`/products/A01/../${held}/cover.jpg`);
  await assertOffLiveImage(`/products/${held}%2Fcover.jpg`);
  await assertOffLiveImage(`/products/${held}%2fcover.jpg`);
});

test("proxy 308s a short live product image spelling to the canonical folder", () => {
  const response = get("/products/a1/cover.jpg");
  assert.equal(response.status, 308);
  const location = response.headers.get("location");
  assert.ok(location);
  assert.equal(new URL(location, "http://127.0.0.1").pathname, "/products/A01/cover.jpg");
});

test("canonical live images and held product pages are not the image 404", () => {
  for (const pathname of ["/products/A01/cover.jpg", `/m/${held}`]) {
    const response = get(pathname);
    assert.notEqual(response.status, 404, pathname);
    assert.notEqual(response.status, 308, pathname);
  }
});

test("a malformed product image percent-escape does not throw and is not the off-live 404", () => {
  let response: Response | undefined;
  assert.doesNotThrow(() => {
    response = get("/products/%E0%A4%A/cover.jpg");
  });
  assert.ok(response);
  assert.notEqual(response.status, 404);
});
