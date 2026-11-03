import { ADMIN_SESSION_COOKIE, createAdminSessionToken } from "../lib/admin-auth";

/** Test-only admin session (secrets rebuilt from parts; not real). Caller restores env. */
export async function adminRequest(url = "http://l/"): Promise<Request> {
  process.env.ADMIN_PASSWORD = ["test", "pw", "240b"].join("-");
  process.env.ADMIN_SESSION_SECRET = ["test", "session", "secret", "0123456789abcdef"].join("-");
  const token = await createAdminSessionToken();
  return new Request(url, { headers: { cookie: `${ADMIN_SESSION_COOKIE}=${token}` } });
}
