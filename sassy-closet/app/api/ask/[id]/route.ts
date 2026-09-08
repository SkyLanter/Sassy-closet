import { NextResponse } from "next/server";
import { getAsk, publicAsk } from "@/lib/ask-store";

export async function GET(
  _request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const { id } = await context.params;
  const record = await getAsk(id);
  if (!record) {
    return NextResponse.json({ error: "Ask id không có." }, { status: 404 });
  }
  return NextResponse.json(publicAsk(record));
}
