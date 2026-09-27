/**
 * Per-mã intake → sell pipeline tracker. Stages follow the standing pipeline:
 * intake → researched → priced → excel → photos → sell tab → PR → merged.
 *
 * Persisted per mã through the same catalog storage backends (see
 * lib/pipeline-store.ts) — no new backend. Manual checkoffs except where the
 * admin can honestly auto-advance: intake import, price apply, catalog save.
 */

export const PIPELINE_STAGES = [
  { id: "intake", label: "Intake", hint: "GF submitted on the intake site (staged)" },
  { id: "needs_research", label: "Needs research", hint: "Public fields BOTH-ok — per-SKU colors/sizes/prices still behind Taobao login" },
  { id: "researched", label: "Researched", hint: "Taobao link browsed — seller SKU truth captured" },
  { id: "priced", label: "Priced", hint: "Calculator run — sell set, or Inbox giá" },
  { id: "excel", label: "Excel", hint: "Row in the SoT Official sheet (OneDrive)" },
  { id: "photos", label: "Photos", hint: "Saved to OneDrive Photos/<MÃ>/" },
  { id: "sell_tab", label: "Sell tab", hint: "Catalog saved — hold/dropship tab staged" },
  { id: "pr", label: "PR", hint: "Branch pushed, PR opened (never auto-merged)" },
  { id: "merged", label: "Merged", hint: "Boss merged — live shop updated" },
] as const;

export type PipelineStageId = (typeof PIPELINE_STAGES)[number]["id"];

export const PIPELINE_STAGE_IDS = PIPELINE_STAGES.map((stage) => stage.id);

export function isPipelineStageId(value: string): value is PipelineStageId {
  return (PIPELINE_STAGE_IDS as readonly string[]).includes(value);
}

export type PipelineStages = Record<PipelineStageId, string | null>;

export type PipelineRow = {
  /** Sell-site mã when known; otherwise the intake-minted mã. Never invented. */
  ma: string;
  /** Intake-minted mã, when it differs from the sell-site mã. */
  intakeMa?: string;
  stages: PipelineStages;
  updatedAt: string;
};

export type PipelineDocument = {
  schema: "pipeline.v1";
  version: 1;
  siteId: string;
  rows: PipelineRow[];
  updatedAt: string;
};

function emptyStages(): PipelineStages {
  return {
    intake: null,
    needs_research: null,
    researched: null,
    priced: null,
    excel: null,
    photos: null,
    sell_tab: null,
    pr: null,
    merged: null,
  };
}

export function emptyPipelineDocument(siteId: string): PipelineDocument {
  return {
    schema: "pipeline.v1",
    version: 1,
    siteId,
    rows: [],
    updatedAt: new Date().toISOString(),
  };
}

export function emptyPipelineRow(ma: string): PipelineRow {
  return { ma, stages: emptyStages(), updatedAt: new Date().toISOString() };
}

/** Tolerant parse — bad rows are dropped, unknown fields ignored. */
export function parsePipelineDocument(raw: unknown, siteId: string): PipelineDocument {
  const fallback = emptyPipelineDocument(siteId);
  if (typeof raw !== "object" || raw === null) {
    return fallback;
  }
  const row = raw as Record<string, unknown>;
  if (!Array.isArray(row.rows)) {
    return fallback;
  }
  const rows: PipelineRow[] = [];
  for (const entry of row.rows) {
    if (typeof entry !== "object" || entry === null) {
      continue;
    }
    const candidate = entry as Record<string, unknown>;
    const ma = typeof candidate.ma === "string" ? candidate.ma.trim().toUpperCase() : "";
    if (!ma) {
      continue;
    }
    const stages = emptyStages();
    const rawStages = candidate.stages;
    if (typeof rawStages === "object" && rawStages !== null) {
      const stageMap = rawStages as Record<string, unknown>;
      for (const id of PIPELINE_STAGE_IDS) {
        const value = stageMap[id];
        stages[id] = typeof value === "string" && value.trim() ? value : null;
      }
    }
    const intakeMa = typeof candidate.intakeMa === "string" && candidate.intakeMa.trim()
      ? candidate.intakeMa.trim().toUpperCase()
      : undefined;
    rows.push({
      ma,
      ...(intakeMa && intakeMa !== ma ? { intakeMa } : {}),
      stages,
      updatedAt: typeof candidate.updatedAt === "string" ? candidate.updatedAt : new Date().toISOString(),
    });
  }
  rows.sort((a, b) => a.ma.localeCompare(b.ma));
  return {
    schema: "pipeline.v1",
    version: 1,
    siteId: typeof row.siteId === "string" && row.siteId.trim() ? row.siteId : siteId,
    rows,
    updatedAt: typeof row.updatedAt === "string" ? row.updatedAt : new Date().toISOString(),
  };
}

export function getPipelineRow(document: PipelineDocument, ma: string): PipelineRow | undefined {
  const target = ma.trim().toUpperCase();
  return document.rows.find((row) => row.ma === target);
}

export function setPipelineStage(
  document: PipelineDocument,
  ma: string,
  stage: PipelineStageId,
  done: boolean,
  at = new Date().toISOString(),
): PipelineDocument {
  const target = ma.trim().toUpperCase();
  const existing = document.rows.find((row) => row.ma === target);
  const nextRow: PipelineRow = existing
    ? { ...existing, stages: { ...existing.stages, [stage]: done ? (existing.stages[stage] ?? at) : null }, updatedAt: at }
    : { ...emptyPipelineRow(target), stages: { ...emptyStages(), [stage]: done ? at : null }, updatedAt: at };
  const rows = document.rows.filter((row) => row.ma !== target);
  rows.push(nextRow);
  rows.sort((a, b) => a.ma.localeCompare(b.ma));
  return { ...document, rows, updatedAt: at };
}

/** Link an intake mã to its sell-site mã once the draft is saved. */
export function linkPipelineIntakeMa(
  document: PipelineDocument,
  ma: string,
  intakeMa: string,
  at = new Date().toISOString(),
): PipelineDocument {
  const target = ma.trim().toUpperCase();
  const clean = intakeMa.trim().toUpperCase();
  if (!target || !clean || target === clean) {
    return document;
  }
  const exists = document.rows.some((row) => row.ma === target);
  const rows = document.rows.map((row) =>
    row.ma === target ? { ...row, intakeMa: clean, updatedAt: at } : row,
  );
  if (!exists) {
    rows.push({ ...emptyPipelineRow(target), intakeMa: clean, updatedAt: at });
  }
  rows.sort((a, b) => a.ma.localeCompare(b.ma));
  return { ...document, rows, updatedAt: at };
}

export function pipelineProgress(row: PipelineRow): { done: number; total: number } {
  const done = PIPELINE_STAGE_IDS.filter((id) => row.stages[id] !== null).length;
  return { done, total: PIPELINE_STAGE_IDS.length };
}

export function nextOpenStage(row: PipelineRow): PipelineStageId | null {
  return PIPELINE_STAGE_IDS.find((id) => row.stages[id] === null) ?? null;
}

export function stageLabel(id: PipelineStageId): string {
  return PIPELINE_STAGES.find((stage) => stage.id === id)?.label ?? id;
}
