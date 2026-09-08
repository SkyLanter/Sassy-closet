import { NextResponse } from "next/server";
import { localAskAnswer } from "@/lib/ask-fallback";

export async function POST(request: Request) {
  let question = "";
  try {
    const body = (await request.json()) as { question?: string };
    question = String(body.question ?? "");
  } catch {
    return NextResponse.json({ error: "JSON body cần question." }, { status: 400 });
  }
  const answer = localAskAnswer(question);
  return NextResponse.json({
    reply: answer.reply,
    copies: answer.copies,
    source: "rules",
    llm: false,
  });
}
