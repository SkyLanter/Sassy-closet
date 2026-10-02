import { createHash } from "node:crypto";
import { buildCaptionVi } from "./captions";
import { assertNever, isKindCode } from "./kinds";
import {
  type BackfillMode,
  NEVER_LIST_MAS,
  sellRewriteBlockReason,
} from "./intake-sell-backfill";
import { normalizeMa } from "./mint";
import { normalizeSourceLink } from "./source-link";
import { photoContentType, type StoreFile } from "./store-backend";
import type { Submission } from "./types";

/**
 * D05 is on the sell catalog and has no intake form. V03 was added through
 * saveSubmission (POST /api/submissions → saveFromForm). This seed fills that
 * same Submission shape from Blob title, price, photos, and source.
 *
 * Blob has no cost, Vietnamese color chip, Taobao snapshot, or auto price.
 * Those stay empty. The English catalog color name is not copied. Title VN
 * is stored in the existing `blurb` field. Photo bytes are copied only when
 * mode is "apply" and Boss says `BOSS_CONFIRM_D05_FORM`.
 */

export const BOSS_CONFIRM_D05_FORM = "Boss says: add the D05 intake form from Blob";

export const D05_MA = "D05";
export const D05_LOCKED_PRICE_USD = 26;

export type D05PhotoPlan = {
  src: string;
  rel: string;
  order: number;
};

export type D05SeedPlan = {
  mode: "dry-run";
  persisted: false;
  ok: boolean;
  reason: string | null;
  ma: "D05";
  titleVn: string;
  titleEn: string;
  priceUsd: number | null;
  sourceLink: string;
  size: string;
  photos: D05PhotoPlan[];
  blurb: string;
  color: "";
  sellUsd: string;
  price: string;
};

export type D05PhotoBytes = {
  bytes: Buffer;
  contentType: string;
};

export function planD05IntakeSeed(catalog: unknown, existingMas: readonly string[]): D05SeedPlan {
  const existing = new Set(existingMas.map((ma) => normalizeMa(ma)));
  if (existing.has(D05_MA)) return refused("D05 intake form already exists.");
  const product = readD05Product(catalog);
  if (!product.ok) return refused(product.reason);

  const photos = product.images.map((image) => ({
    src: image.src,
    rel: photoRel(D05_MA, image.order, image.src),
    order: image.order,
  }));
  return {
    mode: "dry-run",
    persisted: false,
    ok: true,
    reason: null,
    ma: D05_MA,
    titleVn: product.titleVn,
    titleEn: product.titleEn,
    priceUsd: D05_LOCKED_PRICE_USD,
    sourceLink: product.sourceLink,
    size: product.size,
    photos,
    blurb: product.titleVn,
    color: "",
    sellUsd: String(D05_LOCKED_PRICE_USD),
    price: String(D05_LOCKED_PRICE_USD),
  };
}

export function d05SubmissionFromPlan(
  plan: D05SeedPlan,
  input: { id: number; now: string; photoHashes: string[] },
): Submission {
  if (!plan.ok) throw new Error(plan.reason ?? "D05 seed plan is not ok.");
  if (plan.ma !== D05_MA || plan.priceUsd !== D05_LOCKED_PRICE_USD) {
    throw new Error("D05 seed plan is not the locked Blob form.");
  }
  if (input.photoHashes.length !== plan.photos.length) {
    throw new Error("D05 photo hashes do not match the Blob photos.");
  }
  const blocked = sellRewriteBlockReason(plan.ma);
  if (blocked) throw new Error(blocked);

  const submission: Submission = {
    id: input.id,
    ma: D05_MA,
    kind: "D",
    size: plan.size,
    color: "",
    color_note: "",
    pieces: [],
    link: plan.sourceLink,
    price: plan.price,
    cost_cny: "",
    cost_usd: "",
    cost_currency: "USD",
    sell_cny: "",
    sell_usd: plan.sellUsd,
    sell_currency: "USD",
    blurb: plan.blurb,
    photo_paths: plan.photos.map((photo) => photo.rel),
    photo_hashes: [...input.photoHashes],
    status: "staged",
    square: "not_square",
    needs_research: false,
    taobao_snapshot: null,
    auto_price: null,
    created_at: input.now,
    updated_at: input.now,
    caption_vi: "",
    caption_en: "",
    blurb_suggested: "",
    photo_link: `Documents/Sassy Closet/Photos/${D05_MA}/`,
  };
  submission.caption_vi = buildCaptionVi(submission);
  return submission;
}

export async function persistD05IntakeSeed(input: {
  mode: BackfillMode;
  confirmation: string;
  store: StoreFile;
  catalog: unknown;
  now: string;
  fetchPhoto: (url: string) => Promise<D05PhotoBytes>;
  writePhoto: (rel: string, bytes: Buffer, contentType: string) => Promise<void>;
  writeStore: (store: StoreFile) => Promise<void>;
}): Promise<{ persisted: boolean; plan: D05SeedPlan; store: StoreFile }> {
  const plan = planD05IntakeSeed(
    input.catalog,
    input.store.submissions.map((row) => row.ma),
  );
  switch (input.mode) {
    case "dry-run":
      return { persisted: false, plan, store: input.store };
    case "apply":
      break;
    default:
      return assertNever(input.mode, "unknown backfill mode");
  }

  if (input.confirmation !== BOSS_CONFIRM_D05_FORM) {
    throw new Error("Live write refused. Boss confirmation does not match.");
  }
  if (!plan.ok) throw new Error(plan.reason ?? "D05 seed plan is not ok.");
  if (input.store.submissions.some((row) => normalizeMa(row.ma) === D05_MA)) {
    throw new Error("D05 intake form already exists.");
  }

  const fetched: { photo: D05PhotoPlan; bytes: Buffer; contentType: string; hash: string }[] = [];
  for (const photo of plan.photos) {
    const file = await input.fetchPhoto(photo.src);
    if (file.bytes.length === 0) throw new Error(`D05 photo ${photo.src} was empty.`);
    if (!isImage(file)) throw new Error(`D05 photo ${photo.src} is not an image.`);
    fetched.push({
      photo,
      bytes: file.bytes,
      contentType: file.contentType || photoContentType(photo.rel),
      hash: createHash("sha256").update(file.bytes).digest("hex"),
    });
  }

  const submission = d05SubmissionFromPlan(plan, {
    id: nextSubmissionId(input.store),
    now: input.now,
    photoHashes: fetched.map((file) => file.hash),
  });
  assertD05InsertSafe(input.store, submission);
  const next: StoreFile = {
    ...input.store,
    nextId: submission.id + 1,
    submissions: [...input.store.submissions, submission],
  };

  for (const file of fetched) {
    await input.writePhoto(file.photo.rel, file.bytes, file.contentType);
  }
  await input.writeStore(next);
  return { persisted: true, plan, store: next };
}

type D05Product =
  | {
      ok: true;
      titleVn: string;
      titleEn: string;
      sourceLink: string;
      size: string;
      images: { src: string; order: number }[];
    }
  | { ok: false; reason: string };

function readD05Product(catalog: unknown): D05Product {
  if (!isRecord(catalog) || !Array.isArray(catalog.products)) {
    return { ok: false, reason: "Catalog JSON has no products array." };
  }
  const matches = catalog.products.filter(
    (raw): raw is Record<string, unknown> => isRecord(raw) && normalizeMa(String(raw.ma ?? "")) === D05_MA,
  );
  if (matches.length === 0) return { ok: false, reason: "D05 is not in the catalog." };
  if (matches.length > 1) return { ok: false, reason: "Catalog has more than one D05." };
  const raw = matches[0];
  if (!raw) return { ok: false, reason: "D05 is not in the catalog." };

  if (raw.status !== "available") return { ok: false, reason: "D05 is not available on the catalog." };
  if (raw.priceUsd !== D05_LOCKED_PRICE_USD) {
    return { ok: false, reason: "D05 catalog price must be $26." };
  }
  if (typeof raw.type !== "string" || !isKindCode(raw.type) || raw.type !== "D") {
    return { ok: false, reason: "D05 catalog type must be D." };
  }
  const titleVn = typeof raw.titleVn === "string" ? raw.titleVn.trim() : "";
  const titleEn = typeof raw.titleEn === "string" ? raw.titleEn.trim() : "";
  if (!titleVn) return { ok: false, reason: "D05 catalog titleVn is empty." };
  if (!titleEn) return { ok: false, reason: "D05 catalog titleEn is empty." };
  if (typeof raw.sourceLink !== "string") return { ok: false, reason: "D05 catalog sourceLink is missing." };
  const sourceLink = normalizeSourceLink(raw.sourceLink);
  if (!sourceLink) return { ok: false, reason: "D05 catalog sourceLink is empty." };
  const size = orderedSizeLine(raw.sizes);
  if (!size) return { ok: false, reason: "D05 catalog sizes are empty." };
  const images = readImages(raw.images);
  if (!images.ok) return images;
  return { ok: true, titleVn, titleEn, sourceLink, size, images: images.images };
}

const SIZE_ORDER = ["2XS", "XS", "S", "M", "L", "XL", "2XL"] as const;

function orderedSizeLine(raw: unknown): string {
  if (!Array.isArray(raw)) return "";
  const found = new Set<string>();
  for (const item of raw) {
    if (typeof item !== "string") continue;
    const letter = item.trim().toUpperCase();
    if ((SIZE_ORDER as readonly string[]).includes(letter)) found.add(letter);
  }
  return SIZE_ORDER.filter((letter) => found.has(letter)).join(" ");
}

function readImages(
  raw: unknown,
): { ok: true; images: { src: string; order: number }[] } | { ok: false; reason: string } {
  if (!Array.isArray(raw) || raw.length === 0) {
    return { ok: false, reason: "D05 catalog photos are empty." };
  }
  const images: { src: string; order: number }[] = [];
  for (const item of raw) {
    if (!isRecord(item) || typeof item.src !== "string" || typeof item.order !== "number") {
      return { ok: false, reason: "D05 catalog photo is missing src or order." };
    }
    if (!isBlobPhotoUrl(item.src)) {
      return { ok: false, reason: "D05 catalog photo is not a Blob https URL." };
    }
    images.push({ src: item.src, order: item.order });
  }
  images.sort((a, b) => a.order - b.order);
  const orders = new Set(images.map((image) => image.order));
  if (orders.size !== images.length) return { ok: false, reason: "D05 catalog photo order is duplicated." };
  return { ok: true, images };
}

function refused(reason: string): D05SeedPlan {
  return {
    mode: "dry-run",
    persisted: false,
    ok: false,
    reason,
    ma: D05_MA,
    titleVn: "",
    titleEn: "",
    priceUsd: null,
    sourceLink: "",
    size: "",
    photos: [],
    blurb: "",
    color: "",
    sellUsd: "",
    price: "",
  };
}

function photoRel(ma: string, order: number, src: string): string {
  return `${ma}/${String(order).padStart(3, "0")}${extFromUrl(src)}`;
}

function extFromUrl(src: string): string {
  const clean = src.split("?")[0] ?? src;
  const match = clean.toLowerCase().match(/\.(jpe?g|png|webp)$/);
  if (!match) return ".jpg";
  if (match[1] === "jpeg" || match[1] === "jpg") return ".jpg";
  return `.${match[1]}`;
}

function isBlobPhotoUrl(src: string): boolean {
  try {
    const url = new URL(src);
    return url.protocol === "https:" && url.hostname.endsWith(".public.blob.vercel-storage.com");
  } catch {
    return false;
  }
}

function isImage(file: D05PhotoBytes): boolean {
  if (file.contentType.toLowerCase().startsWith("image/")) return true;
  const bytes = file.bytes;
  if (bytes.length >= 3 && bytes[0] === 0xff && bytes[1] === 0xd8 && bytes[2] === 0xff) return true;
  if (bytes.length >= 4 && bytes[0] === 0x89 && bytes[1] === 0x50 && bytes[2] === 0x4e && bytes[3] === 0x47) {
    return true;
  }
  return bytes.length >= 12 && bytes.subarray(0, 4).toString() === "RIFF" && bytes.subarray(8, 12).toString() === "WEBP";
}

function nextSubmissionId(store: StoreFile): number {
  const maxId = store.submissions.reduce((max, row) => Math.max(max, row.id), 0);
  const fromStore = store.nextId > 0 ? store.nextId : maxId + 1;
  return Math.max(fromStore, maxId + 1);
}

function assertD05InsertSafe(store: StoreFile, submission: Submission): void {
  if (submission.ma !== D05_MA) throw new Error("D05 seed tried to write another mã.");
  if (submission.sell_usd !== String(D05_LOCKED_PRICE_USD)) throw new Error("D05 sell_usd must be $26.");
  if (submission.price !== submission.sell_usd) throw new Error("D05 price must match sell_usd.");
  if (submission.color !== "") throw new Error("D05 color must stay empty.");
  if (sellRewriteBlockReason(submission.ma)) throw new Error("D05 seed hit a protected mã.");
  if ((NEVER_LIST_MAS as readonly string[]).includes(submission.ma)) {
    throw new Error(`${submission.ma} must not be added.`);
  }
  if (store.submissions.some((row) => normalizeMa(row.ma) === D05_MA)) {
    throw new Error("D05 intake form already exists.");
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
