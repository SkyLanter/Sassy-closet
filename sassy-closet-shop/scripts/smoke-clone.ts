import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

function fail(message: string): never {
  throw new Error(message);
}

function read(rel: string): string {
  return readFileSync(path.join(process.cwd(), rel), "utf8");
}

const clone = read("docs/OFFICIAL_CLONE.md");
if (!clone.includes("sassy-closet-official") || !clone.includes("NEXT_PUBLIC_SITE_MODE")) {
  fail("OFFICIAL_CLONE.md must name official SITE_ID and SITE_MODE");
}
if (!clone.includes("sassy-closet.vercel.app") || !clone.includes("READ ONLY")) {
  fail("Clone doc must keep intake read-only");
}
if (!clone.includes("noindex") || !clone.includes("catalog:backup")) {
  fail("Clone doc must cover test noindex and catalog backup");
}
if (!clone.includes("m.me") || !clone.includes("?text=")) {
  fail("Clone doc must keep plain Messenger (no ?text=)");
}

const pointer = read("CLONE_TO_OFFICIAL.md");
if (!pointer.includes("docs/OFFICIAL_CLONE.md")) {
  fail("CLONE_TO_OFFICIAL.md must point at docs/OFFICIAL_CLONE.md");
}

const env = read(".env.example");
for (const name of [
  "SITE_ID",
  "NEXT_PUBLIC_SITE_ID",
  "NEXT_PUBLIC_SITE_MODE",
  "NEXT_PUBLIC_SHOP_URL",
  "NEXT_PUBLIC_MESSENGER_URL",
  "BLOB_READ_WRITE_TOKEN",
  "KV_REST_API_URL",
  "KV_REST_API_TOKEN",
]) {
  if (!env.includes(name)) {
    fail(`.env.example missing ${name}`);
  }
}
if (env.includes("ADMIN_PASSWORD=")) {
  fail("Do not add ADMIN_PASSWORD to the official clone template");
}

const pkg = read("package.json");
if (!pkg.includes("catalog:backup") || !pkg.includes("smoke:clone")) {
  fail("package.json must expose catalog:backup and smoke:clone");
}

if (!existsSync(path.join(process.cwd(), "scripts/backup-catalog.ts"))) {
  fail("catalog backup script missing");
}
if (!existsSync(path.join(process.cwd(), "app/api/admin/catalog/export/route.ts"))) {
  fail("catalog export route missing");
}
if (!existsSync(path.join(process.cwd(), "app/api/admin/catalog/import/route.ts"))) {
  fail("catalog import route missing");
}

const settings = read("app/admin/settings-panel.tsx");
if (!settings.includes("Export catalog.v1") || !settings.includes("Import catalog.v1")) {
  fail("Admin settings must keep catalog export/import");
}
if (!settings.includes("assertImportableHandoffJson")) {
  fail("Admin import must validate catalog.v1 before POST");
}

const backup = read("scripts/backup-catalog.ts");
if (!backup.includes("assertHandoffJson")) {
  fail("catalog backup must validate catalog.v1 before write");
}
const exportRoute = read("app/api/admin/catalog/export/route.ts");
if (!exportRoute.includes("assertHandoffJson")) {
  fail("catalog export must validate catalog.v1 before download");
}
const clientSave = read("lib/admin-client-save.ts");
if (!clientSave.includes("assertHandoffExportText") || !clientSave.includes("requireShop")) {
  fail("Admin export/import client must reject HTML exports and require shop revalidate");
}
if (!read("lib/handoff-json.ts").includes("assertImportableHandoffJson")) {
  fail("Import must validate catalog.v1 shape before POST");
}

console.log("official clone template ok");
