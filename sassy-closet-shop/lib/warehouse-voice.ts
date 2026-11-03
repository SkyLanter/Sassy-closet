import type { Fulfillment } from "@/lib/fulfillment";

const ON_HAND = /\bon hand\b/i;
const DANG_CO = /đang có/i;
const INVENTED_ETA = /2[–-]4\s*(week|tuần)|porch date|\$6\.95|flat \$\d/i;

export const WAREHOUSE_ON_HAND_ERROR =
  "Dropship copy cannot say “on hand” — that reads as Bay Area warehouse stock. Use Message-first order language.";
export const WAREHOUSE_DANG_CO_ERROR =
  "Dropship copy cannot say “đang có” — that reads as warehouse stock. Use Message language.";
export const INVENTED_LEAD_ERROR =
  "Do not invent a ship $ or a lead-time guarantee. Quote meetup or US ship in chat.";

/** Customer copy must not claim Bay Area warehouse stock on a Taobao dropship look. */
export function warehouseVoiceError(
  descriptionEn: string,
  descriptionVn: string,
  fulfillment: Fulfillment,
): string | null {
  const blob = `${descriptionEn}\n${descriptionVn}`;
  if (INVENTED_ETA.test(blob)) {
    return INVENTED_LEAD_ERROR;
  }
  switch (fulfillment) {
    case "on_hand":
      return null;
    case "dropship":
      if (ON_HAND.test(blob)) {
        return WAREHOUSE_ON_HAND_ERROR;
      }
      if (DANG_CO.test(blob)) {
        return WAREHOUSE_DANG_CO_ERROR;
      }
      return null;
    default: {
      const _exhaustive: never = fulfillment;
      return _exhaustive;
    }
  }
}
