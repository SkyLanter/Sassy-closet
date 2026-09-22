import { readFileSync } from "node:fs";
import path from "node:path";
import { mergeAddFields, messageReadyAddFields } from "../lib/admin-add";
import { KNOWN_SEED_MAS } from "../lib/catalog-contract";
import { htmlHasNextMaTrap, INVENTED_NEXT_MAS, nextMaTrapLabel } from "../lib/next-ma-trap";
import { messengerHref } from "../lib/messenger";
import { parseCatalogDocument } from "../lib/product-parse";
import { saveConfirmLine } from "../lib/save-confirm";
import { VERCEL_SERVER_ACTION_MAX_BYTES, uploadTooLargeError } from "../lib/upload-limits";

function fail(message: string): never {
  throw new Error(message);
}

const root = process.cwd();

function read(rel: string): string {
  return readFileSync(path.join(root, rel), "utf8");
}

const itemForm = read("app/admin/item-form.tsx");
const catalogList = read("app/admin/catalog-list.tsx");
const consoleText = read("app/admin/console.tsx");
const frame = read("app/admin/frame.tsx");
const actions = read("app/admin/actions.ts");
const imageFields = read("app/admin/image-fields.tsx");
const settings = read("app/admin/settings-panel.tsx");
const productCard = read("components/product-card.tsx");
const messengerCta = read("components/messenger-cta.tsx");
const refresh = read("lib/refresh-shop.ts");

if (itemForm.includes("Add <MaMark ma={predictedMa}")) {
  fail("Add heading must not print Add {next mã} trap tiles");
}
if (itemForm.includes("→ {nextMaForLetter")) {
  fail("Letter picker must not print → Q01 / → D01 invent-mã labels");
}
if (!itemForm.includes('"Add mã"') && !itemForm.includes(">Add mã<") && !itemForm.includes("Add mã")) {
  fail("Add form must stay open as Add mã");
}
if (!itemForm.includes("Assigned on Save") || !itemForm.includes("not a shop tile")) {
  fail("Add must say assigned on Save — not a shop tile");
}
if (!itemForm.includes("Save new mã")) {
  fail("Add submit must be Save new mã, not Add A03");
}
if (!itemForm.includes("admin-save-confirm") || !itemForm.includes("saveConfirmLine")) {
  fail("Save must show mã + status + $ or Hold on the sticky bar");
}
if (itemForm.includes("if (!window.confirm(saveConfirmPrompt(confirmLine)))")) {
  fail("Add/Edit Save must not native-confirm — dismiss is a silent fail");
}
if (!itemForm.includes("never write on hand")) {
  fail("Copy hint must forbid warehouse “on hand” voice");
}
if (saveConfirmLine("A01", "available", 25) !== "Save A01 · Available · $25") {
  fail("Save confirm must name A01 Available $25");
}
if (saveConfirmLine("P05", "hold", null) !== "Save P05 · Hold · Inbox for price") {
  fail("Save confirm must name P05 Hold · Inbox for price");
}
if (!itemForm.includes("uploadOverServerActionLimit")) {
  fail("Add/Edit must refuse >4.5 MB uploads in the client before the Server Action");
}

const adminSources = `${itemForm}\n${catalogList}\n${consoleText}`;
const traps = htmlHasNextMaTrap(adminSources);
if (traps.length > 0) {
  fail(`Admin source still advertises trap tiles: ${traps.join(", ")}`);
}
for (const ma of INVENTED_NEXT_MAS) {
  if (adminSources.includes(nextMaTrapLabel(ma))) {
    fail(`Admin source contains ${nextMaTrapLabel(ma)}`);
  }
}

if (!frame.includes('data-next-ma-trap="off"') || !frame.includes('data-allowlist-tiles="hub-ten"')) {
  fail("Admin frame must mark next-mã trap off + hub-ten tiles");
}
if (!frame.includes('data-save-contract="blob+revalidate"')) {
  fail("Save contract marker must stay");
}
if (!refresh.includes('revalidatePath("/m/[ma]", "page")')) {
  fail("Save must revalidatePath PDP");
}
if (!actions.includes("uploadOverServerActionLimit")) {
  fail("uploadImageAction must use the 4.5 MB Server Action cap");
}
if (!imageFields.includes('data-upload-limit="4.5mb-server-action"')) {
  fail("Image fields must expose the 4.5 MB upload limit");
}
if (!settings.includes('data-catalog-export="json"')) {
  fail("Settings must expose catalog.v1 JSON export");
}
const addApi = read("app/api/admin/add/route.ts");
if (!addApi.includes("addProductToCatalog") || !addApi.includes("commitProductList")) {
  fail("POST /api/admin/add must Add A03+ and commit Blob");
}
if (!addApi.includes("mergeAddFields")) {
  fail("POST /api/admin/add must merge Message-ready Hold fields before Blob commit");
}
if (!addApi.includes("adminMethodNotAllowed")) {
  fail("GET /api/admin/add must be 405, never a missing route");
}
if (!actions.includes("mergeAddFields") || !actions.includes("commitProductList")) {
  fail("addProductAction must merge Add fields and commit Blob");
}
if (!itemForm.includes("postAdminAdd") || !itemForm.includes("postAdminSave") || !itemForm.includes("postAdminRename") || !itemForm.includes("postAdminRemove")) {
  fail("Add/Save/Change mã/Remove must POST JSON receipts, not a Server Action (RSC #441)");
}
if (itemForm.includes("addProductAction") || itemForm.includes("saveProductAction") || itemForm.includes("renameProductAction") || itemForm.includes("removeProductAction")) {
  fail("item-form must not call Server Actions for catalog writes (RSC #441 after Blob write)");
}
if (!itemForm.includes("isOpaqueRscError") || !itemForm.includes("opaquePostSaveMessage")) {
  fail("Save errors must never toast React #441");
}
if (!consoleText.includes("/admin/edit/${options.nextMa}") || consoleText.includes("router.refresh();\n                  return")) {
  fail("Add receipt must soft-navigate to edit without refreshing /admin/new");
}
if (!refresh.includes("after(")) {
  fail("Admin path revalidate must run after the JSON response");
}
const clientSave = read("lib/admin-client-save.ts");
if (!clientSave.includes('"/api/admin/add"') || !clientSave.includes("recoverAddedMa")) {
  fail("Add client must POST /api/admin/add and recover the mã if the flight dies");
}
if (!clientSave.includes("recoverExistingMaSave") || !clientSave.includes("isRecoverableSaveTransportError")) {
  fail("Edit Save must recover from catalog GET when the POST receipt is opaque");
}
const messengerLib = read("lib/messenger.ts");
if (messengerLib.includes("text=") || messengerLib.includes("ref=") || messengerLib.includes("encodeURIComponent")) {
  fail("messengerHref must never compose ?text= or ?ref=");
}
const shipDraft = read("components/ship-draft-form.tsx");
if (shipDraft.includes("messengerHref(facebookPageUrl,") || shipDraft.includes("refMa")) {
  fail("Ship-draft Open Messenger must be a plain Page chat; copy stays on the clipboard button");
}
if (
  !clientSave.includes('"/api/admin/rename"') ||
  !clientSave.includes('"/api/admin/remove"') ||
  !clientSave.includes('"/api/admin/settings"') ||
  !clientSave.includes('"/api/admin/hold"')
) {
  fail("Rename / Remove / Settings / Hold must POST JSON receipts");
}
if (catalogList.includes("bulkHoldAction") || settings.includes("saveSettingsAction") || settings.includes("importCatalogAction")) {
  fail("Catalog Hold and Settings must not use Server Actions (RSC #441 after Blob write)");
}
if (!catalogList.includes("postAdminHold") || !settings.includes("postAdminSettings") || !settings.includes("postAdminImport")) {
  fail("Hold / Settings / Import must use JSON receipts");
}

const addStarter = messageReadyAddFields("A");
if (addStarter.sourceLink !== null || addStarter.priceUsd !== null || addStarter.status !== "hold") {
  fail("Add starter must be Hold with no invented $ or staff link");
}
if (addStarter.descriptionEn !== "" || addStarter.descriptionVn !== "") {
  fail("Add starter must not invent a garment description");
}
const mergedEmpty = mergeAddFields("A", { titleEn: "  " });
if (mergedEmpty.titleEn !== addStarter.titleEn || mergedEmpty.sourceLink !== null) {
  fail("Empty Add titles must keep the letter starter and must not invent a staff link");
}
if (!productCard.includes("MessengerCta") || !productCard.includes('variant="card"')) {
  fail("Product cards must open Messenger with mã (outside the PDP Link)");
}
if (messengerCta.includes("suggestedMessage") || messengerCta.includes("text=") || messengerCta.includes("refMa")) {
  fail("Messenger CTAs must open a plain m.me chat — no composed ?text= / ref=");
}
if (!messengerCta.includes("data-messenger-ref") || !messengerCta.includes("messengerHref(facebookPageUrl)")) {
  fail("Message still labels the mã; the href is the Page chat only");
}

const page = "https://www.facebook.com/profile.php?id=61594312648057";
const href = messengerHref(page);
if (href !== "https://m.me/61594312648057") {
  fail(`Product m.me must be a plain Page chat, got ${href}`);
}
if (href.includes("text=") || href.includes("ref=") || href.includes("?")) {
  fail(`Product m.me must not prefill text or ref, got ${href}`);
}

if (VERCEL_SERVER_ACTION_MAX_BYTES < 4_000_000 || VERCEL_SERVER_ACTION_MAX_BYTES > 4_800_000) {
  fail(`Server Action upload cap drifted: ${VERCEL_SERVER_ACTION_MAX_BYTES}`);
}
if (!uploadTooLargeError(5 * 1024 * 1024).includes("4.5 MB")) {
  fail("Oversize upload error must name the 4.5 MB cap");
}

const seed = parseCatalogDocument(
  JSON.parse(readFileSync(path.join(root, "data/products.json"), "utf8")) as unknown,
);
const seedMas = seed.products.map((product) => product.ma);
if (seedMas.join(",") !== KNOWN_SEED_MAS.join(",")) {
  fail(`Seed must stay the hub ten, got ${seedMas.join(" ")}`);
}
const p02 = seed.products.find((product) => product.ma === "P02");
const p05 = seed.products.find((product) => product.ma === "P05");
if (!p02 || !p05 || p02.status !== "hold" || p05.status !== "hold" || p02.priceUsd !== null || p05.priceUsd !== null) {
  fail("P02/P05 must stay Hold with no USD");
}
if (seed.products.some((product) => product.ma === "Q01" || product.ma === "D01")) {
  fail("Seed must not invent Q01/D01 for empty categories");
}

const chips = read("components/color-name-chips.tsx");
if (chips.includes("backgroundColor") || chips.includes("color.hex")) {
  fail("Shop colors stay text-only names (hex discs are admin-only)");
}

console.log("kit-lane #29 apply ok");
