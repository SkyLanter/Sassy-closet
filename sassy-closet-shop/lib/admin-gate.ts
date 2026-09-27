/** Paths the proxy locks unless the request carries a valid admin session. */

const ADMIN_NEXT_PATH = /^\/admin(?:\/[A-Za-z0-9._~-]+)*(?:\?[A-Za-z0-9._~%=&+-]*)?$/;

export function isAdminPagePath(pathname: string): boolean {
  return pathname === "/admin" || pathname.startsWith("/admin/");
}

export function isAdminApiPath(pathname: string): boolean {
  return pathname === "/api/admin" || pathname.startsWith("/api/admin/");
}

export function isAdminLoginPath(pathname: string): boolean {
  return pathname === "/admin/login";
}

export function isAdminLoginApi(pathname: string): boolean {
  return pathname === "/api/admin/login";
}

export function isAdminLogoutApi(pathname: string): boolean {
  return pathname === "/api/admin/logout";
}

export type AdminGateDecision = "public" | "allow" | "deny";

/**
 * `public` — not an admin surface.
 * `allow` — login routes, or any admin route with a valid session.
 * `deny` — admin page or admin API without a session.
 */
export function adminGateDecision(
  pathname: string,
  _method: string,
  hasSession: boolean,
): AdminGateDecision {
  const page = isAdminPagePath(pathname);
  const api = isAdminApiPath(pathname);
  if (!page && !api) {
    return "public";
  }
  if (isAdminLoginPath(pathname) || isAdminLoginApi(pathname)) {
    return "allow";
  }
  if (hasSession) {
    return "allow";
  }
  return "deny";
}

/** Only same-origin admin paths. Anything else becomes the desk home. */
export function safeAdminNext(raw: string | null | undefined): string {
  if (!raw || raw.length > 200) {
    return "/admin";
  }
  if (raw.includes("..") || raw.includes("\\") || raw.includes("//")) {
    return "/admin";
  }
  if (!ADMIN_NEXT_PATH.test(raw)) {
    return "/admin";
  }
  const pathOnly = raw.split("?")[0] ?? "";
  if (pathOnly === "/admin/login" || pathOnly.startsWith("/admin/login/")) {
    return "/admin";
  }
  return raw;
}
