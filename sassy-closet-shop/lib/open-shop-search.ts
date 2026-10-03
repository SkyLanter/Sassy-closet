export const OPEN_SHOP_SEARCH_EVENT = "sassy:open-search";

/** Ask the sticky header to open its search field. Home does not mount a second box. */
export function requestShopSearch(): void {
  window.dispatchEvent(new Event(OPEN_SHOP_SEARCH_EVENT));
}
