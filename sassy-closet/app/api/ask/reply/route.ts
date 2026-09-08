import { NextResponse } from "next/server";
import { publicAsk, readReplySecret, replyAsk, replySecretOk } from "@/lib/ask-store";

export async function POST(request: Request) {
  let body: { id?: string; answer?: string; secret?: string } = {};
  try {
    body = (await request.json()) as typeof body;
  } catch {
    return NextResponse.json({ error: "JSON body cần id + answer." }, { status: 400 });
  }

  if (!replySecretOk(readReplySecret(request, body))) {
    return NextResponse.json({ error: "Unauthorized." }, { status: 401 });
  }

  try {
    const record = replyAsk(String(body.id ?? ""), String(body.answer ?? ""));
    return NextResponse.json(publicAsk(record));
  } catch (error) {
    const status = (error as { status?: number }).status ?? 500;
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Reply lỗi." },
      { status },
    );
  }
}
