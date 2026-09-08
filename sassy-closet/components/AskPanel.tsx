"use client";

import { useEffect, useRef, useState } from "react";
import type { AskCopy } from "@/lib/types";

type ChatRole = "user" | "assistant";

type ChatItem = {
  id: string;
  role: ChatRole;
  text: string;
  copies: AskCopy[];
  offline?: boolean;
};

const CHIPS = [
  { id: "stock", label: "Còn A01?", text: "còn A01 không?" },
  { id: "caption", label: "Caption A01", text: "viết caption A01" },
  { id: "inbox", label: "Inbox A01", text: "soạn tin messenger A01" },
  { id: "size", label: "Size?", text: "size nào được?" },
];

const POLL_MS = 1000;
const TIMEOUT_MS = 45_000;

export function AskPanel() {
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<string | null>(null);
  const [log, setLog] = useState<ChatItem[]>([
    {
      id: "hello",
      role: "assistant",
      text: "Mini Boss nè. Hỏi mã / size / màu / caption / inbox. Copy thôi — không Post, không Send.",
      copies: [],
    },
  ]);
  const scroller = useRef<HTMLDivElement>(null);
  const seq = useRef(0);

  useEffect(() => {
    scroller.current?.scrollTo({ top: scroller.current.scrollHeight });
  }, [log, busy]);

  async function send(text: string) {
    const question = text.trim();
    if (!question || busy) return;
    setError(null);
    setDraft("");
    const userId = `u-${(seq.current += 1)}`;
    setLog((current) => [
      ...current,
      { id: userId, role: "user", text: question, copies: [] },
    ]);
    setBusy(true);
    try {
      const created = await postAsk(question);
      const ready = await waitForAsk(created.id, created);
      const offline = Boolean(ready.offline) || ready.source === "local";
      setLog((current) => [
        ...current,
        {
          id: `a-${(seq.current += 1)}`,
          role: "assistant",
          text: ready.answer || "Có lỗi nhỏ, thử lại nha 🥺",
          copies: ready.copies ?? [],
          offline,
        },
      ]);
    } catch {
      setError("Chưa gửi được. Kiểm tra mạng rồi thử lại.");
    } finally {
      setBusy(false);
    }
  }

  async function copy(id: string, text: string) {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(id);
    } catch {
      setCopied(null);
    }
  }

  return (
    <div data-testid="mini-boss" className="flex min-h-[28rem] flex-col gap-3">
      <div
        ref={scroller}
        data-testid="mini-boss-log"
        className="max-h-[min(52dvh,28rem)] space-y-2 overflow-y-auto pr-1"
      >
        {log.map((item) => (
          <article
            key={item.id}
            data-testid={`mini-boss-${item.role}`}
            className={
              item.role === "user"
                ? "ml-8 rounded-2xl bg-primary px-3 py-2 text-sm leading-relaxed text-primary-foreground"
                : "mr-6 rounded-2xl bg-white px-3 py-2 text-sm leading-relaxed text-rose-900 ring-1 ring-rose-100"
            }
          >
            {item.offline ? (
              <p
                data-testid="ask-offline-banner"
                className="mb-2 rounded-xl bg-amber-50 px-2 py-1 text-xs font-semibold text-amber-800"
              >
                Mini Boss offline — local draft
              </p>
            ) : null}
            <p className="whitespace-pre-wrap">{item.text}</p>
            {item.copies.map((copyItem) => (
              <div key={copyItem.id} className="mt-2">
                <pre
                  data-testid={`mini-boss-copy-text-${copyItem.id}`}
                  className="whitespace-pre-wrap rounded-xl bg-rose-50 px-3 py-2 font-sans text-xs text-rose-900"
                >
                  {copyItem.text}
                </pre>
                <button
                  type="button"
                  data-testid={`mini-boss-copy-${copyItem.id}`}
                  className="mt-2 h-10 rounded-full bg-primary px-4 text-xs font-semibold text-primary-foreground"
                  onClick={() => void copy(`${item.id}-${copyItem.id}`, copyItem.text)}
                >
                  {copied === `${item.id}-${copyItem.id}` ? "Đã copy" : copyItem.label}
                </button>
              </div>
            ))}
          </article>
        ))}
        {busy ? (
          <p data-testid="mini-boss-busy" className="text-sm text-muted-foreground">
            …
          </p>
        ) : null}
      </div>
      {error ? (
        <p className="rounded-2xl bg-rose-100 px-3 py-2 text-sm text-rose-800">{error}</p>
      ) : null}
      <div className="flex flex-wrap gap-1.5">
        {CHIPS.map((chip) => (
          <button
            key={chip.id}
            type="button"
            data-testid={`mini-boss-chip-${chip.id}`}
            className="min-h-10 rounded-full bg-white px-3 text-xs font-semibold text-rose-800 ring-1 ring-rose-100"
            disabled={busy}
            onClick={() => void send(chip.text)}
          >
            {chip.label}
          </button>
        ))}
      </div>
      <div className="flex gap-2">
        <textarea
          data-testid="mini-boss-input"
          value={draft}
          rows={2}
          placeholder="Hỏi Mini Boss…"
          className="min-h-11 flex-1 rounded-2xl bg-white px-3 py-2 text-base ring-1 ring-rose-100"
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              void send(draft);
            }
          }}
        />
        <button
          type="button"
          data-testid="mini-boss-send"
          className="h-11 shrink-0 self-end rounded-full bg-primary px-4 font-semibold text-primary-foreground disabled:opacity-50"
          disabled={busy || !draft.trim()}
          onClick={() => void send(draft)}
        >
          Gửi
        </button>
      </div>
    </div>
  );
}

type AskPayload = {
  id: string;
  status: "waiting" | "ready" | "error";
  answer?: string;
  copies?: AskCopy[];
  source?: "relay" | "local";
  offline?: boolean;
};

async function postAsk(question: string): Promise<AskPayload> {
  const response = await fetch("/api/ask", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ question }),
  });
  const data = (await response.json()) as AskPayload & { error?: string };
  if (!response.ok) throw new Error(data.error || "ask failed");
  return data;
}

async function waitForAsk(id: string, initial: AskPayload): Promise<AskPayload> {
  if (initial.status === "ready") return initial;
  const started = Date.now();
  while (Date.now() - started < TIMEOUT_MS) {
    await sleep(POLL_MS);
    const response = await fetch(`/api/ask/${encodeURIComponent(id)}`);
    const data = (await response.json()) as AskPayload;
    if (data.status === "ready") return data;
  }
  const last = await fetch(`/api/ask/${encodeURIComponent(id)}`);
  return (await last.json()) as AskPayload;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
