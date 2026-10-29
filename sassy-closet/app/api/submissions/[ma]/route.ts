import { NextResponse } from "next/server";
import { requireShopAdmin } from "@/lib/shop-admin-http";
import { saveFromForm } from "@/lib/form-save";
import { normalizeMa } from "@/lib/mint";
import { scheduleNewMaWebhookFromRow } from "@/lib/newMaWebhook";
import { getSubmission } from "@/lib/store";
import { storeUnavailableResponse } from "@/lib/store-unavailable";

export async function GET(
  request: Request,
  context: { params: Promise<{ ma: string }> },
) {
  const denied = await requireShopAdmin(request);
  if (denied) return denied;
  const { ma } = await context.params;
  let submission;
  try {
    submission = await getSubmission(ma);
  } catch (error) {
    return storeUnavailableResponse(error);
  }
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
  const denied = await requireShopAdmin(request);
  if (denied) return denied;
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
    const status = (error as { status?: number }).status ?? 400;
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Chưa lưu được, thử lại nha." },
      { status },
    );
  }
}
