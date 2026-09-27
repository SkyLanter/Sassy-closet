import { cookies } from "next/headers";
import { ADMIN_SESSION_COOKIE, verifyAdminSession } from "@/lib/admin-auth";

export async function hasAdminSession(): Promise<boolean> {
  const jar = await cookies();
  return verifyAdminSession(jar.get(ADMIN_SESSION_COOKIE)?.value ?? "");
}
