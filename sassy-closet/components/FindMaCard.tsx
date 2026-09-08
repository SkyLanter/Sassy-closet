"use client";

import { useEffect, useState } from "react";
import { PhotoThumbs } from "@/components/PhotoThumbs";
import { captionStarter, editDeepLink, kindColorsLine } from "@/lib/captions";
import {
  STAGED_ONLY_MESSAGE,
  dashIfEmpty,
  moneyLine,
  onHandStatusLabel,
} from "@/lib/on-hand";
import type { MaLookup, OnHandRow } from "@/lib/types";

type CopyKind = "ma" | "link" | "caption" | null;

export function FindMaCard({
  result,
  onClose,
}: {
  result: MaLookup | null;
  onClose: () => void;
}) {
  const [copied, setCopied] = useState<CopyKind>(null);

  useEffect(() => {
    setCopied(null);
  }, [result]);

  if (!result) return null;

  const staged = result.staged;
  const line = kindColorsLine({ kind: staged.kind, color: staged.colors, color_note: staged.color_note });
  const link = editDeepLink(window.location.origin, staged.ma);
  const starter = captionStarter(staged.ma);
  const notes = [staged.notes, staged.blurb].map((part) => part.trim()).filter(Boolean).join(" · ");

  async function copy(kind: Exclude<CopyKind, null>, text: string) {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(kind);
    } catch {
      setCopied(null);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-rose-950/30 p-0 sm:items-center sm:p-6"
      role="presentation"
      onClick={onClose}
    >
      <section
        data-testid="find-card"
        role="dialog"
        aria-labelledby="find-card-title"
        className="max-h-[92dvh] w-full max-w-md overflow-y-auto rounded-t-3xl bg-[oklch(0.995_0.01_50)] p-5 shadow-xl sm:rounded-3xl lg:p-8"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-3">
          <h2
            id="find-card-title"
            data-testid="find-card-title"
            className="text-base font-bold text-rose-700 lg:text-xl"
          >
            Mã · Item card
          </h2>
          <button
            type="button"
            data-testid="find-card-close"
            aria-label="Đóng"
            className="flex h-10 w-10 items-center justify-center rounded-full text-lg font-bold text-rose-700 ring-1 ring-rose-100"
            onClick={onClose}
          >
            ✕
          </button>
        </div>
        <p
          data-testid="find-card-ma"
          className="mt-3 text-center text-5xl font-extrabold tracking-wide text-rose-700 lg:text-6xl"
        >
          {staged.ma}
        </p>
        <p
          data-testid="find-card-line"
          className="mt-2 text-center text-sm font-semibold text-rose-800"
        >
          {line}
        </p>

        <dl className="mt-4 space-y-2 text-sm">
          <Field testId="find-card-kind" label="Loại · Kind" value={dashIfEmpty(staged.kind_label)} />
          <Field testId="find-card-colors" label="Màu · Colors" value={dashIfEmpty(staged.colors)} />
          <Field testId="find-card-sizes" label="Size" value={dashIfEmpty(staged.sizes)} />
          <Field testId="find-card-cost" label="Cost" value={moneyLine(staged.cost_usd, staged.cost_cny)} />
          <Field testId="find-card-sell" label="Sell" value={moneyLine(staged.sell_usd, staged.sell_cny)} />
          <Field
            testId="find-card-link"
            label="Source link"
            value={dashIfEmpty(staged.source_link)}
            href={staged.source_link.trim() || undefined}
          />
          <Field testId="find-card-notes" label="Notes" value={dashIfEmpty(notes)} />
          <Field testId="find-card-photo-folder" label="Photos folder" value={dashIfEmpty(staged.photo_link)} />
          <Field testId="find-card-status" label="Status" value={`${staged.status} · ${staged.square}`} />
        </dl>

        <PhotoThumbs
          photos={staged.photo_paths}
          layout="row"
          testId="find-card-photos"
          emptyTestId="find-card-photos-empty"
          moreTestId="find-card-photos-more"
          thumbTestIdPrefix="find-card-photo"
        />

        <OnHandBlock rows={result.on_hand} stagedOnly={result.staged_only} />

        <div className="mt-5 grid gap-2">
          <button
            type="button"
            data-testid="find-card-copy-ma"
            className="h-12 rounded-full bg-primary text-base font-bold text-primary-foreground"
            onClick={() => void copy("ma", staged.ma)}
          >
            Copy mã
          </button>
          <button
            type="button"
            data-testid="find-card-copy-link"
            className="h-12 rounded-full bg-white text-base font-bold text-rose-800 ring-1 ring-rose-100"
            onClick={() => void copy("link", link)}
          >
            Copy link
          </button>
          <button
            type="button"
            data-testid="find-card-copy-caption"
            className="h-12 rounded-full bg-white text-base font-bold text-rose-800 ring-1 ring-rose-100"
            onClick={() => void copy("caption", starter)}
          >
            Copy caption starter
          </button>
          <a
            data-testid="find-card-open-sua"
            href={`/?ma=${encodeURIComponent(staged.ma)}`}
            className="flex h-12 items-center justify-center rounded-full bg-white text-base font-bold text-rose-800 ring-1 ring-rose-100"
          >
            Open in Sửa
          </a>
        </div>
        {copied ? (
          <p
            data-testid="find-card-copied"
            className="mt-3 rounded-full bg-rose-100 py-2 text-center text-sm font-semibold text-rose-800"
          >
            Đã copy
          </p>
        ) : null}
        <button
          type="button"
          data-testid="find-card-done"
          className="mt-4 h-11 w-full rounded-full text-sm font-semibold text-rose-700"
          onClick={onClose}
        >
          Done
        </button>
      </section>
    </div>
  );
}

function Field({
  label,
  value,
  testId,
  href,
}: {
  label: string;
  value: string;
  testId: string;
  href?: string;
}) {
  return (
    <div className="flex items-start justify-between gap-3 rounded-2xl bg-white px-3 py-2 ring-1 ring-rose-100">
      <dt className="shrink-0 text-xs font-semibold uppercase tracking-wide text-rose-600">{label}</dt>
      <dd data-testid={testId} className="text-right font-semibold text-rose-900 break-all">
        {href && value !== "—" ? (
          <a className="underline-offset-2 hover:underline" href={href} target="_blank" rel="noreferrer">
            {value}
          </a>
        ) : (
          value
        )}
      </dd>
    </div>
  );
}

function OnHandBlock({ rows, stagedOnly }: { rows: OnHandRow[]; stagedOnly: boolean }) {
  return (
    <div data-testid="find-card-on-hand" className="mt-5">
      <h3 className="mb-2 text-sm font-bold text-rose-800">On-hand · Tồn kho</h3>
      {stagedOnly || rows.length === 0 ? (
        <p
          data-testid="find-card-staged-only"
          className="rounded-2xl bg-amber-50 px-3 py-3 text-center text-sm font-semibold text-amber-900 ring-1 ring-amber-100"
        >
          {STAGED_ONLY_MESSAGE}
        </p>
      ) : (
        <ul className="space-y-2">
          {rows.map((row, index) => (
            <li
              key={`${row.size}-${row.color}-${index}`}
              data-testid={`find-card-on-hand-row-${index}`}
              className="rounded-2xl bg-white px-3 py-2 text-sm ring-1 ring-rose-100"
            >
              <p className="font-bold text-rose-900">
                {dashIfEmpty(row.size)} · {dashIfEmpty(row.color)} · qty {dashIfEmpty(row.qty_on_hand)}
              </p>
              <p className="mt-1 text-xs text-rose-700">
                {onHandStatusLabel(row.status)}
                {row.storage_location ? ` · ${row.storage_location}` : ""}
                {row.notes ? ` · ${row.notes}` : ""}
              </p>
              <p className="mt-1 break-all text-[11px] text-rose-600">{row.where_stored}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
