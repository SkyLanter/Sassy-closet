import { emptyStore } from "./store-backend";
import { getFx } from "./store";
import { storeErrorReason } from "./store-unavailable";

export type HomeFx = { usd_cny: number; label: string; fallback: boolean };

/**
 * FX for the intake home page. Display only: if the store can't be read
 * (e.g. Blob blocked), show the default rate so the form still loads.
 * Never writes; saves still refuse when the store is unreadable.
 */
export async function getHomeFx(read: typeof getFx = getFx): Promise<HomeFx> {
  try {
    const fx = await read();
    return { usd_cny: fx.usd_cny, label: fx.label, fallback: false };
  } catch (error) {
    console.error(`[intake] home fx read failed: ${storeErrorReason(error)}`);
    const usd = emptyStore().fx.usd_cny;
    return {
      usd_cny: usd,
      label: `Tỷ giá mặc định: 1 USD = ${usd} ¥ CNY · kho đang không đọc được, báo Mini Boss nha`,
      fallback: true,
    };
  }
}
