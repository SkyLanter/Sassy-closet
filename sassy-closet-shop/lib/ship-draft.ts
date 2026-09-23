import { HOLD_ASK_LABEL, MESSAGE_ORDER, SHIP_QUOTE } from "@/lib/dropship-copy";
import type { ProductStatus } from "@/lib/types";

export type ShipDraftFields = {
  name: string;
  address: string;
  city: string;
  note: string;
};

export const EMPTY_SHIP_DRAFT: ShipDraftFields = {
  name: "",
  address: "",
  city: "",
  note: "",
};

export const SHIP_DRAFT_STORAGE_KEY = "sassy-closet-ship-draft-v1";

export function composeShipDraftMessage(
  ma: string,
  status: ProductStatus,
  fields: ShipDraftFields,
): string {
  const intent = status === "hold" ? HOLD_ASK_LABEL : MESSAGE_ORDER;
  const lines = [`Mã ${ma} — ${intent}.`, SHIP_QUOTE + "."];
  const name = fields.name.trim();
  const address = fields.address.trim();
  const city = fields.city.trim();
  const note = fields.note.trim();
  if (name) {
    lines.push(`Name: ${name}`);
  }
  if (address) {
    lines.push(`Address: ${address}`);
  }
  if (city) {
    lines.push(`City: ${city}`);
  }
  if (note) {
    lines.push(`Note: ${note}`);
  }
  const text = lines.join("\n");
  if (/\$\d/.test(text) || /ship\s*\$/i.test(text)) {
    throw new Error("Ship draft must not invent a ship $");
  }
  return text;
}

export function parseStoredShipDraft(raw: string | null): ShipDraftFields {
  if (!raw) {
    return { ...EMPTY_SHIP_DRAFT };
  }
  try {
    const value = JSON.parse(raw) as Partial<ShipDraftFields>;
    return {
      name: typeof value.name === "string" ? value.name : "",
      address: typeof value.address === "string" ? value.address : "",
      city: typeof value.city === "string" ? value.city : "",
      note: typeof value.note === "string" ? value.note : "",
    };
  } catch {
    return { ...EMPTY_SHIP_DRAFT };
  }
}
