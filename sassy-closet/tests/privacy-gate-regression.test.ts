import assert from "node:assert/strict";
import test from "node:test";

// piece-270: lock unauthenticated privacy behavior for intake routes.
// Every gated route must 401 with no cost/source/link leak, in both 401 modes.
const LEAK = /cost_cny|cost_usd|costCny|costUsd|source_?link|sourceLink|taobao|supplier|\bnhung\b|@[a-z0-9-]+\.[a-z]/i;
const MODES: Array<[string, string | undefined]> = [["json-default", undefined], ["json-0", "0"], ["empty-1", "1"], ["empty-true", "true"]];

async function routes() {
  const list = await import("../app/api/submissions/route");
  const one = await import("../app/api/submissions/[ma]/route");
  const exp = await import("../app/api/export/route");
  const ma = await import("../app/api/ma/[code]/route");
  const maCtx = { params: Promise.resolve({ ma: "S06" }) };
  const codeCtx = { params: Promise.resolve({ code: "S06" }) } as never;
  const fd = () => { const f = new FormData(); f.set("ma", "S06"); f.set("sell_usd", "25"); return f; };
  const json = () => JSON.stringify({ ma: "S06", sell_usd: 25 });
  const req = (method: string, body?: BodyInit, ct?: string) =>
    new Request("http://l/", { method, body, headers: ct ? { "content-type": ct } : undefined });
  return [
    ["GET /api/export", () => exp.GET(req("GET"))],
    ["GET /api/submissions", () => list.GET(req("GET"))],
    ["POST /api/submissions form", () => list.POST(req("POST", fd()))],
    ["POST /api/submissions json", () => list.POST(req("POST", json(), "application/json"))],
    ["GET /api/submissions/[ma]", () => one.GET(req("GET"), maCtx)],
    ["PATCH /api/submissions/[ma] form", () => one.PATCH(req("PATCH", fd()), maCtx)],
    ["PATCH /api/submissions/[ma] json", () => one.PATCH(req("PATCH", json(), "application/json"), maCtx)],
    ["GET /api/ma/[code]", () => ma.GET(req("GET"), codeCtx)],
  ] as Array<[string, () => Promise<Response>]>;
}

for (const [label, env] of MODES) {
  test(`unauthenticated intake routes 401 with no leak (${label})`, async () => {
    const saved = { ...process.env };
    try {
      if (env === undefined) delete process.env.SHOP_ADMIN_401_EMPTY;
      else process.env.SHOP_ADMIN_401_EMPTY = env;
      const empty = env === "1" || env === "true";
      for (const [name, call] of await routes()) {
        const res = await call();
        assert.equal(res.status, 401, name);
        const text = await res.text();
        assert.doesNotMatch(text, LEAK, `${name} leaked`);
        assert.match(res.headers.get("cache-control") ?? "", /no-store/, name);
        assert.equal(res.headers.get("set-cookie"), null, name);
        if (empty) assert.equal(text, "", name);
        else assert.deepEqual(JSON.parse(text), { ok: false, error: "Unauthorized." }, name);
      }
    } finally { process.env = saved; }
  });
}
