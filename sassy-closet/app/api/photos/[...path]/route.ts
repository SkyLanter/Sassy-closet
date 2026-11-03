import { NextResponse } from "next/server";
import { readPhoto } from "@/lib/store";
import { storeUnavailableResponse } from "@/lib/store-unavailable";

export async function GET(
  _request: Request,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  let photo;
  try {
    photo = await readPhoto(path.join("/"));
  } catch (error) {
    if ((error as { status?: number }).status === 400) {
      return NextResponse.json({ error: (error as Error).message }, { status: 400 });
    }
    return storeUnavailableResponse(error);
  }
  if (!photo) {
    return NextResponse.json({ error: "Không thấy ảnh." }, { status: 404 });
  }
  return new NextResponse(new Uint8Array(photo.bytes), {
    headers: { "content-type": photo.type },
  });
}
