import { emptyFitCm, isAsiaSizeLetter } from "@/lib/asia-size";
import type { ItemDraft } from "@/lib/item-draft";
import type { ShopSize } from "@/lib/asia-size";

/**
 * Intake → draft prefill. The intake app (sassy-closet) stages submissions as
 * status "staged" / square "not_square" in its own store
 * (sassy-closet/store.json on its Blob). This sell-site app does NOT share that
 * store, so import works two ways:
 *   1. fetchIntakeStagedAction pulls the intake site's public /api/submissions
 *      (server-side) and filters staged rows, or
 *   2. Boss pastes one submission's JSON (or the /api/submissions payload).
 *
 * Never invent: seller/GF-confirmed colors are marked "confirmed" (green),
 * machine-suggested-only colors "unconfirmed" (red), and empty stays empty.
 * Drafts are always staged (status "hold") — never available, never Square.
 */

export type IntakePiece = {
  id: string;
  photos: number[];
  suggested: string[];
  color: string;
  note: string;
};

export type IntakeSubmission = {
  id: number;
  ma: string;
  kind: string;
  size: string;
  color: string;
  color_note: string;
  pieces: IntakePiece[];
  link: string;
  price: string;
  cost_cny: string;
  cost_usd: string;
  cost_currency: string;
  sell_cny: string;
  sell_usd: string;
  sell_currency: string;
  blurb: string;
  photo_paths: string[];
  photo_hashes: string[];
  status: string;
  square: string;
  created_at: string;
  updated_at: string;
  caption_vi: string;
  caption_en: string;
  blurb_suggested: string;
  photo_link: string;
};

function asString(value: unknown): string {
  return typeof value === "string" ? value : "";
}

function asStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }
  return value.filter((item): item is string => typeof item === "string");
}

/** Keep only the fields this importer understands; coerce defensively. */
export function sanitizeIntakeSubmission(raw: unknown): IntakeSubmission | null {
  if (typeof raw !== "object" || raw === null) {
    return null;
  }
  const row = raw as Record<string, unknown>;
  const ma = asString(row.ma).trim();
  if (!ma) {
    return null;
  }
  const piecesRaw = Array.isArray(row.pieces) ? row.pieces : [];
  const pieces: IntakePiece[] = piecesRaw
    .filter((piece): piece is Record<string, unknown> => typeof piece === "object" && piece !== null)
    .map((piece) => ({
      id: asString(piece.id),
      photos: Array.isArray(piece.photos)
        ? piece.photos.filter((n): n is number => typeof n === "number")
        : [],
      suggested: asStringArray(piece.suggested),
      color: asString(piece.color),
      note: asString(piece.note),
    }));
  return {
    id: typeof row.id === "number" ? row.id : 0,
    ma,
    kind: asString(row.kind),
    size: asString(row.size),
    color: asString(row.color),
    color_note: asString(row.color_note),
    pieces,
    link: asString(row.link),
    price: asString(row.price),
    cost_cny: asString(row.cost_cny),
    cost_usd: asString(row.cost_usd),
    cost_currency: asString(row.cost_currency),
    sell_cny: asString(row.sell_cny),
    sell_usd: asString(row.sell_usd),
    sell_currency: asString(row.sell_currency),
    blurb: asString(row.blurb),
    photo_paths: asStringArray(row.photo_paths),
    photo_hashes: asStringArray(row.photo_hashes),
    status: asString(row.status),
    square: asString(row.square),
    created_at: asString(row.created_at),
    updated_at: asString(row.updated_at),
    caption_vi: asString(row.caption_vi),
    caption_en: asString(row.caption_en),
    blurb_suggested: asString(row.blurb_suggested),
    photo_link: asString(row.photo_link),
  };
}

export type IntakeImportParse =
  | { ok: true; submissions: IntakeSubmission[] }
  | { ok: false; error: string };

/**
 * Accept a pasted payload: one submission object, a bare array of them, or
 * the intake /api/submissions envelope { submissions: [...] }. Only staged
 * rows are importable — anything else is refused, never silently upgraded.
 */
export function parseIntakeImportJson(text: string): IntakeImportParse {
  let raw: unknown;
  try {
    raw = JSON.parse(text);
  } catch {
    return { ok: false, error: "Pasted text is not valid JSON." };
  }
  let candidates: unknown[];
  if (Array.isArray(raw)) {
    candidates = raw;
  } else if (typeof raw === "object" && raw !== null && Array.isArray((raw as Record<string, unknown>).submissions)) {
    candidates = (raw as Record<string, unknown>).submissions as unknown[];
  } else if (typeof raw === "object" && raw !== null) {
    candidates = [raw];
  } else {
    return { ok: false, error: "Pasted JSON is not a submission object." };
  }
  if (candidates.length === 0) {
    return { ok: false, error: "No submissions found in the pasted JSON." };
  }
  const submissions: IntakeSubmission[] = [];
  for (const candidate of candidates) {
    const submission = sanitizeIntakeSubmission(candidate);
    if (!submission) {
      return { ok: false, error: "One entry has no mã — refusing the whole paste. Never invent a mã." };
    }
    if (submission.status !== "staged") {
      return {
        ok: false,
        error: `Mã ${submission.ma} is not staged (status "${submission.status || "?"}"). Only staged intake imports.`,
      };
    }
    submissions.push(submission);
  }
  return { ok: true, submissions };
}

export type ColorTruth = "confirmed" | "unconfirmed";

export type PrefillColor = {
  name: string;
  note: string;
  truth: ColorTruth;
  source: string;
};

export type IntakePrefill = {
  intakeMa: string;
  letter: string;
  colors: PrefillColor[];
  sizes: ShopSize[];
  droppedSizes: string[];
  costCny: number | null;
  costUsd: number | null;
  sellCny: number | null;
  sellUsd: number | null;
  /** Sell chosen in the intake calculator; travels with the draft to Add. */
  suggestedSell: number | null;
  sourceLink: string;
  blurb: string;
  captionVi: string;
  colorNote: string;
  photoCount: number;
  photoPaths: string[];
  photoLink: string;
  createdAt: string;
  warnings: string[];
};

function parseMoney(raw: string): number | null {
  const trimmed = raw.trim().replace(/,/g, "");
  if (!trimmed) {
    return null;
  }
  const value = Number(trimmed);
  return Number.isFinite(value) && value >= 0 ? value : null;
}

function slugifyName(name: string): string {
  return (
    name
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "color"
  );
}

/**
 * Build the draft prefill from a staged intake submission. GF-entered colors
 * (submission.color, piece.color) are "confirmed"; colors that only appear in
 * piece.suggested are "unconfirmed". Empty stays empty — nothing is invented.
 */
export function intakeToPrefill(submission: IntakeSubmission): IntakePrefill {
  const warnings: string[] = [];
  const byName = new Map<string, PrefillColor>();

  function addColor(name: string, note: string, truth: ColorTruth, source: string) {
    const clean = name.trim();
    if (!clean) {
      return;
    }
    const key = clean.toLowerCase();
    const existing = byName.get(key);
    if (existing) {
      if (truth === "confirmed" && existing.truth === "unconfirmed") {
        existing.truth = "confirmed";
        existing.source = source;
      }
      if (note.trim() && !existing.note) {
        existing.note = note.trim();
      }
      return;
    }
    byName.set(key, { name: clean, note: note.trim(), truth, source });
  }

  if (submission.color.trim()) {
    addColor(submission.color, submission.color_note, "confirmed", "GF input");
  }
  for (const piece of submission.pieces) {
    if (piece.color.trim()) {
      addColor(piece.color, piece.note, "confirmed", "GF piece color");
    }
    for (const suggested of piece.suggested) {
      addColor(suggested, piece.note, "unconfirmed", "suggested only");
    }
  }
  const colors = [...byName.values()];
  if (colors.length === 0) {
    warnings.push("No colors on this submission — colors stay empty until research.");
  }
  if (colors.some((color) => color.truth === "unconfirmed")) {
    warnings.push("Unconfirmed (red) colors are suggestions only — confirm against the seller SKU before Save.");
  }

  const sizes: ShopSize[] = [];
  const droppedSizes: string[] = [];
  for (const token of submission.size.split(/[\s,;|/]+/)) {
    const clean = token.trim().toUpperCase();
    if (!clean) {
      continue;
    }
    if (isAsiaSizeLetter(clean)) {
      if (!sizes.includes(clean)) {
        sizes.push(clean);
      }
    } else if (!droppedSizes.includes(token.trim())) {
      droppedSizes.push(token.trim());
    }
  }
  if (droppedSizes.length > 0) {
    warnings.push(`Dropped unknown size tokens (${droppedSizes.join(", ")}) — never invent sizes.`);
  }

  const costCny = parseMoney(submission.cost_cny);
  const costUsd = parseMoney(submission.cost_usd);
  const sellCny = parseMoney(submission.sell_cny);
  const sellUsd = parseMoney(submission.sell_usd);
  if (costCny === null && costUsd === null) {
    warnings.push("No cost on this submission — the price calculator needs a cost.");
  }

  const link = submission.link.trim();
  if (link && !/^https?:\/\//i.test(link)) {
    warnings.push("Source link is not a URL — left out of the draft. Paste a real link, never invent one.");
  }

  const photoCount = submission.photo_paths.length;
  if (photoCount === 0) {
    warnings.push("No intake photos — save photos to OneDrive Photos/<MÃ>/, then upload here.");
  }

  return {
    intakeMa: submission.ma,
    letter: submission.kind.trim().toUpperCase(),
    colors,
    sizes,
    droppedSizes,
    costCny,
    costUsd,
    sellCny,
    sellUsd,
    suggestedSell: null,
    sourceLink: /^https?:\/\//i.test(link) ? link : "",
    blurb: submission.blurb.trim(),
    captionVi: submission.caption_vi.trim(),
    colorNote: submission.color_note.trim(),
    photoCount,
    photoPaths: submission.photo_paths,
    photoLink: submission.photo_link.trim(),
    createdAt: submission.created_at,
    warnings,
  };
}

/**
 * Assemble the ItemDraft. Status is forced to "hold": an imported draft is
 * staged only — never available, never touching Square (this app has no
 * Square integration at all). Hexes are left blank for Boss to pick from
 * the swatch boxes; titles stay empty until research names the piece.
 */
export function prefillToDraft(prefill: IntakePrefill): ItemDraft {
  return {
    titleEn: "",
    titleVn: "",
    descriptionEn: "",
    descriptionVn: prefill.captionVi,
    status: "hold",
    priceInput: "",
    colors: prefill.colors.map((color, index) => ({
      id: `intake-${index}-${slugifyName(color.name)}`,
      hex: "",
      name: color.name,
      note: color.note,
    })),
    images: [{ src: "", colorId: null, order: 1 }],
    sizes: prefill.sizes,
    fitCm: emptyFitCm(),
    fulfillment: "dropship",
    sourceLink: prefill.sourceLink,
  };
}
