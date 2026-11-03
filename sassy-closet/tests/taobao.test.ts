import assert from "node:assert/strict";
import { test } from "node:test";
import {
  extractItemId,
  isTaobaoItem,
  looksBlocked,
  parseTaobaoHtml,
} from "../lib/taobao";

const FIXTURE = `
<html><head>
<meta property="og:title" content="韩版宽松针织开衫女秋冬" />
<meta property="og:image" content="//img.alicdn.com/bao/uploaded/i1/1234567890/O1CN01abc.jpg" />
<title>韩版宽松针织开衫 -淘宝网</title>
</head><body>
<script>
var g_config = {};
window.__INIT_DATA__ = {"skuBase":{
"props":[
{"pid":"1627207","name":"颜色分类","values":[{"vid":"1","name":"杏色"},{"vid":"2","name":"黑色"},{"vid":"3","name":"米白色"}]},
{"pid":"20509","name":"尺码","values":[{"vid":"10","name":"S"},{"vid":"11","name":"M"},{"vid":"12","name":"L"}]}
],
"defaultItemPrice":"68.00","promoPrice":"59.90",
"auctionImages":["//img.alicdn.com/bao/uploaded/i2/1234567890/O1CN01def.jpg","//img.alicdn.com/bao/uploaded/i3/1234567890/O1CN01ghi.png"]
}};
</script>
<!-- pad: real Taobao pages are 100KB+; looksBlocked treats tiny pages as blocked -->
<div style="display:none">${"x".repeat(2400)}</div>
</body></html>
`;

test("extractItemId finds numeric ids from taobao urls and share text", () => {
  assert.equal(extractItemId("https://item.taobao.com/item.htm?id=987654321098"), "987654321098");
  assert.equal(extractItemId("https://e.tb.cn/h.xxx?x=1"), null);
  assert.equal(
    extractItemId("快来看看 https://m.tb.cn/h.gAbCdEf?tk=xyz 复制整段到淘宝"),
    null,
  );
  assert.equal(extractItemId("https://detail.tmall.com/item.htm?id=123456789012&skuId=1"), "123456789012");
});

test("looksBlocked flags short, login-wall and block pages", () => {
  assert.equal(looksBlocked(""), true);
  assert.equal(looksBlocked("too short"), true);
  assert.equal(looksBlocked(`${"x".repeat(3000)}亲，访问受限，请稍后再试`), true);
  assert.equal(
    looksBlocked(`${"x".repeat(3000)}window.location.href="https://login.taobao.com/member/login.jhtml"`),
    true,
  );
  assert.equal(looksBlocked(FIXTURE), false);
});

test("parseTaobaoHtml extracts seller-truth colors, size axes, prices, gallery", () => {
  const item = parseTaobaoHtml(FIXTURE, "987654321098");
  assert.equal(item.itemId, "987654321098");
  assert.ok(item.title.includes("针织开衫"));
  // Seller colors are kept in Chinese, never translated.
  assert.deepEqual(item.colors, ["杏色", "黑色", "米白色"]);
  assert.deepEqual(item.sizeAxes, [{ name: "尺码", values: ["S", "M", "L"] }]);
  assert.equal(item.listCny, "68.00");
  assert.equal(item.promoCny, "59.90");
  assert.equal(item.promoNote, "promo_found");
  assert.ok(item.gallery.length >= 2);
  assert.ok(item.gallery.every((url) => url.startsWith("https://")));
  assert.ok(isTaobaoItem(item));
});

test("parseTaobaoHtml notes pre-promo (优惠前) prices", () => {
  const html = FIXTURE.replace('"promoPrice":"59.90",', "").replace(
    "</script>",
    '<div>优惠前价格 ¥68.00</div></script>',
  );
  const item = parseTaobaoHtml(html, "1");
  assert.equal(item.listCny, "68.00");
  assert.equal(item.promoCny, null);
  assert.equal(item.promoNote, "pre_promo");
});

test("parseTaobaoHtml never invents: empty page gives empty fields", () => {
  const item = parseTaobaoHtml("<html><head><title>t</title></head><body></body></html>", "1");
  assert.deepEqual(item.colors, []);
  assert.deepEqual(item.sizeAxes, []);
  assert.deepEqual(item.gallery, []);
  assert.equal(item.listCny, null);
  assert.equal(item.promoCny, null);
  assert.equal(item.promoNote, null);
});
