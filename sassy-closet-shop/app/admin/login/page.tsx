import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { safeAdminNext } from "@/lib/admin-gate";
import { hasAdminSession } from "@/lib/admin-session-request";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export const metadata: Metadata = {
  title: "Sign in",
  robots: { index: false, follow: false },
};

function loginNotice(code: string | undefined): string | null {
  switch (code) {
    case "1":
      return "That password did not match.";
    case "closed":
      return "The desk is locked.";
    case "slow":
      return "Too many tries. Wait a few minutes, then try again.";
    default:
      return null;
  }
}

export default async function AdminLoginPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string; e?: string }>;
}) {
  if (await hasAdminSession()) {
    redirect("/admin");
  }
  const query = await searchParams;
  const next = safeAdminNext(typeof query.next === "string" ? query.next : null);
  const notice = loginNotice(typeof query.e === "string" ? query.e : undefined);

  return (
    <main className="flex flex-1 items-center justify-center px-4 py-16">
      <form
        method="post"
        action="/api/admin/login"
        className="w-full max-w-sm rounded-2xl border border-gold/45 bg-paper px-6 py-8"
      >
        <span className="mb-4 inline-block h-2.5 w-2.5 rounded-full bg-gold/70" aria-hidden />
        <p className="font-display text-4xl leading-[1.08] text-ink" translate="no">
          Sassy Closet
        </p>
        <h1 className="mt-2 text-sm text-muted" translate="no">
          Sign in
        </h1>
        <label htmlFor="admin-password" className="mt-6 block text-sm text-ink" translate="no">
          Password
        </label>
        <input
          id="admin-password"
          name="password"
          type="password"
          required
          autoFocus
          autoComplete="current-password"
          autoCapitalize="off"
          autoCorrect="off"
          spellCheck={false}
          className="mt-2 w-full min-h-11 rounded-xl border border-line bg-paper px-3 text-base text-ink outline-none focus:border-gold"
        />
        <input type="hidden" name="next" value={next} />
        <button
          type="submit"
          className="mt-5 inline-flex min-h-11 w-full touch-manipulation items-center justify-center rounded-full bg-ink px-5 text-sm text-paper hover-hover:hover:opacity-90"
        >
          Sign in
        </button>
        {notice ? (
          <p role="alert" className="mt-4 text-sm text-muted" translate="no">
            {notice}
          </p>
        ) : null}
      </form>
    </main>
  );
}
