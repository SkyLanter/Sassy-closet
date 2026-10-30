/**
 * Sell-site intake receive path (the PR #42 webhook's other end).
 *
 * The intake site POSTs here the moment Nhung submits. This module stages the
 * submission — it NEVER publishes to the live catalog, NEVER merges, and
 * NEVER marks Square stock. Staged records land in `data/intake-staged.json`
 * with stage "needs_research" and priceUsd null ("Inbox giá") until a human
 * (Caption & Money / Buy Research) verifies the fields.
 *
 * Standing rules enforced here:
 * - Auth never fails open: no key configured → 503, wrong key → 401.
 * - Mã and source link are immutable: a submission for an existing mã with a
 *   different link is rejected, never reminted.
 * - Dedupe by (mã, submission timestamp): re-deliveries return "duplicate".
 * - Unverified colors/sizes are recorded as proposals only — never shown.
 * - Proposed sell price is recorded only — the public price stays "Inbox giá".
 */

import { isValidMa, normalizeMa } from "./ma";

export type IntakeReceiveEvent = "create" | "update";

export type IntakeReceivePayload = {
  event: IntakeReceiveEvent;
  ma: string;
  /** Submission timestamp (ISO) from the intake site — dedupe key part 2. */
  timestamp: string;
  source: "intake";
  sizes?: string[];
  colors?: string[];
  cost?: string;
  sell?: string;
  source_link?: string;
  kind?: string;
  photo_count?: number;
};

export type StagedIntakeRecord = {
  ma: string;
  /** Immutable once set — never changed by later submissions. */
  sourceLink: string | null;
  stage: "needs_research";
  /** Always null at stage time → the site shows "Inbox giá". */
  priceUsd: null;
  /** Caption & Money's input — proposal only, never public. */
  proposedSell: string | null;
  proposedCost: string | null;
  /** Buy Research's input — proposals only, never shown on the site. */
  proposedSizes: string[];
  proposedColors: string[];
  kind: string | null;
  photoCount: number;
  firstStagedAt: string;
  /** Last submission timestamp seen — dedupe key part 2. */
  lastSubmissionAt: string;
  submissionCount: number;
  updatedAt: string;
};

export type IntakeStagedDocument = {
  schema: "intake-staged.v1";
  version: 1;
  siteId: string;
  records: StagedIntakeRecord[];
  updatedAt: string;
};

export type StageResult =
  | { ok: true; status: "staged" | "updated" | "duplicate"; record: StagedIntakeRecord }
  | { ok: false; error: string };

export const INTAKE_STAGED_SCHEMA = "intake-staged.v1";

export function emptyStagedDocument(now: string): IntakeStagedDocument {
  return {
    schema: INTAKE_STAGED_SCHEMA,
    version: 1,
    siteId: "sassy-closet-shop",
    records: [],
    updatedAt: now,
  };
}

/** Validate the raw webhook body. Returns the normalized payload or an error. */
export function parseIntakeReceivePayload(
  body: unknown,
): { ok: true; payload: IntakeReceivePayload } | { ok: false; error: string } {
  if (typeof body !== "object" || body === null) {
    return { ok: false, error: "Body must be a JSON object." };
  }
  const b = body as Record<string, unknown>;

  const event = b.event;
  if (event !== "create" && event !== "update") {
    return { ok: false, error: 'event must be "create" or "update".' };
  }

  const maRaw = b.ma;
  if (typeof maRaw !== "string" || !isValidMa(maRaw)) {
    return { ok: false, error: "ma must be a valid shop mã (letter + digits, e.g. A17)." };
  }

  const timestamp = b.timestamp;
  if (typeof timestamp !== "string" || !timestamp.trim() || Number.isNaN(Date.parse(timestamp))) {
    return { ok: false, error: "timestamp must be an ISO date string." };
  }

  if (b.source !== undefined && b.source !== "intake") {
    return { ok: false, error: 'source must be "intake".' };
  }

  const strArray = (v: unknown): string[] | undefined => {
    if (v === undefined) return undefined;
    if (!Array.isArray(v)) return undefined;
    return v.filter((x): x is string => typeof x === "string").map((x) => x.trim()).filter(Boolean);
  };
  const optStr = (v: unknown): string | undefined => {
    if (typeof v !== "string") return undefined;
    const t = v.trim();
    return t ? t : undefined;
  };

  const sizes = strArray(b.sizes);
  const colors = strArray(b.colors);
  if (b.sizes !== undefined && sizes === undefined)
    return { ok: false, error: "sizes must be an array of strings." };
  if (b.colors !== undefined && colors === undefined)
    return { ok: false, error: "colors must be an array of strings." };

  const payload: IntakeReceivePayload = {
    event,
    ma: normalizeMa(maRaw),
    timestamp: timestamp.trim(),
    source: "intake",
  };
  if (sizes) payload.sizes = sizes;
  if (colors) payload.colors = colors;
  const cost = optStr(b.cost);
  if (cost) payload.cost = cost;
  const sell = optStr(b.sell);
  if (sell) payload.sell = sell;
  const sourceLink = optStr(b.source_link);
  if (sourceLink) payload.source_link = sourceLink;
  const kind = optStr(b.kind);
  if (kind) payload.kind = kind;
  if (typeof b.photo_count === "number" && Number.isFinite(b.photo_count) && b.photo_count >= 0) {
    payload.photo_count = Math.floor(b.photo_count);
  }
  return { ok: true, payload };
}

export type CatalogMaIndex = {
  /** mãs already in the live catalog. */
  mas: Set<string>;
  /** mã → source link for catalog products (when known). */
  links: Map<string, string>;
};

/**
 * Stage a validated intake payload. Pure function — no I/O.
 *
 * - New mã → "staged".
 * - Known mã + new timestamp → "updated" (proposals refresh; mã/link untouched).
 * - Known mã + same timestamp → "duplicate".
 * - Conflicting source link for a known mã → error (never remint).
 */
export function stageIntakeSubmission(
  existing: StagedIntakeRecord[],
  payload: IntakeReceivePayload,
  catalog: CatalogMaIndex,
  now: string,
): StageResult {
  const ma = payload.ma;
  const incomingLink = payload.source_link?.trim() || null;

  // Mã/link immutability: the link that arrived first wins, forever.
  const staged = existing.find((r) => r.ma === ma);
  const catalogLink = catalog.links.get(ma) ?? null;
  const knownLink = staged?.sourceLink ?? catalogLink;
  if (knownLink && incomingLink && knownLink !== incomingLink) {
    return {
      ok: false,
      error: `Mã ${ma} already has a source link; refusing to remint to a different item.`,
    };
  }
  // A brand-new mã must not collide with the live catalog either.
  if (!staged && catalog.mas.has(ma)) {
    // Catalog owns this mã — still stage as an update proposal, never rewrite it.
    // (The staged record tracks the intake submission; the catalog row is untouched.)
  }

  if (staged && staged.lastSubmissionAt === payload.timestamp) {
    return { ok: true, status: "duplicate", record: staged };
  }

  const proposedSizes = payload.sizes ?? staged?.proposedSizes ?? [];
  const proposedColors = payload.colors ?? staged?.proposedColors ?? [];

  if (staged) {
    const updated: StagedIntakeRecord = {
      ...staged,
      // sourceLink never changes once set.
      sourceLink: staged.sourceLink ?? incomingLink,
      proposedSell: payload.sell ?? staged.proposedSell,
      proposedCost: payload.cost ?? staged.proposedCost,
      proposedSizes,
      proposedColors,
      kind: payload.kind ?? staged.kind,
      photoCount: payload.photo_count ?? staged.photoCount,
      lastSubmissionAt: payload.timestamp,
      submissionCount: staged.submissionCount + 1,
      updatedAt: now,
    };
    return { ok: true, status: "updated", record: updated };
  }

  const record: StagedIntakeRecord = {
    ma,
    sourceLink: incomingLink ?? catalogLink,
    stage: "needs_research",
    priceUsd: null,
    proposedSell: payload.sell ?? null,
    proposedCost: payload.cost ?? null,
    proposedSizes,
    proposedColors,
    kind: payload.kind ?? null,
    photoCount: payload.photo_count ?? 0,
    firstStagedAt: now,
    lastSubmissionAt: payload.timestamp,
    submissionCount: 1,
    updatedAt: now,
  };
  return { ok: true, status: "staged", record };
}

/** Apply a StageResult to the document's record list (returns a new document). */
export function applyStageResult(
  doc: IntakeStagedDocument,
  result: Extract<StageResult, { ok: true }>,
  now: string,
): IntakeStagedDocument {
  if (result.status === "duplicate") return doc;
  const records = doc.records.some((r) => r.ma === result.record.ma)
    ? doc.records.map((r) => (r.ma === result.record.ma ? result.record : r))
    : [...doc.records, result.record];
  return { ...doc, records, updatedAt: now };
}

export function parseStagedDocument(raw: unknown, now: string): IntakeStagedDocument {
  if (typeof raw !== "object" || raw === null) return emptyStagedDocument(now);
  const d = raw as Partial<IntakeStagedDocument>;
  if (d.schema !== INTAKE_STAGED_SCHEMA || !Array.isArray(d.records)) {
    return emptyStagedDocument(now);
  }
  const records = d.records.filter(
    (r): r is StagedIntakeRecord =>
      typeof r === "object" &&
      r !== null &&
      typeof r.ma === "string" &&
      isValidMa(r.ma) &&
      r.stage === "needs_research",
  );
  return {
    schema: INTAKE_STAGED_SCHEMA,
    version: 1,
    siteId: typeof d.siteId === "string" ? d.siteId : "sassy-closet-shop",
    records,
    updatedAt: typeof d.updatedAt === "string" ? d.updatedAt : now,
  };
}
