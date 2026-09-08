import { NextResponse } from "next/server";
import {
  applyLocalFallback,
  createAsk,
  notifyWebhook,
  publicAsk,
  webhookConfigured,
} from "@/lib/ask-store";

export async function POST(request: Request) {
  let question = "";
  try {
    const body = (await request.json()) as { question?: string };
    question = String(body.question ?? "");
  } catch {
    return NextResponse.json({ error: "JSON body cần question." }, { status: 400 });
  }

  try {
    const record = createAsk(question);
    if (!webhookConfigured()) {
      await applyLocalFallback(record);
      return NextResponse.json(publicAsk(record));
    }
    try {
      const ok = await notifyWebhook(record);
      if (!ok) await applyLocalFallback(record);
    } catch {
      await applyLocalFallback(record);
    }
    return NextResponse.json(publicAsk(record));
  } catch (error) {
    const status = (error as { status?: number }).status ?? 500;
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Ask lỗi." },
      { status },
    );
  }
}
