import { NextResponse } from "next/server";
import { findByPhotoHash, hashBytes } from "@/lib/store";
import { storeUnavailableResponse } from "@/lib/store-unavailable";

export async function POST(request: Request) {
  const form = await request.formData();
  const photo = form.get("photo");
  if (!(photo instanceof File)) {
    return NextResponse.json(
      { error: "Chưa nhận được ảnh.", error_en: "Send one photo to search." },
      { status: 400 },
    );
  }
  const bytes = Buffer.from(await photo.arrayBuffer());
  let rows;
  try {
    rows = await findByPhotoHash(hashBytes(bytes));
  } catch (error) {
    return storeUnavailableResponse(error);
  }
  const matches = rows.map((row) => ({
    ma: row.ma,
    kind: row.kind,
    color: row.color,
  }));
  return NextResponse.json({ matches });
}
