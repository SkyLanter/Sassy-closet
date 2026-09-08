import { NextResponse } from "next/server";
import { saveFromForm } from "@/lib/form-save";
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
    return NextResponse.json({ submission });
  } catch (error) {
    const status = (error as { status?: number }).status ?? 400;
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Chưa lưu được, thử lại nha." },
      { status },
    );
  }
}
