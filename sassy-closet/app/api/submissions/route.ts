import { NextResponse } from "next/server";
import { saveFromForm } from "@/lib/form-save";
import { listSubmissions } from "@/lib/store";
import { withSharedStore } from "@/lib/with-shared";

export async function GET() {
  return NextResponse.json({
    submissions: await withSharedStore(() => listSubmissions(), "read"),
  });
}

export async function POST(request: Request) {
  try {
    const form = await request.formData();
    const submission = await withSharedStore(() => saveFromForm(form), "write");
    return NextResponse.json({ submission });
  } catch (error) {
    const status = (error as { status?: number }).status ?? 400;
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Chưa lưu được, thử lại nha." },
      { status },
    );
  }
}
