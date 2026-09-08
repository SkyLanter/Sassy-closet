import { NextResponse } from "next/server";
import { publicAsk, readReplySecret, replyAsk, replySecretOk } from "@/lib/ask-store";
import { withSharedStore } from "@/lib/with-shared";

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
    const record = await withSharedStore(
      () => replyAsk(String(body.id ?? ""), String(body.answer ?? "")),
      "write",
    );
    return NextResponse.json(publicAsk(record));
  } catch (error) {
    const status = (error as { status?: number }).status ?? 500;
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Reply lỗi." },
      { status },
    );
  }
}
