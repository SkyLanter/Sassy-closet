import { NextResponse } from "next/server";
import { localAskAnswer } from "@/lib/ask-fallback";
import { withSharedStore } from "@/lib/with-shared";

export async function POST(request: Request) {
  let question = "";
  try {
    const body = (await request.json()) as { question?: string };
    question = String(body.question ?? "");
  } catch {
    return NextResponse.json({ error: "JSON body cần question." }, { status: 400 });
  }
  const answer = await withSharedStore(() => localAskAnswer(question), "read");
  return NextResponse.json({
    reply: answer.reply,
    copies: answer.copies,
    source: "rules",
    llm: false,
  });
}
