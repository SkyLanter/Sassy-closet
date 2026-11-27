import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";

/**
 * A route that parses JSON must treat any non-object body as bad input.
 * `JSON.parse("null")` succeeds and `await request.json()` resolves to null, so
 * `body.secret` and `body.question` threw a TypeError out of the handler and
 * Next answered 500 for what is really a 400.
 *
 * `/api/find-ma` reads form data; a JSON body or no body at all is not a form,
 * and calling `request.formData()` on it threw before the route could answer.
 *
 * Both routes are answerable by anyone with the direct link, so a crafted POST
 * must not crash them. Placeholders only: no real cost, link, or secret.
 */
const ENV_KEYS = ["SASSY_DATA_DIR", "ASK_REPLY_SECRET", "BLOB_READ_WRITE_TOKEN", "BLOB_STORE_ID", "VERCEL"];

function withCleanEnv(run: (tmp: string) => Promise<void>): Promise<void> {
  const saved: Record<string, string | undefined> = {};
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "intake-body-"));
  for (const key of ENV_KEYS) {
    saved[key] = process.env[key];
    delete process.env[key];
  }
  process.env.SASSY_DATA_DIR = tmp;
  return run(tmp).finally(() => {
    for (const key of ENV_KEYS) {
      if (saved[key] === undefined) delete process.env[key];
      else process.env[key] = saved[key];
    }
    fs.rmSync(tmp, { recursive: true, force: true });
  });
}

function jsonRequest(body: string): Request {
  return new Request("http://l/x", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body,
  });
}

test("/api/ask/reply answers 400/401 for every JSON body shape, never throws", async () => {
  await withCleanEnv(async () => {
    const { resetStoreBackendForTests } = await import("../lib/store-backend");
    resetStoreBackendForTests();
    const { POST } = await import("../app/api/ask/reply/route");
    process.env.ASK_REPLY_SECRET = ["test", "reply", "secret"].join("-");
    for (const body of ["null", "[]", "5", '"text"', "{}", "true", '{"secret":null}', '{"id":null,"answer":null}']) {
      const res = await POST(jsonRequest(body));
      assert.equal(res.status, 401, `${body} has no valid secret`);
      assert.match(await res.text(), /Unauthorized/);
    }
    // A wrong secret on a well-formed body is still 401, not 500.
    const wrong = await POST(jsonRequest(JSON.stringify({ id: "x", answer: "y", secret: "nope" })));
    assert.equal(wrong.status, 401);
  });
});

test("/api/ask/reply still accepts the configured secret and answers a missing id", async () => {
  await withCleanEnv(async () => {
    const { resetStoreBackendForTests } = await import("../lib/store-backend");
    resetStoreBackendForTests();
    const { POST } = await import("../app/api/ask/reply/route");
    const secret = ["test", "reply", "secret"].join("-");
    process.env.ASK_REPLY_SECRET = secret;
    const res = await POST(jsonRequest(JSON.stringify({ id: "not-an-ask", answer: "hi", secret })));
    assert.equal(res.status, 404);
    assert.match(await res.text(), /Ask id/);
  });
});

test("/api/find-ma answers 400 when the body is not a photo form", async () => {
  await withCleanEnv(async () => {
    const { resetStoreBackendForTests } = await import("../lib/store-backend");
    resetStoreBackendForTests();
    const { POST } = await import("../app/api/find-ma/route");
    const notForms: Array<[string, Request]> = [
      ["no body", new Request("http://l/x", { method: "POST" })],
      ["json body", jsonRequest("{}")],
      ["text body", new Request("http://l/x", { method: "POST", headers: { "content-type": "text/plain" }, body: "hi" })],
      ["json array", jsonRequest("[]")],
    ];
    for (const [label, request] of notForms) {
      const res = await POST(request);
      assert.equal(res.status, 400, label);
      const body = (await res.json()) as { error: string; error_en?: string };
      assert.match(body.error, /Chưa nhận được ảnh/, label);
    }
  });
});

test("/api/find-ma still searches a real photo form and still rejects a form with no photo", async () => {
  await withCleanEnv(async () => {
    const { resetStoreBackendForTests } = await import("../lib/store-backend");
    resetStoreBackendForTests();
    const { POST } = await import("../app/api/find-ma/route");
    const empty = new FormData();
    empty.set("note", "no photo here");
    const missing = await POST(new Request("http://l/x", { method: "POST", body: empty }));
    assert.equal(missing.status, 400);

    const form = new FormData();
    form.set("photo", new File([new Uint8Array([1, 2, 3, 4])], "photo.jpg", { type: "image/jpeg" }));
    const found = await POST(new Request("http://l/x", { method: "POST", body: form }));
    assert.equal(found.status, 200);
    assert.deepEqual(await found.json(), { matches: [] });
  });
});
