const path = require("node:path");
const Module = require("node:module");
const { AsyncLocalStorage } = require("node:async_hooks");

// Next captures globalThis.AsyncLocalStorage when its storage module first loads.
// Route handlers call connection(), which needs that real store in tests.
if (!globalThis.AsyncLocalStorage) {
  globalThis.AsyncLocalStorage = AsyncLocalStorage;
}

const orig = Module._resolveFilename;
Module._resolveFilename = function resolveAlias(request, parent, isMain, options) {
  if (request.startsWith("@/")) {
    request = path.join(process.cwd(), request.slice(2));
  }
  return orig.call(this, request, parent, isMain, options);
};
