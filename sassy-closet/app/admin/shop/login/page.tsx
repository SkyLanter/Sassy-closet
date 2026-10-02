import { redirect } from "next/navigation";
import { hasShopAdminSession } from "@/lib/admin-session";
import { safeShopAdminNext } from "@/lib/shop-admin-gate";

export const dynamic = "force-dynamic";

function messageFor(code: string | undefined): string | null {
  switch (code) {
    case "1":
      return "Wrong password.";
    case "closed":
      return "Shop tools are locked until the admin password is set.";
    case "slow":
      return "Too many tries. Wait and try again.";
    case undefined:
      return null;
    default:
      return null;
  }
}

export default async function ShopToolsLoginPage({
  searchParams,
}: {
  searchParams: Promise<{ e?: string; next?: string }>;
}) {
  if (await hasShopAdminSession()) {
    redirect("/admin/shop");
  }
  const query = await searchParams;
  const next = safeShopAdminNext(query.next);
  const message = messageFor(query.e);

  return (
    <main className="mx-auto max-w-md px-4 py-10 text-[#5c3d48]">
      <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[#a85d74]">Admin · Shop tools</p>
      <h1 className="mt-1 text-[21px] font-semibold text-[#3c2a2e]">Sign in</h1>
      <p className="mt-2 text-[13.5px] leading-relaxed text-[#7d5360]">
        Password stays on the server. The session cookie is HttpOnly.
      </p>
      {message ? (
        <p role="alert" className="mt-4 text-sm text-[#9b2c2c]">
          {message}
        </p>
      ) : null}
      <form className="mt-6 grid gap-3" method="post" action="/api/shop-catalog/login">
        <input type="hidden" name="next" value={next} />
        <label className="grid gap-1 text-sm">
          <span className="font-semibold text-[#3c2a2e]">Password</span>
          <input
            name="password"
            type="password"
            autoComplete="current-password"
            required
            className="min-h-11 rounded-2xl bg-white px-3 ring-1 ring-[#eadfdc]"
          />
        </label>
        <button
          type="submit"
          className="inline-flex min-h-11 items-center justify-center rounded-full bg-primary px-5 font-bold text-primary-foreground"
        >
          Sign in
        </button>
      </form>
      <p className="mt-6 text-sm">
        <a className="underline-offset-2 hover:underline" href="/">
          Back to intake
        </a>
      </p>
    </main>
  );
}
