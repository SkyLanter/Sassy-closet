import { NextResponse } from "next/server";
import { getAsk, publicAsk } from "@/lib/ask-store";
import { withSharedStore } from "@/lib/with-shared";

export async function GET(
  _request: Request,
  context: { params: Promise<{ id: string }> },
) {
  const { id } = await context.params;
  const record = await withSharedStore(() => getAsk(id), "write");
  if (!record) {
    return NextResponse.json({ error: "Ask id không có." }, { status: 404 });
  }
  return NextResponse.json(publicAsk(record));
}
