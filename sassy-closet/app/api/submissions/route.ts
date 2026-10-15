import { NextResponse } from "next/server";
import { saveFromForm } from "@/lib/form-save";
import { explainIntakeFailure } from "@/lib/intake-errors";
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
    const status = (error as { status?: number }).status ?? 400;
    const raw = error instanceof Error ? error.message : "";
    return NextResponse.json({ error: explainIntakeFailure(raw) }, { status });
  }
}
