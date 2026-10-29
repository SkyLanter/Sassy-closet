import { intakeDirectJson, withIntakeDirectLinkHeaders } from "@/lib/intake-direct-link";
import { lookupMaCard } from "@/lib/ma-card";
import { storeUnavailableResponse } from "@/lib/store-unavailable";

export async function GET(
  _request: Request,
  context: { params: Promise<{ code: string }> },
) {
  const { code } = await context.params;
  let decoded = code ?? "";
  try {
    decoded = decodeURIComponent(decoded);
  } catch {
    // Next already decoded the param; a literal "%" stays as-is (lookup miss → 404).
  }
  let card;
  try {
    card = await lookupMaCard(decoded);
  } catch (error) {
    return withIntakeDirectLinkHeaders(storeUnavailableResponse(error));
  }
  if (!card) {
    return intakeDirectJson({ error: "Không tìm thấy mã" }, 404);
  }
  return intakeDirectJson({
    code: card.code,
    staged: card.staged,
    on_hand: card.on_hand,
    staged_only: card.staged_only,
  });
}
