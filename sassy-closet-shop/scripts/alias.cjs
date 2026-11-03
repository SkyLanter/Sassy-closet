const path = require("node:path");
const Module = require("node:module");

const orig = Module._resolveFilename;
Module._resolveFilename = function resolveAlias(request, parent, isMain, options) {
  if (request.startsWith("@/")) {
    request = path.join(process.cwd(), request.slice(2));
  }
  return orig.call(this, request, parent, isMain, options);
};
