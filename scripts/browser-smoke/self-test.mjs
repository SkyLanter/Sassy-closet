/**
 * Local stub for the read-only browser smoke. No live hosts.
 * A good fixture passes. Each broken fixture fails on its own.
 * The stub records an /api/submissions handler the page must not call.
 */
import { spawn } from "node:child_process";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const DIR = path.dirname(fileURLToPath(import.meta.url));
const SENTINEL = "SENTINEL-COST-FIELD";

function html({ robots, price, offer, currency = "USD", sku = "S06" }) {
  return `<!doctype html><html><head>
<meta name="robots" content="${robots}">
<script type="application/ld+json">${JSON.stringify({
    "@type": "Product",
    sku,
    offers: { "@type": "Offer", priceCurrency: currency, price: offer },
  })}</script>
</head><body>
<span class="ky-pdp-price">${price}</span>
<p>related $99</p>
</body></html>`;
}

function home(robots) {
  return `<!doctype html><html><head><meta name="robots" content="${robots}"></head><body>home</body></html>`;
}

function listen(routes, seen) {
  const server = http.createServer((req, res) => {
    seen.push(`${req.method} ${req.url}`);
    const hit = routes[req.url] ?? { status: 404, body: "missing" };
    res.writeHead(hit.status, { "content-type": "text/html; charset=utf-8" });
    res.end(req.method === "HEAD" ? "" : hit.body);
  });
  return new Promise((resolve) => {
    server.listen(0, "127.0.0.1", () => resolve(server));
  });
}

function run(origin) {
  return new Promise((resolve) => {
    const child = spawn("node", ["smoke.mjs"], {
      cwd: DIR,
      env: {
        ...process.env,
        SHOP_HOSTS: origin,
        INTAKE_BASE: origin,
        HELD_MAS: "k3",
        CHECK_TIMEOUT: "10",
      },
    });
    let out = "";
    child.stdout.on("data", (chunk) => {
      out += chunk;
    });
    child.stderr.on("data", (chunk) => {
      out += chunk;
    });
    child.on("close", (code) => resolve({ code, out }));
  });
}

async function once(routes) {
  const seen = [];
  const server = await listen(
    {
      "/api/submissions": { status: 200, body: `{"${SENTINEL}":1}` },
      ...routes,
    },
    seen,
  );
  const origin = `http://127.0.0.1:${server.address().port}`;
  const result = await run(origin);
  server.close();
  return { ...result, seen };
}

function assertNoApi(result, label) {
  if (result.out.includes(SENTINEL) || result.seen.some((line) => line.includes("/api/"))) {
    console.error(result.out);
    console.error(result.seen.join("\n"));
    console.error(`${label} touched /api/`);
    process.exit(1);
  }
  if (result.seen.some((line) => !line.startsWith("GET ") && !line.startsWith("HEAD "))) {
    console.error(result.seen.join("\n"));
    console.error(`${label} used a method other than GET`);
    process.exit(1);
  }
}

const goodDoc = html({ robots: "noindex, nofollow", price: "$25", offer: "25.00" });
const good = await once({
  "/": { status: 200, body: home("noindex, nofollow") },
  "/m/S06": { status: 200, body: goodDoc },
  "/m/K03": { status: 404, body: "held" },
});
assertNoApi(good, "good");
if (good.code !== 0 || !good.out.includes("BROWSER SMOKE: PASS") || !good.out.includes("S06 $25")) {
  console.error(good.out);
  console.error("self-test expected PASS");
  process.exit(1);
}

const cases = [
  [
    "wrong price",
    {
      "/": { status: 200, body: home("noindex, nofollow") },
      "/m/S06": { status: 200, body: html({ robots: "noindex, nofollow", price: "$16", offer: "25.00" }) },
      "/m/K03": { status: 404, body: "held" },
    },
  ],
  [
    "wrong currency",
    {
      "/": { status: 200, body: home("noindex, nofollow") },
      "/m/S06": {
        status: 200,
        body: html({ robots: "noindex, nofollow", price: "$25", offer: "25.00", currency: "EUR" }),
      },
      "/m/K03": { status: 404, body: "held" },
    },
  ],
  [
    "padded sku still the S06 offer",
    {
      "/": { status: 200, body: home("noindex, nofollow") },
      "/m/S06": {
        status: 200,
        body: html({ robots: "noindex, nofollow", price: "$25", offer: "25.00", sku: "S006" }),
      },
      "/m/K03": { status: 404, body: "held" },
    },
  ],
  [
    "held visible",
    {
      "/": { status: 200, body: home("noindex, nofollow") },
      "/m/S06": { status: 200, body: goodDoc },
      "/m/K03": { status: 200, body: "visible" },
    },
  ],
  [
    "missing noindex",
    {
      "/": { status: 200, body: home("index, follow") },
      "/m/S06": { status: 200, body: goodDoc },
      "/m/K03": { status: 404, body: "held" },
    },
  ],
];

for (const [label, routes] of cases) {
  const result = await once(routes);
  assertNoApi(result, label);
  const expectPass = label.startsWith("padded");
  if (expectPass) {
    if (result.code !== 0) {
      console.error(result.out);
      console.error(`self-test ${label} should PASS`);
      process.exit(1);
    }
    continue;
  }
  if (result.code === 0 || !result.out.includes("BROWSER SMOKE: FAIL")) {
    console.error(result.out);
    console.error(`self-test ${label} should FAIL`);
    process.exit(1);
  }
}

console.log("SELF-TEST: PASS");
