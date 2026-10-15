import { NextResponse } from "next/server";
import { intakeSaveFailure, saveFromForm } from "@/lib/form-save";
import { intakeCatalog } from "@/lib/kinds";
import { scheduleNewMaWebhookFromRow } from "@/lib/newMaWebhook";
import { listSubmissions, storeHealth } from "@/lib/store";

export async function GET() {
  return NextResponse.json({
    submissions: await listSubmissions(),
    storage: storeHealth(),
    catalog: intakeCatalog(),
  });
}

export async function POST(request: Request) {
  try {
    const form = await request.formData();
    const submission = await saveFromForm(form);
    scheduleNewMaWebhookFromRow("create", submission);
    return NextResponse.json({ submission });
  } catch (error) {
    const failure = intakeSaveFailure(error);
    return NextResponse.json(failure.body, { status: failure.status });
  }
}
