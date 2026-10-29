import { maIndexPayload } from "@/lib/ma-index";
import { shopAdminJson } from "@/lib/shop-admin-http";
import { listSubmissions } from "@/lib/store";
import { storeUnavailableResponse } from "@/lib/store-unavailable";

export const dynamic = "force-dynamic";

/**
 * Public mã index for auto-list. No session and no service token.
 * Cost routes stay gated. This payload is a whitelist (see lib/ma-index.ts).
 */
export async function GET() {
  let submissions;
  try {
    submissions = await listSubmissions();
  } catch (error) {
    return storeUnavailableResponse(error);
  }
  return shopAdminJson(maIndexPayload(submissions));
}
