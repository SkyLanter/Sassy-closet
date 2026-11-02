import { intakeDirectJson } from "@/lib/intake-direct-link";
import { getFx, setFx } from "@/lib/store";
import { storeUnavailableResponse } from "@/lib/store-unavailable";

/** Open by link. The rate is public; this response stays noindex without a session. */
export async function GET() {
  try {
    return intakeDirectJson(await getFx());
  } catch (error) {
    return storeUnavailableResponse(error);
  }
}

export async function POST(request: Request) {
  let usdCny = NaN;
  try {
    const body = (await request.json()) as { usd_cny?: number };
    usdCny = Number(body.usd_cny);
  } catch {
    usdCny = NaN;
  }
  if (!Number.isFinite(usdCny) || usdCny <= 0) {
    return intakeDirectJson(
      { error: "Tỷ giá phải là số dương, vd 6.71" },
      400,
    );
  }
  return intakeDirectJson(await setFx(usdCny));
}
