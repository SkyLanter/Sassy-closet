import { NextResponse } from "next/server";
import {
  applyLocalFallback,
  createAsk,
  notifyWebhook,
  publicAsk,
  webhookConfigured,
} from "@/lib/ask-store";
import { withSharedStore } from "@/lib/with-shared";

export async function POST(request: Request) {
  let question = "";
  try {
    const body = (await request.json()) as { question?: string };
    question = String(body.question ?? "");
  } catch {
    return NextResponse.json({ error: "JSON body cần question." }, { status: 400 });
  }

  try {
    return await withSharedStore(async () => {
      const record = createAsk(question);
      if (!webhookConfigured()) {
        applyLocalFallback(record);
        return NextResponse.json(publicAsk(record));
      }
      try {
        const ok = await notifyWebhook(record);
        if (!ok) applyLocalFallback(record);
      } catch {
        applyLocalFallback(record);
      }
      return NextResponse.json(publicAsk(record));
    }, "write");
  } catch (error) {
    const status = (error as { status?: number }).status ?? 500;
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Ask lỗi." },
      { status },
    );
  }
}
