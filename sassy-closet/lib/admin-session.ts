/** Intake has no admin session. The link is enough. */
export async function hasShopAdminSession(): Promise<boolean> {
  return true;
}
