import { NextResponse } from "next/server";
import { saveFromForm } from "@/lib/form-save";
import { listSubmissions, storeHealth } from "@/lib/store";

export async function GET() {
  return NextResponse.json({
    submissions: await listSubmissions(),
    storage: storeHealth(),
  });
}

export async function POST(request: Request) {
  try {
    const form = await request.formData();
    const submission = await saveFromForm(form);
    return NextResponse.json({ submission });
  } catch (error) {
    const status = (error as { status?: number }).status ?? 400;
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Chưa lưu được, thử lại nha." },
      { status },
    );
  }
}
