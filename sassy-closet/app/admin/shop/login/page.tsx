import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";

/** Old sign-in URL. Shop tools have no password. */
export default function ShopToolsLoginPage() {
  redirect("/admin/shop");
}
