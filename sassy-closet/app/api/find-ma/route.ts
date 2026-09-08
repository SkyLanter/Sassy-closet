import { NextResponse } from "next/server";
import { findByPhotoHash, hashBytes } from "@/lib/store";

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
  const matches = (await findByPhotoHash(hashBytes(bytes))).map((row) => ({
    ma: row.ma,
    kind: row.kind,
    color: row.color,
  }));
  return NextResponse.json({ matches });
}
