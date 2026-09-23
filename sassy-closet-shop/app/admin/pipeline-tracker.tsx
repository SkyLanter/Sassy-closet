"use client";

import { useMemo, useState } from "react";
import { MaMark } from "@/components/ma-mark";
import { setPipelineStageAction } from "@/app/admin/actions";
import { FormAlert } from "@/app/admin/fields";
import {
  isPipelineStageId,
  nextOpenStage,
  pipelineProgress,
  PIPELINE_STAGES,
  stageLabel,
  type PipelineDocument,
  type PipelineRow,
  type PipelineStageId,
} from "@/lib/pipeline";
import { isValidMa, normalizeMa } from "@/lib/ma";
import type { Product } from "@/lib/types";

type ToastFn = (tone: "ok" | "error", text: string) => void;

type TrackerRow = {
  ma: string;
  row: PipelineRow | null;
  inCatalog: boolean;
};

export function PipelineTracker({
  products,
  initial,
  canWrite,
  onToast,
}: {
  products: Product[];
  initial: PipelineDocument;
  canWrite: boolean;
  onToast: ToastFn;
}) {
  const [doc, setDoc] = useState<PipelineDocument>(initial);
  const [busyKey, setBusyKey] = useState<string | null>(null);
  const [newMa, setNewMa] = useState("");

  const rows: TrackerRow[] = useMemo(() => {
    const byMa = new Map(doc.rows.map((row) => [row.ma, row]));
    const catalogMas = new Set(products.map((product) => product.ma));
    const all = new Set<string>([...byMa.keys(), ...catalogMas]);
    return [...all]
      .sort((a, b) => a.localeCompare(b))
      .map((ma) => ({ ma, row: byMa.get(ma) ?? null, inCatalog: catalogMas.has(ma) }));
  }, [doc, products]);

  async function toggle(ma: string, stage: PipelineStageId, done: boolean) {
    const key = `${ma}:${stage}`;
    setBusyKey(key);
    try {
      const result = await setPipelineStageAction(ma, stage, done);
      if (!result.ok) {
        onToast("error", result.error);
        return;
      }
      setDoc(result.pipeline);
    } finally {
      setBusyKey(null);
    }
  }

  async function addMa() {
    const target = normalizeMa(newMa);
    if (!isValidMa(target)) {
      onToast("error", `Not a valid mã: ${newMa.trim() || "?"}. Never invent one — type the real code.`);
      return;
    }
    if (!canWrite) {
      onToast("error", "Tracker is read-only until a store is attached (Blob/KV/local).");
      return;
    }
    setNewMa("");
    setBusyKey(`${target}:intake`);
    try {
      // done=false still creates the row so the mã appears in the tracker.
      const result = await setPipelineStageAction(target, "intake", false);
      if (!result.ok) {
        onToast("error", result.error);
        return;
      }
      setDoc(result.pipeline);
    } finally {
      setBusyKey(null);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-3xl text-ink">Pipeline tracker</h2>
        <p className="mt-1 max-w-2xl text-sm text-muted">
          One checklist per mã: intake → researched → priced → excel → photos → sell tab → PR →
          merged. Intake, priced, and sell tab advance automatically from the admin; the rest are
          honest manual checkoffs. Excel lives on OneDrive, PRs merge only by Boss.
        </p>
      </div>

      {!canWrite ? (
        <FormAlert tone="error" text="Tracker is read-only until a store is attached (Blob/KV/local)." />
      ) : null}

      <div className="flex max-w-md flex-wrap items-end gap-2">
        <label className="block flex-1 text-xs uppercase tracking-[0.14em] text-muted">
          Track a mã
          <input
            value={newMa}
            onChange={(event) => setNewMa(event.target.value)}
            placeholder="A24"
            className="mt-1 w-full rounded-lg border border-line bg-paper px-3 py-2 text-sm normal-case tracking-normal text-ink outline-none focus:border-gold"
          />
        </label>
        <button
          type="button"
          onClick={() => void addMa()}
          disabled={!canWrite || !newMa.trim()}
          className="min-h-10 rounded-full border border-line px-4 py-2 text-xs uppercase tracking-[0.12em] text-ink disabled:opacity-40"
        >
          Add
        </button>
      </div>

      {rows.length === 0 ? (
        <p className="rounded-2xl border border-dashed border-line px-4 py-10 text-center text-sm text-muted">
          Nothing tracked yet. Import from Intake or save a draft to start a row.
        </p>
      ) : (
        <div className="overflow-x-auto rounded-2xl border border-line">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-line bg-blush/50 text-[11px] uppercase tracking-[0.12em] text-muted">
              <tr>
                <th className="px-3 py-3 font-medium">Mã</th>
                <th className="px-3 py-3 font-medium">Progress</th>
                {PIPELINE_STAGES.map((stage) => (
                  <th key={stage.id} className="px-2 py-3 text-center font-medium" title={stage.hint}>
                    {stage.label}
                  </th>
                ))}
                <th className="px-3 py-3 font-medium">Next</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(({ ma, row, inCatalog }) => {
                const progress = row ? pipelineProgress(row) : { done: 0, total: PIPELINE_STAGES.length };
                const next = row ? nextOpenStage(row) : ("intake" as PipelineStageId);
                return (
                  <tr key={ma} className="border-b border-line last:border-0 hover:bg-blush/40">
                    <td className="px-3 py-2">
                      <MaMark ma={ma} className="text-[13px] tracking-[0.12em]" />
                      {row?.intakeMa ? (
                        <p className="text-[11px] text-muted">intake {row.intakeMa}</p>
                      ) : null}
                      {!inCatalog ? <p className="text-[11px] text-muted">not in catalog yet</p> : null}
                    </td>
                    <td className="px-3 py-2 tabular-nums text-muted">
                      {progress.done}/{progress.total}
                    </td>
                    {PIPELINE_STAGES.map((stage) => {
                      const done = row?.stages[stage.id] !== null && row?.stages[stage.id] !== undefined;
                      const key = `${ma}:${stage.id}`;
                      return (
                        <td key={stage.id} className="px-2 py-2 text-center">
                          <input
                            type="checkbox"
                            aria-label={`${ma} ${stage.label}`}
                            checked={done}
                            disabled={!canWrite || busyKey === key}
                            onChange={(event) => {
                              if (isPipelineStageId(stage.id)) {
                                void toggle(ma, stage.id, event.target.checked);
                              }
                            }}
                          />
                        </td>
                      );
                    })}
                    <td className="px-3 py-2 text-xs text-muted">{next ? stageLabel(next) : "done ✓"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
