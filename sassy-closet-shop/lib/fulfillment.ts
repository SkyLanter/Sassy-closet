export type Fulfillment = "dropship" | "on_hand";

/** Default is dropship. on_hand only when Boss owns / received the piece. */
export function parseFulfillment(value: unknown, ma?: string): Fulfillment {
  if (value === undefined || value === null || value === "") {
    return "dropship";
  }
  if (value === "dropship" || value === "on_hand") {
    return value;
  }
  throw new Error(
    ma
      ? `Mã ${ma} fulfillment must be dropship or on_hand`
      : "Fulfillment must be dropship or on_hand",
  );
}

export function isOnHand(fulfillment: Fulfillment): boolean {
  return fulfillment === "on_hand";
}
