"use client";

import { useEffect, useMemo, useState } from "react";
import { AskPanel } from "@/components/AskPanel";
import { BrandHeader } from "@/components/BrandHeader";
import { SavedCard } from "@/components/SavedCard";
import { COLORS, KINDS, SIZES, assertNever } from "@/lib/kinds";
import { nextMa, parseHubMa } from "@/lib/mint";
import type { KindCode } from "@/lib/kinds";
import type { Submission, TabId } from "@/lib/types";

type PhotoDraft = {
  id: string;
  file?: File;
  url: string;
};

export function IntakeApp({
  initialFxRate: _initialFxRate,
  initialFxLabel,
}: {
  initialFxRate: number;
  initialFxLabel: string;
}) {
  const [tab, setTab] = useState<TabId>("create");
  const [kind, setKind] = useState<KindCode>("A");
  const [sizes, setSizes] = useState<string[]>([]);
  const [colors, setColors] = useState<string[]>([]);
  const [colorNote, setColorNote] = useState("");
  const [link, setLink] = useState("");
  const [costUsd, setCostUsd] = useState("");
  const [costCny, setCostCny] = useState("");
  const [sellUsd, setSellUsd] = useState("");
  const [sellCny, setSellCny] = useState("");
  const [photos, setPhotos] = useState<PhotoDraft[]>([]);
  const [lookupMa, setLookupMa] = useState("");
  const [loadedMa, setLoadedMa] = useState<string | null>(null);
  const [renameTo, setRenameTo] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState<Submission | null>(null);
  const [knownMas, setKnownMas] = useState<string[]>([]);
  const [fxLabel] = useState(initialFxLabel);
  const [findPreview, setFindPreview] = useState<string | null>(null);
  const [findMatches, setFindMatches] = useState<{ ma: string; kind: string; color: string }[]>([]);
  const [findCopied, setFindCopied] = useState<string | null>(null);

  useEffect(() => {
    const ma = new URLSearchParams(window.location.search).get("ma");
    if (!ma) return;
    setTab("edit");
    setLookupMa(ma);
    void loadMa(ma);
  }, []);

  const colorLine = useMemo(() => colors.join(", "), [colors]);

  function resetForm() {
    setKind("A");
    setSizes([]);
    setColors([]);
    setColorNote("");
    setLink("");
    setCostUsd("");
    setCostCny("");
    setSellUsd("");
    setSellCny("");
    setPhotos([]);
    setLoadedMa(null);
    setRenameTo("");
    setError(null);
  }

  function switchTab(next: TabId) {
    setTab(next);
    setError(null);
    setFindMatches([]);
    setFindPreview(null);
    if (next === "create") resetForm();
    if (next === "edit") {
      resetForm();
    }
  }

  async function refreshMas(): Promise<string[]> {
    try {
      const response = await fetch("/api/submissions");
      const data = (await response.json()) as { submissions?: { ma?: string }[] };
      const mas = (data.submissions ?? []).map((row) => String(row.ma ?? "")).filter(Boolean);
      setKnownMas(mas);
      return mas;
    } catch {
      return knownMas;
    }
  }

  async function loadMa(raw: string) {
    setBusy(true);
    setError(null);
    try {
      const response = await fetch(`/api/submissions/${encodeURIComponent(raw.trim())}`);
      const data = (await response.json()) as { submission?: Submission; error?: string };
      if (!response.ok || !data.submission) {
        setError(data.error || "Không tìm thấy mã này 🥺");
        setLoadedMa(null);
        return;
      }
      applySubmission(data.submission);
      await refreshMas();
    } catch {
      setError("Mạng hơi lag, thử lại nha.");
    } finally {
      setBusy(false);
    }
  }

  function applySubmission(item: Submission) {
    setLoadedMa(item.ma);
    setLookupMa(item.ma);
    setKind(item.kind);
    setSizes(item.size.split(/[\s,]+/).filter(Boolean));
    setColors(
      item.color
        .split(",")
        .map((part) => part.trim())
        .filter(Boolean),
    );
    setColorNote(item.color_note);
    setLink(item.link);
    setCostUsd(item.cost_usd);
    setCostCny(item.cost_cny);
    setSellUsd(item.sell_usd);
    setSellCny(item.sell_cny);
    setPhotos(
      (item.photo_paths ?? []).map((rel) => ({
        id: `keep:${rel}`,
        url: `/api/photos/${rel}`,
      })),
    );
    setRenameTo("");
  }

  async function save(renameMa?: string | null) {
    setError(null);
    setBusy(true);
    try {
      const form = new FormData();
      form.set("kind", kind);
      form.set("prefix", kind);
      form.set("size", sizes.join(" "));
      form.set("link", link.trim());
      form.set("cost_usd", costUsd);
      form.set("cost_cny", costCny);
      form.set("cost_currency", costUsd ? "USD" : costCny ? "CNY" : "USD");
      form.set("sell_usd", sellUsd);
      form.set("sell_cny", sellCny);
      form.set("sell_currency", sellUsd ? "USD" : sellCny ? "CNY" : "USD");
      form.set("color", colorLine);
      form.set("color_note", colorNote);
      form.set("pieces", JSON.stringify([]));
      form.set("keep_photos", JSON.stringify(photos.filter((p) => p.id.startsWith("keep:")).map((p) => p.id.slice(5))));
      form.set("save", "1");
      if (renameMa) form.set("new_ma", renameMa);
      for (const photo of photos) {
        if (photo.file) form.append("photos", photo.file);
      }
      const editing = tab === "edit" && loadedMa;
      const url = editing ? `/api/submissions/${encodeURIComponent(loadedMa)}` : "/api/submissions";
      const response = await fetch(url, { method: editing ? "PATCH" : "POST", body: form });
      const data = (await response.json()) as { submission?: Submission; error?: string };
      if (!response.ok || !data.submission) {
        setError(data.error || "Chưa nhận được mã. Thử lại nha 🥺");
        return;
      }
      setSaved(data.submission);
      setLoadedMa(data.submission.ma);
      setLookupMa(data.submission.ma);
      if (tab === "create") resetForm();
      else applySubmission(data.submission);
      await refreshMas();
    } catch {
      setError("Chưa gửi được. Kiểm tra mạng rồi thử lại 💕");
    } finally {
      setBusy(false);
    }
  }

  async function onSaveClick() {
    if (tab === "edit" && loadedMa && renameTo.trim()) {
      await save(renameTo.trim());
      return;
    }
    await save(null);
  }

  function onKind(next: KindCode) {
    setKind(next);
    if (tab === "edit" && loadedMa) {
      const current = parseHubMa(loadedMa)?.kind;
      if (current && current !== next) {
        setRenameTo(nextMa(next, knownMas));
      }
    }
  }

  async function onFindPhoto(file: File) {
    setError(null);
    setFindCopied(null);
    const preview = URL.createObjectURL(file);
    setFindPreview(preview);
    setBusy(true);
    try {
      const form = new FormData();
      form.set("photo", file);
      const response = await fetch("/api/find-ma", { method: "POST", body: form });
      const data = (await response.json()) as {
        matches?: { ma: string; kind: string; color: string }[];
        error?: string;
      };
      if (!response.ok) {
        setError(data.error || "Không thấy mã khớp");
        setFindMatches([]);
        return;
      }
      setFindMatches(data.matches ?? []);
    } catch {
      setError("Chưa gửi được. Kiểm tra mạng rồi thử lại 💕");
    } finally {
      setBusy(false);
    }
  }

  const canSave = tab === "create" || Boolean(loadedMa);

  return (
    <main
      data-testid="intake-shell"
      className="relative z-10 mx-auto flex min-h-dvh w-full max-w-md flex-col px-4 py-6 md:max-w-2xl md:px-6 lg:max-w-5xl lg:px-10 lg:py-12 xl:max-w-6xl"
    >
      <BrandHeader />
      <div
        data-testid="intake-tabs"
        className="mb-4 grid grid-cols-4 rounded-full bg-white/70 p-1 shadow-sm ring-1 ring-rose-100 lg:mx-auto lg:mb-6 lg:w-full lg:max-w-xl"
      >
        <TabButton id="create" current={tab} onClick={switchTab} mobile="Món mới" desktop="Món mới" />
        <TabButton id="edit" current={tab} onClick={switchTab} mobile="Sửa mã" desktop="Sửa theo mã" />
        <TabButton id="find" current={tab} onClick={switchTab} mobile="Tìm mã" desktop="Tìm mã · Find" />
        <TabButton
          id="ask"
          current={tab}
          onClick={switchTab}
          mobile="Mini Boss"
          desktop="Hỏi Mini Boss · Ask"
          ariaLabel="Hỏi Mini Boss · Ask"
        />
      </div>
      <section className="flex flex-1 flex-col rounded-3xl bg-card/90 p-4 shadow-sm ring-1 ring-rose-100 lg:p-8">
        {renderTab({
          tab,
          kind,
          onKind,
          sizes,
          setSizes,
          colors,
          setColors,
          colorNote,
          setColorNote,
          link,
          setLink,
          costUsd,
          setCostUsd,
          costCny,
          setCostCny,
          sellUsd,
          setSellUsd,
          sellCny,
          setSellCny,
          photos,
          setPhotos,
          lookupMa,
          setLookupMa,
          loadedMa,
          renameTo,
          setRenameTo,
          loadMa,
          onSaveClick,
          canSave,
          busy,
          fxLabel,
          findPreview,
          findMatches,
          findCopied,
          setFindCopied,
          onFindPhoto,
        })}
        {error ? (
          <p data-testid="intake-error" className="mt-4 text-center text-sm text-rose-700">
            {error}
          </p>
        ) : null}
      </section>
      <p className="mt-4 text-center text-xs text-rose-700/70">
        <a className="underline-offset-2 hover:underline" href="/admin">
          Kit export CSV
        </a>{" "}
        · Boss one-pager trong README / BOSS.md
      </p>
      <SavedCard result={saved} onClose={() => setSaved(null)} />
    </main>
  );
}

function renderTab(props: {
  tab: TabId;
  kind: KindCode;
  onKind: (kind: KindCode) => void;
  sizes: string[];
  setSizes: (value: string[]) => void;
  colors: string[];
  setColors: (value: string[]) => void;
  colorNote: string;
  setColorNote: (value: string) => void;
  link: string;
  setLink: (value: string) => void;
  costUsd: string;
  setCostUsd: (value: string) => void;
  costCny: string;
  setCostCny: (value: string) => void;
  sellUsd: string;
  setSellUsd: (value: string) => void;
  sellCny: string;
  setSellCny: (value: string) => void;
  photos: PhotoDraft[];
  setPhotos: (value: PhotoDraft[]) => void;
  lookupMa: string;
  setLookupMa: (value: string) => void;
  loadedMa: string | null;
  renameTo: string;
  setRenameTo: (value: string) => void;
  loadMa: (ma: string) => Promise<void>;
  onSaveClick: () => Promise<void>;
  canSave: boolean;
  busy: boolean;
  fxLabel: string;
  findPreview: string | null;
  findMatches: { ma: string; kind: string; color: string }[];
  findCopied: string | null;
  setFindCopied: (value: string | null) => void;
  onFindPhoto: (file: File) => Promise<void>;
}) {
  switch (props.tab) {
    case "ask":
      return <AskPanel />;
    case "find":
      return (
        <FindPanel
          preview={props.findPreview}
          matches={props.findMatches}
          copied={props.findCopied}
          setCopied={props.setFindCopied}
          onPhoto={props.onFindPhoto}
        />
      );
    case "create":
    case "edit":
      return <ItemForm {...props} />;
    default: {
      const _never: never = props.tab;
      return assertNever(_never, "Unknown tab");
    }
  }
}

function TabButton({
  id,
  current,
  onClick,
  mobile,
  desktop,
  ariaLabel,
}: {
  id: TabId;
  current: TabId;
  onClick: (id: TabId) => void;
  mobile: string;
  desktop: string;
  ariaLabel?: string;
}) {
  const active = current === id;
  return (
    <button
      type="button"
      data-testid={`tab-${id}`}
      aria-label={ariaLabel}
      className={`h-12 rounded-full px-0.5 text-[9px] font-semibold leading-tight sm:px-2 sm:text-[11px] lg:text-sm ${
        active ? "bg-primary text-primary-foreground shadow" : "text-rose-700"
      }`}
      onClick={() => onClick(id)}
    >
      <span className="lg:hidden">{mobile}</span>
      <span className="hidden lg:inline">{desktop}</span>
    </button>
  );
}

function ItemForm(props: {
  tab: TabId;
  kind: KindCode;
  onKind: (kind: KindCode) => void;
  sizes: string[];
  setSizes: (value: string[]) => void;
  colors: string[];
  setColors: (value: string[]) => void;
  colorNote: string;
  setColorNote: (value: string) => void;
  link: string;
  setLink: (value: string) => void;
  costUsd: string;
  setCostUsd: (value: string) => void;
  costCny: string;
  setCostCny: (value: string) => void;
  sellUsd: string;
  setSellUsd: (value: string) => void;
  sellCny: string;
  setSellCny: (value: string) => void;
  photos: PhotoDraft[];
  setPhotos: (value: PhotoDraft[]) => void;
  lookupMa: string;
  setLookupMa: (value: string) => void;
  loadedMa: string | null;
  renameTo: string;
  setRenameTo: (value: string) => void;
  loadMa: (ma: string) => Promise<void>;
  onSaveClick: () => Promise<void>;
  canSave: boolean;
  busy: boolean;
  fxLabel: string;
}) {
  return (
    <div data-testid="intake-grid" className="flex flex-col lg:grid lg:grid-cols-2 lg:gap-x-10">
      <div>
        {props.tab === "edit" ? (
          <fieldset className="mb-4">
            <label className="mb-2 block text-sm font-medium" htmlFor="lookup-ma">
              Mã
            </label>
            <div className="flex gap-2">
              <input
                id="lookup-ma"
                data-testid="lookup-ma"
                value={props.lookupMa}
                onChange={(event) => props.setLookupMa(event.target.value)}
                placeholder="A01"
                className="h-11 flex-1 rounded-xl bg-white px-3 ring-1 ring-rose-100"
              />
              <button
                type="button"
                data-testid="lookup-load"
                className="h-11 rounded-full bg-white px-4 text-sm font-semibold text-rose-800 ring-1 ring-rose-100"
                onClick={() => void props.loadMa(props.lookupMa)}
              >
                Mở
              </button>
            </div>
            {props.loadedMa ? (
              <p className="mt-2 text-xs text-rose-700">Đang sửa {props.loadedMa}</p>
            ) : (
              <p className="mt-2 text-xs text-rose-700/70">Gõ mã như A01 để tìm nha iu ơi.</p>
            )}
            <label className="mt-3 mb-1 block text-xs font-medium" htmlFor="rename-ma">
              Đổi mã · Change code
            </label>
            <input
              id="rename-ma"
              data-testid="rename-ma"
              value={props.renameTo}
              onChange={(event) => props.setRenameTo(event.target.value)}
              placeholder="P hoặc P10"
              className="h-11 w-full rounded-xl bg-white px-3 ring-1 ring-rose-100"
            />
          </fieldset>
        ) : null}
        <fieldset className="mb-4">
          <label className="mb-2 block text-sm font-medium">Loại đồ · Type</label>
          <div className="flex flex-wrap gap-2">
            {KINDS.map((item) => (
              <button
                key={item.code}
                type="button"
                data-testid={`kind-${item.code}`}
                className={`min-h-11 rounded-full px-3 py-2 text-sm font-semibold ring-1 ${
                  props.kind === item.code
                    ? "bg-primary text-primary-foreground ring-primary"
                    : "bg-white text-rose-800 ring-rose-100"
                }`}
                onClick={() => props.onKind(item.code)}
              >
                {item.label}
                <span className="ml-1 text-[11px] opacity-70">{item.hint}</span>
              </button>
            ))}
          </div>
        </fieldset>
        <fieldset className="mb-4" data-testid="piece-board">
          <label className="mb-2 block text-sm font-medium">
            Ảnh + màu <span className="font-normal text-rose-700/60">(tuỳ chọn)</span>
          </label>
          <label className="mt-3 flex min-h-28 cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-rose-200 bg-white text-center text-xs text-rose-700">
            <span className="text-lg">♡</span>
            Thêm ảnh
            <input
              type="file"
              accept="image/*"
              multiple
              className="hidden"
              onChange={(event) => {
                const files = [...(event.target.files ?? [])];
                props.setPhotos([
                  ...props.photos,
                  ...files.map((file) => ({
                    id: `new:${file.name}:${file.size}:${file.lastModified}`,
                    file,
                    url: URL.createObjectURL(file),
                  })),
                ]);
              }}
            />
          </label>
          {props.photos.length ? (
            <div className="mt-3 grid grid-cols-3 gap-2">
              {props.photos.map((photo) => (
                <img key={photo.id} src={photo.url} alt="" className="h-24 w-full rounded-xl object-cover" />
              ))}
            </div>
          ) : null}
          <div className="mt-4" data-testid="available-colors">
            <label className="mb-2 block text-sm font-medium">
              🎨 Màu có sẵn <span className="font-normal text-rose-700/60">(tuỳ chọn)</span>
            </label>
            <div className="flex flex-wrap gap-1.5">
              {COLORS.map((chip) => {
                const on = props.colors.includes(chip.vi);
                return (
                  <button
                    key={chip.code}
                    type="button"
                    data-testid={`color-chip-${chip.code}`}
                    aria-pressed={on}
                    className={`inline-flex min-h-10 items-center rounded-full px-3 text-xs font-semibold ring-1 ${
                      on ? "bg-primary text-primary-foreground ring-primary" : "bg-white text-rose-800 ring-rose-100"
                    }`}
                    onClick={() =>
                      props.setColors(
                        on ? props.colors.filter((c) => c !== chip.vi) : [...props.colors, chip.vi],
                      )
                    }
                  >
                    {chip.vi}
                  </button>
                );
              })}
            </div>
            <label className="mt-3 mb-1 block text-sm font-medium" htmlFor="color-note">
              📝 Ghi chú màu <span className="font-normal text-rose-700/60">(tuỳ chọn)</span>
            </label>
            <input
              id="color-note"
              data-testid="color-note"
              value={props.colorNote}
              onChange={(event) => props.setColorNote(event.target.value)}
              className="h-11 w-full rounded-xl bg-white px-3 ring-1 ring-rose-100"
            />
          </div>
        </fieldset>
      </div>
      <div>
        <fieldset className="mb-4">
          <label className="mb-2 block text-sm font-medium">Size (tuỳ chọn)</label>
          <div className="flex flex-wrap gap-1.5">
            {SIZES.map((size) => {
              const on = props.sizes.includes(size);
              return (
                <button
                  key={size}
                  type="button"
                  data-testid={`size-${size}`}
                  className={`min-h-10 rounded-full px-3 text-sm font-semibold ring-1 ${
                    on ? "bg-primary text-primary-foreground ring-primary" : "bg-white text-rose-800 ring-rose-100"
                  }`}
                  onClick={() =>
                    props.setSizes(on ? props.sizes.filter((s) => s !== size) : [...props.sizes, size])
                  }
                >
                  {size}
                </button>
              );
            })}
          </div>
        </fieldset>
        <fieldset className="mb-4">
          <label className="mb-2 block text-sm font-medium">Giá gốc / cost (tuỳ chọn)</label>
          <div className="grid grid-cols-2 gap-2">
            <input
              data-testid="cost-cny"
              value={props.costCny}
              onChange={(event) => props.setCostCny(event.target.value)}
              placeholder="¥ CNY"
              className="h-11 rounded-xl bg-white px-3 ring-1 ring-rose-100"
            />
            <input
              data-testid="cost-usd"
              value={props.costUsd}
              onChange={(event) => props.setCostUsd(event.target.value)}
              placeholder="$ USD"
              className="h-11 rounded-xl bg-white px-3 ring-1 ring-rose-100"
            />
          </div>
        </fieldset>
        <fieldset className="mb-4">
          <label className="mb-2 block text-sm font-medium">Giá bán / sell (tuỳ chọn)</label>
          <div className="grid grid-cols-2 gap-2">
            <input
              data-testid="sell-cny"
              value={props.sellCny}
              onChange={(event) => props.setSellCny(event.target.value)}
              placeholder="¥ CNY"
              className="h-11 rounded-xl bg-white px-3 ring-1 ring-rose-100"
            />
            <input
              data-testid="sell-usd"
              value={props.sellUsd}
              onChange={(event) => props.setSellUsd(event.target.value)}
              placeholder="$ USD"
              className="h-11 rounded-xl bg-white px-3 ring-1 ring-rose-100"
            />
          </div>
        </fieldset>
        <p className="mb-4 text-center text-[11px] text-rose-700/70">{props.fxLabel}</p>
        <fieldset className="mb-5">
          <label className="mb-2 block text-sm font-medium" htmlFor="link">
            Link shop / Taobao <span className="font-normal text-rose-700/60">(tuỳ chọn)</span>
          </label>
          <input
            id="link"
            data-testid="shop-link"
            value={props.link}
            onChange={(event) => props.setLink(event.target.value)}
            placeholder="https://e.tb.cn/... hoặc dán cả đoạn share"
            className="h-11 w-full rounded-xl bg-white px-3 ring-1 ring-rose-100"
          />
        </fieldset>
        <button
          type="button"
          data-testid="save-mint"
          disabled={props.busy || !props.canSave}
          className="h-12 w-full rounded-full bg-primary text-base font-bold text-primary-foreground disabled:opacity-50 lg:h-14 lg:text-lg"
          onClick={() => void props.onSaveClick()}
        >
          {props.busy
            ? "Đang lưu…"
            : props.tab === "edit"
              ? "Lưu thay đổi · Keep same mã"
              : "Lưu & lấy mã · Mint code"}
        </button>
      </div>
    </div>
  );
}

function FindPanel({
  preview,
  matches,
  copied,
  setCopied,
  onPhoto,
}: {
  preview: string | null;
  matches: { ma: string; kind: string; color: string }[];
  copied: string | null;
  setCopied: (value: string | null) => void;
  onPhoto: (file: File) => Promise<void>;
}) {
  return (
    <div data-testid="find-ma" className="space-y-4">
      <label
        data-testid="find-drop"
        className="flex min-h-36 cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-rose-200 bg-white text-center text-sm text-rose-700"
      >
        {preview ? <img src={preview} alt="" className="mb-2 h-28 rounded-xl object-cover" /> : null}
        Thả / chọn ảnh đã lưu để tìm mã
        <input
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) void onPhoto(file);
          }}
        />
      </label>
      {matches.map((match) => (
        <div key={match.ma} className="flex items-center justify-between rounded-2xl bg-white px-3 py-2 ring-1 ring-rose-100">
          <p className="font-bold text-rose-800">
            {match.ma}
            <span className="ml-2 text-xs font-medium text-rose-600">{match.color}</span>
          </p>
          <button
            type="button"
            className="h-9 rounded-full bg-primary px-3 text-xs font-semibold text-primary-foreground"
            onClick={async () => {
              await navigator.clipboard.writeText(match.ma);
              setCopied(match.ma);
            }}
          >
            {copied === match.ma ? "Đã copy mã" : "Copy mã"}
          </button>
        </div>
      ))}
    </div>
  );
}
