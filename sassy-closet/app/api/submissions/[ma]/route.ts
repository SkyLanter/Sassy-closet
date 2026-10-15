import { NextResponse } from "next/server";
import { intakeSaveFailure, saveFromForm } from "@/lib/form-save";
import { normalizeMa } from "@/lib/mint";
import { scheduleNewMaWebhookFromRow } from "@/lib/newMaWebhook";
import { getSubmission } from "@/lib/store";

export async function GET(
  _request: Request,
  context: { params: Promise<{ ma: string }> },
) {
  const { ma } = await context.params;
  const submission = await getSubmission(ma);
  if (!submission) {
    return NextResponse.json({ error: "Không tìm thấy mã này 🥺" }, { status: 404 });
  }
  return NextResponse.json({
    ma: submission.ma,
    caption_vi: submission.caption_vi,
    submission,
  });
}

export async function PATCH(
  request: Request,
  context: { params: Promise<{ ma: string }> },
) {
  const { ma } = await context.params;
  try {
    const form = await request.formData();
    const submission = await saveFromForm(form, ma);
    const urlMa = normalizeMa(ma);
    const savedMa = normalizeMa(submission.ma);
    scheduleNewMaWebhookFromRow(
      "update",
      submission,
      urlMa !== savedMa ? urlMa : undefined,
    );
    return NextResponse.json({ submission });
  } catch (error) {
    const failure = intakeSaveFailure(error);
    return NextResponse.json(failure.body, { status: failure.status });
  }
}
