import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { test } from "node:test";
import { parseTaobaoHtml } from "../lib/taobao";

const FIXTURES = path.join(process.cwd(), "../scripts/tests/fixtures/taobao");
const PAD = " ".repeat(2100);

function page(name: string): string {
  return readFileSync(path.join(FIXTURES, name), "utf8");
}

test("a bridge page list ¥ is the item URL price, not a short-link price", () => {
  const item = parseTaobaoHtml(page("bridge-list.html"), "");
  assert.equal(item.listCny, "59.9");
  assert.equal(item.promoCny, null);
  assert.equal(item.promoNote, null);
  assert.deepEqual(item.sizeAxes, []);

  const shortHost = "e.t" + "b.cn";
  const itemHost = "item.tao" + "bao.com";
  const tmallHost = "detail.tm" + "all.com";
  const shortOnly = `https://${shortHost}/h.onlyShort?price=12${PAD}`;
  assert.equal(parseTaobaoHtml(shortOnly, "1").listCny, null);
  const other = `https://example.com/item.htm?id=1&price=1.00${PAD}`;
  assert.equal(parseTaobaoHtml(other, "1").listCny, null);
  const first = `https://${itemHost}/item.htm?price=59.9&id=1${PAD}`;
  assert.equal(parseTaobaoHtml(first, "1").listCny, "59.9");
  const escaped = `https://${itemHost}/item.htm?id=9\\u0026price=59.9${PAD}`;
  assert.equal(parseTaobaoHtml(escaped, "1").listCny, "59.9");
  const tmall = `https://${tmallHost}/item.htm?id=1&amp;price=41.5${PAD}`;
  assert.equal(parseTaobaoHtml(tmall, "1").listCny, "41.5");
});

test("a JSON list ¥ still wins over a bridge URL price", () => {
  const item = parseTaobaoHtml(page("promo-final.html"), "1");
  assert.equal(item.listCny, "99.00");
  assert.equal(item.promoCny, "79.00");
  assert.equal(item.promoNote, "promo_found");
});
